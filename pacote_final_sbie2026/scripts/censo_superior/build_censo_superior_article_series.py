#!/usr/bin/env python3
"""Consolida a série de docência em Computação do Censo Superior (1995–2024).

A etapa histórica (1995–2008) deve ser produzida por
``build_censo_superior_historical_1995_2008.py``. Os anos 2009–2024 são lidos
dos perfis gerados diretamente dos ZIPs contemporâneos. O script falha se a
cobertura anual estiver incompleta ou se os testes estruturais modernos não
fecharem.

As colunas ``linhas_*`` contam registros físicos do recorte. A partir de 2009,
um curso pode aparecer em várias dimensões territoriais; por isso ``qt_curso``
é a medida adequada de oferta e não deve ser substituída por ``linhas_recorte``.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


YEARS = tuple(range(1995, 2025))
YEAR_ROW = re.compile(r"^\|\s*((?:19|20)\d{2})\s*\|(.+)\|\s*$")


def clean(value: object) -> str:
    return "" if value is None else " ".join(str(value).replace("\t", " ").split())


def optional_int(value: object) -> int | None:
    text = clean(value)
    if not text:
        return None
    return int(text.replace(".", ""))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for field in row:
            if field not in seen:
                seen.add(field)
                fieldnames.append(field)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def historical_rows(path: Path) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for source in read_csv(path):
        year = int(source["ano"])
        partial = year == 1996
        output.append(
            {
                "ano": year,
                "status_qualidade": source["status_qualidade"],
                "linhas_recorte": optional_int(source.get("linhas_recorte")),
                "linhas_presencial": optional_int(source.get("linhas_presencial")),
                "linhas_ead": optional_int(source.get("linhas_ead")),
                "qt_curso": optional_int(source.get("qt_curso_proxy")),
                "qt_curso_presencial": optional_int(source.get("qt_curso_proxy_presencial")),
                "qt_curso_ead": optional_int(source.get("qt_curso_proxy_ead")),
                "status_qt_curso": "NAO_COMPARAVEL" if partial else "PROXY_LINHAS_GRADUACAO",
                "qt_vagas": optional_int(source.get("qt_vagas")),
                "qt_inscritos": optional_int(source.get("qt_inscritos")),
                "qt_ingressantes": optional_int(source.get("qt_ingressantes")),
                "qt_matriculas": optional_int(source.get("qt_matriculas")),
                "qt_concluintes": optional_int(source.get("qt_concluintes")),
                "status_qt_vagas": source.get("status_qt_vagas", ""),
                "status_qt_inscritos": source.get("status_qt_inscritos", ""),
                "status_qt_ingressantes": source.get("status_qt_ingressantes", ""),
                "status_qt_matriculas": source.get("status_qt_matriculas", ""),
                "status_qt_concluintes": source.get("status_qt_concluintes", ""),
                "tipo_leiaute": "HISTORICO_VARIAVEL",
                "fonte": source["arquivo_zip"],
                "observacao": source["observacao"],
            }
        )
    return output


def assert_modern_profile(profile: dict) -> None:
    year = profile["year"]
    failures: list[str] = []
    if profile["year_mismatches"]:
        failures.append(f"{profile['year_mismatches']} linhas com ano divergente")
    if profile["course_rows_with_missing_ies_parent"]:
        failures.append(f"{profile['course_rows_with_missing_ies_parent']} linhas sem IES")
    for name, result in profile["all_row_identities"].items():
        if result["mismatches"]:
            # Em 2009, os componentes por turno/modalidade foram publicados
            # zerados enquanto QT_INSCRITO_TOTAL foi preenchido. O total direto
            # é a variável oficial utilizável; a exceção fica registrada.
            if year == 2009 and name == "inscritos_turno_modalidade" and result["components_sum"] == 0:
                continue
            failures.append(f"identidade {name}: {result['mismatches']} divergências")
    for selection_name in ("docencia_computacao", "licenciaturas_pedagogia"):
        selection = profile[selection_name]
        if selection["invalid_quantities"]:
            failures.append(f"{selection_name}: quantidades inválidas")
        if selection["negative_quantities"]:
            failures.append(f"{selection_name}: quantidades negativas")
    comp = profile["docencia_computacao"]
    dim = comp["quantity_sums_by_dimension"]
    qt_course_by_dimension = sum(int(values["QT_CURSO"]) for values in dim.values())
    if qt_course_by_dimension != comp["quantity_sums"]["QT_CURSO"]:
        failures.append("QT_CURSO não fecha entre dimensões")
    if failures:
        raise ValueError(f"Perfil {year} inválido: " + "; ".join(failures))


def modern_row(profile: dict) -> dict[str, object]:
    assert_modern_profile(profile)
    comp = profile["docencia_computacao"]
    dimensions = comp["quantity_sums_by_dimension"]
    quantities = comp["quantity_sums"]
    return {
        "ano": profile["year"],
        "status_qualidade": "VALIDADO_MD5_CHAVES_IDENTIDADES",
        "linhas_recorte": comp["rows"],
        "linhas_presencial": comp["modality"].get("1", 0),
        "linhas_ead": comp["modality"].get("2", 0),
        "qt_curso": quantities["QT_CURSO"],
        "qt_curso_presencial": dimensions.get("1", {}).get("QT_CURSO", 0),
        "qt_curso_ead": dimensions.get("3", {}).get("QT_CURSO", 0),
        "status_qt_curso": "OFICIAL_QT_CURSO",
        "qt_vagas": quantities["QT_VG_TOTAL"],
        "qt_inscritos": quantities["QT_INSCRITO_TOTAL"],
        "qt_ingressantes": quantities["QT_ING"],
        "qt_matriculas": quantities["QT_MAT"],
        "qt_concluintes": quantities["QT_CONC"],
        "status_qt_vagas": "OK",
        "status_qt_inscritos": "OK",
        "status_qt_ingressantes": "OK",
        "status_qt_matriculas": "OK",
        "status_qt_concluintes": "OK",
        "tipo_leiaute": "CADASTRO_CURSOS_DIMENSIONAL",
        "fonte": Path(profile["archive"]).name,
        "observacao": "Linhas do recorte incluem dimensões territoriais; QT_CURSO usa dimensões 1 e 3 sem dupla contagem.",
    }


def read_modern_profiles(paths: list[Path]) -> list[dict]:
    profiles: list[dict] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError(f"Esperada lista de perfis em {path}")
        profiles.extend(payload)
    return profiles


def parse_legacy_report(path: Path) -> dict[int, list[int]]:
    rows: dict[int, list[int]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = YEAR_ROW.match(line)
        if not match:
            continue
        cells = [cell.strip() for cell in match.group(2).split("|")]
        try:
            values = [int(cell.replace(".", "")) for cell in cells[-7:]]
        except ValueError:
            continue
        rows[int(match.group(1))] = values
    return rows


def compare_with_legacy(
    rows: list[dict[str, object]], report: Path | None
) -> list[dict[str, object]]:
    legacy = parse_legacy_report(report) if report else {}
    output: list[dict[str, object]] = []
    fields = (
        "linhas_recorte",
        "linhas_presencial",
        "linhas_ead",
        "qt_vagas",
        "qt_ingressantes",
        "qt_matriculas",
        "qt_concluintes",
    )
    for row in rows:
        year = int(row["ano"])
        old_values = legacy.get(year)
        comparison: dict[str, object] = {"ano": year}
        changed: list[str] = []
        for index, field in enumerate(fields):
            new_value = row[field]
            old_value = old_values[index] if old_values else None
            comparison[f"legado_{field}"] = old_value
            comparison[f"recalculado_{field}"] = new_value
            comparison[f"diferenca_{field}"] = (
                int(new_value) - old_value if new_value is not None and old_value is not None else None
            )
            if new_value != old_value:
                changed.append(field)
        comparison["status"] = (
            "NAO_COMPARADO" if report is None else "IDENTICO" if not changed else "ALTERADO_AUDITORIA"
        )
        comparison["campos_alterados"] = "|".join(changed)
        output.append(comparison)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--historical-summary", type=Path, required=True)
    parser.add_argument("--modern-profile", type=Path, action="append", required=True)
    parser.add_argument(
        "--legacy-report",
        type=Path,
        help="Relatório anterior opcional; usado somente para auditoria comparativa",
    )
    parser.add_argument("--series-csv", type=Path, required=True)
    parser.add_argument("--comparison-csv", type=Path, required=True)
    parser.add_argument("--validation-json", type=Path, required=True)
    args = parser.parse_args()

    rows = historical_rows(args.historical_summary)
    rows.extend(modern_row(profile) for profile in read_modern_profiles(args.modern_profile))
    rows.sort(key=lambda item: int(item["ano"]))

    years = [int(row["ano"]) for row in rows]
    if years != list(YEARS):
        raise ValueError(f"Cobertura anual inválida: {years}")
    if any(row["ano"] == 1996 and row["qt_concluintes"] is not None for row in rows):
        raise ValueError("1996 não pode receber quantidade publicada")
    for row in rows:
        if row["qt_curso"] is None:
            continue
        modality_total = (row["qt_curso_presencial"] or 0) + (row["qt_curso_ead"] or 0)
        if row["qt_curso"] != modality_total:
            raise ValueError(
                f"{row['ano']}: qt_curso={row['qt_curso']} não fecha com modalidades={modality_total}"
            )

    comparison = compare_with_legacy(rows, args.legacy_report)
    write_csv(args.series_csv, rows)
    write_csv(args.comparison_csv, comparison)
    validation = {
        "coverage_years": years,
        "coverage_complete": True,
        "year_1996_noncomparable": True,
        "modern_years_validated": [row["ano"] for row in rows if int(row["ano"]) >= 2009],
        "legacy_report_compared": args.legacy_report is not None,
        "legacy_identical_years": [row["ano"] for row in comparison if row["status"] == "IDENTICO"],
        "legacy_changed_years": [row["ano"] for row in comparison if row["status"] == "ALTERADO_AUDITORIA"],
    }
    args.validation_json.parent.mkdir(parents=True, exist_ok=True)
    args.validation_json.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"Série 1995–2024: {len(rows)} anos; "
        f"alterações auditadas em {validation['legacy_changed_years']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
