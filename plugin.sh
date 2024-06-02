#!/bin/bash
cp ./plugin.sh $HOME/.local/bin/
chmod +x $HOME/.local/bin/plugin.sh
killall qgis
pushd $HOME/projetos/ClassificadorSismologico
cp -r ./fonte/interface/farejadorsismo $HOME/.local/share/QGIS/QGIS3/profiles/Gabriel/python/plugins/

rm -rf ./arquivos/registros/farejador.log
touch ./arquivos/registros/farejador.log

exec qgis &
popd

exit 0
