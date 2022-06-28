
variable "default_tags" {
  default = {
    "Owner"   = "jun",
    "Project" = "amazon-data-pipeline"
  }
  description = "Additional resource tags"
  type        = map(string)
}
variable "aws_public_key_name" {}
variable "path_to_public_key" {}

variable "master_root_ebs_size" {}
variable "master_instance_type" {}
variable "node_instance_type" {}
variable "node_root_ebs_size" {}
