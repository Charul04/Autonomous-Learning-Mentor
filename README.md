# Autonomous Learning Mentor

**Theme:** SDG 4 — Quality Education
**Type:** Autonomous Multi-Agent AI System (not a chatbot)

Autonomous Learning Mentor is a production-grade agentic AI application that plans, teaches,
evaluates, monitors, and adapts a student's personalized learning journey using a team of
nine specialized AI agents orchestrated by LangGraph, powered by Groq.

---

## Architecture

The system is built around a real LangGraph `StateGraph`, not sequential function calls.
Each agent is a graph node that receives the shared `MentorState`, performs its specialized
reasoning using Groq, persists relevant data to SQLite, and returns an updated state to the
next node. Conditional edges allow the Adaptive Agent to route execution back to the Planner
Agent (full roadmap regeneration) or forward to the Revision Agent (normal flow). A
`MemorySaver` checkpointer persists graph state per user thread.

```
Goal Agent → Planner Agent → Tutor Agent → Quiz Agent → Progress Agent → Adaptive Agent
                 ↑                                                            │
                 └───────────────── regenerate_plan = true ────────────────────┤
                                                                                ↓
                                                          Revision Agent → Reminder Agent → Memory Agent
```

### Agents

| Agent | Responsibility |
|---|---|
| Goal Agent | Parses the learning goal, computes duration, milestones, and prerequisites |
| Planner Agent | Generates syllabus, weekly modules, daily schedule, and revision slots |
| Tutor Agent | Explains concepts, gives examples, code samples, and exercises via Groq |
| Quiz Agent | Generates MCQ / Coding / Short-answer questions at adjustable difficulty |
| Progress Agent | Computes completion %, average score, weak/strong topics |
| Adaptive Agent | Adjusts difficulty, inserts revision, or triggers roadmap regeneration |
| Revision Agent | Schedules spaced-repetition revision at 1/3/7/14/30 day intervals |
| Reminder Agent | Builds daily task and deadline reminders |
| Memory Agent | Summarizes and persists long-term session memory |

---

## Tech Stack

- **Language:** Python 3.12+
- **Frontend:** Streamlit (custom dark glassmorphism theme)
- **Agent Orchestration:** LangGraph (`StateGraph`, conditional routing, checkpointing)
- **LLM Framework:** LangChain + `langchain-groq`
- **Model:** Groq
- **Database:** SQLite via SQLAlchemy ORM
- **Vector Store:** FAISS with local FastEmbed embeddings (no extra API key required) (for PDF-grounded tutoring)
- **Scheduling:** APScheduler
- **Charts:** Plotly (line, bar, pie, radar, heatmap)
- **Auth:** bcrypt password hashing + SQLite-backed sessions
- **Validation:** Pydantic
- **Data:** Pandas

---

## Folder Structure

```
Autonomous_Learning_Mentor/
├── app.py
├── pages/
│   ├── Home.py
│   ├── Dashboard.py
│   ├── Study_Plan.py
│   ├── Tutor.py
│   ├── Quiz.py
│   ├── Analytics.py
│   └── Settings.py
├── agents/
│   ├── goal_agent.py
│   ├── planner_agent.py
│   ├── tutor_agent.py
│   ├── quiz_agent.py
│   ├── progress_agent.py
│   ├── adaptive_agent.py
│   ├── revision_agent.py
│   ├── reminder_agent.py
│   ├── memory_agent.py
│   └── graph.py
├── database/
│   ├── models.py
│   ├── database.py
│   └── memory.py
├── services/
│   ├── groq_service.py
│   ├── planner.py
│   ├── quiz_generator.py
│   ├── analytics.py
│   ├── scheduler.py
│   └── auth.py
├── utils/
│   ├── constants.py
│   ├── prompts.py
│   ├── helper.py
│   └── config.py
├── assets/
│   ├── logo.png
│   └── style.css
├── requirements.txt
├── .env.example
└── README.md
```

---

## Installation

```bash
git clone <this-repository>
cd Autonomous_Learning_Mentor
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Get a free Groq API key at https://console.groq.com/keys.
You can either place it in `.env` as `GROQ_API_KEY=...`, or enter it later inside the
in-app **Settings** page (it will be validated live against the Groq API and stored locally).

---

## Run Instructions

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

1. **Register** a new account (bcrypt-hashed password stored in SQLite).
2. **Login.**
3. If no Groq key is configured yet, go to **Settings** and add/validate one.
4. On the **Home** page, describe what you want to learn, your target date, daily hours, and
   skill level, then click **Generate My Learning Roadmap** — this runs the full LangGraph
   agent cycle (Goal → Planner → Tutor → Quiz → Progress → Adaptive → Revision → Reminder →
   Memory) once end to end.
5. Explore your **Study Plan**, chat with the **AI Tutor** (optionally grounding it with an
   uploaded PDF via FAISS retrieval), take quizzes in the **Quiz** center, and monitor your
   growth in **Analytics** and the **Dashboard**.

---

## Database Schema

`Users`, `Goals`, `StudyPlans`, `QuizResults`, `Progress`, `ChatHistory`,
`RevisionSchedule`, `Reminders` — all managed through SQLAlchemy ORM models in
`database/models.py`, created automatically on first run.

---

## Screenshots

*(Add screenshots here once you run the app locally)*

- `screenshots/login.png`
- `screenshots/dashboard.png`
- `screenshots/study_plan.png`
- `screenshots/tutor.png`
- `screenshots/quiz.png`
- `screenshots/analytics.png`

---

## Future Improvements

- Multi-user real-time collaboration and leaderboards
- Voice-based tutoring using speech-to-text and text-to-speech
- Native mobile companion app with push reminders
- Support for additional LLM providers alongside Groq
- Fine-grained per-lesson spaced repetition using an SM-2 style algorithm
- Export roadmap and progress reports as PDF

---

## License

This project is provided as-is for educational purposes under the SDG 4: Quality Education
initiative.
