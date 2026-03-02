# TLC Diretrizes para Jupyter Notebooks

## Objetivo
Padronizar notebooks didaticos no projeto para leitura rapida por professores e revisores, mantendo fidelidade ao fluxo oficial implementado em Python/Bash.

## Principios
- Clareza primeiro: quem le deve entender o que foi feito em poucos minutos.
- Fluxo linear: entrada -> transformacao -> saida.
- Minimo de abstracao: evitar engenharia prematura no notebook.
- Rastreabilidade: deixar claro quais arquivos entram, quais filtros aplicam e quais arquivos saem.

## Regras obrigatorias (versao inicial)
- Nao criar classes.
- Nao criar funcoes.
- Organizar o notebook em celulas sequenciais por etapa.
- Nomear variaveis de forma explicita (ex.: `rows_raw`, `final_rows`, `output_csv`).
- Mostrar contagens e resumo de filtros em texto simples.

## Estrutura recomendada de celulas
1. Titulo e objetivo do notebook.
2. Imports minimos.
3. Configuracao (caminhos e parametros).
4. Leitura dos dados de entrada.
5. Transformacoes/filtros em ordem didatica.
6. Exportacao do resultado.
7. Preview final (amostra curta).

## Quando abstrair (excecao)
Somente introduzir funcao ou classe quando houver repeticao clara que:
- dificulta leitura por excesso de codigo duplicado; e
- traz ganho real de compreensao para quem esta aprendendo.

Se abstrair, justificar em uma celula Markdown antes do codigo.

## Boas praticas de comunicacao
- Cada celula deve ter uma responsabilidade principal.
- Preferir comentarios curtos de "por que" ao inves de comentarios obvios.
- Evitar outputs longos; mostrar apenas o essencial.
- Usar nomes de arquivos e pastas reais do projeto.

## Checklist de revisao antes de compartilhar
- [ ] Notebook roda do inicio ao fim sem editar codigo.
- [ ] Nao ha `class` nem `def` (na versao inicial).
- [ ] Entradas e saidas estao claras para o leitor.
- [ ] Regras de filtro estao explicitas e auditaveis.
- [ ] O resultado final (CSV/figura/tabela) foi gerado e conferido.

## Relacao com o fluxo oficial
O notebook didatico deve explicar o fluxo oficial, nao substituir scripts de producao.
- Scripts em `scripts/` e `src/` continuam sendo a referencia operacional.
- O notebook atua como camada de ensino e auditoria.
