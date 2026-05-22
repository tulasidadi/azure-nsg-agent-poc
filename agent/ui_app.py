"""Simple Streamlit UI for Azure NSG Agent POC.

Run from the project root:
    streamlit run agent/ui_app.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

# Allow importing nsg_agent.py when Streamlit runs from project root.
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from nsg_agent import load_existing_rules, parse_request, save_rules, upsert_rule  # noqa: E402


st.set_page_config(page_title="Azure NSG Agent", page_icon="🛡️", layout="centered")

st.title("🛡️ Azure NSG Agent POC")
st.write("Enter a plain-English NSG request. The agent converts it into a Terraform-ready JSON rule file.")

with st.form("nsg_request_form"):
    request = st.text_area(
        "NSG request",
        value="Allow inbound HTTPS from Internet to WebSubnet on port 443 in dev",
        height=120,
        help="Example: Allow inbound HTTPS from Internet to WebSubnet on port 443 in dev",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        env = st.selectbox("Environment", ["dev", "test", "prod"], index=0)
    with col2:
        nsg_name = st.text_input("NSG name", value="web-nsg")
    with col3:
        priority = st.number_input("Starting priority", min_value=100, max_value=4096, value=100, step=10)

    submitted = st.form_submit_button("Send to Agent")

if submitted:
    if not request.strip():
        st.error("Please enter an NSG request.")
    elif not nsg_name.strip():
        st.error("Please enter an NSG name.")
    else:
        try:
            rule = parse_request(request.strip(), int(priority))
            output_file = PROJECT_ROOT / "nsg-rules" / env / f"{nsg_name.strip()}.json"
            existing_rules = load_existing_rules(output_file)
            updated_rules = upsert_rule(existing_rules, rule)
            save_rules(output_file, updated_rules)

            st.success(f"Rule generated and saved to: {output_file.relative_to(PROJECT_ROOT)}")

            st.subheader("Generated rule")
            st.json(rule.model_dump())

            st.subheader("Complete rule file")
            st.code(json.dumps({"rules": updated_rules}, indent=2), language="json")
        except Exception as exc:  # Keep UI friendly for POC/demo use.
            st.error(f"Agent failed: {exc}")

st.divider()
st.caption("Next step in production: replace parse_request() with an LLM extraction call and keep policy validation before Terraform apply.")
