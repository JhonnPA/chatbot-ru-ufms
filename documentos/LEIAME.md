# Base de conhecimento do grupo

Coloquem aqui os **documentos do tema com proveniência explícita**: fontes oficiais,
reorganizações de fontes oficiais e textos do grupo devem ser diferenciados em
`FONTES.md`. É deles que o bot tira as respostas quando o LLM está ligado (RAG).
Formatos aceitos: `.pdf`, `.md`, `.txt`,
`.html`. Este arquivo (`LEIAME.md`) e o `FONTES.md` não entram na base.

```
documentos/
├── FONTES.md            ← obrigatório: de onde veio cada documento
├── geral/               ← vale para qualquer intenção (regimento, FAQ geral, contatos)
├── <intencao_1>/        ← uma pasta com o NOME EXATO de cada intenção do grupo.yaml
├── <intencao_2>/
└── ...
```

* Mínimo de **5 documentos** no total; o ideal é cada intenção ter o seu.
* Bons documentos: regulamentos, resoluções, editais, páginas de perguntas
  frequentes, manuais (baixe as páginas como PDF ou HTML, ou copie o texto para
  `.md`). Podem ser documentos reais da UFMS (citem a URL) ou textos escritos pelo
  grupo, desde que plausíveis e coerentes com as respostas do `grupo.yaml`.
* PDF escaneado (imagem) não tem texto extraível: prefira a versão digital.
* Depois de mudar os documentos, nada a fazer: o índice em `.vectordb/` é recriado
  sozinho; mudanças em `FONTES.md`, configuração e código da base também invalidam
  o cache. O catálogo não é indexado como resposta: sua proveniência acompanha
  os trechos, sem participar da pontuação lexical. Para testar a busca sem gastar créditos:
  `python scripts/indexar_documentos.py --buscar "sua pergunta"`.
* Veja o exemplo completo em `exemplos/biblioteca/documentos/`.

O guia de composição não é um cardápio datado. Não copiar os PDFs semanais de
`referencias/_brutos/cardapios/` como documentos permanentemente vigentes, nem
duplicar o guia bruto que já fundamenta os resumos. Pagamento é relato do grupo;
o texto de conduta registra uma lacuna documental e não cria permissões/proibições.

Na integração 10B, `regras_uso/` também contém os procedimentos de serviço do
Guia 2026 efetivamente conferidos, sem convertê-los em regulamento integral.
O canal permanente de cardápios contém somente orientação de consulta e limites,
sem pratos históricos nem comandos ao LLM. O endereço físico do RU não foi
confirmado; os contatos institucionais estão em `geral/contatos_ru.md`.

Pesquisas, conflitos detalhados, matrizes e candidatos devem ficar fora de
`documentos/`. A palavra `NAO_INDEXAR` no nome não exclui um Markdown da busca.
O dossiê em `referencias/_brutos/dossie_integracao/` não é corpus aprovado.
Não usar resumos de IA como se fossem originais oficiais nem interpretar sua
data de consulta como data atual de uma conversa.
