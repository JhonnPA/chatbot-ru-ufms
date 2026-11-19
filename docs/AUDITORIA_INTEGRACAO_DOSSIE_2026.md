# Auditoria e integração documental do dossiê — Missão 10B

## Escopo e protocolo registrado antes das alterações

Branch confirmada: `feature/rag-openrouter-rangot`; Git inicialmente limpo.
Missão documental offline, sem retreino, avaliação ou chamadas de API. A fonte
normativa é o enunciado original, especialmente pp. 12–13, 16, 21 e 24–25.
O dossiê é pesquisa de ChatGPT/GPT-6, não uma coleção de originais oficiais.
Revisão humana dos documentos integrados não é presumida.

Antes de editar o corpus, foram fixadas as 12 perguntas fictícias abaixo e
capturados seus quatro primeiros trechos com a API existente. A busca usa a
intenção indicada para isolar recuperação de classificação. Q03 não tem filtro
porque localização não é uma nova intenção. Nenhuma frase do teste foi consultada.

| ID | Filtro de intenção | Pergunta fixa |
|---|---|---|
| Q01 | cardapio | Qual é o cardápio do almoço de hoje no RU de Campo Grande? |
| Q02 | cardapio | Em qual site oficial vejo os cardápios de café da manhã, almoço e jantar? |
| Q03 | sem filtro (diagnóstico de localização) | Onde fica o Restaurante Universitário na Cidade Universitária de Campo Grande e qual seu contato? |
| Q04 | horarios | Qual horário de almoço e jantar do RU em Campo Grande? |
| Q05 | horarios | Qual é o horário do almoço do RU em Aquidauana? |
| Q06 | horarios | Qual é o horário do jantar do RU em Corumbá? |
| Q07 | valores | Quanto custa café da manhã e almoço com subsídio e quem tem direito? |
| Q08 | valores | Qual é o preço integral da refeição no RU de Campo Grande? |
| Q09 | cadastro | Quais documentos e sites uso para cadastro do subsídio no RU? |
| Q10 | recarga_creditos | Posso pagar por Pix ou cartão e recarregar créditos no RU? |
| Q11 | regras_uso | Posso repetir arroz, feijão, salada, proteína e sobremesa no RU? |
| Q12 | regras_uso | Posso levar marmita e guardar lugar na fila do RU? |

Baseline: oito documentos, 77 trechos, assinatura `ec950b8816db7b32`.
Q01/Q02 recuperavam composição geral sem o canal de cardápios; Q03 não tinha
endereço comprovado; Q11 recuperou somente contato, sem procedimentos. Horários,
subsídios e cadastro já tinham trechos pertinentes; Q05/Q06 traziam horários
categóricos de outros campi e Q10 tinha lista de pagamentos sem ressalva no
próprio trecho da lista. O baseline foi mantido em memória para comparação com
as mesmas perguntas depois da integração.

## Fontes recebidas e confrontação com originais

Foram lidos integralmente README, RELATORIO_PESQUISA.md, MANIFESTO_FONTES.csv
(25 registros), MATRIZ_RASTREABILIDADE, CONFLITOS_E_VIGENCIA,
LACUNAS_DOCUMENTAIS, CARDAPIOS_E_VALIDADE, INSTRUCOES_INTEGRACAO e os nove
Markdown em RAG_CANDIDATOS. O relatório PDF é uma produção da pesquisa por IA,
não fonte institucional. `FONTES_ORIGINAIS/` está presente e não contém arquivos.
Hashes de materiais gerados não certificam os documentos oficiais citados.

