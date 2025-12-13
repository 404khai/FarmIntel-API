import requests


def geocode(city: str = None, state: str = None, country: str = None):
    name_parts = [p for p in [city, state, country] if p]
    if not name_parts:
        return None
    q = ", ".join(name_parts)
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": q, "count": 1}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    results = data.get("results") or []
    if not results:
        return None
    top = results[0]
    return {"latitude": top.get("latitude"), "longitude": top.get("longitude")}

