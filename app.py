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
    """Crea un pequeño puente para usar el micrófono del navegador."""
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
    """Hace que el navegador lea el texto de la IA."""
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

# --- BÓVEDA DE SEGURIDAD (SECRETS) ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = ""

# --- BANCO DE PREGUNTAS DINÁMICO ---
DYNAMIC_MCQ = {
    "Operaciones & Supply Chain": [
        {"q": "What is 'Lead Time'?", "options": ["Production speed", "Total time from order to delivery", "Machine uptime", "The boss's schedule"], "ans": 1},
        {"q": "Which term describes a delay impact on throughput?", "options": ["Bottleneck", "Buffer", "Backlog", "Lead-time disruption"], "ans": 3},
        {"q": "Inventory Record Accuracy (IRA) is crucial for:", "options": ["EBITDA protection", "MRP reliability", "Safety stock reduction", "All of the above"], "ans": 3},
        {"q": "What is the primary goal of S&OP?", "options": ["To hire people", "To align demand and supply plans", "To count inventory", "To fix machines"], "ans": 1},
        {"q": "EBITDA improves when:", "options": ["OPEX increases", "Revenue grows and costs are optimized", "Margins shrink", "Production slows down"], "ans": 1},
        {"q": "What are 'Hard Savings'?", "options": ["Auditable cost reductions", "Future projections", "Employee happiness", "Idea generation"], "ans": 0},
        {"q": "A 'Stockout' occurs when:", "options": ["Inventory is exhausted", "Sales are too high", "Warehouse is full", "Prices go up"], "ans": 0},
        {"q": "The term 'Takt Time' refers to:", "options": ["Speed of a robot", "Rate of customer demand", "Lunch break duration", "Total shift time"], "ans": 1},
        {"q": "Which verb sounds more executive?", "options": ["Started", "Spearheaded", "Helped", "Tried"], "ans": 1},
        {"q": "An 'Escalation' is usually for:", "options": ["Hiding a mistake", "Seeking higher-level decision making", "Ending a shift", "Repairing a tool"], "ans": 1},
        {"q": "Which metric measures machine effectiveness?", "options": ["KPI", "OEE", "ROI", "SQL"], "ans": 1},
        {"q": "A 'Buffer' is intended to:", "options": ["Hide mistakes", "Absorb variability in supply/demand", "Slow down work", "Stop production"], "ans": 1}
    ],
    "Calidad & Lean Manufacturing": [
        {"q": "What does a high Cpk indicate?", "options": ["Process instability", "Process capability and Spec compliance", "High cost", "Slow production"], "ans": 1},
        {"q": "An '8D Report' is used for:", "options": ["Counting parts", "Systemic problem solving", "Design", "Marketing"], "ans": 1},
        {"q": "The primary focus of IATF 16949 is:", "options": ["Employee benefits", "Customer satisfaction and defect prevention", "Selling cars", "Robot maintenance"], "ans": 1},
        {"q": "What is a 'Non-conformance'?", "options": ["A late employee", "A product that fails spec", "A new idea", "A meeting"], "ans": 1},
        {"q": "The '5 Whys' method is for:", "options": ["Asking questions", "Finding the Root Cause", "Interviewing people", "Setting prices"], "ans": 1},
        {"q": "What is 'Poke-Yoke'?", "options": ["A game", "Error-proofing", "A cleaning method", "Fast production"], "ans": 1},
        {"q": "Which tool identifies failure modes?", "options": ["FMEA", "CAD", "SQL", "PPT"], "ans": 0},
        {"q": "The term 'Muda' in Lean means:", "options": ["Silence", "Waste", "Fast", "Strong"], "ans": 1},
        {"q": "A 'Kaizen' event is for:", "options": ["Stopping work", "Continuous improvement", "A celebration", "A sale"], "ans": 1},
        {"q": "Which verb fits a Quality Manager?", "options": ["Rectified", "Fixed", "Looked at", "Asked for"], "ans": 0},
        {"q": "What is a 'Gemba Walk'?", "options": ["A stroll in the park", "Observing the actual place of work", "Exercising", "A Zoom call"], "ans": 1},
        {"q": "A 'Countermeasure' should be:", "options": ["Temporary", "Permanent and risk-based", "Quick", "Cheap"], "ans": 1}
    ],
    "Data Science & SQL": [
        {"q": "Which SQL command retrieves data?", "options": ["GET", "SELECT", "QUERY", "EXTRACT"], "ans": 1},
        {"q": "What is BigQuery?", "options": ["A search engine", "A data warehouse", "A small database", "A coding language"], "ans": 1},
        {"q": "A 'JOIN' in SQL is used to:", "options": ["Delete data", "Combine rows from tables", "Exit a program", "Split a file"], "ans": 1},
        {"q": "What is 'Data Cleansing'?", "options": ["Washing hardware", "Fixing corrupt or inaccurate records", "Deleting all data", "Moving servers"], "ans": 1},
        {"q": "A 'Dashboard' is primarily for:", "options": ["Storing code", "Data visualization and monitoring", "Typing text", "Sending emails"], "ans": 1},
        {"q": "Predictive Modeling uses:", "options": ["Past data to forecast future events", "Old stories", "Random guesses", "Daily logs"], "ans": 0},
        {"q": "What is an 'Algorithm'?", "options": ["A set of rules to solve a problem", "A type of computer", "A website", "A data center"], "ans": 0},
        {"q": "Which term describes massive data sets?", "options": ["Big Data", "Full Data", "Heavy Data", "Fast Data"], "ans": 0},
        {"q": "An 'Insight' is:", "options": ["A raw number", "A deep understanding derived from data", "A mistake", "A chart"], "ans": 1},
        {"q": "Which verb fits a Data Analyst?", "options": ["Leveraged", "Used", "Seen", "Wrote"], "ans": 0},
        {"q": "What is 'Machine Learning'?", "options": ["Teaching robots to walk", "Systems that learn from data", "Repairing computers", "Coding"], "ans": 1},
        {"q": "A 'Primary Key' is:", "options": ["A login password", "A unique identifier for a record", "A main office key", "An encryption tool"], "ans": 1}
    ],
    "Ingeniería de Producto": [
        {"q": "What is a 'BOM'?", "options": ["A project plan", "Bill of Materials", "A safety alarm", "A financial budget"], "ans": 1},
        {"q": "Which tool is for 3D modeling?", "options": ["Excel", "CAD", "SQL", "Word"], "ans": 1},
        {"q": "What is 'DFM'?", "options": ["Design for Manufacturing", "Data for Management", "Digital File Maker", "Direct Factory Model"], "ans": 0},
        {"q": "A 'Prototype' is:", "options": ["The final product", "An early sample to test a concept", "A machine manual", "A blueprint"], "ans": 1},
        {"q": "Which term describes part fitment?", "options": ["Tolerance", "Weight", "Color", "Price"], "ans": 0},
        {"q": "What is 'PLM'?", "options": ["Product Lifecycle Management", "Plant Level Monitor", "Public Low Market", "Price List Maker"], "ans": 0},
        {"q": "Iterative design means:", "options": ["Doing it once", "Repeating and refining a design", "Copying a competitor", "Working fast"], "ans": 1},
        {"q": "What is 'FEA'?", "options": ["Fast Engine Analysis", "Finite Element Analysis", "Future Event Assessment", "Final Entry Act"], "ans": 1},
        {"q": "A 'Stakeholder' is:", "options": ["A competitor", "Anyone with an interest in the project", "A customer only", "A supplier"], "ans": 1},
        {"q": "Which verb fits an Engineer?", "options": ["Optimized", "Improved", "Changed", "Checked"], "ans": 0},
        {"q": "A 'Blueprint' is:", "options": ["A blue wall", "A technical drawing", "A list of names", "A contract"], "ans": 1},
        {"q": "What is 'R&D'?", "options": ["Repair and Design", "Research and Development", "Real and Direct", "Rates and Data"], "ans": 1}
    ],
    "Otra": [
        {"q": "Which term sounds more executive?", "options": ["I did it", "I spearheaded the initiative", "I helped the team", "I finished it"], "ans": 1},
        {"q": "Professional communication should be:", "options": ["Long and detailed", "Concise and impact-oriented", "Casual and friendly", "Secretive"], "ans": 1},
        {"q": "What is the primary goal of any business?", "options": ["To have many employees", "To create value and profitability", "To buy machines", "To win awards"], "ans": 1},
        {"q": "A 'KPI' is a:", "options": ["Key Performance Indicator", "Key Project Index", "King Price Item", "Knowledge Part Item"], "ans": 0},
        {"q": "Which verb is stronger than 'Looked at'?", "options": ["Seen", "Audited", "Checked", "Faced"], "ans": 1},
        {"q": "An 'Outcome' is:", "options": ["A result or consequence", "The start of a project", "A bill", "A meeting"], "ans": 0},
        {"q": "EBITDA is a measure of:", "options": ["Customer happiness", "Operational profitability", "Machine speed", "Stock prices"], "ans": 1},
        {"q": "A 'Constraint' is:", "options": ["A new opportunity", "A limitation or restriction", "A big budget", "A success"], "ans": 1},
        {"q": "A 'Strategy' is a:", "options": ["Quick fix", "Long-term plan to achieve a goal", "Guess", "Meeting"], "ans": 1},
        {"q": "Which verb fits a Leader?", "options": ["Orchestrated", "Handled", "Helped", "Managed"], "ans": 0},
        {"q": "A 'Milestone' is:", "options": ["A large rock", "A significant stage in a project", "A deadline", "A budget"], "ans": 1},
        {"q": "Stakeholder alignment means:", "options": ["Ignoring people", "Ensuring everyone is in agreement", "Hiring people", "Selling parts"], "ans": 1}
    ]
}

