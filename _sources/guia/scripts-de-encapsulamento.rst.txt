Scripts De Encapsulamento
=========================

Objetivo
--------

Explicar por que criamos scripts de encapsulamento ao redor do
``fluxo_sismo.sh`` e como eles devem ser usados no ciclo de testes e
documentacao.

Problema que existia
--------------------

Executar o legado diretamente em ``.specs/codebase/`` gera artefatos em massa
(logs, CSVs, PDFs e saidas intermediarias). Isso causava:

1. sujeira recorrente na worktree;
2. risco de commit acidental de runtime;
3. baixa reprodutibilidade entre tentativas de teste;
4. dificuldade para publicar evidencias no Sphinx de forma padronizada.

Decisao de arquitetura
----------------------

Manter ``fluxo_sismo.sh`` como orquestrador cientifico e criar wrappers
operacionais em ``scripts/dev/`` para separar:

1. execucao tecnica;
2. arquivamento de evidencias;
3. publicacao na documentacao.

Linha de evolucao (0006 -> 0017 -> 0026)
-----------------------------------------

As tres operacoes formam uma cadeia unica de maturacao operacional:

1. :doc:`Operacao 0006 </operacoes/0006-organizacao-documentacao-e-runner-isolado>`
   - institui o runner isolado para reduzir poluicao da worktree.
2. :doc:`Operacao 0017 </operacoes/0017-runner-matriz-testes-e-guia-operacional>`
   - amplia para matriz de testes com arquivamento padronizado de execucoes.
3. :doc:`Operacao 0026 </operacoes/0026-protocolo-importacao-test-matrix>`
   - fecha o ciclo com importacao automatica de evidencias para o Sphinx.

Em termos de fluxo, isso estabelece o trilho:

1. executar sem poluir;
2. arquivar com rastreabilidade;
3. publicar com navegacao web.

Scripts criados e funcao de cada um
------------------------------------

1. Runner isolado:
   :doc:`/artefatos/run-fluxo-isolated-sh`

   - Script: ``scripts/dev/run_fluxo_isolated.sh``
   - Funcao: executar ``fluxo_sismo.sh`` em copia temporaria (``/tmp``),
     reduzindo poluicao da branch.
   - Quando usar: testes pontuais por flag (``-pe``, ``-pr``, ``-po`` etc.).

2. Runner de matriz com arquivamento:
   :doc:`/artefatos/run-fluxo-test-matrix-archived-sh`

   - Script: ``scripts/dev/run_fluxo_test_matrix_archived.sh``
   - Funcao: rodar bateria de casos com timeouts e salvar evidencias em
     ``.specs/codebase/arquivos/registros/test_matrix/<archive_id>/``.
   - Quando usar: validacao comparativa e reproducivel por operacao.

3. Importador de evidencias para docs:
   :doc:`/artefatos/import-test-matrix-to-docs-sh`

   - Script: ``scripts/dev/import_test_matrix_to_docs.sh``
   - Funcao: importar anexos de uma execucao ``test_matrix`` para
     ``docs/operacoes/anexos`` e gerar paginas renderizadas em
     ``docs/sphinx/source/anexos``.
   - Quando usar: fechamento de operacao com publicacao no Sphinx/GitHub Pages.

Fluxo recomendado
-----------------

1. Executar teste isolado rapido (runner isolado), se necessario.
2. Executar matriz oficial da operacao (runner arquivado).
3. Importar evidencias selecionadas para documentacao (importador).
4. Registrar conclusoes em ``docs/operacoes/<id>.md``.

Por que isso foi feito (resumo)
-------------------------------

1. preserva a logica cientifica do legado, sem refatoracao prematura;
2. melhora higiene de repositorio durante investigacao;
3. torna as execucoes auditaveis por ``archive_id``;
4. padroniza a trilha "teste -> anexo -> pagina Sphinx".

Referencias
-----------

- :doc:`Operacao 0006 </operacoes/0006-organizacao-documentacao-e-runner-isolado>`
- :doc:`Operacao 0017 </operacoes/0017-runner-matriz-testes-e-guia-operacional>`
- :doc:`Operacao 0026 </operacoes/0026-protocolo-importacao-test-matrix>`
- :doc:`Execucoes de teste do fluxo legado </guia/execucoes-de-teste-fluxo-legado>`
