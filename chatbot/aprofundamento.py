"""A1 e limiar: treino/CV, sem avaliação do teste ou persistência de modelos 08."""
from __future__ import annotations

import io
import json
from pathlib import Path
from time import perf_counter

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from threadpoolctl import threadpool_limits

from .experimentos import HASHES_DADOS, SEED, candidato, preparar, sha256
from .modelos import carregar_classificadores, checar_interface
from .rotulos import CHITCHAT, CLASSES_ESCOPO, DOMINIO, ESCLARECER, FORA_DOMINIO

LIMIARES = [0., .2, .25, .3, .35, .4, .45, .5, .55, .6, .65, .7, .75, .8, .85, .9, .95, 1.]
# Decisão operacional interna, declarada antes da execução; não é regra do professor.
CUSTOS = {"falso_aceite": 5, "tema_errado": 3, "esclarecimento": 1,
          "falsa_recusa": 2, "social_fora_trocados": 1}
MODELOS_08 = {"modelos/escopo.joblib": "cd33ffcb0cbdc2727e2fb7bdb3d12d2098d9d4961e5be028152832ff8134b12e",
              "modelos/tema.joblib": "a674cbc37d89aba7130d65361584b08411840eecb8224d003ac15d83580da8ce"}
CASOS_FICTICIOS = [
    ("cardapio", "Olá, qual prato vai compor a refeição de quarta-feira no RU?"),
    ("horarios", "A que horas o restaurante universitário começa e encerra o jantar?"),
    ("valores", "Sou estudante de graduação: qual preço cobram pela refeição?"),
    ("recarga_creditos", "Queria entender como pago a refeição do RU: dá para usar Pix?"),
    ("cadastro", "É minha primeira visita ao restaurante universitário; como libero meu acesso?"),
    ("regras_uso", "Posso almoçar no restaurante levando minha própria garrafa de água?"),
    (CHITCHAT, "Bom dia, assistente, obrigado pela atenção!"),
    (FORA_DOMINIO, "Como faço a renovação de empréstimo na biblioteca do campus?"),
    ("ambiguo_sem_rotulo_unico", "Como eu consigo usar isso?"),
    ("multiplas_intencoes", "Qual é o preço do jantar e o que vai ter para comer?"),
]


def referencias(raiz):
    raiz = Path(raiz)
    nomes = list(HASHES_DADOS) + list(MODELOS_08) + [
        "scripts/avaliar.py", "scripts/verificar_entrega.py", "chatbot/avaliacao.py", "modelos/versoes.json"]
    nomes += [str(p.relative_to(raiz)) for p in sorted((raiz / "resultados/classificadores_08").glob("*")) if p.is_file()]
    obtidos = {n: sha256(raiz / n) for n in nomes}
    for n, h in (HASHES_DADOS | MODELOS_08).items():
        if obtidos[n] != h:
            raise ValueError(f"Referência experimental divergente: {n}")
    return obtidos


def _melhor_indice(r):
    return min(range(len(r["params"])), key=lambda i: (
        -r["mean_test_f1_macro"][i], -r["mean_test_accuracy"][i], r["std_test_f1_macro"][i], i))


def _ajustar(textos, rotulos):
    pipe, grade = candidato("svm_calibrada", "caracteres")
    busca = GridSearchCV(pipe, grade, scoring={"f1_macro": "f1_macro", "accuracy": "accuracy"},
        refit=_melhor_indice, cv=StratifiedKFold(3, shuffle=True, random_state=SEED),
        n_jobs=1, error_score="raise")
    busca.fit(list(textos), list(rotulos))
    return busca.best_estimator_, busca.best_params_


def _tamanho(modelos):
    total, vocab = 0, 0
    for modelo in modelos:
        b = io.BytesIO()
        joblib.dump(modelo, b)
        total += b.tell()
        base = modelo.named_steps["calibrado"].calibrated_classifiers_[0].estimator
        vocab += len(base.named_steps["vetorizador"].vocabulary_)
    return total, vocab


