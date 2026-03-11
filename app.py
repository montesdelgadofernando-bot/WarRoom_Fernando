import React, { useState } from 'react';
import { 
  Play, CheckCircle2, XCircle, Briefcase, BookOpen, 
  ArrowRight, RotateCcw, Award, Target, Mic, 
  Calendar, Zap, TrendingUp, ShieldAlert, Lock
} from 'lucide-react';

// --- DATOS DEL EXAMEN (Diagnóstico) ---
const quizData = [
  {
    id: 1,
    question: "En una entrevista te piden hablar de tus logros financieros. ¿Cuál es la forma más ejecutiva de traducir: 'Logré ahorros de $274,000 anuales'?",
    options: [
      "I made $274,000 dollars in savings this year.",
      "I successfully delivered $274,000 USD in annual audited hard savings.",
      "I got $274,000 of saved money per year.",
      "My work saved $274,000 annually."
    ],
    correctIndex: 1,
    explanation: "'Successfully delivered' demuestra liderazgo accionable, y 'audited hard savings' es el término técnico exacto que un CFO o VP de Operaciones quiere escuchar."
  },
  {
    id: 2,
    question: "Durante una junta global, necesitas explicar que hubo un problema en el piso de producción, pero ya lo están resolviendo. ¿Qué frase proyecta más control?",
    options: [
      "We have a problem in the plant, but we are fixing it now.",
      "Things went wrong on the floor, but we are working on it.",
      "We experienced a line stoppage, but we are currently deploying a proactive countermeasure.",
      "The production stopped, but it will be okay soon."
    ],
    correctIndex: 2,
    explanation: "'Experienced a line stoppage' es vocabulario técnico. 'Deploying a proactive countermeasure' proyecta una mentalidad preventiva y de dominio operativo (8D/Lean)."
  },
  {
    id: 3,
    question: "El entrevistador de Novacard te hace una pregunta compleja sobre la integración de IA y no entiendes exactamente a qué se refiere. ¿Cómo ganas tiempo sin perder autoridad?",
    options: [
      "I'm sorry, I don't understand your question. Can you repeat?",
      "What do you mean by that? My English is not perfect.",
      "That's an insightful point. Could you please elaborate on the specific aspect of AI deployment you are referring to?",
      "Can you say that again but slower?"
    ],
    correctIndex: 2,
    explanation: "Nunca pidas perdón por no entender. 'Could you please elaborate...' te pone en una posición de diálogo de negocios de alto nivel, no de alumno a maestro."
  }
];

