# Protocolo de auditoria dos dados do RANGOT

## Escopo e autoridade

A implementação iniciada na Missão 04 e estendida nas Missões 05–06 autoriza somente
`scripts/auditar_dados.py`,
`tests/test_auditar_dados.py`, este protocolo e `USO_DE_IA.md`, na branch
`feature/curadoria-dados-rangot`. Os limites da Missão 03 registrados no contrato
são históricos; esta missão não autoriza formar os conjuntos finais. A Missão 05
também autoriza a planilha local ignorada `dados/_brutos/revisao_humana.csv`.
A Missão 06 permite incorporar a nova exportação, preservar backups e preparar
planilhas privadas, sem criar conjuntos oficiais ou gerar novas frases.

Prazo prorrogado para **19/11/2026 às 23h59**, conforme informação do responsável
na Missão 06. Este registro não é uma alteração do PDF nem uma verificação externa
da comunicação do professor; o prazo impresso no enunciado permanece histórico.

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
conteúdo recebido. A auditoria e a importação de decisões não gravam arquivos.
`--exportar-revisao` e `--exportar-prioritaria` criam as planilhas privadas;
`--atualizar-base` substitui somente base/revisão locais após conferir backups.
Nenhum modo cria os conjuntos oficiais ou atualiza o Git. `-B` e a configuração
do carregador evitam caches Python.

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
O manifesto JSON não exporta textos; a planilha privada de revisão, disponível
desde a Missão 05, contém os textos originais. Não enviar os brutos ou possíveis
mensagens de teste a sessões
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

Na auditoria automática, todas as células, inclusive as candidatas, têm
`revisao_humana=pendente` e `aprovado=false`. “Candidata” significa apenas passagem
pelos filtros automáticos;
não significa frase válida aprovada, qualidade semântica garantida ou teste congelado.
Desde a Missão 05, `--importar-revisao` reconhece somente decisões explicitamente
declaradas no CSV privado; não converte sugestões ou campos vazios em aprovações.

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

## Revisão humana — Missão 05

### Planilha privada e preservação

Arquivo: `dados/_brutos/revisao_humana.csv`, CSV UTF-8 com cabeçalho e vírgulas.
O caminho deve continuar ignorado e não versionado; exportação e importação
verificam essa condição e recusam links simbólicos. A criação é exclusiva:
arquivo existente nunca é sobrescrito, mesmo que ainda esteja pendente.

Na fotografia da Missão 05 foram preparadas **1.711 linhas**, uma por resposta
preenchida: 479 humanas e 1.232 sintéticas. As 89 células vazias ficam fora da
planilha. Duplicatas continuam
em linhas próprias para permitir julgamento individual; as contagens de capacidade
são deduplicadas depois. Todos os campos `decisao_humana` começam em `pendente`,
e `rotulo_revisado`, `uso_autorizado` e observações começam vazios.

| Campo | Regra |
|---|---|
| `id_resposta` | ID fonte/envio/coluna já usado pelo auditor. Imutável. |
| `id_envio` | Fonte e posição original do envio, sem identificação pessoal. Imutável. |
| `fonte_original`, `origem`, `coluna_original` | Procedência e posição; não podem ser editadas. |
| `texto_original` | Valor lógico exato da resposta no bruto, incluindo espaços e quebras de linha; não editar. |
| `rotulo_sugerido` | Sugestão automática original, não aprovação. Imutável. |
| `motivo_sinalizacao` | Avisos e IDs relacionados a duplicatas/quase duplicatas/paráfrases. Imutável. |
| `sha256_fonte` | Vincula a linha à versão exata do arquivo de origem. Imutável. |
| `rotulo_revisado` | Editável: uma das seis intenções, `chitchat` ou `fora_dominio`. |
| `decisao_humana` | Editável: `aprovar`, `corrigir`, `rejeitar`, `pendente` ou vazio. |
| `uso_autorizado` | Editável: `treino`, `teste`, `ambos` ou vazio, respeitando a origem. |
| `observacoes_revisao` | Editável: justificativa sem dados pessoais; não aparece no JSON público. |

O auditor antigo aparava espaços para comparação; o exportador recupera os
valores exatos dos snapshots CSV, sem modificar essa funcionalidade existente.
Nenhum campo temporal ou metadado pessoal do formulário é copiado. Células com
sinais de e-mail, número longo, autoidentificação ou início de fórmula de planilha
ficam fora da exportação, com sinalização por ID. Esses filtros são heurísticos;
o responsável deve evitar introduzir dados pessoais também nas observações.
Respostas retidas por privacidade não são reescritas para parecerem originais.

### Como revisar

