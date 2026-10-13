# Uganda Tax Engine

## 1. Project Overview

The Uganda Tax Engine is a Python-based project demonstrating the calculation of selected Ugandan taxes using object-oriented programming, Decimal-based monetary calculations, input validation, and automated testing.

The project covers PAYE, NSSF contributions, VAT, corporate tax, withholding tax, and a basic payroll calculation.

## 2. Features

- Resident and nonresident PAYE calculations.
- Employee and employer NSSF contributions.
- VAT calculations for standard-rated, zero-rated, and exempt transactions.
- Corporate tax based on revenue and allowable deductions.
- Withholding tax extension.
- Payroll calculations combining PAYE, NSSF, LST, and net pay.
- Monetary calculations using Python's Decimal type.
- Boundary, validation, and Hypothesis property tests.

## 3. Requirements

- Python 3
- pandas
- hypothesis
- Jupyter Notebook

## 4. Running the Project

1. Install Python and Jupyter Notebook.
2. Install dependencies using `pip install -r requirements.txt`.
3. Open `project2_uganda_tax.ipynb` in Jupyter Notebook.
4. Run the notebook cells in order.
5. Review the calculation outputs and test results.

## 5. Testing

Tests cover resident and nonresident PAYE boundaries, PAYE properties, invalid inputs, NSSF, VAT, corporate tax, withholding tax, and payroll calculations.

## 6. Limitations

This is an educational implementation, not a production payroll or tax filing system. Tax rates, effective dates, taxable allowances, VAT deductions, and other statutory rules must be verified against current legislation and official guidance. Some calculations are simplified for demonstration.

## 7. Sources

- Uganda Revenue Authority: https://ura.go.ug/
- National Social Security Fund Uganda: https://www.nssfug.org/

## 8. Summary

This project demonstrates how object-oriented programming, reusable classes, precise monetary calculations, validation, and automated tests can be used to develop a basic tax calculation system.
