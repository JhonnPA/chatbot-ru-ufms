# RANGOT — chatbot do Restaurante Universitário da UFMS

Trabalho Prático de Inteligência Artificial, FACOM/UFMS, 2026/2, professor Bruno
M. Nogueira. O RANGOT informa sobre o RU, reconhece conversa social, recusa
pedidos fora do domínio e pede esclarecimento quando a intenção tem baixa
confiança. A autoridade é o enunciado original do professor (PDF de 29 páginas
distribuído aos grupos; não versionado neste repositório).

**Estado em 19/11/2026:** dados/modelos congelados, experimentos 08/A1 armazenados
e RAG integrado. A falha de reprodução integral do notebook apontada pela auditoria
independente foi corrigida na Missão 11B: execução integral aprovada (22/22 células)
em cópia `git archive`, com métricas 08/09 reproduzidas sem diferença; veja
[REPRODUTIBILIDADE_11B.md](docs/REPRODUTIBILIDADE_11B.md). `verificar_entrega.py`:
0 erros. Artigo, vídeo e avaliação final ainda não estão concluídos.

## Escopo e arquitetura

| Intenção | Assunto |
|---|---|
| `cardapio` | Composição das refeições e canal oficial de cardápios |
| `horarios` | Horários de funcionamento com identificação do campus |
| `valores` | Subsídios e elegibilidade; integral de Campo Grande não confirmado |
| `recarga_creditos` | Pagamento/recarga, distinguindo relato e comprovação institucional |
| `cadastro` | Requisitos e serviços oficiais de cadastro para subsídio |
| `regras_uso` | Procedimentos comprovados no guia e limites das regras documentadas |

O classificador de **escopo** recebe todas as mensagens e distingue `dominio`,
`chitchat` e `fora_dominio`. O de **intenção** foi treinado somente nas seis
classes do RU. O LangGraph aplica a cascata: abaixo de **0,60** de probabilidade
máxima de intenção, a rota é `esclarecer`; social e fora do domínio têm rotas
próprias. O LLM não escolhe a rota.

Na intenção do RU, o RAG busca documentos daquela intenção e de `geral/`.
Com LLM, a resposta usa os trechos recuperados; sem evidência recuperada, informa
insuficiência. Sem LLM ou em falha de API, há respostas fixas. Preservam-se
`construir_grafo(config, clf_escopo, clf_tema)` e o estado final com `rota` e
`resposta`. Grupo, persona e respostas estão em `grupo.yaml`.

## Dados e experimentos

Treino: **550 exemplos**, 50 por intenção RU, 100 `chitchat` e 150 `fora_dominio`;
268 humanos e 282 LLM (**48,73% humanos**). Teste: **160 exemplos humanos**,
congelados e reservados à avaliação final única. CSVs: `texto,intencao,origem`.
Revisão humana não transforma geração por IA em autoria humana; consulte o
[protocolo](docs/PROTOCOLO_DADOS.md).

Em ambos os estágios foram comparados regressão logística, Complement Naive Bayes
e SVM linear calibrada, com TF-IDF de palavras `(1,2)` e caracteres `char_wb (2,5)`.
Usaram-se `StratifiedKFold(5, shuffle=True, random_state=42)`, pipelines,
GridSearchCV, grades pequenas e F1 macro como critério principal. A calibração
sigmoide da SVM usa três folds internas com o pipeline completo, incluindo
vetorização. Os modelos finais recebem textos crus e fornecem probabilidades.

| Estágio | Vencedor | C | F1 macro CV, média ± desvio | Acurácia CV, média ± desvio |
|---|---|---:|---:|---:|
| Escopo | SVM calibrada + caracteres | 1,0 | 0,922867 ± 0,013300 | 0,930909 ± 0,014771 |
| Intenção | SVM calibrada + caracteres | 0,1 | 0,919959 ± 0,024508 | 0,920000 ± 0,024495 |

São resultados históricos reais de **CV interna da Missão 08**, sem teste reservado.
Busca e OOF pós-seleção compartilham dados e têm viés de seleção; autores/famílias
sintéticas não foram agrupados nas folds. Comparações por origem são descritivas,
sem inferência causal. Não são avaliação padronizada ou nota C7.

O aprofundamento **A1** comparou cascata e classificador único de oito classes em
cinco folds externas comuns, com busca/calibração internas. F1 macro médio:
cascata **0,882105**, único **0,885115**, sem afirmação de significância. A produção
preservou a cascata 08. O limiar 0,60 foi escolhido com probabilidades OOF de treino
e custos explícitos, sem teste; seleção e descrição nos mesmos OOF têm limites.