1. Abra o arquivo **localmente**, importando como UTF-8, separado por vírgula e
   preservando os campos como texto. Não envie a planilha a sessões de geração.
2. Altere somente os quatro campos editáveis. Pode ordenar/filtrar linhas, mas
   não remover linhas, alterar IDs, cabeçalho, texto, origem ou versão.
3. Use `aprovar` para aceitar o rótulo sugerido, inclusive quando uma heurística
   havia barrado a frase. Nesse caso, o rótulo revisado pode ficar vazio ou repetir
   o sugerido. A decisão precisa ser explicitamente digitada pelo responsável.
4. Use `corrigir` com rótulo revisado válido para trocar a classificação ou rotular
   resposta sem sugestão. Não alterar o texto para facilitar a classificação.
5. Use `rejeitar` para excluir do aproveitamento; não apagar a linha. Use
   `pendente`/vazio quando não houver decisão. Um rótulo preenchido sem decisão
   de aprovação/correção continua fora das contagens aprovadas.
6. Avalie múltiplas intenções, contexto implícito e mensagens sem intenção clara.
   Se não houver rótulo único justificável, rejeite ou mantenha pendente.
   `dominio` e `esclarecer` não são rótulos permitidos para essas mensagens.
7. Consulte os IDs relacionados em `motivo_sinalizacao` para analisar duplicatas.
   Duplicatas normalizadas aprovadas devem ter o mesmo rótulo; conflitos impedem
   a importação, em vez de escolher silenciosamente a primeira classificação.
8. Salve como CSV UTF-8 com vírgulas e execute a importação. Edição de texto,
   origem, metadados ou versão, IDs repetidos/desconhecidos, linhas ausentes e
   decisões/rótulos inválidos fazem a importação falhar com código técnico e ID.

Rótulos permitidos: `cardapio`, `horarios`, `valores`, `recarga_creditos`,
`cadastro`, `regras_uso`, `chitchat` e `fora_dominio`. A importação aceita revisão
parcial: linhas ainda pendentes permanecem na planilha e não entram nas contagens
aprovadas. O arquivo registra decisões declaradas pelo responsável, sem autenticar
a identidade de quem o editou.

### Uso de cada exemplo e comparação dos planos

Em `uso_autorizado`, humanas podem receber `treino`, `teste` ou `ambos`.
Vazio não impõe restrição adicional à simulação, mas **não aprova uma divisão**.
Sintéticas aceitam somente vazio ou `treino`: nunca podem ir para teste. A decisão
sobre o rótulo e a aprovação da divisão são etapas diferentes.

Cada envio humano continua em um único lado da simulação. Se uma resposta
aprovada tem uso incompatível com esse lado, ela não é transferida para o outro:
seu ID aparece em `aprovadas_nao_alocadas_por_uso`. Assim, o revisor pode limitar
individualmente o aproveitamento sem separar artificialmente um envio.

```bash
# Planilha deste checkout já preparada: revisar antes de aprovar decisões.
python3 -I -B scripts/auditar_dados.py --importar-revisao

# Mesmo protocolo, manifesto público sem textos/observações:
python3 -I -B scripts/auditar_dados.py --importar-revisao --manifesto

# Somente em checkout SEM a planilha; nunca sobrescreve revisões existentes:
python3 -I -B scripts/auditar_dados.py --exportar-revisao
```

Sem `--importar-revisao`, a auditoria continua apresentando sugestões automáticas
sem aprovações. Com a opção, as divisões principais usam **somente** decisões
`aprovar`/`corrigir` importadas; as propostas automáticas ficam separadas em
`divisoes_automaticas_nao_revisadas`. O resumo informa pendências por sugestão e
origem, aprovadas distintas e o hash da planilha importada, sem publicar seus textos.

A busca compara 29/19, 30/18 e 31/17, sem métricas de modelos; a opção
`--envios-teste` continua permitindo simular um conjunto explícito de IDs.
Reutilizam-se agrupamento, normalização, mínimos, proporções, quarentena de
proximidade e detecção de sobreposição existentes. O resultado permanece uma
simulação, com `divisao_aprovada=false` e `congelado=false`.

No arquivo inicial há **zero decisões concluídas**, portanto zero exemplos
aprovados para contabilizar treino/teste. Não se pode afirmar quantos serão
aproveitados após a revisão nem quantas sintéticas adicionais serão necessárias.
Primeiro importar decisões reais e aprovar uma divisão; somente em missão
posterior autorizada construir os CSVs oficiais e suprir faltas, usando apenas
o treino aprovado para orientar eventual geração.

## Incorporação dos 67 envios — Missão 06

### Evidência de integridade e estado da substituição

