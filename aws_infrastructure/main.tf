terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 0.14.9"
}

provider "aws" {
  region  = "ap-northeast-2"
}

data "aws_ami" "ubuntu_base" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}

resource "aws_key_pair" "amazon_data" {
  key_name    = "amazon_data"
  public_key  = file(var.path_to_public_key)
}


resource "aws_instance" "kubernetes-master" {
  ami                    = data.aws_ami.ubuntu_base.image_id
  instance_type          = var.master_instance_type
  key_name               = aws_key_pair.amazon_data.key_name
  vpc_security_group_ids = [aws_security_group.kub-master-sg.id]

  root_block_device {
    volume_size = var.master_root_ebs_size
  }

  tags = merge(
    var.default_tags,
    {
      "Name" = "Kubernetes-Master"
    }
  )
}

resource "aws_instance" "kubernetes-node" {
  count                  = 2
  ami                    = data.aws_ami.ubuntu_base.image_id
  instance_type          = var.node_instance_type
  key_name               = aws_key_pair.amazon_data.key_name
  vpc_security_group_ids = [aws_security_group.kub-node-sg.id]

  root_block_device {
    volume_size = var.node_root_ebs_size
  }

  tags = merge(
    var.default_tags,
    {
      "Name" = "Kubernetes-node-${count.index + 1}"
    }
  )
}
