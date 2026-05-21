"""Basic policy guardrails for NSG rules."""

import json
import sys
from pathlib import Path

DENIED_INBOUND_PORTS_FROM_INTERNET = {"22", "3389"}
VALID_DIRECTIONS = {"Inbound", "Outbound"}
VALID_ACCESS = {"Allow", "Deny"}
VALID_PROTOCOLS = {"Tcp", "Udp", "Icmp", "Esp", "Ah", "*"}


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    data = json.loads(path.read_text())
    rules = data.get("rules", [])
    priorities = set()

    for index, rule in enumerate(rules, start=1):
        prefix = f"{path}: rule #{index} ({rule.get('rule_name', 'unknown')})"

        if rule.get("direction") not in VALID_DIRECTIONS:
            errors.append(f"{prefix}: invalid direction")
        if rule.get("access") not in VALID_ACCESS:
            errors.append(f"{prefix}: invalid access")
        if rule.get("protocol") not in VALID_PROTOCOLS:
            errors.append(f"{prefix}: invalid protocol")

        priority = rule.get("priority")
        if not isinstance(priority, int) or priority < 100 or priority > 4096:
            errors.append(f"{prefix}: priority must be integer from 100 to 4096")
        elif priority in priorities:
            errors.append(f"{prefix}: duplicate priority {priority}")
        priorities.add(priority)

        if (
            rule.get("direction") == "Inbound"
            and rule.get("access") == "Allow"
            and rule.get("source_address_prefix") == "Internet"
            and str(rule.get("destination_port_range")) in DENIED_INBOUND_PORTS_FROM_INTERNET
        ):
            errors.append(
                f"{prefix}: policy blocks inbound Internet access to port {rule.get('destination_port_range')}"
            )

    return errors


def main() -> None:
    files = list(Path("nsg-rules").glob("**/*.json"))
    if not files:
        print("No rule files found")
        return

    errors: list[str] = []
    for path in files:
        errors.extend(validate_file(path))

    if errors:
        print("NSG policy validation failed:")
        for error in errors:
            print("-", error)
        sys.exit(1)

    print("NSG policy validation passed")


if __name__ == "__main__":
    main()
