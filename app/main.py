from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import PositiveInt

from app.db import ensure_indexes, get_collection
from app.models import ProductCreate, ProductOut, mongo_to_product
from app.services.exchange import ExchangeRateError, usd_to_eur_rate

app = FastAPI(title="Inventory API", version="1.0.0")

# Prometheus instrumentation must be registered before startup.
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.on_event("startup")
async def _startup() -> None:
    await ensure_indexes()


@app.get("/getSingleProduct", response_model=ProductOut)
async def get_single_product(product_id: PositiveInt = Query(..., alias="ProductID")):
    col = get_collection()
    doc = await col.find_one({"ProductID": int(product_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    return mongo_to_product(doc)


@app.get("/getAll", response_model=list[ProductOut])
async def get_all():
    col = get_collection()
    docs = await col.find({}, sort=[("ProductID", 1)]).to_list(length=10_000)
    return [mongo_to_product(d) for d in docs]


@app.post("/addNew", response_model=ProductOut, status_code=201)
async def add_new(product: ProductCreate):
    col = get_collection()
    payload = product.model_dump()
    try:
        await col.insert_one(payload)
    except Exception as e:  # duplicate key or connectivity
        msg = str(e)
        if "duplicate key" in msg.lower():
            raise HTTPException(status_code=409, detail="ProductID already exists")
        raise HTTPException(status_code=500, detail="Insert failed")
    return payload


@app.delete("/deleteOne")
async def delete_one(product_id: PositiveInt = Query(..., alias="ProductID")):
    col = get_collection()
    res = await col.delete_one({"ProductID": int(product_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"deleted": True, "ProductID": int(product_id)}


@app.get("/startsWith", response_model=list[ProductOut])
async def starts_with(letter: str = Query(..., min_length=1, max_length=1)):
    col = get_collection()
    regex = f"^{letter}"
    docs = await col.find({"Name": {"$regex": regex, "$options": "i"}}, sort=[("ProductID", 1)]).to_list(
        length=10_000
    )
    return [mongo_to_product(d) for d in docs]


@app.get("/paginate", response_model=list[ProductOut])
async def paginate(
    start_id: PositiveInt = Query(..., alias="startProductID"),
    end_id: PositiveInt = Query(..., alias="endProductID"),
):
    start_val = int(start_id)
    end_val = int(end_id)
    if start_val > end_val:
        raise HTTPException(status_code=422, detail="startProductID must be <= endProductID")
    col = get_collection()
    docs = await col.find(
        {"ProductID": {"$gte": start_val, "$lte": end_val}},
        sort=[("ProductID", 1)],
        limit=10,
    ).to_list(length=10)
    return [mongo_to_product(d) for d in docs]


@app.get("/convert")
async def convert(product_id: PositiveInt = Query(..., alias="ProductID")) -> dict[str, Any]:
    col = get_collection()
    doc = await col.find_one({"ProductID": int(product_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")

    product = mongo_to_product(doc)
    try:
        rate = await usd_to_eur_rate()
    except ExchangeRateError as e:
        raise HTTPException(status_code=502, detail=str(e))

    usd = float(product["UnitPrice"])
    eur = round(usd * rate, 2)
    return {
        "ProductID": int(product["ProductID"]),
        "Name": product["Name"],
        "UnitPriceUSD": usd,
        "UnitPriceEUR": eur,
        "RateUSDtoEUR": rate,
    }

