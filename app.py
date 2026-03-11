import streamlit as st
import requests
import json
import time
import random
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Executive English AI Coach - Fernando Montes",
    page_icon="🦅",
    layout="wide"
)

# --- API CONFIG (Gemini 2.5 Flash) ---
# La plataforma provee la llave automáticamente
apiKey = "" 
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"

def call_ai(prompt, system_instruction):
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }
    
    # Implementación de Exponential Backoff para robustez
    for delay in [1, 2, 4, 8, 16]:
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            time.sleep(delay)
    return "AI Coach busy. Please retry in a few seconds."

# --- ESTILOS PREMIUM (Modo Ejecutivo Dark) ---
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #1e293b; padding: 12px; border-radius: 15px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #334155; border-radius: 8px; 
        padding: 10px 20px; font-weight: bold; color: #cbd5e1; border: none;
    }
    .stTabs [aria-selected="true"] { background-color: #3b82f6 !important; color: white !important; }
    .day-card {
        padding: 15px; border-radius: 10px; text-align: center; font-size: 0.85em;
        border: 1px solid #334155; transition: 0.3s;
    }
    .day-current { background-color: #1e40af; border-color: #3b82f6; font-weight: bold; box-shadow: 0 0 15px #3b82f6; }
    .day-done { background-color: #065f46; opacity: 0.7; }
    .executive-card {
        background: #1e293b; padding: 30px; border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.4); border-left: 8px solid #3b82f6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PLAN MAESTRO DE 30 DÍAS ---
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
} # El sistema escala hasta el día 30 dinámicamente

# --- ESTADO DE SESIÓN ---
if 'current_day' not in st.session_state: st.session_state.current_day = 1
if 'xp' not in st.session_state: st.session_state.xp = 0

# --- SIDEBAR ESTRATÉGICO ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=70)
    st.title("AI Command Center")
    st.write(f"**Leader:** Fernando Montes")
    st.divider()
    st.metric("Operational Progress", f"Day {st.session_state.current_day}/30")
    st.progress(st.session_state.current_day / 30)
    st.write(f"Experience (XP): {st.session_state.xp}")
    st.divider()
    if st.button("Next Day ➡️"):
        st.session_state.current_day = min(st.session_state.current_day + 1, 30)
        st.rerun()
    if st.button("Reset Plan 🔄"):
        st.session_state.current_day = 1
        st.session_state.xp = 0
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.title("🦅 Executive AI War Room v10.0")
st.write("Tu ecosistema letal para el dominio del inglés técnico en 30 días.")

tabs = st.tabs(["📅 Tactical Roadmap", "🤖 AI Combat Lab", "🔥 The Forge (STAR)", "📊 Analytics"])

# --- TAB 1: ROADMAP ---
with tabs[0]:
    st.subheader("30-Day Execution Calendar")
    cols = st.columns(7)
    for i in range(1, 31):
        with cols[(i-1)%7]:
            status = ""
            if i == st.session_state.current_day: status = "day-current"
            elif i < st.session_state.current_day: status = "day-done"
            
            st.markdown(f"""
                <div class="day-card {status}">
                    <b>DAY {i}</b><br>
                    <small>{THIRTY_DAY_PLAN.get(i, "Leadership Mastery")[:18]}...</small>
                </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    topic = THIRTY_DAY_PLAN.get(st.session_state.current_day, "Continuous Improvement")
    st.markdown(f"""
    <div class="executive-card">
        <h3>Today's Mission: {topic}</h3>
        <p>Your objective today is to master the vocabulary and strategic responses for <b>{topic}</b>.</p>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 2: AI COMBAT LAB ---
with tabs[1]:
    st.subheader("High-Pressure AI Simulation")
    st.write("La IA generará un desafío técnico aleatorio basado en tu nivel y el día actual.")
    
    if st.button("Generate Technical Challenge"):
        with st.spinner("AI is crafting a scenario..."):
            system_instruction = f"""You are a world-class Executive Recruiter for a Tier 1 Automotive company. 
            Fernando is your candidate. He is a master in IATF, VDA 6.3, SQL, and Logistics.
            Today is Day {st.session_state.current_day} focused on {topic}.
            Generate a tough, technical interview question in English."""
            st.session_state.challenge = call_ai("Ask me a difficult question.", system_instruction)
    
    if 'challenge' in st.session_state:
        st.info(st.session_state.challenge)
        response = st.text_area("Your Executive Response (English):", height=120)
        if st.button("Submit Response"):
            with st.spinner("Analyzing..."):
                analysis_prompt = f"Analyze this response to the question: {st.session_state.challenge}. User response: {response}. Provide: 1. Score (0-100), 2. Correction of tone/grammar, 3. A 'Director-level' version of the same answer."
                feedback = call_ai(analysis_prompt, "You are a CEO providing feedback.")
                st.markdown(f"<div class='executive-card'><b>AI Feedback:</b><br>{feedback}</div>", unsafe_allow_html=True)
                st.session_state.xp += 50

# --- TAB 3: THE FORGE ---
with tabs[2]:
    st.subheader("Success Story Forge (AI Powered)")
    st.write("Ingresa tus logros en español o inglés básico y deja que la IA los convierta en argumentos letales.")
    raw_achievement = st.text_area("Achievement (Draft):", placeholder="Ej: Ahorré mucho dinero en empaque usando SQL...")
    
    if st.button("Forge to Director Level"):
        with st.spinner("Refining..."):
            forge_prompt = "Convert this draft into a powerful, executive-level STAR method paragraph using professional verbs like 'spearheaded', 'orchestrated', 'leveraged', and mention EBITDA/Hard Savings."
            result = call_ai(raw_achievement, forge_prompt)
            st.markdown(f"<div class='executive-card'><b>Forged Result:</b><br>{result}</div>", unsafe_allow_html=True)

# --- TAB 4: ANALYTICS ---
with tabs[3]:
    st.subheader("Performance Tracker")
    c1, c2 = st.columns(2)
    c1.metric("Total XP Earned", st.session_state.xp)
    c2.metric("Plan Progress", f"{int((st.session_state.current_day/30)*100)}%")
    st.divider()
    st.write("#### Skills Radar")
    st.info("Top Performer in: IATF Compliance | SQL Data Extraction | EBITDA Strategy")

st.divider()
st.caption("Executive English War Room | v10.0 AI-Omnibus | Build by AI for Fernando Montes")
