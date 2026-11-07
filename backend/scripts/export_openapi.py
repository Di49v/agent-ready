#!/usr/bin/env python3
"""
AgentReady Lab — OpenAPI Specification Exporter.
Exports the OpenAPI 3.1 specification from FastAPI into `openapi/openapi.json`.
Used for APIMatic SDK generation, MCP tool contract verification, and Postman collections.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

# Ensure backend root is in Python path
BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402


def export_openapi() -> Path:
    """Exports OpenAPI schema to openapi/openapi.json."""
    repo_root = BACKEND_ROOT.parent
    output_dir = repo_root / "openapi"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "openapi.json"

    schema = app.openapi()

    # Calculate summary metrics
    paths = schema.get("paths", {})
    operation_ids: list[str] = []
    for path_item in paths.values():
        for method, op in path_item.items():
            if isinstance(op, dict) and "operationId" in op:
                operation_ids.append(op["operationId"])

    schemas = schema.get("components", {}).get("schemas", {})

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    print("=================================================================")
    print("           AGENTREADY LAB — OPENAPI 3.1 SPEC EXPORTED            ")
    print("=================================================================")
    print(f"File Path:       {output_file}")
    print(f"OpenAPI Version: {schema.get('openapi')}")
    print(f"API Title:       {schema.get('info', {}).get('title')} (v{schema.get('info', {}).get('version')})")
    print(f"Total Paths:     {len(paths)}")
    print(f"Operation IDs:   {len(operation_ids)} ({', '.join(sorted(operation_ids)[:6])}...)")
    print(f"Schema Models:   {len(schemas)}")
    print("=================================================================")
    print("Ready for APIMatic CLI / Studio SDK generation.")
    return output_file


if __name__ == "__main__":
    export_openapi()

