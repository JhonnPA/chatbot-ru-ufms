# Declaração de uso de Inteligência Artificial generativa

> **Regra do trabalho:** usar IA generativa é **permitido e incentivado**, mas
> **todo e qualquer uso** precisa estar declarado e detalhado em uma seção própria
> do artigo e na apresentação (vídeo). Uso não declarado é considerado **plágio** e
> leva à **nota zero** no trabalho para todo o grupo.
>
> Este arquivo é o registro de trabalho da declaração, a ser atualizado ao longo
> do projeto e levado para o artigo e o vídeo. Informações não confirmadas estão
> identificadas como pendentes; não devem ser substituídas por suposições.

Os registros 1–5 e a reflexão histórica foram preservados. As afirmações de revisão
nesses registros pertencem ao relato anterior do grupo e não foram revalidadas
nesta sessão. As entradas 6–15 não declaram revisão manual individual concluída;
a entrada 15 registra curadoria por IA sob autorização expressa delegada.
A conferência humana posterior das 709 decisões foi declarada pelo responsável
na Missão 07B e está registrada na entrada 16, preservando esse histórico.

## 1. Ferramentas usadas
 
| Ferramenta (nome e versão/modelo) | Como acessaram | Quem usou |
|---|---|---|
| Claude (Anthropic), modelo Claude Opus 5.5 | claude.ai, navegador, com busca na web | Jonathan Amaral |
| ChatGPT, modelo não informado | Forma de acesso não confirmada neste registro; uso retrospectivo informado pelo responsável na Missão 03 | Identificação do operador a confirmar |
| Codex, identificador exato do modelo não confirmado neste registro | Sessões locais no checkout do RANGOT; inspeção offline e ferramentas locais | Responsável pela sessão; identificação pessoal a confirmar |
 
## 2. Usos, um por linha
 
