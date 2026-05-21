variable "resource_group_name" {
  type        = string
  description = "Azure resource group containing the NSG."
}

variable "nsg_name" {
  type        = string
  description = "Target Azure Network Security Group name."
}

variable "rules_file" {
  type        = string
  description = "Path to JSON rules file."
}
