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
import os
import re
import sys
import subprocess
import tempfile
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

VERSAO = "5"
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
PRIVADOS = {
    "formulario_humano.csv", "formulario_humano_novo.csv", "formulario_humano_backup_48.csv",
    "revisao_humana.csv", "revisao_humana_backup_1711.csv", "sinteticas_llm.csv",
    "migracao_48_67.json", "triagem_semantica_67.json", "plano_curadoria_67.json",
    "revisao_prioritaria.csv", "revisao_humana_67_preparada.csv", "migracao_48_67_preparada.json",
    "revisao_prioritaria_backup_07a.csv", "revisao_humana_backup_07a.csv",
    "plano_curadoria_67_backup_07a.json", "auditoria_delegada_07a.json",
    "ratificacao_07b.json", "manifesto_conjuntos_07b.json", "treino_parcial_07b.csv",
    "candidatas_sinteticas_07b.csv", "busca_sinteticas_07b.json",
    "pacote_treinamento_07b/treino_autorizado.csv", "pacote_treinamento_07b/INSTRUCOES.md",
}
DEFINICOES = {"cardapio": "cardápio do dia ou da semana",
    "horarios": "horários de funcionamento", "valores": "preços das refeições e isenções",
    "recarga_creditos": "recarga de créditos e formas de pagamento", "cadastro": "cadastro e acesso ao RU",
    "regras_uso": "regras de uso do RU", "chitchat": "saudações, agradecimentos, despedidas e interação social",
    "fora_dominio": "pedidos de outros assuntos ou serviços, sem solicitação sobre o RU"}
CAMPOS_OFICIAIS = ("texto", "intencao", "origem")
ORIGEM_DELEGADA = "ia_sob_autorizacao_expressa"
MARCADOR_DELEGADA = "origem_decisao=ia_delegada;autorizacao=missao_07a;"
CAMPOS_PRIORIDADE = ("id_resposta", "texto_original", "origem", "rotulo_sugerido",
                     "uso_proposto", "sinalizacao", "sha256_contexto",
                     "decisao_humana", "rotulo_corrigido")


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
    origem_decisao: str = "declaracao_csv_sem_atestacao"

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
        resultado["origem_decisao"] = self.origem_decisao
        resultado["revisao_manual_individual"] = False if self.origem_decisao == ORIGEM_DELEGADA else None
        if self.origem_decisao == ORIGEM_DELEGADA:
            resultado["revisao_humana"] = "curadoria_ia_delegada"
        return resultado


@dataclass(frozen=True)
class AnalisePlanejada(Analise):
    # Sugestão de IA continua com aprovado=False herdado de Analise.publico().
    uso_autorizado: str = ""


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
            origem_decisao = (ORIGEM_DELEGADA if linha["observacoes_revisao"].startswith(MARCADOR_DELEGADA)
                              else "declaracao_csv_sem_atestacao")
            decisoes[identificador] = {"decisao": decisao, "rotulo": revisado, "uso": uso,
                                      "origem_decisao": origem_decisao}
    except (csv.Error, UnicodeError) as exc:
        raise ErroRevisao("csv_revisao_invalido") from exc
    if set(decisoes) != set(esperadas):
        raise ErroRevisao("revisao_com_linhas_ausentes")
    return decisoes


