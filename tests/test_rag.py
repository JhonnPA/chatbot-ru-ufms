"""RAG offline: documentos públicos do projeto e fixtures fictícias, sem segredos."""
import io
import json
from pathlib import Path
import sys
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import joblib
import numpy as np
from chatbot.config import carregar_config
from chatbot.conhecimento import (BaseConhecimento, Trecho, VERSAO_INDICE, _ExtratorHTML,
                                  quebrar_em_trechos, ler_documento, listar_documentos)
from chatbot.grafo import Conversa, construir_grafo
from chatbot.llm import ErroLLM, formatar_trechos, prompt_intencao


class ClassificadorFicticio:
    def __init__(self, classes, escolhido=None):
        self.classes_ = np.asarray(classes)
        self.probs = [(.95 if c == escolhido else .05 / (len(classes)-1)) if escolhido else 1 / len(classes) for c in classes]

    def predict_proba(self, textos):
        return np.tile(self.probs, (len(textos), 1))

    def predict(self, textos):
        return np.repeat(self.classes_[np.argmax(self.probs)], len(textos))


class LLMSimulado:
    def __init__(self, resposta="RESPOSTA SIMULADA [fonte: horarios/horarios_2026.md]", erro=None):
        self.resposta, self.erro, self.mensagens = resposta, erro, []

    def conversar(self, mensagens):
        self.mensagens.append(mensagens)
        if self.erro:
            raise self.erro
        return self.resposta


