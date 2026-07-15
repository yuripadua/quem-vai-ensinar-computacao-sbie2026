# Contexto operacional para filtragem e futura integração dos microdados do Censo Escolar 2025

## 1. Objetivo deste documento

Este arquivo foi escrito para servir como **contexto de trabalho para o Codex** e como **especificação operacional das filtragens** iniciais dos microdados do Censo Escolar 2025.

O objetivo do artigo ao qual estes filtros servem é estimar, em cenários, **quantos professores precisariam ser capacitados para viabilizar minimamente a implementação da BNCC Computação no Ensino Fundamental brasileiro**, articulando escala da demanda, estrutura escolar, força de trabalho docente, infraestrutura disponível e restrições institucionais.

Nesta etapa, a decisão metodológica é simples:

- **manter todas as variáveis classificadas como `provável entrar` ou `dúvida`;**
- **remover todas as variáveis classificadas como `provável não entrar`;**
- fazer isso separadamente nas quatro tabelas principais do projeto:
  - `Tabela_Escola_2025.csv`
  - `Tabela_Docente_2025.csv`
  - `Tabela_Turma_2025.csv`
  - `Tabela_Matricula_2025.csv`

A filtragem ainda é uma etapa de preparação. Ou seja: o objetivo agora não é produzir a base final do artigo, mas sim uma **base reduzida, auditável e muito mais manejável**, preservando o que pode ser útil para análises principais e secundárias.

## 2. Regras gerais para o Codex

### 2.1. Arquivos presentes na raiz do projeto

- `Tabela_Escola_2025.csv`
- `Tabela_Docente_2025.csv`
- `Tabela_Turma_2025.csv`
- `Tabela_Matricula_2025.csv`
- scripts Python de filtragem
- este arquivo `.md`

### 2.2. Objetivo imediato dos scripts

Para cada uma das quatro tabelas, gerar um novo CSV contendo **apenas** as colunas listadas neste documento, preservando:

- o separador `;`
- a codificação de caracteres adequada ao arquivo de origem
- acentuação e nomes de localidades sem corromper caracteres
- a ordem de colunas aqui especificada, quando possível

### 2.3. Objetivo posterior

Após a filtragem, a intenção é **integrar as tabelas em uma base escolar única**, provavelmente ancorada em `CO_ENTIDADE`, também em CSV separado por `;`, para análise posterior.

### 2.4. Observação importante

O Codex deve sempre **validar o cabeçalho real** dos arquivos CSV antes de filtrar ou integrar. Caso alguma coluna listada aqui não exista no arquivo concreto, o comportamento preferível é:

1. avisar claramente quais colunas faltaram;
2. não inferir substituições automaticamente sem confirmação explícita;
3. registrar a divergência, porque o Censo pode mudar nomes e estruturas entre anos.

## 3. Visão geral das quatro tabelas

| Tabela    | Arquivo                     | Papel analítico resumido                                                                                                                                                                                          | Coluna-chave de integração | Campos mantidos nesta etapa |
| --------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | --------------------------: |
| Escola    | `Tabela_Escola_2025.csv`    | capturar o contexto institucional, territorial e infraestrutural da unidade escolar, permitindo diferenciar cenários de implementação da BNCC Computação (mais desplugados, mais plugados ou híbridos).           | `CO_ENTIDADE`              |                          71 |
| Docente   | `Tabela_Docente_2025.csv`   | capturar a força de trabalho potencialmente mobilizável para a implementação, incluindo volume docente, formação, vínculo, idade, formação continuada e presença explícita de docentes de Informática/Computação. | `CO_ENTIDADE`              |                          70 |
| Turma     | `Tabela_Turma_2025.csv`     | capturar a estrutura de oferta do Ensino Fundamental em termos de turmas, simultaneidade potencial, segmentação por ano/série e sinais indiretos da capacidade operacional da escola.                             | `CO_ENTIDADE`              |                          61 |
| Matrícula | `Tabela_Matricula_2025.csv` | capturar o tamanho da demanda educacional atendida pela escola, por etapa e por ano/série, além de variáveis adicionais que podem tensionar cenários de implementação e necessidade de adaptação.                 | `CO_ENTIDADE`              |                          43 |

## 4. Detalhamento por tabela

### 4.1. Escola — `Tabela_Escola_2025.csv`

**Função analítica da tabela:** capturar o contexto institucional, territorial e infraestrutural da unidade escolar, permitindo diferenciar cenários de implementação da BNCC Computação (mais desplugados, mais plugados ou híbridos).

**Nota de integração:** é a tabela-base territorial e institucional. Em princípio, deve ser a âncora do merge via `CO_ENTIDADE`.

**Quantidade de campos mantidos nesta etapa:** 71

- `provável entrar`: 48
- `dúvida`: 23

#### Grupo: identificação temporal — provável entrar (Prioridade alta)

- `NU_ANO_CENSO` — Ano do Censo

#### Grupo: identificador da escola — provável entrar (Prioridade alta)

- `CO_ENTIDADE` — Código da Escola

#### Grupo: perfil institucional — provável entrar (Prioridade alta)

- `TP_DEPENDENCIA` — Dependência Administrativa
- `TP_CATEGORIA_ESCOLA_PRIVADA` — Categoria da escola privada
- `TP_LOCALIZACAO` — Localização
- `TP_LOCALIZACAO_DIFERENCIADA` — Localização diferenciada da escola
- `TP_SITUACAO_FUNCIONAMENTO` — Situação de funcionamento

#### Grupo: território — provável entrar (Prioridade alta)

- `NO_REGIAO` — Nome da Região Geográfica
- `CO_REGIAO` — Código da Região Geográfica
- `NO_UF` — Nome da Unidade da Federação
- `SG_UF` — Sigla da Unidade da Federação
- `CO_UF` — Código da Unidade da Federação
- `NO_MUNICIPIO` — Nome do Município
- `CO_MUNICIPIO` — Código do Município
- `NO_REGIAO_GEOG_INTERM` — Nome da Região Geográfica Intermediária
- `CO_REGIAO_GEOG_INTERM` — Código da Região Geográfica Intermediária
- `NO_REGIAO_GEOG_IMED` — Nome da Região Geográfica Imediata
- `CO_REGIAO_GEOG_IMED` — Código da Região Geográfica Imediata
- `NO_MESORREGIAO` — Nome da Mesorregião
- `CO_MESORREGIAO` — Código da Mesorregião
- `NO_MICRORREGIAO` — Nome da Microrregião
- `CO_MICRORREGIAO` — Código da Microrregião
- `NO_DISTRITO` — Divisão Intramunicipal - Nome do Distrito
- `CO_DISTRITO` — Divisão Intramunicipal - Código do Distrito
- `NO_REGIAO_ADMINISTRATIVA` — Nome da Região Administrativa referente exclusivamente às regiões administrativas do Distrito Federal (DF)
- `CO_REGIAO_ADMINISTRATIVA` — Código da Região Administrativa referente exclusivamente às regiões administrativas do Distrito Federal (DF)
- `CO_ORGAO_REGIONAL` — Código do Órgão Regional de Ensino

#### Grupo: identificação da escola — provável entrar (Prioridade alta)

- `NO_ENTIDADE` — Nome da Escola

#### Grupo: oferta e mediação — provável entrar (Prioridade alta)

- `IN_ESCOLARIZACAO` — Escola possui uma ou mais matrículas de escolarização em alguma das seguintes etapas de ensino: Creche, Pré-Escola, Ensino Fundamental, Ensino Médio, Educação de Jovens e Adultos (EJA), Curso Técnico Concomitante, Curso Técnico Subsequente, Curso FIC Concomitante, Itinerário Formativo Técnico Profissional (IFTP) Exclusivo - Curso Técnico (não articulado ao ensino médio regular) e Itinerário Formativo Técnico Profissional Exclusivo - Qualificação Profissional (não articulado ao ensino médio regular)
- `IN_MEDIACAO_PRESENCIAL` — Mediação didático-pedagógica oferecida pela escola - Presencial
- `IN_MEDIACAO_SEMIPRESENCIAL` — Mediação didático-pedagógica oferecida pela escola - Semipresencial
- `IN_MEDIACAO_EAD` — Mediação didático-pedagógica oferecida pela escola - Educação a Distância - EAD
- `IN_REGULAR` — Ensino Regular - Modo, maneira ou metodologia de ensino correspondente às turmas com etapas de escolarização consecutivas, Creche ao Ensino Médio

