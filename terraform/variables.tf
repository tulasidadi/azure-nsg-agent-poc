variable "rules_file" {
  description = "Path to NSG rules JSON file"
  type        = string
  default     = "../nsg-rules/dev/web-nsg.json"
}

variable "nsg_name" {
  description = "Name of the Network Security Group"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the Azure resource group"
  type        = string
}
