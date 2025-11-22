from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from bson import ObjectId

from database import create_document, get_documents, get_document, update_document, delete_document
from schemas import Product, ProductOut, CartItem, Cart, Order, OrderOut

app = FastAPI(title="E-commerce API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    message: str


@app.get("/", response_model=Message)
async def root():
    return {"message": "E-commerce API running"}


# Products
@app.post("/products", response_model=Message)
async def create_product(product: Product):
    pid = create_document("product", product.model_dump())
    return {"message": pid}


@app.get("/products", response_model=List[ProductOut])
async def list_products():
    return get_documents("product", {}, limit=200)


@app.get("/products/{product_id}", response_model=ProductOut)
async def get_product(product_id: str):
    prod = get_document("product", {"_id": ObjectId(product_id)})
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod


@app.put("/products/{product_id}", response_model=Message)
async def update_product(product_id: str, product: Product):
    modified = update_document("product", {"_id": ObjectId(product_id)}, product.model_dump())
    if modified == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "updated"}


@app.delete("/products/{product_id}", response_model=Message)
async def delete_product(product_id: str):
    deleted = delete_document("product", {"_id": ObjectId(product_id)})
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "deleted"}


# Cart endpoints (session-based)
@app.post("/cart/{session_id}/items", response_model=Message)
async def add_to_cart(session_id: str, item: CartItem):
    # Upsert: if cart exists, update quantity or add item; else create cart
    from database import collection

    coll = collection("cart")
    cart = coll.find_one({"session_id": session_id})

    if not cart:
        cart_doc = {"session_id": session_id, "items": [item.model_dump()]}
        cid = create_document("cart", cart_doc)
        return {"message": cid}

    # update existing
    updated = False
    for it in cart.get("items", []):
        if it["product_id"] == item.product_id:
            it["quantity"] += item.quantity
            updated = True
            break
    if not updated:
        cart.setdefault("items", []).append(item.model_dump())

    from datetime import datetime
    cart["updated_at"] = datetime.utcnow()
    coll.update_one({"_id": cart["_id"]}, {"$set": cart})
    return {"message": "added"}


@app.get("/cart/{session_id}", response_model=Cart)
async def get_cart(session_id: str):
    from database import collection

    cart = collection("cart").find_one({"session_id": session_id})
    if not cart:
        return {"session_id": session_id, "items": []}
    cart.pop("_id", None)
    return cart


# Order endpoints
@app.post("/orders", response_model=Message)
async def create_order(order: Order):
    oid = create_document("order", order.model_dump())
    return {"message": oid}


@app.get("/orders", response_model=List[OrderOut])
async def list_orders():
    return get_documents("order", {}, limit=200)
