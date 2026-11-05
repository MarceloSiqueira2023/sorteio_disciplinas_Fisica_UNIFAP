"""Persistência local em JSON (dados/config.json).

A pasta dados/ fica fora do Git (ver .gitignore): nomes e fotos não vão
para o repositório público.
"""
from __future__ import annotations

import json
from pathlib import Path

PASTA = Path(__file__).resolve().parent / "dados"
ARQUIVO = PASTA / "config.json"
CHAVES = ("cfg", "profs", "discs", "log")


def carregar() -> dict:
    if not ARQUIVO.exists():
        return {}
    try:
        return json.loads(ARQUIVO.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def salvar(dados) -> None:
    PASTA.mkdir(parents=True, exist_ok=True)
    limpo = {k: dados.get(k) for k in CHAVES if k in dados}
    ARQUIVO.write_text(
        json.dumps(limpo, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def arquivar_log(log: list) -> Path:
    """Grava o log num arquivo separado antes de reiniciar a cadeia."""
    from datetime import datetime
    PASTA.mkdir(parents=True, exist_ok=True)
    arq = PASTA / f"log-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    arq.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    return arq