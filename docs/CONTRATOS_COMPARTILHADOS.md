# Contratos compartilhados do RANGOT

Documento de referência para Codex, Claude Code e integrantes do grupo. Redação assistida por IA; revisão humana do documento ainda pendente. Este registro não comprova conclusão de critérios, execução de experimentos ou aprovação dos dados.

## 1. Autoridade e fontes

**Fonte normativa:** [enunciado do professor](../referencias/_brutos/enunciado_professor.pdf), "Um chatbot que sabe quando (e o que) responder", Inteligência Artificial, graduação FACOM/UFMS 2026/2, Prof. Bruno M. Nogueira, 29 páginas. Leitura conferida em 17/11/2026. As páginas citadas abaixo são as páginas físicas do PDF, contadas de 1 a 29.

SHA-256 do PDF não secreto consultado: `004e80a57f9793fbbb51d5394ae79206fde47c3cb77e9e8a0db7c979deee6ed6`.

**Fontes de interface:** [rótulos](../chatbot/rotulos.py), [dados](../chatbot/dados.py), [modelos](../chatbot/modelos.py), [grafo](../chatbot/grafo.py), [avaliador](../scripts/avaliar.py), [métricas](../chatbot/avaliacao.py) e [verificador](../scripts/verificar_entrega.py). O código foi inspecionado estaticamente, sem executar avaliações.

As seções 2 a 9 identificam requisitos do **professor** e detalhes das **interfaces existentes**. A seção 10 registra **decisões internas** e propostas, sem atribuí-las ao professor. O enunciado prevalece sobre documentação derivada; divergências devem ser registradas, nunca resolvidas pela alteração dos arquivos oficiais protegidos. Exemplos de código, temas, limiares e resultados do PDF não são resultados do RANGOT.

## 2. Critérios oficiais C1–C11

Fonte: seção 10, pp. 26–27.

| Critério | Pontos | O que deve ser demonstrado |
|---|---:|---|
| C1 — Domínio e intenções | 5 | Intenções delimitadas, descrições e respostas coerentes; revisão justificada quando necessária. |
| C2 — Dados | 15 | Volume e diversidade, negativos difíceis, teste humano/coletado, separação treino/teste, origens e prompts documentados. |
| C3 — Classificador de escopo | 12 | Pelo menos três algoritmos, duas representações, CV, tuning, métricas adequadas e escolha justificada. |
| C4 — Classificador de tema | 12 | Mesmos aspectos de C3, incluindo análise das confusões entre intenções. |
| C5 — Integração e base | 10 | Modelos no contrato, documentos e fontes adequados, limiar empírico, persona e demonstração de acertos e limitações. |
| C6 — Aprofundamento | 10 | Qualidade técnica, avaliação e profundidade da análise de pelo menos um aprofundamento. |
| C7 — Avaliação padronizada | 10 | F1 macro ponta a ponta no conjunto combinado usado pelo professor. |
| C8 — Análise crítica | 10 | Resultados e erros, CV × teste, origem dos dados, limitações e relações com a disciplina. |
| C9 — Artigo | 6 | Clareza, SBC, figuras/tabelas legíveis, referências e declaração completa de IA. |
| C10 — Vídeo | 5 | Tempo, clareza, demonstração, declaração de IA e participação de todos. |
| C11 — Reprodutibilidade | 5 | Verificador sem erros, notebook executável, README e dependências completos. |
| **Total** | **100** | A existência deste contrato não atribui pontos nem certifica conformidade. |

## 3. Domínio, dados e proveniência

Fonte: seções 1.4 e 2, pp. 4–6; Passos 4–7, pp. 15–18; seção 5, pp. 22–23.

- Grupo de 3 a 4 integrantes; tema validado pelo professor. Biblioteca universitária é o exemplo e não pode ser escolhida. Definir de 5 a 10 intenções, com descrição e resposta fixa. Nomes usam minúsculas sem acento, dígitos e sublinhado, sem colidir com os rótulos reservados.
- Cada mensagem recebe um único rótulo: intenção do domínio, `chitchat` ou `fora_dominio`. O escopo é derivado automaticamente. `dominio` e `esclarecer` não são intenções a anotar nos CSVs.
- Manter `dados/treino.csv` e `dados/teste.csv` com `texto,intencao,origem`, UTF-8, cabeçalho e separador vírgula; textos com vírgula devem ser corretamente delimitados.

