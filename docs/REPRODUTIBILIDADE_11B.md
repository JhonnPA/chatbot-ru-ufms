# Missão 11B — reprodução integral do notebook

Registro de 19/11/2026. Referência inicial: d50e005d8026859c3346d14217da37f1c66f4ae9,
branch feature/rag-openrouter-rangot, checkout inicialmente limpo.

**Estado atual: Missão 11B concluída. Reprodução integral aprovada e notebook
executado incorporado, sem substituir dados, modelos ou resultados oficiais.**

## Execução aprovada e incorporação

Cleiton Pinheiro Rodrigues executou manualmente o procedimento no terminal
autorizado do macOS em **19/11/2026**, conforme sua confirmação expressa.
A implementação e a conferência das evidências tiveram assistência do Codex;
a execução integral externa não é atribuída ao Codex.

Diretório real: /private/tmp/rangot-repro-11b-fs6erytm.
Foram lidos os arquivos reais em evidencias/: APROVACAO.json, comparacoes.json,
testes.log, integridade_antes.json, integridade_depois.json e versoes.json.
Também foram conferidos o notebook reproduzido, o backup externo e os hashes
dos dois modelos produzidos na cópia. A conclusão não depende apenas do relato.

| Verificação | Resultado conferido |
|---|---|
| APROVACAO.json | aprovada=true; integridade_principal=true; nenhum protegido alterado |
| Notebook | 42 células; 22 de código; contadores 1 a 22; nenhuma saída de erro |
| Comparação 08 | 12 linhas; diferença absoluta máxima 0,0 |
| Comparação 09 | 3 linhas; diferença absoluta máxima 0,0 |
| Limiar e intenções | 0,60; seis intenções preservadas |
| Suíte na cópia | 160 testes aprovados, conforme testes.log |
| Integridade | 39 hashes antes=depois=checkout principal |

Além dos JSONs, as tabelas reproduzidas 08/09 foram comparadas diretamente com
as publicadas no checkout: igualdade exata nas colunas científicas verificadas,
incluindo médias/desvios e parâmetros 08. Tempos não são critério de igualdade.
Os metadados do notebook registram 2026-11-19T15:50:56.819027+00:00.

Antes da incorporação, o backup externo
evidencias/notebook_corrigido_antes.ipynb foi conferido byte a byte com a versão
então presente no checkout e preservado sem sobrescrita. Seu SHA-256 é
a364227bf194e66c5ed2cbc9ba9977af76faab810f587bad205f217bc5c90a41.

Somente notebooks/01_trabalho_grupo_reproduzido.ipynb foi incorporado a
notebooks/01_trabalho_grupo.ipynb. Código, Markdown, IDs e ordem das células
coincidem integralmente com a versão corrigida. As diferenças são outputs,
contadores, metadados de execução e o registro de reprodução manual.
JSON/schema foram validados. O arquivo incorporado é idêntico à origem,
com SHA-256 d3bfa6c6e7bf4ff7343b1ac266c453a02aea61f9980db6c55cb39d6f04a39c5c.

As notas da preparação bloqueada presentes no Markdown e nos metadados de edição
do notebook são históricas; suas fontes foram preservadas junto à execução.
O estado atual está documentado aqui e em reproducao_manual_11b, com as 22 saídas
reais. Não houve restauração artificial de outputs nem alteração de fontes após
a execução para criar aparência de reprodução.

Os modelos reproduzidos permaneceram somente na cópia isolada:

| Modelo reproduzido, não incorporado | SHA-256 |
|---|---|
| Escopo | 12a4677171eb9f5017fe1de34d8d427c1c412cab290e54bc0e3dac66716d96f1 |
| Tema | 626cea921001d32b19b500039d414d6ef6ad009a8309b8db6fd0b7912cec8133 |

Para rastreabilidade, SHA-256 de APROVACAO.json:
e2dae5591f19de62ab402c5c35506b5b62b1ec525eec9d3f7baca42b212d9818.
Os dois manifestos de integridade têm o mesmo SHA-256:
9e5a2915305ea966e2baec711a2bcd9d97048c6b0633a569db9cb21b8e61b02e.
Não foram copiados modelos, CSVs ou resultados da pasta temporária para o Git.

