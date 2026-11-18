#!/usr/bin/env python3
"""Auditoria e revisão dos dois brutos, sem formar conjuntos oficiais.

Só usa biblioteca padrão e a função de normalização existente. O manifesto JSON
contém identificadores e sugestões, nunca textos, timestamps ou dados pessoais.
A exportação textual é restrita à planilha privada ignorada, inicialmente pendente.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import re
import sys
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
# Importar chatbot.texto pelo pacote executaria __init__/config e exigiria PyYAML.
# Carregamos somente o arquivo puro já revisado, sem importar LLM ou configuração.
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("rangot_normalizacao_auditoria", RAIZ / "chatbot/texto.py")
_texto = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_texto)
normalizar = _texto.normalizar

VERSAO = "2"
INTENCOES = ("cardapio", "horarios", "valores", "recarga_creditos", "cadastro", "regras_uso")
CLASSES = INTENCOES + ("fora_dominio", "chitchat")
MIN_TREINO = dict.fromkeys(INTENCOES, 50) | {"fora_dominio": 150, "chitchat": 100}
MIN_TESTE = dict.fromkeys(INTENCOES, 15) | {"fora_dominio": 40, "chitchat": 30}
FONTES = {
    "H": ("dados/_brutos/formulario_humano.csv", "humano"),
    "S": ("dados/_brutos/sinteticas_llm.csv", "llm"),
}
# Prefixos públicos das perguntas; falhar se houver troca/reordenação de colunas.
PERGUNTAS = (
    "se pudesse perguntar qualquer coisa sobre o ru",
    "voce quer saber o que vai ter para comer no ru",
    "voce quer descobrir os horarios de almoco ou jantar do ru",
    "voce quer saber quanto custa comer no ru",
    "voce precisa colocar creditos no cartao do ru",
    "voce nunca usou o ru e quer saber como se cadastrar",
    "voce tem alguma duvida sobre o que pode ou nao fazer dentro do ru",
    "agora esqueca o ru voce quer saber o horario da biblioteca da ufms",
    "voce quer saber como recarregar o passe de onibus estudantil",
    "para terminar como voce costuma cumprimentar ou agradecer um chat bot",
)
ROTULOS_COLUNA = (None,) + INTENCOES + ("fora_dominio", "fora_dominio", "chitchat")
PADROES = {
    "cardapio": r"\b(cardap\w*|cardio|menu|vegetarian\w*|vegan\w*|veggie|gluten|sobremesa|proteinas?|lasanha|feijoada|frango|suco|doces?)\b|(?:que|qual|oq|qq|q)\b.*\b(comer|comida|rango|pratos?)\b",
    "horarios": r"\b(horarios?|horas?|hrs?|abre|abrir|aberto|aberta|fecha|fechar|funcionamento)\b|\b(quando|dias)\b.*\b(funciona|servida|servido)\b",
    "valores": r"\b(quanto|qnt|qto|valor\w*|precos?|custa\w*|gratis|graca|gratuidade|gratuito|isencao|desconto|bolsistas?|paga|pagar|cobrado)\b",
    "recarga_creditos": r"\b(recarg\w*|recarreg\w*|creditos?|saldo|pix|debito|pagamento|cobranca|dinheiro)\b",
    "cadastro": r"\b(cadastr\w*|cadast\w*|carteirinha|calouro|identidade estudantil)\b|\b(primeira vez|nunca fui|nunca usei)\b|\b(perdi|roubaram)\b.*\bcartao\b",
    "regras_uso": r"\b(regras?|permitid\w*|proibid\w*|marmita\w*|mochilas?|visitantes?|visita|chinelo|bermuda|bandeja|repetir|talher|roupa)\b|\b(pode|posso)\b.*\b(entrar|levar|fazer|pegar dois|guardar lugar|ficar estudando)\b",
}
EXTERNO = re.compile(r"\b(biblioteca|biblio\w*|livros?|onibus|busao|passe|passagem|cantina|lanchonete\w*|monitoria|complementares|matricula|rematricula)\b|sistema academico|login no siscad")
SOCIAL = re.compile(r"\b(oi+|oie\w*|ola|opa|salve|slv|obrig\w*|brigad\w*|agradec\w*|valeu|vlw|obg|tmj|tchau|robo|osbregueido)\b|bom dia|boa tarde|boa noite|tamo junto|quem criou|e ai")
DEMANDA = re.compile(r"\b(como|qual|quais|quem|onde|quando|porque|pq|oq|qq|preciso|quero|tem|ta|aceita|funciona|lotado|cozinha)\b")
ASSUNTO = re.compile(r"\b(ru|restaurante|refeitorio|bandejao|cartao|refeic\w*|almoco|janta|cafe|comida|pratos?|credit\w*|saldo|recarga|livros?|passe|biblioteca)\b")
META = re.compile(r"^(sim|nao|n|pelo insta|de hoje|eu nao sei p|pergunta rapida|gostaria de saber todas as opcoes)$|tal coisa|nao tenho nenhuma duvida|nao agradeco|normalmente eu so fecho|desperdicio de tokens")
PESSOAL = re.compile(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|\b\d{9,}\b")
BLOQUEIOS = {"vazia", "sem_texto_normalizado", "metarresposta", "rotulo_inconclusivo", "multiplas_intencoes", "possivel_dado_pessoal", "dominio_indefinido"}
ARQUIVO_REVISAO = "dados/_brutos/revisao_humana.csv"
CAMPOS_REVISAO = ("id_resposta", "id_envio", "fonte_original", "origem", "coluna_original",
                  "texto_original", "rotulo_sugerido", "motivo_sinalizacao", "sha256_fonte",
                  "rotulo_revisado", "decisao_humana", "uso_autorizado", "observacoes_revisao")
EDITAVEIS_REVISAO = {"rotulo_revisado", "decisao_humana", "uso_autorizado", "observacoes_revisao"}
DECISOES = {"", "pendente", "aprovar", "corrigir", "rejeitar"}
USOS = {"", "treino", "teste", "ambos"}
AUTOIDENTIFICACAO = re.compile(r"\b(me chamo|meu nome e|meu cpf|meu rga|meu telefone|meu email)\b")


class ErroAuditoria(ValueError):
    """Mensagens exclusivamente técnicas: nunca incluir conteúdo das entradas."""


class ErroRevisao(ErroAuditoria):
    def __init__(self, codigo, identificador=None):
        super().__init__(codigo)
        self.codigo = codigo
        self.identificador = identificador


@dataclass(frozen=True)
class Celula:
    fonte: str
    envio: int
    coluna: int
    texto: str = field(repr=False)
    rotulo_coluna: str | None = None

    def __post_init__(self):
        if self.fonte not in FONTES or self.envio < 1 or self.coluna < 1:
            raise ErroAuditoria("identificador_invalido")

    @property
    def id(self):
        return f"{self.fonte}{self.envio:04d}:C{self.coluna:02d}"

    @property
    def origem(self):
        return FONTES[self.fonte][1]

    @property
    def normalizado(self):
        return normalizar(self.texto)


@dataclass(frozen=True)
class Analise:
    celula: Celula = field(repr=False)
    sugerido: str | None
    evidencias: tuple[str, ...]
    alertas: tuple[str, ...]

    @property
    def candidata(self):
        return self.sugerido in CLASSES and not BLOQUEIOS.intersection(self.alertas)

    def publico(self):
        return {
            "id": self.celula.id, "origem": self.celula.origem,
            "envio": self.celula.envio, "coluna": self.celula.coluna,
            "rotulo_coluna": self.celula.rotulo_coluna,
            "rotulo_sugerido": self.sugerido, "evidencias": list(self.evidencias),
            "alertas": list(self.alertas), "candidata_provisoria": self.candidata,
            "revisao_humana": "pendente", "aprovado": False,
        }


@dataclass(frozen=True)
class AnaliseRevisada(Analise):
    decisao_humana: str = "pendente"
    uso_autorizado: str = ""
    rotulo_automatico: str | None = None

    @property
    def candidata(self):
        # Revisor pode superar heurísticas, nunca ausência de texto ou privacidade.
        return (self.decisao_humana in {"aprovar", "corrigir"}
                and self.sugerido in CLASSES and bool(self.celula.normalizado)
                and not impedimentos_revisao(self.celula.texto))

    def publico(self):
        resultado = super().publico()
        resultado.update(rotulo_sugerido=self.rotulo_automatico,
                         rotulo_revisado=self.sugerido if self.candidata else None,
                         decisao_humana=self.decisao_humana,
                         uso_autorizado=self.uso_autorizado,
                         revisao_humana=("pendente" if self.decisao_humana == "pendente"
                                         else "decisao_declarada_no_csv"), aprovado=self.candidata)
        return resultado


def permitida_no_uso(analise, uso):
    return analise.candidata and getattr(analise, "uso_autorizado", "") in {"", "ambos", uso}


def impedimentos_revisao(texto):
    motivos = []
    if not texto.strip():
        motivos.append("vazia")
    if PESSOAL.search(texto) or AUTOIDENTIFICACAO.search(normalizar(texto)):
        motivos.append("possivel_dado_pessoal")
    if texto.lstrip().startswith(("=", "+", "-", "@")):
        motivos.append("formula_de_planilha")
    return motivos


def textos_originais(snapshots):
    """Valores lógicos exatos do CSV, incluindo espaços; nunca o metadado temporal."""
    originais = {}
    for fonte, bruto in snapshots.items():
        deslocamento = 1 if fonte == "H" else 0
        leitor = csv.reader(io.StringIO(bruto.decode("utf-8-sig"), newline=""), strict=True)
        next(leitor)
        for envio, linha in enumerate(leitor, 1):
            for j in range(deslocamento, len(linha)):
                originais[f"{fonte}{envio:04d}:C{j + 1:02d}"] = linha[j]
    return originais


def preparar_revisao(celulas, snapshots, proximos):
    originais = textos_originais(snapshots)
    hashes = {f: hashlib.sha256(b).hexdigest() for f, b in snapshots.items()}
    relacionados = defaultdict(set)
    for tipo, grupos in (("duplicata_exata", grupos_duplicados(celulas, False)),
                         ("duplicata_normalizada", grupos_duplicados(celulas))):
        for grupo in grupos:
            for identificador in grupo:
                relacionados[identificador].add(tipo + ":" + ",".join(grupo))
    for par in proximos:
        tipos = (["quase_duplicata"] if par["quase_duplicata"] else [])
        if par["possivel_parafrase"]:
            tipos.append("possivel_parafrase")
        for esquerda, direita in ((par["a"], par["b"]), (par["b"], par["a"])):
            for identificador in esquerda:
                for tipo in tipos:
                    relacionados[identificador].add(tipo + ":" + ",".join(direita))
    linhas, excluidas = [], defaultdict(list)
    analises = marcar_colunas_conflitantes([analisar(c) for c in celulas])
    for analise in analises:
        c = analise.celula
        original = originais[c.id]
        bloqueios = impedimentos_revisao(original)
        if bloqueios:
            for motivo in bloqueios:
                excluidas[motivo].append(c.id)
            continue
        motivos = set(analise.alertas) | relacionados[c.id]
        if not motivos:
            motivos.add("conferir_texto_rotulo_e_origem")
        linhas.append({
            "id_resposta": c.id, "id_envio": f"{c.fonte}{c.envio:04d}",
            "fonte_original": FONTES[c.fonte][0], "origem": c.origem,
            "coluna_original": str(c.coluna), "texto_original": original,
            "rotulo_sugerido": analise.sugerido or "",
            "motivo_sinalizacao": ";".join(sorted(motivos)), "sha256_fonte": hashes[c.fonte],
            "rotulo_revisado": "", "decisao_humana": "pendente",
            "uso_autorizado": "", "observacoes_revisao": "",
        })
    return linhas, dict(sorted(excluidas.items()))


def escrever_revisao_fluxo(fluxo, linhas):
    escritor = csv.DictWriter(fluxo, fieldnames=CAMPOS_REVISAO, lineterminator="\n")
    escritor.writeheader()
    escritor.writerows(linhas)


def importar_revisao_fluxo(fluxo, esperadas):
    esperadas = {r["id_resposta"]: r for r in esperadas}
    leitor = csv.DictReader(fluxo, strict=True)
    try:
        cabecalho = leitor.fieldnames
    except (csv.Error, UnicodeError) as exc:
        raise ErroRevisao("csv_revisao_invalido") from exc
    if cabecalho != list(CAMPOS_REVISAO):
        raise ErroRevisao("cabecalho_revisao_invalido")
    decisoes, rotulos = {}, defaultdict(set)
    try:
        for linha in leitor:
            identificador = linha.get("id_resposta")
            if identificador not in esperadas or identificador in decisoes:
                raise ErroRevisao("ids_revisao_desconhecidos_ou_repetidos")
            if None in linha or any(v is None for v in linha.values()):
                raise ErroRevisao("largura_revisao_invalida", identificador)
            original = esperadas[identificador]
            if any(linha[c] != original[c] for c in CAMPOS_REVISAO if c not in EDITAVEIS_REVISAO):
                raise ErroRevisao("integridade_revisao_violada", identificador)
            decisao = linha["decisao_humana"].strip() or "pendente"
            revisado = linha["rotulo_revisado"].strip()
            uso = linha["uso_autorizado"].strip()
            if decisao not in DECISOES or uso not in USOS:
                raise ErroRevisao("decisao_ou_uso_invalido", identificador)
            if revisado and revisado not in CLASSES:
                raise ErroRevisao("rotulo_revisado_invalido", identificador)
            if original["origem"] == "llm" and uso in {"teste", "ambos"}:
                raise ErroRevisao("sintetica_nao_pode_ser_teste", identificador)
            if impedimentos_revisao(linha["observacoes_revisao"].strip() or "observacao vazia"):
                raise ErroRevisao("observacao_inadequada", identificador)
            if decisao == "aprovar":
                if original["rotulo_sugerido"] not in CLASSES:
                    raise ErroRevisao("aprovacao_exige_rotulo_sugerido_ou_correcao", identificador)
                if revisado and revisado != original["rotulo_sugerido"]:
                    raise ErroRevisao("troca_de_rotulo_exige_corrigir", identificador)
                revisado = original["rotulo_sugerido"]
            if decisao == "corrigir" and not revisado:
                raise ErroRevisao("correcao_exige_rotulo", identificador)
            if decisao in {"aprovar", "corrigir"}:
                if not normalizar(original["texto_original"]):
                    raise ErroRevisao("sem_texto_classificavel", identificador)
                rotulos[normalizar(original["texto_original"])].add(revisado)
                if len(rotulos[normalizar(original["texto_original"])]) > 1:
                    raise ErroRevisao("duplicatas_com_rotulos_revisados_conflitantes", identificador)
            # Não carregar texto livre de observação para os relatórios públicos.
            decisoes[identificador] = {"decisao": decisao, "rotulo": revisado, "uso": uso}
    except (csv.Error, UnicodeError) as exc:
        raise ErroRevisao("csv_revisao_invalido") from exc
    if set(decisoes) != set(esperadas):
        raise ErroRevisao("revisao_com_linhas_ausentes")
    return decisoes


def aplicar_revisoes(analises, decisoes):
    return [AnaliseRevisada(a.celula, decisoes.get(a.celula.id, {}).get("rotulo") or None,
                           a.evidencias, a.alertas,
                           decisoes.get(a.celula.id, {}).get("decisao", "pendente"),
                           decisoes.get(a.celula.id, {}).get("uso", ""), a.sugerido)
            for a in analises]


def resumir_revisao(linhas, decisoes=None):
    decisoes = decisoes or {}
    pendentes = {c: {"humano": 0, "llm": 0} for c in CLASSES + ("sem_rotulo",)}
    estados = Counter()
    for linha in linhas:
        d = decisoes.get(linha["id_resposta"], {}).get("decisao", "pendente")
        estados[d] += 1
        if d == "pendente":
            c = linha["rotulo_sugerido"] or "sem_rotulo"
            pendentes[c][linha["origem"]] += 1
    return {"linhas": len(linhas), "decisoes": dict(sorted(estados.items())),
            "pendentes_por_rotulo_sugerido_e_origem": pendentes}


def caminho_revisao_local():
    p = RAIZ
    for parte in Path(ARQUIVO_REVISAO).parts:
        p = p / parte
        if p.is_symlink():
            raise ErroRevisao("revisao_simbolica_nao_permitida")
    ignorado = subprocess.run(["git", "-C", str(RAIZ), "check-ignore", "-q", "--", ARQUIVO_REVISAO],
                             capture_output=True, check=False)
    if ignorado.returncode != 0:
        raise ErroRevisao("revisao_deve_estar_ignorada_e_nao_versionada")
    return p


def exportar_revisao_local(linhas):
    caminho = caminho_revisao_local()
    try:
        # Exclusivo: não sobrescrever trabalho humano existente, nem um symlink.
        with caminho.open("x", encoding="utf-8-sig", newline="") as fluxo:
            escrever_revisao_fluxo(fluxo, linhas)
    except FileExistsError as exc:
        raise ErroRevisao("revisao_ja_existe_nao_sobrescrever") from exc
    except OSError as exc:
        raise ErroRevisao("nao_foi_possivel_gravar_revisao") from exc


def ler_revisao_local(linhas):
    bruto = caminho_revisao_local().read_bytes()
    fluxo = io.StringIO(bruto.decode("utf-8-sig"), newline="")
    return importar_revisao_fluxo(fluxo, linhas), hashlib.sha256(bruto).hexdigest()


def ler_csv(fluxo, fonte):
    """Posições 1-based no CSV original; envio é registro lógico, não linha física."""
    if fonte not in FONTES:
        raise ErroAuditoria("fonte_invalida")
    deslocamento = 1 if fonte == "H" else 0
    leitor = csv.reader(fluxo, strict=True)
    try:
        cabecalho = next(leitor)
        if len(cabecalho) != 10 + deslocamento:
            raise ErroAuditoria("layout_incompativel")
        if deslocamento and normalizar(cabecalho[0]) != "carimbo de data hora":
            raise ErroAuditoria("layout_incompativel")
        for atual, esperado in zip(cabecalho[deslocamento:], PERGUNTAS):
            if not normalizar(atual).startswith(esperado):
                raise ErroAuditoria("layout_incompativel")
        celulas = []
        envios = 0
        for envios, linha in enumerate(leitor, 1):
            if len(linha) != len(cabecalho):
                raise ErroAuditoria("largura_incompativel")
            for j, rotulo in enumerate(ROTULOS_COLUNA):
                celulas.append(Celula(fonte, envios, j + deslocamento + 1,
                                     linha[j + deslocamento].strip(), rotulo))
        return celulas, envios
    except (StopIteration, csv.Error, UnicodeError) as exc:
        raise ErroAuditoria("csv_invalido") from exc


def caminho_entrada(fonte):
    """Allowlist fixa e rejeição de symlinks antes de abrir qualquer entrada."""
    p = RAIZ
    for parte in Path(FONTES[fonte][0]).parts:
        p = p / parte
        if p.is_symlink():
            raise ErroAuditoria("entrada_simbolica_nao_permitida")
    return p


def ler_entradas():
    celulas, metadados, snapshots = [], {}, {}
    for fonte in FONTES:
        caminho = caminho_entrada(fonte)
        bruto = caminho.read_bytes()
        snapshots[fonte] = bruto
        registros, n = ler_csv(io.StringIO(bruto.decode("utf-8-sig"), newline=""), fonte)
        celulas.extend(registros)
        metadados[fonte] = {"origem": FONTES[fonte][1], "envios": n,
                            "sha256_entrada": hashlib.sha256(bruto).hexdigest()}
    return celulas, metadados, snapshots


def conferir_preservacao(snapshots):
    for fonte, anterior in snapshots.items():
        if caminho_entrada(fonte).read_bytes() != anterior:
            raise ErroAuditoria("entrada_alterada_durante_auditoria")


def analisar(celula):
    t = celula.normalizado
    alertas = set()
    if not celula.texto:
        alertas.add("vazia")
    if not t:
        alertas.add("sem_texto_normalizado")
    if META.search(t):
        alertas.add("metarresposta")
    if PESSOAL.search(celula.texto):
        alertas.add("possivel_dado_pessoal")
    temas = {c for c, padrao in PADROES.items() if re.search(padrao, t)}
    # Preço de visitante não é automaticamente uma regra de entrada.
    if "valores" in temas and re.search(r"visitante|visita", t) and not re.search(r"entrar|levar|regras", t):
        temas.discard("regras_uso")
    # O preço da recarga é tópico de pagamento; não confundir com preço da refeição.
    if "recarga_creditos" in temas and re.search(r"recarg|recarreg|saldo|pix|debito", t):
        temas.discard("valores")
    externo = bool(EXTERNO.search(t))
    ru = bool(re.search(r"\b(ru|r u|bandejao|refeitorio|restaurante universitario)\b", t))
    if externo:
        if ru and temas:
            alertas.add("multiplas_intencoes")
        sugerido, evidencias = "fora_dominio", ("fora_dominio",)
    elif len(temas) == 1:
        sugerido = next(iter(temas))
        evidencias = (sugerido,)
        if sugerido == "recarga_creditos" and not ru:
            alertas.add("dominio_indefinido")
    elif temas:
        sugerido, evidencias = None, tuple(sorted(temas))
        alertas.add("multiplas_intencoes")
    elif SOCIAL.search(t) and ((not DEMANDA.search(t) and not ASSUNTO.search(t))
                               or re.search(r"quem criou|voce e (um )?robo", t)):
        sugerido, evidencias = "chitchat", ("chitchat",)
    else:
        sugerido, evidencias = None, ()
        alertas.add("rotulo_inconclusivo")
    if celula.rotulo_coluna and sugerido and celula.rotulo_coluna != sugerido:
        alertas.add("diverge_da_coluna")
    if len(t.split()) < 3 and sugerido != "chitchat":
        alertas.add("texto_curto_revisar")
    if "/" in celula.texto or "\\n" in celula.texto:
        alertas.add("alternativas_ou_marcacao_revisar")
    return Analise(celula, sugerido, evidencias, tuple(sorted(alertas)))


def grupos_duplicados(celulas, normalizados=True):
    grupos = defaultdict(list)
    for c in celulas:
        chave = c.normalizado if normalizados else c.texto
        if chave:
            grupos[chave].append(c.id)
    return sorted((sorted(ids) for ids in grupos.values() if len(ids) > 1))


_CANON = {"q": "que", "hrs": "horario", "horas": "horario", "hr": "horario",
          "preco": "custo", "valor": "custo", "custa": "custo", "qnt": "quanto",
          "recarregar": "recarga", "recarrego": "recarga", "busao": "onibus"}
_FUNCIONAIS = set("o a os as de do da dos das e em no na nos nas por para pra pro que qual como meu minha um uma eu voce".split())


def sinalizar_proximos(celulas, limiar=0.92):
    """Sinais lexicais, não equivalência semântica; números/negações são preservados."""
    if not 0 < limiar <= 1:
        raise ErroAuditoria("limiar_invalido")
    grupos = defaultdict(list)
    for c in celulas:
        if c.normalizado:
            grupos[c.normalizado].append(c.id)
    textos = sorted(grupos)
    tokens = [{_CANON.get(w, w) for w in t.split() if w not in _FUNCIONAIS} for t in textos]
    pares = []
    for i, a in enumerate(textos):
        for j in range(i + 1, len(textos)):
            b = textos[j]
            razao = 2 * min(len(a), len(b)) / (len(a) + len(b))
            quase, similaridade = False, 0.0
            if min(len(a), len(b)) >= 20 and razao >= limiar:
                comparador = SequenceMatcher(None, a, b, autojunk=False)
                if comparador.quick_ratio() >= limiar:
                    similaridade = comparador.ratio()
                    quase = similaridade >= limiar
            uniao = tokens[i] | tokens[j]
            comuns = tokens[i] & tokens[j]
            jaccard = len(comuns) / len(uniao) if uniao else 0.0
            parafrase = len(comuns) >= 3 and jaccard >= 0.8
            if quase or parafrase:
                pares.append({"a": sorted(grupos[a]), "b": sorted(grupos[b]),
                              "quase_duplicata": quase, "possivel_parafrase": parafrase,
                              "similaridade_caracteres": round(similaridade, 6) if quase else None,
                              "jaccard_lexical": round(jaccard, 6)})
    return pares


def unicos(analises):
    # Priorizar procedência humana já informada em colisões entre fontes.
    vistos = {}
    for a in sorted(analises, key=lambda x: x.celula.id):
        if a.candidata:
            vistos.setdefault(a.celula.normalizado, a)
    return list(vistos.values())


def distribuir(analises):
    registros = unicos(analises)
    return {"total": len(registros),
            "por_classe": {c: sum(a.sugerido == c for a in registros) for c in CLASSES},
            "por_origem": {o: sum(a.celula.origem == o for a in registros) for o in ("humano", "llm")}}


def validar_minimos(contagens, humanas, tipo="treino"):
    if tipo not in {"treino", "teste"} or set(contagens) != set(CLASSES):
        raise ErroAuditoria("contagens_invalidas")
    if any(not isinstance(n, int) or n < 0 for n in contagens.values()):
        raise ErroAuditoria("contagens_invalidas")
    total = sum(contagens.values())
    if not isinstance(humanas, int) or not 0 <= humanas <= total:
        raise ErroAuditoria("contagem_humana_invalida")
    minimos = MIN_TREINO if tipo == "treino" else MIN_TESTE
    faltas = {c: max(0, minimos[c] - contagens[c]) for c in CLASSES}
    origem_ok = humanas * 5 >= total if tipo == "treino" else humanas == total
    return {"faltas": faltas, "total": total,
            "proporcao_humana": humanas / total if total else 0.0,
            "origem_valida": bool(total and origem_ok),
            "minimos_atendidos": not any(faltas.values()) and bool(total and origem_ok)}


def detectar_sobreposicao(treino, teste):
    t = defaultdict(list)
    for a in treino:
        if a.celula.normalizado:
            t[a.celula.normalizado].append(a.celula.id)
    return sorted({(i, a.celula.id) for a in teste if a.celula.normalizado
                   for i in t.get(a.celula.normalizado, [])})


def marcar_colunas_conflitantes(analises):
    sugestoes = defaultdict(set)
    for a in analises:
        if a.celula.normalizado and a.celula.rotulo_coluna:
            sugestoes[a.celula.normalizado].add(a.celula.rotulo_coluna)
    return [Analise(a.celula, a.sugerido, a.evidencias,
                    tuple(sorted(set(a.alertas) | {"colunas_conflitantes"})))
            if len(sugestoes[a.celula.normalizado]) > 1 else a for a in analises]


def componentes_envios(humanos, n_envios):
    pais = list(range(n_envios + 1))

    def raiz(i):
        while pais[i] != i:
            pais[i] = pais[pais[i]]
            i = pais[i]
        return i

    vistos = {}
    for a in humanos:
        if not a.candidata:
            continue
        anterior = vistos.setdefault(a.celula.normalizado, a.celula.envio)
        pais[raiz(a.celula.envio)] = raiz(anterior)
    grupos = defaultdict(list)
    for i in range(1, n_envios + 1):
        grupos[raiz(i)].append(i)
    return sorted(grupos.values())


def avaliar_divisao(analises, envios_teste, n_envios, proximos):
    teste_ids = set(envios_teste)
    if not teste_ids <= set(range(1, n_envios + 1)):
        raise ErroAuditoria("envios_invalidos")
    humanos = [a for a in analises if a.celula.fonte == "H" and a.candidata]
    teste = [a for a in humanos if a.celula.envio in teste_ids and permitida_no_uso(a, "teste")]
    treino_h = [a for a in humanos if a.celula.envio not in teste_ids and permitida_no_uso(a, "treino")]
    ids_teste = {a.celula.id for a in teste}
    todos_h = {a.celula.normalizado for a in analises if a.celula.fonte == "H" and a.celula.normalizado}
    ids_treino = {a.celula.id for a in analises if a.candidata and (
        (a.celula.fonte == "H" and a.celula.envio not in teste_ids and permitida_no_uso(a, "treino")) or
        (a.celula.fonte == "S" and a.celula.normalizado not in todos_h and permitida_no_uso(a, "treino")))}
    retirar, parafrases = set(), 0
    for p in proximos:
        lados = (set(p["a"]), set(p["b"]))
        for esquerda, direita in (lados, lados[::-1]):
            if esquerda & ids_teste and direita & ids_treino:
                if p["quase_duplicata"]:
                    retirar.update(direita & ids_treino)
                elif p["possivel_parafrase"]:
                    parafrases += 1
    treino_h = [a for a in treino_h if a.celula.id not in retirar]
    sinteticos = [a for a in analises if a.celula.fonte == "S" and permitida_no_uso(a, "treino")
                  and a.celula.normalizado not in todos_h and a.celula.id not in retirar]
    h, s, t = distribuir(treino_h), distribuir(sinteticos), distribuir(teste)
    capacidade = {c: h["por_classe"][c] + s["por_classe"][c] for c in CLASSES}
    complemento = {c: max(0, MIN_TREINO[c] - capacidade[c]) for c in CLASSES}
    h_planejadas = sum(min(h["por_classe"][c], MIN_TREINO[c]) for c in CLASSES)
    proporcao = h_planejadas / sum(MIN_TREINO.values())
    sobreposicoes = detectar_sobreposicao(treino_h + sinteticos, teste)
    teste_minimos = validar_minimos(t["por_classe"], t["total"], "teste")
    return {
        "envios_teste": sorted(teste_ids),
        "envios_treino": sorted(set(range(1, n_envios + 1)) - teste_ids),
        "humanas_treino": h, "teste_humano": t, "estoque_sintetico": s,
        "novas_sinteticas_necessarias": complemento,
        "alvo_treino": sum(MIN_TREINO.values()),
        "humanas_planejadas_no_alvo": h_planejadas,
        "proporcao_humana_planejada": proporcao,
        "humanas_adicionais_necessarias_no_alvo": max(0, (sum(MIN_TREINO.values()) + 4) // 5 - h_planejadas),
        "minimos_treino_projetados_apos_complemento": validar_minimos(MIN_TREINO.copy(), h_planejadas),
        "teste_minimos": teste_minimos,
        "sobreposicoes_normalizadas": [list(p) for p in sobreposicoes],
        "aprovadas_nao_alocadas_por_uso": sorted(a.celula.id for a in humanos
            if not permitida_no_uso(a, "teste" if a.celula.envio in teste_ids else "treino")),
        "celulas_quarentena_proximidade": sorted(retirar),
        "sinais_parafrase_a_revisar": parafrases,
        "viavel_condicionada_a_revisao_e_complemento": teste_minimos["minimos_atendidos"] and h_planejadas * 5 >= sum(MIN_TREINO.values()) and not sobreposicoes,
        "revisao_humana": "pendente", "congelado": False,
    }


def propor_divisoes(analises, n_envios, proximos, tamanhos=(29, 30, 31), largura=3):
    """Busca limitada e determinística; ausência de solução não prova inviabilidade."""
    humanos = [a for a in analises if a.celula.fonte == "H"]
    componentes = componentes_envios(humanos, n_envios)
    zeros = (0,) * len(CLASSES)
    estados = {(0, 0): [(zeros, ())]}
    maximo = min(max(tamanhos), n_envios)

    def ordem(estado):
        counts, ids = estado
        cobertura = sum(min(counts[k], MIN_TESTE[c]) for k, c in enumerate(CLASSES))
        return (-cobertura, sum(counts), ids)

    for grupo in componentes:
        dist = distribuir([a for a in humanos if a.celula.envio in grupo
                           and permitida_no_uso(a, "teste")])["por_classe"]
        novos = defaultdict(list)
        for (n, social), candidatos in estados.items():
            novos[n, social].extend(candidatos)
            if n + len(grupo) <= maximo:
                for counts, ids in candidatos:
                    vec = tuple(counts[k] + dist[c] for k, c in enumerate(CLASSES))
                    chave = (n + len(grupo), min(vec[-1], MIN_TESTE["chitchat"] + 2))
                    novos[chave].append((vec, tuple(sorted(ids + tuple(grupo)))))
        estados = {k: sorted(set(v), key=ordem)[:largura] for k, v in novos.items()}
    resultados = []
    for tamanho in tamanhos:
        candidatos = [v for (n, _), vv in estados.items() if n == tamanho for v in vv]
        # Avaliar somente os melhores limites lexicais; não otimiza nenhum modelo.
        candidatos.sort(key=ordem)
        planos = [avaliar_divisao(analises, ids, n_envios, proximos) for _, ids in candidatos[:12]]
        if planos:
            planos.sort(key=lambda p: (
                not p["viavel_condicionada_a_revisao_e_complemento"],
                sum(p["teste_minimos"]["faltas"].values()),
                -min(p["teste_humano"]["por_classe"]["chitchat"], 32),
                -p["humanas_planejadas_no_alvo"], p["envios_teste"]))
            resultados.append(planos[0])
    return resultados


def auditar(celulas, n_envios, limiar=0.92, envios_teste=None):
    analises = marcar_colunas_conflitantes([analisar(c) for c in celulas])
    proximos = sinalizar_proximos(celulas, limiar)
    resumos = {}
    for fonte in FONTES:
        cs = [c for c in celulas if c.fonte == fonte]
        nao_vazias = [c for c in cs if c.texto]
        resumos[fonte] = {
            "celulas": len(cs), "preenchidas": len(nao_vazias),
            "unicas_exatas": len({c.texto for c in nao_vazias}),
            "unicas_normalizadas": len({c.normalizado for c in nao_vazias}),
            "candidatas_automaticas": distribuir([a for a in analises if a.celula.fonte == fonte]),
        }
    exatas, normalizadas = grupos_duplicados(celulas, False), grupos_duplicados(celulas)
    conjunto_h = {c.normalizado for c in celulas if c.fonte == "H" and c.normalizado}
    conjunto_s = {c.normalizado for c in celulas if c.fonte == "S" and c.normalizado}
    return {
        "versao": VERSAO, "natureza": "auditoria_sem_aprovacao_humana",
        "parametros": {"limiar_caracteres": limiar, "jaccard_lexical": 0.8,
                       "busca": "beam_deterministica", "largura": 3},
        "resumo": resumos,
        "alertas": dict(sorted(Counter(s for a in analises for s in a.alertas).items())),
        "duplicatas_exatas": exatas, "duplicatas_normalizadas": normalizadas,
        "intersecao_normalizada_fontes": len(conjunto_h & conjunto_s),
        "proximidades": proximos,
        "divisoes_propostas": (propor_divisoes(analises, n_envios, proximos) if envios_teste is None
                               else [avaliar_divisao(analises, envios_teste, n_envios, proximos)]),
        "celulas": [a.publico() for a in analises],
    }


class ParserSeguro(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, '{"erro":"argumentos_invalidos"}\n')


def interpretar_envios(valor):
    if not re.fullmatch(r"[1-9]\d*(,[1-9]\d*)*", valor):
        raise argparse.ArgumentTypeError("envios_invalidos")
    ids = tuple(map(int, valor.split(",")))
    if len(set(ids)) != len(ids):
        raise argparse.ArgumentTypeError("envios_repetidos")
    return ids


def main(argv=None):
    parser = ParserSeguro(description=__doc__)
    parser.add_argument("--manifesto", action="store_true", help="JSON completo sem textos, somente em stdout")
    parser.add_argument("--envios-teste", type=interpretar_envios,
                        help="simular IDs de envio separados por virgula; nao aprova nem congela")
    revisao = parser.add_mutually_exclusive_group()
    revisao.add_argument("--exportar-revisao", action="store_true", help="criar planilha local ignorada, sem sobrescrever")
    revisao.add_argument("--importar-revisao", action="store_true", help="validar decisoes declaradas na planilha local")
    args = parser.parse_args(argv)
    try:
        celulas, fontes, snapshots = ler_entradas()
        relatorio = auditar(celulas, fontes["H"]["envios"], envios_teste=args.envios_teste)
        conferir_preservacao(snapshots)
        if args.exportar_revisao or args.importar_revisao:
            linhas, excluidas = preparar_revisao(celulas, snapshots, relatorio["proximidades"])
            relatorio["revisao_humana"] = resumir_revisao(linhas)
            relatorio["revisao_humana"]["arquivo_local"] = ARQUIVO_REVISAO
            relatorio["revisao_humana"]["excluidas_por_motivo"] = {k: len(v) for k, v in excluidas.items()}
            if args.exportar_revisao:
                exportar_revisao_local(linhas)
            else:
                decisoes, digest = ler_revisao_local(linhas)
                analises = marcar_colunas_conflitantes([analisar(c) for c in celulas])
                revisadas = aplicar_revisoes(analises, decisoes)
                relatorio["revisao_humana"].update(resumir_revisao(linhas, decisoes))
                relatorio["revisao_humana"]["sha256_revisao"] = digest
                relatorio["revisao_humana"]["aprovadas_distintas"] = distribuir(revisadas)
                relatorio["revisao_humana"]["divisao_aprovada"] = False
                relatorio["divisoes_automaticas_nao_revisadas"] = relatorio["divisoes_propostas"]
                relatorio["divisoes_propostas"] = (
                    propor_divisoes(revisadas, fontes["H"]["envios"], relatorio["proximidades"])
                    if args.envios_teste is None else [avaliar_divisao(
                        revisadas, args.envios_teste, fontes["H"]["envios"], relatorio["proximidades"])])
                relatorio["celulas"] = [a.publico() for a in revisadas]
                relatorio["natureza"] = "auditoria_com_decisoes_declaradas_no_csv"
            conferir_preservacao(snapshots)
        relatorio["fontes"] = fontes
        relatorio["entradas_preservadas"] = True
        relatorio["sha256_codigo"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        relatorio["sha256_normalizador"] = hashlib.sha256((RAIZ / "chatbot/texto.py").read_bytes()).hexdigest()
        if not args.manifesto:
            for chave in ("celulas", "duplicatas_exatas", "duplicatas_normalizadas", "proximidades"):
                relatorio[chave + "_quantidade"] = len(relatorio.pop(chave))
        print(json.dumps(relatorio, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    except ErroRevisao as exc:
        print(json.dumps({"erro": exc.codigo, "id_resposta": exc.identificador}), file=sys.stderr)
        return 2
    except (ErroAuditoria, OSError, UnicodeError):
        print('{"erro":"auditoria_nao_concluida_entradas_ou_layout_invalidos"}', file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
