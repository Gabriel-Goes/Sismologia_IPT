# Operacao 0007 - Compreensao comportamental do `fluxo_sismo.sh`

**Data:** 2026-02-10  
**Branch:** `refactor/fluxo-v2-documentado`

## Objetivo

Entender o comportamento atual do orquestrador legado
`.specs/codebase/fluxo_sismo.sh` sem alterar codigo, usando execucoes
controladas por etapa.

## Estrategia de execucao (baseada na operacao 0005)

Com base na analise historica dos logs (`0005`), evitamos rodar o fluxo completo
de primeira. O teste foi conduzido em modo incremental:

1. ambiente isolado (worktree temporaria), para nao sujar a branch;
2. catalogo menor (`catalogo_jul_filtrado.csv`);
3. execucao por modulo (`-pe`, `-e -t`, `-pr`, `-po`, `-m`, `-r`);
4. observacao de falhas de contrato e dependencias por etapa.

## Evidencias de comportamento do script

Referencias de logica em `.specs/codebase/fluxo_sismo.sh`:

- validacao obrigatoria do primeiro argumento como catalogo:
  `.specs/codebase/fluxo_sismo.sh:52`
- `--help` so e tratado apos validacao de catalogo:
  `.specs/codebase/fluxo_sismo.sh:62`
- backup de `eventos.csv` para pasta `.bkp` sem criar `arquivos/eventos/.bkp`:
  `.specs/codebase/fluxo_sismo.sh:163`
- etapa de mapas executa apenas se `df_nc_pos.csv` existir:
  `.specs/codebase/fluxo_sismo.sh:194`
- etapa de relatorio executa `figures.py`, `mapa.py` e `pdflatex`:
  `.specs/codebase/fluxo_sismo.sh:204`

## Matriz de testes executados

1. `bash ./fluxo_sismo.sh --help` (via runner isolado)  
   Resultado: falha com `Erro: Arquivo --help não encontrado!`.

2. `bash ./fluxo_sismo.sh catalogo_jul_filtrado.csv --help`  
   Resultado: sucesso; menu de ajuda exibido.

3. `bash ./fluxo_sismo.sh catalogo_jul_filtrado.csv -m`  
   Resultado: sucesso sem gerar mapa (comportamento esperado sem
   `df_nc_pos.csv`).

4. `bash ./fluxo_sismo.sh catalogo_jul_filtrado.csv -pe`  
   Resultado: falha em `pre_processa.py` por dependencia ausente:  
   `ModuleNotFoundError: No module named 'shapely'`.

5. `bash ./fluxo_sismo.sh catalogo_jul_filtrado.csv -e -t` (sem preparo extra)  
   Resultado: falha ao mover backup por pasta ausente:  
   `mv ... arquivos/eventos/.bkp/...: No such file or directory`.

6. `bash ./fluxo_sismo.sh catalogo_jul_filtrado.csv -e -t` (com
   `arquivos/eventos/.bkp` pre-criado na worktree temporaria)  
   Resultado: avancou ate `fluxo_eventos.py`, falhando por dependencia ausente:  
   `ModuleNotFoundError: No module named 'tqdm'`.

7. `bash ./fluxo_sismo.sh catalogo_jul_filtrado.csv -pr`  
   Resultado: falha em `fonte/rnc/run.py` por dependencia ausente:  
   `ModuleNotFoundError: No module named 'tensorflow'`.

8. `bash ./fluxo_sismo.sh catalogo_jul_filtrado.csv -po`  
   Resultado: falha em `pos_processa.py` por dependencia ausente:  
   `ModuleNotFoundError: No module named 'seaborn'`.

9. `bash ./fluxo_sismo.sh catalogo_jul_filtrado.csv -r`  
   Resultado: `figures.py` e `mapa.py` executam, `pdflatex` inicia, mas encerra
   com erro TeX: `Undefined control sequence` em `\addto`.

10. `bash ./fluxo_sismo.sh` (sem argumentos)  
    Resultado: script ativa todas as etapas, mas sem catalogo definido; falha
    cedo em `pre_processa.py` (dependencia `shapely` ausente), confirmando o
    comentario no proprio arquivo de que o modo sem argumentos "nao esta
    funcionando".

## Leitura tecnica consolidada

1. O script funciona como orquestrador sequencial por flags.
2. O parse atual obriga catalogo antes de qualquer opcao util.
3. O fluxo e sensivel a estado de diretório de backup (`.bkp`) e ao ambiente
   Python/TeX.
4. A estrategia incremental usada nesta operacao e consistente com os padroes
   do historico de logs (falhas por etapa/dependencia).

## Conclusao para a refatoracao v2

Sem mudar o codigo legado, ja foi possivel mapear comportamento e pontos de
acoplamento operacional. O proximo passo natural e formalizar um "preflight"
de ambiente e de estrutura de pastas antes da reescrita funcional das etapas.
