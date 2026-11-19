# RAG e preparação do OpenRouter — Missão 10

## Estado e evidências

Validação realizada inteiramente offline na branch `feature/rag-openrouter-rangot`.
Foram aprovados **149 testes**: os 124 anteriores e 25 novos. O índice foi
construído em memória com **8 documentos e 77 trechos**. Os dois PDFs indexados
têm 14 páginas no total, todas com texto extraível pelo `pypdf`.

Não houve chamada ao OpenRouter, acesso a credenciais, treinamento, consulta a
frases do teste ou execução da avaliação/verificação oficial. O modelo configurado
continua `openai/gpt-6-luna`; disponibilidade e qualidade remotas não foram
comprovadas. O limiar de intenção permanece **0,60**, sem nova otimização.

Resultados observados estão em [rag_10_offline.json](../resultados/rag_10_offline.json).
O artefato contém somente perguntas fictícias, caminhos públicos e resultados de
integração; não contém exemplos do teste. As respostas do LLM foram simuladas.

## Arquitetura e limites do contexto

1. Os classificadores preservados das Missões 08/09 decidem escopo, intenção e
   eventual esclarecimento. A assinatura `construir_grafo(config, clf_escopo,
   clf_tema)` permanece compatível com seus argumentos opcionais existentes.
2. `chatbot/conhecimento.py` extrai Markdown, texto, HTML ou PDF e conserva
   títulos hierárquicos nos trechos. A representação configurada é TF-IDF de
   caracteres `(3, 5)`, com normalização e similaridade do cosseno.
3. A busca aceita apenas a intenção prevista e a pasta `geral`, com até quatro
   resultados e similaridade mínima configurada de 0,05. Não abre outras
   intenções quando esse filtro fica vazio; consultas sem vocabulário comum não
   devolvem trechos de similaridade zero.
4. Cada trecho informa caminho, página quando PDF e proveniência declarada em
   `documentos/FONTES.md`. Essa proveniência acompanha a resposta recuperada,
   mas não entra nas características usadas para calcular similaridade.
5. Instruções de comportamento permanecem na mensagem de sistema. Pergunta e
   documentos são codificados como dados JSON na mensagem de usuário; documentos
   não podem criar mensagens ou papéis de sistema. O histórico também é tratado
   como dado e não comprova informações factuais.
6. O LLM redige apenas a resposta da rota determinada. Não classifica nem altera
   a rota. Sem LLM, continuam as respostas fixas. Com LLM e sem evidência
   documental, o grafo responde deterministicamente que a informação é
   insuficiente, sem chamar o modelo remoto. Falha de API gera resposta fixa sem
   expor o texto bruto da exceção ao usuário.

Limites: trecho bruto de até 700 caracteres, até quatro trechos no prompt,
até 1.400 caracteres por trecho apresentado e 6.000 para o contexto formatado.
Pergunta e cada mensagem do histórico têm limite de 2.000 caracteres. O histórico
tem três turnos na configuração atual e limite de dez na função. São limites de
caracteres, não de tokens; não eliminam truncamento nem garantem obediência do
LLM. Metadados e títulos consomem parte do contexto.

## Documentos utilizados e autoridade

