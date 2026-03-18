from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Import products.csv into MongoDB (and write JSON dump).")
    p.add_argument("--csv", dest="csv_path", required=True, help="Path to products.csv")
    p.add_argument("--json-out", dest="json_out", default="products.json", help="Where to write JSON dump")
    p.add_argument("--mongo-uri", dest="mongo_uri", default="mongodb://localhost:27017")
    p.add_argument("--db", dest="db", default="inventory")
    p.add_argument("--collection", dest="collection", default="products")
    p.add_argument("--drop", action="store_true", help="Drop collection before import")
    return p.parse_args()


def _row_to_product(row: dict[str, str]) -> dict:
    return {
        "ProductID": int(row["ProductID"]),
        "Name": row["Name"].strip(),
        "UnitPrice": float(row["UnitPrice"]),
        "StockQuantity": int(row["StockQuantity"]),
        "Description": row["Description"].strip(),
    }


async def main() -> None:
    args = _parse_args()
    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    products: list[dict] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expected = {"ProductID", "Name", "UnitPrice", "StockQuantity", "Description"}
        if set(reader.fieldnames or []) != expected:
            raise SystemExit(f"Unexpected CSV headers: {reader.fieldnames} (expected {sorted(expected)})")
        for row in reader:
            products.append(_row_to_product(row))

    json_out = Path(args.json_out)
    json_out.write_text(json.dumps(products, indent=2), encoding="utf-8")

    client = AsyncIOMotorClient(args.mongo_uri)
    col = client[args.db][args.collection]
    await col.create_index("ProductID", unique=True)

    if args.drop:
        await col.drop()
        col = client[args.db][args.collection]
        await col.create_index("ProductID", unique=True)

    # Upsert to make re-runs safe
    for p in products:
        await col.replace_one({"ProductID": p["ProductID"]}, p, upsert=True)

    client.close()
    print(f"Imported {len(products)} products into {args.mongo_uri}/{args.db}.{args.collection}")
    print(f"Wrote JSON dump to {json_out}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

