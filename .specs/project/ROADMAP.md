# ROADMAP

## M0 - Bootstrap cleanroom (done)
- Branch cleanroom criada.
- Snapshot do legado arquivado.
- Estrutura inicial de notebooks e script linear criada.

## M1 - Etapas 1+2: Catalogo e selecao (in progress)
### Goal
Ler catalogo (`QuakeML` ou texto de builder), selecionar eventos alvo e quebrar
em arquivos por evento (`xml|json`) para alimentar a etapa 3.

### Deliverables
- Notebook de selecao (etapas 1+2).
- Export por evento de metadados iniciais.
- Lista de eventos selecionados para aquisicao.

### Verification
- Regras de filtro reproduziveis (regiao, magnitude, profundidade).
- Contagem de eventos antes/depois registrada.

## M2 - Etapa 3: Base local incremental de analise
### Goal
Criar base local por evento com metadados + waveform.

### Deliverables
 **ALGORITMOS DE CELINE HOURCAD SOLICITA ESTRUTURA FIXA. VIDE EXEMPLO ABAIXO:**
#### EXEMPLO DO REPOSITÓRIO DE CELINE HOURCAD
   Dataset
To apply the algorithm, we need a folder architecture:
    - mseed_demo/
        - 2022004T134407/
            - FR_CHLF_2022004T134407.mseed
            - FR_GARF_2022004T134407.mseed
            - FR_GNEF_2022004T134407.mseed
            - FR_VERF_2022004T134407.mseed

#### PROPOSTA DE NOVA ESTRUTURA DE DADOS
**PODEMOS PROPOR ALGO ENTRE O QUE BIANCHI SUGERE E O QUE HOURCAD DEFINE**
    - NDS/
        - YYYYMMDDTHHMMSS/
            - NET_STA_YYYYMMDDTHHMMSS.json **UM PARA CADA EVENTO**
            - NET_STA_YYYYMMDDTHHMMSS.mseed **UM PARA CADA PICK**
        - 2022004T134407/
            - 2022004T134407.json
            - FR_CHLF_2022004T134407.mseed
            - FR_GARF_2022004T134407.mseed
            - FR_GNEF_2022004T134407.mseed
            - FR_VERF_2022004T134407.mseed
**JSON DEVE SER EXPANDÍVEL PARA MAIS INFO COMO RESULTADO DA CNN, SNR, ETC**

### Verification
- Reexecucao nao perde nem duplica eventos ja persistidos.
- Adicao de novos eventos sem reprocessar base completa.

## M3 - Etapa 4: Inferencia CNN paralelizavel
### Goal
Executar inferencia por evento com suporte a paralelismo simples.

### Deliverables
- Script de inferencia por evento.
- Runner de lote paralelo (shell ou python).
- Saida por evento em `prediction.json` ou embutida em `event.json`.  **EMBUTIR EM JSON É ELEGANTE**

### Verification
- Lote de teste executa com resultados consistentes. **LOTE DE TESTES DEVE USAR EVENTOS ALEATÓRIOS DO CATÁLOGO SEMPRE COM 42 COMO SED**
- Escala linear basica ao aumentar workers.

## M4 - Etapa 5: Analise e comunicacao de resultados
### Goal
Consolidar resultados em notebooks para avaliacao cientifica.

### Deliverables
- Notebooks de graficos e mapas.
- Export de tabelas e figuras principais.
- Material pronto para discussao com orientadores.

### Verification
- Pipeline completo reproduzivel em ambiente SEISAPP.
- Resultados
