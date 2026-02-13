# PROJECT

## Name
Seismic Event Discriminator (Alpha 0.1.0)

## Vision
Reescrever o fluxo legado de classificacao sismologica com foco em simplicidade,
rastreabilidade cientifica e facilidade de revisao pelos orientadores.

## Stakeholders
- Gabriel (implementacao e operacao diaria)
- Prof. Marcelo Bianchi (direcao tecnica e cientifica)
- Prof. Lucas (revisao academica e validacao de metodo)

## Guiding Principles
1. Notebook-first para explicacao do processo.
2. Script linear em paralelo para reproducibilidade operacional.
3. Etapas 1 e 2 no mesmo processo.
4. Etapa 3 com base local incremental por evento.
5. Evitar complexidade precoce e abstracoes desnecessarias.

## Scope Of This Cycle
1. Catalogo + selecao de eventos em area alvo de MG.
2. Persistencia por evento em arquivos parametricos (`xml|json`).
3. Aquisicao de formas de onda de 60s e consolidacao da base local.
4. Inferencia CNN por evento com estrategia paralelizavel.
5. Analise final em notebooks (graficos e mapas).

## Out Of Scope (for now)
- Refatorar treino completo da CNN legado.
- Otimizacoes avançadas de infraestrutura.
- Mudancas de arquitetura sem necessidade de validacao experimental.
