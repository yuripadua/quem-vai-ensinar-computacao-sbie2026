# Metodologia e reprodução passo a passo

## 1. Fontes e unidade de análise

O pipeline combina o Censo Escolar 2025 e o Censo da Educação Superior 1995–2024. A unidade principal é a escola com ao menos uma turma do Ensino Fundamental, identificada por `CO_ENTIDADE`. Ausências permanecem ausências; não há imputação, interpolação ou ajuste para forçar coincidência com o artigo.

## 2. Verificação dos originais

Antes dos cálculos:

1. teste o CRC dos ZIPs;
2. confronte os quatro CSVs escolares usados na integração com os MD5 do INEP;
3. confronte os 30 ZIPs superiores com os manifestos anuais;
4. interrompa a execução diante de arquivo truncado, hash divergente, ano ausente ou cópia divergente.

Os hashes estão em `data/metadata/` e as auditorias em `validation/`.

## 3. Integração do Censo Escolar

`01_integrar_censo_escolar_2025.py`:

1. valida os cabeçalhos e as 226 variáveis do esquema;
2. exige `CO_ENTIDADE` não nulo e único nas quatro fontes;
3. seleciona `QT_TUR_FUND_AI > 0` ou `QT_TUR_FUND_AF > 0`;
4. exige cobertura integral das chaves;
5. realiza junções internas 1:1;
6. preserva a ordem da tabela Escola e grava CSV `;`, Windows-1252 e CRLF;
7. exige 119.244 linhas, 226 colunas e SHA-256 `a8efffc8b72ea0644a0c9db3c069b80ef72829c862f4ab179b4bdcf8a86dd3e1`.

## 4. Sinais escolares

- turma de Informática/Computação: `QT_TUR_BAS_DISC_INFO_COMPUTACAO > 0`;
- docente em Informática/Computação: `QT_DOC_BAS_DISC_INFO_COMPUTACAO > 0`;
- formação continuada em Educação/TIC: `QT_DOC_BAS_ESPEC_EDUC_TIC > 0`.

“Algum sinal docente” é a união lógica dos dois últimos. Esses campos são sinais administrativos, não comprovação de aderência à BNCC Computação.

## 5. Cenários de demanda

Para escola `i`, cenário `s` e capacidade `C`:

```text
D_i^s(C) = max(1, teto(H_i^s / C))
```

| Cenário | Anos iniciais | Anos finais |
|---|---|---|
| Mínimo | 1 por turma | 1 por turma |
| Intermediário | 1 por turma | 2 por turma |
| Progressivo | 1 no 1º–2º; 2 no 3º–5º e multietapa | 2 por turma |
| Intensivo | 1 no 1º–2º; 2 no 3º–5º e multietapa | 3 por turma |

As capacidades são frações exatas: `20/1`, `25/1`, `80/3` e `146/5`. Demandas residuais subtraem no máximo uma posição por escola sinalizada. No híbrido, cada turma dos anos iniciais corresponde a uma posição formativa de regente; especialistas dos anos finais seguem carga e capacidade.

## 6. Recortes e validação

`02_gerar_derivados_censo_escolar_2025.py` produz resultados nacionais, quatro tabelas do artigo, recortes territoriais, cenários por UF e métricas textuais. As 27 UFs e cinco regiões são reconciliadas com o total nacional.

No Censo Superior, os leiautes históricos são tratados ano a ano. `gerar_recortes_artigo_2024.py` recalcula docência em Computação, Pedagogia ampla, Pedagogia estrita e Pedagogia/licenciaturas diretamente do ZIP oficial de 2024.

`03_validar_resultados_artigo.py` executa 120 confrontos e retorna código diferente de zero diante de qualquer diferença.
