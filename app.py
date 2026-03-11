import streamlit as st
import requests
import json
import time
import random
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="AI War Room v11.0 - Fernando Montes",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- API CONFIG (Gemini 2.5 Flash) ---
apiKey = "" 
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"

def call_ai(prompt, system_instruction):
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }
    for delay in [1, 2, 4]:
        try:
            response = requests.post(API_URL, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            time.sleep(delay)
    return "The AI Coach is momentarily offline. Please click the button again."

# --- ESTILOS PREMIUM E INTERFAZ INTUITIVA ---
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button {
        width: 100%; border-radius: 10px; height: 3em; 
        background-color: #1e293b; border: 1px solid #3b82f6;
        color: white; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #3b82f6; border: none; transform: translateY(-2px); }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #1e293b; padding: 12px; border-radius: 15px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #334155; border-radius: 8px; 
        padding: 10px 20px; font-weight: bold; color: #cbd5e1; border: none;
    }
    .stTabs [aria-selected="true"] { background-color: #3b82f6 !important; color: white !important; }
    .day-card {
        padding: 15px; border-radius: 12px; text-align: center; font-size: 0.85em;
        border: 2px solid #334155; transition: 0.3s; margin-bottom: 10px;
    }
    .day-current { background-color: #1e40af; border-color: #3b82f6; box-shadow: 0 0 20px #3b82f6; }
    .day-done { background-color: #065f46; border-color: #10b981; opacity: 0.8; }
    .executive-card {
        background: #1e293b; padding: 25px; border-radius: 15px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.4); border-left: 8px solid #3b82f6;
    }
    .guide-box {
        background: #1e3a8a; padding: 15px; border-radius: 10px;
        border-left: 5px solid #60a5fa; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PLAN MAESTRO ---
THIRTY_DAY_PLAN = {
    1: "Executive Pitch & Value Proposition",
    2: "EBITDA, Hard Savings & Financial Reporting",
    3: "IATF 16949: Risk-Based Thinking & Core Tools",
    4: "VDA 6.3: Process Maturity & German Standards",
    5: "SQL & Big Data: Strategic Data Extraction",
    6: "Logistics: S&OP, IRA & Supply Chain Resilience",
    7: "AI & Prompt Engineering for Operations",
    8: "Root Cause Analysis (8D) & Predictive Modeling",
    9: "OEM Negotiations & Stakeholder Management",
    10: "Strategic Cost Reduction (OpEx vs CapEx)"
}

# --- INITIALIZATION ---
if 'current_day' not in st.session_state: st.session_state.current_day = 1
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'show_guide' not in st.session_state: st.session_state.show_guide = True

# --- SIDEBAR ---
with st.sidebar:
    st.title("🦅 Mission Control")
    st.write(f"**Leader:** Fernando Montes")
    st.divider()
    st.metric("Sprint Progress", f"Day {st.session_state.current_day}/30")
    st.progress(st.session_state.current_day / 30)
    st.write(f"**Global XP:** {st.session_state.xp}")
    st.divider()
    
    if st.button("🏁 Completar Día y Avanzar"):
        st.session_state.current_day = min(st.session_state.current_day + 1, 30)
        st.session_state.xp += 100
        st.rerun()
        
    if st.button("⚙️ Reiniciar Todo el Plan"):
        st.session_state.current_day = 1
        st.session_state.xp = 0
        st.rerun()
    
    st.checkbox("Mostrar guías de ayuda", value=True, key="help_toggle")

# --- UI PRINCIPAL ---
st.title("🛡️ Executive AI War Room v11.0")
st.write("Ecosistema de inmersión táctica diseñado para el dominio del inglés técnico.")

if st.session_state.help_toggle:
    st.markdown("""
    <div class="guide-box">
        <b>💡 Guía Rápida:</b> Usa el <b>Roadmap</b> para ver tu plan mensual. En el <b>Combat Lab</b>, desafía a la IA para practicar respuestas reales. 
        En <b>The Forge</b>, pega tus logros y la IA los redactará a nivel Director.
    </div>
    """, unsafe_allow_html=True)

tabs = st.tabs(["📅 Tactical Roadmap", "🤖 AI Combat Lab", "🔥 The Forge (STAR)", "📚 Knowledge Base"])

# --- TAB 1: ROADMAP ---
with tabs[0]:
    st.subheader("Plan de Operaciones: 30 Días")
    cols = st.columns(7)
    for i in range(1, 15): # Mostramos los primeros 14 días para claridad
        with cols[(i-1)%7]:
            status = ""
            if i == st.session_state.current_day: status = "day-current"
            elif i < st.session_state.current_day: status = "day-done"
            
            st.markdown(f"""
                <div class="day-card {status}">
                    <b>DAY {i}</b><br>
                    <small>{THIRTY_DAY_PLAN.get(i, "Advanced Ops")[:15]}...</small>
                </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    current_topic = THIRTY_DAY_PLAN.get(st.session_state.current_day, "Continuous Improvement")
    st.markdown(f"""
    <div class="executive-card">
        <h3 style="color:#60a5fa;">Misión de Hoy: {current_topic}</h3>
        <p>Tu objetivo es dominar la terminología de <b>{current_topic}</b> para sonar como un líder global.</p>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 2: AI COMBAT LAB ---
with tabs[1]:
    st.subheader("Entrenamiento de Alta Presión")
    st.write("Haz clic en el botón para que la IA genere un escenario basado en tu misión de hoy.")
    
    if st.button("🎯 Generar Desafío Técnico de Hoy"):
        with st.spinner("La IA está preparando el escenario..."):
            system_prompt = f"""You are a CEO interviewing Fernando. Today is Day {st.session_state.current_day}: {current_topic}.
            Ask one tough, direct technical question in English. Fernando must prove he is a Director-level leader."""
            st.session_state.active_challenge = call_ai("Ask me a tough question about today's topic.", system_prompt)
    
    if 'active_challenge' in st.session_state:
        st.markdown(f"<div class='executive-card'><b>Auditor/CEO:</b><br>{st.session_state.active_challenge}</div>", unsafe_allow_html=True)
        response = st.text_area("Tu Respuesta Ejecutiva (en Inglés):", placeholder="Type your answer here...", height=150)
        
        if st.button("🚀 Enviar Respuesta para Análisis"):
            if not response:
                st.warning("Escribe algo antes de enviar.")
            else:
                with st.spinner("Analizando tu autoridad lingüística..."):
                    critique_prompt = f"Analyze this response to: {st.session_state.active_challenge}. Response: {response}. Provide: 1. Score (0-100), 2. Correction, 3. The 'Director-level' way to say it."
                    feedback = call_ai(critique_prompt, "You are a CEO giving feedback.")
                    st.markdown(f"<div class='executive-card' style='border-left-color:#10b981;'><b>Feedback del Coach:</b><br>{feedback}</div>", unsafe_allow_html=True)
                    st.session_state.xp += 50

# --- TAB 3: THE FORGE ---
with tabs[2]:
    st.subheader("The Forge: Optimización de Logros")
    st.write("La IA reescribirá tus logros para que impacten en el EBITDA.")
    
    user_draft = st.text_area("Pega aquí un logro de tu CV (Español o Inglés):", placeholder="Ej: Ahorré $274k en cajas en Mercado Libre usando SQL.")
    
    if st.button("⚒️ Forjar a Nivel Director"):
        if not user_draft:
            st.warning("Ingresa un logro para forjar.")
        else:
            with st.spinner("Refinando el argumento..."):
                forge_prompt = "Convert this into a high-level executive STAR paragraph. Use verbs like 'Spearheaded', 'Orchestrated', 'Leveraged'. Focus on Hard Savings and EBITDA impact."
                forged_result = call_ai(user_draft, forge_prompt)
                st.markdown(f"<div class='executive-card'><b>Versión Letal:</b><br>{forged_result}</div>", unsafe_allow_html=True)

# --- TAB 4: ENCYCLOPEDIA ---
with tabs[3]:
    st.subheader("Base de Conocimiento Táctico")
    c1, c2 = st.columns(2)
    with c1:
        st.info("**Quality & Ops:** IATF 16949, VDA 6.3, PFMEA, Root Cause Analysis, 8D Reports.")
    with c2:
        st.info("**Data & Tech:** SQL Queries, BigQuery, Predictive Reliability, Prompt Engineering.")
    st.write("Utiliza estos términos en tus respuestas para aumentar tu XP.")

st.divider()
st.caption(f"Executive English Mastery Suite | v11.0 | Fernando Montes Delgado | Session: {datetime.now().strftime('%Y-%m-%d')}")

