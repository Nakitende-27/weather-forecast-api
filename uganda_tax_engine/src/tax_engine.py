from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from abc import ABC, abstractmethod


class Money:
    def __init__(self, amount):
        self.amount = Decimal(str(amount)).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
    def __add__(self, other):
        return Money(self.amount + other.amount)
    def __sub__(self, other):
        return Money(self.amount - other.amount)
    def __mul__(self, other):
        return Money(self.amount * other)
    def __lt__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount < other.amount
    def __repr__(self):
        return f"Money({self.amount})"
    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount
    def __ge__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount >= other.amount


@dataclass
class TaxContext:
    gross_income: Money
    allowances: Money
    residency_status: str
    effective_date: date

@dataclass
class TaxResult:
    amount: Money

class Tax(ABC):
    @abstractmethod
    def calculate(self, ctx: TaxContext) -> TaxResult:
        pass

class TaxError(Exception):
    pass

class InvalidIncomeError(TaxError):
    pass

class NoScheduleForDateError(TaxError):
    pass

class PAYE(Tax):
    def calculate(self, ctx: TaxContext) -> TaxResult:
            income = ctx.gross_income.amount + ctx.allowances.amount
            if ctx.effective_date < date(2026, 7, 1):
                raise NoScheduleForDateError(
                    "This PAYE schedule applies from 1 July 2026"
                )

            if ctx.residency_status == "resident":
             return self._calculate_resident(income)

            elif ctx.residency_status == "non-resident":
                return self._calculate_nonresident(income)

            else:
                raise ValueError(
                "residency_status must be 'resident' or 'non-resident'"
            )
    def _calculate_resident(self, income: Decimal) -> TaxResult:
            if income < 0:
                raise InvalidIncomeError("Income cannot be negative")

            if income <= Decimal("335000"):
                tax = Money("0")

            elif income <= Decimal("410000"):
                taxable_amount = income - Decimal("335000")
                tax = Money(taxable_amount * Decimal("0.20"))
            elif income <= Decimal("485000"):
                taxable_amount = income - Decimal("410000")
                tax = Money(
                Decimal("15000") + taxable_amount * Decimal("0.25"))
            elif income <= Decimal("10000000"):
                taxable_amount = income - Decimal("485000")
                tax = Money(
                Decimal("33750") + taxable_amount * Decimal("0.30"))

            else:
                taxable_amount = income - Decimal("10000000")
                tax = Money(
                Decimal("2888250") + taxable_amount * Decimal("0.10"))
                
            return TaxResult(amount=tax)
    def _calculate_nonresident(self, income: Decimal) -> TaxResult:
        if income < 0:
            raise InvalidIncomeError("Income cannot be negative")

        if income <= Decimal("335000"):
            tax = Money(income * Decimal("0.10"))

        elif income <= Decimal("410000"):
            taxable_amount = income - Decimal("335000")
            tax = Money(
                Decimal("33500") + taxable_amount * Decimal("0.20")
            )

        elif income <= Decimal("10000000"):
            taxable_amount = income - Decimal("410000")
            tax = Money(
                Decimal("48500") + taxable_amount * Decimal("0.30")
            )

        else:
            taxable_amount = income - Decimal("10000000")
            tax = Money(
                Decimal("2925500") + taxable_amount * Decimal("0.10")
            )

        return TaxResult(amount=tax)


class NSSF:
    def __init__(self):
        self.employee_rate = Decimal("0.05")
        self.employer_rate = Decimal("0.10")
    def calculate(self, gross_income: Money) -> dict:
        if gross_income.amount < 0:
            raise InvalidIncomeError("Income cannot be negative")

        employee_contribution = Money(
            gross_income.amount * self.employee_rate
        )

        employer_contribution = Money(
            gross_income.amount * self.employer_rate
        )

        return {
            "employee": employee_contribution,
            "employer": employer_contribution
        }

class LST:
    def __init__(self, amount=0):
        self.amount = Money(amount)

    def calculate(self) -> Money:
        return self.amount


class Payroll:
    def __init__(self, paye, nssf, lst):
        self.paye = paye
        self.nssf = nssf
        self.lst = lst

    def calculate(self, ctx: TaxContext) -> dict:
        nssf_result = self.nssf.calculate(ctx.gross_income)
        lst_amount = self.lst.calculate()
        paye_result = self.paye.calculate(ctx)

        total_earnings = ctx.gross_income + ctx.allowances

        net_pay = (
            total_earnings
            - nssf_result["employee"]
            - lst_amount
            - paye_result.amount
        )

        return {
            "basic_salary": ctx.gross_income,
            "allowances": ctx.allowances,
            "total_earnings": total_earnings,
            "employee_nssf": nssf_result["employee"],
            "employer_nssf": nssf_result["employer"],
            "lst": lst_amount,
            "paye": paye_result.amount,
            "net_pay": net_pay
        }



class VAT:
    def __init__(self):
        self.standard_rate = Decimal("0.18")

    def calculate(self, invoices: list) -> dict:
        output_vat = Money("0")
        input_vat = Money("0")

        for invoice in invoices:
            amount = invoice["amount"].amount
            category = invoice["category"]
            invoice_type = invoice["invoice_type"]

            if category == "standard-rated":
                tax_amount = Money(amount * self.standard_rate)
            elif category in ("zero-rated", "exempt"):
                tax_amount = Money("0")
            else:
                raise ValueError("Invalid VAT category")

            if invoice_type == "sale":
                output_vat = output_vat + tax_amount
            elif invoice_type == "purchase":
                if invoice.get("input_vat_eligible", False):
                    input_vat = input_vat + tax_amount
            else:
                raise ValueError("Invalid invoice type")

        net_vat_payable = output_vat - input_vat

        return {
            "output_vat": output_vat,
            "input_vat": input_vat,
            "net_vat_payable": net_vat_payable
        }

class CorporateTax:
    def __init__(self):
        self.tax_rate = Decimal("0.30")

    def calculate(self, revenue: Money, allowable_deductions: Money) -> dict:
        if revenue.amount < 0:
            raise InvalidIncomeError("Revenue cannot be negative")

        if allowable_deductions.amount < 0:
            raise ValueError("Allowable deductions cannot be negative")

        taxable_profit = revenue - allowable_deductions

        # A company with no taxable profit should not have negative tax.
        if taxable_profit.amount < 0:
            taxable_profit = Money("0")

        tax_payable = Money(taxable_profit.amount * self.tax_rate)

        return {
            "taxable_profit": taxable_profit,
            "tax_payable": tax_payable
        }


class WithholdingTax:
    def __init__(self):
        self.tax_rate = Decimal("0.06")
    def calculate(self, payment: Money) -> dict:
        if payment.amount < 0:
            raise InvalidIncomeError("Payment cannot be negative")

        tax_withheld = Money(payment.amount * self.tax_rate)
        net_payment = payment - tax_withheld

        return {
            "tax_withheld": tax_withheld,
            "net_payment": net_payment
        }
