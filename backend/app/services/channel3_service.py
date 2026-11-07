"""
Channel3 Product Service for AgentReady Lab.
Queries Channel3 API for real e-commerce products with in-memory TTL caching (300s)
and graceful synthetic fallback fixtures for offline / test execution.
"""
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import httpx
from pydantic import BaseModel, Field

from app.core.config import get_settings

logger = logging.getLogger("agentready.channel3")

FIXTURES_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "fallback_fixtures.json")
)


class Product(BaseModel):
    """Normalized E-commerce Product Model."""
    id: str
    title: str
    description: str
    price: float = Field(..., description="Authoritative merchant unit price")
    currency: str = "USD"
    has_variants: bool = False
    variants: Optional[Dict[str, List[str]]] = None
    requires_selection: Optional[List[str]] = None
    image_url: Optional[str] = None
    inventory: int = 10


class Channel3Service:
    """
    Client for Channel3 catalog search with strict 300s in-memory TTL caching
    to respect Channel3 API data terms and guarantee sub-50ms authoritative lookups.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.ttl_seconds = self.settings.CHANNEL3_CACHE_TTL_SEC
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self._fallback_products: List[Product] = self._load_fallback_fixtures()

    def _load_fallback_fixtures(self) -> List[Product]:
        """Loads baseline catalog fixtures from disk."""
        if not os.path.exists(FIXTURES_PATH):
            logger.warning("Fallback fixtures file not found at %s", FIXTURES_PATH)
            return []
        try:
            with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Product(**item) for item in data]
        except Exception as exc:
            logger.error("Failed to parse fallback fixtures: %s", exc)
            return []

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Retrieves an item from cache if not expired."""
        if key in self._cache:
            expires_at, data = self._cache[key]
            if time.time() < expires_at:
                return data
            # Expired
            del self._cache[key]
        return None

    def _set_in_cache(self, key: str, data: Any) -> None:
        """Stores item in cache with configured TTL."""
        self._cache[key] = (time.time() + self.ttl_seconds, data)

    def clear_cache(self) -> None:
        """Clears all in-memory cached entries."""
        self._cache.clear()

    async def search_products(
        self,
        query: str = "",
        limit: int = 10,
    ) -> List[Product]:
        """
        Searches products by query string.
        Uses in-memory cache if warm, otherwise queries Channel3 API or fallback fixtures.
        """
        cache_key = f"search:{query.lower().strip()}:{limit}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # Check if real Channel3 API key is configured
        has_key = bool(
            self.settings.CHANNEL3_API_KEY
            and not self.settings.CHANNEL3_API_KEY.startswith("your_")
        )

        if has_key:
            try:
                url = "https://api.channel3.ai/v1/search"
                headers = {
                    "Authorization": f"Bearer {self.settings.CHANNEL3_API_KEY}",
                    "Content-Type": "application/json",
                }
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(url, params={"q": query, "limit": limit}, headers=headers)
                    if resp.status_code == 200:
                        items = resp.json().get("products", [])
                        products = [
                            Product(
                                id=item.get("id", f"c3_{idx}"),
                                title=item.get("title", "Product"),
                                description=item.get("description", ""),
                                price=float(item.get("price", 0.0)),
                                currency=item.get("currency", "USD"),
                                has_variants=bool(item.get("variants")),
                                variants=item.get("variants"),
                                requires_selection=item.get("requires_selection"),
                                image_url=item.get("image_url"),
                                inventory=item.get("inventory", 10),
                            )
                            for idx, item in enumerate(items)
                        ]
                        self._set_in_cache(cache_key, products)
                        return products
            except Exception as exc:
                logger.warning("Channel3 API search request failed (%s); using fallback fixtures", exc)

        # Fallback filtering
        q_lower = query.lower().strip()
        if not q_lower:
            results = self._fallback_products[:limit]
        else:
            results = [
                p
                for p in self._fallback_products
                if q_lower in p.title.lower() or q_lower in p.description.lower()
            ][:limit]

        self._set_in_cache(cache_key, results)
        return results

    async def get_all_products(self) -> List[Product]:
        """Returns all products from Channel3 catalog or fallback fixtures."""
        return await self.search_products(query="", limit=50)

    async def get_product(self, product_id: str) -> Optional[Product]:
        """Fetches product details by ID with cache check."""
        cache_key = f"product:{product_id}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # Search in fallback catalog
        for p in self._fallback_products:
            if p.id == product_id:
                self._set_in_cache(cache_key, p)
                return p

        # If not in fallback, search via search_products
        search_res = await self.search_products(query=product_id, limit=1)
        if search_res and search_res[0].id == product_id:
            self._set_in_cache(cache_key, search_res[0])
            return search_res[0]

        return None

    async def get_authoritative_price(
        self,
        product_id: str,
        selected_variants: Optional[Dict[str, str]] = None,
    ) -> Optional[float]:
        """
        Fast authoritative price lookup for checkout validation and price lock verification.
        Executes in sub-millisecond time when served from cache.
        """
        product = await self.get_product(product_id)
        if not product:
            return None
        return product.price


_channel3_service: Optional[Channel3Service] = None


def get_channel3_service() -> Channel3Service:
    """Returns singleton instance of Channel3Service."""
    global _channel3_service
    if _channel3_service is None:
        _channel3_service = Channel3Service()
    return _channel3_service

