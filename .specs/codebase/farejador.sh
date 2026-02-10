#!/bin/bash
#
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_DIR=${PROJ_DIR:-"$SCRIPT_DIR"}

pushd "$PROJ_DIR"
python3 fonte/interface/farejador.py
popd
