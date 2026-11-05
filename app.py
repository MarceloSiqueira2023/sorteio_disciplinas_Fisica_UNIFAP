import streamlit as st

st.set_page_config(page_title="Sorteio de disciplinas", page_icon="🎲", layout="wide")

import ui  # noqa: E402

ui.init()

pagina = st.navigation([
    st.Page("views/sorteio.py", title="Sorteio", icon="🎲", default=True),
    st.Page("views/config.py", title="Configurações", icon="⚙️"),
    st.Page("views/auditoria.py", title="Auditoria", icon="🔍"),
])

with st.sidebar:
    if st.button("Arquivar log e reiniciar cadeia"):
        if st.session_state.log:
            import storage
            arq = storage.arquivar_log(st.session_state.log)
            st.session_state.log = []
            ui.salvar()
            st.success(f"Log arquivado em {arq.name}")
        st.rerun()
    st.caption("Desenvolvido por Marcelo Siqueira")

pagina.run()