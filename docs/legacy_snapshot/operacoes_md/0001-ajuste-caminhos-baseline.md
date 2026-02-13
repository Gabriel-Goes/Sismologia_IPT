# Operacao 0001 - Ajuste de caminhos do baseline em `.specs/codebase`

**Data:** 2026-02-09
**Branch:** `refactor/fluxo-v2-documentado`
**Objetivo:** Corrigir paths hardcoded que apontavam para a raiz antiga do repositório, agora que o baseline foi movido para `.specs/codebase/`.

## Contexto

O baseline legado foi realocado para `.specs/codebase/` para servir como referência de leitura durante a reescrita do fluxo.

Com isso, scripts de entrada e módulos utilitários que assumiam `~/projetos/ClassificadorSismologico` deixaram de resolver corretamente quando executados no novo layout.

## Arquivos ajustados

1. `.specs/codebase/fluxo_sismo.sh`
2. `.specs/codebase/farejador.sh`
3. `.specs/codebase/plugin.sh`
4. `.specs/codebase/fonte/nucleo/utils.py`
5. `.specs/codebase/fonte/relatorio-sismologia/pyscripts/figures.py`
6. `.specs/codebase/fonte/relatorio-sismologia/pyscripts/mapa.py`

## O que foi alterado

- Entrada por shell:
  - scripts passam a resolver diretório base via `SCRIPT_DIR` (diretório do próprio arquivo), em vez de caminho absoluto.
- Baseline pipeline:
  - `BASE_DIR` agora aponta por padrão para o local real do baseline.
  - ajuste de verificação de catálogo para `"$BASE_DIR/arquivos/catalogo/$1"`.
  - correção de paths de backup/log para estrutura atual.
- Utilitário de núcleo:
  - `PROJETO_DIR` e `MSEED_DIR` derivados dinamicamente de `__file__` (Pathlib).
- Scripts de relatório:
  - remoção de dependência de `HOME + /projetos/ClassificadorSismologico`.
  - uso de `Path(__file__).resolve()` para localizar baseline e saídas.

## Resultado esperado

- Baseline antigo permanece utilizável como referência operacional.
- Reescrita do fluxo pode começar sem depender da antiga raiz do projeto.
- Menor acoplamento a ambiente local específico.

## Observações

- Esta operação não altera lógica científica do pipeline.
- Foco exclusivo em compatibilidade de caminho e portabilidade do baseline.

