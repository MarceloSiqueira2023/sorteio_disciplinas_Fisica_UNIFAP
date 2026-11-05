import json

import streamlit as st

import importers
import ui

ui.cabecalho()
st.title("Configurações")

c = st.session_state.cfg
c["instituicao"] = st.text_input("Instituição", c["instituicao"])
c["curso"] = st.text_input("Curso ou colegiado", c["curso"])
st.caption("Tudo aqui é salvo automaticamente em `dados/config.json`.")

aba_p, aba_d, aba_i, aba_s = st.tabs(
    ["Professores", "Disciplinas", "Importar planilhas", "Salvar e carregar"]
)

# ─── Professores ────────────────────────────────────────────────────────
with aba_p:
    with st.form("novo_prof", clear_on_submit=True):
        nome = st.text_input("Nome do professor(a)")
        foto = st.file_uploader("Foto (opcional)", type=["png", "jpg", "jpeg", "webp"])
        st.caption("Para trocar a foto, adicione o mesmo nome com a nova foto.")
        if st.form_submit_button("Salvar professor(a)") and nome.strip():
            nome = nome.strip()
            novo = ui.processar_foto(foto)
            existente = next((p for p in st.session_state.profs if p["nome"] == nome), None)
            if existente:
                existente["foto"] = novo or existente.get("foto")
            else:
                st.session_state.profs.append({"nome": nome, "foto": novo})
            ui.salvar()
            st.rerun()

    st.caption(f"{len(st.session_state.profs)} professor(es) cadastrado(s)")
    for i, p in enumerate(st.session_state.profs):
        a, b, d = st.columns([1, 6, 2], vertical_alignment="center")
        a.markdown(ui.avatar(p, 56), unsafe_allow_html=True)
        b.markdown(f"**{p['nome']}**")
        if d.button("Remover", key=f"rp{i}"):
            st.session_state.profs.pop(i)
            ui.salvar()
            st.rerun()

# ─── Disciplinas ────────────────────────────────────────────────────────
with aba_d:
    with st.form("novas_discs", clear_on_submit=True):
        texto = st.text_area("Disciplinas (uma por linha)", height=160)
        if st.form_submit_button("Adicionar disciplinas"):
            for linha in texto.splitlines():
                if linha.strip() and linha.strip() not in st.session_state.discs:
                    st.session_state.discs.append(linha.strip())
            ui.salvar()
            st.rerun()

    st.caption(f"{len(st.session_state.discs)} disciplina(s) cadastrada(s)")
    for i, disc in enumerate(st.session_state.discs):
        a, b = st.columns([8, 2], vertical_alignment="center")
        a.markdown(disc)
        if b.button("Remover", key=f"rd{i}"):
            st.session_state.discs.pop(i)
            ui.salvar()
            st.rerun()

# ─── Importar planilhas ─────────────────────────────────────────────────
with aba_i:
    st.write("Envie um CSV com os dados. Escolha abaixo se a importação "
             "**substitui** o que já existe ou **mescla** por nome.")
    modo = st.radio("Modo de importação", ["Substituir", "Mesclar por nome"], horizontal=True)

    st.divider()
    st.subheader("Professores")
    col1, col2 = st.columns(2)
    col1.download_button("Baixar modelo em branco (.csv)",
                         importers.modelo_professores(), "professores.csv", "text/csv")
    col2.download_button("Baixar professores atuais (.csv)",
                         importers.exportar_professores(st.session_state.profs),
                         "professores.csv", "text/csv")
    arq_p = st.file_uploader("Planilha de professores (.csv)", type=["csv"], key="csv_prof")
    if arq_p and st.button("Importar professores"):
        try:
            novos, avisos = importers.ler_professores(arq_p)
        except Exception as e:  # noqa: BLE001
            st.error(str(e))
        else:
            if modo == "Substituir":
                st.session_state.profs = novos
            else:
                atuais = {p["nome"]: p for p in st.session_state.profs}
                for n in novos:
                    if n["nome"] in atuais:
                        if n.get("foto"):
                            atuais[n["nome"]]["foto"] = n["foto"]
                    else:
                        st.session_state.profs.append(n)
            ui.salvar()
            st.success(f"{len(novos)} professor(es) importado(s).")
            for a in avisos:
                st.warning(a)
            st.rerun()

    st.divider()
    st.subheader("Disciplinas")
    col1, col2 = st.columns(2)
    col1.download_button("Baixar modelo em branco (.csv)",
                         importers.modelo_disciplinas(), "disciplinas.csv", "text/csv")
    col2.download_button("Baixar disciplinas atuais (.csv)",
                         importers.exportar_disciplinas(st.session_state.discs),
                         "disciplinas.csv", "text/csv")
    arq_d = st.file_uploader("Planilha de disciplinas (.csv)", type=["csv"], key="csv_disc")
    if arq_d and st.button("Importar disciplinas"):
        try:
            novas = importers.ler_disciplinas(arq_d)
        except Exception as e:  # noqa: BLE001
            st.error(str(e))
        else:
            if modo == "Substituir":
                st.session_state.discs = novas
            else:
                for d in novas:
                    if d not in st.session_state.discs:
                        st.session_state.discs.append(d)
            ui.salvar()
            st.success(f"{len(novas)} disciplina(s) importada(s).")
            st.rerun()

# ─── Salvar e carregar ──────────────────────────────────────────────────
with aba_s:
    st.write("Para levar os dados a outra máquina, baixe o JSON abaixo. "
             "Na máquina nova, use o botão de carregar.")
    dados_json = json.dumps(
        {k: st.session_state[k] for k in ("cfg", "profs", "discs")},
        ensure_ascii=False, indent=2,
    )
    st.download_button("Baixar configuração (.json)", dados_json,
                       "sorteio-config.json", "application/json")
    arq = st.file_uploader("Carregar configuração (.json)", type="json")
    if arq and st.button("Aplicar configuração"):
        d = json.load(arq)
        for k in ("cfg", "profs", "discs"):
            if k in d:
                st.session_state[k] = d[k]
        ui.salvar()
        st.rerun()