// --- EL PROGRAMA LETAL DE 30 DÍAS ---
const thirtyDayPlan = [
  {
    day: 1,
    phase: "Fase 1: Cimientos de Autoridad",
    title: "El Pitch del Millón de Dólares (EBITDA)",
    icon: <TrendingUp className="w-6 h-6 text-amber-500" />,
    mission: "Destruir el inglés 'Junior' y forjar tu introducción ejecutiva.",
    task: "Escribe tu presentación personal de 3 líneas enfocándote SOLO en cómo tu trabajo protege el EBITDA de la empresa. Prohibido usar la palabra 'help' o 'work'. Usa 'Spearhead', 'Orchestrate' o 'Optimize'.",
    action: "Grábate en el celular leyendo tu pitch 15 veces seguidas hasta que tu respiración sea fluida y no titubees en las cifras ($274k).",
    locked: false
  },
  {
    day: 7,
    phase: "Fase 1: Cimientos de Autoridad",
    title: "Defensa de Auditoría (IATF & VDA)",
    icon: <ShieldAlert className="w-6 h-6 text-emerald-500" />,
    mission: "Aprender a rebatir hallazgos de auditores alemanes y globales.",
    task: "Un auditor te dice: 'I see a gap in your FMEA updates'. Tu respuesta no puede ser 'I will fix it'. Tienes que responder usando: 'Containment actions', 'Risk-based thinking' y 'Process maturity'.",
    action: "Redacta un correo en inglés de 5 líneas respondiendo al auditor con el plan de acción (8D format).",
    locked: false
  },
  {
    day: 15,
    phase: "Fase 2: Dominio Técnico y Data",
    title: "SQL, BigQuery & Data Storytelling",
    icon: <Zap className="w-6 h-6 text-blue-500" />,
    mission: "Explicar sistemas complejos a directivos que no son técnicos.",
    task: "Explica cómo usaste consultas de SQL para lograr el 100% de IRA (Inventory Record Accuracy) en Mercado Libre.",
    action: "Frente al espejo, explica el proceso en voz alta durante 2 minutos ininterrumpidos usando conectores como: 'Furthermore', 'Consequently', 'By leveraging data sets...'.",
    locked: false
  },
  {
    day: 30,
    phase: "Fase 3: Nivel 'Boardroom' (Mesa Directiva)",
    title: "La Prueba de Fuego (CEO Interview)",
    icon: <Target className="w-6 h-6 text-rose-500" />,
    mission: "Simulación de estrés de alto nivel.",
    task: "Imagina que el CEO global te dice: 'Fernando, our OPEX is too high. What is your 90-day strategy to reduce scrap by 20% without impacting throughput?'",
    action: "Prepara una respuesta de 3 puntos (First..., Second..., Ultimately...). Debes incluir Prompts de IA, Core Tools y Estrategia Financiera. Graba la respuesta en video.",
    locked: true
  }
];

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('home'); 
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [selectedOption, setSelectedOption] = useState(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [activeDay, setActiveDay] = useState(null);

  // --- NAVEGACIÓN ---
  const startQuiz = () => {
    setCurrentScreen('quiz');
    setCurrentQuestionIndex(0);
    setScore(0);
    setSelectedOption(null);
    setShowExplanation(false);
  };

  const handleOptionSelect = (index) => {
    if (showExplanation) return; 
    setSelectedOption(index);
    setShowExplanation(true);
    if (index === quizData[currentQuestionIndex].correctIndex) {
      setScore(score + 1);
    }
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < quizData.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setSelectedOption(null);
      setShowExplanation(false);
    } else {
      setCurrentScreen('results');
    }
  };

  const goToTraining = () => setCurrentScreen('training');
  const goHome = () => setCurrentScreen('home');

  // --- RENDERIZADO DE PANTALLAS ---

  // 1. HOME: Psicología de Autoridad (Índigo oscuro) + Llamado a la acción (Ámbar)
  const renderHome = () => (
    <div className="flex flex-col items-center justify-center min-h-[600px] text-center p-8 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white rounded-2xl shadow-2xl border border-indigo-900/50 relative overflow-hidden">
      {/* Efecto de fondo sutil */}
      <div className="absolute top-0 left-0 w-full h-full bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] opacity-10 pointer-events-none"></div>
      
      <div className="z-10 flex flex-col items-center">
        <div className="bg-indigo-900/50 p-4 rounded-full mb-6 border border-indigo-500/30">
          <Briefcase className="w-16 h-16 text-amber-500" />
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold mb-4 tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-300">
          Executive Mastery Protocol
        </h1>
        <p className="text-xl text-amber-400 font-medium mb-4 tracking-wide">
          Fernando Montes | Target: C-Level & VP Roles
        </p>
        <p className="text-base text-slate-300 mb-10 max-w-lg leading-relaxed">
          Este no es un curso de inglés básico. Es un simulador de presión diseñado para transformar tu experiencia operativa en <b>autoridad lingüística corporativa</b> en 30 días.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-5 w-full max-w-md">
          <button 
            onClick={startQuiz}
            className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-900 px-6 py-4 rounded-xl font-bold text-lg transition-all duration-300 transform hover:-translate-y-1 hover:shadow-[0_0_20px_rgba(245,158,11,0.4)]"
          >
            <Play className="w-6 h-6" /> Iniciar Diagnóstico
          </button>
          <button 
            onClick={goToTraining}
            className="flex-1 flex items-center justify-center gap-2 bg-indigo-800/80 hover:bg-indigo-700 text-white border border-indigo-500/30 px-6 py-4 rounded-xl font-bold text-lg transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg"
          >
            <Calendar className="w-6 h-6" /> Plan 30 Días
          </button>
        </div>
      </div>
    </div>
  );

  // 2. QUIZ: Psicología de Foco (Blanco limpio, contrastes altos para corrección)
  const renderQuiz = () => {
    const currentQuestion = quizData[currentQuestionIndex];
    const isAnswered = showExplanation;

    return (
      <div className="min-h-[600px] p-8 bg-white rounded-2xl shadow-2xl flex flex-col border border-slate-100">
        <div className="flex justify-between items-center mb-8 pb-4 border-b border-slate-100">
          <span className="text-sm font-extrabold text-indigo-900 uppercase tracking-widest flex items-center gap-2">
            <Target className="w-5 h-5 text-amber-500"/> Escenario {currentQuestionIndex + 1} / {quizData.length}
          </span>
          <span className="bg-slate-900 text-amber-400 text-sm font-bold px-4 py-1.5 rounded-full shadow-inner">
            Score: {score}
          </span>
        </div>

        <h2 className="text-2xl font-bold text-slate-800 mb-8 leading-normal">
          {currentQuestion.question}
        </h2>

        <div className="space-y-4 flex-grow">
          {currentQuestion.options.map((option, index) => {
            let btnClass = "w-full text-left p-5 rounded-xl border-2 transition-all duration-200 font-semibold text-[1.05rem] ";
            
            if (!isAnswered) {
              btnClass += "border-slate-200 text-slate-600 hover:border-indigo-400 hover:bg-indigo-50 hover:text-indigo-900 shadow-sm hover:shadow-md";
            } else {
              if (index === currentQuestion.correctIndex) {
                btnClass += "border-emerald-500 bg-emerald-50 text-emerald-800 shadow-md transform scale-[1.02]"; 
              } else if (index === selectedOption) {
                btnClass += "border-rose-500 bg-rose-50 text-rose-800"; 
              } else {
                btnClass += "border-slate-100 text-slate-400 opacity-60"; 
              }
            }

            return (
              <button 
                key={index}
                onClick={() => handleOptionSelect(index)}
                disabled={isAnswered}
                className={btnClass}
              >
                <div className="flex justify-between items-center">
                  <span>{option}</span>
                  {isAnswered && index === currentQuestion.correctIndex && <CheckCircle2 className="w-6 h-6 text-emerald-500 flex-shrink-0 ml-3" />}
                  {isAnswered && index === selectedOption && index !== currentQuestion.correctIndex && <XCircle className="w-6 h-6 text-rose-500 flex-shrink-0 ml-3" />}
                </div>
              </button>
            );
          })}
        </div>

        {showExplanation && (
          <div className="mt-8 p-6 bg-indigo-50 border-l-4 border-indigo-600 rounded-r-xl shadow-sm animate-fade-in">
            <p className="text-base text-indigo-950">
              <span className="font-extrabold text-indigo-700 uppercase tracking-wider text-sm block mb-1">Análisis Estratégico</span>
              {currentQuestion.explanation}
            </p>
          </div>
        )}

        <div className="mt-8 flex justify-end">
          <button
            onClick={handleNextQuestion}
            disabled={!isAnswered}
            className={`flex items-center gap-2 px-8 py-4 rounded-xl font-bold text-lg transition-all duration-300 ${
              isAnswered 
                ? 'bg-slate-900 text-white hover:bg-indigo-900 hover:shadow-lg transform hover:-translate-y-1' 
                : 'bg-slate-100 text-slate-300 cursor-not-allowed'
            }`}
          >
            {currentQuestionIndex < quizData.length - 1 ? 'Siguiente Escenario' : 'Ver Diagnóstico'} 
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    );
  };

  // 3. RESULTS: Énfasis en la recompensa y el plan a seguir
  const renderResults = () => {
    const percentage = (score / quizData.length) * 100;
    
    return (
      <div className="min-h-[600px] flex flex-col items-center justify-center p-8 bg-gradient-to-b from-white to-slate-50 rounded-2xl shadow-2xl text-center border border-slate-200">
        <Award className={`w-28 h-28 mb-6 ${percentage >= 80 ? 'text-emerald-500 drop-shadow-lg' : 'text-amber-500 drop-shadow-md'}`} />
        <h2 className="text-3xl font-extrabold text-slate-900 mb-2">Diagnóstico Táctico Completado</h2>
        <p className={`text-6xl font-black mb-6 ${percentage >= 80 ? 'text-emerald-600' : 'text-indigo-600'}`}>
          {percentage}%
        </p>
        
        <div className="bg-slate-900 p-6 rounded-xl max-w-lg mb-10 shadow-lg text-left">
          <h3 className="text-amber-400 font-bold mb-2 uppercase tracking-wide text-sm">Veredicto del Sistema:</h3>
          <p className="text-slate-200 leading-relaxed text-sm">
            {percentage === 100 
              ? "Instinto corporativo impecable. Tienes el vocabulario. Ahora el reto de 30 días forzará tu fluidez verbal bajo presión extrema." 
              : "Detectamos mentalidad de alto nivel pero con 'fugas' en el vocabulario técnico en inglés. Un CFO o VP necesita precisión absoluta. El programa de 30 días cerrará esa brecha."}
          </p>
        </div>
        
        <div className="flex gap-4 w-full max-w-md">
          <button 
            onClick={goToTraining}
            className="flex-1 flex justify-center items-center gap-2 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-900 px-6 py-4 rounded-xl font-bold transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg"
          >
            <Zap className="w-5 h-5" /> Iniciar Reto 30 Días
          </button>
          <button 
            onClick={startQuiz}
            className="flex items-center gap-2 bg-slate-200 hover:bg-slate-300 text-slate-700 px-6 py-4 rounded-xl font-bold transition-all"
          >
            <RotateCcw className="w-5 h-5" />
          </button>
        </div>
      </div>
    );
  };

  // 4. THE 30-DAY FORGE (Psicología de Compromiso y Progreso)
  const renderTraining = () => (
    <div className="min-h-[600px] bg-slate-900 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
      {/* Header del Plan */}
      <div className="bg-indigo-950 p-6 border-b border-indigo-800/50 flex justify-between items-center sticky top-0 z-20">
        <div>
          <h2 className="text-2xl font-extrabold text-white flex items-center gap-2">
            <Calendar className="w-6 h-6 text-amber-500"/> El Plan de 30 Días
          </h2>
          <p className="text-indigo-300 text-sm mt-1">Sigue el protocolo. No te saltes días. Habla en voz alta.</p>
        </div>
        <button onClick={goHome} className="bg-slate-800 hover:bg-slate-700 text-white p-3 rounded-lg transition-colors border border-slate-600">
          <RotateCcw className="w-5 h-5" />
        </button>
      </div>

      {/* Contenido scrolleable */}
      <div className="p-6 overflow-y-auto flex-grow space-y-6 bg-gradient-to-b from-slate-900 to-slate-800">
        {thirtyDayPlan.map((day) => (
          <div 
            key={day.day} 
            className={`relative p-6 rounded-xl border-2 transition-all duration-300 ${
              day.locked 
                ? 'bg-slate-800/50 border-slate-700 opacity-75 grayscale' 
                : 'bg-white border-slate-200 hover:border-amber-400 hover:shadow-[0_8px_30px_rgba(245,158,11,0.15)] transform hover:-translate-y-1'
            }`}
          >
            {day.locked && (
              <div className="absolute top-4 right-4 text-slate-500 flex items-center gap-1 text-xs font-bold uppercase tracking-widest">
                <Lock className="w-4 h-4" /> Bloqueado
              </div>
            )}
            
            <div className="flex items-start gap-4 mb-4">
              <div className={`p-3 rounded-lg flex-shrink-0 ${day.locked ? 'bg-slate-700' : 'bg-slate-100'}`}>
                {day.icon}
              </div>
              <div>
                <span className={`text-xs font-black tracking-widest uppercase block mb-1 ${day.locked ? 'text-slate-500' : 'text-indigo-600'}`}>
                  Día {day.day} • {day.phase}
                </span>
                <h3 className={`text-xl font-bold ${day.locked ? 'text-slate-400' : 'text-slate-900'}`}>
                  {day.title}
                </h3>
              </div>
            </div>

            <div className={`space-y-4 ${day.locked ? 'text-slate-500' : 'text-slate-600'}`}>
              <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                <p className="text-sm"><strong>🎯 Misión:</strong> {day.mission}</p>
              </div>
              <p className="text-sm"><strong>📝 Ejercicio Escrito:</strong> {day.task}</p>
              
              <div className={`p-4 rounded-lg border-l-4 text-sm font-medium ${
                day.locked ? 'bg-slate-800 border-slate-600 text-slate-400' : 'bg-amber-50 border-amber-500 text-amber-900'
              }`}>
                <strong>🔥 Acción Requerida:</strong> {day.action}
              </div>
            </div>

            {!day.locked && (
              <button className="mt-5 w-full bg-slate-900 hover:bg-indigo-700 text-white font-bold py-3 rounded-lg transition-colors flex justify-center items-center gap-2">
                <Mic className="w-4 h-4"/> Iniciar Práctica de Hoy
              </button>
            )}
          </div>
        ))}
        
        <div className="text-center pt-4 pb-8">
          <p className="text-slate-500 text-sm font-medium">Completa las misiones diarias para desbloquear los siguientes niveles estratégicos.</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="w-full max-w-4xl mx-auto font-sans p-4">
      {currentScreen === 'home' && renderHome()}
      {currentScreen === 'quiz' && renderQuiz()}
      {currentScreen === 'results' && renderResults()}
      {currentScreen === 'training' && renderTraining()}
      
      {/* Estilos globales para animaciones */}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fadeIn 0.4s ease-out forwards;
        }
      `}} />
    </div>
  );
}
