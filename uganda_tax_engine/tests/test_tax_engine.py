import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from hypothesis import given, strategies as st

# Make the src folder available when tests run independently.
PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "src"))

from tax_engine import Money, TaxContext, PAYE, NSSF, VAT, CorporateTax, WithholdingTax, Payroll, LST, InvalidIncomeError


class TestPAYE(unittest.TestCase):

    def setUp(self):
        self.paye = PAYE()

    def calculate_paye(self, income):
        context = TaxContext(
            gross_income=Money(income),
            allowances=Money(0),
            residency_status="resident",
            effective_date=date(2026, 10, 1)
        )
        return self.paye.calculate(context).amount.amount

    def test_resident_paye_boundaries(self):
        cases = [
            (335000, Decimal("0.00")),
            (335001, Decimal("0.20")),
            (410000, Decimal("15000.00")),
            (485000, Decimal("33750.00")),
            (10000000, Decimal("2888250.00")),
            (10000001, Decimal("2888250.10")),
        ]

        for income, expected_tax in cases:
            with self.subTest(income=income):
                self.assertEqual(
                    self.calculate_paye(income),
                    expected_tax
                )


@given(st.integers(min_value=0, max_value=20_000_000))
def test_paye_is_non_negative(income):
    context = TaxContext(
        gross_income=Money(income),
        allowances=Money(0),
        residency_status="resident",
        effective_date=date(2026, 10, 1)
    )

    tax = PAYE().calculate(context).amount.amount
    assert tax >= Decimal("0.00")


@given(
    st.integers(min_value=0, max_value=20_000_000),
    st.integers(min_value=0, max_value=20_000_000)
)
def test_paye_is_monotonic(income_a, income_b):
    lower_income, higher_income = sorted([income_a, income_b])

    lower_context = TaxContext(
        gross_income=Money(lower_income),
        allowances=Money(0),
        residency_status="resident",
        effective_date=date(2026, 10, 1)
    )
    higher_context = TaxContext(
        gross_income=Money(higher_income),
        allowances=Money(0),
        residency_status="resident",
        effective_date=date(2026, 10, 1)
    )

    lower_tax = PAYE().calculate(lower_context).amount.amount
    higher_tax = PAYE().calculate(higher_context).amount.amount

    assert higher_tax >= lower_tax


@given(st.integers(min_value=0, max_value=20_000_000))
def test_paye_does_not_exceed_income(income):
    context = TaxContext(
        gross_income=Money(income),
        allowances=Money(0),
        residency_status="resident",
        effective_date=date(2026, 10, 1)
    )

    tax = PAYE().calculate(context).amount.amount
    assert tax <= Decimal(str(income))


if __name__ == "__main__":
    unittest.main()


class TestNSSF(unittest.TestCase):

    def setUp(self):
        self.nssf = NSSF()

    def test_employee_and_employer_contributions(self):
        result = self.nssf.calculate(Money(500000))

        self.assertEqual(
            result["employee"].amount,
            Decimal("25000.00")
        )
        self.assertEqual(
            result["employer"].amount,
            Decimal("50000.00")
        )

    def test_zero_income(self):
        result = self.nssf.calculate(Money(0))

        self.assertEqual(
            result["employee"].amount,
            Decimal("0.00")
        )
        self.assertEqual(
            result["employer"].amount,
            Decimal("0.00")
        )

    def test_negative_income_is_rejected(self):
        with self.assertRaises(InvalidIncomeError):
            self.nssf.calculate(Money(-1000))


