import streamlit as st
import re
import random
from itertools import product
import pandas as pd

st.set_page_config(page_title="Calculadora Tabla de la Verdad", layout="centered")

# ---------------------------------------------------------------
# DATOS
# ---------------------------------------------------------------
INTEGRANTES = [
    "Melany Briggite Guzmán Macias",
    "Edison Franchesco Morales Piza",
    "Elkin Javier Morocho Gordillo",
]

# ---------------------------------------------------------------
# FONDO: cielo nocturno con estrellas parpadeantes + lluvia Matrix
# (semilla fija para que no cambie en cada clic)
# ---------------------------------------------------------------
rng = random.Random(7)

# Estrellas que parpadean
estrellas_html = ""
for _ in range(110):
    left = rng.uniform(0, 100)
    top = rng.uniform(0, 100)
    size = rng.choice([1, 1, 2, 2, 3])
    dur = rng.uniform(1.8, 5.0)
    delay = rng.uniform(0, 5)
    estrellas_html += (
        f'<span class="estrella" style="left:{left:.1f}vw; top:{top:.1f}vh; '
        f'width:{size}px; height:{size}px; '
        f'animation-duration:{dur:.1f}s; animation-delay:-{delay:.1f}s;"></span>'
    )

# Lluvia de código estilo Matrix
CARACTERES = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホ0123456789"
N_COLUMNAS = 32
matrix_html = ""
for i in range(N_COLUMNAS):
    left = i * (100 / N_COLUMNAS) + rng.uniform(0, 1.5)
    dur = rng.uniform(7, 16)
    delay = rng.uniform(0, 12)
    size = rng.choice([14, 16, 18])
    texto = "<br>".join(rng.choice(CARACTERES) for _ in range(22))
    matrix_html += (
        f'<div class="matrix-col" style="left:{left:.1f}vw; font-size:{size}px; '
        f'line-height:{size + 4}px; animation-duration:{dur:.1f}s; '
        f'animation-delay:-{delay:.1f}s;">{texto}</div>'
    )

integrantes_html = "".join(f"<li>{n}</li>" for n in INTEGRANTES)

