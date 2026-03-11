import streamlit as st
import time
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Executive English Mastery - Fernando Montes",
    page_icon="🦅",
    layout="wide"
)

# --- CSS PERSONALIZADO (Interfaz de Alto Rendimiento) ---
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #1e293b; padding: 10px; border-radius: 15px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #334155; border-radius: 8px; 
        padding: 10px 20px; font-weight: bold; color: #cbd5e1; border: none;
    }
    .stTabs [aria-selected="true"] { background-color: #3b82f6 !important; color: white !important; }
    .executive-card {
        background: #1e293b; padding: 25px; border-radius: 15px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3); border-left: 8px solid #3b82f6;
        margin-bottom: 20px;
    }
    .power-verb-box {
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        padding: 15px; border-radius: 10px; border: 1px solid #3b82f6; margin: 10px 0;
    }
    .badge-tech { background-color: #1e40af; color: #dbeafe; padding: 4px 10px; border-radius: 8px; font-weight: bold; }
    .badge-ops { background-color: #92400e; color: #fef3c7; padding: 4px 10px; border-radius: 8px; font-weight: bold; }
    .badge-compliance { background-color: #065f46; color: #dcfce7; padding: 4px 10px; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS MAESTRA (V1.0 - V9.0) ---
INTEL_DB = {
    "🚀 Pitch & Strategy": [
        {"q": "How do you present the $274k savings at Mercado Libre?", "opts": ["I saved $274k in boxes.", "I successfully delivered $274k in audited hard savings via packaging optimization.", "I reduced cost by $274k.", "I led a project to save money."], "ans": 1, "exp": "'Audited hard savings' es el lenguaje del CFO."},
        {"q": "Define your professional profile for a VP role:", "opts": ["I am a quality manager.", "I am an Operations Strategist specialized in protecting EBITDA.", "I manage people in logistics.", "I am a Green Belt engineer."], "ans": 1, "exp": "Enfocarte en 'EBITDA protection' te eleva a nivel directivo."}
    ],
    "🛠️ IATF, VDA & Core Tools": [
        {"q": "How do you describe 'Risk-based thinking' in an audit?", "opts": ["Thinking about problems.", "A proactive approach to identify and mitigate QMS threats.", "Checking FMEA every day.", "Following ISO 9001 exactly."], "ans": 1, "exp": "Pilar preventivo de la IATF 16949."},
        {"q": "What is VDA 6.3 for Audi/VW?", "opts": ["A German checklist.", "The standard for process maturity and OEM compliance.", "A quality manual for parts.", "A German ISO certification."], "ans": 1, "exp": "'Process maturity' es la métrica clave en VDA."}
    ],
    "📊 SQL, Big Data & IA": [
        {"q": "How do you use SQL in your operations?", "opts": ["I search for info in the DB.", "I execute complex queries to extract raw datasets for real-time KPI monitoring.", "I ask IT for data.", "I search in BigQuery tables."], "ans": 1, "exp": "Describe autonomía técnica y capacidad de análisis estratégica."},
        {"q": "Define Prompt Engineering for Ops Leaders:", "opts": ["Chatting with AI.", "Strategic design of inputs to optimize LLM outputs for automated RCA.", "Writing code in Python.", "Searching in Google."], "ans": 1, "exp": "Se vende como una habilidad de optimización de procesos."}
    ]
}

POWER_VERBS_DRILLS = [
    ("I fixed the problem", "I rectified the non-conformance"),
    ("I saved money", "I delivered substantial hard savings"),
    ("I used data", "I leveraged data analytics to drive decision-making"),
    ("I started a project", "I spearheaded a strategic initiative"),
    ("I talked to the client", "I orchestrated cross-functional negotiations")
]

# --- LÓGICA DE ESTADO ---
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'level' not in st.session_state: st.session_state.level = 1
if 'forged_star' not in st.session_state: st.session_state.forged_star = ""

# --- SIDEBAR ---
with st.sidebar:
    st.title("🦅 Executive Intelligence")
    st.write(f"**Leader:** Fernando Montes")
    st.divider()
    st.metric("Authority Level", f"LVL {st.session_state.level}")
    st.write(f"XP Progress: {st.session_state.xp}/1000")
    st.progress(min(st.session_state.xp / 1000, 1.0))
    st.divider()
    st.subheader("🛠️ Current Tech Stack")
    st.code("SQL | BigQuery | AI\nLean Six Sigma GB\nIATF | VDA 6.3 | NOM", language="text")

# --- UI PRINCIPAL ---
st.title("🛡️ Executive English Mastery App")
st.write("Suite definitiva de entrenamiento para líderes de Operaciones y Calidad.")

tabs = st.tabs(["🔥 The Forge (STAR)", "⚔️ Combat Lab", "🛡️ Audit Defense", "📖 Encyclopedia"])

# --- TAB 1: THE FORGE ---
with tabs[0]:
    st.subheader("🏗️ The Achievement Forge")
    st.write("Forja tus éxitos reales en argumentos de nivel Director.")
    col_in, col_out = st.columns(2)
    with col_in:
        sit = st.text_area("Situation (Contexto):", placeholder="Ej: Crisis de quejas con Audi/VW")
        task = st.text_area("Task (Reto):", placeholder="Ej: Cerrar 20 quejas críticas en 30 días")
        act = st.text_area("Action (Herramienta):", placeholder="Ej: SQL queries, Root Cause Analysis, AI")
        res = st.text_area("Result (Impacto):", placeholder="Ej: $274k ahorrados, 100% IRA")
    with col_out:
        if st.button("✨ Forjar Argumento Directivo"):
            st.session_state.forged_star = f"""
            "During a critical downturn regarding {sit}, I was tasked with {task}. 
            I spearheaded a recovery strategy leveraging {act} to streamline our response. 
            As a result, I successfully delivered {res}, directly impacting the EBITDA and securing our OEM standing."
            """
        if st.session_state.forged_star:
            st.markdown(f"<div class='executive-card'>{st.session_state.forged_star}</div>", unsafe_allow_html=True)
            st.success("Logro convertido a Nivel Director. Memoriza este 'script'.")

# --- TAB 2: COMBAT LAB ---
with tabs[1]:
    st.subheader("⚔️ Power Verb Combat")
    st.write("Sustituye el inglés 'débil' por inglés de 'alto impacto'.")
    if st.button("Get New Drill"):
        st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS)
    if 'current_drill' in st.session_state:
        drill = st.session_state.current_drill
        st.markdown(f"<div class='power-verb-box'>Junior says: <b>'{drill[0]}'</b></div>", unsafe_allow_html=True)
        user_ans = st.text_input("How does an Executive say it? (Usa el Power Verb):")
        if st.button("Neutralize!"):
            if drill[1].lower() in user_ans.lower():
                st.balloons()
                st.success(f"🎯 CORRECT! +100 XP. Phrase: '{drill[1]}'")
                st.session_state.xp += 100
                if st.session_state.xp >= 1000:
                    st.session_state.level += 1
                    st.session_state.xp = 0
            else:
                st.error(f"⚠️ Basic detected. Executive way: '{drill[1]}'")

# --- TAB 3: AUDIT DEFENSE ---
with tabs[2]:
    st.subheader("🛡️ Audit Resistance Simulator")
    mod = st.selectbox("Select Intelligence Module:", list(INTEL_DB.keys()))
    for i, item in enumerate(INTEL_DB[mod]):
        st.write(f"**Scenario {i+1}: {item['q']}**")
        ans = st.radio("Choose your defense:", item['opts'], key=f"audit_{mod}_{i}")
        if st.button("Defend!", key=f"def_{mod}_{i}"):
            if item['opts'].index(ans) == item['ans']:
                st.success("🎯 Auditor Satisfied. Level: COMPLIANT.")
                st.session_state.xp += 50
            else:
                st.error("❌ Finding detected. Too basic. Redesign your speech.")
                st.write(f"**Strategy:** {item['exp']}")

# --- TAB 4: ENCYCLOPEDIA ---
with tabs[3]:
    st.subheader("📖 Technical Encyclopedia")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<span class='badge-ops'>🏭 Ops & Quality</span>", unsafe_allow_html=True)
        st.write("- **IATF 16949:** Quality Management System.")
        st.write("- **VDA 6.3:** Process Audit Standard.")
        st.write("- **Hard Savings:** Audited profit impact.")
        st.write("- **OEE:** Overall Equipment Effectiveness.")
    with c2:
        st.markdown("<span class='badge-tech'>🧬 Tech & Data</span>", unsafe_allow_html=True)
        st.write("- **SQL Query:** Database command.")
        st.write("- **BigQuery:** Data warehouse engine.")
        st.write("- **Predictive Modeling:** Failure forecasting.")
        st.write("- **LLM:** AI Engine (Prompting).")
    with c3:
        st.markdown("<span class='badge-compliance'>⚖️ Compliance</span>", unsafe_allow_html=True)
        st.write("- **NOM:** Official Mexican Standards.")
        st.write("- **ISO 9001:** Quality Governance.")
        st.write("- **CSR:** Customer-Specific Requirements.")
        st.write("- **NC:** Non-conformance.")

st.divider()
st.caption("Custom Coaching System for Fernando Montes | v9.0 Comprehensive Master")
