from typing import Union

from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
import requests, time
from fastapi.background import BackgroundTasks


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # React app / Frontend
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods
    allow_headers=["*"], # Allow all headers
)

# This should be different database from inventory database
redis = get_redis_connection(
    host="redis-15407.c16.us-east-1-2.ec2.redns.redis-cloud.com", 
    port=15407, 
    db=0, 
    password="",
    decode_responses=True

)  


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str # pending, paid, shipped, delivered


    class Meta:
        database = redis

@app.post("/orders")
async def create(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()

    req = requests.get(f"http://localhost:8000/products/%s" % body["id"])
    product = req.json()

    order = Order(
        product_id=body["id"],
        price=product["price"],
        fee=0.5 * product["price"],
        total=1.2* product["price"] ,
        quantity=body["quantity"],
        status="pending"
    )
    order.save()

    background_tasks.add_task(order_completed, order)   

    return order 

def order_completed(order: Order):
    time.sleep(5)   
    order.status = "completed"
    order.save()
    # Send reddis stream 
    redis.xadd("order_completed", order.dict(), "*")


@app.get("/orders/{pk}")
def get(pk: str):
    return Order.get(pk)