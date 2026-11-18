"""Fixtures técnicas fictícias; nenhum dado bruto ou frase reservada é usado."""
from __future__ import annotations

import csv
import io
import json
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import auditar_dados as a


def celula(texto, fonte="H", envio=1, coluna=3, rotulo="cardapio"):
    return a.Celula(fonte, envio, coluna, texto, rotulo)


def csv_ficticio(fonte="H", linhas=None):
    """Reutiliza apenas os cabeçalhos públicos; respostas inventadas para testes."""
    saida = io.StringIO(newline="")
    escritor = csv.writer(saida)
    escritor.writerow((["Carimbo de data/hora"] if fonte == "H" else []) + list(a.PERGUNTAS))
    for linha in linhas or [[""] * 10]:
        escritor.writerow((["METADADO_FICTICIO_NAO_PUBLICAR"] if fonte == "H" else []) + linha)
    return saida.getvalue()


class LeituraENormalizacao(unittest.TestCase):
    def test_normalizacao_oficial(self):
        self.assertEqual(a.normalizar("  NÉBULA, AZUL!\n42  "), "nebula azul 42")
        self.assertEqual(a.normalizar("não SEM 88"), "nao sem 88")

    def test_csv_aspas_virgula_multilinha_e_ids(self):
        linha = [""] * 10
        linha[1] = "Menu da lua Violeta,\ncom opção orbital"
        texto = csv_ficticio(linhas=[linha, [""] * 10])
        fluxo = io.StringIO(texto, newline="")
        registros, n = a.ler_csv(fluxo, "H")
        self.assertEqual((n, len(registros)), (2, 20))
        self.assertEqual(registros[1].id, "H0001:C03")
        self.assertEqual(registros[1].texto, linha[1])
        self.assertEqual(registros[10].id, "H0002:C02")
        self.assertEqual(fluxo.getvalue(), texto)
        self.assertNotIn("METADADO_FICTICIO", repr(registros))

    def test_origem_e_colunas_dependem_da_fonte(self):
        for fonte, origem, primeira in [("H", "humano", 2), ("S", "llm", 1)]:
            registros, _ = a.ler_csv(io.StringIO(csv_ficticio(fonte)), fonte)
            self.assertTrue(all(c.origem == origem for c in registros))
            self.assertEqual(registros[0].coluna, primeira)

    def test_recusa_fonte_ou_identificadores_invalidos(self):
        with self.assertRaises(a.ErroAuditoria):
            a.ler_csv(io.StringIO(""), "desconhecida")
        for kwargs in [{"fonte": "X"}, {"envio": 0}, {"coluna": 0}]:
            with self.assertRaises(a.ErroAuditoria):
                celula("MARCADOR_FICTICIO", **kwargs)

    def test_layout_reordenado_e_largura_errada(self):
        dados = csv_ficticio()
        for invalido in ["", dados.replace(a.PERGUNTAS[1], "cabecalho desconhecido"), dados + "uma,coluna\n"]:
            with self.assertRaises(a.ErroAuditoria):
                a.ler_csv(io.StringIO(invalido), "H")

    def test_csv_malformado_nao_expoe_conteudo(self):
        dados = csv_ficticio() + '"MARCADOR_PRIVADO_SEM_FECHO'
        with self.assertRaisesRegex(a.ErroAuditoria, "^csv_invalido$"):
            a.ler_csv(io.StringIO(dados), "H")

    def test_rejeita_symlink_antes_de_ler(self):
        with patch.object(Path, "is_symlink", return_value=True), patch.object(Path, "read_bytes") as leitura:
            with self.assertRaises(a.ErroAuditoria):
                a.caminho_entrada("H")
            leitura.assert_not_called()


