# Python Mini-Projects — OOP Coursework

This repository contains two Python mini-projects developed for Object-Oriented Programming (OOP) coursework. The projects demonstrate API integration, data analysis, object-oriented design, error handling, and automated testing.

## Project 1: Weather Forecast API

**Notebook:** `Project1_Weather.ipynb`

This project retrieves weather forecasts for a user-specified location using the Open-Meteo Geocoding and Forecast APIs, with MET Norway's Locationforecast API as an alternative data source.

Key features:
- HTTP requests using Python's `urllib` and `requests`.
- Location geocoding and forecast retrieval.
- JSON parsing and presentation using pandas DataFrames.
- Forecast summaries and visualisations.
- Timeouts, exception handling, retries, and exponential backoff.
- Automated tests using mocked HTTP responses.

Reusable code is in `src/weather_api.py`, with tests in `tests/test_weather_api.py`.

## Project 2: Uganda Tax Engine

**Notebook:** `uganda_tax_engine/project2_uganda_tax.ipynb`

This project implements a basic Uganda tax calculation engine using object-oriented programming and precise monetary calculations.

Key features:
- PAYE calculations.
- Employee and employer NSSF contributions.
- Local Service Tax (LST).
- VAT calculations.
- Corporate tax and withholding tax.
- Payroll calculations.
- Input validation, custom exceptions, and automated tests.

Reusable classes and tax logic are in `uganda_tax_engine/src/tax_engine.py`, with tests in `uganda_tax_engine/tests/test_tax_engine.py`.

The tax engine is an educational implementation, not a production payroll or tax filing system. Statutory rates and rules should be verified against current official guidance.

## Repository Structure

```text
Weather forecast/
├── Project1_Weather.ipynb
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   └── weather_api.py
├── tests/
│   └── test_weather_api.py
└── uganda_tax_engine/
    ├── project2_uganda_tax.ipynb
    ├── README.md
    ├── requirements.txt
    ├── src/
    │   └── tax_engine.py
    └── tests/
        └── test_tax_engine.py
```

## Requirements

- Python 3
- Jupyter Notebook or VS Code with Jupyter support
- `requests`
- `pandas`
- `matplotlib`
- `hypothesis`

Install the dependencies from the repository root:

```bash
python -m pip install -r requirements.txt
```

## Running the Projects

1. Clone or download this repository.
2. Install the dependencies using the command above.
3. Open `Project1_Weather.ipynb` and run the cells from top to bottom.
4. Open `uganda_tax_engine/project2_uganda_tax.ipynb` and run its cells from top to bottom.
5. Review each notebook's outputs, explanations, findings, and limitations.

Weather forecasts require internet access and available API services. The tax calculations and automated tests can be run locally.

## Running the Tests

From the repository root, run the weather API tests:

```bash
python -m unittest discover -s tests -v
```

Run the tax engine tests:

```bash
python -m unittest discover -s uganda_tax_engine/tests -p "test_tax_engine.py" -v
```

The weather tests use mocked HTTP responses, while the tax tests check calculations, boundaries, and invalid inputs.

## Sources

- Open-Meteo: https://open-meteo.com/
- MET Norway Locationforecast: https://api.met.no/weatherapi/locationforecast/2.0/documentation
- Uganda Revenue Authority: https://ura.go.ug/
- National Social Security Fund Uganda: https://www.nssfug.org/

## Academic Use and Limitations

These projects were developed for educational purposes. The results depend on the quality and availability of the underlying APIs, the assumptions made in the tax calculations, and the scope of the implemented tests. Consult the individual project notebooks and README files for detailed methods, findings, and limitations.