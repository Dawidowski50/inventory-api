import os

import httpx


BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def test_get_all():
    r = httpx.get(f"{BASE_URL}/getAll", timeout=10.0)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_single_existing():
    r = httpx.get(f"{BASE_URL}/getSingleProduct", params={"ProductID": 1001}, timeout=10.0)
    assert r.status_code == 200
    body = r.json()
    assert body["ProductID"] == 1001
    assert "Name" in body


def test_paginate_limit_10():
    r = httpx.get(
        f"{BASE_URL}/paginate",
        params={"startProductID": 1001, "endProductID": 1200},
        timeout=10.0,
    )
    assert r.status_code == 200
    arr = r.json()
    assert isinstance(arr, list)
    assert len(arr) <= 10


def test_starts_with():
    r = httpx.get(f"{BASE_URL}/startsWith", params={"letter": "s"}, timeout=10.0)
    assert r.status_code == 200
    arr = r.json()
    assert isinstance(arr, list)
    for p in arr:
        assert p["Name"].lower().startswith("s")


def test_convert():
    r = httpx.get(f"{BASE_URL}/convert", params={"ProductID": 1001}, timeout=10.0)
    # Can be 502 if FX API blocked; accept 200/502 for CI environments without outbound.
    assert r.status_code in (200, 502)
    if r.status_code == 200:
        body = r.json()
        assert "UnitPriceEUR" in body


def test_add_and_delete():
    product = {
        "ProductID": 999999,
        "Name": "Pytest Product",
        "UnitPrice": 1.23,
        "StockQuantity": 1,
        "Description": "Created by pytest",
    }
    r = httpx.post(f"{BASE_URL}/addNew", json=product, timeout=10.0)
    assert r.status_code in (201, 409)
    # If it was created now, it must be deletable now.
    if r.status_code == 201:
        d = httpx.delete(f"{BASE_URL}/deleteOne", params={"ProductID": product["ProductID"]}, timeout=10.0)
        assert d.status_code == 200
        assert d.json().get("deleted") is True

        # Deleting again should 404
        d2 = httpx.delete(f"{BASE_URL}/deleteOne", params={"ProductID": product["ProductID"]}, timeout=10.0)
        assert d2.status_code == 404


def test_metrics():
    r = httpx.get(f"{BASE_URL}/metrics", timeout=10.0)
    assert r.status_code == 200
    assert "# HELP" in r.text

