#!/bin/bash

# if qgis is runing, close it
if pgrep -x "qgis.bin" > /dev/null
then
    echo "QGIS is running. Closing it..."
    pkill qgis.bin
fi

cp -r $HOME/projetos/ClassificadorSismologico/fonte/interface/farejadorsismo $HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins

pushd $HOME
export PYTHONPATH="$PYTHONPATH:/home/ggrl/.pyenv/versions/geologia/lib/python3.13/site-packages"
exec qgis &
popd

echo "Farejador de Sismos instalado com sucesso!"
