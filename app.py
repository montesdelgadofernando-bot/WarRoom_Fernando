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

# --- BANCO DE PREGUNTAS MCQ COMPLEJAS (Toma de decisiones) ---
DYNAMIC_MCQ = {
    "Operaciones & Supply Chain": [
        {"q": "Un proveedor crítico anuncia un aumento del 25% en el tiempo de entrega. ¿Cómo reportas el impacto a la junta?", "options": ["Esperar a que llegue el material.", "Reportar una disrupción en el lead-time y su impacto proyectado en el OEE.", "Pedir al proveedor que trabaje más rápido.", "Aumentar el stock de seguridad sin analizar costos."], "ans": 1},
        {"q": "El EBITDA se está reduciendo debido al aumento de fletes. ¿Cuál es tu movimiento estratégico?", "options": ["Cortar personal de logística.", "Optimizar la precisión de inventario (IRA) y liderar una estrategia multi-modal.", "Subir los precios y esperar.", "Detener todos los embarques."], "ans": 1},
        {"q": "En una reunión de S&OP, hay una brecha enorme entre demanda y capacidad. Debes:", "options": ["Producir a máxima velocidad.", "Orquestar una alineación cross-functional para priorizar SKUs de alto margen.", "Decirle a ventas que deje de vender.", "Esperar datos del próximo mes."], "ans": 1},
        {"q": "Los costos de mantenimiento de inventario están al 30%. ¿Cómo los reduces de forma ejecutiva?", "options": ["Tirar el stock viejo.", "Implementar un sistema pull JIT respaldado por modelos predictivos.", "Mover stock a un almacén barato.", "Dejar de comprar por una semana."], "ans": 1},
        {"q": "En un reporte de proyecto, ¿cuál frase demuestra mayor autoridad?", "options": ["Ayudé al equipo a terminar.", "Lideré la iniciativa estratégica para entregar un 15% de ahorros duros.", "Estuve presente durante la ejecución.", "El proyecto se terminó a tiempo."], "ans": 1},
        {"q": "Un cuello de botella reduce la salida diaria un 10%. Tu acción inmediata es:", "options": ["Contratar más gente ahí.", "Realizar un análisis de Takt-time para balancear la línea.", "Pedir que la máquina corra más rápido.", "Reportar la máquina descompuesta."], "ans": 1}
    ],
    "Calidad & Lean Manufacturing": [
        {"q": "Una auditoría VDA 6.3 detecta una falla sistémica en tratamiento térmico. Tu respuesta profesional es:", "options": ["Arreglaremos la máquina mañana.", "Hemos desplegado una acción de contención e iniciado un RCA robusto para identificar la contramedida.", "El auditor está mal.", "Detendremos la línea hasta cambiar de proveedor."], "ans": 1},
        {"q": "Tu Cpk es de 0.85. ¿Qué le comunicas a un cliente global?", "options": ["El proceso es estable.", "El proceso es incapaz de cumplir especificaciones y requiere estabilización inmediata.", "El costo es muy bajo.", "La máquina va lento."], "ans": 1},
        {"q": "En un evento Kaizen identificas 'Muda' en el flujo. ¿Cuál es el impacto?", "options": ["Moral alta.", "Mejora del EBITDA mediante la eliminación de desperdicio y optimización del ciclo.", "Almacén limpio.", "Mejor marketing."], "ans": 1},
        {"q": "Un cliente descubre un defecto en una parte crítica de seguridad. ¿Primer paso ejecutivo?", "options": ["Pedir perdón.", "Orquestar una cuarentena global del lote e iniciar un reporte 8D.", "Despedir al operador.", "Decirle al cliente que lo use."], "ans": 1},
        {"q": "En diseño, ¿cuál herramienta predice modos de falla antes de que ocurran?", "options": ["Lista de verificación.", "Un FMEA cross-functional.", "Auditoría post-producción.", "Encuestas."], "ans": 1},
        {"q": "Forma avanzada de describir 'A prueba de errores' en un resumen ejecutivo:", "options": ["Arreglar errores.", "Implementar dispositivos Poke-Yoke para asegurar manufactura con cero defectos.", "Revisar todo dos veces.", "Contratar inspectores."], "ans": 1}
    ]
}

