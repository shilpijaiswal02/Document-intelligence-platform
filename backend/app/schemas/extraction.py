from typing import Any

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    source_text: str | None = None
    page_number: int | None = None


class LineItem(BaseModel):
    item_number: str | None = None
    description: str | None = None
    hsn_sac: str | None = None
    quantity: float | None = None
    unit: str | None = None
    rate: float | None = None
    discount: float | None = None
    amount: float | None = None
    tax_rate: float | None = None
    tax_amount: float | None = None
    net_amount: float | None = None
    gross_amount: float | None = None


class DocumentExtraction(BaseModel):
    header: dict[str, Any] = Field(
        default_factory=dict
    )

    dates: list[dict[str, Any]] = Field(
        default_factory=list
    )

    parties: dict[str, Any] = Field(
        default_factory=dict
    )

    currency: str | None = None

    totals: dict[str, Any] = Field(
        default_factory=dict
    )

    line_items: list[LineItem] = Field(
        default_factory=list
    )

    comparative_periods: list[dict[str, Any]] = Field(
        default_factory=list
    )

    tables: list[dict[str, Any]] = Field(
        default_factory=list
    )

    additional_fields: dict[str, Any] = Field(
        default_factory=dict
    )

    evidence: list[Evidence] = Field(
        default_factory=list
    )