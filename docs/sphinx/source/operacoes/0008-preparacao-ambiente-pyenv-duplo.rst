Operacao 0008 - Preparacao de ambiente com pyenv duplo
=======================================================

Resumo
------

Definicao de estrategia de ambiente com dois virtualenvs (`pyenv-virtualenv`):
um para o pipeline geral e outro para a RNC legado com TensorFlow antigo.

Efeito principal
----------------

- reduz conflito entre stack de processamento e stack legado da RNC;
- transforma setup manual em roteiro reproduzivel via script;
- prepara migracao do ambiente para o servidor SEISAPP antes da reescrita v2.

Artefatos
---------

- ``scripts/dev/setup_pyenv_dual_envs.sh``
- ``scripts/dev/requirements-core-pipeline.txt``
- ``scripts/dev/requirements-rnc-legacy.txt``

Documento detalhado
-------------------

- :doc:`Documento detalhado </detalhes/0008-preparacao-ambiente-pyenv-duplo>`
- :doc:`Script de bootstrap pyenv duplo </artefatos/setup-pyenv-dual-envs-sh>`
- :doc:`Requirements core </artefatos/requirements-core-pipeline-txt>`
- :doc:`Requirements RNC legado </artefatos/requirements-rnc-legacy-txt>`