| Intenção/pasta | Documento efetivamente indexado | Autoridade e cobertura |
|---|---|---|
| `cardapio` | `cardapio/cardapio_2026.md` — 7 trechos | Reorganização do Guia Prático oficial de 2026. Composição geral de refeições; não comprova pratos para um dia ou semana específica. |
| `horarios` | `horarios/horarios_2026.md` — 6 trechos | Reorganização do guia, com horários por campus. Não comprova alterações excepcionais posteriores; distinguir Campo Grande dos demais campi. |
| `valores` | `valores/valores_2026.md` — 4 trechos; `valores/edital_114_2026.pdf` — 13 trechos, 3 páginas | Guia informa preços subsidiados e condições, sem quantia do valor integral. O edital é específico de PEC-G/PEC-PLE em 2026/2; não estender seus benefícios, público ou prazos a todos. |
| `cadastro` | `cadastro/requisitos_subsidio_2026.md` — 3 trechos | Reorganização do guia: requisitos e documentos de acesso com subsídio. Condições não autorizam inferir elegibilidade individual sem os dados pertinentes. |
| `regras_uso` | `regras_uso/regras_de_uso_2026.md` — 2 trechos | Texto do grupo registrando limite da pesquisa, sem regulamento específico de conduta localizado. Não fundamenta permissões ou proibições sobre marmitas, roupas, visitantes, recipientes ou equipamentos. |
| `recarga_creditos` | `recarga_creditos/formas_de_pagamento.md` — 4 trechos | Experiência dos integrantes em Campo Grande, novembro de 2026. Deve ser atribuída ao grupo e confirmada com o RU; não é norma oficial sobre Pix, cartões ou inexistência de créditos. |
| `geral` | `geral/resolucao_399_2025.pdf` — 38 trechos, 11 páginas | Documento oficial amplo de assistência estudantil. Pode apoiar questões de auxílio; não equivale a regulamento de conduta no refeitório. Vigência e alterações posteriores não foram verificadas externamente nesta missão. |

Todos os arquivos têm proveniência no catálogo. `FONTES.md` e `LEIAME.md` são
controle, não documentos de resposta. Arquivos ocultos e links simbólicos não
entram na listagem documental. O carregador não segue URLs nem abre caminhos
citados no catálogo. Os PDFs foram processados localmente; não foi necessário OCR.

O PDF bruto do guia não foi acrescentado porque duplicaria os quatro documentos
derivados. Os cardápios semanais em `referencias/_brutos/cardapios/` continuam
fora do índice: são temporários e precisam de data, campus e validade confirmados
antes de eventual inclusão. Nenhuma pesquisa externa foi realizada.

Há cobertura temática das seis intenções, mas **cobertura factual parcial**.
Recuperar um documento por semelhança lexical não comprova que ele responda à
pergunta. Os documentos gerais podem introduzir ruído. Não foi medida precisão
de recuperação em um benchmark nem alterado o protocolo científico 08/09.

## Correções e prevenção de informações inventadas

- Eliminada a expansão silenciosa da busca para intenções alheias.
- Preservados títulos ancestrais nos trechos para manter campus, assunto e
  condições próximos do conteúdo; o documento de cadastro ganhou título mais
  descritivo, sem mudança dos requisitos.
- Retirada a identificação indiscriminada dos trechos como oficiais e a
  apresentação da resposta fixa de `grupo.yaml` como documento substituto.
- Contexto documental separado das instruções de sistema, com orientação
  explícita contra comandos inseridos em fontes, perguntas ou histórico.
- Prompt exige reconhecer insuficiência, preservar datas, público-alvo e campus,
  atribuir relatos informais e citar somente caminhos recebidos. A data da
  execução não prova vigência documental.
- Menu geral identificado como geral, sem cardápio datado. Texto sobre regras
  agora registra ausência de fonte localizada, sem afirmar inexistência de normas.
- Resposta fixa de pagamento atribuída ao relato do grupo; resposta fixa de
  cardápio qualificada como informação geral do guia. Somente esses dois valores
  foram alterados em `grupo.yaml`; sua estrutura foi preservada.

Essas medidas reduzem risco; não demonstram que o GPT-6 Luna sempre recusará
inferências ou instruções maliciosas. A conferência real deve comparar a resposta
ao trecho e à autoridade da fonte. Em especial, pergunta sobre preço integral,
prato de data específica ou regra não documentada deve reconhecer a lacuna.

## Índice e atualização

O cache local continua `.vectordb/indice.joblib`, ignorado pelo Git. A versão do
índice passou a 2. A assinatura considera conteúdo e caminhos dos documentos,
`FONTES.md`, configuração da base, intenções e código do módulo. Mudanças nesses
elementos invalidam o cache, inclusive alterações de conteúdo do mesmo tamanho.
Cache incompatível/corrompido é reconstruído pela API existente.

