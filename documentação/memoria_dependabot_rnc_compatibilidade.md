# Memoria: Dependabot x Ambiente RNC Legado

Data da verificacao: 2026-02-11

## Contexto

No `origin/main` foram mesclados PRs Dependabot que alteraram `scripts/dev/requirements-rnc-legacy.txt`:
- PR #8: `protobuf 3.20.0 -> 5.29.6`
- PR #9: `tensorflow 2.8.0 -> 2.12.1`
- PR #10: `ipython 7.28.0 -> 8.10.0`
- PR #11: `numpy 1.21.3 -> 1.22.0`

No branch `refactor/fluxo-v2-documentado`, o arquivo ainda permanece com os pins antigos (compatibilidade legada).

## Ambiente legado atual

`setup_pyenv_dual_envs.sh` define:
- Python RNC: `3.7.9`
- Virtualenv RNC: `sismo-rnc-379`

## Diagnostico de impacto

Os bumps do Dependabot quebram a reproducao do ambiente legado por incompatibilidade de versao:

1. `ipython==8.10.0` exige Python >= 3.8.
2. `numpy==1.22.0` exige Python >= 3.8.
3. `tensorflow==2.12.1` nao resolve em Python 3.7.
4. `tensorflow==2.12.1` conflita com `protobuf==5.29.6` (TF 2.12 exige `protobuf < 5`).
5. `tensorflow==2.12.1` conflita com `tensorflow-estimator==2.8.0` (TF 2.12 exige estimator >= 2.12).
6. Mesmo em Python 3.11, `tensorflow-io-gcs-filesystem==0.24.0` nao possui wheel compativel.

## Conclusao operacional

As atualizacoes de seguranca sao validas do ponto de vista de dependencia, mas nao podem ser aplicadas diretamente ao ambiente RNC legado sem estrategia de migracao de stack.

Diretriz: separar trilhas de dependencia (legado x modernizada) antes de aplicar bump automatico no mesmo arquivo.
