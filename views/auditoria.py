import inspect
import json

import pandas as pd
import streamlit as st

import core
import ui

ui.cabecalho()
st.title("Auditoria")
st.write("Cada sorteio guarda o seed, os participantes e o hash do registro anterior. "
         "Anulações também entram na cadeia, para que o histórico nunca seja reescrito. "
         "Qualquer pessoa pode refazer o cálculo e chegar ao mesmo ganhador.")

log = st.session_state.log
if log:
    resultados = core.verificar(log)
    if all(ok for _, ok in resultados):
        st.success(f"{len(log)} registro(s) conferidos; cadeia de hashes íntegra.")
    else:
        st.error("Inconsistência nos registros: "
                 + ", ".join(str(n) for n, ok in resultados if not ok))

    df = pd.DataFrame(log)
    if "tipo" not in df.columns:
        df["tipo"] = "sorteio"
    df["tipo"] = df["tipo"].fillna("sorteio")

    anulados_set = core.anulados(log)

    def _status(row):
        if row["tipo"] == "anulacao":
            return "—"
        return "anulado" if row["n"] in anulados_set else "ativo"

    df["status"] = df.apply(_status, axis=1)

    cols = [c for c in ["n", "quando", "tipo", "disciplina", "ganhador",
                        "status", "ref", "motivo", "seed", "hash"] if c in df.columns]
    st.dataframe(df[cols], hide_index=True)

    n_ativos = sum(1 for s in df["status"] if s == "ativo")
    n_anul = sum(1 for s in df["status"] if s == "anulado")
    n_reg = sum(1 for t in df["tipo"] if t == "anulacao")
    st.caption(f"{n_ativos} sorteio(s) ativo(s), {n_anul} anulado(s), "
               f"{n_reg} anulação(ões) na cadeia.")

    st.download_button("Baixar registro (JSON)", json.dumps(log, ensure_ascii=False, indent=2),
                       "auditoria.json", "application/json")

    ult = next((e for e in reversed(log)
                if e.get("tipo", "sorteio") == "sorteio" and e["n"] not in anulados_set), None)
    if ult:
        st.subheader("Verificar o último sorteio ativo por conta própria")
        st.code(f"import random\n"
                f"participantes = {ult['participantes']!r}\n"
                f"print(random.Random({ult['seed']!r}).choice(sorted(participantes)))  # {ult['ganhador']}",
                language="python")
else:
    st.info("Nenhum sorteio realizado ainda.")

st.subheader("Código-fonte do sorteio (core.py)")
st.code(inspect.getsource(core), language="python")