class RotulosEDuplicatas(unittest.TestCase):
    def test_exatas_normalizadas_e_vazias(self):
        cs = [celula("NEBULA, AZUL!"), celula("nebula azul", envio=2),
              celula("NEBULA, AZUL!", fonte="S"), celula("", envio=3), celula("", envio=4)]
        self.assertEqual(a.grupos_duplicados(cs, False), [["H0001:C03", "S0001:C03"]])
        self.assertEqual(a.grupos_duplicados(cs), [["H0001:C03", "H0002:C03", "S0001:C03"]])

    def test_quase_duplicata_e_parafrase_sao_sinais(self):
        cs = [celula("Menu orbital extraordinario violeta"),
              celula("Menu orbital extraordinario violetaa", envio=2),
              celula("custo refeicao nebulosa azul", envio=3),
              celula("azul nebulosa refeicao preco", envio=4)]
        pares = a.sinalizar_proximos(cs)
        self.assertTrue(any(p["quase_duplicata"] for p in pares))
        self.assertTrue(any(p["possivel_parafrase"] for p in pares))
        self.assertNotIn("Menu orbital", json.dumps(pares))
        self.assertTrue(all("nao" in a.normalizar(t) for t in ["NÃO", "não!"]))

    def test_limites_de_proximidade(self):
        for limiar in [0, -0.1, 1.1]:
            with self.assertRaises(a.ErroAuditoria):
                a.sinalizar_proximos([], limiar)

    def test_vazia_marcacao_e_ambiguidade(self):
        for texto, flag in [("", "vazia"), ("???", "sem_texto_normalizado"),
                            ("tal coisa no planeta Violeta", "metarresposta"),
                            ("fragmento lunar isolado", "rotulo_inconclusivo")]:
            analise = a.analisar(celula(texto))
            self.assertFalse(analise.candidata)
            self.assertIn(flag, analise.alertas)

    def test_preco_de_visitante_na_coluna_errada(self):
        r = a.analisar(celula("Preço para visitante do RU de Netuno", rotulo="regras_uso"))
        self.assertEqual(r.sugerido, "valores")
        self.assertIn("diverge_da_coluna", r.alertas)
        self.assertFalse(r.publico()["aprovado"])
        self.assertEqual(r.publico()["revisao_humana"], "pendente")

    def test_negativo_nao_e_horario_do_ru(self):
        r = a.analisar(celula("Horário da biblioteca no asteroide Violeta", rotulo="horarios"))
        self.assertEqual(r.sugerido, "fora_dominio")

    def test_saudacao_nao_transforma_pedido_desconhecido_em_social(self):
        r = a.analisar(celula("Boa noite, quem administra o RU de Saturno?"))
        self.assertIsNone(r.sugerido)
        self.assertIn("rotulo_inconclusivo", r.alertas)

    def test_pergunta_sobre_identidade_do_bot_e_social(self):
        r = a.analisar(celula("Quem criou o robô da estação Violeta?", rotulo=None))
        self.assertEqual(r.sugerido, "chitchat")

    def test_topico_com_erro_nao_vira_social_por_falta_de_match(self):
        r = a.analisar(celula("Opa, cdastro do RU em Io", rotulo="cadastro"))
        self.assertIsNone(r.sugerido)
        self.assertFalse(r.candidata)

    def test_multiplas_intencoes_e_recarga_sem_dominio(self):
        r = a.analisar(celula("Menu e horários do RU de Saturno"))
        self.assertIn("multiplas_intencoes", r.alertas)
        self.assertFalse(r.candidata)
        r = a.analisar(celula("Recarregar cartão de grãos lunares", rotulo="recarga_creditos"))
        self.assertIn("dominio_indefinido", r.alertas)
        self.assertFalse(r.candidata)

    def test_dado_pessoal_ficticio_so_sinaliza(self):
        r = a.analisar(celula("Menu para pessoa@example.invalid na lua"))
        self.assertIn("possivel_dado_pessoal", r.alertas)
        self.assertNotIn("example.invalid", json.dumps(r.publico()))

    def test_distribuicao_prioriza_humano_sem_inflar(self):
        rs = [a.analisar(celula("Menu orbital de Saturno", fonte="S")),
              a.analisar(celula("Menu orbital de Saturno")),
              a.analisar(celula("Horário do RU em Marte", envio=2, rotulo="horarios"))]
        d = a.distribuir(rs)
        self.assertEqual(d["total"], 2)
        self.assertEqual(d["por_origem"], {"humano": 2, "llm": 0})
        self.assertEqual(d["por_classe"]["cardapio"], 1)
        self.assertEqual(d["por_classe"]["horarios"], 1)
        self.assertEqual(d["por_classe"]["cadastro"], 0)

    def test_colunas_conflitantes_nao_sao_aprovacao(self):
        rs = [a.analisar(celula("Menu orbital de Saturno", rotulo=c, coluna=i))
              for i, c in [(3, "cardapio"), (4, "horarios")]]
        marcadas = a.marcar_colunas_conflitantes(rs)
        self.assertTrue(all("colunas_conflitantes" in r.alertas for r in marcadas))
        self.assertTrue(all(r.publico()["aprovado"] is False for r in marcadas))


