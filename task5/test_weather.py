"""Automated tests for Task 5: Weather Dashboard using pytest and mocking."""

import os
import sys
from unittest.mock import patch, MagicMock
import pytest
import requests

sys.path.insert(0, os.path.dirname(__file__))

from weather_dashboard import fetch_weather, format_weather


@pytest.fixture
def sample_weather_response():
    return {
        "name": "Nairobi",
        "sys": {"country": "KE"},
        "weather": [{"description": "scattered clouds"}],
        "main": {
            "temp": 24.5,
            "feels_like": 25.0,
            "humidity": 65,
        },
        "wind": {"speed": 4.1},
    }


def test_fetch_weather_success(sample_weather_response):
    """Test successful API call returns parsed weather dictionary."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = sample_weather_response

    with patch("requests.get", return_value=mock_resp) as mock_get:
        data = fetch_weather("Nairobi", api_key="fake_test_key")
        assert data["name"] == "Nairobi"
        assert data["main"]["temp"] == 24.5
        mock_get.assert_called_once()


def test_fetch_weather_city_not_found():
    """Test 404 error raises informative ValueError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 404

    with patch("requests.get", return_value=mock_resp):
        with pytest.raises(ValueError, match="City 'Atlantis' not found"):
            fetch_weather("Atlantis", api_key="fake_test_key")


def test_fetch_weather_unauthorized():
    """Test 401 error raises unauthorized API key ValueError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401

    with patch("requests.get", return_value=mock_resp):
        with pytest.raises(ValueError, match="Unauthorized API key"):
            fetch_weather("London", api_key="bad_key")


def test_fetch_weather_missing_key():
    """Test missing or empty API key raises ValueError when fallback is disabled."""
    with pytest.raises(ValueError, match="Missing API key"):
        fetch_weather("London", api_key="", fallback=False)


def test_fetch_weather_timeout():
    """Test network timeout raises requests.RequestException."""
    with patch("requests.get", side_effect=requests.exceptions.Timeout):
        with pytest.raises(requests.RequestException, match="timed out"):
            fetch_weather("Tokyo", api_key="fake_test_key")


def test_format_weather(sample_weather_response):
    """Test formatted CLI output contains expected fields."""
    output = format_weather(sample_weather_response)
    assert "Nairobi, KE" in output
    assert "Scattered Clouds" in output
    assert "24.5 C" in output
    assert "65%" in output
    assert "4.1 m/s" in output
