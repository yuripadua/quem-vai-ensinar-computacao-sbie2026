#!/usr/bin/env python3
"""Valida e, opcionalmente, copia o dicionário das 226 variáveis integradas."""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    package = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=package / "config" / "colunas_base_integrada_2025.txt")
    parser.add_argument("--template", type=Path, default=package / "data" / "metadata" / "dicionario_base_integrada_2025.csv")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    schema = [line.strip() for line in args.schema.read_text(encoding="utf-8").splitlines() if line.strip()]
    with args.template.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    variables = [row.get("variavel", "").strip() for row in rows]
    missing_descriptions = [row.get("variavel", "") for row in rows if not row.get("descricao", "").strip()]
    if len(schema) != 226 or len(schema) != len(set(schema)):
        raise RuntimeError(f"Esquema inválido: {len(schema)} colunas")
    if variables != schema:
        raise RuntimeError("O dicionário não cobre o esquema na mesma ordem")
    if missing_descriptions:
        raise RuntimeError(f"Descrições ausentes: {missing_descriptions}")
    if args.output and args.output.resolve() != args.template.resolve():
        args.output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.template, args.output)
    print(f"PASS: dicionário com {len(rows)} variáveis e nenhuma descrição ausente")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
