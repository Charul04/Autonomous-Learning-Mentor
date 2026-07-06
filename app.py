import streamlit as st
from datetime import datetime
from database.database import init_db
from services.auth import register_user, login_user
from utils.config import get_groq_api_key
from utils.constants import APP_TITLE, APP_TAGLINE

st.set_page_config(page_title=APP_TITLE, page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")


def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def init_session_state():
    defaults = {
        "authenticated": False,
        "user_id": None,
        "username": None,
        "auth_mode": "login",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_auth_screen():
    st.markdown(
        f"""
        <div class="gradient-header" style="text-align:center;">
            <h1>{APP_TITLE}</h1>
            <p>{APP_TAGLINE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["Login", "Register"])

        with tab_login:
            login_identifier = st.text_input("Username", key="login_identifier")
            login_password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", key="login_button", use_container_width=True):
                result = login_user(login_identifier, login_password)
                if result["success"]:
                    st.session_state.authenticated = True
                    st.session_state.user_id = result["user_id"]
                    st.session_state.username = result["username"]
                    st.rerun()
                else:
                    st.error(result["message"])

        with tab_register:
            reg_username = st.text_input("Username", key="reg_username")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
            if st.button("Create Account", key="register_button", use_container_width=True):
                if reg_password != reg_password_confirm:
                    st.error("Passwords do not match.")
                else:
                    result = register_user(reg_username, reg_password)
                    if result["success"]:
                        st.success("Account created successfully. Please login.")
                    else:
                        st.error(result["message"])
        st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown(f"### {APP_TITLE}")
        st.markdown(f"**Welcome, {st.session_state.username}**")
        st.divider()
        st.page_link("app.py", label="Home")
        st.page_link("pages/Dashboard.py", label="Dashboard")
        st.page_link("pages/Study_Plan.py", label="Study Plan")
        st.page_link("pages/Tutor.py", label="AI Tutor")
        st.page_link("pages/Quiz.py", label="Quiz")
        st.page_link("pages/Settings.py", label="Settings")
        st.divider()
        if st.button("Logout", use_container_width=True):
            for key in ["authenticated", "user_id", "username"]:
                st.session_state[key] = None
            st.session_state.authenticated = False
            st.rerun()


def render_home():
    st.markdown(
        f"""
        <div class="gradient-header">
            <h1>Welcome back, {st.session_state.username}</h1>
            <p>Your autonomous AI mentor is ready to plan, teach, evaluate, and adapt to your learning journey.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    from database.memory import get_active_goal
    goal = get_active_goal(st.session_state.user_id)

    if not goal:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Let's set up your learning goal")
        topic = st.text_input("What do you want to learn?", placeholder="e.g. Python, Data Structures, Machine Learning")
        from datetime import date, timedelta
        target_date = st.date_input(
            "Target Completion Date",
            value=date.today() + timedelta(days=30),
            min_value=date.today() + timedelta(days=1),
        )
        st.caption("Pick a date at least a few weeks out so the Planner Agent can build a proper multi-day roadmap.")
        daily_hours = st.slider("Daily Study Hours", 0.5, 12.0, 2.0, 0.5)
        skill_level = st.selectbox("Current Skill Level", ["Beginner", "Intermediate", "Advanced"])

        if st.button("Generate My Learning Roadmap", use_container_width=True):
            if not topic.strip():
                st.error("Please enter a learning topic.")
            elif not get_groq_api_key():
                st.error("Please configure your Groq API key in Settings first.")
            else:
                with st.spinner("Agents are collaborating to build your personalized roadmap..."):
                    from agents.graph import run_full_mentor_cycle
                    initial_state = {
                        "user_id": st.session_state.user_id,
                        "user_goal": {
                            "topic": topic,
                            "target_date": target_date.isoformat(),
                            "daily_hours": daily_hours,
                            "skill_level": skill_level,
                        },
                        "start_date": datetime.now().date().isoformat(),
                        "current_difficulty": "Medium",
                        "completed_topics": [],
                        "days_missed": 0,
                        "total_study_hours": 0.0,
                    }
                    try:
                        final_state = run_full_mentor_cycle(initial_state, thread_id=st.session_state.user_id)
                        st.session_state["last_cycle_state"] = final_state
                        st.success("Your roadmap has been generated by the agent team!")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Agent workflow failed: {exc}")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader(f"Current Goal: {goal['topic']}")
        st.write(f"Target Date: {goal['target_date']} | Daily Hours: {goal['daily_hours']} | Level: {goal['skill_level']}")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Go to Dashboard", use_container_width=True):
                st.switch_page("pages/Dashboard.py")
        with col2:
            if st.button("Start Tutoring", use_container_width=True):
                st.switch_page("pages/Tutor.py")
        with col3:
            if st.button("Take a Quiz", use_container_width=True):
                st.switch_page("pages/Quiz.py")
        with col4:
            if st.button("Start New Goal", use_container_width=True):
                from services.planner import deactivate_current_goal
                deactivate_current_goal(st.session_state.user_id)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def main():
    init_db()
    init_session_state()
    load_css()

    if not st.session_state.authenticated:
        render_auth_screen()
    else:
        render_sidebar()
        render_home()


if __name__ == "__main__":
    main()
