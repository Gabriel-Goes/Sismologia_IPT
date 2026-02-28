# Scripts Legados de Diagnostico

Este diretorio concentra utilitarios historicos de diagnostico e comparacao.
Eles nao fazem parte do fluxo operacional principal do projeto.

Fluxo operacional atual (pre-RNC):
- `scripts/run_real_mg_maglt4_depthlt10.sh`

Scripts legados movidos:
- `run_step02_one.py`: teste live pontual de consulta FDSN para um evento.
- `test_assoc_random100.py`: amostragem aleatoria para avaliacao de associacao.
- `check_no_match_endpoints.py`: rechecagem de `no_match` em endpoints alternativos.
- `check_unb_matches_picks.py`: diagnostico focado em eventos com origem UnB.
- `compare_worker_runs.py`: comparacao de resumos entre execucoes com workers diferentes.
- `keep_tunnel_seisapp_interativo.sh`: loop manual de tunel reverso SSH.
- `summarize_unmatch_agencies.py`: sumario de `no_match` por agencia/fonte SISBRA.

Observacao:
- Esses scripts podem referenciar convencoes antigas de arquivos/saidas.
- Use-os apenas para auditoria e investigacao historica.
