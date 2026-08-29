import requests
from fastmcp import FastMCP

mcp = FastMCP("Weather Server")



@mcp.tool()
def get_weather(location: str) -> str:
    """
    Get the current weather for a location using Open-Meteo API.

    Args:
        location (str): City or place name (e.g., "Chennai")

    Example:
        get_weather("Chennai")
    """
    try:
        # -----------------------------------------
        # STEP 1: Geocoding - Find latitude & longitude
        # -----------------------------------------
        geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        geocoding_params = {"name": location, "count": 1, "language": "en", "format": "json"}

        response = requests.get(geocoding_url, params=geocoding_params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        if not results:
            return f"Location not found: {location}"

        place = results[0]
        latitude, longitude = place["latitude"], place["longitude"]
        city = place.get("name", location)
        country = place.get("country", "")

        # -----------------------------------------
        # STEP 2: Weather data
        # -----------------------------------------
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "precipitation,"
                "weather_code,"
                "wind_speed_10m"
            )
        }

        weather_response = requests.get(weather_url, params=weather_params, timeout=10)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        current = weather_data.get("current", {})

        # -----------------------------------------
        # STEP 3: Extract weather information
        # -----------------------------------------
        temperature = current.get("temperature_2m", "N/A")
        humidity = current.get("relative_humidity_2m", "N/A")
        feels_like = current.get("apparent_temperature", "N/A")
        precipitation = current.get("precipitation", "N/A")
        wind_speed = current.get("wind_speed_10m", "N/A")
        weather_code = current.get("weather_code", "N/A")

    
        return (
            f"Weather for {city}, {country}\n"
            f"Temperature: {temperature}°C\n"
            f"Feels like: {feels_like}°C\n"
            f"Humidity: {humidity}%\n"
            f"Precipitation: {precipitation} mm\n"
            f"Wind speed: {wind_speed} km/h\n"
            f"Weather code: {weather_code}"
        )

    except requests.RequestException as e:
        return f"Weather API error: {e}"
    except Exception as e:
        return f"Weather error: {e}"


if __name__ == "__main__":
    mcp.run()