#### Grupo: infraestrutura/equipamentos — provável entrar (Prioridade alta)

- `IN_LABORATORIO_INFORMATICA` — Dependências físicas existentes e utilizadas na escola - Laboratório de informática
- `IN_COMPUTADOR` — Equipamentos existentes na escola para uso técnico e administrativo - Computador
- `IN_DESKTOP_ALUNO` — Computadores em uso pelos alunos - Computador de mesa (desktop)
- `QT_DESKTOP_ALUNO` — Quantidade de computadores em uso pelos alunos - Computador de mesa (desktop)
- `IN_COMP_PORTATIL_ALUNO` — Computadores em uso pelos alunos - Computador portátil
- `QT_COMP_PORTATIL_ALUNO` — Quantidade de computadores em uso pelos alunos - Computador portátil
- `IN_TABLET_ALUNO` — Computadores em uso pelos alunos - Tablet
- `QT_TABLET_ALUNO` — Quantidade de computadores em uso pelos alunos - Tablet
- `QT_COMPUTADOR` — Quantidade de computadores na escola
- `IN_INTERNET` — Acesso à Internet
- `IN_INTERNET_ALUNOS` — Acesso à Internet - Para uso dos alunos
- `IN_INTERNET_APRENDIZAGEM` — Acesso à Internet - Para uso nos processos de ensino e aprendizagem
- `IN_ACESSO_INTERNET_COMPUTADOR` — Equipamentos que os alunos usam para acessar a internet da escola - Computadores de mesa, portáteis e tablets da escola (no laboratório de informática, biblioteca, sala de aula etc.)
- `IN_ACES_INTERNET_DISP_PESSOAIS` — Equipamentos que os alunos usam para acessar a internet da escola - Dispositivos pessoais (computadores portáteis, celulares, tablets etc.)
- `IN_BANDA_LARGA` — Internet Banda Larga

#### Grupo: infraestrutura física — dúvida (Prioridade em aberto / manter por enquanto)

- `IN_SALA_PROFESSOR` — Dependências físicas existentes e utilizadas na escola - Sala de professores
- `QT_SALAS_EXISTENTES` — Número de salas de aula existentes na escola
- `QT_SALAS_UTILIZADAS_DENTRO` — Número de salas de aula utilizadas na escola - Dentro do prédio
- `QT_SALAS_UTILIZADAS_FORA` — Número de salas de aula utilizadas na escola - Fora do prédio
- `QT_SALAS_UTILIZADAS` — Número de salas de aula utilizadas na escola (dentro e fora do prédio)
- `QT_SALAS_UTILIZA_CLIMATIZADAS` — Condições das salas de aula utilizadas na escola (dentro e fora do prédio escolar) - Número de salas de aula climatizadas
- `QT_SALAS_UTILIZADAS_ACESSIVEIS` — Condições das salas de aula utilizadas na escola (dentro e fora do prédio escolar) - Número de salas de aula com acessibilidade para pessoas com deficiência ou mobilidade reduzida

#### Grupo: infraestrutura/equipamentos — dúvida (Prioridade em aberto / manter por enquanto)

- `IN_EQUIP_COPIADORA` — Equipamentos existentes na escola para uso técnico e administrativo - Copiadora
- `IN_EQUIP_IMPRESSORA` — Equipamentos existentes na escola para uso técnico e administrativo - Impressora
- `IN_EQUIP_IMPRESSORA_MULT` — Equipamentos existentes na escola para uso técnico e administrativo - Impressora Multifuncional
- `IN_EQUIP_SCANNER` — Equipamentos existentes na escola para uso técnico e administrativo - Scanner
- `IN_EQUIP_NENHUM` — Nenhum dos equipamentos listados para uso técnico e administrativo - Antena parabólica, Computador, Copiadora, Impressora, Impressora Multifuncional ou Scanner
- `IN_EQUIP_LOUSA_DIGITAL` — Equipamentos existentes na escola para o processo ensino e aprendizagem - Lousa digital
- `QT_EQUIP_LOUSA_DIGITAL` — Quantidade de Lousas digitais
- `IN_EQUIP_MULTIMIDIA` — Equipamentos existentes na escola para o processo ensino e aprendizagem - Projetor Multimídia (Datashow)
- `QT_EQUIP_MULTIMIDIA` — Quantidade de Projetores Multimídia (Datashow)

#### Grupo: organização do ensino — dúvida (Prioridade em aberto / manter por enquanto)

- `IN_SERIE_ANO` — Forma de organização do ensino - Série/Ano (séries anuais)
- `IN_PERIODOS_SEMESTRAIS` — Forma de organização do ensino - Períodos semestrais
- `IN_FUNDAMENTAL_CICLOS` — Forma de organização do ensino - Ciclo(s) do Ensino Fundamental
- `IN_GRUPOS_NAO_SERIADOS` — Forma de organização do ensino - Grupos não-seriados com base na idade ou competência (art. 23 LDB)
- `IN_MODULOS` — Forma de organização do ensino - Módulos
- `IN_FORMACAO_ALTERNANCIA` — Forma de organização do ensino - Alternância regular de períodos de estudos (proposta pedagógica de formação por alternância com tempo-escola e tempo-comunidade)

#### Grupo: materiais pedagógicos — dúvida (Prioridade em aberto / manter por enquanto)

- `IN_MATERIAL_PED_MULTIMIDIA` — Instrumentos e materiais socioculturais e/ou pedagógicos em uso na escola para o desenvolvimento de atividades de ensino e aprendizagem - Acervo multimídia

**Leitura metodológica resumida:** nesta tabela, o núcleo é territorial, institucional e de infraestrutura. Os blocos de dúvida foram mantidos porque podem ajudar a estimar limitações físicas, organização pedagógica e grau de flexibilidade operacional da escola.

### 4.2. Docente — `Tabela_Docente_2025.csv`

**Função analítica da tabela:** capturar a força de trabalho potencialmente mobilizável para a implementação, incluindo volume docente, formação, vínculo, idade, formação continuada e presença explícita de docentes de Informática/Computação.

**Nota de integração:** deve ser agregada e integrada no nível da escola via `CO_ENTIDADE`.

**Quantidade de campos mantidos nesta etapa:** 70

- `provável entrar`: 43
- `dúvida`: 27

#### Grupo: identificação temporal — provável entrar (Prioridade alta)

- `NU_ANO_CENSO` — Ano do Censo

#### Grupo: identificador da escola — provável entrar (Prioridade alta)

- `CO_ENTIDADE` — Código da Escola

#### Grupo: docentes por etapa — provável entrar (Prioridade alta)

- `QT_DOC_BAS` — Número de Docentes da Educação Básica

- `QT_DOC_FUND` — Número de Docentes do Ensino Fundamental
- `QT_DOC_FUND_AI` — Número de Docentes do Ensino Fundamental - Anos Iniciais
- `QT_DOC_FUND_AF` — Número de Docentes do Ensino Fundamental - Anos Finais

#### Grupo: docentes por ano/série — provável entrar (Prioridade alta)

- `QT_DOC_FUND_AI_1` — Número de Docentes do Ensino Fundamental - Anos Iniciais - 1º Ano
- `QT_DOC_FUND_AI_2` — Número de Docentes do Ensino Fundamental - Anos Iniciais - 2º Ano
- `QT_DOC_FUND_AI_3` — Número de Docentes do Ensino Fundamental - Anos Iniciais - 3º Ano
- `QT_DOC_FUND_AI_4` — Número de Docentes do Ensino Fundamental - Anos Iniciais - 4º Ano
- `QT_DOC_FUND_AI_5` — Número de Docentes do Ensino Fundamental - Anos Iniciais - 5º Ano
- `QT_DOC_FUND_AF_6` — Número de Docentes do Ensino Fundamental - Anos Finais - 6º Ano
- `QT_DOC_FUND_AF_7` — Número de Docentes do Ensino Fundamental - Anos Finais - 7º Ano
- `QT_DOC_FUND_AF_8` — Número de Docentes do Ensino Fundamental - Anos Finais - 8º Ano
- `QT_DOC_FUND_AF_9` — Número de Docentes do Ensino Fundamental - Anos Finais - 9º Ano