def metricas_rotas(real, predito, intencoes):
    real, predito = np.asarray(real), np.asarray(predito)
    dominio = np.isin(real, intencoes)
    aceito = np.isin(predito, intencoes)
    classes = list(intencoes) + [CHITCHAT, FORA_DOMINIO]
    return {"f1_macro": float(f1_score(real, predito, labels=classes, average="macro", zero_division=0)),
        "accuracy": float(accuracy_score(real, predito)), "erros": int(np.sum(real != predito)),
        "falsos_aceites": int(np.sum(~dominio & aceito)), "falsas_recusas": int(np.sum(dominio & np.isin(predito, [CHITCHAT, FORA_DOMINIO]))),
        "taxa_falso_aceite": float(np.sum(~dominio & aceito) / max(1, np.sum(~dominio))),
        "taxa_falsa_recusa": float(np.sum(dominio & np.isin(predito, [CHITCHAT, FORA_DOMINIO])) / max(1, np.sum(dominio)))}


def comparar(raiz):
    """Cinco folds externas comuns, estratificadas nas oito classes originais."""
    config, dados, _ = preparar(raiz)
    refs = referencias(raiz)
    ref_escopo, ref_tema = carregar_classificadores(config)
    checar_interface(ref_escopo, CLASSES_ESCOPO, "escopo")
    checar_interface(ref_tema, config.nomes_intencoes, "tema")
    classes = config.nomes_intencoes + [CHITCHAT, FORA_DOMINIO]
    folds = StratifiedKFold(5, shuffle=True, random_state=SEED).split(dados["texto"], dados["intencao"])
    linhas, met_folds, ajustes, custos = [], [], [], []
    with threadpool_limits(limits=1):
        for numero, (tr, va) in enumerate(folds, 1):
            treino, validacao = dados.iloc[tr], dados.iloc[va]
            dom = treino["escopo"].eq(DOMINIO)
            x = validacao["texto"].tolist()
            inicio = perf_counter()
            escopo, pe = _ajustar(treino["texto"], treino["escopo"])
            tema, pt = _ajustar(treino.loc[dom, "texto"], treino.loc[dom, "intencao"])
            segundos_cascata = perf_counter() - inicio
            inicio = perf_counter()
            unico, pu = _ajustar(treino["texto"], treino["intencao"])
            segundos_unico = perf_counter() - inicio
            # A referência de produção fica fixa em C=1 (escopo), C=.1 (tema).
            inicio = perf_counter()
            re = escopo if pe == {"calibrado__estimator__classificador__C": 1.} else clone(ref_escopo).fit(treino["texto"].tolist(), treino["escopo"].tolist())
            rt = tema if pt == {"calibrado__estimator__classificador__C": .1} else clone(ref_tema).fit(treino.loc[dom, "texto"].tolist(), treino.loc[dom, "intencao"].tolist())
            segundos_ref_adicional = perf_counter() - inicio
            ajustes.append({"fold": numero, "escopo": json.dumps(pe, sort_keys=True),
                "tema": json.dumps(pt, sort_keys=True), "unico": json.dumps(pu, sort_keys=True),
                "ref_reaproveita_escopo": re is escopo, "ref_reaproveita_tema": rt is tema,
                "n_treino": len(tr), "n_treino_tema": int(dom.sum()), "n_validacao": len(va)})
            for nome, modelos, segundos in (("cascata_cv_interna", (escopo, tema), segundos_cascata),
                ("unico_cv_interna", (unico,), segundos_unico),
                ("cascata_referencia_08", (re, rt), segundos_ref_adicional)):
                inicio = perf_counter()
                if len(modelos) == 2:
                    s, t = modelos
                    ps = s.predict_proba(x)
                    it = t.predict_proba(x)
                    pred_s = s.classes_[np.argmax(ps, axis=1)]
                    pred_t = t.classes_[np.argmax(it, axis=1)]
                    pred = np.where(pred_s == DOMINIO, pred_t, pred_s)
                    conf_t = np.max(it, axis=1)
                else:
                    p = unico.predict_proba(x)
                    pred = unico.classes_[np.argmax(p, axis=1)]
                    pred_s = np.where(np.isin(pred, config.nomes_intencoes), DOMINIO, pred)
                    pred_t = np.array([""] * len(x))
                    conf_t = np.zeros(len(x))
                segundos_pred = perf_counter() - inicio
                met_folds.append({"arquitetura": nome, "fold": numero,
                    **metricas_rotas(validacao["intencao"], pred, config.nomes_intencoes)})
                tamanho, vocab = _tamanho(modelos)
                custos.append({"arquitetura": nome, "fold": numero, "pipelines": len(modelos),
                    "segundos_ajuste": segundos, "ms_por_mensagem_batch": segundos_pred * 1000 / len(x),
                    "bytes_modelos_em_memoria": tamanho, "vocabularios_soma": vocab,
                    "ajuste_ref_tempo_somente_adicional": nome == "cascata_referencia_08"})
                for pos, pr, psr, ptr, cf in zip(va, pred, pred_s, pred_t, conf_t):
                    r = dados.iloc[pos]
                    linhas.append({"arquitetura": nome, "fold": numero, "linha_treino": int(r["linha_treino"]),
                        "real": r["intencao"], "origem": r["origem"], "escopo_real": r["escopo"],
                        "escopo_predito": str(psr), "tema_predito": str(ptr), "confianca_tema": float(cf), "predito": str(pr)})
    predicoes = pd.DataFrame(linhas).sort_values(["arquitetura", "linha_treino"]).reset_index(drop=True)
    tabela_folds = pd.DataFrame(met_folds)
    resumo, matrizes, propagacao = [], [], []
    for nome, sub in predicoes.groupby("arquitetura", sort=True):
        f = tabela_folds.loc[tabela_folds["arquitetura"].eq(nome)]
        resumo.append({"arquitetura": nome, "f1_macro_media": float(f["f1_macro"].mean()),
            "f1_macro_desvio": float(f["f1_macro"].std(ddof=0)), "accuracy_media": float(f["accuracy"].mean()),
            "accuracy_desvio": float(f["accuracy"].std(ddof=0)),
            **{k + "_oof": v for k, v in metricas_rotas(sub["real"], sub["predito"], config.nomes_intencoes).items()}})
        cm = confusion_matrix(sub["real"], sub["predito"], labels=classes)
        matrizes += [{"arquitetura": nome, "real": r, "predito": p, "quantidade": int(cm[i, j])}
                     for i, r in enumerate(classes) for j, p in enumerate(classes)]
        if nome != "unico_cv_interna":
            dom = sub["escopo_real"].eq(DOMINIO)
            passou = sub["escopo_predito"].eq(DOMINIO)
            certo_tema = sub["real"].eq(sub["tema_predito"])
            propagacao.append({"arquitetura": nome, "n_dominio": int(dom.sum()),
                "dominio_perdido_no_escopo": int((dom & ~passou).sum()),
                "tema_correto_mas_bloqueado_pelo_escopo": int((dom & ~passou & certo_tema).sum()),
                "dominio_passou_mas_tema_errou": int((dom & passou & ~certo_tema).sum()),
                "n_nao_dominio": int((~dom).sum()), "nao_dominio_encaminhado_ao_tema": int((~dom & passou).sum())})
    if referencias(raiz) != refs:
        raise ValueError("Referências 08 ou dados alterados")
    return {"resumo": pd.DataFrame(resumo), "folds": tabela_folds, "predicoes": predicoes,
        "matrizes": pd.DataFrame(matrizes), "propagacao": pd.DataFrame(propagacao),
        "ajustes": pd.DataFrame(ajustes), "custos": pd.DataFrame(custos), "referencias": refs}


