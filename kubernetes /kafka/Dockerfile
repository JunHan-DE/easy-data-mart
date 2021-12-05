# Dockerfile for Kafka S3 Sink Connector
FROM bitnami/kafka:latest

RUN mkdir -p /opt/bitnami/kafka/plugins && \
    cd /opt/bitnami/kafka/plugins && \
    curl --remote-name --location --silent https://search.maven.org/remotecontent?filepath=org/mongodb/kafka/mongo-kafka-connect/1.2.0/mongo-kafka-connect-1.2.0-all.jar

CMD /opt/bitnami/kafka/bin/connect-distributed.sh /opt/bitnami/kafka/config/connect-distributed.properties /opt/bitnami/kafka/config/mongo.properties
