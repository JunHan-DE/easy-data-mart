# Handy Data Mesh

### End-to-end data system that a client can configure data pipeline as well as a data engineer can handle the governance


## Description


As company grows, data team has increased the risk of losing the domain values as they ETL various service domain data.

I implemented a data mesh that provides data ownership to each data issuer 
while data team can take advantage of the data management with Kafka.

## Architecture 

![data mesh drawio-4](https://user-images.githubusercontent.com/74975256/176082480-84112fbc-fab2-40b1-b4f9-fd0caf260c2c.png)


Users can request their query for data transformation via POST. 
POST includes source/target database information.

<img width="831" alt="dkre" src="https://user-images.githubusercontent.com/74975256/176082569-b31a409d-abf7-429d-bc9c-edd24e388549.png">


## How to Use

### 1. deploy Kubernetes Cluster on EC2

* create `variables.tfvars` to contain arguments in `variables.tf`
    ```
    cd aws_infrastructure
    terraform init
    terraform apply -var-file variables.tfvars
    ```

* once EC2 clusters are deployed on AWS, init the kubernetes
    ```
    kubeadm init --apiserver-advertise-address=0.0.0.0 --pod-network-cidr=192.168.0.0/16 
    ```

### 2. deploy Kafka, Ksql, and REST API client server

1. build & push docker image for each component
    ```
   docker build . -t YOUR_REPO/TAG; docker push YOUR_REPO/TAG 
   ```
2. deploy onto Kubernetes
    ```
   kubectl apply -f YAML_FILE
   ```

### 3. Run POST request according to the Swagger UI
* Go to see the document
    ```
    http://127.0.0.1:8000/docs
    ```

## TODO


* Currently data mesh supports PostgreSQL, S3, and Elastic Search. more and more database
  need to be supported.
* Support complicated transformation logic. 
