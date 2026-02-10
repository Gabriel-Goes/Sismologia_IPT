# Roadmap

**Current Milestone:** M1 - Base da Refatoracao  
**Status:** In Progress

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

