#!/bin/bash

DATES="2022-12-01 2022-12-30"
ID="IT"
#PYTHON="/usr/bin/python"
PYTHON3="/home/ipt/.config/geo/bin/python3"
SEISCOMP="/home/ipt/softwares/seiscomp/bin/seiscomp"
CREATEMAP="/home/ipt/bin/make_maps_"$ID".py"
ENERGYFIG="/home/ipt/bin/energy_fig.py"


echo "Creating event files..."
$SEISCOMP exec $PYTHON3 fdsnwscsv_.py $DATES $ID
EVENTS=$(find . -maxdepth 1 -name "events-*.csv")

echo "Creating maps..."
for i in $EVENTS
do
	echo $i
    $PYTHON3 $CREATEMAP $i 
    mv $i files/
    mv *png figures
done

#~ echo "Creating energy plots..."
#~ $PYTHON $ENERGYFIG $OUTPUT

#~ echo "Cleaning up..."
#~ rm events*.csv
#

$PYTHON3 cria_pred.py
