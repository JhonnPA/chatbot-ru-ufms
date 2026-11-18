"""Experimentos 08: somente treino/CV; teste acessado exclusivamente por hash.

Os estimadores persistidos usam apenas classes sklearn e normalização importável.
Não há LLM, busca de limiar, A1 ou avaliação oficial neste módulo.
"""
from __future__ import annotations

import hashlib
import json
import platform
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from threadpoolctl import threadpool_limits

from .config import carregar_config
from .dados import adicionar_escopo, carregar_dados, validar_dados
from .modelos import carregar_classificadores, checar_interface, salvar_classificadores
from .representacoes import tfidf_caracteres, tfidf_palavras
from .rotulos import CLASSES_ESCOPO, DOMINIO
from .texto import normalizar

SEED = 42
FOLDS = 5
HASHES_DADOS = {
    "dados/treino.csv": "fc260493bf144e3a6b5ecac2e2e7064f31b53dda597948cfc8e689fea5b665f5",
    "dados/teste.csv": "fa760e167d565a9a3e5bd015465c4ec945f7855e0bd78b5542dc561e21ea9b81",
}
PROTEGIDOS = ("scripts/avaliar.py", "scripts/verificar_entrega.py", "chatbot/avaliacao.py", "grupo.yaml")
ALGORITMOS = ("logistica", "complement_nb", "svm_calibrada")
REPRESENTACOES = ("palavras", "caracteres")
LIMITACOES = (
    "CV interna usada para escolher algoritmos/representacoes/hiperparametros. "
    "Medias da busca e OOF do vencedor possuem vies de selecao: nao sao estimativa independente ou teste final. "
    "Nao foi realizada CV aninhada. Familias de parafrases e autores podem atravessar folds estratificadas; "
    "nao houve agrupamento por familia/autoria, o que pode elevar os resultados. "
    "Comparacoes por origem sao descritivas, sem controle causal de classe, estilo ou dificuldade. "
    "As probabilidades OOF nao definem limiar nesta missao; A1 e limiar ficam para a Missao 09."
)


def sha256(caminho):
    """Hash de um arquivo permitido, sem interpretar seu conteúdo."""
    p = Path(caminho)
    if p.is_symlink():
        raise ValueError("Arquivo simbólico não permitido")
    return hashlib.sha256(p.read_bytes()).hexdigest()


def conferir_integridade(raiz, anterior=None):
    raiz = Path(raiz)
    hashes = {n: sha256(raiz / n) for n in (*HASHES_DADOS, *PROTEGIDOS)}
    for nome, esperado in HASHES_DADOS.items():
        if hashes[nome] != esperado:
            raise ValueError(f"Hash contratual divergente: {nome}")
    if anterior is not None and hashes != anterior:
        raise ValueError("Dados, configuração ou arquivos oficiais foram alterados durante a execução")
    return hashes


def preparar(raiz):
    """Lê apenas o treino; não chama carregar_dados para o teste."""
    raiz = Path(raiz)
    hashes = conferir_integridade(raiz)
    config = carregar_config(raiz / "grupo.yaml")
    dados = adicionar_escopo(carregar_dados(config.treino), config)
    problemas = validar_dados(dados, config)
    if problemas:
        raise ValueError("Treino inválido: " + "; ".join(problemas))
    if dados["texto"].map(normalizar).duplicated().any():
        raise ValueError("Duplicata normalizada no treino")
    minimos = dict.fromkeys(config.nomes_intencoes, 50) | {"chitchat": 100, "fora_dominio": 150}
    contagens = dados["intencao"].value_counts()
    if len(dados) != 550 or any(contagens.get(c, 0) < n for c, n in minimos.items()):
        raise ValueError("Mínimos ou total do treinamento divergentes")
    if dados["origem"].isin(["humano", "coletado"]).mean() < .2:
        raise ValueError("Proporção humana insuficiente")
    dados["linha_treino"] = np.arange(len(dados)) + 2  # registros lógicos; não linhas físicas
    return config, dados, hashes


def conjuntos_estagios(dados):
    return {"escopo": dados.copy(), "tema": dados.loc[dados["escopo"] == DOMINIO].copy()}


def particoes(rotulos):
    cv = StratifiedKFold(n_splits=FOLDS, shuffle=True, random_state=SEED)
    return list(cv.split(np.zeros(len(rotulos)), rotulos))


