import streamlit as st
import requests
import time
import random
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Executive Mastery SaaS", 
    page_icon="⚙️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PSICOLOGÍA DE COLOR Y DISEÑO (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    
    /* Botones de Acción (Ámbar) */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em; 
        background: linear-gradient(90deg, #f59e0b 0%, #f97316 100%);
        color: #0f172a !important; font-weight: 900; font-size: 1.1em;
        border: none; transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(245, 158, 11, 0.4); }
    
    /* Tarjetas Ejecutivas */
    .hero-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
        padding: 40px; border-radius: 20px; text-align: center;
        border: 1px solid #3b82f6; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 30px;
    }
    .executive-card {
        background-color: #1e293b; padding: 30px; border-radius: 15px;
        border-left: 6px solid #3b82f6; margin-bottom: 20px;
    }
    .level-box {
        background-color: #064e3b; padding: 30px; border-radius: 15px;
        border-left: 6px solid #10b981; margin-top: 15px; color: #ecfdf5; text-align: center;
    }
    .day-card {
        background-color: #1e293b; padding: 20px; border-radius: 15px;
        border: 2px solid #334155; margin-bottom: 15px; transition: 0.3s;
    }
    .day-active { border-color: #f59e0b; background-color: #451a03; box-shadow: 0 0 15px rgba(245, 158, 11, 0.3); }
    
    /* Badges */
    .badge-tech { background-color: #1e40af; color: #dbeafe; padding: 4px 10px; border-radius: 8px; font-weight: bold; }
    .badge-ops { background-color: #92400e; color: #fef3c7; padding: 4px 10px; border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- COMPONENTE DE VOZ (JavaScript Bridge) ---
def st_speech_to_text(key):
    script = """
    <script>
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    function startDictation() {
        recognition.start();
        document.getElementById('mic-status').innerText = '🔴 Listening...';
    }

    recognition.onresult = (event) => {
        const speechToText = event.results[0][0].transcript;
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: speechToText,
            key: '""" + key + """'
        }, '*');
        document.getElementById('mic-status').innerText = '✅ Success!';
    };

    recognition.onerror = () => {
        document.getElementById('mic-status').innerText = '⚠️ Mic Error';
    };
    </script>
    <div style="text-align: center;">
        <button onclick="startDictation()" style="background: #f59e0b; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer;">🎙️ Click to Speak (English)</button>
        <p id="mic-status" style="color: #94a3b8; font-size: 0.8em; margin-top: 5px;">Ready</p>
    </div>
    """
    return components.html(script, height=100)

def st_text_to_speech(text):
    if text:
        clean_text = text.replace('"', '\\"').replace('\n', ' ')
        script = f"""
        <script>
        const msg = new SpeechSynthesisUtterance("{clean_text}");
        msg.lang = 'en-US';
        msg.rate = 0.9;
        window.speechSynthesis.speak(msg);
        </script>
        """
        components.html(script, height=0)

# --- BÓVEDA DE SEGURIDAD ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = ""

# --- BANCO DE PREGUNTAS MCQ COMPLEJAS (RESTABLECIDO) ---
DYNAMIC_MCQ = {
    "Operaciones & Supply Chain": [
        {"q": "A critical tier-1 supplier announces a 25% increase in lead time. How do you report the impact to the board?", "options": ["Wait for the material and report later.", "Report a lead-time disruption and its projected impact on throughput and OEE.", "Ask the supplier to work overtime.", "Increase safety stock without analyzing financial carrying costs."], "ans": 1},
        {"q": "EBITDA is shrinking due to rising multi-modal freight costs. What is your move?", "options": ["Reduce the logistics headcount immediately.", "Orchestrate a multi-modal strategy focused on IRA and cost optimization.", "Increase prices without market analysis.", "Stop all shipments until rates drop."], "ans": 1},
        {"q": "In an S&OP meeting, there is a major gap between demand and capacity. You should:", "options": ["Ignore it and produce at max capacity.", "Align demand and supply plans by prioritizing high-margin SKUs.", "Tell sales to stop taking orders.", "Wait for next month's forecast."], "ans": 1},
        {"q": "Your inventory carrying cost is 30%. What is the executive solution?", "options": ["Dispose of old inventory immediately.", "Implement a pull system backed by predictive modeling to reduce buffers.", "Rent a cheaper warehouse.", "Stop procurement for a month."], "ans": 1},
        {"q": "Which phrase demonstrates highest authority in a P&L update?", "options": ["I helped reduce costs last quarter.", "I spearheaded a strategic initiative delivering $274k in hard savings.", "I was responsible for the cost cutting plan.", "The team reduced costs under my supervision."], "ans": 1},
        {"q": "A bottleneck is impacting 15% of your throughput. Your first step is:", "options": ["Hire more operators.", "Perform a Takt-time analysis to balance the flow and maximize OEE.", "Increase machine speed.", "Report a technical breakdown."], "ans": 1}
    ],
    "Calidad & Lean Manufacturing": [
        {"q": "An IATF 16949 audit detects a systemic failure in RCA. Your professional response is:", "options": ["We will fix it by next week.", "We have deployed immediate containment and are initiating a robust 8D report.", "The auditor misunderstood our process.", "We will retrain all operators immediately."], "ans": 1},
        {"q": "Your process Cpk is 0.82. What does this communicate to a global stakeholder?", "options": ["The process is stable but slow.", "The process is incapable of meeting specifications and requires stabilization.", "The product cost is too high.", "The machine needs a new operator."], "ans": 1},
        {"q": "A major non-conformance is found in the design phase. Which tool identifies it?", "options": ["A basic checklist.", "A cross-functional FMEA (Failure Mode and Effects Analysis).", "A customer survey.", "A post-production audit."], "ans": 1},
        {"q": "How do you explain 'Muda' to a CFO focusing on financial impact?", "options": ["It means we have too much trash.", "It represents non-value-added activities impacting EBITDA and cycle time.", "It is a Japanese word for cleanliness.", "It means we need more robots."], "ans": 1},
        {"q": "What is the most executive way to describe 'Poke-Yoke'?", "options": ["Fixing errors manually.", "Implementing error-proofing devices to ensure zero-defect manufacturing.", "Double-checking every part.", "Buying high-quality tools."], "ans": 1},
        {"q": "A 'Gemba Walk' is primarily used by leaders to:", "options": ["Walk around for exercise.", "Observe the actual place of work to identify improvement opportunities.", "Check if people are working hard.", "Talk to the staff about their personal lives."], "ans": 1}
    ],
    "Data Science & SQL": [
        {"q": "The board asks for a projection of failure rates. You should offer:", "options": ["A guess based on last year.", "A predictive model leveraged through BigQuery and SQL analytics.", "A spreadsheet with old data.", "A chart showing previous errors."], "ans": 1},
        {"q": "A 'JOIN' operation in SQL is failing due to data integrity. You say:", "options": ["The tables don't like each other.", "We are experiencing a relational mismatch that requires data cleansing.", "The computer is slow.", "We need to delete the data."], "ans": 1},
        {"q": "How do you justify a 'Big Data' investment to a non-technical CEO?", "options": ["It makes us look modern.", "It allows us to extract actionable insights to drive profitability.", "It stores more files than Excel.", "It is faster than our current server."], "ans": 1},
        {"q": "What is a 'Primary Key' in terms of business impact?", "options": ["A password to enter the office.", "A unique identifier ensuring data accuracy and reporting reliability.", "The main computer in the room.", "A set of rules for the team."], "ans": 1},
        {"q": "When a dashboard shows a KPI in red, your executive response is:", "options": ["I will fix the chart.", "I am analyzing the root cause to deploy a corrective measure.", "It's probably a data error.", "We will look at it next week."], "ans": 1},
        {"q": "Machine Learning is best described to a VP as:", "options": ["Robots doing human work.", "Systems that leverage data patterns to optimize decision-making.", "A fancy type of calculator.", "Automatic coding."], "ans": 1}
    ],
    "Ingeniería de Producto": [
        {"q": "A BOM error is discovered after production started. You report:", "options": ["We made a small mistake.", "A critical BOM misalignment was identified; initiating a technical revision.", "We will change it later.", "The design team is busy."], "ans": 1},
        {"q": "What is 'DFM' in a cost-optimization meeting?", "options": ["Designing for Money.", "Design for Manufacturing to reduce complexity and OPEX.", "Doing Fine Models.", "Data for Management."], "ans": 1},
        {"q": "A prototype fails a stress test. Your high-level report says:", "options": ["The part broke.", "The component experienced a structural failure under specification limits.", "We need better material.", "The test was too hard."], "ans": 1},
        {"q": "Which term describes 'Tolerance' in an executive summary?", "options": ["How much we can stand a problem.", "The allowable variation in a physical dimension to ensure fitment.", "The price range of a part.", "The time we have to finish."], "ans": 1},
        {"q": "Iterative design is used to:", "options": ["Make things slowly.", "Continuously refine a product based on data and feedback.", "Copy other designs.", "Save money on designers."], "ans": 1},
        {"q": "FEA stands for a method that:", "options": ["Finds Every Atom.", "Finite Element Analysis to predict how parts react to forces.", "Fast Engineering Action.", "Future Entry Assessment."], "ans": 1}
    ],
    "Otra": [
        {"q": "Which phrase demonstrates highest authority?", "options": ["I helped with the project.", "I spearheaded the strategic initiative.", "I did the work.", "I was part of the group."], "ans": 1},
        {"q": "Professional communication should always be:", "options": ["Extremely long.", "Concise and impact-oriented.", "Casual and funny.", "Detailed and technical only."], "ans": 1},
        {"q": "What is a 'KPI'?", "options": ["Key Performance Indicator.", "King Price Item.", "Knowledge Part Index.", "Keep People Informed."], "ans": 0},
        {"q": "An 'Outcome' is better defined as:", "options": ["The start of something.", "A result or consequence of an action.", "A bill to pay.", "A meeting."], "ans": 1},
        {"q": "Stakeholder alignment means:", "options": ["Ignoring people.", "Ensuring all parties agree on the strategic goal.", "Hiring new staff.", "Selling parts."], "ans": 1},
        {"q": "EBITDA is a measure of:", "options": ["Employee happiness.", "Operational profitability.", "Market share.", "Total debt."], "ans": 1}
    ]
}

# --- BASE DE CONOCIMIENTO (RESTABLECIDA) ---
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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=20)
        return response.json()['candidates'][0]['content']['parts'][0]['text'] if response.status_code == 200 else f"Error: {response.status_code}"
    except: return "Connection error."

# --- MANEJO DE ESTADO ---
if 'screen' not in st.session_state: st.session_state.screen = 'home'
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_area' not in st.session_state: st.session_state.user_area = "Operaciones & Supply Chain"
if 'english_level' not in st.session_state: st.session_state.english_level = "No Evaluado"
if 'placement_step' not in st.session_state: st.session_state.placement_step = 0
if 'placement_score' not in st.session_state: st.session_state.placement_score = 0
if 'placement_ai_responses' not in st.session_state: st.session_state.placement_ai_responses = []
if 'dynamic_scenarios' not in st.session_state: st.session_state.dynamic_scenarios = []
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'current_day' not in st.session_state: st.session_state.current_day = 1
if 'current_drill' not in st.session_state: st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS)

# --- PANEL LATERAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 3em;'>⚙️</h1>", unsafe_allow_html=True)
    st.title("Executive Control")
    if not API_KEY: st.error("🔒 Bóveda Vacía")
    else: st.success("🔒 Conexión Segura")
    st.divider()
    if st.session_state.user_name:
        st.write(f"**Líder:** {st.session_state.user_name}")
        st.markdown(f"**Nivel:** `<span style='color:#f59e0b; font-weight:bold;'>{st.session_state.english_level}</span>`")
        st.write(f"**XP:** {st.session_state.xp}")
    if st.button("🔄 Reset Protocol"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# --- FLUJO PRINCIPAL ---

if st.session_state.english_level == "No Evaluado":
    # 1. HOME
    if st.session_state.screen == 'home':
        st.markdown("""
            <div class="hero-box">
                <h1>Executive Mastery Protocol</h1>
                <p>Auditoría de 16 etapas iniciada. Selecciona tu especialidad para activar el simulador.</p>
            </div>
        """, unsafe_allow_html=True)
        col1, _ = st.columns([1, 1])
        with col1:
            st.markdown("<div class='executive-card'>", unsafe_allow_html=True)
            name = st.text_input("Nombre Completo:")
            area = st.selectbox("Especialidad Táctica:", list(DYNAMIC_MCQ.keys()))
            if st.button("Iniciar Protocolo 16 Etapas 🧠"):
                if name:
                    st.session_state.user_name = name
                    st.session_state.user_area = area
                    st.session_state.screen = 'placement_test'
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # 2. EXAMEN (12 MCQ + 4 AI)
    elif st.session_state.screen == 'placement_test':
        questions = DYNAMIC_MCQ.get(st.session_state.user_area, DYNAMIC_MCQ["Otra"])
        total_mcq = len(questions)
        total_ai = 4
        total_steps = total_mcq + total_ai
        current_step = st.session_state.placement_step
        
        st.title(f"🎯 Etapa {current_step + 1} de {total_steps} ({st.session_state.user_area})")
        st.progress(current_step / total_steps)

        if current_step < total_mcq:
            q_data = questions[current_step]
            st.markdown(f"<div class='executive-card'><h4>{q_data['q']}</h4></div>", unsafe_allow_html=True)
            for i, opt in enumerate(q_data['options']):
                if st.button(opt, key=f"btn_{current_step}_{i}"):
                    if i == q_data['ans']: st.session_state.placement_score += 15
                    st.session_state.placement_step += 1
                    st.rerun()
        else:
            ai_step_idx = current_step - total_mcq
            if not st.session_state.dynamic_scenarios:
                with st.spinner("Generando 4 escenarios dinámicos con IA..."):
                    prompt = f"Generate 4 distinct, very tough executive scenarios for a {st.session_state.user_area} leader. Focus on crisis and authority. Format: Scenario 1 --- Scenario 2 --- Scenario 3 --- Scenario 4"
                    res = call_ai(prompt, API_KEY)
                    st.session_state.dynamic_scenarios = res.split('---')

            current_scenario = st.session_state.dynamic_scenarios[ai_step_idx]
            st.markdown(f"<div class='executive-card'><b>Escenario AI {ai_step_idx + 1}:</b><br><br>{current_scenario}</div>", unsafe_allow_html=True)
            ans = st.text_area("Respuesta Ejecutiva:", key=f"ai_ans_{ai_step_idx}")
            st_speech_to_text(key=f"voice_{ai_step_idx}")
            if st.button("Validar Etapa"):
                if len(ans) > 30:
                    st.session_state.placement_ai_responses.append({"q": current_scenario, "a": ans})
                    st.session_state.placement_step += 1
                    if st.session_state.placement_step == total_steps: st.session_state.screen = 'finalizing'
                    st.rerun()
                else: st.warning("Por favor desarrolla más tu respuesta.")

    # 3. FINALIZACIÓN
    elif st.session_state.screen == 'finalizing':
        with st.spinner("Auditando nivel de autoridad..."):
            ai_text = "\n".join([f"Q: {x['q']}\nA: {x['a']}" for x in st.session_state.placement_ai_responses])
            prompt = f"Audit this {st.session_state.user_area} expert. MCQ Score: {st.session_state.placement_score}. Open responses: {ai_text}. Determine CEFR Level, Score 0-100, Diagnostic of weaknesses, Error Feedback, and 2 Pro Tips in Spanish."
            res = call_ai(prompt, API_KEY)
            st.session_state.placement_eval_detailed = res
            for level in ["C2", "C1", "B2", "B1"]:
                if level in res: st.session_state.english_level = f"{level} - Certified"; break
            if st.session_state.english_level == "No Evaluado": st.session_state.english_level = "B1 - Intermediate"
            st.session_state.screen = 'results'
            st.rerun()

    elif st.session_state.screen == 'results':
        st.markdown(f"<div class='level-box'><h1>{st.session_state.english_level}</h1></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='executive-card'><p style='white-space: pre-wrap;'>{st.session_state.placement_eval_detailed}</p></div>", unsafe_allow_html=True)
        if st.button("Desbloquear War Room ⚔️"):
            st.session_state.screen = 'dashboard'
            st.rerun()

# --- FASE 2: WAR ROOM (RESTAURADO CON FEEDBACK) ---
else:
    st.title(f"🛡️ War Room: {st.session_state.user_name}")
    tabs = st.tabs(["📅 Roadmap 30 Días", "🤖 AI Lab", "⚔️ Power Verbs", "🔥 The Forge", "📖 Enciclopedia"])
    
    with tabs[0]:
        st.subheader("Tu Ruta de Transformación Táctica")
        for plan in THIRTY_DAY_PLAN:
            is_active = "day-active" if plan['day'] == st.session_state.current_day else ""
            st.markdown(f"<div class='day-card {is_active}'><b>DÍA {plan['day']}</b> • {plan['title']}<br><small>{plan['focus']}</small></div>", unsafe_allow_html=True)

    with tabs[1]:
        mission = next((p for p in THIRTY_DAY_PLAN if p['day'] == st.session_state.current_day), THIRTY_DAY_PLAN[-1])
        st.subheader(f"Misión: {mission['title']}")
        if st.button("🎙️ Generar Escenario con el Mentor"):
            with st.spinner("Preparando entrenamiento..."):
                st.session_state.daily_q = call_ai(f"Elite Mentor. Tough question about {mission['focus']} for a {st.session_state.user_area} expert.", API_KEY)
                st_text_to_speech(st.session_state.daily_q)
        if 'daily_q' in st.session_state:
            st.info(st.session_state.daily_q)
            ans = st.text_area("Responde:")
            st_speech_to_text(key="lab_voice")
            if st.button("Auditar Respuesta"):
                feedback = call_ai(f"Evaluate answer: {ans}. Give SCORE, Technical Feedback, and 1 Pro Tip in Spanish.", API_KEY)
                st.markdown(f"<div class='level-box'>{feedback}</div>", unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("Power Verbs Drill")
        drill = st.session_state.current_drill
        st.markdown(f"<div class='executive-card'>Junior: '{drill[0]}'</div>", unsafe_allow_html=True)
        pv_ans = st.text_input("Versión Ejecutiva:")
        if st.button("Validar Impacto"):
            if drill[1].lower() in pv_ans.lower():
                st.success("¡Correcto!")
                st.session_state.xp += 50
                st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS)
                st.rerun()
            else: st.error(f"Usa: '{drill[1]}'")

    with tabs[3]:
        st.subheader("The Forge")
        draft = st.text_area("Ingresa un logro:")
        if st.button("⚒️ Forjar"):
            res = call_ai(f"Transform to STAR executive achievement with a Pro Tip: {draft}", API_KEY)
            st.markdown(f"<div class='executive-card'>{res}</div>", unsafe_allow_html=True)

    with tabs[4]:
        st.subheader("Enciclopedia")
        st.markdown("<span class='badge-ops'>🏭 Ops</span> EBITDA, S&OP, IATF, RCA.", unsafe_allow_html=True)

st.divider()
st.caption("Protocolo desarrollado por Ing. Fernando Montes Delgado | All Areas Restored | Feedback Enabled")