A exportação nova tem 67 envios, 11 colunas e 669 respostas preenchidas; a anterior
tem 48 envios e 479 respostas. Os cabeçalhos são iguais, as larguras consistentes
e não há duplicação integral de envio ou de suas dez respostas na nova versão.
A comparação exata por registro, independente da ordem, preservou todos os
48 envios, incluindo cada resposta e o metadado temporal original, sem publicar
esse metadado. São 19 adições, nas posições 49–67 da nova exportação.

| Arquivo privado | SHA-256 |
|---|---|
| Base anterior e `formulario_humano_backup_48.csv` | `b27a639bc111689ca9a42c024e2b45f1f9b53f7879affc4b63799e417b5fc304` |
| `formulario_humano_novo.csv` | `53aef836b97ed2c3d46afa2ff15bc9b2b07225189e6fed498123fe573d20448c` |
| Revisão anterior e `revisao_humana_backup_1711.csv` | `9e6334c152c89b6345b49c1fa871c372cd8bee5d50d9f34812eda5df2d026379` |
| `sinteticas_llm.csv` | `87dd6717fb62280cda1cdb7fbb29c8b5730153cdaf3ccf49448998d73a0f44e8` |

O sandbox bloqueou a gravação nativa antes de criar o journal ou substituir os
arquivos ativos. **A base ativa continua com 48 envios e a revisão ativa com
1.711 linhas.** A nova versão foi processada em memória e seus artefatos privados
foram preparados pelo editor. Não substituir a exportação pelo editor: os bytes
incluem CRLF e ausência de quebra final, que precisam permanecer íntegros.

Arquivos preparados e ignorados:

- `revisao_humana_67_preparada.csv`: 1.901 respostas, 669 humanas e 1.232 sintéticas;
  nenhuma aprovação, textos originais exatos e IDs das primeiras 48 participações
  preservados. As 89 células vazias das duas fontes ficam fora.
- `migracao_48_67_preparada.json`: hashes e vínculos entre IDs das versões;
  explicitamente marcado como preparação com substituição bloqueada.
- `triagem_semantica_67.json`: sugestões do Codex por ID e hash do texto, vinculadas
  ao hash da nova fonte; não contém textos, timestamps ou aprovações humanas.
- `plano_curadoria_67.json` e `revisao_prioritaria.csv`: proposta e seleção reduzida
  descritas abaixo. Nunca versionar ou publicar esses arquivos privados.

Para concluir a migração nativa, manualmente no checkout:

```bash
python3 -I -B scripts/auditar_dados.py --planejar-atualizacao
python3 -I -B scripts/auditar_dados.py --atualizar-base
python3 -I -B scripts/auditar_dados.py --importar-revisao
```

O comando de atualização exige base/revisão ativas idênticas aos respectivos
backups, verifica novamente as entradas antes da gravação e cria
`migracao_48_67.json` sem sobrescrever um journal existente. Cada substituição
usa arquivo temporário no próprio diretório e `os.replace`; as duas substituições
não constituem uma transação única. Se ocorrer falha intermediária, conferir
journal, hashes e backups antes de qualquer recuperação manual. Não repetir o
comando após migração concluída, nem sobrescrever backups para contornar erros.

### Triagem semântica e busca por envio

O Codex examinou as respostas, considerando o pedido completo, ironia, elipses,
erros de digitação e tópicos externos. As sugestões por resposta estão no arquivo
privado de triagem, não em regras que copiam o rótulo da coluna para futuras bases.
Rótulos humanos existentes prevalecem sobre a triagem; rejeições não são revertidas.

Das 669 respostas humanas: 581 são candidatas provisórias, 36 ambíguas,
34 metarrespostas, seis com múltiplas intenções e 12 fora do catálogo sem rótulo
único seguro. Após deduplicação, há **570 candidatas distintas**. Essa triagem é
assistência generativa, não revisão humana. Frases elípticas selecionadas para
treino continuam exigindo julgamento sobre sua classificação sem contexto.

A nova busca compara 29, 30, 31, 33, 35, 37 e 39 envios para teste, largura cinco.
Preserva cada envio em um lado e distribui proporcionalmente as 19 adições entre
os lados, usando a versão de coleta, sem publicar ou usar timestamps para seleção.
O objetivo é cobertura dos mínimos e capacidade humana do treino, sem desempenho
de modelos. É uma busca limitada: uma alternativa com falta não prova inexistência
de outra solução com o mesmo tamanho.

Na nova busca, duplicatas entre envios não obrigam agrupar grandes cadeias de
cumprimentos: a ocorrência do lado de treino fica em quarentena quando coincide
com a reserva de teste. Quase duplicatas também retiram candidatas de treino;
possíveis paráfrases ainda exigem revisão humana. As modalidades anteriores do
auditor preservam seu comportamento e continuam detectando sobreposições.

