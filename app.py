import streamlit as st
import requests
import time
import random

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
    
    /* Tabs Navegación */
    .stTabs [data-baseweb="tab-list"] { background-color: #1e293b; padding: 10px; border-radius: 15px; border: 1px solid #334155; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #4f46e5 !important; color: white !important; border-radius: 8px;}
    
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
    .day-active {
        border-color: #f59e0b; background-color: #451a03; 
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.3);
    }
    .badge-tech { background-color: #1e40af; color: #dbeafe; padding: 4px 10px; border-radius: 8px; font-weight: bold; }
    .badge-ops { background-color: #92400e; color: #fef3c7; padding: 4px 10px; border-radius: 8px; font-weight: bold; }
    .badge-compliance { background-color: #065f46; color: #dcfce7; padding: 4px 10px; border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- BÓVEDA DE SEGURIDAD (SECRETS) ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = ""

# --- PILARES DE CONOCIMIENTO TÉCNICO ---
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

# --- MOTOR DE INTELIGENCIA ARTIFICIAL ---
def call_ai(prompt, api_key):
    if not api_key: 
        return "⚠️ Error de Configuración: La Bóveda de Secretos en Streamlit Cloud está vacía."
    
    # Usamos el modelo estable y avanzado solicitado
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=20)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error en el servidor de IA ({response.status_code}). Verifica tu API Key en los Secretos."
    except Exception:
        return "Falla de conexión. Reintenta en unos segundos."

# --- MANEJO DE ESTADO DE SESIÓN ---
if 'screen' not in st.session_state: st.session_state.screen = 'home'
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_area' not in st.session_state: st.session_state.user_area = ""
if 'english_level' not in st.session_state: st.session_state.english_level = "No Evaluado"
if 'current_day' not in st.session_state: st.session_state.current_day = 1
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'current_drill' not in st.session_state: st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS)

# --- PANEL DE CONTROL LATERAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 3em;'>⚙️</h1>", unsafe_allow_html=True)
    st.title("Mission Control")
    
    if not API_KEY:
        st.error("🔒 Bóveda de Seguridad: VACÍA")
        st.caption("Configura 'GEMINI_API_KEY' en los Secrets de Streamlit Cloud.")
        active_key = ""
    else:
        st.success("🔒 Conexión Segura: ACTIVADA")
        active_key = API_KEY
    
    st.divider()
    
    if st.session_state.user_name:
        st.write(f"**Líder:** {st.session_state.user_name}")
        st.write(f"**Especialidad:** {st.session_state.user_area}")
        st.markdown(f"**Nivel Actual:** `<span style='color:#f59e0b; font-weight:bold;'>{st.session_state.english_level}</span>`", unsafe_allow_html=True)
        st.write(f"**Total XP:** {st.session_state.xp}")
        st.progress(st.session_state.current_day / 30)
        st.divider()
        
    if st.button("🔄 Reiniciar Protocolo"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- NAVEGACIÓN DE PANTALLAS ---

# 1. PANTALLA DE INICIO Y PERFIL
if st.session_state.english_level == "No Evaluado":
    if st.session_state.screen == 'home':
        st.markdown("""
            <div class="hero-box">
                <h1 style="color: white; font-size: 3em; margin-bottom: 10px;">Executive Mastery Protocol</h1>
                <p style="color: #cbd5e1; font-size: 1.2em; max-width: 800px; margin: 20px auto;">
                    Simulador de autoridad lingüística para Ingenieros. Evaluación adaptativa impulsada por IA inspirada en el aprendizaje acelerado.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("<div class='executive-card'>", unsafe_allow_html=True)
            st.markdown("### 👤 Perfil Táctico")
            name = st.text_input("Nombre Completo:")
            area = st.selectbox("Especialidad:", ["Operaciones & Supply Chain", "Calidad & Lean Manufacturing", "Data Science & SQL", "Ingeniería de Producto", "Otra"])
            
            if st.button("Generar Examen de Colocación 🧠"):
                if not active_key: st.error("IA no configurada en la bóveda de secretos.")
                elif not name: st.error("Ingresa tu nombre.")
                else:
                    st.session_state.user_name = name
                    st.session_state.user_area = area
                    st.session_state.screen = 'placement_test'
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # 2. EXAMEN DE COLOCACIÓN (MENTORING STYLE)
    elif st.session_state.screen == 'placement_test':
        st.title("🎯 AI Placement Assessment")
        st.write("Tu Coach Elite evaluará tu nivel para personalizar tu ruta. Responde con confianza.")
        
        if 'placement_q' not in st.session_state:
            with st.spinner("Tu mentor está preparando una pregunta de alto nivel..."):
                prompt = f"You are an Elite Executive Coach for high performers. Ask ONE engaging conversational question in English for a {st.session_state.user_area} engineer. Focus on a project or success. Keep vocabulary accessible (B1/B2 level)."
                st.session_state.placement_q = call_ai(prompt, active_key)
                st.rerun()
                
        st.markdown(f"<div class='executive-card'><b>Elite Coach:</b><br><br><i>\"{st.session_state.placement_q}\"</i></div>", unsafe_allow_html=True)
        ans = st.text_area("Tu Respuesta (Inglés):", height=150)
        
        if st.button("Descubrir mi Nivel 🚀"):
            if len(ans) < 15:
                st.warning("Por favor, escribe un poco más para un diagnóstico preciso.")
            else:
                with st.spinner("Analizando tu autoridad lingüística..."):
                    eval_prompt = f"""Analyze this response from a {st.session_state.user_area} engineer. 
                    Question: {st.session_state.placement_q}. Answer: {ans}. 
                    Determine CEFR Level. Format strictly in SPANISH:
                    NIVEL: [Level]
                    TUS FORTALEZAS: [1 sentence of praise, building confidence]
                    HACK DE APRENDIZAJE: [1 actionable hack used by polyglots for this specific user]"""
                    result = call_ai(eval_prompt, active_key)
                    st.session_state.placement_eval = result
                    
                    if "C2" in result: st.session_state.english_level = "C2 - Executive"
                    elif "C1" in result: st.session_state.english_level = "C1 - Advanced"
                    elif "B2" in result: st.session_state.english_level = "B2 - Upper Intermediate"
                    elif "B1" in result: st.session_state.english_level = "B1 - Intermediate"
                    else: st.session_state.english_level = "A2/B1 - Foundation"
                    
                    st.session_state.screen = 'placement_results'
                    st.rerun()

    elif st.session_state.screen == 'placement_results':
        st.markdown(f"""
            <div class="level-box">
                <h2>Nivel de Mando Determinado</h2>
                <h1 style="font-size: 4em; margin: 10px 0;">{st.session_state.english_level}</h1>
                <p>{st.session_state.user_name} | {st.session_state.user_area}</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"<div class='executive-card'><h3>🔍 Reporte Analítico:</h3><p>{st.session_state.placement_eval}</p></div>", unsafe_allow_html=True)
        if st.button("Entrar al War Room (Dashboard) ⚔️"):
            st.session_state.screen = 'dashboard'
            st.rerun()

# 3. WAR ROOM (DASHBOARD COMPLETO)
else:
    st.title(f"🛡️ Executive War Room: {st.session_state.user_name}")
    
    tabs = st.tabs(["📅 Roadmap 30 Días", "🤖 AI Combat Lab", "⚔️ Power Verbs", "🔥 The Forge", "📖 Enciclopedia"])
    
    # --- TAB 1: ROADMAP ---
    with tabs[0]:
        st.subheader("Tu Ruta de Transformación")
        for plan in THIRTY_DAY_PLAN:
            is_active = "day-active" if plan['day'] == st.session_state.current_day else ""
            st.markdown(f"""
                <div class="day-card {is_active}">
                    <span style="color: #3b82f6; font-weight: 900;">DÍA {plan['day']}</span>
                    <h3 style="margin-top: 5px; color: white;">{plan['title']}</h3>
                    <p style="color:#94a3b8; margin-bottom:0;">{plan['focus']}</p>
                </div>
            """, unsafe_allow_html=True)

    # --- TAB 2: AI COMBAT LAB (FEEDBACK MOTIVADOR 80/20) ---
    with tabs[1]:
        mission = next((p for p in THIRTY_DAY_PLAN if p['day'] == st.session_state.current_day), THIRTY_DAY_PLAN[-1])
        st.subheader(f"Misión del Día: {mission['title']}")
        
        if st.button("🎙️ Iniciar Simulación con el Mentor"):
            with st.spinner("Tu mentor está entrando a la sala..."):
                prompt = f"You are an inspiring Executive Mentor. Mentee: {st.session_state.user_area} engineer, Level {st.session_state.english_level}. Focus: {mission['focus']}. Ask a challenging but motivating workplace question."
                st.session_state.daily_q = call_ai(prompt, active_key)
                
        if 'daily_q' in st.session_state:
            st.markdown(f"<div class='executive-card'><b>Elite Mentor:</b><br><br>\"{st.session_state.daily_q}\"</div>", unsafe_allow_html=True)
            user_ans = st.text_area("Tu Respuesta Ejecutiva (en Inglés):", height=150)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⚖️ Feedback de Alto Rendimiento"):
                    if not user_ans: st.warning("Escribe algo.")
                    else:
                        with st.spinner("Generando retroalimentación acelerada..."):
                            f_prompt = f"Evaluate this answer to '{st.session_state.daily_q}'. Provide in SPANISH: 1. ENERGÍA (0-100), 2. LO EXCELENTE, 3. AJUSTE DEL 1% (80/20 rule), 4. VERSIÓN BOARDROOM (perfect executive script for shadowing)."
                            feedback = call_ai(f_prompt, active_key)
                            st.markdown(f"<div class='level-box'><b>Reporte del Mentor:</b><br>{feedback}</div>", unsafe_allow_html=True)
                            st.session_state.xp += 100
            with col2:
                if st.button("🔥 Completar y Avanzar"):
                    st.session_state.current_day += 1
                    if 'daily_q' in st.session_state: del st.session_state.daily_q
                    st.rerun()

    # --- TAB 3: POWER VERBS ---
    with tabs[2]:
        st.subheader("Drill: Power Verbs (Reflejos)")
        drill = st.session_state.current_drill
        st.markdown(f"<div class='executive-card' style='border-color:#f59e0b;'>Un Junior diría: <b>'{drill[0]}'</b></div>", unsafe_allow_html=True)
        pv_ans = st.text_input("Versión Ejecutiva (Sustituye por el Power Verb):")
        if st.button("Neutralizar 🎯"):
            if drill[1].lower() in pv_ans.lower():
                st.success(f"¡Correcto! XP +50. La frase letal es: '{drill[1]}'")
                st.session_state.xp += 50
                st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS)
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"Sigue siendo básico. Usa la frase: '{drill[1]}'")

    # --- TAB 4: THE FORGE ---
    with tabs[3]:
        st.subheader("La Fragua (STAR Method & EBITDA)")
        draft = st.text_area("Logro básico o tarea realizada:", placeholder="Ej: Reduje el scrap en la línea 4.")
        if st.button("⚒️ Forjar Logro VP"):
            if not draft: st.warning("Escribe un logro.")
            else:
                with st.spinner("Refinando con IA..."):
                    forge_p = f"Convert this into a powerful executive STAR achievement in English focused on EBITDA and leadership: '{draft}'"
                    res = call_ai(forge_p, active_key)
                    st.markdown(f"<div class='executive-card'><b>Versión Ejecutiva:</b><br>{res}</div>", unsafe_allow_html=True)

    # --- TAB 5: ENCICLOPEDIA ---
    with tabs[4]:
        st.subheader("Glosario de Autoridad Técnica")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<span class='badge-ops'>🏭 Operaciones</span>", unsafe_allow_html=True)
            st.write("- **EBITDA:** Beneficio operativo real.")
            st.write("- **Hard Savings:** Ahorros auditables directos.")
            st.write("- **IATF 16949:** Estándar de calidad automotriz.")
            st.write("- **VDA 6.3:** Auditoría de proceso alemana.")
        with c2:
            st.markdown("<span class='badge-tech'>🧬 Tech & Supply</span>", unsafe_allow_html=True)
            st.write("- **SQL:** Lenguaje de consulta de datos.")
            st.write("- **IRA:** Accuracy de inventario.")
            st.write("- **S&OP:** Planeación de ventas y operaciones.")
            st.write("- **Prompting:** Instrucciones para modelos de IA.")

st.divider()
st.caption("Protocolo desarrollado para Fernando Montes Delgado | Architecture: Python/Streamlit | UI: Executive Behavior Design")
