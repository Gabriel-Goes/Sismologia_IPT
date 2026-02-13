# Feature Spec: 01-catalogo-selecao

## Problem
Precisamos consolidar as etapas 1 e 2 em um unico processo que:
1) leia catalogo de origem (QuakeML/builder),
2) selecione eventos da regiao alvo,
3) quebre os eventos em arquivos por evento para alimentar a etapa 3.

## Goal
Gerar um conjunto de eventos selecionados, cada um com arquivo parametrico
(`xml|json`) pronto para extensao posterior.

## Inputs
- Catalogo bruto de origem (`.xml` QuakeML ou texto do builder FDSN).
- Criterios de filtro:
  - regiao alvo (MG),
  - magnitude maxima,
  - profundidade maxima.

## Outputs
- Lista/indice de eventos selecionados.
- Arquivo por evento:
  - `data/events/<event_id>/event.xml` (quando houver QuakeML),
  - `data/events/<event_id>/event.json` (estrutura operacional).

## Requirements
1. Etapas 1 e 2 devem estar no mesmo notebook/script.
2. Regras de filtro devem ser explicitas e reproduziveis.
3. `event.json` deve conter campos minimos de origem:
   - event_id, origin_time, latitude, longitude, depth_km, magnitude.
4. Processo deve registrar contagem antes/depois do filtro.

## Acceptance Criteria
1. Execucao em lote de teste gera arquivos por evento sem ambiguidade.
2. Um orientador consegue abrir notebook e entender os filtros aplicados.
3. Saida serve diretamente como entrada da etapa 3.
