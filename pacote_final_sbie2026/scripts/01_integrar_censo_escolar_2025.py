#!/usr/bin/env python3
"""Reconstrói a base escolar integrada de 2025 a partir dos CSVs oficiais."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
import sys
import tempfile
from pathlib import Path


SOURCES = {
    "escola": ("Tabela_Escola_2025.csv", "cp1252"),
    "docente": ("Tabela_Docente_2025.csv", "utf-8-sig"),
    "turma": ("Tabela_Turma_2025.csv", "utf-8-sig"),
    "matricula": ("Tabela_Matricula_2025.csv", "utf-8-sig"),
}
EXPECTED_MD5 = {
    "escola": "0e4c68d54b18657b0fb4e4fd8f8936d9",
    "docente": "e745bd8a3ae39edf97e28c6030024d16",
    "turma": "88d8e42cff804aef9761ed21d032de1e",
    "matricula": "16ce341a6ab57c8cd07f28064063ca0c",
}
KEY = "CO_ENTIDADE"
EXPECTED_ROWS = 119_244
EXPECTED_COLUMNS = 226
EXPECTED_SHA256 = "a8efffc8b72ea0644a0c9db3c069b80ef72829c862f4ab179b4bdcf8a86dd3e1"


def digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm, usedforsecurity=False)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def locate_one(root: Path, filename: str) -> Path:
    matches = sorted(path for path in root.rglob(filename) if path.is_file())
    if len(matches) != 1:
        raise RuntimeError(f"Esperado exatamente um {filename} sob {root}; encontrados: {matches}")
    return matches[0]


def header(path: Path, encoding: str) -> list[str]:
    with path.open("r", encoding=encoding, newline="") as handle:
        values = next(csv.reader(handle, delimiter=";"), None)
    if not values or len(values) != len(set(values)):
        raise RuntimeError(f"Cabeçalho ausente ou duplicado: {path}")
    return values


def load_table(
    connection: sqlite3.Connection,
    name: str,
    path: Path,
    encoding: str,
    selected: list[str],
) -> dict[str, object]:
    columns = [KEY, *[column for column in selected if column != KEY]]
    definitions = [f'{quote("_ordem")} INTEGER NOT NULL']
    definitions.extend(
        f"{quote(column)} TEXT PRIMARY KEY" if column == KEY else f"{quote(column)} TEXT"
        for column in columns
    )
    connection.execute(f"CREATE TABLE {quote(name)} ({', '.join(definitions)})")
    placeholders = ",".join("?" for _ in range(len(columns) + 1))
    insert = (
        f"INSERT INTO {quote(name)} ({quote('_ordem')},"
        f"{','.join(quote(column) for column in columns)}) VALUES ({placeholders})"
    )
    count = 0
    batch: list[tuple[object, ...]] = []
    with path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        for order, row in enumerate(reader):
            if None in row:
                raise RuntimeError(f"Linha com campos excedentes em {path}, registro {order + 2}")
            key = (row.get(KEY) or "").strip()
            if not key:
                raise RuntimeError(f"Chave {KEY} vazia em {path}, registro {order + 2}")
            batch.append(tuple([order, *[(row.get(column) or "") for column in columns]]))
            if len(batch) == 5000:
                try:
                    connection.executemany(insert, batch)
                except sqlite3.IntegrityError as exc:
                    raise RuntimeError(f"Chave duplicada em {path}: {exc}") from exc
                batch.clear()
            count += 1
    if batch:
        try:
            connection.executemany(insert, batch)
        except sqlite3.IntegrityError as exc:
            raise RuntimeError(f"Chave duplicada em {path}: {exc}") from exc
    connection.commit()
    return {"arquivo": path.name, "linhas": count, "chaves_unicas": count}


def build(args: argparse.Namespace) -> dict[str, object]:
    raw_dir = args.raw_dir.resolve()
    schema = [line.strip() for line in args.schema.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(schema) != EXPECTED_COLUMNS or schema[0] != KEY or len(schema) != len(set(schema)):
        raise RuntimeError(f"Esquema inválido: {len(schema)} colunas; esperado {EXPECTED_COLUMNS}")

    paths: dict[str, Path] = {}
    headers: dict[str, list[str]] = {}
    hashes: dict[str, str] = {}
    for table, (filename, encoding) in SOURCES.items():
        paths[table] = locate_one(raw_dir, filename)
        hashes[table] = digest(paths[table], "md5")
        if hashes[table] != EXPECTED_MD5[table]:
            raise RuntimeError(
                f"MD5 divergente em {filename}: {hashes[table]}; esperado {EXPECTED_MD5[table]}"
            )
        headers[table] = header(paths[table], encoding)

    source_for: dict[str, str] = {KEY: "escola"}
    for column in schema[1:]:
        candidates = [table for table, columns in headers.items() if column in columns]
        if len(candidates) != 1:
            raise RuntimeError(f"Origem ambígua ou ausente para {column}: {candidates}")
        source_for[column] = candidates[0]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    temporary = tempfile.NamedTemporaryFile(
        prefix="integracao_censo_escolar_", suffix=".sqlite", dir=args.output.parent, delete=False
    )
    temporary.close()
    database = Path(temporary.name)
    audit: dict[str, object] = {
        "status": "INICIADO",
        "raw_dir": str(args.raw_dir),
        "schema": str(args.schema),
        "output": str(args.output),
        "sources": {},
    }
    try:
        connection = sqlite3.connect(database)
        connection.execute("PRAGMA journal_mode=OFF")
        connection.execute("PRAGMA synchronous=OFF")
        for table, (_, encoding) in SOURCES.items():
            selected = [column for column in schema if source_for.get(column) == table]
            report = load_table(connection, table, paths[table], encoding, selected)
            report.update({"md5": hashes[table], "md5_esperado": EXPECTED_MD5[table], "md5_confere": True})
            audit["sources"][table] = report

        recorte = (
            "CAST(COALESCE(t.QT_TUR_FUND_AI,'0') AS INTEGER) > 0 OR "
            "CAST(COALESCE(t.QT_TUR_FUND_AF,'0') AS INTEGER) > 0"
        )
        selected_count = connection.execute(f"SELECT COUNT(*) FROM turma t WHERE {recorte}").fetchone()[0]
        coverage = {}
        for table in ("escola", "docente", "matricula"):
            coverage[table] = connection.execute(
                f"SELECT COUNT(*) FROM turma t LEFT JOIN {quote(table)} x "
                f"ON x.{quote(KEY)}=t.{quote(KEY)} WHERE ({recorte}) AND x.{quote(KEY)} IS NULL"
            ).fetchone()[0]
        if any(coverage.values()):
            raise RuntimeError(f"Chaves do recorte sem correspondência: {coverage}")

        aliases = {"escola": "e", "docente": "d", "turma": "t", "matricula": "m"}
        select = ",".join(f"{aliases[source_for[column]]}.{quote(column)}" for column in schema)
        query = f"""
            SELECT {select}
            FROM turma t
            INNER JOIN escola e ON e.{quote(KEY)}=t.{quote(KEY)}
            INNER JOIN docente d ON d.{quote(KEY)}=t.{quote(KEY)}
            INNER JOIN matricula m ON m.{quote(KEY)}=t.{quote(KEY)}
            WHERE {recorte}
            ORDER BY e.{quote('_ordem')}
        """
        written = 0
        with args.output.open("w", encoding="cp1252", newline="") as handle:
            writer = csv.writer(handle, delimiter=";", lineterminator="\r\n")
            writer.writerow(schema)
            for row in connection.execute(query):
                writer.writerow(["" if value is None else value for value in row])
                written += 1
        connection.close()

        output_hash = digest(args.output, "sha256")
        audit["join"] = {
            "relation": "1:1",
            "filter": "QT_TUR_FUND_AI > 0 OR QT_TUR_FUND_AF > 0",
            "selected_keys": selected_count,
            "unmatched_keys": coverage,
            "rows_written": written,
            "columns_written": len(schema),
        }
        audit.update(
            {
                "output_sha256": output_hash,
                "expected_sha256": EXPECTED_SHA256,
                "matches_expected_sha256": output_hash == EXPECTED_SHA256,
            }
        )
        if written != EXPECTED_ROWS or output_hash != EXPECTED_SHA256:
            raise RuntimeError(f"Base reconstruída diverge: {written} linhas; SHA-256 {output_hash}")
        if args.reference_base:
            reference_hash = digest(args.reference_base.resolve(), "sha256")
            audit["reference_comparison"] = {
                "identical": reference_hash == output_hash,
                "detail": f"gerado={output_hash}; referencia={reference_hash}",
            }
            if reference_hash != output_hash:
                raise RuntimeError("Base gerada diverge da referência")
        audit["status"] = "PASS"
        return audit
    finally:
        database.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "config" / "colunas_base_integrada_2025.txt",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--audit",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "validation" / "auditoria_integracao_censo_escolar_2025.json",
    )
    parser.add_argument("--reference-base", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = build(args)
    except Exception as exc:
        args.audit.parent.mkdir(parents=True, exist_ok=True)
        args.audit.write_text(json.dumps({"status": "FAIL", "erro": str(exc)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    args.audit.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {report['join']['rows_written']} escolas; SHA-256 {report['output_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
