# Protocolo de auditoria dos dados do RANGOT

## Escopo e autoridade

A Missão 04 autoriza somente `scripts/auditar_dados.py`,
`tests/test_auditar_dados.py`, este protocolo e `USO_DE_IA.md`, na branch
`feature/curadoria-dados-rangot`. Os limites da Missão 03 registrados no contrato
são históricos; esta missão não autoriza formar os conjuntos finais.

Fonte científica: [enunciado oficial](../referencias/_brutos/enunciado_professor.pdf),
29 páginas, especialmente pp. 8–9, 17–20 e 22–27, e
[contrato compartilhado](CONTRATOS_COMPARTILHADOS.md). A ferramenta não executa
treino, avaliação final, verificador oficial, busca remota ou OpenRouter.

## Entradas e identificação

- `dados/_brutos/formulario_humano.csv`: 48 envios, 11 colunas. A primeira coluna
  é metadado e não entra na representação das células, manifesto ou console.
- `dados/_brutos/sinteticas_llm.csv`: 132 registros, 10 colunas. Uma linha contém
  várias respostas; 132 registros não equivalem a 132 frases.
- As origens `humano` e `llm` são vinculadas às fontes conforme confirmação do
  responsável. Não são inferidas pela fluência, formato ou conteúdo da mensagem.
- O programa abre somente esses dois caminhos fixos e rejeita links simbólicos
  nos caminhos antes da leitura. Valida largura e ordem das perguntas; alterações
  no formulário exigem revisar o esquema, sem adivinhar a nova correspondência.

IDs como `H0007:C03` e `S0007:C02` indicam fonte, sétimo registro de dados e coluna
original, ambos com posições começando em 1. Cabeçalho não é envio; uma resposta
multilinha continua pertencendo ao mesmo registro CSV. IDs só identificam a mesma
célula enquanto o arquivo bruto permanece na mesma versão, identificada por SHA-256.
Não identificam uma pessoa e não provam que envios diferentes sejam de autores distintos.

## Execução offline e manifesto

Na raiz do checkout, sem instalar dependências:

```bash
python3 -I -B scripts/auditar_dados.py
python3 -I -B scripts/auditar_dados.py --manifesto
python3 -I -B -m unittest discover -s tests -p test_auditar_dados.py -v
```

O primeiro comando resume contagens e planos. O segundo emite em stdout o
manifesto JSON completo, com células, rótulos propostos, motivos de revisão,
grupos de duplicatas, proximidades e planos. Ambos omitem textos, cabeçalhos,
timestamps e identificadores pessoais. Erros de entrada/argumentos não repetem
conteúdo recebido. Nenhum comando da ferramenta grava arquivos, cria conjuntos
ou atualiza o Git. `-B` e a configuração do carregador evitam caches Python.

A opção `--envios-teste` aceita uma lista de números de envio separados por
vírgula, sem espaços. Ela simula somente a divisão explicitamente informada,
inclusive a proposta de uma auditoria anterior, sem substituí-la pela busca
automática. IDs repetidos, inválidos ou fora do arquivo são recusados; o uso da
opção não registra aprovação humana.

O normalizador é a função existente em `chatbot/texto.py`, carregada diretamente
para evitar que `chatbot/__init__.py` importe dependências desnecessárias.
O manifesto registra hashes dos dois brutos, do script e do normalizador,
versão das regras e parâmetros, sem timestamp de execução: mesmas entradas,
código, normalizador e versão de Python devem produzir JSON idêntico.

Se o operador quiser guardar o manifesto, primeiro confirme que o destino é
ignorado pelo Git e só então redirecione a saída para a área privada:

```bash
git check-ignore -- dados/_brutos/auditoria_manifesto.json
# Prosseguir somente se o comando anterior confirmar que o caminho é ignorado.
python3 -I -B scripts/auditar_dados.py --manifesto > dados/_brutos/auditoria_manifesto.json
```

Essa gravação é opcional e manual. Não adicionar o manifesto bruto a commits.
A ferramenta não oferece exportação de textos; o revisor consulta cada célula no
CSV local pelo ID. Não enviar os brutos ou possíveis mensagens de teste a sessões
de geração sintética. Os logs públicos contêm apenas contagens e referências técnicas.

## Propostas automáticas e revisão humana

O programa distingue `rotulo_coluna` (expectativa da pergunta do formulário) de
`rotulo_sugerido` (regras lexicais explícitas). Não copia cegamente o rótulo da
coluna. A detecção de assunto externo tem prioridade; mensagens que misturam RU
e outro assunto são sinalizadas. Mais de uma intenção detectada gera pendência;
saudação não transforma pedido desconhecido em conversa social.