| # | Etapa | O que a IA fez | Prompt (resumo) | O que o grupo fez com o resultado |
|---|---|---|---|---|
| 1 | Base de conhecimento | A partir do Guia Prático do RU 2026, pesquisado e fornecido pelo grupo, apontou quais intenções o guia não cobria e sugeriu documentos oficiais complementares da UFMS | "Com base no Guia Prático do RU da UFMS (2026) que estamos enviando, identifique quais intenções do chatbot ele não cobre e indique documentos oficiais da UFMS vigentes em 2026 (resoluções, editais da Proaes) que preencham essas lacunas, com a pasta de cada um." | Avaliamos as sugestões, escolhemos a Resolução nº 399-Coun/UFMS e o Edital nº 114/2026-Proaes/Aginter, baixamos os PDFs nos sites oficiais, conferimos datas e conteúdo e os fornecemos para a organização da base |
| 2 | Base de conhecimento | Reorganizou o Guia Prático do RU 2026 em 4 arquivos `.md`, um por intenção (cardapio, horarios, valores, cadastro) | "Divida o conteúdo do Guia Prático do RU 2026 em documentos Markdown, um por intenção (cardapio, horarios, valores, cadastro), mantendo apenas informações presentes no guia, sem acrescentar ou inferir dados." | Conferimos cada arquivo, item a item, contra o PDF original |
| 3 | Base de conhecimento | Fez uma busca na web por regras de conduta do RU da UFMS e redigiu `regras_uso/regras_de_uso_2026.md`, registrando a ausência de documento oficial e indicando o contato da Proaes | "Pesquise em fontes oficiais da UFMS as regras de uso do RU (marmita, mochila, conduta no refeitório). Se não houver documento oficial, escreva um documento curto que deixe isso explícito e oriente o usuário a procurar a Proaes pelo e-mail ru.proaes@ufms.br." | Conferimos a ausência de regulamento pesquisando no Boletim Oficial e no site da Proaes, definimos que o documento trataria só de conduta e revisamos o texto |
| 4 | Base de conhecimento | Redigiu `recarga_creditos/formas_de_pagamento.md` a partir da informação fornecida pelo grupo | "O RU da UFMS não usa sistema de créditos: a refeição é paga na hora, no débito, crédito ou Pix. Escreva um documento curto sobre as formas de pagamento, usando os valores do Guia Prático do RU 2026, sem acrescentar regras." | As formas de pagamento vieram da nossa experiência como usuários do RU; conferimos o texto |
| 5 | Configuração (`grupo.yaml`) | Redigiu as descrições, as respostas fixas e a persona das 6 intenções definidas pelo grupo na proposta, com base no Guia Prático do RU 2026 | "Preencha o grupo.yaml com as intenções cardapio, horarios, valores, recarga_creditos, cadastro e regras_uso, com respostas fixas fundamentadas no Guia Prático do RU 2026, sem inventar informações." | Conferimos as respostas contra o guia e preenchemos o nome do grupo e os integrantes |
| 6 | Planejamento e interpretação de requisitos | Assistência com ChatGPT, conforme informada pelo responsável na Missão 03, para planejar o trabalho e interpretar requisitos; histórico externo não inspecionado pelo Codex | Resumo da finalidade informado nesta missão: planejar o RANGOT e compreender os requisitos. Prompt original, modelo e conversa completa pendentes de recuperação | Registro retrospectivo solicitado pelo responsável. Não há confirmação nesta sessão do que foi aproveitado, alterado ou revisado por humanos |
| 7 | Preparação do ambiente Codex | Assistência generativa na preparação das configurações e dos prompts do Codex, informada pelo responsável. Nesta sessão, o Codex inspecionou os artefatos e os commits locais existentes, sem atribuir a si sua implementação anterior | Finalidade: preparar instruções, configurações e prompts para uso seguro do Codex no RANGOT. Ferramenta/modelo da preparação original e prompts anteriores a confirmar | Artefatos já existentes nas sessões auditadas. Autor da preparação, decisões de adoção e revisão humana ainda precisam ser confirmados |
| 8 | Auditoria de infraestrutura e colaboração — Missão 01 | Codex inspecionou instruções locais, configuração versionada, Git e interfaces; propôs responsabilidades, fluxo de PRs e contrato comum, sem modificar arquivos | Instrução intitulada “MISSÃO 01 — Auditoria de infraestrutura e colaboração multiagente”: leitura, evidências, contratos comuns e proposta de primeira alteração | Relatório e propostas apresentados nesta conversa. Aprovação das propostas e revisão humana do conteúdo não confirmadas; nenhum commit realizado nessa missão |
| 9 | Auditoria de requisitos, documentos e avaliação — Missão 02 | Codex auditou estaticamente código e documentos; identificou que o PDF então disponível era de Computação Distribuída e explicitou a limitação de autoridade documental | “MISSÃO 02 — Auditoria definitiva e planejamento dos dados do RANGOT”: auditar dados, base, contratos e C1–C11 sem implementar ou avaliar | Relatório apresentado; a leitura do PDF correto ocorreu somente na Missão 03. Revisão humana das conclusões ainda pendente; sem treinamento ou avaliação final |
| 10 | Interpretação dos CSVs e planejamento de curadoria — Missão 02 | Codex calculou contagens e duplicatas em memória, sugeriu rótulos/exclusões e simulou divisões por envio e complementação do treino para os 48 envios humanos e a base de 132 linhas sintéticas | Parte de dados da Missão 02: avaliar qualidade, proveniência, independência dos conjuntos e quantidades adicionais, sem gerar frases | Contagens semânticas e divisão são propostas da IA, sem aprovação humana registrada. Nenhum CSV foi alterado ou congelado. A geração original da base sintética não é atribuída ao Codex por esta entrada |
| 11 | Contrato compartilhado e atualização desta declaração — Missão 03 | Codex leu o enunciado correto de 29 páginas e interfaces existentes e redigiu com assistência generativa `docs/CONTRATOS_COMPARTILHADOS.md`, distinguindo requisitos oficiais de decisões internas; preparou esta atualização preservando os registros anteriores | “MISSÃO 03 — Formalização definitiva dos contratos do RANGOT”: conferir o PDF, formalizar o contrato e registrar a assistência, com alterações restritas a dois documentos | Implementação documental autorizada nesta missão; revisão humana do texto ainda pendente. Não houve geração de frases, treinamento, chamada ao OpenRouter ou avaliação final; a situação da gravação e dos commits é informada no relatório da missão |
| 12 | Auditoria científica reproduzível — Missão 04 | Codex implementou auditoria offline em `scripts/auditar_dados.py`, testes com fixtures fictícias de software e `docs/PROTOCOLO_DADOS.md`; reutilizou a normalização existente, preparou manifesto sem textos e propostas automáticas pendentes de revisão, sem formar conjuntos finais | “MISSÃO 04 — Implementação da auditoria científica dos dados do RANGOT”: ler brutos sem modificá-los, sinalizar qualidade/duplicatas, avaliar divisões por envio e validar mínimos com testes offline | Implementação autorizada em quatro arquivos; testes e resultados da execução são informados no relatório da missão. Revisão humana de código, rótulos e divisão permanece pendente. Fixtures são exclusivas dos testes de software, não frases para os CSVs científicos; sem treinamento, avaliação final ou OpenRouter |
| 13 | Fluxo de revisão humana — Missão 05 | Codex estendeu o auditor existente para exportar planilha local ignorada com textos originais e decisões pendentes, validar/importar decisões declaradas, recontar aprovadas e simular divisões por envio; acrescentou testes fictícios e documentação, sem aprovar rótulos nem criar conjuntos oficiais | “MISSÃO 05 — Curadoria humana e preparação dos conjuntos do RANGOT”: preservar textos/origens, permitir correções humanas, manter revisão privada e reavaliar 29/19, 30/18 e 31/17 sem modelos | Implementação e preparação da planilha autorizadas; decisões e aprovação da divisão pertencem ao responsável humano e começam pendentes. Testes e verificações técnicas são informados no relatório da missão. Nenhum treinamento, avaliação final, geração para os CSVs científicos ou OpenRouter foi executado |
| 14 | Ampliação da base e curadoria prioritária — Missão 06 | Codex comparou as versões e backups sem depender da ordem, implementou migração rastreável de decisões, examinou semanticamente as 669 respostas humanas e preparou sugestões privadas por ID/hash, uma revisão ampliada pendente e uma seleção prioritária com proposta de divisão por envio | “MISSÃO 06 — Atualizar a base humana para 67 envios e preparar a curadoria definitiva”: verificar preservação dos 48 envios e 19 adições, preservar origens/textos, planejar mínimos sem modelos e facilitar revisão humana | Código, testes e documentação implementados; a gravação nativa da substituição foi bloqueada pelo sandbox antes de alterar base/revisão ativas. Arquivos privados da nova revisão e proposta preparados pelo editor. Rótulos e divisão continuam sem aprovação humana. Sem treinamento, avaliação final, geração adicional de dados científicos ou OpenRouter |
| 15 | Curadoria semântica com aprovação delegada — Missão 07A | Codex, família GPT-6 informada nesta sessão, variante exata não exposta, leu individualmente as 654 candidatas e 55 suplentes/complementos incorporados; registrou 575 aprovações delegadas, cinco correções, 116 rejeições e 13 pendências; implementou ledger privado, validação e importação com proveniência, testes fictícios e documentação | “MISSÃO 07A — Curadoria semântica com aprovação delegada pelo responsável”: autorização expressa para decidir individualmente e registrar aprovações, com origem IA declarada, sem atribuir revisão manual individual ao responsável | O responsável declarou ter examinado o CSV e delegou decisões; não confirmou leitura individual de todas as frases. Revisão mestre importada com observações de delegação e backups preservados. Teste proposto com 160 textos humanos originais; treino com 420 exemplos e falta de 130 pelos critérios adotados. Persistem 13 pendências e não houve congelamento, construção dos CSVs oficiais, treinamento, avaliação final, geração adicional de frases científicas ou OpenRouter |
| 16 | Ratificação humana e preparação dos conjuntos — Missão 07B | Codex registrou a conferência expressa do responsável, validou o snapshot ratificado, materializou e congelou 160 textos humanos originais em dados/teste.csv, exportou treino parcial autorizado de 420 exemplos e pacote exclusivo de treinamento, e investigou reaproveitamento da base sintética com cinco novas candidatas separadas para conferência | “MISSÃO 07B — Ratificar a curadoria e construir os conjuntos do RANGOT”: preservar as 709 decisões ratificadas, manter pendências excluídas, congelar teste após validação, buscar reaproveitamento e isolar o material da futura geração | O responsável declarou leitura integral e concordância com 575 aprovações, cinco correções, 116 rejeições e 13 pendências. Essa conferência posterior não altera a autoria delegada histórica das decisões da Missão 07A. As cinco novas candidatas permanecem pendentes e não entram no treino autorizado. Treino oficial ainda incompleto; sem geração de frases científicas, treinamento de modelos, avaliadores ou OpenRouter |

