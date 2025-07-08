#!/bin/bash
#
PROJ_DIR=${PROJ_DIR:-"$HOME/projetos/ClassificadorSismologico"}

pushd "$PROJ_DIR"
python3 fonte/interface/farejador.py
popd
