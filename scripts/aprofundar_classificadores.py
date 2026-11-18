"""A1/limiar em memória ou gravação dos artefatos, sem treinar nos dados de teste."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ["MPLCONFIGDIR"] = str(RAIZ / ".cache/matplotlib")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    modo = p.add_mutually_exclusive_group(required=True)
    modo.add_argument("--emitir-json", action="store_true", help="executar sem gravar; exportar artefatos textuais reais")
    modo.add_argument("--gravar", action="store_true", help="executar, salvar resultados e configurar limiar_tema")
    args = p.parse_args()
    from chatbot.aprofundamento import executar_memoria, gravar
    resultado = executar_memoria(RAIZ)
    if args.gravar:
        gravar(RAIZ, resultado)
        print(json.dumps(resultado["metadados"], ensure_ascii=False))
    else:
        print(json.dumps(resultado, ensure_ascii=False))


if __name__ == "__main__":
    main()