| IDs do dossiê | Confrontação e decisão |
|---|---|
| F01 | Guia local com 16 páginas; conferidos contatos p. 4, horários p. 6, valores/cadastro p. 7, composição pp. 8–12 e orientações alimentares p. 13. Aceitos somente esses fatos e limites. A URL direta é indicação do dossiê; não houve download para comparar bytes. |
| F02 | Página central sem snapshot local. Endereço do RU, atualização bienal do CadÚnico e outros fatos exclusivos dessa página não incorporados como oficiais. |
| F03 | Canal de cardápios fornecido expressamente pelo responsável, também referenciado pelo dossiê. Aceito como endereço para consulta, sem alegar verificação HTTP, conteúdo atual ou validade de pratos. |
| F04–F06 | Os PDFs locais de jantar/almoço/café têm respectivamente 2/2/1 páginas. Conferidos períodos e marcações do corpo das tabelas; nenhum tem campus explícito. Mantidos fora do índice ativo. |
| F07 | Resolução 399/2025 local, 11 páginas: art. 51 na p. 10 revoga Resolução 124/2021; art. 52 na p. 11 prevê vigência na publicação (BSE de 28/03/2025). Não certificada ausência de alterações posteriores. PDF ativo preservado. |
| F08–F10 | IN17/2022, IN7/2021 e IN46/2025 sem originais locais. Alegações de revogação e regras não verificadas nesta missão; nada incorporado como norma atual. |
| F11 | IN49/2025 é citada no preâmbulo do edital local, p. 1. A citação não comprova seu teor, tabela de preços nem revogação da IN46. |
| F12 | Edital 114/2026 local, 3 páginas, público internacional específico e semestre 2026/2. Correção importante: 28/11/2026 é vigência de subsídios no item 7.2, p. 2, e não prazo geral de inscrição, como pode sugerir o manifesto. PDF preservado. |
| F13, F21 | Formulários de reclamação/intoxicação sem cópia conferível. Não incorporados como canais comprovados nesta missão; usado somente e-mail institucional do guia. |
| F14–F17 | Páginas locais CPAN/CPAQ/CPTL sem snapshot. Divergências são relatos da pesquisa, não confrontação independente. Nenhum horário ou preço exclusivo dessas páginas foi adotado. |
| F18 | URL de acesso ao Guia já declarada no projeto, sem nova verificação online. Detalhes conferidos no PDF local. |
| F19 | Página alegadamente histórica, sem original local e desnecessária à base atual. Preços antigos não incorporados. |
| F20, F25 | Contratos/anexos e IN52/2026 sem original pertinente conferido; não incorporados. |
| F22–F23 | Endereços de Identidade e Siscad constam do Guia, p. 7, inclusive links. URLs preservadas/explicitadas; serviços não acessados nem cadastro executado. |
| F24 | Fluxo de pós-graduação exclusivo de página não preservada. Não incorporado. |

URLs foram lidas e associadas às respectivas alegações, mas não acessadas. A
data de consulta 18/11/2026 do dossiê permanece uma declaração da pesquisa; não
é atribuída ao Codex nem transformada em data atual de conversas. Também não é
prova de publicação editorial. A natureza institucional de um domínio não basta
para atestar atualização, revogação ou aplicação a Campo Grande.

### Cardápios e limites da evidência local

Os três PDFs têm pratos previstos para 16–19/11/2026 e marcações temporárias
posteriores. O almoço indica 20 como feriado e 21 como não letivo; o café indica
ambos como feriado; jantar tem colunas até 20. As categorias são do documento,
não certificação jurídica de feriado nem comprovação de atendimento real.
No almoço de 16/11, a tabela p. 1 diz polenta e os ingredientes p. 2 dizem
mandioca: divergência confirmada. Os arquivos locais foram renomeados; não é
possível verificar pelo nome local o intervalo da URL remota F05. Datas no corpo
foram conferidas, sem deduzir campus ou oferta efetiva.

Nenhum desses pratos, tabela semanal, candidato histórico ou relatório de
conflitos foi copiado para `documentos/`. Não existe filtro temporal novo: a
decisão conservadora foi excluir os menus datados e orientar consulta ao canal.

## Seleção dos nove candidatos

Nenhum arquivo foi copiado integralmente. A integração foi técnica e assistida
por IA; aprovação manual dos novos documentos pelo grupo continua pendente.

| Candidato (relativo a RAG_CANDIDATOS) | Destino/decisão e motivo |
|---|---|
| `cardapio/consulta_cardapio_oficial.md` | Aceito parcialmente, reescrito sem comandos ao LLM nem instruções de implementação; novo documento curto de consulta, sem pratos históricos. |
| `cardapio/cardapios_2026_11_16_a_21_NAO_INDEXAR.md` | Rejeitado para corpus ativo: temporal e campus não confirmado. O nome não impede indexação recursiva. |
| `horarios/horarios_cidade_universitaria.md` | Fatos conferidos já existentes; preservado documento atual, sem criar duplicata. |
| `horarios/horarios_outros_campi_CONFLITOS.md` | Relatório não indexado. Horários categóricos CPAQ/CPAN removidos do resumo e substituídos por limite de confirmação, sem adotar números web. Três Lagoas mantido conforme Guia. |
| `regras_uso/procedimentos_comprovados.md` | Aceita parte conferida no Guia e integrada ao documento existente. Links/formulários não conferidos foram descartados. |
| `cadastro/cadastro_e_identificacao.md` | Mantidos requisitos do Guia e explicitadas URLs. Descartados fluxo de pós-graduação e prazo bienal sem original. Acrescentado limite de atuação do chatbot. |
| `valores/subsidio_2026.md` | Mínimos factuais já existentes preservados. Acrescentadas ausência do integral numérico e delimitação do edital; sem novos preços. |
| `recarga_creditos/limites_documentais_pagamento.md` | Aproveitado limite de comprovação; preservada experiência declarada do grupo, sem negar existência de créditos por ausência de prova. |
| `geral/visao_geral_ru.md` | Não copiado: público já documentado e endereço do RU não comprovado. Criado somente resumo de contatos do Guia e limite de localização. |

