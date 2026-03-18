from __future__ import annotations

import httpx

from app.config import settings


class ExchangeRateError(RuntimeError):
    pass


async def usd_to_eur_rate() -> float:
    """
    Uses Frankfurter (ECB-based) rates.
    Docs: https://www.frankfurter.app/
    """
    url = f"{settings.fx_base_url.rstrip('/')}/latest"
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url, params={"from": "USD", "to": "EUR"})
    if r.status_code != 200:
        raise ExchangeRateError(f"FX API error {r.status_code}")
    data = r.json()
    rate = data.get("rates", {}).get("EUR")
    if not isinstance(rate, (int, float)):
        raise ExchangeRateError("Unexpected FX API response")
    return float(rate)