def tabela_limiares(predicoes, intencoes, custos=None):
    custos = CUSTOS if custos is None else custos
    p = predicoes.loc[predicoes["arquitetura"].eq("cascata_referencia_08")].copy()
    if p.empty or p["linha_treino"].duplicated().any():
        raise ValueError("Limiar exige uma previsão OOF de referência por exemplo")
    dom = p["escopo_real"].eq(DOMINIO).to_numpy()
    passa = p["escopo_predito"].eq(DOMINIO).to_numpy()
    correto = p["real"].eq(p["predito"]).to_numpy()
    linhas = []
    for limiar in LIMIARES:
        esclarece = passa & p["confianca_tema"].lt(limiar).to_numpy()
        aceita = passa & ~esclarece
        rota = np.where(esclarece, ESCLARECER, p["predito"])
        fa = int((aceita & ~dom).sum())
        tema_errado = int((aceita & dom & ~correto).sum())
        fr = int((~passa & dom).sum())
        social_trocado = int((~dom & ~passa & ~correto).sum())
        perda = custos["falso_aceite"] * fa + custos["tema_errado"] * tema_errado + custos["esclarecimento"] * int(esclarece.sum()) + custos["falsa_recusa"] * fr + custos["social_fora_trocados"] * social_trocado
        n = int(aceita.sum())
        linhas.append({"limiar": limiar, "aceites_dominio": n,
            "acertos_diretos": int((aceita & correto).sum()),
            "accuracy_aceites": float((aceita & correto).sum() / n) if n else None,
            "esclarecimentos": int(esclarece.sum()), "esclarecimentos_dominio": int((esclarece & dom).sum()),
            "esclarecimentos_nao_dominio": int((esclarece & ~dom).sum()),
            "erros_diretos": fa + tema_errado, "erros_evitados": int((esclarece & ~correto).sum()),
            "acertos_convertidos_esclarecimento": int((esclarece & correto).sum()),
            "falsos_aceites": fa, "falsas_recusas": fr, "perda_total": perda, "perda_media": perda / len(p),
            **metricas_rotas(p["real"], rota, intencoes)})
    return pd.DataFrame(linhas)


