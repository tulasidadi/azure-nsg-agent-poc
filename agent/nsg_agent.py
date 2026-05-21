"""
Simple Azure NSG Agent POC.

This version is intentionally safe and deterministic for a client POC:
- It accepts a plain-English request.
- It extracts common fields using simple rules.
- It writes a JSON rule file consumed by Terraform.

Later you can replace parse_request() with an LLM call.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator


Direction = Literal["Inbound", "Outbound"]
Access = Literal["Allow", "Deny"]
Protocol = Literal["Tcp", "Udp", "Icmp", "Esp", "Ah", "*"]


class NSGRule(BaseModel):
    rule_name: str
    direction: Direction
    priority: int = Field(ge=100, le=4096)
    access: Access
    protocol: Protocol
    source_address_prefix: str
    source_port_range: str
    destination_address_prefix: str
    destination_port_range: str
    description: str

    @field_validator("rule_name")
    @classmethod
    def valid_rule_name(cls, value: str) -> str:
        value = value.strip().replace(" ", "-")
        value = re.sub(r"[^a-zA-Z0-9_.-]", "-", value)
        return value[:80]


def normalize_port(text: str) -> str:
    port_match = re.search(r"port\s+(\d+)", text, flags=re.IGNORECASE)
    if port_match:
        return port_match.group(1)

    common_ports = {
        "https": "443",
        "http": "80",
        "ssh": "22",
        "rdp": "3389",
        "sql": "1433",
        "postgres": "5432",
        "mysql": "3306",
    }
    lower = text.lower()
    for name, port in common_ports.items():
        if name in lower:
            return port
    return "*"


def parse_request(request: str, priority: int) -> NSGRule:
    """Parse a simple NSG request. Replace with LLM extraction later."""
    lower = request.lower()

    direction: Direction = "Outbound" if "outbound" in lower else "Inbound"
    access: Access = "Deny" if "deny" in lower or "block" in lower else "Allow"
    protocol: Protocol = "Tcp"

    destination_port = normalize_port(request)

    source = "Internet" if "internet" in lower else "*"
    destination = "*"

    # Basic subnet/service tag detection for demo
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]*", request)
    for word in words:
        if word.lower().endswith("subnet"):
            if direction == "Inbound":
                destination = word
            else:
                source = word

    action = access
    port_label = destination_port if destination_port != "*" else "AnyPort"
    rule_name = f"{action}-{direction}-{source}-to-{destination}-Port-{port_label}"

    return NSGRule(
        rule_name=rule_name,
        direction=direction,
        priority=priority,
        access=access,
        protocol=protocol,
        source_address_prefix=source,
        source_port_range="*",
        destination_address_prefix=destination,
        destination_port_range=destination_port,
        description=request,
    )


def load_existing_rules(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "rules" in data:
        return data["rules"]
    if isinstance(data, list):
        return data
    raise ValueError(f"Unsupported rule file format: {path}")


def save_rules(path: Path, rules: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump({"rules": rules}, f, indent=2)
        f.write("\n")


def upsert_rule(rules: list[dict], new_rule: NSGRule) -> list[dict]:
    output = [r for r in rules if r.get("rule_name") != new_rule.rule_name]
    priorities = {r.get("priority") for r in output}
    rule_dict = new_rule.model_dump()
    while rule_dict["priority"] in priorities:
        rule_dict["priority"] += 10
    output.append(rule_dict)
    return sorted(output, key=lambda r: r["priority"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Azure NSG rule JSON from request")
    parser.add_argument("--request", required=True, help="Plain-English NSG rule request")
    parser.add_argument("--env", default="dev", choices=["dev", "test", "prod"], help="Environment")
    parser.add_argument("--nsg-name", required=True, help="Target NSG name")
    parser.add_argument("--priority", type=int, default=100, help="Starting priority")
    args = parser.parse_args()

    rule = parse_request(args.request, args.priority)
    output_file = Path("nsg-rules") / args.env / f"{args.nsg_name}.json"
    rules = load_existing_rules(output_file)
    rules = upsert_rule(rules, rule)
    save_rules(output_file, rules)

    print("Generated/updated rule file:", output_file)
    print(json.dumps(rule.model_dump(), indent=2))


if __name__ == "__main__":
    main()
