# Operacao 0011 - Preenchimento dos docs de metodos da API

**Data:** 2026-02-10  
**Branch:** `main`

## Objetivo

Preencher as paginas de API que estavam com conteudo minimo (apenas titulo e
assinatura), adicionando explicacao clara do que cada metodo/classe faz.

## Problema identificado

As paginas em `docs/sphinx/source/api/generated/*.rst` estavam praticamente
vazias para leitura humana, dificultando:

- entendimento rapido do fluxo;
- revisao por orientadores;
- uso da navegacao `[docs] <-> [source]`.

## Ajuste estrutural

Arquivo alterado:

- `docs/sphinx/source/conf.py`

Mudanca:

- `autosummary_generate = False`

Motivo:

- evitar que o Sphinx reescreva as paginas `api/generated/*.rst` a cada build;
- manter as descricoes manuais persistentes no GitHub Pages.

## Conteudo adicionado

Foram reescritas as 14 paginas de API com secoes padronizadas:

1. **Resumo**
2. **Parametros**
3. **Retorno**
4. **Efeitos colaterais** (quando aplicavel)
5. **Observacao** (quando aplicavel)

Objetos cobertos:

- `analise_dados.gera_mapas.plot_pred_map`
- `analise_dados.gera_mapas.plot_macroregions`
- `analise_dados.pos_processa.clean_data`
- `analise_dados.pos_processa.recall_event`
- `nucleo.fluxo_eventos.iterar_eventos`
- `nucleo.fluxo_eventos.fluxo_eventos`
- `nucleo.fluxo_eventos.main`
- `nucleo.utils.DualOutput`
- `nucleo.utils.csv2list`
- `rnc.data_process.get_fft`
- `rnc.data_process.spectro_extract`
- `rnc.prediction.discrim`
- `rnc.run.read_args`
- `rnc.run.main`

## Preservacao de rastreabilidade

As paginas mantiveram diretivas `autofunction`/`autoclass`, entao:

- assinatura e docstring continuam aparecendo;
- link `[source]` continua funcional;
- pagina de codigo em `_modules` continua com link `[docs]`.

## Validacao local

Comando:

```bash
PYENV_VERSION=sismologia sphinx-build -b html docs/sphinx/source docs/sphinx/build/html
```

Resultado:

- build concluido com sucesso;
- paginas renderizam texto explicativo dos metodos;
- conteudo manual nao foi sobrescrito no build.
