Padrao De Links Da Documentacao
===============================

Objetivo
--------

Definir regra unica de navegacao: toda mencao a arquivo, modulo, classe ou
funcao deve apontar para uma pagina da documentacao, e nao para download.

Regra obrigatoria
-----------------

1. Arquivo citado -> link para pagina em :doc:`/artefatos/index` ou
   :doc:`/anexos/index`.
2. Modulo, classe ou funcao Python citada -> link para :doc:`/api/index`.
3. Nao usar ``:download:`` para arquivos de referencia da documentacao.
4. Se a pagina do alvo ainda nao existir, criar a pagina antes de citar.

Exemplos validos
----------------

- arquivo Bash: :doc:`/artefatos/fluxo-sismo-sh`
- requirements core: :doc:`/artefatos/requirements-core-pipeline-txt`
- anexo de matriz: :doc:`/anexos/anexo-0018-matriz-testes-fluxo-sismo-10-tsv`
- funcao de aquisicao: :doc:`/api/generated/nucleo.fluxo_eventos.fluxo_eventos`
- funcao de pos-processamento: :doc:`/api/generated/analise_dados.pos_processa.main`

Observacao
----------

Links para GitHub continuam permitidos como complemento dentro da pagina
(documentacao <-> source), mas a navegacao primaria deve permanecer no site.
