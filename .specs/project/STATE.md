# STATE

## Last Update
2026-02-12

## Current Branch
`seismic-event-discriminator`

## Confirmed Decisions
1. Etapas 1 e 2 devem ser um processo unico de selecao.
2. Entrada de catalogo deve partir de fonte `QuakeML`/builder (nao tratar como
   "CSV nativo de origem").
3. Etapa 3 deve construir base local incremental por evento:
   - `sismo_xxx.[xml|json]`
   - `sismo_xxx.ms` (mseed)
4. Metadados da etapa 3 devem carregar picks por estacao e abrir espaco para SNR.
5. Etapa 4 deve ser paralelizavel (N eventos independentes).
6. Etapa 5 deve ser notebook-driven para analise final.

## Active Feature Set
- `01-catalogo-selecao`
- `03-base-local-eventos`
- `04-inferencia-cnn-paralela`
- `05-analise-resultados`

## Current Risks
1. Instabilidade de conectividade FDSN/tuneis. **DEVO SOLICITAR VPN IAG E PARAR DE ENTRAR PELA PORTA E ABRIR A JANELA PRA ENTRAR POR ELA MAIS TARDE SEM AVISAR AO BIANCHI E JACKSON**
2. Inconsistencia de formatos de catalogo na origem. **O CATÁLOGO DE ORIGEM SEMPRE VIRÁ EM FORMATO QUAKEML ADQUIRIDO PREFERENCIALMENTE POR FLUXOS AUTOMATIZADOS EM BASH ATRAVÉS DE FDSN**
3. Acoplamento precoce de inferencia antes da base local estar estavel. **O QUE ISTO QUER DIZER?**

## Next Action
Implementar etapa 1+2 com export por evento (`xml|json`) e registrar contrato
de arquivo para etapa 3.
