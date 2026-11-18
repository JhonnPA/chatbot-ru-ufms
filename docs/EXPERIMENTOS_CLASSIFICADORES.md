# Experimentos de classificadores — Missão 08

## Estado desta sessão

**Implementação preparada; execução científica bloqueada.** A branch conferida é
`feature/classificadores-rangot`, inicialmente limpa. Os dois hashes oficiais foram
confirmados. Não há métricas estimadas, vencedores selecionados ou modelos salvos.

Os Pythons 3.14.5 e 3.12.13 encontrados não têm numpy, pandas, scikit-learn,
matplotlib, PyYAML, scipy ou joblib disponíveis no modo isolado. Não existe `.venv`
no checkout. A execução real do script terminou com código 2 por falta de `yaml`.
A criação da pasta de resultados pelo processo Python foi negada com
`PermissionError: Operation not permitted`. O editor permitiu preparar fontes e
esta documentação; isso não demonstra permissão para salvar modelos em execução.
Não se solicitou rede nem ampliação do sandbox.

Os 116 testes descobertos tiveram **110 aprovações e seis testes ML ignorados**
explicitamente por falta de bibliotecas. Os 107 testes anteriores do auditor
continuam aprovados. Os seis testes ignorados não validam os modelos. O notebook
está preenchido, com saídas vazias até uma execução real completa; não foi declarado
executado. O estado observado está em `resultados/classificadores_08/ESTADO_EXECUCAO.json`.

## Fontes e isolamento

Foram consultadas as páginas 7–10 e 18–20 do enunciado oficial de 29 páginas,
extraídas localmente com PDFKit. Elas exigem pipelines, três algoritmos, duas
representações, CV estratificada de cinco folds, tuning, F1 macro, matrizes, curvas
e análise de erros. Os números do exemplo do professor não são resultados do RANGOT.

O módulo lê `dados/treino.csv` pela interface oficial, derivando escopo com
`adicionar_escopo`. Tema recebe somente os 300 exemplos originalmente de domínio;
escopo recebe todos os 550. O teste é acessado exclusivamente como bytes para
SHA-256, sem parsing, sem rótulos, frases, seleção, calibração ou avaliações.
Configuração, dados e três arquivos oficiais são protegidos por hashes antes/depois.
Não há importação de LLM, grafo ou avaliador no fluxo experimental.

## Comparação e seleção

Em ambos os estágios:

- Regressão logística: modelo linear de probabilidades de classe, ajustado por
  perda logística e regularização L2. `C` controla o inverso da regularização.
- Complement Naive Bayes: usa frequências no complemento de cada classe sob
  uma aproximação de independência entre características. `alpha` suaviza
  frequências, permitindo trabalhar com TF-IDF esparso e não negativo.
- LinearSVC: aprende separadores lineares de margem; não fornece probabilidades
  diretamente. É calibrada por sigmoides com três folds internas estratificadas.
  O estimador calibrado é o pipeline completo, incluindo TF-IDF, para não aprender
  vocabulário/IDF na validação interna. O objeto final também é um Pipeline.

Representações: TF-IDF de palavras (1,2) e `char_wb` (2,5), ambas com
`chatbot.texto.normalizar`, TF sublinear, `min_df=1` e sem remoção de stopwords.
Logística/SVM usam pesos balanceados. Grades: C = 0,1/1/10;
alpha = 0,1/0,5/1. São 18 configurações por estágio, cada qual com cinco folds.

As mesmas partições `StratifiedKFold(5, shuffle=True, random_state=42)` são
reutilizadas para todos os candidatos de um estágio. `GridSearchCV` mede F1 macro
e acurácia, com média e desvio populacional (ddof=0), `error_score='raise'`, um job e
uma thread numérica. Critério principal: maior F1 macro; desempate por acurácia,
menor desvio e ordem estável. Nenhum parâmetro é escolhido no teste.

Para o vencedor, o módulo recalcula previsões fora das folds, verifica concordância
da média com a busca e refaz o ajuste final com todos os exemplos pertinentes.
As matrizes e métricas por origem usam somente essas previsões OOF. As curvas de
validação reutilizam os três pontos da grade unidimensional do vencedor; não são
execuções simuladas nem exigem repetir ajustes já feitos.

## Limitações científicas

CV usada na seleção e OOF posterior do vencedor têm **viés de seleção**; não são
avaliação independente nem final. Não há CV aninhada nesta implementação. Folds
estratificadas não agrupam autores/envios ou famílias de paráfrases; exemplos
relacionados podem aparecer em treino e validação e elevar os escores internos.
Essa limitação é explicitada sem reabrir a curadoria ou usar o teste para corrigi-la.

Comparar humano/LLM por origem é descritivo e mistura diferenças de classes,
estilo, dificuldade e repetição. Não constitui estudo causal ou o aprofundamento
A3. O notebook permite ler os erros do treino e comparar comprimento e origem;
a interpretação científica pelo grupo permanece necessária. O resumo automático
registra confusões reais, sem substituir essa interpretação.

As probabilidades OOF são exportadas para estudos posteriores, mas nenhum limiar
é selecionado e não há A1, integração do grafo, OpenRouter ou avaliação final.
Confirmação humana das 124 frases 07E foi registrada em `USO_DE_IA.md`; não foi
estendida à revisão manual de outras frases ou à geração das cinco candidatas 07G.

## Execução manual em ambiente preparado

Os comandos abaixo são para um terminal autorizado **fora deste sandbox**, em
checkout sem segredos. Não foram executados por esta sessão. Não copie credenciais,
configurações de autenticação ou arquivos de ambientes pessoais.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip --isolated install -r requirements.txt
.venv/bin/python -m ipykernel install --prefix .venv --name rangot --display-name 'Python (RANGOT)'
.venv/bin/python -B -m unittest discover -s tests
.venv/bin/python -m nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.kernel_name=rangot \
  --ExecutePreprocessor.timeout=1800 notebooks/01_trabalho_grupo.ipynb
```

O notebook chama o mesmo módulo do script e salva seus resultados. Para executar
somente o experimento por CLI, sem repetir o notebook desnecessariamente:

```bash
.venv/bin/python -B scripts/experimentar_classificadores.py
```

O script não preenche as saídas do notebook; a entrega exige a execução completa
do notebook e a preservação das saídas reais. Se a execução falhar, não declarar
sucesso com base apenas na existência de arquivos parciais.

## Artefatos após uma execução bem-sucedida

`salvar_classificadores` oficial grava `modelos/escopo.joblib`, `modelos/tema.joblib`
e `modelos/versoes.json`. O carregamento é verificado com textos fictícios,
classes exatas, igualdade das previsões e probabilidades finitas somando um.

Em `resultados/classificadores_08/`: comparação CV, resultados completos das grades,
métricas de folds/classe/origem, previsões/probabilidades OOF identificadas por
registro lógico do treino, matrizes e curvas em CSV; três figuras SVG; versões,
hashes, parâmetros e resumo científico. Não há cópia de textos do teste.
O estado de execução só passa a concluído depois de salvar/recarregar modelos,
produzir resultados e conferir novamente a integridade.

Após a execução real, revisar resultados e saídas do notebook, registrar as versões
efetivamente utilizadas e conferir `git diff --check`. A próxima etapa é a Missão
09 — A1, limiar e integração, depois de completar as pendências da Missão 08.