#### Grupo: docentes de computação — provável entrar (Prioridade alta)

- `QT_DOC_BAS_DISC_INFO_COMPUTACAO` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Informática / Computação

#### Grupo: docentes em arranjos especiais do EF — provável entrar (Prioridade alta)

- `QT_DOC_FUND_AI_MULTIETAPA` — Número de Docentes do Ensino Fundamental - Educação Infantil e Ensino Fundamental Multietapa
- `QT_DOC_FUND_AF_MULTI` — Número de Docentes do Ensino Fundamental - Multi
- `QT_DOC_FUND_AF_CORRFLUXO` — Número de Docentes do Ensino Fundamental - Correção de Fluxo

#### Grupo: idade docente — provável entrar (Prioridade alta)

- `QT_DOC_BAS_0_24` — Número de Docentes da Educação Básica - Até 24 anos de idade na data de referência do Censo Escolar (última quarta-feira do mês de maio de 2025)
- `QT_DOC_BAS_25_29` — Número de Docentes da Educação Básica - Entre 25 e 29 anos de idade na data de referência do Censo Escolar (última quarta-feira do mês de maio de 2025)
- `QT_DOC_BAS_30_39` — Número de Docentes da Educação Básica - Entre 30 e 39 anos de idade na data de referência do Censo Escolar (última quarta-feira do mês de maio de 2025)
- `QT_DOC_BAS_40_49` — Número de Docentes da Educação Básica - Entre 40 e 49 anos de idade na data de referência do Censo Escolar (última quarta-feira do mês de maio de 2025)
- `QT_DOC_BAS_50_54` — Número de Docentes da Educação Básica - Entre 50 e 54 anos de idade na data de referência do Censo Escolar (última quarta-feira do mês de maio de 2025)
- `QT_DOC_BAS_55_59` — Número de Docentes da Educação Básica - Entre 55 e 59 anos de idade na data de referência do Censo Escolar (última quarta-feira do mês de maio de 2025)
- `QT_DOC_BAS_60_MAIS` — Número de Docentes da Educação Básica - Com 60 ou mais anos de idade na data de referência do Censo Escolar (última quarta-feira do mês de maio de 2025)

#### Grupo: escolaridade/formação — provável entrar (Prioridade alta)

- `QT_DOC_BAS_ESCO_EF` — Número de Docentes da Educação Básica - Maior nível de Escolaridade concluída - Ensino Fundamental
- `QT_DOC_BAS_ESCO_EM` — Número de Docentes da Educação Básica - Maior nível de Escolaridade concluída - Ensino Médio
- `QT_DOC_BAS_ESCO_SUP_GRAD` — Número de Docentes da Educação Básica - Maior nível de Escolaridade concluída - Educação Superior (Graduação)
- `QT_DOC_BAS_ESCO_SUP_GRAD_LICEN` — Número de Docentes da Educação Básica - Número de Docentes da Educação Básica - Maior nível de Escolaridade concluída - Educação Superior Licenciatura
- `QT_DOC_BAS_ESCO_SUP_GRAD_SLICEN` — Número de Docentes da Educação Básica - Número de Docentes da Educação Básica - Maior nível de Escolaridade concluída - Educação Superior Sem Licenciatura
- `QT_DOC_BAS_ESCO_SUP_POS_ESPEC` — Número de Docentes da Educação Básica - Pós-Graduação concluída - Especialização
- `QT_DOC_BAS_ESCO_SUP_POS_MESTRA` — Número de Docentes da Educação Básica - Pós-Graduação concluída - Mestrado
- `QT_DOC_BAS_ESCO_SUP_POS_DOUTO` — Número de Docentes da Educação Básica - Pós-Graduação concluída - Doutorado
- `QT_DOC_BAS_ESCO_SUP_POS_NENHUM` — Número de Docentes da Educação Básica - Pós-Graduação concluída - Não tem pós-graduação concluída

#### Grupo: vínculo funcional — provável entrar (Prioridade alta)

- `QT_DOC_BAS_VINCULO_CONCUR` — Número de Docentes da Educação Básica - Situação Funcional/Regime de contratação/Tipo de Vínculo (Apenas para docente de escola pública) - Concursado/efetivo/estável
- `QT_DOC_BAS_VINCULO_CONTRA` — Número de Docentes da Educação Básica - Situação Funcional/Regime de contratação/Tipo de Vínculo (Apenas para docente de escola pública) - Contrato temporário
- `QT_DOC_BAS_VINCULO_TERCEIR` — Número de Docentes da Educação Básica - Situação Funcional/Regime de contratação/Tipo de Vínculo (Apenas para docente de escola pública) - Contrato terceirizado
- `QT_DOC_BAS_VINCULO_CLT` — Número de Docentes da Educação Básica - Situação Funcional/Regime de contratação/Tipo de Vínculo (Apenas para docente de escola pública) - Contrato CLT

#### Grupo: formação continuada — provável entrar (Prioridade alta)

- `QT_DOC_BAS_ESPEC_EDUC_TIC` — Número de Docentes da Educação Básica - Outros cursos - Formação Continuada com no mínimo 80 horas - Educação e Tecnologia de Informação e Comunicação (TIC)
- `QT_DOC_BAS_ESPEC_ANOS_INICIAIS` — Número de Docentes da Educação Básica - Outros cursos - Formação Continuada com no mínimo 80 horas - Específico para anos iniciais do ensino fundamental
- `QT_DOC_BAS_ESPEC_ANOS_FINAIS` — Número de Docentes da Educação Básica - Outros cursos - Formação Continuada com no mínimo 80 horas - Específico para anos finais do ensino fundamental
- `QT_DOC_BAS_ESPEC_NENHUM` — Número de Docentes da Educação Básica - Outros cursos - Formação Continuada com no mínimo 80 horas - Nenhum

#### Grupo: docentes por disciplina — dúvida (Prioridade em aberto / manter por enquanto)

- `QT_DOC_BAS_DISC_LINGUA_PORT` — Número de Docentes da Educação Básica - Disciplina que atua - Áreas do conhecimento/Componentes curriculares - Língua/ Literatura Portuguesa
- `QT_DOC_BAS_DISC_EDUC_FISICA` — Número de Docentes da Educação Básica - Disciplina que atua - Áreas do conhecimento/Componentes curriculares - Educação Física
- `QT_DOC_BAS_DISC_ARTES` — Número de Docentes da Educação Básica - Disciplina que atua - Áreas do conhecimento/Componentes curriculares - Artes (Educação Artística, Teatro, Dança, Música, Artes Plásticas e outras)
- `QT_DOC_BAS_DISC_LINGUA_ING` — Número de Docentes da Educação Básica - Disciplina que atua - Áreas do conhecimento/Componentes curriculares - Língua/ Literatura estrangeira - Inglês
- `QT_DOC_BAS_DISC_LINGUA_ESPA` — Número de Docentes da Educação Básica - Disciplina que atua - Áreas do conhecimento/Componentes curriculares - Língua/ Literatura estrangeira - Espanhol
- `QT_DOC_BAS_DISC_LINGUA_FRANC` — Número de Docentes da Educação Básica - Disciplina que atua - Áreas do conhecimento/Componentes curriculares - Língua/ Literatura estrangeira - Francês
- `QT_DOC_BAS_DISC_LINGUA_OUTRA` — Número de Docentes da Educação Básica - Disciplina que atua - Áreas do conhecimento/Componentes curriculares - Língua/ Literatura estrangeira - Outra
- `QT_DOC_BAS_DISC_LIBRAS` — Número de Docentes da Educação Básica - Disciplina que atua - Áreas do conhecimento/Componentes curriculares - Libras
- `QT_DOC_BAS_DISC_LINGUA_INDIG` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Língua Indígena
- `QT_DOC_BAS_DISC_PORT_SEG_LINGUA` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Língua Portuguesa como segunda língua
- `QT_DOC_BAS_DISC_MATEMATICA` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Matemática
- `QT_DOC_BAS_DISC_CIENCIAS` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Ciências
- `QT_DOC_BAS_DISC_FISICA` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Física
- `QT_DOC_BAS_DISC_QUIMICA` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Química
- `QT_DOC_BAS_DISC_BIOLOGIA` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Biologia
- `QT_DOC_BAS_DISC_HISTORIA` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - História
- `QT_DOC_BAS_DISC_GEOGRAFIA` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Geografia
- `QT_DOC_BAS_DISC_SOCIOLOGIA` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Sociologia
- `QT_DOC_BAS_DISC_FILOSOFIA` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Filosofia
- `QT_DOC_BAS_DISC_EST_SOCIAIS` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Estudos Sociais
- `QT_DOC_BAS_DISC_EST_SOCIAIS_SOCI` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Estudos Sociais ou Sociologia
- `QT_DOC_BAS_DISC_ENSINO_RELIGIOSO` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Ensino Religioso
- `QT_DOC_BAS_DISC_PROFISSIONA` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Disciplinas dos cursos técnicos profissionais
- `QT_DOC_BAS_DISC_ESTAGIO_SUPER` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Estágio curricular supervisionado
- `QT_DOC_BAS_DISC_PEDAGOGICAS` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Disciplinas pedagógicas
- `QT_DOC_BAS_DISC_PROJETO_DE_VIDA` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Projeto de vida
- `QT_DOC_BAS_DISC_OUTRAS` — Número de Docentes da Educação Básica - Disciplina que atua - /Componentes curriculares - Outras disciplinas

