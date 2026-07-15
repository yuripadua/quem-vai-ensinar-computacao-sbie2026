#!/usr/bin/env python3
"""Executa o pipeline reproduzível do Censo Superior para o artigo.

O diretório bruto deve conter os 30 ZIPs oficiais, de 1995 a 2024. Cópias com
sufixos como ``(1)`` são aceitas somente quando têm SHA-256 idêntico; cópias
divergentes fazem a execução parar. O pipeline não usa e-MEC, PPCs, Tavily,
planilhas intermediárias nem qualquer imputação.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


YEARS = tuple(range(1995, 2025))
ARCHIVE_RE = re.compile(r"microdados_censo_da_educacao_superior_((?:19|20)\d{2}).*\.zip$", re.I)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def discover_archives(raw_dir: Path) -> tuple[dict[int, Path], dict[int, list[dict[str, str]]]]:
    grouped: dict[int, list[Path]] = {year: [] for year in YEARS}
    for path in raw_dir.rglob("*.zip"):
        match = ARCHIVE_RE.match(path.name)
        if match:
            year = int(match.group(1))
            if year in grouped:
                grouped[year].append(path)

    missing = [year for year, paths in grouped.items() if not paths]
    if missing:
        raise ValueError(f"Faltam ZIPs oficiais para: {missing}")

    selected: dict[int, Path] = {}
    duplicates: dict[int, list[dict[str, str]]] = {}
    for year, paths in grouped.items():
        entries = [{"path": str(path.resolve()), "sha256": sha256(path)} for path in sorted(paths)]
        hashes = {entry["sha256"] for entry in entries}
        if len(hashes) != 1:
            raise ValueError(f"Cópias divergentes para {year}: {entries}")
        # Prefere o nome oficial sem sufixo; o conteúdo já foi confirmado como idêntico.
        selected[year] = min(paths, key=lambda path: ("(" in path.stem, len(path.name), path.name))
        duplicates[year] = entries
    return selected, duplicates


def run(command: list[str]) -> None:
    printable = " ".join(command)
    print(f"\n$ {printable}", flush=True)
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--legacy-computing-report", type=Path)
    parser.add_argument("--legacy-licensure-report", type=Path)
    args = parser.parse_args()

    if bool(args.legacy_computing_report) != bool(args.legacy_licensure_report):
        parser.error("Informe os dois relatórios legados ou nenhum deles")

    scripts = Path(__file__).resolve().parent
    output = args.output_dir.resolve()
    audit_dir = output / "auditoria"
    profile_dir = output / "perfis"
    output.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)
    profile_dir.mkdir(parents=True, exist_ok=True)

    archives, duplicates = discover_archives(args.raw_dir.resolve())
    all_paths = [str(archives[year]) for year in YEARS]
    modern_paths = [str(archives[year]) for year in range(2009, 2025)]
    historical_paths = [str(archives[year]) for year in range(1995, 2009)]

    run(
        [
            sys.executable,
            str(scripts / "audit_censo_superior_archives.py"),
            *all_paths,
            "--json",
            str(audit_dir / "auditoria_censo_superior_1995_2024.json"),
            "--csv",
            str(audit_dir / "auditoria_censo_superior_1995_2024.csv"),
        ]
    )
    run(
        [
            sys.executable,
            str(scripts / "profile_censo_superior_course_recortes.py"),
            *modern_paths,
            "--json",
            str(profile_dir / "perfil_recortes_censo_superior_2009_2024.json"),
            "--csv",
            str(profile_dir / "perfil_recortes_censo_superior_2009_2024.csv"),
        ]
    )
    historical_summary = output / "serie_docencia_computacao_1995_2008.csv"
    run(
        [
            sys.executable,
            str(scripts / "build_censo_superior_historical_1995_2008.py"),
            *historical_paths,
            "--details-csv",
            str(output / "recorte_docencia_computacao_1995_2008_detalhe.csv"),
            "--summary-csv",
            str(historical_summary),
            "--json",
            str(audit_dir / "auditoria_docencia_computacao_1995_2008.json"),
        ]
    )

    build_command = [
        sys.executable,
        str(scripts / "build_censo_superior_article_series.py"),
        "--historical-summary",
        str(historical_summary),
        "--modern-profile",
        str(profile_dir / "perfil_recortes_censo_superior_2009_2024.json"),
        "--series-csv",
        str(output / "serie_docencia_computacao_1995_2024.csv"),
        "--comparison-csv",
        str(output / "comparacao_serie_legada_recalculada_1995_2024.csv"),
        "--validation-json",
        str(audit_dir / "validacao_serie_docencia_computacao_1995_2024.json"),
    ]
    if args.legacy_computing_report:
        build_command.extend(["--legacy-report", str(args.legacy_computing_report.resolve())])
    run(build_command)

    if args.legacy_computing_report:
        run(
            [
                sys.executable,
                str(scripts / "validate_censo_superior_legacy_reports.py"),
                "--profile-json",
                str(profile_dir / "perfil_recortes_censo_superior_2009_2024.json"),
                "--computing-report",
                str(args.legacy_computing_report.resolve()),
                "--licensure-report",
                str(args.legacy_licensure_report.resolve()),
            ]
        )

    manifest = {
        "coverage": list(YEARS),
        "raw_dir": str(args.raw_dir.resolve()),
        "selected_archives": {str(year): str(path.resolve()) for year, path in archives.items()},
        "duplicate_candidates": duplicates,
        "synthetic_or_imputed_values": False,
        "ppc_emec_used": False,
    }
    (audit_dir / "manifesto_execucao.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nPipeline concluído. Saídas: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
