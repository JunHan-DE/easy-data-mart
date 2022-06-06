import asyncio
import confluent_kafka
from confluent_kafka import KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from time import time
from threading import Thread
import uvicorn
from app.kafka.producer.aio_producer import AIOProducer

config = {
    "bootstrap.servers": "jun-kafka-0.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092,"
                         "jun-kafka-1.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092,"
                         "jun-kafka-2.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092"
}

app = FastAPI()


class Item(BaseModel):
    name: str


class EtlConfig(BaseModel):
    source_type: str
    source_db_name: str
    source_db_host: str
    source_db_port: str
    source_table_name: str
    target_type: str
    target_db_name: str
    target_db_host: str
    target_db_port: str
    target_table_name: str



aio_producer = None
admin_client = None

@app.on_event("startup")
async def startup_event():
    global aio_producer, admin_client
    aio_producer = AIOProducer(config)
    admin_client = AdminClient(config)

@app.on_event("shutdown")
def shutdown_event():
    aio_producer.close()


@app.post("/items1")
async def create_item1(item: Item):
    try:
        result = await aio_producer.produce("items", item.name)
        return {"timestamp": result.timestamp()}
    except KafkaException as ex:
        raise HTTPException(status_code=500, detail=ex.args[0].str())


@app.get("/health/")
async def check_server_health_status() -> dict:
    return {"status": 200}


@app.get("/etl")
async def run_etl_code(config: EtlConfig):
    topic = (
        config.source_table_name
        if config.source_table_name == config.target_table_name
        else f"{config.source_table_name}_to_{config.target_table_name}"
    )
    # 1. create topic
    topics = [NewTopic(
            topic=topic, num_partitions=3, replication_factor=2
    )]
    admin_client.create_topics(topics)
    # 2. add source kafka connect

    # 3. add sink kafka connect


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
