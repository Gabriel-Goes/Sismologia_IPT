# Operacao 0009 - Estrutura Sphinx API/source e artefatos renderizados

**Data:** 2026-02-10  
**Branch:** `refactor/fluxo-v2-documentado`

## Objetivo

Evoluir a documentacao para um fluxo navegavel no padrao:

1. User Guide -> API;
2. API -> `[source]`;
3. Source -> `[docs]`.

Tambem converter referencias de artefatos (`.sh` e `.txt`) de download direto
para paginas renderizadas no GitHub Pages.

## Escopo executado

1. Atualizacao do Sphinx (`docs/sphinx/source/conf.py`):
   - extensoes adicionais: `autosummary`, `autosectionlabel`, `extlinks`,
     `sphinx_copybutton`, `sphinx_design`;
   - configuracao de `sys.path` para importar modulos da baseline em
     `.specs/codebase/fonte`;
   - `autodoc_mock_imports` para dependencias pesadas no build de docs;
   - `extlinks` para linkar arquivo fonte no GitHub (`:ghblob:`).

2. Reorganizacao da navegacao principal:
   - inclusao de `guia/index`, `api/index` e `artefatos/index` no
     `docs/sphinx/source/index.rst`;
   - ajuste da `visao_geral` para refletir essa estrutura.

3. User Guide e API Reference:
   - criacao de `docs/sphinx/source/guia/fluxo-e-referencias.rst`;
   - criacao de `docs/sphinx/source/api/index.rst`;
   - geracao de paginas `api/generated/*.rst` para funcoes-chave do baseline.

4. Renderizacao de artefatos nao-Python:
   - criacao de `docs/sphinx/source/artefatos/*.rst` com `literalinclude`;
   - links para fonte via `:ghblob:`;
   - troca em `operacoes/0008` de links `:download:` para `:doc:`.

5. Workflow de docs no GitHub Actions:
   - instalacao de `sphinx-copybutton` e `sphinx-design` em
     `.github/workflows/docs.yml`.

## Validacao local

Comando executado:

```bash
PYENV_VERSION=sismologia sphinx-build -b html docs/sphinx/source docs/sphinx/build/html
```

Resultado:

- build concluido com sucesso;
- paginas de API com botao `[source]`;
- paginas `_modules` com backlink `[docs]`;
- artefatos `.sh/.txt` renderizados como pagina HTML no site.

## Impacto

- melhora de navegacao e rastreabilidade entre guia tecnico, referencia e fonte;
- elimina comportamento de "download forcado" para artefatos textuais;
- base preparada para crescer com documentacao por operacao sem perder contexto
  do codigo legado.

## Limites atuais

- nem todo script da baseline e seguro para autodoc em tempo de importacao;
- escopo da API atual cobre objetos com import mais previsivel;
- novos modulos podem ser incluidos gradualmente conforme refatoracao v2.
