"""Lógica do sorteio. Este arquivo inteiro é exibido na página de Auditoria.

Como o resultado é decidido:
1. Um seed aleatório é gerado com `secrets` (fonte criptográfica do sistema).
2. O ganhador é `random.Random(seed).choice(...)` sobre a lista ORDENADA
   de participantes. Mesmo seed + mesmos participantes = mesmo ganhador.
3. Cada registro é gravado com o hash do anterior (cadeia SHA-256):
   alterar qualquer registro depois quebra a verificação.

Anulação:
   Um sorteio nunca é apagado. Em vez disso, uma entrada `tipo="anulacao"`
   é acrescentada à cadeia, referenciando o `n` do sorteio anulado. A
   disciplina volta a ficar pendente, mas o histórico permanece intacto
   e verificável.
"""
import hashlib
import json
import random
import secrets
from datetime import datetime

ZERO = "0" * 64


def novo_seed() -> str:
    return secrets.token_hex(16)


def sortear(participantes: list[str], seed: str) -> str:
    return random.Random(seed).choice(sorted(participantes))


def _hash(entrada: dict) -> str:
    corpo = {k: v for k, v in entrada.items() if k != "hash"}
    texto = json.dumps(corpo, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(texto.encode()).hexdigest()


def registrar(log: list, disciplina: str, participantes: list[str],
              seed: str, ganhador: str) -> dict:
    entrada = {
        "n": len(log) + 1,
        "tipo": "sorteio",
        "quando": datetime.now().isoformat(timespec="seconds"),
        "disciplina": disciplina,
        "participantes": sorted(participantes),
        "seed": seed,
        "ganhador": ganhador,
        "anterior": log[-1]["hash"] if log else ZERO,
    }
    entrada["hash"] = _hash(entrada)
    log.append(entrada)
    return entrada


def registrar_anulacao(log: list, n_sorteio: int, motivo: str = "") -> dict:
    """Registra a anulação de um sorteio — preserva o histórico na cadeia."""
    if any(e.get("tipo") == "anulacao" and e.get("ref") == n_sorteio for e in log):
        raise ValueError(f"Sorteio {n_sorteio} já está anulado.")
    if not any(e.get("n") == n_sorteio and e.get("tipo", "sorteio") == "sorteio" for e in log):
        raise ValueError(f"Sorteio {n_sorteio} não existe.")
    entrada = {
        "n": len(log) + 1,
        "tipo": "anulacao",
        "quando": datetime.now().isoformat(timespec="seconds"),
        "ref": n_sorteio,
        "motivo": motivo or "Refazer sorteio",
        "anterior": log[-1]["hash"] if log else ZERO,
    }
    entrada["hash"] = _hash(entrada)
    log.append(entrada)
    return entrada


def anulados(log: list) -> set[int]:
    """Conjunto dos `n` de sorteios anulados."""
    return {e["ref"] for e in log if e.get("tipo") == "anulacao"}


def disciplinas_sorteadas(log: list) -> set[str]:
    """Disciplinas com sorteio ativo (não anulado)."""
    anul = anulados(log)
    return {
        e["disciplina"]
        for e in log
        if e.get("tipo", "sorteio") == "sorteio" and e["n"] not in anul
    }


def verificar(log: list) -> list[tuple[int, bool]]:
    """Refaz cada sorteio e confere a cadeia de hashes.
    Entradas 'anulacao' só conferem a integridade do hash."""
    resultado, anterior = [], ZERO
    for e in log:
        ok_base = e["anterior"] == anterior and e["hash"] == _hash(e)
        if e.get("tipo") == "anulacao":
            ok = ok_base
        else:
            ok = ok_base and e["ganhador"] == sortear(e["participantes"], e["seed"])
        resultado.append((e["n"], ok))
        anterior = e["hash"]
    return resultado