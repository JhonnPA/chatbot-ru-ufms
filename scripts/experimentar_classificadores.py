"""Executar a Missão 08 offline a partir da raiz, sem ler CSV de teste."""
from __future__ import annotations

import os
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
# Caminho público de cache; não ler/dumpar variáveis de ambiente ou segredos.
os.environ["MPLCONFIGDIR"] = str(RAIZ / ".cache/matplotlib")


def main():
    try:
        from chatbot.experimentos import executar
    except ModuleNotFoundError as exc:
        print(f"Dependência indisponível: {exc.name}. Prepare requirements.txt em ambiente autorizado.", file=sys.stderr)
        return 2
    executar(RAIZ)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
