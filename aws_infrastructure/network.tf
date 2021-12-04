
data "external" "myipaddr_local" {
  program = ["bash", "-c", "curl -s 'https://api.ipify.org?format=json'"]
}

resource "aws_security_group" "kub-master-sg" {
  name        = "kub-master-sg"
  description = "Security Group for Kubernetes Master"
  #vpc_id                 = var.vpc_id
  revoke_rules_on_delete = true

  tags = merge(
    {
      "Name" = "kub-master-sg"
    },
    var.default_tags,
  )
}

#security group kubernetes nodes
resource "aws_security_group" "kub-node-sg" {
  name        = "kub-node-sg"
  description = "Security Group for Kubernetes Node Servers"
  #vpc_id                 = var.vpc_id
  revoke_rules_on_delete = true

  tags = merge(
    {
      "Name" = "kub-node-sg"
    },
    var.default_tags,
  )
}

#security Group Rules for Kubernetes Cluster
resource "aws_security_group_rule" "computed_ingress_rule1" {

  security_group_id = aws_security_group.kub-master-sg.id
  type              = "ingress"

  cidr_blocks      = [join("", [data.external.myipaddr_local.result.ip, "/32"])]
  ipv6_cidr_blocks = []
  prefix_list_ids  = []
  description      = "Ingress from Local Computer"

  from_port = 0
  to_port   = 0
  protocol  = "all"
}

resource "aws_security_group_rule" "computed_ingress_rule2" {

  security_group_id = aws_security_group.kub-node-sg.id
  type              = "ingress"

  cidr_blocks      = [join("", [data.external.myipaddr_local.result.ip, "/32"])]
  ipv6_cidr_blocks = []
  prefix_list_ids  = []
  description      = "Ingress from Local Computer"

  from_port = 0
  to_port   = 0
  protocol  = "all"
}

resource "aws_security_group_rule" "computed_egress_rule1" {

  security_group_id = aws_security_group.kub-master-sg.id
  type              = "egress"

  cidr_blocks      = ["0.0.0.0/0"]
  ipv6_cidr_blocks = []
  prefix_list_ids  = []
  description      = "egress"

  from_port = 0
  to_port   = 0
  protocol  = "all"
}

resource "aws_security_group_rule" "computed_egress_rule2" {

  security_group_id = aws_security_group.kub-node-sg.id
  type              = "egress"

  cidr_blocks      = ["0.0.0.0/0"]
  ipv6_cidr_blocks = []
  prefix_list_ids  = []
  description      = "egress"

  from_port = 0
  to_port   = 0
  protocol  = "all"
}