def aplicar_revisoes(analises, decisoes):
    return [AnaliseRevisada(a.celula, decisoes.get(a.celula.id, {}).get("rotulo") or None,
                           a.evidencias, a.alertas,
                           decisoes.get(a.celula.id, {}).get("decisao", "pendente"),
                           decisoes.get(a.celula.id, {}).get("uso", ""), a.sugerido,
                           decisoes.get(a.celula.id, {}).get("origem_decisao", "declaracao_csv_sem_atestacao"))
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


def digest(bruto):
    return hashlib.sha256(bruto).hexdigest()


def codificar_json(objeto):
    return (json.dumps(objeto, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def caminho_privado(nome):
    if nome not in PRIVADOS:
        raise ErroRevisao("arquivo_privado_nao_autorizado")
    p = RAIZ
    relativo = Path("dados/_brutos") / nome
    for parte in relativo.parts:
        p = p / parte
        if p.is_symlink():
            raise ErroRevisao("arquivo_privado_simbolico")
    r = subprocess.run(["git", "-C", str(RAIZ), "check-ignore", "-q", "--", str(relativo)],
                       capture_output=True, check=False)
    if r.returncode != 0:
        raise ErroRevisao("arquivo_privado_deve_estar_ignorado")
    return p


def gravar_privado(nome, bruto, substituir=False):
    """Substituição atômica de um arquivo; nunca remove backups ou exportações."""
    p = caminho_privado(nome)
    if not substituir:
        with p.open("xb") as f:
            f.write(bruto)
        return
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(dir=p.parent, prefix=".curadoria-", delete=False) as f:
            temporario = Path(f.name)
            f.write(bruto)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporario, p)
    finally:
        if temporario is not None and temporario.exists():
            temporario.unlink()


def comparar_versoes_humanas(anterior, nova):
    """Comparação exata por registro, independente da ordem; metadados não saem."""
    hash_nova = digest(nova)
    tabelas = []
    for bruto in (anterior, nova):
        ler_csv(io.StringIO(bruto.decode("utf-8-sig"), newline=""), "H")
        tabelas.append(list(csv.reader(io.StringIO(bruto.decode("utf-8-sig"), newline=""), strict=True)))
    velha, nova = tabelas
    if velha[0] != nova[0]:
        raise ErroRevisao("cabecalhos_das_versoes_diferentes")
    for tabela in tabelas:
        if len({tuple(l) for l in tabela[1:]}) != len(tabela) - 1:
            raise ErroRevisao("envios_integrais_duplicados")
        if len({tuple(l[1:]) for l in tabela[1:]}) != len(tabela) - 1:
            raise ErroRevisao("vinculo_de_envios_ambiguo")
    indice = {tuple(l): i for i, l in enumerate(nova[1:], 1)}
    faltantes = [f"H{i:04d}" for i, l in enumerate(velha[1:], 1) if tuple(l) not in indice]
    if faltantes:
        raise ErroRevisao("envio_anterior_alterado_ou_ausente", faltantes[0])
    mapa = {i: indice[tuple(l)] for i, l in enumerate(velha[1:], 1)}
    return {"envios_anteriores": len(velha) - 1, "envios_novos": len(nova) - 1,
            "acrescentados": sorted(set(range(1, len(nova))) - set(mapa.values())),
            "mapa_envios": mapa, "sha256_anterior": digest(anterior),
            "sha256_nova": hash_nova, "preservacao_integral": True}


def celulas_dos_snapshots(snapshots):
    return [c for fonte, bruto in snapshots.items()
            for c in ler_csv(io.StringIO(bruto.decode("utf-8-sig"), newline=""), fonte)[0]]


def migrar_revisao(anterior, nova, sintetico, revisao_anterior):
    comparacao = comparar_versoes_humanas(anterior, nova)
    antes = {"H": anterior, "S": sintetico}
    depois = {"H": nova, "S": sintetico}
    cs_antes, cs_depois = celulas_dos_snapshots(antes), celulas_dos_snapshots(depois)
    esperadas, _ = preparar_revisao(cs_antes, antes, sinalizar_proximos(cs_antes))
    decisoes = importar_revisao_fluxo(io.StringIO(revisao_anterior.decode("utf-8-sig"), newline=""), esperadas)
    antigas = list(csv.DictReader(io.StringIO(revisao_anterior.decode("utf-8-sig"), newline="")))
    novas, excluidas = preparar_revisao(cs_depois, depois, sinalizar_proximos(cs_depois))
    por_id = {r["id_resposta"]: r for r in novas}
    vinculos = {}
    for r in antigas:
        identificador = r["id_resposta"]
        if r["origem"] == "humano":
            envio = int(r["id_envio"][1:])
            novo_id = f'H{comparacao["mapa_envios"][envio]:04d}:C{int(r["coluna_original"]):02d}'
        else:
            novo_id = identificador
        nova_linha = por_id.get(novo_id)
        if (nova_linha is None or nova_linha["texto_original"] != r["texto_original"]
                or nova_linha["origem"] != r["origem"]):
            raise ErroRevisao("migracao_sem_vinculo_inequivoco", identificador)
        for campo in EDITAVEIS_REVISAO:
            nova_linha[campo] = r[campo]
        vinculos[identificador] = novo_id
    fluxo = io.StringIO(newline="")
    escrever_revisao_fluxo(fluxo, novas)
    resultado = fluxo.getvalue().encode("utf-8-sig")
    importar_revisao_fluxo(io.StringIO(fluxo.getvalue(), newline=""), preparar_revisao(
        cs_depois, depois, sinalizar_proximos(cs_depois))[0])
    rastreio = {"versao": VERSAO, "comparacao": comparacao, "ids_migrados": vinculos,
                "sha256_revisao_anterior": digest(revisao_anterior),
                "sha256_revisao_nova": digest(resultado), "sha256_sintetico": digest(sintetico),
                "decisoes_preservadas": dict(Counter(d["decisao"] for d in decisoes.values())),
                "linhas_novas": len(novas), "excluidas": {k: len(v) for k, v in excluidas.items()}}
    return resultado, rastreio


def atualizar_base_local(aplicar=False):
    nomes = ("formulario_humano.csv", "formulario_humano_novo.csv", "formulario_humano_backup_48.csv",
             "revisao_humana.csv", "revisao_humana_backup_1711.csv", "sinteticas_llm.csv")
    brutos = {n: caminho_privado(n).read_bytes() for n in nomes}
    if brutos[nomes[0]] != brutos[nomes[2]] or brutos[nomes[3]] != brutos[nomes[4]]:
        raise ErroRevisao("backup_desatualizado_ou_base_ja_substituida")
    revisao, rastreio = migrar_revisao(brutos[nomes[0]], brutos[nomes[1]], brutos[nomes[5]], brutos[nomes[3]])
    if aplicar:
        for n, b in brutos.items():
            if caminho_privado(n).read_bytes() != b:
                raise ErroRevisao("arquivo_alterado_durante_migracao")
        # Journal antes das substituições: backups íntegros permitem recuperar falha parcial.
        gravar_privado("migracao_48_67.json", codificar_json(rastreio | {"estado": "preparada"}))
        gravar_privado("revisao_humana.csv", revisao, substituir=True)
        gravar_privado("formulario_humano.csv", brutos[nomes[1]], substituir=True)
        gravar_privado("migracao_48_67.json", codificar_json(rastreio | {"estado": "concluida"}), substituir=True)
    return {k: v for k, v in rastreio.items() if k != "ids_migrados"} | {"substituicao_executada": aplicar}


SINAIS_SEMANTICOS = {"contexto_eliptico", "alternativas_no_mesmo_texto", "fronteira_dominio",
                    "linguagem_ofensiva", "pressuposto_a_conferir", "multiplos_topicos_fora_dominio",
                    "pedido_indireto", "erro_digitacao", "revisao_semantica_ia"}
SITUACOES_SEMANTICAS = {"candidata", "ambigua", "metarresposta", "multiplas_intencoes", "fora_catalogo"}


def validar_triagem(objeto, celulas, sha256_humano):
    if (objeto.get("versao") != 1 or objeto.get("sha256_humano") != sha256_humano
            or objeto.get("autoria") != "sugestao_ia_sem_aprovacao_humana"):
        raise ErroRevisao("versao_ou_fonte_da_triagem_incompativel")
    esperadas = {c.id: c for c in celulas if c.fonte == "H" and c.texto
                 and not impedimentos_revisao(c.texto)}
    itens = objeto.get("itens", {})
    if not isinstance(itens, dict) or set(itens) != set(esperadas):
        raise ErroRevisao("ids_da_triagem_incompativeis")
    for identificador, item in itens.items():
        c = esperadas[identificador]
        if (not isinstance(item, dict) or item.get("sha256_texto") != digest(c.texto.encode())
                or item.get("rotulo") not in (None,) + CLASSES
                or item.get("situacao") not in SITUACOES_SEMANTICAS
                or item.get("uso") not in {"ambos", "treino"}
                or not isinstance(item.get("sinais"), list)
                or any(s not in SINAIS_SEMANTICOS for s in item["sinais"])):
            raise ErroRevisao("item_de_triagem_invalido", identificador)
        if item["situacao"] == "candidata" and item["rotulo"] is None:
            raise ErroRevisao("candidata_sem_rotulo", identificador)
    return itens


def analises_para_planejamento(analises, decisoes, triagem):
    revisadas = {a.celula.id: a for a in aplicar_revisoes(analises, decisoes)}
    resultado = []
    for a in analises:
        revisada = revisadas[a.celula.id]
        if impedimentos_revisao(a.celula.texto):
            resultado.append(AnalisePlanejada(a.celula, None, (), ("rotulo_inconclusivo",)))
        elif revisada.decisao_humana != "pendente":
            resultado.append(revisada)
        elif a.celula.id in triagem:
            item = triagem[a.celula.id]
            alertas = set(item["sinais"])
            if item["situacao"] != "candidata":
                alertas.add("rotulo_inconclusivo")
            resultado.append(AnalisePlanejada(a.celula, item["rotulo"], ("sugestao_semantica_ia",),
                                             tuple(sorted(alertas)), item["uso"]))
        else:
            resultado.append(a)
    return resultado


def selecionar_distintas(analises, rotulo, limite):
    if limite <= 0:
        return []
    selecionadas, vistas = [], set()
    for a in sorted(analises, key=lambda a: (len(a.alertas), a.celula.id)):
        if a.candidata and a.sugerido == rotulo and a.celula.normalizado not in vistas:
            selecionadas.append(a)
            vistas.add(a.celula.normalizado)
            if len(selecionadas) == limite:
                break
    return selecionadas


def preparar_selecao_prioritaria(analises, plano, proximos, fontes, originais):
    envios = set(plano["envios_teste"])
    teste = [a for a in analises if a.celula.fonte == "H" and a.celula.envio in envios
             and permitida_no_uso(a, "teste")]
    reserva = {a.celula.normalizado for a in teste}
    bloqueados = set(plano["celulas_quarentena_proximidade"])
    treino_h = [a for a in analises if a.celula.fonte == "H" and a.celula.envio not in envios
                and permitida_no_uso(a, "treino") and a.celula.normalizado not in reserva
                and a.celula.id not in bloqueados]
    todas_h = {a.celula.normalizado for a in analises if a.celula.fonte == "H"}
    treino_s = [a for a in analises if a.celula.fonte == "S" and permitida_no_uso(a, "treino")
                and a.celula.normalizado not in todas_h and a.celula.id not in bloqueados]
    selecionadas = []
    for c in CLASSES:
        selecionadas += [(a, "teste") for a in selecionar_distintas(teste, c, MIN_TESTE[c])]
        hs = selecionar_distintas(treino_h, c, MIN_TREINO[c])
        selecionadas += [(a, "treino") for a in hs]
        faltam = MIN_TREINO[c] - len(hs)
        if faltam:
            selecionadas += [(a, "treino") for a in selecionar_distintas(treino_s, c, faltam)]
    regras = {"versao": 1, "fontes": fontes, "envios_teste": sorted(envios),
              "selecionadas": [{"id": a.celula.id, "rotulo": a.sugerido, "uso": uso}
                                for a, uso in selecionadas]}
    contexto = digest(codificar_json(regras))
    sinais = defaultdict(set)
    for par in proximos:
        for identificador in par["a"] + par["b"]:
            sinais[identificador].add("quase_duplicata" if par["quase_duplicata"] else "possivel_parafrase")
    duplicadas = grupos_duplicados([a.celula for a in analises])
    for grupo in duplicadas:
        for identificador in grupo:
            sinais[identificador].add("duplicata_normalizada")
    linhas = [{"id_resposta": a.celula.id, "texto_original": originais[a.celula.id],
               "origem": a.celula.origem, "rotulo_sugerido": a.sugerido, "uso_proposto": uso,
               "sinalizacao": ";".join(sorted(set(a.alertas) | sinais[a.celula.id])),
               "sha256_contexto": contexto, "decisao_humana": "pendente", "rotulo_corrigido": ""}
              for a, uso in selecionadas]
    return linhas, regras | {"sha256_contexto": contexto}


def importar_prioritaria(fluxo, esperadas, linhas_mestre, proveniencias=None):
    leitor = csv.DictReader(fluxo, strict=True)
    if leitor.fieldnames != list(CAMPOS_PRIORIDADE):
        raise ErroRevisao("cabecalho_prioritaria_invalido")
    por_id = {r["id_resposta"]: r for r in esperadas}
    mestre = {r["id_resposta"]: dict(r) for r in linhas_mestre}
    vistos = set()
    for r in leitor:
        identificador = r.get("id_resposta")
        if identificador not in por_id or identificador in vistos or None in r or any(v is None for v in r.values()):
            raise ErroRevisao("linhas_prioritaria_invalidas")
        vistos.add(identificador)
        original = por_id[identificador]
        if any(r[c] != original[c] for c in CAMPOS_PRIORIDADE if c not in {"decisao_humana", "rotulo_corrigido"}):
            raise ErroRevisao("integridade_prioritaria_violada", identificador)
        d, rotulo = r["decisao_humana"].strip() or "pendente", r["rotulo_corrigido"].strip()
        if d not in DECISOES or (rotulo and rotulo not in CLASSES):
            raise ErroRevisao("decisao_prioritaria_invalida", identificador)
        observacao = None
        if proveniencias is not None:
            p = proveniencias.get(identificador, {})
            final = rotulo if d == "corrigir" else original["rotulo_sugerido"] if d == "aprovar" else None
            if p.get("decisao") != d or p.get("rotulo_final") != final:
                raise ErroRevisao("decisao_diverge_da_auditoria_delegada", identificador)
            observacao = (MARCADOR_DELEGADA + "ferramenta=" + p["ferramenta"] + ";modelo=" + p["modelo"]
                          + ";revisao_manual_individual=false; " + p["justificativa"])
        if d == "pendente":
            if observacao is not None and mestre[identificador]["decisao_humana"] in {"", "pendente"}:
                mestre[identificador]["observacoes_revisao"] = observacao
            continue
        if d == "aprovar" and rotulo and rotulo != original["rotulo_sugerido"]:
            raise ErroRevisao("troca_de_rotulo_exige_corrigir", identificador)
        if d == "corrigir" and not rotulo:
            raise ErroRevisao("correcao_exige_rotulo", identificador)
        m = mestre[identificador]
        escolhido = rotulo if d == "corrigir" else original["rotulo_sugerido"]
        atualizada = dict(m)
        atualizada["decisao_humana"] = ("corrigir" if d == "aprovar" and escolhido != m["rotulo_sugerido"] else d)
        atualizada["rotulo_revisado"] = escolhido if d in {"aprovar", "corrigir"} else ""
        atualizada["uso_autorizado"] = original["uso_proposto"]
        if observacao is not None:
            atualizada["observacoes_revisao"] = observacao
        if m["decisao_humana"] not in {"", "pendente"} and m != atualizada:
            raise ErroRevisao("decisao_mestre_existente_nao_sobrescrever", identificador)
        mestre[identificador] = atualizada
    if vistos != set(por_id):
        raise ErroRevisao("prioritaria_com_linhas_ausentes")
    # A validação integral (rótulos conflitantes, origem, versão) continua centralizada.
    f = io.StringIO(newline="")
    escrever_revisao_fluxo(f, mestre.values())
    importar_revisao_fluxo(io.StringIO(f.getvalue(), newline=""), linhas_mestre)
    return list(mestre.values())


def contexto_curadoria(usar_exportacao_nova=False):
    if not usar_exportacao_nova:
        celulas, fontes, snapshots = ler_entradas()
        bruto_revisao = caminho_revisao_local().read_bytes()
        return celulas, fontes, snapshots, bruto_revisao
    # Preflight: planeja a versão nova sem exigir sua substituição no sandbox.
    atualizar_base_local(aplicar=False)
    anterior = caminho_privado("formulario_humano.csv").read_bytes()
    nova = caminho_privado("formulario_humano_novo.csv").read_bytes()
    sintetico = caminho_privado("sinteticas_llm.csv").read_bytes()
    revisao, _ = migrar_revisao(anterior, nova, sintetico, caminho_revisao_local().read_bytes())
    snapshots = {"H": nova, "S": sintetico}
    celulas = celulas_dos_snapshots(snapshots)
    fontes = {f: {"origem": FONTES[f][1], "envios": len([c for c in celulas if c.fonte == f]) // 10,
                   "sha256_entrada": digest(b)} for f, b in snapshots.items()}
    return celulas, fontes, snapshots, revisao


def conferir_contexto(snapshots, usar_exportacao_nova=False):
    for fonte, bruto in snapshots.items():
        nome = ("formulario_humano_novo.csv" if usar_exportacao_nova and fonte == "H"
                else Path(FONTES[fonte][0]).name)
        if caminho_privado(nome).read_bytes() != bruto:
            raise ErroRevisao("fonte_alterada_durante_planejamento")


def planejar_curadoria_local(exportar=False, usar_exportacao_nova=False):
    celulas, fontes, snapshots, bruto_revisao = contexto_curadoria(usar_exportacao_nova)
    proximos = sinalizar_proximos(celulas)
    linhas, _ = preparar_revisao(celulas, snapshots, proximos)
    decisoes = importar_revisao_fluxo(io.StringIO(bruto_revisao.decode("utf-8-sig"), newline=""), linhas)
    sha_revisao = digest(bruto_revisao)
    bruto_triagem = caminho_privado("triagem_semantica_67.json").read_bytes()
    triagem = validar_triagem(json.loads(bruto_triagem), celulas, fontes["H"]["sha256_entrada"])
    analises = analises_para_planejamento(marcar_colunas_conflitantes([analisar(c) for c in celulas]), decisoes, triagem)
    comparacao = comparar_versoes_humanas(caminho_privado("formulario_humano_backup_48.csv").read_bytes(), snapshots["H"])
    planos = propor_divisoes(analises, fontes["H"]["envios"], proximos,
                            tamanhos=(29, 30, 31, 33, 35, 37, 39), largura=5, agrupar_duplicatas=False,
                            estrato_envios=comparacao["acrescentados"])
    if not planos:
        raise ErroRevisao("busca_sem_plano_nao_prova_inviabilidade")
    escolhido = min(planos, key=lambda p: (
        not p["viavel_condicionada_a_revisao_e_complemento"], sum(p["teste_minimos"]["faltas"].values()),
        -p["humanas_planejadas_no_alvo"], sum(p["novas_sinteticas_necessarias"].values()), len(p["envios_teste"])))
    prioridades, regras = preparar_selecao_prioritaria(analises, escolhido, proximos, fontes, textos_originais(snapshots))
    plano = regras | {"sha256_triagem": digest(bruto_triagem), "sha256_revisao_inicial": sha_revisao,
                      "divisao_aprovada": False, "congelado": False,
                      "linhas_prioridade": [{k: v for k, v in r.items() if k != "texto_original"} for r in prioridades]}
    conferir_contexto(snapshots, usar_exportacao_nova)
    if exportar:
        # Não sobrescrever uma revisão prioritária ou um plano anteriores.
        if any(caminho_privado(n).exists() for n in ("revisao_prioritaria.csv", "plano_curadoria_67.json")):
            raise ErroRevisao("plano_ou_prioritaria_ja_existe")
        if usar_exportacao_nova:
            gravar_privado("revisao_humana_67_preparada.csv", bruto_revisao)
        f = io.StringIO(newline="")
        e = csv.DictWriter(f, fieldnames=CAMPOS_PRIORIDADE, lineterminator="\n")
        e.writeheader()
        e.writerows(prioridades)
        gravar_privado("plano_curadoria_67.json", codificar_json(plano))
        gravar_privado("revisao_prioritaria.csv", f.getvalue().encode("utf-8-sig"))
    return {"natureza": "proposta_ia_sem_aprovacao", "candidatas_humanas": distribuir(
                [a for a in analises if a.celula.fonte == "H"]),
            "situacoes_semanticas": dict(Counter(i["situacao"] for i in triagem.values())),
            "alternativas": planos, "proposta": escolhido, "linhas_prioritarias": len(prioridades),
            "selecionadas_por_uso_e_origem": dict(Counter(r["uso_proposto"] + ":" + r["origem"] for r in prioridades)),
            "base_ativa_substituida": not usar_exportacao_nova,
            "divisao_aprovada": False, "congelado": False}


def linhas_prioritarias_do_plano(plano, mestre, fontes, sha_triagem):
    regras = {k: plano[k] for k in ("versao", "fontes", "envios_teste", "selecionadas")}
    if (plano["versao"] != 1 or plano["fontes"] != fontes
            or plano["sha256_contexto"] != digest(codificar_json(regras))
            or plano["sha256_triagem"] != sha_triagem):
        raise ErroRevisao("plano_prioritario_incompativel")
    por_id = {r["id_resposta"]: r for r in mestre}
    especificacoes = [{"id": r["id_resposta"], "rotulo": r["rotulo_sugerido"], "uso": r["uso_proposto"]}
                      for r in plano["linhas_prioridade"]]
    if especificacoes != plano["selecionadas"] or len({r["id"] for r in especificacoes}) != len(especificacoes):
        raise ErroRevisao("especificacoes_prioritarias_incompativeis")
    linhas = []
    for r in plano["linhas_prioridade"]:
        identificador = r["id_resposta"]
        if identificador not in por_id:
            raise ErroRevisao("id_prioritario_desconhecido")
        original = por_id[identificador]
        if (r["origem"] != original["origem"] or r["sha256_contexto"] != plano["sha256_contexto"]
                or r["rotulo_sugerido"] not in CLASSES or r["uso_proposto"] not in {"treino", "teste"}
                or (r["origem"] == "llm" and r["uso_proposto"] != "treino")):
            raise ErroRevisao("origem_ou_uso_prioritario_invalido", identificador)
        if original["origem"] == "humano":
            esperado = "teste" if int(original["id_envio"][1:]) in plano["envios_teste"] else "treino"
            if r["uso_proposto"] != esperado:
                raise ErroRevisao("envio_humano_separado_indevidamente", identificador)
        linhas.append(r | {"texto_original": original["texto_original"]})
    return linhas


def validar_auditoria_delegada(auditoria, linhas, mestre, fontes, anteriores):
    """Vincula decisões de IA a autorização, textos, origens e versões; não autentica pessoas."""
    if not isinstance(auditoria, dict):
        raise ErroRevisao("auditoria_delegada_invalida")
    autorizacao = auditoria.get("autorizacao", {})
    if (not isinstance(autorizacao, dict) or auditoria.get("versao") != 1 or auditoria.get("origem_decisao") != ORIGEM_DELEGADA
            or autorizacao.get("referencia") != "missao_07a"
            or autorizacao.get("revisao_manual_individual") is not False
            or autorizacao.get("responsavel_revisou_todas_as_frases") is not False
            or auditoria.get("fontes") != fontes
            or not auditoria.get("ferramenta") or not auditoria.get("modelo")):
        raise ErroRevisao("autorizacao_ou_versao_da_delegacao_invalida")
    registros = auditoria.get("registros", {})
    ids = {r["id_resposta"] for r in linhas}
    antigos = {r["id_resposta"]: r for r in anteriores}
    originais = {r["id_resposta"]: r for r in mestre}
    if not isinstance(registros, dict) or set(registros) != ids or not set(antigos) <= ids:
        raise ErroRevisao("ids_da_delegacao_incompativeis")
    for linha in linhas:
        identificador = linha["id_resposta"]
        if identificador not in originais:
            raise ErroRevisao("delegacao_com_id_desconhecido")
        r, original = registros[identificador], originais[identificador]
        if not isinstance(r, dict):
            raise ErroRevisao("registro_delegado_invalido", identificador)
        anterior = antigos.get(identificador, original)["rotulo_sugerido"] or None
        if (r.get("texto_original") != original["texto_original"]
                or r.get("sha256_texto") != digest(original["texto_original"].encode())
                or r.get("origem_frase") != original["origem"]
                or r.get("uso_proposto") != linha["uso_proposto"]
                or r.get("rotulo_anterior") != anterior
                or r.get("rotulo_proposto") != linha["rotulo_sugerido"]
                or r.get("origem_decisao") != ORIGEM_DELEGADA
                or r.get("revisao_manual_individual") is not False
                or r.get("ferramenta") != auditoria["ferramenta"] or r.get("modelo") != auditoria["modelo"]
                or not isinstance(r.get("justificativa"), str) or not r["justificativa"].strip()
                or impedimentos_revisao(r["justificativa"])):
            raise ErroRevisao("registro_delegado_invalido", identificador)
        ref = r.get("substitui")
        if ref is not None:
            if (identificador in antigos or ref not in antigos
                    or registros[ref]["decisao"] not in {"rejeitar", "pendente", "corrigir"}
                    or antigos[ref]["uso_proposto"] != linha["uso_proposto"]
                    or antigos[ref]["rotulo_sugerido"] != r.get("rotulo_final")):
                raise ErroRevisao("substituicao_delegada_invalida", identificador)
    return registros


def conferir_prioritaria_local(usar_exportacao_nova=False, delegada=False, aplicar=False):
    celulas, fontes, snapshots, bruto_mestre = contexto_curadoria(usar_exportacao_nova)
    esperadas, _ = preparar_revisao(celulas, snapshots, sinalizar_proximos(celulas))
    mestre = list(csv.DictReader(io.StringIO(bruto_mestre.decode("utf-8-sig"), newline="")))
    importar_revisao_fluxo(io.StringIO(bruto_mestre.decode("utf-8-sig"), newline=""), esperadas)
    plano = json.loads(caminho_privado("plano_curadoria_67.json").read_bytes())
    linhas = linhas_prioritarias_do_plano(plano, mestre, fontes,
              digest(caminho_privado("triagem_semantica_67.json").read_bytes()))
    bruto = caminho_privado("revisao_prioritaria.csv").read_bytes()
    proveniencias, auditoria = None, None
    # Um ledger delegado existente nunca deve ser ignorado por um comando legado.
    delegada = delegada or caminho_privado("auditoria_delegada_07a.json").exists()
    if delegada:
        auditoria = json.loads(caminho_privado("auditoria_delegada_07a.json").read_bytes())
        backup_mestre = caminho_privado("revisao_humana_backup_07a.csv").read_bytes()
        backup_prioritaria = caminho_privado("revisao_prioritaria_backup_07a.csv").read_bytes()
        backup_plano = caminho_privado("plano_curadoria_67_backup_07a.json").read_bytes()
        if (digest(backup_mestre) != auditoria["sha256_mestre_antes"]
                or digest(backup_prioritaria) != auditoria["sha256_prioritaria_antes"]
                or digest(backup_plano) != auditoria["sha256_plano_antes"]
                or digest(bruto) != auditoria["sha256_prioritaria_depois"]
                or digest(caminho_privado("plano_curadoria_67.json").read_bytes()) != auditoria["sha256_plano_depois"]
                or digest(bruto_mestre) not in {auditoria["sha256_mestre_antes"], auditoria["sha256_mestre_depois"]}):
            raise ErroRevisao("hashes_da_delegacao_incompativeis")
        anteriores = list(csv.DictReader(io.StringIO(backup_prioritaria.decode("utf-8-sig"), newline="")))
        proveniencias = validar_auditoria_delegada(auditoria, linhas, mestre, fontes, anteriores)
    novas = importar_prioritaria(io.StringIO(bruto.decode("utf-8-sig"), newline=""), linhas, mestre, proveniencias)
    f = io.StringIO(newline="")
    escrever_revisao_fluxo(f, novas)
    decisoes = importar_revisao_fluxo(io.StringIO(f.getvalue(), newline=""), esperadas)
    analises = aplicar_revisoes([analisar(c) for c in celulas], decisoes)
    revisao_atualizada = f.getvalue().encode("utf-8-sig")
    if delegada:
        if digest(revisao_atualizada) != auditoria["sha256_mestre_depois"]:
            raise ErroRevisao("resultado_da_delegacao_divergente")
        aprovadas = [a for a in analises if a.candidata]
        teste = [a for a in aprovadas if permitida_no_uso(a, "teste") and a.celula.envio in plano["envios_teste"]]
        treino = [a for a in aprovadas if permitida_no_uso(a, "treino") and (
            a.celula.fonte == "S" or a.celula.envio not in plano["envios_teste"])]
        if any(a.celula.origem != "humano" for a in teste) or detectar_sobreposicao(treino, teste):
            raise ErroRevisao("vazamento_na_delegacao")
        ids_t, ids_h = {a.celula.id for a in treino}, {a.celula.id for a in teste}
        for par in sinalizar_proximos(celulas):
            if par["quase_duplicata"] and ((set(par["a"]) & ids_t and set(par["b"]) & ids_h)
                                          or (set(par["b"]) & ids_t and set(par["a"]) & ids_h)):
                raise ErroRevisao("quase_duplicata_entre_treino_e_teste")
    conferir_contexto(snapshots, usar_exportacao_nova)
    gravou = False
    if aplicar:
        if not delegada:
            raise ErroRevisao("gravacao_exige_ledger_delegado")
        if caminho_revisao_local().read_bytes() != bruto_mestre:
            raise ErroRevisao("mestre_alterado_durante_importacao")
        if bruto_mestre != revisao_atualizada:
            gravar_privado("revisao_humana.csv", revisao_atualizada, substituir=True)
            gravou = True
    resultado = {"revisao": resumir_revisao(esperadas, decisoes), "gravacao_executada": gravou,
            "divisao_aprovada": False, "sha256_prioritaria": digest(bruto),
            "plano_somente_aprovadas": avaliar_divisao(analises, plano["envios_teste"], fontes["H"]["envios"],
                                                      sinalizar_proximos(celulas), quarentenar_duplicatas=True)}
    if delegada:
        resultado["curadoria_delegada"] = {"origem_decisao": ORIGEM_DELEGADA, "revisao_manual_individual": False,
            "mestre_persistido": gravou or bruto_mestre == revisao_atualizada,
            "analisadas_com_registro": len(proveniencias),
            "decisoes_prioritarias": dict(Counter(p["decisao"] for p in proveniencias.values())),
            "originais": len(anteriores), "suplentes": len(proveniencias) - len(anteriores)}
    return resultado


def serializar_oficial(registros):
    f = io.StringIO(newline="")
    w = csv.DictWriter(f, fieldnames=CAMPOS_OFICIAIS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    w.writerows(registros)
    return f.getvalue().encode("utf-8")


def selecionar_ratificadas(prioritaria, originais):
    """Somente aprovar/corrigir do snapshot ratificado, preservando valores originais."""
    mestre = {r["id_resposta"]: r for r in originais}
    treino, teste, vistos = [], [], set()
    for r in prioritaria:
        identificador = r["id_resposta"]
        if identificador in vistos or identificador not in mestre:
            raise ErroRevisao("id_ratificado_invalido")
        vistos.add(identificador)
        m = mestre[identificador]
        if r["texto_original"] != m["texto_original"] or r["origem"] != m["origem"]:
            raise ErroRevisao("original_ratificado_alterado", identificador)
        if r["decisao_humana"] not in {"aprovar", "corrigir"}:
            continue
        rotulo = r["rotulo_corrigido"] if r["decisao_humana"] == "corrigir" else r["rotulo_sugerido"]
        if rotulo not in CLASSES or r["uso_proposto"] not in {"treino", "teste"}:
            raise ErroRevisao("rotulo_ou_destino_ratificado_invalido", identificador)
        item = {"id_resposta": identificador, "texto": m["texto_original"], "intencao": rotulo, "origem": m["origem"]}
        (teste if r["uso_proposto"] == "teste" else treino).append(item)
    return treino, teste


def verificar_selecao_oficial(treino, teste):
    conjuntos = {}
    for tipo, linhas in (("treino", treino), ("teste", teste)):
        contagens, humanas, normas = Counter(), 0, set()
        for r in linhas:
            if r["intencao"] not in CLASSES or r["origem"] not in {"humano", "coletado", "llm"}:
                raise ErroRevisao("classe_ou_origem_oficial_invalida")
            if tipo == "teste" and r["origem"] != "humano":
                raise ErroRevisao("teste_ratificado_deve_ser_humano")
            n = normalizar(r["texto"])
            if not n or n in normas:
                raise ErroRevisao("vazia_ou_duplicata_no_conjunto_oficial")
            normas.add(n)
            contagens[r["intencao"]] += 1
            humanas += r["origem"] in {"humano", "coletado"}
        conjuntos[tipo] = {"normas": normas, "contagens": {c: contagens[c] for c in CLASSES}, "humanas": humanas}
    if conjuntos["treino"]["normas"] & conjuntos["teste"]["normas"]:
        raise ErroRevisao("vazamento_no_conjunto_oficial")
    t, h = conjuntos["teste"], conjuntos["treino"]
    validacao_teste = validar_minimos(t["contagens"], t["humanas"], "teste")
    if t["contagens"] != MIN_TESTE or not validacao_teste["minimos_atendidos"]:
        raise ErroRevisao("teste_nao_atende_composicao_exata")
    return {"teste": validacao_teste | {"por_classe": t["contagens"]},
            "treino": validar_minimos(h["contagens"], h["humanas"]) | {"por_classe": h["contagens"]}}


def pacote_somente_treinamento(treino, faltas):
    descricao = "\n".join(f"- {c}: {d}." for c, d in DEFINICOES.items())
    quotas = "\n".join(f"- {c}: {faltas[c]}." for c in CLASSES)
    texto = ("# Pacote exclusivo de treinamento — RANGOT\n\n"
        "Contém somente exemplos de treinamento autorizados e definições públicas de intenções.\n"
        "Não copie outros arquivos do repositório para o ambiente gerador.\n\n"
        "## Intenções\n\n" + descricao + "\n\n## Quantidades ainda sem exemplos autorizados\n\n" + quotas +
        "\n\nAntes de gerar, conferir a seleção suplementar da base existente com o responsável e atualizar as quantidades.\n"
        "Este pacote não autoriza execução de API ou geração nesta missão.\n\n"
        "## Instruções para a futura geração em ambiente isolado\n\n"
        "Use somente treino_autorizado.csv como exemplos; não busque outros arquivos do projeto.\n"
        "Gere perguntas de usuários, nunca respostas factuais inventadas sobre serviços do RU.\n"
        "Todo texto gerado recebe origem=llm. Preserve os oito rótulos, sem usar dominio ou esclarecer.\n"
        "Varie construções, objetivos, extensões, registro formal/informal, elipses reconhecíveis e erros de digitação.\n"
        "Não infle o volume trocando apenas saudação, pontuação, grafia ou partículas de um template.\n"
        "Para fora_dominio, varie serviços UFMS: secretaria, assistência, estágio, TI, calendário e mobilidade;\n"
        "combine negativos fáceis e difíceis com palavras compartilhadas com o RU.\n"
        "Não invente dados pessoais nem regras, valores ou funcionamento institucional.\n"
        "Registre ferramenta/modelo e prompts reais; submeta cada candidata à revisão e deduplicação antes de usar.\n")
    return {"pacote_treinamento_07b/INSTRUCOES.md": texto.encode(),
            "pacote_treinamento_07b/treino_autorizado.csv": serializar_oficial(treino)}


def montar_conjuntos_07b():
    # Reusar a validação já implementada; não repetir a análise semântica ratificada.
    conferido = conferir_prioritaria_local(delegada=True)
    if not conferido["curadoria_delegada"]["mestre_persistido"]:
        raise ErroRevisao("curadoria_ratificada_nao_persistida")
    ratificacao = json.loads(caminho_privado("ratificacao_07b.json").read_bytes())
    fontes = {n: caminho_privado(n).read_bytes() for n in ("revisao_prioritaria.csv", "revisao_humana.csv",
              "plano_curadoria_67.json", "auditoria_delegada_07a.json")}
    if (ratificacao.get("versao") != 1 or ratificacao.get("referencia") != "missao_07b"
            or ratificacao.get("leitura_integral_confirmada") is not True
            or ratificacao.get("pendencias_nao_aprovadas") is not True
            or ratificacao.get("sha256_arquivos") != {n: digest(b) for n, b in fontes.items()}):
        raise ErroRevisao("ratificacao_07b_incompativel")
    leitor = lambda b: list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"), newline="")))
    linhas, mestre = leitor(fontes["revisao_prioritaria.csv"]), leitor(fontes["revisao_humana.csv"])
    if Counter(r["decisao_humana"] for r in linhas) != Counter(ratificacao["decisoes_ratificadas"]):
        raise ErroRevisao("decisoes_divergem_da_ratificacao")
    treino, teste = selecionar_ratificadas(linhas, mestre)
    resultado = verificar_selecao_oficial(treino, teste)
    p = conferido["plano_somente_aprovadas"]
    if p["sobreposicoes_normalizadas"] or p["celulas_quarentena_proximidade"] or p["sinais_parafrase_a_revisar"]:
        raise ErroRevisao("proximidade_problematicas_antes_congelamento")
    bteste, btreino = serializar_oficial(teste), serializar_oficial(treino)
    manifesto = {"versao": 1, "referencia": "missao_07b", "congelado": True,
        "rotulos_ratificados_pelo_responsavel": True,
        "origens_teste": dict(Counter(r["origem"] for r in teste)),
        "sha256_teste": digest(bteste), "sha256_treino_parcial": digest(btreino),
        "sha256_ratificacao": digest(caminho_privado("ratificacao_07b.json").read_bytes()),
        "composicao": resultado, "ids_teste": [r["id_resposta"] for r in teste],
        "ids_treino_autorizado": [r["id_resposta"] for r in treino],
        "treino_oficial_completo": resultado["treino"]["minimos_atendidos"],
        "textos_originais_preservados": True, "sobreposicoes_normalizadas": 0}
    arquivos = {"dados/teste.csv": bteste,
        "dados/_brutos/treino_parcial_07b.csv": btreino,
        "dados/_brutos/manifesto_conjuntos_07b.json": codificar_json(manifesto)}
    arquivos.update({"dados/_brutos/" + n: b for n, b in pacote_somente_treinamento(treino, resultado["treino"]["faltas"]).items()})
    if resultado["treino"]["minimos_atendidos"]:
        arquivos["dados/treino.csv"] = btreino
    return arquivos, manifesto


def conferir_conjuntos_07b():
    arquivos, manifesto = montar_conjuntos_07b()
    for nome, esperado in arquivos.items():
        p = RAIZ
        for parte in Path(nome).parts:
            p = p / parte
            if p.is_symlink():
                raise ErroRevisao("artefato_oficial_simbolico")
        if p.read_bytes() != esperado:
            raise ErroRevisao("artefato_diverge_do_congelamento")
    return {k: v for k, v in manifesto.items() if not k.startswith("ids_")}


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


def avaliar_divisao(analises, envios_teste, n_envios, proximos, quarentenar_duplicatas=False):
    teste_ids = set(envios_teste)
    if not teste_ids <= set(range(1, n_envios + 1)):
        raise ErroAuditoria("envios_invalidos")
    humanos = [a for a in analises if a.celula.fonte == "H" and a.candidata]
    teste = [a for a in humanos if a.celula.envio in teste_ids and permitida_no_uso(a, "teste")]
    reserva = {a.celula.normalizado for a in teste}
    retirar_exatas = {a.celula.id for a in humanos if a.celula.envio not in teste_ids
                      and a.celula.normalizado in reserva} if quarentenar_duplicatas else set()
    treino_h = [a for a in humanos if a.celula.envio not in teste_ids and permitida_no_uso(a, "treino")
                and a.celula.id not in retirar_exatas]
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
        "celulas_quarentena_duplicata_normalizada": sorted(retirar_exatas),
        "aprovadas_nao_alocadas_por_uso": sorted(a.celula.id for a in humanos
            if not permitida_no_uso(a, "teste" if a.celula.envio in teste_ids else "treino")),
        "celulas_quarentena_proximidade": sorted(retirar),
        "sinais_parafrase_a_revisar": parafrases,
        "viavel_condicionada_a_revisao_e_complemento": teste_minimos["minimos_atendidos"] and h_planejadas * 5 >= sum(MIN_TREINO.values()) and not sobreposicoes,
        "revisao_humana": "pendente", "congelado": False,
    }


def propor_divisoes(analises, n_envios, proximos, tamanhos=(29, 30, 31), largura=3,
                    agrupar_duplicatas=True, estrato_envios=None):
    """Busca limitada e determinística; ausência de solução não prova inviabilidade."""
    humanos = [a for a in analises if a.celula.fonte == "H"]
    componentes = componentes_envios(humanos, n_envios) if agrupar_duplicatas else [[i] for i in range(1, n_envios + 1)]
    zeros = (0,) * len(CLASSES)
    estrato = set(estrato_envios or [])
    estados = {(0, 0, 0): [(zeros, ())]}
    maximo = min(max(tamanhos), n_envios)

    def ordem(estado):
        counts, ids = estado
        cobertura = sum(min(counts[k], MIN_TESTE[c]) for k, c in enumerate(CLASSES))
        return (-cobertura, sum(counts), ids)

    for grupo in componentes:
        dist = distribuir([a for a in humanos if a.celula.envio in grupo
                           and permitida_no_uso(a, "teste")])["por_classe"]
        novos = defaultdict(list)
        for (n, social, estratificados), candidatos in estados.items():
            novos[n, social, estratificados].extend(candidatos)
            if n + len(grupo) <= maximo:
                for counts, ids in candidatos:
                    vec = tuple(counts[k] + dist[c] for k, c in enumerate(CLASSES))
                    chave = (n + len(grupo), min(vec[-1], MIN_TESTE["chitchat"] + 2),
                             estratificados + len(set(grupo) & estrato))
                    novos[chave].append((vec, tuple(sorted(ids + tuple(grupo)))))
        estados = {k: sorted(set(v), key=ordem)[:largura] for k, v in novos.items()}
    resultados = []
    for tamanho in tamanhos:
        alvo_estrato = (tamanho * len(estrato) + n_envios // 2) // n_envios
        candidatos = [v for (n, _, e), vv in estados.items() if n == tamanho and e == alvo_estrato for v in vv]
        # Avaliar somente os melhores limites lexicais; não otimiza nenhum modelo.
        candidatos.sort(key=ordem)
        planos = [avaliar_divisao(analises, ids, n_envios, proximos,
                                  quarentenar_duplicatas=not agrupar_duplicatas) for _, ids in candidatos[:12]]
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
    parser.add_argument("--usar-exportacao-nova", action="store_true",
                        help="planejar/validar a versao nova em memoria, antes da substituicao")
    revisao = parser.add_mutually_exclusive_group()
    revisao.add_argument("--exportar-revisao", action="store_true", help="criar planilha local ignorada, sem sobrescrever")
    revisao.add_argument("--importar-revisao", action="store_true", help="validar decisoes declaradas na planilha local")
    revisao.add_argument("--planejar-atualizacao", action="store_true", help="comparar versoes e backups sem gravar")
    revisao.add_argument("--atualizar-base", action="store_true", help="migrar base/revisao privadas com backups verificados")
    revisao.add_argument("--planejar-curadoria", action="store_true", help="simular divisao com sugestoes semanticas privadas")
    revisao.add_argument("--exportar-prioritaria", action="store_true", help="criar plano e revisao reduzida sem sobrescrever")
    revisao.add_argument("--importar-prioritaria", action="store_true", help="validar revisao reduzida e recontar, sem gravar")
    revisao.add_argument("--importar-delegada", action="store_true", help="validar ledger e decisoes delegadas sem gravar")
    revisao.add_argument("--aplicar-delegada", action="store_true", help="validar delegacao e persistir mestre com proveniencia")
    revisao.add_argument("--conferir-conjuntos", action="store_true", help="conferir hashes e composicao dos artefatos ratificados")
    args = parser.parse_args(argv)
    try:
        acoes = (args.planejar_atualizacao, args.atualizar_base, args.planejar_curadoria,
                 args.exportar_prioritaria, args.importar_prioritaria, args.importar_delegada, args.aplicar_delegada,
                 args.conferir_conjuntos)
        if any(acoes):
            if args.envios_teste is not None:
                raise ErroRevisao("acao_incompativel_com_envios_explicitos")
            if args.conferir_conjuntos:
                if args.usar_exportacao_nova:
                    raise ErroRevisao("congelamento_exige_fontes_ativas")
                resultado = conferir_conjuntos_07b()
            elif args.planejar_atualizacao or args.atualizar_base:
                if args.usar_exportacao_nova:
                    raise ErroRevisao("acao_incompativel_com_fonte_nova")
                resultado = atualizar_base_local(aplicar=args.atualizar_base)
            elif args.importar_prioritaria or args.importar_delegada or args.aplicar_delegada:
                resultado = conferir_prioritaria_local(args.usar_exportacao_nova,
                    delegada=args.importar_delegada or args.aplicar_delegada, aplicar=args.aplicar_delegada)
            else:
                resultado = planejar_curadoria_local(exportar=args.exportar_prioritaria,
                                                      usar_exportacao_nova=args.usar_exportacao_nova)
            print(json.dumps(resultado, ensure_ascii=False, sort_keys=True, indent=2))
            return 0
        if args.usar_exportacao_nova:
            raise ErroRevisao("fonte_nova_exige_acao_de_curadoria")
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
    except (ErroAuditoria, OSError, UnicodeError, csv.Error, json.JSONDecodeError, KeyError, TypeError):
        print('{"erro":"auditoria_nao_concluida_entradas_ou_layout_invalidos"}', file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
