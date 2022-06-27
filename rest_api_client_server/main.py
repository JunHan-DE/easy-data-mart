import typing

from confluent_kafka import KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
from fastapi import FastAPI, HTTPException
from time import time
from ksql import KSQLAPI

import uvicorn
from app.utils.kafka.aio_producer import AIOProducer
from app.sql.ksql import (
    create_stream_ksql,
    create_postgres_source_connect_ksql,
    create_es_sink_connect_ksql,
)
from app.utils.database.models import (
    EtlConfig,
    Items,
)
from app.common.config import conf
from app.common.variables import db_connector_mapper

app = FastAPI()
aio_producer: typing.Union[AIOProducer, None] = None
admin_client: typing.Union[AdminClient, None] = None
ksql_client: typing.Union[KSQLAPI, None] = None
conf = conf()
cnt = 0

BOOTSTRAP_SERVERS = {
    "bootstrap.servers": "0.0.0.0:9092"
}
KSQL_SERVER = "http://0.0.0.0:8088"


@app.post("/etl")
async def run_etl_code(config: EtlConfig):

    topic = (
        config.source_table_name
        if config.source_table_name == config.target_table_name
        else f"test_{config.source_table_name}_to_{config.target_table_name}"
    )

    source_connect = db_connector_mapper.get(config.source_type)
    target_connect = db_connector_mapper.get(config.target_type)

    # 1. create topic
    topics = [NewTopic(topic=topic, num_partitions=1, replication_factor=1)]
    admin_client.create_topics(topics)

    # 2. add streams
    ksql_client.ksql(
        create_stream_ksql.format(
            topic=topic,
            column_info=config.source_table_columns,
        )
    )

    # 2. add source kafka connect
    # TODO: Add conditions to Support more source connectors
    ksql_client.ksql(
        create_postgres_source_connect_ksql.format(
            db_name=config.source_db_name,
            db_password=config.source_db_password,
            db_port=config.source_db_port,
            db_user=config.source_db_user,
            extract_key_field=config.extract_key_field,
        )
    )

    # 3. add sink kafka connect
    ksql_client.ksql(
        create_es_sink_connect_ksql.format(
            topic=topic,
        )
    )

    return {
        "is_success": True,
        "message": "ETL has been finished and Data Ingestion from source to target is working in progress."
    }


def ack(err, msg):
    global cnt
    cnt = cnt + 1


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



@app.post("/produce/items")
async def create_item2(item: Items):
    try:
        aio_producer.produce("items", item.name, on_delivery=ack)
        return {"timestamp": time()}
    except KafkaException as ex:
        raise HTTPException(status_code=500, detail=ex.args[0].str())


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