| Mínimo | Treinamento | Teste |
|---|---:|---:|
| Por intenção do domínio | 50 | 15 |
| `chitchat` | 100 | 30 |
| `fora_dominio` | 150 | 40 |
| Origem `humano` ou `coletado` | Pelo menos 20% do total | 100% |
| Para N intenções | 50 × N + 250 | 15 × N + 70 |

Com seis intenções, esses mínimos correspondem a **550** exemplos de treino e **160** de teste. Em um treino de 550, pelo menos **110** devem ser humanos/coletados; em conjuntos maiores, recalcular a fração de 20%.

| `origem` | Significado no enunciado e na interface |
|---|---|
| `humano` | Texto escrito por pessoa. |
| `coletado` | Texto de fonte real, como fórum, FAQ ou e-mail anonimizado. |
| `llm` | Texto gerado por LLM; declarar ferramenta/modelo e prompts. |
| `aumentado` | Variação automática de outra frase; documentar o procedimento. |
| `massive` | Texto proveniente da base auxiliar MASSIVE. |

Frases sintéticas precisam de revisão linha por linha, remoção de repetições/estranhezas e correção dos rótulos antes de entrar no treino. Guardar os prompts em `dados/prompts_llm.md` e declarar o uso. O teste aceita somente `humano`/`coletado`, preferencialmente de pessoas externas ao grupo; geração, tradução ou paráfrase por LLM não transforma texto em humano.

O `fora_dominio` deve conter negativos fáceis e, principalmente, difíceis: temas vizinhos, com vocabulário parecido com o domínio. Variar estilos e registrar autoria/procedência; o PDF recomenda que cada integrante escreva para todas as intenções, evitando associar uma classe ao estilo de uma pessoa.

### Separação e prevenção de vazamento

**Professor:** nenhuma frase do teste pode aparecer no treino. O teste fica reservado para uma única avaliação final, depois das escolhas; algoritmo, representação, hiperparâmetros e limiar são escolhidos exclusivamente no treinamento e sua validação cruzada (seção 3.5, pp. 8–9; Passos 6 e 14; seção 5).

**Interface:** `chatbot.dados.vazamento` compara minúsculas e espaços normalizados. Isso não garante detectar acentos, pontuação, paráfrases ou variações próximas; verificações complementares do grupo estão na seção 10. Não usar mensagens reservadas ao teste para inspirar novos exemplos de treinamento.

## 4. Comparações, validação e limiar

Fonte: seções 3.3–3.7, pp. 7–10; Passos 9–12, pp. 18–20; seção 5, pp. 22–23.

1. Em **cada estágio**, comparar pelo menos três algoritmos vistos na disciplina e pelo menos duas representações de texto. Regressão logística, MLP e árvore, assim como TF-IDF de palavras e caracteres, são exemplos fornecidos no roteiro, não uma lista exclusiva. Discutir pré-processamento.
2. Usar validação cruzada estratificada de **cinco folds**, só no treino; apresentar F1 macro, métrica principal, com média e desvio dos cinco folds. O roteiro exemplifica `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`; o valor da semente é exemplo, não exigência autônoma.
3. O vetorizador também aprende: treiná-lo com o classificador dentro do `Pipeline` de cada fold, sem aprender vocabulário/IDF no conjunto inteiro antes da CV.
4. Ajustar os melhores candidatos com `GridSearchCV` no treino. Registrar grades e escolhas; apresentar pelo menos uma curva de validação em cada estágio, repetindo para tema o protocolo de escopo.
5. Escopo usa todas as mensagens de treino; tema usa somente as de domínio. Apresentar F1 macro, acurácia e matrizes de confusão; analisar falso aceite, falsa recusa, confusões entre intenções e gravidade dos erros no domínio.
6. Analisar previsões de CV, por exemplo com `cross_val_predict`, incluindo erros por origem, mensagens curtas, digitação e negativos difíceis. O ciclo de melhoria de dados usa erros do treino/CV.
7. Escolher `roteamento.limiar_tema` empiricamente com probabilidades de CV, comparando previsões corretas e erradas. Para cada candidato, quantificar respostas diretas, acurácia nelas, erros evitados e acertos convertidos em esclarecimento. Justificar o compromisso; valores ilustrativos do PDF não são limiares obrigatórios.