## Histórico do bloqueio inicial

Na etapa inicial, o sandbox recusou criar a cópia descartável:
~~~text
mktemp -d /tmp/rangot-repro-11b-XXXXXX
mktemp: mkdtemp failed [...] Operation not permitted
~~~
Não houve ampliação de permissões nem execução do notebook no checkout principal.
O Codex executou **0 das 22 células** naquela etapa e preparou o procedimento
para o responsável. Esse bloqueio histórico foi superado pela execução manual
integral acima, sem treinamento científico no checkout principal.

## Causa-raiz e caminhos de gravação

O enunciado original de 29 páginas foi consultado; prevalecem suas interfaces,
a separação treino/teste e os requisitos experimentais. A falha foi confirmada
por inspeção das chamadas e por reserialização em memória, sem repetir o treino.

A célula de índice 23 chama finalizar(), em chatbot/experimentos.py. Essa rotina
chama validar_serializacao() e salvar_classificadores(), grava modelos/escopo.joblib,
modelos/tema.joblib e modelos/versoes.json, além das tabelas, SVGs e metadados em
resultados/classificadores_08/. Os caminhos vêm de grupo.yaml e da raiz do projeto.

A célula de índice 32 chama executar_memoria(), que chama comparar() e
referencias(), em chatbot/aprofundamento.py. Antes da correção, referencias()
exigia os SHA-256 binários originais da Missão 08. Uma serialização legítima
produzida pela célula 23 podia divergir desses bytes e ser rejeitada. A checagem
reaparecia ao final de comparar(), executar_memoria() e na célula 41.
Os índices são os do JSON do notebook, começando em zero; não são contadores
de execução do kernel.

As células anteriores ajustam os candidatos em memória; a célula 23 é o ponto
de exportação 08. A1 produz seus artefatos em memória; a célula 41 corrigida
exporta-os somente na cópia descartável, sem chamar gravar(), que altera YAML.
Os gráficos 08 dependem dos arquivos escritos na célula 23. As tabelas originais
08/09 e os modelos oficiais são agora carregados antes de qualquer ajuste.
Não é necessário nenhum arquivo privado ignorado pelo Git.

Há quatro verificações distintas:

- Integridade binária: um SHA-256 identifica exatamente os bytes de um artefato
  oficial ou de um novo snapshot; continua necessária.
- Equivalência funcional: classes, previsões e probabilidades podem coincidir
  mesmo quando os bytes diferem. Sondas finitas não provam igualdade para toda
  entrada possível.
- Reprodução científica: métricas, parâmetros, folds e protocolo devem ser
  confrontados com os resultados publicados, independentemente do hash binário.
- Contrato: os pipelines precisam manter classes, predict/predict_proba,
  serialização e compatibilidade com o grafo; não basta ter métricas parecidas.

Na verificação em memória dos dois oficiais, carregar→serializar→recarregar
mudou ambos os SHA-256, mas manteve classes, previsões e probabilidades em duas
entradas fictícias (diferença máxima 0). Os hashes reserializados foram:

| Modelo | SHA-256 da reserialização em memória, sem novo ajuste |
|---|---|
| Escopo | 5d650ec9bbdf5bf04876d6d5eb6a520cafbcdc3f6102f439f32a5ab67a8379f0 |
| Tema | c32583e791c6a4afabd153485085f4c88992345050aad18674c2bb39e5606bf9 |

Isso confirma que identidade binária não é requisito de equivalência nessas
sondas. Isoladamente, aquele diagnóstico não comprovava reprodução de treino;
a execução integral posterior é a evidência registrada no encerramento.
Representação interna do objeto, memoização do serializador, compressão e
versões de Python/joblib/sklearn podem afetar os bytes. Esta missão não atribui
o caso original a uma dessas causas isoladas sem evidência adicional.

## Correção mínima

