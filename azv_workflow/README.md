# AZV Workflow

Eigenständiges Projekt (keine Abhängigkeit zu einem anderen Repo). Zwei-Agenten-Workflow
(Extraktion + AZV-Bewertung) mit agentischer Rückkopplung: Agent 2 kann Agent 1 um eine
erneute Extraktion bitten (`request_reextraction`). In dieser Variante enthält die
Systeminstruktion von Agent 2 eine **verpflichtende** Anweisung: bei jedem vermuteten
Datumsfehler muss zuerst eine Reextraktion angefordert werden, bevor überhaupt bewertet wird.
Zusätzlich läuft Agent 2 mit `temperature=0`, um die Sampling-Varianz gegenüber der
`azv_agent`-Variante zu reduzieren.

## Ablaufdiagramm (im Anhang der Arbeit zu finden)


**Wichtig für die Einordnung:** Der Tool-Aufruf ist hier keine Ermessensentscheidung des Modells
mehr, sondern eine im Prompt fest vorgeschriebene Handlungsregel (,,wenn Bedingung X erfüllt,
dann MUSS Y erfolgen``) -- die inhaltliche Entscheidungslogik ist damit im Kern vorab
festgelegt, auch wenn sie in natürlicher Sprache statt in Code ausgedrückt ist. Dies entspricht
der Workflow-Charakteristik im Sinne des in der zugehörigen Arbeit verwendeten
Kriterienkatalogs (Kontrollfluss liegt beim Entwickler, nicht beim Modell).

## Setup mit uv

```bash
uv sync
cp .env.example .env
# .env öffnen und OPENAI_API_KEY eintragen
```


## Ausführen

```bash
# Normaler Lauf
uv run azv-workflow --invoice data/musterrechnung.png --contract data/vertrag.pdf

# Mit künstlich injiziertem, decision-relevantem Fehler (treatment_period)
uv run azv-workflow --invoice data/musterrechnung.png --contract data/vertrag.pdf --inject-error
