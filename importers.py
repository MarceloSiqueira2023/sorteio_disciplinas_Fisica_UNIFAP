"""Leitura/escrita de planilhas CSV de professores e disciplinas.

Formato interno (mesmo do ui.py):
    profs: [{"nome": str, "foto": base64-JPEG-200x200 | None}, ...]
    discs: [str, ...]

CSV de professores:
    colunas obrigatórias: nome
    colunas opcionais:    foto_base64   (JPEG/PNG em base64, sem prefixo data:)
                          foto_mime     (ignorada — sempre reencodamos para JPEG)

CSV de disciplinas:
    coluna obrigatória: nome

Aceita separador , ou ; e UTF-8 (com/sem BOM) ou latin-1. Fotos passam
por PIL, então PNG, WebP e fotos tortas do celular funcionam também.
"""
from __future__ import annotations

import base64
import binascii
import csv
import io
from typing import BinaryIO

import pandas as pd
from PIL import Image, ImageOps

MODELO_PROFS = (
    "nome,foto_base64\n"
    "Maria Angélica,\n"
    "Zenaide,\n"
)
MODELO_DISCS = (
    "nome\n"
    "Física Geral I\n"
    "Física Geral II\n"
)


def _ler_csv(arquivo: BinaryIO) -> pd.DataFrame:
    ultimo: Exception | None = None
    for sep in (",", ";"):
        for enc in ("utf-8-sig", "latin-1"):
            try:
                arquivo.seek(0)
                df = pd.read_csv(
                    arquivo, dtype=str, keep_default_na=False,
                    encoding=enc, sep=sep,
                )
            except Exception as e:  # noqa: BLE001
                ultimo = e
                continue
            df.columns = [str(c).strip().lower() for c in df.columns]
            if "nome" in df.columns:
                return df
    raise ValueError(f"Não consegui ler o CSV: {ultimo or 'sem coluna nome'}")


def _normalizar_foto(b64: str) -> str | None:
    """Decodifica base64, corta em quadrado 200x200 e devolve JPEG base64.
    Retorna None se a imagem for inválida."""
    try:
        bruto = base64.b64decode(b64, validate=True)
    except (binascii.Error, ValueError):
        return None
    try:
        img = ImageOps.exif_transpose(Image.open(io.BytesIO(bruto))).convert("RGB")
    except Exception:  # noqa: BLE001
        return None
    img = ImageOps.fit(img, (200, 200))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def ler_professores(arquivo: BinaryIO) -> tuple[list[dict], list[str]]:
    df = _ler_csv(arquivo)
    profs: list[dict] = []
    avisos: list[str] = []
    for idx, row in df.iterrows():
        nome = (row.get("nome") or "").strip()
        if not nome:
            continue
        b64 = (row.get("foto_base64") or "").strip()
        foto = None
        if b64:
            foto = _normalizar_foto(b64)
            if foto is None:
                avisos.append(
                    f"Linha {idx + 2}: foto inválida para {nome!r}; ignorada."
                )
        profs.append({"nome": nome, "foto": foto})
    return profs, avisos


def ler_disciplinas(arquivo: BinaryIO) -> list[str]:
    df = _ler_csv(arquivo)
    vistas: list[str] = []
    for v in df["nome"]:
        nome = (v or "").strip()
        if nome and nome not in vistas:
            vistas.append(nome)
    return vistas


def exportar_professores(profs: list[dict]) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["nome", "foto_base64"])
    for p in profs:
        w.writerow([p["nome"], p.get("foto") or ""])
    return buf.getvalue().encode("utf-8")


def exportar_disciplinas(discs: list[str]) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["nome"])
    for d in discs:
        w.writerow([d])
    return buf.getvalue().encode("utf-8")


def modelo_professores() -> bytes:
    return MODELO_PROFS.encode("utf-8")


def modelo_disciplinas() -> bytes:
    return MODELO_DISCS.encode("utf-8")