# --- BASE DE CONOCIMIENTO (PLAN 30 DÍAS) ---
THIRTY_DAY_PLAN = [
    {"day": 1, "phase": "Cimientos", "title": "El Pitch de Impacto (EBITDA)", "focus": "Cómo presentar tu valor financiero y ahorros duros."},
    {"day": 2, "phase": "Defensa", "title": "Auditorías Globales", "focus": "Contención, RCA, IATF 16949 y VDA 6.3."},
    {"day": 3, "phase": "Sistemas", "title": "Cultura Cero Defectos", "focus": "Métricas de Calidad, FMEA y Risk-based thinking."},
    {"day": 4, "phase": "Tech Ops", "title": "Data Storytelling", "focus": "Explicar SQL, BigQuery y extracción de datos a Directivos."},
    {"day": 5, "phase": "Escala", "title": "S&OP & Logística", "focus": "Inventory Record Accuracy (IRA) y Supply Chain."},
    {"day": 6, "phase": "Futuro", "title": "Inteligencia Artificial", "focus": "Prompt Engineering y Modelos Predictivos en piso."},
    {"day": 7, "phase": "Boardroom", "title": "Prueba de Fuego (CEO)", "focus": "Estructuras ejecutivas bajo presión extrema."},
]

# --- POWER VERBS ---
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

