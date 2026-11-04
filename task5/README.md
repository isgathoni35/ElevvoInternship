# Task 5: Weather Dashboard Using a Public REST API

A clean command-line weather tool that fetches live conditions from the OpenWeatherMap REST API, manages API secrets using `python-dotenv`, handles errors gracefully, and includes offline mock tests using `pytest`.

---

## Features
- **Public REST API**: Integrates with OpenWeatherMap's Current Weather API endpoint.
- **Secrets Management**: Loads API credentials from a `.env` file or environment variables without exposing secrets in code.
- **Error Handling**: Gracefully handles non-existent cities (404), invalid or missing API keys (401), request timeouts, and connection losses.
- **Clean CLI UI**: Presents weather condition, temperature (°C), feels-like, humidity, and wind speed in an easy-to-read table.
- **Bonus**: Automated offline unit test suite using `pytest` and `unittest.mock` to verify all status codes and exception handlers without making network calls.

---

## Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp task5/.env.example task5/.env
   ```
2. Obtain a free API key from [OpenWeatherMap](https://openweathermap.org/api) and paste it into `task5/.env`:
   ```env
   OPENWEATHER_API_KEY=your_actual_key_here
   ```

---

## How to Run

### 1. Run the Dashboard
```bash
# Pass city as CLI argument
python task5/weather_dashboard.py London

# Or run interactively
python task5/weather_dashboard.py
```

### 2. Run the Automated Tests (Offline with pytest)
```bash
pytest task5/test_weather.py -v
```