### Proposta condicionada à aprovação

Proposta: **31 envios para reserva de teste e 36 para treino**, com nove dos
19 envios novos no lado do teste e dez no treino. IDs completos ficam no plano
privado. Nenhuma divisão foi aprovada ou congelada.

| Classe | Candidatas humanas distintas, antes da divisão | Humanas selecionadas para treino | Sintéticas existentes selecionadas | Teste selecionado | Complemento projetado |
|---|---:|---:|---:|---:|---:|
| cardapio | 87 | 42 | 8 | 15 | 0 |
| horarios | 69 | 36 | 14 | 15 | 0 |
| valores | 63 | 33 | 17 | 15 | 0 |
| recarga_creditos | 63 | 32 | 18 | 15 | 0 |
| cadastro | 53 | 27 | 23 | 15 | 0 |
| regras_uso | 59 | 29 | 21 | 15 | 0 |
| chitchat | 54 | 23 | 21 | 30 | 56 |
| fora_dominio | 122 | 58 | 92 | 40 | 0 |
| **Total** | **570** | **280** | **214** | **160** | **56** |

As 56 faltantes são uma projeção com as sugestões atuais: rejeições/correções e
recuperação de frases existentes podem mudar o número. Nenhuma frase foi gerada.
Com aprovação e complemento válido, seriam 550 exemplos de treino, 280 humanos
(50,91%), 50 por intenção, 100 sociais e 150 externos. O teste teria 160 humanos,
15 por intenção, 30 sociais e 40 externos. Há zero interseções normalizadas na
proposta; isso não certifica ausência de paráfrases sem julgamento humano.

O lado reservado ao teste tem 236 candidatas distintas, das quais 160 foram
priorizadas; as 76 restantes continuam reservadas, sem transferência para treino.
Sem revisão não há exemplos aprovados para os conjuntos oficiais. Conteúdo da
reserva não deve orientar futuras gerações, tuning ou escolha de modelos.

### Procedimento rápido de aprovação

1. Abra localmente `revisao_prioritaria.csv` como CSV UTF-8 com vírgulas, todos os
   campos como texto. São **654 linhas**, em vez de 1.901: 160 para teste,
   280 humanas para treino e 214 sintéticas existentes para treino.
2. Filtre primeiro `uso_proposto=teste`, depois humanas de treino, por fim sintéticas.
   Examine texto e rótulo de cada linha; priorize os avisos de ambiguidade,
   duplicação e possível paráfrase. Não envie o material a geradores de dados.
3. Edite somente `decisao_humana` e `rotulo_corrigido`: `aprovar` aceita a sugestão,
   `corrigir` exige uma das oito classes válidas, `rejeitar` exclui e `pendente`
   mantém fora. Não alterar textos, IDs, origem, uso proposto, avisos ou hash.
4. Valide após salvar. Antes da migração nativa:

   ```bash
   python3 -I -B scripts/auditar_dados.py --importar-prioritaria --usar-exportacao-nova
   ```

   Depois da migração, use o mesmo comando **sem** `--usar-exportacao-nova`.
   A importação reconta apenas decisões explícitas, aceita revisão parcial e não
   grava na planilha mestre nem cria os CSVs oficiais. Guarda-se a própria planilha
   prioritária como registro das decisões para a próxima missão.
5. Confirme ao agente as decisões e a aprovação dos IDs de envio propostos.
   Rejeições que inviabilizem mínimos exigem nova seleção ou coleta, sem forçar
   aprovação. O congelamento e a construção dos CSVs ficam para nova autorização.

Para reproduzir a busca antes da migração:
`python3 -I -B scripts/auditar_dados.py --planejar-curadoria --usar-exportacao-nova`.
`--exportar-prioritaria` prepara os arquivos somente se ainda não existirem;
recusa sobrescrever trabalho do revisor. O hash do contexto vincula seleção,
rótulos propostos, lados e versões das fontes. É integridade, não autenticação
da identidade do responsável que declara as decisões.

## Curadoria sob autorização delegada — Missão 07A

### Autoridade, ferramenta e limites

O responsável informou ter examinado o CSV e autorizou expressamente o Codex a
decidir individualmente, inclusive registrar `decisao_humana=aprovar` sob delegação.
Também determinou: **“Essa autorização não significa que eu tenha revisado
individualmente todas as frases. Não declare isso.”** Esta seção registra essa
decisão interna do grupo, não uma nova exigência ou aprovação do professor.

Ferramenta: **Codex**. Modelo: **família GPT-6**, informada nesta sessão;
variante/identificador exato não exposto. Não se pesquisaram configurações ou
credenciais para preencher essa lacuna. A política do PDF permite IA em qualquer
etapa, com declaração; continuam obrigatórias a autoria humana do texto de teste,
a separação dos conjuntos e a responsabilidade do grupo pelo material entregue.

