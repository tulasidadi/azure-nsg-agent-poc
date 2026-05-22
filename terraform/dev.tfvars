# Azure subscription and resource group configuration
resource_group_name = "my-resource-group"
location            = "eastus"
environment         = "dev"

# NSG configuration
nsg_name = "dev-web-nsg"

# NSG rules file path
rules_file = "../nsg-rules/dev/web-nsg.json"