def candidato(algoritmo, representacao):
    if representacao not in REPRESENTACOES or algoritmo not in ALGORITMOS:
        raise ValueError("Candidato desconhecido")
    vetor = tfidf_palavras() if representacao == "palavras" else tfidf_caracteres()
    if algoritmo == "svm_calibrada":
        base = Pipeline([
            ("vetorizador", vetor),
            ("classificador", LinearSVC(C=1, class_weight="balanced", dual=True,
                                        max_iter=10000, random_state=SEED)),
        ])
        # O calibrador envolve TODO o pipeline. Cada divisão interna reaprende
        # vocabulário/IDF; a validação externa nunca participa da calibração.
        calibrador = CalibratedClassifierCV(
            estimator=base, method="sigmoid", ensemble=False,
            cv=StratifiedKFold(3, shuffle=True, random_state=SEED), n_jobs=1,
        )
        return Pipeline([("calibrado", calibrador)]), {"calibrado__estimator__classificador__C": [.1, 1., 10.]}
    if algoritmo == "logistica":
        clf = LogisticRegression(C=1, class_weight="balanced", solver="lbfgs",
                                 max_iter=4000, random_state=SEED)
        grade = {"classificador__C": [.1, 1., 10.]}
    else:
        clf = ComplementNB(alpha=1)
        grade = {"classificador__alpha": [.1, .5, 1.]}
    return Pipeline([("vetorizador", vetor), ("classificador", clf)]), grade


def _indice_melhor(resultados):
    # Desempate previamente definido, sem inspeção de erros nem acesso ao teste.
    return min(range(len(resultados["params"])), key=lambda i: (
        -resultados["mean_test_f1_macro"][i], -resultados["mean_test_accuracy"][i],
        resultados["std_test_f1_macro"][i], i,
    ))


def previsoes_oof(estimator, dados, alvo, classes, folds):
    """Parâmetros já selecionados: diagnóstico OOF com viés de seleção declarado."""
    predicoes, metricas_folds = [], []
    for numero, (tr, va) in enumerate(folds, 1):
        modelo = clone(estimator)
        modelo.fit(dados["texto"].iloc[tr].tolist(), dados[alvo].iloc[tr].tolist())
        textos = dados["texto"].iloc[va].tolist()
        pred = modelo.predict(textos)
        prob = modelo.predict_proba(textos)
        ordem = [list(modelo.classes_).index(c) for c in classes]
        prob = prob[:, ordem]
        real = dados[alvo].iloc[va].to_numpy()
        metricas_folds.append({"fold": numero, "n_validacao": len(va),
            "f1_macro": float(f1_score(real, pred, labels=classes, average="macro", zero_division=0)),
            "accuracy": float(accuracy_score(real, pred))})
        for pos, previsto, probabilidades in zip(va, pred, prob):
            r = dados.iloc[pos]
            predicoes.append({"linha_treino": int(r["linha_treino"]), "fold": numero,
                "real": str(r[alvo]), "predito": str(previsto), "origem": r["origem"],
                "confianca": float(np.max(probabilidades)),
                "probabilidades": json.dumps(dict(zip(classes, map(float, probabilidades))), sort_keys=True)})
    return pd.DataFrame(predicoes).sort_values("linha_treino").reset_index(drop=True), pd.DataFrame(metricas_folds)


