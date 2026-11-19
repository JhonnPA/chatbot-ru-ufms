# Prompts e proveniência da geração sintética — RANGOT

## Geração complementar 07D e conferência 07E

- Ferramenta: **ChatGPT**, interação textual; o registro relata Python 3 para escrita e validação dos arquivos.
- Modelo declarado pelo registro recebido: **GPT-6**. Identificador técnico/build e parâmetros de amostragem não informados; esta sessão não os verificou externamente.
- Data declarada da geração: **18/11/2026**. Lote único: **07D-L01**; registros lógicos 1–125 (linhas 2–126 do CSV entregue).
- Fontes declaradas: exclusivamente os anexos INSTRUCOES.md e treino_autorizado.csv, com 425 exemplos autorizados (268 humanos, 157 LLM).
- O responsável informou conversa separada sem acesso ao teste. O registro confirma restrição de fontes, mas ressalva que não comprova isolamento físico/virtual. Não declarar essa comprovação como concluída.
- Geração diretamente no ChatGPT, **sem OpenRouter**, conforme o registro fornecido; nenhuma chamada de geração ocorreu na Missão 07E.
- Todas as 125 novas frases mantêm origem=llm; não há geração humana nem aprovação manual inventada.
- Distribuição gerada: recarga_creditos=1, cadastro=5, regras_uso=7, chitchat=54, fora_dominio=58.
- SHA-256 do complemento original: 7e4357fb1b24a7b337a75a6707709509d2108f4ef9d6c16479a48f31cf24526a.
- SHA-256 do registro privado original REGISTRO_GERACAO_07D.md: 9cbb7641bf50ab582beca306208afaf22455521a137251e8595c35755da655a1.
- O arquivo privado original contém a resposta integral do lote, em ordem idêntica à do CSV. Este documento transcreve abaixo o prompt e o anexo de instruções efetivamente registrados, sem reconstruir prompts não fornecidos.

A curadoria assistida por Codex da Missão 07E examinou individualmente os 125 textos e recomenda 124 como adequados. A candidata G07D:013 foi separada por forte proximidade semântica com S0087:C07, já pertencente ao treino, para decisão do responsável. Nenhum rótulo foi corrigido por comparação com o teste. Não houve duplicatas normalizadas ou interseções normalizadas com treino/teste, nem sinais no detector existente de proximidade entre novas frases e teste. Esses controles não garantem detectar toda paráfrase semântica.

A conferência final humana sobre as 125 candidatas permanece pendente. O treino proposto privado tem 549 exemplos, 268 humanos e 281 LLM (48,82% humano), faltando uma frase de regras_uso. O CSV oficial completo não foi materializado. Se o responsável aceitar a distinção do caso sinalizado, a projeção é 550 e 48,73% humano. Não houve treinamento ou avaliação final.

O registro não esclarece ferramenta/modelo/prompts da geração sintética anterior das 132 linhas; essa pendência histórica permanece. Os exemplos fictícios de testes de software não são dados científicos.

## Prompt da conferência 07E (resumo da solicitação real)

“MISSÃO 07E — Validar as 125 frases sintéticas e finalizar os dados do RANGOT”: verificar individualmente rótulos, naturalidade, diversidade, duplicatas, paráfrases e contaminação, preservar origem llm e teste, produzir conferência privada com recomendações, construir treino completo proposto somente se todos os requisitos passarem e registrar a revisão humana ainda pendente. Não gerar substituições, treinar ou avaliar modelos.

## Prompt integral efetivamente recebido (mensagem do solicitante)

<details>
<summary>Expandir prompt do usuário</summary>

