# Prompt para iniciar o Codex — RANGOT

Você está em um **checkout novo e isolado, sem `.env` e sem acesso a credenciais**. Configure seu trabalho para **raciocínio no nível mais alto suportado** (`xhigh` neste projeto), mas priorize resultados auditáveis e ações mínimas. Antes de qualquer ação, leia `AGENTS.md`, `docs/AUDITORIA_INICIAL_RANGOT.md` e, quando pertinente, as skills locais `.agents/skills/rangot-auditoria/SKILL.md`, `.agents/skills/rangot-experimentos/SKILL.md`, `.agents/skills/rangot-entrega/SKILL.md`.

## Missão desta primeira sessão: SOMENTE PLANO E AUDITORIA OFFLINE

- Não editar nenhum arquivo do projeto nesta primeira sessão, nem commitar, nem conectar à internet.
- Fazer auditoria detalhada com evidências, confirmando os pontos da auditoria inicial. Pode examinar arquivos não secretos da cópia local, mas **não ler nem procurar arquivos/variáveis de segredo**.
- Reconhecer como contrato inalterável: `scripts/avaliar.py`, `scripts/verificar_entrega.py`, `chatbot/avaliacao.py`; formato `texto,intencao,origem`; grafo com classificadores determinando a rota e pipelines salvos nas duas paths oficiais.
- `dados/treino.csv` e `dados/teste.csv` estão vazios no ZIP; 35 respostas de formulário humano e 132 registros sem origem esclarecida foram enviados ao responsável em arquivos separados. Não simular que estão no repo. **NÃO** usar CSV de origem não confirmada como humano/coletado; **NÃO** acessar dados de teste para otimização. Primeiro propor procedimento de curadoria e congelamento.
- A avaliação padronizada no teste poderá ocorrer UMA vez somente após os modelos/limiar estarem fechados e com autorização expressa. Não executar agora.
- Nenhum teste ou script que chame OpenRouter ou carregue a chave, inclusive testar_llm, gerar_dados_llm, conversar.py ou células de notebook que carreguem `.env`.
- Propor trabalho com 3 algoritmos x 2 representações em dois classificadores, CV estratificada 5-fold, GridSearchCV, curvas, matrizes de confusão, limiar out-of-fold e aprofundamento A1.
- Especificar quais tarefas cabem em branches `feature/*`, commits atômicos sugeridos, testes offline e ordem de PRs para `develop`.
- Preparar plano até 18/11/2026 14h para artigo SBC, vídeo, usos de IA e verificador.

## Resposta esperada

Tabela C1–C11 com status, pontos e evidências; diagnóstico dos dados; riscos de integridade acadêmica; sequência operacional; primeira tarefa pequena proposta (a executar somente com aprovação). Não exibir dados pessoais ou segredos.
