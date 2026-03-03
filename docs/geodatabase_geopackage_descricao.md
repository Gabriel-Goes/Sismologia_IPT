# Descrição do GeoPackage `geodatabase.gpkg`

- Arquivo analisado (seisapp): `/home/gabrielgoes/geodatabase.gpkg`
- Origem de sincronizacao (GeoServer): `/home/database/geodatabase.gpkg`
- Data da análise (UTC): `2026-03-03 01:04:35Z`
- Total de camadas: **23**

## Proveniencia do arquivo

- Origem: copiado via `rsync` do servidor **GeoServer** para o ambiente atual.
- Objetivo no pipeline: fornecer o poligono de MG em modo offline (sem depender de download `geobr`).
- Camada prioritaria para filtro deterministico MG:
  - `ibge_mg_uf_2024` (1 poligono de MG)
- Camada de fallback no mesmo arquivo:
  - `ibge_br_ufs_2024` (27 UFs; filtrar `SIGLA_UF == "MG"`).

## Compreensão Breve

Este GeoPackage reúne dados geocientíficos e cartográficos do Brasil, com foco em litologia, ocorrências minerais, projetos/levantamentos e camadas de referência territorial (incluindo limites administrativos do IBGE).

## Resumo de Tipos de Camada

- `Geometry`: 5 camada(s)
- `LineString`: 3 camada(s)
- `MultiPolygon`: 1 camada(s)
- `Point`: 4 camada(s)
- `PointZ`: 1 camada(s)
- `Polygon`: 9 camada(s)

## Inventário de Camadas

### ocorr_min_cprm

- Tipo geométrico: `Point`
- Número de feições: `34623`
- Número de colunas de atributos: `32`
- Colunas:

```text
ID_AFLORAM, ORIGEM, METODO_GEO, TOPONIMIA, MUNICIPIO, UF, GEOLOGO, DATA_CADAS, TIPO_AFLOR, DESCRICAO, NUMERO_CAM, ROCHAS, SUREG, PROJETO, CODIGO_FOL, FOLHA, ID_OCORREN, PROVINCIA, STATUS_ECO, IMPORTANCI, LOCALIZACA, SITUACAO_M, MOTIVO_INA, SITUACAO_G, MOTIVO_I_1, SUBSTANCIA, ROCHAS_HOS, ROCHAS_ENC, CLASSES_UT, MORFOLOGIA, TEXTURAS, TIPOS_ALTE
```

### aflora

- Tipo geométrico: `Point`
- Número de feições: `331169`
- Número de colunas de atributos: `16`
- Colunas:

```text
ID_AFLORAM, ORIGEM, METODO_GEO, TOPONIMIA, MUNICIPIO, UF, GEOLOGO, DATA_CADAS, TIPO_AFLOR, DESCRICAO, NUMERO_CAM, ROCHAS, SUREG, PROJETO, CODIGO_FOL, FOLHA
```

### am_petro

- Tipo geométrico: `Point`
- Número de feições: `20810`
- Número de colunas de atributos: `29`
- Colunas:

```text
COD_AMOSTR, COD_AFLORA, COD_ROCHA, NUM_CAMPO_, COD_LAMINA, NUM_CAMPO1, NOTAS, PETROGRAFO, PROJETO, BASE_CARTO, TIPO_SECAO, GRAU_INTEM, TAMANHO_AM, COR_RX_FRE, COR_RX_INT, GRANULACAO, GRANULAC_1, GRANULAC_2, SELECIONAM, CONSISTENC, CONTATO, COD_CLASSI, PROTOLITO, ROCHA, LINK, LOCAL_LAMI, LOTE_LAMIN, NUM_LAB_LA, FICHA
```

### proj_cprm

- Tipo geométrico: `Geometry`
- Número de feições: `2127`
- Número de colunas de atributos: `20`
- Colunas:

```text
ID_PROJETO, NOME, ANO_CONCLU, ESCALA, ID_CENTRO_, CENTRO_CUS, ID_CATEGOR, CATEGORIA, TIPO_PRODU, REFERENCIA, FOLHAS, ENTIDADES, TEMAS, LOCAIS, UFS, PUBLICACOE, SUREGS, BASES, SHAPE_AREA, SHAPE_LEN
```

### proj_aerogeof

- Tipo geométrico: `Geometry`
- Número de feições: `296`
- Número de colunas de atributos: `16`
- Colunas:

```text
ID_PROJETO, TITULO, METODOS, ALTURA_VOO, AREA_LEVAN, QUILOMETRA, DIRECAO_LV, DIRECAO_LC, ESPACAMENT, ESPACAME_1, ID_SERIE, SERIE, DISPONIBIL, IMAGENS, SHAPE_AREA, SHAPE_LEN
```

### litologia_1kk

- Tipo geométrico: `Geometry`
- Número de feições: `46715`
- Número de colunas de atributos: `26`
- Colunas:

```text
ID_UNIDADE, SIGLA, HIERARQUIA, NOME, AMBIENTE_T, SUB_AMBIEN, SIGLA_PAI, NOME_PAI, LEGENDA, ESCALA, MAPA, LITOTIPOS, RANGE, IDADE_MIN, IDADE_MAX, EON_MIN, EON_MAX, ERA_MIN, ERA_MAX, SISTEMA_MI, SISTEMA_MA, EPOCA_MIN, EPOCA_MAX, SIGLAS_HIS, SHAPE_AREA, SHAPE_LEN
```

