Operacao 0016 - Estabilizacao dos testes do fluxo_sismo.sh com 50 amostras
===========================================================================

Resumo
------

Consolidacao dos ajustes tecnicos para tornar reproduzivel a bateria de testes
do legado com ``--test`` e 50 amostras, separando:

- problemas de ambiente/conectividade (FDSN);
- problemas de robustez do proprio pipeline legado.

Efeito principal
----------------

- ``pre``, ``predict``, ``pos``, ``maps`` e ``report`` passaram em ambiente
  local com artefatos legados disponiveis;
- ``eventos`` e ``todos`` continuam dependentes de acesso FDSN no host.
- fallback FDSN reforcado com verificacao de servico ``event`` por endpoint;
- ``seisrequest`` passou a ser fallback util para ``station/dataselect``, mas
  nao substitui o servico ``event`` do SeisComP/USP.

Arquivos de interesse
---------------------

- ``.specs/codebase/fluxo_sismo.sh``
- ``.specs/codebase/fonte/nucleo/fluxo_eventos.py``
- ``.specs/codebase/fonte/rnc/run.py``
- ``.specs/codebase/fonte/rnc/data_process.py``
- ``.specs/codebase/fonte/relatorio-sismologia/relatorio_preditivo.tex``
- ``.specs/codebase/fonte/relatorio-sismologia/sismo_iptex.cls``
- ``docs/operacoes/anexos/0016-matriz-testes-fluxo-sismo-50.tsv``
- ``docs/operacoes/anexos/0016-teste-e-t-10.log``

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0016-estabilizacao-testes-fluxo-sismo-50-amostras>`
- :download:`Matriz final (TSV) <../../../operacoes/anexos/0016-matriz-testes-fluxo-sismo-50.tsv>`
- :download:`Reteste -e -t (10 eventos) <../../../operacoes/anexos/0016-teste-e-t-10.log>`
