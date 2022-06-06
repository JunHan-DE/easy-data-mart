# Dockerfile for test container of ksql server
FROM debian:latest

USER root

RUN apt update && \
    apt install -y software-properties-common curl gnupg default-jdk

# Import the public key
RUN curl -sq http://ksqldb-packages.s3.amazonaws.com/deb/0.26/archive.key | apt-key add -

# Add the ksqlDB apt repository & install the package
RUN add-apt-repository "deb http://ksqldb-packages.s3.amazonaws.com/deb/0.26 stable main" && \
    apt update && \
    apt install confluent-ksqldb

ENV KSQL_LISTENERS=http://0.0.0.0:8088 \
    KSQL_BOOTSTRAP_SERVERS=jun-kafka-0.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092,jun-kafka-1.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092,jun-kafka-2.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092 \
    KSQL_KSQL_LOGGING_PROCESSING_STREAM_AUTO_CREATE=true \
    KSQL_KSQL_LOGGING_PROCESSING_TOPIC_AUTO_CREATE=true

WORKDIR /etc/ksqldb

RUN sed 's/bootstrap.servers=localhost:9092/bootstrap.servers=jun-kafka-0.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092,jun-kafka-1.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092,jun-kafka-2.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092/g' ksql-server.properties && \
    sed 's/\# ksql.connect.worker.config/ksql.connect.worker.config/g' ksql-server.properties