1. O notebook recusa executar quando a raiz contém .git, antes de ajustar ou
   gravar modelos. Deve ser usado em cópia independente de git archive.
2. Autentica os hashes oficiais e guarda os objetos oficiais e as tabelas
   publicadas em memória antes do experimento 08.
3. Após a exportação 08, validar_modelos_reproduzidos() exige sklearn 1.9.1,
   seed 42, cinco folds, hashes dos dados, os mesmos vencedores e os mesmos
   hiperparâmetros: SVM calibrada/caracteres, C=1 no escopo e C=0.1 no tema.
4. Exige Pipeline, configuração completa equivalente ao candidato original,
   classes e ordem corretas, probabilidades válidas e previsões idênticas aos
   modelos oficiais nas sondas. Usa somente os 550 textos de treino para escopo,
   os 300 de domínio para tema e duas entradas fictícias; não abre o teste
   como CSV. A normalização continua a do pipeline original.
5. Probabilidades devem coincidir com tolerância absoluta 1e-10, relativa zero;
   somas das linhas têm tolerância absoluta 1e-12. São limites para arredondamento
   numérico no ambiente compatível, não autorização para outro classificador.
   Configuração/classes/previsões precisam coincidir sem tolerância.
6. Somente após essas validações A1 recebe os novos hashes registrados pelos
   metadados da exportação. referencias() continua verificando bytes durante
   a execução; sem argumento adicional continua exigindo os hashes oficiais.
   Não existe fallback que aceite automaticamente qualquer modelo em disco.
7. O notebook compara as métricas médias/desvios e parâmetros dos 12 candidatos
   08 e todas as colunas de a1_comparacao.csv com as tabelas originais carregadas
   antes da gravação. Usa tolerância numérica absoluta 1e-10 e relativa zero;
   exige o limiar 0,60. Tempos de execução são medidos, mas não exigidos iguais.
   Uma divergência interrompe a reprodução; não é corrigida alterando resultados.

Nenhum protocolo, grade, algoritmo, dado, custo ou decisão científica foi
alterado. chatbot/experimentos.py não precisou ser modificado. A assinatura
oficial do grafo e os classificadores implantados permanecem preservados.

O notebook mantém 42 células, sendo 22 de código, na mesma ordem. As saídas e
contadores das sete células de código modificadas (2, 3, 5, 23, 32, 33 e 41)
foram limpos para não atribuir resultados históricos ao novo código.
As saídas restantes eram históricas naquela etapa. Após a execução manual,
todas as 22 células têm saídas reais regeneradas, incorporadas no encerramento.

## Ambiente observado e resultados de referência

| Componente | Versão instalada |
|---|---|
| Python | 3.12.13 |
| scikit-learn | 1.9.1 |
| NumPy / pandas | 2.5.5 / 3.1.1 |
| SciPy / joblib | 1.18.1 / 1.6.0 |
| matplotlib | 3.11.2 |
| nbconvert / nbclient / ipykernel | 7.17.2 / 0.11.0 / 7.4.0 |

requirements.txt fixa somente scikit-learn==1.9.1 para compatibilidade com os
pipelines publicados. Nenhuma biblioteca foi instalada ou atualizada.
Outras plataformas/versões numéricas podem exigir investigação; não se promete
igualdade universal de resultados nem se relaxam as verificações automaticamente.

| Experimento | F1 macro publicado | Acurácia publicada | Reprodução 11B |
|---|---:|---:|---|
| Escopo 08, SVM/caracteres | 0,922867 | 0,930909 | Idêntica; diferença 0,0 |
| Tema 08, SVM/caracteres | 0,919959 | 0,920000 | Idêntica; diferença 0,0 |
| A1 cascata com CV interna | 0,882105 | 0,889091 | Idêntica; diferença 0,0 |
| A1 único com CV interna | 0,885115 | 0,890909 | Idêntica; diferença 0,0 |

Essas métricas publicadas de treino/CV foram reproduzidas sem diferença; não são
teste independente nem melhoria de desempenho. Limiar 0,60 também reproduzido.
Os riscos de viés de seleção e famílias sintéticas atravessarem folds permanecem.

