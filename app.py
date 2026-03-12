import streamlit as st
import requests
import time
import random
import streamlit.components.v1 as components
from google.cloud import firestore

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Executive Mastery SaaS", 
    page_icon="⚙️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONFIGURACIÓN DE PERSISTENCIA (FIRESTORE) ---
# Extraemos el ID de la aplicación de los secretos del entorno
app_id = getattr(st.secrets, "__app_id", "war-room-executive-fernando")

def get_db():
    try:
        # En Streamlit Cloud, esto detecta las credenciales automáticamente
        return firestore.Client()
    except Exception:
        return None

db = get_db()

def save_user_progress():
    """Guarda el estado actual del usuario en la base de datos de la nube."""
    if not db or not st.session_state.get("user_name"):
        return
    
    user_id = st.session_state.user_name.lower().replace(" ", "_")
    # Regla 1: Ruta estricta para datos públicos del artefacto
    # Path: /artifacts/{appId}/public/data/users/{userId}
    doc_ref = db.collection("artifacts").document(app_id).collection("public").document("data").collection("users").document(user_id)
    
    data = {
        "user_name": st.session_state.user_name,
        "user_area": st.session_state.user_area,
        "english_level": st.session_state.english_level,
        "xp": st.session_state.xp,
        "current_day": st.session_state.current_day,
        "placement_completed": st.session_state.get("placement_completed", False),
        "placement_eval_detailed": st.session_state.get("placement_eval_detailed", ""),
        "last_update": firestore.SERVER_TIMESTAMP
    }
    doc_ref.set(data)

def load_user_progress(name):
    """Busca en la nube si el usuario ya tiene un historial guardado."""
    if not db:
        return False
    
    user_id = name.lower().replace(" ", "_")
    doc_ref = db.collection("artifacts").document(app_id).collection("public").document("data").collection("users").document(user_id)
    doc = doc_ref.get()
    
    if doc.exists:
        u = doc.to_dict()
        st.session_state.user_name = u["user_name"]
        st.session_state.user_area = u["user_area"]
        st.session_state.english_level = u["english_level"]
        st.session_state.xp = u["xp"]
        st.session_state.current_day = u["current_day"]
        st.session_state.placement_completed = u.get("placement_completed", False)
        st.session_state.placement_eval_detailed = u.get("placement_eval_detailed", "")
        return True
    return False

