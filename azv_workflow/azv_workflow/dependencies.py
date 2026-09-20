from dataclasses import dataclass

from .models import InvoiceExtraction


@dataclass(frozen=True)
class WorkflowDeps:
    contract_text: str


@dataclass
class CheckerDeps:
    contract_text: str
    invoice_content: list
    max_reextractions: int = 2
    reextraction_count: int = 0
    latest_extraction: InvoiceExtraction | None = None
    original_extraction: InvoiceExtraction | None = None
    give_contract_to_extractor: bool = True
