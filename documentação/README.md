# Documentacao

Este diretorio complementa a estrategia de dois trilhos:

1. **Legado:** o que o sistema atual faz e como executa.
2. **Refatoracao:** como vamos reescrever e validar o v2.

## Trilho Legado

- `documentação/estado_atual_sistema.md`: snapshot tecnico inicial do legado
  (baseline historico da fase de leitura inicial).
- `documentação/inventario_arquivos.md`: inventario de arquivos lidos no
  levantamento inicial.

## Trilho Refatoracao

- `documentação/guia_skill_tlc_spec_driven.md`: processo operacional para
  conduzir planejamento e execucao em modo spec-driven.
- `documentação/Possible_Paper_OutLine.md`: direcao tecnica/cientifica para
  narrativa academica e justificativas do trabalho.
- `documentação/memoria_ambiente_pyenv_virtualenv.md`: memoria operacional do
  setup de ambiente com `pyenv` + `pyenv-virtualenv` (core + RNC).

## Fontes Canonicas Por Trilha

- **Legado:** `.specs/codebase/*` + `docs/sphinx/source/guia|api|artefatos`
- **Refatoracao:** `.specs/project/*` + `docs/operacoes/*`

## Observacao

Os arquivos `estado_atual_sistema.md` e `inventario_arquivos.md` permanecem
como registro historico da primeira etapa de entendimento do legado.
