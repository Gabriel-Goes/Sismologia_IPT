# SISBRA - Catálogo de Sismos do Brasil

This the GIT repo for the SISBRA catalog. This catalog is constructed by [CS/USP](http://www.moho.iag.usp.br/) with support from many other contributors from inside the [RSBR](http://www.rsbr.gov.br/) (USP, UnB, UFRN, Obsevatório Nacional e CPRM) and outside (IPT-SP, UNESP-SP, UFMS, etc.).

The main file was constructed by Marcelo Assumpção. It was versioned into this GIT repository by Marcelo B. de Bianchi.

## What's inside

The SISBRA repo holds basically the RAW catalog and FELT catalog. The RAW has events that have occurred in around Brazil. FELT contains South American earthquakes felt in major cities (like São Paulo, Rio de Janeiro, etc.).

The catalog files are normally hand edited and later validated.

The repo holds a Python language code capable of reading the RAW files with capacity to export it to CLEAN and SCR files. The tool can also generate CSV files from RAW files. While reading the file the tool is capable of validating many aspects of the files.

Together with the Python code there is a `Makefile`. The `Makefile` is used to (1) Do some very basic checking of the files and (2) To prepare a new release.

## Want to contribute

We appreciate any comments or contributions to this repository information. We do accept contributions but they will be evaluated prior to acceptance.

**If you have any questions about this repository or want to contribute don't hesitate to write us at `sismologia@iag.usp.br`.**

The most proper way to change the master branch is by making a merge-request. Your proposed changes will be evaluated before it is accepted or rejected using a git style revision process (preferably). 

## Using the Makefile

Basic check of the catalog:

```
$ make
```

to build a release you should edit the Makefile and define the `rcode` variable to the new release string. Also please edit the CAT and FELT files to the ones you would like to use. After that, type:

```
$ make release
```

and even, to generate a map, using gmt (version 6.2+)

```
$ make map
```

The `Makefile` depends on a number of tools like Python (3.6+), Libreoffice, (gnu)date, (gnu)md5sum, flip, file, (gnu)grep zip and (gnu)sed.

## Fields in RAW (and CSV) files

The catalog are tabbed files with information in columns. Each earthquake is defined in a line. The columns are:

 * year (ano): Is the year of the earthquake
 * hh[mm[ss][L]] (hh,min,ss.s): indicates the hour, minute and second of the earthquake origin time. The `L` code indicates that the time is in local time. The `L` code stays together with the time string in RAW files, in CSV files generated it is split to a new column.
 * latit longit: are epicenter coordinates (latitude and longitude) normally associated to GPS datum.
 * err or err(km): is the epicentral error estimated in km.
 * st: is the Brazilian abbreviated state code (normally two letters). For epicenters outside Brazil it can also has the country code.
 * depth: is the earthquake depth, in km (hypocenter). A value of 0.0 always means missing information.
 * mag: is the Richter magnitude value. 

 > The mR and mb magnitudes are approximately equivalent (Assumpção et al. 2022). Although calculated differently for each earthquake (as indicated by camp "tm"), it can be considered that the catalog magnitudes are homogenized for the magnitude mb|mR.

 * tm: is the magnitude type code. Its values can be:
   * -1 : no magnitude information is available. It just means that the earthquake was felt in someplace.
   *  0 : Richter mb magnitude (teleseismic P-wave)
   *  1 : Richter mR magnitude (P-wave regional magnitude, Assumpção, 1983)
   *  2 : average between mb and mR
   *  3 : Richter magnitude (mb/mR) obtained from affected area:

   ```
   mb = 1.63 + 0.60*log(Area-II)
   mb = 2.29 + 0.55*log(Area-IV)    (Berrocal et al., 1984)

   or

   mb = 2.44  - 0.015*log(Area-II) + 0.092*[log(Area-II)]²  (Assumpção et al., 2014)

   where, Area-II = total area that the earthquake was felt, and, Area-IV = area with intensities >= IV MM.
   ```
   
   * 4 : Magnitude inferred from the maximum reported intensity when there is no affected area.

   ```
   mb = 1.21  +  0.45 * Io	(shallow earthquake felt at the epicenter only)
   ```
   
   * 5 : Magnitude indirectly inferred. It can be ML, or inferred from microseismic information. 
 
 * CAT: Category of the earthquake. Valid options are:
   * A: historic earthquake with enough information to build maps and determine the epicenter 
   * B: historic earthquake with information that allows estimating the total area affected and some intensities.
   * C: historic event with right information of its occurrence but without information about affected area or intensities.
   * D: Wrong event (date or location wrong), doubtful.
   * R: Repeated event, related to other earthquake in list (with wrong date from the initial information)
   * E: Andes earthquake with recorded effects in Brazil
   * I: Instrumental earthquake, detected by seismographic stations
 * Io: maximum intensity at the epicenter in the Modified-Mercalli scale (MM).
 * Af: Affected area in 10³km² = Area-II
 * Localidade/localities: closest city to the epicenter.
 * (source)_comment: Main sources of information for the epicenter and magnitude. Other related comments.

## Main Abbreviations

 * NEIC = National Earthquake Information Center,  U.S. Geological Survey (USGS)
 * ISC = International Seismological Centre, UK
 * UnB, UFRN, USP: Universidades de Brasília, Rio Grande do Norte, e São Paulo
 * RSBR = Rede Sismográfica Brasileira
 * INPRES = Instituto de Prevención Sísmica, Argentina
 * CPRM = Serviço Geológico do Brasil
 * earthquakes without source or comment information corresponds to events derived from Berrocal et al.(1984)

## References

 * Assumpção, M., 1983. A regional magnitude scale for Brazil. Bull. Seism. Soc. Am., 73, 237-246.

 * Assumpção, M., J. Ferreira, L. Barros, F.H. Bezerra, G.S. França, J.R. Barbosa, E. Menezes, L.C. Ribotta, M. Pirchiner, A. Nascimento, J.C. Dourado, 2014. Intraplate Seismicity in Brazil. In Intraplate Earthquakes, chapter 3, ed. P. Talwani, Cambridge U.P., ISBN 978-1-107-04038-0.

 * Berrocal, J., M. Assumpção, R. Antezana, C.M. Dias Neto, R. Ortega, H. França & J. Veloso, 1984. Sismicidade do Brasil. Editado por IAG-USP/CNEN, São Paulo, 320 pp.

 * Bianchi, M.B, M. Assumpção, M.P. Rocha, J.M. Carvalho, P.A. Azevedo, S.L. Fontes, F.L. Dias, J.M. Ferreira, A.F. Nascimento, M.V. Ferreira, and I.S.L. Costa, 2018. The Brazilian Seismographic Network (RSBR): Improving Seismic Monitoring in Brazil. Seism. Res. Lett., 89(2A), 452-457, doi: 10.1785/0220170227 
 