Vazios, ausência de texto normalizado, metarrespostas, possível dado pessoal,
múltiplas intenções e recarga sem domínio distinguível bloqueiam a candidatura
automática. Respostas curtas, alternativas separadas e divergências da coluna
recebem avisos adicionais. Textos normalizados iguais associados a expectativas
de coluna diferentes
recebem também `colunas_conflitantes`, mantendo a decisão humana pendente.
Esses sinais são incompletos: regras lexicais podem
errar com gírias, negações, elipses, ironia, erros de digitação e perguntas implícitas.

Todas as células, inclusive as candidatas, têm `revisao_humana=pendente` e
`aprovado=false`. “Candidata” significa apenas passagem pelos filtros automáticos;
não significa frase válida aprovada, qualidade semântica garantida ou teste congelado.
Não há importação de aprovações nem comando para marcar aprovação nesta versão.

O responsável deve revisar texto, rótulo, intenção dominante, proveniência e avisos.
Mensagens sem rótulo justificável ficam pendentes; não usar `esclarecer` como classe
do CSV. Revisão de rótulos não equivale à geração humana de frases pela IA.

## Duplicatas e possíveis paráfrases

1. Exatas: igualdade após aparar espaços nas extremidades, sem alterar os arquivos.
2. Normalizadas: aplicação de `chatbot.texto.normalizar`, com minúsculas, remoção
   de acentos/pontuação e espaços simples. Textos normalizados vazios não são
   agrupados como duplicatas.
3. Quase duplicatas: `SequenceMatcher` com razão ≥0,92 em textos normalizados de
   pelo menos 20 caracteres. A ordem lexicográfica das entradas torna o cálculo
   determinístico. Frases menores não são cobertas por esse sinal de caracteres.
4. Possíveis paráfrases: Jaccard ≥0,80, pelo menos três termos comuns, após retirar
   palavras funcionais e aplicar um pequeno mapa explícito de variantes lexicais.
   Números e negações são preservados. É um sinal lexical, não uma análise semântica
   por embeddings nem comprovação de equivalência.

Os dois últimos sinais servem à revisão. Similaridade alta pode ocorrer entre
perguntas diferentes; paráfrases reais podem passar despercebidas. Não há seleção
ou ajuste de modelo usando o teste. Os limiares acima são regras de integridade,
não o limiar de roteamento do chatbot, que será escolhido futuramente por CV.

## Viabilidade por envio e prevenção de sobreposição

A busca simula 29/19, 30/18 e 31/17 envios de teste/treino sem assumir que 30/18
seja ideal. Participações conectadas por duplicatas normalizadas entre candidatas
ficam no mesmo componente. Uma busca determinística de largura limitada mantém
três estados por combinação de tamanho e contagem social, priorizando cobertura
dos mínimos. Não encontrar solução não prova impossibilidade.

Todas as respostas candidatas de um envio seguem o mesmo lado. Deduplicam-se as
contagens de cada lado; uma proximidade com o teste põe a candidata correspondente
do lado de treino em quarentena, sem transferir frases entre conjuntos. O estoque
sintético exclui coincidências normalizadas com todo o bruto humano e proximidades
com a reserva proposta. Possíveis paráfrases continuam explicitamente pendentes.

O cálculo verifica interseções normalizadas entre candidatas dos dois lados.
Sintéticas jamais são atribuídas ao teste. Os planos não leem nem gravam
`dados/treino.csv` ou `dados/teste.csv`; são simulações de capacidade.

| Requisito | Treino | Teste |
|---|---:|---:|
| Por intenção RU | 50 | 15 |
| `chitchat` | 100 | 30 |
| `fora_dominio` | 150 | 40 |
| `humano` + `coletado` | ≥20% | 100% |
| Total mínimo para seis intenções | 550 | 160 |

`validar_minimos` verifica cada classe e a fração humana/coletada no total
informado, incluindo vazios/contagens inválidas. Nos planos, a proporção projetada
é o número de humanas candidatas que cabe nas quotas dividido por **550**, não
a proporção artificialmente alta do subconjunto humano ainda incompleto.
Reportam-se separadamente estoque sintético, falta por classe e necessidade de
origem humana. Havendo complemento indicado, o plano é condicionado à obtenção,
revisão e deduplicação futuras dessas frases; nada é gerado ou selecionado como
conjunto final. Mesmo um plano numericamente viável continua sem aprovação humana.

## Evidências e próximos passos

O script confere novamente os bytes dos dois arquivos ao terminar e falha se uma
entrada mudou durante a auditoria. Testes usam exclusivamente fixtures fictícias
de software, sem usar os brutos nem mensagens reservadas e sem convertê-las em
dados científicos de origem humana. São cobertos CSV, origem, normalização,
duplicatas, sinais lexicais, proporções, mínimos, agrupamento, sobreposição,
privacidade, determinismo e preservação das entradas.

