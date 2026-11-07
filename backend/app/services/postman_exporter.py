"""
AgentReady Lab — Postman Collection v2.1.0 Exporter (Task 7.1 / Section B3.9 & Deliverables).
Exports reproduction test requests for failed dual-ledger findings,
enabling external developers and QA engineers to reproduce edge cases in Postman.
"""
import json
import uuid
from typing import Any, Dict, List, Optional

from app.schemas.contracts import FindingDetail, RunSummary


class PostmanCollectionExporter:
    """
    Serializes a crash-test run and its failed findings into a standard
    Postman Collection v2.1.0 JSON format.
    """

    POSTMAN_SCHEMA_URL = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"

    def generate_collection(
        self,
        summary: RunSummary,
        findings: List[FindingDetail],
    ) -> Dict[str, Any]:
        """Generates Postman Collection v2.1.0 dictionary."""
        collection_id = str(uuid.uuid4())
        run_id = summary.id
        target = summary.target
        score = summary.score if summary.score is not None else "N/A"

        collection: Dict[str, Any] = {
            "info": {
                "_postman_id": collection_id,
                "name": f"AgentReady Lab — Crash Test Reproduction ({target} · {run_id})",
                "description": (
                    f"# AgentReady Lab Reproduction Suite\n\n"
                    f"- **Run ID:** `{run_id}`\n"
                    f"- **Target Store:** `{target}`\n"
                    f"- **Score:** `{score}/100`\n"
                    f"- **Total Findings:** {len(findings)}\n\n"
                    f"Use this collection to reproduce detected race conditions and compliance violations directly in Postman."
                ),
                "schema": self.POSTMAN_SCHEMA_URL,
            },
            "variable": [
                {
                    "key": "baseUrl",
                    "value": "http://localhost:8000",
                    "type": "string",
                    "description": "AgentReady Lab Backend API URL",
                },
                {
                    "key": "targetBaseUrl",
                    "value": "http://localhost:8000",
                    "type": "string",
                    "description": "Target Store base URL",
                },
                {
                    "key": "paypalSandboxUrl",
                    "value": "https://api-m.sandbox.paypal.com",
                    "type": "string",
                    "description": "Hard-pinned PayPal Sandbox API URL",
                },
                {
                    "key": "runId",
                    "value": run_id,
                    "type": "string",
                    "description": "Current Crash Test Run ID",
                },
            ],
            "item": [],
        }

        # 1. Baseline Vitality & Health Request
        collection["item"].append({
            "name": "0. Vitality & Sandbox Lock Check",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{baseUrl}}/healthz",
                    "host": ["{{baseUrl}}"],
                    "path": ["healthz"],
                },
                "description": "Verifies that the backend is alive and locked to the PayPal Sandbox.",
            },
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status is 200', function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "pm.test('PayPal Sandbox Lock Confirmed', function () {",
                            "    var json = pm.response.json();",
                            "    pm.expect(json.paypal_base_url).to.include('sandbox.paypal.com');",
                            "});",
                        ],
                        "type": "text/javascript",
                    },
                }
            ],
        })

        # 2. Reproduction requests for each finding
        for idx, finding in enumerate(findings, start=1):
            item = self._build_finding_request(idx, finding, target)
            collection["item"].append(item)

        # 3. Signed Probe Ledger Endpoint Request
        collection["item"].append({
            "name": "Audit. Store Internal Ledger Probe (/_lab/ledger)",
            "request": {
                "method": "GET",
                "header": [
                    {
                        "key": "X-Lab-Signature",
                        "value": "signed_probe_shared_secret",
                        "type": "text",
                    }
                ],
                "url": {
                    "raw": "{{targetBaseUrl}}/_lab/ledger",
                    "host": ["{{targetBaseUrl}}"],
                    "path": ["_lab", "ledger"],
                },
                "description": "Reads merchant store internal orders and claimed payments for dual-ledger audit.",
            },
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status is 200', function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "pm.test('Ledger returns orders array', function () {",
                            "    var json = pm.response.json();",
                            "    pm.expect(json).to.have.property('orders');",
                            "});",
                        ],
                        "type": "text/javascript",
                    },
                }
            ],
        })

        return collection

    def generate_collection_json(
        self,
        summary: RunSummary,
        findings: List[FindingDetail],
        indent: int = 2,
    ) -> str:
        """Serializes Postman Collection dictionary to JSON string."""
        collection_dict = self.generate_collection(summary, findings)
        return json.dumps(collection_dict, indent=indent)

    def _build_finding_request(
        self,
        index: int,
        finding: FindingDetail,
        target: str,
    ) -> Dict[str, Any]:
        """Maps an individual FindingDetail into a reproduction Postman request item."""
        title = finding.title
        rule_num = finding.rule_number
        evidence_str = ", ".join(finding.evidence_ids) if finding.evidence_ids else "N/A"

        # Determine payload & method based on rule number
        if rule_num == 1:
            # Rule 1: Pay Once / Idempotency retry
            method = "POST"
            path = ["v1", "arena", "run"]
            body_json = {
                "prompt": "Buy running shoes size 8 under $80",
                "target": target,
                "chaos_switches": ["drop_retry"],
            }
            test_script = [
                f"// Reproduction for Rule 1: {title}",
                "pm.test('Response received from target', function () {",
                "    pm.expect(pm.response.code).to.be.oneOf([200, 201, 202]);",
                "});",
                "// Inspect dual-ledger captures on PayPal Sandbox for evidence: " + evidence_str,
            ]
        elif rule_num == 2:
            # Rule 2: Right Amount / Price Tampering
            method = "POST"
            path = ["v1", "arena", "run"]
            body_json = {
                "prompt": "Buy running shoes size 8 under $80",
                "target": target,
                "chaos_switches": ["tamper_price"],
            }
            test_script = [
                f"// Reproduction for Rule 2: {title}",
                "pm.test('Response indicates price check or acceptance', function () {",
                "    pm.expect(pm.response.code).to.be.oneOf([200, 202, 409]);",
                "});",
            ]
        elif rule_num == 5:
            # Rule 5: Webhook Signature Verification
            method = "POST"
            path = ["webhooks", "paypal"]
            body_json = {
                "event_type": "PAYMENT.CAPTURE.COMPLETED",
                "resource": {
                    "id": finding.evidence_ids[0] if finding.evidence_ids else "CAP-FORGED-001",
                    "amount": {"value": "120.00", "currency_code": "USD"},
                },
            }
            test_script = [
                f"// Reproduction for Rule 5: {title}",
                "pm.test('Webhook processing outcome', function () {",
                "    pm.expect(pm.response.code).to.be.oneOf([200, 401]);",
                "});",
            ]
        else:
            # General fallback reproduction
            method = "GET"
            path = ["v1", "runs", "{{runId}}", "findings"]
            body_json = None
            test_script = [
                f"// Finding {index}: {title}",
                "pm.test('Findings list returns 200', function () {",
                "    pm.response.to.have.status(200);",
                "});",
            ]

        request_dict: Dict[str, Any] = {
            "method": method,
            "header": [
                {
                    "key": "Content-Type",
                    "value": "application/json",
                    "type": "text",
                }
            ],
            "url": {
                "raw": f"{{{{baseUrl}}}}/{'/'.join(path)}",
                "host": ["{{baseUrl}}"],
                "path": path,
            },
            "description": (
                f"**Rule {rule_num} Finding:** {title}\n\n"
                f"- **Severity:** `{finding.severity}`\n"
                f"- **PayPal Evidence IDs:** `{evidence_str}`\n\n"
                f"**Explanation:**\n{finding.explanation or finding.description or 'No explanation provided.'}"
            ),
        }

        if body_json is not None:
            request_dict["body"] = {
                "mode": "raw",
                "raw": json.dumps(body_json, indent=2),
                "options": {
                    "raw": {
                        "language": "json",
                    }
                },
            }

        return {
            "name": f"{index}. [{finding.severity}] {title}",
            "request": request_dict,
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "exec": test_script,
                        "type": "text/javascript",
                    },
                }
            ],
        }


_postman_exporter: Optional[PostmanCollectionExporter] = None


def get_postman_exporter() -> PostmanCollectionExporter:
    """Returns singleton instance of PostmanCollectionExporter."""
    global _postman_exporter
    if _postman_exporter is None:
        _postman_exporter = PostmanCollectionExporter()
    return _postman_exporter

