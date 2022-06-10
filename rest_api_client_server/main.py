import asyncio
import typing

from confluent_kafka import KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
from fastapi import FastAPI, HTTPException
from time import time
from ksql import KSQLAPI

import uvicorn
from app.utils.kafka.aio_producer import AIOProducer
from app.sql.ksql import create_stream_sql
from app.common.variables import (
    EtlConfig,
    Item,
)
from app.common.config import conf

app = FastAPI()
aio_producer: typing.Union[AIOProducer, None] = None
admin_client: typing.Union[AdminClient, None] = None
ksql_client: typing.Union[KSQLAPI, None] = None
conf = conf()

# BOOTSTRAP_SERVERS = {
#     "bootstrap.servers": "jun-kafka-0.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092,"
#                          "jun-kafka-1.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092,"
#                          "jun-kafka-2.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092"
# }
BOOTSTRAP_SERVERS = {
    "bootstrap.servers": "0.0.0.0:9092"
}
KSQL_SERVER = "http://0.0.0.0:8088"


@app.on_event("startup")
async def startup_event():

    global aio_producer, admin_client, ksql_client, conf
    aio_producer = AIOProducer(BOOTSTRAP_SERVERS)
    admin_client = AdminClient(BOOTSTRAP_SERVERS)
    ksql_client = KSQLAPI(KSQL_SERVER)


@app.on_event("shutdown")
def shutdown_event():
    aio_producer.close()


@app.get("/health/")
async def check_server_health_status() -> dict:
    return {"status": 200}


@app.post("/etl")
async def run_etl_code(config: EtlConfig):

    topic = (
        config.source_table_name
        if config.source_table_name == config.target_table_name
        else f"jdbc_{config.source_table_name}_to_{config.target_table_name}"
    )

    # 1. create topic
    topics = [NewTopic(topic=topic, num_partitions=3, replication_factor=2)]
    admin_client.create_topics(topics)

    # 2. add streams
    # ksql_client.create_stream(
    #     table_name=topic,
    #     columns_type=["is_success VARCHAR"],
    #     topic=topic,
    # )

    ksql_client.ksql("""CREATE STREAM JDBC_CUSTOMERS_TO_CUSTOMER (IS_SUCCESS STRING) WITH (KAFKA_TOPIC='jdbc_customers_to_customer', PARTITIONS=2, REPLICAS=1, VALUE_FORMAT='JSON')""")
    # 2. add source kafka connect
    # ksql_client.ksql(f"""
    #     CREATE SOURCE CONNECTOR IF NOT EXISTS `{topic}-jdbc-connector` WITH(
    #     "connector.class"='io.confluent.connect.jdbc.JdbcSourceConnector',
    #     "connection.url"='jdbc:postgresql://{config.source_db_host}:{config.source_db_port}/{config.source_db_name}',
    #     "mode"='bulk',
    #     "topic.prefix"='jdbc-',
    #     "table.whitelist"='users',
    #     "key"='username');
    # """)
    ksql_client.ksql(f"""CREATE SOURCE CONNECTOR `demo-source-connector` WITH ('connector.class'               = 'io.debezium.connector.postgresql.PostgresConnector',
  'database.dbname'               = 'demo',
  'database.hostname'             = 'postgres',
  'database.password'             = 'postgres',
  'database.port'                 = '5432',
  'database.server.name'          = 'workshop_pg',
  'database.user'                 = 'postgres',
  'plugin.name'                   = 'pgoutput',
  'snapshot.mode'                 = 'always',
  'table.whitelist'               = 'public.customers,public.companies',
  'transforms'                    = 'extractKey,extractValue',
  'transforms.extractKey.field'   = 'id',
  'transforms.extractKey.type'    = 'org.apache.kafka.connect.transforms.ExtractField$Key',
  'transforms.extractValue.field' = 'after',
  'transforms.extractValue.type'  = 'org.apache.kafka.connect.transforms.ExtractField$Value');""")

    # 3. add sink kafka connect
    # ksql_client.ksql(f"""
    #     CREATE SINK CONNECTOR IF NOT EXISTS `{topic}-jdbc-connector` WITH(
    #     "connector.class"='io.confluent.connect.jdbc.JdbcSourceConnector',
    #     "connection.url"='jdbc:postgresql://{config.source_db_host}:{config.source_db_port}/{config.source_db_name}',
    #     "mode"='bulk',
    #     "topic.prefix"='jdbc-',
    #     "table.whitelist"='users',
    #     "key"='username');
    # """)
    ksql_client.ksql(f"""CREATE SINK CONNECTOR `workshop-es-sink-connector` WITH (
  'behavior.on.null.values' = 'delete',
  'connector.class'         = 'io.confluent.connect.elasticsearch.ElasticsearchSinkConnector',
  'connection.url'          = 'http://elasticsearch:9200',
  'schema.ignore'           = 'true',
  'tasks.max'               = '1',
  'topics'                  = 'jdbc_customers_to_customer',
  'type.name'               = 'ksql-workshop',
  'write.method'            = 'upsert'
);""")
    print("ksql started to add source and sink JDBC connector ")

    return {
        "is_success": True
    }


cnt = 0


def ack(err, msg):
    global cnt
    cnt = cnt + 1


@app.post("/items2")
async def create_item2(item: Item):
    try:
        aio_producer.produce("items", item.name, on_delivery=ack)
        return {"timestamp": time()}
    except KafkaException as ex:
        raise HTTPException(status_code=500, detail=ex.args[0].str())


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
