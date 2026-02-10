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

- :doc:`fluxo_sismo.sh </artefatos/fluxo-sismo-sh>`
- :doc:`nucleo.fluxo_eventos.main </api/generated/nucleo.fluxo_eventos.main>`
- :doc:`nucleo.fluxo_eventos.fluxo_eventos </api/generated/nucleo.fluxo_eventos.fluxo_eventos>`
- :doc:`rnc.run.main </api/generated/rnc.run.main>`
- :doc:`rnc.data_process.spectro_extract </api/generated/rnc.data_process.spectro_extract>`
- :doc:`relatorio_preditivo.tex </artefatos/relatorio-preditivo-tex>`
- :doc:`sismo_iptex.cls </artefatos/sismo-iptex-cls>`
- :doc:`Anexo matriz 0016 (TSV) </anexos/anexo-0016-matriz-testes-fluxo-sismo-50-tsv>`
- :doc:`Anexo reteste 0016 (LOG) </anexos/anexo-0016-reteste-e-t-10-log>`

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0016-estabilizacao-testes-fluxo-sismo-50-amostras>`
- :doc:`Matriz final (TSV) </anexos/anexo-0016-matriz-testes-fluxo-sismo-50-tsv>`
- :doc:`Reteste -e -t (10 eventos) </anexos/anexo-0016-reteste-e-t-10-log>`
