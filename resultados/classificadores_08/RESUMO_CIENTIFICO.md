# Resultados científicos — Missão 08

Resultados reais de treino/CV interna. CV interna usada para escolher algoritmos/representacoes/hiperparametros. Medias da busca e OOF do vencedor possuem vies de selecao: nao sao estimativa independente ou teste final. Nao foi realizada CV aninhada. Familias de parafrases e autores podem atravessar folds estratificadas; nao houve agrupamento por familia/autoria, o que pode elevar os resultados. Comparacoes por origem sao descritivas, sem controle causal de classe, estilo ou dificuldade. As probabilidades OOF nao definem limiar nesta missao; A1 e limiar ficam para a Missao 09.

## escopo

Selecionado: svm_calibrada/caracteres; parâmetros: {"calibrado__estimator__classificador__C": 1.0}.
F1 macro CV: 0.922867 ± 0.013300; acurácia: 0.930909 ± 0.014771.
A configuração foi escolhida pelo maior F1 macro, com desempates definidos antes da execução.

Diagnóstico OOF: {"f1_macro_oof_agrupado": 0.9230893654149468, "accuracy_oof_agrupada": 0.9309090909090909, "n": 550, "erros": 38, "falsos_aceites": 17, "falsas_recusas": 15, "n_nao_dominio": 250, "n_dominio": 300, "taxa_falso_aceite": 0.068, "taxa_falsa_recusa": 0.05}

Por origem (descrição, sem interpretação causal):

etapa,origem,n,f1_macro,accuracy
escopo,humano,268,0.9271254075851777,0.9440298507462687
escopo,llm,282,0.9167663817663817,0.9184397163120568

Confusões observadas (quantidades OOF):

etapa,real,predito,quantidade
escopo,fora_dominio,dominio,11
escopo,dominio,fora_dominio,9
escopo,dominio,chitchat,6
escopo,chitchat,dominio,6
escopo,chitchat,fora_dominio,4
escopo,fora_dominio,chitchat,2

## tema

Selecionado: svm_calibrada/caracteres; parâmetros: {"calibrado__estimator__classificador__C": 0.1}.
F1 macro CV: 0.919959 ± 0.024508; acurácia: 0.920000 ± 0.024495.
A configuração foi escolhida pelo maior F1 macro, com desempates definidos antes da execução.

Diagnóstico OOF: {"f1_macro_oof_agrupado": 0.9203778393448444, "accuracy_oof_agrupada": 0.92, "n": 300, "erros": 24}

Por origem (descrição, sem interpretação causal):

etapa,origem,n,f1_macro,accuracy
tema,humano,190,0.9399465406748932,0.9368421052631579
tema,llm,110,0.8846309809899536,0.8909090909090909

Confusões observadas (quantidades OOF):

etapa,real,predito,quantidade
tema,horarios,cardapio,3
tema,valores,cardapio,3
tema,recarga_creditos,valores,2
tema,cadastro,recarga_creditos,2
tema,cardapio,horarios,1
tema,regras_uso,cardapio,1
tema,cadastro,regras_uso,1
tema,cadastro,valores,1
tema,recarga_creditos,regras_uso,1
tema,recarga_creditos,cadastro,1
tema,recarga_creditos,cardapio,1
tema,cardapio,valores,1
tema,valores,regras_uso,1
tema,valores,horarios,1
tema,horarios,valores,1
tema,cardapio,regras_uso,1
tema,cardapio,cadastro,1
tema,regras_uso,valores,1

## Limites e próximos passos

Inspecionar os erros de treinamento mostrados no notebook; não reinterpretar a CV como desempenho em pessoas/autorias independentes. A comparação humano/LLM mistura diferenças de classe, estilo e repetição. Falso aceite produz resposta fora de escopo e falsa recusa reduz cobertura. Não alterar dados ou modelos a partir do teste reservado. A Missão 09 fará A1, limiar e integração; avaliação oficial permanece não executada.
