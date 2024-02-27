#!/bin/bash

PYTHON3="/home/ipt/.config/geo/bin/python3"
ENERGYFIG="/home/ipt/lucas_bin/energy_fig.py"
CREATEMAP="/home/ipt/lucas_bin/make_maps_"$ID".py"
EVENTS=$(find ./files/ -maxdepth 1 -name "events-*.csv")

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
echo ''