Os procedimentos de serviço agora aparecem em `regras_uso` porque o filtro por
intenção não acessa `cardapio`: o resumo seletivo evita a lacuna anterior sem
duplicar o PDF inteiro. O Guia comprova salada/arroz/feijão à vontade (pp. 10/12),
proteínas e guarnição servidas uma vez pelo colaborador (pp. 10/11), sobremesa
em uma porção de 150 g (pp. 11/12), vegetarianismo e consulta ao nutricionista
(p. 13), contatos (p. 4). Não foi generalizado o serviço da sobremesa como
necessariamente feito por funcionário, nem criada garantia sobre alergênicos.

## Comparação da recuperação antes/depois

Mesmo código, TF-IDF, k=4, mínimo 0,05 e mesmas perguntas/filtros. O treinamento
de classificadores não participou da comparação. Atualizar o índice documental
recalcula IDF; escores entre corpora não são probabilidades nem medida de acerto.

| ID | Cosseno do 1º antes → depois | Fonte do 1º depois | Leitura qualitativa do top 4 |
|---|---|---|---|
| Q01 | 0,266 → 0,385 | `cardapio/consulta_cardapio_oficial.md` | Agora recupera canal e ausência de cardápio datado; antes só composição. |
| Q02 | 0,227 → 0,391 | `cardapio/consulta_cardapio_oficial.md` | Canal de consulta em 1º; antes não havia URL de consulta aos cardápios. |
| Q03 | 0,325 → 0,309 | `geral/contatos_ru.md` | Contato e limite de localização em 1º; endereço exato continua sem prova. |
| Q04 | 0,373 → 0,329 | `horarios/horarios_2026.md` | Trecho de Campo Grande em 1º antes e depois, com horários preservados. |
| Q05 | 0,420 → 0,487 | `horarios/horarios_2026.md` | Quadro categórico substituído por necessidade de confirmação, sem importar versão web. |
| Q06 | 0,338 → 0,441 | `horarios/horarios_2026.md` | Quadro categórico substituído por necessidade de confirmação, sem importar versão web. |
| Q07 | 0,274 → 0,260 | `valores/valores_2026.md` | R$ 1,00/R$ 3,00 e elegibilidade permanecem no 1º trecho. |
| Q08 | 0,329 → 0,510 | `valores/valores_2026.md` | Agora o 1º trecho explicita ausência de quantia integral comprovada. |
| Q09 | 0,328 → 0,297 | `cadastro/requisitos_subsidio_2026.md` | Lista completa preservada no top 4 (3º); primeiro resultado agora é ressalva de cadastro. |
| Q10 | 0,516 → 0,339 | `recarga_creditos/formas_de_pagamento.md` | Agora o 1º trecho contém atribuição do relato e limite institucional. |
| Q11 | 0,072 → 0,366 | `regras_uso/regras_de_uso_2026.md` | Antes somente contato; agora serviço à vontade em 1º e porções individuais em 2º. |
| Q12 | 0,240 → 0,355 | `regras_uso/regras_de_uso_2026.md` | Limitação sobre marmita/fila em 1º, sem permissão ou proibição inferida. |

Resultado final: **10 documentos, 83 trechos**, assinatura
`d4c1c697863a38f8`, diferente do baseline. A lista de requisitos de cadastro
permanece completa entre os primeiros quatro trechos, mas passou ao terceiro:
há perda de prioridade, não perda da evidência entregue. Horários CG e preços
subsidiados continuam em primeiro. Persistem ruído da resolução geral e outros
campi entre resultados secundários. Não se afirma qualidade universal nem
precisão@k de benchmark; este é um roteiro pequeno de regressão documental,
sem ajuste de representações, limiares ou modelos.

