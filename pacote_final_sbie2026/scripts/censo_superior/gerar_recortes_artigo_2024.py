#!/usr/bin/env python3
"""Recalcula os quatro recortes de formação inicial usados no artigo em 2024."""

from __future__ import annotations

import argparse
import csv
import json
import zipfile
from collections import Counter
from pathlib import Path

from profile_censo_superior_course_recortes import (
    classify_computing_teacher_course,
    clean,
    find_member,
    is_graduation,
    iter_dict_rows,
    normalize,
    to_int,
)


EXPECTED = {
    "docencia_computacao": 925,
    "pedagogia_amplo_artigo": 105726,
    "pedagogia_nome_estrito": 105502,
    "pedagogia_e_licenciaturas": 206967,
}


def empty() -> dict[str, object]:
    return {"rows": 0, "codes": set(), "qt_curso": 0, "graduates": 0, "criteria": Counter()}


def add(selection: dict[str, object], row: dict[str, str], criterion: str) -> None:
    selection["rows"] += 1
    code = clean(row.get("CO_CURSO"))
    if code:
        selection["codes"].add(code)
    selection["qt_curso"] += to_int(row.get("QT_CURSO")) or 0
    selection["graduates"] += to_int(row.get("QT_CONC")) or 0
    selection["criteria"][criterion] += 1


def calculate(archive: Path) -> list[dict[str, object]]:
    selections = {
        "docencia_computacao": empty(),
        "pedagogia_amplo_artigo": empty(),
        "pedagogia_nome_estrito": empty(),
        "pedagogia_e_licenciaturas": empty(),
    }
    with zipfile.ZipFile(archive) as zf:
        member = find_member(zf, "MICRODADOS_CADASTRO_CURSOS", 2024)
        for row in iter_dict_rows(zf, member):
            if not is_graduation(row):
                continue
            name = normalize(row.get("NO_CURSO"))
            cine_label = normalize(row.get("NO_CINE_ROTULO"))
            degree = clean(row.get("TP_GRAU_ACADEMICO"))
            computing = classify_computing_teacher_course(row)
            if computing:
                add(selections["docencia_computacao"], row, computing)
            name_pedagogy = "pedagog" in name
            cine_pedagogy = "formacao pedagogica de professor para a educacao basica" in cine_label
            if name_pedagogy:
                add(selections["pedagogia_amplo_artigo"], row, "nome_pedagogia")
                add(selections["pedagogia_nome_estrito"], row, "nome_pedagogia")
                add(selections["pedagogia_e_licenciaturas"], row, "nome_pedagogia")
            elif cine_pedagogy:
                add(selections["pedagogia_amplo_artigo"], row, "cine_formacao_pedagogica_educacao_basica")
            if not name_pedagogy and degree == "2":
                add(selections["pedagogia_e_licenciaturas"], row, "grau_academico=2")

    labels = {
        "docencia_computacao": ("Docência em Computação/Informática", "Regras nominais, de grau e CINE documentadas no script de perfil"),
        "pedagogia_amplo_artigo": ("Pedagogia - recorte amplo usado no artigo", "União: NO_CURSO contém pedagog* ou NO_CINE_ROTULO indica formação pedagógica de professor para a educação básica"),
        "pedagogia_nome_estrito": ("Pedagogia - nome do curso contém pedagog*", "NO_CURSO contém pedagog*; apenas graduação"),
        "pedagogia_e_licenciaturas": ("Pedagogia e demais licenciaturas", "Pedagogia por nome ou grau acadêmico de licenciatura; apenas graduação"),
    }
    rows = []
    for recorte_id, selection in selections.items():
        if selection["graduates"] != EXPECTED[recorte_id]:
            raise RuntimeError(
                f"{recorte_id}: {selection['graduates']} concluintes; esperado {EXPECTED[recorte_id]}"
            )
        label, definition = labels[recorte_id]
        rows.append(
            {
                "ano": 2024,
                "recorte_id": recorte_id,
                "recorte": label,
                "definicao_operacional": definition,
                "linhas": selection["rows"],
                "codigos_curso_distintos": len(selection["codes"]),
                "qt_curso": selection["qt_curso"],
                "concluintes": selection["graduates"],
                "criterios_linhas": json.dumps(dict(selection["criteria"]), ensure_ascii=False, sort_keys=True),
            }
        )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--validation", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = calculate(args.archive)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    if args.validation:
        report = {
            "status": "PASS",
            "archive": args.archive.name,
            "expected_concluintes": EXPECTED,
            "observed_concluintes": {row["recorte_id"]: row["concluintes"] for row in rows},
            "differences": {row["recorte_id"]: row["concluintes"] - EXPECTED[row["recorte_id"]] for row in rows},
            "note": "O recorte amplo soma 224 concluintes classificados pelo CINE, embora o nome do curso não contenha pedagog*.",
        }
        args.validation.parent.mkdir(parents=True, exist_ok=True)
        args.validation.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: recortes de 2024 reproduzidos sem divergências")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