Os resumos das entradas 8–16 correspondem às instruções desta conversa; suas
íntegras não estão arquivadas no repositório. Os resumos retrospectivos 6–7
registram o relato do responsável, sem reconstruir prompts anteriores como se
fossem transcrições verificadas.

## 3. O que NÃO foi feito com IA

As três afirmações históricas abaixo são preservadas do relato anterior; esta
sessão não comprova a autoria externa desses materiais. Não estender essas
afirmações à triagem dos CSVs ou à redação deste contrato, que receberam apoio
generativo conforme as entradas 8–16.
 
- Escolha do tema e definição das intenções (feitas pelo grupo na proposta de 23/10/2026).
- Informação sobre as formas de pagamento (débito, crédito, Pix).
- Obtenção do Guia Prático do RU 2026 e download dos documentos oficiais.
- Autoria das frases do teste: declarada humana pelo responsável; nenhuma foi gerada ou parafraseada pela IA. A seleção/rotulagem delegada da Missão 07A foi posteriormente conferida e ratificada pelo responsável na Missão 07B. O teste de 160 frases foi congelado com os textos originais preservados.
- Análise de erros experimentais e conclusões finais: ainda não realizadas nessas missões; registrar qualquer assistência futura antes de afirmar independência de IA.

## 4. Reflexão (2 a 4 frases)
 
