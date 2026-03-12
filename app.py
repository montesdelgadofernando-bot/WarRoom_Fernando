import streamlit as st
import requests
import time
import random
import streamlit.components.v1 as components

# --- IMPORTACIÓN SEGURA DE FIRESTORE ---
try:
    from google.cloud import firestore
except ImportError:
    firestore = None

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
    try:
        if firestore:
            return firestore.Client()
        return None
    except Exception:
        return None

db = get_db()

def save_user_progress():
    """Guarda el estado actual del usuario en la base de datos de la nube."""
    if not db or not st.session_state.get("user_name"):
        return
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
    except:
        pass # Si falla el guardado, ignoramos para no romper la app

def load_user_progress(name):
    """Busca en la nube si el usuario ya tiene un historial guardado."""
    if not db:
        return False
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
            return True
    except:
        pass
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
    <div style="text-align: center;"><button onclick="startDictation()" style="background: #f59e0b; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor:pointer;">🎙️ Click to Speak (English)</button></div>
    """
    return components.html(script, height=80)

def st_text_to_speech(text):
    if text:
        clean = text.replace('"', '\\"').replace('\n', ' ')
        components.html(f"<script>const m=new SpeechSynthesisUtterance('{clean}');m.lang='en-US';m.rate=0.95;window.speechSynthesis.speak(m);</script>", height=0)

# --- BÓVEDA DE API ---
try: 
    API_KEY = st.secrets["GEMINI_API_KEY"]
except: 
    API_KEY = ""

# --- BANCOS DE PREGUNTAS (100% COMPLETOS Y RESTAURADOS PARA 12 ETAPAS MCQ) ---
DYNAMIC_MCQ = {
    "Operaciones & Supply Chain": [
        {"q": "What is 'Lead Time'?", "options": ["Production speed", "Total time from order to delivery", "Machine uptime", "The boss's schedule"], "ans": 1},
        {"q": "Which term describes a delay impact on throughput?", "options": ["Bottleneck", "Buffer", "Backlog", "Lead-time disruption"], "ans": 3},
        {"q": "What is the primary goal of S&OP?", "options": ["To hire people", "To align demand and supply plans", "To count inventory", "To fix machines"], "ans": 1},
        {"q": "Inventory Record Accuracy (IRA) is crucial for:", "options": ["EBITDA protection", "MRP reliability", "Safety stock reduction", "All of the above"], "ans": 3},
        {"q": "A 'Stockout' occurs when:", "options": ["Inventory is exhausted", "Sales are too high", "Warehouse is full", "Prices go up"], "ans": 0},
        {"q": "EBITDA improves when:", "options": ["OPEX increases", "Revenue grows and costs are optimized", "Margins shrink", "Production slows down"], "ans": 1},
        {"q": "A critical tier-1 supplier announces a 25% increase in lead time. How do you report the impact to the board?", "options": ["Wait for the material and report later.", "Report a lead-time disruption and its projected impact on throughput and OEE.", "Ask the supplier to work overtime.", "Increase safety stock without analyzing financial carrying costs."], "ans": 1},
        {"q": "EBITDA is shrinking due to rising multi-modal freight costs. What is your move?", "options": ["Reduce the logistics headcount immediately.", "Orchestrate a multi-modal strategy focused on IRA and cost optimization.", "Increase prices without market analysis.", "Stop all shipments until rates drop."], "ans": 1},
        {"q": "In an S&OP meeting, there is a major gap between demand and capacity. You should:", "options": ["Ignore it and produce at max capacity.", "Align demand and supply plans by prioritizing high-margin SKUs.", "Tell sales to stop taking orders.", "Wait for next month's forecast."], "ans": 1},
        {"q": "Your inventory carrying cost is 30%. What is the executive solution?", "options": ["Dispose of old inventory immediately.", "Implement a pull system backed by predictive modeling to reduce buffers.", "Rent a cheaper warehouse.", "Stop procurement for a month."], "ans": 1},
        {"q": "Which phrase demonstrates highest authority in a P&L update?", "options": ["I helped reduce costs last quarter.", "I spearheaded a strategic initiative delivering $274k in hard savings.", "I was responsible for the cost cutting plan.", "The team reduced costs under my supervision."], "ans": 1},
        {"q": "A bottleneck is impacting 15% of your throughput. Your first step is:", "options": ["Hire more operators.", "Perform a Takt-time analysis to balance the flow and maximize OEE.", "Increase machine speed.", "Report a technical breakdown."], "ans": 1}
    ],
    "Calidad & Lean Manufacturing": [
        {"q": "What does a high Cpk indicate?", "options": ["Process instability", "Process capability and Spec compliance", "High cost", "Slow production"], "ans": 1},
        {"q": "An '8D Report' is used for:", "options": ["Counting parts", "Systemic problem solving", "Design", "Marketing"], "ans": 1},
        {"q": "The primary focus of IATF 16949 is:", "options": ["Employee benefits", "Customer satisfaction and defect prevention", "Selling cars", "Robot maintenance"], "ans": 1},
        {"q": "What is a 'Non-conformance'?", "options": ["A late employee", "A product that fails spec", "A new idea", "A meeting"], "ans": 1},
        {"q": "The '5 Whys' method is for:", "options": ["Asking questions", "Finding the Root Cause", "Interviewing people", "Setting prices"], "ans": 1},
        {"q": "What is 'Poke-Yoke'?", "options": ["A game", "Error-proofing", "A cleaning method", "Fast production"], "ans": 1},
        {"q": "An IATF 16949 audit detects a systemic failure in RCA. Your professional response is:", "options": ["We will fix it by next week.", "We have deployed immediate containment and are initiating a robust 8D report.", "The auditor misunderstood our process.", "We will retrain all operators immediately."], "ans": 1},
        {"q": "Your process Cpk is 0.82. What does this communicate to a global stakeholder?", "options": ["The process is stable but slow.", "The process is incapable of meeting specifications and requires stabilization.", "The product cost is too high.", "The machine needs a new operator."], "ans": 1},
        {"q": "A major non-conformance is found in the design phase. Which tool identifies it?", "options": ["A basic checklist.", "A cross-functional FMEA (Failure Mode and Effects Analysis).", "A customer survey.", "A post-production audit."], "ans": 1},
        {"q": "How do you explain 'Muda' to a CFO focusing on financial impact?", "options": ["It means we have too much trash.", "It represents non-value-added activities impacting EBITDA and cycle time.", "It is a Japanese word for cleanliness.", "It means we need more robots."], "ans": 1},
        {"q": "What is the most executive way to describe 'Poke-Yoke'?", "options": ["Fixing errors manually.", "Implementing error-proofing devices to ensure zero-defect manufacturing.", "Double-checking every part.", "Buying high-quality tools."], "ans": 1},
        {"q": "A 'Gemba Walk' is primarily used by leaders to:", "options": ["Walk around for exercise.", "Observe the actual place of work to identify improvement opportunities.", "Check if people are working hard.", "Talk to the staff about their personal lives."], "ans": 1}
    ],
    "Data Science & SQL": [
        {"q": "Which SQL command retrieves data?", "options": ["GET", "SELECT", "QUERY", "EXTRACT"], "ans": 1},
        {"q": "What is BigQuery?", "options": ["A search engine", "A data warehouse", "A small database", "A coding language"], "ans": 1},
        {"q": "A 'JOIN' in SQL is used to:", "options": ["Delete data", "Combine rows from tables", "Exit a program", "Split a file"], "ans": 1},
        {"q": "What is 'Data Cleansing'?", "options": ["Washing hardware", "Fixing corrupt or inaccurate records", "Deleting all data", "Moving servers"], "ans": 1},
        {"q": "A 'Dashboard' is primarily for:", "options": ["Storing code", "Data visualization and monitoring", "Typing text", "Sending emails"], "ans": 1},
        {"q": "Predictive Modeling uses:", "options": ["Past data to forecast future events", "Old stories", "Random guesses", "Daily logs"], "ans": 0},
        {"q": "The board asks for a projection of failure rates. You should offer:", "options": ["A guess based on last year.", "A predictive model leveraged through BigQuery and SQL analytics.", "A spreadsheet with old data.", "A chart showing previous errors."], "ans": 1},
        {"q": "A 'JOIN' operation in SQL is failing due to data integrity. You say:", "options": ["The tables don't like each other.", "We are experiencing a relational mismatch that requires data cleansing.", "The computer is slow.", "We need to delete the data."], "ans": 1},
        {"q": "How do you justify a 'Big Data' investment to a non-technical CEO?", "options": ["It makes us look modern.", "It allows us to extract actionable insights to drive profitability.", "It stores more files than Excel.", "It is faster than our current server."], "ans": 1},
        {"q": "What is a 'Primary Key' in terms of business impact?", "options": ["A password to enter the office.", "A unique identifier ensuring data accuracy and reporting reliability.", "The main computer in the room.", "A set of rules for the team."], "ans": 1},
        {"q": "When a dashboard shows a KPI in red, your executive response is:", "options": ["I will fix the chart.", "I am analyzing the root cause to deploy a corrective measure.", "It's probably a data error.", "We will look at it next week."], "ans": 1},
        {"q": "Machine Learning is best described to a VP as:", "options": ["Robots doing human work.", "Systems that leverage data patterns to optimize decision-making.", "A fancy type of calculator.", "Automatic coding."], "ans": 1}
    ],
    "Ingeniería de Producto": [
        {"q": "What is a 'BOM'?", "options": ["A project plan", "Bill of Materials", "A safety alarm", "A financial budget"], "ans": 1},
        {"q": "Which tool is for 3D modeling?", "options": ["Excel", "CAD", "SQL", "Word"], "ans": 1},
        {"q": "What is 'DFM'?", "options": ["Design for Manufacturing", "Data for Management", "Digital File Maker", "Direct Factory Model"], "ans": 0},
        {"q": "A 'Prototype' is:", "options": ["The final product", "An early sample to test a concept", "A machine manual", "A blueprint"], "ans": 1},
        {"q": "Which term describes part fitment?", "options": ["Tolerance", "Weight", "Color", "Price"], "ans": 0},
        {"q": "What is 'PLM'?", "options": ["Product Lifecycle Management", "Plant Level Monitor", "Public Low Market", "Price List Maker"], "ans": 0},
        {"q": "A technical specification deviation is requested by production. Your move is:", "options": ["Approve it immediately to save time.", "Conduct a risk-based assessment to ensure specification compliance and structural integrity.", "Say no without checking.", "Tell them to ask the manager."], "ans": 1},
        {"q": "The R&D project is over budget. How do you justify the variance?", "options": ["The engineers are expensive.", "The project has shifted scope to leverage higher ROI through advanced material selection.", "We made a mistake in the math.", "We will spend less next month."], "ans": 1},
        {"q": "A CAD model shows a tolerance stack-up issue. This will lead to:", "options": ["A prettier design.", "Potential non-conformances during assembly impacting throughput.", "Cheaper manufacturing.", "Nothing important."], "ans": 1},
        {"q": "What is 'Structural Integrity' in an executive report?", "options": ["A person's character.", "The ability of a component to withstand designed loads without failure.", "The price of steel.", "The height of a building."], "ans": 1},
        {"q": "Spearheading a 'DFM' project means:", "options": ["Designing for Money.", "Designing for Manufacturing to optimize production efficiency and reduce OPEX.", "Doing Fine Math.", "Developing Fast Machines."], "ans": 1},
        {"q": "The FEA results are inconclusive. You should:", "options": ["Ignore them.", "Initiate a physical prototype stress test to validate the simulation data.", "Ship the product anyway.", "Wait for a software update."], "ans": 1}
    ],
    "Logística": [
        {"q": "What is the primary function of a 3PL?", "options": ["Make products", "Third-Party Logistics provider handling outsourced supply chain operations", "Sell products", "Buy materials"], "ans": 1},
        {"q": "What does 'Last-Mile Delivery' refer to?", "options": ["The longest part of a trip", "The final step of the delivery process from a distribution center to the end user", "A marathon", "International shipping"], "ans": 1},
        {"q": "Cross-docking is used to:", "options": ["Build ships", "Minimize warehouse storage time by transferring materials directly to outbound gates", "Store items forever", "Clean the docks"], "ans": 1},
        {"q": "Reverse Logistics deals with:", "options": ["Driving backwards", "Returns, recycling, and disposal of products", "Fast shipping", "Air freight"], "ans": 1},
        {"q": "In logistics, 'SKU' stands for:", "options": ["Safe Key Unit", "Stock Keeping Unit", "Standard Kilogram Usage", "Store Keep Up"], "ans": 1},
        {"q": "Lead time in logistics is:", "options": ["Time spent waiting for a meeting", "Total time elapsed from order placement to delivery", "Time to manufacture", "Time to pay"], "ans": 1},
        {"q": "The 3PL provider reports a massive backlog at the port. How do you mitigate the EBITDA impact?", "options": ["Wait for customs to clear the backlog.", "Spearhead an expedited multi-modal route to protect the production schedule.", "Tell the board that it is an act of God.", "Cancel all outgoing shipments immediately."], "ans": 1},
        {"q": "Warehouse utilization has reached 98%. What is your strategic recommendation?", "options": ["Rent more space immediately regardless of cost.", "Implement a lean inventory strategy focused on increasing inventory turns.", "Stop receiving material.", "Ask workers to stack boxes higher."], "ans": 1},
        {"q": "Last-mile delivery costs have spiked 20%. How do you maintain margins?", "options": ["Reduce the number of deliveries.", "Leverage route optimization algorithms and renegotiate contracts with carriers.", "Stop delivering to distant areas.", "Ask customers to pay double for shipping."], "ans": 1},
        {"q": "A critical shipment of components is lost. Your high-level response is:", "options": ["I will find the box.", "I am orchestrating a contingency plan with alternative suppliers to avoid line stoppages.", "The carrier is responsible.", "We will wait for the insurance payout."], "ans": 1},
        {"q": "What does 'LTL' stand for in an executive summary?", "options": ["Low Total Loss.", "Less than Truckload - used for optimizing logistics costs.", "Long Term Logistics.", "Linear Time Lag."], "ans": 1},
        {"q": "Your 'Inventory Record Accuracy' (IRA) is 85%. This indicates:", "options": ["A job well done.", "A systemic failure in materials management impacting MRP reliability.", "Too much paperwork.", "The warehouse is too big."], "ans": 1}
    ],
    "Producción": [
        {"q": "What is the goal of 'Cycle Time' reduction?", "options": ["Make workers tired", "Increase throughput and capacity", "Use more electricity", "Decrease product quality"], "ans": 1},
        {"q": "A 'Bill of Materials' (BOM) is essential for:", "options": ["Paying bills", "Knowing exactly what components are required to build a product", "Marketing", "HR"], "ans": 1},
        {"q": "What does WIP stand for?", "options": ["Work In Progress", "Waste In Production", "Workers In Plant", "Weight In Pounds"], "ans": 0},
        {"q": "Throughput Yield measures:", "options": ["How much material is wasted", "The number of good units produced out of the total units started", "Machine temperature", "Overtime hours"], "ans": 1},
        {"q": "What is 'Line Balancing'?", "options": ["Making the machines look nice", "Equitably distributing tasks to minimize idle time and bottlenecks", "Weighing the products", "Cleaning the floor"], "ans": 1},
        {"q": "A 'Kanban' system is used to:", "options": ["Signal the need to move or produce materials", "Punish workers", "Count money", "Design CAD files"], "ans": 0},
        {"q": "The OEE of your main line has dropped to 60%. What is your leadership action?", "options": ["Tell the maintenance team to work harder.", "Spearhead a Gemba-focused audit to identify and eliminate systemic downtime.", "Lower the production target.", "Buy a new machine."], "ans": 1},
        {"q": "A shift manager reports a surge in scrap rates. How do you address the board?", "options": ["The material was bad.", "I have deployed a proactive countermeasure focused on stabilizing process parameters.", "We will look at it tomorrow.", "We are firing the shift manager."], "ans": 1},
        {"q": "Throughput is limited by a bottleneck. You recommend:", "options": ["Ignoring it.", "Performing a Takt-time analysis to balance line capacity and optimize flow.", "Running every station at maximum speed.", "Increasing the headcount everywhere."], "ans": 1},
        {"q": "What is the primary impact of a 'SMED' initiative?", "options": ["Better employee morale.", "Reduction in changeover time to enhance production flexibility and EBITDA.", "A cleaner floor.", "Newer equipment."], "ans": 1},
        {"q": "The factory is experiencing 'Sub-optimization'. This means:", "options": ["Everything is perfect.", "Local improvements are hurting the performance of the entire system.", "Costs are too low.", "The team is small."], "ans": 1},
        {"q": "Which phrase sounds more professional when reporting a production record?", "options": ["We made a lot of parts.", "We successfully delivered a record throughput while maintaining zero-defect standards.", "The machines worked well.", "Everyone was fast today."], "ans": 1}
    ],
    "Project Manager": [
        {"q": "What is a 'Gantt Chart' used for?", "options": ["Budgeting", "Visualizing project schedules, task dependencies, and critical paths", "Hiring", "Quality Control"], "ans": 1},
        {"q": "Scope Creep refers to:", "options": ["Moving slowly", "Uncontrolled changes or continuous growth in a project's scope", "A scary project", "Under budget delivery"], "ans": 1},
        {"q": "An 'Agile' methodology focuses on:", "options": ["Rigid planning", "Iterative development, flexibility, and customer collaboration", "Long documentation", "Working alone"], "ans": 1},
        {"q": "What is a 'Stakeholder Register'?", "options": ["A list of employees", "A document identifying all individuals affected by or influencing the project", "A financial ledger", "A vendor list"], "ans": 1},
        {"q": "A 'Kick-off Meeting' is intended to:", "options": ["Fire people", "Align the team and stakeholders on the project's objectives and baseline", "Celebrate the end", "Order food"], "ans": 1},
        {"q": "What does 'ROI' stand for?", "options": ["Return on Investment", "Rate of Interest", "Risk of Inflation", "Rule of Integration"], "ans": 0},
        {"q": "A key stakeholder requests a major scope change mid-project. You should:", "options": ["Do it immediately.", "Assess the impact on the critical path and EBITDA before orchestrating an alignment meeting.", "Say no and ignore them.", "Tell them it's too late."], "ans": 1},
        {"q": "The project is on the 'Critical Path'. This means:", "options": ["It is a dangerous road.", "Any delay in these tasks will impact the final delivery date.", "The project is almost finished.", "The budget is small."], "ans": 1},
        {"q": "How do you report a 10% budget overrun to the VP?", "options": ["We spent too much.", "Identifying a capital reallocation to mitigate the variance while ensuring project milestones.", "The team was slow.", "It was the supplier's fault."], "ans": 1},
        {"q": "Stakeholder alignment is failing. Your leadership action is:", "options": ["Work alone.", "Spearhead a cross-functional workshop to re-baseline project goals and expectations.", "Send a mass email and hope for the best.", "Cancel the project."], "ans": 1},
        {"q": "What is a 'Risk Mitigation Plan'?", "options": ["A way to avoid work.", "A proactive strategy to reduce the likelihood or impact of potential threats.", "A legal document.", "A list of past mistakes."], "ans": 1},
        {"q": "The project reaches a 'Milestone'. You communicate:", "options": ["We finished a part.", "Successfully achieved a strategic project milestone on time and within specification.", "We are moving forward.", "The team is happy."], "ans": 1}
    ],
    "Otra": [
        {"q": "Which phrase demonstrates highest authority?", "options": ["I helped with the project.", "I spearheaded the strategic initiative.", "I did the work.", "I was part of the group."], "ans": 1},
        {"q": "Professional communication should always be:", "options": ["Extremely long.", "Concise and impact-oriented.", "Casual and funny.", "Detailed and technical only."], "ans": 1},
        {"q": "What is a 'KPI'?", "options": ["Key Performance Indicator.", "King Price Item.", "Knowledge Part Index.", "Keep People Informed."], "ans": 0},
        {"q": "An 'Outcome' is better defined as:", "options": ["The start of something.", "A result or consequence of an action.", "A bill to pay.", "A meeting."], "ans": 1},
        {"q": "Stakeholder alignment means:", "options": ["Ignoring people.", "Ensuring all parties agree on the strategic goal.", "Hiring new staff.", "Selling parts."], "ans": 1},
        {"q": "EBITDA is a measure of:", "options": ["Employee happiness.", "Operational profitability.", "Market share.", "Total debt."], "ans": 1},
        {"q": "When writing an executive email, you should put the main point:", "options": ["At the very end.", "In the first sentence (BLUF - Bottom Line Up Front).", "Hidden in the middle.", "In a separate attachment."], "ans": 1},
        {"q": "A 'Silo Mentality' in business is:", "options": ["Good for teamwork.", "When departments fail to share information, hurting overall efficiency.", "Storing grain.", "Working very fast."], "ans": 1},
        {"q": "To 'Leverage' a resource means to:", "options": ["Use it to maximum advantage.", "Break it.", "Sell it.", "Hide it."], "ans": 0},
        {"q": "A 'Deliverable' is:", "options": ["A package in the mail.", "A tangible or intangible good produced as a result of a project.", "A conversation.", "A promise."], "ans": 1},
        {"q": "What does 'Synergy' imply?", "options": ["Conflict.", "The combined value is greater than the sum of separate effects.", "Working slow.", "Spending money."], "ans": 1},
        {"q": "In a boardroom, 'Hard Savings' refers to:", "options": ["Saving time on a task.", "Auditable, direct reduction in expenses that impact the P&L.", "Future cost avoidance.", "Recycling paper."], "ans": 1}
    ]
}

# --- KNOWLEDGE BASE (PLAN 30 DÍAS Y DRILLS) ---
THIRTY_DAY_PLAN = [
    {"day": 1, "phase": "Cimientos", "title": "El Pitch de Impacto (EBITDA)", "focus": "Cómo presentar tu valor financiero y ahorros duros."},
    {"day": 2, "phase": "Defensa", "title": "Auditorías Globales", "focus": "Contención, RCA, IATF 16949 y VDA 6.3."},
    {"day": 3, "phase": "Sistemas", "title": "Cultura Cero Defectos", "focus": "Métricas de Calidad, FMEA y Risk-based thinking."},
    {"day": 4, "phase": "Tech Ops", "title": "Data Storytelling", "focus": "Explicar SQL, BigQuery y extracción de datos a Directivos."},
    {"day": 5, "phase": "Escala", "title": "S&OP & Logística", "focus": "Inventory Record Accuracy (IRA) y Supply Chain."},
    {"day": 6, "phase": "Futuro", "title": "Inteligencia Artificial", "focus": "Prompt Engineering y Modelos Predictivos en piso."},
    {"day": 7, "phase": "Boardroom", "title": "Prueba de Fuego (CEO)", "focus": "Estructuras ejecutivas bajo presión extrema."}
]

POWER_VERBS_DRILLS = [
    ("I fixed the problem", "I rectified the non-conformance"),
    ("I saved money", "I delivered substantial hard savings"),
    ("I used data", "I leveraged data analytics to drive decision-making"),
    ("I started a project", "I spearheaded a strategic initiative"),
    ("I talked to the client", "I orchestrated cross-functional negotiations")
]

# --- MOTOR DE IA (GEMINI 3 FLASH PREVIEW RESTAURADO) ---
def call_ai(prompt, api_key):
    if not api_key: return "⚠️ Error: Falta la API Key en la configuración."
    # Restaurado al modelo padrino según lo solicitado
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=20)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error en la IA: Código {response.status_code}. Detalles: {response.text}"
    except Exception as e: 
        return f"Error de conexión con Google: {str(e)}"

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
if 'current_drill' not in st.session_state: st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS)

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

# --- FLUJO PRINCIPAL ---

if not st.session_state.get("placement_completed"):
    # 1. INGRESO (PERSISTENTE)
    if st.session_state.screen == 'home':
        st.markdown("<div class='hero-box'><h1>Executive Mastery Protocol</h1><p>Tu progreso se sincroniza automáticamente en la nube.</p></div>", unsafe_allow_html=True)
        col1, _ = st.columns([1, 1])
        with col1:
            st.markdown("<div class='executive-card'>", unsafe_allow_html=True)
            name_input = st.text_input("Ingresa tu Nombre Completo:")
            if st.button("Acceder al Sistema 🧠"):
                if name_input:
                    with st.spinner("Buscando expediente en la nube..."):
                        if load_user_progress(name_input):
                            st.success(f"¡Bienvenido de vuelta, {name_input}!")
                            time.sleep(1.5)
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

    # 2. EXAMEN (12 MCQ + 4 AI = 16 ETAPAS)
    elif st.session_state.screen == 'placement_test':
        questions = DYNAMIC_MCQ.get(st.session_state.user_area, DYNAMIC_MCQ["Otra"])
        total_mcq = len(questions) # Esto es 12
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
                    if i == q['ans']: st.session_state.placement_score += 10
                    st.session_state.placement_step += 1
                    st.rerun()
        else:
            ai_step = current_step - total_mcq
            if not st.session_state.dynamic_scenarios:
                with st.spinner("Generando escenarios tácticos con IA..."):
                    prompt = f"Generate 4 tough executive scenarios for a {st.session_state.user_area} leader. Format: Scenario 1 --- Scenario 2 --- Scenario 3 --- Scenario 4"
                    res = call_ai(prompt, API_KEY)
                    st.session_state.dynamic_scenarios = res.split('---')

            current_scenario = st.session_state.dynamic_scenarios[ai_step] if ai_step < len(st.session_state.dynamic_scenarios) else "Explain a major failure and your corrective action."
            st.markdown(f"<div class='executive-card'><b>Escenario AI:</b><br>{current_scenario}</div>", unsafe_allow_html=True)
            ans = st.text_area("Tu Respuesta en Inglés:", key=f"ans_{ai_step}")
            st_speech_to_text(key=f"voice_{ai_step}")
            if st.button("Validar Etapa"):
                if len(ans) > 20:
                    st.session_state.placement_ai_responses.append({"q": current_scenario, "a": ans})
                    st.session_state.placement_step += 1
                    if st.session_state.placement_step >= total_steps: 
                        st.session_state.screen = 'finalizing'
                    st.rerun()
                else:
                    st.warning("Desarrolla más tu respuesta para poder evaluar tu nivel.")

    elif st.session_state.screen == 'finalizing':
        with st.spinner("El Mentor Elite está auditando tu nivel de autoridad..."):
            ai_text = "\n".join([f"Q: {x['q']}\nA: {x['a']}" for x in st.session_state.placement_ai_responses])
            prompt = f"Audit engineer {st.session_state.user_area}. Score {st.session_state.placement_score}. Open responses: {ai_text}. Determine CEFR Level, Score 0-100, Diagnostic, and 2 Pro Tips in Spanish."
            res = call_ai(prompt, API_KEY)
            st.session_state.placement_eval_detailed = res
            for level in ["C2", "C1", "B2", "B1", "A2"]:
                if level in res: 
                    st.session_state.english_level = f"{level} - Certified"
                    break
            if st.session_state.english_level == "No Evaluado": st.session_state.english_level = "B1 - Intermediate"
            
            st.session_state.placement_completed = True
            save_user_progress()
            st.session_state.screen = 'results'
            st.rerun()

    elif st.session_state.screen == 'results':
        st.markdown(f"<div class='level-box'><h1>{st.session_state.english_level}</h1><p>Auditoría Finalizada (16/16 Etapas)</p></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='executive-card'><p style='white-space: pre-wrap;'>{st.session_state.placement_eval_detailed}</p></div>", unsafe_allow_html=True)
        if st.button("Desbloquear War Room ⚔️"):
            st.session_state.screen = 'dashboard'
            st.rerun()

# 3. WAR ROOM (PERSISTENTE)
else:
    st.title(f"🛡️ War Room: {st.session_state.user_name}")
    tabs = st.tabs(["📅 Roadmap 30 Días", "🤖 AI Combat Lab", "⚔️ Power Verbs", "🔥 The Forge", "📖 Enciclopedia"])
    
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
        # Encontrar la misión actual basada en el día
        mission = next((p for p in THIRTY_DAY_PLAN if p['day'] == st.session_state.current_day), THIRTY_DAY_PLAN[-1])
        st.subheader(f"Misión Diaria: {mission['title']}")
        if st.button("🎙️ Generar Escenario con el Mentor"):
            with st.spinner("Preparando..."):
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
                st.info(f"💡 **TIP PRO:** '{drill[1].split()[1]}' es un verbo de acción que implica liderazgo.")
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
            st.write("- **EBITDA:** Beneficio operativo antes de intereses, impuestos, depreciación y amortización.")
            st.write("- **Hard Savings:** Ahorros duros que impactan directamente el estado de resultados.")
            st.write("- **S&OP:** Sales and Operations Planning. Alineación de demanda y suministro.")
        with c2:
            st.markdown("<span class='badge-tech'>🧬 Tech & Data</span>", unsafe_allow_html=True)
            st.write("- **SQL Query:** Consulta estructurada a bases de datos.")
            st.write("- **BigQuery:** Data Warehouse empresarial de Google.")
            st.write("- **IRA:** Inventory Record Accuracy. Precisión de inventario.")
        with c3:
            st.markdown("<span class='badge-compliance'>⚖️ Quality</span>", unsafe_allow_html=True)
            st.write("- **IATF 16949:** Sistema de Gestión de Calidad Automotriz global.")
            st.write("- **Cpk:** Índice de capacidad del proceso a largo plazo.")
            st.write("- **RCA:** Root Cause Analysis (Análisis de Causa Raíz).")

st.divider()
st.caption("Protocolo diseñado por Ing. Fernando Montes Delgado | Cloud Persistence & Full Knowledge Base Enabled | Gemini 3 Flash Preview")
