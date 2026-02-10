# ClassificadorSismologico - Refatoracao do Fluxo v2

**Vision:** Reescrever o pipeline sismologico de ponta a ponta com arquitetura modular, contratos explicitos de dados e documentacao rastreavel para uso tecnico e academico.  
**For:** Equipe tecnica de sismologia (IPT/IAG) e professores avaliadores do projeto.  
**Solves:** Dificuldade de manutencao e evolucao do fluxo atual devido a acoplamento alto, caminhos fixos e baixa padronizacao entre etapas.

## Documentation Axes

Este projeto adota dois objetivos documentais em paralelo:

1. **Objetivo da refatoracao (trilho de execucao):**
- planejar e executar a reescrita v2 com rastreabilidade por decisao, tarefa e
  validacao.

2. **Objetivo da codebase legado (trilho de compreensao):**
- explicar com precisao o comportamento atual do sistema legado, incluindo
  ordem de execucao, contratos de entrada/saida e dependencias.

## Goals (Refatoracao)

- [ ] Entregar novo fluxo modular com as etapas `ingestao -> preprocessamento -> aquisicao -> inferencia -> posprocessamento -> relatorio`, mantendo equivalencia funcional com baseline em dataset de referencia.
- [ ] Documentar 100% das decisoes e etapas da refatoracao em `.specs/` e `documentação/`, com historico por feature e criterio de validacao por tarefa.
- [ ] Reduzir dependencia de caminho hardcoded para configuracao centralizada em arquivo de configuracao e variaveis de ambiente.

## Goals (Compreensao Do Legado)

- [ ] Mapear fluxo ponta a ponta do legado (`fluxo_sismo.sh` e modulos Python chamados).
- [ ] Manter referencia de contratos por etapa (arquivos CSV, mseed, npy, relatorios).
- [ ] Manter API/artefatos documentados com explicacao funcional e links para source.
- [ ] Registrar limites, fragilidades e riscos tecnicos observados no legado.

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

## Operational Rule

Cada operacao no diario deve indicar contexto explicito:

- `Contexto: refatoracao`
- `Contexto: legado`

Mudancas que misturam os dois contextos devem ser separadas sempre que
possivel, para manter auditabilidade.
