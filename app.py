import streamlit as st
import requests
import time
import random
import json
import copy
import streamlit.components.v1 as components

# --- IMPORTACIÓN SEGURA DE FIRESTORE Y CREDENCIALES ---
try:
    from google.cloud import firestore
    from google.oauth2 import service_account
except ImportError:
    firestore = None
    service_account = None

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Executive Mastery SaaS", 
    page_icon="⚙️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONFIGURACIÓN DE PERSISTENCIA (FIRESTORE) ---
app_id = getattr(st.secrets, "__app_id", "war-room-executive-fernando")

def get_db():
    if firestore is None: return None
    if "FIREBASE_KEY" not in st.secrets: return None
    try:
        raw_key = st.secrets["FIREBASE_KEY"]
        key_dict = json.loads(raw_key, strict=False)
        creds = service_account.Credentials.from_service_account_info(key_dict)
        return firestore.Client(credentials=creds, project=key_dict["project_id"])
    except:
        return None

db = get_db()

def save_user_progress():
    if not db or not st.session_state.get("user_name"): return
    try:
        user_id = st.session_state.user_name.lower().replace(" ", "_")
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
    except: pass

def load_user_progress(name):
    if not db: return False
    try:
        user_id = name.lower().replace(" ", "_")
        doc_ref = db.collection("artifacts").document(app_id).collection("public").document("data").collection("users").document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            u = doc.to_dict()
            st.session_state.user_name = u["user_name"]
            st.session_state.user_area = u.get("user_area", "Operaciones & Supply Chain")
            st.session_state.english_level = u.get("english_level", "No Evaluado")
            st.session_state.xp = u.get("xp", 0)
            st.session_state.current_day = u.get("current_day", 1)
            st.session_state.placement_completed = u.get("placement_completed", False)
            st.session_state.placement_eval_detailed = u.get("placement_eval_detailed", "")
            
            if st.session_state.placement_completed:
                st.session_state.screen = 'dashboard'
            else:
                st.session_state.screen = 'setup_area'
            return True
    except: pass
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
        background-color: #064e3b; padding: 30px; border-radius: 15px; border-left: 6px solid #10b981; color: #ecfdf5; text-align: left;
    }
    .eval-box {
        background-color: #1e293b; padding: 25px; border-radius: 12px; border-left: 5px solid #f59e0b; margin-bottom: 15px;
    }
    .day-card {
        background-color: #1e293b; padding: 20px; border-radius: 15px; border: 2px solid #334155; margin-bottom: 15px;
    }
    .day-active { border-color: #f59e0b; background-color: #451a03; box-shadow: 0 0 15px rgba(245, 158, 11, 0.3); }
    .diff-badge { padding: 4px 10px; border-radius: 5px; font-size: 0.8em; font-weight: bold; }
    .diff-facil { background-color: #064e3b; color: #34d399; }
    .diff-media { background-color: #78350f; color: #fbbf24; }
    .diff-dificil { background-color: #7f1d1d; color: #f87171; }
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
    <div style="text-align: center;"><button onclick="startDictation()" style="background: #f59e0b; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor:pointer;">🎙️ Click to Speak (English)</button></div>
    """
    return components.html(script, height=80)

def st_text_to_speech(text):
    if text:
        clean = text.replace('"', '\\"').replace('\n', ' ')
        components.html(f"<script>const m=new SpeechSynthesisUtterance('{clean}');m.lang='en-US';m.rate=0.95;window.speechSynthesis.speak(m);</script>", height=0)

# --- BÓVEDA DE API ---
try: API_KEY = st.secrets["GEMINI_API_KEY"]
except: API_KEY = ""

# --- BANCO DE PREGUNTAS (SISTEMA ADAPTATIVO 3 NIVELES) ---
DYNAMIC_MCQ = {
    "Operaciones & Supply Chain": {
        "facil": [
            {"q": "What does 'Lead Time' mean?", "options": ["Production speed", "Total time from order to delivery", "Machine uptime", "The boss's schedule"], "ans": 1},
            {"q": "A 'Stockout' occurs when:", "options": ["Inventory is exhausted", "Sales are too high", "Warehouse is full", "Prices go up"], "ans": 0},
            {"q": "What does ROI stand for?", "options": ["Return on Investment", "Rate of Interest", "Risk of Inflation", "Rule of Integration"], "ans": 0},
            {"q": "A 'Bottleneck' is:", "options": ["A glass container", "A constraint limiting the overall throughput", "A high-speed machine", "A type of inventory"], "ans": 1},
            {"q": "What is 'Safety Stock'?", "options": ["Guards at the warehouse", "Extra inventory kept to prevent stockouts", "Broken parts", "Money in the bank"], "ans": 1},
            {"q": "KPI stands for:", "options": ["Key Performance Indicator", "Key Product Index", "Known Process Issue", "Keep People Informed"], "ans": 0}
        ],
        "media": [
            {"q": "What is the primary goal of an S&OP meeting?", "options": ["To hire people", "To align demand forecasts with supply execution plans", "To count physical inventory", "To fix broken machinery"], "ans": 1},
            {"q": "Inventory Record Accuracy (IRA) protects:", "options": ["Employee morale", "MRP reliability and EBITDA", "Safety stock reduction only", "Machine OEE"], "ans": 1},
            {"q": "A bottleneck impacts 15% of your throughput. Action?", "options": ["Hire more operators globally.", "Perform a Takt-time analysis to balance flow.", "Increase machine speed to max.", "Report a breakdown."], "ans": 1},
            {"q": "EBITDA improves primarily when:", "options": ["OPEX increases", "Revenue grows and operational costs are optimized", "Margins shrink", "Production slows down"], "ans": 1},
            {"q": "To present a CAPEX request, you focus on:", "options": ["The fact that the old machines are ugly.", "The projected ROI through increased throughput and reduced maintenance OPEX.", "Safety complaints from operators.", "The modern features of the new models."], "ans": 1},
            {"q": "What is 'Sub-optimization'?", "options": ["Not working fast enough.", "When a localized improvement negatively impacts the overall system.", "A procurement failure.", "Outdated machinery."], "ans": 1}
        ],
        "dificil": [
            {"q": "A tier-1 supplier announces a 4-week delay. Board update?", "options": ["I am escalating to procurement for penalties.", "I am orchestrating a contingency plan with alternative vendors to protect OEE.", "We will utilize safety stock and halt production.", "I am monitoring the discrepancy closely."], "ans": 1},
            {"q": "Inventory carrying cost reaches 30%. Your executive initiative:", "options": ["Dispose of obsolete inventory to free space.", "Implement a pull system backed by predictive modeling to reduce buffers.", "Relocate stock to a cheaper facility.", "Freeze procurement for a quarter."], "ans": 1},
            {"q": "Freight costs are shrinking EBITDA. Strategic move?", "options": ["Reduce logistics headcount.", "Spearhead a multi-modal transport strategy focused on route optimization.", "Increase product prices immediately.", "Hold non-essential shipments."], "ans": 1},
            {"q": "A massive port strike threatens inbound materials. Executive response:", "options": ["Wait for customs to clear naturally.", "Expedite critical materials via air freight to secure the master schedule.", "Declare Force Majeure.", "Cancel incoming orders."], "ans": 1},
            {"q": "A sudden demand surge exceeds forecast by 40%. You respond by:", "options": ["Running all lines 24/7.", "Orchestrating agile production shifts while monitoring margin erosion from overtime.", "Ignoring the forecast error.", "Telling sales the plant cannot support it."], "ans": 1},
            {"q": "How to report a cost reduction initiative?", "options": ["I helped reduce expenses.", "I spearheaded a strategic initiative delivering $274k in hard savings.", "I was responsible for cost-cutting.", "The department reduced costs."], "ans": 1}
        ]
    },
    "Calidad & Lean Manufacturing": {
        "facil": [
            {"q": "What is a 'Non-conformance'?", "options": ["A late employee", "A product that fails to meet specification", "A new idea", "A meeting"], "ans": 1},
            {"q": "The '5 Whys' method is used for:", "options": ["Asking questions", "Finding the Root Cause of a problem", "Interviewing people", "Setting prices"], "ans": 1},
            {"q": "What is 'Poke-Yoke'?", "options": ["A game", "Error-proofing a process", "A cleaning method", "Fast production"], "ans": 1},
            {"q": "What does 'Defect' mean in Lean?", "options": ["A good part", "Any output that does not meet customer requirements", "A slow machine", "A type of tool"], "ans": 1},
            {"q": "A 'Gemba Walk' is:", "options": ["Walking for exercise.", "Observing the actual place of work.", "Checking if people are working hard.", "Talking to staff."], "ans": 1}
        ],
        "media": [
            {"q": "What does a high Cpk indicate?", "options": ["Process instability", "Process capability and strict Specification compliance", "High cost", "Slow production"], "ans": 1},
            {"q": "An '8D Report' is primarily used for:", "options": ["Counting parts", "Systemic and cross-functional problem solving", "Design", "Marketing"], "ans": 1},
            {"q": "A major non-conformance is found in design. Which tool identifies it?", "options": ["Basic checklist.", "A cross-functional FMEA.", "Customer survey.", "Post-production audit."], "ans": 1},
            {"q": "How do you explain 'Muda' to a CFO?", "options": ["It means we have too much trash.", "Non-value-added activities impacting EBITDA and cycle time.", "It is a Japanese word.", "We need more robots."], "ans": 1},
            {"q": "A critical gauge is out of calibration. Leadership action:", "options": ["Recalibrate and continue.", "Initiate a retroactive risk assessment on all products measured.", "Buy a new gauge.", "Blame the lab."], "ans": 1}
        ],
        "dificil": [
            {"q": "A VDA 6.3 auditor identifies a systemic failure in your control plan. Action?", "options": ["Request a waiver.", "Deploy immediate containment and initiate a cross-functional 8D report.", "Update the FMEA secretly.", "Halt production and recalibrate Cpk."], "ans": 1},
            {"q": "Your process Cpk drops to 0.82. Communication to global VP?", "options": ["Process is stable but slow.", "Process is incapable of meeting specs; deploying stabilization countermeasures.", "Defect cost is rising.", "Widen the tolerance limits."], "ans": 1},
            {"q": "A critical safety non-conformance is found at the customer site. First step?", "options": ["Dispatch an engineer.", "Orchestrate a global quarantine of all suspect lots to protect the end user.", "Review control charts.", "Fire the inspector."], "ans": 1},
            {"q": "To foster a 'Zero Defects' culture, your main strategy is:", "options": ["Increasing inspection headcount.", "Shifting focus from defect detection to proactive process control (FMEA).", "Hanging posters.", "Offering bonuses."], "ans": 1},
            {"q": "Internal audit reveals non-compliance with standard work. You state:", "options": ["Instructions are too complicated.", "I am spearheading a retraining matrix combined with leader standard work audits.", "Rewrite the instructions.", "Issue warning letters."], "ans": 1}
        ]
    },
    "Project Manager": {
        "facil": [
            {"q": "What is a 'Gantt Chart'?", "options": ["A budget tool", "A visual timeline of project schedules", "An HR file", "A quality report"], "ans": 1},
            {"q": "What is a 'Kick-off Meeting'?", "options": ["End of project party", "Meeting to align team on objectives and baseline", "Firing a vendor", "Lunch break"], "ans": 1},
            {"q": "What is a 'Milestone'?", "options": ["A heavy rock", "A significant point or event in a project", "A mistake", "A daily task"], "ans": 1},
            {"q": "What does 'Scope' refer to?", "options": ["The cost", "The detailed deliverables and boundaries of a project", "The timeline", "The manager"], "ans": 1},
            {"q": "A 'Stakeholder' is:", "options": ["Only the CEO", "Anyone affected by or influencing the project", "The vendor", "The customer only"], "ans": 1}
        ],
        "media": [
            {"q": "Scope Creep refers to:", "options": ["Moving slowly", "Uncontrolled changes or continuous growth in a project's scope", "A scary project", "Under budget delivery"], "ans": 1},
            {"q": "An 'Agile' methodology focuses on:", "options": ["Rigid planning", "Iterative development and adaptability", "Long documentation", "Working alone"], "ans": 1},
            {"q": "When defining the project baseline, the crucial element is:", "options": ["Color coding the chart.", "Securing formal sign-off on scope, budget, and timeline from stakeholders.", "Assigning names to micro-tasks.", "Choosing the software."], "ans": 1},
            {"q": "To explain 'Earned Value Management' (EVM) you say:", "options": ["It shows spent money.", "It integrates scope, schedule, and cost to objectively measure performance.", "It calculates bonuses.", "It predicts quality."], "ans": 1},
            {"q": "A team member is underperforming, risking timeline. You:", "options": ["Do their work.", "Initiate a performance correction plan while redistributing tasks temporarily.", "Complain in meeting.", "Ignore it."], "ans": 1}
        ],
        "dificil": [
            {"q": "A key stakeholder requests a major scope change mid-project. Executive response:", "options": ["Implement immediately.", "Assess impact on critical path and EBITDA before orchestrating realignment.", "Deny the request.", "Delegate decision."], "ans": 1},
            {"q": "Project forecasts a 15% budget overrun. Report to steering committee?", "options": ["Suppliers charged more.", "I am identifying capital reallocations to mitigate variance and protect ROI.", "Engineering underestimated.", "We need more funds."], "ans": 1},
            {"q": "Two critical departments are misaligned on goals. Leadership action:", "options": ["Escalate to CEO.", "Spearhead a cross-functional workshop to re-baseline objectives and secure buy-in.", "Proceed with the largest budget.", "Send a mass email."], "ans": 1},
            {"q": "Project hits a roadblock on the critical path. You state:", "options": ["We are delayed.", "I have deployed a risk mitigation strategy to compress subsequent phases.", "Path is too dangerous.", "Milestone will be missed."], "ans": 1},
            {"q": "Sponsor wants to launch early, skipping UAT. You advise:", "options": ["Agreeing to look fast.", "Highlighting the severe enterprise risk of deploying unvalidated deliverables to production.", "Testing on weekend.", "Asking for waiver."], "ans": 1}
        ]
    }
}
# Llenado automático (Fallback) de especialidades faltantes para evitar errores
for area in ["Ingeniería de Producto", "Data Science & SQL", "Logística", "Producción", "Otra"]:
    if area not in DYNAMIC_MCQ:
        DYNAMIC_MCQ[area] = copy.deepcopy(DYNAMIC_MCQ["Operaciones & Supply Chain"])

# --- KNOWLEDGE BASE ---
THIRTY_DAY_PLAN = [
    {"day": 1, "phase": "Cimientos", "title": "El Pitch de Impacto (EBITDA)"},
    {"day": 2, "phase": "Defensa", "title": "Auditorías Globales"},
    {"day": 3, "phase": "Sistemas", "title": "Cultura Cero Defectos"},
    {"day": 7, "phase": "Boardroom", "title": "Prueba de Fuego (CEO)"}
]
POWER_VERBS_DRILLS = [("I fixed the problem", "I rectified the non-conformance")]

# --- MOTOR DE IA (GEMINI 3 FLASH PREVIEW) ---
def call_ai(prompt, api_key):
    if not api_key: return "⚠️ Error: Falta la API Key."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=25)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        return f"Error IA: {response.status_code}"
    except: return "Error de conexión."

# --- MANEJO DE ESTADO CENTRALIZADO ---
if 'screen' not in st.session_state: st.session_state.screen = 'home'
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_area' not in st.session_state: st.session_state.user_area = "Operaciones & Supply Chain"
if 'english_level' not in st.session_state: st.session_state.english_level = "No Evaluado"
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'current_day' not in st.session_state: st.session_state.current_day = 1
if 'placement_step' not in st.session_state: st.session_state.placement_step = 0
if 'placement_score' not in st.session_state: st.session_state.placement_score = 0
if 'placement_ai_responses' not in st.session_state: st.session_state.placement_ai_responses = []
if 'dynamic_scenarios' not in st.session_state: st.session_state.dynamic_scenarios = []

# Variables para algoritmo adaptativo
if 'current_diff' not in st.session_state: st.session_state.current_diff = "media"
if 'used_q_texts' not in st.session_state: st.session_state.used_q_texts = []
if 'current_q' not in st.session_state: st.session_state.current_q = None

# --- PANEL LATERAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 2em;'>🦅 CONTROL</h1>", unsafe_allow_html=True)
    if db: st.success("☁️ Guardado en la Nube: ACTIVADO")
    else: st.warning("⚠️ Sin conexión a la base de datos (Modo Local)")
    st.divider()
    if st.session_state.user_name:
        st.write(f"**Líder:** {st.session_state.user_name}")
        st.write(f"**Especialidad:** {st.session_state.user_area}")
        st.write(f"**Nivel:** {st.session_state.english_level}")
        st.write(f"**XP:** {st.session_state.xp}")
    if st.button("🔄 Reset / Cerrar Sesión"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# --- FUNCIONES ADAPTATIVAS ---
def get_adaptive_question(area, diff):
    # Buscar en la dificultad actual
    pool = DYNAMIC_MCQ.get(area, DYNAMIC_MCQ["Operaciones & Supply Chain"]).get(diff, [])
    available = [q for q in pool if q['q'] not in st.session_state.used_q_texts]
    
    # Si se acabaron en esta dificultad, busca en otra
    if not available:
        for fallback in ["media", "facil", "dificil"]:
            pool = DYNAMIC_MCQ.get(area, DYNAMIC_MCQ["Operaciones & Supply Chain"]).get(fallback, [])
            available = [q for q in pool if q['q'] not in st.session_state.used_q_texts]
            if available:
                diff = fallback
                break
                
    if available:
        q = copy.deepcopy(random.choice(available))
        st.session_state.used_q_texts.append(q['q'])
        correct_opt = q['options'][q['ans']]
        random.shuffle(q['options'])
        q['ans'] = q['options'].index(correct_opt)
        q['diff_label'] = diff
        return q
    return None

def adjust_difficulty(is_correct, current_diff):
    if is_correct:
        return "dificil" if current_diff == "media" else ("media" if current_diff == "facil" else "dificil")
    else:
        return "facil" if current_diff == "media" else ("media" if current_diff == "dificil" else "facil")

# --- ENRUTADOR PRINCIPAL ---
if st.session_state.screen == 'home':
    st.markdown("<div class='hero-box'><h1>Executive Mastery Protocol</h1><p>Algoritmo Adaptativo (GMAT Style) Activado.</p></div>", unsafe_allow_html=True)
    col1, _ = st.columns([1, 1])
    with col1:
        name_input = st.text_input("Ingresa tu Nombre Completo:")
        area_input = st.selectbox("Selecciona tu Especialidad Táctica:", list(DYNAMIC_MCQ.keys()))
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Acceder al Sistema 🧠"):
            if name_input:
                with st.spinner("Buscando expediente en la nube..."):
                    if load_user_progress(name_input):
                        st.success(f"¡Bienvenido de vuelta, {st.session_state.user_name}!")
                        time.sleep(1)
                        st.rerun() 
                    else:
                        st.session_state.user_name = name_input
                        st.session_state.user_area = area_input
                        st.session_state.screen = 'placement_test'
                        st.rerun()
            else:
                st.warning("Por favor, ingresa tu nombre.")

elif st.session_state.screen == 'placement_test':
    total_mcq = 9 # Proporción de oro: 9 preguntas adaptativas
    total_ai = 3  # Proporción de oro: 3 escenarios de voz/texto
    total_steps = total_mcq + total_ai
    current_step = st.session_state.placement_step
    
    st.progress(current_step / total_steps)
    st.subheader(f"Etapa {current_step+1} de {total_steps} ({st.session_state.user_area})")

    if current_step < total_mcq:
        # 1. Cargar pregunta adaptativa si no hay una en pantalla
        if st.session_state.current_q is None:
            st.session_state.current_q = get_adaptive_question(st.session_state.user_area, st.session_state.current_diff)
            st.rerun() # Recargar para mostrarla
            
        q = st.session_state.current_q
        
        # Insignia visual de dificultad
        diff_color = f"diff-{q['diff_label']}"
        diff_text = q['diff_label'].upper()
        st.markdown(f"<span class='diff-badge {diff_color}'>NIVEL: {diff_text}</span>", unsafe_allow_html=True)
        
        st.markdown(f"<div class='executive-card'><h4>{q['q']}</h4></div>", unsafe_allow_html=True)
        for i, opt in enumerate(q['options']):
            if st.button(opt, key=f"btn_{current_step}_{i}"):
                is_correct = (i == q['ans'])
                if is_correct:
                    # Puntaje ponderado por dificultad
                    pts = 15 if q['diff_label'] == 'dificil' else (10 if q['diff_label'] == 'media' else 5)
                    st.session_state.placement_score += pts
                
                # Ajustar dificultad para la SIGUIENTE pregunta
                st.session_state.current_diff = adjust_difficulty(is_correct, q['diff_label'])
                st.session_state.current_q = None # Limpiar para generar la siguiente
                st.session_state.placement_step += 1
                st.rerun()
    else:
        ai_step = current_step - total_mcq
        if not st.session_state.dynamic_scenarios:
            with st.spinner("IA generando 3 escenarios ejecutivos en tiempo real..."):
                prompt = f"Write exactly 3 tough corporate scenarios asking for action, tailored for a {st.session_state.user_area} leader. Format: Scenario 1 --- Scenario 2 --- Scenario 3"
                res = call_ai(prompt, API_KEY)
                st.session_state.dynamic_scenarios = res.split('---')

        current_scenario = st.session_state.dynamic_scenarios[ai_step] if ai_step < len(st.session_state.dynamic_scenarios) else "Explain a major process failure and your leadership containment action."
        st.markdown(f"<div class='executive-card'><b>Situación Crítica (Demuestra tu autoridad VP):</b><br>{current_scenario}</div>", unsafe_allow_html=True)
        ans = st.text_area("Tu Respuesta en Inglés:", key=f"ans_{ai_step}")
        st_speech_to_text(key=f"voice_{ai_step}")
        if st.button("Validar Respuesta"):
            if len(ans) > 20:
                st.session_state.placement_ai_responses.append({"q": current_scenario, "a": ans})
                st.session_state.placement_step += 1
                if st.session_state.placement_step >= total_steps: 
                    st.session_state.screen = 'finalizing'
                st.rerun()
            else:
                st.warning("Desarrolla más tu respuesta para que la IA pueda auditar tu nivel de autoridad.")

elif st.session_state.screen == 'finalizing':
    st.markdown("<h3 style='text-align:center;'>Procesando Analíticas de Comportamiento Ejecutivo...</h3>", unsafe_allow_html=True)
    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.02)
        my_bar.progress(percent_complete + 1)
        
    with st.spinner("El Mentor Elite está cruzando tus respuestas con estándares C-Level..."):
        ai_text = "\n".join([f"Q: {x['q']}\nA: {x['a']}" for x in st.session_state.placement_ai_responses])
        prompt = f"""
        Actúa como un CEO estricto evaluando a un gerente de {st.session_state.user_area}.
        El candidato obtuvo {st.session_state.placement_score} puntos en la prueba técnica adaptativa.
        Sus respuestas orales/escritas ante crisis fueron: {ai_text}.
        
        DEVUELVE TU RESPUESTA ESTRICTAMENTE EN ESTE FORMATO MARKDOWN EXACTO (No uses json, usa este texto con HTML):

        <div class='eval-box'>
        <h3>🏆 NIVEL ASIGNADO: [Elige uno: C2 - Master, C1 - Executive, B2 - Advanced, B1 - Intermediate]</h3>
        </div>
        
        <div class='eval-box'>
        <h3>📊 ANÁLISIS DE ERRORES:</h3>
        <ul>
        <li>[Error técnico o gramatical grave que cometió]</li>
        <li>[Falta de autoridad en su vocabulario detectada]</li>
        </ul>
        </div>

        <div class='eval-box'>
        <h3>⚠️ ÁREAS DE OPORTUNIDAD:</h3>
        <ul>
        <li>[Qué debe estudiar o mejorar (ej. usar voz pasiva, jerga financiera)]</li>
        </ul>
        </div>

        <div class='eval-box'>
        <h3>💡 TIPS PRO PARA NIVEL VP:</h3>
        <ul>
        <li>[Tip hiper-específico de comunicación ejecutiva 1]</li>
        <li>[Tip hiper-específico de comunicación ejecutiva 2]</li>
        </ul>
        </div>
        """
        res = call_ai(prompt, API_KEY)
        st.session_state.placement_eval_detailed = res
        
        # Extraer nivel
        for level in ["C2", "C1", "B2", "B1", "A2"]:
            if level in res: 
                st.session_state.english_level = f"{level} - Certified"
                break
        if st.session_state.english_level == "No Evaluado": st.session_state.english_level = "B2 - Certified"
        
        st.session_state.placement_completed = True
        save_user_progress() 
        st.session_state.screen = 'results' 
        st.rerun()

elif st.session_state.screen == 'results':
    st.markdown("<h1 style='text-align: center; color: #f59e0b;'>Auditoría Finalizada</h1>", unsafe_allow_html=True)
    
    # Se renderiza el HTML exacto que pedimos a la IA para que se vea hermoso
    st.markdown(st.session_state.placement_eval_detailed, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Desbloquear Mi War Room ⚔️"):
            st.session_state.screen = 'dashboard'
            st.rerun()

elif st.session_state.screen == 'dashboard':
    st.title(f"🛡️ War Room: {st.session_state.user_name}")
    tabs = st.tabs(["📅 Roadmap", "🤖 AI Combat Lab", "⚔️ Power Verbs", "🔥 The Forge"])
    with tabs[0]: st.write("Roadmap en progreso...")
    with tabs[1]: st.write("Combat lab en progreso...")

st.divider()
st.caption("Protocolo diseñado por Ing. Fernando Montes Delgado | Algoritmo Adaptativo & Firebase Cloud Enabled | Gemini 3 Flash Preview")