```text
# RANGOT — Missão 07D: geração isolada de dados sintéticos

Estou desenvolvendo o projeto RANGOT, chatbot acadêmico do Restaurante Universitário da UFMS.

Anexei exclusivamente dois arquivos:

- INSTRUCOES.md
- treino_autorizado.csv

Leia as instruções e analise os exemplos de treinamento.

Não utilize arquivos externos, repositórios conectados, memórias de conversas anteriores ou exemplos de teste. Trabalhe exclusivamente com os dois anexos.

## Objetivo

Gerar 125 frases sintéticas inéditas para completar o treinamento dos classificadores.

Quantidades obrigatórias:

- recarga_creditos: 1
- cadastro: 5
- regras_uso: 7
- chitchat: 54
- fora_dominio: 58

## Requisitos

1. Use frases naturais de estudantes brasileiros.
2. Varie significativamente vocabulário, estrutura e estilo.
3. Inclua escrita formal, informal, abreviações e erros naturais.
4. Evite repetições, paráfrases triviais e frases quase idênticas.
5. Chitchat deve conter conversa social sem solicitações sobre o RU.
6. Fora_dominio deve incluir assuntos universitários vizinhos ao RU, especialmente negativos difíceis.
7. Todas as frases geradas devem ter origem llm.
8. Não copie exemplos do arquivo de treinamento.
9. Não invente autoria humana.
10. Não utilize nem solicite o conjunto de teste.

## Entregáveis

Crie efetivamente dois arquivos:

gerados_complementares_07d.csv

CSV UTF-8 com exatamente as colunas:

texto,intencao,origem

REGISTRO_GERACAO_07D.md

Registre ferramenta, modelo, prompt, distribuição por classe, critérios de diversidade e limitações.

Valide programaticamente as 125 linhas, os rótulos, as origens e a ausência de duplicatas normalizadas entre os dados fornecidos e os gerados.

Disponibilize os dois arquivos como anexos para download.

Não declare que foram aprovados pelo grupo ou que já passaram pela auditoria contra o teste reservado.

Não treine classificadores nesta tarefa.
```

</details>

## Instruções efetivamente fornecidas no anexo INSTRUCOES.md

<details>
<summary>Expandir instruções do anexo integral</summary>

```markdown
# Pacote exclusivo de treinamento — RANGOT

Contém somente exemplos de treinamento autorizados e definições públicas de intenções.
Não copie outros arquivos do repositório para o ambiente gerador.

## Intenções

- cardapio: cardápio do dia ou da semana.
- horarios: horários de funcionamento.
- valores: preços das refeições e isenções.
- recarga_creditos: recarga de créditos e formas de pagamento.
- cadastro: cadastro e acesso ao RU.
- regras_uso: regras de uso do RU.
- chitchat: saudações, agradecimentos, despedidas e interação social.
- fora_dominio: pedidos de outros assuntos ou serviços, sem solicitação sobre o RU.

## Quantidades ainda sem exemplos autorizados

- cardapio: 0.
- horarios: 0.
- valores: 0.
- recarga_creditos: 1.
- cadastro: 5.
- regras_uso: 7.
- fora_dominio: 58.
- chitchat: 54.

As cinco candidatas suplementares foram conferidas e ratificadas pelo responsável na Missão 07C e já estão neste treino. O déficit recalculado é de 125 exemplos: gerar somente estas quantidades, sem ampliar classes já completas.
Nesta sessão não houve geração. A geração futura ocorre exclusivamente no ambiente isolado descrito abaixo.

## Instruções para a futura geração em ambiente isolado

Use somente treino_autorizado.csv como exemplos; não busque outros arquivos do projeto.
Gere perguntas de usuários, nunca respostas factuais inventadas sobre serviços do RU.
Todo texto gerado recebe origem=llm. Preserve os oito rótulos, sem usar dominio ou esclarecer.
Varie construções, objetivos, extensões, registro formal/informal, elipses reconhecíveis e erros de digitação.
Não infle o volume trocando apenas saudação, pontuação, grafia ou partículas de um template.
Para fora_dominio, varie serviços UFMS: secretaria, assistência, estágio, TI, calendário e mobilidade;
combine negativos fáceis e difíceis com palavras compartilhadas com o RU.
Não invente dados pessoais nem regras, valores ou funcionamento institucional.
Registre ferramenta/modelo e prompts reais; submeta cada candidata à revisão e deduplicação antes de usar.

## Isolamento obrigatório e execução humana futura

Use outro computador ou uma VM nova sem checkout do projeto, sem pastas do host montadas, sem diretórios compartilhados e sem acesso aos arquivos do teste. Um novo diretório, conversa ou sessão no mesmo host com acesso ao repositório não é isolamento suficiente. Não reutilize esta conversa como contexto do gerador.

Leve somente INSTRUCOES.md e treino_autorizado.csv. Não copie credenciais, configurações do agente, históricos, formulários, manifests, scripts do projeto ou outros arquivos. A origem llm das 157 frases já sintéticas permanece inalterada; as 268 humanas são apenas referências autorizadas de treinamento.

No ambiente isolado, abra uma conversa nova na ferramenta escolhida pelo responsável e forneça somente estes dois arquivos. Use este documento integralmente como instrução. Não há nesta missão modelo gerador escolhido ou execução comprovada. Nenhuma chamada ao OpenRouter é necessária ou autorizada por este procedimento. A ferramenta deve trabalhar sem acesso ao checkout original, ao teste ou ao histórico desta sessão.

## Entrega do gerador e rastreabilidade

Entregue candidatas_complemento.csv em UTF-8, separado por vírgula, cabeçalho texto,intencao,origem, com exatamente 125 linhas de dados nas quotas acima e origem=llm em todas. Não misture respostas do bot com perguntas de usuários. Para perguntas curtas, preserve uma intenção recuperável; múltiplas intenções ou ambiguidades reais devem ir para análise, sem aprovação forçada.

Além do CSV, produza registro_geracao.md com: ferramenta, identificador real do modelo/versão quando exposto (caso contrário, não informado), data da execução, prompts integrais efetivamente enviados e respostas originais por lote, parâmetros disponíveis e associação de cada linha ao lote de origem. Não invente identificadores, execuções ou revisão humana. IDs de lote e número da linha podem ser registrados neste arquivo auxiliar sem acrescentar colunas ao CSV.

Para os 58 fora_dominio, priorize negativos difíceis de outros serviços UFMS que compartilhem vocabulário com o RU (p.ex., acesso, horários, valores, cadastro e pagamento), variando finalidade e serviço. Não faça apenas substituição de nomes em templates. Para chitchat, varie funções sociais e estilos mantendo o rótulo inequívoco. As cinco classes deficitárias devem ter diversidade lexical, semântica e de extensão, inclusive informalidade e erros plausíveis de digitação.

O resultado é uma lista de candidatas, sem aprovação automática. Após devolução ao curador, conferir individualmente semântica, classe, origem, duplicatas normalizadas e famílias de paráfrases dentro do complemento e contra o treino. A checagem de interseções com o teste é feita separadamente pelo curador no ambiente que guarda o teste, apenas para prevenir vazamento, sem transmitir exemplos ou detalhes do teste ao gerador.

Somente após revisão e autorização, juntar ao treino e conferir: 50 por cada intenção RU, 100 chitchat, 150 fora_dominio, pelo menos 20% humano/coletado, ausência de sobreposição com o teste. Com estas quotas e 268 humanas, a projeção é 550 exemplos e 48,73% humano. Não declarar treinamento, métricas ou avaliação final como executados.

```

