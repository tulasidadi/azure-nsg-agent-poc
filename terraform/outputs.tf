output "created_rules" {
  value = [for r in azurerm_network_security_rule.rules : r.name]
}
