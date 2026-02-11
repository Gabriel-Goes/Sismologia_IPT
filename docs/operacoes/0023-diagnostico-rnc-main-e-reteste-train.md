# Operacao 0023 - Diagnostico da RNC pos-merge Dependabot e reteste do train.py

**Data:** 2026-02-11  
**Branch:** `refactor/fluxo-v2-documentado`  
**Contexto:** `refatoracao`  
**Status:** `em andamento (incremental)`

## Objetivo

Consolidar o que foi descoberto apos os merges do Dependabot no `main` para
`requirements-rnc-legacy.txt`, verificando:

1. se os novos pins do `main` executam a RNC;
2. por que a RNC ainda aparenta depender do ambiente legado;
3. o comportamento atualizado de `train.py` apos a adicao de
   `.specs/codebase/arquivos/resultados/analisado.csv`.

A adocao de uma trilha de validacao em Python 3.11 decorre da necessidade de
responder aos alertas criticos de seguranca sem interromper imediatamente a
trilha legada. Assim, a estrategia adotada consiste em conduzir uma migracao
controlada, com execucao paralela: manutencao do legado para continuidade
experimental e validacao incremental da trilha modernizada para convergencia
futura.

## Evidencias desta iteracao

1. Compatibilidade dos requirements do `main`:
   - [0023-requirements-main-compat.log](/anexos/anexo-0023-requirements-main-compat-log)
2. Reteste de `train.py` no ambiente legado:
   - [0023-train-legacy-379.log](/anexos/anexo-0023-train-legacy-379-log)
3. Reteste de `train.py` no ambiente moderno de teste:
   - [0023-train-modern-311.log](/anexos/anexo-0023-train-modern-311-log)
4. Checagem de schema de `analisado.csv`:
   - [0023-analisado-schema-check.log](/anexos/anexo-0023-analisado-schema-check-log)

## O que ficou claro nesta iteracao

1. O `requirements-rnc-legacy.txt` atualizado no `main` nao e instalavel como
   esta, nem em Python 3.7 nem em Python 3.11.
2. Os bloqueios sao concretos e reproduziveis:
   - `ipython==8.10.0` nao fecha em Python 3.7;
   - `tensorflow-io-gcs-filesystem==0.24.0` nao fecha em Python 3.11;
   - existe conflito interno em `tensorflow==2.12.1` com
     `protobuf==5.29.6` e `tensorflow-estimator==2.8.0`.
3. `train.py` foi atualizado para aceitar fallback de coluna:
   - `Num_Stations` (esperada originalmente) ou `Num_Estacoes` (schema atual).
4. Foi instalado `scikit-learn==1.0.2` no ambiente legado `sismo-rnc-379`.
5. Apos os ajustes acima, o bloqueio convergiu nos dois ambientes de teste:
   - legado (`sismo-rnc-379`): `FileNotFoundError` de espectro `.npy`;
   - moderno (`rnc-main-main-311`): `FileNotFoundError` de espectro `.npy`.
6. A causa e estrutural no fluxo de treino atual:
   - os espectros `.npy` ainda nao foram gerados/disponibilizados no caminho
     esperado por `train.py`.

## Interpretacao tecnica

Os resultados obtidos indicam que a dependencia atual da RNC em relacao ao
ambiente legado nao se restringe ao modelo em si, mas envolve, sobretudo,
acoplamentos de infraestrutura de dependencias e de contrato de dados. Em
termos praticos, a estabilizacao da trilha modernizada requer:

1. definicao de um conjunto minimo e consistente de dependencias;
2. normalizacao de schema entre etapas do pipeline;
3. garantia de disponibilidade e resolucao correta dos artefatos espectrais
   (``.npy``).

## Proximo incremento desta operacao

Esta operacao sera atualizada com:

1. proposta de `requirements-rnc-modern.txt` minimo e validado;
2. validacao incremental dos scripts `run.py`, `data_process.py`,
   `prediction.py` e `train.py` sob essa trilha modernizada.
