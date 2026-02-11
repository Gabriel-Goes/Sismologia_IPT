# Operacao 0024 - Organizacao da fase de testes de execucao

**Data:** 2026-02-11  
**Branch:** `refactor/fluxo-v2-documentado`  
**Contexto:** `refatoracao`  
**Status:** `concluida`  
**Fase:** `execucao-legado`  
**Tag:** `teste-execucao`

## Objetivo

Formalizar a transicao da fase de leitura/compreensao do legado para a fase de
teste de execucao do codigo, mantendo rastreabilidade por operacao e commit.

## Decisao de organizacao

A numeracao das operacoes continua linear (`0001`, `0002`, ...), mas a partir
desta etapa cada operacao passa a explicitar duas marcacoes sinteticas:

1. `Fase`: identifica o macrobloco de trabalho.
2. `Tag`: identifica o tipo da operacao dentro da fase.

## Convencao adotada para as proximas operacoes

1. Operacoes de teste de execucao do legado:
   - `Fase: execucao-legado`
   - `Tag: teste-execucao`
2. Operacoes de estabilizacao de dependencias/ambiente:
   - `Fase: execucao-legado` ou `modernizacao-rnc` (quando aplicavel)
   - `Tag: hardening-ambiente`
3. Operacoes de implementacao da refatoracao v2:
   - `Fase: implementacao-v2`
   - `Tag: refactor-codigo`

## Diretriz para os testes imediatos

Como o acervo local de formas de onda ja existe, os testes desta fase devem
priorizar fluxo sem aquisicao (`-e`), validando primeiro:

1. `-pr` (predicao)
2. `-po` (pos-processamento)
3. `-m` (mapas)
4. `-r` (relatorio)

Somente depois disso sera executada a validacao no IAG da etapa de aquisicao
(`-e`) via `seisarc`.

## Resultado desta operacao

1. Estrutura de classificacao das operacoes definida.
2. Fronteira clara entre fase de compreensao e fase de execucao estabelecida.
3. Proximo passo de teste pratico sem `-e` pronto para execucao e registro.
