# Concerns

## High Risk Areas

### 1. Contratos implícitos entre etapas

- `event.json` e o CSV de download funcionam como API interna do pipeline.
- Nao ha schema formal nem cobertura automatizada para esses contratos.

### 2. Acoplamento por naming e layout de arquivos

- descoberta de triplets, gates e inferencia dependem do nome e da localizacao dos `.mseed`.
- a convivencia entre naming legado e naming novo aumenta a superficie de erro.

### 3. Dependencia forte de ambiente e rede

- execucao real depende de endpoint FDSN acessivel, ambiente Python correto e fonte geografica valida.
- varias falhas so aparecem em runtime operacional.

### 4. Ausencia de suite pequena automatizada

- nao existem fixtures pequenas versionadas para validar refactors rapidamente.
- a verificacao atual custa caro porque depende de dados reais e artefatos de lote.

### 5. Mistura de baseline vivo com historico

- `docs/legacy_snapshot/`, `docs/site/`, `scripts/legacy/` e `third_party/rnc_legacy/` convivem com o codigo ativo.
- sem disciplina, fica facil tomar snapshot historico como comportamento atual.

### 6. Repositorio mistura codigo e artefatos pesados

- o repo concentra codigo, modelo `.h5`, catalogos, notebooks e memoria operacional.
- isso ajuda auditabilidade, mas piora clareza sobre o que e fonte, dado e saida.

## Medium Risk Areas

### 1. `sys.path` manual nos scripts

- varios runners alteram `sys.path` para importar `src/`.
- isso e pragmatico, mas fragiliza empacotamento e execucao fora do layout esperado.

### 2. Parsing defensivo espalhado

- o uso intenso de `_safe_*` e `try/except` reduz quebras com dados heterogeneos.
- o custo e menor observabilidade e mais dificuldade para distinguir dado ruim de bug real.

### 3. Conhecimento operacional distribuido

- parte do baseline esta no codigo, parte em `README.md`, parte em `docs/` e parte em `.specs/`.
- se isso nao for mantido junto, a documentacao deriva rapidamente.
