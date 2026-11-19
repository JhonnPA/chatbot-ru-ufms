# Auditoria inicial — RANGOT (17/11/2026)

Fonte: pacote `chatbot-ru-ufms-develop.zip` enviado pelo grupo e dois CSVs não versionados. Esta é uma fotografia do ZIP, não uma afirmação sobre o estado remoto atual.

## Verificado

- `grupo.yaml`: 6 intenções (`cardapio`, `horarios`, `valores`, `recarga_creditos`, `cadastro`, `regras_uso`); limiar `roteamento.limiar_tema` = 0.0, não fundamentado experimentalmente.
- `documentos/`: 8 documentos de domínio, `FONTES.md` existente. Verificar conteúdo, rastreabilidade e cobertura por intenção posteriormente.
- `dados/treino.csv` e `dados/teste.csv`: somente cabeçalho. **Nenhum registro** de treino ou teste preparado na branch do ZIP.
- `modelos/`: apenas `.gitkeep`; sem `escopo.joblib` ou `tema.joblib` do RANGOT. Os modelos em `exemplos/biblioteca/` não são os da UFMS.
- `notebooks/01_trabalho_grupo.ipynb`: notebook modelo com TODOs e 0 outputs executados; requer desenvolvimento.
- `LINKS.txt`: video/repositório não preenchidos. `relatorio/`: README, sem artigo PDF.
- `USO_DE_IA.md`: versão inicial; atualizar com TODOS os novos usos de IA, inclusive este planejamento e futuras alterações com Codex.
- A listagem do ZIP **não contém arquivo `.env`**. Isso não prova que não exista segredo dentro de algum arquivo versionado; uma verificação de segurança independente ainda é necessária. Não lemos a chave.

## CSV 1 — formulário exportado do Google Forms

- 35 registros; 11 colunas, incluindo carimbo de data/hora.
- Seis perguntas específicas do RU: 35 respostas por intenção (210 brutas).
- Duas perguntas negativas de serviços próximos: 35 cada (70 brutas).
- Conversa social: 34 respostas (uma ausente); pelo menos 30 antes da revisão da qualidade.
- Campo aberto adicional sobre o RU: 35 respostas que exigem rotulagem manual e que podem ser reservadas, mas **não utilizar para treino se pertencem aos participantes do conjunto de teste**.
- Há algumas duplicatas após normalizar pontuação/acentos: inspecionar e excluir apenas com preservação de proveniência.
- A origem das frases do formulário deve ser confirmada como humana pelo responsável. Se confirmado, pode atender à quantidade mínima de teste, reservando esse conjunto de uma vez e mantendo-o intocado para seleção dos modelos.

## CSV 2 — respostas_chatbot_ru.csv

- 132 linhas, 10 colunas; parece seguir as dez perguntas do Forms, mas sem timestamps nem identificação de origem.
- Seis perguntas de intenção, duas negativas, campo aberto e uma pergunta social; a última tem **44 respostas, apenas 22 únicas depois de normalização**. Nas demais há repetições normalizadas.
- Quatro textos normalizados coincidem com o formulário, distribuídos nas colunas correspondentes; remover todo vazamento entre treino e teste.
- Origem **não comprovada**: não classificar automaticamente como `humano` nem incluir no teste. Se for sintético, usar `origem=llm` apenas se a geração e modelo/prompts forem comprovados; se outra origem, documentá-la corretamente.
- Mesmo que se aproveite como treino, **chitchat exigirá complemento** para chegar a 100 mensagens distintas.

## Critérios de nota e etapas

- C1 5pts: conteúdo configurado, validação e coerência a revisar.
- C2 15pts: **bloqueador**. Treino/teste finais ainda não estruturados; confirmar origem, separar teste e atingir mínimos de treino/humanos.
- C3+C4 24pts: **bloqueador**. Experimentos de escopo e tema ainda não executados/salvos.
- C5 10pts: base de documentos presente; integração/limiar e demonstração ausentes.
- C6 10pts: A1 (cascata vs classificador único) recomendado, não executado.
- C7 10pts: desempenho desconhecido; teste final deve rodar uma vez ao final.
- C8 10pts: análises de erro, CV×teste e origem ainda ausentes.
- C9 6pts: artigo SBC ausente.
- C10 5pts: vídeo ausente no ZIP.
- C11 5pts: notebook não executado, README e verificador precisam ser finalizados.

## Decisão científica indispensável

Antes de escrever dados, confirmar a proveniência do CSV complementar e manter reserva independente de teste humano. Meta de treinamento: >=590 frases (50 x 6 +100+150), >=118 humano/coletado. Meta de teste: >=160 (15 x 6 +30+40), 100% humano/coletado. Evitar usar o teste para ajustes ou como fonte de novos dados de treino.
