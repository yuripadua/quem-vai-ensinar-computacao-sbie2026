# Proveniência e obtenção das fontes

## Censo Escolar 2025

- página oficial: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar
- SHA-256 do ZIP usado: `4dd0c065492ec379c217457188932742748f3734c24d6ca27a2aea44aa010a5a`
- SHA-256 da base integrada: `a8efffc8b72ea0644a0c9db3c069b80ef72829c862f4ab179b4bdcf8a86dd3e1`
- Caderno de Conceitos: https://download.inep.gov.br/publicacoes/institucionais/estatisticas_e_indicadores/cadernos_de_conceitos_2025.pdf

Os MD5 dos seis CSVs constam em `data/metadata/manifesto_fontes_censo_escolar_2025.csv`.

## Censo Superior 1995–2024

- página oficial: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior
- cobertura: 30 arquivos anuais, 1995–2024.

Os SHA-256 anuais e os testes de integridade estão em `data/metadata/manifesto_fontes_censo_superior_1995_2024.csv` e `validation/auditoria_censo_superior_1995_2024.csv`.

## Estrutura esperada

```text
raw/
├── microdados_censo_escolar_2025/dados/
│   ├── Tabela_Escola_2025.csv
│   ├── Tabela_Docente_2025.csv
│   ├── Tabela_Turma_2025.csv
│   └── Tabela_Matricula_2025.csv
└── censo_superior/
    ├── microdados_censo_da_educacao_superior_1995.zip
    ├── ...
    └── microdados_censo_da_educacao_superior_2024.zip
```
