# Missão 11A — correções documentais e preparação para entrega

Registro de 19/11/2026. Leitura e implementação assistidas pelo Codex, com
confirmações atribuídas aos responsáveis e limitações de evidência explicitadas.

## Estado inicial, autoridade e escopo

- Diretório: checkout `rangot-codex` do RANGOT.
- Branch: `feature/rag-openrouter-rangot`; Git inicialmente limpo.
- HEAD confirmado: `1899eb83dc37484c111e9ca89ee4f6beffd61450`, igual à referência.
- Enunciado lido integralmente: 29 páginas, “Um chatbot que sabe quando (e o que)
  responder”, Prof. Bruno M. Nogueira, FACOM/UFMS 2026/2.
- SHA-256: `004e80a57f9793fbbb51d5394ae79206fde47c3cb77e9e8a0db7c979deee6ed6`.
- Consultados `AGENTS.md`, skills de auditoria/entrega/experimentos e contratos
  compartilhados. As decisões internas antigas da seção 10 do contrato refletem
  sua missão de redação; não substituem a autorização específica da 11A.

Esta missão não executou treinamento, GridSearch, calibração, otimização de
limiar, notebook, API, avaliação oficial ou verificador. Não fez commit, staging,
push, merge, rebase ou reset, nem acessou segredos. Os comandos de reprodução e
fechamento no README são instruções futuras para ambiente/autorização próprios.

## Correções realizadas

| Arquivo | Alteração |
|---|---|
| `grupo.yaml` | Somente comentário inicial: substituído marcador TODO por descrição do RANGOT; valores YAML iguais aos iniciais. |
| `README.md` | Documentação específica: seis intenções, classificadores, CV, resultados reais, A1, limiar, RAG, instalação, execução, reprodução e pendências. |
| `LINKS.txt` | Exatamente duas linhas: vídeo vazio e repositório informado, sem Markdown ou URL inventada. |
| `USO_DE_IA.md` | Revisão retrospectiva dos dados, auditorias relatadas, Claude Code esclarecido, ressalva High/xhigh, operadores e assistência 11A. |
| `dados/prompts_llm.md` | Separação entre aprovação humana confirmada e proveniência incompleta das 158 frases; histórico de geração preservado. |
| `docs/PROTOCOLO_DADOS.md` | Confirmação posterior dos dados utilizados e vínculo de G07G:003, sem alterar decisões/CSV ou snapshots privados. |
| `docs/EXPERIMENTOS_CLASSIFICADORES.md` | Ressalva inicial: bloqueio da sessão de implementação é histórico; artefatos executados existem, mas reprodução integral é pendência. |
| `docs/APROFUNDAMENTO_A1.md` | Ressalva sobre execução histórica, relato de falha integral e distinção entre integração fictícia e testes humanos. |
| `docs/MISSAO_11A.md` | Este relatório, validações e plano de fechamento. |

Os dois últimos documentos de metodologia receberam apenas notas; números e
protocolo científicos foram preservados. Nenhum documento do corpus ativo foi
alterado. Não se corrigiu o verificador nem se afirmou que ele passou.

## Revisão humana: confirmação e cronologia

Cleiton Pinheiro Rodrigues reiterou expressamente em **19/11/2026** ter feito as
revisões de dados solicitadas pelo Codex e apresentadas a ele durante a construção
dos conjuntos: dados humanos utilizados, decisões de curadoria, as 124 frases
07E e a selecionada G07G:003. Essa é evidência declaratória do responsável,
posterior à curadoria delegada e seleção técnica; a data original de cada
revisão não foi informada e não foi inventada.

**G07G:003:** “Dá ruim se alguém colocar música numa caixinha de som enquanto
tá almoçando no RU?”. Origem de geração IA; seleção assistida pelo Codex;
incorporação como `regras_uso,llm`; revisão humana posterior confirmada.
O texto coincide entre a terceira candidata (linha 4 com cabeçalho), o manifesto
07G e o último exemplo de treinamento (registro 550, linha lógica 551 com cabeçalho).
SHA-256 do texto: `857013762edbb357fd633c4a66a0a464902fdd8aae2703b259becdbc2b098120`.

Não houve mudança de texto, origem, intenção ou posição, nem nova solicitação
de aprovação. A confirmação não transforma geração em humana e não aprova
automaticamente as 13 pendências excluídas, G07D:013 ou candidatas não utilizadas.
Os manifestos privados mantêm o estado histórico `nao_confirmada` daquela etapa;
o registro posterior está em USO/protocolo. A confirmação não foi estendida
automaticamente a código, notebook, documentos ou análises não apresentados.

