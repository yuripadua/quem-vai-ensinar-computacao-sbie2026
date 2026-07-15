# Linhagem dos dados

```text
ZIP oficial do Censo Escolar 2025
  └─ Escola + Docente + Turma + Matrícula
       └─ MD5, chave única e junção 1:1 por CO_ENTIDADE
            └─ filtro de escolas com Ensino Fundamental
                 └─ Tabela_Integrada_Censo_2025.csv (119.244 × 226)
                      ├─ tabelas nacionais do artigo
                      ├─ região, UF, dependência e localização
                      ├─ cenários especialista
                      └─ cenários híbridos

ZIPs oficiais do Censo Superior 1995–2024
  ├─ layouts históricos 1995–2008
  └─ cadastro dimensional 2009–2024
       └─ regras nominais, de grau e CINE
            └─ série anual e recortes de formação inicial
```

## Cardinalidade escolar

| Fonte | Linhas oficiais | Relação no recorte |
|---|---:|---|
| Escola | 214.192 | 1:1 |
| Docente | 178.772 | 1:1 |
| Turma | 178.772 | 1:1 |
| Matrícula | 178.766 | 1:1 |
| Base integrada | 119.244 | chave única |

As 226 variáveis provêm de Escola (57), Docente (68), Turma (59), Matrícula (41) e da chave comum. O detalhamento está em `data/metadata/dicionario_base_integrada_2025.csv`.
