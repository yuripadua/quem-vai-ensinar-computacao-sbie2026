#!/usr/bin/env python3
"""Compara relatórios legados do Censo Superior com perfis refeitos do bruto."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


YEAR_ROW = re.compile(r"^\|\s*((?:19|20)\d{2})\s*\|(.+)\|\s*$")


def parse_integer(value: str) -> int:
    return int(value.strip().replace(".", ""))


def read_year_rows(path: Path, trailing_numeric_columns: int) -> dict[int, list[int]]:
    rows: dict[int, list[int]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = YEAR_ROW.match(line)
        if not match:
            continue
        year = int(match.group(1))
        cells = [cell.strip() for cell in match.group(2).split("|")]
        try:
            numbers = [parse_integer(cell) for cell in cells[-trailing_numeric_columns:]]
        except ValueError:
            continue
        if len(numbers) == trailing_numeric_columns:
            rows[year] = numbers
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile-json", type=Path, required=True)
    parser.add_argument("--computing-report", type=Path, required=True)
    parser.add_argument("--licensure-report", type=Path, required=True)
    args = parser.parse_args()

    profiles = {item["year"]: item for item in json.loads(args.profile_json.read_text(encoding="utf-8"))}
    computing_rows = read_year_rows(args.computing_report, trailing_numeric_columns=7)
    licensure_rows = read_year_rows(args.licensure_report, trailing_numeric_columns=3)
    failures: list[str] = []

    for year, profile in sorted(profiles.items()):
        comp = profile["docencia_computacao"]
        comp_expected = [
            comp["rows"],
            comp["modality"].get("1", 0),
            comp["modality"].get("2", 0),
            comp["quantity_sums"]["QT_VG_TOTAL"],
            comp["quantity_sums"]["QT_ING"],
            comp["quantity_sums"]["QT_MAT"],
            comp["quantity_sums"]["QT_CONC"],
        ]
        if computing_rows.get(year) != comp_expected:
            failures.append(
                f"{year} computação: relatório={computing_rows.get(year)}; bruto={comp_expected}"
            )

        lic_expected_rows = profile["licenciaturas_pedagogia"]["rows"]
        lic_report_row = licensure_rows.get(year)
        lic_report_selected = lic_report_row[-1] if lic_report_row else None
        if lic_report_selected != lic_expected_rows:
            failures.append(
                f"{year} licenciaturas/Pedagogia: relatório={lic_report_selected}; bruto={lic_expected_rows}"
            )

    if failures:
        print("FALHA")
        for failure in failures:
            print(f"- {failure}")
        return 1

    years = sorted(profiles)
    print(f"OK: relatórios legados reproduzidos exatamente para {years[0]}–{years[-1]}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