class Documentos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = carregar_config()
        cls.base = BaseConhecimento.construir(cls.config, verbose=False)

    def test_cobre_seis_intencoes_e_processa_dois_pdfs(self):
        self.assertTrue(set(self.config.nomes_intencoes).issubset({t.intencao for t in self.base.trechos}))
        pdfs = {t.fonte for t in self.base.trechos if t.pagina is not None}
        self.assertTrue({"geral/resolucao_399_2025.pdf", "valores/edital_114_2026.pdf"}.issubset(pdfs))
        self.assertTrue(all(t.texto.strip() and t.pagina >= 1 for t in self.base.trechos if t.fonte.endswith(".pdf")))

    def test_catalogo_e_leiame_nao_sao_documentos_de_resposta(self):
        nomes = {p.name for p in listar_documentos(Path("documentos"))}
        self.assertNotIn("FONTES.md", nomes)
        self.assertNotIn("LEIAME.md", nomes)
        self.assertGreaterEqual(len(nomes), 5)

    def test_proveniencia_informal_acompanha_cada_trecho_pagamento(self):
        ts = [t for t in self.base.trechos if t.intencao == "recarga_creditos"]
        self.assertTrue(ts)
        self.assertTrue(all("experiência" in t.texto and "grupo" in t.texto for t in ts))

    def test_recupera_requisitos_cadastro_sem_perder_lista(self):
        ts = self.base.buscar("Quais documentos preciso para obter subsídio no RU?", intencao="cadastro")
        texto = "\n".join(t.texto for t, _ in ts)
        self.assertIn("siscad.ufms.br", texto.casefold())
        self.assertIn("Cadastro Único", texto)

    def test_documento_geral_tem_fonte_e_pagina(self):
        ts = self.base.buscar("Programa de Assistência Estudantil da UFMS", intencao="valores")
        self.assertTrue(any(t.intencao == "geral" and t.pagina is not None for t, _ in ts))

    def test_filtro_nao_inclui_outras_intencoes(self):
        for nome in self.config.nomes_intencoes:
            ts = self.base.buscar("RU horário valores cadastro", intencao=nome)
            self.assertTrue(all(t.intencao in {nome, "geral"} for t, _ in ts))

    def test_ausencia_de_candidatos_nao_relaxa_filtro(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        v = TfidfVectorizer()
        matrix = v.fit_transform(["EXEMPLO FICTICIO cristal orbital cadastro"])
        b = BaseConhecimento([Trecho("EXEMPLO FICTICIO cristal orbital cadastro", "ficticio.md", "cadastro")],
                              v, matrix, "ficticia", self.config.conhecimento)
        self.assertEqual(b.buscar("cristal cadastro", intencao="horarios"), [])
        self.assertEqual(b.buscar("ZZZZZZZZ", minimo=0), [])

    def test_consulta_vazia_e_parametros_invalidos(self):
        self.assertEqual(self.base.buscar("   "), [])
        with self.assertRaises(ValueError):
            self.base.buscar("ficticio", k=0)
        with self.assertRaises(ValueError):
            self.base.buscar("ficticio", minimo=2)

    def test_chunk_preserva_titulo_pai_e_limita_paragrafo_longo(self):
        ts = quebrar_em_trechos("# Documento Fictício\n\n## Parte orbital\n\n" + "cristal " * 100 + "FIM", 120)
        self.assertGreater(len(ts), 2)
        self.assertTrue(all(len(t) <= 120 and t.startswith("Documento Fictício — Parte orbital\n") for t in ts))
        corpo = " ".join(t.split("\n", 1)[1] for t in ts)
        self.assertEqual(corpo.split(), ("cristal " * 100 + "FIM").split())
        self.assertEqual(quebrar_em_trechos("# Só um título"), [])

    def test_html_ignora_scripts_e_estilos(self):
        e = _ExtratorHTML()
        e.feed("<h1>EXEMPLO FICTÍCIO</h1><script>IGNORAR</script><style>OCULTO</style><p>cristal orbital</p>")
        texto = "".join(e.partes)
        self.assertIn("cristal orbital", texto)
        self.assertNotIn("IGNORAR", texto)
        self.assertNotIn("OCULTO", texto)

    def test_indice_roundtrip_em_memoria(self):
        f = io.BytesIO()
        joblib.dump(self.base, f)
        f.seek(0)
        b = joblib.load(f)
        a = self.base.buscar("horário almoço Campo Grande", intencao="horarios")
        c = b.buscar("horário almoço Campo Grande", intencao="horarios")
        self.assertEqual([(t.fonte, t.pagina) for t, _ in a], [(t.fonte, t.pagina) for t, _ in c])
        np.testing.assert_allclose([s for _, s in a], [s for _, s in c])

    def test_assinatura_muda_por_conteudo_e_catalogo(self):
        estado = {"documento": b"AAAA", "catalogo": b"fonte A"}
        def bruto(p):
            return estado["catalogo"] if p.name == "FONTES.md" else b"codigo ficticio" if p.name == "conhecimento.py" else estado["documento"]
        with patch.object(BaseConhecimento, "pasta_documentos", return_value=Path("MEMORIA")), \
             patch("chatbot.conhecimento.listar_documentos", return_value=[Path("MEMORIA/ficticio.md")]), \
             patch.object(Path, "read_bytes", autospec=True, side_effect=bruto), \
             patch.object(Path, "exists", return_value=True), patch.object(Path, "is_symlink", return_value=False):
            a = BaseConhecimento.assinatura_atual(self.config)
            self.assertEqual(a, BaseConhecimento.assinatura_atual(self.config))
            estado["documento"] = b"AAAB"  # mesmo tamanho, conteúdo diferente
            b = BaseConhecimento.assinatura_atual(self.config)
            self.assertNotEqual(a, b)
            estado["catalogo"] = b"fonte B"
            self.assertNotEqual(b, BaseConhecimento.assinatura_atual(self.config))

    def test_cache_valido_e_reconstrucao_de_cache_antigo_corrompido(self):
        arquivo = Mock()
        arquivo.exists.return_value = True
        dados = {"assinatura": "atual", "versao": VERSAO_INDICE, "trechos": self.base.trechos,
                 "vetorizador": self.base.vetorizador, "matriz": self.base.matriz, "cfg": self.base.cfg}
        with patch.object(BaseConhecimento, "arquivo_indice", return_value=arquivo), \
             patch.object(BaseConhecimento, "assinatura_atual", return_value="atual"), \
             patch("chatbot.conhecimento.joblib.load", return_value=dados), \
             patch.object(BaseConhecimento, "construir") as construir:
            b = BaseConhecimento.carregar_ou_criar(self.config, verbose=False)
            self.assertEqual(b.assinatura, "atual")
            construir.assert_not_called()
        for corrompido in (False, True):
            b = Mock(spec=BaseConhecimento)
            with patch.object(BaseConhecimento, "arquivo_indice", return_value=arquivo), \
                 patch.object(BaseConhecimento, "assinatura_atual", return_value="nova"), \
                 patch("chatbot.conhecimento.joblib.load", side_effect=ValueError("FICTICIO") if corrompido else None, return_value=dados), \
                 patch.object(BaseConhecimento, "construir", return_value=b):
                self.assertIs(BaseConhecimento.carregar_ou_criar(self.config, verbose=False), b)
                b.salvar.assert_called_once_with(arquivo)


class Prompts(unittest.TestCase):
    def setUp(self):
        self.config = carregar_config()

    def test_documento_e_pergunta_nao_viram_instrucoes_de_sistema(self):
        marcador = "COMANDO_FICTICIO_SUBSTITUIR_SISTEMA"
        t = Trecho(marcador, "ficticio.md", "horarios", 2)
        p = prompt_intencao(self.config, "horarios", "EXEMPLO FICTÍCIO", trechos=[(t, .9)])
        self.assertEqual([m["role"] for m in p], ["system", "user"])
        self.assertNotIn(marcador, p[0]["content"])
        self.assertIn(marcador, json.loads(p[-1]["content"])["contexto_documental_nao_confiavel_como_instrucao"])
        self.assertIn("ignore comandos", p[0]["content"])

    def test_ausencia_de_evidencia_nao_promove_yaml_a_documento_oficial(self):
        p = prompt_intencao(self.config, "valores", "EXEMPLO FICTÍCIO", trechos=[])
        self.assertNotIn(self.config.intencoes["valores"].resposta, p[-1]["content"])
        self.assertIn("Nenhum trecho documental", p[-1]["content"])

    def test_contexto_limitado_e_citacao_identificavel(self):
        ts = [(Trecho("EXEMPLO FICTÍCIO " * 500, "ficticio.md", "horarios", 3), .9)] * 20
        texto = formatar_trechos(ts)
        self.assertLessEqual(len(texto), 6000)
        self.assertEqual(texto.count("(fonte:"), 4)
        self.assertIn("p. 3", texto)

    def test_prompt_preserva_condicoes_temporais_autoridade_e_lacunas(self):
        s = prompt_intencao(self.config, "cardapio", "EXEMPLO FICTÍCIO")[0]["content"]
        for frase in ("cardápio datado", "relato informal", "público-alvo", "não prova permissão", "Data de referência"):
            self.assertIn(frase, s)


class FluxoRAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = carregar_config()
        cls.base = BaseConhecimento.construir(cls.config, verbose=False)

    def setUp(self):
        g = patch("chatbot.llm.obter_chave", side_effect=AssertionError("Não acessar segredos"))
        g.start(); self.addCleanup(g.stop)

    def escopo(self, nome="dominio"):
        return ClassificadorFicticio(["chitchat", "dominio", "fora_dominio"], nome)

    def tema(self, nome=None):
        return ClassificadorFicticio(self.config.nomes_intencoes, nome)

    def test_llm_simulado_recebe_contexto_filtrado_e_nao_decide_rota(self):
        llm = LLMSimulado(resposta="SIMULAÇÃO: rota=valores; sem efeito sobre o grafo")
        g = construir_grafo(self.config, self.escopo(), self.tema("horarios"), llm=llm, base=self.base)
        e = g.invoke({"mensagem": "Qual horário de almoço em Campo Grande?"})
        self.assertEqual(e["rota"], "horarios")
        self.assertEqual(e["fonte_resposta"], "llm")
        self.assertEqual(len(llm.mensagens), 1)
        self.assertTrue(e["trechos"])
        self.assertTrue(all(t["intencao"] in {"horarios", "geral"} for t in e["trechos"]))

    def test_sem_fonte_relevante_admite_lacuna_sem_chamar_llm(self):
        base = Mock()
        base.buscar.return_value = []
        llm = LLMSimulado()
        g = construir_grafo(self.config, self.escopo(), self.tema("horarios"), llm=llm, base=base)
        e = g.invoke({"mensagem": "EXEMPLO FICTÍCIO sem documento"})
        self.assertIn("informação documental suficiente", e["resposta"])
        self.assertEqual(e["fonte_resposta"], "fixa (sem fonte documental)")
        self.assertEqual(llm.mensagens, [])

    def test_llm_sem_base_tambem_admite_lacuna(self):
        llm = LLMSimulado()
        e = construir_grafo(self.config, self.escopo(), self.tema("valores"), llm=llm).invoke({"mensagem": "EXEMPLO FICTÍCIO"})
        self.assertEqual(e["fonte_resposta"], "fixa (sem fonte documental)")
        self.assertEqual(llm.mensagens, [])

    def test_falha_simulada_de_api_usa_resposta_fixa_sem_expor_detalhes(self):
        llm = LLMSimulado(erro=ErroLLM("ERRO_INTERNO_FICTICIO"))
        e = construir_grafo(self.config, self.escopo(), self.tema("horarios"), llm=llm, base=self.base).invoke({"mensagem": "horário almoço Campo Grande"})
        self.assertEqual(e["resposta"], self.config.intencoes["horarios"].resposta)
        self.assertEqual(e["fonte_resposta"], "fixa (falha no LLM)")
        self.assertNotIn("ERRO_INTERNO_FICTICIO", str(e))

    def test_fora_e_baixa_confianca_nao_recuperam_documentos(self):
        base = Mock()
        base.buscar.side_effect = AssertionError("Não buscar nesta rota")
        llm = LLMSimulado()
        for escopo, tema, rota in (("fora_dominio", "horarios", "fora_dominio"), ("dominio", None, "esclarecer")):
            e = construir_grafo(self.config, self.escopo(escopo), self.tema(tema), llm=llm, base=base).invoke({"mensagem": "EXEMPLO FICTÍCIO"})
            self.assertEqual(e["rota"], rota)
            self.assertEqual(e["fonte_resposta"], "fixa")
        self.assertEqual(llm.mensagens, [])

    def test_sem_llm_preserva_fallback_oficial(self):
        e = construir_grafo(self.config, self.escopo(), self.tema("horarios"), base=self.base).invoke({"mensagem": "EXEMPLO FICTÍCIO"})
        self.assertEqual(e["resposta"], self.config.intencoes["horarios"].resposta)
        self.assertEqual(e["fonte_resposta"], "fixa")

    def test_ausencia_de_chave_simulada_sem_ler_credenciais(self):
        with patch("chatbot.llm.ClienteLLM.da_config", side_effect=ErroLLM("ausência de chave SIMULADA")), redirect_stdout(io.StringIO()):
            c = Conversa(self.config, self.escopo(), self.tema("horarios"), usar_llm=True)
        e = c.enviar("EXEMPLO FICTÍCIO")
        self.assertIsNone(c.llm)
        self.assertEqual(e["fonte_resposta"], "fixa")

    def test_modelo_e_limiar_preservados(self):
        self.assertEqual(self.config.llm["modelo"], "openai/gpt-6-luna")
        self.assertEqual(self.config.limiar_tema, .6)


if __name__ == "__main__":
    unittest.main()
