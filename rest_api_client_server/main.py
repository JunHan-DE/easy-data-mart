import asyncio
import confluent_kafka
from confluent_kafka import KafkaException
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from time import time
from threading import Thread
import uvicorn
from app.kafka.producer.aio_producer import AIOProducer

config = {"bootstrap.servers": "localhost:9092"}

app = FastAPI()


class Item(BaseModel):
    name: str


aio_producer = None


@app.on_event("startup")
async def startup_event():
    global producer, aio_producer
    aio_producer = AIOProducer(config)


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
