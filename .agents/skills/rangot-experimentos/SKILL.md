---
name: rangot-experimentos
description: Implementar e conferir os experimentos offline de classificação de escopo e intenção do RANGOT com TF-IDF, CV, F1 macro, tuning e aprofundamento A1, evitando vazamento de teste.
---

# Experimentos científicos reproduzíveis

## Protocolo obrigatório

- **Isolar conjunto de teste**: nenhuma avaliação repetida ou escolha de parâmetros pelo teste. Não buscar/copiar/gerar exemplos do teste ao construir treino.
- Treino tem rótulos `texto,intencao,origem`. Etapa 1: `dominio/chitchat/fora_dominio`; etapa 2: apenas intenções do domínio.
- Pelo menos 3 algoritmos vistos em aula (por exemplo Regressão Logística, MLP, Árvore) e 2 representações (TF-IDF de palavras, de caracteres), para ambos os estágios.
- Pipeline completo (vetorizador + classificador) dentro de `StratifiedKFold(5, shuffle=True, random_state=42)`. F1 macro como principal; registrar média e desvio, acurácia, gráficos e matriz de confusão de CV.
- Ajuste do melhor candidato via GridSearchCV **somente no treino**. Reportar grades e curva de validação sem usar dados de teste.
- Usar previsões out-of-fold de treino para limiar e contagem de esclarecimentos. Alinhar classes de `predict_proba` e observar conjuntos vazios ao calcular métricas.
- Reportar falso aceite (`fora_dominio/chitchat` aceito como `dominio`), falsa recusa (`dominio` rejeitado), confusões do estágio 2, exemplos de erros e limite do estudo.
- A1: comparar uma cascata com um classificador único de 8 classes, no mesmo conjunto de CV, de forma comparável, sem LLM. Documentar quando a cascata ajuda e custos de propagação de erro.
- Salvar somente pipelines carregáveis (sem definições de função dentro do notebook) usando `salvar_classificadores`.
- Não modificar nem contornar scripts de avaliação oficiais; não executar `avaliar.py` no teste antes de autorização. Nenhuma chamada à API externa ou leitura de segredos.

## Entrega da etapa

Gerar notebook completo e reproduzível, métricas de CV autênticas, arquivos dos modelos válidos, metodologia replicável, análises e commits atômicos **após autorização**. Não declarar desempenho no teste até avaliação final autorizada.
