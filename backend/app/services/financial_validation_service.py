import math
import re
from typing import Any


TOLERANCE = 0.01


def first_present(*values):
    """
    Return the first value that is not None.

    Important:
    0 is a valid financial value and must NOT be treated as missing.
    """
    for value in values:
        if value is not None:
            return value
    return None


def to_number(value: Any) -> float | None:
    """
    Convert common financial number formats to float.

    Examples:
        1,234.50 -> 1234.50
        (500)    -> -500
        [500]    -> -500
        $ 1,000  -> 1000
        None     -> None
    """
    if value is None:
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if not isinstance(value, str):
        return None

    value = value.strip()

    if not value:
        return None

    is_negative = False

    # Parentheses/brackets represent negative values.
    if (
        (value.startswith("(") and value.endswith(")"))
        or (value.startswith("[") and value.endswith("]"))
    ):
        is_negative = True
        value = value[1:-1].strip()

    # Remove currency symbols and other non-numeric characters,
    # while preserving decimal signs and separators.
    value = re.sub(r"[^\d,.\-+]", "", value)

    if not value:
        return None

    # Handle numbers such as:
    # 1,234.56
    # 1.234,56
    # 1234,56
    if "," in value and "." in value:
        if value.rfind(",") > value.rfind("."):
            # European style: 1.234,56
            value = value.replace(".", "")
            value = value.replace(",", ".")
        else:
            # Standard style: 1,234.56
            value = value.replace(",", "")

    elif "," in value:
        parts = value.split(",")

        if len(parts) == 2 and len(parts[1]) <= 2:
            # Decimal comma: 1234,56
            value = value.replace(",", ".")
        else:
            # Thousands separator: 1,234
            value = value.replace(",", "")

    try:
        number = float(value)
    except ValueError:
        return None

    if is_negative:
        number = -abs(number)

    return number


def approximately_equal(
    calculated: float | None,
    reported: float | None,
    tolerance: float = TOLERANCE,
) -> bool:
    """
    Compare calculated and reported financial values.
    """
    if calculated is None or reported is None:
        return False

    return math.isclose(
        calculated,
        reported,
        abs_tol=tolerance,
        rel_tol=0.0,
    )


def create_check(
    formula: str,
    input_values: dict[str, Any],
    calculated_value: float | None,
    reported_value: float | None,
) -> dict[str, Any]:
    """
    Create a standard validation check.

    Missing required values result in NOT_APPLICABLE.
    """
    calculated = to_number(calculated_value)
    reported = to_number(reported_value)

    if calculated is None or reported is None:
        status = "NOT_APPLICABLE"
        variance = None
    else:
        variance = round(calculated - reported, 2)

        status = (
            "PASS"
            if approximately_equal(calculated, reported)
            else "FAIL"
        )

    return {
        "formula": formula,
        "input_values": input_values,
        "calculated_value": calculated,
        "reported_value": reported,
        "variance": variance,
        "status": status,
    }


