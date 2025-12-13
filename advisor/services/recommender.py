from typing import Dict, Any, List


CROP_THRESHOLDS = {
    "maize": {"tmin": 10.0, "tmax": 35.0, "precip_mm": 3.0},
    "rice": {"tmin": 18.0, "tmax": 40.0, "precip_mm": 5.0},
    "wheat": {"tmin": 5.0, "tmax": 30.0, "precip_mm": 2.0},
    "soybean": {"tmin": 10.0, "tmax": 35.0, "precip_mm": 2.0},
}


def score_completeness(farm: Dict[str, Any]) -> float:
    base = 0.6
    if farm.get("sensor_data"):
        base += 0.2
    return min(base, 1.0)


def recommend_planting(crop: str, forecast: List[Dict[str, Any]]) -> Dict[str, Any]:
    th = CROP_THRESHOLDS.get(crop.lower(), {"tmin": 8.0, "tmax": 38.0, "precip_mm": 2.0})
    candidates = []
    for day in forecast:
        ok_temp = day["tmin"] is not None and day["tmax"] is not None and th["tmin"] <= day["tmin"] <= th["tmax"]
        ok_rain = day["precip_mm"] is not None and day["precip_mm"] >= th["precip_mm"]
        if ok_temp and ok_rain:
            candidates.append(day)
    if candidates:
        best = candidates[0]
        conf = 0.7
        return {
            "date": best["date"],
            "window": [candidates[0]["date"], candidates[min(len(candidates)-1, 6)]["date"]],
            "confidence": conf,
            "explanation": "Weather meets crop thresholds for temperature and rainfall",
        }
    best = forecast[0] if forecast else None
    return {
        "date": best["date"] if best else None,
        "window": None,
        "confidence": 0.4,
        "explanation": "No ideal days found; picking earliest acceptable date",
    }


def recommend_irrigation(sensor: Dict[str, Any], forecast: List[Dict[str, Any]]) -> Dict[str, Any]:
    moisture = sensor.get("soil_moisture") if sensor else None
    schedule = []
    if moisture is not None:
        target = 35.0
        deficit = max(0.0, target - moisture)
        if deficit > 0:
            amount = round(deficit * 1.5, 2)
            schedule.append({"date": forecast[0]["date"] if forecast else None, "amount_mm": amount})
        conf = 0.75
        expl = "Sensor moisture drives irrigation adjustments"
    else:
        rain_next = sum([d.get("precip_mm") or 0 for d in forecast[:3]])
        if rain_next < 5:
            schedule.append({"date": forecast[0]["date"] if forecast else None, "amount_mm": 10})
        conf = 0.5
        expl = "Forecast-driven irrigation due to low expected rainfall"
    return {"schedule": schedule, "confidence": conf, "explanation": expl}


def recommend_fertilization(crop: str, soil_type: str, sensor: Dict[str, Any]) -> Dict[str, Any]:
    crop_l = crop.lower()
    if crop_l in ("maize", "wheat", "rice"):
        base = {"type": "NPK 15-15-15", "rate_kg_per_ha": 100, "timing": ["at planting", "4-6 weeks"]}
    elif crop_l in ("soybean",):
        base = {"type": "NPK 10-20-10", "rate_kg_per_ha": 80, "timing": ["at planting"]}
    else:
        base = {"type": "NPK 12-24-12", "rate_kg_per_ha": 90, "timing": ["at planting"]}
    conf = 0.6
    if sensor:
        n = sensor.get("nitrogen")
        p = sensor.get("phosphorus")
        k = sensor.get("potassium")
        adj = 0
        if n and n < 10:
            adj += 20
        if p and p < 10:
            adj += 10
        if k and k < 10:
            adj += 10
        if adj:
            base["rate_kg_per_ha"] += adj
            conf = 0.75
    explanation = "Crop-specific base with sensor-driven adjustments"
    return {"type": base["type"], "rate_kg_per_ha": base["rate_kg_per_ha"], "timing": base["timing"], "confidence": conf, "explanation": explanation}


def build_recommendations(farm: Dict[str, Any], forecast: List[Dict[str, Any]]) -> Dict[str, Any]:
    planting = recommend_planting(farm["crop_type"], forecast)
    irrigation = recommend_irrigation(farm.get("sensor_data") or {}, forecast)
    fertilization = recommend_fertilization(farm["crop_type"], farm["soil_type"], farm.get("sensor_data") or {})
    overall = min(1.0, (planting["confidence"] + irrigation["confidence"] + fertilization["confidence"]) / 3 * score_completeness(farm))
    return {
        "planting": planting,
        "irrigation": irrigation,
        "fertilization": fertilization,
        "overall_confidence": round(overall, 2),
    }