### litologia_250k

- Tipo geométrico: `Polygon`
- Número de feições: `18642`
- Número de colunas de atributos: `26`
- Colunas:

```text
ID_UNIDADE, SIGLA, HIERARQUIA, NOME, AMBIENTE_T, SUB_AMBIEN, SIGLA_PAI, NOME_PAI, LEGENDA, ESCALA, MAPA, LITOTIPOS, RANGE, IDADE_MIN, IDADE_MAX, EON_MIN, EON_MAX, ERA_MIN, ERA_MAX, SISTEMA_MI, SISTEMA_MA, EPOCA_MIN, EPOCA_MAX, SIGLAS_HIS, SHAPE_AREA, SHAPE_LEN
```

### litologia_100k

- Tipo geométrico: `Geometry`
- Número de feições: `59268`
- Número de colunas de atributos: `26`
- Colunas:

```text
ID_UNIDADE, SIGLA, HIERARQUIA, NOME, AMBIENTE_T, SUB_AMBIEN, SIGLA_PAI, NOME_PAI, LEGENDA, ESCALA, MAPA, LITOTIPOS, RANGE, IDADE_MIN, IDADE_MAX, EON_MIN, EON_MAX, ERA_MIN, ERA_MAX, SISTEMA_MI, SISTEMA_MA, EPOCA_MIN, EPOCA_MAX, SIGLAS_HIS, SHAPE_AREA, SHAPE_LEN
```

### litologia_50k

- Tipo geométrico: `Polygon`
- Número de feições: `2796`
- Número de colunas de atributos: `26`
- Colunas:

```text
ID_UNIDADE, SIGLA, HIERARQUIA, NOME, AMBIENTE_T, SUB_AMBIEN, SIGLA_PAI, NOME_PAI, LEGENDA, ESCALA, MAPA, LITOTIPOS, RANGE, IDADE_MIN, IDADE_MAX, EON_MIN, EON_MAX, ERA_MIN, ERA_MAX, SISTEMA_MI, SISTEMA_MA, EPOCA_MIN, EPOCA_MAX, SIGLAS_HIS, SHAPE_AREA, SHAPE_LEN
```

### socorro_250k

- Tipo geométrico: `Geometry`
- Número de feições: `217`
- Número de colunas de atributos: `2`
- Colunas:

```text
id, SIGLA
```

### mc_1kk

- Tipo geométrico: `Polygon`
- Número de feições: `49`
- Número de colunas de atributos: `2`
- Colunas:

```text
id_folha, EPSG
```

### mc_50k

- Tipo geométrico: `Polygon`
- Número de feições: `11805`
- Número de colunas de atributos: `2`
- Colunas:

```text
id_folha, EPSG
```

### mc_100k

- Tipo geométrico: `Polygon`
- Número de feições: `3056`
- Número de colunas de atributos: `2`
- Colunas:

```text
id_folha, EPSG
```

### mc_25k

- Tipo geométrico: `Polygon`
- Número de feições: `46365`
- Número de colunas de atributos: `2`
- Colunas:

```text
id_folha, EPSG
```

### mc_250k

- Tipo geométrico: `Polygon`
- Número de feições: `560`
- Número de colunas de atributos: `3`
- Colunas:

```text
id_folha, EPSG, SIGLA
```

### perfis

- Tipo geométrico: `LineString`
- Número de feições: `1`
- Número de colunas de atributos: `1`
- Colunas:

```text
MSH
```

### afloramentos2025

- Tipo geométrico: `PointZ`
- Número de feições: `62`
- Número de colunas de atributos: `2`
- Colunas:

```text
Name, Description
```

### Pontos_GMG

- Tipo geométrico: `Point`
- Número de feições: `88`
- Número de colunas de atributos: `11`
- Colunas:

```text
field_1, field_2, field_3, field_4, field_5, field_6, field_7, field_8, field_9, field_10, field_12
```

### Estruturas-PNM

- Tipo geométrico: `LineString`
- Número de feições: `1`
- Número de colunas de atributos: `1`
- Colunas:

```text
Falhas
```

### perfil_acai

- Tipo geométrico: `LineString`
- Número de feições: `1`
- Número de colunas de atributos: `1`
- Colunas:

```text
azimute
```

### ibge_mg_uf_2024

- Tipo geométrico: `Polygon`
- Número de feições: `1`
- Número de colunas de atributos: `7`
- Colunas:

```text
CD_UF, NM_UF, SIGLA_UF, CD_REGIA, NM_REGIA, SIGLA_RG, AREA_KM2
```

### ibge_mg_municipios_2024

- Tipo geométrico: `Polygon`
- Número de feições: `853`
- Número de colunas de atributos: `15`
- Colunas:

```text
CD_MUN, NM_MUN, CD_RGI, NM_RGI, CD_RGINT, NM_RGINT, CD_UF, NM_UF, SIGLA_UF, CD_REGIA, NM_REGIA, SIGLA_RG, CD_CONCU, NM_CONCU, AREA_KM2
```

### ibge_br_ufs_2024

- Tipo geométrico: `MultiPolygon`
- Número de feições: `27`
- Número de colunas de atributos: `7`
- Colunas:

```text
CD_UF, NM_UF, SIGLA_UF, CD_REGIA, NM_REGIA, SIGLA_RG, AREA_KM2
```
