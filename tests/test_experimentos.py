"""Proteção do teste e contratos ML com exemplos técnicos fictícios."""
from __future__ import annotations

import ast
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
DISPONIVEL = all(importlib.util.find_spec(p) is not None for p in ("numpy", "pandas", "sklearn", "yaml", "joblib"))
if DISPONIVEL:
    import joblib
    import numpy as np
    import pandas as pd
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.pipeline import Pipeline
    from chatbot import experimentos as e


class ProtecaoDoTeste(unittest.TestCase):
    def test_leitura_de_dados_restrita_ao_treino(self):
        arvore = ast.parse((RAIZ / "chatbot/experimentos.py").read_text())
        leituras = [n for n in ast.walk(arvore) if isinstance(n, ast.Call) and
                    isinstance(n.func, ast.Name) and n.func.id == "carregar_dados"]
        self.assertEqual(len(leituras), 1)
        argumento = leituras[0].args[0]
        self.assertIsInstance(argumento, ast.Attribute)
        self.assertEqual(argumento.attr, "treino")

    def test_nao_importa_llm_grafo_ou_avaliadores(self):
        arvore = ast.parse((RAIZ / "chatbot/experimentos.py").read_text())
        modulos = [n.module for n in ast.walk(arvore) if isinstance(n, ast.ImportFrom)]
        self.assertFalse(set(modulos) & {"llm", "grafo", "avaliacao"})

    def test_notebook_nao_executa_etapas_reservadas(self):
        nb = json.loads((RAIZ / "notebooks/01_trabalho_grupo.ipynb").read_bytes())
        for c in nb["cells"]:
            if c["cell_type"] != "code":
                continue
            fonte = "".join(c["source"])
            ast.parse(fonte)
            for comando in ("scripts/avaliar.py", "scripts/verificar_entrega.py", "ClienteLLM", "carregar_dados(config.teste)"):
                self.assertNotIn(comando, fonte)


@unittest.skipUnless(DISPONIVEL, "Dependências ML indisponíveis; não executado nem contabilizado como validação ML")
class ContratosML(unittest.TestCase):
    def ficticios(self):
        classes = ["chitchat", "dominio", "fora_dominio"]
        palavras = ["cristal", "esfera", "prisma"]
        textos, rotulos = [], []
        for c, palavra in zip(classes, palavras):
            for i in range(12):
                textos.append(f"EXEMPLO FICTÍCIO {palavra} orbital {palavra} série {i}")
                rotulos.append(c)
        return textos, rotulos

    def test_folds_estratificadas_disjuntas_e_reproduziveis(self):
        x, y = self.ficticios()
        p = e.particoes(y)
        q = e.particoes(y)
        self.assertEqual(len(p), 5)
        vistos = []
        for (tr, va), (tr2, va2) in zip(p, q):
            self.assertFalse(set(tr) & set(va))
            self.assertEqual(set(np.array(y)[va]), set(y))
            np.testing.assert_array_equal(tr, tr2)
            np.testing.assert_array_equal(va, va2)
            vistos.extend(va)
        self.assertEqual(sorted(vistos), list(range(len(x))))

    def test_svm_calibra_pipeline_completo(self):
        pipe, grade = e.candidato("svm_calibrada", "caracteres")
        cal = pipe.named_steps["calibrado"]
        self.assertIsInstance(cal, CalibratedClassifierCV)
        self.assertIsInstance(cal.estimator, Pipeline)
        self.assertIn("vetorizador", cal.estimator.named_steps)
        self.assertEqual(cal.cv.n_splits, 3)
        self.assertFalse(cal.ensemble)
        self.assertEqual(len(next(iter(grade.values()))), 3)

    def test_seis_pipelines_round_trip_em_memoria_e_probabilidades(self):
        x, y = self.ficticios()
        for algoritmo in e.ALGORITMOS:
            for representacao in e.REPRESENTACOES:
                with self.subTest(algoritmo=algoritmo, representacao=representacao):
                    pipe, grade = e.candidato(algoritmo, representacao)
                    pipe.fit(x, y)
                    self.assertIsInstance(pipe, Pipeline)
                    self.assertEqual(set(pipe.classes_), set(y))
                    ficticio = ["EXEMPLO FICTÍCIO esfera orbital 73"]
                    esperado = pipe.predict_proba(ficticio)
                    self.assertEqual(esperado.shape, (1, 3))
                    np.testing.assert_allclose(esperado.sum(axis=1), 1)
                    fluxo = io.BytesIO()
                    joblib.dump(pipe, fluxo)
                    fluxo.seek(0)
                    novo = joblib.load(fluxo)
                    np.testing.assert_allclose(novo.predict_proba(ficticio), esperado)
                    np.testing.assert_array_equal(novo.predict(ficticio), pipe.predict(ficticio))

    def test_tema_exclui_chitchat_e_fora_pelo_rotulo_original(self):
        dados = pd.DataFrame({"texto": ["FICTÍCIO cristal", "FICTÍCIO prisma", "FICTÍCIO esfera"],
            "intencao": ["cardapio", "chitchat", "fora_dominio"], "escopo": ["dominio", "chitchat", "fora_dominio"]})
        sub = e.conjuntos_estagios(dados)
        self.assertEqual(sub["tema"]["intencao"].tolist(), ["cardapio"])
        self.assertEqual(len(sub["escopo"]), 3)

    def test_tema_rejeita_dados_fora_do_dominio(self):
        dados = pd.DataFrame({"texto": ["FICTÍCIO prisma"], "escopo": ["fora_dominio"], "intencao": ["fora_dominio"]})
        with self.assertRaisesRegex(ValueError, "somente"):
            e.experimentar_estagio("tema", dados, ["cardapio"])

    def test_oof_alinha_probabilidades_a_ordem_contratual(self):
        x, y = self.ficticios()
        dados = pd.DataFrame({"texto": x, "escopo": y, "origem": ["llm"] * len(x),
                              "linha_treino": np.arange(len(x)) + 2})
        pipe, _ = e.candidato("logistica", "palavras")
        classes = ["dominio", "chitchat", "fora_dominio"]
        oof, metricas = e.previsoes_oof(pipe, dados, "escopo", classes, e.particoes(y))
        self.assertEqual(len(oof), len(x))
        self.assertEqual(oof["linha_treino"].nunique(), len(x))
        self.assertEqual(len(metricas), 5)
        for _, r in oof.iterrows():
            probabilidades = json.loads(r["probabilidades"])
            self.assertEqual(set(probabilidades), set(classes))
            self.assertAlmostEqual(sum(probabilidades.values()), 1)
            self.assertEqual(max(probabilidades, key=probabilidades.get), r["predito"])


if __name__ == "__main__":
    unittest.main()
