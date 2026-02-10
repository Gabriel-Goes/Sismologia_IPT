# Possible Paper Outline

## Why is catalog completeness important?
Because it informs Gutenberg-Richter relationships, which in turn inform seismic hazard analysis.
The b parameter is used to estimate the recurrence time of larger events;
(Cite some papers here. Mention more reasons why it is important).

In intraplate regions like Brazil, small magnitude earthquakes exert a large control on the slope of the GR distribution, since larger events are much harder to come by.

**Small earthquakes in the past might have triggered catastrophic tailings dam failures in Brazil, making seismic hazard studies with a clean catalog important in areas with a large concentration of critical structures.**
**I would say this is the main justification for this study.**

## Why does the model work?
Because high frequencies in quarry blasts cancel-out due to line blasts.
However, after traveling for a certain distance, natural attenuation of high frequencies makes natural and anthropogenic events indistinguishable when using this approach, rendering the method unreliable.
Can this be remedied in some way by employing other methods in addition to the classifier?

Retraining the model seems like a very good idea given the Korea results
(see attached poster).

### How to get reliable blasts for training?
 - Cross correlation of waveforms with known blasts.
 - Known blasts from Salles Catalog.
 - Spatial analysis of events (SIGEmine).
 - Temporal filtering (Both for blasts and Natural Earthquakes).

Attenuation is going to be different in different parts of Brazil (Korea is tiny).
This retraining can probably only be carried out in areas with relatively high station density, and even then tentatively (Brazilian Southeast and Northeast).
#### Along the coast? How to get this data?
For sparse station coverage, different approaches might be needed.
**Brian (NU undergrad) is interested in doing some work here with new neural models.**
(This would take more time).

## Proximos passos:
 - Documentar os processos que foram feitos para chegar em nossos resultados;
 - Remover eventos Magnitude > 4 e profundidade > 10km;
 - Utilizar sismos do Sudeste (MG) selecionar melhor estações;
 - Utilizar JupyterNotebook para processamento dos dados destrinchando o passo a passo;
 - Utilizar a seisapp;

## Futuro:
 - Identificar motivos de eventos antropogênicos durante a madrugada
 - Buscar catálogo do Boletim