## Proveniência: o que se sabe e o que falta

Os IDs do manifesto 07G correspondem a 550 registros: 268 humanos, 157 `S...`,
124 `G07D:...` e uma `G07G:003`. O manifesto 07C já contém os 157 exemplos da
fonte original. Assim, 282 LLM = 157 + 124 + 1; aprovação humana desses
exemplos e identificação de seu gerador são questões diferentes.

| Parte | Comprovado nos arquivos | Declaração do responsável | Ainda ausente |
|---|---|---|---|
| 157 da fonte original | IDs/células e contagens em manifestos 07B/07C/07G, fonte sintética e seleção persistidas | Origem IA e revisão dos exemplos utilizados | Ferramenta/modelo da geração, prompts integrais, datas/condições originais e autoria operacional do lote |
| 124 do complemento 07D | Registro da geração, prompt e instruções transcritos; lote de 125 com G07D:013 excluída | ChatGPT/GPT-6 High, geração separada e revisão das 124 incorporadas | Build/amostragem e comprovação técnica de isolamento físico/virtual |
| G07G:003 | Fonte de cinco candidatas, decisão por ID, texto e hash iguais no treino | Origem IA e revisão humana posterior | Ferramenta/modelo/prompt e condições originais da geração das cinco |

A base original tem 132 linhas com múltiplas respostas; isso não equivale a
132 frases. Seu SHA-256 local é
`87dd6717fb62280cda1cdb7fbb29c8b5730153cdaf3ccf49448998d73a0f44e8`.
O CSV preserva conteúdo e os manifestos rastreiam seleção, mas não substituem
um registro de geração. Faltam os prompts originais que produziram a base
multirresposta e os que produziram as cinco candidatas 07G; prompts de
curadoria ou instruções para gerações futuras não são esses prompts históricos.

Não se atribuiu essa geração a Cleiton/ChatGPT por associação com o uso confirmado
da ferramenta em outras etapas. Não se reconstruiu prompt fictício nem se afirmou
impossibilidade definitiva de recuperação: os registros não foram recuperados
entre os materiais disponíveis examinados nesta missão.

## Ferramentas, operadores e divergência High/xhigh

- Cleiton: ChatGPT web/GPT-6 High e Codex/GPT-6.1-Sol High conforme confirmação
  retrospectiva para o desenvolvimento; testes manuais com OpenRouter/GPT-6 Luna
  e em modo sem LLM confirmados pelo responsável.
- Jonathan: Claude no aplicativo Claude/claude.ai, Opus 5.5 conforme histórico.
  Em 19/11/2026, confirmou **não utilizar Claude Code**. A linha preventiva
  `CLAUDE.md` no `.gitignore`, linha 19, não comprova uso.
- Gabriel e Felippe: usos ou ausência de IA aguardam confirmação individual;
  não foi atribuída ferramenta nem declarada ausência de uso.
- OpenRouter/GPT-6 Luna é o LLM do chatbot, não ferramenta de desenvolvimento
  presumida para os lotes antigos.

| Evidência sobre Codex | O que permite afirmar | Limite |
|---|---|---|
| `.codex/config.toml`, linha 3: `model_reasoning_effort = "xhigh"` | Configuração persistida observada | Não comprova o modo efetivo de cada sessão |
| Declaração retrospectiva de Cleiton: High | Configuração de uso informada pelo próprio responsável | Não há captura/telemetria independente por sessão disponibilizada |
| Configuração exibida/ativa em cada sessão | Não foi disponibilizado registro independente | Divergência permanece como ressalva, sem escolher arbitrariamente uma versão |

O arquivo `.codex/config.toml` não foi alterado. Não se procurou evidência em
variáveis de credenciais, histórico de shell, configurações pessoais externas
ou outros segredos.

## Duas auditorias independentes

Os resumos fornecidos no pedido 11A foram examinados e registrados nas entradas
31/32 de USO_DE_IA.md. Relatórios integrais, prompt original, traceback e valor
da estimativa condicional não foram fornecidos/localizados nos caminhos de
documentação examinados; foi solicitada indicação dos arquivos ao responsável.
Sem esses materiais, a fonte é explicitamente o relato recebido:

- **Codex, Cleiton:** auditoria técnica/acadêmica somente leitura do commit de
  referência, PDF de 29 páginas, contratos, dados, modelos, notebook, resultados
  e RAG, achados P0–P3 e estimativa condicional. Sem modificação/avaliação oficial
  segundo o resumo. Não se inventaram valores de nota ou lista adicional de achados.