## 5. Contratos dos modelos, do grafo e dos arquivos

Fonte: seção 8, pp. 24–25; Passo 13, p. 21; interfaces citadas na seção 1.

| Elemento | Contrato preservado |
|---|---|
| Configuração | `grupo.yaml` mantém os nomes das chaves e a estrutura do modelo. |
| Arquivos de modelos | `modelos/escopo.joblib` e `modelos/tema.joblib`. |
| Entrada | Lista de textos crus; salvar o pipeline completo, não apenas o classificador após vetorização externa. |
| Interface de classificação | `predict(lista_de_textos)` e `classes_`; escopo conhece exatamente `dominio`, `chitchat`, `fora_dominio`; tema conhece exatamente as intenções do `grupo.yaml`. |
| Probabilidades | `predict_proba` é opcional no carregamento básico, mas necessário para o mecanismo de confiança/esclarecimento. As colunas seguem `classes_`. Sem esse método, o grafo existente usa confiança 1,0. |
| Persistência | Usar `chatbot.modelos.salvar_classificadores`, que confere interfaces e salva os modelos e informações de versão. |
| Grafo | Preservar `construir_grafo(config, clf_escopo, clf_tema)`, devolvendo grafo compilado. Parâmetros opcionais existentes não quebram essa chamada. |
| Invocação | `grafo.invoke({"mensagem": texto})` termina com `rota` e `resposta`. Rotas válidas: intenções, `chitchat`, `fora_dominio` ou `esclarecer`. |
| Decisão | Classificadores determinam a rota; LLM só redige a resposta depois da classificação. Sem LLM, funcionar com respostas fixas. |
| Dependências | Toda biblioteca adicional deve constar em `requirements.txt`. Funções/classes próprias de pipelines devem ser importáveis de módulos em `chatbot/`, não definidas apenas no notebook. |

**Arquivos oficiais que não podem ser modificados, mesmo para corrigir problemas:**

- `scripts/avaliar.py`;
- `scripts/verificar_entrega.py`;
- `chatbot/avaliacao.py`.

Na correção, esses arquivos são substituídos pelas versões oficiais. Problemas devem ser relatados sem contornar o contrato.

## 6. Base de conhecimento e demonstração

Fonte: seções 2 e 3.10, pp. 5 e 12–13; Passos 5 e 13, pp. 16–17 e 21; seção 5.

Reunir pelo menos **cinco documentos**, cobrindo todas as intenções e organizados em `documentos/<intencao>/` e `documentos/geral/`. Aceitar PDF com texto digital, MD, TXT e HTML. Em `documentos/FONTES.md`, registrar por documento URL/data de acesso, setor que forneceu ou autoria e base utilizada.

O professor permite documentos escritos pelo grupo, desde que plausíveis, coerentes com as respostas fixas e declarados; assistência de IA também entra no registro de IA. Um relato do grupo não deve ser identificado como publicação oficial.

A busca usa a intenção prevista e documentos gerais. Ajustar persona, contato e recuperação; demonstrar acertos, erros e pergunta sem resposta na base. Nessa situação, o bot deve admitir a limitação, sem inventar informações.

## 7. Aprofundamento obrigatório

Fonte: seção 6, p. 23. Implementar e analisar **pelo menos um**:

| Opção | Comparação/estudo previsto |
|---|---|
| A1 | Cascata versus classificador único com N + 2 classes. |
| A2 | Rejeição apenas por limiar, sem classificador de escopo, versus rejeição explícita. |
| A3 | Origem: treino sintético, humano e misto no mesmo teste humano, incluindo curva de aprendizado. |
| A4 | Embeddings de sentenças versus TF-IDF, incluindo custo e latência. |
| A5 | Contexto de conversa, avaliado em conversas com duas ou mais mensagens. |
| A6 | Terceiro classificador: conversa social ou subdivisão de intenção. |
| A7 | LLM zero-shot como comparação, com desempenho, custo, latência e privacidade; não substitui o roteamento entregue. |
| A8 | Qualidade da recuperação: acerto@k, representações, tamanhos de trecho e filtro por intenção. |