## Respostas fixas alteradas

Somente três textos de `intencoes.*.resposta` em `grupo.yaml`:

- `cardapio`: falta de cardápio com data/campus confirmados e URL de consulta;
  distingue publicação planejada de refeição efetivamente servida.
- `recarga_creditos`: relato de Pix/cartões preservado como experiência;
  documentação oficial não confirma meios nem existência/inexistência de recarga.
- `regras_uso`: procedimentos do Guia com limite de abrangência e contato, sem
  criar regulamento de marmita, fila ou outras condutas.

Descrições, intenções, persona, contatos configurados, representações, modelo,
limiar, rotas e estrutura YAML permanecem iguais. Nenhuma mudança de código foi
necessária ou realizada. `cardapio_2026.md` e os dois PDFs ativos foram preservados.

## Lacunas e próximas ações

O endereço específico do RU não foi incorporado: o endereço do Conselho ou da
PROAES nos rodapés de atos não comprova localização do restaurante. Obter fonte
oficial localizável para endereço, horários atuais CPAQ/CPAN, meios de pagamento,
recarga e valor integral de Campo Grande. Não deduzir proibição/permissão de
marmita, mochilas, comida externa, som, fotografias, acompanhantes ou prioridade.
O acesso institucional não equivale a subsídio automaticamente concedido.

A Resolução 399 trata também de outros auxílios; critérios gerais, como a renda
do art. 46, não foram transpostos ao subsídio de refeições do Guia. O teor da
IN49/2025 e a cadeia normativa completa continuam sem conferência; não foram
inventadas revogações. Atualizações de contatos e calendário dependem da unidade.

O responsável informou nesta missão que já demonstrou integração real com
OpenRouter/GPT-6 Luna. Isso é registrado como declaração do responsável, não
execução pelo Codex ou validação remota destes novos documentos. Depois da
conferência manual, repetir demonstração factual em ambiente autorizado e
levar a proveniência real ao artigo/vídeo, sem expor segredos. Avaliação final
única depende de autorização própria e não foi iniciada.

## Testes, contratos e limitações de execução

Comandos efetivamente executados, sem OpenRouter:

```bash
.venv/bin/python -B -m unittest discover -s tests
.venv/bin/python -I -B scripts/indexar_documentos.py --buscar 'Qual horário de almoço e jantar do RU em Campo Grande?' --intencao horarios
.venv/bin/python -I -B scripts/indexar_documentos.py --forcar
.venv/bin/python -I -B scripts/indexar_documentos.py --buscar 'Em qual site oficial vejo os cardápios de café da manhã, almoço e jantar?' --intencao cardapio
git diff --check
```

- **149 testes aprovados**, sem ignorados; nenhum arquivo de teste ou código
  alterado e nenhuma biblioteca acrescentada.
- A consulta CLI anterior à edição foi bem-sucedida. Após a edição, `--forcar`
  construiu o índice em memória, mas falhou na gravação. A consulta CLI posterior
  também detectou automaticamente que os documentos mudaram e reconstruiu o
  índice, porém não chegou a imprimir a busca por falhar ao salvar o cache.
  A consulta e comparação posterior foram efetivamente realizadas pela API
  `BaseConhecimento.buscar` em memória, não atribuídas a uma CLI concluída.
- O bloqueio foi `PermissionError: Operation not permitted` ao gravar
  `.vectordb/indice.joblib`. Nenhuma permissão foi ampliada. Persistência real do
  índice novo permanece pendente no terminal autorizado. Serialização e leitura
  com joblib em memória preservaram assinatura e resultados das 12 perguntas.
- SHA-256 inicial/final **igual em 44 arquivos**: conjuntos, modelos, três
  oficiais, três módulos do RAG, dependências, notebook, resultados 08/09 e
  quatro PDFs brutos. Nenhuma inspeção semântica do teste foi realizada.
- Comparação estrutural do YAML confirmou somente as três respostas acima;
  `roteamento.limiar_tema=0.6`, `llm.modelo=openai/gpt-6-luna`, todas as demais
  chaves, valores e interfaces ficaram iguais. Rotas e classes não mudaram.
- As dez fontes ativas têm correspondência exata no catálogo; nenhum candidato
  histórico/relatório foi indexado. Os dois PDFs já ativos foram preservados.
- Os 18 materiais gerados listados em `INTEGRIDADE_ARQUIVOS_GERADOS.json`
  coincidem em tamanho e hash com seu manifesto. Essa verificação não autentica
  os originais ausentes, as URLs ou a vigência das alegações da pesquisa.