**Leitura metodológica resumida:** esta é a tabela mais importante para o coração do artigo. Ela combina escala docente, composição etária, formação, vínculo, formação continuada e presença explícita de docentes de Informática/Computação. Os campos por disciplina ficaram como dúvida porque podem ser úteis para modelar quem poderia ser reconvertido para atuar com BNCC Computação.

### 4.3. Turma — `Tabela_Turma_2025.csv`

**Função analítica da tabela:** capturar a estrutura de oferta do Ensino Fundamental em termos de turmas, simultaneidade potencial, segmentação por ano/série e sinais indiretos da capacidade operacional da escola.

**Nota de integração:** deve ser agregada e integrada no nível da escola via `CO_ENTIDADE`.

**Quantidade de campos mantidos nesta etapa:** 61

- `provável entrar`: 19
- `dúvida`: 42

#### Grupo: identificação temporal — provável entrar (Prioridade alta)

- `NU_ANO_CENSO` — Ano do Censo

#### Grupo: identificador da escola — provável entrar (Prioridade alta)

- `CO_ENTIDADE` — Código da Escola

#### Grupo: turmas por etapa — provável entrar (Prioridade alta)

- `QT_TUR_BAS` — Número de Turmas da Educação Básica

- `QT_TUR_FUND` — Número de Turmas do Ensino Fundamental
- `QT_TUR_FUND_AI` — Número de Turmas do Ensino Fundamental - Anos Iniciais
- `QT_TUR_FUND_AF` — Número de Turmas do Ensino Fundamental - Anos Finais

#### Grupo: turmas por ano/série — provável entrar (Prioridade alta)

- `QT_TUR_FUND_AI_1` — Número de Turmas do Ensino Fundamental - Anos Iniciais - 1º Ano
- `QT_TUR_FUND_AI_2` — Número de Turmas do Ensino Fundamental - Anos Iniciais - 2º Ano
- `QT_TUR_FUND_AI_3` — Número de Turmas do Ensino Fundamental - Anos Iniciais - 3º Ano
- `QT_TUR_FUND_AI_4` — Número de Turmas do Ensino Fundamental - Anos Iniciais - 4º Ano
- `QT_TUR_FUND_AI_5` — Número de Turmas do Ensino Fundamental - Anos Iniciais - 5º Ano
- `QT_TUR_FUND_AF_6` — Número de Turmas do Ensino Fundamental - Anos Finais - 6º Ano
- `QT_TUR_FUND_AF_7` — Número de Turmas do Ensino Fundamental - Anos Finais - 7º Ano
- `QT_TUR_FUND_AF_8` — Número de Turmas do Ensino Fundamental - Anos Finais - 8º Ano
- `QT_TUR_FUND_AF_9` — Número de Turmas do Ensino Fundamental - Anos Finais - 9º Ano

#### Grupo: turmas de computação — provável entrar (Prioridade alta)

- `QT_TUR_BAS_DISC_INFO_COMPUTACAO` — Áreas do conhecimento/Componentes curriculares - Informática / Computação

#### Grupo: arranjos especiais de turma — provável entrar (Prioridade alta)

- `QT_TUR_FUND_AI_MULTIETAPA` — Número de Turmas do Ensino Fundamental - Educação Infantil e Ensino Fundamental Multietapa
- `QT_TUR_FUND_AF_MULTI` — Número de Turmas do Ensino Fundamental - Multi
- `QT_TUR_FUND_AF_CORRFLUXO` — Número de Turmas do Ensino Fundamental - Correção de Fluxo

#### Grupo: turno/tempo integral no EF — dúvida (Prioridade em aberto / manter por enquanto)

- `QT_TUR_FUND_D` — Número de Turmas do Ensino Fundamental - Turno Diurno
- `QT_TUR_FUND_DM` — Número de Turmas do Ensino Fundamental - Turno Diurno - Matutino
- `QT_TUR_FUND_DV` — Número de Turmas do Ensino Fundamental - Turno Diurno - Vespertino
- `QT_TUR_FUND_N` — Número de Turmas do Ensino Fundamental - Turno Noturno
- `QT_TUR_FUND_AI_D` — Número de Turmas do Ensino Fundamental - Anos Iniciais - Turno Diurno
- `QT_TUR_FUND_AI_DM` — Número de Turmas do Ensino Fundamental - Anos Iniciais - Turno Diurno - Matutino
- `QT_TUR_FUND_AI_DV` — Número de Turmas do Ensino Fundamental - Anos Iniciais - Turno Diurno - Vespertino
- `QT_TUR_FUND_AI_N` — Número de Turmas do Ensino Fundamental - Anos Iniciais - Turno Noturno
- `QT_TUR_FUND_AF_D` — Número de Turmas do Ensino Fundamental - Anos Finais - Turno Diurno
- `QT_TUR_FUND_AF_DM` — Número de Turmas do Ensino Fundamental - Anos Finais - Turno Diurno - Matutino
- `QT_TUR_FUND_AF_DV` — Número de Turmas do Ensino Fundamental - Anos Finais - Turno Diurno - Vespertino
- `QT_TUR_FUND_AF_N` — Número de Turmas do Ensino Fundamental - Anos Finais - Turno Noturno
- `QT_TUR_FUND_INT` — Número de Turmas do Ensino Fundamental - Tempo Integral
- `QT_TUR_FUND_AI_INT` — Número de Turmas do Ensino Fundamental - Anos Iniciais - Tempo Integral
- `QT_TUR_FUND_AF_INT` — Número de Turmas do Ensino Fundamental - Anos Finais - Tempo Integral

#### Grupo: turmas por disciplina — dúvida (Prioridade em aberto / manter por enquanto)