# --- ESTADO DE SESIÓN ---
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
        st.markdown(f"**Nivel:** `<span style='color:#f59e0b; font-weight:bold;'>{st.session_state.english_level}</span>`", unsafe_allow_html=True)
        st.write(f"**XP:** {st.session_state.xp}")
    if st.button("🔄 Reset Protocol"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# --- FLUJO ---

if st.session_state.english_level == "No Evaluado":
    # --- PANTALLA INICIAL ---
    if st.session_state.screen == 'home':
        st.markdown("""
            <div class="hero-box">
                <h1>Executive Mastery Protocol</h1>
                <p>Auditoría de 16 etapas iniciada. Selecciona tu área de mando.</p>
            </div>
        """, unsafe_allow_html=True)
        col1, _ = st.columns([1, 1])
        with col1:
            st.markdown("<div class='executive-card'>", unsafe_allow_html=True)
            name = st.text_input("Nombre Completo:")
            area = st.selectbox("Especialidad Táctica:", list(DYNAMIC_MCQ.keys()))
            if st.button("Activar Protocolo de 16 Etapas 🧠"):
                if name:
                    st.session_state.user_name = name
                    st.session_state.user_area = area
                    st.session_state.screen = 'placement_test'
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- EXAMEN (12 MCQ + 4 AI) ---
    elif st.session_state.screen == 'placement_test':
        questions = DYNAMIC_MCQ.get(st.session_state.user_area, DYNAMIC_MCQ["Operaciones & Supply Chain"])
        total_mcq = len(questions)
        total_ai = 4
        total_steps = total_mcq + total_ai
        current_step = st.session_state.placement_step
        
        st.title(f"🎯 Etapa {current_step + 1} de {total_steps}")
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
                with st.spinner("Generando escenarios personalizados..."):
                    prompt = f"Generate 4 distinct executive scenarios for a {st.session_state.user_area} leader. Format: Scenario 1 --- Scenario 2..."
                    res = call_ai(prompt, API_KEY)
                    st.session_state.dynamic_scenarios = res.split('---')

            current_scenario = st.session_state.dynamic_scenarios[ai_step_idx]
            st.markdown(f"<div class='executive-card'><b>Escenario AI:</b><br><br>{current_scenario}</div>", unsafe_allow_html=True)
            ans = st.text_area("Respuesta Ejecutiva:", key=f"ai_ans_{ai_step_idx}")
            st_speech_to_text(key=f"voice_{ai_step_idx}")
            if st.button("Validar Etapa"):
                if len(ans) > 30:
                    st.session_state.placement_ai_responses.append({"q": current_scenario, "a": ans})
                    st.session_state.placement_step += 1
                    if st.session_state.placement_step == total_steps: st.session_state.screen = 'finalizing'
                    st.rerun()

    # --- FINALIZACIÓN ---
    elif st.session_state.screen == 'finalizing':
        with st.spinner("Auditoría en curso..."):
            ai_text = "\n".join([f"Q: {x['q']}\nA: {x['a']}" for x in st.session_state.placement_ai_responses])
            prompt = f"Audit this {st.session_state.user_area} expert. MCQ Score: {st.session_state.placement_score}. Answers: {ai_text}. Provide CEFR Level, Final Score (0-100), and Detailed Feedback in Spanish including errors and pro tips."
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
        if st.button("Unlock War Room ⚔️"):
            st.session_state.screen = 'dashboard'
            st.rerun()

# --- WAR ROOM (DASHBOARD COMPLETO) ---
else:
    st.title(f"🛡️ War Room: {st.session_state.user_name}")
    tabs = st.tabs(["📅 Roadmap", "🤖 Combat Lab", "⚔️ Power Verbs", "🔥 The Forge", "📖 Enciclopedia"])
    
    # 1. ROADMAP
    with tabs[0]:
        st.subheader("Tu Ruta de Transformación Táctica")
        for plan in THIRTY_DAY_PLAN:
            is_active = "day-active" if plan['day'] == st.session_state.current_day else ""
            st.markdown(f"""
                <div class="day-card {is_active}">
                    <b>DÍA {plan['day']}</b> • {plan['title']}
                    <p style='font-size: 0.9em; color: #94a3b8;'>{plan['focus']}</p>
                </div>
            """, unsafe_allow_html=True)

    # 2. COMBAT LAB (CON FEEDBACK Y TIPS PRO)
    with tabs[1]:
        mission = next((p for p in THIRTY_DAY_PLAN if p['day'] == st.session_state.current_day), THIRTY_DAY_PLAN[-1])
        st.subheader(f"Misión: {mission['title']}")
        
        if st.button("🎙️ Generar Escenario Táctico"):
            with st.spinner("Preparando..."):
                prompt = f"You are an Elite Mentor. Ask a challenging question about {mission['focus']} to a {st.session_state.user_area} expert. Level {st.session_state.english_level}."
                st.session_state.daily_q = call_ai(prompt, API_KEY)
                st_text_to_speech(st.session_state.daily_q)
        
        if 'daily_q' in st.session_state:
            st.markdown(f"<div class='executive-card'><b>Mentor:</b> {st.session_state.daily_q}</div>", unsafe_allow_html=True)
            ans = st.text_area("Tu respuesta:")
            st_speech_to_text(key="combat_voice")
            
            if st.button("Auditar Respuesta Ejecutiva"):
                with st.spinner("Auditando..."):
                    # Prompt que fuerza Feedback y Tips Pro
                    prompt = f"""Evaluate: {ans}. 
                    Provide in SPANISH:
                    1. SCORE (0-100)
                    2. FEEDBACK TÉCNICO: ¿Qué errores gramaticales o de autoridad hubo?
                    3. TIP PRO: Un consejo de nivel VP para mejorar esta respuesta específica.
                    4. VERSIÓN BOARDROOM: El script perfecto en inglés.
                    """
                    feedback = call_ai(prompt, API_KEY)
                    st.markdown(f"<div class='level-box' style='background-color: #1e293b; border-left-color: #f59e0b;'>{feedback}</div>", unsafe_allow_html=True)
                    st.session_state.xp += 100

    # 3. POWER VERBS (CON FEEDBACK Y TIPS PRO)
    with tabs[2]:
        st.subheader("Combate de Reflejos: Power Verbs")
        drill = st.session_state.current_drill
        st.markdown(f"<div class='executive-card' style='border-color:#f59e0b;'>Un Junior diría: <b>'{drill[0]}'</b></div>", unsafe_allow_html=True)
        pv_ans = st.text_input("Versión Ejecutiva:")
        
        if st.button("Validar Impacto 🎯"):
            if drill[1].lower() in pv_ans.lower():
                st.success("¡Excelente! Has neutralizado la frase básica.")
                st.session_state.xp += 50
                st.info(f"💡 **TIP PRO:** '{drill[1].split()[1]}' es un verbo de acción que implica liderazgo y responsabilidad total. Úsalo en tus juntas de resultados.")
                time.sleep(2)
                st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS)
                st.rerun()
            else:
                st.error(f"Sigue siendo básico. La frase letal es: '{drill[1]}'")
                st.caption(f"💡 **TIP PRO:** Evita verbos como 'fixed' o 'did'. Usa verbos que demuestren un proceso o una estrategia, como 'rectified' o 'orchestrated'.")

    # 4. THE FORGE (CON FEEDBACK Y TIPS PRO)
    with tabs[3]:
        st.subheader("La Fragua: Forja de Logros")
        draft = st.text_area("Ingresa un logro básico (ej: Reduje scrap):")
        if st.button("⚒️ Forjar Logro VP"):
            with st.spinner("Forjando..."):
                res = call_ai(f"Transform to STAR executive achievement in English focused on EBITDA with a Pro Tip in Spanish: {draft}", API_KEY)
                st.markdown(f"<div class='executive-card'><b>Resultado VP:</b><br>{res}</div>", unsafe_allow_html=True)

    # 5. ENCICLOPEDIA
    with tabs[4]:
        st.subheader("Enciclopedia Técnica")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<span class='badge-ops'>🏭 Ops</span> EBITDA, Hard Savings, Lead-time.", unsafe_allow_html=True)
        with col2:
            st.markdown("<span class='badge-tech'>🧬 Tech</span> SQL, BigQuery, Cpk, RCA.", unsafe_allow_html=True)

st.divider()
st.caption("Protocolo desarrollado por Ing. Fernando Montes Delgado | Feedback & Pro Tips Enabled")
