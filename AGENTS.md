# RANGOT / Chatbot RU UFMS — Política obrigatória do Codex

**Objetivo:** maximizar a nota do Trabalho Prático de IA 2026/2 sem violar o contrato, a segurança de credenciais nem a integridade do teste. Entrega interna 18/11/2026 14h, prazo oficial 18/11/2026 23h59.

## P0: segurança (prioridade absoluta)

- **NÃO ler, abrir, buscar, indexar, copiar, imprimir, resumir, fazer hash nem acessar de qualquer forma** `.env`, `.env.*`, tokens, Keychain, secrets de Colab, variáveis de ambiente que possam conter credenciais, arquivos de autenticação, históricos de shell ou pastas pessoais externas. **Não executar comandos que listam variáveis de ambiente** (`env`, `printenv`, `set`, dumps de processo).
- **Não executar** `scripts/testar_llm.py`, `scripts/gerar_dados_llm.py`, `scripts/conversar.py`, o bloco de LLM no notebook, ou outras chamadas ao OpenRouter. Trabalhar totalmente offline com a opção de fallback do chatbot. **Não modificar a lógica de segredos em `chatbot/llm.py`** para contornar a proteção.
- Não executar buscas globais indiscriminadas ou comandos que exijam permissão fora deste repositório. Não solicitar rede, privilégios ampliados, `danger-full-access` ou autenticação.
- Se achar que uma operação pode ler qualquer credencial, **não a execute**: escreva instruções sem segredos para o humano realizar em ambiente **diferente**. Não tente testar/validar a chave.
- Este AGENTS.md **não é uma barreira técnica**. O operador é responsável por executar o Codex em checkout de código sem segredos e com sandbox restrito. Nunca adicione `.env` a esta cópia.
- Antes de sugerir o `.zip` final, verifique apenas **nomes de arquivos** suspeitos no commit e faça a checagem oficial em ambiente SEM `.env`.

## P0: contrato inegociável do professor

- Não alterar `scripts/avaliar.py`, `scripts/verificar_entrega.py` ou `chatbot/avaliacao.py`, **nem para corrigir uma falha**. Reportar problemas de execução, não contornar o avaliador.
- Preservar chaves/estrutura de `grupo.yaml`, CSV `texto,intencao,origem`, `modelos/escopo.joblib`, `modelos/tema.joblib`, API de `construir_grafo(config, clf_escopo, clf_tema)` e estado final com `rota` e `resposta`.
- Classificadores, e **não LLM**, determinam as rotas; a avaliação oficial roda sem LLM.
- O teste do próprio grupo é **100% humano/coletado**. Não produzir frases de teste com IA; não misturar teste com treino; não ajustar modelo/limiar a partir de teste, nem rodar avaliação final antes de autorização explícita.
- Origem: não rotular como `humano` qualquer texto sintético ou de proveniência incerta; solicitar comprovação. O CSV de 132 linhas enviado pelo responsável tem origem ainda não esclarecida; tratá-lo como **não aprovado para treino humano/teste** até esclarecer.
- Toda seleção de algoritmos, vetorizadores, hiperparâmetros e limiar usa exclusivamente treino + CV estratificada. Preferir F1 macro; reportar média e desvio por 5 folds, análise de erros e evitar leakage ao construir Pipeline.
- **Não falsificar métricas, prints, testes, referências, documentação, contribuição humana nem execução de notebook.** Todo uso de IA (Codex, ChatGPT, geração de frases, redação) deve ser registrado em `USO_DE_IA.md`, artigo e vídeo.

## Skills locais: quando usar

- **Antes de qualquer mudança** ou ao receber CSV/repositório: abrir `.agents/skills/rangot-auditoria/SKILL.md`.
- **Antes de experimentos, notebooks ou modelos**: abrir `.agents/skills/rangot-experimentos/SKILL.md`.
- **Antes da versão final ou de preparar o ZIP**: abrir `.agents/skills/rangot-entrega/SKILL.md`.
- Não instalar skills externas nem rodar scripts de terceiros sem revisão e consentimento do responsável.

## Gitflow e mudanças

- Base principal `develop`; trabalho em `feature/*`, commits pequenos, semânticos, rastreáveis (Conventional Commits), com PR revisado para `develop`.
- Não atuar em `main`/`develop` diretamente. Cada commit deve ter um único propósito. Evitar `git add -A`, preferir `git add` de caminhos específicos, conferir `git diff --cached --name-only` e `git diff --cached --check` antes de commitar.
- Commits são permitidos **somente após o responsável autorizar a implementação e revisar o escopo**; push/PR/merge/rebase/reset/delete apenas com autorização específica. Não assinar mensagens de commit como IA.
- Nunca adicionar/commitar `.env`, credenciais, resultados falsos, artefatos do ambiente ou diretórios ocultos desconhecidos.
- A cada tarefa: explicar objetivo, modificações, evidências, testes offline e riscos. Não causar alterações fora do escopo.

## Processo priorizado

1. Auditoria de arquivos **não secretos**. Inventariar C1–C11 e requisitos obrigatórios; não inferir conclusão por documentação antiga.
2. Conjuntos de dados: elaborar plano de rotulagem humana e separar teste congelado de treinamento; contar duplicatas, vazamento e mínimos de cada classe. O CSV de Forms tem 35 formulários, mas exige revisão humana de rótulos.
3. Treino: ao menos 50 por intenção, 100 chitchat, 150 fora_dominio, 20% humano/coletado; teste: 15 por intenção, 30 chitchat, 40 fora_dominio, 100% humano/coletado.
4. Escopo e tema: 3 algoritmos × 2 TF-IDFs em cada estágio, 5 folds, GridSearchCV, curva de validação, matrizes, falso aceite/recusa, erros por intenção e origem.
5. Limiar: ajustar exclusivamente com probabilidades out-of-fold dos dados de treino, quantificando acertos, erros e esclarecimentos.
6. Aprofundamento A1 inicialmente preferido: classificador único vs cascata, com comparação controlada e mesmo protocolo de CV.
7. Salvar pipelines com a função oficial; validar contrato e conversa offline (sem OpenRouter). Execução do LLM deve ocorrer manualmente em ambiente separado.
8. Avaliação final **uma única vez, depois do congelamento dos modelos** e somente mediante autorização; artigo SBC até 10 páginas, vídeo até 10 min, contribuições e declaração de IA; ZIP com `git archive`.
9. `scripts/verificar_entrega.py` deve terminar sem erros em **cópia sem segredos**; não reescrever o script para passar no verificador.

## Comunicação

Responda em português claro com: STATUS, EVIDÊNCIAS, PRÓXIMAS TAREFAS, ARQUIVOS A ALTERAR, TESTES OFFLINE, RISCOS E APROVAÇÕES. Pergunte primeiro somente se a decisão realmente bloquear a execução. Não reproduza dados pessoais ou segredos nos relatórios.
