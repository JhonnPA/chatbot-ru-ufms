# Mac: preparar uma cópia segura do RANGOT e iniciar o Codex

**Atenção:** um `.gitignore`, um `AGENTS.md` e `env -u` não impedem tecnicamente um processo com acesso ao sistema de ler segredos. Para a exigência absoluta de não leitura, use uma VM/container/conta isolada com sistema de arquivos e credenciais separados. Uma segunda cópia do repositório sem `.env` no mesmo usuário reduz o risco, mas por si só não prova isolamento contra leitura de outras pastas.

## Preparação humana, fora do Codex

Instalar Codex CLI se necessário: `brew install --cask codex` ou `npm install -g @openai/codex`. Autenticação do Codex é separada da chave do OpenRouter.

No Terminal, com ambiente destinado ao Codex **sem segredos acessíveis**:

```bash
mkdir -p "$HOME/Projetos"
cd "$HOME/Projetos"
git clone --branch develop https://github.com/JhonnPA/chatbot-ru-ufms.git rangot-codex
cd rangot-codex
# Não continue se a cópia tiver arquivos de credenciais. Não abra seu conteúdo.
if [ -e .env ]; then echo 'PARE: .env presente nesta cópia'; exit 1; fi
git switch -c feature/infra-codex-seguro
```

Baixar o pacote `RANGOT_CODEX_SETUP.zip` e extrair no diretório recém-clonado, **sem sobrescrever arquivos existentes**:

```bash
unzip -n "$HOME/Downloads/RANGOT_CODEX_SETUP.zip" -d .
git status --short
git check-ignore .env
```

`git check-ignore .env` deve exibir `.env`, confirmando que o nome é ignorado; isso não é uma garantia contra leitura, apenas Git.

## Primeira sessão (auditoria read-only)

```bash
codex --sandbox read-only --ask-for-approval on-request -c 'model_reasoning_effort="xhigh"'
```

Cole o conteúdo de `docs/PROMPT_PRIMEIRA_SESSAO_CODEX.md` como mensagem inicial. Na CLI, confira o painel de permissões (`/permissions`): somente leitura, sem acesso ampliado. Não autorize pedidos de rede/credenciais.

## Sessões seguintes, após aprovar uma tarefa pequena

```bash
codex --sandbox workspace-write --ask-for-approval on-request -c 'model_reasoning_effort="xhigh"'
```

`.codex/config.toml` também define `xhigh`/workspace-write/sem rede (quando o projeto é confiável), mas flags explícitas prevalecem. Se o modelo atual não aceitar `xhigh`, consultar os níveis suportados e ajustar o esforço, sem substituir por um modelo de OpenRouter caro. O esforço do Codex não altera `grupo.yaml`.

## Commits atômicos

Depois de revisar o escopo da alteração feita, e antes de commitar, confira:

```bash
git status --short
git diff --check
git add AGENTS.md .codex/config.toml .agents/skills docs/AUDITORIA_INICIAL_RANGOT.md docs/PROMPT_PRIMEIRA_SESSAO_CODEX.md docs/GUIA_LOCAL_MAC_GIT.md
git diff --cached --name-only
git diff --cached --check
git commit -m "chore(codex): configurar fluxo seguro e skills do RANGOT"
```

Antes de cada novo assunto, partir de `develop` atualizado e criar branch `feature/*`; produzir uma sequência de commits semânticos pequenos; abrir PR para `develop` após validação humana, **não fazer push/merge automático**. Se já tiver um AGENTS.md/config, primeiro revise e mescle as diferenças manualmente.

## Trabalho científico / datas

- Primeiro: curadoria dos CSVs (origens), congelamento do teste humano e treino >=20% humano.
- Depois: comparações e CV só com o treino, modelos, limiar, aprofundamento A1.
- Só depois: avaliação final no teste UMA vez (offline), sem otimizá-lo depois.
- Fechar artigo, vídeo, `USO_DE_IA.md`, notebook executado, verificador e ZIP final com `git archive -o entrega_rangot.zip HEAD`.

O ZIP do professor (18/11 23:59) deve ser a versão commitada, sem `.env`. Em caso de chave já divulgada fora do local permitido, solicitar rotação ao professor.
