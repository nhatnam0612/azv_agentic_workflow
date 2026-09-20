# AZV Workflow – Date Hint Variante

Eigenständiges Projekt (keine Abhängigkeit zu einem anderen Repo). Zwei-Agenten-Workflow
(Extraktion + AZV-Bewertung) mit agentischer Rückkopplung: Agent 2 kann Agent 1 um eine
erneute Extraktion bitten (`request_reextraction`). In dieser Variante enthält die
Systeminstruktion von Agent 2 eine **verpflichtende** Anweisung: bei jedem vermuteten
Datumsfehler muss zuerst eine Reextraktion angefordert werden, bevor überhaupt bewertet wird.

## Setup mit uv

```bash
uv sync
cp .env.example .env
# .env öffnen und OPENAI_API_KEY eintragen
```

## Testdaten

Lege deine Musterrechnung und deinen Vertrag in `data/` ab, z.B.:

```
data/musterrechnung.png
data/vertrag.txt      # oder .pdf
```

`read_contract_text()` in `azv_workflow/document_utils.py` unterstützt `.txt`, `.md` und
`.pdf` (Textextraktion via pypdf, kein OCR für gescannte PDFs ohne Textlayer).

## Ausführen

```bash
# Normaler Lauf
uv run azv-workflow --invoice data/musterrechnung.png --contract data/vertrag.txt

# Mit künstlich injiziertem, aber AZV-irrelevantem Datumsfehler (invoice_date)
uv run azv-workflow --invoice data/musterrechnung.png --contract data/vertrag.txt --inject-error

# Ablation: Agent 1 bekommt den Vertragstext nicht (weder initial noch bei Reextraktion)
uv run azv-workflow --invoice data/musterrechnung.png --contract data/vertrag.txt --withhold-contract-from-extractor
```

Ohne installierten Entry Point geht auch:

```bash
uv run python -m azv_workflow.main --invoice data/musterrechnung.png --contract data/vertrag.txt
```
