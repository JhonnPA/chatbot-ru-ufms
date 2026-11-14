# Declaração de uso de Inteligência Artificial generativa

> **Regra do trabalho:** usar IA generativa é **permitido e incentivado**, mas
> **todo e qualquer uso** precisa estar declarado e detalhado em uma seção própria
> do artigo e na apresentação (vídeo). Uso não declarado é considerado **plágio** e
> leva à **nota zero** no trabalho para todo o grupo.
>
> Este arquivo é o rascunho de trabalho da declaração: preencham **ao longo** do
> projeto (não no último dia) e copiem a tabela para o artigo. Apaguem as linhas de
> exemplo e todas as marcações TODO.

## 1. Ferramentas usadas
 
| Ferramenta (nome e versão/modelo) | Como acessaram | Quem usou |
|---|---|---|
| Claude (Anthropic), modelo Claude Opus 5.5 | claude.ai, navegador, com busca na web | Jonathan Amaral |
 
## 2. Usos, um por linha
 
| # | Etapa | O que a IA fez | Prompt (resumo) | O que o grupo fez com o resultado |
|---|---|---|---|---|
| 1 | Base de conhecimento | A partir do Guia Prático do RU 2026, pesquisado e fornecido pelo grupo, apontou quais intenções o guia não cobria e sugeriu documentos oficiais complementares da UFMS | "Com base no Guia Prático do RU da UFMS (2026) que estamos enviando, identifique quais intenções do chatbot ele não cobre e indique documentos oficiais da UFMS vigentes em 2026 (resoluções, editais da Proaes) que preencham essas lacunas, com a pasta de cada um." | Avaliamos as sugestões, escolhemos a Resolução nº 399-Coun/UFMS e o Edital nº 114/2026-Proaes/Aginter, baixamos os PDFs nos sites oficiais, conferimos datas e conteúdo e os fornecemos para a organização da base |
| 2 | Base de conhecimento | Reorganizou o Guia Prático do RU 2026 em 4 arquivos `.md`, um por intenção (cardapio, horarios, valores, cadastro) | "Divida o conteúdo do Guia Prático do RU 2026 em documentos Markdown, um por intenção (cardapio, horarios, valores, cadastro), mantendo apenas informações presentes no guia, sem acrescentar ou inferir dados." | Conferimos cada arquivo, item a item, contra o PDF original |
| 3 | Base de conhecimento | Fez uma busca na web por regras de conduta do RU da UFMS e redigiu `regras_uso/regras_de_uso_2026.md`, registrando a ausência de documento oficial e indicando o contato da Proaes | "Pesquise em fontes oficiais da UFMS as regras de uso do RU (marmita, mochila, conduta no refeitório). Se não houver documento oficial, escreva um documento curto que deixe isso explícito e oriente o usuário a procurar a Proaes pelo e-mail ru.proaes@ufms.br." | Conferimos a ausência de regulamento pesquisando no Boletim Oficial e no site da Proaes, definimos que o documento trataria só de conduta e revisamos o texto |
| 4 | Base de conhecimento | Redigiu `recarga_creditos/formas_de_pagamento.md` a partir da informação fornecida pelo grupo | "O RU da UFMS não usa sistema de créditos: a refeição é paga na hora, no débito, crédito ou Pix. Escreva um documento curto sobre as formas de pagamento, usando os valores do Guia Prático do RU 2026, sem acrescentar regras." | As formas de pagamento vieram da nossa experiência como usuários do RU; conferimos o texto |
| 5 | Configuração (`grupo.yaml`) | Redigiu as descrições, as respostas fixas e a persona das 6 intenções definidas pelo grupo na proposta, com base no Guia Prático do RU 2026 | "Preencha o grupo.yaml com as intenções cardapio, horarios, valores, recarga_creditos, cadastro e regras_uso, com respostas fixas fundamentadas no Guia Prático do RU 2026, sem inventar informações." | Conferimos as respostas contra o guia e preenchemos o nome do grupo e os integrantes |
 
## 3. O que NÃO foi feito com IA
 
- Escolha do tema e definição das intenções (feitas pelo grupo na proposta de 23/10/2026).
- Informação sobre as formas de pagamento (débito, crédito, Pix).
- Obtenção do Guia Prático do RU 2026 e download dos documentos oficiais.
- COMPLETAR AO LONGO DO PROJETO: frases do teste, análise dos erros, conclusões.
## 4. Reflexão (2 a 4 frases)
 
A IA acelerou a busca de documentos oficiais e a organização da base de conhecimento. Ela errou em pontos que só identificamos conferindo as fontes: usou primeiro o Guia do RU de 2025, com valores e horários desatualizados, até fornecermos a versão de 2026; e listou o mesmo edital duas vezes, com links diferentes. Também não sabia que o RU não usa créditos, o que corrigimos com a nossa experiência. Por isso, conferimos todo arquivo gerado contra o documento original antes de incluí-lo.
