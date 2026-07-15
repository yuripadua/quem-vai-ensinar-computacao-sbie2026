#!/usr/bin/env python3
"""Confronta os derivados calculados com os valores do artigo aceito."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value: str) -> int | float:
    text = value.strip()
    if not text:
        raise ValueError("valor vazio")
    return float(text) if "." in text else int(text)


class Validator:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, metric: str, expected: object, observed: object, tolerance: float = 0.0, note: str = "") -> None:
        if isinstance(expected, (int, float)) and isinstance(observed, (int, float)):
            difference: object = observed - expected
            passed = math.isclose(float(observed), float(expected), abs_tol=tolerance, rel_tol=0.0)
        else:
            difference = "" if observed == expected else "DIFERENTE"
            passed = observed == expected
        self.rows.append(
            {
                "grupo": group,
                "metrica": metric,
                "esperado": expected,
                "observado": observed,
                "diferenca": difference,
                "tolerancia": tolerance,
                "status": "PASS" if passed else "FAIL",
                "observacao": note,
            }
        )

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)


def validate(package: Path, expected_path: Path) -> Validator:
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    basic = package / "data" / "derived" / "censo_escolar_2025"
    higher = package / "data" / "derived" / "censo_superior"
    validator = Validator()

    national = read_csv(basic / "resumo_nacional.csv")[0]
    for metric, value in expected["censo_escolar_2025"]["resumo_nacional"].items():
        validator.check("censo_escolar_2025", metric, value, number(national[metric]))

    table_02 = {row["dependencia"]: row for row in read_csv(basic / "tabela_02_escala_dependencia.csv")}
    fields_02 = ["escolas", "matriculas", "turmas_ef", "turmas_anos_iniciais", "turmas_anos_finais", "docentes_ef_vinculos_escola"]
    for dependency, values in expected["censo_escolar_2025"]["tabela_02_dependencia"].items():
        for field, value in zip(fields_02, values):
            validator.check("tabela_02", f"{dependency}.{field}", value, int(table_02[dependency][field]))

    table_04 = {row["cenario"]: row for row in read_csv(basic / "tabela_04_demanda_cenarios.csv")}
    for scenario, values in expected["censo_escolar_2025"]["tabela_04_demanda"].items():
        for capacity, value in zip(("20", "25", "26.7", "29.2"), values):
            validator.check("tabela_04", f"{scenario}.{capacity}", value, int(table_04[scenario][capacity]))

    textual = json.loads((basic / "metricas_textuais_artigo.json").read_text(encoding="utf-8"))
    for metric, value in expected["censo_escolar_2025"]["metricas_textuais"].items():
        validator.check("texto_artigo", metric, value, textual[metric])

    dependency_rows = {row["dependencia_nome"]: row for row in read_csv(basic / "resumo_por_dependencia.csv")}
    region_rows = {row["regiao"]: row for row in read_csv(basic / "resumo_por_regiao.csv")}
    total = int(national["escolas"])
    observed_percentages = {
        "nacional.escolas_internet": round(100 * int(national["escolas_internet"]) / total, 1),
        "nacional.escolas_internet_aprendizagem": round(100 * int(national["escolas_internet_aprendizagem"]) / total, 1),
        "nacional.escolas_internet_alunos": round(100 * int(national["escolas_internet_alunos"]) / total, 1),
        "nacional.escolas_laboratorio_informatica": round(100 * int(national["escolas_laboratorio_informatica"]) / total, 1),
        "municipal.escolas": round(100 * int(dependency_rows["Municipal"]["escolas"]) / total, 1),
    }
    for prefix, row in (("municipal", dependency_rows["Municipal"]), ("norte", region_rows["Norte"]), ("sul", region_rows["Sul"])):
        for metric in (
            "escolas_turma_computacao",
            "escolas_docente_computacao",
            "escolas_docente_educacao_tic",
            "escolas_algum_sinal_docente",
            "escolas_laboratorio_informatica",
            "escolas_internet_alunos",
        ):
            observed_percentages[f"{prefix}.{metric}"] = round(float(row[f"pct_{metric}"]), 1)
    for metric, value in expected["censo_escolar_2025"]["percentuais_artigo_uma_decimal"].items():
        validator.check("percentuais_artigo", metric, value, observed_percentages[metric])

    uf_rows = read_csv(basic / "resumo_por_uf.csv")
    for metric in (
        "escolas",
        "matriculas_ef",
        "turmas_ef",
        "turmas_anos_iniciais",
        "turmas_anos_finais",
        "docentes_ef_vinculos_escola",
        "escolas_algum_sinal_docente",
        "demanda_intermediario_25",
    ):
        validator.check("reconciliacao_territorial", f"soma_ufs.{metric}", int(national[metric]), sum(int(row[metric]) for row in uf_rows))
    for metric in ("escolas", "matriculas_ef", "turmas_ef", "demanda_intermediario_25"):
        validator.check("reconciliacao_territorial", f"soma_regioes.{metric}", int(national[metric]), sum(int(row[metric]) for row in region_rows.values()))

    series = read_csv(higher / "serie_docencia_computacao_1995_2024.csv")
    years = [int(row["ano"]) for row in series]
    validator.check("censo_superior", "cobertura_1995_2024", list(range(1995, 2025)), years)
    by_year = {int(row["ano"]): row for row in series}
    graduates = {year: int(row["qt_concluintes"]) for year, row in by_year.items() if row["qt_concluintes"].strip()}
    higher_expected = expected["censo_superior"]
    validator.check("censo_superior", "concluintes_docencia_computacao_2024", higher_expected["concluintes_docencia_computacao_2024"], graduates[2024])
    peak_year = max(graduates, key=lambda year: graduates[year])
    validator.check("censo_superior", "pico_concluintes", higher_expected["pico_concluintes_docencia_computacao"], graduates[peak_year])
    validator.check("censo_superior", "ano_pico", higher_expected["ano_pico"], peak_year)
    validator.check("censo_superior", "anos_equivalentes_2024", higher_expected["anos_equivalentes_2024_uma_decimal"], round(int(national["demanda_intermediario_25"]) / graduates[2024], 1))
    validator.check("censo_superior", "1996_nao_comparavel", "", by_year[1996]["qt_concluintes"])
    validator.check("censo_superior", "1998_concluintes_ausente", "", by_year[1998]["qt_concluintes"])

    recortes = {row["recorte_id"]: row for row in read_csv(higher / "recortes_formacao_inicial_2024.csv")}
    for metric, key in (
        ("concluintes_pedagogia_amplo_artigo_2024", "pedagogia_amplo_artigo"),
        ("concluintes_pedagogia_nome_estrito_2024", "pedagogia_nome_estrito"),
        ("concluintes_pedagogia_e_licenciaturas_2024", "pedagogia_e_licenciaturas"),
    ):
        note = "Recorte estrito publicado por transparência; o artigo usa o recorte amplo." if key == "pedagogia_nome_estrito" else ""
        validator.check("censo_superior", metric, higher_expected[metric], int(recortes[key]["concluintes"]), note=note)
    return validator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--expected", type=Path)
    parser.add_argument("--output-csv", type=Path)
    parser.add_argument("--output-json", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    package = args.package.resolve()
    expected = args.expected or package / "config" / "valores_artigo_aceito.json"
    output_csv = args.output_csv or package / "validation" / "validacao_artigo_aceito.csv"
    output_json = args.output_json or package / "validation" / "validacao_artigo_aceito.json"
    try:
        validator = validate(package, expected)
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(validator.rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(validator.rows)
    report = {
        "status": "PASS" if validator.passed else "FAIL",
        "checks": len(validator.rows),
        "passed": sum(row["status"] == "PASS" for row in validator.rows),
        "failed": sum(row["status"] == "FAIL" for row in validator.rows),
        "failures": [row for row in validator.rows if row["status"] == "FAIL"],
    }
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: {report['passed']}/{report['checks']} verificações")
    return 0 if validator.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
