import streamlit as st
import re
import random
from itertools import product
import pandas as pd

st.set_page_config(page_title="Calculadora Tabla de la Verdad", layout="centered")

# ---------------------------------------------------------------
# ESTILOS: fondo animado + panel de integrantes a la derecha
# ---------------------------------------------------------------
INTEGRANTES = [
    "Melany Briggite Guzmán Macias",
    "Edison Franchesco Morales Piza",
    "Elkin Javier Morocho Gordillo",
]

# Dígitos 0/1 flotantes (semilla fija para que no cambien en cada clic)
rng = random.Random(42)
digitos_html = ""
for _ in range(30):
    d = rng.choice(["0", "1"])
    left = rng.randint(0, 98)
    size = rng.randint(16, 42)
    dur = rng.randint(10, 24)
    delay = rng.randint(0, 15)
    digitos_html += (
        f'<span class="bit" style="left:{left}vw; font-size:{size}px; '
        f'animation-duration:{dur}s; animation-delay:-{delay}s;">{d}</span>'
    )

integrantes_html = "".join(f"<li>{n}</li>" for n in INTEGRANTES)

st.markdown(
    f"""
    <style>
    /* Fondo degradado animado */
    .stApp {{
        background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1a1a40, #3a1c71);
        background-size: 400% 400%;
        animation: gradientBG 18s ease infinite;
    }}
    @keyframes gradientBG {{
        0%   {{ background-position: 0% 50%; }}
        50%  {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Header transparente */
    header[data-testid="stHeader"] {{ background: transparent; }}

    /* Dígitos 0 y 1 flotando */
    .bit {{
        position: fixed;
        bottom: -60px;
        color: rgba(0, 255, 200, 0.25);
        font-family: monospace;
        font-weight: bold;
        pointer-events: none;
        z-index: 0;
        animation-name: subir;
        animation-timing-function: linear;
        animation-iteration-count: infinite;
    }}
    @keyframes subir {{
        0%   {{ transform: translateY(0) rotate(0deg); opacity: 0; }}
        10%  {{ opacity: 1; }}
        90%  {{ opacity: 1; }}
        100% {{ transform: translateY(-115vh) rotate(360deg); opacity: 0; }}
    }}

    /* Contenido por encima del fondo y texto claro */
    .block-container {{ position: relative; z-index: 1; }}
    .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label,
    .stApp span, .stApp li {{ color: #f1f5f9; }}

    /* Botones */
    .stButton > button {{
        background: rgba(255, 255, 255, 0.10);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.30);
        backdrop-filter: blur(6px);
        transition: all 0.2s ease;
    }}
    .stButton > button:hover {{
        background: rgba(0, 255, 200, 0.25);
        border-color: #00ffc8;
        transform: translateY(-2px);
    }}
    .stButton > button[kind="primary"] {{
        background: linear-gradient(90deg, #00c6ff, #7b2ff7);
        border: none;
    }}

    /* Panel de integrantes (derecha) */
    .panel-integrantes {{
        position: fixed;
        top: 90px;
        right: 24px;
        width: 250px;
        padding: 18px 20px;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.10);
        border: 1px solid rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
        z-index: 5;
    }}
    .panel-integrantes h4 {{
        margin: 0 0 10px 0;
        color: #00ffc8;
        font-size: 1.05rem;
        letter-spacing: 1px;
    }}
    .panel-integrantes ul {{
        list-style: none;
        margin: 0;
        padding: 0;
    }}
    .panel-integrantes li {{
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.15);
        font-size: 0.92rem;
        color: #ffffff;
    }}
    .panel-integrantes li:last-child {{ border-bottom: none; }}

    /* En pantallas pequeñas el panel pasa a ser un bloque normal */
    @media (max-width: 1250px) {{
        .panel-integrantes {{
            position: relative;
            top: 0;
            right: 0;
            width: auto;
            margin-bottom: 16px;
        }}
    }}
    </style>

    {digitos_html}

    <div class="panel-integrantes">
        <h4>👥 INTEGRANTES</h4>
        <ul>{integrantes_html}</ul>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# INTERFAZ
# ---------------------------------------------------------------
st.title("🧬 Calculadora de Tabla de la Verdad")
st.markdown("Construye tu expresión haciendo clic. El resultado se mostrará **exclusivamente en 0 y 1**.")

# --- Estado de la sesión ---
if "expr" not in st.session_state:
    st.session_state.expr = ""

# --- UI: Constructor de Expresión ---
st.subheader("🛠️ Constructor de Expresión")

cols = st.columns(6)
variables = ["A", "B", "C", "D", "E", "F"]
for i, v in enumerate(variables):
    with cols[i % 6]:
        if st.button(f"{v}", key=f"btn_{v}", use_container_width=True):
            st.session_state.expr += f" {v} "

st.markdown("---")

st.subheader("➕ Operadores")

cols = st.columns(6)
operadores = ["AND", "OR", "NOT", "XOR", "->", "<->", "(", ")"]
for i, op in enumerate(operadores):
    with cols[i % 6]:
        if st.button(f"{op}", key=f"btn_{op}", use_container_width=True):
            if op == "NOT":
                st.session_state.expr += " NOT "
            elif op in ["(", ")"]:
                st.session_state.expr += f"{op}"
            else:
                st.session_state.expr += f" {op} "

col_limpiar, col_preview, col_gen = st.columns([2, 3, 2])

with col_limpiar:
    if st.button("🗑️ Limpiar", type="secondary", use_container_width=True):
        st.session_state.expr = ""

with col_preview:
    st.code(st.session_state.expr.strip() or "(vacío)", language="text")

# --- Lógica Central ---
def normalizar_expresion(expr: str) -> str:
    e = expr.strip().upper()
    e = re.sub(r'\bAND\b', ' and ', e)
    e = re.sub(r'\bOR\b', ' or ', e)
    e = re.sub(r'\bNOT\b', ' not ', e)
    e = re.sub(r'\bXOR\b', ' ^ ', e)

    # Implicación y Bicondicional
    e = re.sub(r'([A-Z])\s*->\s*([A-Z])', r'(not \1 or \2)', e)
    e = re.sub(r'([A-Z])\s*<->\s*([A-Z])', r'(\1 == \2)', e)

    return re.sub(r'\s+', ' ', e).strip()

def extraer_variables(expr: str) -> list:
    return sorted(set(re.findall(r'\b[A-Z]\b', expr)))

def generar_tabla(expr_raw: str):
    if not expr_raw.strip():
        return [], []

    expr_norm = normalizar_expresion(expr_raw)
    variables = extraer_variables(expr_norm)

    if not variables:
        return [], []

    tabla = []

    # Generamos combinaciones directamente en 0/1
    for valores in product([0, 1], repeat=len(variables)):
        entorno = {v: bool(val) for v, val in zip(variables, valores)}
        try:
            resultado = eval(expr_norm, {"__builtins__": {}}, entorno)
            # Lista plana [0, 1, 0] en lugar de ([0, 1], 0)
            fila = list(valores) + [int(bool(resultado))]
            tabla.append(fila)
        except Exception:
            return [], []

    return variables, tabla

# --- Ejecución ---
if st.button("🚀 Generar Tabla", type="primary", use_container_width=True):
    if not st.session_state.expr.strip():
        st.warning("⚠️ Ingresa o construye una expresión primero.")
    else:
        vars, tabla = generar_tabla(st.session_state.expr)

        if not vars:
            st.error("❌ Expresión inválida o sin variables detectadas.")
        else:
            cols_df = vars + ["Resultado"]
            df = pd.DataFrame(tabla, columns=cols_df)

            st.success(f"✅ Tabla generada para {len(vars)} variable(s)")
            st.dataframe(df, use_container_width=True, hide_index=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Descargar CSV", csv, "tabla_verdad.csv", "text/csv")
