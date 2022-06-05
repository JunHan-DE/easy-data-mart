import asyncio
import confluent_kafka
from confluent_kafka import KafkaException
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from time import time
from threading import Thread
import uvicorn

config = {"bootstrap.servers": "localhost:9092"}

app = FastAPI()


class Item(BaseModel):
    name: str


aio_producer = None
producer = None


@app.on_event("startup")
async def startup_event():
    global producer, aio_producer
    aio_producer = AIOProducer(config)
    producer = Producer(config)


@app.on_event("shutdown")
def shutdown_event():
    aio_producer.close()
    producer.close()


@app.post("/items1")
async def create_item1(item: Item):
    try:
        result = await aio_producer.produce("items", item.name)
        return {"timestamp": result.timestamp()}
    except KafkaException as ex:
        raise HTTPException(status_code=500, detail=ex.args[0].str())


cnt = 0


def ack(err, msg):
    global cnt
    cnt = cnt + 1


@app.post("/items2")
async def create_item2(item: Item):
    try:
        aio_producer.produce2("items", item.name, on_delivery=ack)
        return {"timestamp": time()}
    except KafkaException as ex:
        raise HTTPException(status_code=500, detail=ex.args[0].str())


@app.post("/items3")
async def create_item3(item: Item):
    try:
        producer.produce("items", item.name, on_delivery=ack)
        return {"timestamp": time()}
    except KafkaException as ex:
        raise HTTPException(status_code=500, detail=ex.args[0].str())


@app.post("/items4")
async def create_item4(item: Item):
    try:
        producer.produce("items", item.name)
        return {"timestamp": time()}
    except KafkaException as ex:
        raise HTTPException(status_code=500, detail=ex.args[0].str())


@app.post("/items5")
async def create_item5(item: Item):
    return {"timestamp": time()}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

# app = Flask(__name__)
#
# mysql = MySQL()
#
# # MySQL configurations
# app.config["MYSQL_DATABASE_USER"] = "root"
# app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("db_root_password")
# app.config["MYSQL_DATABASE_DB"] = os.getenv("db_name")
# app.config["MYSQL_DATABASE_HOST"] = os.getenv("MYSQL_SERVICE_HOST")
# app.config["MYSQL_DATABASE_PORT"] = int(os.getenv("MYSQL_SERVICE_PORT"))
# mysql.init_app(app)
#
#
# @app.route("/")
# def index():
#     """Function to test the functionality of the API"""
#     return "Hello, world!"
#
#
# @app.route("/create", methods=["POST"])
# def add_user():
#     """Function to add a user to the MySQL database"""
#     json = request.json
#     name = json["name"]
#     email = json["email"]
#     pwd = json["pwd"]
#     if name and email and pwd and request.method == "POST":
#         sql = "INSERT INTO users(user_name, user_email, user_password) " \
#               "VALUES(%s, %s, %s)"
#         data = (name, email, pwd)
#         try:
#             conn = mysql.connect()
#             cursor = conn.cursor()
#             cursor.execute(sql, data)
#             conn.commit()
#             cursor.close()
#             conn.close()
#             resp = jsonify("User added successfully!")
#             resp.status_code = 200
#             return resp
#         except Exception as exception:
#             return jsonify(str(exception))
#     else:
#         return jsonify("Please provide name, email and pwd")
#
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
