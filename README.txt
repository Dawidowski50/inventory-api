Inventory API - README.txt
Generated: 2026-03-18T12:00:45

Endpoints
---------
GET    /getSingleProduct  Query: ProductID (int)
GET    /getAll            No params
POST   /addNew            Body JSON: ProductID, Name, UnitPrice, StockQuantity, Description
DELETE /deleteOne         Query: ProductID (int)
GET    /startsWith        Query: letter (single character)
GET    /paginate          Query: startProductID (int), endProductID (int)  (returns up to 10)
GET    /convert           Query: ProductID (int)  (USD→EUR)
GET    /docs              FastAPI Swagger UI
GET    /openapi.json      OpenAPI JSON
GET    /metrics           Prometheus metrics (monitoring)

FastAPI documentation
--------------------
See /docs (Swagger UI) or /redoc when the API is running.
Reference: https://fastapi.tiangolo.com/

