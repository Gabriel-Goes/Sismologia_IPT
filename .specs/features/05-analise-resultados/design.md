# Design: 05-analise-resultados

## Notebook Layout
1. Carregar base local consolidada.
2. Limpar/normalizar campos de predicao.
3. Gerar estatisticas resumo.
4. Plotar graficos de distribuicao e mapa.
5. Exportar figuras e tabelas para `outputs/`.

## Data Access Pattern
- Ler apenas artefatos persistidos por evento.
- Evitar chamadas de rede nesta etapa.

## Outputs
- `outputs/tables/*.csv`
- `outputs/figures/*.png`

## Implementation Style
- Um ou mais notebooks.
- Sem dependencia de scripts bash para leitura da analise.