- `QT_TUR_BAS_DISC_LINGUA_PORT` — Áreas do conhecimento/Componentes curriculares - Língua/ Literatura Portuguesa
- `QT_TUR_BAS_DISC_EDUC_FISICA` — Áreas do conhecimento/Componentes curriculares - Educação Física
- `QT_TUR_BAS_DISC_ARTES` — Áreas do conhecimento/Componentes curriculares - Artes (Educação Artística, Teatro, Dança, Música, Artes Plásticas e outras)
- `QT_TUR_BAS_DISC_LINGUA_ING` — Áreas do conhecimento/Componentes curriculares - Língua/ Literatura estrangeira - Inglês
- `QT_TUR_BAS_DISC_LINGUA_ESPA` — Áreas do conhecimento/Componentes curriculares - Língua/ Literatura estrangeira - Espanhol
- `QT_TUR_BAS_DISC_LINGUA_FRANC` — Áreas do conhecimento/Componentes curriculares - Língua/ Literatura estrangeira - Francês
- `QT_TUR_BAS_DISC_LINGUA_OUTRA` — Áreas do conhecimento/Componentes curriculares - Língua/ Literatura estrangeira - Outra
- `QT_TUR_BAS_DISC_LIBRAS` — Áreas do conhecimento/Componentes curriculares - Libras
- `QT_TUR_BAS_DISC_LINGUA_INDIG` — Áreas do conhecimento/Componentes curriculares - Língua Indígena
- `QT_TUR_BAS_DISC_PORT_SEG_LINGUA` — Áreas do conhecimento/Componentes curriculares - Língua Portuguesa como segunda língua
- `QT_TUR_BAS_DISC_MATEMATICA` — Áreas do conhecimento/Componentes curriculares - Matemática
- `QT_TUR_BAS_DISC_CIENCIAS` — Áreas do conhecimento/Componentes curriculares - Ciências
- `QT_TUR_BAS_DISC_FISICA` — Áreas do conhecimento/Componentes curriculares - Física
- `QT_TUR_BAS_DISC_QUIMICA` — Áreas do conhecimento/Componentes curriculares - Química
- `QT_TUR_BAS_DISC_BIOLOGIA` — Áreas do conhecimento/Componentes curriculares - Biologia
- `QT_TUR_BAS_DISC_HISTORIA` — Áreas do conhecimento/Componentes curriculares - História
- `QT_TUR_BAS_DISC_GEOGRAFIA` — Áreas do conhecimento/Componentes curriculares - Geografia
- `QT_TUR_BAS_DISC_SOCIOLOGIA` — Áreas do conhecimento/Componentes curriculares - Sociologia
- `QT_TUR_BAS_DISC_FILOSOFIA` — Áreas do conhecimento/Componentes curriculares - Filosofia
- `QT_TUR_BAS_DISC_EST_SOCIAIS` — Áreas do conhecimento/Componentes curriculares - Estudos Sociais
- `QT_TUR_BAS_DISC_EST_SOCIAIS_SOCI` — Áreas do conhecimento/Componentes curriculares - Estudos Sociais ou Sociologia
- `QT_TUR_BAS_DISC_ENSINO_RELIGIOSO` — Áreas do conhecimento/Componentes curriculares - Ensino Religioso
- `QT_TUR_BAS_DISC_PROFISSIONA` — Áreas do conhecimento/Componentes curriculares - Disciplinas dos cursos técnicos profissionais
- `QT_TUR_BAS_DISC_ESTAGIO_SUPER` — Áreas do conhecimento/Componentes curriculares - Estágio curricular supervisionado
- `QT_TUR_BAS_DISC_PEDAGOGICAS` — Áreas do conhecimento/Componentes curriculares - Disciplinas pedagógicas
- `QT_TUR_BAS_DISC_PROJETO_DE_VIDA` — Áreas do conhecimento/Componentes curriculares - Projeto de vida
- `QT_TUR_BAS_DISC_OUTRAS` — Áreas do conhecimento/Componentes curriculares - Outras disciplinas

**Leitura metodológica resumida:** esta tabela ajuda a transformar matrículas em necessidade operacional concreta. Os campos de dúvida foram mantidos porque podem sustentar, se necessário, análises sobre simultaneidade, turno, tempo integral e capacidade semanal de oferta.

### 4.4. Matrícula — `Tabela_Matricula_2025.csv`

**Função analítica da tabela:** capturar o tamanho da demanda educacional atendida pela escola, por etapa e por ano/série, além de variáveis adicionais que podem tensionar cenários de implementação e necessidade de adaptação.

**Nota de integração:** deve ser agregada e integrada no nível da escola via `CO_ENTIDADE`.

**Quantidade de campos mantidos nesta etapa:** 43

- `provável entrar`: 15
- `dúvida`: 28

#### Grupo: identificação temporal — provável entrar (Prioridade alta)

- `NU_ANO_CENSO` — Ano do Censo

#### Grupo: identificador da escola — provável entrar (Prioridade alta)

- `CO_ENTIDADE` — Código da Escola

#### Grupo: matrículas por etapa — provável entrar (Prioridade alta)

- `QT_MAT_BAS` — Número de Matrículas da Educação Básica

- `QT_MAT_FUND` — Número de Matrículas do Ensino Fundamental
- `QT_MAT_FUND_AI` — Número de Matrículas do Ensino Fundamental - Anos Iniciais
- `QT_MAT_FUND_AF` — Número de Matrículas do Ensino Fundamental - Anos Finais

#### Grupo: matrículas por ano/série — provável entrar (Prioridade alta)

- `QT_MAT_FUND_AI_1` — Número de Matrículas do Ensino Fundamental - Anos Iniciais - 1º Ano
- `QT_MAT_FUND_AI_2` — Número de Matrículas do Ensino Fundamental - Anos Iniciais - 2º Ano
- `QT_MAT_FUND_AI_3` — Número de Matrículas do Ensino Fundamental - Anos Iniciais - 3º Ano
- `QT_MAT_FUND_AI_4` — Número de Matrículas do Ensino Fundamental - Anos Iniciais - 4º Ano
- `QT_MAT_FUND_AI_5` — Número de Matrículas do Ensino Fundamental - Anos Iniciais - 5º Ano
- `QT_MAT_FUND_AF_6` — Número de Matrículas do Ensino Fundamental - Anos Finais - 6º Ano
- `QT_MAT_FUND_AF_7` — Número de Matrículas do Ensino Fundamental - Anos Finais - 7º Ano
- `QT_MAT_FUND_AF_8` — Número de Matrículas do Ensino Fundamental - Anos Finais - 8º Ano
- `QT_MAT_FUND_AF_9` — Número de Matrículas do Ensino Fundamental - Anos Finais - 9º Ano

#### Grupo: educação especial no EF — dúvida (Prioridade em aberto / manter por enquanto)

- `QT_MAT_ESP_FUND` — Número de Matrículas da Educação Especial - Ensino Fundamental
- `QT_MAT_ESP_FUND_AI` — Número de Matrículas da Educação Especial - Ensino Fundamental - Anos Iniciais
- `QT_MAT_ESP_FUND_AF` — Número de Matrículas da Educação Especial - Ensino Fundamental - Anos Finais
- `QT_MAT_ESP_CC_FUND` — Número de Matrículas da Educação Especial em Classes Comuns - Ensino Fundamental
- `QT_MAT_ESP_CC_FUND_AI` — Número de Matrículas da Educação Especial em Classes Comuns - Ensino Fundamental - Anos Iniciais
- `QT_MAT_ESP_CC_FUND_AF` — Número de Matrículas da Educação Especial em Classes Comuns - Ensino Fundamental - Anos Finais
- `QT_MAT_ESP_CE_FUND` — Número de Matrículas da Educação Especial em Classes Exclusivas - Ensino Fundamental
- `QT_MAT_ESP_CE_FUND_AI` — Número de Matrículas da Educação Especial em Classes Exclusivas - Ensino Fundamental - Anos Iniciais
- `QT_MAT_ESP_CE_FUND_AF` — Número de Matrículas da Educação Especial em Classes Exclusivas - Ensino Fundamental - Anos Finais
- `QT_MAT_BAS_LIBRAS` — Número de Matrículas da Educação Básica - Classe bilíngue de surdos tendo a Libras (Língua Brasileira de Sinais) como língua de instrução, ensino, comunicação e interação e a língua portuguesa escrita como segunda língua

#### Grupo: turno/tempo integral no EF — dúvida (Prioridade em aberto / manter por enquanto)

- `QT_MAT_FUND_D` — Número de Matrículas do Ensino Fundamental - Turno Diurno
- `QT_MAT_FUND_DM` — Número de Matrículas do Ensino Fundamental - Turno Diurno - Matutino
- `QT_MAT_FUND_DV` — Número de Matrículas do Ensino Fundamental - Turno Diurno - Vespertino
- `QT_MAT_FUND_N` — Número de Matrículas do Ensino Fundamental - Turno Noturno
- `QT_MAT_FUND_AI_D` — Número de Matrículas do Ensino Fundamental - Anos Iniciais - Turno Diurno
- `QT_MAT_FUND_AI_DM` — Número de Matrículas do Ensino Fundamental - Anos Iniciais - Turno Diurno - Matutino
- `QT_MAT_FUND_AI_DV` — Número de Matrículas do Ensino Fundamental - Anos Iniciais - Turno Diurno - Vespertino
- `QT_MAT_FUND_AI_N` — Número de Matrículas do Ensino Fundamental - Anos Iniciais - Turno Noturno
- `QT_MAT_FUND_AF_D` — Número de Matrículas do Ensino Fundamental - Anos Finais - Turno Diurno
- `QT_MAT_FUND_AF_DM` — Número de Matrículas do Ensino Fundamental - Anos Finais - Turno Diurno - Matutino
- `QT_MAT_FUND_AF_DV` — Número de Matrículas do Ensino Fundamental - Anos Finais - Turno Diurno - Vespertino
- `QT_MAT_FUND_AF_N` — Número de Matrículas do Ensino Fundamental - Anos Finais - Turno Noturno
- `QT_MAT_FUND_INT` — Número de Matrículas do Ensino Fundamental - Tempo Integral
- `QT_MAT_FUND_AI_INT` — Número de Matrículas do Ensino Fundamental - Anos Iniciais - Tempo Integral
- `QT_MAT_FUND_AF_INT` — Número de Matrículas do Ensino Fundamental - Anos Finais - Tempo Integral

