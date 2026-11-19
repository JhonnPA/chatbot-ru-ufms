---
name: rangot-entrega
description: Revisar checklist, conformidade científica, documentação e pacote de entrega do RANGOT da UFMS, com verificação offline sem chaves e sem alteração no avaliador.
---

# Checagem final da entrega

1. Verificar contrato: CSVs, modelos, `grupo.yaml`, APIs do grafo, arquivos oficiais intactos e dependências em `requirements.txt`.
2. Revisar notebook executado (saídas reais, sem segredos), matrizes, limiar, aprofundamento e relatórios de CV/teste. Não usar o teste novamente para otimização.
3. Conferir `USO_DE_IA.md`, seção de IA e contribuições no artigo, declaração verbal no vídeo; nenhuma omissão de uso de Codex/LLM/ChatGPT.
4. Artigo SBC <=10 páginas incluindo referências, figuras legíveis, `relatorio/relatorio.pdf`.
5. Vídeo <=10 minutos, todos integrantes aparecem, demonstração de acerto, erro e pergunta não respondível, URL em `LINKS.txt` e artigo.
6. Verificador oficial `python scripts/verificar_entrega.py` somente na cópia isolada **sem nenhum arquivo secreto**. Nunca alterar este script nem qualquer verificador oficial.
7. Testes finais de integridade de dados e staging via **nomes de arquivos**, não conteúdos secretos. Jamais `git add -f .env` ou `git add -A` cegamente.
8. Após revisão humana, commit dos artefatos necessários e `git archive -o entrega_rangot.zip HEAD`; inspecionar listagem interna do ZIP sem conteúdo de segredos. Conferir prazo no AVA.
