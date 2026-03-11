import streamlit as st
import time
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Executive English Mastery - Master Blueprint",
    page_icon="🦅",
    layout="wide"
)

# --- ESTILOS PROFESIONALES (Premium Suite) ---
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 12px; background-color: #1e293b; padding: 10px; border-radius: 15px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #334155; border-radius: 10px; 
        padding: 10px 25px; font-weight: 700; color: #cbd5e1; border: none;
    }
    .stTabs [aria-selected="true"] { background-color: #3b82f6 !important; color: white !important; }
    .executive-card {
        background: #1e293b; padding: 30px; border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5); border-left: 8px solid #3b82f6;
        margin-bottom: 25px;
    }
    .power-verb-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white; padding: 15px; border-radius: 12px; margin-bottom: 10px;
    }
    .badge {
        padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold;
        display: inline-block; margin-bottom: 10px;
    }
    .badge-tech { background-color: #dbeafe; color: #1e40af; }
    .badge-ops { background-color: #fef3c7; color: #92400e; }
    .badge-compliance { background-color: #dcfce7; color: #166534; }
    .star-box { background-color: #1e293b; border: 1px solid #3b82f6; padding: 20px; border-radius: 12px; color: #f8fafc; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS MAESTRA (Consolidado Total v1.0 - v9.0) ---
COURSE_DATA = {
    "🚀 M1: Pitch & EBITDA Protection": [
        {
            "q": "How do you present the $274k savings at Mercado Libre to a CEO?",
            "opts": ["I saved $274,000 in shipping boxes.", "I successfully delivered $274k USD in audited hard savings via packaging optimization.", "I reduced cost by 13% in the warehouse.", "I made a project to save $274k."],
            "ans": 1,
            "exp": "'Audited hard savings' es el término financiero que valida tu impacto real ante la dirección."
        },
        {
            "q": "Define your role for a Director-level interview:",
            "opts": ["I am a quality manager with engineering experience.", "I am an Operations Strategize specialized in protecting EBITDA through Lean-IA integration.", "I manage multi-functional teams in logistics.", "I solve quality problems for OEM clients."],
            "ans": 1,
            "exp": "Venderte como 'Strategist' te posiciona como un líder que entiende el negocio, no solo el piso de producción."
        }
    ],
    "🛠️ M2: APQP, VDA 6.3 & IATF 16949": [
        {
            "q": "How do you describe 'Risk-based thinking' in an IATF audit?",
            "opts": ["Thinking about problems before they happen.", "A proactive approach to identify and mitigate QMS threats via PFMEA analysis.", "Checking the quality sheet every day.", "Following the manual instructions exactly."],
            "ans": 1,
            "exp": "Es el núcleo de la norma IATF. Demuestra mentalidad preventiva y dominio de herramientas de calidad."
        },
        {
            "q": "Explain the importance of VDA 6.3 to Audi/VW:",
            "opts": ["It is a German quality checklist.", "It ensures process maturity and full adherence to OEM standards.", "I use it for German car manufacturers.", "It is the equivalent of ISO 9001 in Germany."],
            "ans": 1,
            "exp": "'Process maturity' es el KPI sagrado para los auditores alemanes."
        }
    ],
    "📊 M3: SQL, BigQuery & Statistics": [
        {
            "q": "How do you use SQL in your operations?",
            "opts": ["I look for info in the database.", "I execute complex queries to extract raw datasets for real-time KPI monitoring.", "I ask the IT team for the reports.", "I use computers to analyze the data."],
            "ans": 1,
            "exp": "Muestra autonomía técnica: tú extraes la data, tú la analizas y tú tomas decisiones basadas en ella."
        },
        {
            "q": "Explain a P-value below 0.05 in a Lean project:",
            "opts": ["The result is good.", "The result is statistically significant, allowing us to reject the null hypothesis.", "It means we saved money.", "There is a 5% error in the data."],
            "ans": 1,
            "exp": "Lenguaje de Green Belt: demuestras validez estadística en tus proyectos de mejora continua."
        }
    ],
    "🤖 M4: AI & Prompt Engineering": [
        {
            "q": "How does AI enhance your Quality Management System?",
            "opts": ["AI helps me write emails faster.", "We leverage Generative AI and Prompt Engineering to automate RCA and streamline QMS governance.", "I use ChatGPT to find the rules.", "AI is the future of the factory floor."],
            "ans": 1,
            "exp": "Indica que estás a la vanguardia (QMS 4.0) integrando tecnología avanzada en la gestión de calidad."
        }
    ],
    "🇲🇽 M5: NOM & Compliance": [
        {
            "q": "Why is NOM compliance critical for your role in Mexico?",
            "opts": ["Because it is the law in Mexico.", "Adherence to NOM ensures regulatory compliance and product safety in the local market.", "To avoid government penalties.", "It is a requirement for ISO 9001."],
            "ans": 1,
            "exp": "'Adherence' y 'Regulatory compliance' son las palabras que dan seguridad a una junta directiva internacional."
        }
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
if 'q_idx' not in st.session_state: st.session_state.q_idx = 0
if 'current_mod' not in st.session_state: st.session_state.current_mod = list(COURSE_DATA.keys())[0]

# --- SIDEBAR (STATUS PANEL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.title("Executive Intelligence")
    st.write(f"**Leader:** Fernando Montes Delgado")
    st.divider()
    st.metric("Authority Level", f"LVL {st.session_state.level}")
    st.write(f"XP Progress: {st.session_state.xp}/1000")
    st.progress(min(st.session_state.xp / 1000, 1.0))
    st.divider()
    st.subheader("🛠️ Current Tech Stack")
    st.code("SQL | BigQuery | AI\nLean Six Sigma GB\nIATF | VDA 6.3 | NOM", language="text")

# --- UI PRINCIPAL ---
st.title("🛡️ Executive English Mastery - The Omnibus Edition")
st.write("Estrategia Táctica 360° para Líderes de Operaciones, Calidad y Tech.")

tabs = st.tabs(["🚀 Training Lab", "🔥 The Forge (STAR)", "🛡️ Audit Defense", "📖 Encyclopedia"])

# --- TAB 1: TRAINING LAB ---
with tabs[0]:
    st.subheader("⚔️ Power Verb Combat")
    st.write("Entrena tus reflejos: sustituye inglés básico por inglés de alto impacto.")
    if st.button("Get New Drill"):
        st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS)
    
    if 'current_drill' in st.session_state:
        drill = st.session_state.current_drill
        st.markdown(f"<div class='executive-card'>Junior level says: <b>'{drill[0]}'</b></div>", unsafe_allow_html=True)
        user_ans = st.text_input("How does an Executive say it? (Type the phrase):")
        if st.button("Neutralize!"):
            if drill[1].lower() in user_ans.lower():
                st.balloons()
                st.success(f"🎯 CORRECT! +100 XP. La frase correcta es: '{drill[1]}'")
                st.session_state.xp += 100
                if st.session_state.xp >= 1000:
                    st.session_state.level += 1
                    st.session_state.xp = 0
            else:
                st.error(f"⚠️ Basic detected. El nivel directivo exige: '{drill[1]}'")

# --- TAB 2: THE FORGE ---
with tabs[1]:
    st.subheader("🏗️ Success Story Builder (STAR Method)")
    st.write("Forja tus logros de Mercado Libre, Marelli o Hi-Cone en argumentos de nivel Director.")
    c1, c2 = st.columns(2)
    with c1:
        sit = st.text_area("Situation:", placeholder="Ej: Crisis de quejas con Audi/VW por desviaciones en proceso")
        task = st.text_area("Task:", placeholder="Ej: Cerrar 20 quejas críticas en 30 días para asegurar el contrato")
        act = st.text_area("Action:", placeholder="Ej: SQL queries para identificar el lote, Root Cause Analysis con IA")
        res = st.text_area("Result:", placeholder="Ej: $274k ahorrados auditados, 100% IRA mantenido")
    with c2:
        if st.button("✨ Forjar Argumento Directivo"):
            st.session_state.forged_star = f"""
            "During a critical period regarding {sit}, I was tasked with {task}. 
            I spearheaded a recovery strategy leveraging {act} to streamline our response and ensure compliance. 
            As a result, I successfully delivered {res}, directly impacting the EBITDA and securing our OEM standing."
            """
        if st.session_state.forged_star:
            st.markdown(f"<div class='star-box'>{st.session_state.forged_star}</div>", unsafe_allow_html=True)
            st.info("💡 Tip: Lee este párrafo en voz alta 10 veces frente al espejo para ganar fluidez.")

# --- TAB 3: AUDIT DEFENSE ---
with tabs[2]:
    st.subheader("🛡️ Audit Resistance Simulator")
    mod = st.selectbox("Select Intelligence Module:", list(COURSE_DATA.keys()))
    questions = COURSE_DATA[mod]
    
    if st.session_state.q_idx < len(questions):
        q = questions[st.session_state.q_idx]
        st.write(f"### {q['q']}")
        ans = st.radio("Choose your defense strategy:", q['opts'], key=f"audit_{mod}")
        if st.button("Defend!"):
            if q['opts'].index(ans) == q['ans']:
                st.success("🎯 Auditor Satisfied. Level: COMPLIANT.")
                st.session_state.xp += 50
            else:
                st.error("❌ Finding detected. Too basic for this level.")
                st.write(f"**Strategic Breakdown:** {q['exp']}")
            time.sleep(2)
            st.session_state.q_idx = (st.session_state.q_idx + 1) % len(questions)
            st.rerun()

# --- TAB 4: ENCYCLOPEDIA ---
with tabs[3]:
    st.subheader("📖 The Omnibus Technical Encyclopedia")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<span class='badge badge-ops'>🏭 Ops & Quality</span>", unsafe_allow_html=True)
        st.write("- **IATF 16949:** Automotive QMS Standard.")
        st.write("- **VDA 6.3:** German Process Audit Standard.")
        st.write("- **APQP/PPAP:** Core Launch Tools.")
        st.write("- **Hard Savings:** Audited profit impact.")
    with c2:
        st.markdown("<span class='badge badge-tech'>🧬 Tech & Data</span>", unsafe_allow_html=True)
        st.write("- **SQL Query:** Database command.")
        st.write("- **BigQuery:** Data warehouse engine.")
        st.write("- **Predictive Modeling:** Failure forecasting.")
        st.write("- **LLM:** AI Engine (Prompting).")
    with c3:
        st.markdown("<span class='badge badge-compliance'>⚖️ Compliance</span>", unsafe_allow_html=True)
        st.write("- **NOM:** Official Mexican Standards.")
        st.write("- **ISO 9001:** Quality Governance.")
        st.write("- **CSR:** Customer-Specific Requirements.")

st.divider()
st.caption("Fernando Montes Delgado | Operations & Quality Mastery System | v9.0 Omnibus Edition")
