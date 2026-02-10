# ClassificadorSismologico - Refatoracao do Fluxo v2

**Vision:** Reescrever o pipeline sismologico de ponta a ponta com arquitetura modular, contratos explicitos de dados e documentacao rastreavel para uso tecnico e academico.  
**For:** Equipe tecnica de sismologia (IPT/IAG) e professores avaliadores do projeto.  
**Solves:** Dificuldade de manutencao e evolucao do fluxo atual devido a acoplamento alto, caminhos fixos e baixa padronizacao entre etapas.

## Goals

- [ ] Entregar novo fluxo modular com as etapas `ingestao -> preprocessamento -> aquisicao -> inferencia -> posprocessamento -> relatorio`, mantendo equivalencia funcional com baseline em dataset de referencia.
- [ ] Documentar 100% das decisoes e etapas da refatoracao em `.specs/` e `documentação/`, com historico por feature e criterio de validacao por tarefa.
- [ ] Reduzir dependencia de caminho hardcoded para configuracao centralizada em arquivo de configuracao e variaveis de ambiente.

## Tech Stack

**Core:**

- Framework: Pipeline por scripts Python + orquestracao Bash
- Language: Python (3.11 como alvo principal, legado 3.7 em contexto de modelo antigo)
- Data format: CSV, MiniSEED, NPY
- GIS/GUI: QGIS plugin + PyQt

**Key dependencies:**

- `obspy`
- `tensorflow`
- `pandas`
- `geopandas`
- `matplotlib`

## Scope

**v1 includes:**

- Mapeamento tecnico completo do estado atual (brownfield).
- Reescrita do pipeline principal com separacao por modulos e contratos.
- Definicao de interfaces de entrada/saida por etapa (schema de CSV e estrutura de diretorios).
- Validacao de equivalencia de resultados com conjunto de dados de referencia.
- Documentacao tecnica e academica de cada etapa.

**Explicitly out of scope:**

- Re-treinamento de novos modelos de rede neural nesta fase.
- Mudanca de objetivo cientifico (classificacao natural vs antropogenico).
- Redesign visual profundo do plugin QGIS alem do necessario para compatibilidade.

## Constraints

- Timeline: Refatoracao incremental, priorizando entregas pequenas e verificaveis.
- Technical: Preservar resultados cientificos e formatos minimos esperados pelo fluxo atual.
- Resources: Projeto mantido por equipe reduzida; foco em simplicidade e rastreabilidade.

