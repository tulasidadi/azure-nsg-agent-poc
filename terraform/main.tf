locals {
  rules_data = jsondecode(file(var.rules_file))
  rules      = { for rule in local.rules_data.rules : rule.rule_name => rule }
}

data "azurerm_network_security_group" "target" {
  name                = var.nsg_name
  resource_group_name = var.resource_group_name
}

resource "azurerm_network_security_rule" "rules" {
  for_each = local.rules

  name                        = each.value.rule_name
  priority                    = each.value.priority
  direction                   = each.value.direction
  access                      = each.value.access
  protocol                    = each.value.protocol
  source_port_range           = each.value.source_port_range
  destination_port_range      = each.value.destination_port_range
  source_address_prefix       = each.value.source_address_prefix
  destination_address_prefix  = each.value.destination_address_prefix
  description                 = each.value.description

  resource_group_name         = var.resource_group_name
  network_security_group_name = data.azurerm_network_security_group.target.name
}