As 654 candidatas foram lidas integralmente pelo Codex. Expressões regulares e
colunas não decidiram a curadoria: saudação não anulou pedido operacional,
negações do domínio foram consideradas e dúvidas sem rótulo seguro ficaram
pendentes. Não houve revisão manual individual atribuída ao responsável.

Critérios internos de qualidade, adicionais aos mínimos oficiais:

- Excluir repetições que apenas acrescentam saudação, partícula ou erro de grafia.
  O professor não exige unicidade semântica absoluta por intenção; este filtro
  busca evitar que repetições superficiais inflem a diversidade e a capacidade.
- Preservar elipses com operação reconhecível no contexto fixo do assistente RU,
  sem usar a coluna de coleta como contexto oculto. Pedidos que poderiam apontar
  para intenções diferentes permaneceram pendentes.
- Manter variações com condições explícitas, como curso ou dia consultado,
  registrando que pertencem a famílias de templates. Considerar essas famílias
  na futura validação cruzada, sem alegar que esse experimento já foi executado.
- Não transformar perguntas sobre regras, cardápios ou recarga em afirmações
  factuais sobre o RU; a autoria e o texto original permanecem intactos.

### Backups, ledger e importação

A base ativa já tinha sido migrada para 67 envios no início da missão, e sua
revisão tinha 1.901 linhas pendentes. Antes de registrar decisões, preservaram-se
os arquivos privados `revisao_humana_backup_07a.csv`,
`revisao_prioritaria_backup_07a.csv` e `plano_curadoria_67_backup_07a.json`.

O registro auxiliar `dados/_brutos/auditoria_delegada_07a.json` contém, para cada
ID, texto original, hash, origem da frase, rótulos anterior/proposto/final,
decisão, justificativa, referência de duplicata ou substituição e ferramenta/modelo.
Registra `origem_decisao=ia_sob_autorizacao_expressa` e
`revisao_manual_individual=false`, com referência à autorização da Missão 07A.
Todos esses arquivos continuam privados, ignorados e fora dos commits.

A planilha prioritária e o plano foram versionados localmente por hashes,
preservando os backups e os IDs das 654 candidatas iniciais. Acrescentaram-se
55 suplentes/complementos da base existente, analisados individualmente e sem
alterar textos ou origens. São 53 relações de substituição e dois complementos
para mínimos ainda insuficientes. A divisão por envio permaneceu **31/36**.

O importador reutiliza as validações anteriores e confere também autorização,
ledger, backups, hashes, IDs, rótulos e origem da decisão. As observações do mestre
recebem o marcador `origem_decisao=ia_delegada;autorizacao=missao_07a;`, ferramenta,
modelo, justificativa e indicação explícita de ausência de revisão manual individual.
O nome legado `decisao_humana` foi mantido por compatibilidade; não comprova quem
fez a revisão. Os relatórios distinguem a curadoria delegada das demais declarações.

```bash
# Reproduzir a validação, sem gravar:
python3 -I -B scripts/auditar_dados.py --importar-delegada

# Persistir somente após validar ledger e backups; repetição é idempotente:
python3 -I -B scripts/auditar_dados.py --aplicar-delegada
```

O comando legado `--importar-prioritaria` também exige o ledger quando ele existe,
para não perder a proveniência delegada. Nenhum desses comandos cria CSVs oficiais.
A escrita nativa foi bloqueada pelo sandbox; após a validação, a revisão mestre
foi gravada pelo editor e revalidada pelo mesmo importador. Hash atual do mestre:
`7c59cb6bb992110a9c6957c9a63053b92736643c9abd0fe294107138a6fe99c4`.

### Resultado efetivo, não aprovação manual individual

| Universo | Aprovar por delegação | Corrigir | Rejeitar | Pendente |
|---|---:|---:|---:|---:|
| 654 candidatas iniciais | 524 | 1 | 116 | 13 |
| 55 suplentes/complementos | 51 | 4 | 0 | 0 |
| **709 registros** | **575** | **5** | **116** | **13** |

Das rejeições, 115 se referem a variantes superficiais/paráfrases adjudicadas e
uma a metarresposta sem pedido classificável. As cinco correções explícitas estão
nos IDs `S0087:C07`, `H0043:C02`, `H0049:C08`, `H0066:C02` e `S0024:C05`.
Os textos e as justificativas completas ficam exclusivamente no ledger privado.