## Procedimento manual de reprodução isolada — etapa final

O roteiro anterior já aplicava as mudanças não commitadas: depois do archive,
copiava explicitamente o módulo, notebook, requirements.txt e teste corrigidos.
Não era necessário commitar para utilizá-los. Os 77 arquivos versionados da
lista de archive incluem os modelos, metadados, dados e resultados de referência.
Somente modelos/.gitkeep aparece como nome oculto; os materiais privados não
fazem parte da seleção.

A revisão desta etapa mantém esse procedimento e acrescenta preservação explícita
dos outputs históricos, notebook parcial em caso de exceção e aprovação final
condicionada à integridade principal. Nenhum código experimental foi alterado.

### Auditoria dos outputs

Índices abaixo começam em zero, no JSON, e não são números de execução do kernel.

| Célula | Outputs históricos removidos | Conteúdo a regenerar |
|---|---:|---|
| 2 | 1 | Ambiente Python e integridade dos dados |
| 3 | 1 | Versões, seed e folds |
| 5 | 2 | Identificação e tabela de intenções |
| 23 | 5 | Contratos de serialização, versões e três gráficos 08 |
| 32 | 1 | Execução A1, arquitetura e limiar |
| 33 | 5 | Tabelas e gráfico comparativo A1 |
| 41 | 1 | Integridade e limiar final |

Inicialmente foram removidos 16 blocos de saída nessas sete células. O volume de
milhares de linhas decorre principalmente de SVGs e tabelas HTML. As saídas das
outras 15 células foram preservadas como história na preparação. Na execução
manual posterior, todas as 22 células geraram saídas reais em um novo kernel.

Os outputs antigos devem ser conservados como história no commit de referência,
no base.tar e no notebook_historico_HEAD.ipynb da pasta de evidências. A versão
corrigida antes da execução também será preservada separadamente. Não recolocar
outputs antigos nas sete células modificadas como se pertencessem ao novo código.
O roteiro limpa todos os outputs somente na cópia antes de iniciar o novo kernel,
para impedir mistura de saídas antigas com uma execução parcial.

### Riscos e condições

Executar o bloco único no terminal do macOS, sem credenciais no ambiente de teste.
Ele usa o Python existente 3.12.13/sklearn 1.9.1, sem instalar bibliotecas;
divergência interrompe o procedimento. As correções locais devem continuar nos
seis caminhos identificados no início desta missão; mudanças adicionais exigem
nova conferência. O caminho do projeto é o confirmado neste checkout.

Serão ajustados e exportados modelos e resultados somente na cópia descartável;
não há promoção automática desses artefatos. A cópia separa gravações, mas não
constitui uma barreira de permissões do sistema operacional. O kernel recebe
somente um ambiente explícito de execução, sem herdar variáveis de credenciais.
Não há execução de avaliação/verificador oficial nem chamadas ao OpenRouter.

A pasta criada em /tmp é temporária. Preservá-la para revisão e fazer backup
manual em local aprovado antes de reiniciar o computador; não publicá-la inteira
no Git. Contém uma cópia do teste congelado, consultado exclusivamente por hash.

~~~sh
'/Users/ton/6semestre/IA/trabalho /rangot-codex/.venv/bin/python' -I -B - <<'RANGOT_11B'
import hashlib, json, os, platform, shutil, subprocess, sys, tempfile, traceback
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

repo = Path("/Users/ton/6semestre/IA/trabalho /rangot-codex")
ref = "d50e005d8026859c3346d14217da37f1c66f4ae9"
def git(*args):
    return subprocess.check_output(["git", "-C", str(repo), *args])
def sha(p):
    assert not p.is_symlink(), f"Link simbólico recusado: {p.name}"
    return hashlib.sha256(p.read_bytes()).hexdigest()
