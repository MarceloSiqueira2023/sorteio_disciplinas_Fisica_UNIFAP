# Sorteio de disciplinas

Sorteio auditável de disciplinas entre professores. Configurável para qualquer curso: nome da instituição, professores (com foto redonda opcional) e disciplinas.

- **Sorteio**: escolha a disciplina, os professores participantes e sorteie.
- **Configurações**: cadastro manual, importação e exportação em JSON.
- **Auditoria**: mostra o `core.py`, refaz cada sorteio a partir do seed e confere a cadeia SHA-256.

## Rodar (Python 3.12, Ubuntu)

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Publicar na Streamlit Cloud

Suba o repositório no GitHub e aponte o deploy para `app.py`. Os dados ficam na sessão do navegador: baixe a configuração e o registro de auditoria ao terminar.