# --- BASE DE CONOCIMIENTO: PLAN 30 DÍAS ---
THIRTY_DAY_PLAN = [
    {"day": 1, "phase": "Cimientos", "title": "El Pitch de Impacto (EBITDA)", "focus": "Cómo presentar tu valor financiero y ahorros duros."},
    {"day": 2, "phase": "Defensa", "title": "Auditorías Globales", "focus": "Contención, RCA, IATF 16949 y VDA 6.3."},
    {"day": 3, "phase": "Sistemas", "title": "Cultura Cero Defectos", "focus": "Métricas de Calidad, FMEA y Risk-based thinking."},
    {"day": 4, "phase": "Tech Ops", "title": "Data Storytelling", "focus": "Explicar SQL, BigQuery y extracción de datos a Directivos."},
    {"day": 5, "phase": "Escala", "title": "S&OP & Logística", "focus": "Inventory Record Accuracy (IRA) y Supply Chain."},
    {"day": 6, "phase": "Futuro", "title": "Inteligencia Artificial", "focus": "Prompt Engineering y Modelos Predictivos en piso."},
    {"day": 7, "phase": "Boardroom", "title": "Prueba de Fuego (CEO)", "focus": "Estructuras ejecutivas bajo presión extrema."},
]

# --- BASE DE CONOCIMIENTO: POWER VERBS ---
POWER_VERBS_DRILLS = [
    ("I fixed the problem", "I rectified the non-conformance"),
    ("I saved money", "I delivered substantial hard savings"),
    ("I used data", "I leveraged data analytics to drive decision-making"),
    ("I started a project", "I spearheaded a strategic initiative"),
    ("I talked to the client", "I orchestrated cross-functional negotiations")
]

