# Weather Forecast API Mini-Project
Project Overview
This project retrieves and analyses weather forecast data for a user-specified location using public weather APIs. It demonstrates how to make HTTP requests in Python, convert JSON responses into structured data, handle API failures, and present forecast information using tables, summaries, and charts.

The project uses the Open-Meteo Geocoding API to identify a location and retrieve its coordinates. These coordinates are then used with the Open-Meteo Forecast API to retrieve daily weather information. MET Norway's Locationforecast API is also used as an alternative weather data source.

## 2. Project Objectives

The main objectives are to:

- Understand HTTP requests, response status codes, headers, and JSON data.
- Retrieve geographic coordinates from a location name.
- Obtain and analyse weather forecast data from public APIs.
- Present forecast results in a pandas DataFrame, summary, and chart.
- Implement timeouts, error handling, and retries with exponential backoff.
- Test the request-handling function without relying on a live internet connection.
- Consider API licensing, usage requirements, and location-data privacy.

## 3. Project Structure

```text
Weather forecast/
├── project1_Weather.ipynb
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   └── weather_api.py
└── tests/
    └── test_weather_api.py
```

The notebook contains the analysis, explanations, visualisations, and project report. The `src` directory contains reusable Python code for weather API requests. The `tests` directory contains automated tests for the request-handling function.

## 4. APIs Used

### Open-Meteo

The Open-Meteo Geocoding API converts a place name into geographic coordinates. The Forecast API uses those coordinates to retrieve daily weather variables, including maximum and minimum temperature, precipitation, wind speed, and weather codes.

Website: https://open-meteo.com/

### MET Norway Locationforecast

MET Norway provides an alternative forecast source. Its Locationforecast API returns forecast data for specified coordinates, including temperature, humidity, wind, pressure, cloud cover, and precipitation information.

Documentation: https://api.met.no/weatherapi/locationforecast/2.0/documentation

## 5. Requirements

The project requires Python and the following external libraries:

- `requests`
- `pandas`
- `matplotlib`

The dependencies are listed in `requirements.txt`.

## 6. Setup and Installation

Open a terminal in the project directory and install the required libraries:

```bash
python -m pip install -r requirements.txt
```

Open `project1_weather_api.ipynb` in VS Code with Jupyter support. Select a Python kernel with the required libraries installed.

Run the notebook from top to bottom using **Restart & Run All**. The notebook should execute without errors, provided the APIs are accessible and their services are available.

The current example uses Kampala as the location. Change the location variable if you want to retrieve forecasts for another place.

## 7. Running the Tests

From the project root directory, run:

```bash
python -m unittest discover -s tests -v
```

The tests use mocked HTTP responses, so they do not require live API access. They check successful requests, handling of HTTP 400 errors, retries after connection failures, retries after HTTP 503 errors, and rejection of invalid retry settings.

All five tests passed during development.

## 8. Reliability and Error Handling

The reusable function in `src/weather_api.py` sets a request timeout, checks HTTP responses, retries connection failures and server-side errors, and uses exponential backoff between attempts. It raises a custom `WeatherAPIError` when a request cannot be completed successfully.

The notebook also demonstrates invalid location searches, invalid coordinates, simulated connection failures, and very short timeouts. These examples show why API responses and failures need to be handled carefully.

## 9. Main Findings

The project demonstrates a complete workflow from a location name to a displayed weather forecast. Geocoding makes it possible to obtain coordinates from a place name, while the forecast APIs provide the weather variables used in the analysis.

The pandas DataFrame makes the forecast easier to inspect, while the summary and chart help communicate temperature and precipitation patterns. The reliability tests demonstrate that temporary failures can be retried and that client errors can be reported without unnecessary retries.

The notebook also highlights the importance of checking API licensing and usage conditions, providing appropriate attribution, identifying the application through the required User-Agent when using MET Norway, and considering the privacy implications of sending location queries to third-party services.

## 10. Limitations

Forecasts are estimates and can change as new observations and model outputs become available. API availability, response structure, rate limits, and terms of use may also change. The displayed forecast depends on the selected location and the data returned at the time the notebook is run.

The current tests focus on the reusable request function rather than validating every possible API response or the accuracy of the weather forecasts.

## 11. Sources and Attribution

- Open-Meteo: https://open-meteo.com/
- Open-Meteo Terms: https://open-meteo.com/en/terms
- MET Norway Locationforecast documentation: https://api.met.no/weatherapi/locationforecast/2.0/documentation
- MET Norway licensing: https://docs.api.met.no/doc/License.html
- MET Norway Terms of Service: https://api.met.no/doc/TermsOfService

Refer to the notebook for the detailed discussion of data flow, licensing, reliability, privacy, and the forecast results.