- Modelos: `modelos/escopo.joblib`, `modelos/tema.joblib`, `modelos/versoes.json`.
- Resultados: `resultados/classificadores_08/` e `resultados/aprofundamento_09/`,
  com tabelas, matrizes, curvas, parâmetros e metadados.
- Notebook: [01_trabalho_grupo.ipynb](notebooks/01_trabalho_grupo.ipynb), com saídas
  saídas da execução integral aprovada na Missão 11B (ver seção de reprodução abaixo).
- Metodologia: [experimentos](docs/EXPERIMENTOS_CLASSIFICADORES.md),
  [A1](docs/APROFUNDAMENTO_A1.md) e [Missão 11A](docs/MISSAO_11A.md).

## RAG e fontes

O corpus atual tem **dez documentos e 83 trechos**. O recuperador usa TF-IDF de
caracteres, trechos brutos de até 700 caracteres, cosseno, até quatro resultados
e mínimo configurado de 0,05. [FONTES.md](documentos/FONTES.md) distingue PDFs
oficiais, resumos do guia e relatos do grupo. O índice `.vectordb/indice.joblib`
é reconstruído quando documentos, catálogo, configuração ou código relevante
mudam, desde que haja permissão de escrita.

Não há consulta de internet durante a conversa. Sem cardápio com data e campus
comprovados na base, o bot orienta consulta a
https://proaes.ufms.br/category/restaurante-universitario/.
Planejamento não comprova o que foi servido. PDFs semanais e relatórios de pesquisa
ficam fora do corpus ativo. Pix/cartões são relato do grupo, sem confirmação
institucional; ausência de documentação não prova inexistência de créditos.

Veja [RAG_OPENROUTER.md](docs/RAG_OPENROUTER.md) e a
[integração 10B](docs/AUDITORIA_INTEGRACAO_DOSSIE_2026.md).
`resultados/rag_10_offline.json` preserva oito documentos/77 trechos anteriores
à 10B; não descreve o tamanho atual do corpus.

## Instalação e conversa

Requisito declarado: Python >= 3.10. Modelos salvos com Python **3.12.13** e
scikit-learn **1.9.1**. Para reprodução, conferir as demais versões em
`resultados/classificadores_08/metadados.json`: `requirements.txt` contém
intervalos, não lock completo. Não resolver incompatibilidade retreinando os
modelos congelados neste checkout.

Comandos para o responsável em terminal autorizado:

```bash
git clone https://github.com/JhonnPA/chatbot-ru-ufms.git
cd chatbot-ru-ufms
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -B -m unittest discover -s tests
```

A partir da raiz, conversa offline e busca sem chave:

```bash
.venv/bin/python -B scripts/conversar.py --sem-llm --depurar
.venv/bin/python -B scripts/indexar_documentos.py --forcar
.venv/bin/python -B scripts/indexar_documentos.py --buscar 'Posso repetir arroz e feijão no RU?' --intencao regras_uso
```

O modelo de redação é `openai/gpt-6-luna`, via OpenRouter. Em terminal privado
fora do Codex, fornecer a chave somente ao processo conforme o procedimento de
entrada oculta em [RAG_OPENROUTER.md](docs/RAG_OPENROUTER.md) e iniciar:

```bash
.venv/bin/python -B scripts/conversar.py --depurar
```

Cleiton confirmou testes manuais reais com GPT-6 Luna e sem LLM. Isso não é
avaliação oficial nem prova de acerto universal. Conferir a fonte da resposta e
uso de chamadas: fallback fixo não comprova sucesso da API. Nenhuma chamada real
foi executada pelo Codex na Missão 11A.

## Reprodução do notebook

O notebook treina, busca hiperparâmetros e **regrava os modelos**. Por isso ele
se recusa a rodar dentro de um checkout git (proteção dos modelos congelados) e
deve ser executado numa cópia gerada por `git archive`, como a do ZIP de entrega.
Antes do A1, `validar_modelos_reproduzidos()` exige scikit-learn 1.9.1 e confere
configuração, classes, predições e probabilidades dos modelos re-serializados
contra os oficiais; diferenças de bytes do `.joblib` entre ambientes são esperadas.