CSS = """
<style>
/* Cielo nocturno */
.stApp {
    background: radial-gradient(ellipse at 50% 120%, #1b1040 0%, #0b1330 45%, #020617 100%);
    background-attachment: fixed;
}
header[data-testid="stHeader"] { background: transparent; }

/* Estrellas parpadeantes */
.estrella {
    position: fixed;
    background: #ffffff;
    border-radius: 50%;
    box-shadow: 0 0 6px 1px rgba(255, 255, 255, 0.8);
    pointer-events: none;
    z-index: 0;
    animation-name: parpadeo;
    animation-iteration-count: infinite;
    animation-timing-function: ease-in-out;
}
@keyframes parpadeo {
    0%, 100% { opacity: 0.15; transform: scale(0.7); }
    50%      { opacity: 1;    transform: scale(1.4); }
}

/* Lluvia Matrix */
.matrix-col {
    position: fixed;
    top: 0;
    font-family: "Courier New", monospace;
    font-weight: bold;
    text-align: center;
    white-space: nowrap;
    pointer-events: none;
    z-index: 0;
    opacity: 0.55;
    background: linear-gradient(to bottom, rgba(0,255,65,0) 0%, rgba(0,255,65,0.6) 70%, #b8ffc9 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    animation-name: caer;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
}
@keyframes caer {
    from { transform: translateY(-110%); }
    to   { transform: translateY(100vh); }
}

/* Contenido por encima del fondo */
.block-container { position: relative; z-index: 1; }
.stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label,
.stApp span, .stApp li { color: #e6fff0; }

/* Botones */
.stButton > button,
.stDownloadButton > button {
    background: rgba(0, 20, 10, 0.65);
    color: #00ff41;
    border: 1px solid rgba(0, 255, 65, 0.45);
    backdrop-filter: blur(6px);
    transition: all 0.2s ease;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    background: rgba(0, 255, 65, 0.25);
    border-color: #00ff41;
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 0 12px rgba(0, 255, 65, 0.5);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #00b34a, #00ff41);
    color: #00220d;
    border: none;
    font-weight: bold;
}

.stDownloadButton > button p { color: inherit; }

/* Panel de integrantes (derecha) */
.panel-integrantes {
    position: fixed;
    top: 90px;
    right: 24px;
    width: 250px;
    padding: 18px 20px;
    border-radius: 16px;
    background: rgba(0, 15, 10, 0.55);
    border: 1px solid rgba(0, 255, 65, 0.4);
    backdrop-filter: blur(10px);
    box-shadow: 0 0 24px rgba(0, 255, 65, 0.25);
    z-index: 5;
}
.panel-integrantes h4 {
    margin: 0 0 10px 0;
    color: #00ff41;
    font-size: 1.05rem;
    letter-spacing: 1px;
}
.panel-integrantes ul { list-style: none; margin: 0; padding: 0; }
.panel-integrantes li {
    padding: 8px 0;
    border-bottom: 1px solid rgba(0, 255, 65, 0.2);
    font-size: 0.92rem;
    color: #ffffff;
}
.panel-integrantes li:last-child { border-bottom: none; }

/* En pantallas pequeñas el panel pasa a ser un bloque normal */
@media (max-width: 1250px) {
    .panel-integrantes {
        position: relative;
        top: 0;
        right: 0;
        width: auto;
        margin-bottom: 16px;
    }
}
/* Título con letras animadas (ola + neón) */
.titulo-animado {
    font-family: "Courier New", monospace;
    font-size: clamp(1.1rem, 3.4vw, 1.8rem);
    font-weight: 800;
    text-align: center;
    margin: 0 0 4px 0;
    line-height: 1.3;
}
.titulo-animado .emoji { display: inline-block; margin-right: 8px; animation: girar 4s linear infinite; }
.titulo-animado .palabra { display: inline-block; white-space: nowrap; }
.titulo-animado .letra {
    display: inline-block;
    color: #00ff41;
    animation: ola 2.4s ease-in-out infinite;
}
@keyframes ola {
    0%, 100% { transform: translateY(0);    color: #00ff41; text-shadow: 0 0 4px #00ff41; }
    50%      { transform: translateY(-8px); color: #eafff0;
               text-shadow: 0 0 6px #ffffff, 0 0 18px #00ff41, 0 0 34px #00ff41; }
}
@keyframes girar {
    0%, 100% { transform: rotate(-12deg) scale(1); }
    50%      { transform: rotate(12deg) scale(1.2); }
}

/* Frase que se escribe sola con cursor parpadeante */
.maquina {
    display: block;
    width: 21ch;
    margin: 0 auto 18px auto;
    overflow: hidden;
    white-space: nowrap;
    font-family: "Courier New", monospace;
    font-size: 1.05rem;
    color: #00ff41;
    border-right: 3px solid #00ff41;
    animation: escribir 6s steps(21, end) infinite, cursor 0.7s step-end infinite;
}
@keyframes escribir {
    0%   { width: 0; }
    55%  { width: 21ch; }
    90%  { width: 21ch; }
    100% { width: 0; }
}
@keyframes cursor {
    0%, 100% { border-color: #00ff41; }
    50%      { border-color: transparent; }
}

/* Subtítulos con brillo neón */
.stApp h2, .stApp h3 { text-shadow: 0 0 8px rgba(0, 255, 65, 0.55); }
</style>
"""

PANEL = f"""
<div class="panel-integrantes">
    <h4>👥 INTEGRANTES</h4>
    <ul>{integrantes_html}</ul>
</div>
"""

st.markdown(CSS + estrellas_html + matrix_html + PANEL, unsafe_allow_html=True)

# ---------------------------------------------------------------
# INTERFAZ
# ---------------------------------------------------------------
TITULO = "Calculadora de Tabla de la Verdad"
palabras_html = []
idx = 0
for palabra in TITULO.split(" "):
    spans = ""
    for c in palabra:
        spans += f'<span class="letra" style="animation-delay:{idx * 0.08:.2f}s">{c}</span>'
        idx += 1
    idx += 1  # espacio
    palabras_html.append(f'<span class="palabra">{spans}</span>')
letras = " ".join(palabras_html)
st.markdown(
    f'<h1 class="titulo-animado"><span class="emoji">🧬</span>{letras}</h1>'
    '<span class="maquina">Lógica binaria: 0 y 1</span>',
    unsafe_allow_html=True,
)
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

    # Generamos combinaciones en 0/1, de mayor a menor (1 primero)
    for valores in product([1, 0], repeat=len(variables)):
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
