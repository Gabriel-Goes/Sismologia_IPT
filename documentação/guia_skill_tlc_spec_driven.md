# Guia de uso da skill `tlc-spec-driven` no Codex + Neovim

Este guia descreve como usar o repositório `tech-leads-club/agent-skills` no contexto deste projeto para apoiar a refatoração com documentação rastreável.

## 1) Objetivo no projeto

Usar a skill para conduzir a refatoração em fases documentadas:

1. mapear estado atual do código;
2. especificar cada frente de refatoração;
3. desenhar solução antes de codar;
4. quebrar em tarefas atômicas;
5. implementar e validar com critérios claros.

Isso gera histórico técnico em arquivos versionáveis para apresentação acadêmica.

## 2) Onde a skill fica no Codex

No ambiente Codex, a skill do agente fica em:

- global: `~/.codex/skills/`
- local (opcional por projeto): `.codex/skills/`

No nosso caso, a skill está instalada em:

- `~/.codex/skills/tlc-spec-driven/SKILL.md`

## 3) Instalação e manutenção

Comandos úteis do CLI `@tech-leads-club/agent-skills`:

```bash
# instalar skill especifica para Codex (global)
npx @tech-leads-club/agent-skills install -s tlc-spec-driven -a codex -g

# listar skills disponiveis
npx @tech-leads-club/agent-skills list

# atualizar skill instalada
npx @tech-leads-club/agent-skills update -s tlc-spec-driven

# limpar cache do catalogo
npx @tech-leads-club/agent-skills cache --clear
```

## 4) Evitar erro de "invalid SKILL.md"

Se aparecer `skipped loading ... invalid SKILL.md`:

1. validar front matter YAML do `SKILL.md`;
2. garantir campos `name` e `description` validos;
3. em caso de `:` no texto de `description`, usar aspas;
4. reiniciar o Codex para recarregar skills.

## 5) Fluxo recomendado para este repositório

A skill cria e usa a pasta `.specs/`:

```text
.specs/
├── project/
│   ├── PROJECT.md
│   ├── ROADMAP.md
│   └── STATE.md
├── codebase/
│   ├── STACK.md
│   ├── ARCHITECTURE.md
│   ├── CONVENTIONS.md
│   ├── STRUCTURE.md
│   ├── TESTING.md
│   └── INTEGRATIONS.md
└── features/
    └── [feature]/
        ├── spec.md
        ├── design.md
        └── tasks.md
```

Aplicacao direta ao `ClassificadorSismologico`:

1. "Map codebase"
2. "Initialize project"
3. "Create roadmap"
4. Para cada frente de refatoração: "Specify feature ...", "Design feature ...", "Break into tasks"
5. Implementar tarefa a tarefa: "Implement T1", "Validate"
6. Ao encerrar sessão: "Pause work"
7. Ao voltar: "Resume work"

## 6) Rotina no Neovim (pratica)

1. Abrir o projeto no Neovim.
2. Abrir terminal interno (`:terminal`) no diretório do projeto.
3. Rodar o Codex na raiz do repositório.
4. Conduzir a sessão usando os gatilhos da skill em linguagem natural.
5. Versionar `.specs/` e `documentação/` junto com os commits.

## 7) Integracao com a pasta `documentação/`

Regra sugerida para rastreabilidade com professores:

1. `.specs/` = documentação operacional da engenharia (estado, decisão, tarefas);
2. `documentação/` = narrativa acadêmica consolidada.

Sugestão de espelhamento:

- `.specs/codebase/ARCHITECTURE.md` -> `documentação/estado_atual_sistema.md`
- `.specs/project/ROADMAP.md` -> `documentação/plano_refatoracao.md`
- `.specs/features/*/tasks.md` -> `documentação/diario_refatoracao.md`

## 8) Primeiro ciclo sugerido (sem alterar lógica de negócio)

Feature alvo:

- `refatorar-pipeline-shell`

Objetivo:

- documentar contratos de entrada/saida do `fluxo_sismo.sh` e separar responsabilidades por etapa, sem mudar resultado científico.

Sequência de prompts:

1. "Specify feature refatorar-pipeline-shell focando em contratos de I/O e observabilidade"
2. "Design feature refatorar-pipeline-shell priorizando reaproveitamento de codigo atual"
3. "Break into tasks with atomic changes and verification commands"

## 9) Referencias

- https://github.com/tech-leads-club/agent-skills
- https://github.com/tech-leads-club/agent-skills/tree/main/packages/skills-catalog/skills/(development)/tlc-spec-driven
