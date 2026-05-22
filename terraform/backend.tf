terraform {
  backend "azurerm" {
    resource_group_name  = "dev-rg"
    storage_account_name = "devnsgstate"
    container_name       = "tfstate"
    key                  = "nsg.tfstate"
  }
}
