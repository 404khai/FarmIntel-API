import requests
from django.conf import settings

class WeatherAnalyticsService:
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

    @staticmethod
    def get_coordinates(city, state=None, country=None):
        """Convert city, state, country into lat/lon using Open-Meteo Geocoding API."""
        # Open-Meteo searches by 'name' (city) primarily. 
        # Adding state/country to the name often fails if the format isn't exact.
        # It's safer to search by city name and filter/trust the top result, 
        # or rely on the API's relevance sorting.
        
        params = {
            "name": city,
            "count": 5,
            "language": "en",
            "format": "json"
        }
        
        try:
            response = requests.get(WeatherAnalyticsService.GEOCODING_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "results" in data and len(data["results"]) > 0:
                # Ideally, we could filter results by country_code if user.country is an ISO code
                # For now, take the top result as it's usually the most relevant major city
                result = data["results"][0]
                return result["latitude"], result["longitude"]
        except Exception as e:
            print(f"Geocoding error: {e}")
        
        return None, None

    @staticmethod
    def get_farmer_analytics(user):
        """Fetch weather and soil stats for a user's location."""
        lat, lon = WeatherAnalyticsService.get_coordinates(
            city=user.city,
            state=user.state,
            country=user.country
        )

        if not lat or not lon:
            return {"error": "Could not determine location coordinates."}

        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,precipitation,soil_moisture_0_to_7cm",
            "timezone": "auto",
            "forecast_days": 7
        }

        try:
            response = requests.get(WeatherAnalyticsService.WEATHER_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Extract current or summary data
            hourly = data.get("hourly", {})
            
            # Simple average/current stats for the dashboard
            current_temp = hourly.get("temperature_2m", [0])[0]
            current_soil_moisture = hourly.get("soil_moisture_0_to_7cm", [0])[0]
            total_expected_rainfall = sum(hourly.get("precipitation", [0]))

            return {
                "location": {
                    "city": user.city,
                    "state": user.state,
                    "country": user.country,
                    "latitude": lat,
                    "longitude": lon
                },
                "stats": {
                    "temperature": current_temp,
                    "soil_moisture": current_soil_moisture,
                    "expected_rainfall": round(total_expected_rainfall, 2),
                },
                "unit_details": {
                    "temperature": data.get("hourly_units", {}).get("temperature_2m", "°C"),
                    "soil_moisture": data.get("hourly_units", {}).get("soil_moisture_0_to_7cm", "m³/m³"),
                    "precipitation": data.get("hourly_units", {}).get("precipitation", "mm")
                }
            }
        except Exception as e:
            return {"error": f"Weather API error: {str(e)}"}
