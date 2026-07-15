#!/usr/bin/env python3
"""Perfila recortes de cursos do Censo Superior diretamente dos ZIPs oficiais.

Replica, para fins de auditoria, as regras documentadas nos scripts legados 23
e 28. As saídas são diagnósticas: não constituem bases finais do artigo e não
alteram nem imputam valores dos microdados.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path


QUANTITY_FIELDS = (
    "QT_CURSO",
    "QT_VG_TOTAL",
    "QT_INSCRITO_TOTAL",
    "QT_ING",
    "QT_MAT",
    "QT_CONC",
    "QT_CONC_FEM",
    "QT_CONC_MASC",
)

IDENTITIES = {
    "vagas_turno_modalidade": (
        "QT_VG_TOTAL",
        ("QT_VG_TOTAL_DIURNO", "QT_VG_TOTAL_NOTURNO", "QT_VG_TOTAL_EAD"),
    ),
    "inscritos_turno_modalidade": (
        "QT_INSCRITO_TOTAL",
        ("QT_INSCRITO_TOTAL_DIURNO", "QT_INSCRITO_TOTAL_NOTURNO", "QT_INSCRITO_TOTAL_EAD"),
    ),
    "ingressantes_sexo": ("QT_ING", ("QT_ING_FEM", "QT_ING_MASC")),
    "matriculas_sexo": ("QT_MAT", ("QT_MAT_FEM", "QT_MAT_MASC")),
    "concluintes_sexo": ("QT_CONC", ("QT_CONC_FEM", "QT_CONC_MASC")),
}


def normalize(value: object) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    return " ".join(text.encode("ascii", "ignore").decode("ascii").lower().split())


def clean(value: object) -> str:
    return "" if value is None else " ".join(str(value).replace("\t", " ").split())


def to_int(value: object) -> int | None:
    text = clean(value)
    if not text:
        return None
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    try:
        number = float(text.replace(",", "."))
    except ValueError:
        return None
    return int(number) if number.is_integer() else None


def find_member(zf: zipfile.ZipFile, token: str, year: int) -> str:
    tokens = [token]
    if token == "MICRODADOS_CADASTRO_IES":
        # O INEP mudou o nome físico a partir de 2022, mantendo o mesmo
        # conteúdo lógico e o nome anterior no manifesto MD5.
        tokens.append("MICRODADOS_ED_SUP_IES")
    expected = {f"{candidate}_{year}.csv".lower() for candidate in tokens}
    matches = [name for name in zf.namelist() if Path(name).name.lower() in expected]
    if len(matches) != 1:
        raise ValueError(f"Esperado exatamente um de {sorted(expected)}; encontrados: {matches}")
    return matches[0]


def iter_dict_rows(zf: zipfile.ZipFile, member: str):
    raw = zf.open(member)
    text = io.TextIOWrapper(raw, encoding="cp1252", errors="strict", newline="")
    reader = csv.DictReader(text, delimiter=";")
    if not reader.fieldnames:
        text.close()
        raise ValueError(f"Cabeçalho não encontrado em {member}")
    try:
        for row in reader:
            yield row
    finally:
        text.close()


def is_graduation(row: dict[str, str]) -> bool:
    level = clean(row.get("TP_NIVEL_ACADEMICO"))
    return not level or level == "1"


def modern_is_licensure_or_pedagogy(row: dict[str, str]) -> tuple[bool, str]:
    if not is_graduation(row):
        return False, ""
    course_name = normalize(row.get("NO_CURSO"))
    cine_text = normalize(
        " | ".join(
            clean(row.get(field))
            for field in (
                "NO_CINE_ROTULO",
                "NO_CINE_AREA_GERAL",
                "NO_CINE_AREA_ESPECIFICA",
                "NO_CINE_AREA_DETALHADA",
            )
        )
    )
    degree = clean(row.get("TP_GRAU_ACADEMICO"))
    if "pedagog" in course_name:
        return True, "nome_pedagogia"
    if degree in {"2", "4"}:
        return True, f"grau_academico={degree}"
    if "formacao de professor" in cine_text or ("educacao" in cine_text and "professor" in cine_text):
        return True, "cine_formacao_professor"
    return False, ""


def is_education_professional_technology(row: dict[str, str]) -> bool:
    name = normalize(row.get("NO_CURSO"))
    return "educacao profissional" in name and "tecnologic" in name


def is_teacher_computing_cine(row: dict[str, str]) -> bool:
    cine_label = normalize(row.get("NO_CINE_ROTULO"))
    cine_text = " | ".join(
        normalize(row.get(field))
        for field in (
            "NO_CINE_ROTULO",
            "NO_CINE_AREA_GERAL",
            "NO_CINE_AREA_ESPECIFICA",
            "NO_CINE_AREA_DETALHADA",
        )
    )
    return (
        "computacao formacao de professor" in cine_label
        or "formacao de professor de computacao" in cine_text
        or ("computacao" in cine_text and "formacao de professor" in cine_text and "educacao" in cine_text)
    )


def classify_computing_teacher_course(row: dict[str, str]) -> str:
    if not is_graduation(row) or is_education_professional_technology(row):
        return ""
    course_name = normalize(row.get("NO_CURSO"))
    degree = clean(row.get("TP_GRAU_ACADEMICO"))
    licensure_degree = degree in {"2", "4"}
    teacher_computing_cine = is_teacher_computing_cine(row)
    has_computing_term = "comput" in course_name or "informat" in course_name
    explicit_licensure = (
        any(term in course_name for term in ("licenciatura", "licenciatura plena", "licenc"))
        and has_computing_term
    )
    informatics_education = any(
        term in course_name
        for term in (
            "informatica na educacao",
            "informatica educacional",
            "informatica educativa",
            "educacao em comput",
            "ensino de comput",
        )
    )
    requested_pedagogy = (
        "pedagogia" in course_name
        and "multimeios" in course_name
        and ("informatica" in course_name or "comput" in course_name)
    )
    requested_interdisciplinary = "interdisciplinar em matematica e computacao e suas tecnologias" in course_name

    if teacher_computing_cine and explicit_licensure:
        return "cine_computacao_professor_e_nome_licenciatura"
    if teacher_computing_cine and informatics_education:
        return "cine_computacao_professor_e_nome_informatica_educacional"
    if teacher_computing_cine:
        return "cine_computacao_formacao_professor"
    if explicit_licensure:
        return "nome_licenciatura_computacao_informatica"
    if informatics_education and licensure_degree:
        return "nome_informatica_educacao_grau_licenciatura"
    if requested_pedagogy:
        return "pedagogia_multimeios_informatica"
    if requested_interdisciplinary:
        return "interdisciplinar_matematica_computacao"
    return ""


def new_identity_counter() -> dict[str, dict[str, int]]:
    return {
        name: {
            "tested": 0,
            "matches": 0,
            "mismatches": 0,
            "total_sum": 0,
            "components_sum": 0,
            "delta_sum": 0,
            "max_abs_delta": 0,
        }
        for name in IDENTITIES
    }


def check_identities(row: dict[str, str], counters: dict[str, dict[str, int]]) -> None:
    for name, (total_field, component_fields) in IDENTITIES.items():
        raw_values = [clean(row.get(field)) for field in (total_field, *component_fields)]
        if any(value == "" for value in raw_values):
            continue
        parsed = [to_int(value) for value in raw_values]
        if any(value is None for value in parsed):
            continue
        total = parsed[0]
        components = sum(parsed[1:])
        delta = total - components
        counters[name]["tested"] += 1
        counters[name]["total_sum"] += total
        counters[name]["components_sum"] += components
        counters[name]["delta_sum"] += delta
        counters[name]["max_abs_delta"] = max(counters[name]["max_abs_delta"], abs(delta))
        if delta == 0:
            counters[name]["matches"] += 1
        else:
            counters[name]["mismatches"] += 1


def empty_selection() -> dict:
    return {
        "rows": 0,
        "course_codes": set(),
        "course_code_qt_course": Counter(),
        "ies_codes": set(),
        "criteria": Counter(),
        "modality": Counter(),
        "quantity_sums": Counter(),
        "quantity_sums_by_dimension": defaultdict(Counter),
        "invalid_quantities": Counter(),
        "negative_quantities": Counter(),
        "identities": new_identity_counter(),
    }


def add_selection(selection: dict, row: dict[str, str], criterion: str) -> None:
    selection["rows"] += 1
    course_code = clean(row.get("CO_CURSO"))
    ies_code = clean(row.get("CO_IES"))
    if course_code:
        selection["course_codes"].add(course_code)
        selection["course_code_qt_course"][course_code] += to_int(row.get("QT_CURSO")) or 0
    if ies_code:
        selection["ies_codes"].add(ies_code)
    selection["criteria"][criterion] += 1
    modality = clean(row.get("TP_MODALIDADE_ENSINO")) or "blank"
    dimension = clean(row.get("TP_DIMENSAO")) or "blank"
    selection["modality"][modality] += 1
    for field in QUANTITY_FIELDS:
        raw = clean(row.get(field))
        value = to_int(raw)
        if raw and value is None:
            selection["invalid_quantities"][field] += 1
        elif value is not None:
            selection["quantity_sums"][field] += value
            selection["quantity_sums_by_dimension"][dimension][field] += value
            if value < 0:
                selection["negative_quantities"][field] += 1
    check_identities(row, selection["identities"])


def finalize_selection(selection: dict) -> dict:
    codes_without_positive_qt_course = sorted(
        code for code in selection["course_codes"] if selection["course_code_qt_course"].get(code, 0) <= 0
    )
    return {
        "rows": selection["rows"],
        "distinct_course_codes": len(selection["course_codes"]),
        "distinct_ies_codes": len(selection["ies_codes"]),
        "course_codes_without_positive_qt_course": codes_without_positive_qt_course,
        "criteria": dict(sorted(selection["criteria"].items())),
        "modality": dict(sorted(selection["modality"].items())),
        "quantity_sums": {field: selection["quantity_sums"].get(field, 0) for field in QUANTITY_FIELDS},
        "quantity_sums_by_dimension": {
            dimension: {field: sums.get(field, 0) for field in QUANTITY_FIELDS}
            for dimension, sums in sorted(selection["quantity_sums_by_dimension"].items())
        },
        "invalid_quantities": dict(sorted(selection["invalid_quantities"].items())),
        "negative_quantities": dict(sorted(selection["negative_quantities"].items())),
        "identities": selection["identities"],
    }


def profile_archive(path: Path) -> dict:
    year_match = re.search(r"(19|20)\d{2}", path.name)
    if not year_match:
        raise ValueError(f"Ano não identificado no nome: {path}")
    year = int(year_match.group(0))
    with zipfile.ZipFile(path) as zf:
        ies_member = find_member(zf, "MICRODADOS_CADASTRO_IES", year)
        course_member = find_member(zf, "MICRODADOS_CADASTRO_CURSOS", year)
        ies_codes = {clean(row.get("CO_IES")) for row in iter_dict_rows(zf, ies_member) if clean(row.get("CO_IES"))}

        total_rows = 0
        year_mismatches = 0
        course_codes = Counter()
        course_ies_codes = set()
        course_ies_missing_parent = Counter()
        degree_counts = Counter()
        level_counts = Counter()
        modality_counts = Counter()
        dimension_counts = Counter()
        missing_degree_by_level = Counter()
        all_identities = new_identity_counter()
        all_quantity_sums_by_dimension = defaultdict(Counter)
        lic_ped = empty_selection()
        computing = empty_selection()

        for row in iter_dict_rows(zf, course_member):
            total_rows += 1
            if clean(row.get("NU_ANO_CENSO")) != str(year):
                year_mismatches += 1
            course_code = clean(row.get("CO_CURSO"))
            ies_code = clean(row.get("CO_IES"))
            if course_code:
                course_codes[course_code] += 1
            if ies_code:
                course_ies_codes.add(ies_code)
                if ies_code not in ies_codes:
                    course_ies_missing_parent[ies_code] += 1
            degree = clean(row.get("TP_GRAU_ACADEMICO")) or "blank"
            level = clean(row.get("TP_NIVEL_ACADEMICO")) or "blank"
            modality = clean(row.get("TP_MODALIDADE_ENSINO")) or "blank"
            dimension = clean(row.get("TP_DIMENSAO")) or "blank"
            degree_counts[degree] += 1
            level_counts[level] += 1
            modality_counts[modality] += 1
            dimension_counts[dimension] += 1
            if degree == "blank":
                missing_degree_by_level[level] += 1
            for field in QUANTITY_FIELDS:
                value = to_int(row.get(field))
                if value is not None:
                    all_quantity_sums_by_dimension[dimension][field] += value
            check_identities(row, all_identities)

            include, criterion = modern_is_licensure_or_pedagogy(row)
            if include:
                add_selection(lic_ped, row, criterion)
            computing_criterion = classify_computing_teacher_course(row)
            if computing_criterion:
                add_selection(computing, row, computing_criterion)

        lic_ped_result = finalize_selection(lic_ped)
        computing_result = finalize_selection(computing)
        anomaly_codes = set(lic_ped_result["course_codes_without_positive_qt_course"])
        anomaly_details = defaultdict(list)
        if anomaly_codes:
            for row in iter_dict_rows(zf, course_member):
                course_code = clean(row.get("CO_CURSO"))
                if course_code not in anomaly_codes:
                    continue
                anomaly_details[course_code].append(
                    {
                        "NO_CURSO": clean(row.get("NO_CURSO")),
                        "NO_CINE_ROTULO": clean(row.get("NO_CINE_ROTULO")),
                        "TP_GRAU_ACADEMICO": clean(row.get("TP_GRAU_ACADEMICO")),
                        "TP_NIVEL_ACADEMICO": clean(row.get("TP_NIVEL_ACADEMICO")),
                        "TP_MODALIDADE_ENSINO": clean(row.get("TP_MODALIDADE_ENSINO")),
                        "TP_DIMENSAO": clean(row.get("TP_DIMENSAO")),
                        "QT_CURSO": clean(row.get("QT_CURSO")),
                        "QT_CONC": clean(row.get("QT_CONC")),
                    }
                )

    duplicate_course_codes = sum(1 for count in course_codes.values() if count > 1)
    duplicate_course_code_rows = sum(count - 1 for count in course_codes.values() if count > 1)
    return {
        "year": year,
        "archive": str(path.resolve()),
        "course_rows": total_rows,
        "ies_rows": len(ies_codes),
        "year_mismatches": year_mismatches,
        "distinct_course_codes": len(course_codes),
        "course_codes_with_multiple_rows": duplicate_course_codes,
        "rows_beyond_first_per_course_code": duplicate_course_code_rows,
        "distinct_course_ies_codes": len(course_ies_codes),
        "course_rows_with_missing_ies_parent": sum(course_ies_missing_parent.values()),
        "missing_ies_parent_codes": dict(sorted(course_ies_missing_parent.items())),
        "degree_counts": dict(sorted(degree_counts.items())),
        "level_counts": dict(sorted(level_counts.items())),
        "modality_counts": dict(sorted(modality_counts.items())),
        "dimension_counts": dict(sorted(dimension_counts.items())),
        "missing_degree_by_level": dict(sorted(missing_degree_by_level.items())),
        "all_row_identities": all_identities,
        "all_quantity_sums_by_dimension": {
            dimension: {field: sums.get(field, 0) for field in QUANTITY_FIELDS}
            for dimension, sums in sorted(all_quantity_sums_by_dimension.items())
        },
        "licenciaturas_pedagogia": lic_ped_result,
        "licenciaturas_pedagogia_course_code_anomalies": {
            code: rows for code, rows in sorted(anomaly_details.items())
        },
        "docencia_computacao": computing_result,
    }


def write_summary(profiles: list[dict], path: Path) -> None:
    fields = [
        "ano",
        "linhas_cursos",
        "codigos_curso_distintos",
        "linhas_adicionais_mesmo_codigo_curso",
        "ies",
        "linhas_sem_ies_correspondente",
        "linhas_licenciaturas_pedagogia",
        "codigos_curso_licenciaturas_pedagogia",
        "qt_curso_licenciaturas_pedagogia",
        "concluintes_licenciaturas_pedagogia",
        "linhas_docencia_computacao",
        "codigos_curso_docencia_computacao",
        "qt_curso_docencia_computacao",
        "concluintes_docencia_computacao",
        "divergencias_ano",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for profile in profiles:
            lic = profile["licenciaturas_pedagogia"]
            comp = profile["docencia_computacao"]
            writer.writerow(
                {
                    "ano": profile["year"],
                    "linhas_cursos": profile["course_rows"],
                    "codigos_curso_distintos": profile["distinct_course_codes"],
                    "linhas_adicionais_mesmo_codigo_curso": profile["rows_beyond_first_per_course_code"],
                    "ies": profile["ies_rows"],
                    "linhas_sem_ies_correspondente": profile["course_rows_with_missing_ies_parent"],
                    "linhas_licenciaturas_pedagogia": lic["rows"],
                    "codigos_curso_licenciaturas_pedagogia": lic["distinct_course_codes"],
                    "qt_curso_licenciaturas_pedagogia": lic["quantity_sums"]["QT_CURSO"],
                    "concluintes_licenciaturas_pedagogia": lic["quantity_sums"]["QT_CONC"],
                    "linhas_docencia_computacao": comp["rows"],
                    "codigos_curso_docencia_computacao": comp["distinct_course_codes"],
                    "qt_curso_docencia_computacao": comp["quantity_sums"]["QT_CURSO"],
                    "concluintes_docencia_computacao": comp["quantity_sums"]["QT_CONC"],
                    "divergencias_ano": profile["year_mismatches"],
                }
            )


def main() -> int:
    csv.field_size_limit(min(sys.maxsize, 2_147_483_647))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs="+", type=Path)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    args = parser.parse_args()

    profiles = [profile_archive(path) for path in sorted(args.archives)]
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(profiles, ensure_ascii=False, indent=2), encoding="utf-8")
    write_summary(profiles, args.csv)
    for profile in profiles:
        print(
            f"{profile['year']}: cursos={profile['course_rows']}; "
            f"lic/ped={profile['licenciaturas_pedagogia']['rows']}; "
            f"computação={profile['docencia_computacao']['rows']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
