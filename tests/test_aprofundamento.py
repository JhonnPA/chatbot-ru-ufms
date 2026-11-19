"""Contratos A1/limiar/grafo com fixtures fictícias, sem abrir dados de teste."""
import unittest
from dataclasses import replace
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from chatbot.aprofundamento import metricas_rotas, selecionar_limiar, tabela_limiares
from chatbot.config import carregar_config
from chatbot.grafo import construir_grafo, prever_com_confianca
from chatbot.rotulos import CLASSES_ESCOPO


class ClassificadorFicticio:
    def __init__(self, classes, probabilidades):
        self.classes_ = np.asarray(classes)
        self.probabilidades = probabilidades
        self.chamadas = 0

    def predict_proba(self, textos):
        self.chamadas += 1
        return np.tile(self.probabilidades, (len(textos), 1))

    def predict(self, textos):
        return np.repeat(self.classes_[np.argmax(self.probabilidades)], len(textos))


class Limiar(unittest.TestCase):
    def test_conta_falsos_aceites_recusas_e_erros_propagados(self):
        r = metricas_rotas(["cardapio", "fora_dominio", "cadastro", "chitchat"],
                           ["fora_dominio", "cardapio", "regras_uso", "chitchat"],
                           ["cardapio", "cadastro", "regras_uso"])
        self.assertEqual(r["falsos_aceites"], 1)
        self.assertEqual(r["falsas_recusas"], 1)
        self.assertEqual(r["erros"], 3)

    def dados(self):
        return pd.DataFrame({"arquitetura": ["cascata_referencia_08"] * 3,
            "linha_treino": [2, 3, 4], "real": ["cardapio", "fora_dominio", "fora_dominio"],
            "predito": ["cardapio", "cardapio", "fora_dominio"],
            "escopo_real": ["dominio", "fora_dominio", "fora_dominio"],
            "escopo_predito": ["dominio", "dominio", "fora_dominio"],
            "confianca_tema": [.9, .4, .2]})

    def test_custo_prefere_evitar_erro_sem_perder_acerto_certo(self):
        t = tabela_limiares(self.dados(), ["cardapio"])
        self.assertEqual(selecionar_limiar(t), .45)
        r = t.loc[t["limiar"].eq(.45)].iloc[0]
        self.assertEqual(r["erros_evitados"], 1)
        self.assertEqual(r["acertos_convertidos_esclarecimento"], 0)
        self.assertEqual(r["falsos_aceites"], 0)

    def test_igualdade_ao_limiar_aceita_como_no_grafo(self):
        t = tabela_limiares(self.dados(), ["cardapio"])
        self.assertEqual(t.loc[t["limiar"].eq(.4), "esclarecimentos"].iloc[0], 0)

    def test_rejeita_registro_oof_repetido(self):
        p = self.dados()
        p.loc[1, "linha_treino"] = 2
        with self.assertRaises(ValueError):
            tabela_limiares(p, ["cardapio"])


class IntegracaoOffline(unittest.TestCase):
    def setUp(self):
        self.config = replace(carregar_config(), limiar_tema=.7)
        self.seguro = patch("chatbot.llm.obter_chave", side_effect=AssertionError("Acesso a segredo proibido"))
        self.seguro.start()
        self.addCleanup(self.seguro.stop)

    def escopo(self, classe):
        return ClassificadorFicticio(CLASSES_ESCOPO, [.96 if c == classe else .02 for c in CLASSES_ESCOPO])

    def tema(self, classe=None):
        classes = list(reversed(self.config.nomes_intencoes))
        return ClassificadorFicticio(classes, [(.95 if c == classe else .01) if classe else 1/6 for c in classes])

    def test_classes_probabilidades_alinhadas_sem_ordem_assumida(self):
        m = self.tema("cadastro")
        c, prob, alternativas = prever_com_confianca(m, "EXEMPLO FICTICIO ORBITAL")
        self.assertEqual(c, "cadastro")
        self.assertEqual(prob, .95)
        self.assertEqual(alternativas[0][0], "cadastro")

    def test_seis_rotas_e_respostas_fixas_pelo_contrato_original(self):
        for nome in self.config.nomes_intencoes:
            with self.subTest(nome=nome):
                g = construir_grafo(self.config, self.escopo("dominio"), self.tema(nome))
                estado = g.invoke({"mensagem": "EXEMPLO FICTICIO NEBULA 73"})
                self.assertEqual(estado["rota"], nome)
                self.assertEqual(estado["resposta"], self.config.intencoes[nome].resposta)
                self.assertEqual(estado["fonte_resposta"], "fixa")

    def test_fora_e_social_nao_chamam_tema_nem_llm(self):
        for nome in ("fora_dominio", "chitchat"):
            tema = self.tema("cardapio")
            g = construir_grafo(self.config, self.escopo(nome), tema)
            e = g.invoke({"mensagem": "EXEMPLO FICTICIO PRISMA 91"})
            self.assertEqual(e["rota"], nome)
            self.assertEqual(e["fonte_resposta"], "fixa")
            self.assertEqual(tema.chamadas, 0)

    def test_baixa_confianca_pede_esclarecimento_com_duas_alternativas(self):
        g = construir_grafo(self.config, self.escopo("dominio"), self.tema())
        e = g.invoke({"mensagem": "EXEMPLO FICTICIO AMBIGUO"})
        self.assertEqual(e["rota"], "esclarecer")
        self.assertEqual(e["fonte_resposta"], "fixa")
        self.assertGreaterEqual(len(e["candidatas"]), 2)
        self.assertIn("Sua dúvida", e["resposta"])


if __name__ == "__main__":
    unittest.main()