#### Grupo: território/residência — dúvida (Prioridade em aberto / manter por enquanto)

- `QT_MAT_ZR_URB` — Número de Matrículas da Educação Básica - Localização/Zona de residência do Aluno - Urbana
- `QT_MAT_ZR_RUR` — Número de Matrículas da Educação Básica - Localização/Zona de residência do Aluno - Rural
- `QT_MAT_ZR_NA` — Número de Matrículas da Educação Básica - Localização/Zona de residência do Aluno - Não aplicável para alunos residentes no exterior

**Leitura metodológica resumida:** esta tabela mede a demanda discente atendida pela escola. Os campos de dúvida ficaram porque podem ser úteis em cenários específicos, como adaptações para educação especial, turnos diferenciados e tensão entre demanda e capacidade de oferta.

## 5. Resumo operacional das colunas a manter por tabela

Abaixo está um resumo enxuto, pensado para implementação direta dos filtros. O objetivo é permitir que o Codex monte listas de colunas (`keep_columns`) por arquivo.

### Escola

```python
escola_keep_columns = [
    "NU_ANO_CENSO",
    "CO_ENTIDADE",
    "TP_DEPENDENCIA",
    "TP_CATEGORIA_ESCOLA_PRIVADA",
    "TP_LOCALIZACAO",
    "TP_LOCALIZACAO_DIFERENCIADA",
    "TP_SITUACAO_FUNCIONAMENTO",
    "NO_REGIAO",
    "CO_REGIAO",
    "NO_UF",
    "SG_UF",
    "CO_UF",
    "NO_MUNICIPIO",
    "CO_MUNICIPIO",
    "NO_REGIAO_GEOG_INTERM",
    "CO_REGIAO_GEOG_INTERM",
    "NO_REGIAO_GEOG_IMED",
    "CO_REGIAO_GEOG_IMED",
    "NO_MESORREGIAO",
    "CO_MESORREGIAO",
    "NO_MICRORREGIAO",
    "CO_MICRORREGIAO",
    "NO_DISTRITO",
    "CO_DISTRITO",
    "NO_REGIAO_ADMINISTRATIVA",
    "CO_REGIAO_ADMINISTRATIVA",
    "NO_ENTIDADE",
    "CO_ORGAO_REGIONAL",
    "IN_ESCOLARIZACAO",
    "IN_MEDIACAO_PRESENCIAL",
    "IN_MEDIACAO_SEMIPRESENCIAL",
    "IN_MEDIACAO_EAD",
    "IN_REGULAR",
    "IN_LABORATORIO_INFORMATICA",
    "IN_SALA_PROFESSOR",
    "QT_SALAS_EXISTENTES",
    "QT_SALAS_UTILIZADAS_DENTRO",
    "QT_SALAS_UTILIZADAS_FORA",
    "QT_SALAS_UTILIZADAS",
    "QT_SALAS_UTILIZA_CLIMATIZADAS",
    "QT_SALAS_UTILIZADAS_ACESSIVEIS",
    "IN_COMPUTADOR",
    "IN_EQUIP_COPIADORA",
    "IN_EQUIP_IMPRESSORA",
    "IN_EQUIP_IMPRESSORA_MULT",
    "IN_EQUIP_SCANNER",
    "IN_EQUIP_NENHUM",
    "IN_EQUIP_LOUSA_DIGITAL",
    "QT_EQUIP_LOUSA_DIGITAL",
    "IN_EQUIP_MULTIMIDIA",
    "QT_EQUIP_MULTIMIDIA",
    "IN_DESKTOP_ALUNO",
    "QT_DESKTOP_ALUNO",
    "IN_COMP_PORTATIL_ALUNO",
    "QT_COMP_PORTATIL_ALUNO",
    "IN_TABLET_ALUNO",
    "QT_TABLET_ALUNO",
    "QT_COMPUTADOR",
    "IN_INTERNET",
    "IN_INTERNET_ALUNOS",
    "IN_INTERNET_APRENDIZAGEM",
    "IN_ACESSO_INTERNET_COMPUTADOR",
    "IN_ACES_INTERNET_DISP_PESSOAIS",
    "IN_BANDA_LARGA",
    "IN_SERIE_ANO",
    "IN_PERIODOS_SEMESTRAIS",
    "IN_FUNDAMENTAL_CICLOS",
    "IN_GRUPOS_NAO_SERIADOS",
    "IN_MODULOS",
    "IN_FORMACAO_ALTERNANCIA",
    "IN_MATERIAL_PED_MULTIMIDIA",
]
```

### Docente

```python
docente_keep_columns = [
    "NU_ANO_CENSO",
    "CO_ENTIDADE",
    "QT_DOC_BAS",
    "QT_DOC_FUND",
    "QT_DOC_FUND_AI",
    "QT_DOC_FUND_AI_1",
    "QT_DOC_FUND_AI_2",
    "QT_DOC_FUND_AI_3",
    "QT_DOC_FUND_AI_4",
    "QT_DOC_FUND_AI_5",
    "QT_DOC_FUND_AF",
    "QT_DOC_FUND_AF_6",
    "QT_DOC_FUND_AF_7",
    "QT_DOC_FUND_AF_8",
    "QT_DOC_FUND_AF_9",
    "QT_DOC_BAS_DISC_INFO_COMPUTACAO",
    "QT_DOC_FUND_AI_MULTIETAPA",
    "QT_DOC_FUND_AF_MULTI",
    "QT_DOC_FUND_AF_CORRFLUXO",
    "QT_DOC_BAS_0_24",
    "QT_DOC_BAS_25_29",
    "QT_DOC_BAS_30_39",
    "QT_DOC_BAS_40_49",
    "QT_DOC_BAS_50_54",
    "QT_DOC_BAS_55_59",
    "QT_DOC_BAS_60_MAIS",
    "QT_DOC_BAS_ESCO_EF",
    "QT_DOC_BAS_ESCO_EM",
    "QT_DOC_BAS_ESCO_SUP_GRAD",
    "QT_DOC_BAS_ESCO_SUP_GRAD_LICEN",
    "QT_DOC_BAS_ESCO_SUP_GRAD_SLICEN",
    "QT_DOC_BAS_ESCO_SUP_POS_ESPEC",
    "QT_DOC_BAS_ESCO_SUP_POS_MESTRA",
    "QT_DOC_BAS_ESCO_SUP_POS_DOUTO",
    "QT_DOC_BAS_ESCO_SUP_POS_NENHUM",
    "QT_DOC_BAS_VINCULO_CONCUR",
    "QT_DOC_BAS_VINCULO_CONTRA",
    "QT_DOC_BAS_VINCULO_TERCEIR",
    "QT_DOC_BAS_VINCULO_CLT",
    "QT_DOC_BAS_ESPEC_EDUC_TIC",
    "QT_DOC_BAS_ESPEC_ANOS_INICIAIS",
    "QT_DOC_BAS_ESPEC_ANOS_FINAIS",
    "QT_DOC_BAS_ESPEC_NENHUM",
    "QT_DOC_BAS_DISC_LINGUA_PORT",
    "QT_DOC_BAS_DISC_EDUC_FISICA",
    "QT_DOC_BAS_DISC_ARTES",
    "QT_DOC_BAS_DISC_LINGUA_ING",
    "QT_DOC_BAS_DISC_LINGUA_ESPA",
    "QT_DOC_BAS_DISC_LINGUA_FRANC",
    "QT_DOC_BAS_DISC_LINGUA_OUTRA",
    "QT_DOC_BAS_DISC_LIBRAS",
    "QT_DOC_BAS_DISC_LINGUA_INDIG",
    "QT_DOC_BAS_DISC_PORT_SEG_LINGUA",
    "QT_DOC_BAS_DISC_MATEMATICA",
    "QT_DOC_BAS_DISC_CIENCIAS",
    "QT_DOC_BAS_DISC_FISICA",
    "QT_DOC_BAS_DISC_QUIMICA",
    "QT_DOC_BAS_DISC_BIOLOGIA",
    "QT_DOC_BAS_DISC_HISTORIA",
    "QT_DOC_BAS_DISC_GEOGRAFIA",
    "QT_DOC_BAS_DISC_SOCIOLOGIA",
    "QT_DOC_BAS_DISC_FILOSOFIA",
    "QT_DOC_BAS_DISC_EST_SOCIAIS",
    "QT_DOC_BAS_DISC_EST_SOCIAIS_SOCI",
    "QT_DOC_BAS_DISC_ENSINO_RELIGIOSO",
    "QT_DOC_BAS_DISC_PROFISSIONA",
    "QT_DOC_BAS_DISC_ESTAGIO_SUPER",
    "QT_DOC_BAS_DISC_PEDAGOGICAS",
    "QT_DOC_BAS_DISC_PROJETO_DE_VIDA",
    "QT_DOC_BAS_DISC_OUTRAS",
]
```