Na compatibilização com o mestre, 48 aprovações de rótulos já sugeridos na planilha
prioritária foram transportadas como `corrigir`, pois a sugestão lexical antiga
do mestre diferia. Assim, o mestre registra 527 `aprovar`, 53 `corrigir`,
116 `rejeitar` e 1.205 `pendente`. As últimas incluem 1.192 respostas fora do
conjunto de decisões registradas nesta missão. Não contar essa conversão como novas
frases ou novas revisões; permanecem **580 exemplos aceitos**.

| Classe | Treino humano | Treino LLM existente | Treino total | Teste humano | Falta para treino |
|---|---:|---:|---:|---:|---:|
| cardapio | 40 | 10 | 50 | 15 | 0 |
| horarios | 34 | 16 | 50 | 15 | 0 |
| valores | 32 | 18 | 50 | 15 | 0 |
| recarga_creditos | 32 | 14 | 46 | 15 | 4 |
| cadastro | 26 | 17 | 43 | 15 | 7 |
| regras_uso | 26 | 17 | 43 | 15 | 7 |
| chitchat | 25 | 21 | 46 | 30 | 54 |
| fora_dominio | 53 | 39 | 92 | 40 | 58 |
| **Total** | **268** | **152** | **420** | **160** | **130** |

Treino atual: **63,81% humano**. Se as 130 faltantes fossem posteriormente obtidas
como LLM, revisadas e independentes, o alvo de 550 teria **48,73% humano**.
Esta é uma projeção, não autorização para gerar ou uma execução já realizada.
As faltas são da seleção aprovada, não prova de esgotamento das outras respostas
da base. Curadoria adicional do acervo ainda pendente pode reduzir o complemento;
não interpretar 130 como quantidade inevitável de novas frases sintéticas.

O teste proposto tem todos os mínimos e é 100% humano, com quatro substituições:
`H0018:C02 → H0021:C03`, `H0037:C07 → H0064:C07`,
`H0005:C09 → H0061:C09` e `H0040:C09 → H0057:C10`.
Os mesmos envios continuam reservados. As verificações não encontraram
interseções normalizadas, quase duplicatas ou sinais lexicais de paráfrase entre
os aceitos de treino e teste, nos limiares documentados. Isso não prova ausência
universal de parentesco semântico. O ledger também registra uma possível
paráfrase interna ao teste, mantida com ressalva por solicitar informações adicionais.

### Pendências e preparação do congelamento

Continuam pendentes `H0005:C09`, `H0012:C05`, `H0017:C07`, `H0020:C03`,
`H0020:C10`, `H0028:C08`, `H0030:C06`, `H0033:C03`, `H0033:C11`,
`H0036:C02`, `H0049:C10`, `H0066:C04` e `S0010:C01`.
Os motivos envolvem instituição citada, objeto omitido, fronteira de intenção,
mistura de pedidos e interpretação não segura. Não foram aprovados para fechar quotas.

O treino ainda não atende aos mínimos: a curadoria não está concluída como
preparação de todos os dados oficiais. Resolver necessidades específicas, obter
complemento válido e independente, e autorizar o congelamento são etapas seguintes.
O teste está preparado para essa decisão, mas permanece `congelado=false`;
`dados/treino.csv` e `dados/teste.csv` não foram criados ou alterados.

No artigo e no vídeo, distinguir autoria humana dos textos de teste de seleção,
rotulagem e aprovação assistidas por IA delegada. Uma futura geração deve receber
somente treino aprovado e contagens de falta em contexto sem respostas de teste.

## Ratificação e congelamento — Missão 07B

O responsável declarou leitura integral de `revisao_prioritaria.csv` e ratificou
as **709 decisões**: 575 aprovações, cinco correções, 116 rejeições e 13 pendências.
A conferência humana posterior está registrada separadamente em
`dados/_brutos/ratificacao_07b.json`, vinculada aos hashes da planilha, do mestre,
do plano e do ledger. O histórico de decisões por IA da Missão 07A foi preservado;
não se reescreveram suas declarações de ausência de revisão manual à época.
As 13 pendências continuam excluídas, e a ratificação não abrange candidatas novas.

### Teste congelado

`dados/teste.csv` foi preenchido a partir do cabeçalho vazio existente, com somente
`texto,intencao,origem`, UTF-8 e quebras LF. Tem exatamente **160 frases humanas**:
15 de cada intenção do RU, 30 `chitchat` e 40 `fora_dominio`. Foram preservados os
valores originais dos textos, incluindo espaços e quebras internas; não se
reescreveram frases nem se incluíram rejeitadas ou pendentes.

**SHA-256:** `fa760e167d565a9a3e5bd015465c4ec945f7855e0bd78b5542dc561e21ea9b81`.