As contagens semânticas de auditorias anteriores foram propostas não persistidas;
não são oráculo dos testes nem constantes para forçar 121 frases humanas.
A ferramenta deve expor divergências para revisão, não esconder insuficiências.
Após revisão humana, será necessária nova autorização para registrar decisões,
definir a divisão e congelar os CSVs finais. Somente treino/CV poderá orientar
modelos, hiperparâmetros, limiar e eventual geração futura.

### Fotografia reproduzível da Missão 04

Execução com Python **3.14.5** nos brutos disponíveis, com as regras desta versão;
nenhuma célula foi aprovada. Os 36 testes de software passaram. Duas emissões completas consecutivas
do manifesto tiveram conteúdo idêntico, e as entradas permaneceram iguais byte a byte.

Versões das entradas utilizadas, identificadas sem publicar conteúdos:

- Humano, SHA-256: `b27a639bc111689ca9a42c024e2b45f1f9b53f7879affc4b63799e417b5fc304`.
- Sintético, SHA-256: `87dd6717fb62280cda1cdb7fbb29c8b5730153cdaf3ccf49448998d73a0f44e8`.

| Medida | Humano | Sintético |
|---|---:|---:|
| Envios/registros | 48 | 132 |
| Células de resposta, incluindo vazias | 480 | 1.320 |
| Preenchidas | 479 | 1.232 |
| Distintas exatas | 466 | 1.232 |
| Distintas normalizadas | 456 | 1.114 |

Globalmente: oito grupos de duplicatas exatas, 111 normalizados, seis textos
normalizados compartilhados entre as fontes e 676 pares com algum sinal de
proximidade lexical. Grupos, pares e repetições excedentes são medidas diferentes.
Um sinal não equivale a duplicata confirmada.

| Rótulo automático, candidatas distintas | Humano | Sintético |
|---|---:|---:|
| `cardapio` | 48 | 132 |
| `horarios` | 39 | 123 |
| `valores` | 38 | 119 |
| `recarga_creditos` | 15 | 83 |
| `cadastro` | 33 | 79 |
| `regras_uso` | 36 | 116 |
| `fora_dominio` | 85 | 229 |
| `chitchat` | 40 | 22 |
| Total | 334 | 903 |

Esses estoques são anteriores às exclusões específicas de cada plano. As regras
produziram 66 avisos de domínio indefinido, 26 de múltiplas intenções, 32 divergências
da coluna e 16 células com expectativas de coluna conflitantes. Os avisos podem
se acumular na mesma célula e não são decisões humanas.

| Busca automática: envios teste/treino | Humanas no treino após quarentena | Proporção em 550 | Pendências numéricas do teste |
|---|---:|---:|---|
| 29/19 | 110 | 20,00% | Uma social e uma de recarga |
| 30/18 | 104 | 18,91% | Uma de recarga |
| 31/17 | 98 | 17,82% | Nenhuma por classe; treino abaixo de 20% humano |

Nenhum desses planos foi certificado como viável. Na alternativa automática
30/18, a projeção exige revisão/obtenção de pelo menos seis humanas para substituir
sintéticas dentro do alvo 550, além de suprir a pendência do teste. A falta social
de treino calculada para esse estoque é 69; não é autorização para geração.

A proposta histórica 30/18 pode ser comparada com exatamente os mesmos envios:

```bash
python3 -I -B scripts/auditar_dados.py --envios-teste 3,4,5,7,8,10,11,13,15,16,17,18,19,21,22,23,24,26,27,29,31,32,33,35,36,37,39,46,47,48
```

Ela resulta, **sob os filtros automáticos**, em 106 humanas no treino (19,27%) e
222 candidatas no teste, das quais 12 de recarga e 31 sociais. Há zero interseções
normalizadas entre as candidatas dos lados; faltam quatro humanas no alvo de
treino e três candidatas de recarga no teste. O estoque social de treino deixaria
70 a complementar. Isso não invalida semanticamente as frases antes sinalizadas
como aproveitáveis: evidencia a diferença entre regras lexicais e a revisão
semântica proposta na auditoria anterior. Não confirma os 121 exemplos anteriores.

Recomendação: manter 30/18 apenas como hipótese para a revisão, comparando a
proposta histórica e a busca. Revisar primeiro recarga/cadastro, mensagens com
domínio implícito, metarrespostas e conflitos, e só então recalcular a divisão.
Se a revisão não suprir os mínimos, obter coleta humana adicional; não substituir
teste humano por síntese nem ajustar o protocolo para forçar aprovação.