def experimentar_estagio(etapa, dados, classes):
    if etapa not in ("escopo", "tema"):
        raise ValueError("Estágio desconhecido")
    alvo = "escopo" if etapa == "escopo" else "intencao"
    dados = dados.reset_index(drop=True)
    if etapa == "tema" and not dados["escopo"].eq(DOMINIO).all():
        raise ValueError("Tema aceita somente rótulos originais de domínio")
    folds = particoes(dados[alvo])
    comparacao, linhas_grade, escolhidos = [], [], {}
    with threadpool_limits(limits=1):
        for algoritmo in ALGORITMOS:
            for representacao in REPRESENTACOES:
                pipe, grade = candidato(algoritmo, representacao)
                inicio = perf_counter()
                busca = GridSearchCV(pipe, grade, cv=folds,
                    scoring={"f1_macro": "f1_macro", "accuracy": "accuracy"},
                    refit=False, n_jobs=1, return_train_score=True, error_score="raise")
                busca.fit(dados["texto"].tolist(), dados[alvo].tolist())
                r = busca.cv_results_
                melhor = _indice_melhor(r)
                identificador = f"{algoritmo}/{representacao}"
                escolhidos[identificador] = (pipe, r["params"][melhor])
                comparacao.append({"etapa": etapa, "algoritmo": algoritmo, "representacao": representacao,
                    "f1_macro_media": float(r["mean_test_f1_macro"][melhor]),
                    "f1_macro_desvio": float(r["std_test_f1_macro"][melhor]),
                    "accuracy_media": float(r["mean_test_accuracy"][melhor]),
                    "accuracy_desvio": float(r["std_test_accuracy"][melhor]),
                    "parametros": json.dumps(r["params"][melhor], sort_keys=True),
                    "segundos_busca": perf_counter() - inicio})
                for i, parametros in enumerate(r["params"]):
                    linha = {"etapa": etapa, "algoritmo": algoritmo, "representacao": representacao,
                             "parametros": json.dumps(parametros, sort_keys=True)}
                    for metrica in ("f1_macro", "accuracy"):
                        for tipo in ("train", "test"):
                            for estatistica in ("mean", "std"):
                                k = f"{estatistica}_{tipo}_{metrica}"
                                linha[k] = float(r[k][i])
                        for fold in range(FOLDS):
                            k = f"split{fold}_test_{metrica}"
                            linha[k] = float(r[k][i])
                    linha["mean_fit_time"] = float(r["mean_fit_time"][i])
                    linhas_grade.append(linha)
        tabela = pd.DataFrame(comparacao).sort_values(
            ["f1_macro_media", "accuracy_media", "f1_macro_desvio", "algoritmo", "representacao"],
            ascending=[False, False, True, True, True], kind="stable").reset_index(drop=True)
        vencedor = tabela.iloc[0].to_dict()
        pipe, parametros = escolhidos[f"{vencedor['algoritmo']}/{vencedor['representacao']}"]
        selecionado = clone(pipe).set_params(**parametros)
        oof, metricas_folds = previsoes_oof(selecionado, dados, alvo, classes, folds)
        if not np.isclose(metricas_folds["f1_macro"].mean(), vencedor["f1_macro_media"], atol=1e-10):
            raise RuntimeError("OOF não reproduziu a configuração da busca")
        modelo_final = clone(selecionado).fit(dados["texto"].tolist(), dados[alvo].tolist())
    oof.insert(0, "etapa", etapa)
    metricas_folds.insert(0, "etapa", etapa)
    cm = confusion_matrix(oof["real"], oof["predito"], labels=classes)
    matriz = pd.DataFrame([{"etapa": etapa, "real": real, "predito": predito, "quantidade": int(cm[i, j])}
        for i, real in enumerate(classes) for j, predito in enumerate(classes)])
    origem = []
    for nome, sub in oof.groupby("origem", sort=True):
        origem.append({"etapa": etapa, "origem": nome, "n": len(sub),
            "f1_macro": float(f1_score(sub["real"], sub["predito"], labels=classes, average="macro", zero_division=0)),
            "accuracy": float(accuracy_score(sub["real"], sub["predito"]))})
    precision, recall, f1, support = precision_recall_fscore_support(
        oof["real"], oof["predito"], labels=classes, zero_division=0)
    por_classe = pd.DataFrame({"etapa": etapa, "classe": classes, "precision": precision,
                              "recall": recall, "f1": f1, "suporte": support})
    grade_df = pd.DataFrame(linhas_grade)
    curvas = grade_df.loc[(grade_df["algoritmo"] == vencedor["algoritmo"]) &
                          (grade_df["representacao"] == vencedor["representacao"])].copy()
    extras = {"f1_macro_oof_agrupado": float(f1_score(oof["real"], oof["predito"], labels=classes,
                                                       average="macro", zero_division=0)),
              "accuracy_oof_agrupada": float(accuracy_score(oof["real"], oof["predito"])),
              "n": len(dados), "erros": int(oof["real"].ne(oof["predito"]).sum())}
    if etapa == "escopo":
        fora = oof["real"].ne(DOMINIO)
        dentro = ~fora
        extras.update({"falsos_aceites": int((fora & oof["predito"].eq(DOMINIO)).sum()),
            "falsas_recusas": int((dentro & oof["predito"].ne(DOMINIO)).sum()),
            "n_nao_dominio": int(fora.sum()), "n_dominio": int(dentro.sum())})
        extras["taxa_falso_aceite"] = extras["falsos_aceites"] / extras["n_nao_dominio"]
        extras["taxa_falsa_recusa"] = extras["falsas_recusas"] / extras["n_dominio"]
    return {"modelo": modelo_final, "vencedor": vencedor, "comparacao": tabela, "grade": grade_df,
            "oof": oof, "folds": metricas_folds, "matriz": matriz, "origem": pd.DataFrame(origem),
            "classes": por_classe, "curvas": curvas, "extras": extras}