O professor não obriga A1. Escolha do grupo e protocolo precisam ser documentados. Estudos que mencionam o mesmo teste devem ser planejados antes do acesso final, sem usá-lo iterativamente para escolher modelos; decisões operacionais internas constam na seção 10.

## 8. Avaliação final e nota de desempenho

Fonte: Passo 14, pp. 21–22; seções 5 e 8, pp. 23–25.

Com todas as escolhas concluídas, executar a avaliação padronizada **uma única vez** no teste, sem LLM. Preservar `resultados/avaliacao.json` e `resultados/avaliacao_previsoes.csv`, comparar com CV e analisar qualitativamente os erros e a origem dos dados. As métricas do exemplo da biblioteca não são métricas do RANGOT.

A interface relata escopo, tema-oráculo (somente mensagens realmente de domínio) e ponta a ponta, além de falso aceite, falsa recusa, esclarecimento e latência. A rota `esclarecer` não equivale a acertar a intenção verdadeira.

O professor calcula C7 pelo **F1 macro ponta a ponta na união** de quatro conjuntos: teste do grupo; conversa social/fora do domínio do professor; frases de domínio dos testes de outros grupos como fora do domínio; e frases do domínio do grupo escritas pelo professor. O teste local sozinho não comprova a nota C7.

| F1 macro combinado | Pontos C7 |
|---|---:|
| ≥ 0,85 | 10 |
| ≥ 0,75 e < 0,85 | 8 |
| ≥ 0,65 e < 0,75 | 6 |
| ≥ 0,50 e < 0,65 | 4 |
| < 0,50 | 2 |

Qualquer **ERRO** do verificador, ou bot não executável, zera **C7 e C11**. Isso prevalece sobre a tabela de desempenho.

## 9. Artigo, vídeo, IA, segurança e submissão

Fonte: seção 7, p. 24; seções 9–11, pp. 25–27; Passos 2 e 15, pp. 14–15 e 22; checklist, p. 29.

### Artigo e repositório

- Artigo SBC em `relatorio/relatorio.pdf`, até **10 páginas**, incluindo figuras e referências. A estrutura sugerida abrange fundamentação, domínio/dados/documentos, metodologia, resultados, discussão, conclusão, contribuição dos integrantes e declaração de IA.
- Entregar repositório completo com dados, documentos, modelos treinados, `notebooks/01_trabalho_grupo.ipynb` executado do início ao fim, `README.md` atualizado, dependências, `USO_DE_IA.md` e `LINKS.txt`.
- Antes da entrega, verificador oficial com **zero erros**. Gerar o ZIP do conteúdo commitado com `git archive`; conferir que contém os artefatos necessários e não contém credenciais.

### Vídeo e participação

Vídeo de até **10 minutos**, YouTube público/não listado ou Google Drive acessível a quem tem o link. Todos os integrantes participam de todas as etapas e aparecem no vídeo. Incluir demonstração do bot, erro explicado e pergunta sem resposta nos documentos. Registrar URL em `LINKS.txt`, no formato `video: https://...`, e em nota de rodapé na conclusão do artigo.

### Declaração de IA

Todo uso generativo, inclusive planejamento, código, dados, tradução/paráfrase, documentação, análise, artigo, roteiro e LLM do bot, deve ser declarado em `USO_DE_IA.md`, em seção própria do artigo e no vídeo. Para cada uso: ferramenta/modelo, etapa, atividade, prompt ou resumo com referência ao registro, e o que o grupo verificou/aproveitou/descartou. Não preencher lacunas com informações inventadas.

No artigo, dizer também o que não foi feito com IA e apresentar reflexão sobre ajuda, erros e verificação. Reservar **pelo menos 30 segundos** do vídeo para esses usos. O grupo responde por cada código, número e frase e deve conseguir explicá-los.

### Credenciais e OpenRouter

O professor fornece uma chave por grupo com créditos limitados e prevê armazenamento local no computador de cada integrante ou nos Secrets do Colab; nunca publicar em código, notebook, prints, mensagens ou entrega. Em vazamento, avisar o professor para revogação. O modelo do bot é configurado em `llm.modelo`; exemplos de modelo/preço do PDF não são verificação atual de disponibilidade/custo. A restrição adicional de acesso pelos agentes está na seção 10.