class ProtocoloCientifico(unittest.TestCase):
    def test_treino_minimos_e_fronteira_dos_20_porcento(self):
        self.assertEqual(sum(a.MIN_TREINO.values()), 550)
        self.assertFalse(a.validar_minimos(a.MIN_TREINO.copy(), 109)["minimos_atendidos"])
        self.assertTrue(a.validar_minimos(a.MIN_TREINO.copy(), 110)["minimos_atendidos"])
        maiores = a.MIN_TREINO | {"cardapio": 100}
        self.assertFalse(a.validar_minimos(maiores, 110)["minimos_atendidos"])
        self.assertTrue(a.validar_minimos(maiores, 120)["minimos_atendidos"])

    def test_teste_requer_todas_humanas_coletadas(self):
        self.assertEqual(sum(a.MIN_TESTE.values()), 160)
        self.assertTrue(a.validar_minimos(a.MIN_TESTE.copy(), 160, "teste")["minimos_atendidos"])
        self.assertFalse(a.validar_minimos(a.MIN_TESTE.copy(), 159, "teste")["minimos_atendidos"])

    def test_minimos_por_classe_e_vazio(self):
        cs = a.MIN_TREINO | {"cardapio": 49}
        self.assertEqual(a.validar_minimos(cs, 120)["faltas"]["cardapio"], 1)
        vazias = dict.fromkeys(a.CLASSES, 0)
        self.assertFalse(a.validar_minimos(vazias, 0)["origem_valida"])

    def test_contagens_invalidas(self):
        for contagens, n in [({}, 0), (a.MIN_TREINO | {"cardapio": -1}, 0),
                             (a.MIN_TREINO, 551), (a.MIN_TREINO, -1)]:
            with self.assertRaises(a.ErroAuditoria):
                a.validar_minimos(contagens, n)

    def test_detecta_sobreposicao_sem_imprimir_texto(self):
        treino = [a.analisar(celula("MENU da NÉBULA!"))]
        teste = [a.analisar(celula("menu da nebula", envio=2))]
        self.assertEqual(a.detectar_sobreposicao(treino, teste), [("H0001:C03", "H0002:C03")])

    def test_componentes_mantem_envios_relacionados_juntos(self):
        rs = [a.analisar(celula("Menu da nebulosa", envio=i)) for i in [1, 3]]
        rs.append(a.analisar(celula("Menu do asteroide", envio=2)))
        self.assertEqual(a.componentes_envios(rs, 3), [[1, 3], [2]])

    def test_divisao_invalida_nao_certifica(self):
        rs = [a.analisar(celula("Menu da nebulosa", envio=i)) for i in [1, 2]]
        plano = a.avaliar_divisao(rs, [1], 2, [])
        self.assertTrue(plano["sobreposicoes_normalizadas"])
        self.assertFalse(plano["viavel_condicionada_a_revisao_e_complemento"])
        self.assertFalse(plano["congelado"])
        with self.assertRaises(a.ErroAuditoria):
            a.avaliar_divisao(rs, [3], 2, [])

    def test_proximidade_so_quarentena_do_lado_treino(self):
        cs = [celula("Menu orbital extraordinario violeta"),
              celula("Menu orbital extraordinario violetaa", envio=2)]
        plano = a.avaliar_divisao([a.analisar(c) for c in cs], [1], 2, a.sinalizar_proximos(cs))
        self.assertEqual(plano["celulas_quarentena_proximidade"], ["H0002:C03"])
        self.assertEqual(plano["humanas_treino"]["total"], 0)
        self.assertEqual(plano["teste_humano"]["total"], 1)

    def test_sinteticas_nunca_entram_na_reserva_humana(self):
        rs = [a.analisar(celula("Menu da estação Violeta")),
              a.analisar(celula("Menu da estação Amarela", fonte="S"))]
        plano = a.avaliar_divisao(rs, [1], 1, [])
        self.assertEqual(plano["teste_humano"]["por_origem"], {"humano": 1, "llm": 0})
        self.assertEqual(plano["humanas_treino"]["total"], 0)

    def test_busca_e_reprodutivel_e_respeita_componentes(self):
        rs = [a.analisar(celula("Menu da nebulosa", envio=i)) for i in [1, 2]]
        rs.append(a.analisar(celula("Menu de Plutao", envio=3)))
        primeiro = a.propor_divisoes(rs, 3, [], tamanhos=(1, 2))
        self.assertEqual(primeiro, a.propor_divisoes(rs, 3, [], tamanhos=(1, 2)))
        for p in primeiro:
            self.assertEqual(1 in p["envios_teste"], 2 in p["envios_teste"])

    def test_plano_explicito_nao_e_substituido_pela_busca(self):
        cs = [celula("Menu orbital da lua Violeta", envio=i) for i in [1, 2]]
        r = a.auditar(cs, 2, envios_teste=(2,))
        self.assertEqual(len(r["divisoes_propostas"]), 1)
        self.assertEqual(r["divisoes_propostas"][0]["envios_teste"], [2])

    def test_interpretacao_dos_envios(self):
        self.assertEqual(a.interpretar_envios("8,5"), (8, 5))
        for invalido in ["", "0", "1,1", "-1", "1,texto", "1, 2"]:
            with self.assertRaises(a.argparse.ArgumentTypeError):
                a.interpretar_envios(invalido)