def selecionar_limiar(tabela):
    # Custo mínimo; empate: preservar mais acertos diretos e menor limiar.
    return float(tabela.sort_values(["perda_total", "acertos_diretos", "limiar"],
        ascending=[True, False, True], kind="stable").iloc[0]["limiar"])


def integrar(raiz, limiar):
    from dataclasses import replace
    from .config import carregar_config
    from .grafo import construir_grafo

    config = replace(carregar_config(Path(raiz) / "grupo.yaml"), limiar_tema=limiar)
    escopo, tema = carregar_classificadores(config)
    grafo = construir_grafo(config, escopo, tema)
    linhas = []
    for esperado, texto in CASOS_FICTICIOS:
        estado = grafo.invoke({"mensagem": texto})
        if estado.get("fonte_resposta") != "fixa" or not estado.get("resposta"):
            raise AssertionError("Integração offline deve terminar com resposta fixa")
        linhas.append({"tipo_esperado": esperado, "texto_ficticio": texto,
            "rota": estado["rota"], "confianca_intencao": estado.get("confianca_intencao", 0.),
            "resposta": estado["resposta"], "fonte_resposta": estado["fonte_resposta"],
            "escopo": estado["escopo"]})
    return pd.DataFrame(linhas)


def figuras(resumo, limiares):
    """SVG científico standalone: dados reais, sem cache nem acesso a diretório pessoal."""
    from html import escape
    from math import ceil

    def inicio(titulo):
        return ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="440" viewBox="0 0 1000 440">',
            '<style>text{font:14px sans-serif;fill:#203240}.axis{stroke:#52636f;fill:none}.grid{stroke:#dce4e8}</style>',
            f'<title>{escape(titulo)}</title><rect width="1000" height="440" fill="white"/>',
            f'<text x="500" y="28" text-anchor="middle" style="font-size:19px">{escape(titulo)}</text>']

    def linha(x1, y1, x2, y2, classe="axis", cor=None):
        return f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" class="{classe}"' + (f' style="stroke:{cor}"' if cor else '') + '/>'

    s = inicio("A1 — cinco folds comuns; média e desvio do F1 macro")
    for i in range(6):
        val = i / 5
        y = 355 - val * 270
        s += [linha(140, y, 850, y, "grid"), f'<text x="125" y="{y+5:.3f}" text-anchor="end">{val:.1f}</text>']
    tab = resumo.loc[resumo["arquitetura"].isin(["cascata_cv_interna", "unico_cv_interna"])]
    for x, (_, r), cor in zip((350, 650), tab.iterrows(), ("#24608a", "#bf622a")):
        y = 355 - r["f1_macro_media"] * 270
        baixo = 355 - (r["f1_macro_media"] - r["f1_macro_desvio"]) * 270
        alto = 355 - (r["f1_macro_media"] + r["f1_macro_desvio"]) * 270
        nome = "Cascata" if r["arquitetura"] == "cascata_cv_interna" else "Único — oito classes"
        s += [f'<rect x="{x-65}" y="{y:.3f}" width="130" height="{355-y:.3f}" fill="{cor}"/>',
              linha(x, alto, x, baixo), linha(x-12, alto, x+12, alto), linha(x-12, baixo, x+12, baixo),
              f'<text x="{x}" y="{alto-12:.3f}" text-anchor="middle">{r["f1_macro_media"]:.4f} ± {r["f1_macro_desvio"]:.4f}</text>',
              f'<text x="{x}" y="385" text-anchor="middle">{nome}</text>']
    s += ['<text x="500" y="418" text-anchor="middle">CV de treinamento; não é avaliação independente ou teste final</text>', '</svg>']
    saida = {"a1_comparacao.svg": "\n".join(s) + "\n"}
    s = inicio("Limiar de tema — compromisso entre cobertura, erros e esclarecimento")
    series = [("erros_diretos", "#b94c43"), ("esclarecimentos", "#24608a"),
              ("acertos_convertidos_esclarecimento", "#bc7d23")]
    ymax = max(10, ceil(float(limiares[[c for c, _ in series]].max().max()) / 50) * 50)
    ymax_custo = max(.1, ceil(float(limiares["perda_media"].max()) * 11) / 10)
    escolhido = selecionar_limiar(limiares)
    for x0, limite, titulo in ((70, ymax, "Quantidades OOF"), (570, ymax_custo, "Custo médio declarado")):
        for i in range(5):
            valor = limite * i / 4
            y = 335 - i * 60
            s += [linha(x0, y, x0+350, y, "grid"), f'<text x="{x0-8}" y="{y+5}" text-anchor="end">{valor:.2f}</text>']
        for i in range(5):
            x = x0 + i * 87.5
            s += [f'<text x="{x:.3f}" y="358" text-anchor="middle">{i/4:.2f}</text>']
        s += [f'<text x="{x0+175}" y="66" text-anchor="middle">{titulo}</text>',
              f'<text x="{x0+175}" y="383" text-anchor="middle">Limiar de tema</text>',
              linha(x0+escolhido*350, 85, x0+escolhido*350, 335, cor="#697b4c")]
        quais = series if x0 == 70 else [("perda_media", "#24608a")]
        for nome, cor in quais:
            pontos = " ".join(f'{x0+float(r.limiar)*350:.3f},{335-float(getattr(r,nome))/limite*240:.3f}' for r in limiares.itertuples())
            s.append(f'<polyline points="{pontos}" fill="none" stroke="{cor}" stroke-width="2"/>')
    for x, (nome, cor) in zip((60, 330, 590), series):
        s += [f'<text x="{x}" y="411" style="fill:{cor};font-size:12px">{escape(nome)}</text>']
    s += ['<text x="500" y="434" text-anchor="middle" style="font-size:12px">Seleção no mesmo OOF; custo declarado antes da execução; linha vertical: limiar escolhido</text>', '</svg>']
    saida["limiar_compromisso.svg"] = "\n".join(s) + "\n"
    return saida


