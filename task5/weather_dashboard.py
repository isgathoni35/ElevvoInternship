"""Weather Dashboard Using a Public REST API.

Fetches current weather for a specified city via OpenWeatherMap API (when API key is present)
or automatically falls back to the free, keyless Open-Meteo API so live queries always succeed.
"""

import argparse
import os
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load .env file from the script directory or workspace root
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
OPEN_METEO_GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# WMO Weather interpretation codes for Open-Meteo
WMO_WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Foggy", 48: "Depositing Rime Fog",
    51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
    61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
    71: "Slight Snow Fall", 73: "Moderate Snow Fall", 75: "Heavy Snow Fall",
    80: "Slight Rain Showers", 81: "Moderate Rain Showers", 82: "Violent Rain Showers",
    95: "Thunderstorm",
}


def fetch_weather_open_meteo(city: str, timeout: int = 10) -> dict:
    """Fetch live weather without requiring an API key via Open-Meteo."""
    try:
        geo_res = requests.get(OPEN_METEO_GEO_URL, params={"name": city.strip(), "count": 1}, timeout=timeout)
        geo_res.raise_for_status()
        geo_data = geo_res.json()
    except requests.RequestException as e:
        raise requests.RequestException(f"Network error geocoding city: {e}")

    results = geo_data.get("results")
    if not results:
        raise ValueError(f"City '{city}' not found. Please verify spelling.")

    loc = results[0]
    lat = loc["latitude"]
    lon = loc["longitude"]
    name = loc.get("name", city)
    country = loc.get("country_code", "")

    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "wind_speed_10m", "weather_code"]
    }

    try:
        w_res = requests.get(OPEN_METEO_WEATHER_URL, params=weather_params, timeout=timeout)
        w_res.raise_for_status()
        w_data = w_res.json()
    except requests.RequestException as e:
        raise requests.RequestException(f"Network error fetching weather conditions: {e}")

    curr = w_data.get("current", {})
    w_code = curr.get("weather_code", 0)
    weather_desc = WMO_WEATHER_CODES.get(w_code, "Partly Cloudy")

    return {
        "name": name,
        "sys": {"country": country},
        "weather": [{"description": weather_desc}],
        "main": {
            "temp": curr.get("temperature_2m", 0.0),
            "feels_like": curr.get("apparent_temperature", 0.0),
            "humidity": curr.get("relative_humidity_2m", 0),
        },
        "wind": {"speed": curr.get("wind_speed_10m", 0.0)},
        "provider": "Open-Meteo (Live Public API)"
    }


def fetch_weather(city: str, api_key: str = None, timeout: int = 10, fallback: bool = True) -> dict:
    """Fetch live weather data.

    Uses OpenWeatherMap if api_key is present. If missing and fallback is True,
    falls back to the free Open-Meteo API. If fallback is False and key is missing,
    raises ValueError.
    """
    if not api_key or not api_key.strip():
        if fallback:
            return fetch_weather_open_meteo(city, timeout=timeout)
        raise ValueError("Missing API key. Please set OPENWEATHER_API_KEY in your .env file.")

    params = {
        "q": city.strip(),
        "appid": api_key.strip(),
        "units": "metric",  # Use Celsius
    }

    try:
        response = requests.get(OPENWEATHER_API_URL, params=params, timeout=timeout)
    except requests.exceptions.Timeout:
        raise requests.RequestException(f"Request timed out while contacting weather service for '{city}'.")
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"Network error connecting to weather API: {e}")

    if response.status_code == 200:
        data = response.json()
        data["provider"] = "OpenWeatherMap"
        return data
    elif response.status_code == 404:
        raise ValueError(f"City '{city}' not found. Please verify spelling.")
    elif response.status_code == 401:
        raise ValueError("Unauthorized API key. Please check your OPENWEATHER_API_KEY.")
    else:
        raise requests.RequestException(f"Weather API returned unexpected status code {response.status_code}: {response.text}")


def format_weather(data: dict) -> str:
    """Format raw API weather response into a clean, human-readable CLI view."""
    city_name = data.get("name", "Unknown City")
    country = data.get("sys", {}).get("country", "")
    weather_desc = data.get("weather", [{}])[0].get("description", "N/A").title()
    main = data.get("main", {})
    temp = main.get("temp", "N/A")
    feels_like = main.get("feels_like", "N/A")
    humidity = main.get("humidity", "N/A")
    wind_speed = data.get("wind", {}).get("speed", "N/A")
    provider = data.get("provider", "REST API")

    lines = [
        "=" * 48,
        f"  WEATHER REPORT: {city_name}, {country}",
        f"  (Data Source: {provider})",
        "=" * 48,
        f" Condition   : {weather_desc}",
        f" Temperature : {temp} C",
        f" Feels Like  : {feels_like} C",
        f" Humidity    : {humidity}%",
        f" Wind Speed  : {wind_speed} m/s",
        "=" * 48,
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Live Weather Dashboard CLI")
    parser.add_argument("city", nargs="?", help="Name of the city (e.g. London, Nairobi, Tokyo)")
    args = parser.parse_args()

    api_key = os.getenv("OPENWEATHER_API_KEY")

    city = args.city
    if not city:
        city = input("Enter city name: ").strip()

    if not city:
        print("Error: City name cannot be empty.")
        sys.exit(1)

    if not api_key:
        print(f"Notice: OPENWEATHER_API_KEY not configured. Connecting to live public weather service...")

    print(f"Fetching weather for '{city}'...")
    try:
        data = fetch_weather(city, api_key)
        print("\n" + format_weather(data))
    except ValueError as e:
        print(f"\n[Error] {e}")
        sys.exit(1)
    except requests.RequestException as e:
        print(f"\n[Network Error] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