class PrivacidadeEPreservacao(unittest.TestCase):
    def test_cli_manifesto_deterministico_sem_textos_ou_metadados(self):
        dados = {fonte: csv_ficticio(fonte, [["MARCADOR_TEXTO_FICTICIO"] + [""] * 9]).encode()
                 for fonte in a.FONTES}

        class SomenteLeitura:
            def __init__(self, fonte):
                self.fonte = fonte

            def read_bytes(self):
                return dados[self.fonte]

        anterior = dados.copy()
        saidas = []
        with patch.object(a, "caminho_entrada", side_effect=SomenteLeitura), \
                patch.object(Path, "write_text", side_effect=AssertionError("escrita indevida")), \
                patch.object(Path, "write_bytes", side_effect=AssertionError("escrita indevida")):
            for _ in range(2):
                out = io.StringIO()
                with redirect_stdout(out):
                    self.assertEqual(a.main(["--manifesto"]), 0)
                saidas.append(out.getvalue())
        self.assertEqual(saidas[0], saidas[1])
        self.assertEqual(dados, anterior)
        self.assertNotIn("MARCADOR_TEXTO_FICTICIO", saidas[0])
        self.assertNotIn("METADADO_FICTICIO_NAO_PUBLICAR", saidas[0])
        relatorio = json.loads(saidas[0])
        self.assertTrue(relatorio["entradas_preservadas"])
        self.assertTrue(all(not c["aprovado"] for c in relatorio["celulas"]))

    def test_detecta_entrada_alterada(self):
        class Alterada:
            def read_bytes(self):
                return b"alterado"
        with patch.object(a, "caminho_entrada", return_value=Alterada()):
            with self.assertRaisesRegex(a.ErroAuditoria, "^entrada_alterada_durante_auditoria$"):
                a.conferir_preservacao({"H": b"original"})

    def test_erro_cli_nao_repete_argumento(self):
        out = io.StringIO()
        with redirect_stderr(out), self.assertRaises(SystemExit):
            a.main(["--MARCADOR_PRIVADO_FICTICIO"])
        self.assertNotIn("MARCADOR_PRIVADO_FICTICIO", out.getvalue())

    def test_erro_de_entrada_e_sanitizado(self):
        out = io.StringIO()
        with patch.object(a, "ler_entradas", side_effect=OSError("MARCADOR_PRIVADO_FICTICIO")), redirect_stderr(out):
            self.assertEqual(a.main([]), 2)
        self.assertNotIn("MARCADOR_PRIVADO_FICTICIO", out.getvalue())


def preparar_fixture_revisao(humanas=None, sinteticas=None):
    if humanas is None:
        h = [""] * 10
        h[0] = "Fragmento órfico da lua violeta"
        h[1] = "  Menu orbital, violeta\npara a estação azul  "
        h[4] = "Recarregar cristais da nebulosa"
        humanas = [h]
    if sinteticas is None:
        s = [""] * 10
        s[1] = "Menu do planeta Ocre"
        sinteticas = [s]
    snapshots = {"H": csv_ficticio("H", humanas).encode(), "S": csv_ficticio("S", sinteticas).encode()}
    celulas = []
    for fonte, bruto in snapshots.items():
        cs, _ = a.ler_csv(io.StringIO(bruto.decode(), newline=""), fonte)
        celulas.extend(cs)
    linhas, excluidas = a.preparar_revisao(celulas, snapshots, a.sinalizar_proximos(celulas))
    return celulas, snapshots, linhas, excluidas