Nesta sessão o índice novo foi construído **somente em memória**: o shell tem
permissão de leitura. Serialização/carregamento em memória e caminhos de
invalidação/reconstrução foram testados com mocks. A persistência do índice real
será feita pelo responsável no terminal autorizado com os comandos abaixo.

## Testes offline realizados

Comando executado, sem gravação de bytecode:

```bash
.venv/bin/python -I -B -m unittest discover -s tests
```

Resultado: **149 testes, todos aprovados, sem testes ignorados**. Os 25 novos em
`tests/test_rag.py` cobrem leitura real da base/PDFs, recuperação das seis
intenções e de fontes gerais, filtro estrito, proveniência, hierarquia e tamanho
de trechos, HTML, assinatura/cache, prompt e limites, roteamento e falhas
simuladas. O cliente remoto e a leitura de chave são bloqueados por mocks nos
testes do grafo, inclusive no cenário de chave ausente.

Doze cenários com classificadores controlados verificaram os componentes:
horário, valores, cadastro, pagamento, cardápio datado e regra ausente chegaram
à intenção e ao LLM simulado com fontes; fora de domínio ficou em resposta fixa;
ambiguidade e duas intenções com probabilidades incertas pediram esclarecimento;
falha simulada retornou resposta fixa; sem fonte não chamou LLM; ausência de chave
simulada manteve o funcionamento offline. Isso comprova encadeamento, não a
correção de uma resposta que ainda não foi gerada pelo serviço remoto.

Uma execução adicional de nove perguntas fictícias com os **modelos reais
preservados** mostrou limites que não foram ocultados nem corrigidos por tuning:

- Horário, valores, cadastro e regra não documentada seguiram as intenções
  esperadas; biblioteca foi recusada como fora do domínio.
- Pergunta sobre Pix pediu esclarecimento (confiança de intenção 0,4633).
- Cardápio datado foi classificado incorretamente como `horarios` (0,8727).
- “Como uso isso?” foi classificado como `cadastro` (0,7236) e recuperou apenas
  material geral; isso não torna a pergunta documentalmente respondível.
- Pergunta com cardápio e preço pediu esclarecimento (0,5276). O sistema não
  tem detector explícito de múltiplas intenções: probabilidades altas podem
  selecionar apenas uma, sem garantia de esclarecimento.

Não são estimativas de desempenho, resultados do teste congelado ou justificativa
para mudar o limiar 0,60. O LLM não deve corrigir a rota imposta pelo classificador;
deve reconhecer quando o contexto daquela rota não responde à pergunta.

## Teste real pelo responsável, fora da sessão do Codex

Executar em terminal privado e ambiente autorizado, separado da sessão do Codex,
na raiz de uma cópia com estas alterações e dependências já instaladas. Manter
este checkout do Codex sem segredos. Não copiar credenciais para o pacote,
notebook, Git ou arquivos de configuração; não colar a chave na conversa.
Se uma chave anterior tiver sido exposta, revogá-la e obter substituta com o
responsável/professor antes do teste. Esta missão não constatou comprometimento.

Primeiro reconstruir/verificar o índice, sem API:

```bash
.venv/bin/python -I -B scripts/indexar_documentos.py --forcar
.venv/bin/python -I -B scripts/indexar_documentos.py --buscar "Qual horário do almoço em Campo Grande?" --intencao horarios
.venv/bin/python -I -B scripts/conversar.py --sem-llm --depurar
```

Depois, em terminal interativo privado, o comando abaixo solicita a chave com
entrada oculta e a mantém apenas no processo filho. Não há chave literal no
comando/histórico; entrada vazia cancela antes de iniciar o chatbot e antes de
qualquer procura alternativa de credenciais. O endereço público da API é fixado
explicitamente. **Este comando não foi executado pelo Codex.**

```bash
.venv/bin/python -I -B -c 'import getpass,os,runpy,sys; chave=getpass.getpass("Chave OpenRouter (entrada oculta): ").strip(); assert chave, "Chave não informada; teste cancelado"; os.environ["OPENROUTER_API_KEY"]=chave; del chave; os.environ["OPENROUTER_BASE_URL"]="https://openrouter.ai/api/v1"; sys.argv=["scripts/conversar.py","--depurar"]; runpy.run_path("scripts/conversar.py",run_name="__main__")'
```