def resumo_cientifico(resumo, propagacao, limiares, custos, integracao, limiar):
    tab = resumo.loc[resumo["arquitetura"].isin(["cascata_cv_interna", "unico_cv_interna"])].copy()
    ganho = float(tab.loc[tab["arquitetura"].eq("unico_cv_interna"), "f1_macro_media"].iloc[0] - tab.loc[tab["arquitetura"].eq("cascata_cv_interna"), "f1_macro_media"].iloc[0])
    escolhido = limiares.loc[limiares["limiar"].eq(limiar)].iloc[0]
    base = limiares.loc[limiares["limiar"].eq(0)].iloc[0]
    linhas = ["# A1, limiar e integração — resultados reais da Missão 09", "",
        "Cinco folds externas comuns estratificadas nas oito classes; busca de C em três folds internas, calibração em três folds próprias. SVM linear calibrada e TF-IDF char_wb (2,5) em ambas as arquiteturas. O tema é ajustado somente nos rótulos originais de domínio do treino externo. Sem teste reservado.", "",
        "## A1: desempenho ponta a ponta", "", "```csv", tab.to_csv(index=False).strip(), "```", "",
        f"Diferença de F1 macro médio (único − cascata): {ganho:.6f}. A diferença é pequena e as folds não são amostras independentes; não se afirma significância ou superioridade geral. A família/representação foi informada pela 08, portanto a busca interna de C não elimina todo o viés de seleção anterior.", "",
        "O classificador único tem uma vetorização e aprende as oito classes conjuntamente. A cascata separa explicitamente o escopo e reduz o conjunto do tema, mas paga duas calibrações/vetorizações e pode bloquear perguntas cujo tema seria reconhecido. Os arquivos de produção 08 foram preservados: o único é comparação experimental, e a integração continua usando os dois classificadores exigidos pelo contrato.", "",
        "## Propagação de erros", "", "```csv", propagacao.to_csv(index=False).strip(), "```", "",
        "## Custo observado", "", "```csv",
        custos.loc[custos["arquitetura"].ne("cascata_referencia_08")].groupby("arquitetura")[["segundos_ajuste", "ms_por_mensagem_batch", "bytes_modelos_em_memoria", "vocabularios_soma"]].mean().to_csv().strip(), "```", "",
        "Tempos são observações locais, um job/thread, sem benchmark estatístico. A predição diagnóstica da cascata calcula tema para toda a validação para analisar propagação; não equivale à latência online, que pode pular o tema nas recusas. O tempo da cascata de referência registra só refits adicionais/reuso e não deve ser comparado com o ajuste completo das arquiteturas. Tamanhos são serializações em memória de modelos das folds, não novos arquivos de produção.", "",
        "## Limiar operacional da cascata 08", "",
        f"Limiar de tema escolhido: {limiar:.2f}. Critério pré-declarado: custo de falso aceite 5, intenção errada 3, esclarecimento 1, falsa recusa 2 e troca social/fora 1. São pesos internos, não uma exigência do professor nem utilidades validadas com usuários.", "",
        f"Sem limiar: {int(base['aceites_dominio'])} respostas de intenção, {int(base['erros_diretos'])} erradas, precisão condicional {base['accuracy_aceites']:.4%}. Com limiar: {int(escolhido['aceites_dominio'])} respostas de intenção, {int(escolhido['erros_diretos'])} erradas, precisão condicional {escolhido['accuracy_aceites']:.4%}; {int(escolhido['esclarecimentos'])} esclarecimentos, {int(escolhido['erros_evitados'])} erros evitados e {int(escolhido['acertos_convertidos_esclarecimento'])} acertos convertidos. Custo total {int(base['perda_total'])} → {int(escolhido['perda_total'])}. F1 ponta a ponta no mesmo OOF: {base['f1_macro']:.6f} → {escolhido['f1_macro']:.6f}; esclarecimento não é acerto de intenção.", "",
        "O limiar usa previsões OOF das configurações fixas 08, produzidas nas folds comuns desta missão; não mistura OOF de tema/escopo com divisões incompatíveis. A seleção e a descrição do limiar usam os mesmos OOF e são otimistas. Não há avaliação independente da política; famílias/autores podem atravessar folds. A sensibilidade dos pesos está em limiares_sensibilidade.csv, sem escolher pesos pelos resultados.", "",
        "## Integração e limites semânticos", "", "```csv",
        integracao[["tipo_esperado", "rota", "confianca_intencao", "fonte_resposta"]].to_csv(index=False).strip(), "```", "",
        "Todos os cenários são fictícios, fixados antes da seleção do limiar, sem entrar nos CSVs científicos. As respostas são fixas e não usam chave ou OpenRouter. Os testes contratuais com classificadores controlados cobrem seis intenções, social, fora e esclarecimento; eles não demonstram qualidade semântica dos modelos reais.", "",
        "Os casos naturais permanecem no relatório inclusive quando falham. Limiar de confiança não é detector garantido de ambiguidade ou múltiplas intenções: uma pergunta ambígua pode ser classificada como social, e uma pergunta composta pode receber somente a intenção dominante. Erros confiantes de cardápio/pagamento também podem passar pelo limiar. Não se modificaram frases, pesos ou modelos para fazer estes exemplos passar.", "",
        "Próxima etapa: revisão dos resultados pelo grupo e preparação autorizada do RAG. Nenhuma avaliação oficial ou verificação de entrega foi executada."]
    return "\n".join(linhas) + "\n"


