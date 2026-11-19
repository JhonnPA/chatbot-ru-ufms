---
name: rangot-auditoria
description: Auditar o repositório e os dados do chatbot RANGOT UFMS de forma offline, sem tocar em segredos ou avaliação final, produzindo uma lista de lacunas por critério.
---

# Auditoria segura do RANGOT

1. Antes de acessar qualquer arquivo, leia as restrições do `AGENTS.md`.
2. Trabalhe somente com arquivos explicitamente permitidos do projeto. Não ler `.env*`, secrets, variáveis de ambiente, históricos, Keychain ou chaves. Se existirem, não tentar acessar nem descobrir valores.
3. Verifique `grupo.yaml`, documentação, `FONTES.md`, `USO_DE_IA.md`, `dados/treino.csv`, `dados/teste.csv` (apenas quando o gestor disponibilizar o arquivo congelado), modelos, notebook, README e LINKS.
4. Nunca execute `scripts/avaliar.py` durante a auditoria; não execute scripts de OpenRouter. Somente conferir os arquivos e código-fonte oficial sem modificá-los.
5. Tabelar mínimos por intenção (seis classes), 100 de chitchat, 150 de fora_dominio, 20% treino humano/coletado; teste humano com 15/intenção, 30 social, 40 fora.
6. Identificar duplicatas exatas/normalizadas e rótulos ambíguos. Não transferir frases de teste para treino nem usar conteúdo de teste para decisões de modelo.
7. Classificar C1–C11 em concluído, parcial, pendente ou bloqueado, com caminho/evidência, pontos de risco e recomendações.
8. Anotar fatos observados e hipóteses separadamente; nunca afirmar que um dataset tem origem humana sem comprovação.
9. Produzir somente relatório e proposta de pequenas tarefas atômicas. Nenhum commit, chamada de LLM ou alteração na primeira auditoria.
