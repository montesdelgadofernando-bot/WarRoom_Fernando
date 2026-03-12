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
            loaded_area = u.get("user_area", ["Operaciones & Supply Chain"])
            st.session_state.user_area = loaded_area if isinstance(loaded_area, list) else [loaded_area]
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

# --- PSICOLOGÍA DE COLOR Y DISEÑO (CSS + MODO IMPRESIÓN PDF) ---
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
    .mission-card {
        background-color: #0f172a; padding: 25px; border-radius: 15px; border: 1px solid #334155; margin-top: 20px;
    }
    .level-box {
        background-color: #064e3b; padding: 30px; border-radius: 15px; border-left: 6px solid #10b981; color: #ecfdf5; text-align: left;
    }
    .eval-box {
        background-color: #1e293b; padding: 25px; border-radius: 12px; border-left: 5px solid #f59e0b; margin-bottom: 15px;
    }
    .circuit-box {
        background-color: #1e293b; border: 1px solid #3b82f6; padding: 20px; border-radius: 10px; margin-top: 15px;
    }
    .diff-badge { padding: 4px 10px; border-radius: 5px; font-size: 0.8em; font-weight: bold; }
    .diff-facil { background-color: #064e3b; color: #34d399; }
    .diff-media { background-color: #78350f; color: #fbbf24; }
    .diff-dificil { background-color: #7f1d1d; color: #f87171; }
    
    @media print {
        header, [data-testid="stSidebar"], .stButton { display: none !important; }
        .stApp { background-color: white !important; color: black !important; }
        .eval-box { 
            background-color: white !important; 
            color: black !important; 
            border: 1px solid #cbd5e1 !important; 
            border-left: 6px solid #3b82f6 !important; 
            page-break-inside: avoid; 
            box-shadow: none !important;
        }
        h1, h2, h3, h4, p, li, span, b, i { color: black !important; }
        iframe { display: none !important; }
        body { font-family: 'Helvetica', 'Arial', sans-serif !important; }
    }
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
for area in ["Ingeniería de Producto", "Data Science & SQL", "Logística", "Producción", "Otra"]:
    if area not in DYNAMIC_MCQ:
        DYNAMIC_MCQ[area] = copy.deepcopy(DYNAMIC_MCQ["Operaciones & Supply Chain"])

# --- DATA DRILLS (VERBOS Y CONECTORES) ---
POWER_VERBS_DRILLS = [
    ("I fixed the problem", "I rectified the non-conformance"),
    ("I saved money", "I delivered substantial hard savings"),
    ("I used data", "I leveraged data analytics to drive decision-making"),
    ("I started a project", "I spearheaded a strategic initiative"),
    ("I talked to the client", "I orchestrated cross-functional negotiations"),
    ("I lowered the cost", "I optimized the OPEX parameters"),
    ("I found the error", "I identified the root cause constraint")
]

CONNECTORS_DRILLS = [
    {"junior": "The supplier was late. We missed the deadline.", "type": "Causa y Efecto", "target": ["consequently", "as a result", "therefore", "thus"]},
    {"junior": "The budget was cut. We delivered the project on time.", "type": "Contraste", "target": ["nevertheless", "however", "despite this", "yet"]},
    {"junior": "We increased production. We maintained zero defects.", "type": "Adición", "target": ["furthermore", "moreover", "in addition", "additionally"]},
    {"junior": "We need to reduce costs. We will automate the line.", "type": "Propósito", "target": ["in order to", "so as to", "to effectively"]},
    {"junior": "The system failed. The power went out.", "type": "Causa", "target": ["due to", "because of", "stemming from"]}
]

# --- GENERADOR DE PLAN 30 DÍAS (SISTEMA DE CIRCUITO 30 MIN) ---
def generate_30_day_plan():
    plan = {}
    phases = ["Fundamentos (Día 1-5)", "Dominio Técnico (Día 6-15)", "Gestión de Crisis (Día 16-22)", "Liderazgo (Día 23-28)", "Boardroom (Día 29-30)"]
    templates = [
        ("El Pitch de Impacto", "Crear una presentación personal enfocada en EBITDA.", "Audio grabado de tu pitch sin dudar."),
        ("Contención 8D", "Redactar un correo de respuesta a un problema de calidad.", "Email de 5 líneas con acciones de contención."),
        ("Métricas de OEE", "Explicar el OEE de tu línea a un directivo.", "Párrafo explicando disponibilidad, rendimiento y calidad."),
        ("El Stakeholder Difícil", "Rebatir a alguien que quiere cambiar el alcance.", "Guión de respuesta educada pero firme."),
        ("Negociación de Proveedor", "Exigir a un proveedor que reduzca su Lead Time.", "Script de llamada (3 minutos)."),
        ("Data Storytelling", "Explicar cómo sacaste datos de un SQL o Dashboard.", "Explicación de 1 minuto frente al espejo."),
        ("Defensa de CAPEX", "Justificar la compra de una máquina de $100k USD.", "One-pager (1 hoja) con ROI y Payback.")
    ]
    for day in range(1, 31):
        phase_idx = min((day - 1) // 6, 4) 
        temp = templates[day % len(templates)]
        if day == 1: temp = ("El Pitch de Impacto (EBITDA)", "Redactar tu valor financiero.", "Audio grabado del pitch.")
        if day == 15: temp = ("Auditoría Global", "Simular respuesta a un auditor VDA 6.3/IATF.", "Reporte 8D resumido en inglés.")
        if day == 30: temp = ("La Prueba de Fuego (CEO)", "Responder cómo reducirás OPEX sin afectar calidad.", "Video de 3 minutos sin cortes.")

        # Ahora el Plan es un circuito completo de 30 minutos
        circuit_html = f"""
        <div class="circuit-box">
            <h4 style="margin-top:0; color:#3b82f6;">⏳ Tu Circuito de Entrenamiento de Hoy (30 Minutos)</h4>
            <p style="font-size:0.9em; color:#cbd5e1; margin-bottom:15px;">Para generar fluidez real, debes completar estas 4 estaciones. Evita la gramática, enfócate en el impacto.</p>
            <ul style="list-style-type: none; padding: 0;">
                <li style="margin-bottom:10px;"><b>1️⃣ AI Combat Lab (10 min):</b> Solicita una pregunta al CEO sobre <i>{temp[0]}</i> y graba tu respuesta.</li>
                <li style="margin-bottom:10px;"><b>2️⃣ Power Verbs (5 min):</b> Ve a la pestaña y destruye al menos 3 frases de nivel Junior.</li>
                <li style="margin-bottom:10px;"><b>3️⃣ Conectores Lógicos (10 min):</b> Une 4 oraciones fracturadas para ganar fluidez ejecutiva.</li>
                <li style="margin-bottom:0;"><b>4️⃣ La Fragua (5 min):</b> Redacta tu <i>{temp[2]}</i> y fórjalo a nivel Vicepresidente.</li>
            </ul>
        </div>
        """
        
        plan[day] = {
            "phase": phases[phase_idx], "title": temp[0], "actividad": temp[1], "entregable": temp[2], "circuit": circuit_html
        }
    return plan

THIRTY_DAY_PLAN = generate_30_day_plan()

# --- ENCICLOPEDIA TÉCNICA INTERACTIVA ---
ENCYCLOPEDIA = {
    "Operaciones & Supply Chain": {
        "EBITDA": {"desc": "Beneficio antes de intereses, impuestos, depreciación y amortización.", "uso": "Furthermore, this strategic initiative protected our EBITDA margins by 12%."},
        "S&OP": {"desc": "Sales and Operations Planning. Alineación mensual de demanda y capacidad.", "uso": "Consequently, we re-baselined the S&OP to mitigate forecast variance."},
        "Throughput": {"desc": "Tasa real de producción o flujo de trabajo del sistema.", "uso": "We maximized throughput; moreover, we maintained rigorous zero-defect standards."}
    },
    "Calidad & Lean Manufacturing": {
        "RCA (Root Cause Analysis)": {"desc": "Metodología para identificar el origen sistemático de un problema.", "uso": "I spearheaded a data-driven RCA to subsequently deploy countermeasures."},
        "Cpk (Process Capability)": {"desc": "Índice que mide qué tan centrado y estable está un proceso.", "uso": "We stabilized the parameters, effectively raising the Cpk from 0.8 to 1.67."},
        "Containment": {"desc": "Acción inmediata para proteger al cliente de un defecto.", "uso": "Due to the defect, immediate containment actions were deployed to quarantine lots."}
    },
    "Project Management & Data": {
        "Scope Creep": {"desc": "Aumento descontrolado del alcance original de un proyecto.", "uso": "To prevent scope creep, we implemented a strict change-control board."},
        "Agile / Scrum": {"desc": "Metodología iterativa para entrega rápida de valor.", "uso": "We transitioned to Agile, significantly improving cross-functional collaboration."},
        "ROI (Return on Investment)": {"desc": "Retorno de inversión de un proyecto o maquinaria.", "uso": "Consequently, the projected ROI for this CAPEX request is under 14 months."}
    }
}

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
if 'user_area' not in st.session_state: st.session_state.user_area = ["Operaciones & Supply Chain"] 
if 'english_level' not in st.session_state: st.session_state.english_level = "No Evaluado"
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'current_day' not in st.session_state: st.session_state.current_day = 1
if 'placement_step' not in st.session_state: st.session_state.placement_step = 0
if 'placement_score' not in st.session_state: st.session_state.placement_score = 0
if 'placement_ai_responses' not in st.session_state: st.session_state.placement_ai_responses = []
if 'dynamic_scenarios' not in st.session_state: st.session_state.dynamic_scenarios = []

# Variables para algoritmo adaptativo y UI Interactivas
if 'current_diff' not in st.session_state: st.session_state.current_diff = "media"
if 'used_q_texts' not in st.session_state: st.session_state.used_q_texts = []
if 'current_q' not in st.session_state: st.session_state.current_q = None
if 'current_drill' not in st.session_state: st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS)
if 'current_connector_drill' not in st.session_state: st.session_state.current_connector_drill = random.choice(CONNECTORS_DRILLS)
if 'selected_roadmap_day' not in st.session_state: st.session_state.selected_roadmap_day = 1
if 'assistant_suggestions' not in st.session_state: st.session_state.assistant_suggestions = {}
if 'encyclopedia_result' not in st.session_state: st.session_state.encyclopedia_result = None

# --- PANEL LATERAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 2em;'>🦅 CONTROL</h1>", unsafe_allow_html=True)
    if db: st.success("☁️ Guardado en la Nube: ACTIVADO")
    else: st.warning("⚠️ Sin conexión a la base de datos (Modo Local)")
    st.divider()
    
    st.markdown("### 🧭 Navegación Rápida")
    if st.button("🏠 Home (Inicio)", use_container_width=True):
        st.session_state.screen = 'home'
        st.rerun()
        
    if st.session_state.get("placement_completed"):
        if st.button("📊 Último Diagnóstico", use_container_width=True):
            st.session_state.screen = 'results'
            st.rerun()
        if st.button("🛡️ Mi War Room", use_container_width=True):
            st.session_state.screen = 'dashboard'
            st.rerun()
    st.divider()

    if st.session_state.user_name:
        areas_str_sidebar = ", ".join(st.session_state.user_area) if isinstance(st.session_state.user_area, list) else st.session_state.user_area
        st.write(f"**Líder:** {st.session_state.user_name}")
        st.write(f"**Especialidad:** {areas_str_sidebar}")
        st.write(f"**Nivel:** {st.session_state.english_level}")
        st.write(f"**XP:** {st.session_state.xp}")
    if st.button("🔄 Reset / Cerrar Sesión"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# --- FUNCIONES ADAPTATIVAS E INMERSIÓN NATURAL ---
def get_adaptive_question(areas, diff):
    areas_list = areas if isinstance(areas, list) else [areas]
    pool = []
    for a in areas_list:
        pool.extend(DYNAMIC_MCQ.get(a, DYNAMIC_MCQ["Operaciones & Supply Chain"]).get(diff, []))
        
    available = [q for q in pool if q['q'] not in st.session_state.used_q_texts]
    if not available:
        for fallback in ["media", "facil", "dificil"]:
            pool_fallback = []
            for a in areas_list:
                pool_fallback.extend(DYNAMIC_MCQ.get(a, DYNAMIC_MCQ["Operaciones & Supply Chain"]).get(fallback, []))
            available = [q for q in pool_fallback if q['q'] not in st.session_state.used_q_texts]
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
    if is_correct: return "dificil" if current_diff == "media" else ("media" if current_diff == "facil" else "dificil")
    else: return "facil" if current_diff == "media" else ("media" if current_diff == "dificil" else "facil")

def generate_vocabulary_suggestions(context, areas):
    areas_str = ", ".join(areas) if isinstance(areas, list) else areas
    prompt = f"""Actúa como un Asistente de Adquisición Natural de Idioma para un líder en {areas_str}.
    El usuario necesita escribir o hablar sobre: '{context}'.
    Ignora las reglas gramaticales complejas. Enséñale por inmersión (como aprenden los niños), dándole los bloques de construcción exactos para sonar natural y con autoridad.
    Sugiere vocabulario en inglés dividido en 2 listas muy cortas y directas:
    1. 🔗 Conectores Lógicos Naturales (3 sugerencias de conectores para unir ideas fluidamente, ej. Moreover, As a result, Consequently).
    2. 🚀 Power Verbs / Nivel VP (3 verbos o frases de alto impacto corporativo para evitar palabras básicas).
    Formato Markdown, usando viñetas. Sin introducciones largas, ve directo al grano."""
    return call_ai(prompt, API_KEY)

# --- ENRUTADOR PRINCIPAL ---
if st.session_state.screen == 'home':
    st.markdown("<div class='hero-box'><h1>Executive Mastery Protocol</h1><p>Algoritmo Adaptativo (GMAT Style) Activado.</p></div>", unsafe_allow_html=True)
    col1, _ = st.columns([1, 1])
    with col1:
        name_input = st.text_input("Ingresa tu Nombre Completo:")
        area_input = st.multiselect("Selecciona tus Especialidades Tácticas (máximo 3):", list(DYNAMIC_MCQ.keys()), default=["Operaciones & Supply Chain"], max_selections=3)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Acceder al Sistema 🧠"):
            if name_input and len(area_input) > 0:
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
            elif not name_input:
                st.warning("Por favor, ingresa tu nombre.")
            elif len(area_input) == 0:
                st.warning("Por favor, selecciona al menos una especialidad.")

elif st.session_state.screen == 'placement_test':
    total_mcq = 9 
    total_ai = 3  
    total_steps = total_mcq + total_ai
    current_step = st.session_state.placement_step
    
    areas_str = ", ".join(st.session_state.user_area) if isinstance(st.session_state.user_area, list) else st.session_state.user_area
    
    st.progress(current_step / total_steps)
    st.subheader(f"Etapa {current_step+1} de {total_steps} ({areas_str})")

    if current_step < total_mcq:
        if st.session_state.current_q is None:
            st.session_state.current_q = get_adaptive_question(st.session_state.user_area, st.session_state.current_diff)
            st.rerun() 
            
        q = st.session_state.current_q
        diff_color = f"diff-{q['diff_label']}"
        diff_text = q['diff_label'].upper()
        st.markdown(f"<span class='diff-badge {diff_color}'>NIVEL: {diff_text}</span>", unsafe_allow_html=True)
        
        st.markdown(f"<div class='executive-card'><h4>{q['q']}</h4></div>", unsafe_allow_html=True)
        for i, opt in enumerate(q['options']):
            if st.button(opt, key=f"btn_{current_step}_{i}"):
                is_correct = (i == q['ans'])
                if is_correct:
                    pts = 15 if q['diff_label'] == 'dificil' else (10 if q['diff_label'] == 'media' else 5)
                    st.session_state.placement_score += pts
                st.session_state.current_diff = adjust_difficulty(is_correct, q['diff_label'])
                st.session_state.current_q = None 
                st.session_state.placement_step += 1
                st.rerun()
    else:
        ai_step = current_step - total_mcq
        if not st.session_state.dynamic_scenarios:
            with st.spinner("IA generando 3 escenarios ejecutivos en tiempo real..."):
                prompt = f"Write exactly 3 tough corporate scenarios asking for action, tailored for a {areas_str} leader. Format: Scenario 1 --- Scenario 2 --- Scenario 3"
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
        areas_str = ", ".join(st.session_state.user_area) if isinstance(st.session_state.user_area, list) else st.session_state.user_area
        
        prompt = f"""
        Actúa como un CEO estricto evaluando a un gerente experto en {areas_str}.
        El candidato obtuvo {st.session_state.placement_score} puntos en la prueba adaptativa.
        Sus respuestas orales ante crisis fueron: {ai_text}.
        
        Evalúa su impacto, uso de conectores lógicos y nivel de autoridad (ignora la gramática básica).
        DEVUELVE TU RESPUESTA ESTRICTAMENTE EN ESTE FORMATO MARKDOWN EXACTO:

        <div class='eval-box'>
        <h3>🏆 NIVEL ASIGNADO: [Elige uno: C2 - Master, C1 - Executive, B2 - Advanced, B1 - Intermediate]</h3>
        </div>
        
        <div class='eval-box'>
        <h3>📊 ANÁLISIS DE FLUIDEZ Y AUTORIDAD:</h3>
        <ul><li>[Falta de impacto o conectores que cometió 1]</li><li>[Falta de autoridad en su vocabulario 2]</li></ul>
        </div>

        <div class='eval-box'>
        <h3>⚠️ ÁREAS DE OPORTUNIDAD:</h3>
        <ul><li>[Qué conectores lógicos o jerga debe integrar para sonar natural]</li></ul>
        </div>

        <div class='eval-box'>
        <h3>💡 TIPS PRO PARA NIVEL VP:</h3>
        <ul><li>[Tip 1 sobre inmersión corporativa]</li><li>[Tip 2 sobre estructurar ideas]</li></ul>
        </div>
        """
        res = call_ai(prompt, API_KEY)
        st.session_state.placement_eval_detailed = res
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
    areas_str = ", ".join(st.session_state.user_area) if isinstance(st.session_state.user_area, list) else st.session_state.user_area
    st.markdown(f"<p style='text-align:center; font-size:1.2em;'>Candidato: <b>{st.session_state.user_name}</b> | Especialidad: <b>{areas_str}</b></p>", unsafe_allow_html=True)
    st.markdown(st.session_state.placement_eval_detailed, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        components.html("""
            <button onclick="window.parent.print()" style="width:100%; padding: 12px; margin-bottom: 10px; background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%); color: white; border: none; border-radius: 12px; font-weight: bold; font-size: 1.1em; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                🖨️ Guardar Reporte como PDF
            </button>
        """, height=65)

        if st.button("Desbloquear Mi War Room ⚔️"):
            st.session_state.screen = 'dashboard'
            st.rerun()

# --- WAR ROOM ---
elif st.session_state.screen == 'dashboard':
    st.title(f"🛡️ War Room: {st.session_state.user_name}")
    # ¡Agregamos la pestaña 6: Conectores Lógicos!
    tabs = st.tabs(["📅 Roadmap (30 Min)", "📖 Enciclopedia", "🤖 AI Combat Lab", "⚔️ Power Verbs", "🔗 Conectores", "🔥 The Forge"])
    
    # 1. ROADMAP INTERACTIVO (AHORA CON CIRCUITO DE 30 MIN)
    with tabs[0]:
        st.subheader("Tu Calendario Táctico (Circuito Diario)")
        st.write("Selecciona el día actual. Tu objetivo es completar el circuito de 30 minutos rotando por las pestañas.")
        
        cols = st.columns(6)
        for i in range(1, 31):
            col_idx = (i - 1) % 6
            with cols[col_idx]:
                btn_type = "primary" if st.session_state.selected_roadmap_day == i else "secondary"
                if st.button(f"Día {i}", key=f"grid_day_{i}", type=btn_type, use_container_width=True):
                    st.session_state.selected_roadmap_day = i
                    st.rerun()
        
        selected_data = THIRTY_DAY_PLAN[st.session_state.selected_roadmap_day]
        st.markdown(f"""
            <div class="mission-card">
                <span style="color: #3b82f6; font-weight: 900; font-size: 1.2em;">DÍA {st.session_state.selected_roadmap_day} • {selected_data['phase']}</span>
                <h2 style="color: white; margin-top: 5px;">{selected_data['title']}</h2>
                <hr style="border-color: #334155;">
                <p><b>🎯 Actividad del Día:</b> {selected_data['actividad']}</p>
                <p><b>📦 Entregable Final:</b> <span style="color: #10b981;">{selected_data['entregable']}</span></p>
                
                {selected_data['circuit']}
            </div>
        """, unsafe_allow_html=True)
        
        sug_key_1 = f"rm_{st.session_state.selected_roadmap_day}"
        with st.expander("🤖 Asistente Estratégico (Conectores y Power Verbs)"):
            if st.button("💡 Sugerir bloques de construcción para tu circuito", key="btn_a_1"):
                with st.spinner("Analizando por inmersión..."):
                    st.session_state.assistant_suggestions[sug_key_1] = generate_vocabulary_suggestions(selected_data['actividad'], st.session_state.user_area)
            if st.session_state.assistant_suggestions.get(sug_key_1):
                st.markdown(f"<div class='eval-box' style='padding:15px; font-size:0.9em; margin-top:10px;'>{st.session_state.assistant_suggestions[sug_key_1]}</div>", unsafe_allow_html=True)

        if st.button("✅ Terminé mi Circuito de 30 Minutos (Avanzar de Día)"):
            st.session_state.xp += 500
            st.session_state.current_day = min(30, st.session_state.selected_roadmap_day + 1)
            st.session_state.selected_roadmap_day = st.session_state.current_day
            save_user_progress()
            st.success("¡Circuito completado con éxito! Fluidez adquirida y guardada en la nube.")
            time.sleep(1.5)
            st.rerun()

    # 2. ENCICLOPEDIA VP INTERACTIVA
    with tabs[1]:
        st.subheader("Enciclopedia de Jerga Corporativa (Buscador AI)")
        search_term = st.text_input("🔍 Buscar término (ej. Bottleneck, Kanban):", key="search_term_input")
        if st.button("Buscar en la Base de Datos C-Level", type="primary"):
            if search_term:
                with st.spinner(f"Analizando '{search_term}'..."):
                    prompt_enc = f"""Actúa como diccionario corporativo. Término: '{search_term}'.
                    Devuelve HTML:
                    <div style='background-color:#0f172a; padding:25px; border-radius:15px; border-left:6px solid #f59e0b;'>
                    <h3 style='color:white; margin-top:0;'>📖 {search_term.upper()}</h3>
                    <p style='color:#cbd5e1;'><b>Definición:</b> [Definición clara en español]</p>
                    <hr style='border-color:#334155;'>
                    <p style='color:#f87171;'><b>🚫 Un Junior diría:</b> <i>"[Frase sin conectores]"</i></p>
                    <p style='color:#34d399;'><b>✅ Un VP diría:</b> <i>"[Frase usando un conector lógico y Power Verb]"</i></p>
                    </div>"""
                    st.session_state.encyclopedia_result = call_ai(prompt_enc, API_KEY)
        if st.session_state.encyclopedia_result:
            st.markdown(st.session_state.encyclopedia_result, unsafe_allow_html=True)
            if st.button("Limpiar Búsqueda"):
                st.session_state.encyclopedia_result = None
                st.rerun()

        st.markdown("<br>### 📚 Términos Sugeridos", unsafe_allow_html=True)
        category = st.selectbox("Explorar:", list(ENCYCLOPEDIA.keys()))
        for term, data in ENCYCLOPEDIA[category].items():
            with st.expander(f"📌 {term}"):
                st.markdown(f"**Definición:** {data['desc']}")
                st.markdown(f"<div style='background-color:#1e293b; padding:10px; border-left:4px solid #f59e0b;'><b>Cómo lo hila un VP:</b><br> <i>\"{data['uso']}\"</i></div>", unsafe_allow_html=True)

    # 3. AI COMBAT LAB
    with tabs[2]:
        mission = THIRTY_DAY_PLAN[st.session_state.selected_roadmap_day]
        st.subheader(f"Combat Lab: {mission['title']}")
        st.write("Completa 1 escenario oral/escrito como parte de tu circuito.")
        if st.button("🎙️ Entrevistarme sobre este tema"):
            with st.spinner("Llamando al CEO..."):
                areas_str = ", ".join(st.session_state.user_area) if isinstance(st.session_state.user_area, list) else st.session_state.user_area
                st.session_state.daily_q = call_ai(f"Act as a strict CEO. Ask a challenging question about '{mission['actividad']}' to an expert in {areas_str}. English Level: {st.session_state.english_level}.", API_KEY)
                st_text_to_speech(st.session_state.daily_q)
        
        if 'daily_q' in st.session_state:
            st.info(st.session_state.daily_q)
            ans = st.text_area("Tu Respuesta Ejecutiva (Únelo con conectores):")
            st_speech_to_text(key="combat_voice")
            if st.button("Auditar Respuesta"):
                with st.spinner("Auditando fluidez..."):
                    prompt = f"""Evaluate: {ans}. Provide in SPANISH: 1. SCORE (0-100) 2. FEEDBACK (Enfocado en uso de conectores e impacto) 3. TIP PRO 4. VERSIÓN BOARDROOM."""
                    res = call_ai(prompt, API_KEY)
                    st.markdown(f"<div class='level-box' style='background-color: #1e293b; border-left-color: #f59e0b;'>{res}</div>", unsafe_allow_html=True)
                    st.session_state.xp += 100
                    save_user_progress()

    # 4. POWER VERBS
    with tabs[3]:
        st.subheader("Combate de Reflejos: Power Verbs")
        st.write("Supera 3 a 4 frases para completar esta parte de tu circuito diario.")
        drill = st.session_state.current_drill
        st.markdown(f"<div class='executive-card' style='border-color:#f59e0b;'>Un Junior diría: <b>'{drill[0]}'</b></div>", unsafe_allow_html=True)
        
        pv_ans = st.text_input("Sustituye por el verbo de la versión ejecutiva:")
        if st.button("Validar Impacto 🎯"):
            if drill[1].lower() in pv_ans.lower() or any(word in pv_ans.lower() for word in drill[1].split() if len(word)>4):
                st.success(f"¡Excelente! La frase completa es: '{drill[1]}'")
                st.session_state.xp += 50
                time.sleep(2)
                st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS)
                save_user_progress()
                st.rerun()
            else:
                st.error(f"Sigue siendo básico. Necesitas usar palabras de: '{drill[1]}'")

    # 5. NUEVA PESTAÑA: CONECTORES LÓGICOS
    with tabs[4]:
        st.subheader("🔗 Simulador de Conectores Lógicos")
        st.write("Une estas dos oraciones cortas en una sola frase ejecutiva fluida. (Haz 3 o 4 por circuito)")
        
        c_drill = st.session_state.current_connector_drill
        st.markdown(f"""
        <div class='executive-card' style='border-color:#34d399;'>
            <span style='color:#34d399; font-weight:bold; font-size:0.8em; text-transform:uppercase;'>Tipo de Relación: {c_drill['type']}</span>
            <h3 style='margin-top:5px; color:white;'>"{c_drill['junior']}"</h3>
        </div>
        """, unsafe_allow_html=True)
        
        sug_key_c = f"conn_{c_drill['type']}"
        with st.expander("🤖 Asistente (Sugerir Conectores)"):
            if st.button("💡 Dime qué conectores de " + c_drill['type'] + " puedo usar"):
                st.info(f"Opciones ejecutivas válidas: **{', '.join(c_drill['target'])}**")
        
        conn_ans = st.text_area("Reescribe uniendo las ideas (Ej: The system failed; consequently, the power went out):")
        
        if st.button("Evaluar Fluidez 🔗"):
            # Validación simple comprobando si usó alguna de las palabras objetivo
            if any(target.lower() in conn_ans.lower() for target in c_drill['target']):
                st.success("¡Perfecto! Has logrado fluidez nivel VP al conectar estas ideas.")
                st.session_state.xp += 50
                time.sleep(2)
                st.session_state.current_connector_drill = random.choice(CONNECTORS_DRILLS)
                save_user_progress()
                st.rerun()
            else:
                st.error(f"Te faltó el conector correcto. Intenta usar palabras como: {c_drill['target'][0]} o {c_drill['target'][1]}.")

    # 6. THE FORGE
    with tabs[5]:
        st.subheader("La Fragua: Forja de Logros")
        st.write("Transforma 1 logro básico al final de tu circuito diario.")
        draft = st.text_area("Ingresa un logro básico (ej: Reduje el tiempo de entrega 10%):")
        if st.button("⚒️ Forjar Logro VP"):
            with st.spinner("Forjando texto corporativo fluido..."):
                res = call_ai(f"Transform to STAR executive achievement in English focused on EBITDA using natural logical connectors (Furthermore, As a result) with a Pro Tip in Spanish: {draft}", API_KEY)
                st.markdown(f"<div class='executive-card'>{res}</div>", unsafe_allow_html=True)
                save_user_progress()

st.divider()
st.caption("Protocolo diseñado por Ing. Fernando Montes Delgado | Adquisición Natural & Algoritmo Adaptativo | Gemini 3 Flash Preview")
