# A1, limiar e integração — resultados reais da Missão 09

Cinco folds externas comuns estratificadas nas oito classes; busca de C em três folds internas, calibração em três folds próprias. SVM linear calibrada e TF-IDF char_wb (2,5) em ambas as arquiteturas. O tema é ajustado somente nos rótulos originais de domínio do treino externo. Sem teste reservado.

## A1: desempenho ponta a ponta

```csv
arquitetura,f1_macro_media,f1_macro_desvio,accuracy_media,accuracy_desvio,f1_macro_oof,accuracy_oof,erros_oof,falsos_aceites_oof,falsas_recusas_oof,taxa_falso_aceite_oof,taxa_falsa_recusa_oof
cascata_cv_interna,0.8821050625944131,0.014005977819395238,0.889090909090909,0.010601730717900566,0.8825190070892993,0.889090909090909,61,20,13,0.08,0.043333333333333335
unico_cv_interna,0.8851152036523725,0.018913247406286998,0.890909090909091,0.019069251784911864,0.8854211136755381,0.8909090909090909,60,17,20,0.068,0.06666666666666667
```

Diferença de F1 macro médio (único − cascata): 0.003010. A diferença é pequena e as folds não são amostras independentes; não se afirma significância ou superioridade geral. A família/representação foi informada pela 08, portanto a busca interna de C não elimina todo o viés de seleção anterior.

O classificador único tem uma vetorização e aprende as oito classes conjuntamente. A cascata separa explicitamente o escopo e reduz o conjunto do tema, mas paga duas calibrações/vetorizações e pode bloquear perguntas cujo tema seria reconhecido. Os arquivos de produção 08 foram preservados: o único é comparação experimental, e a integração continua usando os dois classificadores exigidos pelo contrato.

## Propagação de erros

```csv
arquitetura,n_dominio,dominio_perdido_no_escopo,tema_correto_mas_bloqueado_pelo_escopo,dominio_passou_mas_tema_errou,n_nao_dominio,nao_dominio_encaminhado_ao_tema
cascata_cv_interna,300,13,11,22,250,20
cascata_referencia_08,300,16,14,22,250,19
```

## Custo observado

```csv
arquitetura,segundos_ajuste,ms_por_mensagem_batch,bytes_modelos_em_memoria,vocabularios_soma
cascata_cv_interna,1.2458157335961004,0.07040151458402925,609792.8,11841.2
unico_cv_interna,0.9195486081967829,0.036521665434437724,614408.4,7434.2
```

Tempos são observações locais, um job/thread, sem benchmark estatístico. A predição diagnóstica da cascata calcula tema para toda a validação para analisar propagação; não equivale à latência online, que pode pular o tema nas recusas. O tempo da cascata de referência registra só refits adicionais/reuso e não deve ser comparado com o ajuste completo das arquiteturas. Tamanhos são serializações em memória de modelos das folds, não novos arquivos de produção.

## Limiar operacional da cascata 08

Limiar de tema escolhido: 0.60. Critério pré-declarado: custo de falso aceite 5, intenção errada 3, esclarecimento 1, falsa recusa 2 e troca social/fora 1. São pesos internos, não uma exigência do professor nem utilidades validadas com usuários.

Sem limiar: 303 respostas de intenção, 41 erradas, precisão condicional 86.4686%. Com limiar: 271 respostas de intenção, 21 erradas, precisão condicional 92.2509%; 32 esclarecimentos, 20 erros evitados e 12 acertos convertidos. Custo total 199 → 159. F1 ponta a ponta no mesmo OOF: 0.878652 → 0.883098; esclarecimento não é acerto de intenção.

O limiar usa previsões OOF das configurações fixas 08, produzidas nas folds comuns desta missão; não mistura OOF de tema/escopo com divisões incompatíveis. A seleção e a descrição do limiar usam os mesmos OOF e são otimistas. Não há avaliação independente da política; famílias/autores podem atravessar folds. A sensibilidade dos pesos está em limiares_sensibilidade.csv, sem escolher pesos pelos resultados.

## Integração e limites semânticos

```csv
tipo_esperado,rota,confianca_intencao,fonte_resposta
cardapio,valores,0.885929109741886,fixa
horarios,horarios,0.9235888574672001,fixa
valores,valores,0.8645347871753708,fixa
recarga_creditos,valores,0.6826485616483978,fixa
cadastro,esclarecer,0.5875102439203995,fixa
regras_uso,regras_uso,0.9488506705437946,fixa
chitchat,chitchat,0.0,fixa
fora_dominio,fora_dominio,0.0,fixa
ambiguo_sem_rotulo_unico,chitchat,0.0,fixa
multiplas_intencoes,valores,0.6397561202183233,fixa
```

Todos os cenários são fictícios, fixados antes da seleção do limiar, sem entrar nos CSVs científicos. As respostas são fixas e não usam chave ou OpenRouter. Os testes contratuais com classificadores controlados cobrem seis intenções, social, fora e esclarecimento; eles não demonstram qualidade semântica dos modelos reais.

Os casos naturais permanecem no relatório inclusive quando falham. Limiar de confiança não é detector garantido de ambiguidade ou múltiplas intenções: uma pergunta ambígua pode ser classificada como social, e uma pergunta composta pode receber somente a intenção dominante. Erros confiantes de cardápio/pagamento também podem passar pelo limiar. Não se modificaram frases, pesos ou modelos para fazer estes exemplos passar.

Próxima etapa: revisão dos resultados pelo grupo e preparação autorizada do RAG. Nenhuma avaliação oficial ou verificação de entrega foi executada.
