# Operacao 0019 - Padrao de links e anexos renderizados no Sphinx

**Data:** 2026-02-10  
**Branch:** `refactor/fluxo-v2-documentado`  
**Contexto:** `refatoracao`  
**Status:** `concluida`

## Objetivo

Aplicar a regra de navegacao da documentacao:

1. mencao a arquivo/modulo/classe/funcao deve ter link navegavel;
2. anexos de operacao (`csv/tsv/log`) devem abrir em pagina web da doc;
3. remover uso de links de download para anexos.

## Escopo executado

1. Criacao da secao `Anexos` no Sphinx:
   - `docs/sphinx/source/anexos/index.rst`
   - paginas renderizadas para anexos das operacoes 0005, 0016 e 0018.
2. Substituicao de `:download:` por `:doc:` nas paginas de operacao:
   - `0005`, `0016`, `0018`.
3. Registro do padrao de links no User Guide:
   - `docs/sphinx/source/guia/padrao-de-links.rst`
   - navegacao atualizada em `docs/sphinx/source/guia/index.rst`.
4. Expansao de paginas de `Artefatos` para suportar novos alvos de link:
   - runner de matriz;
   - `.python-version`;
   - memoria de ambiente pyenv;
   - `sismo_iptex.cls`.
5. Ajustes de navegacao global:
   - `docs/sphinx/source/index.rst` inclui `Anexos`.

## Resultado

1. Os anexos citados em operacoes agora abrem em paginas web renderizadas.
2. As paginas de operacao passaram a apontar para doc pages, nao para download.
3. O padrao de links virou regra explicita da documentacao.

## Observacoes

1. Links para GitHub continuam como complemento dentro das paginas de artefato/anexo.
2. A navegacao principal permanece dentro do GitHub Pages/Sphinx.

## Proximo passo

Aplicar a correcao tecnica do contrato de dados entre `-pr` e `-po` para evitar
quebras quando `predito.csv` vier vazio ou com schema parcial.
