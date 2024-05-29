#!/bin/bash
#
pushd $HOME/projetos/ClassificadorSismologico/
exec python3 fonte/farejador_eventos/farejador.py
popd
