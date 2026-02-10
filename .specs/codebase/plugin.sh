#!/bin/bash

# if qgis is runing, close it
if pgrep -x "qgis.bin" > /dev/null
then
    echo "QGIS is running. Closing it..."
    pkill qgis.bin
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_DIR=${PROJ_DIR:-"$SCRIPT_DIR"}
PLUGIN_DIR=${PLUGIN_DIR:-"$HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins"}
VENV_DIR=${VENV_DIR:-"$HOME/.pyenv/versions/geologia"}

cp -r "$PROJ_DIR/fonte/interface/farejadorsismo" "$PLUGIN_DIR"

pushd "$HOME"
export PYTHONPATH="$PYTHONPATH:$VENV_DIR/lib/python3.13/site-packages:$VENV_DIR/bin/python"
popd

qgis &

echo "Farejador de Sismos instalado com sucesso!"
