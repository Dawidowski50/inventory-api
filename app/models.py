from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PositiveFloat, PositiveInt


class ProductBase(BaseModel):
    ProductID: PositiveInt = Field(..., description="Unique product ID")
    Name: str = Field(..., min_length=1, max_length=200)
    UnitPrice: PositiveFloat = Field(..., description="Unit price in USD")
    StockQuantity: PositiveInt = Field(..., description="Current stock quantity")
    Description: str = Field(..., min_length=1, max_length=2000)


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)


def mongo_to_product(doc: dict[str, Any]) -> dict[str, Any]:
    doc = dict(doc)
    doc.pop("_id", None)
    return doc