# --- MOTOR DE INTELIGENCIA ARTIFICIAL ---
def call_ai(prompt, api_key):
    if not api_key: return "⚠️ Error: Falta la API Key."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=20)
        return response.json()['candidates'][0]['content']['parts'][0]['text'] if response.status_code == 200 else f"Error: {response.status_code}"
    except: return "Error de conexión."

# --- MANEJO DE ESTADO DE SESIÓN ---
if 'screen' not in st.session_state: st.session_state.screen = 'home'
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_area' not in st.session_state: st.session_state.user_area = "Operaciones & Supply Chain"
if 'english_level' not in st.session_state: st.session_state.english_level = "No Evaluado"
if 'placement_step' not in st.session_state: st.session_state.placement_step = 0
if 'placement_score' not in st.session_state: st.session_state.placement_score = 0
if 'placement_ai_responses' not in st.session_state: st.session_state.placement_ai_responses = []
if 'current_day' not in st.session_state: st.session_state.current_day = 1
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'current_drill' not in st.session_state: st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS)

# --- PANEL DE CONTROL LATERAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 3em;'>⚙️</h1>", unsafe_allow_html=True)
    st.title("Mission Control")
    if not API_KEY: st.error("🔒 Bóveda Vacía")
    else: st.success("🔒 Conexión Segura")
    st.divider()
    if st.session_state.user_name:
        st.write(f"**Líder:** {st.session_state.user_name}")
        st.write(f"**Área:** {st.session_state.user_area}")
        st.markdown(f"**Nivel:** `<span style='color:#f59e0b; font-weight:bold;'>{st.session_state.english_level}</span>`", unsafe_allow_html=True)
        st.write(f"**XP:** {st.session_state.xp}")
    if st.button("🔄 Reiniciar Protocolo"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# --- FLUJO PRINCIPAL ---

if st.session_state.english_level == "No Evaluado":
    # --- PANTALLA DE INICIO ---
    if st.session_state.screen == 'home':
        st.markdown("""
            <div class="hero-box">
                <h1>Executive Mastery Protocol</h1>
                <p>Bienvenido al simulador de mando. Tu especialidad determinará el rigor técnico del examen.</p>
            </div>
        """, unsafe_allow_html=True)
        col1, _ = st.columns([1, 1])
        with col1:
            st.markdown("<div class='executive-card'>", unsafe_allow_html=True)
            name = st.text_input("Nombre Completo:")
            area = st.selectbox("Especialidad Táctica:", list(DYNAMIC_MCQ.keys()))
            if st.button("Activar Protocolo de 15 Etapas 🧠"):
                if name:
                    st.session_state.user_name = name
                    st.session_state.user_area = area
                    st.session_state.screen = 'placement_test'
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- EXAMEN DINÁMICO (15 ETAPAS) ---
    elif st.session_state.screen == 'placement_test':
        questions = DYNAMIC_MCQ[st.session_state.user_area]
        total_steps = len(questions) + 3
        current_step = st.session_state.placement_step
        
        st.title(f"🎯 Etapa {current_step + 1} de {total_steps} ({st.session_state.user_area})")
        st.progress(current_step / total_steps)

        if current_step < len(questions):
            q_data = questions[current_step]
            st.markdown(f"<div class='executive-card'><h4>{q_data['q']}</h4></div>", unsafe_allow_html=True)
            for i, opt in enumerate(q_data['options']):
                if st.button(opt, key=f"btn_{current_step}_{i}"):
                    if i == q_data['ans']: st.session_state.placement_score += 10
                    st.session_state.placement_step += 1
                    st.rerun()
        else:
            ai_step = current_step - len(questions)
            scenarios = [
                f"Explain a technical failure in {st.session_state.user_area} and its impact on the company's EBITDA.",
                "How would you lead a cross-functional team during a global audit crisis?",
                "What is your 90-day strategy to optimize the bottleneck in your current operation?"
            ]
            st.markdown(f"<div class='executive-card'><b>Escenario AI {ai_step + 1}:</b><br><br><i>\"{scenarios[ai_step]}\"</i></div>", unsafe_allow_html=True)
            ans = st.text_area("Responde en inglés con autoridad:", key=f"ai_{ai_step}")
            if st.button("Validar Respuesta"):
                if len(ans) > 20:
                    st.session_state.placement_ai_responses.append(ans)
                    st.session_state.placement_step += 1
                    if st.session_state.placement_step == total_steps: st.session_state.screen = 'finalizing'
                    st.rerun()

    # --- EVALUACIÓN FINAL IA ---
    elif st.session_state.screen == 'finalizing':
        with st.spinner("Tu Mentor Elite está auditando tus resultados..."):
            all_text = " ".join(st.session_state.placement_ai_responses)
            prompt = f"Audit this {st.session_state.user_area} expert. Score: {st.session_state.placement_score}/120. Answers: {all_text}. Determine CEFR Level (A2-C2). Feedback in Spanish."
            res = call_ai(prompt, API_KEY)
            st.session_state.placement_eval = res
            for level in ["C2", "C1", "B2", "B1"]:
                if level in res:
                    st.session_state.english_level = f"{level} - Certified"
                    break
            if st.session_state.english_level == "No Evaluado": st.session_state.english_level = "B1 - Intermediate"
            st.session_state.screen = 'results'
            st.rerun()

    elif st.session_state.screen == 'results':
        st.markdown(f"<div class='level-box'><h1>{st.session_state.english_level}</h1><p>Auditoría de 15 etapas completada.</p></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='executive-card'>{st.session_state.placement_eval}</div>", unsafe_allow_html=True)
        if st.button("Desbloquear War Room ⚔️"):
            st.session_state.screen = 'dashboard'
            st.rerun()

# --- FASE 2: WAR ROOM (RESTAURADO) ---
else:
    st.title(f"🛡️ War Room: {st.session_state.user_name}")
    
    tabs = st.tabs(["📅 Roadmap 30 Días", "🤖 AI Combat Lab", "⚔️ Power Verbs", "🔥 The Forge", "📖 Enciclopedia"])
    
    # 1. ROADMAP (PLAN 30 DÍAS)
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

    # 2. COMBAT LAB (SIMULACIONES MULTIMEDIA)
    with tabs[1]:
        mission = next((p for p in THIRTY_DAY_PLAN if p['day'] == st.session_state.current_day), THIRTY_DAY_PLAN[-1])
        st.subheader(f"Misión Diaria: {mission['title']}")
        
        col_m1, col_m2 = st.columns([2, 1])
        
        with col_m1:
            if st.button("🎙️ Generar Escenario con el Mentor"):
                with st.spinner("Preparando entrenamiento..."):
                    st.session_state.daily_q = call_ai(f"Elite Mentor. Ask a tough question about {mission['focus']} to a {st.session_state.user_area} expert.", API_KEY)
                    # Al generar, la IA habla automáticamente
                    st_text_to_speech(st.session_state.daily_q)
            
            if 'daily_q' in st.session_state:
                st.markdown(f"<div class='executive-card'><b>Mentor:</b> {st.session_state.daily_q}</div>", unsafe_allow_html=True)
                
                # BOTÓN PARA VOLVER A ESCUCHAR
                if st.button("🔊 Re-play AI Voice"):
                    st_text_to_speech(st.session_state.daily_q)
                
                # ÁREA DE RESPUESTA
                ans_text = st.text_area("Tu respuesta (Escribe o usa el dictado abajo):", key="combat_ans_area")
                
                # COMPONENTE DE DICTADO (STT)
                st_speech_to_text(key="speech_input")
                
                # Sincronización del dictado con el área de texto
                if st.session_state.get('speech_input'):
                    st.write(f"✍️ **Dictado detectado:** {st.session_state.speech_input}")
                    if st.button("Usar dictado como respuesta"):
                        st.session_state.combat_ans_area = st.session_state.speech_input
                
                if st.button("Auditar Respuesta Ejecutiva"):
                    with st.spinner("Evaluando impacto..."):
                        # Pedimos traducción y feedback detallado
                        prompt = f"""Evaluate: {ans_text}. 
                        Question was: {st.session_state.daily_q}.
                        Provide in SPANISH:
                        1. SCORE (0-100)
                        2. FEEDBACK TÉCNICO
                        3. TRADUCCIÓN DE TU RESPUESTA: [Traducción exacta al español]
                        4. VERSIÓN BOARDROOM: [Perfect script in English]
                        """
                        feedback = call_ai(prompt, API_KEY)
                        st.markdown(f"<div class='level-box'>{feedback}</div>", unsafe_allow_html=True)
                        st.session_state.xp += 100

        with col_m2:
            st.markdown("""
                <div class='executive-card' style='font-size: 0.9em; border-left-color: #f59e0b;'>
                <h4>💡 Tips de Role-play</h4>
                <ul>
                    <li><b>Escucha activa:</b> Usa el botón 🔊 para imitar la entonación del mentor.</li>
                    <li><b>Dictado:</b> Usa el micrófono para validar tu fluidez. Si la IA no te entiende, un humano tampoco lo hará.</li>
                    <li><b>Traducción:</b> Revisa la sección de traducción para asegurar que tus ideas se mantienen fieles en ambos idiomas.</li>
                </ul>
                </div>
            """, unsafe_allow_html=True)

    # 3. POWER VERBS
    with tabs[2]:
        st.subheader("Combate de Reflejos: Power Verbs")
        drill = st.session_state.current_drill
        st.markdown(f"<div class='executive-card' style='border-color:#f59e0b;'>Un Junior diría: <b>'{drill[0]}'</b></div>", unsafe_allow_html=True)
        pv_ans = st.text_input("Sustituye por la versión ejecutiva:")
        if st.button("Validar Impacto 🎯"):
            if drill[1].lower() in pv_ans.lower():
                st.success(f"¡Neutralizado! Versión correcta: '{drill[1]}'")
                st.session_state.xp += 50
                st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS)
                time.sleep(1)
                st.rerun()
            else: st.error(f"Sigue siendo básico. La frase letal es: '{drill[1]}'")

    # 4. THE FORGE
    with tabs[3]:
        st.subheader("La Fragua: Forja de Logros")
        draft = st.text_area("Ingresa un logro básico:")
        if st.button("⚒️ Forjar Logro VP"):
            with st.spinner("Refinando..."):
                res = call_ai(f"Transform to STAR executive achievement in English focused on EBITDA: {draft}", API_KEY)
                st.markdown(f"<div class='executive-card'><b>Resultado VP:</b><br>{res}</div>", unsafe_allow_html=True)

    # 5. ENCICLOPEDIA
    with tabs[4]:
        st.subheader("Enciclopedia Técnica")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("<span class='badge-ops'>🏭 Ops & Supply</span>", unsafe_allow_html=True)
            st.write("- **EBITDA:** Beneficio operativo.")
            st.write("- **Hard Savings:** Ahorros reales.")
        with c2:
            st.markdown("<span class='badge-tech'>🧬 Tech & Data</span>", unsafe_allow_html=True)
            st.write("- **SQL Query:** Consulta de datos.")
            st.write("- **BigQuery:** Almacén de Google.")
        with c3:
            st.markdown("<span class='badge-compliance'>⚖️ Quality</span>", unsafe_allow_html=True)
            st.write("- **IATF 16949:** Calidad Automotriz.")
            st.write("- **Cpk:** Capacidad de proceso.")

st.divider()
st.caption("Protocolo desarrollado para Fernando Montes Delgado | Multimedia Enabled: STT & TTS Integration")