class TestVAT(unittest.TestCase):

    def setUp(self):
        self.vat = VAT()

    def test_vat_calculations(self):
        invoices = [
            {
                "amount": Money(100000),
                "category": "standard-rated",
                "invoice_type": "sale"
            },
            {
                "amount": Money(50000),
                "category": "standard-rated",
                "invoice_type": "purchase",
                "input_vat_eligible": True
            },
            {
                "amount": Money(30000),
                "category": "standard-rated",
                "invoice_type": "purchase",
                "input_vat_eligible": False
            },
            {
                "amount": Money(200000),
                "category": "zero-rated",
                "invoice_type": "sale"
            },
            {
                "amount": Money(150000),
                "category": "exempt",
                "invoice_type": "sale"
            }
        ]

        result = self.vat.calculate(invoices)

        self.assertEqual(
            result["output_vat"].amount,
            Decimal("18000.00")
        )
        self.assertEqual(
            result["input_vat"].amount,
            Decimal("9000.00")
        )
        self.assertEqual(
            result["net_vat_payable"].amount,
            Decimal("9000.00")
        )

    def test_zero_rated_and_exempt_invoices_have_no_vat(self):
        invoices = [
            {
                "amount": Money(100000),
                "category": "zero-rated",
                "invoice_type": "sale"
            },
            {
                "amount": Money(100000),
                "category": "exempt",
                "invoice_type": "sale"
            }
        ]

        result = self.vat.calculate(invoices)

        self.assertEqual(
            result["output_vat"].amount,
            Decimal("0.00")
        )

    def test_invalid_vat_category_is_rejected(self):
        invoices = [{
            "amount": Money(100000),
            "category": "reduced-rated",
            "invoice_type": "sale"
        }]

        with self.assertRaises(ValueError):
            self.vat.calculate(invoices)

    def test_invalid_invoice_type_is_rejected(self):
        invoices = [{
            "amount": Money(100000),
            "category": "standard-rated",
            "invoice_type": "refund"
        }]

        with self.assertRaises(ValueError):
            self.vat.calculate(invoices)


class TestCorporateTax(unittest.TestCase):

    def setUp(self):
        self.corporate_tax = CorporateTax()

    def test_profitable_company(self):
        result = self.corporate_tax.calculate(
            revenue=Money(100000000),
            allowable_deductions=Money(60000000)
        )

        self.assertEqual(
            result["taxable_profit"].amount,
            Decimal("40000000.00")
        )
        self.assertEqual(
            result["tax_payable"].amount,
            Decimal("12000000.00")
        )

    def test_deductions_exceed_revenue(self):
        result = self.corporate_tax.calculate(
            revenue=Money(50000000),
            allowable_deductions=Money(60000000)
        )

        self.assertEqual(
            result["taxable_profit"].amount,
            Decimal("0.00")
        )
        self.assertEqual(
            result["tax_payable"].amount,
            Decimal("0.00")
        )

    def test_negative_revenue_is_rejected(self):
        with self.assertRaises(InvalidIncomeError):
            self.corporate_tax.calculate(
                revenue=Money(-1000),
                allowable_deductions=Money(0)
            )

    def test_negative_deductions_are_rejected(self):
        with self.assertRaises(ValueError):
            self.corporate_tax.calculate(
                revenue=Money(1000000),
                allowable_deductions=Money(-1000)
            )


class TestWithholdingTax(unittest.TestCase):

    def setUp(self):
        self.withholding_tax = WithholdingTax()

    def test_tax_withheld_and_net_payment(self):
        result = self.withholding_tax.calculate(Money(1000000))

        self.assertEqual(
            result["tax_withheld"].amount,
            Decimal("60000.00")
        )
        self.assertEqual(
            result["net_payment"].amount,
            Decimal("940000.00")
        )

    def test_zero_payment(self):
        result = self.withholding_tax.calculate(Money(0))

        self.assertEqual(
            result["tax_withheld"].amount,
            Decimal("0.00")
        )
        self.assertEqual(
            result["net_payment"].amount,
            Decimal("0.00")
        )

    def test_negative_payment_is_rejected(self):
        with self.assertRaises(InvalidIncomeError):
            self.withholding_tax.calculate(Money(-1000))


class TestPayroll(unittest.TestCase):

    def test_net_pay_includes_allowances(self):
        payroll = Payroll(
            paye=PAYE(),
            nssf=NSSF(),
            lst=LST()
        )

        context = TaxContext(
            gross_income=Money(500000),
            allowances=Money(100000),
            residency_status="resident",
            effective_date=date(2026, 10, 1)
        )

        result = payroll.calculate(context)

        self.assertEqual(
            result["total_earnings"].amount,
            Decimal("600000.00")
        )
        self.assertEqual(
            result["employee_nssf"].amount,
            Decimal("25000.00")
        )
        self.assertEqual(
            result["paye"].amount,
            Decimal("68250.00")
        )
        self.assertEqual(
            result["net_pay"].amount,
            Decimal("506750.00")
        )
        self.assertEqual(
            result["employer_nssf"].amount,
            Decimal("50000.00")
        )
