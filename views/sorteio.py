import random
import time
from collections import Counter
from html import escape

import pandas as pd
import streamlit as st

import core
import ui

ui.cabecalho()
st.title("Sorteio de disciplinas")

profs = {p["nome"]: p for p in st.session_state.profs}
log = st.session_state.log
anulados_set = core.anulados(log)
sorteadas = core.disciplinas_sorteadas(log)
pendentes = [d for d in st.session_state.discs if d not in sorteadas]

if not profs or not st.session_state.discs:
    st.info("Cadastre professores e disciplinas em Configurações para começar.")
    st.stop()

if pendentes:
    disc = st.selectbox("Disciplina a sortear", pendentes)
    pool = st.multiselect("Professores neste sorteio", list(profs), default=list(profs))
    palco = st.empty()
    if st.button("Sortear", type="primary", disabled=not pool):
        fim = time.time() + 3
        while time.time() < fim:  # animação apenas visual; o sorteio real é core.sortear
            palco.markdown(ui.cartao(profs[random.choice(pool)], "Sorteando"), unsafe_allow_html=True)
            time.sleep(0.1)
        seed = core.novo_seed()
        ganhador = core.sortear(pool, seed)
        core.registrar(log, disc, pool, seed, ganhador)
        ui.salvar()
        palco.markdown(ui.cartao(profs[ganhador], f"{disc} ficou com", fim=True), unsafe_allow_html=True)
else:
    st.success("Todas as disciplinas foram sorteadas.")

if log:
    st.header("Resultado")
    ativos = [e for e in log
              if e.get("tipo", "sorteio") == "sorteio" and e["n"] not in anulados_set]

    for e in reversed(ativos):
        p = profs.get(e["ganhador"], {"nome": e["ganhador"]})
        a, b = st.columns([8, 2], vertical_alignment="center")
        a.markdown(
            f'<div class="linha">{ui.avatar(p, 44)}<span>{escape(e["disciplina"])}</span>'
            f'<b>{escape(e["ganhador"])}</b></div>', unsafe_allow_html=True)
        if b.button("Anular", key=f"anular_{e['n']}"):
            core.registrar_anulacao(log, e["n"], motivo="Refazer sorteio")
            ui.salvar()
            st.rerun()

    if ativos:
        st.subheader("Disciplinas por professor")
        st.bar_chart(pd.Series(Counter(e["ganhador"] for e in ativos)))
        csv = pd.DataFrame(ativos)[["disciplina", "ganhador"]].to_csv(index=False)
        st.download_button("Baixar resultado (CSV)", csv, "sorteio.csv", "text/csv")