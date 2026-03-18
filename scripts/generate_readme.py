from __future__ import annotations

from datetime import datetime

ENDPOINTS = [
    ("/getSingleProduct", "GET", "Query: ProductID (int)"),
    ("/getAll", "GET", "No params"),
    ("/addNew", "POST", "Body JSON: ProductID, Name, UnitPrice, StockQuantity, Description"),
    ("/deleteOne", "DELETE", "Query: ProductID (int)"),
    ("/startsWith", "GET", "Query: letter (single character)"),
    ("/paginate", "GET", "Query: startProductID (int), endProductID (int)  (returns up to 10)"),
    ("/convert", "GET", "Query: ProductID (int)  (USD→EUR)"),
    ("/docs", "GET", "FastAPI Swagger UI"),
    ("/openapi.json", "GET", "OpenAPI JSON"),
    ("/metrics", "GET", "Prometheus metrics (monitoring)"),
]


def main() -> None:
    lines: list[str] = []
    lines.append("Inventory API - README.txt")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")
    lines.append("Endpoints")
    lines.append("---------")
    for path, method, params in ENDPOINTS:
        lines.append(f"{method:6} {path:18} {params}")
    lines.append("")
    lines.append("FastAPI documentation")
    lines.append("--------------------")
    lines.append("See /docs (Swagger UI) or /redoc when the API is running.")
    lines.append("Reference: https://fastapi.tiangolo.com/")
    lines.append("")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