- As 25 entradas anteriores da tabela de uso de IA foram preservadas; as novas
  entradas distinguem pesquisa recebida de integração realizada. Nenhuma revisão
  humana do novo corpus foi inventada.
- `git diff --check` sem erros; avaliação oficial, verificador, treinamento,
  consulta de credenciais e chamadas de API não executados.

### Hashes locais para rastreabilidade

| Arquivo | SHA-256 inicial e final |
|---|---|
| `referencias/_brutos/guia_ru_2026.pdf` | `13d5879325b950c519b5842668b3ba084f7b1303e919755567e4f0d9605b36f7` |
| `referencias/_brutos/cardapios/almoco.pdf` | `5cc526da70bb4ea6ff0ec5f4419fcacda69d92d256928b6441d683091bffae1a` |
| `referencias/_brutos/cardapios/jantar.pdf` | `aa54449c2356ad9d1e38c71149f528aab2ba671cb609b81058363dd0f2a2326a` |
| `referencias/_brutos/cardapios/cafe.pdf` | `c75d3a81777a7bded853f68449af24f1118106db054c4281a04c942f29ba2f73` |
| `dados/treino.csv` | `fc260493bf144e3a6b5ecac2e2e7064f31b53dda597948cfc8e689fea5b665f5` |
| `dados/teste.csv` | `fa760e167d565a9a3e5bd015465c4ec945f7855e0bd78b5542dc561e21ea9b81` |

Esses hashes identificam os arquivos locais; não demonstram igualdade com
binários de URLs que não foram baixadas nesta missão. O guia é citado por página
física. Não foram incluídos novos PDFs nem modificados originais.

### Persistência a executar pelo responsável

Em terminal com escrita autorizada, na raiz do projeto, sem necessidade de chave:

```bash
.venv/bin/python -B scripts/indexar_documentos.py --forcar
.venv/bin/python -B scripts/indexar_documentos.py --buscar 'Em qual site oficial vejo os cardápios de café da manhã, almoço e jantar?' --intencao cardapio
.venv/bin/python -B scripts/indexar_documentos.py --buscar 'Posso repetir arroz, feijão, salada, proteína e sobremesa no RU?' --intencao regras_uso
```

O resultado esperado do índice é dez documentos e 83 trechos, sem conexão externa.
Essa tarefa de persistência não é nova autorização para avaliação final ou API.

## Arquivos e commits atômicos pendentes

Lista exata de arquivos desta missão:

```text
documentos/FONTES.md
documentos/LEIAME.md
documentos/cardapio/consulta_cardapio_oficial.md (novo)
documentos/geral/contatos_ru.md (novo)
documentos/cadastro/requisitos_subsidio_2026.md
documentos/horarios/horarios_2026.md
documentos/recarga_creditos/formas_de_pagamento.md
documentos/regras_uso/regras_de_uso_2026.md
documentos/valores/valores_2026.md
grupo.yaml
USO_DE_IA.md
docs/AUDITORIA_INTEGRACAO_DOSSIE_2026.md (novo)
```

O staging desses documentos e da configuração foi tentado com caminhos explícitos
e bloqueado ao criar `.git/index.lock` (`Operation not permitted`). Nenhum commit
foi feito e nenhuma permissão foi ampliada. Comandos para o responsável, após
conferir o escopo, na branch `feature/rag-openrouter-rangot`:

```bash
git diff --check
git add -- documentos/FONTES.md documentos/LEIAME.md documentos/cardapio/consulta_cardapio_oficial.md documentos/geral/contatos_ru.md documentos/cadastro/requisitos_subsidio_2026.md documentos/horarios/horarios_2026.md documentos/recarga_creditos/formas_de_pagamento.md documentos/regras_uso/regras_de_uso_2026.md documentos/valores/valores_2026.md grupo.yaml
git diff --cached --name-only
git diff --cached --check
git diff --cached
git commit -m "docs(rag): integrar fatos conferidos e limites das fontes"

git add -- USO_DE_IA.md docs/AUDITORIA_INTEGRACAO_DOSSIE_2026.md
git diff --cached --name-only
git diff --cached --check
git diff --cached
git commit -m "docs(ia): registrar curadoria e validacao documental 10B"
```

Os comandos não incluem dossiê bruto, PDFs de pesquisa, índice local, dados
privados, modelos ou resultados científicos. Não executar push nem avaliação
oficial como parte destes commits.
