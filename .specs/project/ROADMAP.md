# Roadmap

**Current Milestone:** M1 - Base da Refatoracao  
**Status:** In Progress

**Dual Track:** Este roadmap considera dois trilhos continuos:
- trilho de refatoracao (execucao v2);
- trilho de compreensao do legado (mapeamento e documentacao comportamental).

---

## M1 - Base da Refatoracao

**Goal:** Estabelecer baseline tecnico confiavel e contratos de dados para orientar a reescrita.  
**Target:** Documentacao de baseline completa + plano aprovado.

### Features

**Mapeamento Brownfield** - COMPLETE

- Levantar stack, arquitetura, convencoes, estrutura, testes e integracoes em `.specs/codebase/`.

**Inicializacao de Projeto Spec-Driven** - COMPLETE

- Definir visao, escopo, objetivos e restricoes em `.specs/project/PROJECT.md`.
- Definir memoria de execucao em `.specs/project/STATE.md`.

**Plano de Refatoracao por Frentes** - IN PROGRESS

- Dividir reescrita em frentes pequenas (pipeline core, configuracao, validacao, relatorio).

**Arquitetura De Documentacao Em Dois Trilhos** - IN PROGRESS

- Separar explicitamente o que e objetivo da refatoracao vs objetivo do legado.
- Garantir navegacao continua no Sphinx para ambos os trilhos.
- Aplicar regra de contexto em operacoes (`refatoracao`/`legado`).

---

## M2 - Reescrita do Pipeline Core

**Goal:** Reescrever o fluxo principal com contratos explicitos e baixo acoplamento.

### Features

**Refatorar Orquestracao do Fluxo** - PLANNED

- Redesenhar orquestrador principal.
- Separar responsabilidades por modulo.
- Padronizar parametros de execucao.

**Refatorar Contratos de Dados Intermediarios** - PLANNED

- Definir schemas de CSV por etapa.
- Validar consistencia de colunas e tipos.

**Refatorar Integracoes FDSN com Fallback Claros** - PLANNED

- Encapsular clientes e politicas de fallback.
- Melhorar rastreabilidade de falhas.

**Documentar Fluxo Legado Em Detalhe Operacional** - PLANNED

- Explicitar sequencia de execucao do `fluxo_sismo.sh`.
- Relacionar modulos chamados, dependencias e artefatos por etapa.
- Consolidar contratos de dados do legado para comparacao com v2.

---

## M3 - Validacao, Relatorio e Entrega

**Goal:** Garantir equivalencia funcional, documentacao completa e handoff academico.

### Features

**Validacao de Equivalencia com Baseline** - PLANNED

- Comparar saidas principais entre fluxo atual e fluxo v2.
- Reportar desvios e aceitacao.

**Documentacao Final de Refatoracao** - PLANNED

- Consolidar diario tecnico em `documentação/`.
- Consolidar decisoes e justificativas.

**Pacote de Entrega para Avaliacao** - PLANNED

- Organizar evidencias de testes.
- Organizar roteiro de reproducao.

---

## Future Considerations

- Automatizar validacoes em CI.
- Evoluir estrategia de testes para modulos de aquisicao e inferencia.
- Planejar evolucao futura de GUI/QGIS apos estabilizacao do pipeline.
