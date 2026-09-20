# AZV Multi-Agent Workflow

This project implements a two-agent workflow with **Pydantic AI**, **Pydantic**, and the **OpenAI API**.

## Architecture
Musterrechnung (image/PDF)
          |
          v
+------------------------+
| Agent 1: Invoice       |
| extraction             |
|                        |
| Pydantic output:       |
| InvoiceExtraction      |
+-----------+------------+
            |
            | tool delegation
            v
+------------------------+
| Agent 2: Contract      |
| checker                |
|                        |
| Contract + extraction  |
| -> AZVAssessment       |
+-----------+------------+
            |
            v
     WorkflowResult
   (extraction + check)

The implementation follows the Pydantic AI multi-agent delegation pattern: Agent 1 exposes a tool that calls Agent 2, and the parent run passes its usage context to the delegated run. Pydantic models are used as structured outputs for both stages.

## Important interpretation

The workflow is deliberately conservative. A treatment being outside the coverage period is **not automatically treated as an Anzeigepflichtverletzung**. The second agent returns `UNKLAR` when the supplied material does not establish enough facts. `human_review_required` is always true.


## Requirements

- Python 3.11+
- `uv`
- OpenAI API key

## Setup

From this directory:

```bash
uv sync
cp .env.example .env
```

Put your key in `.env`:

```text
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2
```

## Run with the supplied example documents

```bash
uv run azv-agent \
  --invoice data/musterrechnung.png \
  --contract data/zahnzusatzversicherungsvertrag.pdf \
  --output result.json
```

## Expected output

The terminal prints JSON containing:

- extracted invoice metadata
- all extracted invoice line items
- Agent 2 classification: `AZV_FALL`, `KEIN_AZV_FALL`, or `UNKLAR`
- confidence
- reasons
- relevant invoice items
- relevant contract clauses
- missing information
- a human-review flag

## Files

```text
azv_multi_agent_workflow/
├── data/
│   ├── musterrechnung.png
│   ├── zahnzusatzversicherungsvertrag.pdf
│   └── zahnzusatzversicherungsvertrag.txt
├── azv_workflow/
│   ├── __init__.py
│   ├── agents.py
│   ├── document_utils.py
│   ├── main.py
│   └── models.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## Why Pydantic is used

Pydantic defines the schemas that the agents must return. This makes the invoice extraction and AZV assessment machine-readable and validated instead of relying on free-form text.


# Hauptaufbau: Agent 1 kennt den Vertrag, Test mit injiziertem (irrelevantem) Datumsfehler
azv-workflow --invoice data/musterrechnung.png --contract data/vertrag.pdf --inject-error

# Ablation: Agent 1 kennt den Vertrag NICHT -> sollte den bereits beobachteten Fehlschluss reproduzieren
azv-workflow --invoice data/musterrechnung.png --contract data/vertrag.pdf --withhold-contract-from-extractor