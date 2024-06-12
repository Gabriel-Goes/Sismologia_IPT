#!/bin/bash

# if qgis is runing, close it
if pgrep -x "qgis.bin" > /dev/null
then
    echo "QGIS is running. Closing it..."
    pkill qgis.bin
fi

cp -r $HOME/projetos/ClassificadorSismologico/fonte/interface/farejadorsismo $HOME/.local/share/QGIS/QGIS3/profiles/Gabriel/python/plugins

pushd $HOME
export PYTHONPATH=$HOME/.pyenv/versions/sismologia/lib/python3.11/site-packages:$HOME/.pyenv/versions/sismologia/bin/python:$PYTHONPATH
exec qgis &
popd

echo "Farejador de Sismos instalado com sucesso!"
