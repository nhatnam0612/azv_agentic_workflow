import argparse
import sys
from pathlib import Path

from .agents import run_workflow


def main() -> int:
    parser = argparse.ArgumentParser(description="AZV Multi-Agent Workflow")
    parser.add_argument("--invoice", type=Path, required=True, help="Pfad zur Musterrechnung (PNG/JPG/PDF)")
    parser.add_argument("--contract", type=Path, required=True, help="Pfad zum Vertrag (.txt, .md oder .pdf)")
    parser.add_argument(
        "--inject-error",
        action="store_true",
        help="Verfälscht absichtlich ein Extraktionsfeld (invoice_date), um den Re-Extraktions-Loop zu testen",
    )
    parser.add_argument(
        "--withhold-contract-from-extractor",
        action="store_true",
        help="Ablationstest: Agent 1 erhält den Vertragstext NICHT (weder initial noch bei Reextraktion)",
    )
    args = parser.parse_args()

    result = run_workflow(
        args.invoice,
        args.contract,
        inject_error=args.inject_error,
        give_contract_to_extractor=not args.withhold_contract_from_extractor,
    )
    print(result.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