- **Claude, Jonathan:** mesmo commit, inspeção de enunciado/artefatos, reprodução
  ou verificação experimental em ambiente isolado conforme relato do auditor,
  falha de reprodução integral e pendências de documentação/entrega. Sem alteração
  no repositório ou avaliação oficial segundo o relato. Não foi Claude Code.

A implementação 11A não é uma repetição independente desses experimentos e não
declara todos os achados corrigidos. Saídas existentes do notebook não demonstram
execução integral por kernel limpo. A inspeção estática mostrou células que
refazem buscas/treino e gravam modelos, motivo adicional para isolar a reprodução
e não executá-la neste checkout congelado. A causa exata da falha relatada
continua sem comprovação técnica nesta missão.

## Resultados históricos, atuais, simulados e humanos

| Evidência | Natureza | Leitura correta |
|---|---|---|
| `resultados/classificadores_08/` | Treino/CV interna e OOF pós-seleção históricos | Escopo F1 0,922867, intenção 0,919959; viés de seleção/famílias não agrupadas; não é teste final |
| `resultados/aprofundamento_09/` | A1/CV e integração fictícia sem LLM | F1 médio cascata 0,882105 e único 0,885115; modelos 08 mantidos; não é nota C7 |
| `integracao_ficticios.csv` da 09 | Dez perguntas fictícias, modelos reais e respostas fixas históricas | Erros de cardápio/pagamento para valores, esclarecimento em cadastro e ambiguidade/múltiplas intenções foram preservados |
| `resultados/rag_10_offline.json` | Snapshot de oito documentos/77 trechos, mocks de LLM e cenários controlados/reais | Campo `llm` significa chamada simulada nesse artefato, sem API real |
| Corpus após 10B | Dez documentos e 83 trechos atuais | Ampliação documental não é retreino ou nova medida de classificação |
| Testes manuais de Cleiton | Execução humana com API e sem LLM, declarada | Sem transcrição completa/data de cada teste/tokens para auditoria; não equivalem a avaliação padronizada |
| Avaliação oficial | Não executada nesta missão | Não há métricas oficiais novas nem nota garantida |

Na 10, a pergunta fictícia de menu datado caiu em `horarios`, Pix pediu
esclarecimento e a vaga “Como uso isso?” caiu em cadastro. Na 09 há perguntas
diferentes: não se infere melhora/piora de modelos por comparação direta desses
roteiros. Respostas fixas da 09 antecedem as revisões documentais da 10/10B.
Não foram sobrescritas para parecer atuais. A pergunta genérica sobre documentos
para subsídio, sem identificar o RU, continua semanticamente ambígua e não é
falso negativo confirmado apenas por receber uma recusa.

## Validações offline

Executado: `.venv/bin/python -B -m unittest discover -s tests`.
Resultado: **149 testes aprovados, sem ignorados**, sem alterar testes.
Conferências estáticas/comparações de integridade complementam a suíte;
nenhum verificador oficial foi executado. Os resultados finais dessas
conferências são registrados abaixo após sua conclusão.

### Integridade e contratos confirmados

- Comparação inicial/final: **44 arquivos com SHA-256 idêntico**, incluindo
  datasets, modelos/versões, scripts oficiais, código, notebook e artefatos 08/09
  e snapshot RAG 10. Nenhum desses arquivos foi modificado.
- YAML válido e dicionário carregado idêntico ao de HEAD: somente o comentário
  inicial mudou. Palavra `TODO` ausente no arquivo, seis intenções e limiar
  **0,60** preservados; persona, respostas, grupo e modelo LLM iguais.
- Assinatura AST do grafo e bytes de seu código preservados; suíte cobre
  contratos offline. Nenhuma alteração de rota, classe ou biblioteca.
- G07G:003 tem texto/hash/origem/intenção/posição preservados; nenhuma revisão
  foi reimportada. O teste não foi aberto para interpretação ou avaliação.
- `LINKS.txt` confere exatamente com o conteúdo solicitado. Links locais
  verificados. Staging vazio, HEAD/branch iguais ao início, nove arquivos de
  escopo documental/configuração como únicas alterações.
- Nenhum arquivo secreto novo foi rastreado: não houve staging e os nomes
  alterados/criados foram conferidos por lista explícita, sem leitura de segredos.
- `git diff --check` sem erros; arquivo novo também conferido quanto a espaços.