def gravar(p, valor):
    p.write_text(json.dumps(valor, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

assert git("branch", "--show-current").decode().strip() == "feature/rag-openrouter-rangot"
assert git("rev-parse", "HEAD").decode().strip() == ref
locais = ["chatbot/aprofundamento.py", "notebooks/01_trabalho_grupo.ipynb",
          "requirements.txt", "tests/test_reprodutibilidade.py",
          "docs/REPRODUTIBILIDADE_11B.md", "USO_DE_IA.md"]
estado = git("status", "--porcelain", "--untracked-files=all").decode()
assert {l[3:] for l in estado.splitlines()} == set(locais), estado
assert platform.python_version() == "3.12.13"
assert version("scikit-learn") == "1.9.1"
for nome in locais:
    assert (repo / nome).is_file() and not (repo / nome).is_symlink(), nome

raizes = ["chatbot", "scripts", "tests", "documentos", "notebooks/01_trabalho_grupo.ipynb",
          "dados/treino.csv", "dados/teste.csv", "modelos", "grupo.yaml", "requirements.txt",
          "resultados/classificadores_08", "resultados/aprofundamento_09"]
arvore = git("ls-tree", "-r", ref, "--", *raizes).decode().splitlines()
assert len(arvore) == 77
for linha in arvore:
    atributo, nome = linha.split("\t", 1)
    assert atributo.split()[0] in ("100644", "100755"), nome
    assert all(not parte.startswith(".") or parte == ".gitkeep" for parte in Path(nome).parts), nome
protegidos = ["dados/treino.csv", "dados/teste.csv", "modelos/escopo.joblib",
              "modelos/tema.joblib", "modelos/versoes.json", "scripts/avaliar.py",
              "scripts/verificar_entrega.py", "chatbot/avaliacao.py", "chatbot/grafo.py",
              "grupo.yaml", "resultados/rag_10_offline.json",
              "resultados/classificadores_08", "resultados/aprofundamento_09"]
nomes = git("ls-tree", "-r", "--name-only", ref, "--", *protegidos).decode().splitlines()
assert len(nomes) == 39
antes = {n: sha(repo / n) for n in nomes}
assert all(h == hashlib.sha256(git("show", f"{ref}:{n}")).hexdigest() for n, h in antes.items())

repro = Path(tempfile.mkdtemp(prefix="rangot-repro-11b-", dir="/tmp")).resolve()
assert not repro.is_relative_to(repo.resolve())
evid = repro / "evidencias"
evid.mkdir()
gravar(evid / "integridade_antes.json", antes)
gravar(evid / "entradas_locais.json", {n: sha(repo / n) for n in locais})
(evid / "git_status_antes.txt").write_text(estado, encoding="utf-8")
print("Diretório preservado:", repro, flush=True)
nb = None
aprovacao = {"aprovada": False, "celulas_validadas": 0}
with (evid / "execucao.log").open("w", encoding="utf-8") as log:
    try:
        subprocess.run(["git", "-C", str(repo), "archive", "--format=tar",
                        "--output=" + str(repro / "base.tar"), ref, "--", *raizes], check=True)
        subprocess.run(["/usr/bin/tar", "-xf", str(repro / "base.tar"), "-C", str(repro)], check=True)
        for nome in locais[:4]:
            shutil.copy2(repo / nome, repro / nome)
            assert sha(repo / nome) == sha(repro / nome)
        for nome in locais[4:]:
            shutil.copy2(repo / nome, evid / Path(nome).name)
        (evid / "notebook_historico_HEAD.ipynb").write_bytes(git("show", ref + ":notebooks/01_trabalho_grupo.ipynb"))
        shutil.copy2(repro / locais[1], evid / "notebook_corrigido_antes.ipynb")
        shutil.copy2(repro / "resultados/classificadores_08/comparacao_cv.csv", evid / "referencia_08.csv")
        shutil.copy2(repro / "resultados/aprofundamento_09/a1_comparacao.csv", evid / "referencia_09.csv")
        ambiente = {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "PYTHONDONTWRITEBYTECODE": "1"}
        for chave, pasta in {
            "JUPYTER_CONFIG_DIR": ".jupyter", "JUPYTER_RUNTIME_DIR": ".runtime",
            "JUPYTER_DATA_DIR": ".jupyter_data", "IPYTHONDIR": ".ipython",
            "MPLCONFIGDIR": ".cache/matplotlib", "XDG_CACHE_HOME": ".cache",
            "JUPYTER_PATH": ".kernel/share/jupyter",
        }.items():
            (repro / pasta).mkdir(parents=True, exist_ok=True)
            ambiente[chave] = str(repro / pasta)
        os.environ.update(ambiente)  # Somente diretórios públicos de execução; não lê segredos.
        os.chdir(repro)
        pacotes = ["scikit-learn", "numpy", "pandas", "scipy", "joblib", "matplotlib",
                   "nbclient", "nbformat", "ipykernel"]
        gravar(evid / "versoes.json", {"python": platform.python_version(),
                                     "pacotes": {n: version(n) for n in pacotes}})
        with (evid / "kernel.log").open("w") as saida:
            subprocess.run([sys.executable, "-B", "-m", "ipykernel", "install",
                            "--prefix", str(repro / ".kernel"), "--name", "rangot-repro-11b"],
                           env=ambiente, stdout=saida, stderr=subprocess.STDOUT, check=True)
        with (evid / "testes.log").open("w") as saida:
            subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests"],
                           cwd=repro, env=ambiente, stdout=saida, stderr=subprocess.STDOUT, check=True)
        import nbformat
        import pandas as pd
        import yaml
        from nbclient import NotebookClient
        cfg = yaml.safe_load((repro / "grupo.yaml").read_text(encoding="utf-8"))
        intencoes = {"cardapio", "horarios", "valores", "recarga_creditos", "cadastro", "regras_uso"}
        assert set(cfg["intencoes"]) == intencoes and cfg["roteamento"]["limiar_tema"] == 0.60
        for caminho in [*cfg["dados"].values(), *cfg["modelos"].values()]:
            assert (repro / caminho).resolve().is_relative_to(repro)
        nb = nbformat.read(repro / locais[1], as_version=4)
        fontes = [(c.cell_type, c.source) for c in nb.cells]
        for c in nb.cells:
            if c.cell_type == "code":
                c.outputs, c.execution_count = [], None
                c.metadata.pop("execution", None)
        print("Executando testes e notebook; aguarde. Log:", evid / "execucao.log", flush=True)
        NotebookClient(nb, timeout=1800, kernel_name="rangot-repro-11b",
                       resources={"metadata": {"path": str(repro)}}).execute(env=ambiente)
        codigos = [c for c in nb.cells if c.cell_type == "code"]
        assert len(codigos) == 22
        assert [c.execution_count for c in codigos] == list(range(1, 23))
        assert not any(o.output_type == "error" for c in codigos for o in c.outputs)
        assert fontes == [(c.cell_type, c.source) for c in nb.cells]
        comparacoes = {}
        for etapa, gerado, referencia, chaves, colunas in [
            ("08", "resultados/classificadores_08/comparacao_cv.csv", "referencia_08.csv",
             ["etapa", "algoritmo", "representacao"],
             ["f1_macro_media", "f1_macro_desvio", "accuracy_media", "accuracy_desvio", "parametros"]),
            ("09", "resultados/aprofundamento_09/a1_comparacao.csv", "referencia_09.csv", ["arquitetura"], None),
        ]:
            atual = pd.read_csv(repro / gerado).set_index(chaves).sort_index()
            antigo = pd.read_csv(evid / referencia).set_index(chaves).sort_index()
            if colunas is not None:
                atual, antigo = atual[colunas], antigo[colunas]
            pd.testing.assert_frame_equal(atual, antigo, check_dtype=False,
                                          check_exact=False, atol=1e-10, rtol=0)
            numericas = atual.select_dtypes(include="number").columns
            comparacoes[etapa] = {"linhas": len(atual), "diferenca_absoluta_maxima":
                                  float((atual[numericas] - antigo[numericas]).abs().max().max())}
        meta09 = json.loads((repro / "resultados/aprofundamento_09/metadados.json").read_text())
        assert meta09["limiar_tema"] == 0.60
        gravar(evid / "comparacoes.json", comparacoes)
        aprovacao.update(celulas_validadas=22, comparacoes= comparacoes, limiar_tema=0.60,
                         intencoes=sorted(intencoes),
                         hashes_modelos_reproduzidos={n: sha(repro / n) for n in
                             ("modelos/escopo.joblib", "modelos/tema.joblib")})
        nb.metadata["reproducao_manual_11b"] = {
            "utc": datetime.now(timezone.utc).isoformat(), "celulas_validadas": 22,
            "metodo": "NotebookClient; kernel Jupyter novo; execução manual externa ao Codex",
            "referencia": ref, "comparacoes": comparacoes,
        }
        aprovacao["aprovada"] = True
    except BaseException as erro:
        aprovacao["erro"] = f"{type(erro).__name__}: {erro}"
        traceback.print_exc(file=log)
    finally:
        if nb is not None:
            nbformat.write(nb, repro / "notebooks/01_trabalho_grupo_reproduzido.ipynb")
        depois = {n: sha(repo / n) for n in nomes}
        gravar(evid / "integridade_depois.json", depois)
        alterados = [n for n in nomes if antes[n] != depois[n]]
        aprovacao["integridade_principal"] = not alterados
        aprovacao["arquivos_protegidos_alterados"] = alterados
        aprovacao["aprovada"] = aprovacao["aprovada"] and not alterados
        gravar(evid / "APROVACAO.json", aprovacao)
print(json.dumps(aprovacao, ensure_ascii=False, indent=2))
print("Evidências e notebook preservados em:", repro)
print("Nenhum artefato foi copiado de volta ao projeto principal.")
raise SystemExit(0 if aprovacao["aprovada"] else 1)
RANGOT_11B
~~~

### Sucesso, falha e entrega do notebook executado

Sucesso exige saída final com aprovada=true em evidencias/APROVACAO.json e código
de saída zero. O roteiro exige 22 contadores consecutivos, nenhuma saída de erro,
fontes das células preservadas, métricas 08/09 compatíveis, limiar 0,60 e seis
intenções. A comparação usa atol=1e-10 e rtol=0; tempos de execução não são
critérios de igualdade. As verificações funcionais estritas dos pipelines já
implementadas permanecem ativas no notebook.

Consultar evidencias/comparacoes.json, execucao.log, testes.log, versoes.json,
entradas_locais.json e os dois manifestos de integridade. Os hashes dos 39
arquivos oficiais devem coincidir antes/depois. A aprovação técnica não é
declaração de revisão humana.

Falha produz aprovada=false e código de saída diferente de zero. O traceback
fica em execucao.log; falhas anteriores ao kernel podem estar em kernel.log ou
testes.log. Se o notebook chegou a ser carregado, o finally salva
notebooks/01_trabalho_grupo_reproduzido.ipynb com as saídas reais disponíveis,
inclusive execução parcial. Sem APROVACAO.json válido com aprovada=true,
não considerar a reprodução aprovada. Não afrouxar tolerâncias para ocultar
divergências, nem substituir resultados publicados.

Após o responsável conferir o resultado, a importação deve copiar **somente**
notebooks/01_trabalho_grupo_reproduzido.ipynb da cópia para
notebooks/01_trabalho_grupo.ipynb do projeto principal. Antes disso, preservar
o notebook principal atual na pasta de evidências e confirmar que seus fontes
ainda correspondem à versão corrigida usada na execução. Conferir o diff e os
hashes oficiais novamente após essa única cópia. Não copiar dados/, modelos/,
resultados/ ou a cópia inteira para o checkout.

O notebook executado ganha metadados de reprodução manual, mantendo os registros
históricos de 08/09 e da edição Codex. O registro anterior de ausência de execução
pelo Codex continua verdadeiro; não atribuir ao Codex uma execução feita pelo
responsável. No encerramento, as evidências retornadas foram lidas e os registros
atualizados, sem presumir revisão humana de código ou de outros artefatos.

Na preparação, o Codex validou apenas sintaxe Python/AST e shell do bloco, sem
executá-lo. Posteriormente, Cleiton realizou a execução manual; neste encerramento
o Codex conferiu as evidências reais e incorporou somente o notebook executado.

## Testes e integridade

Comando executado no checkout:
~~~sh
.venv/bin/python -B -m unittest discover -s tests
~~~
Resultado: **160 testes aprovados**, incluindo os 149 existentes e 11 novos.
Os novos testes ajustam apenas pequenos modelos com fixtures fictícias em memória;
não reproduzem o treinamento científico. Cobrem reserialização válida, rejeição
de modelo/configuração/classes/probabilidades incorretas, protocolo/dados
divergentes, snapshot incompleto, mudança posterior de bytes e a integração
estática das células. Complementam a execução integral comprovada pelas
evidências reais, sem a substituir.

Os 39 arquivos protegidos fotografados no início foram conferidos ao final.
SHA-256 antes = depois:

| Arquivo | SHA-256 preservado |
|---|---|
| dados/treino.csv | fc260493bf144e3a6b5ecac2e2e7064f31b53dda597948cfc8e689fea5b665f5 |
| dados/teste.csv | fa760e167d565a9a3e5bd015465c4ec945f7855e0bd78b5542dc561e21ea9b81 |
| modelos/escopo.joblib | cd33ffcb0cbdc2727e2fb7bdb3d12d2098d9d4961e5be028152832ff8134b12e |
| modelos/tema.joblib | a674cbc37d89aba7130d65361584b08411840eecb8224d003ac15d83580da8ce |
| modelos/versoes.json | 911d4fe6380721a7c1779e1dcaa0a6fe6e2bd2fcc38bded00bdd6b6f944a968f |
| scripts/avaliar.py | 5ee29c8f0b7aacc146706948dd26803600ad9da8b683a3d22a1a9ab64f0ddda2 |
| scripts/verificar_entrega.py | 42bda3906b0f295603162d4d2320191327cc4f472b59ac3fd2bf874fc1feacec |
| chatbot/avaliacao.py | 4c40ed6d4ee3cdabf54a4b387b8085faea6a76ec93f8b7a104a29d04facb6035 |

grupo.yaml, chatbot/grafo.py, os 28 arquivos publicados 08/09 e o resultado
histórico RAG também permanecem intactos. Seis intenções, limiar 0,60,
interfaces do grafo e modelos não foram alterados. O teste foi usado somente
para hash; nenhum exemplo foi consultado. Não houve avaliação oficial,
verificador oficial, OpenRouter, acesso a credenciais ou commit.
git diff --check limpo; os dois novos arquivos também passaram pela checagem de
espaçamento com git diff --no-index --check. JSON/schema do notebook e sintaxe
das 22 células foram validados sem reexecutar o notebook no checkout principal.

## Commits sugeridos, não executados

Executar somente após revisar o diff e as evidências; não inclui push:
~~~sh
git add chatbot/aprofundamento.py tests/test_reprodutibilidade.py requirements.txt
git diff --cached --name-only
git diff --cached --check
git commit -m "fix(reproducao): validar modelos reserializados antes do A1"

git add notebooks/01_trabalho_grupo.ipynb
git diff --cached --name-only
git diff --cached --check
git commit -m "fix(notebook): incorporar reproducao integral validada"

git add docs/REPRODUTIBILIDADE_11B.md USO_DE_IA.md
git diff --cached --name-only
git diff --cached --check
git commit -m "docs(reproducao): registrar execucao integral aprovada"
~~~

Os critérios de encerramento da Missão 11B foram atendidos: 22 células executadas,
métricas idênticas, limiar reproduzido e integridade principal preservada.
Permanecem a revisão do diff e a realização dos commits pelo responsável;
publicação, integração e avaliação oficial não foram executadas nesta missão.
Não há revisão humana presumida do código ou da documentação assistida por IA.