### Turma

```python
turma_keep_columns = [
    "NU_ANO_CENSO",
    "CO_ENTIDADE",
    "QT_TUR_BAS",
    "QT_TUR_FUND",
    "QT_TUR_FUND_AI",
    "QT_TUR_FUND_AI_1",
    "QT_TUR_FUND_AI_2",
    "QT_TUR_FUND_AI_3",
    "QT_TUR_FUND_AI_4",
    "QT_TUR_FUND_AI_5",
    "QT_TUR_FUND_AF",
    "QT_TUR_FUND_AF_6",
    "QT_TUR_FUND_AF_7",
    "QT_TUR_FUND_AF_8",
    "QT_TUR_FUND_AF_9",
    "QT_TUR_BAS_DISC_INFO_COMPUTACAO",
    "QT_TUR_FUND_AI_MULTIETAPA",
    "QT_TUR_FUND_AF_MULTI",
    "QT_TUR_FUND_AF_CORRFLUXO",
    "QT_TUR_FUND_D",
    "QT_TUR_FUND_DM",
    "QT_TUR_FUND_DV",
    "QT_TUR_FUND_N",
    "QT_TUR_FUND_AI_D",
    "QT_TUR_FUND_AI_DM",
    "QT_TUR_FUND_AI_DV",
    "QT_TUR_FUND_AI_N",
    "QT_TUR_FUND_AF_D",
    "QT_TUR_FUND_AF_DM",
    "QT_TUR_FUND_AF_DV",
    "QT_TUR_FUND_AF_N",
    "QT_TUR_FUND_INT",
    "QT_TUR_FUND_AI_INT",
    "QT_TUR_FUND_AF_INT",
    "QT_TUR_BAS_DISC_LINGUA_PORT",
    "QT_TUR_BAS_DISC_EDUC_FISICA",
    "QT_TUR_BAS_DISC_ARTES",
    "QT_TUR_BAS_DISC_LINGUA_ING",
    "QT_TUR_BAS_DISC_LINGUA_ESPA",
    "QT_TUR_BAS_DISC_LINGUA_FRANC",
    "QT_TUR_BAS_DISC_LINGUA_OUTRA",
    "QT_TUR_BAS_DISC_LIBRAS",
    "QT_TUR_BAS_DISC_LINGUA_INDIG",
    "QT_TUR_BAS_DISC_PORT_SEG_LINGUA",
    "QT_TUR_BAS_DISC_MATEMATICA",
    "QT_TUR_BAS_DISC_CIENCIAS",
    "QT_TUR_BAS_DISC_FISICA",
    "QT_TUR_BAS_DISC_QUIMICA",
    "QT_TUR_BAS_DISC_BIOLOGIA",
    "QT_TUR_BAS_DISC_HISTORIA",
    "QT_TUR_BAS_DISC_GEOGRAFIA",
    "QT_TUR_BAS_DISC_SOCIOLOGIA",
    "QT_TUR_BAS_DISC_FILOSOFIA",
    "QT_TUR_BAS_DISC_EST_SOCIAIS",
    "QT_TUR_BAS_DISC_EST_SOCIAIS_SOCI",
    "QT_TUR_BAS_DISC_ENSINO_RELIGIOSO",
    "QT_TUR_BAS_DISC_PROFISSIONA",
    "QT_TUR_BAS_DISC_ESTAGIO_SUPER",
    "QT_TUR_BAS_DISC_PEDAGOGICAS",
    "QT_TUR_BAS_DISC_PROJETO_DE_VIDA",
    "QT_TUR_BAS_DISC_OUTRAS",
]
```

### Matrícula

```python
matricula_keep_columns = [
    "NU_ANO_CENSO",
    "CO_ENTIDADE",
    "QT_MAT_BAS",
    "QT_MAT_FUND",
    "QT_MAT_FUND_AI",
    "QT_MAT_FUND_AI_1",
    "QT_MAT_FUND_AI_2",
    "QT_MAT_FUND_AI_3",
    "QT_MAT_FUND_AI_4",
    "QT_MAT_FUND_AI_5",
    "QT_MAT_FUND_AF",
    "QT_MAT_FUND_AF_6",
    "QT_MAT_FUND_AF_7",
    "QT_MAT_FUND_AF_8",
    "QT_MAT_FUND_AF_9",
    "QT_MAT_ESP_FUND",
    "QT_MAT_ESP_FUND_AI",
    "QT_MAT_ESP_FUND_AF",
    "QT_MAT_ESP_CC_FUND",
    "QT_MAT_ESP_CC_FUND_AI",
    "QT_MAT_ESP_CC_FUND_AF",
    "QT_MAT_ESP_CE_FUND",
    "QT_MAT_ESP_CE_FUND_AI",
    "QT_MAT_ESP_CE_FUND_AF",
    "QT_MAT_FUND_D",
    "QT_MAT_FUND_DM",
    "QT_MAT_FUND_DV",
    "QT_MAT_FUND_N",
    "QT_MAT_FUND_AI_D",
    "QT_MAT_FUND_AI_DM",
    "QT_MAT_FUND_AI_DV",
    "QT_MAT_FUND_AI_N",
    "QT_MAT_FUND_AF_D",
    "QT_MAT_FUND_AF_DM",
    "QT_MAT_FUND_AF_DV",
    "QT_MAT_FUND_AF_N",
    "QT_MAT_FUND_INT",
    "QT_MAT_FUND_AI_INT",
    "QT_MAT_FUND_AF_INT",
    "QT_MAT_BAS_LIBRAS",
    "QT_MAT_ZR_URB",
    "QT_MAT_ZR_RUR",
    "QT_MAT_ZR_NA",
]
```

## 6. Diretriz para a futura integração das tabelas

A integração posterior ainda será decidida com mais refinamento, mas a orientação atual é esta:

- usar a **Escola** como tabela-âncora, porque ela concentra identificação territorial e perfil institucional;
- integrar **Docente**, **Turma** e **Matrícula** no nível da escola por `CO_ENTIDADE`;
- manter `NU_ANO_CENSO` em todas as tabelas como salvaguarda temporal;
- preservar `;` como separador de saída;
- evitar perda de acentuação em nomes de região, município, distrito e escola;
- validar duplicidade por `CO_ENTIDADE` antes do merge;
- registrar qualquer discrepância de contagem entre tabelas (por exemplo, escola presente em uma tabela e ausente em outra).

## 7. O que este documento **não** está resolvendo ainda

Este documento ajuda a filtrar e preparar as bases, mas ainda **não define** de forma final:

- quais variáveis de dúvida permanecerão no modelo analítico final do artigo;
- como será feita a modelagem exata dos cenários de capacitação docente;
- quais agregações derivadas serão criadas depois da integração;
- se o merge final ficará 100% no nível da escola ou se haverá versões secundárias por região, rede ou porte.

## 8. Síntese final para o Codex

Em termos práticos, o Codex deve entender a tarefa da seguinte maneira:

1. filtrar os quatro CSVs, mantendo somente `provável entrar` + `dúvida`;
2. preservar `;` e caracteres acentuados;
3. validar a existência real das colunas antes de filtrar;
4. gerar quatro CSVs reduzidos;
5. preparar o terreno para um merge posterior por `CO_ENTIDADE`.