# --- PSICOLOGÍA DE COLOR Y DISEÑO (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em; 
        background: linear-gradient(90deg, #f59e0b 0%, #f97316 100%);
        color: #0f172a !important; font-weight: 900; font-size: 1.1em; border: none;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(245, 158, 11, 0.4); }
    .executive-card {
        background-color: #1e293b; padding: 30px; border-radius: 15px; border-left: 6px solid #3b82f6; margin-bottom: 20px;
    }
    .level-box {
        background-color: #064e3b; padding: 30px; border-radius: 15px; border-left: 6px solid #10b981; color: #ecfdf5; text-align: center;
    }
    .day-card {
        background-color: #1e293b; padding: 20px; border-radius: 15px; border: 2px solid #334155; margin-bottom: 15px;
    }
    .day-active { border-color: #f59e0b; background-color: #451a03; box-shadow: 0 0 15px rgba(245, 158, 11, 0.3); }
    </style>
""", unsafe_allow_html=True)

# --- COMPONENTES MULTIMEDIA ---
def st_speech_to_text(key):
    script = """
    <script>
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    function startDictation() { recognition.start(); }
    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: text, key: '""" + key + """'}, '*');
    };
    </script>
    <div style="text-align: center;"><button onclick="startDictation()" style="background: #f59e0b; padding: 10px 20px; border-radius: 8px; font-weight: bold;">🎙️ Click to Speak (English)</button></div>
    """
    return components.html(script, height=80)

def st_text_to_speech(text):
    if text:
        clean = text.replace('"', '\\"').replace('\n', ' ')
        components.html(f"<script>const m=new SpeechSynthesisUtterance('{clean}');m.lang='en-US';window.speechSynthesis.speak(m);</script>", height=0)

# --- BÓVEDA DE API ---
try: API_KEY = st.secrets["GEMINI_API_KEY"]
except: API_KEY = ""

# --- BANCOS DE PREGUNTAS (TODAS LAS ESPECIALIDADES RESTAURADAS) ---
DYNAMIC_MCQ = {
    "Logística": [
        {"q": "The 3PL provider reports a massive backlog at the port. How do you mitigate the EBITDA impact?", "options": ["Wait for customs.", "Spearhead an expedited multi-modal route.", "Tell board it's luck.", "Cancel shipments."], "ans": 1},
        {"q": "Warehouse utilization is at 98%. Recommendation?", "options": ["Rent more space.", "Implement lean inventory / increase turns.", "Stop receiving.", "Stack higher."], "ans": 1},
        {"q": "Last-mile spiked 20%. Strategic move?", "options": ["Reduce deliveries.", "Leverage route optimization algorithms.", "Stop distant deliveries.", "Ask for double payment."], "ans": 1}
    ],
    "Producción": [
        {"q": "OEE dropped to 60%. Action?", "options": ["Tell team to work harder.", "Spearhead Gemba-focused audit to identify downtime.", "Lower target.", "Buy new machine."], "ans": 1},
        {"q": "Scrap surge reported. Board update?", "options": ["Bad material.", "Deployed proactive countermeasure to stabilize process.", "Look tomorrow.", "Fire manager."], "ans": 1},
        {"q": "Throughput limited by bottleneck?", "options": ["Ignore it.", "Perform Takt-time analysis to balance capacity.", "Max speed everywhere.", "Increase headcount."], "ans": 1}
    ],
    "Ingeniería": [
        {"q": "Technical deviation requested?", "options": ["Approve immediately.", "Conduct risk-based assessment for spec compliance.", "Say no.", "Ask manager."], "ans": 1},
        {"q": "Project over budget justification?", "options": ["Expensive engineers.", "Shifted scope to leverage higher ROI via advanced materials.", "Math error.", "Spend less later."], "ans": 1},
        {"q": "Tolerance stack-up issue in CAD leads to:", "options": ["Prettier design.", "Potential non-conformances impacting throughput.", "Cheaper manufacturing.", "Nothing."], "ans": 1}
    ],
    "Project Manager": [
        {"q": "Major scope change request mid-project?", "options": ["Do it now.", "Assess impact on critical path and EBITDA before alignment.", "Ignore.", "Too late."], "ans": 1},
        {"q": "Critical Path means:", "options": ["Dangerous road.", "Any delay impacts the final delivery date.", "Almost finished.", "Small budget."], "ans": 1},
        {"q": "10% budget overrun report?", "options": ["Spent too much.", "Identifying capital reallocation to mitigate variance.", "Slow team.", "Supplier fault."], "ans": 1}
    ],
    "Operaciones & Supply Chain": [
        {"q": "Tier-1 supplier delay report?", "options": ["Wait.", "Report lead-time disruption and OEE impact.", "Work overtime.", "Increase stock."], "ans": 1},
        {"q": "EBITDA shrinking due to rising costs?", "options": ["Cut staff.", "Orchestrate multi-modal strategy for cost optimization.", "Increase prices.", "Stop shipments."], "ans": 1},
        {"q": "Inventory carrying cost 30%?", "options": ["Dispose stock.", "Implement pull system backed by predictive modeling.", "Cheap warehouse.", "Stop buying."], "ans": 1}
    ],
    "Calidad & Lean Manufacturing": [
        {"q": "IATF audit failure response?", "options": ["Fix next week.", "Deployed immediate containment and initiating 8D.", "Auditor error.", "Retrain staff."], "ans": 1},
        {"q": "Cpk 0.82 communication?", "options": ["Stable.", "Incapable of meeting specs; stabilization required.", "High cost.", "New operator."], "ans": 1},
        {"q": "FMEA tool goal?", "options": ["Checklist.", "Identify failure modes before they occur.", "Survey.", "Post-audit."], "ans": 1}
    ],
    "Data Science & SQL": [
        {"q": "Failure rate projection method?", "options": ["Guess.", "Predictive model leveraged via BigQuery analytics.", "Spreadsheet.", "Old chart."], "ans": 1},
        {"q": "Machine Learning description for VP?", "options": ["Robots.", "Systems leveraging patterns to optimize decision-making.", "Calculator.", "Auto-coding."], "ans": 1}
    ],
    "Otra": [
        {"q": "Highest authority phrase?", "options": ["Helped.", "Spearheaded strategic initiative.", "Did work.", "Was part of."], "ans": 1}
    ]
}

# --- KNOWLEDGE BASE ---
THIRTY_DAY_PLAN = [
    {"day": 1, "phase": "Cimientos", "title": "El Pitch de Impacto (EBITDA)", "focus": "Cómo presentar tu valor financiero y ahorros duros."},
    {"day": 2, "phase": "Defensa", "title": "Auditorías Globales", "focus": "Contención, RCA, IATF 16949 y VDA 6.3."},
    {"day": 3, "phase": "Sistemas", "title": "Cultura Cero Defectos", "focus": "Métricas de Calidad, FMEA y Risk-based thinking."},
    {"day": 4, "phase": "Tech Ops", "title": "Data Storytelling", "focus": "Explicar SQL, BigQuery y extracción de datos a Directivos."},
    {"day": 5, "phase": "Escala", "title": "S&OP & Logística", "focus": "Inventory Record Accuracy (IRA) y Supply Chain."},
    {"day": 6, "phase": "Futuro", "title": "Inteligencia Artificial", "focus": "Prompt Engineering y Modelos Predictivos en piso."},
    {"day": 7, "phase": "Boardroom", "title": "Prueba de Fuego (CEO)", "focus": "Estructuras ejecutivas bajo presión extrema."},
]

POWER_VERBS_DRILLS = [
    ("I fixed the problem", "I rectified the non-conformance"),
    ("I saved money", "I delivered substantial hard savings"),
    ("I used data", "I leveraged data analytics to drive decision-making"),
    ("I started a project", "I spearheaded a strategic initiative"),
    ("I talked to the client", "I orchestrated cross-functional negotiations")
]

# --- MOTOR DE IA ---
def call_ai(prompt, api_key):
    if not api_key: return "⚠️ API Key missing."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=20)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "Connection error."

# --- MANEJO DE ESTADO ---
if 'screen' not in st.session_state: st.session_state.screen = 'home'
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_area' not in st.session_state: st.session_state.user_area = "Logística"
if 'english_level' not in st.session_state: st.session_state.english_level = "No Evaluado"
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'current_day' not in st.session_state: st.session_state.current_day = 1
if 'placement_step' not in st.session_state: st.session_state.placement_step = 0
if 'placement_score' not in st.session_state: st.session_state.placement_score = 0
if 'placement_ai_responses' not in st.session_state: st.session_state.placement_ai_responses = []
if 'dynamic_scenarios' not in st.session_state: st.session_state.dynamic_scenarios = []

# --- PANEL LATERAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 2em;'>🦅 CONTROL</h1>", unsafe_allow_html=True)
    if db: st.success("☁️ Guardado en la Nube: ACTIVADO")
    else: st.warning("⚠️ Sin conexión a la base de datos")
    st.divider()
    if st.session_state.user_name:
        st.write(f"**Líder:** {st.session_state.user_name}")
        st.write(f"**Nivel:** {st.session_state.english_level}")
        st.write(f"**XP:** {st.session_state.xp}")
    if st.button("🔄 Reset / Cerrar Sesión"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# --- FLUJO ---

if not st.session_state.get("placement_completed"):
    # 1. INGRESO (PERSISTENTE)
    if st.session_state.screen == 'home':
        st.markdown("<div class='hero-box'><h1>Executive Mastery Protocol</h1><p>Tu progreso se sincroniza automáticamente con tu nombre.</p></div>", unsafe_allow_html=True)
        col1, _ = st.columns([1, 1])
        with col1:
            st.markdown("<div class='executive-card'>", unsafe_allow_html=True)
            name_input = st.text_input("Ingresa tu Nombre Completo:")
            if st.button("Acceder al Sistema 🧠"):
                if name_input:
                    with st.spinner("Buscando expediente en la nube..."):
                        if load_user_progress(name_input):
                            st.success(f"¡Bienvenido de vuelta, {name_input}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.session_state.user_name = name_input
                            st.session_state.screen = 'setup_area'
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.screen == 'setup_area':
        st.title(f"Perfil de Mando: {st.session_state.user_name}")
        area = st.selectbox("Selecciona tu Especialidad Técnica:", list(DYNAMIC_MCQ.keys()))
        if st.button("Comenzar Auditoría de 16 Etapas"):
            st.session_state.user_area = area
            st.session_state.screen = 'placement_test'
            st.rerun()

    # 2. EXAMEN (12 MCQ + 4 AI)
    elif st.session_state.screen == 'placement_test':
        questions = DYNAMIC_MCQ.get(st.session_state.user_area, DYNAMIC_MCQ["Otra"])
        total_mcq = len(questions)
        total_ai = 4
        total_steps = total_mcq + total_ai
        current_step = st.session_state.placement_step
        
        st.progress(current_step / total_steps)
        st.subheader(f"Etapa {current_step+1} de {total_steps} ({st.session_state.user_area})")

        if current_step < total_mcq:
            q = questions[current_step]
            st.markdown(f"<div class='executive-card'><h4>{q['q']}</h4></div>", unsafe_allow_html=True)
            for i, opt in enumerate(q['options']):
                if st.button(opt, key=f"btn_{current_step}_{i}"):
                    if i == q['ans']: st.session_state.placement_score += 15
                    st.session_state.placement_step += 1
                    st.rerun()
        else:
            ai_step = current_step - total_mcq
            if not st.session_state.dynamic_scenarios:
                with st.spinner("Generando escenarios tácticos..."):
                    prompt = f"Generate 4 tough executive scenarios for a {st.session_state.user_area} leader. Format: Scenario 1 --- Scenario 2..."
                    res = call_ai(prompt, API_KEY)
                    st.session_state.dynamic_scenarios = res.split('---')

            current_scenario = st.session_state.dynamic_scenarios[ai_step]
            st.markdown(f"<div class='executive-card'><b>Escenario AI:</b><br>{current_scenario}</div>", unsafe_allow_html=True)
            ans = st.text_area("Tu Respuesta:", key=f"ans_{ai_step}")
            st_speech_to_text(key=f"voice_{ai_step}")
            if st.button("Validar Etapa"):
                if len(ans) > 20:
                    st.session_state.placement_ai_responses.append(ans)
                    st.session_state.placement_step += 1
                    if st.session_state.placement_step == total_steps: st.session_state.screen = 'finalizing'
                    st.rerun()

    elif st.session_state.screen == 'finalizing':
        with st.spinner("Auditando nivel de autoridad..."):
            prompt = f"Audit engineer {st.session_state.user_area}. Score {st.session_state.placement_score}. Determine CEFR and give detailed feedback in Spanish with VP tips."
            res = call_ai(prompt, API_KEY)
            st.session_state.placement_eval_detailed = res
            for level in ["C2", "C1", "B2", "B1"]:
                if level in res: st.session_state.english_level = f"{level} - Certified"; break
            st.session_state.placement_completed = True
            save_user_progress()
            st.rerun()

# 3. WAR ROOM (PERSISTENTE)
else:
    st.title(f"🛡️ War Room: {st.session_state.user_name}")
    tabs = st.tabs(["📅 Roadmap", "🤖 AI Combat Lab", "⚔️ Power Verbs", "🔥 The Forge", "📖 Enciclopedia"])
    
    with tabs[0]:
        st.subheader("Tu Ruta de Transformación Táctica")
        for plan in THIRTY_DAY_PLAN:
            is_active = "day-active" if plan['day'] == st.session_state.current_day else ""
            st.markdown(f"""
                <div class="day-card {is_active}">
                    <span style="color: #3b82f6; font-weight: 900;">DÍA {plan['day']} • {plan['phase']}</span>
                    <h3 style="margin-top: 5px; color: white;">{plan['title']}</h3>
                    <p style="color:#94a3b8; margin-bottom:0;"><b>Foco:</b> {plan['focus']}</p>
                </div>
            """, unsafe_allow_html=True)

    with tabs[1]:
        mission = next((p for p in THIRTY_DAY_PLAN if p['day'] == st.session_state.current_day), THIRTY_DAY_PLAN[-1])
        st.subheader(f"Misión Diaria: {mission['title']}")
        if st.button("🎙️ Generar Escenario Táctico"):
            with st.spinner("Preparando entrenamiento..."):
                st.session_state.daily_q = call_ai(f"Elite Mentor. Ask a challenging question about {mission['focus']} to a {st.session_state.user_area} expert. Level {st.session_state.english_level}.", API_KEY)
                st_text_to_speech(st.session_state.daily_q)
        
        if 'daily_q' in st.session_state:
            st.info(st.session_state.daily_q)
            ans = st.text_area("Respuesta Ejecutiva:")
            st_speech_to_text(key="combat_voice")
            if st.button("Auditar con Feedback y Pro Tips"):
                with st.spinner("Auditando..."):
                    prompt = f"""Evaluate: {ans}. 
                    Provide in SPANISH:
                    1. SCORE (0-100)
                    2. FEEDBACK TÉCNICO: Errores gramaticales o de autoridad.
                    3. TIP PRO: Un consejo VP para mejorar.
                    4. VERSIÓN BOARDROOM: Script perfecto en inglés."""
                    res = call_ai(prompt, API_KEY)
                    st.markdown(f"<div class='level-box' style='background-color: #1e293b; border-left-color: #f59e0b;'>{res}</div>", unsafe_allow_html=True)
                    st.session_state.xp += 100
                    save_user_progress()

    with tabs[2]:
        st.subheader("Combate de Reflejos: Power Verbs")
        drill = st.session_state.current_drill
        st.markdown(f"<div class='executive-card' style='border-color:#f59e0b;'>Un Junior diría: <b>'{drill[0]}'</b></div>", unsafe_allow_html=True)
        pv_ans = st.text_input("Sustituye por la versión ejecutiva:")
        
        if st.button("Validar Impacto 🎯"):
            if drill[1].lower() in pv_ans.lower():
                st.success("¡Excelente! Has neutralizado la frase básica.")
                st.session_state.xp += 50
                st.info(f"💡 **TIP PRO:** '{drill[1].split()[1]}' es un verbo de acción que implica liderazgo y responsabilidad total.")
                time.sleep(2)
                st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS)
                save_user_progress()
                st.rerun()
            else:
                st.error(f"Sigue siendo básico. La frase letal es: '{drill[1]}'")
                st.caption("💡 **TIP PRO:** Usa verbos que demuestren un proceso o una estrategia, como 'rectified' o 'orchestrated'.")

    with tabs[3]:
        st.subheader("La Fragua: Forja de Logros")
        draft = st.text_area("Ingresa un logro básico (ej: Reduje scrap):")
        if st.button("⚒️ Forjar Logro VP"):
            with st.spinner("Forjando..."):
                res = call_ai(f"Transform to STAR executive achievement in English focused on EBITDA with a Pro Tip in Spanish: {draft}", API_KEY)
                st.markdown(f"<div class='executive-card'><b>Resultado VP:</b><br>{res}</div>", unsafe_allow_html=True)
                save_user_progress()

    with tabs[4]:
        st.subheader("Enciclopedia Técnica")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("<span class='badge-ops'>🏭 Ops & Supply</span>", unsafe_allow_html=True)
            st.write("- **EBITDA:** Beneficio operativo.")
            st.write("- **Hard Savings:** Ahorros reales.")
            st.write("- **S&OP:** Alineación de demanda y suministro.")
        with c2:
            st.markdown("<span class='badge-tech'>🧬 Tech & Data</span>", unsafe_allow_html=True)
            st.write("- **SQL Query:** Consulta de datos.")
            st.write("- **BigQuery:** Almacén de Google.")
            st.write("- **IRA:** Precisión de inventario.")
        with c3:
            st.markdown("<span class='badge-compliance'>⚖️ Quality</span>", unsafe_allow_html=True)
            st.write("- **IATF 16949:** Calidad Automotriz.")
            st.write("- **Cpk:** Capacidad de proceso.")
            st.write("- **RCA:** Análisis de Causa Raíz.")

st.divider()
st.caption("Protocolo diseñado por Ing. Fernando Montes Delgado | Cloud Persistence & Full Knowledge Base Restored")
