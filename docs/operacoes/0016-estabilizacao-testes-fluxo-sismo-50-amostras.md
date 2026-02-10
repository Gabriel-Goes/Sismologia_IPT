# Operacao 0016 - Estabilizacao dos testes do `fluxo_sismo.sh` com `--test` (50 amostras)

**Data:** 2026-02-10  
**Branch:** `refactor/fluxo-v2-documentado`  
**Contexto:** `refatoracao`  
**Status:** `concluida`

## Objetivo

Documentar, de forma rastreavel, os passos executados para estabilizar o
comportamento do pipeline legado em modo de teste (`--test`) com amostragem de
50 eventos, antes do ciclo presencial no ambiente do IAG/SEISAPP.

## Entendimento consolidado do fluxo (o que precisava ficar claro)

1. `-pr` (RNC) **nao precisa** obrigatoriamente de `-e` na mesma execucao.
2. `-pr` precisa de insumos preexistentes:
   - `arquivos/eventos/eventos.csv`
   - arquivos em `arquivos/mseed/*`
3. Como existem artefatos legados locais (execucoes antigas), etapas como
   `-po`, `-m`, `-r` e o proprio `-pr` podem funcionar mesmo sem `-e` no mesmo
   comando.
4. O que estava confundindo os testes era o efeito colateral de `-e`:
   o script movia `eventos.csv` para `.bkp` antes do download; com FDSN offline,
   o arquivo nao era recriado e o `-pr` seguinte quebrava.

## Metodo aplicado

Todos os testes de validacao foram executados em copias isoladas em `/tmp`,
mantendo a arvore do repositorio limpa de artefatos de execucao.

Exemplo de pasta de evidencia final:

- `/tmp/matrix-after-pr-fixes-20260210_155406`

## Passos executados (ordem real)

1. Reproducao inicial do problema com matriz de flags (`-pe`, `-e`, `-pr`,
   `-po`, `-m`, `-r`, `todos`) em `--test`.
2. Confirmacao de que `eventos.csv` esta versionado no Git e disponivel na
   codebase legado, descartando hipotese de `.gitignore` como causa principal.
3. Correcao de robustez GMT/PyGMT para `coast`:
   - configuracao de `GMT_USERDIR` gravavel;
   - vinculacao dos datasets locais `gshhg/dcw` em `~/.gmt/geography`.
4. Correcao da etapa de relatorio para nao travar interativamente:
   - `pdflatex -interaction=nonstopmode -halt-on-error`.
5. Correcao LaTeX de idioma no relatorio preditivo:
   - reativacao de `babel` em `relatorio_preditivo.tex`.
6. Correcao de recurso grafico ausente no `sismo_iptex.cls`:
   - fallback de `footImage.pdf` para `footer_IPT.png`.
7. Correcao de fallback FDSN em `fluxo_eventos.py`:
   - tentativa de cliente principal e backup antes de abortar.
8. Ajuste de amostragem de teste do fluxo de eventos:
   - `TEST_EVENT_LIMIT` (default `50`) em `fluxo_eventos.py`.
9. Ajuste de amostragem de teste da RNC:
   - novo argumento `--test-limit` em `fonte/rnc/run.py`;
   - `fluxo_sismo.sh` passa `--test-limit` para `-pr -t`.
10. Correcao de bug legado da RNC em `data_process.py`:
    - escrita robusta em colunas lista (`Error`, `Warning`, `Compo`) sem
      indexacao frágil (`[0].append(...)`);
    - leitura de mseed respeitando parametro `mseed_dir`.
11. Correcao do backup de `eventos.csv` em `-e`:
    - trocado `mv` por `cp` para preservar insumo legado quando FDSN falha.

## Resultado final da matriz (50 amostras)

Arquivo consolidado (trazido de `/tmp` para o repositorio):

- `docs/operacoes/anexos/0016-matriz-testes-fluxo-sismo-50.tsv`

Resumo:

1. `pre` -> `rc=0`
2. `eventos` -> `rc=1` (sem acesso aos servidores FDSN no ambiente atual)
3. `predict` -> `rc=0`
4. `pos` -> `rc=0`
5. `maps` -> `rc=0`
6. `report` -> `rc=0`
7. `todos` -> `rc=1` (falha herdada de `-e` por indisponibilidade FDSN)

## Atualizacao complementar: FDSN (`-e -t`) com 10 eventos

1. Foi adicionado novo endpoint de backup no `fluxo_eventos.py`:
   - `http://seisrequest.iag.usp.br`
2. A logica de conexao FDSN foi reforcada para listar os servicos expostos
   por cada cliente e validar explicitamente a existencia do servico `event`.
3. Endpoints sem `event` agora sao ignorados para a etapa `-e`, com mensagem
   explicita no log.
4. Se nenhum endpoint com `event` estiver disponivel, o fluxo falha cedo com
   mensagem clara indicando a dependencia de acesso ao ambiente IAG/SeisComP.
5. Reteste executado com `TEST_EVENT_LIMIT=10` para `-e -t`:
   - `seisrequest` respondeu apenas com `dataselect` e `station`;
   - `rsbr` respondeu com `event`, mas os `EventID` amostrados (`usp...`) nao
     foram encontrados no catalogo remoto;
   - o teste concluiu sem download de eventos, confirmando o bloqueio de
     rede/catalogo fora do ambiente IAG.

## Interpretacao tecnica

1. A estabilizacao local foi alcancada para o fluxo que depende de artefatos
   ja existentes (`eventos.csv`, `mseed`, resultados legados).
2. O unico bloqueio funcional restante para `eventos`/`todos` e conectividade
   com os endpoints FDSN no ambiente de teste atual.
3. O comportamento observado nos logs passa a ser coerente com o desenho do
   pipeline legado: etapas sao parcialmente desacopladas quando os artefatos
   de entrada ja existem.
4. O endpoint `seisrequest` e util para `station` e `dataselect`, mas nao
   substitui o acesso ao servico `event` do SeisComP/USP para aquisicao
   completa via `-e`.

## Arquivos alterados nesta etapa

1. `.specs/codebase/fluxo_sismo.sh`
2. `.specs/codebase/fonte/nucleo/fluxo_eventos.py`
3. `.specs/codebase/fonte/rnc/run.py`
4. `.specs/codebase/fonte/rnc/data_process.py`
5. `.specs/codebase/fonte/relatorio-sismologia/relatorio_preditivo.tex`
6. `.specs/codebase/fonte/relatorio-sismologia/sismo_iptex.cls`

## Evidencias

1. Matriz final local:
   - `docs/operacoes/anexos/0016-matriz-testes-fluxo-sismo-50.tsv`
2. Pasta de execucao isolada da matriz final:
   - `/tmp/matrix-after-pr-fixes-20260210_155406`
3. Reteste de `-pr -t` com 50 eventos e retorno `rc=0`:
   - `/tmp/retest-pr-limit2-20260210_155231`
4. Reteste de conectividade FDSN em `-e -t` com 10 eventos:
   - `docs/operacoes/anexos/0016-teste-e-t-10.log`

## Proximo passo

Executar a mesma bateria no ambiente com acesso de rede ao IAG/SEISAPP para
validar `-e` e, por consequencia, `todos` com download real via FDSN.