| Arquivo | SHA-256 preservado |
|---|---|
| `dados/treino.csv` | `fc260493bf144e3a6b5ecac2e2e7064f31b53dda597948cfc8e689fea5b665f5` |
| `dados/teste.csv` | `fa760e167d565a9a3e5bd015465c4ec945f7855e0bd78b5542dc561e21ea9b81` |
| `modelos/escopo.joblib` | `cd33ffcb0cbdc2727e2fb7bdb3d12d2098d9d4961e5be028152832ff8134b12e` |
| `modelos/tema.joblib` | `a674cbc37d89aba7130d65361584b08411840eecb8224d003ac15d83580da8ce` |
| `modelos/versoes.json` | `911d4fe6380721a7c1779e1dcaa0a6fe6e2bd2fcc38bded00bdd6b6f944a968f` |
| `scripts/avaliar.py` | `5ee29c8f0b7aacc146706948dd26803600ad9da8b683a3d22a1a9ab64f0ddda2` |
| `scripts/verificar_entrega.py` | `42bda3906b0f295603162d4d2320191327cc4f472b59ac3fd2bf874fc1feacec` |
| `chatbot/avaliacao.py` | `4c40ed6d4ee3cdabf54a4b387b8085faea6a76ec93f8b7a104a29d04facb6035` |
| `notebooks/01_trabalho_grupo.ipynb` | `89963d7bd0fae1ce22f02f81e0a61bf42c2a183f89caa2a90f340a6a0ba0c3e1` |

A suíte passou nesta missão, mas isso não comprova reprodução integral do
notebook nem sucesso do verificador oficial. O controle remove o marcador
potencialmente bloqueante do comentário, sem afirmar que todos os bloqueios
de entrega foram resolvidos.

## Pendências para a Missão 11B e entrega

1. Obter relatórios integrais/traceback das auditorias, caso disponíveis, e
   diagnosticar a reprodução completa em cópia isolada e ambiente com versões
   registradas, mediante autorização específica. Não retreinar/regravar neste
   checkout nem iniciar a 11B automaticamente.
2. Recuperar evidências originais de geração dos 158 exemplos, se disponíveis;
   caso contrário, declarar a limitação, sem prompts reconstruídos. Não pedir
   nova aprovação das 124 frases ou de G07G:003.
3. Documentar a divergência High/xhigh sem inferir modo de sessões e obter
   confirmação individual dos usos de IA por Gabriel/Felippe.
4. Revisar cientificamente os resultados e limites; preservar snapshots,
   métodos, erros e distinção entre teste fictício, simulado, humano e padronizado.
5. Concluir artigo SBC (até dez páginas) e vídeo (até dez minutos, todos aparecem,
   pelo menos 30 segundos de declaração de IA). Preencher `video:` somente com
   URL verdadeira/acessível e incluí-la em nota de rodapé na conclusão do artigo.
6. Confirmar a versão final auditada/aprovada correspondente ao GitHub e ao ZIP;
   autorização separada para avaliação final única e verificador em cópia sem
   segredos. Não há nota oficial ou entrega pronta declaradas.

O PDF/AGENTS mantêm a data original de 18/11/2026. O responsável informou na
Missão 06 prorrogação para 19/11/2026 às 23h59; comprovar o comunicado no AVA
antes da submissão. Esta declaração não altera o texto do enunciado.

## Comandos sugeridos para commits atômicos

Somente sugestões para o responsável, **não executadas** nesta missão. Conferir
o diff antes de cada commit; nenhum comando abaixo faz push ou avaliação:

```bash
git diff --check
git add -- grupo.yaml
git diff --cached --name-only
git diff --cached --check
git diff --cached
git commit -m 'fix(config): remover marcador pendente do comentario'

git add -- README.md LINKS.txt
git diff --cached --name-only
git diff --cached --check
git diff --cached
git commit -m 'docs(entrega): documentar execucao e links do RANGOT'

git add -- USO_DE_IA.md dados/prompts_llm.md docs/PROTOCOLO_DADOS.md docs/EXPERIMENTOS_CLASSIFICADORES.md docs/APROFUNDAMENTO_A1.md docs/MISSAO_11A.md
git diff --cached --name-only
git diff --cached --check
git diff --cached
git commit -m 'docs(ia): registrar revisoes humanas e ressalvas de auditoria'
```

Não incluir brutos privados, caches, credenciais ou resultados reexecutados nos
commits. A revisão humana destes novos textos não é presumida.
