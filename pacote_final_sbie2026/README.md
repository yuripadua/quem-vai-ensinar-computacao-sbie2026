# Quem Vai Ensinar Computação?

Artefatos suplementares do artigo **“Quem Vai Ensinar Computação? Dimensionando a Demanda Docente para a BNCC Computação no Brasil”**, de Yuri Souza Padua e Rodolfo Azevedo, aceito no SBIE 2026.

Este pacote contém scripts, bases derivadas, dicionário de variáveis, planilha consolidada e validações. Usa exclusivamente microdados públicos do INEP. **PPCs, e-MEC, buscas na web, PDFs curriculares e o projeto paralelo de coleta de PPCs não fazem parte deste repositório.**

## Resultados centrais reproduzidos

- 119.244 escolas com Ensino Fundamental em 2025;
- 1.173.351 turmas e 25.806.767 matrículas;
- 21.226 escolas (17,8%) com ao menos um dos dois sinais docentes de Computação/TIC;
- demanda intermediária de 139.319 professores capacitados, com capacidade de 25 aulas semanais;
- 771.085 posições formativas no cenário híbrido de duas aulas nos anos finais;
- 925 concluintes em cursos de docência em Computação/Informática em 2024;
- pico de 1.477 concluintes em 2015.

A validação automatizada confronta 120 resultados com o PDF/LaTeX aceito e retorna erro diante de qualquer divergência.

## Conteúdo

| Caminho | Conteúdo |
|---|---|
| `data/processed/` | base escolar integrada compactada, com uma linha por escola |
| `data/derived/censo_escolar_2025/` | tabelas do artigo e recortes por região, UF, dependência e localização |
| `data/derived/censo_superior/` | série de formação docente em Computação (1995–2024) e recortes de 2024 |
| `data/metadata/` | dicionário da base e manifestos das fontes |
| `planilha/` | planilha consolidada com 17 abas |
| `scripts/` | integração, recortes, agregações e validação |
| `validation/` | auditorias, confrontos com o artigo e registros de qualidade |
| `docs/` | metodologia, linhagem, limitações e proveniência |
| `SHA256SUMS.txt` | hashes de todos os arquivos distribuídos |

## Validação rápida

Requer Python 3.11 ou mais recente. Os scripts usam somente a biblioteca-padrão.

```bash
python3 scripts/03_validar_resultados_artigo.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

O resultado esperado é `PASS: 120/120 verificações`.

## Reprodução desde os microdados

1. Baixe os microdados nas páginas oficiais do [Censo Escolar](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar) e do [Censo da Educação Superior](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior).
2. Extraia o Censo Escolar de 2025. Mantenha os 30 ZIPs do Censo Superior, de 1995 a 2024, sem descompactá-los.
3. Execute:

```bash
python3 scripts/run_pipeline.py \
  --raw-escolar-dir raw/microdados_censo_escolar_2025/dados \
  --raw-superior-dir raw/censo_superior
```

Para reproduzir somente o Censo Escolar, omita `--raw-superior-dir`; a série superior auditada distribuída no pacote será preservada. Consulte `docs/METODOLOGIA.md`.

## Observação sobre Pedagogia

O valor de 105.726 concluintes citado no artigo corresponde a um recorte amplo: cursos cujo nome contém `pedagog*` **ou** cujo rótulo CINE identifica formação pedagógica de professor para a Educação Básica. O recorte estrito apenas pelo nome produz 105.502 concluintes. Ambos são publicados; a diferença de 224 não é ocultada nem imputada.

## Dados brutos e privacidade

Os ZIPs originais do INEP não são redistribuídos devido ao volume e à disponibilidade na fonte oficial. O pacote não contém registros individuais de estudantes ou professores. Nenhum valor foi inventado, imputado ou interpolado.

## Citação e licença

Use `CITATION.cff` para citar o artigo e o artefato. O código é MIT; os microdados originais permanecem sujeitos aos termos e metadados do INEP.
