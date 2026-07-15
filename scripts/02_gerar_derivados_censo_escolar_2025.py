#!/usr/bin/env python3
"""Gera tabelas e recortes territoriais do artigo a partir da base integrada."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


CAPACITIES = {"20": (20, 1), "25": (25, 1), "26.7": (80, 3), "29.2": (146, 5)}
DEPENDENCIES = {"1": "Federal", "2": "Estadual", "3": "Municipal", "4": "Privada"}
LOCATIONS = {"1": "Urbana", "2": "Rural"}

COUNT_FIELDS = [
    "escolas",
    "matriculas_ef",
    "turmas_ef",
    "turmas_anos_iniciais",
    "turmas_anos_finais",
    "docentes_ef_vinculos_escola",
    "escolas_turma_computacao",
    "escolas_docente_computacao",
    "escolas_docente_educacao_tic",
    "escolas_ambos_sinais_docentes",
    "escolas_algum_sinal_docente",
    "escolas_sem_sinal_docente",
    "escolas_laboratorio_informatica",
    "escolas_internet",
    "escolas_internet_aprendizagem",
    "escolas_internet_alunos",
    "escolas_turma_matematica",
    "escolas_turma_lingua_portuguesa",
    "escolas_turma_ciencias",
    "escolas_turma_artes",
    "escolas_turma_lingua_inglesa",
]
PERCENT_BASES = [
    "escolas_turma_computacao",
    "escolas_docente_computacao",
    "escolas_docente_educacao_tic",
    "escolas_ambos_sinais_docentes",
    "escolas_algum_sinal_docente",
    "escolas_sem_sinal_docente",
    "escolas_laboratorio_informatica",
    "escolas_internet",
    "escolas_internet_aprendizagem",
    "escolas_internet_alunos",
    "escolas_turma_matematica",
    "escolas_turma_lingua_portuguesa",
    "escolas_turma_ciencias",
    "escolas_turma_artes",
    "escolas_turma_lingua_inglesa",
]
DEMAND_FIELDS = [
    *[f"demanda_minimo_{capacity}" for capacity in CAPACITIES],
    *[
        field
        for capacity in CAPACITIES
        for field in (
            f"demanda_intermediario_{capacity}",
            f"demanda_residual_docente_computacao_{capacity}",
            f"demanda_residual_algum_sinal_docente_{capacity}",
        )
    ],
    *[f"demanda_progressivo_{capacity}" for capacity in CAPACITIES],
    *[f"demanda_intensivo_{capacity}" for capacity in CAPACITIES],
    "posicoes_regentes_anos_iniciais",
    "posicoes_especialistas_anos_finais_2aulas_cap25",
    "posicoes_especialistas_anos_finais_3aulas_cap25",
    "demanda_hibrida_2aulas_anos_finais_cap25",
    "demanda_hibrida_3aulas_anos_finais_cap25",
    "escolas_demanda_intermediaria_cap25_maior_1",
]
OUTPUT_FIELDS = COUNT_FIELDS + DEMAND_FIELDS + [f"pct_{field}" for field in PERCENT_BASES]


def integer(row: dict[str, str], field: str) -> int:
    value = (row.get(field) or "").strip()
    return int(float(value)) if value else 0


def present(row: dict[str, str], field: str) -> int:
    return int(integer(row, field) > 0)


def demand(hours: int, capacity: tuple[int, int], floor: bool = True) -> int:
    numerator, denominator = capacity
    value = (hours * denominator + numerator - 1) // numerator
    return max(1, value) if floor else value


def school_metrics(row: dict[str, str]) -> Counter[str]:
    ai = integer(row, "QT_TUR_FUND_AI")
    af = integer(row, "QT_TUR_FUND_AF")
    turma_comp = present(row, "QT_TUR_BAS_DISC_INFO_COMPUTACAO")
    docente_comp = present(row, "QT_DOC_BAS_DISC_INFO_COMPUTACAO")
    docente_tic = present(row, "QT_DOC_BAS_ESPEC_EDUC_TIC")
    algum_docente = int(bool(docente_comp or docente_tic))
    ambos_docentes = int(bool(docente_comp and docente_tic))

    ai_progressivo = (
        integer(row, "QT_TUR_FUND_AI_1")
        + integer(row, "QT_TUR_FUND_AI_2")
        + 2
        * (
            integer(row, "QT_TUR_FUND_AI_3")
            + integer(row, "QT_TUR_FUND_AI_4")
            + integer(row, "QT_TUR_FUND_AI_5")
            + integer(row, "QT_TUR_FUND_AI_MULTIETAPA")
        )
    )
    hours = {
        "minimo": ai + af,
        "intermediario": ai + 2 * af,
        "progressivo": ai_progressivo + 2 * af,
        "intensivo": ai_progressivo + 3 * af,
    }
    metrics: Counter[str] = Counter(
        {
            "escolas": 1,
            "matriculas_ef": integer(row, "QT_MAT_FUND"),
            "turmas_ef": integer(row, "QT_TUR_FUND"),
            "turmas_anos_iniciais": ai,
            "turmas_anos_finais": af,
            "docentes_ef_vinculos_escola": integer(row, "QT_DOC_FUND"),
            "escolas_turma_computacao": turma_comp,
            "escolas_docente_computacao": docente_comp,
            "escolas_docente_educacao_tic": docente_tic,
            "escolas_ambos_sinais_docentes": ambos_docentes,
            "escolas_algum_sinal_docente": algum_docente,
            "escolas_sem_sinal_docente": 1 - algum_docente,
            "escolas_laboratorio_informatica": present(row, "IN_LABORATORIO_INFORMATICA"),
            "escolas_internet": present(row, "IN_INTERNET"),
            "escolas_internet_aprendizagem": present(row, "IN_INTERNET_APRENDIZAGEM"),
            "escolas_internet_alunos": present(row, "IN_INTERNET_ALUNOS"),
            "escolas_turma_matematica": present(row, "QT_TUR_BAS_DISC_MATEMATICA"),
            "escolas_turma_lingua_portuguesa": present(row, "QT_TUR_BAS_DISC_LINGUA_PORT"),
            "escolas_turma_ciencias": present(row, "QT_TUR_BAS_DISC_CIENCIAS"),
            "escolas_turma_artes": present(row, "QT_TUR_BAS_DISC_ARTES"),
            "escolas_turma_lingua_inglesa": present(row, "QT_TUR_BAS_DISC_LINGUA_ING"),
        }
    )
    for capacity_name, capacity in CAPACITIES.items():
        minimum = demand(hours["minimo"], capacity)
        intermediate = demand(hours["intermediario"], capacity)
        metrics[f"demanda_minimo_{capacity_name}"] = minimum
        metrics[f"demanda_intermediario_{capacity_name}"] = intermediate
        metrics[f"demanda_residual_docente_computacao_{capacity_name}"] = max(0, intermediate - docente_comp)
        metrics[f"demanda_residual_algum_sinal_docente_{capacity_name}"] = max(0, intermediate - algum_docente)
        metrics[f"demanda_progressivo_{capacity_name}"] = demand(hours["progressivo"], capacity)
        metrics[f"demanda_intensivo_{capacity_name}"] = demand(hours["intensivo"], capacity)

    specialists_2 = demand(2 * af, CAPACITIES["25"], floor=False) if af else 0
    specialists_3 = demand(3 * af, CAPACITIES["25"], floor=False) if af else 0
    metrics["posicoes_regentes_anos_iniciais"] = ai
    metrics["posicoes_especialistas_anos_finais_2aulas_cap25"] = specialists_2
    metrics["posicoes_especialistas_anos_finais_3aulas_cap25"] = specialists_3
    metrics["demanda_hibrida_2aulas_anos_finais_cap25"] = ai + specialists_2
    metrics["demanda_hibrida_3aulas_anos_finais_cap25"] = ai + specialists_3
    metrics["escolas_demanda_intermediaria_cap25_maior_1"] = int(metrics["demanda_intermediario_25"] > 1)
    return metrics


def percentage(value: int, total: int) -> int | float:
    result = round(100 * value / total, 2) if total else 0.0
    return int(result) if float(result).is_integer() else result


def finalize(counter: Counter[str]) -> dict[str, int | float]:
    row: dict[str, int | float] = {field: counter[field] for field in COUNT_FIELDS + DEMAND_FIELDS}
    for field in PERCENT_BASES:
        row[f"pct_{field}"] = percentage(counter[field], counter["escolas"])
    return row


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def generate(input_path: Path, output_dir: Path, audit_path: Path) -> dict[str, object]:
    national: Counter[str] = Counter()
    by_uf: defaultdict[str, Counter[str]] = defaultdict(Counter)
    by_region: defaultdict[str, Counter[str]] = defaultdict(Counter)
    by_dependency: defaultdict[str, Counter[str]] = defaultdict(Counter)
    by_location: defaultdict[str, Counter[str]] = defaultdict(Counter)
    by_cross: defaultdict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    keys: set[str] = set()
    rows = 0

    with input_path.open("r", encoding="cp1252", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        for source in reader:
            key = (source.get("CO_ENTIDADE") or "").strip()
            if not key or key in keys:
                raise RuntimeError(f"CO_ENTIDADE ausente ou duplicado: {key!r}")
            keys.add(key)
            metrics = school_metrics(source)
            uf = (source.get("SG_UF") or "").strip()
            region = (source.get("NO_REGIAO") or "").strip()
            dependency = (source.get("TP_DEPENDENCIA") or "").strip()
            location = (source.get("TP_LOCALIZACAO") or "").strip()
            if not uf or not region or dependency not in DEPENDENCIES or location not in LOCATIONS:
                raise RuntimeError(f"Dimensão territorial inválida em {key}")
            national.update(metrics)
            by_uf[uf].update(metrics)
            by_region[region].update(metrics)
            by_dependency[dependency].update(metrics)
            by_location[location].update(metrics)
            by_cross[(region, dependency, location)].update(metrics)
            rows += 1
    if rows != 119244:
        raise RuntimeError(f"Número inesperado de escolas: {rows}")

    national_row = finalize(national)
    write_csv(output_dir / "resumo_nacional.csv", [national_row], OUTPUT_FIELDS)
    uf_rows = [{"uf": key, **finalize(by_uf[key])} for key in sorted(by_uf)]
    write_csv(output_dir / "resumo_por_uf.csv", uf_rows, ["uf", *OUTPUT_FIELDS])
    region_rows = [{"regiao": key, **finalize(by_region[key])} for key in sorted(by_region)]
    write_csv(output_dir / "resumo_por_regiao.csv", region_rows, ["regiao", *OUTPUT_FIELDS])
    dependency_rows = [
        {"dependencia": key, "dependencia_nome": DEPENDENCIES[key], **finalize(by_dependency[key])}
        for key in sorted(by_dependency, key=int)
    ]
    write_csv(
        output_dir / "resumo_por_dependencia.csv",
        dependency_rows,
        ["dependencia", "dependencia_nome", *OUTPUT_FIELDS],
    )
    location_rows = [
        {"localizacao": key, "localizacao_nome": LOCATIONS[key], **finalize(by_location[key])}
        for key in sorted(by_location, key=int)
    ]
    write_csv(
        output_dir / "resumo_por_localizacao.csv",
        location_rows,
        ["localizacao", "localizacao_nome", *OUTPUT_FIELDS],
    )
    cross_rows = [
        {
            "regiao": region,
            "dependencia": dependency,
            "dependencia_nome": DEPENDENCIES[dependency],
            "localizacao": location,
            "localizacao_nome": LOCATIONS[location],
            **finalize(by_cross[(region, dependency, location)]),
        }
        for region, dependency, location in sorted(by_cross, key=lambda value: (value[0], int(value[1]), int(value[2])))
    ]
    write_csv(
        output_dir / "resumo_por_regiao_dependencia_localizacao.csv",
        cross_rows,
        ["regiao", "dependencia", "dependencia_nome", "localizacao", "localizacao_nome", *OUTPUT_FIELDS],
    )

    table_01 = [
        {"cenario": "Mínimo", "anos_iniciais": "1 aula/semana", "anos_finais": "1 aula/semana"},
        {"cenario": "Intermediário", "anos_iniciais": "1 aula/semana", "anos_finais": "2 aulas/semana"},
        {"cenario": "Progressivo", "anos_iniciais": "1 aula no 1º-2º; 2 aulas no 3º-5º e multietapa", "anos_finais": "2 aulas/semana"},
        {"cenario": "Intensivo", "anos_iniciais": "1 aula no 1º-2º; 2 aulas no 3º-5º e multietapa", "anos_finais": "3 aulas/semana"},
    ]
    write_csv(output_dir / "tabela_01_cenarios_carga.csv", table_01, ["cenario", "anos_iniciais", "anos_finais"])

    scale_fields = ["escolas", "matriculas_ef", "turmas_ef", "turmas_anos_iniciais", "turmas_anos_finais", "docentes_ef_vinculos_escola"]
    table_02 = [
        {
            "dependencia": DEPENDENCIES[key],
            "escolas": by_dependency[key]["escolas"],
            "matriculas": by_dependency[key]["matriculas_ef"],
            "turmas_ef": by_dependency[key]["turmas_ef"],
            "turmas_anos_iniciais": by_dependency[key]["turmas_anos_iniciais"],
            "turmas_anos_finais": by_dependency[key]["turmas_anos_finais"],
            "docentes_ef_vinculos_escola": by_dependency[key]["docentes_ef_vinculos_escola"],
        }
        for key in sorted(by_dependency, key=int)
    ]
    table_02.append(
        {
            "dependencia": "Total",
            "escolas": national["escolas"],
            "matriculas": national["matriculas_ef"],
            **{field: national[field] for field in scale_fields[2:]},
        }
    )
    write_csv(
        output_dir / "tabela_02_escala_dependencia.csv",
        table_02,
        ["dependencia", "escolas", "matriculas", "turmas_ef", "turmas_anos_iniciais", "turmas_anos_finais", "docentes_ef_vinculos_escola"],
    )

    signal_rows = [
        {"indicador": "Com turma de Informática/Computação", "escolas": national[field], "percentual": percentage(national[field], rows)}
        for field in ["escolas_turma_computacao"]
    ]
    for label, field in (
        ("Com docente em Informática/Computação", "escolas_docente_computacao"),
        ("Com docente em Educação/TIC", "escolas_docente_educacao_tic"),
        ("Com ambos os sinais docentes", "escolas_ambos_sinais_docentes"),
        ("Com ao menos um sinal docente", "escolas_algum_sinal_docente"),
        ("Sem nenhum dos sinais docentes", "escolas_sem_sinal_docente"),
    ):
        signal_rows.append({"indicador": label, "escolas": national[field], "percentual": percentage(national[field], rows)})
    signal_rows.extend(
        [
            {"indicador": "Componentes consolidados (faixa: Matemática, Língua Portuguesa, Ciências e Artes)", "escolas": "118067-119096", "percentual": "99.01-99.88"},
            {"indicador": "Língua Inglesa", "escolas": national["escolas_turma_lingua_inglesa"], "percentual": percentage(national["escolas_turma_lingua_inglesa"], rows)},
        ]
    )
    write_csv(output_dir / "tabela_03_sinais_computacao.csv", signal_rows, ["indicador", "escolas", "percentual"])

    scenario_fields = [
        ("Mínimo", "demanda_minimo"),
        ("Intermediário bruto", "demanda_intermediario"),
        ("Residual: docente Info./Comp.", "demanda_residual_docente_computacao"),
        ("Residual: algum sinal docente", "demanda_residual_algum_sinal_docente"),
        ("Progressivo", "demanda_progressivo"),
        ("Intensivo", "demanda_intensivo"),
    ]
    table_04 = [
        {"cenario": label, **{capacity: national[f"{prefix}_{capacity}"] for capacity in CAPACITIES}}
        for label, prefix in scenario_fields
    ]
    write_csv(output_dir / "tabela_04_demanda_cenarios.csv", table_04, ["cenario", *CAPACITIES])

    specialist_rows = []
    for uf in sorted(by_uf):
        for label, prefix in scenario_fields:
            specialist_rows.append({"uf": uf, "cenario": label, **{capacity: by_uf[uf][f"{prefix}_{capacity}"] for capacity in CAPACITIES}})
    write_csv(output_dir / "demanda_especialista_por_uf.csv", specialist_rows, ["uf", "cenario", *CAPACITIES])

    hybrid_rows = [
        {
            "uf": uf,
            "posicoes_regentes_anos_iniciais": by_uf[uf]["posicoes_regentes_anos_iniciais"],
            "especialistas_anos_finais_2aulas_cap25": by_uf[uf]["posicoes_especialistas_anos_finais_2aulas_cap25"],
            "total_hibrido_2aulas_cap25": by_uf[uf]["demanda_hibrida_2aulas_anos_finais_cap25"],
            "especialistas_anos_finais_3aulas_cap25": by_uf[uf]["posicoes_especialistas_anos_finais_3aulas_cap25"],
            "total_hibrido_3aulas_cap25": by_uf[uf]["demanda_hibrida_3aulas_anos_finais_cap25"],
        }
        for uf in sorted(by_uf)
    ]
    write_csv(
        output_dir / "demanda_hibrida_por_uf.csv",
        hybrid_rows,
        ["uf", "posicoes_regentes_anos_iniciais", "especialistas_anos_finais_2aulas_cap25", "total_hibrido_2aulas_cap25", "especialistas_anos_finais_3aulas_cap25", "total_hibrido_3aulas_cap25"],
    )

    textual = {
        "adicional_sobre_piso_intermediario": national["demanda_intermediario_25"] - national["escolas"],
        "escolas_com_demanda_intermediaria_cap25_maior_1": national["escolas_demanda_intermediaria_cap25_maior_1"],
        "hibrido_2aulas_cap25_regentes_anos_iniciais": national["posicoes_regentes_anos_iniciais"],
        "hibrido_2aulas_cap25_especialistas_anos_finais": national["posicoes_especialistas_anos_finais_2aulas_cap25"],
        "hibrido_2aulas_cap25_total": national["demanda_hibrida_2aulas_anos_finais_cap25"],
        "hibrido_3aulas_cap25_especialistas_anos_finais": national["posicoes_especialistas_anos_finais_3aulas_cap25"],
        "hibrido_3aulas_cap25_total": national["demanda_hibrida_3aulas_anos_finais_cap25"],
    }
    (output_dir / "metricas_textuais_artigo.json").write_text(json.dumps(textual, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    outputs = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    audit = {"status": "PASS", "input": input_path.name, "rows": rows, "unique_school_keys": len(keys), "ufs": len(by_uf), "regions": len(by_region), "outputs": outputs}
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "derived" / "censo_escolar_2025")
    parser.add_argument("--audit", type=Path, default=Path(__file__).resolve().parents[1] / "validation" / "auditoria_derivados_censo_escolar_2025.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = generate(args.input, args.output_dir, args.audit)
    print(f"PASS: {report['rows']} escolas, {len(report['outputs'])} arquivos derivados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
