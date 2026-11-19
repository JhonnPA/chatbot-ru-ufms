"""Regressões da reprodução 08→09, com modelos/entradas fictícios e I/O em memória."""
import ast
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import joblib
import numpy as np
import pandas as pd
from chatbot import aprofundamento as a
from chatbot.config import carregar_config
from chatbot.experimentos import candidato


class Reproducao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = carregar_config()
        rotulos = cls.cfg.nomes_intencoes + ["chitchat", "fora_dominio"]
        cls.dados = pd.DataFrame([
            {"texto": f"EXEMPLO FICTÍCIO {c} cristal {i}", "intencao": c,
             "escopo": "dominio" if c in cls.cfg.nomes_intencoes else c}
            for c in rotulos for i in range(12)])
        cls.oficiais = []
        for etapa, C in (("escopo", 1.), ("tema", .1)):
            m, _ = candidato("svm_calibrada", "caracteres")
            m.set_params(calibrado__estimator__classificador__C=C)
            d = cls.dados if etapa == "escopo" else cls.dados.loc[cls.dados["escopo"].eq("dominio")]
            cls.oficiais.append(m.fit(d["texto"].tolist(), d["escopo" if etapa == "escopo" else "intencao"].tolist()))

    def setUp(self):
        self.novos = []
        self.hashes = dict(a.HASHES_DADOS)
        self.meta = {"seed": a.SEED, "folds": 5, "hashes_entrada": dict(a.HASHES_DADOS),
                     "contratos_modelos": {}, "selecionados": {}}
        for etapa, modelo, C in zip(("escopo", "tema"), self.oficiais, (1., .1)):
            f = io.BytesIO()
            joblib.dump(modelo, f, compress=3)
            h = hashlib.sha256(f.getvalue()).hexdigest()
            f.seek(0)
            self.novos.append(joblib.load(f))
            self.hashes[f"modelos/{etapa}.joblib"] = h
            self.meta["contratos_modelos"][f"sha256_{etapa}"] = h
            self.meta["selecionados"][etapa] = {"algoritmo": "svm_calibrada", "representacao": "caracteres",
                "parametros": json.dumps({"calibrado__estimator__classificador__C": C})}
        def sha(p):
            return next((h for n, h in self.hashes.items() if str(p).endswith(n)), "0" * 64)
        for mock in (patch.object(a, "preparar", return_value=(self.cfg, self.dados, {})),
                     patch.object(a, "carregar_classificadores", return_value=self.novos),
                     patch.object(a, "sha256", side_effect=sha)):
            mock.start()
            self.addCleanup(mock.stop)

    def validar(self):
        return a.validar_modelos_reproduzidos(Path("MEMORIA"), self.oficiais, self.meta)

    def test_novos_bytes_equivalentes_aceitos_sem_hash_antigo(self):
        perfil = self.validar()
        self.assertEqual(perfil, {n: self.hashes[n] for n in a.MODELOS_08})
        self.assertNotEqual(perfil, a.MODELOS_08)
        self.assertTrue(a.referencias("MEMORIA", modelos_esperados=perfil))

    def test_modo_oficial_continua_rejeitando_outros_bytes(self):
        with self.assertRaisesRegex(ValueError, "Referência experimental divergente"):
            a.referencias("MEMORIA")

    def test_snapshot_validado_continua_detectando_alteracao_posterior(self):
        perfil = self.validar()
        self.hashes["modelos/escopo.joblib"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "Referência experimental divergente"):
            a.referencias("MEMORIA", modelos_esperados=perfil)

    def test_metadados_nao_autorizam_mudar_hiperparametros(self):
        self.meta["selecionados"]["tema"]["parametros"] = json.dumps({"calibrado__estimator__classificador__C": 10})
        with self.assertRaisesRegex(ValueError, "Decisão científica divergente"):
            self.validar()

    def test_pipeline_com_parametro_errado_rejeitado(self):
        self.novos[0].set_params(calibrado__estimator__classificador__C=10)
        with self.assertRaisesRegex(ValueError, "Configuração do pipeline divergente"):
            self.validar()

    def test_pesos_errados_nao_passam_so_por_classes_e_parametros(self):
        base = self.novos[0].named_steps["calibrado"].calibrated_classifiers_[0].estimator
        base.named_steps["classificador"].coef_ *= -1
        with self.assertRaises(AssertionError):
            self.validar()

    def test_ordem_de_classes_errada_rejeitada(self):
        m = self.novos[1].named_steps["calibrado"]
        m.classes_ = m.classes_[::-1].copy()
        with self.assertRaises(AssertionError):
            self.validar()

    def test_probabilidades_invalidas_rejeitadas(self):
        n = len(self.dados) + 2
        with patch.object(self.novos[0], "predict_proba", return_value=np.full((n, 3), np.nan)):
            with self.assertRaisesRegex(ValueError, "Probabilidades inválidas"):
                self.validar()

    def test_outro_treino_e_hash_de_modelo_errado_rejeitados(self):
        self.meta["hashes_entrada"]["dados/treino.csv"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Dados de reprodução divergentes"):
            self.validar()
        self.meta["hashes_entrada"] = dict(a.HASHES_DADOS)
        self.meta["contratos_modelos"]["sha256_tema"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Referência experimental divergente"):
            self.validar()

    def test_snapshot_incompleto_rejeitado(self):
        with self.assertRaisesRegex(ValueError, "Snapshot deve conter"):
            a.referencias("MEMORIA", modelos_esperados={})

    def test_notebook_bloqueia_checkout_antes_de_qualquer_ajuste(self):
        nb = json.loads(Path("notebooks/01_trabalho_grupo.ipynb").read_text())
        codes = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
        self.assertEqual(len(codes), 22)
        for s in codes:
            ast.parse(s)
        self.assertIn('(raiz / ".git").exists()', codes[0])
        self.assertIn("raise RuntimeError", codes[0])
        self.assertIn("modelos_oficiais08 = carregar_classificadores", "".join(nb["cells"][5]["source"]))
        self.assertIn("validar_modelos_reproduzidos", "".join(nb["cells"][23]["source"]))
        for i in (32, 41):
            self.assertIn("modelos_esperados=modelos_esperados08", "".join(nb["cells"][i]["source"]))


if __name__ == "__main__":
    unittest.main()