def build_validation_result(
    checks: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Build the final validation result.

    Overall document status is FAILED only when at least one
    applicable check fails.
    """
    failed = any(check["status"] == "FAIL" for check in checks)

    return {
        "status": "FAILED" if failed else "PASS",
        "checks": checks,
        "tolerance": TOLERANCE,
    }


# ============================================================
# Generic helpers
# ============================================================

def get_numeric(data: dict[str, Any], *keys) -> float | None:
    """
    Return the first available numeric value from a dictionary.
    """
    values = []

    for key in keys:
        values.append(data.get(key))

    return to_number(first_present(*values))


def get_nested_numeric(
    data: dict[str, Any],
    container_key: str,
    *keys,
) -> float | None:
    """
    Read a numeric value from a nested dictionary.
    """
    container = data.get(container_key)

    if not isinstance(container, dict):
        return None

    return get_numeric(container, *keys)


def extract_period_values(
    period: dict[str, Any],
    *keys,
) -> float | None:
    """
    Extract a numeric value from a comparative period.
    """
    return get_numeric(period, *keys)


# ============================================================
# INVOICE VALIDATION
# ============================================================

def validate_invoice(data: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    totals = data.get("totals", {})

    if not isinstance(totals, dict):
        totals = {}

    line_items = data.get("line_items", [])

    if not isinstance(line_items, list):
        line_items = []

    # --------------------------------------------------------
    # 1. Quantity × Unit Price ≈ Line Total
    # --------------------------------------------------------

    for index, item in enumerate(line_items, start=1):
        if not isinstance(item, dict):
            continue

        quantity = get_numeric(
            item,
            "quantity",
            "qty",
        )

        unit_price = get_numeric(
            item,
            "rate",
            "unit_price",
            "unit_price_excluding_tax",
            "price",
        )

        line_total = get_numeric(
            item,
            "amount",
            "line_total",
            "net_amount",
            "gross_amount",
        )

        calculated_value = None

        if quantity is not None and unit_price is not None:
            calculated_value = quantity * unit_price

        checks.append(
            create_check(
                formula="Quantity × Unit Price ≈ Line Total",
                input_values={
                    "line_item": index,
                    "quantity": quantity,
                    "unit_price": unit_price,
                },
                calculated_value=calculated_value,
                reported_value=line_total,
            )
        )

    # --------------------------------------------------------
    # 2. Sum Line Totals ≈ Subtotal
    # --------------------------------------------------------

    subtotal = get_numeric(
        totals,
        "subtotal",
        "sub_total",
        "net_amount",
        "taxable_amount",
        "taxable_value",
    )

    line_totals = []

    for item in line_items:
        if not isinstance(item, dict):
            continue

        amount = get_numeric(
            item,
            "amount",
            "line_total",
            "net_amount",
        )

        if amount is not None:
            line_totals.append(amount)

    calculated_subtotal = (
        sum(line_totals)
        if line_totals and len(line_totals) == len(line_items)
        else None
    )

    checks.append(
        create_check(
            formula="Sum of Line Totals ≈ Subtotal",
            input_values={
                "line_totals": line_totals,
            },
            calculated_value=calculated_subtotal,
            reported_value=subtotal,
        )
    )

    # --------------------------------------------------------
    # 3. Taxable Amount + Tax ≈ Total
    #
    # Only applicable when the document explicitly provides
    # taxable amount/subtotal and tax and total.
    # --------------------------------------------------------

    taxable_amount = get_numeric(
        totals,
        "taxable_amount",
        "taxable_value",
        "subtotal",
        "sub_total",
        "net_amount",
    )

    tax_amount = get_numeric(
        totals,
        "total_tax_amount",
        "tax_amount",
        "tax",
        "vat",
        "gst",
    )

    total_amount = get_numeric(
        totals,
        "total",
        "total_amount",
        "gross_amount",
        "grand_total",
    )

    calculated_total = None

    if taxable_amount is not None and tax_amount is not None:
        calculated_total = taxable_amount + tax_amount

    checks.append(
        create_check(
            formula="Taxable Amount + Tax ≈ Total",
            input_values={
                "taxable_amount": taxable_amount,
                "tax_amount": tax_amount,
            },
            calculated_value=calculated_total,
            reported_value=total_amount,
        )
    )

    # --------------------------------------------------------
    # 4. Cash Paid - Total ≈ Change
    # --------------------------------------------------------

    cash_paid = get_numeric(
        totals,
        "cash_paid",
        "amount_paid",
        "paid_amount",
        "cash_received",
    )

    change = get_numeric(
        totals,
        "change",
        "change_due",
        "balance_change",
    )

    calculated_change = None

    if cash_paid is not None and total_amount is not None:
        calculated_change = cash_paid - total_amount

    checks.append(
        create_check(
            formula="Cash Paid - Total ≈ Change",
            input_values={
                "cash_paid": cash_paid,
                "total": total_amount,
            },
            calculated_value=calculated_change,
            reported_value=change,
        )
    )

    return build_validation_result(checks)


# ============================================================
# BALANCE SHEET VALIDATION
# ============================================================

def validate_balance_sheet(data: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    totals = data.get("totals", {})

    if not isinstance(totals, dict):
        totals = {}

    # --------------------------------------------------------
    # 1. Total Capital & Liabilities ≈ Total Assets
    # --------------------------------------------------------

    total_assets = get_numeric(
        totals,
        "total_assets",
        "assets",
    )

    total_capital_liabilities = get_numeric(
        totals,
        "total_capital_and_liabilities",
        "total_capital_liabilities",
        "capital_and_liabilities",
        "total_liabilities_and_equity",
    )

    checks.append(
        create_check(
            formula="Total Capital & Liabilities ≈ Total Assets",
            input_values={
                "total_capital_and_liabilities": total_capital_liabilities,
                "total_assets": total_assets,
            },
            calculated_value=total_capital_liabilities,
            reported_value=total_assets,
        )
    )

    # --------------------------------------------------------
    # 2. Sum Asset Components ≈ Total Assets
    # --------------------------------------------------------

    asset_components = data.get("asset_components")

    if asset_components is None:
        asset_components = data.get("assets")

    asset_values = []

    if isinstance(asset_components, dict):
        for value in asset_components.values():
            numeric_value = to_number(value)

            if numeric_value is not None:
                asset_values.append(numeric_value)

    elif isinstance(asset_components, list):
        for item in asset_components:
            if isinstance(item, dict):
                value = first_present(
                    item.get("amount"),
                    item.get("value"),
                    item.get("total"),
                )
            else:
                value = item

            numeric_value = to_number(value)

            if numeric_value is not None:
                asset_values.append(numeric_value)

    calculated_assets = (
        sum(asset_values)
        if asset_values
        else None
    )

    checks.append(
        create_check(
            formula="Sum of Asset Components ≈ Total Assets",
            input_values={
                "asset_components": asset_values,
            },
            calculated_value=calculated_assets,
            reported_value=total_assets,
        )
    )

    # --------------------------------------------------------
    # 3. Sum Capital & Liability Components ≈ Total
    # --------------------------------------------------------

    liability_components = data.get(
        "capital_and_liability_components"
    )

    if liability_components is None:
        liability_components = data.get(
            "liability_components"
        )

    liability_values = []

    if isinstance(liability_components, dict):
        for value in liability_components.values():
            numeric_value = to_number(value)

            if numeric_value is not None:
                liability_values.append(numeric_value)

    elif isinstance(liability_components, list):
        for item in liability_components:
            if isinstance(item, dict):
                value = first_present(
                    item.get("amount"),
                    item.get("value"),
                    item.get("total"),
                )
            else:
                value = item

            numeric_value = to_number(value)

            if numeric_value is not None:
                liability_values.append(numeric_value)

    calculated_liabilities = (
        sum(liability_values)
        if liability_values
        else None
    )

    checks.append(
        create_check(
            formula=(
                "Sum of Capital & Liability Components "
                "≈ Total Capital & Liabilities"
            ),
            input_values={
                "capital_and_liability_components": liability_values,
            },
            calculated_value=calculated_liabilities,
            reported_value=total_capital_liabilities,
        )
    )

    # --------------------------------------------------------
    # Comparative periods
    # --------------------------------------------------------

    comparative_periods = data.get("comparative_periods", [])

    if isinstance(comparative_periods, list):

        for period in comparative_periods:

            if not isinstance(period, dict):
                continue

            period_name = first_present(
                period.get("period"),
                period.get("year"),
                period.get("date"),
                "comparative_period",
            )

            period_assets = get_numeric(
                period,
                "total_assets",
                "assets",
            )

            period_capital_liabilities = get_numeric(
                period,
                "total_capital_and_liabilities",
                "total_capital_liabilities",
                "capital_and_liabilities",
                "total_liabilities_and_equity",
            )

            checks.append(
                create_check(
                    formula=(
                        "Comparative Period: "
                        "Total Capital & Liabilities ≈ Total Assets"
                    ),
                    input_values={
                        "period": period_name,
                        "total_capital_and_liabilities": (
                            period_capital_liabilities
                        ),
                    },
                    calculated_value=period_capital_liabilities,
                    reported_value=period_assets,
                )
            )

    return build_validation_result(checks)


# ============================================================
# PROFIT & LOSS VALIDATION
# ============================================================

def validate_profit_and_loss(
    data: dict[str, Any],
) -> dict[str, Any]:

    checks: list[dict[str, Any]] = []

    totals = data.get("totals", {})

    if not isinstance(totals, dict):
        totals = {}

    # --------------------------------------------------------
    # 1. Interest Earned + Other Income ≈ Total Income
    # --------------------------------------------------------

    interest_earned = get_numeric(
        totals,
        "interest_earned",
        "interest_income",
    )

    other_income = get_numeric(
        totals,
        "other_income",
    )

    total_income = get_numeric(
        totals,
        "total_income",
    )

    calculated_income = None

    if interest_earned is not None and other_income is not None:
        calculated_income = interest_earned + other_income

    checks.append(
        create_check(
            formula="Interest Earned + Other Income ≈ Total Income",
            input_values={
                "interest_earned": interest_earned,
                "other_income": other_income,
            },
            calculated_value=calculated_income,
            reported_value=total_income,
        )
    )

    # --------------------------------------------------------
    # 2. Interest Expended + Operating Expenses
    #    + Provisions & Contingencies ≈ Total Expenditure
    # --------------------------------------------------------

    interest_expended = get_numeric(
        totals,
        "interest_expended",
        "interest_expense",
    )

    operating_expenses = get_numeric(
        totals,
        "operating_expenses",
        "operating_expense",
    )

    provisions = get_numeric(
        totals,
        "provisions_and_contingencies",
        "provisions",
        "contingencies",
    )

    total_expenditure = get_numeric(
        totals,
        "total_expenditure",
        "total_expenses",
        "total_expense",
    )

    calculated_expenditure = None

    if (
        interest_expended is not None
        and operating_expenses is not None
        and provisions is not None
    ):
        calculated_expenditure = (
            interest_expended
            + operating_expenses
            + provisions
        )

    checks.append(
        create_check(
            formula=(
                "Interest Expended + Operating Expenses + "
                "Provisions & Contingencies ≈ Total Expenditure"
            ),
            input_values={
                "interest_expended": interest_expended,
                "operating_expenses": operating_expenses,
                "provisions_and_contingencies": provisions,
            },
            calculated_value=calculated_expenditure,
            reported_value=total_expenditure,
        )
    )

    # --------------------------------------------------------
    # 3. Total Income - Total Expenditure
    #    ≈ Consolidated Net Profit before Minority Interest
    # --------------------------------------------------------

    net_profit_before_minority = get_numeric(
        totals,
        "consolidated_net_profit_before_minority_interest",
        "net_profit_before_minority_interest",
        "profit_before_minority_interest",
    )

    calculated_net_profit = None

    if total_income is not None and total_expenditure is not None:
        calculated_net_profit = (
            total_income - total_expenditure
        )

    checks.append(
        create_check(
            formula=(
                "Total Income - Total Expenditure ≈ "
                "Consolidated Net Profit before Minority Interest"
            ),
            input_values={
                "total_income": total_income,
                "total_expenditure": total_expenditure,
            },
            calculated_value=calculated_net_profit,
            reported_value=net_profit_before_minority,
        )
    )

    # --------------------------------------------------------
    # 4. Profit before Minority Interest - Minority Interest
    #    ≈ Consolidated Net Profit attributable to Group
    # --------------------------------------------------------

    minority_interest = get_numeric(
        totals,
        "minority_interest",
        "minority_interest_expense",
    )

    net_profit_attributable = get_numeric(
        totals,
        "consolidated_net_profit_attributable_to_group",
        "net_profit_attributable_to_group",
        "consolidated_net_profit",
        "net_profit",
    )

    calculated_attributable_profit = None

    if (
        net_profit_before_minority is not None
        and minority_interest is not None
    ):
        calculated_attributable_profit = (
            net_profit_before_minority - minority_interest
        )

    checks.append(
        create_check(
            formula=(
                "Profit before Minority Interest - Minority Interest "
                "≈ Consolidated Net Profit attributable to Group"
            ),
            input_values={
                "profit_before_minority_interest": (
                    net_profit_before_minority
                ),
                "minority_interest": minority_interest,
            },
            calculated_value=calculated_attributable_profit,
            reported_value=net_profit_attributable,
        )
    )

    # --------------------------------------------------------
    # 5. Current Profit + Brought Forward Profit
    #    ≈ Total Available for Appropriation
    # --------------------------------------------------------

    current_profit = get_numeric(
        totals,
        "current_profit",
        "profit_for_the_year",
        "current_year_profit",
    )

    brought_forward_profit = get_numeric(
        totals,
        "brought_forward_profit",
        "profit_brought_forward",
        "retained_earnings_brought_forward",
    )

    total_available_appropriation = get_numeric(
        totals,
        "total_available_for_appropriation",
        "total_available_for_appropriation",
    )

    calculated_appropriation = None

    if (
        current_profit is not None
        and brought_forward_profit is not None
    ):
        calculated_appropriation = (
            current_profit + brought_forward_profit
        )

    checks.append(
        create_check(
            formula=(
                "Current Profit + Brought Forward Profit "
                "≈ Total Available for Appropriation"
            ),
            input_values={
                "current_profit": current_profit,
                "brought_forward_profit": brought_forward_profit,
            },
            calculated_value=calculated_appropriation,
            reported_value=total_available_appropriation,
        )
    )

    # --------------------------------------------------------
    # Comparative periods
    # --------------------------------------------------------

    comparative_periods = data.get("comparative_periods", [])

    if isinstance(comparative_periods, list):

        for period in comparative_periods:

            if not isinstance(period, dict):
                continue

            period_name = first_present(
                period.get("period"),
                period.get("year"),
                period.get("date"),
                "comparative_period",
            )

            period_interest_earned = get_numeric(
                period,
                "interest_earned",
                "interest_income",
            )

            period_other_income = get_numeric(
                period,
                "other_income",
            )

            period_total_income = get_numeric(
                period,
                "total_income",
            )

            calculated_period_income = None

            if (
                period_interest_earned is not None
                and period_other_income is not None
            ):
                calculated_period_income = (
                    period_interest_earned
                    + period_other_income
                )

            checks.append(
                create_check(
                    formula=(
                        "Comparative Period: "
                        "Interest Earned + Other Income "
                        "≈ Total Income"
                    ),
                    input_values={
                        "period": period_name,
                        "interest_earned": period_interest_earned,
                        "other_income": period_other_income,
                    },
                    calculated_value=calculated_period_income,
                    reported_value=period_total_income,
                )
            )

            period_interest_expended = get_numeric(
                period,
                "interest_expended",
                "interest_expense",
            )

            period_operating_expenses = get_numeric(
                period,
                "operating_expenses",
                "operating_expense",
            )

            period_provisions = get_numeric(
                period,
                "provisions_and_contingencies",
                "provisions",
                "contingencies",
            )

            period_total_expenditure = get_numeric(
                period,
                "total_expenditure",
                "total_expenses",
                "total_expense",
            )

            calculated_period_expenditure = None

            if (
                period_interest_expended is not None
                and period_operating_expenses is not None
                and period_provisions is not None
            ):
                calculated_period_expenditure = (
                    period_interest_expended
                    + period_operating_expenses
                    + period_provisions
                )

            checks.append(
                create_check(
                    formula=(
                        "Comparative Period: "
                        "Interest Expended + Operating Expenses + "
                        "Provisions & Contingencies "
                        "≈ Total Expenditure"
                    ),
                    input_values={
                        "period": period_name,
                        "interest_expended": period_interest_expended,
                        "operating_expenses": period_operating_expenses,
                        "provisions_and_contingencies": (
                            period_provisions
                        ),
                    },
                    calculated_value=calculated_period_expenditure,
                    reported_value=period_total_expenditure,
                )
            )

    return build_validation_result(checks)


# ============================================================
# CASH FLOW VALIDATION
# ============================================================

def validate_cash_flow(
    data: dict[str, Any],
) -> dict[str, Any]:

    checks: list[dict[str, Any]] = []

    totals = data.get("totals", {})

    if not isinstance(totals, dict):
        totals = {}

    # --------------------------------------------------------
    # 1. Operating + Investing + Financing
    #    + FX Adjustment ≈ Net Increase in Cash
    # --------------------------------------------------------

    operating = get_numeric(
        totals,
        "operating_activities",
        "cash_from_operating_activities",
        "operating_cash_flow",
    )

    investing = get_numeric(
        totals,
        "investing_activities",
        "cash_from_investing_activities",
        "investing_cash_flow",
    )

    financing = get_numeric(
        totals,
        "financing_activities",
        "cash_from_financing_activities",
        "financing_cash_flow",
    )

    fx_adjustment = get_numeric(
        totals,
        "foreign_exchange_adjustment",
        "fx_adjustment",
        "foreign_exchange_translation_adjustment",
        "translation_adjustment",
    )

    net_increase = get_numeric(
        totals,
        "net_increase_in_cash",
        "net_change_in_cash",
        "increase_decrease_in_cash",
    )

    calculated_net_increase = None

    if (
        operating is not None
        and investing is not None
        and financing is not None
        and fx_adjustment is not None
    ):
        calculated_net_increase = (
            operating
            + investing
            + financing
            + fx_adjustment
        )

    checks.append(
        create_check(
            formula=(
                "Operating + Investing + Financing + "
                "FX/Translation Adjustment ≈ Net Increase in Cash"
            ),
            input_values={
                "operating_activities": operating,
                "investing_activities": investing,
                "financing_activities": financing,
                "fx_adjustment": fx_adjustment,
            },
            calculated_value=calculated_net_increase,
            reported_value=net_increase,
        )
    )

    # --------------------------------------------------------
    # 2. Opening Cash + Net Increase + Cash Acquired /
    #    Other Adjustments ≈ Closing Cash
    # --------------------------------------------------------

    opening_cash = get_numeric(
        totals,
        "opening_cash",
        "cash_at_beginning",
        "cash_and_cash_equivalents_at_beginning",
    )

    cash_acquired = get_numeric(
        totals,
        "cash_acquired",
        "cash_acquired_from_business_combinations",
        "other_adjustments",
        "cash_adjustments",
    )

    closing_cash = get_numeric(
        totals,
        "closing_cash",
        "cash_at_end",
        "cash_and_cash_equivalents_at_end",
    )

    calculated_closing_cash = None

    if (
        opening_cash is not None
        and net_increase is not None
        and cash_acquired is not None
    ):
        calculated_closing_cash = (
            opening_cash
            + net_increase
            + cash_acquired
        )

    checks.append(
        create_check(
            formula=(
                "Opening Cash + Net Increase + "
                "Cash Acquired/Other Adjustments ≈ Closing Cash"
            ),
            input_values={
                "opening_cash": opening_cash,
                "net_increase": net_increase,
                "cash_acquired_or_other_adjustments": cash_acquired,
            },
            calculated_value=calculated_closing_cash,
            reported_value=closing_cash,
        )
    )

    # --------------------------------------------------------
    # Comparative periods
    # --------------------------------------------------------

    comparative_periods = data.get("comparative_periods", [])

    if isinstance(comparative_periods, list):

        for period in comparative_periods:

            if not isinstance(period, dict):
                continue

            period_name = first_present(
                period.get("period"),
                period.get("year"),
                period.get("date"),
                "comparative_period",
            )

            period_operating = get_numeric(
                period,
                "operating_activities",
                "cash_from_operating_activities",
                "operating_cash_flow",
            )

            period_investing = get_numeric(
                period,
                "investing_activities",
                "cash_from_investing_activities",
                "investing_cash_flow",
            )

            period_financing = get_numeric(
                period,
                "financing_activities",
                "cash_from_financing_activities",
                "financing_cash_flow",
            )

            period_fx = get_numeric(
                period,
                "foreign_exchange_adjustment",
                "fx_adjustment",
                "foreign_exchange_translation_adjustment",
                "translation_adjustment",
            )

            period_net_increase = get_numeric(
                period,
                "net_increase_in_cash",
                "net_change_in_cash",
                "increase_decrease_in_cash",
            )

            calculated_period_net_increase = None

            if (
                period_operating is not None
                and period_investing is not None
                and period_financing is not None
                and period_fx is not None
            ):
                calculated_period_net_increase = (
                    period_operating
                    + period_investing
                    + period_financing
                    + period_fx
                )

            checks.append(
                create_check(
                    formula=(
                        "Comparative Period: "
                        "Operating + Investing + Financing + "
                        "FX/Translation Adjustment "
                        "≈ Net Increase in Cash"
                    ),
                    input_values={
                        "period": period_name,
                        "operating_activities": period_operating,
                        "investing_activities": period_investing,
                        "financing_activities": period_financing,
                        "fx_adjustment": period_fx,
                    },
                    calculated_value=calculated_period_net_increase,
                    reported_value=period_net_increase,
                )
            )

    return build_validation_result(checks)


# ============================================================
# MAIN DISPATCHER
# ============================================================

def validate_financial_document(
    document_type: str,
    data: dict[str, Any],
) -> dict[str, Any]:

    if document_type == "invoice":
        return validate_invoice(data)

    if document_type == "balance_sheet":
        return validate_balance_sheet(data)

    if document_type == "profit_and_loss":
        return validate_profit_and_loss(data)

    if document_type == "cash_flow_statement":
        return validate_cash_flow(data)

    return {
        "status": "FAILED",
        "checks": [],
        "tolerance": TOLERANCE,
        "error": f"Unsupported document type: {document_type}",
    }