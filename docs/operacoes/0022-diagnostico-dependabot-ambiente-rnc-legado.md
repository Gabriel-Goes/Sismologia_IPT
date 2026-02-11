# Operacao 0022 - Diagnostico do Dependabot no ambiente RNC legado

**Data:** 2026-02-11  
**Branch:** `refactor/fluxo-v2-documentado`  
**Contexto:** `refatoracao`  
**Status:** `concluida`

## Objetivo

Avaliar o impacto dos bumps de dependencias mesclados no `main` sobre o
ambiente legado RNC (`sismo-rnc-379`, Python 3.7.9) e definir a acao tecnica
para preservar a reproducibilidade do fluxo legado.

A presente etapa foi motivada pela identificacao de alertas criticos de
seguranca emitidos pelo Dependabot no conjunto de dependencias da trilha RNC.
Nesse contexto, tornou-se necessario avaliar, de forma sistematica, os efeitos
das atualizacoes propostas sobre a reprodutibilidade do ambiente legado
(`sismo-rnc-379`, Python 3.7.9), de modo a equilibrar requisitos de seguranca
e continuidade operacional.

## Escopo da verificacao

1. Comparacao entre `origin/main` e `origin/refactor/fluxo-v2-documentado` no
   arquivo `scripts/dev/requirements-rnc-legacy.txt`.
2. Validacao de resolucao de dependencias com `pip --dry-run` em:
   - ambiente legado (`PYENV_VERSION=sismo-rnc-379`, Python 3.7.9);
   - ambiente Python 3.11 para isolar conflitos entre pacotes.

## Diagnostico

Bumps identificados no `main`:

1. `ipython 7.28.0 -> 8.10.0`
2. `numpy 1.21.3 -> 1.22.0`
3. `tensorflow 2.8.0 -> 2.12.1`
4. `protobuf 3.20.0 -> 5.29.6`

Incompatibilidades confirmadas:

1. `ipython==8.10.0` requer Python >= 3.8.
2. `numpy==1.22.0` requer Python >= 3.8.
3. `tensorflow==2.12.1` nao fecha no Python 3.7.
4. `tensorflow==2.12.1` conflita com `protobuf==5.29.6`
   (`tensorflow 2.12` exige `protobuf < 5`).
5. `tensorflow==2.12.1` conflita com `tensorflow-estimator==2.8.0`
   (`tensorflow 2.12` exige `tensorflow-estimator >= 2.12,<2.13`).
6. Mesmo em Python 3.11, `tensorflow-io-gcs-filesystem==0.24.0` nao possui
   distribuicao compativel.

## Acao tomada com base no diagnostico

1. Mantido `scripts/dev/requirements-rnc-legacy.txt` da branch de refatoracao
   com pins legados para nao quebrar o ambiente `sismo-rnc-379`.
2. Registrada memoria tecnica consolidada em:
   - `documentação/memoria_dependabot_rnc_compatibilidade.md`
3. Definida diretriz operacional:
   - separar trilhas de dependencia (`legado` x `modernizada`) antes de aceitar
     bumps automaticos no mesmo arquivo de requirements.

## Resultado

1. Reprodutibilidade do fluxo legado RNC preservada na branch de refatoracao.
2. Risco de quebra por merges automaticos documentado e rastreavel.
3. Base tecnica pronta para migracao controlada de stack em operacao futura.

## Proximo passo

Planejar operacao de separacao de requirements (legado x modernizado), com
politica explicita para Dependabot por trilha.
