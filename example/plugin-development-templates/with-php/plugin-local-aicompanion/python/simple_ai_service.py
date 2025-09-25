#!/usr/bin/env python3
"""
AI Learning Companion - Simplified Service
Core AI functionality without complex dependencies
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
from dotenv import load_dotenv
try:
    import snowflake.connector
except Exception:
    snowflake = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load env from .env if present (safe no-op if absent)
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE', 'moodle_app')
SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA', 'public')
ENABLE_SNOWFLAKE_LOGGING = False  # disable to avoid connector errors/noise

class SimpleAILearningCompanion:
    """Simplified AI Learning Companion class"""
    
    def __init__(self):
        self.learning_patterns = {}
        self.snowflake_conn = None
    
    def _ensure_snowflake(self) -> bool:
        """Connect to Snowflake if credentials and connector are available."""
        if not ENABLE_SNOWFLAKE_LOGGING:
            return False
        try:
            if self.snowflake_conn:
                return True
            # Validate minimal configuration
            if not (SNOWFLAKE_ACCOUNT and SNOWFLAKE_USER and SNOWFLAKE_PASSWORD):
                return False
            # Connector may be unavailable
            if 'snowflake' not in globals() and 'snowflake' not in locals():
                return False
            # Establish connection
            self.snowflake_conn = snowflake.connector.connect(
                user=SNOWFLAKE_USER,
                password=SNOWFLAKE_PASSWORD,
                account=SNOWFLAKE_ACCOUNT,
                database=SNOWFLAKE_DATABASE,
                schema=SNOWFLAKE_SCHEMA
            )
            # Create table if not exists
            with self.snowflake_conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS CHAT_LOGS (
                        USER_ID INT,
                        ROLE STRING,
                        MESSAGE STRING,
                        TS TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                    )
                    """
                )
            logger.info("Snowflake connection established and CHAT_LOGS ensured")
            return True
        except Exception as e:
            logger.error(f"Snowflake init failed: {e}")
            self.snowflake_conn = None
            return False
    
    def _log_chat(self, user_id: int, role: str, message: str) -> None:
        """Best-effort insert of chat messages into Snowflake."""
        try:
            if not self._ensure_snowflake():
                return
            with self.snowflake_conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO CHAT_LOGS (USER_ID, ROLE, MESSAGE) VALUES (%s, %s, %s)",
                    (int(user_id), role, message[:4000])
                )
            self.snowflake_conn.commit()
        except Exception as e:
            logger.warning(f"Snowflake logging skipped: {e}")
        
    def get_ai_response(self, message: str, user_id: int, chat_history: List[Dict]) -> str:
        """Generate AI response using OpenAI"""
        try:
            # Prepare messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": self._get_system_prompt(user_id)
                }
            ]
            
            # Add recent chat history
            for msg in chat_history[-10:]:  # Last 10 messages
                messages.append({
                    "role": "user" if msg['sender'] == 'user' else "assistant",
                    "content": msg['message']
                })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Call Gemini API
            response = self._call_gemini_api(messages)
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again later."
    
    def _get_system_prompt(self, user_id: int) -> str:
        """Get personalized system prompt"""
        return """You are an AI Learning Companion designed to help students with their learning journey. 
        You are friendly, encouraging, and knowledgeable about educational topics. 
        Provide helpful, accurate, and personalized responses to help students learn effectively.
        
        Key guidelines:
        - Be encouraging and supportive
        - Provide clear, easy-to-understand explanations
        - Ask follow-up questions to understand the student's needs
        - Suggest practical learning strategies
        - Be patient and understanding
        - Focus on helping the student succeed"""
    
    def _call_gemini_api(self, messages: List[Dict]) -> str:
        """Call Google Gemini API"""
        if not GEMINI_API_KEY:
            return "I'm sorry, but the AI service is not properly configured. Please contact your administrator."
        
        try:
            # Convert messages to Gemini format
            # Get the last user message and system prompt
            user_message = ""
            system_prompt = ""
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_prompt = msg['content']
                elif msg['role'] == 'user':
                    user_message = msg['content']
            
            # Combine system prompt and user message
            full_prompt = f"{system_prompt}\n\nUser: {user_message}"
            
            # Use supported Gemini model and API version
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
            )
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": full_prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500
                }
            }
            
            # simple retry on rate limits
            for attempt in range(2):
                response = requests.post(url, json=data, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        return result['candidates'][0]['content']['parts'][0]['text']
                    else:
                        return "I'm sorry, I couldn't generate a proper response."
                # handle quota with brief backoff
                try:
                    err = response.json().get('error', {})
                    retry_secs = 0
                    for d in err.get('details', []) or []:
                        if isinstance(d, dict) and d.get('@type', '').endswith('RetryInfo'):
                            rs = d.get('retryDelay', '0s').rstrip('s')
                            retry_secs = int(float(rs)) if rs else 0
                    if retry_secs <= 0:
                        retry_secs = 3
                except Exception:
                    retry_secs = 3
                time.sleep(min(retry_secs, 5))
            logger.error(f"Gemini API error: {response.status_code} - {response.text}")
            return self._local_chat_response(user_message)
                
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return self._local_chat_response(user_message)

    def _call_gemini_json(self, prompt: str) -> Optional[dict]:
        """Call Gemini expecting JSON output. Returns parsed dict or None."""
        if not GEMINI_API_KEY:
            return None
        try:
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
            )
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 800,
                    "responseMimeType": "application/json"
                }
            }
            # simple retry on rate limits
            for attempt in range(2):
                resp = requests.post(url, json=data, timeout=40)
                if resp.status_code == 200:
                    result = resp.json()
                    text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                    if not text:
                        return None
                    return json.loads(text)
                try:
                    err = resp.json().get('error', {})
                    retry_secs = 0
                    for d in err.get('details', []) or []:
                        if isinstance(d, dict) and d.get('@type', '').endswith('RetryInfo'):
                            rs = d.get('retryDelay', '0s').rstrip('s')
                            retry_secs = int(float(rs)) if rs else 0
                    if retry_secs <= 0:
                        retry_secs = 3
                except Exception:
                    retry_secs = 3
                time.sleep(min(retry_secs, 5))
            logger.error(f"Gemini JSON error: {resp.status_code} - {resp.text}")
            return None
        except Exception as e:
            logger.error(f"Gemini JSON exception: {e}")
            return None

    def _local_chat_response(self, user_message: str) -> str:
        """Offline fallback: helpful answer when Gemini is rate-limited/unavailable."""
        msg = (user_message or '').lower().strip()
        if not msg:
            return "Hi! How can I help you learn today? Ask about any topic."
        if any(g in msg for g in ["hello", "hi", "hey"]):
            return "Hi! What topic are you studying? I can explain concepts or make a quick quiz."
        if "neural network" in msg or "perceptron" in msg:
            return (
                "Neural network: layers of simple units (neurons) that learn weights to map inputs to outputs.\n"
                "- Each layer does a linear transform + nonlinearity to model complex patterns.\n"
                "- Training: minimize loss with backpropagation and gradient descent.\n"
                "- Tiny example: pixels -> hidden -> output (cat vs dog).\n"
                "Want a 5-question quiz or a real-world example?"
            )
        if "machine learning" in msg:
            return (
                "Machine learning lets models learn from data instead of fixed rules.\n"
                "Types: Supervised (labels), Unsupervised (no labels), Reinforcement (rewards).\n"
                "Pipeline: collect/clean -> split -> train -> evaluate -> iterate."
            )
        if "linear regression" in msg:
            return (
                "Linear regression fits y = w·x + b to predict a number.\n"
                "Learn w,b by minimizing MSE; assess with R²/RMSE; watch outliers."
            )
        if ("sql" in msg) and ("join" in msg or "query" in msg):
            return (
                "SQL joins: INNER (match both), LEFT (all left + matches), RIGHT, FULL.\n"
                "Example: SELECT a.id,b.total FROM orders a INNER JOIN payments b ON a.id=b.order_id;"
            )
        topic = (user_message or 'this topic').strip().rstrip('?')
        return (
            f"Here’s a quick explainer on {topic}:\n"
            "- What it is: a concise definition in simple terms.\n"
            "- Why it matters: common real-world uses.\n"
            "- Try it: outline 3 steps to practice.\n"
            f"Say 'quiz on {topic}' for 5 quick questions or ask a follow-up."
        )

    # Removed Cortex integration per configuration: Gemini-only
    
    def generate_learning_recommendations(self, user_id: int) -> List[str]:
        """Generate personalized learning recommendations"""
        recommendations = [
            "Set specific, achievable learning goals for each study session",
            "Take regular breaks every 25-30 minutes to maintain focus",
            "Use active recall techniques like flashcards and practice quizzes",
            "Create a dedicated study space free from distractions",
            "Review and summarize what you've learned at the end of each session",
            "Connect new information to what you already know",
            "Teach someone else what you've learned to reinforce understanding",
            "Use different learning methods: reading, videos, hands-on practice",
            "Track your progress and celebrate small victories",
            "Ask questions when you don't understand something"
        ]
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def get_mock_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get mock analytics data for demonstration"""
        return {
            'completed_courses': 3,
            'total_study_time': 25.5,
            'average_quiz_score': 78.5,
            'study_days': 18,
            'avg_engagement': 0.75,
            'study_streak_days': 4,
            'strengths': [
                'Strong in problem-solving',
                'Excellent time management',
                'Good at visual learning'
            ],
            'improvements': [
                'Focus on practical applications',
                'Try different learning methods',
                'Increase study consistency'
            ],
            'mastery': [
                {'topic': 'Algebra', 'level': 72},
                {'topic': 'Data Structures', 'level': 64},
                {'topic': 'Statistics', 'level': 58}
            ]
        }

# Initialize AI companion
ai_companion = SimpleAILearningCompanion()
# In-memory quiz storage (simple, per-process)
last_quiz: Dict[str, Any] = { 'questions': [] }
# In-memory per-user metrics (simple demo store)
user_metrics: Dict[int, Dict[str, Any]] = {}

def _get_user_metrics(user_id: int) -> Dict[str, Any]:
    m = user_metrics.get(user_id)
    if not m:
        m = {'quiz_attempts': [], 'interview_feedback': []}
        user_metrics[user_id] = m
    return m

@app.route('/', methods=['GET'])
def home():
    """Simple dashboard: chat UI and analytics"""
    return (
        """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI Learning Companion</title>
  <style>
    :root{
      --bg: #0b1220;
      --bg2: #0f172a;
      --card: #111827;
      --border: #1f2937;
      --text: #e5e7eb;
      --muted: #9ca3af;
      --primary: #6366f1;
      --accent: #22d3ee;
      --you: #1f2937;
      --ai: #0b1220;
    }
    body { font-family: 'Segoe UI', Inter, Arial, sans-serif; margin: 0; background: radial-gradient(1200px 800px at 20% 0%, var(--bg2), var(--bg)); color: var(--text); }
    .container { max-width: 1100px; margin: 0 auto; padding: 28px 20px 60px; }
    .hero { display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding: 24px 0 10px; }
    .hero h1 { margin: 0; font-size: 36px; letter-spacing: 0.5px; }
    .hero .subtitle { margin-top: 8px; color: var(--muted); min-height: 22px; }
    .typewriter { border-right: 2px solid var(--accent); white-space: nowrap; overflow: hidden; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 16px; margin: 12px 0; box-shadow: 0 8px 24px rgba(0,0,0,.25); }
    .row { display: flex; gap: 16px; flex-wrap: wrap; }
    .col { flex: 1 1 320px; min-width: 280px; }
    textarea, input { width: 100%; box-sizing: border-box; padding: 12px; border-radius: 10px; border: 1px solid var(--border); background: #0b1220; color: var(--text); }
    button { padding: 10px 14px; border-radius: 10px; border: 0; background: var(--primary); color: #fff; cursor: pointer; box-shadow: 0 6px 16px rgba(99,102,241,.35); }
    button.secondary { background: #334155; }
    button:disabled { background: #6b7280; cursor: not-allowed; box-shadow:none; }
    .chat { height: 360px; overflow: auto; background: #0b1220; border: 1px solid var(--border); border-radius: 12px; padding: 12px; }
    .bubble { max-width: 78%; padding: 10px 12px; border-radius: 12px; margin: 10px 0; line-height: 1.35; word-wrap: break-word; box-shadow: 0 3px 10px rgba(0,0,0,.25); }
    .you { background: var(--you); margin-left: auto; border: 1px solid var(--border); }
    .ai { background: var(--ai); margin-right: auto; border: 1px solid var(--border); }
    .label { font-size: 11px; color: var(--muted); margin-bottom: 4px; }
    .badge { display: inline-block; background: #0b1220; color: #93c5fd; padding: 4px 8px; border-radius: 9999px; margin: 2px 6px 2px 0; font-size: 12px; border:1px solid var(--border); }
    .muted { color: var(--muted); font-size: 12px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="hero">
      <h1 id="title">AI Learning Companion</h1>
      <div id="subtitle" class="subtitle typewriter"></div>
    </div>

    <div class="row">
      <div class="col">
        <div class="card">
          <h3>Chat</h3>
          <div id="chat" class="chat"></div>
          <div style="margin-top:8px">
            <textarea id="message" rows="3" placeholder="Ask anything about your learning..."></textarea>
          </div>
          <div style="display:flex; gap:8px; margin-top:8px; flex-wrap:wrap">
            <input id="userid" type="number" value="1" min="1" style="max-width:140px"/>
            <button id="send">Send</button>
            <button id="clear" class="secondary">Clear</button>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col">
        <div class="card">
          <h3>Smart Quiz Generator</h3>
          <div class="row">
            <div class="col"><input id="quiz-topic" placeholder="Topic (e.g., Python, Algebra)"/></div>
            <div class="col"><input id="quiz-num" type="number" value="5" min="1" max="15"/></div>
            <div class="col"><button id="gen-quiz">Generate Quiz</button></div>
          </div>
          <div id="quiz-area" style="margin-top:8px"></div>
          <div style="margin-top:8px"><button id="grade-quiz" class="secondary">Grade</button></div>
        </div>
      </div>
      <div class="col">
        <div class="card">
          <h3>Interview Coach</h3>
          <div class="row">
            <div class="col">
              <textarea id="interview-q" rows="2" placeholder="Ask for a mock interview question (topic)..."></textarea>
              <button id="ask-interview">Ask</button>
            </div>
            <div class="col">
              <textarea id="interview-a" rows="3" placeholder="Paste/type your answer for feedback..."></textarea>
              <button id="coach-interview" class="secondary">Get Feedback</button>
            </div>
          </div>
          <div id="interview-out" style="margin-top:8px"></div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col">
        <div class="card">
          <h3>Analytics</h3>
          <div id="analytics"></div>
          <div id="analytics-insights" style="margin-top:8px"></div>
          <div style="margin-top:8px">
            <button id="refresh">Refresh Analytics</button>
          </div>
        </div>
      </div>
      <div class="col">
        <div class="card">
          <h3>Employability Bridge</h3>
          <div id="career"></div>
          <div style="margin-top:8px"><button id="refresh-career">Refresh</button></div>
        </div>
      </div>
    </div>
    
    <!-- Duplicate feature row removed -->
  </div>

  <script>
    // Typewriter effect
    (function(){
      const el = document.getElementById('subtitle');
      const text = 'Chat with AI and view your learning analytics';
      let i = 0;
      function tick(){
        if(!el) return;
        el.textContent = text.slice(0, i++);
        if(i <= text.length){ setTimeout(tick, 25); }
      }
      tick();
    })();
    const chatEl = document.getElementById('chat');
    const msgEl = document.getElementById('message');
    const userEl = document.getElementById('userid');
    const sendBtn = document.getElementById('send');
    const clearBtn = document.getElementById('clear');
    const analyticsEl = document.getElementById('analytics');
    const refreshBtn = document.getElementById('refresh');
    const analyticsInsightsEl = document.getElementById('analytics-insights');
    const quizTopicEl = document.getElementById('quiz-topic');
    const quizNumEl = document.getElementById('quiz-num');
    const genQuizBtn = document.getElementById('gen-quiz');
    const quizAreaEl = document.getElementById('quiz-area');
    const gradeQuizBtn = document.getElementById('grade-quiz');
    const careerEl = document.getElementById('career');
    const refreshCareerBtn = document.getElementById('refresh-career');
    const interviewQEl = document.getElementById('interview-q');
    const interviewAEl = document.getElementById('interview-a');
    const interviewOutEl = document.getElementById('interview-out');
    

    let history = [];

    function addMsg(role, text) {
      const wrap = document.createElement('div');
      const bubble = document.createElement('div');
      bubble.className = 'bubble ' + (role==='You' ? 'you' : (role==='Assistant' ? 'ai' : ''));
      const label = document.createElement('div');
      label.className = 'label';
      label.textContent = role;
      const content = document.createElement('div');
      content.innerHTML = String(text || '').replace(/</g,'&lt;');
      bubble.appendChild(label);
      bubble.appendChild(content);
      wrap.appendChild(bubble);
      chatEl.appendChild(wrap);
      chatEl.scrollTop = chatEl.scrollHeight;
    }

    async function send() {
      const text = msgEl.value.trim();
      if (!text) return;
      sendBtn.disabled = true;
      addMsg('You', text);
      history.push({ sender: 'user', message: text });
      msgEl.value = '';
      try {
        const res = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, user_id: Number(userEl.value)||1, chat_history: history })
        });
        const data = await res.json();
        const reply = data.response || data.error || 'No response';
        addMsg('Assistant', reply);
        history.push({ sender: 'assistant', message: reply });
      } catch (e) {
        addMsg('System', 'Failed to reach server');
      } finally {
        sendBtn.disabled = false;
      }
    }

    async function refreshDerivedInsights(){
      if (!analyticsInsightsEl) return;
      analyticsInsightsEl.textContent = 'Loading insights...';
      try {
        const res = await fetch(`/analytics/insights/${Number(userEl.value)||1}`);
        const data = await res.json();
        if (data && data.insights){
          const q = data.insights.quiz||{};
          const i = data.insights.interview||{};
          const attempts = (q.attempts||[]).map(a=>`<span class='badge'>${a.score}/${a.total}</span>`).join('');
          const tones = Object.entries(i.tones||{}).map(([k,v])=>`<span class='badge'>${k}: ${v}</span>`).join('');
          analyticsInsightsEl.innerHTML = `
            <div style='margin-top:8px'><strong>Smart Quiz</strong> — Avg Score: ${q.avg_score_pct||0}% | Attempts: ${attempts||'—'}</div>
            <div style='margin-top:8px'><strong>Interview Coach</strong> — Clarity: ${i.avg_clarity||0}/10 | Structure: ${i.avg_structure||0}/10 | Tones: ${tones||'—'}</div>
            <div style='margin-top:8px'><strong>AI Summary</strong>: ${(data.ai_summary||'').toString().replace(/</g,'&lt;')}</div>
          `;
        } else { analyticsInsightsEl.textContent = 'No derived insights yet. Try a quiz or interview first.'; }
      } catch { analyticsInsightsEl.textContent = 'Failed to load insights'; }
    }

    async function refreshAnalytics() {
      analyticsEl.textContent = 'Loading...';
      try {
        const res = await fetch(`/analytics/insights/${Number(userEl.value)||1}`);
        const data = await res.json();
        analyticsEl.innerHTML = '';
        if (data && data.insights) {
          const q = data.insights.quiz||{};
          const i = data.insights.interview||{};
          analyticsEl.innerHTML = `
            <div><strong>Average quiz score</strong>: ${q.avg_score_pct||0}%</div>
            <div><strong>Quiz attempts</strong>: ${(q.attempts||[]).length}</div>
            <div><strong>Interview clarity</strong>: ${i.avg_clarity||0}/10</div>
            <div><strong>Interview structure</strong>: ${i.avg_structure||0}/10</div>
          `;
        } else {
          analyticsEl.textContent = 'No analytics yet. Try a quiz and interview.';
        }
      } catch (e) {
        analyticsEl.textContent = 'Failed to load analytics';
      }
    }

    // Quizzes
    if (genQuizBtn) genQuizBtn.addEventListener('click', async () => {
      quizAreaEl.textContent = 'Generating...';
      try {
        const res = await fetch('/quiz/generate', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ topic: quizTopicEl.value||'General', num_questions: Number(quizNumEl.value)||5 }) });
        const data = await res.json();
        if (data && data.questions) {
          quizAreaEl.innerHTML = data.questions.map((q,i)=>{
            const opts = (q.options||[]).map((o,j)=>`<div><label><input type='radio' name='q${i}' value='${j}'/> ${o.replace(/</g,'&lt;')}</label></div>`).join('');
            return `<div class='card'><div><strong>Q${i+1}:</strong> ${q.question.replace(/</g,'&lt;')}</div>${opts}</div>`;
          }).join('');
        } else {
          quizAreaEl.textContent = 'Failed to generate quiz';
        }
      } catch { quizAreaEl.textContent = 'Failed to generate quiz'; }
    });

    if (gradeQuizBtn) gradeQuizBtn.addEventListener('click', async () => {
      try {
        const answers = [];
        (quizAreaEl.querySelectorAll('.card')||[]).forEach((card, i)=>{
          const sel = card.querySelector(`input[name='q${i}']:checked`);
          answers.push({ index:i, choice: sel?Number(sel.value):-1 });
        });
        const res = await fetch('/quiz/grade', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ answers }) });
        const data = await res.json();
        quizAreaEl.innerHTML += `<div class='card'><strong>Score:</strong> ${data.score}/${data.total} <div>${(data.feedback||[]).map(f=>`<div class='badge'>${f.replace(/</g,'&lt;')}</div>`).join('')}</div></div>`;
      } catch { quizAreaEl.innerHTML += `<div class='card'>Failed to grade.</div>`; }
    });

    // Career
    async function refreshCareer(){
      if (!careerEl) return;
      careerEl.textContent = 'Loading...';
      try {
        const res = await fetch(`/career/${Number(userEl.value)||1}`);
        const data = await res.json();
        if (data && data.recommendations) {
          const r = data.recommendations;
          careerEl.innerHTML = `
            <div><strong>Roles:</strong> ${(r.roles||[]).map(x=>`<span class='badge'>${x}</span>`).join('')}</div>
            <div style='margin-top:8px'><strong>Skills to build:</strong> ${(r.skills||[]).map(x=>`<span class='badge'>${x}</span>`).join('')}</div>
            <div style='margin-top:8px'><strong>Internships:</strong> ${(r.internships||[]).map(x=>`<div class='badge'>${x}</div>`).join('')}</div>
            <div style='margin-top:8px'><strong>Resume tips:</strong> ${(r.resume_tips||[]).map(x=>`<div class='badge'>${x}</div>`).join('')}</div>
          `;
        } else { careerEl.textContent = 'No data'; }
      } catch { careerEl.textContent = 'Failed to load'; }
    }
    if (refreshCareerBtn) refreshCareerBtn.addEventListener('click', refreshCareer);

    // Interview
    const askBtn = document.getElementById('ask-interview');
    const coachBtn = document.getElementById('coach-interview');
    if (askBtn) askBtn.addEventListener('click', async ()=>{
      if (!interviewOutEl) return;
      interviewOutEl.textContent = 'Loading...';
      try {
        const res = await fetch('/interview/ask', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ topic: interviewQEl.value||'general' }) });
        const data = await res.json();
        interviewOutEl.textContent = data.question || data.error || 'No question';
      } catch { interviewOutEl.textContent = 'Failed'; }
    });
    if (coachBtn) coachBtn.addEventListener('click', async ()=>{
      if (!interviewOutEl) return;
      interviewOutEl.textContent = 'Evaluating...';
      try {
        const res = await fetch('/interview/coach', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ answer: interviewAEl.value||'' }) });
        const data = await res.json();
        const fb = data && data.feedback;
        if (!fb) {
          interviewOutEl.textContent = 'No feedback';
          return;
        }
        if (typeof fb === 'string') {
          interviewOutEl.innerHTML = `<div><strong>Feedback:</strong> ${fb.replace(/</g,'&lt;')}</div>`;
        } else {
          const recs = (fb.recommendations||[]).map(r=>`<li>${String(r).replace(/</g,'&lt;')}</li>`).join('');
          interviewOutEl.innerHTML = `
            <div class='card'>
              <div style='margin-bottom:6px'><strong>Summary:</strong> ${String(fb.summary||'').replace(/</g,'&lt;')}</div>
              <div style='margin-bottom:6px'><strong>Tone:</strong> ${String(fb.tone||'').replace(/</g,'&lt;')}</div>
              <div style='margin-bottom:6px'><strong>Clarity:</strong> ${Number(fb.clarity)||'-'} / 10</div>
              <div style='margin-bottom:6px'><strong>Structure:</strong> ${Number(fb.structure)||'-'} / 10</div>
              <div><strong>Recommendations:</strong><ul>${recs}</ul></div>
            </div>
          `;
        }
      } catch { interviewOutEl.textContent = 'Failed'; }
    });

    sendBtn.addEventListener('click', send);
    clearBtn.addEventListener('click', () => { chatEl.innerHTML=''; history = []; });
    refreshBtn.addEventListener('click', ()=>{ refreshAnalytics(); refreshDerivedInsights(); });
    refreshCareer();
  </script>