def importar_fixture(linhas, esperadas):
    fluxo = io.StringIO(newline="")
    a.escrever_revisao_fluxo(fluxo, linhas)
    fluxo.seek(0)
    return a.importar_revisao_fluxo(fluxo, esperadas)


class RevisaoHumana(unittest.TestCase):
    def setUp(self):
        self.cs, self.snapshots, self.esperadas, self.excluidas = preparar_fixture_revisao()
        self.linhas = [dict(r) for r in self.esperadas]

    def revisar(self, identificador, decisao, rotulo="", uso=""):
        r = next(r for r in self.linhas if r["id_resposta"] == identificador)
        r.update(decisao_humana=decisao, rotulo_revisado=rotulo, uso_autorizado=uso)

    def aplicar(self):
        ds = importar_fixture(self.linhas, self.esperadas)
        return a.aplicar_revisoes([a.analisar(c) for c in self.cs], ds)

    def test_exporta_texto_exato_sem_metadados_e_sem_decisoes(self):
        fluxo = io.StringIO(newline="")
        a.escrever_revisao_fluxo(fluxo, self.linhas)
        self.assertNotIn("METADADO_FICTICIO", fluxo.getvalue())
        fluxo.seek(0)
        rows = list(csv.DictReader(fluxo))
        r = next(r for r in rows if r["id_resposta"] == "H0001:C03")
        self.assertEqual(r["texto_original"], "  Menu orbital, violeta\npara a estação azul  ")
        self.assertTrue(all(r["decisao_humana"] == "pendente" and not r["rotulo_revisado"] for r in rows))
        self.assertEqual(r["id_envio"], "H0001")
        self.assertEqual(r["origem"], "humano")

    def test_pendente_nao_herda_candidatura_automatica(self):
        self.assertGreater(a.distribuir([a.analisar(c) for c in self.cs])["total"], 0)
        revisadas = self.aplicar()
        self.assertEqual(a.distribuir(revisadas)["total"], 0)
        self.assertTrue(all(not r.publico()["aprovado"] for r in revisadas))

    def test_humano_pode_aprovar_exemplo_barrado_pela_heuristica(self):
        c = next(c for c in self.cs if c.id == "H0001:C06")
        self.assertFalse(a.analisar(c).candidata)
        self.revisar(c.id, "aprovar")
        dist = a.distribuir(self.aplicar())
        self.assertEqual(dist["por_classe"]["recarga_creditos"], 1)
        self.assertEqual(dist["por_origem"]["humano"], 1)

    def test_corrigir_exige_decisao_explicita_e_rotulo_valido(self):
        self.revisar("H0001:C02", "corrigir", "cadastro")
        self.assertEqual(a.distribuir(self.aplicar())["por_classe"]["cadastro"], 1)
        self.revisar("H0001:C02", "corrigir", "")
        with self.assertRaises(a.ErroRevisao):
            self.aplicar()

    def test_nao_aprova_rotulo_ausente_sem_correcao(self):
        self.revisar("H0001:C02", "aprovar")
        with self.assertRaises(a.ErroRevisao):
            self.aplicar()

    def test_rejeicao_remove_candidata(self):
        self.revisar("H0001:C03", "rejeitar")
        self.assertEqual(a.distribuir(self.aplicar())["total"], 0)

    def test_rotulos_reservados_e_desconhecidos_sao_recusados(self):
        for invalido in ["dominio", "esclarecer", "humano", "inventado", "cardápio"]:
            self.revisar("H0001:C02", "corrigir", invalido)
            with self.assertRaises(a.ErroRevisao):
                self.aplicar()

    def test_aprovar_nao_troca_rotulo_silenciosamente(self):
        self.revisar("H0001:C03", "aprovar", "horarios")
        with self.assertRaises(a.ErroRevisao):
            self.aplicar()

    def test_identificador_texto_origem_e_versao_sao_imutaveis(self):
        for campo in ["id_resposta", "id_envio", "fonte_original", "origem", "coluna_original",
                      "texto_original", "rotulo_sugerido", "motivo_sinalizacao", "sha256_fonte"]:
            alteradas = [dict(r) for r in self.esperadas]
            alteradas[0][campo] += "ALTERADO"
            with self.assertRaises(a.ErroRevisao):
                importar_fixture(alteradas, self.esperadas)

    def test_nao_remove_espacos_do_original_na_importacao(self):
        r = next(r for r in self.linhas if r["id_resposta"] == "H0001:C03")
        r["texto_original"] = r["texto_original"].strip()
        with self.assertRaises(a.ErroRevisao):
            self.aplicar()

    def test_nao_aceita_linhas_ausentes_ou_repetidas(self):
        for alteradas in [self.linhas[1:], self.linhas + [self.linhas[0]]]:
            with self.assertRaises(a.ErroRevisao):
                importar_fixture(alteradas, self.esperadas)

    def test_ordenacao_da_planilha_nao_muda_ids_ou_resultados(self):
        self.revisar("H0001:C03", "aprovar")
        original = a.distribuir(self.aplicar())
        self.linhas.reverse()
        self.assertEqual(a.distribuir(self.aplicar()), original)

    def test_cabecalho_e_csv_invalidos(self):
        for texto in ["", '"cabecalho sem fim', "texto,rotulo\nx,y\n",
                      ",".join(a.CAMPOS_REVISAO) + '\n"sem fim']:
            with self.assertRaises(a.ErroRevisao):
                a.importar_revisao_fluxo(io.StringIO(texto), self.esperadas)

    def test_alteracao_do_bruto_invalida_revisao(self):
        novos = dict(self.snapshots)
        novos["H"] = novos["H"].replace(b"METADADO_FICTICIO", b"OUTRO_METADADO_FICTICIO")
        atualizadas, _ = a.preparar_revisao(self.cs, novos, [])
        with self.assertRaises(a.ErroRevisao):
            importar_fixture(self.linhas, atualizadas)

    def test_origem_sintetica_nao_vira_humana(self):
        self.revisar("S0001:C02", "aprovar")
        dist = a.distribuir(self.aplicar())
        self.assertEqual(dist["por_origem"], {"humano": 0, "llm": 1})
        for uso in ["teste", "ambos"]:
            self.revisar("S0001:C02", "aprovar", uso=uso)
            with self.assertRaises(a.ErroRevisao):
                self.aplicar()

    def test_destinacao_por_exemplo_e_respeitada_sem_separar_envio(self):
        self.revisar("H0001:C03", "aprovar", uso="treino")
        plano = a.avaliar_divisao(self.aplicar(), [1], 1, [])
        self.assertEqual(plano["teste_humano"]["total"], 0)
        self.assertEqual(plano["humanas_treino"]["total"], 0)
        self.assertEqual(plano["aprovadas_nao_alocadas_por_uso"], ["H0001:C03"])

    def test_decisao_e_uso_invalidos_nao_sao_aceitos(self):
        for decisao, uso in [("aprovacao_auto", ""), ("aprovar", "validacao")]:
            self.revisar("H0001:C03", decisao, uso=uso)
            with self.assertRaises(a.ErroRevisao):
                self.aplicar()

    def test_dados_pessoais_e_formulas_nao_sao_exportados(self):
        h = [""] * 10
        h[:4] = ["Contato pessoa@example.invalid", "Meu nome é Pessoa Imaginária",
                 "=2+2", "Menu da lua anônima"]
        cs, snapshots, linhas, excluidas = preparar_fixture_revisao([h])
        self.assertEqual(len([r for r in linhas if r["origem"] == "humano"]), 1)
        self.assertEqual(len(excluidas["possivel_dado_pessoal"]), 2)
        self.assertEqual(len(excluidas["formula_de_planilha"]), 1)
        self.assertEqual(snapshots["H"], csv_ficticio("H", [h]).encode())

    def test_observacoes_nao_aparecem_no_relatorio(self):
        self.revisar("H0001:C03", "aprovar")
        self.linhas[1]["observacoes_revisao"] = "NOTA_FICTICIA_PRIVADA"
        self.assertNotIn("NOTA_FICTICIA_PRIVADA", json.dumps([r.publico() for r in self.aplicar()]))
        self.linhas[1]["observacoes_revisao"] = "pessoa@example.invalid"
        with self.assertRaises(a.ErroRevisao):
            self.aplicar()

    def test_duplicatas_aprovadas_contam_uma_vez_e_conflitos_sao_recusados(self):
        h1, h2 = [""] * 10, [""] * 10
        h1[1], h2[1] = "Menu da estação turquesa", "MENU DA ESTAÇÃO TURQUESA!"
        cs, _, linhas, _ = preparar_fixture_revisao([h1, h2])
        originais = [dict(r) for r in linhas]
        for r in linhas:
            if r["origem"] == "humano":
                r["decisao_humana"] = "aprovar"
        ds = importar_fixture(linhas, originais)
        revisadas = a.aplicar_revisoes([a.analisar(c) for c in cs], ds)
        self.assertEqual(a.distribuir(revisadas)["por_origem"]["humano"], 1)
        segunda = next(r for r in linhas if r["id_resposta"] == "H0002:C03")
        segunda.update(decisao_humana="corrigir", rotulo_revisado="horarios")
        with self.assertRaises(a.ErroRevisao):
            importar_fixture(linhas, originais)

    def test_arquivo_local_nao_pode_sobrescrever_revisao(self):
        from unittest.mock import Mock
        caminho = Mock()
        caminho.open.side_effect = FileExistsError()
        with patch.object(a, "caminho_revisao_local", return_value=caminho):
            with self.assertRaises(a.ErroRevisao):
                a.exportar_revisao_local(self.linhas)
        caminho.open.assert_called_once_with("x", encoding="utf-8-sig", newline="")

    def test_bloqueio_de_escrita_tem_erro_tecnico_sem_conteudo(self):
        from unittest.mock import Mock
        caminho = Mock()
        caminho.open.side_effect = PermissionError("CONTEUDO_PRIVADO_FICTICIO")
        with patch.object(a, "caminho_revisao_local", return_value=caminho):
            with self.assertRaises(a.ErroRevisao) as erro:
                a.exportar_revisao_local(self.linhas)
        self.assertEqual(erro.exception.codigo, "nao_foi_possivel_gravar_revisao")
        self.assertNotIn("CONTEUDO_PRIVADO_FICTICIO", str(erro.exception))

    def test_revisao_exige_gitignore_e_recusa_symlink(self):
        from types import SimpleNamespace
        with patch.object(Path, "is_symlink", return_value=False), \
                patch.object(a.subprocess, "run", return_value=SimpleNamespace(returncode=1)):
            with self.assertRaises(a.ErroRevisao):
                a.caminho_revisao_local()
        with patch.object(Path, "is_symlink", return_value=True), patch.object(a.subprocess, "run") as git:
            with self.assertRaises(a.ErroRevisao):
                a.caminho_revisao_local()
            git.assert_not_called()

    def test_cli_reconta_somente_decisoes_importadas_sem_textos(self):
        self.revisar("H0001:C06", "aprovar")
        fluxo = io.StringIO(newline="")
        a.escrever_revisao_fluxo(fluxo, self.linhas)
        bruto_revisao = fluxo.getvalue().encode()
        snapshots = self.snapshots

        class Entrada:
            def __init__(self, fonte):
                self.fonte = fonte

            def read_bytes(self):
                return snapshots[self.fonte]

        class Revisao:
            def read_bytes(self):
                return bruto_revisao

        saida = io.StringIO()
        with patch.object(a, "caminho_entrada", side_effect=Entrada), \
                patch.object(a, "caminho_revisao_local", return_value=Revisao()), redirect_stdout(saida):
            self.assertEqual(a.main(["--importar-revisao", "--manifesto", "--envios-teste", "1"]), 0)
        r = json.loads(saida.getvalue())
        self.assertEqual(r["revisao_humana"]["aprovadas_distintas"]["total"], 1)
        self.assertEqual(r["divisoes_propostas"][0]["teste_humano"]["total"], 1)
        self.assertIn("divisoes_automaticas_nao_revisadas", r)
        for linha in self.esperadas:
            self.assertNotIn(linha["texto_original"], saida.getvalue())
        self.assertFalse(r["revisao_humana"]["divisao_aprovada"])


if __name__ == "__main__":
    unittest.main()
