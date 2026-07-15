#!/usr/bin/env python3
"""Audita ZIPs oficiais do Censo da Educação Superior sem alterar as fontes.

O script verifica a integridade CRC, compara os CSVs com os MD5 publicados
dentro de cada ZIP e produz um perfil estrutural compacto. Nenhum dado é
imputado, harmonizado ou sintetizado.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import BinaryIO, Iterable


IMPORTANT_FIELDS = (
    "NU_ANO_CENSO",
    "CO_IES",
    "CO_CURSO",
    "NO_CURSO",
    "CO_OCDE_AREA_GERAL",
    "CO_OCDE_AREA_ESPECIFICA",
    "CO_OCDE_AREA_DETALHADA",
    "CO_OCDE",
    "TP_GRAU_ACADEMICO",
    "TP_MODALIDADE_ENSINO",
    "QT_VAGAS_NOVAS_OFERECIDAS",
    "QT_INSCRITO_TOTAL",
    "QT_INGRESSO_TOTAL",
    "QT_MATRICULA_TOTAL",
    "QT_CONCLUINTE_TOTAL",
)

KEY_CANDIDATES = ("CO_CURSO", "CO_IES")
MD5_RE = re.compile(r"^([0-9a-fA-F]{32})\s+\*?(.+?)\s*$")


def hash_stream(stream: BinaryIO, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def hash_file(path: Path, algorithm: str = "sha256") -> str:
    with path.open("rb") as stream:
        return hash_stream(stream, algorithm)


def decode_text(raw: bytes) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "cp1252", "latin1"):
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("unknown", raw, 0, 1, "codificação não identificada")


def detect_csv_format(zf: zipfile.ZipFile, member: str) -> tuple[str, str]:
    with zf.open(member) as stream:
        sample = stream.read(256 * 1024)
    text, encoding = decode_text(sample)
    first_line = text.splitlines()[0] if text.splitlines() else ""
    delimiters = ("|", ";", "\t", ",")
    delimiter = max(delimiters, key=first_line.count)
    if first_line.count(delimiter) == 0:
        raise ValueError(f"Separador não identificado em {member}")
    return encoding, delimiter


def parse_official_md5(zf: zipfile.ZipFile, members: Iterable[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for member in members:
        raw = zf.read(member)
        text, _ = decode_text(raw)
        for line in text.splitlines():
            match = MD5_RE.match(line.strip())
            if not match:
                continue
            digest, file_name = match.groups()
            parsed[Path(file_name.strip()).name.lower()] = digest.lower()
    return parsed


def resolve_official_md5(
    member: str, official_md5: dict[str, str]
) -> tuple[str | None, str | None]:
    """Resolve o nome real do CSV contra o nome publicado no manifesto.

    Nos pacotes de 2022 em diante, o arquivo de IES passou a se chamar
    ``MICRODADOS_ED_SUP_IES_AAAA.CSV``, mas o manifesto MD5 continuou usando
    ``MICRODADOS_CADASTRO_IES_AAAA.csv``. A equivalência é apenas nominal; o
    hash continua sendo comparado byte a byte.
    """

    basename = Path(member).name.lower()
    candidates = [basename]
    if "microdados_ed_sup_ies_" in basename:
        candidates.append(basename.replace("microdados_ed_sup_ies_", "microdados_cadastro_ies_"))
    for candidate in candidates:
        if candidate in official_md5:
            return official_md5[candidate], candidate
    return None, None


def profile_csv(
    zf: zipfile.ZipFile,
    member: str,
    expected_md5: str | None,
    manifest_basename: str | None,
) -> dict:
    encoding, delimiter = detect_csv_format(zf, member)
    with zf.open(member) as raw_stream:
        actual_md5 = hash_stream(raw_stream, "md5")

    csv.field_size_limit(min(sys.maxsize, 2_147_483_647))
    with zf.open(member) as raw_stream:
        text_stream = io.TextIOWrapper(raw_stream, encoding=encoding, errors="strict", newline="")
        reader = csv.reader(text_stream, delimiter=delimiter)
        header = next(reader, [])
        header = [value.lstrip("\ufeff").strip() for value in header]
        index = {name: position for position, name in enumerate(header)}
        tracked = [name for name in IMPORTANT_FIELDS if name in index]
        nonempty = {name: 0 for name in tracked}
        distinct = {name: set() for name in KEY_CANDIDATES if name in index}
        data_rows = 0
        malformed_rows = 0
        blank_rows = 0
        min_fields: int | None = None
        max_fields: int | None = None

        for row in reader:
            if not row or all(not value.strip() for value in row):
                blank_rows += 1
                continue
            data_rows += 1
            field_count = len(row)
            min_fields = field_count if min_fields is None else min(min_fields, field_count)
            max_fields = field_count if max_fields is None else max(max_fields, field_count)
            if field_count != len(header):
                malformed_rows += 1
                continue
            for name in tracked:
                value = row[index[name]].strip()
                if value:
                    nonempty[name] += 1
            for name, values in distinct.items():
                value = row[index[name]].strip()
                if value:
                    values.add(value)

    completeness = {
        name: {
            "nonempty": count,
            "empty": data_rows - count,
            "nonempty_rate": round(count / data_rows, 8) if data_rows else None,
        }
        for name, count in nonempty.items()
    }
    distinct_counts = {name: len(values) for name, values in distinct.items()}

    return {
        "member": member,
        "basename": Path(member).name,
        "encoding": encoding,
        "delimiter": delimiter,
        "column_count": len(header),
        "columns": header,
        "data_rows": data_rows,
        "blank_rows": blank_rows,
        "malformed_rows": malformed_rows,
        "min_fields": min_fields,
        "max_fields": max_fields,
        "md5_expected": expected_md5,
        "md5_actual": actual_md5,
        "md5_matches": expected_md5 == actual_md5 if expected_md5 else None,
        "md5_manifest_basename": manifest_basename,
        "completeness": completeness,
        "distinct_key_counts": distinct_counts,
    }


def audit_archive(path: Path) -> dict:
    year_match = re.search(r"(19|20)\d{2}", path.name)
    year = int(year_match.group(0)) if year_match else None
    archive = {
        "year": year,
        "archive": str(path.resolve()),
        "size_bytes": path.stat().st_size,
        "sha256": hash_file(path),
    }

    with zipfile.ZipFile(path) as zf:
        members = zf.namelist()
        bad_member = zf.testzip()
        csv_members = [name for name in members if name.lower().endswith(".csv")]
        md5_members = [name for name in members if name.lower().endswith(".txt") and "md5" in name.lower()]
        dictionary_members = [
            name
            for name in members
            if not Path(name).name.startswith("~$")
            and ("dicion" in name.lower() or "dictionary" in name.lower())
            and name.lower().endswith((".xlsx", ".xls", ".csv", ".pdf"))
        ]
        readme_members = [
            name
            for name in members
            if not Path(name).name.startswith("~$")
            and ("leia" in name.lower() or "readme" in name.lower() or "nota informativa" in name.lower())
            and name.lower().endswith((".pdf", ".txt", ".doc", ".docx"))
        ]
        official_md5 = parse_official_md5(zf, md5_members)
        csv_profiles = []
        for member in csv_members:
            expected, manifest_basename = resolve_official_md5(member, official_md5)
            csv_profiles.append(profile_csv(zf, member, expected, manifest_basename))

    archive.update(
        {
            "zip_member_count": len(members),
            "crc_ok": bad_member is None,
            "bad_member": bad_member,
            "csv_count": len(csv_members),
            "md5_manifest_count": len(md5_members),
            "official_md5_entry_count": len(official_md5),
            "all_csv_md5_match": bool(csv_profiles)
            and all(profile["md5_matches"] is True for profile in csv_profiles),
            "dictionary_members": dictionary_members,
            "readme_members": readme_members,
            "csv_profiles": csv_profiles,
        }
    )
    return archive


def write_summary_csv(audits: list[dict], path: Path) -> None:
    fieldnames = [
        "year",
        "archive",
        "archive_size_bytes",
        "archive_sha256",
        "crc_ok",
        "all_csv_md5_match",
        "csv_basename",
        "encoding",
        "delimiter",
        "column_count",
        "data_rows",
        "malformed_rows",
        "md5_expected",
        "md5_actual",
        "md5_matches",
        "md5_manifest_basename",
        "co_curso_nonempty",
        "co_curso_distinct",
        "no_curso_nonempty",
        "co_ies_nonempty",
        "co_ies_distinct",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for audit in audits:
            for profile in audit["csv_profiles"]:
                completeness = profile["completeness"]
                distinct = profile["distinct_key_counts"]
                writer.writerow(
                    {
                        "year": audit["year"],
                        "archive": audit["archive"],
                        "archive_size_bytes": audit["size_bytes"],
                        "archive_sha256": audit["sha256"],
                        "crc_ok": audit["crc_ok"],
                        "all_csv_md5_match": audit["all_csv_md5_match"],
                        "csv_basename": profile["basename"],
                        "encoding": profile["encoding"],
                        "delimiter": profile["delimiter"],
                        "column_count": profile["column_count"],
                        "data_rows": profile["data_rows"],
                        "malformed_rows": profile["malformed_rows"],
                        "md5_expected": profile["md5_expected"],
                        "md5_actual": profile["md5_actual"],
                        "md5_matches": profile["md5_matches"],
                        "md5_manifest_basename": profile["md5_manifest_basename"],
                        "co_curso_nonempty": completeness.get("CO_CURSO", {}).get("nonempty"),
                        "co_curso_distinct": distinct.get("CO_CURSO"),
                        "no_curso_nonempty": completeness.get("NO_CURSO", {}).get("nonempty"),
                        "co_ies_nonempty": completeness.get("CO_IES", {}).get("nonempty"),
                        "co_ies_distinct": distinct.get("CO_IES"),
                    }
                )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs="+", type=Path, help="ZIPs oficiais a auditar")
    parser.add_argument("--json", type=Path, required=True, help="Relatório detalhado em JSON")
    parser.add_argument("--csv", type=Path, required=True, help="Resumo tabular em CSV")
    args = parser.parse_args()

    missing = [str(path) for path in args.archives if not path.is_file()]
    if missing:
        parser.error("Arquivos inexistentes: " + ", ".join(missing))

    audits = [audit_archive(path) for path in sorted(args.archives)]
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(audits, ensure_ascii=False, indent=2), encoding="utf-8")
    write_summary_csv(audits, args.csv)

    for audit in audits:
        print(
            f"{audit['year']}: CRC={'OK' if audit['crc_ok'] else 'FALHA'}; "
            f"MD5={'OK' if audit['all_csv_md5_match'] else 'FALHA'}; "
            f"CSVs={audit['csv_count']}"
        )
    return 0 if all(a["crc_ok"] and a["all_csv_md5_match"] for a in audits) else 1


if __name__ == "__main__":
    raise SystemExit(main())
