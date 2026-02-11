Operacao 0007 - Compreensao comportamental do fluxo_sismo.sh
=============================================================

Resumo
------

Leitura operacional do `fluxo_sismo.sh` por execucao incremental de etapas em
ambiente isolado, sem alteracao de codigo-fonte.

Efeito principal
----------------

- mapeamento objetivo do comportamento por flag;
- identificacao de bloqueios por dependencias de ambiente;
- validacao de pontos de fragilidade do orquestrador (parse e precondicoes de
  diretorio).

Pontos observados
-----------------

- `--help` exige catalogo como primeiro argumento;
- `-m` finaliza com sucesso mesmo sem entrada de mapas (no-op controlado);
- `-pe`, `-e -t`, `-pr`, `-po` e `-r` falham em etapas distintas por
  dependencias/precondicoes, com rastreabilidade documentada.

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0007-compreensao-comportamento-fluxo-sismo>`
