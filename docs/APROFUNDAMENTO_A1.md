# A1, limiar e integração — Missão 09

## Protocolo e resultados

Enunciado consultado: pp. 10–11 (limiar/grafo), 23 (A1) e 25 (contratos), extraídas
localmente com PDFKit. Nenhum exemplo do teste foi carregado: apenas seu SHA-256.
Dados, modelos e todos os resultados 08 foram preservados por hashes.

O A1 usa cinco folds externas comuns, estratificadas nas oito classes do treino.
Em cada treino externo, escopo, tema e modelo único selecionam C entre 0,1/1/10
em três folds internas; a calibração sigmoid tem três folds próprias e contém
todo o pipeline de TF-IDF de caracteres + SVM. O tema recebe apenas os rótulos
originais de domínio do treino externo. Isso permite medir o erro propagado;
não se concatenaram previsões 08 de tema e escopo feitas com folds incompatíveis.

| Arquitetura | F1 macro média ± desvio | Acurácia média | Erros OOF | Falsos aceites | Falsas recusas |
|---|---:|---:|---:|---:|---:|
| Cascata, seleção interna | 0,882105 ± 0,014006 | 0,889091 | 61 | 20/250 | 13/300 |
| Único, seleção interna | 0,885115 ± 0,018913 | 0,890909 | 60 | 17/250 | 20/300 |

O único tem vantagem numérica pequena: +0,003010 em F1 e um erro a menos.
Vence em quatro das cinco folds, mas perde cerca de 0,0427 na terceira; não há
afirmação de significância estatística ou superioridade universal. A cascata
reduz falsas recusas e permite diagnóstico separado de escopo, ao custo de mais
componentes. Na cascata, 13 perguntas legítimas foram perdidas no escopo, incluindo
11 cujo tema estaria correto; 22 passaram pelo escopo e tiveram tema errado.

Nesta execução, o único ajustou mais rápido e teve aproximadamente metade do
tempo de predição **diagnóstica batch**. Esse diagnóstico calcula tema para toda
a validação para medir propagação; a rota online pula o tema nas recusas e não
tem latência medida aqui. Os tamanhos serializados em memória ficaram próximos,
com o único ligeiramente maior, apesar de usar um único vocabulário. Os valores
por fold e tempos reais estão em `a1_custos.csv`, sem pretensão de benchmark.

O único permanece experimental. A integração usa a cascata 08, com os dois
classificadores e classes exigidas pelo contrato, preservando seus arquivos.
O A1 atende à comparação de arquiteturas sem substituir os modelos de referência.

## Limiar de produção: 0,60

Uma terceira linha, `cascata_referencia_08`, produz OOF nas mesmas folds externas
com C fixos da produção (escopo=1; tema=0,1). O limiar é escolhido a partir desse
fluxo completo, incluindo não-domínio aceito pelo escopo.

Pesos declarados antes de executar: falso aceite=5, intenção errada=3,
esclarecimento=1, falsa recusa=2, troca social/fora=1. Minimizar o custo total;
empate por mais acertos diretos e menor limiar. Esses pesos são decisão interna
assistida por IA, não uma regra do professor nem uma utilidade validada com usuários.

| Diagnóstico OOF da referência 08 | Sem limiar | Limiar 0,60 |
|---|---:|---:|
| Respostas diretas de intenção | 303 | 271 |
| Respostas diretas erradas | 41 | 21 |
| Acurácia condicional das respostas diretas | 86,47% | 92,25% |
| Esclarecimentos | 0 | 32 |
| Falsos aceites | 19 | 13 |
| Custo total declarado | 199 | 159 |
| F1 macro ponta a ponta | 0,878652 | 0,883098 |
| Acurácia ponta a ponta | 0,885455 | 0,863636 |

São 20 erros diretos evitados e 12 acertos convertidos em esclarecimento.
Esclarecimento não conta como acerto da intenção. A sensibilidade deu 0,60 para
pesos de erros diretos (3,2) e (5,3), mas 0,85 para (8,5): não existe limiar ótimo
independente do custo adotado. Alterou-se somente `roteamento.limiar_tema` no YAML.
A rejeição inicial continua decidida pelo classificador de escopo; nenhum limiar
novo ou decisão de rota por LLM foi introduzido.

## Integração e limitações observadas

A API `construir_grafo(config, clf_escopo, clf_tema)` foi preservada. O grafo
existente já aplica o limiar e fornece respostas fixas sem LLM; não precisou ser
refatorado. Testes com classificadores controlados cobrem as seis intenções,
chitchat, fora_dominio e esclarecimento; impedem acesso à função de credenciais.

Dez perguntas fictícias foram fixadas antes de conhecer os resultados. Nos oito
casos com classe esperada, cinco retornaram a rota pretendida, dois confundiram
cardápio/pagamento com valores e um cadastro foi esclarecido. Todos tiveram rota
e resposta fixa. A pergunta ambígua foi tratada como social, e a mensagem com duas
intenções recebeu apenas valores. Esses resultados estão preservados, sem
retocar exemplos, modelos ou limiar para fazê-los passar.

O classificador de rótulo único e o limiar não garantem detectar ambiguidade ou
múltiplas intenções. Erros confiantes ainda podem receber resposta; a interação
requer uma solicitação por vez. O limiar oferece esclarecimento quando o tema é
incerto, sem inferir que todos os casos ambíguos terão confiança baixa.

## Reprodutibilidade e artefatos

```bash
.venv/bin/python -I -B scripts/aprofundar_classificadores.py --gravar
.venv/bin/python -I -B -m unittest discover -s tests
```

`--gravar` exige escrita e exporta resultados/configura o limiar. No sandbox desta
sessão, a execução usou `--emitir-json` em memória e o editor permitido persistiu
os artefatos textuais calculados. O Matplotlib não conseguiu abrir cache gravável;
as duas figuras SVG standalone foram construídas diretamente das tabelas reais,
sem bibliotecas adicionais, rede ou acesso a pastas pessoais.

O notebook conserva integralmente as 31 células/saídas 08 e acrescenta 11 células
09, incluindo seis de código efetivamente executadas em Python 3.12.13, com stdout
e displays reais capturados. O executor foi registrado nos metadados; não se
alega execução dessas novas células por kernel Jupyter. O código continua
executável em Jupyter preparado. As células calculam novamente o A1 e exibem
análise, figuras, tabela de limiares e cenários reais da integração fictícia.

`resultados/aprofundamento_09/` contém tabelas por fold, OOF, confusões,
propagação, C escolhidos, custos, limiares/sensibilidade, integração, dois SVGs,
metadados com hashes e resumo científico derivado dos resultados.
Na tabela OOF, `confianca_tema=0` do classificador único é uma sentinela de campo
não aplicável: ele não possui estágio de tema separado. Não é sua probabilidade
de previsão e não é usada na seleção do limiar.

Persistem limites estatísticos: família/representação escolhidas com o mesmo
treino na 08; famílias/autorias atravessam folds; seleção e descrição do limiar
nos mesmos OOF; ausência de validação independente dos custos. Não interpretar
estes valores como desempenho no teste reservado ou como nota C7. Resultados e
decisões técnicas assistidas por IA ainda precisam ser compreendidos e conferidos
pelo grupo. Nenhum avaliador oficial, verificador ou OpenRouter foi executado.
