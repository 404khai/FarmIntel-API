import requests


def fetch_daily_forecast(latitude: float, longitude: float, days: int = 14):
    base = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "sunshine_duration",
            "relative_humidity_2m_mean",
        ],
        "timezone": "auto",
    }
    r = requests.get(base, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    daily = data.get("daily", {})
    dates = daily.get("time", [])[:days]
    out = []
    for i, d in enumerate(dates):
        out.append(
            {
                "date": d,
                "tmax": daily.get("temperature_2m_max", [None] * len(dates))[i],
                "tmin": daily.get("temperature_2m_min", [None] * len(dates))[i],
                "precip_mm": daily.get("precipitation_sum", [None] * len(dates))[i],
                "sunshine_s": daily.get("sunshine_duration", [None] * len(dates))[i],
                "humidity_mean": daily.get("relative_humidity_2m_mean", [None] * len(dates))[i],
            }
        )
    return out
