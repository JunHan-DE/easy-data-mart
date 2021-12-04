# local Adddress
output "myipaddr_local" {
  value = data.external.myipaddr_local.result.ip
}

#Kubernetes master instance
output "Kubernetes_master_instance_id" {
  value = aws_instance.kubernetes-master.id
}

output "Kubernetes_master_instance_public_ip" {
  value = aws_instance.kubernetes-master.public_ip
}

# Kubernetes nodes
output "kubernetes_nodes" {
  value = {
    "Id"        = aws_instance.kubernetes-node.*.id,
    "Public_IP" = aws_instance.kubernetes-node.*.public_ip
  }

}