Se houver conflito entre este documento e o cabeçalho real dos arquivos CSV, o cabeçalho real deve ser tratado como fonte operacional imediata, mas a divergência precisa ser registrada.

## 9. Histórico de Execução (Log de Ações)

Abaixo está o registro das ações já executadas com base neste planejamento:

1. **Filtragem Individual dos Arquivos CSV:**
   - Foi atualizado e executado um script (`filtrar_microdados_censo_2025.py`) para gerar um novo CSV filtrado para cada arquivo original, seguindo estritamente as colunas listadas neste documento e garantindo que não houvesse perda de dados.
   - Foram gerados arquivos como `Tabela_Escola_2025_filtrado.csv`, `Tabela_Docente_2025_filtrado.csv`, `Tabela_Turma_2025_filtrado.csv` e `Tabela_Matricula_2025_filtrado.csv`.

2. **Integração das Tabelas:**
   - Foi criado e executado o script `integrar_microdados_censo_2025.py`.
   - Realizou-se a integração dos arquivos filtrados em um único arquivo `Tabela_Integrada_Censo_2025.csv`, utilizando `CO_ENTIDADE` como chave de cruzamento.
 
3. **Filtragem por Segmento (EF1 e EF2):**
   - Ocorreu uma filtragem para manter na base de análise apenas as escolas que declararam oferta de Ensino Fundamental Anos Iniciais (EF1) ou Anos Finais (EF2).
   - Escolas que não atendiam a esse critério foram separadas. Foram gerados arquivos segmentados (`..._selecionado.csv` e `..._removido.csv`) correspondentes.

4. **Análise e Limpeza de Colunas Inúteis:**
   - Foi realizada uma análise descritiva no arquivo `Tabela_Integrada_Censo_2025.csv` (que possuía 119.244 escolas integradas) para identificar colunas "inúteis" (onde todas as informações possuem o mesmo valor - 100% homogêneas).
   - Foi criado e executado o script `remover_colunas_inuteis.py` para remover do arquivo integrado essas colunas do grupo 1 (totalmente homogêneas, sendo identificadas e removidas 5 colunas), otimizando a base.

5. **Painel temporal 2009-2025 do recorte de Ensino Fundamental:**
   - Foram criados e executados scripts em `scripts/` para inventariar os microdados anuais, comparar cabeçalhos com a referência de 2025, consultar dicionários de dados e gerar recortes anuais em Parquet.
   - O recorte para 2009-2024 foi definido por presença de matrícula no Ensino Fundamental (`QT_MAT_FUND_AI > 0`, `QT_MAT_FUND_AF > 0` ou `QT_MAT_FUND > 0`), pois os indicadores usados no script de 2025 (`IN_COMUM_FUND_AI`, `IN_COMUM_FUND_AF`, `IN_ESP_EXCLUSIVA_FUND_AI`, `IN_ESP_EXCLUSIVA_FUND_AF`) não existem nos microdados anuais anteriores.
   - Foram gerados `output/tables/recorte_ef_2009.parquet` a `output/tables/recorte_ef_2025.parquet`, o banco `output/db/censo_ef.duckdb` e os consolidados `output/tables/painel_temporal_ef_*.csv` e `output/tables/painel_temporal_ef.xlsx`.
   - A comparação feita nessa etapa usou os CSVs escolares agregados disponíveis localmente (`microdados_ed_basica_<ano>.csv`) e os dicionários desses arquivos. Nessa base agregada local, não foram encontrados equivalentes estritos para `QT_TUR_BAS_DISC_INFO_COMPUTACAO`, `QT_DOC_BAS_DISC_INFO_COMPUTACAO` e `QT_DOC_BAS_ESPEC_EDUC_TIC`. Foram encontrados apenas sinais contextuais de tecnologia/infraestrutura, como laboratório de informática, internet, multimídia e profissionais/monitores de apoio a tecnologias educacionais.
   - Essa constatação não elimina a possibilidade metodológica de reconstruir indicadores históricos de Informática/Computação a partir de microdados granulares de turma, docente/vínculo docente-turma e matrícula. Conforme registrado em `censo_escolar_computacao_series_historicas.md`, a reconstrução deve verificar, por ano e por leiaute, a presença de `IN_DISC_INFORMATICA_COMPUTACAO` ou do código `16 — Informática/Computação`, distinguindo atuação docente, formação superior e formação continuada em Educação e TIC.
   - O relatório detalhado dessa checagem foi salvo em `output/comparisons/schema_and_tech_dictionary_review.md` e `output/comparisons/tech_dictionary_candidates_2009_2024.csv`.

6. **Correção metodológica sobre variáveis históricas de Informática/Computação:**
   - Foi acrescentado o documento `censo_escolar_computacao_series_historicas.md` para consolidar a interpretação metodológica das variáveis de Informática/Computação em série histórica.
   - O entendimento atualizado é que os agregados de 2025 (`QT_TUR_BAS_DISC_INFO_COMPUTACAO`, `QT_DOC_BAS_DISC_INFO_COMPUTACAO` e `QT_DOC_BAS_ESPEC_EDUC_TIC`) não devem ser buscados como equivalentes diretos nos CSVs escolares agregados de 2009-2024.
   - Para anos anteriores a 2025, os indicadores de turmas, docentes e matrículas relacionados a Informática/Computação dependem de reconstrução a partir de arquivos granulares, quando disponíveis, e não dos arquivos escolares agregados usados no painel temporal inicial.
   - Para a escrita do artigo, essa distinção é central: infraestrutura tecnológica escolar pode ser acompanhada nos arquivos agregados; oferta/atuação em Informática/Computação exige validação de microdados granulares; formação continuada em Educação e TIC só deve ser usada nos anos em que houver campo específico validado no leiaute anual.

7. **Painel de infraestrutura tecnológica no recorte de Ensino Fundamental:**
   - Foi criado e executado o script `scripts/05_build_infra_tecnologica_panel.py`, operando sobre os arquivos reduzidos `output/tables/recorte_ef_*.parquet`, sem reprocessar os CSVs brutos anuais.
   - Foram geradas tabelas anuais e segmentadas por UF, dependência administrativa e UF x dependência administrativa em `output/tables/painel_infra_tecnologica_ef_*.csv`, além do workbook `output/tables/painel_infra_tecnologica_ef.xlsx`.
   - Foi gerado o relatório `output/comparisons/infra_tecnologica_ef_review.md` e a auditoria de disponibilidade de colunas `output/comparisons/infra_tecnologica_ef_column_availability.csv`.
   - A leitura metodológica principal é que a série de infraestrutura tecnológica tem duas fases de mensuração: uma série legada de computadores (`QT_COMPUTADOR` e `QT_COMP_ALUNO`), com valores positivos principalmente entre 2009 e 2018, e uma série desagregada de dispositivos de alunos (`QT_DESKTOP_ALUNO`, `QT_COMP_PORTATIL_ALUNO` e `QT_TABLET_ALUNO`), com valores positivos a partir de 2019.
   - Foi identificado que o código `88888`, definido nos dicionários como marcação de valor extremo para variáveis quantitativas, estava sendo somado indevidamente como quantidade real nas colunas `QT_DESKTOP_ALUNO`, `QT_COMP_PORTATIL_ALUNO` e `QT_TABLET_ALUNO`. Esse problema inflava fortemente os indicadores de dispositivos por matrícula em alguns estados.
   - Foi criado e executado o script `scripts/07_corrigir_infra_tecnologica_88888.py`, gerando versões corrigidas com sufixo `_corrigido`, o relatório `output/comparisons/infra_tecnologica_ef_88888_auditoria.md` e as tabelas de auditoria `output/comparisons/infra_tecnologica_ef_88888_anomalias.csv` e `output/comparisons/infra_tecnologica_ef_88888_escolas.csv`.
   - No recorte de Ensino Fundamental, escolas com laboratório de informática caem de 50.480 em 2009 para 40.498 em 2025, com pico em 2012 (73.612 escolas). Na série desagregada corrigida de 2019 a 2025, os dispositivos de alunos somados passam de 1.189.236 para 3.175.342, equivalendo a uma alta de 4,4 para 12,3 dispositivos por 100 matrículas EF.
