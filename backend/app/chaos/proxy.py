"""
Deterministic Seeded Chaos Proxy for AgentReady Lab.
Controls fault injection timing, batched 5-buyer concurrency (Semaphore 5),
and deterministic test reproducibility using seeded pseudorandom generators (seed=101).
"""
import asyncio
import copy
import logging
import random
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from app.chaos.faults import FaultType, InjectedFault
from app.core.config import get_settings
from app.schemas.contracts import RunEvent

logger = logging.getLogger("agentready.chaos_proxy")


class ChaosProxy:
    """
    Deterministic proxy that intercepts and mutates checkout and webhook traffic.
    Guarantees that runs with the same seed generate bit-for-bit identical fault traces.
    """

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.rng = random.Random(seed)
        self.settings = get_settings()
        self.semaphore = asyncio.Semaphore(self.settings.MAX_CONCURRENT_BUYERS)
        self.injected_faults: List[InjectedFault] = []

    def reset_seed(self, seed: int) -> None:
        """Resets the pseudorandom generator seed for deterministic replay."""
        self.seed = seed
        self.rng = random.Random(seed)
        self.injected_faults.clear()

    def inject_fault(
        self,
        fault_type: FaultType,
        lane: int,
        persona_id: str,
        payload: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], InjectedFault]:
        """
        Applies a deterministic fault mutation to an outbound payload.
        Records the fault in the audit log and returns (mutated_payload, fault_record).
        """
        mutated = copy.deepcopy(payload)
        fault_id = f"fault_{self.seed}_{lane}_{len(self.injected_faults) + 1}"
        params: Dict[str, Any] = {}
        desc = ""

        if fault_type == FaultType.MUTATE_PRICE:
            # Deterministically choose low price (e.g. $1.50 or $0.99)
            tampered_price = round(self.rng.choice([1.50, 0.99, 2.00]), 2)
            mutated["client_price"] = tampered_price
            if "items" in mutated and len(mutated["items"]) > 0:
                mutated["items"][0]["price"] = tampered_price
            params = {"original_price": payload.get("client_price"), "tampered_price": tampered_price}
            desc = f"Mutated price from {payload.get('client_price')} to ${tampered_price:.2f}"

        elif fault_type == FaultType.MUTATE_QUANTITY:
            # Prompt injection quantity mutation (e.g. 1 -> 5 units)
            injected_qty = self.rng.choice([5, 10])
            if "items" in mutated and len(mutated["items"]) > 0:
                mutated["items"][0]["quantity"] = injected_qty
            params = {"tampered_quantity": injected_qty}
            desc = f"Mutated quantity from 1 to {injected_qty} units"

        elif fault_type == FaultType.STRIP_IDEMPOTENCY_KEY:
            # Drops idempotency headers
            mutated.pop("idempotency_key", None)
            mutated.pop("PayPal-Request-Id", None)
            desc = "Stripped idempotency key / PayPal-Request-Id header"

        elif fault_type == FaultType.FORGE_WEBHOOK_SIGNATURE:
            # Replaces authentic signature with invalid forged token
            mutated["PAYPAL-TRANSMISSION-SIG"] = "forged_signature_invalid"
            params = {"signature": "forged_signature_invalid"}
            desc = "Forged PayPal webhook signature headers"

        elif fault_type == FaultType.AMBIGUOUS_VARIANTS:
            # Strips required variant choices (size/color)
            mutated["selected_variants"] = None
            desc = "Stripped required variant selections (size/color)"

        elif fault_type == FaultType.DROP_POST_CAPTURE_RESPONSE:
            # Simulates network disconnect after payment completion
            mutated["simulate_dropped_connection"] = True
            desc = "Simulated connection drop immediately following PayPal payment capture"

        fault = InjectedFault(
            fault_id=fault_id,
            fault_type=fault_type,
            lane=lane,
            persona_id=persona_id,
            description=desc,
            parameters=params,
        )
        self.injected_faults.append(fault)
        logger.info("ChaosProxy [%s]: %s on Lane %d (%s)", fault_id, desc, lane, persona_id)
        return mutated, fault

    def generate_fault_plan(self) -> List[InjectedFault]:
        """
        Generates deterministic fault plan for all 9 lanes based on the seed.
        """
        plan: List[InjectedFault] = []
        # Lane 1: The Retrier
        plan.append(InjectedFault(
            fault_id=f"plan_{self.seed}_l1",
            fault_type=FaultType.DUPLICATE_CHECKOUT_REQUEST,
            lane=1,
            persona_id="the_retrier",
            description="Rapid duplicate capture request without idempotency delay",
            parameters={"retry_count": 2},
        ))
        # Lane 2: The Tamperer
        p2_price = round(self.rng.choice([1.50, 0.99]), 2)
        plan.append(InjectedFault(
            fault_id=f"plan_{self.seed}_l2",
            fault_type=FaultType.MUTATE_PRICE,
            lane=2,
            persona_id="the_tamperer",
            description=f"Client-side price tampering to ${p2_price:.2f}",
            parameters={"tampered_price": p2_price},
        ))
        # Lane 4: The Webhook Skeptic
        plan.append(InjectedFault(
            fault_id=f"plan_{self.seed}_l4",
            fault_type=FaultType.FORGE_WEBHOOK_SIGNATURE,
            lane=4,
            persona_id="the_webhook_skeptic",
            description="Inject forged webhook without valid PayPal signature",
        ))
        # Lane 6: The Ghost Order
        plan.append(InjectedFault(
            fault_id=f"plan_{self.seed}_l6",
            fault_type=FaultType.DROP_POST_CAPTURE_RESPONSE,
            lane=6,
            persona_id="the_ghost_order",
            description="Drop store fulfillment database insert after PayPal capture",
        ))
        # Lane 8: The Misreader
        plan.append(InjectedFault(
            fault_id=f"plan_{self.seed}_l8",
            fault_type=FaultType.AMBIGUOUS_VARIANTS,
            lane=8,
            persona_id="the_misreader",
            description="Omit size and color attributes on multi-variant item",
        ))
        # Lane 9: The Content Trap
        plan.append(InjectedFault(
            fault_id=f"plan_{self.seed}_l9",
            fault_type=FaultType.MUTATE_QUANTITY,
            lane=9,
            persona_id="the_content_trap",
            description="Prompt injection in item description alters quantity to 5",
            parameters={"tampered_quantity": 5},
        ))
        return plan

