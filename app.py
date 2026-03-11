import streamlit as st
import requests
import time
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Executive Mastery SaaS", page_icon="🦅", layout="wide")

# --- CSS (PSICOLOGÍA DE COLOR Y DISEÑO CONDUCTUAL) ---
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
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: #1e293b; padding: 10px; border-radius: 15px; border: 1px solid #334155; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #4f46e5 !important; color: white !important; border-radius: 8px;}
    
    /* Tarjetas y Contenedores */
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

# --- OBTENCIÓN DE API KEY SILENCIOSA ---
# REEMPLAZA EL TEXTO ENTRE COMILLAS CON TU LLAVE REAL:
API_KEY = "AIzaSyB-0E_uJwBSA1FVpC2E6mus3ZX06TkV1Xo"

# --- PILARES DE CONOCIMIENTO RESTAURADOS ---
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

# --- FUNCIONES DE IA ---
def call_ai(prompt, api_key):
    if not api_key: return "⚠️ Error: Falta la API Key en la configuración del servidor."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=15)
        return response.json()['candidates'][0]['content']['parts'][0]['text'] if response.status_code == 200 else f"Error procesando la IA: {response.status_code}"
    except: return "Error de conexión con el servidor de Google."

# --- MANEJO DE ESTADO ---
if 'screen' not in st.session_state: st.session_state.screen = 'home'
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_area' not in st.session_state: st.session_state.user_area = ""
if 'english_level' not in st.session_state: st.session_state.english_level = "No Evaluado"
if 'current_day' not in st.session_state: st.session_state.current_day = 1
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'current_drill' not in st.session_state: st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS)

