# AZV Multi-Agent Workflow

Dieses Projekt implementiert einen Zwei-Agenten-Workflow mit **Pydantic AI**, **Pydantic** und der **OpenAI API**.

## Ablaufdiagramm (im Anhang der Arbeit zu finden)


## Wichtiger Interpretationshinweis

Der Workflow ist bewusst konservativ ausgelegt. Eine Behandlung außerhalb des Versicherungszeitraums wird **nicht automatisch als Anzeigepflichtverletzung** gewertet. Agent 2 gibt `UNKLAR` zurück, wenn die vorliegenden Unterlagen nicht ausreichen, um einen Sachverhalt eindeutig festzustellen. `human_review_required` ist immer auf `true` gesetzt.

## Voraussetzungen

- Python 3.11+
- `uv`
- OpenAI-API-Schlüssel

## Setup

Aus diesem Verzeichnis heraus:

```bash
uv sync
cp .env.example .env
```

Trage deinen Schlüssel in `.env` ein:

```text
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2
```

## Ausführen mit den mitgelieferten Beispieldokumenten

```bash
uv run azv-agent \
  --invoice data/musterrechnung.png \
  --contract davertrag.pdf \
```

## Erwarteter Output

Im Terminal wird ein JSON-Objekt ausgegeben mit:

- extrahierten Rechnungsmetadaten
- allen extrahierten Rechnungspositionen
- der Klassifikation von Agent 2: `AZV_FALL`, `KEIN_AZV_FALL` oder `UNKLAR`
- der Konfidenz
- den Begründungen
- den relevanten Rechnungspositionen
- den relevanten Vertragsklauseln
- fehlenden Informationen
- einem Human-Review-Flag

## Beispielaufrufe

```bash
# Hauptaufbau: Agent 1 kennt den Vertrag, Test mit injiziertem (irrelevantem) Datumsfehler
uv run azv-agent --invoice data/musterrechnung.png --contract data/vertrag.pdf --inject-error