A IA acelerou a busca de documentos oficiais e a organização da base de conhecimento. Ela errou em pontos que só identificamos conferindo as fontes: usou primeiro o Guia do RU de 2025, com valores e horários desatualizados, até fornecermos a versão de 2026; e listou o mesmo edital duas vezes, com links diferentes. Também não sabia que o RU não usa créditos, o que corrigimos com a nossa experiência. Por isso, conferimos todo arquivo gerado contra o documento original antes de incluí-lo.

### Complemento das missões do Codex — revisão humana pendente

O Codex ajudou a identificar a referência incorreta do enunciado, a separar
contratos oficiais de decisões internas e a planejar uma curadoria rastreável.
As sugestões semânticas sobre os dados e os textos produzidos continuam
dependentes de revisão humana; contagens de candidatos não são métricas de
desempenho nem aprovação de rótulos. Na Missão 03, a extração offline do PDF
correto confirmou o título, as 29 páginas e a rubrica C1–C11, sem chamadas externas.

Na Missão 04, a assistência passou da auditoria em memória para uma implementação
reproduzível e seus testes de software. As regras lexicais explicitam limitações
e mantêm sugestões sem aprovação humana; divergências em relação às contagens
anteriores precisam ser revisadas, sem ajustar as regras para forçar uma divisão.

Na Missão 05, a IA implementou a preparação e a validação da planilha de revisão,
preservando os textos originais e separando sugestões de decisões explicitamente
declaradas pelo responsável. A existência da planilha e a aprovação dos testes de
software não significam que as frases ou a divisão de treino/teste foram aprovadas
por humanos; essa revisão permanece pendente.

## 5. Pendências para fechar a declaração

A Missão 07A tornou explícita a diferença entre autoria humana do texto e autoria
da decisão de curadoria. O Codex excluiu repetições e manteve dúvidas em aberto,
mostrando que a capacidade anterior era provisória. A delegação não dispensa o
grupo de compreender e justificar o material, nem permite declarar que todos os
conjuntos estão completos enquanto persistirem as faltas documentadas.

- Missões 07A/07B: levar ao artigo e ao vídeo a autoria delegada inicial das decisões e a conferência humana posterior expressamente declarada. As 13 pendências permanecem excluídas; o teste já foi congelado. O treino tem 420 exemplos autorizados e falta de 130. Conferir as cinco novas candidatas existentes antes de definir o complemento final; nenhuma foi abrangida pela ratificação anterior.

- Missão 06 (histórico): a incorporação dos 67 envios foi observada concluída antes da Missão 07A. As projeções anteriores foram substituídas pela curadoria delegada registrada na entrada 15; não eram resultados de modelos nem revisão manual individual.

- Confirmar ferramenta/modelo, operador e prompts originais dos usos retrospectivos de ChatGPT e da preparação do Codex, sem inferir versões a partir da ferramenta atual.
- Recuperar ferramenta/modelo, prompts e revisão da geração original das 132 linhas sintéticas, confirmadas como IA pelo responsável; as linhas têm múltiplas respostas e não equivalem a 132 frases. Essa atividade não está declarada como concluída ou revisada nesta atualização.
- Confirmar quais sugestões das auditorias e do contrato foram aproveitadas, corrigidas ou descartadas, com responsáveis pela revisão humana.
- Identificar eventual uso de Claude Code separadamente do uso histórico de Claude via navegador; não há evidência de execução de Claude Code por esta sessão.
- Registrar futuras gerações, código, artigo, vídeo e uso do LLM do bot. Nenhuma dessas execuções futuras está presumida como realizada.
- Levar os usos efetivos para a seção própria do artigo, com reflexão e contribuição dos integrantes, e para o vídeo, reservando pelo menos 30 segundos conforme a seção 7 do enunciado.