def validar_serializacao(config, escopo, tema):
    salvar_classificadores(escopo, tema, config)
    carregados = carregar_classificadores(config)
    ficticios = ["EXEMPLO FICTÍCIO esfera orbital 73", "EXEMPLO FICTÍCIO prisma violeta 91"]
    for nome, original, carregado, classes in zip(
        ("escopo", "tema"), (escopo, tema), carregados, (CLASSES_ESCOPO, config.nomes_intencoes)):
        checar_interface(carregado, classes, nome)
        if not isinstance(carregado, Pipeline) or not hasattr(carregado, "predict_proba"):
            raise TypeError("Modelo salvo deve ser Pipeline com probabilidades")
        np.testing.assert_array_equal(original.predict(ficticios), carregado.predict(ficticios))
        probabilidades = carregado.predict_proba(ficticios)
        np.testing.assert_allclose(probabilidades, original.predict_proba(ficticios), atol=1e-12)
        if probabilidades.shape != (2, len(classes)) or not np.isfinite(probabilidades).all():
            raise ValueError("Probabilidades inválidas")
        np.testing.assert_allclose(probabilidades.sum(axis=1), 1)
    return {"round_trip": True, "ficticios": 2,
            "sha256_escopo": sha256(config.modelo_escopo), "sha256_tema": sha256(config.modelo_tema)}


def salvar_figuras(resultados, pasta):
    # Cache do matplotlib deve ser configurado pelo entrypoint antes deste import.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay

    fig, axs = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)
    for ax, (etapa, r) in zip(axs, resultados.items()):
        tab = r["comparacao"]
        labels = tab["algoritmo"] + "/" + tab["representacao"]
        ax.barh(labels, tab["f1_macro_media"], xerr=tab["f1_macro_desvio"], color="#24608a", capsize=3)
        ax.set(xlim=(0, 1), title=etapa, xlabel="F1 macro CV interna (média ± desvio, 5 folds)")
        ax.invert_yaxis()
    fig.savefig(pasta / "comparacao_cv.svg")
    plt.close(fig)
    fig, axs = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    for ax, (etapa, r) in zip(axs, resultados.items()):
        classes = CLASSES_ESCOPO if etapa == "escopo" else r["classes"]["classe"].tolist()
        matrix = r["matriz"].pivot(index="real", columns="predito", values="quantidade").reindex(index=classes, columns=classes)
        ConfusionMatrixDisplay(matrix.to_numpy(), display_labels=classes).plot(
            ax=ax, colorbar=False, cmap="Blues", xticks_rotation=45)
        ax.set_title(etapa + " — OOF pós-seleção")
    fig.savefig(pasta / "matrizes_confusao.svg")
    plt.close(fig)
    fig, axs = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
    for ax, (etapa, r) in zip(axs, resultados.items()):
        tab = r["curvas"]
        params = [next(iter(json.loads(p).values())) for p in tab["parametros"]]
        for tipo, nome in (("train", "treino"), ("test", "validação")):
            ax.errorbar(params, tab[f"mean_{tipo}_f1_macro"], yerr=tab[f"std_{tipo}_f1_macro"],
                        marker="o", capsize=3, label=nome)
        parametro = next(iter(json.loads(tab.iloc[0]["parametros"]))).split("__")[-1]
        ax.set(xscale="log", ylim=(0, 1.03), xlabel=parametro,
               ylabel="F1 macro (média ± desvio)", title=etapa + " — " + r["vencedor"]["algoritmo"])
        ax.legend()
    fig.savefig(pasta / "curvas_validacao.svg")
    plt.close(fig)