```bash
mkdir /tmp/rangot-repro
git archive HEAD | tar -x -C /tmp/rangot-repro
cd /tmp/rangot-repro
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m ipykernel install --prefix .venv --name rangot --display-name 'Python (RANGOT)'
.venv/bin/python -m nbconvert --to notebook --execute \
  --ExecutePreprocessor.kernel_name=rangot \
  --ExecutePreprocessor.timeout=1800 \
  --output 01_trabalho_grupo_reproduzido.ipynb \
  notebooks/01_trabalho_grupo.ipynb
```

Resultado registrado na Missão 11B: 22/22 células sem erro e métricas 08/09
reproduzidas com diferença máxima 0,0 ([detalhes](docs/REPRODUTIBILIDADE_11B.md)).
Não usar o teste para escolher modelos, corrigir dados ou ajustar limiar.

## Limitações e rastreabilidade

- Frases vagas e mensagens com duas intenções podem receber classe única: o limiar
  não garante detectar ambiguidade. Pergunta genérica sobre subsídio sem mencionar
  RU não é falso negativo confirmado por si só.
- `integracao_ficticios.csv` da Missão 09 contém erros históricos e respostas
  fixas. `rag_10_offline.json` combina classificadores controlados/modelos reais
  com LLM simulado; seu campo `llm` não comprova chamada remota.
- Faltam evidências completas de geração de **158 exemplos LLM**: 157 da base
  original e `G07G:003`. Isso difere da revisão humana dos exemplos, confirmada
  por Cleiton em 19/11/2026. Não inventar prompts ou ferramenta geradora.
- Persistem lacunas sobre endereço específico do RU, integral de Campo Grande,
  pagamentos oficiais, horários CPAQ/CPAN e condutas sem norma local.
- Configuração persistida `xhigh` e declaração retrospectiva High do Codex são
  evidências distintas; o arquivo não comprova o modo efetivo de cada sessão.

## Estrutura

```text
grupo.yaml                  configuração, intenções, respostas e limiar
chatbot/                    classificadores, grafo, recuperação e cliente LLM
scripts/                    conversa, indexação e experimentos
dados/                      conjuntos congelados e proveniência
documentos/                 dez fontes ativas e catálogo
modelos/                    pipelines e versões preservados
notebooks/01_trabalho_grupo.ipynb
resultados/classificadores_08/
resultados/aprofundamento_09/
docs/                       contratos, protocolos, auditorias e procedimentos
referencias/_brutos/         originais e pesquisa; não é corpus ativo
relatorio/                  destino do artigo SBC, ainda a concluir
USO_DE_IA.md                 histórico e confirmações posteriores
LINKS.txt                   vídeo e repositório da entrega
```

Arquivos privados de revisão/pesquisa e caches não devem entrar em commits ou ZIP.

## Segurança e fechamento acadêmico

Não guardar credenciais no checkout do Codex nem publicá-las em código, notebook,
logs, prints, histórico ou ZIP. Não enviar chaves pela conversa. O agente não
acessa segredos, variáveis de credenciais ou Keychain. Em exposição, solicitar
revogação ao responsável/professor antes de novo uso.

CSV, modelos e scripts oficiais são protegidos. Somente depois de resolver a
reprodução, concluir decisões, congelar a versão e obter autorização expressa
para a etapa final, em cópia sem segredos:

```bash
# Etapa final futura; não executar como teste preliminar.
.venv/bin/python -B scripts/avaliar.py
.venv/bin/python -B scripts/verificar_entrega.py
```

A avaliação é **única**, sem LLM. O verificador também acessa o teste: não serve
para ciclos exploratórios. O professor calcula C7 em conjunto combinado, não
apenas no teste local. Qualquer erro do verificador ou bot não executável zera
C7 e C11 conforme o enunciado. Não há nota garantida; esses comandos não foram executados
na Missão 11A.

Antes da submissão: artigo SBC em `relatorio/relatorio.pdf`, até dez páginas;
vídeo até dez minutos, todos os integrantes e pelo menos 30 segundos declarando IA.
`video:` em `LINKS.txt` fica vazio até existir URL verdadeira e acessível; preencher
também a nota de rodapé na conclusão do artigo. O repositório é
https://github.com/JhonnPA/chatbot-ru-ufms e deve corresponder à versão final
auditada/aprovada. O ZIP é a versão efetivamente avaliada: usar `git archive`
apenas após os commits finais aprovados e inspecionar nomes de arquivos.
Nenhum artigo, vídeo, commit ou ZIP foi produzido na Missão 11A.

O histórico de IA deve ser levado ao artigo e vídeo, conforme
[USO_DE_IA.md](USO_DE_IA.md). Pendências e evidências: [Missão 11A](docs/MISSAO_11A.md).