def executar_memoria(raiz):
    r = comparar(raiz)
    config, _, _ = preparar(raiz)
    limiares = tabela_limiares(r["predicoes"], config.nomes_intencoes)
    limiar = selecionar_limiar(limiares)
    sensibilidade = []
    for fa, tema in ((3, 2), (5, 3), (8, 5)):
        custos = CUSTOS | {"falso_aceite": fa, "tema_errado": tema}
        tab = tabela_limiares(r["predicoes"], config.nomes_intencoes, custos)
        sensibilidade.append({"custo_falso_aceite": fa, "custo_tema_errado": tema, "limiar": selecionar_limiar(tab)})
    integracao = integrar(raiz, limiar)
    arquivos = {nome + ".csv": r[chave].to_csv(index=False, lineterminator="\n") for nome, chave in
        (("a1_comparacao", "resumo"), ("a1_folds", "folds"), ("predicoes_oof", "predicoes"),
         ("a1_matrizes", "matrizes"), ("a1_propagacao", "propagacao"), ("a1_ajustes", "ajustes"), ("a1_custos", "custos"))}
    arquivos["limiares.csv"] = limiares.to_csv(index=False, lineterminator="\n")
    arquivos["limiares_sensibilidade.csv"] = pd.DataFrame(sensibilidade).to_csv(index=False, lineterminator="\n")
    arquivos["integracao_ficticios.csv"] = integracao.to_csv(index=False, lineterminator="\n")
    arquivos.update(figuras(r["resumo"], limiares))
    arquivos["RESUMO_CIENTIFICO.md"] = resumo_cientifico(r["resumo"], r["propagacao"], limiares, r["custos"], integracao, limiar)
    meta = {"missao": "09", "seed": SEED, "folds_externas": 5, "folds_busca_interna": 3,
        "folds_calibracao": 3, "classes_estratificacao_externa": "oito intencoes originais",
        "algoritmo": "LinearSVC calibrada sigmoid; TF-IDF char_wb (2,5)", "grade_C": [.1, 1., 10.],
        "cascata_producao": "Modelos 08 preservados; escopo C=1, tema C=.1",
        "limiar_tema": limiar, "custos_declarados": CUSTOS, "limiares_analisados": LIMIARES,
        "criterio": "Minimizar custo OOF; desempate por mais acertos diretos e menor limiar. Custos declarados antes da execução.",
        "limitacoes": "Familia/representacao escolhidas na 08 com este treino; CV interna adicional so para C nao remove todo vies de selecao anterior. Familias/autores podem atravessar folds. Limiar escolhido e descrito nos mesmos OOF: diagnostico otimista, sem estimativa independente de sua politica. Custos sao decisao interna, nao regra do professor. Tempos batch em amostra pequena e referencia com tempo de refit apenas adicional nao sao benchmark de producao.",
        "referencias_08_e_dados": r["referencias"], "avaliacao_oficial_executada": False,
        "melhor_a1": r["resumo"].loc[r["resumo"]["arquitetura"].ne("cascata_referencia_08")].sort_values("f1_macro_media", ascending=False).iloc[0]["arquitetura"],
        "integracao": "construir_grafo(config, clf_escopo, clf_tema), sem LLM, com limiar selecionado; ficticios fixados antes dos resultados"}
    from importlib.metadata import version
    import hashlib
    import platform
    meta["python"] = platform.python_version()
    meta["versoes"] = {p: version(p) for p in ("numpy", "pandas", "scikit-learn", "joblib", "langgraph")}
    meta["figuras"] = "SVG standalone derivado de tabelas reais; Matplotlib indisponivel no sandbox sem cache gravavel"
    meta["tempo_inferencia"] = "Diagnostico batch calcula tema em todos os exemplos; nao e latencia de producao"
    meta["sha256_artefatos"] = {n: hashlib.sha256(t.encode()).hexdigest() for n, t in arquivos.items()}
    arquivos["metadados.json"] = json.dumps(meta, ensure_ascii=False, indent=2) + "\n"
    if referencias(raiz) != r["referencias"]:
        raise AssertionError("Dados, modelos 08 ou resultados 08 alterados")
    return {"arquivos": arquivos, "metadados": meta}


def gravar(raiz, resultado):
    pasta = Path(raiz) / "resultados/aprofundamento_09"
    pasta.mkdir(parents=True, exist_ok=True)
    for nome, texto in resultado["arquivos"].items():
        (pasta / nome).write_text(texto, encoding="utf-8")
    config = Path(raiz) / "grupo.yaml"
    import re
    anterior = config.read_text(encoding="utf-8")
    texto, n = re.subn(r"(?m)^(  limiar_tema:) [^\n]+$", r"\g<1> " + str(resultado["metadados"]["limiar_tema"]), anterior)
    if n != 1:
        raise ValueError("Campo de limiar não encontrado de forma inequívoca")
    config.write_text(texto, encoding="utf-8")
