import base64
import io
from html import escape

import streamlit as st
from PIL import Image, ImageOps

import storage

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700;9..144,800&family=Instrument+Sans:wght@400;500;600&display=swap');
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp button {font-family:'Instrument Sans',sans-serif}
.stApp p, .stApp li, .stApp label {font-size:1.15rem}
.stApp h1, .stApp h2, .stApp h3 {font-family:'Fraunces',serif;font-weight:800;letter-spacing:-.01em}
.stApp h1 {font-size:3rem}
.stApp h2 {font-size:2rem}
.block-container {max-width:1000px;padding-top:2.5rem}
.inst {color:#9aa7bd;font-size:1.05rem;margin-bottom:.2rem}
.stButton>button, .stDownloadButton>button {width:100%;border-radius:12px;font-size:1.15rem}
[data-testid="stBaseButton-primary"] {min-height:3.6rem;font-size:1.4rem;background:#e2b155;color:#0f1a2e;font-weight:700;border:0}
.av {display:block;margin:0 auto;border-radius:50%;object-fit:cover;border:3px solid #e2b155}
.ini {display:flex;align-items:center;justify-content:center;margin:0 auto;border-radius:50%;background:#26385a;color:#e2b155;font-family:'Fraunces',serif;font-weight:800;border:3px solid #e2b155}
.winner {text-align:center;padding:2.5rem 1rem;border:2px solid #e2b155;border-radius:6px;background:#16233b;margin:1rem 0 2rem}
.winner .rot {color:#9aa7bd;font-size:1.2rem;margin:1.2rem 0 .3rem}
.winner .nome {font-family:'Fraunces',serif;font-size:3.2rem;font-weight:800;line-height:1.1}
.linha {display:flex;align-items:center;gap:1rem;padding:.7rem 0;border-bottom:1px solid #2a3a58;font-size:1.2rem}
.linha span {flex:1}
.linha b {font-weight:600;color:#e2b155}
.linha .av, .linha .ini {margin:0;flex:none;border-width:2px}
@media (prefers-reduced-motion:no-preference) {.winner.fim {animation:pop .5s ease-out}}
@keyframes pop {from {transform:scale(.96);opacity:.4} to {transform:none;opacity:1}}
</style>
"""


def init():
    st.session_state.setdefault("cfg", {"instituicao": "Nome da Instituição", "curso": "Nome do Curso"})
    for k in ("profs", "discs", "log"):
        st.session_state.setdefault(k, [])
    if not st.session_state.get("_carregado"):
        dados = storage.carregar()
        for k in ("cfg", "profs", "discs", "log"):
            if dados.get(k) is not None:
                st.session_state[k] = dados[k]
        st.session_state["_carregado"] = True
    st.markdown(CSS, unsafe_allow_html=True)


def salvar():
    """Grava o estado atual em dados/config.json."""
    storage.salvar(st.session_state)


def cabecalho():
    c = st.session_state.cfg
    st.markdown(f'<div class="inst">{escape(c["instituicao"])}, {escape(c["curso"])}</div>',
                unsafe_allow_html=True)


def processar_foto(arquivo) -> str | None:
    if arquivo is None:
        return None
    img = ImageOps.exif_transpose(Image.open(arquivo)).convert("RGB")
    img = ImageOps.fit(img, (200, 200))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def avatar(prof: dict, tam: int = 64) -> str:
    if prof.get("foto"):
        return (f'<img class="av" src="data:image/jpeg;base64,{prof["foto"]}" '
                f'style="width:{tam}px;height:{tam}px">')
    palavras = [w for w in prof["nome"].split() if w[0].isalpha() and w[0].isupper()] or prof["nome"].split()
    ini = escape("".join(w[0] for w in palavras[:2]).upper())
    return (f'<div class="ini" style="width:{tam}px;height:{tam}px;font-size:{int(tam * .4)}px">{ini}</div>')


def cartao(prof: dict, rotulo: str, fim: bool = False) -> str:
    return (f'<div class="winner{" fim" if fim else ""}">{avatar(prof, 160)}'
            f'<div class="rot">{escape(rotulo)}</div>'
            f'<div class="nome">{escape(prof["nome"])}</div></div>')