#  Python software for discrimination between natural and anthropogenic events

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/git/https%3A%2F%2Fgitlab.univ-nantes.fr%2FE181658E%2Fdiscrimination_eq_q/HEAD)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7064191.svg)](https://doi.org/10.5281/zenodo.7064191)

## Install miniconda and requirements

* Download this repository :

```
git clone https://gitlab.univ-nantes.fr/E181658E/discrimination_eq_q.git
cd discrimination_eq_q
```

* Install to default environment :

```
conda env update -f=environment.yml -n base
```

* Install to "discrim" virtual envirionment

```
conda env create -f environment.yml
conda activate discrim
```

## Reference

Céline Hourcade, Mickaël Bonnin, Éric Beucler, New CNN based tool to discriminate anthropogenic from natural low magnitude seismic events, Geophysical Journal International, 2022;, ggac441, https://doi.org/10.1093/gji/ggac441

## Dataset

To apply the algorithm, we need a folder architecture:
 * mseed_demo
   * 2022004T134407
        * FR_CHLF_2022004T134407.mseed
        * FR_GARF_2022004T134407.mseed
        * FR_GNEF_2022004T134407.mseed
        * FR_VERF_2022004T134407.mseed

Each mseed file corresponds to the raw 3 component recordings of 60 sec.

A csv file is also required to apply the algorithm. 
It is composed of a column with folders/events to discriminate. If the -valid option is specified, the file must have a second column with the label associated with the event. 


| time     | label_cat      |
| ------------- | ------------- |
| 2022004T134407         | 0         |
| 2022003T041502         | 0         | 
| 2022001T213524         | 0         | 
| 2022004T111745         | 1         | 

Label 0 means "Natural event", label 1 "Anthropogenic event".

## Trained model

Located in directory: model/model_2021354T1554.h5


## Prediction

As input, you need a one-column csv file with the folders/events to be discriminated.
The algorithm supports the mseed data format.

-  mseed format
```
 python run.py --data_dir ./mseed_demo --spectro_dir ./spectro_demo --output_dir ./output_demo --csv_dir demo_pred.csv
```

Output files are automatically saved in "output_demo".
The algorithm produces two output files: "prediction_network_level.csv" and "prediction_station_level.csv".

-  prediction_station_level.csv

This output corresponds to the prediction of each mseed file and therefore for each station.

| file_name     | station      | prob_nat   | prob_ant   | pred   | nature
| ------------- | ------------- | --------    |--------    |--------    |--------    |
| FR_CHLF_2022004T134407         | CHLF         | 0.962   |0.038    | 0   | Natural   |
| FR_GARF_2022004T134407         | GARF         | 0.982   |0.018    | 0   | Natural   |
| FR_GNEF_2022004T134407         | GNEF         | 0.914   |0.086    | 0   | Natural   |
| FR_VERF_2022004T134407         | VERF         | 0.985   |0.015    | 0   | Natural   |

-  prediction_network_level.csv

This output corresponds to the prediction of each event. We sum the probabilities for each class for all stations of a given
event and then average them. This gives us an event-based classification.

| event      | prob_nat   | prob_ant   | pred   | nature
| ------------- | ------------- | --------    |--------    |--------    |
| 2022003T041502         | 0.988           | 0.012   | 0 |  Natural   |
| 2022004T111745          | 0.005   |0.995    | 1   | Anthropogenic   |
| 2022004T111040         | 0.005   |0.995  | 1   | Anthropogenic   |
| 2022004T105235        | 0.011  |0.989 | 1   | Anthropogenic   |



## Validation

This mode can be used if the label is known. The -valid argument is then specified.
As input you need a csv file of two columns with the associated label for each event.
The algorithm supports the mseed data format.

-  mseed format
```
 python run.py --data_dir ./mseed_demo --spectro_dir ./spectro_demo --output_dir ./output_demo --csv_dir demo_valid.csv --valid
```

Output files are automatically saved in "output_demo".
The algorithm produces two output files: "prediction_network_level.csv" and "prediction_station_level.csv".

-  prediction_station_level.csv

This output corresponds to the prediction of each mseed file and therefore for each station.

| file_name     | station  |   label_cat | prob_nat   | prob_ant   | pred   | nature   |
| ------------- | ------------- | --------    |--------    |--------    |--------    |  --------    |
| FR_CHLF_2022004T134407         | CHLF    | 0     | 0.962   |0.038    | 0   | Natural   |
| FR_GARF_2022004T134407         | GARF    | 0      | 0.982   |0.018    | 0   | Natural   |
| FR_GNEF_2022004T134407         | GNEF    | 0      | 0.914   |0.086    | 0   | Natural   |
| FR_VERF_2022004T134407         | VERF    | 0      | 0.985   |0.015    | 0   | Natural   |

-  prediction_network_level.csv

This output corresponds to the prediction of each event. We sum the probabilities for each class for all stations of a given
event and then average them. This gives us an event-based classification.

| event     | label_cat | prob_nat   | prob_ant   | pred   | nature   |
| ------------- | ------------- | --------    |--------    |--------    |  --------    |
| 2022003T041502    | 0      | 0.988           | 0.012   | 0 |  Natural   |
| 2022004T111745    | 1      | 0.005   |0.995    | 1   | Anthropogenic   |
| 2022004T111040    | 1     | 0.005   |0.995  | 1   | Anthropogenic   |
| 2022004T105235    | 1    | 0.011  |0.989 | 1   | Anthropogenic   |