O manifesto privado `dados/_brutos/manifesto_conjuntos_07b.json` registra
`congelado=true`, composição, IDs, hashes e vínculo com a ratificação. O
`congelado=false` dos planos históricos descreve a etapa anterior, não este estado.
Não houve duplicatas normalizadas ou interseções com o treino aceito, nem sinais
de proximidade problemática entre os conjuntos nos controles já implementados.
O teste permanece vedado a seleção de modelos, tuning, limiares e geração.

### Treinamento e reaproveitamento

Há **420 exemplos autorizados**, 268 humanos e 152 LLM, em
`dados/_brutos/treino_parcial_07b.csv`: **63,81% humano**. O arquivo oficial
`dados/treino.csv` conserva somente o cabeçalho vazio; não é um treinamento completo.

| Classe deficitária | Falta autorizada atual | Candidatas novas para conferência | Falta se todas forem ratificadas |
|---|---:|---:|---:|
| recarga_creditos | 4 | 3 | 1 |
| cadastro | 7 | 2 | 5 |
| regras_uso | 7 | 0 | 7 |
| chitchat | 54 | 0 | 54 |
| fora_dominio | 58 | 0 | 58 |
| **Total** | **130** | **5** | **125** |

As outras três classes já têm 50 exemplos autorizados cada. Com um alvo de 550
e todos os complementos de origem LLM, a proporção humana projetada é **48,73%**.
Nenhuma frase nova foi gerada, e nenhuma candidata suplementar foi incorporada.

A busca percorreu as 1.232 respostas preenchidas da base sintética: 256 já tinham
decisões ratificadas; nove coincidiam com humanas; 259 tinham famílias próximas
ratificadas sem novidade suficiente na triagem; 453 repetiam núcleos já examinados.
Foram examinados 255 representantes restantes. Normalização/similaridade apenas
reduziram a fila; a recomendação final considerou o significado individual.
O resumo privado `busca_sinteticas_07b.json` registra fonte, hash, método e limites.
Essa busca não certifica esgotamento absoluto do acervo.

Cinco candidatas estão em `dados/_brutos/candidatas_sinteticas_07b.csv`, todas com
`origem=llm` e `decisao_humana=pendente`: `S0004:C05`, `S0009:C05`, `S0025:C05`,
`S0004:C06` e `S0005:C06`. As três de recarga têm domínio RU implícito e exigem
conferência dessa interpretação. As duas de cadastro consultam local de retirada
e procedimento de emissão do cartão e pertencem a uma família relacionada.
Os textos, sugestões, famílias e justificativas estão na planilha privada;
não se atribui a elas a ratificação das 709 decisões anteriores.

### Pacote isolado e verificação

Para o futuro ambiente gerador, copiar **somente**
`dados/_brutos/pacote_treinamento_07b/`, que contém:

- `treino_autorizado.csv`: cópia exata dos 420 exemplos autorizados de treino.
- `INSTRUCOES.md`: definições das oito classes, faltas atuais e instruções de
  diversidade, revisão e registro de ferramenta/modelo/prompts.

O pacote não contém formulários, textos/IDs/manifestos do teste, nem as candidatas
novas ainda não ratificadas. Antes de gerar, conferir essas candidatas e atualizar
as quantidades necessárias. As 130 faltas atuais não são autorização para geração
e podem diminuir com novo reaproveitamento autorizado.

```bash
python3 -I -B scripts/auditar_dados.py --conferir-conjuntos
```

Esse comando reusa a validação da curadoria, confere a ratificação por hashes,
reconstrói os bytes esperados e verifica teste, parcial, manifesto e pacote.
Não treina, não gera frases, não executa avaliadores e não altera o teste congelado.
Somente as cinco candidatas novas e as pendências específicas exigem conferência
adicional; não repetir a revisão ratificada nem reabrir o teste para melhoria de modelos.

## Incorporação ratificada e complemento isolado — Missão 07C

O responsável declarou ter conferido as cinco frases e seus rótulos e autorizou
expressamente apenas sua incorporação ao treino: `S0004:C05`, `S0009:C05`,
`S0025:C05` (`recarga_creditos`), `S0004:C06` e `S0005:C06` (`cadastro`).
Foram conferidos individualmente IDs, textos contra a fonte sintética original,
rótulos e hashes de texto. A origem continua `llm`; não houve reescrita.
As famílias relacionadas já sinalizadas foram aceitas pelo responsável e devem
ser consideradas no agrupamento para a futura validação cruzada.

A ratificação está em `dados/_brutos/ratificacao_07c.json`, vinculada ao hash da
planilha de cinco candidatas, da fonte original, do manifesto anterior e da cópia
aprovada `candidatas_aprovadas_07c.csv`. Esta cópia registra `aprovar`, o rótulo
conferido e a origem humana expressa da aprovação. Os snapshots 07A/07B foram
preservados: o estado pendente das cinco no arquivo 07B é histórico, substituído
somente para esses IDs pela aprovação 07C. As outras 13 pendências não mudaram.

