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
    page_title="Global Executive Mastery", 
    page_icon="💼", 
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
            "user_position": st.session_state.get("user_position", "Director or Manager"),
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
            loaded_area = u.get("user_area", ["Operaciones & Supply Chain"])
            st.session_state.user_area = loaded_area if isinstance(loaded_area, list) else [loaded_area]
            st.session_state.user_position = u.get("user_position", "Director or Manager")
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

# --- CSS + MODO IMPRESIÓN ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em; 
        background: linear-gradient(90deg, #f59e0b 0%, #f97316 100%);
        color: #0f172a !important; font-weight: 900; font-size: 1.1em; border: none;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(245, 158, 11, 0.4); }
    .executive-card { background-color: #1e293b; padding: 30px; border-radius: 15px; border-left: 6px solid #3b82f6; margin-bottom: 20px; }
    .mission-card { background-color: #0f172a; padding: 25px; border-radius: 15px; border: 1px solid #334155; margin-top: 20px; }
    .level-box { background-color: #064e3b; padding: 30px; border-radius: 15px; border-left: 6px solid #10b981; color: #ecfdf5; }
    .eval-box { background-color: #1e293b; padding: 25px; border-radius: 12px; border-left: 5px solid #f59e0b; margin-bottom: 15px; }
    .circuit-box { background-color: #1e293b; border: 1px solid #3b82f6; padding: 20px; border-radius: 10px; margin-top: 15px; }
    .diff-badge { padding: 4px 10px; border-radius: 5px; font-size: 0.8em; font-weight: bold; }
    .diff-facil { background-color: #064e3b; color: #34d399; }
    .diff-media { background-color: #78350f; color: #fbbf24; }
    .diff-dificil { background-color: #7f1d1d; color: #f87171; }
    @media print {
        header, [data-testid="stSidebar"], .stButton { display: none !important; }
        .stApp { background-color: white !important; color: black !important; }
        .eval-box { background-color: white !important; color: black !important; border: 1px solid #cbd5e1 !important; border-left: 6px solid #3b82f6 !important; }
        h1, h2, h3, h4, p, li, span, b, i { color: black !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- MULTIMEDIA ---
def st_speech_to_text(key):
    script = """<script>const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)(); recognition.lang = 'en-US'; recognition.interimResults = false; function startDictation() { recognition.start(); } recognition.onresult = (event) => { const text = event.results[0][0].transcript; window.parent.postMessage({type: 'streamlit:setComponentValue', value: text, key: '""" + key + """'}, '*'); }; </script><div style="text-align: center;"><button onclick="startDictation()" style="background: #f59e0b; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor:pointer;">🎙️ Click to Speak (English)</button></div>"""
    return components.html(script, height=80)

def st_text_to_speech(text):
    if text:
        clean = text.replace('"', '\\"').replace('\n', ' ')
        components.html(f"<script>const m=new SpeechSynthesisUtterance('{clean}');m.lang='en-US';m.rate=0.95;window.speechSynthesis.speak(m);</script>", height=0)

# --- API ---
try: API_KEY = st.secrets["GEMINI_API_KEY"]
except: API_KEY = ""

# --- BANCO DE PREGUNTAS (SISTEMA ADAPTATIVO AVANZADO - OPCIONES COMPLEJAS) ---
DYNAMIC_MCQ = {
    "Operaciones & Supply Chain": {
        "facil": [
            {"q": "When optimizing a value stream, 'Lead Time' is best defined functionally as:", "options": ["The total velocity of production minus machine downtime.", "The overall elapsed time from the receipt of a customer order to its final delivery.", "The accumulated operational hours required to manufacture a single batch.", "The forecasted timeline provided by procurement for raw materials."], "ans": 1},
            {"q": "To effectively mitigate a 'Stockout' risk without inflating carrying costs, a manager should:", "options": ["Increase the total warehouse footprint globally.", "Over-order raw materials quarterly to ensure availability.", "Halt production schedules until demand completely stabilizes.", "Dynamically adjust Safety Stock levels based on demand variance."], "ans": 3},
            {"q": "In CAPEX justification, identifying the 'Bottleneck' implies finding:", "options": ["The machine with the highest preventive maintenance cost.", "The constraint that dictates the maximum throughput of the entire system.", "The oldest equipment on the production floor.", "The operational step with the highest headcount."], "ans": 1},
            {"q": "A 'KPI' dashboard is essentially useless if it does not:", "options": ["Feature highly complex graphical representations.", "Include every possible metric from the shop floor.", "Align directly with strategic business objectives and drive actionable insights.", "Require daily manual updates from the engineering team."], "ans": 2},
            {"q": "Implementing 'Safety Stock' acts primarily as a buffer against:", "options": ["Foreseeable fluctuations in labor availability.", "Uncertainties in supplier lead times and sudden demand spikes.", "Scheduled preventive maintenance downtime.", "Standard variations in currency exchange rates."], "ans": 1}
        ],
        "media": [
            {"q": "The primary strategic objective of a mature S&OP cycle is to:", "options": ["Isolate the sales team from production constraints.", "Ensure procurement buys materials at the lowest possible bulk cost.", "Align demand forecasts synchronously with supply execution and capacity plans.", "Minimize the need for cross-functional communication."], "ans": 2},
            {"q": "If Inventory Record Accuracy (IRA) drops below 90%, the most immediate risk is:", "options": ["A slight decrease in employee morale.", "Compromised MRP reliability leading to unplanned stockouts or excess capital tie-up.", "An immediate audit failure by external financial regulators.", "Increased cycle times on non-critical assemblies."], "ans": 1},
            {"q": "A bottleneck impacts 15% of your throughput. Your executive action is to:", "options": ["Immediately hire more operators across all shifts.", "Perform a Takt-time analysis to rebalance the flow around the constraint.", "Increase the machine speed parameters to maximum capacity.", "Submit a formal complaint to the equipment manufacturer."], "ans": 1},
            {"q": "An initiative successfully improves EBITDA primarily when:", "options": ["Operational expenses (OPEX) increase proportionally with revenue.", "Top-line revenue grows while operational costs are simultaneously optimized.", "Gross margins shrink due to aggressive market pricing.", "Production output is slowed to ensure perfect quality."], "ans": 1},
            {"q": "When presenting a CAPEX request to the Board, the focal point should be:", "options": ["The outdated aesthetics of the current machinery.", "The projected ROI through increased throughput and reduced maintenance OPEX.", "The volume of safety complaints submitted by union operators.", "The advanced software features of the new models."], "ans": 1}
        ],
        "dificil": [
            {"q": "A tier-1 supplier declares a 4-week Force Majeure delay. Your update to the Board should state:", "options": ["We are waiting for procurement to enforce contract penalties.", "I am orchestrating a contingency plan with alternative vendors to protect our OEE.", "We will utilize our entire safety stock and subsequently halt production.", "The discrepancy is being monitored closely by the logistics team."], "ans": 1},
            {"q": "Inventory carrying cost reaches a critical 30%. Your executive countermeasure is to:", "options": ["Dispose of obsolete inventory immediately to free up physical space.", "Implement a pull system backed by predictive modeling to systematically reduce buffers.", "Relocate current stock to a geographically cheaper facility.", "Freeze all procurement activities for the upcoming fiscal quarter."], "ans": 1},
            {"q": "Freight costs are eroding EBITDA margins due to expedites. The strategic move is to:", "options": ["Reduce the logistics department's headcount to offset costs.", "Spearhead a multi-modal transport strategy focused on rigorous route optimization.", "Increase finished product prices immediately to absorb the variance.", "Place a hold on all non-essential inbound shipments."], "ans": 1},
            {"q": "A sudden demand surge exceeds the quarter forecast by 40%. You respond by:", "options": ["Running all production lines 24/7 without adjusting maintenance schedules.", "Orchestrating agile production shifts while strictly monitoring margin erosion from overtime.", "Disregarding the forecast error as an anomaly.", "Informing the sales director that the plant capacity cannot support the surge."], "ans": 1},
            {"q": "When reporting a successful cost-reduction initiative, the most authoritative phrasing is:", "options": ["I helped reduce expenses in my department.", "I spearheaded a strategic initiative delivering $274k in audited hard savings.", "I was responsible for the team's cost-cutting efforts.", "The operations department managed to reduce overall costs."], "ans": 1}
        ]
    },
    "Calidad & Lean Manufacturing": {
        "facil": [
            {"q": "In Lean terminology, a 'Non-conformance' is officially understood as:", "options": ["A minor deviation that does not affect functionality.", "Any output or process state that fails to meet defined specifications.", "A disagreement between quality and production managers.", "A delay in the supplier's delivery schedule."], "ans": 1},
            {"q": "The primary utility of the '5 Whys' methodology is:", "options": ["To conduct thorough performance reviews of operators.", "To systematically drill down to the fundamental Root Cause of an anomaly.", "To justify budgetary increases for the quality department.", "To communicate issues to the end customer."], "ans": 1},
            {"q": "A 'Poke-Yoke' mechanism is implemented to:", "options": ["Speed up the assembly line.", "Error-proof a process, making it impossible to pass a defect forward.", "Clean the workspace efficiently.", "Track the attendance of line workers."], "ans": 1},
            {"q": "What constitutes a 'Defect' under the Lean manufacturing framework?", "options": ["A product that requires minimal rework.", "Any process output that fails to deliver value according to customer requirements.", "A machine operating at 80% capacity.", "A tool that needs recalibration."], "ans": 1},
            {"q": "Executing a 'Gemba Walk' requires a leader to:", "options": ["Review KPI dashboards from their office.", "Observe the actual place of work to understand the real process and identify Muda.", "Conduct a formal audit with external regulators.", "Give motivational speeches to the floor staff."], "ans": 1}
        ],
        "media": [
            {"q": "A Cpk index significantly greater than 1.33 quantitatively indicates:", "options": ["Process instability and a high likelihood of defects.", "High process capability and strict compliance with specification limits.", "Excessive operational costs relative to output.", "A slow, over-controlled production flow."], "ans": 1},
            {"q": "Initiating an '8D Report' is the standard protocol primarily for:", "options": ["Routine daily shift handovers.", "Systemic, cross-functional problem solving to prevent recurrence of critical failures.", "Designing new product prototypes.", "Marketing quality improvements to clients."], "ans": 1},
            {"q": "To proactively identify potential non-conformances during the design phase, the best tool is:", "options": ["A basic operator checklist.", "A cross-functional Failure Mode and Effects Analysis (FMEA).", "A post-production customer satisfaction survey.", "A randomized quality audit."], "ans": 1},
            {"q": "When explaining 'Muda' to a CFO, the most impactful translation is:", "options": ["It signifies that our facility produces too much physical trash.", "Non-value-added activities that directly negatively impact EBITDA and cycle times.", "It is a Japanese cultural term for continuous effort.", "It implies we need to invest heavily in robotics."], "ans": 1},
            {"q": "A critical measurement gauge is found to be out of calibration. The leadership action is to:", "options": ["Recalibrate it quietly and continue production.", "Initiate a retroactive risk assessment on all product lots measured since the last valid calibration.", "Immediately purchase a replacement gauge.", "Discipline the laboratory technician responsible."], "ans": 1}
        ],
        "dificil": [
            {"q": "A VDA 6.3 auditor identifies a systemic failure in your process control plan. Your response:", "options": ["Submit a formal request for a deviation waiver.", "Deploy immediate containment actions and initiate a cross-functional 8D investigation.", "Update the FMEA document internally without notifying the customer.", "Halt all production lines globally until a new Cpk is established."], "ans": 1},
            {"q": "Your critical process Cpk drops unexpectedly to 0.82. You communicate this to the global VP by stating:", "options": ["The process is stable but currently running slower than usual.", "The process is currently incapable of meeting specs; we are deploying immediate stabilization countermeasures.", "The cost of defects is rising, we need more budget.", "We need engineering to widen the tolerance limits."], "ans": 1},
            {"q": "A critical safety non-conformance is detected at the customer site. Your first executive step is to:", "options": ["Dispatch a quality engineer to verify the claim.", "Orchestrate a global quarantine of all suspect lots to unequivocally protect the end user.", "Review historical control charts for anomalies.", "Terminate the contract of the final inspector."], "ans": 1},
            {"q": "To foster a genuine 'Zero Defects' culture, your overarching strategy focuses on:", "options": ["Exponentially increasing end-of-line inspection headcount.", "Shifting the organizational focus from defect detection to proactive process control via FMEA.", "Displaying quality metrics aggressively on the shop floor.", "Offering financial bonuses for zero-defect days."], "ans": 1},
            {"q": "An internal audit reveals widespread non-compliance with Standard Work. You state:", "options": ["The current work instructions are overly complicated for the operators.", "I am spearheading a comprehensive retraining matrix coupled with rigorous leader standard work audits.", "We need to completely rewrite all instructions.", "I will issue formal warning letters to non-compliant staff."], "ans": 1}
        ]
    }
}
for area in ["Project Manager", "Ingeniería de Producto", "Data Science & SQL", "Logística", "Producción", "Otra"]:
    if area not in DYNAMIC_MCQ: DYNAMIC_MCQ[area] = copy.deepcopy(DYNAMIC_MCQ["Operaciones & Supply Chain"])

# --- DRILLS & VOCAB ---
POWER_VERBS_DRILLS = [("I fixed the problem", "I rectified the non-conformance"), ("I saved money", "I delivered substantial hard savings"), ("I used data", "I leveraged data analytics"), ("I started a project", "I spearheaded a strategic initiative"), ("I led the team", "I orchestrated the cross-functional team")]
CONNECTORS_DRILLS = [{"junior": "The supplier was late. We missed the deadline.", "type": "Causa y Efecto", "target": ["consequently", "therefore", "thus"]}, {"junior": "The budget was cut. We delivered the project on time.", "type": "Contraste", "target": ["nevertheless", "however", "despite this"]}, {"junior": "We increased production. We maintained zero defects.", "type": "Adición", "target": ["furthermore", "moreover", "additionally"]}]

DAILY_VOCAB = ["Leverage (Aprovechar al máximo)", "Spearhead (Liderar iniciativa)", "Mitigate (Reducir riesgo)", "EBITDA (Rentabilidad operativa)", "Consequently (Por lo tanto)", "Furthermore (Además)", "Orchestrate (Coordinar estratégicamente)", "Hard Savings (Ahorros auditables)", "Constraint (Cuello de botella)", "Deploy (Implementar/Desplegar)"]

# --- PLAN PROGRESIVO DE 90 DÍAS (3 MESES) ---
def generate_90_day_plan():
    plan = {}
    phases = ["Mes 1: Cimientos de Autoridad (A1->B1)", "Mes 2: Liderazgo Estratégico (B1->B2)", "Mes 3: Boardroom Fluency (B2->C1+)"]
    templates = [
        ("Pitch de Impacto Financiero", "Estructurar presentación en términos de EBITDA.", "Audio grabado del pitch corporativo."),
        ("Contención de Crisis (8D)", "Redactar un correo directivo ante un problema operativo.", "Email con conectores de causalidad."),
        ("Storytelling de KPIs", "Explicar métricas a directivos no técnicos.", "Discurso fluido de 2 minutos."),
        ("Manejo de Stakeholders", "Rebatir cambios de alcance sin perder compostura.", "Guión de negociación asertiva."),
        ("Defensa de Presupuesto (CAPEX)", "Justificar una inversión mediante el cálculo de ROI.", "One-pager de rentabilidad."),
        ("Auditoría Global", "Responder a hallazgos de auditores internacionales.", "Defensa verbal usando 'Risk-based thinking'.")
    ]
    for day in range(1, 91):
        phase_idx = min((day - 1) // 30, 2) 
        temp = templates[day % len(templates)]
        
        # Temas para Inmersión Activa según el día
        video_topic = "Supply Chain Resilience" if day % 2 == 0 else "Leadership under pressure"
        
        circuit_html = f"""
        <div class='circuit-box'>
            <h4 style='margin-top:0; color:#3b82f6;'>⏳ Circuito Diario de Entrenamiento (50 Minutos)</h4>
            <p style='font-size:0.9em; color:#cbd5e1; margin-bottom:15px;'>El aprendizaje tradicional no funciona. Sigue este circuito inmersivo para forjar fluidez neurolingüística.</p>
            <ul style='list-style-type: none; padding: 0;'>
                <li style='margin-bottom:10px;'><b>1️⃣ Inmersión Activa (10 min):</b> Busca en YouTube un video sobre <i>{video_topic}</i> (Harvard Business Review). Pausa cada minuto e intenta repetir lo que entendiste.</li>
                <li style='margin-bottom:10px;'><b>2️⃣ Shadowing Auditivo (10 min):</b> Ve a la pestaña '🎧 Shadowing', escucha la cadencia y repite en voz alta para romper el acento.</li>
                <li style='margin-bottom:10px;'><b>3️⃣ AI Combat Lab (10 min):</b> Solicita tu simulación del día al CEO y responde articulando ideas.</li>
                <li style='margin-bottom:10px;'><b>4️⃣ Conectores & Verbos (10 min):</b> Supera 3 ejercicios de reflejos en las pestañas de Vocabulario.</li>
                <li style='margin-bottom:0;'><b>5️⃣ La Fragua (10 min):</b> Documenta un logro operativo en formato C-Level.</li>
            </ul>
        </div>
        """
        plan[day] = {"phase": phases[phase_idx], "title": temp[0], "actividad": temp[1], "entregable": temp[2], "circuit": circuit_html}
    return plan

NINETY_DAY_PLAN = generate_90_day_plan()

# --- AI API ---
def call_ai(prompt, api_key):
    if not api_key: return "⚠️ Error: API Key no configurada en Secrets."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
    try:
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=25)
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "Error de conexión o timeout con la IA."

# --- ESTADO CENTRALIZADO ---
if 'screen' not in st.session_state: st.session_state.screen = 'home'
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_area' not in st.session_state: st.session_state.user_area = ["Operaciones & Supply Chain"]
if 'user_position' not in st.session_state: st.session_state.user_position = "Director or Manager"
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'current_day' not in st.session_state: st.session_state.current_day = 1
if 'placement_step' not in st.session_state: st.session_state.placement_step = 0
if 'placement_score' not in st.session_state: st.session_state.placement_score = 0
if 'placement_ai_responses' not in st.session_state: st.session_state.placement_ai_responses = []
if 'dynamic_scenarios' not in st.session_state: st.session_state.dynamic_scenarios = []
if 'current_diff' not in st.session_state: st.session_state.current_diff = "media"
if 'used_q_texts' not in st.session_state: st.session_state.used_q_texts = []
if 'current_q' not in st.session_state: st.session_state.current_q = None
if 'current_drill' not in st.session_state: st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS)
if 'current_connector_drill' not in st.session_state: st.session_state.current_connector_drill = random.choice(CONNECTORS_DRILLS)
if 'selected_roadmap_day' not in st.session_state: st.session_state.selected_roadmap_day = 1
if 'assistant_suggestions' not in st.session_state: st.session_state.assistant_suggestions = {}

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align:center;'>🦅 CONTROL</h1>", unsafe_allow_html=True)
    if db: st.success("☁️ Nube: ACTIVADA")
    else: st.warning("⚠️ Modo Local")
    st.divider()
    
    st.markdown("### 🧭 Navegación")
    if st.button("🏠 Home", use_container_width=True): st.session_state.screen = 'home'; st.rerun()
    if st.session_state.get("placement_completed"):
        if st.button("📊 Diagnóstico", use_container_width=True): st.session_state.screen = 'results'; st.rerun()
        if st.button("🛡️ War Room", use_container_width=True): st.session_state.screen = 'dashboard'; st.rerun()
    st.divider()
    
    if st.session_state.user_name:
        areas_str_side = ", ".join(st.session_state.user_area) if isinstance(st.session_state.user_area, list) else st.session_state.user_area
        st.write(f"**Líder:** {st.session_state.user_name}")
        st.write(f"**Rol:** {st.session_state.user_position}")
        st.write(f"**Track:** {areas_str_side}")
        st.write(f"**Nivel:** {st.session_state.english_level}")
        st.write(f"**XP:** {st.session_state.xp}")
        if st.button("🔄 Cerrar Sesión"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

# --- FUNCIONES DE ADAPTACIÓN ---
def get_adaptive_question(areas, diff):
    pool = []
    for a in (areas if isinstance(areas, list) else [areas]):
        pool.extend(DYNAMIC_MCQ.get(a, DYNAMIC_MCQ["Operaciones & Supply Chain"]).get(diff, []))
    available = [q for q in pool if q['q'] not in st.session_state.used_q_texts]
    if not available: return None
    q = copy.deepcopy(random.choice(available))
    st.session_state.used_q_texts.append(q['q'])
    correct_opt = q['options'][q['ans']]
    random.shuffle(q['options'])
    q['ans'] = q['options'].index(correct_opt)
    q['diff_label'] = diff
    return q

def generate_vocabulary_suggestions(context, areas, position):
    areas_str = ", ".join(areas) if isinstance(areas, list) else areas
    prompt = f"""Actúa como Coach Lingüístico para un {position} en {areas_str}.
    El usuario debe hablar sobre: '{context}'.
    Enséñale por inmersión. Sugiere en INGLÉS:
    1. 🔗 Conectores Lógicos Naturales (3 opciones, ej. Moreover, Consequently).
    2. 🚀 Power Verbs de alto impacto corporativo (3 opciones).
    Formato Markdown corto, sin introducciones."""
    return call_ai(prompt, API_KEY)

# --- PANTALLAS ---
if st.session_state.screen == 'home':
    st.markdown("<div class='hero-box'><h1>Global Executive Mastery</h1><p>El Simulador C-Level Definitivo | Edición 2025</p></div>", unsafe_allow_html=True)
    st.info("💡 **Instrucciones:** Selecciona tu perfil con precisión. Nuestra IA cruzará tu **Especialidad** con tu **Posición** para generar un algoritmo de evaluación personalizado. El objetivo no es solo evaluar tu gramática, sino tu instinto de supervivencia corporativa y tu mentalidad financiera.")
    
    col1, _ = st.columns([1, 1])
    with col1:
        name = st.text_input("Nombre Completo:")
        position = st.selectbox("Posición Actual / Target (Define rigor de la IA):", ["Director or Manager", "Engineer or Technician"])
        area = st.multiselect("Especialidades Tácticas (max 3):", list(DYNAMIC_MCQ.keys()), default=["Operaciones & Supply Chain"], max_selections=3)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Iniciar Protocolo 🧠"):
            if name and area:
                with st.spinner("Buscando expediente en la nube..."):
                    if load_user_progress(name):
                        st.success(f"¡Bienvenido de vuelta, {st.session_state.user_name}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.session_state.user_name = name; st.session_state.user_position = position; st.session_state.user_area = area; st.session_state.screen = 'placement_test'
                        st.rerun()
            else: st.warning("Completa todos los campos.")

elif st.session_state.screen == 'placement_test':
    total_mcq = 10 
    total_ai = 3
    total_steps = total_mcq + total_ai
    step = st.session_state.placement_step
    
    areas_str = ", ".join(st.session_state.user_area) if isinstance(st.session_state.user_area, list) else st.session_state.user_area
    st.progress(step / total_steps)
    st.subheader(f"Auditoría Táctica: Paso {step+1} de {total_steps}")
    st.info(f"💡 Perfil cruzado: **{st.session_state.user_position}** en **{areas_str}**. Lee detenidamente; las opciones están diseñadas para poner a prueba tu dominio técnico en inglés, no solo tu traducción.")

    if step < total_mcq:
        if st.session_state.current_q is None:
            st.session_state.current_q = get_adaptive_question(st.session_state.user_area, st.session_state.current_diff)
            st.rerun()
        q = st.session_state.current_q
        st.markdown(f"<span class='diff-badge diff-{q['diff_label']}'>NIVEL: {q['diff_label'].upper()}</span>", unsafe_allow_html=True)
        st.markdown(f"<div class='executive-card'><h4>{q['q']}</h4></div>", unsafe_allow_html=True)
        for i, opt in enumerate(q['options']):
            if st.button(opt, key=f"q_{step}_{i}"):
                is_correct = (i == q['ans'])
                if is_correct: st.session_state.placement_score += 10
                st.session_state.current_diff = "dificil" if is_correct else "facil"
                st.session_state.current_q = None; st.session_state.placement_step += 1; st.rerun()
    else:
        ai_step = step - total_mcq
        if not st.session_state.dynamic_scenarios:
            with st.spinner("IA generando 3 escenarios ejecutivos en tiempo real basados en tu posición..."):
                prompt = f"Write exactly 3 tough corporate scenarios asking for action, tailored for a {st.session_state.user_position} expert in {areas_str}. Format: Scenario 1 --- Scenario 2 --- Scenario 3"
                res = call_ai(prompt, API_KEY)
                st.session_state.dynamic_scenarios = res.split('---')
        st.markdown(f"<div class='executive-card'><b>Situación de Crisis (Responde con Autoridad):</b><br>{st.session_state.dynamic_scenarios[ai_step]}</div>", unsafe_allow_html=True)
        ans = st.text_area("Tu Respuesta en Inglés:")
        st_speech_to_text(key=f"voice_{ai_step}")
        if st.button("Validar Maniobra"):
            if len(ans) > 15:
                st.session_state.placement_ai_responses.append(ans); st.session_state.placement_step += 1
                if st.session_state.placement_step >= total_steps: st.session_state.screen = 'finalizing'
                st.rerun()
            else: st.warning("Desarrolla más tu respuesta. Un directivo no responde con monosílabos.")

elif st.session_state.screen == 'finalizing':
    st.markdown("<h3 style='text-align:center;'>Procesando Analíticas de Liderazgo...</h3>", unsafe_allow_html=True)
    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.02)
        my_bar.progress(percent_complete + 1)
    with st.spinner("Cruzando datos con el perfil C-Level..."):
        ai_text = "\n".join(st.session_state.placement_ai_responses)
        areas_str = ", ".join(st.session_state.user_area) if isinstance(st.session_state.user_area, list) else st.session_state.user_area
        prompt = f"""Actúa como CEO estricto evaluando a un candidato para {st.session_state.user_position} experto en {areas_str}.
        Puntaje test: {st.session_state.placement_score}. Respuestas: {ai_text}.
        Evalúa impacto y fluidez ejecutiva. DEVUELVE ESTE HTML EXACTO:
        <div class='eval-box'><h3>🏆 NIVEL ASIGNADO: [Elige: C2 - Master, C1 - Executive, B2 - Advanced, B1 - Intermediate]</h3></div>
        <div class='eval-box'><h3>📊 ANÁLISIS DE FLUIDEZ:</h3><ul><li>[Error de impacto 1]</li><li>[Falta de autoridad 2]</li></ul></div>
        <div class='eval-box'><h3>💡 TIPS PRO PARA ROL {st.session_state.user_position}:</h3><ul><li>[Tip 1]</li></ul></div>"""
        res = call_ai(prompt, API_KEY)
        st.session_state.placement_eval_detailed = res
        for level in ["C2", "C1", "B2", "B1", "A2"]:
            if level in res: st.session_state.english_level = f"{level} - Certified"; break
        if st.session_state.english_level == "No Evaluado": st.session_state.english_level = "B2 - Certified"
        st.session_state.placement_completed = True; save_user_progress(); st.session_state.screen = 'results'; st.rerun()

elif st.session_state.screen == 'results':
    st.markdown("<h1 style='text-align:center;'>Diagnóstico Final Táctico</h1>", unsafe_allow_html=True)
    st.info("💡 **Tu Reporte VP:** Este documento valida tu estado actual frente a los estándares de las mesas directivas globales. Imprímelo o guárdalo; tu objetivo es destruir estas áreas de oportunidad en los próximos 90 días.")
    st.markdown(st.session_state.placement_eval_detailed, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        components.html("""<button onclick="window.parent.print()" style="width:100%; padding: 12px; margin-bottom: 10px; background: #3b82f6; color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer;">🖨️ Guardar PDF</button>""", height=65)
        if st.button("Desbloquear Mi War Room ⚔️"): st.session_state.screen = 'dashboard'; st.rerun()

elif st.session_state.screen == 'dashboard':
    st.title(f"🛡️ War Room: {st.session_state.user_name}")
    tabs = st.tabs(["📅 Plan 90 Días", "🎧 Shadowing", "📖 Enciclopedia", "🤖 Combat Lab", "⚔️ Verbos", "🔗 Conectores", "🔥 Fragua"])
    
    with tabs[0]:
        st.subheader("Tu Calendario Táctico (Circuito Diario de 50 Min)")
        st.info("💡 **Instrucciones:** Selecciona el día actual. Sigue rigurosamente el circuito paso a paso. La clave para pasar de B1 a C1 en 3 meses es la inmersión constante y repetitiva sin enfocarse en reglas de gramática.")
        
        st.markdown(f"""
        <div style="background-color: #064e3b; padding: 15px; border-radius: 8px; border-left: 5px solid #10b981; margin-bottom: 20px;">
            <h4 style="margin-top:0; color:#ecfdf5;">📱 Vocabulario Offline de Hoy (Día {st.session_state.selected_roadmap_day})</h4>
            <p style="margin-bottom:0; color:#d1fae5; font-size:0.9em;">Anótalo en tu celular y oblígate a usarlo en tu próxima junta o correo:</p>
            <b style="color:white; font-size:1.1em;">{DAILY_VOCAB[st.session_state.selected_roadmap_day % len(DAILY_VOCAB)]}</b> | 
            <b style="color:white; font-size:1.1em;">{DAILY_VOCAB[(st.session_state.selected_roadmap_day+1) % len(DAILY_VOCAB)]}</b>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(10)
        for i in range(1, 91):
            with cols[(i-1) % 10]:
                btn_type = "primary" if st.session_state.selected_roadmap_day == i else "secondary"
                if st.button(f"D{i}", key=f"grid_{i}", type=btn_type, use_container_width=True):
                    st.session_state.selected_roadmap_day = i; st.rerun()
        
        selected_data = NINETY_DAY_PLAN[st.session_state.selected_roadmap_day]
        st.markdown(f"<div class='mission-card'><span style='color:#3b82f6; font-weight:900;'>DÍA {st.session_state.selected_roadmap_day} • {selected_data['phase']}</span><h2 style='color:white;'>{selected_data['title']}</h2><hr style='border-color:#334155;'><p><b>🎯 Actividad:</b> {selected_data['actividad']}</p>{selected_data['circuit']}</div>", unsafe_allow_html=True)
        if st.button("✅ Terminé mi Circuito de 50 Minutos (Avanzar)"):
            st.session_state.xp += 800; st.session_state.selected_roadmap_day = min(90, st.session_state.selected_roadmap_day + 1); save_user_progress(); st.success("¡Circuito Registrado!"); time.sleep(1); st.rerun()

    with tabs[1]:
        st.subheader("🎧 Entrenamiento Auditivo (Shadowing)")
        st.info("💡 **El Método:** Lee la frase, presiona el botón para escuchar la pronunciación nativa, e inmediatamente repítela en voz alta intentando copiar la entonación exacta. Esto elimina el acento y forja memoria muscular verbal.")
        
        phrases_to_shadow = [
            "Furthermore, we must deploy immediate containment actions.",
            "Consequently, the projected ROI validates this CAPEX request.",
            "By leveraging these data sets, we successfully mitigated the supply chain risk."
        ]
        
        for idx, phrase in enumerate(phrases_to_shadow):
            st.markdown(f"<div class='executive-card' style='padding:20px; margin-bottom:10px;'><h3 style='color:white; margin:0;'>\"{phrase}\"</h3></div>", unsafe_allow_html=True)
            if st.button("🔊 Escuchar y Repetir", key=f"shadow_{idx}"):
                st_text_to_speech(phrase)

    with tabs[2]:
        st.subheader("Enciclopedia C-Level")
        st.info("💡 **Instrucciones:** Busca términos técnicos. La IA te mostrará la diferencia radical entre cómo un Junior explica el concepto y cómo un VP lo articula en una junta.")
        search_term = st.text_input("🔍 Buscar término (ej. Kanban, EBITDA):", key="search_term_input")
        if st.button("Buscar en Base C-Level", type="primary"):
            if search_term:
                with st.spinner(f"Analizando '{search_term}'..."):
                    prompt_enc = f"""Actúa como diccionario corporativo para la alta dirección. Término: '{search_term}'.
                    CRITICAL INSTRUCTION: Generate the ENTIRE response strictly in ENGLISH. Do not use Spanish.
                    Devuelve HTML:
                    <div style='background-color:#0f172a; padding:25px; border-left:6px solid #f59e0b;'>
                    <h3 style='color:white; margin-top:0;'>📖 {search_term.upper()}</h3>
                    <p style='color:#cbd5e1;'><b>Definition:</b> [Clear, executive English definition]</p>
                    <hr style='border-color:#334155;'>
                    <p style='color:#f87171;'><b>🚫 Junior phrasing:</b> <i>"[Weak English phrase]"</i></p>
                    <p style='color:#34d399;'><b>✅ VP phrasing:</b> <i>"[Strong English phrase using Power Verbs and Connectors]"</i></p>
                    </div>"""
                    st.session_state.encyclopedia_result = call_ai(prompt_enc, API_KEY)
        if st.session_state.encyclopedia_result:
            st.markdown(st.session_state.encyclopedia_result, unsafe_allow_html=True)
            if st.button("Limpiar"): st.session_state.encyclopedia_result = None; st.rerun()

    with tabs[3]:
        st.subheader("AI Combat Lab")
        st.info("💡 **Instrucciones:** El CEO (IA) te hará una pregunta agresiva sobre la misión de hoy considerando tu nivel y puesto. Pide sugerencias ANTES de responder y utiliza conectores para blindar tu respuesta.")
        mission = NINETY_DAY_PLAN[st.session_state.selected_roadmap_day]
        if st.button("🎙️ Solicitar Pregunta del CEO"):
            with st.spinner("CEO conectándose..."):
                areas_str = ", ".join(st.session_state.user_area) if isinstance(st.session_state.user_area, list) else st.session_state.user_area
                st.session_state.daily_q = call_ai(f"Act as strict CEO. Ask a challenging question about '{mission['actividad']}' to a {st.session_state.user_position} in {areas_str}. Level: {st.session_state.english_level}.", API_KEY)
                st_text_to_speech(st.session_state.daily_q)
        if 'daily_q' in st.session_state:
            st.warning(st.session_state.daily_q)
            
            # Botón de ayuda visible
            with st.expander("🤖 Asistente de Inmersión (Úsalo antes de responder)"):
                st.write("Genera bloques lógicos en inglés para armar tu respuesta sin pensar en gramática:")
                if st.button("💡 Dame Conectores y Power Verbs para esta crisis"):
                    with st.spinner("Analizando contexto..."):
                        st.session_state.assistant_suggestions['combat'] = generate_vocabulary_suggestions(st.session_state.daily_q, st.session_state.user_area, st.session_state.user_position)
                if st.session_state.assistant_suggestions.get('combat'):
                    st.markdown(f"<div class='eval-box'>{st.session_state.assistant_suggestions['combat']}</div>", unsafe_allow_html=True)

            ans = st.text_area("Ejecuta tu respuesta:")
            st_speech_to_text(key="combat_voice")
            if st.button("Auditar Impacto"):
                with st.spinner("Auditando..."):
                    res = call_ai(f"Evaluate: {ans}. SPANISH. 1. SCORE 2. FEEDBACK (Uso de conectores) 3. VERSIÓN BOARDROOM.", API_KEY)
                    st.markdown(f"<div class='level-box'>{res}</div>", unsafe_allow_html=True); st.session_state.xp += 100; save_user_progress()

    with tabs[4]:
        st.subheader("Combate de Reflejos: Power Verbs")
        st.info("💡 **Instrucciones:** Erradica tu vocabulario básico. Sustituye la frase del Junior por el 'Power Verb' que un directivo utilizaría.")
        drill = st.session_state.current_drill
        st.markdown(f"<div class='executive-card'>Un Junior diría: <b>'{drill[0]}'</b></div>", unsafe_allow_html=True)
        pv_ans = st.text_input("Sustituye por el verbo VP:")
        if st.button("Validar Impacto 🎯"):
            if drill[1].lower() in pv_ans.lower() or any(w in pv_ans.lower() for w in drill[1].split() if len(w)>4):
                st.success(f"¡Destruido! Versión oficial: '{drill[1]}'"); time.sleep(1.5); st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS); st.rerun()
            else: st.error(f"Demasiado pasivo. Tip: Usa palabras de: '{drill[1]}'")

    with tabs[5]:
        st.subheader("Simulador de Conectores")
        st.info("💡 **Instrucciones:** No traduzcas; conecta. Une las dos oraciones utilizando un conector lógico avanzado (Consequently, Therefore, Furthermore).")
        c_drill = st.session_state.current_connector_drill
        st.markdown(f"<div class='executive-card' style='border-color:#34d399;'><span>Tipo: {c_drill['type']}</span><h3 style='color:white;'>\"{c_drill['junior']}\"</h3></div>", unsafe_allow_html=True)
        conn_ans = st.text_area("Reescribe uniendo fluidamente:")
        if st.button("Evaluar Fluidez 🔗"):
            if any(t.lower() in conn_ans.lower() for t in c_drill['target']):
                st.success("¡Flujo Perfecto!"); time.sleep(1.5); st.session_state.current_connector_drill = random.choice(CONNECTORS_DRILLS); st.rerun()
            else: st.error(f"Usa un conector como: {c_drill['target'][0]} o {c_drill['target'][1]}.")

    with tabs[6]:
        st.subheader("La Fragua: Forja de Logros")
        st.info("💡 **Instrucciones:** Ingresa un logro de piso o técnico. La IA lo transformará en una declaración de impacto orientada a ahorros y rentabilidad corporativa.")
        draft = st.text_area("Ingresa un logro básico (ej: Reparamos la máquina y ganamos tiempo):")
        if st.button("⚒️ Forjar a Nivel VP"):
            with st.spinner("Forjando..."):
                res = call_ai(f"Transform to STAR executive achievement in English focused on EBITDA using natural logical connectors. Pro Tip in Spanish: {draft}", API_KEY)
                st.markdown(f"<div class='executive-card'>{res}</div>", unsafe_allow_html=True)

st.divider()
st.caption("Protocolo diseñado por Ing. Fernando Montes Delgado | Adquisición Natural C-Level | Edición 2025")
