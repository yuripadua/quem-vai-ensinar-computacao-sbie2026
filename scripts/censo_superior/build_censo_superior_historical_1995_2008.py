#!/usr/bin/env python3
"""Constrói o recorte histórico de docência em Computação (1995–2008).

O script lê diretamente os ZIPs oficiais do INEP, sem alterar ou extrair as
fontes. As regras de quantidade seguem os dicionários anuais. Em particular:

* 1995: inscritos = primeira opção diurna + primeira opção noturna;
* matrículas históricas usam a fotografia do segundo semestre;
* concluintes somam primeiro e segundo semestres quando ambos existem;
* EaD de 2001–2006 e de 2007–2008 usa blocos próprios do questionário;
* 1996 é mantido como fonte oficial parcial e não é convertido em zero.

Nenhum valor é imputado, interpolado ou ajustado para coincidir com resultados
anteriores. Campos em branco continuam identificados nos status de cobertura.
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
from collections import Counter
from pathlib import Path
from typing import Iterable


YEARS = tuple(range(1995, 2009))
DELIMITER = "|"
PARTIAL_SOURCE_YEARS = {1996}


def clean(value: object) -> str:
    return "" if value is None else " ".join(str(value).replace("\t", " ").split())


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", clean(value))
    return " ".join(text.encode("ascii", "ignore").decode("ascii").lower().split())


def positive(value: object) -> bool:
    return normalize(value) in {"1", "s", "sim", "true"}


def first(row: dict[str, str], *fields: str) -> str:
    for field in fields:
        value = clean(row.get(field))
        if value:
            return value
    return ""


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


def detect_encoding(sample: bytes) -> str:
    candidates: list[tuple[int, str]] = []
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            text = sample.decode(encoding)
        except UnicodeDecodeError:
            continue
        score = text.count("Ã") + text.count("Â") + text.count("\ufffd")
        candidates.append((score, encoding))
    if not candidates:
        raise ValueError("Codificação não identificada")
    return min(candidates)[1]


def course_name(row: dict[str, str]) -> str:
    return first(row, "NO_CURSO", "NOMEDOCURSO", "NOME_CURSO", "NO_CURSO_INEP")


def course_habilitation(row: dict[str, str]) -> str:
    return first(row, "NO_CURSO_HABILITACAO", "NO_CURSO_INEP")


def course_area(row: dict[str, str]) -> str:
    fields = (
        "NO_AREA_CONHE",
        "NO_AREA_CONHECIMENTO",
        "NO_AREA",
        "NOMEAREACURSO",
        "NOMEAREAGERAL",
        "NOMEAREAESPECIFICA",
        "NOMEAREAESPECIFIC",
        "NOMEAREADETALHADA",
    )
    return " | ".join(first(row, field) for field in fields if first(row, field))


def classify(row: dict[str, str], year: int) -> str:
    name = " | ".join(part for part in (course_name(row), course_habilitation(row)) if part)
    normalized_name = normalize(name)
    normalized_area = normalize(course_area(row))

    if any(term in normalized_name for term in ("computacao grafica", "artes visuais", "educacao artistica")):
        return ""
    if (
        normalized_name.startswith("matematica")
        or " matematica" in normalized_name
        or "matematica:" in normalized_name
    ) and "formacao de professor de computacao" not in normalized_area:
        return ""

    has_computing = "comput" in normalized_name or "informat" in normalized_name
    explicit_licensure = ("licenciatura" in normalized_name or "licenc" in normalized_name) and has_computing
    informatics_education = any(
        term in normalized_name
        for term in (
            "informatica na educacao",
            "educacao em comput",
            "ensino de comput",
        )
    )
    teacher_area = (
        "formacao de professor de computacao" in normalized_area
        or "professor de computacao" in normalized_area
    )
    licensure_flag = year >= 2000 and any(
        positive(row.get(field)) for field in ("EH_LICENCPLENA", "EH_LICCURTA")
    )

    if explicit_licensure:
        return "nome_licenciatura_computacao_informatica"
    if informatics_education:
        return "nome_informatica_educacao"
    if teacher_area:
        return "area_formacao_professor_computacao"
    if licensure_flag and has_computing:
        return "flag_licenciatura_nome_computacao_informatica"
    return ""


def values_for_fields(row: dict[str, str], fields: Iterable[str]) -> tuple[int, int, list[str]]:
    total = 0
    nonblank = 0
    invalid: list[str] = []
    for field in fields:
        if field not in row:
            continue
        raw = clean(row.get(field))
        if not raw:
            continue
        nonblank += 1
        number = to_int(raw)
        if number is None:
            invalid.append(field)
        else:
            total += number
    return total, nonblank, invalid


def fields_matching(row: dict[str, str], pattern: str) -> list[str]:
    compiled = re.compile(pattern)
    return [field for field in row if compiled.fullmatch(field)]


def metric(row: dict[str, str], fields: Iterable[str], source: str) -> dict[str, object]:
    chosen_fields = list(fields)
    value, nonblank, invalid = values_for_fields(row, chosen_fields)
    if invalid:
        status = "VALOR_INVALIDO"
    elif nonblank:
        status = "OK"
    else:
        status = "SEM_DADO"
    return {"value": value, "source": source, "status": status, "fields": chosen_fields, "invalid": invalid}


def choose_prefix_source(
    row: dict[str, str], sources: list[tuple[str, str]], metric_name: str
) -> dict[str, object]:
    candidates: list[dict[str, object]] = []
    for label, prefix in sources:
        fields = [field for field in row if field.startswith(prefix)]
        candidate = metric(row, fields, label)
        if candidate["status"] == "OK" and int(candidate["value"]) != 0:
            candidates.append(candidate)
    if not candidates:
        all_fields = [field for _, prefix in sources for field in row if field.startswith(prefix)]
        return metric(row, all_fields, "+".join(label for label, _ in sources))
    selected = candidates[0]
    if len(candidates) > 1:
        selected = dict(selected)
        selected["status"] = "MULTIPLAS_FONTES_NAO_SOMADAS"
        selected["source"] = f"{selected['source']}|alternativas=" + ",".join(
            f"{item['source']}:{item['value']}" for item in candidates[1:]
        )
    selected["metric"] = metric_name
    return selected


def quantities_1995_1996(row: dict[str, str]) -> dict[str, dict[str, object]]:
    return {
        "vagas": metric(row, ["QT_VAGAS_DIURNO", "QT_VAGAS_NOTURNO"], "QT_VAGAS_DIURNO+QT_VAGAS_NOTURNO"),
        # O Leia-me define o total por primeira opção; a segunda opção não é somada.
        "inscritos": metric(row, ["QT_INSC_1OPC_DIURNO", "QT_INSC_1OPC_NOTURNO"], "QT_INSC_1OPC_DIURNO+QT_INSC_1OPC_NOTURNO"),
        "ingressantes": metric(
            row,
            [
                "QT_INGR_VEST_FEMI_DIURNO",
                "QT_INGR_OUTROS_FEMI_DIURNO",
                "QT_INGR_VEST_MASC_DIURNO",
                "QT_INGR_OUTROS_MASC_DIURNO",
                "QT_INGR_VEST_FEMI_NOTURNO",
                "QT_INGR_OUTROS_FEMI_NOTURNO",
                "QT_INGR_VEST_MASC_NOTURNO",
                "QT_INGR_OUTROS_MASC_NOTURNO",
            ],
            "QT_INGR_VEST+QT_INGR_OUTROS",
        ),
        "matriculas": metric(
            row,
            ["QT_MAT_ATU_DIU_FEMI", "QT_MAT_ATU_DIU_MASC", "QT_MAT_ATU_NOT_FEMI", "QT_MAT_ATU_NOT_MASC"],
            "QT_MAT_ATU (fotografia do 2º semestre)",
        ),
        "concluintes": metric(
            row,
            ["QT_DIPLO_1SEM_FEMI", "QT_DIPLO_1SEM_MASC", "QT_DIPLO_2SEM_FEMI", "QT_DIPLO_2SEM_MASC"],
            "QT_DIPLO_1SEM+QT_DIPLO_2SEM",
        ),
    }


def quantities_1997(row: dict[str, str]) -> dict[str, dict[str, object]]:
    return {
        "vagas": metric(row, ["QT_VAGA"], "QT_VAGA"),
        "inscritos": metric(row, ["QT_INSCRITO"], "QT_INSCRITO"),
        # O arquivo tem uma linha por forma de ingresso. NO_INGRESSO contém o
        # rótulo da forma (por exemplo, transferência); QT_DIURNO/QT_NOTURNO
        # trazem as quantidades de ingressantes por turno. Os demais totais do
        # curso se repetem nessas linhas e são deduplicados em ``summarize``.
        "ingressantes": metric(row, ["QT_DIURNO", "QT_NOTURNO"], "QT_DIURNO+QT_NOTURNO por forma de ingresso"),
        "matriculas": metric(row, ["QT_FEM_MAT_DIURNO", "QT_FEM_MAT_NOT", "QT_MASC_MAT_DIURNO", "QT_MASC_MAT_NOT"], "QT_FEM/MASC_MAT_DIURNO+NOT"),
        "concluintes": metric(row, ["QT_FEM_DIP", "QT_MASC_DIP"], "QT_FEM_DIP+QT_MASC_DIP"),
    }


def quantities_1998_1999(row: dict[str, str], year: int) -> dict[str, dict[str, object]]:
    if year == 1998:
        vagas = ["C0111", "C0115"]
        inscritos = ["C0112", "C0113", "C0116", "C0117"]
        ingressantes = fields_matching(row, r"C02[1-4][1-4]")
        matriculas = ["MATRICULADOS"]
    else:
        vagas = ["C0111", "C0112", "C0121", "C0122"]
        inscritos = ["C0131", "C0132", "C0133", "C0134", "C0141", "C0142", "C0143", "C0144"]
        # Apenas os sufixos 1–4 representam sexo/turno no quadro usado;
        # outros sufixos pertencem a decomposições que não devem ser somadas.
        ingressantes = fields_matching(row, r"C02\d*[1-4]")
        matriculas = ["C0411", "C0412", "C0413", "C0414"]
    return {
        "vagas": metric(row, vagas, "campos C01 de vagas"),
        "inscritos": metric(row, inscritos, "campos C01 de candidatos inscritos"),
        "ingressantes": metric(row, ingressantes, "campos C02 de ingressantes"),
        "matriculas": metric(row, matriculas, "MATRICULADOS" if year == 1998 else "C0411-C0414"),
        "concluintes": metric(row, ["C0811", "C0812", "C0813", "C0814"], "C0811-C0814"),
    }


def quantities_2000(row: dict[str, str]) -> dict[str, dict[str, object]]:
    return {
        "vagas": metric(row, ["C0111", "C0112", "C0121", "C0122", "C0131", "C0132", "C0141", "C0142"], "Q01/C011-C014 vagas"),
        "inscritos": metric(row, ["C0113", "C0114", "C0115", "C0116", "C0123", "C0124", "C0125", "C0126", "C0133", "C0134", "C0135", "C0136", "C0143", "C0144", "C0145", "C0146"], "Q01/C011-C014 candidatos"),
        "ingressantes": metric(row, fields_matching(row, r"C09\d*[12]"), "Q04/C09 ingressantes por idade e sexo"),
        "matriculas": metric(row, ["C0431", "C0432", "C0433", "C0434"], "Q05/C043 fotografia do 2º semestre"),
        "concluintes": metric(row, ["C1311", "C1312", "C1313", "C1314", "C1321", "C1322", "C1323", "C1324"], "Q12/C131-C132 ambos os semestres"),
    }


def quantities_2001_2008_presencial(row: dict[str, str]) -> dict[str, dict[str, object]]:
    return {
        "vagas": choose_prefix_source(row, [("Q06_CURSO_C630", "C63"), ("Q07_HABILITACOES_C64", "C64"), ("Q08_MODALIDADES_C65", "C65"), ("Q09_MODALIDADES_HABILITACOES_C66", "C66"), ("Q05_AREA_C62", "C62")], "vagas"),
        "inscritos": choose_prefix_source(row, [("Q11_CURSO_C68", "C68"), ("Q12_HABILITACOES_C69", "C69"), ("Q13_MODALIDADES_C70", "C70"), ("Q14_MODALIDADES_HABILITACOES_C71", "C71"), ("Q10_AREA_C67", "C67")], "inscritos"),
        "ingressantes": metric(row, fields_matching(row, r"C09\d*[12]"), "Q22/C09 ingressantes por idade e sexo"),
        "matriculas": metric(row, ["C0431", "C0432", "C0433", "C0434"], "Q24/C043 fotografia do 2º semestre"),
        "concluintes": metric(row, ["C8111", "C8112", "C8113", "C8114", "C8121", "C8122", "C8123", "C8124"], "Q33/C811-C812 ambos os semestres"),
    }


def quantities_2001_2006_ead(row: dict[str, str]) -> dict[str, dict[str, object]]:
    process_groups = r"(?:0[1-5]|0[7-9]|1[01])"
    return {
        "vagas": metric(row, fields_matching(row, rf"C84{process_groups}1"), "Q41/C84 vagas dos dois semestres"),
        "inscritos": metric(row, fields_matching(row, rf"C84{process_groups}[23]"), "Q41/C84 candidatos inscritos dos dois semestres"),
        "ingressantes": metric(row, fields_matching(row, rf"C84{process_groups}[45]|C84(?:06|12)[45]"), "Q41/C84 ingressantes por processo e outras formas"),
        "matriculas": metric(row, ["C2021", "C2022"], "Q43/C202 fotografia do 2º semestre"),
        "concluintes": metric(row, ["C2211", "C2212", "C2221", "C2222"], "Q45/C221-C222 ambos os semestres"),
    }


def quantities_2007_2008_ead(row: dict[str, str]) -> dict[str, dict[str, object]]:
    return {
        "vagas": metric(row, fields_matching(row, r"C94\d{2}1"), "Q04/C94 vagas dos dois semestres"),
        "inscritos": metric(row, fields_matching(row, r"C98\d{2}[12]"), "Q08/C98 candidatos inscritos dos dois semestres"),
        "ingressantes": metric(row, fields_matching(row, r"C161\d{3}"), "Q18/C161 ingressantes totais por idade e sexo"),
        "matriculas": metric(row, ["C167021", "C167022"], "Q24/C167 fotografia do 2º semestre"),
        "concluintes": metric(row, ["C164011", "C164012", "C164021", "C164022"], "Q21/C164 ambos os semestres"),
    }


def reconstruct_quantities(row: dict[str, str], year: int, modality: str) -> dict[str, dict[str, object]]:
    if year in {1995, 1996}:
        return quantities_1995_1996(row)
    if year == 1997:
        return quantities_1997(row)
    if year in {1998, 1999}:
        return quantities_1998_1999(row, year)
    if year == 2000:
        return quantities_2000(row)
    if modality == "ead" and year <= 2006:
        return quantities_2001_2006_ead(row)
    if modality == "ead":
        return quantities_2007_2008_ead(row)
    return quantities_2001_2008_presencial(row)


def graduation_members(zf: zipfile.ZipFile) -> list[str]:
    return [
        member
        for member in zf.namelist()
        if re.search(r"(?:^|/)GRADUACAO[^/]*\.CSV$", member, flags=re.IGNORECASE)
    ]


def record_from_row(
    archive: Path,
    member: str,
    line_number: int,
    year: int,
    row: dict[str, str],
    criterion: str,
) -> dict[str, object]:
    modality = "ead" if "DISTANCIA" in Path(member).name.upper() else "presencial"
    quantities = reconstruct_quantities(row, year, modality)
    output: dict[str, object] = {
        "ano": year,
        "arquivo_zip": archive.name,
        "arquivo_csv": member,
        "linha_csv": line_number,
        "modalidade": modality,
        "co_ies": first(row, "IES", "MASCARA", "CO_IES"),
        "co_curso": first(row, "CURSO", "CD_CURSO", "CO_CURSO", "CO_CURSO_INEP", "CD_CURSO_SEEC"),
        "no_curso": course_name(row),
        "area_curso": course_area(row),
        "criterio_selecao": criterion,
        "status_fonte": "FONTE_OFICIAL_PARCIAL" if year in PARTIAL_SOURCE_YEARS else "FONTE_OFICIAL",
    }
    for name, item in quantities.items():
        output[f"qt_{name}"] = item["value"]
        output[f"fonte_qt_{name}"] = item["source"]
        output[f"status_qt_{name}"] = item["status"]
    return output


def summarize(records: list[dict[str, object]], year: int, archive: Path) -> dict[str, object]:
    selected = [record for record in records if record["ano"] == year]
    if year in PARTIAL_SOURCE_YEARS:
        return {
            "ano": year,
            "arquivo_zip": archive.name,
            "status_qualidade": "FONTE_OFICIAL_PARCIAL_NAO_COMPARAVEL",
            "linhas_recorte": "",
            "linhas_presencial": "",
            "linhas_ead": "",
            "qt_curso_proxy": "",
            "qt_curso_proxy_presencial": "",
            "qt_curso_proxy_ead": "",
            "qt_vagas": "",
            "qt_inscritos": "",
            "qt_ingressantes": "",
            "qt_matriculas": "",
            "qt_concluintes": "",
            "observacao": "Somente 53 de 7.256 registros oficiais têm nome/classificação; nenhum zero é inferido.",
        }

    course_keys = {
        (
            clean(record.get("arquivo_csv")),
            clean(record.get("co_ies")),
            clean(record.get("co_curso")),
            clean(record.get("no_curso")),
        )
        for record in selected
    }
    course_keys_by_modality = {
        modality: {
            (
                clean(record.get("arquivo_csv")),
                clean(record.get("co_ies")),
                clean(record.get("co_curso")),
                clean(record.get("no_curso")),
            )
            for record in selected
            if clean(record.get("modalidade")) == modality
        }
        for modality in ("presencial", "ead")
    }
    summary: dict[str, object] = {
        "ano": year,
        "arquivo_zip": archive.name,
        "status_qualidade": "RECONSTRUIDO_DICIONARIO_OFICIAL",
        "linhas_recorte": len(selected),
        "linhas_presencial": sum(record["modalidade"] == "presencial" for record in selected),
        "linhas_ead": sum(record["modalidade"] == "ead" for record in selected),
        "qt_curso_proxy": len(course_keys),
        "qt_curso_proxy_presencial": len(course_keys_by_modality["presencial"]),
        "qt_curso_proxy_ead": len(course_keys_by_modality["ead"]),
        "observacao": "QT_CURSO não existia no leiaute; linhas do arquivo de graduação são mantidas como proxy identificada.",
    }
    for metric_name in ("vagas", "inscritos", "ingressantes", "matriculas", "concluintes"):
        status_field = f"status_qt_{metric_name}"
        value_field = f"qt_{metric_name}"
        statuses = Counter(clean(record.get(status_field)) for record in selected)
        valid_statuses = {"OK", "MULTIPLAS_FONTES_NAO_SOMADAS"}
        invalid_count = sum(
            count for status, count in statuses.items() if status not in valid_statuses | {"SEM_DADO"}
        )
        with_data = sum(count for status, count in statuses.items() if status in valid_statuses)
        if invalid_count:
            summary[value_field] = ""
            aggregate_status = "VALOR_INVALIDO"
        elif not selected or with_data == 0:
            summary[value_field] = ""
            aggregate_status = "SEM_DADO"
        else:
            if year == 1997 and metric_name != "ingressantes":
                # Vagas, inscritos, matrículas e diplomados são totais do
                # curso repetidos em cada forma de ingresso. Conserva-se uma
                # única observação por curso, após verificar a consistência.
                grouped: dict[tuple[str, str, str, str], list[int]] = {}
                for record in selected:
                    if clean(record.get(status_field)) not in valid_statuses:
                        continue
                    key = (
                        clean(record.get("arquivo_csv")),
                        clean(record.get("co_ies")),
                        clean(record.get("co_curso")),
                        clean(record.get("no_curso")),
                    )
                    grouped.setdefault(key, []).append(int(record[value_field]))
                inconsistent = {key: values for key, values in grouped.items() if len(set(values)) != 1}
                if inconsistent:
                    raise ValueError(
                        f"1997: total de {metric_name} divergente entre formas de ingresso: {inconsistent}"
                    )
                summary[value_field] = sum(values[0] for values in grouped.values())
            else:
                summary[value_field] = sum(
                    int(record[value_field])
                    for record in selected
                    if clean(record.get(status_field)) in valid_statuses
                )
            aggregate_status = "OK" if with_data == len(selected) else "PARCIAL"
        summary[f"status_{value_field}"] = aggregate_status
        summary[f"linhas_sem_dado_{metric_name}"] = statuses.get("SEM_DADO", 0)
    return summary


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs="+", type=Path)
    parser.add_argument("--details-csv", type=Path, required=True)
    parser.add_argument("--summary-csv", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    args = parser.parse_args()

    csv.field_size_limit(min(sys.maxsize, 2_147_483_647))
    archives_by_year: dict[int, Path] = {}
    for archive in args.archives:
        match = re.search(r"(?:19|20)\d{2}", archive.name)
        if not archive.is_file() or not match:
            parser.error(f"ZIP inexistente ou sem ano no nome: {archive}")
        year = int(match.group())
        if year not in YEARS:
            parser.error(f"Ano fora de 1995–2008: {archive}")
        if year in archives_by_year:
            parser.error(f"Mais de um ZIP para {year}")
        archives_by_year[year] = archive
    missing = [str(year) for year in YEARS if year not in archives_by_year]
    if missing:
        parser.error("Faltam ZIPs: " + ", ".join(missing))

    records: list[dict[str, object]] = []
    for year in YEARS:
        archive = archives_by_year[year]
        with zipfile.ZipFile(archive) as zf:
            members = graduation_members(zf)
            if not members:
                raise ValueError(f"Nenhum GRADUACAO*.CSV em {archive}")
            for member in sorted(members):
                with zf.open(member) as sample_stream:
                    encoding = detect_encoding(sample_stream.read(200_000))
                with zf.open(member) as binary_stream:
                    text_stream = io.TextIOWrapper(binary_stream, encoding=encoding, errors="strict", newline="")
                    reader = csv.DictReader(text_stream, delimiter=DELIMITER)
                    if not reader.fieldnames:
                        raise ValueError(f"Cabeçalho ausente em {archive.name}:{member}")
                    for line_number, row in enumerate(reader, start=2):
                        criterion = classify(row, year)
                        if criterion:
                            records.append(record_from_row(archive, member, line_number, year, row, criterion))

    summaries = [summarize(records, year, archives_by_year[year]) for year in YEARS]
    write_csv(args.details_csv, records)
    write_csv(args.summary_csv, summaries)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(
        json.dumps({"summary": summaries, "records": records}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    for summary in summaries:
        print(
            f"{summary['ano']}: status={summary['status_qualidade']}; "
            f"linhas={summary['linhas_recorte']}; concluintes={summary['qt_concluintes']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