O LLM redige com os trechos recuperados, não escolhe a rota. Sem chave ou com falha de chamada, respostas fixas garantem funcionamento; a avaliação automática independe de internet/créditos.

### Prazo e penalidades oficiais

Entrega da proposta: **23/10/2026**, formulário no AVA. Entrega final: **18/11/2026, até 23h59**, por um integrante no AVA, em ZIP. A versão avaliada é a do ZIP; incluir endereço do repositório em `LINKS.txt` se compartilhado com o professor.

- IA não declarada, plágio ou atraso: nota zero, nos termos do enunciado.
- Teste com frases de LLM ou repetidas do treino: **C7 zero e C2 reduzido à metade**.
- Vídeo acima de 10 minutos: **−5 pontos**; páginas após a décima não são lidas.
- Publicação da chave: **−5 pontos**, além da necessidade de revogação.
- A nota pode ser individualizada diante de participação desigual.

## 10. Decisões internas e estado de aprovação

Esta seção não cria novas exigências do professor. Registra regras operacionais do grupo e limites desta missão.

- **Segurança dos agentes:** trabalhar offline, sem ler/procurar credenciais, arquivos de credenciais, variáveis secretas, Keychain ou Secrets do Colab. Não executar OpenRouter, scripts que carregam a chave nem células de LLM. Demonstrações reais com LLM ficam para execução humana autorizada em ambiente separado; registrar resultados reais. Não alterar a lógica de segredos para contornar a restrição.
- **Congelamento e autorização:** responsável humano aprova rótulos e proveniência, congela teste, modelos e limiar e autoriza expressamente a avaliação final. Agentes não a executam automaticamente. Depois, não retreinar/ajustar a partir do resultado do teste.
- **Curadoria proposta:** rastrear envio/célula, revisar duplicatas exatas, normalizadas e próximas e manter relacionadas as respostas de um envio. O professor exige independência; a estratégia específica de agrupamento, o manifesto e a divisão dos 48 envios ainda dependem de aprovação humana. Não usar reserva de teste como inspiração para síntese.
- **Proveniência informada:** o responsável confirmou nas missões anteriores 48 envios humanos e uma base de 132 linhas sintéticas. Isso não equivale a aprovar seus rótulos ou todas as células. Frases geradas/parafraseadas por IA recebem `llm`; origem incerta não é promovida a humana.
- **Protocolo proposto:** TF-IDF de palavras e caracteres; cinco folds com partições/semente registradas; considerar grupos de autoria/envio e famílias sintéticas para evitar dependência entre folds. A definição de agrupamento e eventual adaptação da estratégia de CV precisam de justificativa e aprovação antes dos experimentos. Não são exigências literais de um estimador específico pelo professor.
- **Aprofundamento inicialmente preferido:** A1; com as seis intenções hoje configuradas, o modelo único teria oito classes. A opção ainda precisa ser confirmada para implementação; não há resultado experimental neste contrato.
- **Git e colaboração:** Codex é o agente principal; Claude Code pode apoiar tarefas delimitadas, sob os mesmos contratos. Trabalhar em `feature/*`, com escopo e responsável por arquivo definidos, commits atômicos e PR revisado para `develop`. Branch atual desta missão: `feature/codex-config-segura`. Não presumir a branch do outro checkout nem alterar configurações específicas do Claude.
- **Limite desta missão:** somente este documento e `USO_DE_IA.md`; dois commits locais autorizados. Nenhuma autorização para modificar PDFs/CSVs/modelos, gerar frases, treinar, avaliar, fazer push, merge ou escrever em `develop`.
- **Verificador:** a inspeção estática mostrou que ele percorre arquivos procurando chaves e executa o grafo com mensagens do teste. Por decisão de segurança e integridade, executá-lo somente na etapa final autorizada, em cópia sem segredos; nunca reescrevê-lo para passar.
- **Pendências:** revisão humana deste texto, recuperação de modelos/prompts de usos anteriores de IA, aprovação da curadoria e do aprofundamento. Números e divisões sugeridos em auditorias são propostas, não métricas nem dados congelados.

A leitura deste documento por ambos os agentes deve ser solicitada explicitamente pelos operadores; sua existência no Git não comprova carregamento automático nem revisão pelo outro integrante.