</body>
</html>
        """,
        200,
        {"Content-Type": "text/html; charset=utf-8"}
    )

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'AI Learning Companion - Simplified'
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 1)
        chat_history = data.get('chat_history', [])
        
        if not message:
            return jsonify({'error': 'Missing message parameter'}), 400
        
        # Generate AI response
        response = ai_companion.get_ai_response(message, user_id, chat_history)
        # Best-effort Snowflake logging (user and assistant message)
        try:
            ai_companion._log_chat(user_id, 'user', message)
            ai_companion._log_chat(user_id, 'assistant', response)
        except Exception as _:
            pass
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/analytics/<int:user_id>', methods=['GET'])
def get_analytics(user_id):
    """Get user analytics"""
    try:
        analytics = ai_companion.get_mock_analytics(user_id)
        recommendations = ai_companion.generate_learning_recommendations(user_id)
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in analytics endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/analytics/advanced/<int:user_id>', methods=['GET'])
def get_advanced_analytics(user_id):
    """Advanced analytics with mastery and streak"""
    try:
        analytics = ai_companion.get_mock_analytics(user_id)
        recommendations = ai_companion.generate_learning_recommendations(user_id)
        return jsonify({
            'success': True,
            'analytics': analytics,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in advanced analytics endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/quiz/generate', methods=['POST'])
def quiz_generate():
    """Generate a multiple-choice quiz from a topic using Gemini if available"""
    try:
        data = request.get_json() or {}
        topic = (data.get('topic') or 'General').strip()
        num = int(data.get('num_questions') or 5)
        num = max(1, min(num, 15))
        questions = []
        # Use Gemini JSON
        prompt = (
            "You are a quiz generator. Return JSON with field 'questions' which is an array of objects, each object has: "
            "question (string), options (array of 4 strings), correct_index (0-3). "
            f"Create {num} fair, diverse MCQs for topic: {topic}."
        )
        ai_json = ai_companion._call_gemini_json(prompt)
        if ai_json and isinstance(ai_json.get('questions'), list):
            # Basic validation
            for q in ai_json['questions'][:num]:
                if isinstance(q.get('options'), list) and len(q['options']) == 4 and isinstance(q.get('correct_index'), int):
                    questions.append({
                        'question': str(q.get('question', '')),
                        'options': [str(o) for o in q['options']],
                        'correct_index': int(q['correct_index']) % 4
                    })
        # Fallback to static if AI failed
        if not questions:
            for i in range(num):
                q = {
                    'question': f"[{topic}] Question {i+1}: Select the best answer.",
                    'options': [
                        f"{topic} concept A",
                        f"{topic} concept B",
                        f"{topic} concept C",
                        f"{topic} concept D"
                    ],
                    'correct_index': i % 4
                }
                questions.append(q)
        last_quiz['questions'] = questions
        return jsonify({'success': True, 'topic': topic, 'questions': questions})
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/quiz/grade', methods=['POST'])
def quiz_grade():
    """Grade a quiz using last generated questions"""
    try:
        data = request.get_json() or {}
        answers = data.get('answers') or []
        questions = last_quiz.get('questions') or []
        score = 0
        feedback: List[str] = []
        for ans in answers:
            idx = int(ans.get('index', -1))
            choice = int(ans.get('choice', -1))
            if 0 <= idx < len(questions):
                correct = questions[idx].get('correct_index', -1)
                if choice == correct:
                    score += 1
                else:
                    feedback.append(f"Q{idx+1}: Consider reviewing {questions[idx]['options'][correct]}")
        # Log attempt
        try:
            u = _get_user_metrics(int(request.args.get('user_id') or 1))
            u['quiz_attempts'].append({
                'score': score,
                'total': len(questions),
                'timestamp': datetime.now().isoformat()
            })
        except Exception:
            pass
        return jsonify({'success': True, 'score': score, 'total': len(questions), 'feedback': feedback})
    except Exception as e:
        logger.error(f"Error grading quiz: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/career/<int:user_id>', methods=['GET'])
def career_recommendations(user_id):
    """Employability recommendations (AI-powered, uses quiz/interview insights)"""
    try:
        insights = _aggregate_insights(user_id)
        # Ask Gemini to tailor roles/skills/internships/tips to this user's metrics
        ai_data = None
        if GEMINI_API_KEY:
            schema = (
                "Return JSON with keys: roles (array of 3 strings), skills (array of 4 strings), "
                "internships (array of 2 strings), resume_tips (array of 3 short strings), summary (string<=60 words)."
            )
            prompt = (
                f"You are a career coach. {schema} Consider this learner's metrics: "
                f"quiz_avg={insights.get('quiz',{}).get('avg_score_pct',0)}%, "
                f"quiz_attempts={len(insights.get('quiz',{}).get('attempts',[]))}, "
                f"interview_clarity={insights.get('interview',{}).get('avg_clarity',0)}/10, "
                f"interview_structure={insights.get('interview',{}).get('avg_structure',0)}/10, "
                f"tones={insights.get('interview',{}).get('tones',{})}. "
                "Suggest realistic roles and internships based on strengths and gaps. Keep text concise."
            )
            ai_data = ai_companion._call_gemini_json(prompt)
        if not ai_data or not isinstance(ai_data, dict):
            # Fallback heuristics
            quiz_avg = insights.get('quiz',{}).get('avg_score_pct',0)
            roles = ['Data Analyst','Business Analyst','Junior ML Engineer'] if quiz_avg>=60 else ['Learning Associate','Data Intern','IT Support Intern']
            skills = ['Python','SQL','Version Control','Communication'] if quiz_avg>=60 else ['Study Skills','Problem Solving','Python Basics','Excel']
            internships = ['Analytics Intern @ FinTech Co','Data Ops Intern @ Retail Corp']
            tips = ['Quantify outcomes on resume','Map projects to job skills','Highlight continuous learning']
            ai_data = {'roles': roles,'skills': skills,'internships': internships,'resume_tips': tips,'summary': 'Focus on core skills and showcase projects aligned to roles.'}
        return jsonify({'success': True, 'recommendations': ai_data})
    except Exception as e:
        logger.error(f"Error in career endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/interview/ask', methods=['POST'])
def interview_ask():
    """Return a mock interview question for a topic"""
    try:
        data = request.get_json() or {}
        topic = (data.get('topic') or 'general').lower()
        question = (
            f"{topic.title()} interview: Explain a key concept and provide a real-world example."
            if topic != 'hr' else
            "HR interview: Tell me about a time you overcame a challenge."
        )
        return jsonify({'success': True, 'question': question})
    except Exception as e:
        logger.error(f"Error in interview ask: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/interview/coach', methods=['POST'])
def interview_coach():
    """Provide feedback on an answer; use Gemini if configured (concise, actionable)"""
    try:
        data = request.get_json() or {}
        answer = (data.get('answer') or '').strip()
        # Try Gemini JSON with rubric
        if GEMINI_API_KEY and len(answer) > 0:
            rubric = (
                "Return JSON with keys: summary (string, <=60 words), "
                "tone (string), clarity (1-10), structure (1-10), recommendations (array of 3 short strings)."
            )
            prompt = (
                f"You are an interview coach. {rubric} Analyze this answer and be supportive, specific.\nAnswer: "
                f"""{answer}"""
            )
            j = ai_companion._call_gemini_json(prompt)
            if j:
                # Log feedback
                try:
                    u = _get_user_metrics(int(request.args.get('user_id') or 1))
                    u['interview_feedback'].append({
                        'clarity': j.get('clarity'),
                        'structure': j.get('structure'),
                        'tone': j.get('tone'),
                        'timestamp': datetime.now().isoformat()
                    })
                except Exception:
                    pass
                return jsonify({'success': True, 'feedback': j})
        # Fallback heuristic
        feedback = {
            'summary': 'Good attempt. Add a concrete example and measurable impact.',
            'tone': 'neutral',
            'clarity': 6,
            'structure': 6,
            'recommendations': [
                'Use STAR format (Situation, Task, Action, Result).',
                'Replace filler words with confident phrasing.',
                'Add metrics (e.g., reduced time by 20%).'
            ]
        }
        try:
            u = _get_user_metrics(int(request.args.get('user_id') or 1))
            u['interview_feedback'].append({
                'clarity': feedback['clarity'],
                'structure': feedback['structure'],
                'tone': feedback['tone'],
                'timestamp': datetime.now().isoformat()
            })
        except Exception:
            pass
        return jsonify({'success': True, 'feedback': feedback})
    except Exception as e:
        logger.error(f"Error in interview coach: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def _aggregate_insights(user_id: int) -> Dict[str, Any]:
    m = _get_user_metrics(user_id)
    quiz = m.get('quiz_attempts', [])
    iv = m.get('interview_feedback', [])
    quiz_avg = (sum(a.get('score', 0) for a in quiz) / max(1, sum(a.get('total', 0) for a in quiz)) * 100.0) if quiz else 0.0
    iv_clarity = (sum((a.get('clarity') or 0) for a in iv) / max(1, len(iv))) if iv else 0.0
    iv_structure = (sum((a.get('structure') or 0) for a in iv) / max(1, len(iv))) if iv else 0.0
    tones = {}
    for a in iv:
        t = (a.get('tone') or '').lower()
        if t:
            tones[t] = tones.get(t, 0) + 1
    return {
        'quiz': {
            'attempts': quiz[-10:],
            'avg_score_pct': round(quiz_avg, 1)
        },
        'interview': {
            'avg_clarity': round(iv_clarity, 1),
            'avg_structure': round(iv_structure, 1),
            'tones': tones
        }
    }

def _ai_summary_for_insights(user_id: int, insights: Dict[str, Any]) -> Optional[str]:
    try:
        q = insights.get('quiz', {})
        i = insights.get('interview', {})
        prompt = (
            "You are an analytics coach. Given quiz and interview metrics, write a concise 4-6 line summary "
            "with strengths and top 3 improvement suggestions.\n" 
            f"Quiz avg score: {q.get('avg_score_pct')}%. Attempts: {len(q.get('attempts', []))}.\n"
            f"Interview clarity avg: {i.get('avg_clarity')}, structure avg: {i.get('avg_structure')}, tones: {i.get('tones')}\n"
            "Focus on actionable advice and encouragement."
        )
        # Gemini JSON summary
        j = ai_companion._call_gemini_json(prompt)
        if j and isinstance(j, dict) and j.get('summary'):
            return str(j.get('summary'))
        # fallback: plain text
        t = ai_companion._call_gemini_api([
            {'role':'system','content':'You are a helpful analytics coach.'},
            {'role':'user','content': prompt}
        ])
        return t
    except Exception:
        return None

@app.route('/analytics/insights/<int:user_id>', methods=['GET'])
def analytics_insights(user_id):
    """Return aggregated analytics derived from Smart Quiz and Interview Coach, plus AI summary."""
    try:
        insights = _aggregate_insights(user_id)
        summary = _ai_summary_for_insights(user_id, insights) if GEMINI_API_KEY else None
        return jsonify({'success': True, 'insights': insights, 'ai_summary': summary})
    except Exception as e:
        logger.error(f"Error in analytics insights endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Get personalized learning recommendations"""
    try:
        recommendations = ai_companion.generate_learning_recommendations(user_id)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in recommendations endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify service is running"""
    return jsonify({
        'message': 'AI Learning Companion service is running!',
        'timestamp': datetime.now().isoformat(),
        'endpoints': [
            'GET /health - Health check',
            'POST /chat - Chat with AI',
            'GET /analytics/<user_id> - Get analytics',
            'GET /recommendations/<user_id> - Get recommendations',
            'GET /test - This test endpoint'
        ]
    })

@app.route('/sf/health', methods=['GET'])
def snowflake_health():
    """Check Snowflake connectivity and return count of chat logs (if available)"""
    try:
        ok = ai_companion._ensure_snowflake()
        if not ok:
            return jsonify({
                'snowflake': 'disabled or not configured',
                'configured': bool(SNOWFLAKE_ACCOUNT and SNOWFLAKE_USER and SNOWFLAKE_PASSWORD)
            })
        out = {'snowflake': 'connected'}
        with ai_companion.snowflake_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM CHAT_LOGS")
            (cnt,) = cur.fetchone()
            out['chat_logs'] = int(cnt)
        return jsonify(out)
    except Exception as e:
        logger.error(f"Snowflake health error: {e}")
        return jsonify({'snowflake': 'error', 'detail': str(e)}), 500

if __name__ == '__main__':
    # Start the Flask app
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 Starting AI Learning Companion service on port {port}")
    print(f"📝 Gemini API Key configured: {'✅ Yes' if bool(GEMINI_API_KEY) else '❌ No'}")
    print(f"🌐 Service will be available at: http://localhost:{port}")
    print(f"🔍 Test endpoint: http://localhost:{port}/test")
    app.run(host='0.0.0.0', port=port, debug=True)
