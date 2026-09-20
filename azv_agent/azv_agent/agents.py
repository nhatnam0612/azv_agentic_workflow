import os
import copy
import logging
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext, ModelRetry

from .dependencies import CheckerDeps
from .models import AZVAssessment, InvoiceExtraction, WorkflowResult

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("azv_workflow")


extractor_agent = Agent(
    f"openai:{MODEL}",
    name="invoice_extractor",
    output_type=InvoiceExtraction,
    instructions=(
        "You are Agent 1, the invoice extraction agent. "
        "Read the supplied Musterrechnung carefully and extract the visible facts into the "
        "InvoiceExtraction schema. Preserve GOZ numbers, dates, teeth, quantities, factors, "
        "and euro amounts exactly where possible. Do not infer missing facts. "
        "You may additionally receive the insurance contract text as background context. "
        "Use it ONLY to sanity-check what you extract from the invoice (e.g. to confirm your "
        "own reading is plausible) — never extract fields into InvoiceExtraction from the "
        "contract itself, and never claim the contract is 'missing' if it was provided to you. "
        "If you receive a specific correction request naming a suspected field, re-read the "
        "invoice document with that in mind and correct only what the document evidence "
        "actually supports."
    ),
)

checker_agent = Agent(
    f"openai:{MODEL}",
    deps_type=CheckerDeps,
    name="azv_contract_checker",
    output_type=AZVAssessment,
    instructions=(
        "You are Agent 2, an insurance contract checking assistant. "
        "Assess whether the extracted invoice information is consistent with an "
        "Anzeigepflichtverletzung (AZV) case under the supplied contract. "
        "Use ONLY the contract text and invoice data supplied in the prompt. "
        "Do not invent clauses, dates, coverage, or facts. Do not claim the contract or the "
        "invoice data is missing unless it is genuinely absent from THIS prompt — check the "
        "CONTRACT TEXT and EXTRACTED INVOICE sections below carefully before making that claim. "
        "Distinguish clearly between: (1) services covered by the contract, "
        "(2) temporal eligibility, and (3) facts that would actually establish an AZV. "
        "If a value in the extracted invoice looks internally inconsistent, implausible, or "
        "contradicts the contract in a way suggesting a MISREAD (e.g. a date, amount, or code "
        "that doesn't fit the document context), call `request_reextraction` with a precise "
        "field hint and reason instead of guessing or marking the case UNKLAR for that reason. "
        "Only do this for suspected extraction errors, not for facts genuinely absent from the "
        "invoice, and not because you believe the contract itself is missing — the contract "
        "was already given to you directly in this prompt, not to Agent 1. "
        "You may call it at most twice. If evidence is still insufficient afterwards, "
        "return UNKLAR. This is decision support, not a binding decision. Always require human review."
    ),
)


def _log_diff(old: InvoiceExtraction, new: InvoiceExtraction) -> None:
    old_d, new_d = old.model_dump(), new.model_dump()
    for key in new_d:
        if key == "lines":
            continue
        if old_d.get(key) != new_d.get(key):
            logger.info("   Korrektur erkannt -> %s: '%s' -> '%s'", key, old_d.get(key), new_d.get(key))


@checker_agent.tool
async def request_reextraction(
    ctx: RunContext[CheckerDeps], field_hint: str, reason: str
) -> InvoiceExtraction:
    """Ask Agent 1 to re-check the original invoice for a specific suspected extraction error.

    Args:
        field_hint: which field(s) look wrong, e.g. "Rechnungsdatum / Behandlungsdatum".
        reason: why the current value looks implausible/inconsistent.
    """
    if ctx.deps.reextraction_count >= ctx.deps.max_reextractions:
        logger.warning(
            "[AGENT 2] Re-extraction limit (%d) erreicht – fahre mit bestehenden Daten fort.",
            ctx.deps.max_reextractions,
        )
        raise ModelRetry(
            "Re-extraction limit reached. Proceed with the data you have and reflect the "
            "remaining uncertainty in your confidence/reasons instead."
        )
    ctx.deps.reextraction_count += 1

    logger.info(
        "[AGENT 2 -> AGENT 1] Verdacht auf Extraktionsfehler erkannt. Feld: '%s' | Grund: %s",
        field_hint, reason,
    )
    logger.info(
        "[AGENT 2 -> AGENT 1] Fordere Re-Extraktion an (Versuch %d/%d) | Vertragskontext für Agent 1: %s ...",
        ctx.deps.reextraction_count, ctx.deps.max_reextractions, ctx.deps.give_contract_to_extractor,
    )

    correction_prompt = (
        "Re-examine the original invoice document below. Agent 2 flagged a possible extraction error.\n\n"
        f"SUSPECTED FIELD(S): {field_hint}\n"
        f"REASON FOR SUSPICION: {reason}\n\n"
        "Return the corrected, complete InvoiceExtraction. Only change fields the document "
        "actually supports changing; keep everything else as originally extracted."
    )
    extractor_input = [correction_prompt]
    if ctx.deps.give_contract_to_extractor:
        extractor_input.append(
            f"ZUR INFORMATION – VERTRAGSTEXT (nur Kontext, keine Vertragsfelder extrahieren):\n{ctx.deps.contract_text}"
        )
    extractor_input.extend(ctx.deps.invoice_content)

    result = await extractor_agent.run(extractor_input, usage=ctx.usage)

    logger.info("[AGENT 1 -> AGENT 2] Re-Extraktion abgeschlossen. Korrigierte Daten werden zurückgesendet.")
    old = ctx.deps.latest_extraction or ctx.deps.original_extraction
    if old is not None:
        _log_diff(old, result.output)

    ctx.deps.latest_extraction = result.output
    return result.output


