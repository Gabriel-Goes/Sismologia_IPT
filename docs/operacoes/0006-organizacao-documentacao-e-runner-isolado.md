# Operacao 0006 - Organizacao da documentacao e runner isolado

**Data:** 2026-02-10  
**Branch:** `refactor/fluxo-v2-documentado`

## Objetivo

Consolidar a documentacao da iteracao v2 na raiz do repositorio e reduzir
ruido operacional durante testes do baseline legado, preservando a rastreabilidade
por commit.

## Commits vinculados

1. `7af9b70` - `docs(repo): mover documentação v2 para a raiz`
2. `9e8cf72` - `chore(dev): adicionar runner isolado do fluxo_sismo`
3. `d5eac5b` - `docs(article): adicionar outline inicial do paper`

## Escopo executado

1. Movimentacao da documentacao da iteracao atual:
   - de `.specs/codebase/documentação/`
   - para `documentação/`

2. Inclusao de runner de desenvolvimento em `scripts/dev/run_fluxo_isolated.sh`:
   - executa `.specs/codebase/fluxo_sismo.sh` em worktree temporaria;
   - evita sujar a worktree principal com logs e artefatos gerados;
   - permite manter o repositorio limpo entre operacoes documentais.

3. Inclusao de diretrizes para o artigo em:
   - `documentação/Possible_Paper_OutLine.md`

## Motivacao tecnica

Durante a leitura e reproducao do fluxo legado, a execucao do shell pipeline
gera alteracoes em arquivos versionados (logs, relatorios e arquivos auxiliares).
Isso atrapalha a separacao por operacao e aumenta risco de commit acidental de
artefatos.

O runner isolado resolve esse problema sem alterar a logica cientifica do fluxo:
os testes seguem executaveis, mas em um espaco descartavel.

## Impacto no projeto

- melhora da higiene do repositório para ciclos de analise/refatoracao;
- documentacao da branch v2 separada do baseline legado;
- diretriz inicial consolidada para redacao do paper.

## Fora de escopo

- nao houve mudanca na logica de classificacao sismica;
- nao houve alteracao de algoritmos de aquisicao, inferencia ou pos-processamento.