O treinamento corrente é `dados/_brutos/treino_parcial_07c.csv`, com **425 frases**:
**268 humanas e 157 LLM (63,06% humano)**. Seu manifesto privado é
`dados/_brutos/manifesto_conjuntos_07c.json`, com seleção por IDs, composição,
proveniência, hashes e vínculo com o manifesto 07B. O treino oficial permanece
somente com cabeçalho até completar os mínimos com candidatas revisadas e autorizadas.

| Classe | Treino autorizado | Complemento necessário |
|---|---:|---:|
| cardapio | 50 | 0 |
| horarios | 50 | 0 |
| valores | 50 | 0 |
| recarga_creditos | 49 | 1 |
| cadastro | 45 | 5 |
| regras_uso | 43 | 7 |
| chitchat | 46 | 54 |
| fora_dominio | 92 | 58 |
| **Total** | **425** | **125** |

Não há duplicatas normalizadas no treino nem interseções normalizadas com o teste;
as cinco adições não apresentaram sinais de proximidade problemática com o teste
no detector existente. O teste de 160 humanas não foi alterado e conserva SHA-256
`fa760e167d565a9a3e5bd015465c4ec945f7855e0bd78b5542dc561e21ea9b81`.
Com 125 complementos LLM aprovados, a projeção é 550 frases e **48,73% humano**.

### Transferência mínima para geração futura

O pacote atual é `dados/_brutos/pacote_treinamento_07c/`, contendo exclusivamente
`INSTRUCOES.md` e `treino_autorizado.csv` (as mesmas 425 frases do parcial).
Inclui definições públicas das oito classes, quotas, diversidade, negativos difíceis,
revisão e registro dos prompts integrais, modelo real e proveniência por lote.
Não contém mensagens ou manifesto do teste, formulário completo ou credenciais.
O pacote 07B e seu verificador continuam históricos; não representam o treino corrente.

**Comandos manuais, não executados nesta missão.** Neste checkout, empacotar somente
os dois arquivos explicitamente permitidos:

```bash
tar -czf /tmp/rangot-geracao-07c.tar.gz \
  -C dados/_brutos/pacote_treinamento_07c \
  INSTRUCOES.md treino_autorizado.csv
```

Transferir somente esse arquivo para outro computador ou VM sem o checkout,
sem pastas compartilhadas e sem volumes do host montados. Uma nova sessão ou
diretório no mesmo host com acesso ao teste não atende ao isolamento exigido.
Não copiar configurações do agente, credenciais ou histórico desta conversa.
No ambiente separado, ajustar o caminho do arquivo recebido e executar:

```bash
mkdir -m 700 rangot-geracao-07c
tar -xzf /caminho/recebido/rangot-geracao-07c.tar.gz \
  -C rangot-geracao-07c INSTRUCOES.md treino_autorizado.csv
cd rangot-geracao-07c
cat INSTRUCOES.md
```

Na ferramenta de IA escolhida pelo responsável nesse ambiente, iniciar uma conversa
nova e fornecer exclusivamente os dois arquivos, usando `INSTRUCOES.md` como
instrução integral. A escolha e identificação real do modelo devem ser registradas;
nenhuma ferramenta geradora ou execução futura é declarada como já realizada.
Não há chamada ao OpenRouter neste procedimento. A saída prevista é
`candidatas_complemento.csv` com `texto,intencao,origem`, 125 candidatas nas quotas
acima e sempre `origem=llm`, acompanhada de `registro_geracao.md` com prompts,
respostas originais e identificação por lote.

Devolver somente as candidatas e esse registro ao curador. Cada frase requer revisão
semântica, de origem, duplicatas e famílias de paráfrases contra o treino; o curador
confere separadamente possíveis interseções com o teste, sem revelar suas mensagens
ao gerador. Só então incorporar o complemento autorizado e verificar os mínimos
50 por intenção, 100 chitchat, 150 fora_dominio e 20% humano/coletado. Não preencher
quotas com mensagens ambíguas nem promover textos LLM a humanos. Não houve geração,
treinamento de classificadores, avaliação final ou criação do ambiente externo nesta missão.

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
Decisões humanas podem ser registradas nas planilhas privadas desta missão.
Construir e congelar os CSVs finais exige nova autorização após aprovação da
divisão. Somente treino/CV poderá orientar modelos, hiperparâmetros e limiar.
Uma futura geração deve receber apenas o treino aprovado e o protocolo de
faltas, em contexto que não contenha as respostas reservadas ao teste.

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