def finalizar(raiz, config, dados, hashes, resultados):
    pasta = Path(raiz) / "resultados/classificadores_08"
    pasta.mkdir(parents=True, exist_ok=True)
    contratos = validar_serializacao(config, resultados["escopo"]["modelo"], resultados["tema"]["modelo"])
    nomes = {"comparacao": "comparacao_cv", "grade": "grid_search", "oof": "predicoes_oof_treino",
             "folds": "metricas_folds", "matriz": "matrizes_confusao", "origem": "metricas_origem",
             "classes": "metricas_classe", "curvas": "curvas_validacao"}
    for chave, nome in nomes.items():
        pd.concat([r[chave] for r in resultados.values()], ignore_index=True).to_csv(
            pasta / (nome + ".csv"), index=False, lineterminator="\n")
    salvar_figuras(resultados, pasta)
    meta = {"missao": "08", "seed": SEED, "folds": FOLDS, "jobs": 1,
        "algoritmos": list(ALGORITMOS), "representacoes": {"palavras": "word (1,2)", "caracteres": "char_wb (2,5)"},
        "calibracao_svm": "sigmoid; 3 folds internas; vetorizador dentro do estimador calibrado; ensemble=False",
        "normalizacao": "chatbot.texto.normalizar; min_df=1; sublinear_tf=True; sem remoção de stopwords",
        "metrica_principal": "f1_macro", "desvio": "populacional (ddof=0), cinco folds",
        "selecao": "F1 macro; desempate acurácia, menor desvio, ordem estável de nome/grade",
        "python": platform.python_version(),
        "versoes": {p: version(p) for p in ("numpy", "pandas", "scikit-learn", "scipy", "joblib", "matplotlib", "threadpoolctl")},
        "hashes_entrada": hashes, "contratos_modelos": contratos,
        "distribuicao_treino": dados.groupby(["intencao", "origem"]).size().unstack(fill_value=0).to_dict(),
        "total_treino": len(dados), "proporcao_humana": float(dados["origem"].isin(["humano", "coletado"]).mean()),
        "selecionados": {etapa: r["vencedor"] for etapa, r in resultados.items()},
        "diagnostico_oof_pos_selecao": {etapa: r["extras"] for etapa, r in resultados.items()},
        "limitacoes": LIMITACOES, "teste_usado": "somente SHA-256; nenhum CSV de teste carregado",
        "avaliacao_final_executada": False, "a1_executado": False, "limiar_selecionado": False}
    (pasta / "metadados.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    linhas = ["# Resultados científicos — Missão 08", "", "Resultados reais de treino/CV interna. " + LIMITACOES, ""]
    for etapa, r in resultados.items():
        v = r["vencedor"]
        linhas += [f"## {etapa}", "", f"Selecionado: {v['algoritmo']}/{v['representacao']}; parâmetros: {v['parametros']}.",
            f"F1 macro CV: {v['f1_macro_media']:.6f} ± {v['f1_macro_desvio']:.6f}; "
            f"acurácia: {v['accuracy_media']:.6f} ± {v['accuracy_desvio']:.6f}.",
            "A configuração foi escolhida pelo maior F1 macro, com desempates definidos antes da execução.",
            "", "Diagnóstico OOF: " + json.dumps(r["extras"], ensure_ascii=False), "",
            "Por origem (descrição, sem interpretação causal):", "", r["origem"].to_csv(index=False).strip(), "",
            "Confusões observadas (quantidades OOF):", ""]
        erros = r["matriz"].query("real != predito and quantidade > 0").sort_values("quantidade", ascending=False)
        linhas += [erros.to_csv(index=False).strip() if not erros.empty else "Nenhum erro OOF nessa execução.", ""]
    linhas += ["## Limites e próximos passos", "", "Inspecionar os erros de treinamento mostrados no notebook; "
        "não reinterpretar a CV como desempenho em pessoas/autorias independentes. A comparação humano/LLM mistura "
        "diferenças de classe, estilo e repetição. Falso aceite produz resposta fora de escopo e falsa recusa "
        "reduz cobertura. Não alterar dados ou modelos a partir do teste reservado. A Missão 09 fará A1, limiar "
        "e integração; avaliação oficial permanece não executada."]
    (pasta / "RESUMO_CIENTIFICO.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    conferir_integridade(raiz, hashes)
    estado = {"missao": "08", "estado": "concluida", "modelos_salvos_e_recarregados": True,
              "metricas_reais_geradas": True, "avaliacao_final_executada": False}
    (pasta / "ESTADO_EXECUCAO.json").write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return meta


def executar(raiz):
    config, dados, hashes = preparar(raiz)
    estagios = conjuntos_estagios(dados)
    resultados = {}
    for etapa, sub in estagios.items():
        print(f"Executando {etapa}: {len(sub)} exemplos; 3 algoritmos × 2 representações × 5 folds", flush=True)
        classes = CLASSES_ESCOPO if etapa == "escopo" else config.nomes_intencoes
        resultados[etapa] = experimentar_estagio(etapa, sub, classes)
        print(json.dumps(resultados[etapa]["vencedor"], ensure_ascii=False), flush=True)
    return finalizar(raiz, config, dados, hashes, resultados)
