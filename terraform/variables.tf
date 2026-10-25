variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "project_name" {
  type    = string
  default = "nexvion"
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "public_key_path" {
  type    = string
  default = "~/.ssh/id_ed25519.pub"
}

variable "ssh_cidr" {
  type        = string
  description = "IP range allowed to SSH. Use your own IP/32 for better security."
  default     = "0.0.0.0/0"
}
