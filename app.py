import streamlit as st
import requests
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Global Engineering Onboarding", page_icon="🌍", layout="wide")

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
    
    /* Tarjetas y Contenedores */
    .hero-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
        padding: 40px; border-radius: 20px; text-align: center;
        border: 1px solid #3b82f6; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 30px;
    }
    .quiz-card {
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
    </style>
""", unsafe_allow_html=True)

# --- PLAN BASE DE 30 DÍAS (Se adapta al área del usuario) ---
THIRTY_DAY_PLAN = [
    {"day": 1, "phase": "Cimientos", "title": "El Pitch de Impacto (EBITDA / ROI)", "focus": "Cómo presentar tu valor financiero"},
    {"day": 2, "phase": "Defensa", "title": "Gestión de Crisis y Auditorías", "focus": "Terminología de contención y RCA"},
    {"day": 3, "phase": "Sistemas", "title": "Cultura de Calidad/Eficiencia", "focus": "Métricas, KPIs, y OKRs"},
    {"day": 4, "phase": "Tech Ops", "title": "Data Storytelling", "focus": "Explicar datos técnicos a no-técnicos"},
    {"day": 5, "phase": "Liderazgo", "title": "Stakeholder Management", "focus": "Negociación interdepartamental"},
    {"day": 6, "phase": "Futuro", "title": "Integración de IA en tu Área", "focus": "Prompting y optimización de procesos"},
    {"day": 7, "phase": "Boardroom", "title": "Presentación a Dirección General", "focus": "Estructuras ejecutivas de comunicación"},
]

# --- FUNCIONES DE IA ---
def call_ai(prompt, api_key):
    if not api_key: return "⚠️ Error: Ingresa tu API Key de Gemini en el panel lateral."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=15)
        return response.json()['candidates'][0]['content']['parts'][0]['text'] if response.status_code == 200 else "Error procesando la IA."
    except: return "Error de conexión con el servidor de Google."

# --- MANEJO DE ESTADO ---
if 'screen' not in st.session_state: st.session_state.screen = 'home'
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_area' not in st.session_state: st.session_state.user_area = ""
if 'english_level' not in st.session_state: st.session_state.english_level = "No Evaluado"
if 'current_day' not in st.session_state: st.session_state.current_day = 1
if 'xp' not in st.session_state: st.session_state.xp = 0

# --- MENÚ LATERAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 3em;'>⚙️</h1>", unsafe_allow_html=True)
    st.title("Centro de Comando")
    
    api_key = st.text_input("🔑 Gemini API Key:", type="password", help="Tu llave para acceder a la IA")
    
    if st.session_state.user_name:
        st.write(f"**Ingeniero:** {st.session_state.user_name}")
        st.write(f"**Área:** {st.session_state.user_area}")
        st.markdown(f"**Nivel Actual:** `<span style='color:#f59e0b; font-weight:bold;'>{st.session_state.english_level}</span>`", unsafe_allow_html=True)
        st.write(f"**Total XP:** {st.session_state.xp}")
        st.progress(st.session_state.current_day / 30)
    
    st.divider()
    if st.button("🏠 Inicio / Cambiar Perfil"):
        st.session_state.screen = 'home'
        st.rerun()
    if st.session_state.english_level != "No Evaluado":
        if st.button("📅 Ir al Plan de Entrenamiento"):
            st.session_state.screen = 'roadmap'
            st.rerun()

# --- PANTALLAS ---

# 1. HOME: CREACIÓN DE PERFIL
if st.session_state.screen == 'home':
    st.markdown("""
        <div class="hero-box">
            <h1 style="color: white; font-size: 3em; margin-bottom: 10px;">Global Engineering Onboarding</h1>
            <p style="color: #cbd5e1; font-size: 1.2em; max-width: 800px; margin: 20px auto;">
                Este sistema evalúa tu nivel técnico de inglés mediante IA y construye un plan de entrenamiento de 30 días para llevarte a nivel Dirección.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
        st.markdown("### 👤 Configura tu Perfil Táctico")
        name = st.text_input("Tu Nombre Completo:")
        area = st.selectbox("Tu Área de Especialidad Técnica:", ["Operaciones & Supply Chain", "Calidad & Lean Manufacturing", "Software & IT", "Data Science & Analytics", "Ingeniería de Producto", "Ventas Técnicas / Comercial", "Otra"])
        
        if st.button("Generar Examen de Colocación 🧠"):
            if not api_key:
                st.error("Por favor, ingresa tu API Key en el menú lateral izquierdo primero.")
            elif not name:
                st.error("Por favor ingresa tu nombre.")
            else:
                st.session_state.user_name = name
                st.session_state.user_area = area
                st.session_state.screen = 'placement_test'
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# 2. PLACEMENT TEST: EXAMEN DINÁMICO CON IA
elif st.session_state.screen == 'placement_test':
    st.title("🎯 Examen de Colocación (AI Assessment)")
    st.write("La IA ha generado una pregunta de entrevista ejecutiva basada en tu área. Responde en inglés con al menos 3 oraciones.")
    
    if 'placement_q' not in st.session_state:
        with st.spinner("Generando escenario técnico adaptado a tu perfil..."):
            prompt = f"You are a global recruiter. Ask ONE challenging, open-ended interview question in English for a {st.session_state.user_area} engineer. The question must require them to explain a complex technical concept or a difficult decision they made."
            st.session_state.placement_q = call_ai(prompt, api_key)
            st.rerun()
            
    st.markdown(f"<div class='quiz-card'><b>Global Recruiter:</b><br><br><i>\"{st.session_state.placement_q}\"</i></div>", unsafe_allow_html=True)
    
    user_placement_ans = st.text_area("Tu Respuesta (En Inglés):", height=200, placeholder="Type your detailed answer here. Don't worry about being perfect, just show your current level...")
    
    if st.button("Auditar mi Nivel de Inglés 🚀"):
        if len(user_placement_ans) < 20:
            st.warning("Tu respuesta es muy corta. Escribe al menos un par de oraciones para una evaluación precisa.")
        else:
            with st.spinner("La IA está analizando tu gramática, vocabulario técnico y estructura..."):
                eval_prompt = f"""
                Analyze this english response from a {st.session_state.user_area} engineer.
                Question: {st.session_state.placement_q}
                Answer: {user_placement_ans}
                
                Determine their CEFR English level (A2, B1, B2, C1, or C2).
                Format the exact response in SPANISH like this:
                NIVEL: [Only the level, e.g., B2]
                ANALISIS: [2 sentences explaining why]
                """
                result = call_ai(eval_prompt, api_key)
                st.session_state.placement_eval = result
                
                # Extraer el nivel rudimentariamente
                if "C2" in result: st.session_state.english_level = "C2 - Executive"
                elif "C1" in result: st.session_state.english_level = "C1 - Advanced"
                elif "B2" in result: st.session_state.english_level = "B2 - Upper Intermediate"
                elif "B1" in result: st.session_state.english_level = "B1 - Intermediate"
                else: st.session_state.english_level = "A2/B1 - Foundation"
                
                st.session_state.screen = 'placement_results'
                st.rerun()

# 3. RESULTADOS DEL EXAMEN
elif st.session_state.screen == 'placement_results':
    st.markdown(f"""
        <div class="level-box">
            <h2>Diagnóstico de Inteligencia Artificial Completado</h2>
            <h1 style="font-size: 4em; margin: 10px 0;">{st.session_state.english_level}</h1>
            <p>Perfil: {st.session_state.user_name} | {st.session_state.user_area}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div class='quiz-card'><h3>🔍 Reporte Analítico:</h3><p>{st.session_state.placement_eval}</p></div>", unsafe_allow_html=True)
    
    if st.button("Iniciar mi Entrenamiento de 30 Días ⚔️"):
        st.session_state.screen = 'roadmap'
        st.rerun()

# 4. ROADMAP DE ENTRENAMIENTO
elif st.session_state.screen == 'roadmap':
    st.title(f"📅 Plan Operativo para: {st.session_state.user_name}")
    st.write(f"**Área:** {st.session_state.user_area} | **Nivel Objetivo:** C1/C2 Executive")
    
    for plan in THIRTY_DAY_PLAN:
        is_active = "day-active" if plan['day'] == st.session_state.current_day else ""
        st.markdown(f"""
            <div class="day-card {is_active}">
                <span style="color: #3b82f6; font-weight: 900; letter-spacing: 1px;">DÍA {plan['day']} • {plan['phase']}</span>
                <h3 style="margin-top: 5px; color: white;">{plan['title']}</h3>
                <p style="color:#94a3b8; margin-bottom:0;"><b>Foco en {st.session_state.user_area}:</b> {plan['focus']}</p>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Entrar al AI Combat Lab (Reto de Hoy) 🤖"):
        st.session_state.screen = 'ai_lab'
        st.rerun()

# 5. AI COMBAT LAB (ADAPTADO AL NIVEL Y ÁREA)
elif st.session_state.screen == 'ai_lab':
    current_mission = next((p for p in THIRTY_DAY_PLAN if p['day'] == st.session_state.current_day), THIRTY_DAY_PLAN[-1])
    
    st.markdown(f"## 🤖 Entrenamiento Táctico: Día {st.session_state.current_day}")
    st.write(f"Tema: **{current_mission['title']}**")
    
    if st.button("🎙️ Generar Escenario Ejecutivo"):
        with st.spinner("La IA está adaptando el reto a tu nivel y área..."):
            prompt = f"""
            You are a CEO interviewing {st.session_state.user_name}, an engineer in {st.session_state.user_area}. 
            Their current English level is {st.session_state.english_level}.
            Today's training topic is: {current_mission['focus']}.
            Generate ONE tough, specific workplace scenario or interview question based on their area. 
            Keep it strictly in English.
            """
            st.session_state.daily_q = call_ai(prompt, api_key)
            
    if 'daily_q' in st.session_state:
        st.markdown(f"<div class='quiz-card'><b>C-Level Executive:</b><br><br>\"{st.session_state.daily_q}\"</div>", unsafe_allow_html=True)
        user_ans = st.text_area("Tu Respuesta Ejecutiva (en Inglés):", height=150)
        
        col_eval, col_adv = st.columns(2)
        with col_eval:
            if st.button("⚖️ Evaluar y Corregir"):
                if not user_ans:
                    st.warning("Escribe una respuesta para ser evaluado.")
                else:
                    with st.spinner("Auditando..."):
                        eval_prompt = f"""
                        Evaluate this answer from a {st.session_state.user_area} engineer with a {st.session_state.english_level} level.
                        Question: '{st.session_state.daily_q}'
                        Answer: '{user_ans}'
                        Provide in SPANISH: 1. A score (0-100), 2. Constructive feedback on grammar and vocabulary, 3. Provide the PERFECT, Director-level script they should have used in English.
                        """
                        feedback = call_ai(eval_prompt, api_key)
                        st.markdown(f"<div class='level-box' style='background-color:#064e3b;'><b>Reporte Táctico:</b><br>{feedback}</div>", unsafe_allow_html=True)
                        st.session_state.xp += 100
        with col_adv:
            if st.button("🔥 Completar Misión Diaria y Avanzar"):
                st.session_state.current_day += 1
                if 'daily_q' in st.session_state: del st.session_state.daily_q
                st.session_state.screen = 'roadmap'
                st.rerun()