# --- MENÚ LATERAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 3em;'>⚙️</h1>", unsafe_allow_html=True)
    st.title("Mission Control")
    
    # Hemos eliminado la caja de texto. Ahora siempre tomará la llave interna.
    st.success("Conexión segura establecida con IA.")
    active_key = API_KEY
    
    st.divider()
    
    if st.session_state.user_name:
        st.write(f"**Líder:** {st.session_state.user_name}")
        st.write(f"**Área:** {st.session_state.user_area}")
        st.markdown(f"**Nivel:** `<span style='color:#f59e0b; font-weight:bold;'>{st.session_state.english_level}</span>`", unsafe_allow_html=True)
        st.write(f"**Total XP:** {st.session_state.xp}")
        st.progress(st.session_state.current_day / 30)
        st.divider()
        
    if st.button("🔄 Reiniciar Perfil"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ==========================================
# FASE 1: ONBOARDING Y DIAGNÓSTICO
# ==========================================
if st.session_state.english_level == "No Evaluado":
    
    if st.session_state.screen == 'home':
        st.markdown("""
            <div class="hero-box">
                <h1 style="color: white; font-size: 3em; margin-bottom: 10px;">Executive Mastery Protocol</h1>
                <p style="color: #cbd5e1; font-size: 1.2em; max-width: 800px; margin: 20px auto;">
                    Evaluación táctica impulsada por IA. Ingresa tus datos para generar tu perfil de mando y tu plan a medida.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("<div class='executive-card'>", unsafe_allow_html=True)
            st.markdown("### 👤 Configura tu Perfil Táctico")
            name = st.text_input("Tu Nombre Completo:")
            area = st.selectbox("Tu Área de Especialidad Técnica:", ["Operaciones & Supply Chain", "Calidad & Lean Manufacturing", "Data Science & SQL", "Ingeniería de Producto", "Otra"])
            
            if st.button("Generar Examen de Colocación 🧠"):
                if not active_key: st.error("Error: IA no conectada.")
                elif not name: st.error("Ingresa tu nombre.")
                else:
                    st.session_state.user_name = name
                    st.session_state.user_area = area
                    st.session_state.screen = 'placement_test'
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.screen == 'placement_test':
        st.title("🎯 Examen de Colocación (AI Assessment)")
        st.write("La IA ha generado un escenario basado en tu área. Responde en inglés con al menos 3 oraciones.")
        
        if 'placement_q' not in st.session_state:
            with st.spinner("Generando escenario técnico..."):
                prompt = f"You are a global recruiter. Ask ONE challenging interview question in English for a {st.session_state.user_area} engineer. Require them to explain a complex technical concept."
                st.session_state.placement_q = call_ai(prompt, active_key)
                st.rerun()
                
        st.markdown(f"<div class='executive-card'><b>Global Recruiter:</b><br><br><i>\"{st.session_state.placement_q}\"</i></div>", unsafe_allow_html=True)
        ans = st.text_area("Tu Respuesta (En Inglés):", height=150)
        
        if st.button("Auditar mi Nivel de Inglés 🚀"):
            if len(ans) < 20:
                st.warning("Respuesta muy corta. Escribe más detalle.")
            else:
                with st.spinner("Analizando tu autoridad lingüística..."):
                    eval_prompt = f"Analyze this english response from a {st.session_state.user_area} engineer. Question: {st.session_state.placement_q}. Answer: {ans}. Determine CEFR Level (A2, B1, B2, C1, C2). Format: NIVEL: [Level]\nANALISIS: [Explanation]"
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
                <h2>Diagnóstico de Inteligencia Artificial Completado</h2>
                <h1 style="font-size: 4em; margin: 10px 0;">{st.session_state.english_level}</h1>
                <p>Perfil: {st.session_state.user_name} | {st.session_state.user_area}</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"<div class='executive-card'><h3>🔍 Reporte Analítico:</h3><p>{st.session_state.placement_eval}</p></div>", unsafe_allow_html=True)
        
        if st.button("Abrir el War Room (Dashboard) ⚔️"):
            st.session_state.screen = 'dashboard'
            st.rerun()

# ==========================================
# FASE 2: WAR ROOM (DASHBOARD CON PILARES)
# ==========================================
else:
    st.title(f"🛡️ Executive War Room: {st.session_state.user_name}")
    st.write("Tu ecosistema completo de entrenamiento táctico y vocabulario técnico.")
    
    tabs = st.tabs(["📅 Roadmap (Misión Diaria)", "🤖 AI Combat Lab", "⚔️ Power Verbs", "🔥 The Forge", "📖 Enciclopedia Técnica"])
    
    # --- TAB 1: ROADMAP ---
    with tabs[0]:
        st.subheader("Tu Plan de 30 Días")
        for plan in THIRTY_DAY_PLAN:
            is_active = "day-active" if plan['day'] == st.session_state.current_day else ""
            st.markdown(f"""
                <div class="day-card {is_active}">
                    <span style="color: #3b82f6; font-weight: 900;">DÍA {plan['day']} • {plan['phase']}</span>
                    <h3 style="margin-top: 5px; color: white;">{plan['title']}</h3>
                    <p style="color:#94a3b8; margin-bottom:0;"><b>Foco Operativo:</b> {plan['focus']}</p>
                </div>
            """, unsafe_allow_html=True)

    # --- TAB 2: AI COMBAT Lab ---
    with tabs[1]:
        current_mission = next((p for p in THIRTY_DAY_PLAN if p['day'] == st.session_state.current_day), THIRTY_DAY_PLAN[-1])
        st.subheader(f"Entrenamiento Táctico: Día {st.session_state.current_day}")
        st.write(f"**Tema:** {current_mission['title']} ({current_mission['focus']})")
        
        if st.button("🎙️ Generar Escenario Ejecutivo"):
            with st.spinner("La IA está adaptando el reto..."):
                prompt = f"You are a CEO interviewing an engineer ({st.session_state.user_area}) with {st.session_state.english_level} English. Training topic: {current_mission['focus']}. Ask ONE tough scenario question in English."
                st.session_state.daily_q = call_ai(prompt, active_key)
                
        if 'daily_q' in st.session_state:
            st.markdown(f"<div class='executive-card'><b>C-Level Executive:</b><br><br>\"{st.session_state.daily_q}\"</div>", unsafe_allow_html=True)
            user_ans = st.text_area("Tu Respuesta (en Inglés):", height=150)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⚖️ Evaluar y Corregir"):
                    if not user_ans: st.warning("Escribe una respuesta.")
                    else:
                        with st.spinner("Auditando..."):
                            eval_prompt = f"Evaluate this answer from a {st.session_state.user_area} engineer. Question: '{st.session_state.daily_q}'. Answer: '{user_ans}'. Provide in SPANISH: 1. Score (0-100), 2. Feedback, 3. The PERFECT Director-level script in English."
                            feedback = call_ai(eval_prompt, active_key)
                            st.markdown(f"<div class='level-box'><b>Reporte Táctico:</b><br>{feedback}</div>", unsafe_allow_html=True)
                            st.session_state.xp += 100
            with col2:
                if st.button("🔥 Completar Misión Diaria"):
                    st.session_state.current_day += 1
                    if 'daily_q' in st.session_state: del st.session_state.daily_q
                    st.rerun()

    # --- TAB 3: POWER VERBS (RESTAURADO) ---
    with tabs[2]:
        st.subheader("Combate de Reflejos: Power Verbs")
        st.write("Sustituye el inglés 'débil' por inglés de 'alto impacto'.")
        
        if st.button("Siguiente Drill 🔄"):
            st.session_state.current_drill = random.choice(POWER_VERBS_DRILLS)
            st.rerun()
            
        drill = st.session_state.current_drill
        st.markdown(f"<div class='executive-card' style='border-color:#f59e0b;'>Un Junior diría:<br><h3 style='margin:0;'>'{drill[0]}'</h3></div>", unsafe_allow_html=True)
        
        pv_ans = st.text_input("¿Cómo lo dice un Ejecutivo? (Escribe la frase):")
        if st.button("Neutralizar 🎯"):
            if drill[1].lower() in pv_ans.lower() or pv_ans.lower() in drill[1].lower():
                st.success(f"¡Correcto! +50 XP. La frase letal es: '{drill[1]}'")
                st.session_state.xp += 50
            else:
                st.error(f"Demasiado básico. La versión ejecutiva es: '{drill[1]}'")

    # --- TAB 4: THE FORGE (RESTAURADO) ---
    with tabs[3]:
        st.subheader("La Fragua de Logros (Método STAR)")
        st.write("Ingresa un logro básico y la IA lo redactará como un argumento de alto impacto para tu CV o entrevista.")
        
        draft = st.text_area("Ingresa tu logro (Español o Inglés):", placeholder="Ej: Reduje costos de empaque en $274k USD en Mercado Libre usando análisis de SQL.")
        
        if st.button("⚒️ Forjar a Nivel Director"):
            if not active_key: st.error("Falta API Key.")
            elif not draft: st.warning("Escribe un logro.")
            else:
                with st.spinner("Transformando experiencia en autoridad..."):
                    forge_prompt = f"Convert this basic achievement into a powerful, executive STAR-method paragraph in English. Focus on EBITDA impact, leadership verbs, and technical authority. Achievement: '{draft}'"
                    result = call_ai(forge_prompt, active_key)
                    st.markdown(f"<div class='executive-card'><b>Tu Nueva Historia de Éxito:</b><br>{result}</div>", unsafe_allow_html=True)

    # --- TAB 5: ENCICLOPEDIA (RESTAURADO) ---
    with tabs[4]:
        st.subheader("Pilar de Conocimiento: Enciclopedia Técnica")
        st.write("Terminología global que debes dominar según tu área.")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("<span class='badge-ops'>🏭 Ops & Quality</span>", unsafe_allow_html=True)
            st.write("- **EBITDA:** Beneficios antes de intereses, impuestos, depreciación y amortización.")
            st.write("- **Hard Savings:** Ahorros duros que impactan directamente el P&L (Estado de resultados).")
            st.write("- **IATF 16949:** Sistema de Gestión de Calidad Automotriz.")
            st.write("- **VDA 6.3:** Estándar Alemán de Auditoría de Procesos.")
        with c2:
            st.markdown("<span class='badge-tech'>🧬 Tech & Data</span>", unsafe_allow_html=True)
            st.write("- **SQL Query:** Consulta estructurada a bases de datos.")
            st.write("- **BigQuery:** Data Warehouse empresarial de Google.")
            st.write("- **Prompt Engineering:** Diseño estratégico de instrucciones para IA.")
            st.write("- **Predictive Modeling:** Análisis estadístico para prever fallos.")
        with c3:
            st.markdown("<span class='badge-compliance'>⚖️ Supply & Comp</span>", unsafe_allow_html=True)
            st.write("- **IRA:** Inventory Record Accuracy (Precisión de inventario).")
            st.write("- **S&OP:** Sales and Operations Planning.")
            st.write("- **NOM:** Normas Oficiales Mexicanas.")
            st.write("- **Countermeasure:** Acción de contención inmediata.")

