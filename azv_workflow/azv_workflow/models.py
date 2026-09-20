from typing import Literal
from pydantic import BaseModel, Field


class InvoiceLine(BaseModel):
    date: str | None = None
    tooth: str | None = None
    goa_number: str | None = None
    service: str
    quantity: float | None = None
    factor: float | None = None
    amount_eur: float | None = None


class InvoiceExtraction(BaseModel):
    invoice_number: str | None = None
    invoice_date: str | None = None
    treatment_period: str | None = None
    patient_name: str | None = None
    dentist_name: str | None = None
    insurer_reference: str | None = None
    total_invoice_eur: float | None = None
    lines: list[InvoiceLine] = Field(default_factory=list)
    extraction_notes: list[str] = Field(default_factory=list)


class AZVAssessment(BaseModel):
    classification: Literal["AZV_FALL", "KEIN_AZV_FALL", "UNKLAR"]
    confidence: float = Field(ge=0, le=1)
    reasons: list[str] = Field(default_factory=list)
    relevant_invoice_items: list[str] = Field(default_factory=list)
    relevant_contract_clauses: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    human_review_required: bool = True


class WorkflowResult(BaseModel):
    invoice: InvoiceExtraction
    assessment: AZVAssessment
