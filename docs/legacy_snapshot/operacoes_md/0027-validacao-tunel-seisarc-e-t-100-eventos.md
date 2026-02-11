# Operacao 0027 - Validacao de aquisicao via tunel (SEISARC) com `-e -t` (100 eventos)

## Contexto

No ambiente atual, o endpoint principal do IAG (`10.110.1.132:18003`) nao estava
acessivel diretamente a partir do GeoServer. Foi validado um tunel SSH reverso
SEISAPP -> GeoServer expondo o servico FDSN em `http://127.0.0.1:18080`.

## Ajustes aplicados

1. Inclusao do endpoint de tunel na prioridade de fallback em
   `fonte/nucleo/fluxo_eventos.py`:
   - `http://127.0.0.1:18080` (`GeoServer tunnel -> seisarc (backup 0)`).
2. Padrao do modo teste alinhado para 100 eventos:
   - `TEST_EVENT_LIMIT` default em `fluxo_eventos.py` e `fluxo_sismo.sh`.

## Execucao de validacao

Comando executado:

```bash
PATH="$HOME/.pyenv/shims:$PATH" \
PYENV_VERSION=sismo-core-311 \
TEST_EVENT_LIMIT=100 \
bash fluxo_sismo.sh catalogo_jul.csv -e -t
```

## Resultado

- Execucao concluida com sucesso (`exit code 0`).
- Endpoint principal indisponivel, mas tunel `127.0.0.1:18080` conectado com os
  servicos `event`, `dataselect` e `station`.
- Arquivos de saida gerados:
  - `arquivos/eventos/eventos.csv` (101 linhas)
  - `arquivos/eventos/erros.csv` (2368 linhas)
  - `arquivos/registros/Sismo_Pipeline.log`

## Decisao operacional

Enquanto o acesso direto ao endpoint principal nao estiver disponivel no host de
execucao, o tunel reverso deve permanecer como fallback operacional do passo `-e`.