</details>

## Complemento final fornecido e curadoria — Missão 07G

O responsável forneceu cinco candidatas independentes de `regras_uso`, todas
`origem=llm`, no arquivo privado `dados/_brutos/candidatas_regras_07g.csv`.
SHA-256 da fonte: `a03f06e11ffe6aeb6c4965eec5b3d0849af0130def86a8dd2ce79d7c5a19d003`.
Ferramenta, modelo, prompt e comprovação do ambiente de geração dessas cinco não
foram fornecidos. Esses metadados continuam pendentes; não atribuir a geração
ao ChatGPT/GPT-6 da 07D nem inventar um prompt de geração. A origem LLM foi
declarada expressamente pelo responsável. Esta sessão não gerou novas frases.

Solicitação real de curadoria (resumo): “MISSÃO 07G — Conclusão definitiva dos
dados do RANGOT”: analisar cinco candidatas, selecionar no máximo uma distinta,
natural e inequivocamente de regras_uso, controlar duplicatas e contaminação sem
adaptar exemplos pelo teste e construir treino com os 549 anteriores e a selecionada.

O Codex examinou as cinco e selecionou G07G:003, terceira linha de dados (linha 4
do arquivo), sobre usar caixinha de som durante o almoço no RU. A intenção de
conduta e o domínio são explícitos; não se identificou paráfrase trivial no treino
nem sinal de contaminação. As outras quatro ficaram fora do conjunto final.
A decisão é curadoria assistida por IA sob autorização expressa, sem confirmação
de revisão manual individual do grupo. G07D:013 continua excluída.

O treino oficial foi materializado com 550 exemplos, 268 humanos e 282 LLM,
48,73% humano, atendendo aos mínimos por classe. SHA-256:
`fc260493bf144e3a6b5ecac2e2e7064f31b53dda597948cfc8e689fea5b665f5`.
As insuficiências descritas na conferência histórica 07E foram resolvidas nessa
etapa, preservando os registros anteriores. O teste foi usado apenas para
verificação de contaminação e conservou seus bytes e hash. Não houve treinamento
de classificadores nem avaliação final.