def _inject_extraction_error(extraction: InvoiceExtraction) -> InvoiceExtraction:
    """Nur für Demo-/Testzwecke: verfälscht absichtlich ein Feld, damit Agent 2
    einen Extraktionsfehler vermutet und request_reextraction auslöst."""
    corrupted = copy.deepcopy(extraction)
    corrupted.invoice_date = "25.10.2020"
    logger.warning(
        "[TESTMODUS] Extraktion künstlich verfälscht: invoice_date '%s' -> '%s'",
        extraction.invoice_date, corrupted.invoice_date,
    )
    return corrupted


def run_workflow(
    invoice_path: Path,
    contract_path: Path,
    inject_error: bool = False,
    give_contract_to_extractor: bool = True,
) -> WorkflowResult:
    from .document_utils import invoice_content, read_contract_text

    logger.info(
        "[KONFIGURATION] Agent 1 erhält Vertragstext als Kontext: %s",
        give_contract_to_extractor,
    )

    logger.info("=== SCHRITT 1: AGENT 1 – Rechnungsextraktion ===")
    contract_text = read_contract_text(contract_path)
    content = invoice_content(invoice_path)
    if not isinstance(content, list):
        content = [content]

    extraction_input = ["Extract this Musterrechnung."]
    if give_contract_to_extractor:
        extraction_input.append(
            f"ZUR INFORMATION – VERTRAGSTEXT (nur Kontext, keine Vertragsfelder extrahieren):\n{contract_text}"
        )
    extraction_input.extend(content)

    extraction_result = extractor_agent.run_sync(extraction_input)
    extraction = extraction_result.output
    logger.info(
        "[AGENT 1] Extraktion abgeschlossen: Rechnungsdatum=%s, Behandlungszeitraum=%s",
        extraction.invoice_date, extraction.treatment_period,
    )

    extraction_for_checker = extraction
    if inject_error:
        extraction_for_checker = _inject_extraction_error(extraction)

    deps = CheckerDeps(
        contract_text=contract_text,
        invoice_content=content,
        original_extraction=extraction_for_checker,
        give_contract_to_extractor=give_contract_to_extractor,
    )

    prompt = f"""
CONTRACT TEXT
-------------
{contract_text}

EXTRACTED INVOICE
-----------------
{extraction_for_checker.model_dump_json(indent=2)}

Task: Determine whether the facts support an AZV case under this contract.
Return a structured assessment. Pay particular attention to whether the invoice treatment
predates the contract/insurance start date and whether the supplied material contains actual
evidence of a pre-existing fact that should have been disclosed.
Do not equate 'not covered' with 'Anzeigepflichtverletzung'.
"""
    assessment_result = checker_agent.run_sync(
        prompt, deps=deps, usage=extraction_result.usage
    )

    if deps.reextraction_count > 0:
        logger.info("=== SCHRITT 3: AGENT 2 – Neubewertung mit korrigierten Daten ===")
        logger.info("[AGENT 2] Anzahl Re-Extraktionen in diesem Lauf: %d", deps.reextraction_count)
    else:
        logger.info("[AGENT 2] Keine Re-Extraktion nötig – Originaldaten waren konsistent genug.")

    final_extraction = deps.latest_extraction or extraction_for_checker
    logger.info(
        "=== ERGEBNIS: %s (Confidence %.2f) ===",
        assessment_result.output.classification, assessment_result.output.confidence,
    )

    return WorkflowResult(invoice=final_extraction, assessment=assessment_result.output)