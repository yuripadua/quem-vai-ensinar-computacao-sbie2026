from __future__ import annotations

import csv
import hashlib
import json
import unittest
import zipfile
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
EXPECTED_BASE_SHA256 = "a8efffc8b72ea0644a0c9db3c069b80ef72829c862f4ab179b4bdcf8a86dd3e1"


class ArtifactTests(unittest.TestCase):
    def test_article_validation_passes(self) -> None:
        report = json.loads((PACKAGE / "validation" / "validacao_artigo_aceito.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["checks"], 120)
        self.assertEqual(report["failed"], 0)

    def test_integrated_schema_has_226_unique_columns(self) -> None:
        columns = [line.strip() for line in (PACKAGE / "config" / "colunas_base_integrada_2025.txt").read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(len(columns), 226)
        self.assertEqual(len(columns), len(set(columns)))

    def test_dictionary_covers_schema(self) -> None:
        schema = [line.strip() for line in (PACKAGE / "config" / "colunas_base_integrada_2025.txt").read_text(encoding="utf-8").splitlines() if line.strip()]
        with (PACKAGE / "data" / "metadata" / "dicionario_base_integrada_2025.csv").open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([row["variavel"] for row in rows], schema)
        self.assertTrue(all(row["descricao"].strip() for row in rows))

    def test_integrated_base_hash(self) -> None:
        archive = PACKAGE / "data" / "processed" / "Tabela_Integrada_Censo_2025.csv.zip"
        with zipfile.ZipFile(archive) as zf:
            data = zf.read("Tabela_Integrada_Censo_2025.csv")
        self.assertEqual(hashlib.sha256(data).hexdigest(), EXPECTED_BASE_SHA256)

    def test_no_ppc_or_emec_artifacts(self) -> None:
        forbidden = ("ppc", "emec", "tavily", "gemini")
        names = [path.name.lower() for path in PACKAGE.rglob("*") if path.is_file()]
        self.assertFalse([name for name in names if any(token in name for token in forbidden)])


if __name__ == "__main__":
    unittest.main()
