#!/usr/bin/env python3
"""Executa a reconstrução e a validação dos dados tabulares do artigo."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(command: list[str]) -> None:
    print("$ " + " ".join(command))
    subprocess.run(command, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-escolar-dir", type=Path, required=True)
    parser.add_argument("--raw-superior-dir", type=Path)
    parser.add_argument("--work-dir", type=Path, default=Path("build"))
    parser.add_argument("--reference-base", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    package = Path(__file__).resolve().parents[1]
    scripts = package / "scripts"
    args.work_dir.mkdir(parents=True, exist_ok=True)
    integrated = args.work_dir / "Tabela_Integrada_Censo_2025.csv"
    command = [
        sys.executable,
        str(scripts / "01_integrar_censo_escolar_2025.py"),
        "--raw-dir",
        str(args.raw_escolar_dir.resolve()),
        "--output",
        str(integrated.resolve()),
        "--audit",
        str(package / "validation" / "auditoria_integracao_censo_escolar_2025.json"),
    ]
    if args.reference_base:
        command.extend(["--reference-base", str(args.reference_base.resolve())])
    run(command)
    run(
        [
            sys.executable,
            str(scripts / "02_gerar_derivados_censo_escolar_2025.py"),
            "--input",
            str(integrated.resolve()),
            "--output-dir",
            str(package / "data" / "derived" / "censo_escolar_2025"),
            "--audit",
            str(package / "validation" / "auditoria_derivados_censo_escolar_2025.json"),
        ]
    )
    run([sys.executable, str(scripts / "04_gerar_dicionario_base_integrada.py")])
    if args.raw_superior_dir:
        run(
            [
                sys.executable,
                str(scripts / "censo_superior" / "run_censo_superior_article_pipeline.py"),
                "--raw-dir",
                str(args.raw_superior_dir.resolve()),
                "--output-dir",
                str((package / "data" / "derived" / "censo_superior").resolve()),
            ]
        )
    else:
        print("AVISO: os derivados auditados do Censo Superior distribuídos no pacote foram mantidos.")
    run([sys.executable, str(scripts / "03_validar_resultados_artigo.py"), "--package", str(package)])
    print("Pipeline concluído sem divergências.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
