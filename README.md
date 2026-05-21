# Azure NSG Agent POC

This POC takes a plain-English NSG request, converts it into a structured NSG rule JSON file, commits it to GitHub, and GitHub Actions deploys the rule to Azure using Terraform.

## Flow

User request -> AI/Rule Agent -> `nsg-rules/<env>/<nsg>.json` -> Pull Request -> GitHub Actions validate/plan -> approval -> Terraform apply -> Azure NSG updated

## Prerequisites

- Azure subscription
- Existing Resource Group and NSG
- GitHub repository
- GitHub Actions OIDC configured with Azure
- Terraform installed locally only if testing locally
- Python 3.11+

## Azure/GitHub secrets and variables

Use GitHub repository Variables:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP`
- `AZURE_NSG_NAME`
- `AZURE_LOCATION`

Use OIDC where possible instead of client secrets.

## Run locally

```bash
cd azure-nsg-agent-poc
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r agent/requirements.txt
python agent/nsg_agent.py --request "Allow inbound HTTPS from Internet to WebSubnet on port 443 in dev" --env dev --nsg-name web-nsg
```

This creates:

```text
nsg-rules/dev/web-nsg.json
```

## Deploy through GitHub Actions

Commit the generated JSON and open a PR. GitHub Actions will validate and plan. After merge to main, GitHub Actions applies Terraform to Azure.

