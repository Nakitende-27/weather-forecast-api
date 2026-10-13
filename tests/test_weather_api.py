
"""Offline tests for the weather API request function."""

import unittest
from unittest.mock import Mock, patch

import requests

from src.weather_api import get_weather_with_retry, WeatherAPIError


class TestWeatherAPI(unittest.TestCase):
    """Test weather requests without accessing the real internet."""

    @patch("src.weather_api.requests.get")
    def test_successful_request(self, mock_get):
        """Test that a successful response returns JSON data."""
        mock_response = Mock()
        mock_response.json.return_value = {"temperature": 25}
        mock_get.return_value = mock_response

        result = get_weather_with_retry("https://example.com/weather")

        self.assertEqual(result, {"temperature": 25})
        mock_get.assert_called_once()

    @patch("src.weather_api.requests.get")
    def test_http_400_is_not_retried(self, mock_get):
        """Test that an HTTP 400 error fails without retrying."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError(
                "400 Bad Request",
                response=mock_response,
            )
        )
        mock_get.return_value = mock_response

        with self.assertRaises(WeatherAPIError):
            get_weather_with_retry("https://example.com/weather")

        mock_get.assert_called_once()

    @patch("src.weather_api.time.sleep")
    @patch("src.weather_api.requests.get")
    def test_connection_error_is_retried(self, mock_get, mock_sleep):
        """Test that a connection error is retried."""
        mock_response = Mock()
        mock_response.json.return_value = {"temperature": 25}

        mock_get.side_effect = [
            requests.exceptions.ConnectionError("Connection failed"),
            mock_response,
        ]

        result = get_weather_with_retry(
            "https://example.com/weather",
            max_retries=2,
        )

        self.assertEqual(result, {"temperature": 25})
        self.assertEqual(mock_get.call_count, 2)
        mock_sleep.assert_called_once_with(1)

    @patch("src.weather_api.time.sleep")
    @patch("src.weather_api.requests.get")
    def test_http_503_is_retried(self, mock_get, mock_sleep):
        """Test that an HTTP 503 server error is retried."""
        failed_response = Mock()
        failed_response.status_code = 503
        failed_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError(
                "503 Service Unavailable",
                response=failed_response,
            )
        )

        successful_response = Mock()
        successful_response.json.return_value = {"temperature": 24}

        mock_get.side_effect = [
            failed_response,
            successful_response,
        ]

        result = get_weather_with_retry(
            "https://example.com/weather",
            max_retries=2,
        )

        self.assertEqual(result, {"temperature": 24})
        self.assertEqual(mock_get.call_count, 2)
        mock_sleep.assert_called_once_with(1)

    def test_invalid_retry_count_is_rejected(self):
        """Test that zero attempts are rejected."""
        with self.assertRaises(ValueError):
            get_weather_with_retry(
                "https://example.com/weather",
                max_retries=0,
            )


if __name__ == "__main__":
    unittest.main()
