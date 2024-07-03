from typing import Union

from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # React app / Frontend
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods
    allow_headers=["*"], # Allow all headers
)

redis = get_redis_connection(
    host="redis-15407.c16.us-east-1-2.ec2.redns.redis-cloud.com", 
    port=15407, 
    db=0, 
    password="",
    decode_responses=True

)  

# Product CRUD 

class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis



@app.get("/products")
def all():
    return [format(pk) for pk in Product.all_pks()]


def format(pk: str):
    product = Product.get(pk)

    return {
        "id": pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity
    
    }

@app.post("/products")
def create(product: Product):
    product.save()
    return product

@app.get("/products/{pk}")
def get(pk: str):
    return Product.get(pk)


@app.delete("/products/{pk}")
def delete(pk: str):
    return Product.get(pk).delete()
     

