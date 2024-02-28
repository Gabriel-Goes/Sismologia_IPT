#!/bin/bash
# Este código recebe uma data de início e uma data de fim e um ID de rede sismo
# lógica. Com estas informações cria um arquivo event-<ID>.csv com os eventos sismicos
# que ocorreram no intervalo de tempo especificado e foram capturados pela rede sismológica.
# Com este arquivo, segue-se para o passo de aquisição das formas de onda e criação dos mapas.
# -----------------------------------------------------------------------------
DATES="2023-11-01 2023-11-15"
ID="USP"
# -----------------------------------------------------------------------------
PYTHON3="/home/ipt/.config/geo/bin/python3"
SEISCOMP="/home/ipt/softwares/seiscomp/bin/seiscomp"
ENERGYFIG="/home/ipt/lucas_bin/energy_fig.py"
CREATEMAP="/home/ipt/lucas_bin/make_maps_"$ID".py"
EVENTS=$(find ./files/ -maxdepth 1 -name "events-*.csv")
# -----------------------------------------------------------------------------
echo " ---------------- Iniciando do Pipeline --------------------------------"
echo " -> Executando  Processar_Dados_Sismicos.py..."
$SEISCOMP exec $PYTHON3 pyscripts/Processar_Dados_Sismicos.py $DATES $ID
echo " -------------- Processo de criação de mapas iniciado ------------------"
for i in $EVENTS
    do
        echo $i
        $PYTHON3 $CREATEMAP $i
        mv $i files/
        mv *png figures
done
#~ echo " ---------------- Iniciando o energy_fig.py ---------------------------- "
#~ echo "Creating energy plots..."
#~ $PYTHON $ENERGYFIG $OUTPUT
#~ echo "Cleaning up..."
#~ rm events*.csv
echo " ---------------- Iniciando o cria_pred.py ---------------------------- "
$PYTHON3 pyscripts/Gerar_predcsv.py