O cliente usa o modelo configurado `openai/gpt-6-luna`. O roteiro não exige
consultar arquivos de segredos nem configurar credenciais nesta sessão.
Digitar `sair` encerra o processo. O script de conversa não imprime a chave.

Experimentar perguntas fictícias da tabela de cenários, sem abrir o teste oficial.
Verificar rota, confiança, trechos e atribuição na resposta. Para horário e
subsídio, comparar o texto produzido com o guia; para Pix, exigir atribuição ao
relato do grupo; para cardápio datado e regras ausentes, exigir reconhecimento da
insuficiência, sem inventar prato, permissão ou proibição. Usar pergunta de uma
intenção por vez quando o bot solicitar esclarecimento.

Uma chamada só está comprovada se houver resposta com `fonte_resposta=llm` e
contagem de chamadas bem-sucedidas maior que zero ao encerrar. O nome do modelo
no início da conversa não comprova execução; resposta fixa de fallback também
não comprova sucesso. Registrar apenas pergunta fictícia, rota, caminhos das
fontes, resposta revisada e uso agregado de tokens, sem segredos ou dados pessoais.

Sem resposta da API: a interface mantém fallback e marca falha. Somente no
ambiente privado do responsável, conferir autorização da chave (401), créditos
(402), disponibilidade do modelo indicado pelo professor (404), limite de
requisições (429) e conectividade. Não trocar o modelo exigido silenciosamente,
não compartilhar logs de autenticação e não publicar a chave nem parcialmente.

## Integridade e pendências antes da avaliação final

Hashes dos conjuntos mantidos, sem inspecionar exemplos do teste:

```text
treino: fc260493bf144e3a6b5ecac2e2e7064f31b53dda597948cfc8e689fea5b665f5
teste:  fa760e167d565a9a3e5bd015465c4ec945f7855e0bd78b5542dc561e21ea9b81
```

Modelos, scripts oficiais e resultados/notebook 08/09 foram preservados. A lógica
de obtenção de credenciais e a classe do cliente OpenRouter não foram alteradas.

Pendências: executar/conferir a conversa remota pelo responsável; obter fonte
oficial para pagamentos e regras específicas, valor integral e cardápios datados
quando necessários; verificar validade atual de editais e eventuais mudanças
institucionais. Confirmar também as pendências anteriores de proveniência 07G,
sem completá-las por suposição. Não há nova revisão humana presumida.

A avaliação oficial única e o verificador de entrega permanecem **não executados**.
O fechamento acadêmico, artigo e vídeo não fazem parte desta missão.

## Commits locais pendentes

O staging foi tentado apenas com os arquivos de código/testes e bloqueado pelo
sandbox ao criar `.git/index.lock` (`Operation not permitted`). Nenhuma permissão
foi ampliada e nenhum commit foi criado. Executar manualmente, na mesma branch,
após conferir os diffs. A implementação inclui as qualificações das fontes de
que o comportamento RAG depende; o segundo commit registra sua validação.

```bash
git diff --check
git add -- chatbot/conhecimento.py chatbot/llm.py chatbot/grafo.py tests/test_rag.py grupo.yaml documentos/FONTES.md documentos/LEIAME.md documentos/cadastro/requisitos_subsidio_2026.md documentos/cardapio/cardapio_2026.md documentos/recarga_creditos/formas_de_pagamento.md documentos/regras_uso/regras_de_uso_2026.md
git diff --cached --name-only
git diff --cached --check
git diff --cached
git commit -m "fix(rag): preservar contexto e autoridade das fontes"

git add -- docs/RAG_OPENROUTER.md resultados/rag_10_offline.json USO_DE_IA.md
git diff --cached --name-only
git diff --cached --check
git diff --cached
git commit -m "docs(rag): registrar validacao offline e teste seguro"
```

Não incluir `.vectordb`, dados privados ou credenciais. Não há push nem execução
da avaliação nos comandos acima.
