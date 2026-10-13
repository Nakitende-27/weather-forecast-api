
"""Reusable functions for making reliable weather API requests."""

import time
from typing import Any

import requests


class WeatherAPIError(Exception):
    """Raised when a weather API request fails permanently."""


def get_weather_with_retry(
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 10,
    max_retries: int = 3,
) -> dict[str, Any]:
    """
    Send a GET request and retry temporary failures.

    Args:
        url: API endpoint URL.
        params: Optional query parameters.
        headers: Optional HTTP request headers.
        timeout: Maximum seconds to wait for each request.
        max_retries: Maximum total number of attempts.

    Returns:
        The response data as a Python dictionary.

    Raises:
        WeatherAPIError: If the request ultimately fails.
        ValueError: If timeout or max_retries is invalid.
    """
    if timeout <= 0:
        raise ValueError("timeout must be greater than zero.")

    if max_retries < 1:
        raise ValueError("max_retries must be at least 1.")

    last_error = None

    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout,
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as error:
            status_code = error.response.status_code

            # Retry server errors (HTTP 5xx), but not client errors (HTTP 4xx).
            if not 500 <= status_code <= 599:
                raise WeatherAPIError(
                    f"Weather API returned HTTP {status_code}: {error}"
                ) from error

            last_error = error

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as error:
            last_error = error

        except requests.exceptions.RequestException as error:
            raise WeatherAPIError(
                f"Weather request failed: {error}"
            ) from error

        except ValueError as error:
            # The server returned a response that was not valid JSON.
            raise WeatherAPIError(
                f"Weather API returned invalid JSON: {error}"
            ) from error

        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            print(
                f"Attempt {attempt + 1} failed. "
                f"Retrying in {wait_time} seconds..."
            )
            time.sleep(wait_time)

    raise WeatherAPIError(
        f"Weather request failed after {max_retries} attempts. "
        f"Last error: {last_error}"
    ) from last_error
