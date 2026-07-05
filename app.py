import streamlit as st
import io
import PyPDF2
import datetime
import plotly.express as px
import pandas as pd

import memory
import agent

# Set Streamlit page configuration
st.set_page_config(
    page_title="Study Prep Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize SQLite database
memory.init_db()

# Apply custom CSS for modern, premium look (sleek layout, clean typography, custom cards, grids)
st.markdown("""
<style>
    /* Premium style configurations */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-family: 'Inter', -apple-system, sans-serif;
        font-weight: 700;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0f1626 !important;
        border-right: 1px solid #1e293b;
    }
    
    /* Main Gradient Header */
    .main-header {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    /* Styled Metric Card */
    .metric-card {
        background-color: #131b2e;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #1e293b;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        text-align: center;
        transition: all 0.3s;
    }
    .metric-card:hover {
        border-color: #06b6d4;
        box-shadow: 0 8px 24px rgba(6, 182, 212, 0.15);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #06b6d4;
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 5px;
    }
    
    /* Quiz Question Card */
    .question-card {
        background-color: #131b2e;
        border-left: 6px solid #06b6d4;
        border-radius: 12px;
        padding: 26px;
        margin-bottom: 30px;
        border-top: 1px solid #1e293b;
        border-right: 1px solid #1e293b;
        border-bottom: 1px solid #1e293b;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        transition: all 0.3s;
    }
    .question-card:hover {
        box-shadow: 0 12px 30px rgba(6, 182, 212, 0.15);
    }
    
    .topic-tag {
        display: inline-block;
        background-color: #083344;
        color: #22d3ee;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 12px;
        border: 1px solid #0e7490;
    }
    
    .sidebar-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    /* Landing page hero & grid styles */
    .hero-container {
        text-align: center;
        padding: 50px 30px;
        background: radial-gradient(circle at center, #162238 0%, #0b0f19 80%);
        border-radius: 16px;
        border: 1px solid #1e293b;
        margin-bottom: 40px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    .hero-title {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.8rem;
        font-weight: 850;
        margin-bottom: 10px;
    }
    .hero-tagline {
        font-size: 1.4rem;
        color: #38bdf8;
        font-weight: 600;
        margin-bottom: 24px;
        letter-spacing: 0.02em;
    }
    .hero-desc {
        max-width: 850px;
        margin: 0 auto;
        color: #94a3b8;
        line-height: 1.7;
        font-size: 1.1rem;
        margin-bottom: 35px;
    }
    .step-card {
        background-color: #101726;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 24px 20px;
        text-align: center;
        height: 100%;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s;
    }
    .step-card:hover {
        border-color: #06b6d4;
        transform: translateY(-2px);
    }
    .step-icon {
        font-size: 2.8rem;
        margin-bottom: 18px;
    }
    .step-title {
        font-size: 1.15rem;
        font-weight: 750;
        color: #ffffff;
        margin-bottom: 10px;
    }
    .step-desc {
        font-size: 0.92rem;
        color: #94a3b8;
        line-height: 1.5;
    }
    .feature-card {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 26px;
        height: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
    }
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(6, 182, 212, 0.25);
        border-color: #06b6d4;
    }
    .feature-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #22d3ee;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .feature-desc {
        color: #94a3b8;
        font-size: 0.98rem;
        line-height: 1.6;
    }
    
    /* Custom buttons styling */
    .stButton>button {
        background: linear-gradient(135deg, #06b6d4 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        padding: 10px 24px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(6, 182, 212, 0.2) !important;
    }
    .stButton>button:hover {
        opacity: 0.95 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(6, 182, 212, 0.4) !important;
    }
    
    /* Specific Home CTA Button style override */
    .cta-button>div>button {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important;
        font-size: 1.25rem !important;
        padding: 14px 40px !important;
        border-radius: 9999px !important;
        box-shadow: 0 8px 20px rgba(6, 182, 212, 0.4) !important;
    }
    .cta-button>div>button:hover {
        box-shadow: 0 10px 25px rgba(6, 182, 212, 0.6) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Sidebar navigation styling (cleaner label fonts) */
    div[data-testid="stSidebar"] div.stRadio > div {
        gap: 8px;
    }
    div[data-testid="stSidebar"] div.stRadio label p {
        font-size: 1.02rem !important;
        font-weight: 600 !important;
    }
    
    /* Clickable Feature Card Button styling */
    .feature-card-btn button {
        background-color: #131b2e !important;
        color: #f1f5f9 !important;
        border: 1px solid #1e293b !important;
        padding: 20px !important;
        border-radius: 12px !important;
        text-align: left !important;
        width: 100% !important;
        min-height: 140px !important;
        display: block !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        line-height: 1.5 !important;
    }
    .feature-card-btn button:hover {
        border-color: #06b6d4 !important;
        box-shadow: 0 10px 25px rgba(6, 182, 212, 0.25) !important;
        transform: translateY(-3px) !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to extract PDF text
def extract_pdf_text(file_bytes):
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Error parsing PDF file: {e}")
        return ""

# Helper function to get styled difficulty badge HTML
def get_difficulty_badge(difficulty: str) -> str:
    diff_val = (difficulty or "medium").lower()
    if diff_val == "easy":
        style = "background-color: #065f46; color: #34d399; border: 1px solid #047857;"
    elif diff_val == "hard":
        style = "background-color: #7f1d1d; color: #f87171; border: 1px solid #b91c1c;"
    else:
        style = "background-color: #854d0e; color: #fbbf24; border: 1px solid #a16207;"
    return f'<span style="display: inline-block; padding: 4px 12px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px; margin-left: 6px; {style}">{diff_val.upper()}</span>'

# Page routing callback
def go_to_study():
    st.session_state.current_page = "📝 Upload & Study"

# Initialize global tracking states
if "consecutive_failures" not in st.session_state:
    st.session_state.consecutive_failures = 0
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Home"
if "filter_topic" not in st.session_state:
    st.session_state.filter_topic = None

# Sidebar Navigation (bound to session state key "current_page" with emoji icons)
main_pages = [
    "🏠 Home",
    "📝 Upload & Study",
    "💬 Study Coach",
    "📈 Progress Dashboard",
    "🗂️ My Decks",
    "📚 Revision Sheets",
    "🏆 Achievements"
]
if st.session_state.current_page in main_pages:
    sidebar_index = main_pages.index(st.session_state.current_page)
else:
    if st.session_state.current_page.startswith("Feature:"):
        sidebar_index = 0
    else:
        sidebar_index = 3

with st.sidebar:
    # App Logo Icon and Title
    col_logo, col_title = st.columns([1, 3])
    with col_logo:
        st.image("study_agent_logo.png", use_container_width=True)
    with col_title:
        st.markdown('<div class="sidebar-title" style="margin-top: 10px;">Study Prep Agent</div>', unsafe_allow_html=True)
        
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Subject Deck Switcher in Sidebar
    st.markdown("📂 **Subject Deck**")
    all_decks = memory.get_all_decks()
    if all_decks:
        deck_names = [d["name"] for d in all_decks]
        active_id = st.session_state.get("active_deck_id")
        active_idx = 0
        if active_id:
            for idx, d in enumerate(all_decks):
                if d["id"] == active_id:
                    active_idx = idx
                    break
        else:
            # Auto-select first deck if none is set
            st.session_state.active_deck_id = all_decks[0]["id"]
            st.session_state.active_deck_name = all_decks[0]["name"]
            
        selected_deck_name = st.selectbox(
            "Select active deck:",
            options=deck_names,
            index=active_idx,
            label_visibility="collapsed"
        )
        
        # Update active deck states on selectbox change
        for d in all_decks:
            if d["name"] == selected_deck_name:
                if st.session_state.get("active_deck_id") != d["id"]:
                    st.session_state.active_deck_id = d["id"]
                    st.session_state.active_deck_name = d["name"]
                    st.session_state.quiz_active = False
                    st.session_state.quiz_questions = []
                    st.session_state.filter_topic = None
                    st.rerun()
                break
    else:
        st.info("No decks created yet. Create a deck on the Home page!")
        st.session_state.active_deck_id = None
        st.session_state.active_deck_name = None
        
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Sidebar navigation binding (with Emoji icons)
    page_sel = st.radio(
        "Navigation",
        options=main_pages,
        index=sidebar_index
    )
    
    # Handle user sidebar navigation click
    if page_sel != st.session_state.current_page:
        is_feature_subpage = (st.session_state.current_page.startswith("Feature:") and page_sel == "🏠 Home")
        is_topic_subpage = (st.session_state.current_page.startswith("Topic:") and page_sel == "📈 Progress Dashboard")
        if not (is_feature_subpage or is_topic_subpage):
            st.session_state.current_page = page_sel
            st.session_state.filter_topic = None

# Use current_page state for layout rendering
page = st.session_state.current_page
if page == "🏠 Home":
    # Fetch real stats from SQLite
    all_decks = memory.get_all_decks()
    conn = memory.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM quiz_history")
        total_questions_logged = cursor.fetchone()[0]
    except Exception:
        total_questions_logged = 0
        
    try:
        cursor.execute("""
            SELECT topic, CAST(SUM(is_correct) AS FLOAT) / COUNT(*) as acc
            FROM quiz_history
            GROUP BY topic
            HAVING acc >= 0.75 AND COUNT(*) >= 3
        """)
        mastered_topics_count = len(cursor.fetchall())
    except Exception:
        mastered_topics_count = 0
    conn.close()

    # Hero Section Grid (SaaS Polished Columns Layout)
    col_hero_left, col_hero_right = st.columns([6, 5])
    with col_hero_left:
        st.markdown("""
        <div style="padding-top: 10px; padding-bottom: 10px;">
            <h1 class="main-header" style="font-size: 3.4rem; line-height: 1.1; margin-bottom: 15px; text-align: left;">Study Prep Agent</h1>
            <div class="hero-tagline" style="font-size: 1.25rem; color: #38bdf8; font-weight: 600; margin-bottom: 20px; text-align: left;">
                "The study buddy that remembers what you don't know"
            </div>
            <p style="color: #cbd5e1; font-size: 1.02rem; line-height: 1.65; margin-bottom: 35px; text-align: left;">
                An intelligent, adaptive exam preparation assistant designed to optimize your learning. 
                Simply upload your study materials, and let our generative AI construct custom multiple-choice 
                and short-answer practice sessions, giving you instant conceptual explanations 
                while tracking your progress to automatically reinforce your weaker areas.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Start Studying CTA Button
        st.markdown('<div class="cta-button" style="text-align: left; margin-bottom: 25px;">', unsafe_allow_html=True)
        st.button("Start Studying ➔", on_click=go_to_study, key="cta_start_studying_btn")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_hero_right:
        # Illustrative premium live preview card mockup representing a study session
        st.markdown("""
        <div style="background-color: #131b2e; padding: 24px; border-radius: 16px; border: 1.5px solid #06b6d4; box-shadow: 0 12px 30px rgba(6, 182, 212, 0.15); margin-top: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="background-color: #083344; color: #22d3ee; padding: 4px 10px; border-radius: 9999px; font-size: 0.7rem; font-weight: 700; border: 1px solid #0e7490; text-transform: uppercase;">GEOGRAPHY</span>
                <span style="background-color: #7f1d1d; color: #f87171; padding: 4px 10px; border-radius: 9999px; font-size: 0.7rem; font-weight: 700; border: 1px solid #b91c1c;">HARD</span>
            </div>
            <h4 style="color: #ffffff; font-size: 1rem; font-weight: 750; margin-top: 5px; margin-bottom: 15px; line-height: 1.45;">
                Which of the following describes the zone where two crustal plates slip past each other horizontally?
            </h4>
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <div style="background-color: #1e293b; padding: 10px 14px; border-radius: 8px; border: 1px solid #334155; font-size: 0.85rem; color: #94a3b8; display: flex; justify-content: space-between;">
                    <span>A. Convergent Boundary</span>
                </div>
                <div style="background-color: #064e3b; padding: 10px 14px; border-radius: 8px; border: 1px solid #059669; font-size: 0.85rem; color: #34d399; font-weight: 600; display: flex; justify-content: space-between; align-items: center;">
                    <span>B. Transform Fault Boundary</span>
                    <span style="font-size: 0.75rem; background-color: #047857; color: #ffffff; padding: 2px 6px; border-radius: 4px;">🟢 Selected</span>
                </div>
                <div style="background-color: #1e293b; padding: 10px 14px; border-radius: 8px; border: 1px solid #334155; font-size: 0.85rem; color: #94a3b8;">
                    C. Divergent Rift Zone
                </div>
            </div>
            <div style="margin-top: 15px; background-color: #1e293b; padding: 12px; border-radius: 8px; border: 1px solid #334155; font-size: 0.82rem; line-height: 1.4; color: #cbd5e1;">
                💡 <b>Coach:</b> Convection cells force lateral shearing horizontally along transform faults.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Real Statistics Strip
    st.markdown(f"""
    <div style="background-color: #101625; padding: 15px 30px; border-radius: 12px; border: 1px solid #1e293b; display: flex; justify-content: space-around; align-items: center; margin-top: 25px; margin-bottom: 35px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);">
        <div style="text-align: center; flex: 1;">
            <div style="color: #06b6d4; font-size: 1.8rem; font-weight: 800;">{len(all_decks)}</div>
            <div style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Decks Created</div>
        </div>
        <div style="border-left: 1px solid #1e293b; height: 35px;"></div>
        <div style="text-align: center; flex: 1;">
            <div style="color: #3b82f6; font-size: 1.8rem; font-weight: 800;">{total_questions_logged}</div>
            <div style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Questions Answered</div>
        </div>
        <div style="border-left: 1px solid #1e293b; height: 35px;"></div>
        <div style="text-align: center; flex: 1;">
            <div style="color: #10b981; font-size: 1.8rem; font-weight: 800;">{mastered_topics_count}</div>
            <div style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Concepts Mastered</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
        
    st.markdown("<hr style='border: 0; border-top: 1px solid #1e293b; margin: 30px 0;'>", unsafe_allow_html=True)
    
    # About the Project Section
    st.markdown("### About the Project")
    about_col_left, about_col_right = st.columns([5, 5])
    with about_col_left:
        st.markdown("""
        <div style="background-color: #0e1320; padding: 25px; border-radius: 12px; border: 1px solid #1e293b; height: 100%;">
            <h4 style="color: #06b6d4; margin-top:0; font-weight:700;">🧠 Adaptive Learning Loop</h4>
            <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0;">
                Study Prep Agent is powered by an active recall methodology. Instead of passive reading, the system forces 
                your brain to retrieve information through dynamic quizzes. Performance logs are tracked using an integrated 
                SQLite schema, feeding an adaptive algorithm that automatically weights weaker topics in subsequent practice sets.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with about_col_right:
        st.markdown("""
        <div style="background-color: #0e1320; padding: 25px; border-radius: 12px; border: 1px solid #1e293b; height: 100%;">
            <h4 style="color: #3b82f6; margin-top:0; font-weight:700;">🤖 Multi-Agent Critic Framework</h4>
            <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0;">
                To ensure high quality, the system leverages a multi-agent generation loop. 
                First, a generator drafts quiz questions and initial response critiques. 
                A secondary referee agent analyzes the output, assessing explanation correctness, 
                clarity, and potential edge cases. A final refiner synthesizes the notes, producing precise feedback.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<hr style='border: 0; border-top: 1px solid #1e293b; margin: 30px 0;'>", unsafe_allow_html=True)
    
    # Core Application Hubs Section
    st.markdown("### Core Application Hubs")
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-top: -10px; margin-bottom: 25px;'>Navigate directly to any section of the study agent below to start learning:</p>", unsafe_allow_html=True)
    
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    with nav_col1:
        st.markdown("""
        <div style="background-color: #131b2e; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; text-align: center; min-height: 190px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="font-size: 2rem; margin-bottom: 5px;">📝</div>
                <h4 style="color: #ffffff; font-size: 1.05rem; margin: 0; font-weight:700;">Upload & Quiz</h4>
                <p style="color: #94a3b8; font-size: 0.78rem; margin-top: 8px; line-height: 1.3;">Upload notes, generate custom adaptive quizzes, and practice concepts.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Quizzes ➔", key="nav_to_quizzes", use_container_width=True):
            st.session_state.current_page = "📝 Upload & Study"
            st.rerun()
            
    with nav_col2:
        st.markdown("""
        <div style="background-color: #131b2e; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; text-align: center; min-height: 190px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="font-size: 2rem; margin-bottom: 5px;">💬</div>
                <h4 style="color: #ffffff; font-size: 1.05rem; margin: 0; font-weight:700;">AI Study Coach</h4>
                <p style="color: #94a3b8; font-size: 0.78rem; margin-top: 8px; line-height: 1.3;">Discuss your notes, ask questions, or request quick concept drills.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Chatting ➔", key="nav_to_coach", use_container_width=True):
            st.session_state.current_page = "💬 Study Coach"
            st.rerun()
            
    with nav_col3:
        st.markdown("""
        <div style="background-color: #131b2e; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; text-align: center; min-height: 190px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="font-size: 2rem; margin-bottom: 5px;">📈</div>
                <h4 style="color: #ffffff; font-size: 1.05rem; margin: 0; font-weight:700;">Progress Dashboard</h4>
                <p style="color: #94a3b8; font-size: 0.78rem; margin-top: 8px; line-height: 1.3;">Track topic accuracies, streaks, and view the Mastery Map.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Progress ➔", key="nav_to_dashboard", use_container_width=True):
            st.session_state.current_page = "📈 Progress Dashboard"
            st.rerun()
            
    with nav_col4:
        st.markdown("""
        <div style="background-color: #131b2e; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; text-align: center; min-height: 190px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="font-size: 2rem; margin-bottom: 5px;">📚</div>
                <h4 style="color: #ffffff; font-size: 1.05rem; margin: 0; font-weight:700;">Revision Sheets</h4>
                <p style="color: #94a3b8; font-size: 0.78rem; margin-top: 8px; line-height: 1.3;">Generate sheets covering just concepts under 70% accuracy.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Sheets ➔", key="nav_to_sheets", use_container_width=True):
            st.session_state.current_page = "📚 Revision Sheets"
            st.rerun()
            
    st.markdown("<hr style='border: 0; border-top: 1px solid #1e293b; margin: 30px 0;'>", unsafe_allow_html=True)
    st.markdown("### How It Works")
    
    # Steps columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="step-card">
            <div class="step-icon">📤</div>
            <div class="step-title">1. Upload Notes</div>
            <div class="step-desc">Paste your lecture notes or upload text and PDF slides directly into the study agent.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="step-card">
            <div class="step-icon">🧠</div>
            <div class="step-title">2. AI Generates Quiz</div>
            <div class="step-desc">The model analyzes the material to extract topics and generates a customized MCQ & short-answer session.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="step-card">
            <div class="step-icon">⚡</div>
            <div class="step-title">3. Instant Feedback</div>
            <div class="step-desc">Practice page-by-page and receive immediate grading accompanied by conversational explanations.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
        <div class="step-card">
            <div class="step-icon">📈</div>
            <div class="step-title">4. Adaptive Bias</div>
            <div class="step-desc">The system logs your performance history to detect and prioritize weak concepts in future sessions.</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<hr style='border: 0; border-top: 1px solid #1e293b; margin: 30px 0;'>", unsafe_allow_html=True)
    
    # Today's Recommended Study Card
    st.markdown("### Today's Recommended Study")
    active_deck_id = st.session_state.get("active_deck_id")
    recommended_deck_name = st.session_state.get("active_deck_name")
    
    has_history = False
    weakest_topic = None
    weakest_accuracy = None
    
    if active_deck_id:
        stats = memory.get_topic_stats(deck_id=active_deck_id)
        if stats:
            has_history = True
            # Fetch weak topics (threshold=1.01 to get any topic with accuracy < 101%) ordered by weakest first
            weak_topics_list = memory.get_weak_topics(threshold=1.01, deck_id=active_deck_id)
            if weak_topics_list:
                weakest_topic = weak_topics_list[0]
                # Find its accuracy
                for s in stats:
                    if s["topic"] == weakest_topic:
                        weakest_accuracy = s["accuracy"]
                        break
                        
    if has_history and weakest_topic is not None:
        st.markdown(f"""
        <div style="background-color: #131b2e; padding: 20px; border-radius: 12px; border: 1px solid #f59e0b; margin-bottom: 15px;">
            <h4 style="color: #f59e0b; margin-top: 0; font-weight:700;">🎯 Daily Study Target: {recommended_deck_name}</h4>
            <p style="color: #ffffff; font-size: 1.05rem; margin-top: 8px; margin-bottom: 8px;">
                Based on your progress, we recommend reviewing: <b style="color: #06b6d4;">{weakest_topic}</b>
            </p>
            <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 0;">
                💡 You're at <b>{weakest_accuracy}%</b> accuracy here. Focus on this concept to boost your overall subject score.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Place button under card
        if st.button("🚀 Review Now", key="recommendation_review_btn", use_container_width=True):
            st.session_state.bias_topic = weakest_topic
            st.session_state.current_page = "📝 Upload & Study"
            st.rerun()
    else:
        st.markdown("""
        <div style="background-color: #131b2e; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; margin-bottom: 15px;">
            <h4 style="color: #94a3b8; margin-top: 0; font-weight:700;">🎯 Daily Study Target</h4>
            <p style="color: #cbd5e1; font-size: 0.95rem; margin-top: 8px; margin-bottom: 0;">
                Complete your first quiz to get personalized recommendations!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<hr style='border: 0; border-top: 1px solid #1e293b; margin: 30px 0;'>", unsafe_allow_html=True)
    st.markdown("### Your Subject Decks")
    
    # Load all decks
    all_decks = memory.get_all_decks()
    
    # Decks grid: 3 columns per row
    deck_cols = st.columns(3)
    
    # Loop over all decks and render them as cards
    for idx, deck in enumerate(all_decks):
        col_idx = idx % 3
        with deck_cols[col_idx]:
            # Fetch overall stats for this deck
            stats = memory.get_performance_summary(deck_id=deck["id"])
            total = stats["total_questions"]
            accuracy = stats["average_score_pct"]
            
            # Highlight card if active
            is_active = (st.session_state.get("active_deck_id") == deck["id"])
            border_color = "#06b6d4" if is_active else "#1e293b"
            glow_class = "box-shadow: 0 0 15px rgba(6, 182, 212, 0.2);" if is_active else ""
            
            # Render a styled card containing a button
            st.markdown(f"""
            <div style="background-color: #131b2e; padding: 20px; border-radius: 12px; border: 1px solid {border_color}; {glow_class} min-height: 180px;">
                <h4 style="color: #ffffff; margin-top: 0; font-weight:700;">📂 {deck['name']}</h4>
                <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 8px;">
                    Questions Logged: <b>{total}</b><br>
                    Overall Accuracy: <b>{accuracy}%</b>
                </p>
                <div style="color: #06b6d4; font-size: 0.85rem; font-weight: 700; margin-bottom: 12px;">
                    {'🟢 Currently Active' if is_active else '📁 Click below to activate'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Place select button under the card description
            if st.button(f"Activate {deck['name']}", key=f"btn_activate_deck_{deck['id']}", use_container_width=True):
                st.session_state.active_deck_id = deck["id"]
                st.session_state.active_deck_name = deck["name"]
                st.session_state.quiz_active = False
                st.session_state.quiz_questions = []
                st.session_state.filter_topic = None
                st.session_state.current_page = "📝 Upload & Study"
                st.rerun()
                
            st.markdown("<br>", unsafe_allow_html=True)
            
    # Render the "+ New Deck" card in the next grid position
    new_deck_col_idx = len(all_decks) % 3
    with deck_cols[new_deck_col_idx]:
        st.markdown("""
        <div style="background-color: #0c101a; padding: 20px; border-radius: 12px; border: 1px dashed #06b6d4; min-height: 180px; text-align: center; display: flex; flex-direction: column; justify-content: center;">
            <h4 style="color: #06b6d4; margin-top: 0; font-weight:700;">➕ Create Deck</h4>
            <p style="color: #94a3b8; font-size: 0.85rem;">Add a new subject to study separately.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show create deck form in an expander
        with st.expander("Configure New Deck"):
            with st.form("create_deck_form", clear_on_submit=True):
                deck_name = st.text_input("Deck Name:", placeholder="e.g. Accounting Unit 2")
                deck_input_method = st.radio("Notes source:", ["Paste Text", "Upload File (.txt, .pdf)"], key="deck_input_method")
                
                deck_source_text = ""
                if deck_input_method == "Paste Text":
                    deck_source_text = st.text_area("Paste Study Notes:", height=150, placeholder="Paste notes here...")
                else:
                    deck_file = st.file_uploader("Upload Notes File:", type=["txt", "pdf"], key="deck_file_uploader")
                    if deck_file is not None:
                        file_ext = deck_file.name.split(".")[-1].lower()
                        if file_ext == "pdf":
                            pdf_bytes = deck_file.read()
                            deck_source_text = extract_pdf_text(pdf_bytes)
                        else:
                            deck_source_text = deck_file.read().decode("utf-8", errors="ignore")
                
                submit_deck = st.form_submit_button("Create Deck")
                if submit_deck:
                    if not deck_name.strip():
                        st.error("Please provide a deck name.")
                    elif not deck_source_text.strip():
                        st.error("Please provide study notes or upload a file.")
                    else:
                        try:
                            # Create deck
                            new_id = memory.create_deck(deck_name.strip(), deck_source_text.strip())
                            st.session_state.active_deck_id = new_id
                            st.session_state.active_deck_name = deck_name.strip()
                            st.success(f"Deck '{deck_name}' created successfully!")
                            st.session_state.current_page = "📝 Upload & Study"
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to create deck (name might already exist): {e}")

    st.markdown("<hr style='border: 0; border-top: 1px solid #1e293b; margin: 30px 0;'>", unsafe_allow_html=True)
    st.markdown("### Key Features")
    
    # Features Grid (2x2)
    feat_col1, feat_col2 = st.columns(2)
    
    with feat_col1:
        st.markdown('<div class="feature-card-btn">', unsafe_allow_html=True)
        if st.button("🎯 Adaptive Difficulty\n\nLearn how quizzes automatically scale up or down based on your performance streaks and prioritize your weak areas.", key="feat_adapt"):
            st.session_state.current_page = "Feature: Adaptive Difficulty"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown('<div class="feature-card-btn">', unsafe_allow_html=True)
        if st.button("🤖 Multi-Agent Review\n\nRead about the collaborative critique and explanation refiner agent that helps clarify difficult concepts.", key="feat_multi"):
            st.session_state.current_page = "Feature: Multi-Agent Review"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with feat_col2:
        st.markdown('<div class="feature-card-btn">', unsafe_allow_html=True)
        if st.button("💾 Spaced Repetition Memory\n\nSee how your quiz attempts are recorded in SQLite to track long-term retention and topic progression.", key="feat_spaced"):
            st.session_state.current_page = "Feature: Spaced Repetition Memory"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown('<div class="feature-card-btn">', unsafe_allow_html=True)
        if st.button("📋 Revision Sheets\n\nGenerate customized summaries covering just your weak concepts with key points and common mistakes.", key="feat_sheet"):
            st.session_state.current_page = "Feature: Revision Sheets"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- PAGE 1: Upload & Study -----------------
elif page == "📝 Upload & Study":
    # Ensure an active deck is selected
    active_deck_id = st.session_state.get("active_deck_id")
    if not active_deck_id:
        all_decks = memory.get_all_decks()
        if not all_decks:
            st.warning("⚠️ **No subject decks found.**")
            st.info("To start studying, please go to the Home page and create a subject deck or upload study materials!")
            if st.button("➡️ Go to Home Page", key="go_home_no_decks"):
                st.session_state.current_page = "🏠 Home"
                st.rerun()
            st.stop()
        else:
            st.session_state.active_deck_id = all_decks[0]["id"]
            st.session_state.active_deck_name = all_decks[0]["name"]
            st.rerun()
            
    active_deck = memory.get_deck(st.session_state.active_deck_id)
    
    st.markdown(f'<div class="main-header">🎓 Study Prep: {active_deck["name"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">An intelligent exam preparation assistant. Test your knowledge on the active subject deck notes. The system automatically tracks your results to prioritize weak areas in future quizzes.</div>', unsafe_allow_html=True)
    
    # Initialize session states for one-question-at-a-time quiz
    if "quiz_active" not in st.session_state:
        st.session_state.quiz_active = False
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = []
    if "current_q_index" not in st.session_state:
        st.session_state.current_q_index = 0
    if "current_q_answered" not in st.session_state:
        st.session_state.current_q_answered = False
    if "current_q_feedback" not in st.session_state:
        st.session_state.current_q_feedback = {}
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
    if "quiz_responses" not in st.session_state:
        st.session_state.quiz_responses = []
    if "quiz_topic_summary" not in st.session_state:
        st.session_state.quiz_topic_summary = ""
    if "quiz_db_saved" not in st.session_state:
        st.session_state.quiz_db_saved = False
    if "show_truncation_warning" not in st.session_state:
        st.session_state.show_truncation_warning = False

    # State 1: Configure & Upload
    if not st.session_state.quiz_active:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("1. Input Material")
            input_method = st.radio("Choose input method:", ["Use Deck Notes", "Upload File (.txt, .pdf)", "Paste Text"], horizontal=True)
            
            study_text = ""
            if input_method == "Use Deck Notes":
                study_text = active_deck["source_text"]
                st.info(f"📂 Loaded notes from **{active_deck['name']}**.")
                st.text_area("Notes Preview (Read-only):", value=study_text, height=200, disabled=True)
            elif input_method == "Paste Text":
                study_text = st.text_area(
                    "Paste your study notes or textbook text here:",
                    value=active_deck["source_text"],
                    height=250,
                    placeholder="Type or paste study text..."
                )
            else:
                uploaded_file = st.file_uploader("Upload a file:", type=["txt", "pdf"])
                if uploaded_file is not None:
                    # Fix: Reset file pointer using seek(0) in case of reruns
                    uploaded_file.seek(0)
                    file_extension = uploaded_file.name.split(".")[-1].lower()
                    if file_extension == "pdf":
                        with st.spinner("Extracting text from PDF..."):
                            pdf_bytes = uploaded_file.read()
                            study_text = extract_pdf_text(pdf_bytes)
                        if study_text:
                            st.success(f"Successfully extracted text from {uploaded_file.name}!")
                    else:
                        # Plain text
                        study_text = uploaded_file.getvalue().decode("utf-8")
                        st.success(f"Successfully read {uploaded_file.name}!")
                else:
                    study_text = active_deck["source_text"]
                    st.info(f"📂 Using existing notes from deck **{active_deck['name']}** until a file is uploaded.")
                        
        with col2:
            st.subheader("2. Quiz Preferences")
            q_count = st.slider("Number of questions:", min_value=3, max_value=10, value=5)
            
            # Show weak topics pulled from SQLite for the active deck
            weak_topics = memory.get_weak_topics(threshold=0.6, deck_id=active_deck_id)
            bias_t = st.session_state.get("bias_topic")
            if bias_t and bias_t not in weak_topics:
                weak_topics.append(bias_t)
                
            if bias_t:
                st.info(f"🎯 **Target study concept preset:** Biasing quiz questions to focus on: **{bias_t}**")
                
            if weak_topics:
                st.markdown("💡 **Your weak topics detected in this deck (<60% accuracy):**")
                for wt in weak_topics:
                    prefix = "🎯 " if wt == bias_t else "- ⚠️ "
                    st.caption(f"{prefix}{wt}")
                st.info("The system will prioritize these concepts, biasing roughly 60% of the quiz questions towards them.")
            else:
                st.info("No prior weak topics detected. Quiz questions will cover all extracted topics equally.")

            st.markdown("<br>", unsafe_allow_html=True)
            generate_session_btn = st.button("Generate Study Session")
            
            if generate_session_btn:
                if not study_text.strip():
                    st.error("Please provide study material first by pasting text or uploading a file.")
                else:
                    with st.spinner("Extracting topics and generating customized quiz..."):
                        try:
                            # Extract topics (includes safe token truncation)
                            extracted_topics, was_truncated = agent.extract_topics(study_text)
                            st.session_state.show_truncation_warning = was_truncated
                            
                            # DEBUG PRINT
                            print(f"\n[DEBUG] extract_topics() returned: {extracted_topics}")
                            
                            # DEBUG PRINT
                            print(f"[DEBUG] Calling generate_quiz() with topics: {extracted_topics}, weak_topics: {weak_topics}, num_questions: {q_count}")
                            print(f"[DEBUG] Sample study_text passed (first 100 chars): {study_text[:100]!r}\n")
                            
                            # Generate quiz questions
                            quiz_questions = agent.generate_quiz(
                                topics=extracted_topics,
                                weak_topics=weak_topics,
                                num_questions=q_count,
                                study_text=study_text
                            )
                            
                            if quiz_questions:
                                # Reset consecutive failure count on success
                                st.session_state.consecutive_failures = 0
                                
                                # Setup session state variables
                                st.session_state.quiz_questions = quiz_questions
                                st.session_state.quiz_active = True
                                st.session_state.current_q_index = 0
                                st.session_state.current_q_answered = False
                                st.session_state.current_q_feedback = {}
                                st.session_state.quiz_score = 0
                                st.session_state.quiz_responses = []
                                st.session_state.quiz_db_saved = False
                                
                                # Summary description
                                summary_desc = ", ".join(extracted_topics[:2])
                                if len(extracted_topics) > 2:
                                    summary_desc += "..."
                                st.session_state.quiz_topic_summary = summary_desc
                                st.rerun()
                            else:
                                raise agent.GeminiAPIError("The generated quiz was empty.")
                                
                        except agent.GeminiAPIError as e:
                            st.session_state.consecutive_failures += 1
                            if st.session_state.consecutive_failures >= 2:
                                st.error(
                                    "⚠️ **Multiple study session attempts have failed.**\n\n"
                                    "Please try providing different, richer study text, check "
                                    "your API key/network connection, or verify rate limits."
                                )
                            else:
                                st.error(f"Generation failed: {e}")
                        except Exception as e:
                            st.session_state.consecutive_failures += 1
                            if st.session_state.consecutive_failures >= 2:
                                st.error(
                                    "⚠️ **Multiple study session attempts have failed.**\n\n"
                                    "Please check your input data or configuration and try again."
                                )
                            else:
                                st.error(f"An unexpected error occurred: {e}")

    # State 2: Active Interactive Quiz (One question at a time)
    else:
        questions = st.session_state.quiz_questions
        current_idx = st.session_state.current_q_index
        total_qs = len(questions)

        # Show truncation warning if it occurred
        if st.session_state.show_truncation_warning:
            st.warning("⚠️ **Notice:** The study material provided was too large and was truncated to a safe token limit.")

        # check if quiz completed
        if current_idx < total_qs:
            q = questions[current_idx]
            
            st.markdown(f"### Question {current_idx + 1} of {total_qs}")
            st.progress((current_idx) / total_qs)
            
            st.markdown('<div class="question-card">', unsafe_allow_html=True)
            topic_html = f'<span class="topic-tag">{q.get("topic", "General")}</span>'
            diff_html = get_difficulty_badge(q.get("difficulty", "medium"))
            st.markdown(f'{topic_html} {diff_html}', unsafe_allow_html=True)
            st.markdown(f"#### {q.get('question')}")
            
            q_type = q.get("type", "mcq")
            correct_ans = q.get("correct_answer")
            options = q.get("options", [])
            
            user_input_val = None
            
            # Select/Input answer
            if q_type == "mcq":
                # Render options normally if not answered, else render styled results
                if st.session_state.current_q_answered:
                    feedback = st.session_state.current_q_feedback
                    user_ans = feedback["user_answer"]
                    
                    # Custom styled visual feedback highlights
                    for opt in options:
                        if opt == correct_ans:
                            st.markdown(f"""
                            <div style="background-color: #064e3b; border: 1px solid #10b981; padding: 12px 18px; border-radius: 8px; margin-bottom: 10px; color: #ecfdf5; font-weight: 500; font-family: sans-serif;">
                                🟢 <b>{opt}</b> (Correct Answer)
                            </div>
                            """, unsafe_allow_html=True)
                        elif opt == user_ans:
                            st.markdown(f"""
                            <div style="background-color: #7f1d1d; border: 1px solid #f87171; padding: 12px 18px; border-radius: 8px; margin-bottom: 10px; color: #fef2f2; font-weight: 500; font-family: sans-serif;">
                                🔴 <b>{opt}</b> (Your Selection - Incorrect)
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="border: 1px solid #1e293b; padding: 12px 18px; border-radius: 8px; margin-bottom: 10px; color: #94a3b8; background-color: #0f172a; opacity: 0.6; font-family: sans-serif;">
                                ⚪ {opt}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    user_input_val = st.radio(
                        "Choose one:",
                        options=options,
                        key=f"active_q_radio_{current_idx}",
                        index=None
                    )
            else:
                # Short Answer
                if st.session_state.current_q_answered:
                    feedback = st.session_state.current_q_feedback
                    user_ans = feedback["user_answer"]
                    
                    st.text_input("Your answer:", value=user_ans, disabled=True, key=f"q_val_{current_idx}")
                    
                    if feedback["is_correct"]:
                        st.markdown(f"""
                        <div style="background-color: #064e3b; border: 1px solid #10b981; padding: 16px 20px; border-radius: 8px; margin-top: 15px; color: #ecfdf5; line-height: 1.5; font-family: sans-serif;">
                            🟢 <b>Correct Answer!</b><br>
                            Reference Answer: <b>{correct_ans}</b>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background-color: #7f1d1d; border: 1px solid #f87171; padding: 16px 20px; border-radius: 8px; margin-top: 15px; color: #fef2f2; line-height: 1.5; font-family: sans-serif;">
                            🔴 <b>Incorrect</b><br>
                            Your Answer: <i>"{user_ans}"</i><br>
                            Reference Answer: <b>{correct_ans}</b>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    user_input_val = st.text_input(
                        "Type your answer:",
                        key=f"active_q_text_{current_idx}",
                        placeholder="Short answer..."
                    )
                
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Submit Answer
            if not st.session_state.current_q_answered:
                submit_ans_btn = st.button("Submit Answer")
                if submit_ans_btn:
                    if user_input_val is None or (isinstance(user_input_val, str) and not user_input_val.strip()):
                        st.warning("Please provide an answer before submitting.")
                    else:
                        with st.spinner("Checking answer..."):
                            is_correct = False
                            draft_explanation = ""
                            final_explanation = ""
                            
                            if q_type == "mcq":
                                is_correct = (user_input_val.strip() == correct_ans.strip())
                                if is_correct:
                                    draft_explanation = "Correct!"
                                    final_explanation = "Correct!"
                                else:
                                    draft_explanation = agent.generate_explanation(q.get("question"), correct_ans, options)
                                    final_explanation = agent.critique_explanation(q.get("question"), correct_ans, draft_explanation)
                            else:
                                # Short answer evaluation using Gemini
                                eval_result = agent.evaluate_short_answer(
                                    question=q.get("question"),
                                    correct_answer=correct_ans,
                                    user_answer=user_input_val
                                )
                                is_correct = eval_result.get("is_correct", False)
                                draft_explanation = eval_result.get("explanation", "")
                                if is_correct:
                                    final_explanation = draft_explanation
                                else:
                                    final_explanation = agent.critique_explanation(q.get("question"), correct_ans, draft_explanation)
                                
                            # Record feedback state
                            st.session_state.current_q_feedback = {
                                "is_correct": is_correct,
                                "user_answer": user_input_val,
                                "correct_answer": correct_ans,
                                "draft_explanation": draft_explanation,
                                "explanation": final_explanation
                            }
                            
                            # Increment total score if correct
                            if is_correct:
                                st.session_state.quiz_score += 1
                                
                            # Log answer response to DB immediately
                            q_topic = q.get("topic", "General")
                            memory.log_answer(q_topic, is_correct, deck_id=st.session_state.get("active_deck_id"))
                            
                            # Append to responses log
                            st.session_state.quiz_responses.append({
                                "question": q.get("question"),
                                "type": q_type,
                                "user_answer": user_input_val,
                                "correct_answer": correct_ans,
                                "is_correct": is_correct,
                                "draft_explanation": draft_explanation,
                                "explanation": final_explanation,
                                "topic": q_topic,
                                "difficulty": q.get("difficulty", "medium")
                            })
                            
                            st.session_state.current_q_answered = True
                            st.rerun()
            
            # Post-Submission Feedback
            else:
                feedback = st.session_state.current_q_feedback
                
                # Show Gemini explanation
                st.info(feedback["explanation"])
                
                # Collapsible see how explanation was generated
                if not feedback["is_correct"]:
                    with st.expander("🛠️ See how this explanation was generated"):
                        st.markdown(f"**Agent 1 (Draft Explanation):**\n{feedback['draft_explanation']}")
                        st.markdown(f"**Agent 2 (Critique & Refined Explanation):**\n{feedback['explanation']}")
                
                # Navigation button
                button_label = "Next Question" if (current_idx + 1) < total_qs else "Show Summary"
                next_q_btn = st.button(button_label)
                if next_q_btn:
                    # Move to next question
                    st.session_state.current_q_index += 1
                    st.session_state.current_q_answered = False
                    st.session_state.current_q_feedback = {}
                    st.rerun()

        # Quiz Finished State
        else:
            st.subheader("Quiz Completed! 🎉")
            
            total_score = st.session_state.quiz_score
            pct = round((total_score / total_qs) * 100)
            
            # Save results to DB exactly once
            if not st.session_state.quiz_db_saved:
                st.session_state.quiz_db_saved = True
            
            # Display Score Panels
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Questions", total_qs)
            with col2:
                st.metric("Final Score", f"{total_score} / {total_qs}")
            with col3:
                st.metric("Accuracy", f"{pct}%")
                
            # Score feedback banner
            if pct >= 80:
                st.success("🎯 Outstanding! You've mastered these concepts.")
            elif pct >= 50:
                st.info("👍 Good job! Spend a bit more time reviewing the topics below.")
            else:
                st.error("📚 Study Recommended. We suggest reviewing your source materials on these concepts.")
                
            # Topics to Review Analysis
            st.markdown("### Topics to Review")
            failed_topics = set()
            for resp in st.session_state.quiz_responses:
                if not resp["is_correct"]:
                    failed_topics.add(resp["topic"])
                    
            if failed_topics:
                st.write("Based on your answers, focus on reviewing these key topics:")
                for ft in failed_topics:
                    st.markdown(f"- ⚠️ **{ft}**")
            else:
                st.success("🟢 Excellent! You answered all questions correctly. No review needed!")
                
            # Detailed response log review
            with st.expander("Review Question Explanations"):
                for idx, resp in enumerate(st.session_state.quiz_responses):
                    marker = "🟢" if resp["is_correct"] else "🔴"
                    st.markdown(f"**{marker} Question {idx + 1}: {resp['question']}**")
                    topic_html = f'<span class="topic-tag">{resp.get("topic", "General")}</span>'
                    diff_html = get_difficulty_badge(resp.get("difficulty", "medium"))
                    st.markdown(f'{topic_html} {diff_html}', unsafe_allow_html=True)
                    st.write(f"- Your Answer: `{resp['user_answer']}`")
                    st.write(f"- Correct Answer: `{resp['correct_answer']}`")
                    st.write(f"- Explanation: {resp['explanation']}")
                    st.markdown("---")
                    
            new_session_btn = st.button("Start New Study Session")
            if new_session_btn:
                st.session_state.quiz_active = False
                st.session_state.quiz_questions = []
                st.session_state.current_q_index = 0
                st.session_state.current_q_answered = False
                st.session_state.quiz_score = 0
                st.session_state.quiz_responses = []
                st.session_state.quiz_db_saved = False
                st.session_state.show_truncation_warning = False
                if "bias_topic" in st.session_state:
                    del st.session_state.bias_topic
                st.rerun()

# ----------------- PAGE 2: Progress Dashboard -----------------
elif page == "📈 Progress Dashboard":
    st.markdown('<div class="main-header">Progress Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Monitor your quiz scores, identify concept-level weaknesses, and observe learning trends.</div>', unsafe_allow_html=True)
    
    if st.session_state.get("filter_topic"):
        col_filt1, col_filt2 = st.columns([5, 1])
        with col_filt1:
            st.info(f"🔍 Currently viewing filtered logs for topic: **{st.session_state.filter_topic}**")
        with col_filt2:
            if st.button("❌ Clear Filter", key="btn_clear_filter"):
                st.session_state.filter_topic = None
                st.rerun()
    
    # Load data
    summary = memory.get_performance_summary(deck_id=st.session_state.get("active_deck_id"))
    history = memory.get_recent_history(limit=50, deck_id=st.session_state.get("active_deck_id"))
    
    if not history:
        st.info("No study history found. Create a quiz in the 'Upload & Study' page to start collecting statistics!")
        
        # Show a visual placeholder graphic/card
        st.markdown("""
        <div style="background-color: #131b2e; padding: 40px; border-radius: 12px; text-align: center; border: 1px dashed #06b6d4;">
            <h3 style="color: #06b6d4;">Start Your Learning Journey</h3>
            <p style="color: #94a3b8; max-width: 500px; margin: 10px auto;">
                Once you generate and submit quizzes, this page will populate with:
            </p>
            <ul style="color: #94a3b8; text-align: left; display: inline-block; margin-top: 10px;">
                <li>Overall progress stats & accuracy metrics</li>
                <li>Visual timelines of your performance improvement</li>
                <li>Focus topics that need closer review</li>
                <li>Detailed history of your quiz sessions</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 1. Stats Overview Section
        st.subheader("Stats Overview")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        # Load advanced stats
        streak = memory.get_streak(deck_id=st.session_state.get("active_deck_id"))
        best_topic_info = memory.get_best_topic(deck_id=st.session_state.get("active_deck_id"))
        improved_topic_info = memory.get_most_improved_topic(deck_id=st.session_state.get("active_deck_id"))
        total_questions = summary["total_questions"]
        
        with col_m1:
            st.metric(
                label="Current Streak",
                value=f"{streak} 🔥" if streak > 0 else "0",
                delta="Consecutive correct" if streak > 0 else None
            )
            
        with col_m2:
            if best_topic_info:
                st.metric(
                    label="Best Topic",
                    value=best_topic_info[0],
                    delta=f"{best_topic_info[1]}% Accuracy"
                )
                if st.button("🔍 Filter Topic", key="btn_filter_best"):
                    st.session_state.filter_topic = best_topic_info[0]
                    st.rerun()
            else:
                st.metric(label="Best Topic", value="N/A")
                
        with col_m3:
            if improved_topic_info:
                st.metric(
                    label="Most Improved Topic",
                    value=improved_topic_info[0],
                    delta=f"+{improved_topic_info[1]}% accuracy increase"
                )
                if st.button("🔍 Filter Topic", key="btn_filter_improved"):
                    st.session_state.filter_topic = improved_topic_info[0]
                    st.rerun()
            else:
                st.metric(label="Most Improved Topic", value="N/A")
                
        with col_m4:
            st.metric(
                label="Total Answered",
                value=total_questions,
                delta="Questions attempted"
            )
            
        st.markdown("---")
        
        # 2. Charts Section
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Accuracy Trend Over Time")
            if st.session_state.get("filter_topic"):
                timeline_data = memory.get_accuracy_over_time_for_topic(st.session_state.filter_topic, deck_id=st.session_state.get("active_deck_id"))
            else:
                timeline_data = memory.get_accuracy_over_time(deck_id=st.session_state.get("active_deck_id"))
                
            if timeline_data:
                df_time = pd.DataFrame(timeline_data)
                df_time["timestamp"] = pd.to_datetime(df_time["timestamp"])
                df_time = df_time.sort_values("timestamp")
                
                title_suffix = f" for '{st.session_state.filter_topic}'" if st.session_state.get("filter_topic") else ""
                fig_timeline = px.line(
                    df_time,
                    x="timestamp",
                    y="accuracy",
                    markers=True,
                    labels={"accuracy": "Accuracy (%)", "timestamp": "Quiz Date & Time"},
                    title=f"Running Accuracy Progression{title_suffix}",
                    color_discrete_sequence=["#06b6d4"]
                )
                fig_timeline.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#f1f5f9',
                    xaxis=dict(showgrid=True, gridcolor='#1e293b'),
                    yaxis=dict(showgrid=True, gridcolor='#1e293b', range=[0, 105])
                )
                st.plotly_chart(fig_timeline, use_container_width=True)
            else:
                st.info("Insufficient history for timeline.")
                
        with col_chart2:
            st.subheader("Topic Mastery Map")
            topic_data = memory.get_topic_stats(deck_id=st.session_state.get("active_deck_id"))
            if topic_data:
                # Build grid layout
                import math
                num_topics = len(topic_data)
                cols = math.ceil(math.sqrt(num_topics)) if num_topics > 0 else 1
                
                rows_data = []
                for idx, t in enumerate(topic_data):
                    x = idx % cols
                    y = idx // cols
                    
                    acc = t["accuracy"]
                    if acc < 40.0:
                        color = "red"
                        hex_color = "#ef4444"
                    elif acc <= 75.0:
                        color = "yellow"
                        hex_color = "#f59e0b"
                    else:
                        color = "green"
                        hex_color = "#10b981"
                        
                    rows_data.append({
                        "topic": t["topic"],
                        "x": x,
                        "y": y,
                        "accuracy": acc,
                        "total_questions": t["total"],
                        "color_cat": color,
                        "hex_color": hex_color,
                        "size": 25 + min(t["total"] * 6, 50)
                    })
                
                df_map = pd.DataFrame(rows_data)
                
                import plotly.graph_objects as go
                fig_map = go.Figure()
                
                categories = [
                    ("green", "Mastered (>75%)", "#10b981"),
                    ("yellow", "Developing (40-75%)", "#f59e0b"),
                    ("red", "Needs Review (<40%)", "#ef4444")
                ]
                
                for cat, label, color_code in categories:
                    df_cat = df_map[df_map["color_cat"] == cat]
                    if not df_cat.empty:
                        fig_map.add_trace(go.Scatter(
                            x=df_cat["x"],
                            y=df_cat["y"],
                            mode="markers+text",
                            text=df_cat["topic"],
                            textposition="bottom center",
                            textfont=dict(color='#ffffff', size=11, family="Outfit, sans-serif"),
                            marker=dict(
                                size=df_cat["size"],
                                color=color_code,
                                line=dict(width=2, color="#ffffff"),
                                opacity=0.9
                            ),
                            hoverinfo="text",
                            hovertext=df_cat.apply(lambda r: f"<b>{r['topic']}</b><br>Accuracy: {r['accuracy']}%<br>Questions: {r['total_questions']}", axis=1),
                            name=label
                        ))
                
                fig_map.update_layout(
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=280,
                    hovermode="closest",
                    clickmode="event+select",
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5,
                        font=dict(color="#f1f5f9", size=9)
                    )
                )
                
                # Render using st.plotly_chart with on_select="rerun"
                selected_data = st.plotly_chart(fig_map, on_select="rerun", use_container_width=True, key="mastery_map_plotly")
                
                # Check for node click selection
                if selected_data and "selection" in selected_data and "points" in selected_data["selection"]:
                    pts = selected_data["selection"]["points"]
                    if pts:
                        pt_x = pts[0].get("x")
                        pt_y = pts[0].get("y")
                        if pt_x is not None and pt_y is not None:
                            match = df_map[(df_map["x"] == pt_x) & (df_map["y"] == pt_y)]
                            if not match.empty:
                                clicked_t = match.iloc[0]["topic"]
                                if st.session_state.get("filter_topic") != clicked_t:
                                    st.session_state.filter_topic = clicked_t
                                    st.rerun()
            else:
                st.info("Insufficient topic history to render map.")

        st.markdown("---")
        
        # Topic Mastery Map details panel
        if st.session_state.get("filter_topic"):
            st.markdown(f'<div style="background-color: #131b2e; padding: 15px; border-radius: 8px; border: 1px solid #3b82f6; margin-bottom: 20px;">'
                        f'<h4 style="margin: 0; color: #3b82f6;">🔍 Selected Topic Mastery Detail: {st.session_state.filter_topic}</h4>'
                        f'<p style="margin: 5px 0 0 0; color: #94a3b8; font-size: 0.9rem;">'
                        f'The charts above and log table below are now filtered to show stats and history specifically for <b>{st.session_state.filter_topic}</b>.'
                        f'</p></div>', unsafe_allow_html=True)
        
        # 3. Topic Strength/Weakness Cards & History Logs
        col_left, col_right = st.columns([1, 2])
        
        with col_left:
            st.subheader("Strengths & Weaknesses")
            
            # Strongest Topics
            st.markdown("🎯 **Strongest Topics (>=70% accuracy)**")
            strong_list = summary.get("strongest_topics", [])
            if strong_list:
                for topic in strong_list:
                    st.success(f"**{topic}**")
            else:
                st.caption("No strong topics logged yet.")
                
            # Weakest Topics
            st.markdown("⚠️ **Weakest Topics (<70% accuracy)**")
            weak_list = summary.get("weakest_topics", [])
            if weak_list:
                for idx, topic in enumerate(weak_list):
                    col_t, col_b = st.columns([3, 2])
                    with col_t:
                        st.error(f"**{topic}**")
                    with col_b:
                        if st.button("💬 Ask Coach", key=f"ask_coach_weak_{idx}", use_container_width=True):
                            st.session_state.current_page = "💬 Study Coach"
                            chat_key = f"coach_chat_history_{active_deck_id}"
                            prefilled_prompt = f"Can you help me understand {topic} better?"
                            if chat_key not in st.session_state:
                                st.session_state[chat_key] = [
                                    {"role": "assistant", "content": f"Hi! I'm your Study Coach for **{active_deck_name}**. Ask me any questions about your notes, or tell me to quiz you on key concepts!"}
                                ]
                            st.session_state[chat_key].append({"role": "user", "content": prefilled_prompt})
                            st.rerun()
            else:
                st.caption("No weak topics logged yet.")
                
        with col_right:
            st.subheader("Recent Answer Logs")
            
            # Filter history locally if filter_topic is active
            if st.session_state.get("filter_topic"):
                filtered_history = [h for h in history if h["topic"] == st.session_state.filter_topic]
            else:
                filtered_history = history
                
            if filtered_history:
                df_history = pd.DataFrame(filtered_history)
                df_history["Date & Time"] = pd.to_datetime(df_history["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
                df_history["Result"] = df_history["is_correct"].apply(lambda x: "🟢 Correct" if x else "🔴 Incorrect")
                
                st.dataframe(
                    df_history[["Date & Time", "topic", "Result"]],
                    column_config={
                        "Date & Time": "Date & Time",
                        "topic": "Topic Covered",
                        "Result": "Result"
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No recent answer logs for this filtered topic.")
            
            # Option to reset database
            st.markdown("<br><br>", unsafe_allow_html=True)
            with st.expander("⚠️ Danger Zone"):
                st.write("Resetting your history will delete all quiz records and database performance stats forever.")
                if st.button("Reset All Quiz History"):
                    conn = memory.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DROP TABLE IF EXISTS quiz_history")
                    conn.commit()
                    conn.close()
                    memory.init_db()
                    if "revision_sheet_content" in st.session_state:
                        del st.session_state.revision_sheet_content
                    st.success("History reset successfully!")
                    st.rerun()
                    
        # 4. Revision Sheet Section (Full Width)
        st.markdown("---")
        st.subheader("📚 Adaptive Revision Sheets")
        st.write("Construct a customized revision guide focusing on concepts where your score is currently below 70%.")
        
        # Pull weak topics using threshold=0.7 (matches weakest list) for the active deck
        weak_topics_to_review = memory.get_weak_topics(threshold=0.7, deck_id=st.session_state.get("active_deck_id"))
        
        generate_sheet_btn = st.button("Generate Revision Sheet")
        
        if generate_sheet_btn:
            if not weak_topics_to_review:
                st.info("ℹ️ You currently have no weak topics to review (accuracy < 70%). Practice more quizzes to collect performance logs!")
            else:
                with st.spinner("Generating personalized revision summary with Gemini..."):
                    try:
                        revision_sheet_md = agent.generate_revision_sheet(weak_topics_to_review)
                        st.session_state.revision_sheet_content = revision_sheet_md
                        
                        # Save to revision sheets library database
                        active_deck_id = st.session_state.get("active_deck_id")
                        if active_deck_id:
                            memory.save_revision_sheet(active_deck_id, revision_sheet_md)
                            st.success("✨ Saved revision sheet to your library!")
                    except agent.GeminiAPIError as e:
                        st.error(f"Failed to generate revision sheet: {e}")
                        
        if "revision_sheet_content" in st.session_state and st.session_state.revision_sheet_content:
            st.markdown('<div class="question-card">', unsafe_allow_html=True)
            st.markdown("### Your Custom Study Sheet")
            st.markdown(st.session_state.revision_sheet_content)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.download_button(
                label="📥 Download Revision Sheet (.md)",
                data=st.session_state.revision_sheet_content,
                file_name="revision_sheet.md",
                mime="text/markdown"
            )

# ----------------- FEATURE DETAIL SUBPAGES -----------------
elif page == "Feature: Adaptive Difficulty":
    col_back, _ = st.columns([1, 6])
    with col_back:
        if st.button("⬅️ Back to Home", key="back_adapt"):
            st.session_state.current_page = "🏠 Home"
            st.rerun()
            
    st.markdown('<div class="main-header">🎯 Adaptive Difficulty</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">How our platform adjusts quiz difficulty based on your performance.</div>', unsafe_allow_html=True)
    
    col_desc, col_vis = st.columns([3, 2])
    with col_desc:
        st.markdown("""
        ### Dynamic Feedback Loop
        Our adaptive difficulty system monitors your answer streaks and recent mistakes on a topic-by-topic basis:
        * **Streaks (Level Up ⬆️):** Answering 3 or more questions correctly in a row on a topic upgrades the target difficulty level to **HARD**.
        * **Mistakes (Level Down ⬇️):** Getting a question incorrect immediately flags the topic and drops the target difficulty level to **EASY**.
        * **Baseline:** All new topics start at a balanced **MEDIUM** difficulty.
        
        This real-time difficulty tailoring ensures that you are constantly challenged without being overwhelmed, maximizing your learning efficiency.
        """)
        if st.button("🚀 Try it now", key="try_adapt"):
            st.session_state.current_page = "📝 Upload & Study"
            st.rerun()
            
    with col_vis:
        st.markdown("""
        <div style="background-color: #131b2e; padding: 24px; border-radius: 12px; border: 1px solid #1e293b; text-align: center;">
            <h4 style="color: #06b6d4; margin-top:0; font-weight:700;">Difficulty Engine Loop</h4>
            <pre style="color: #f1f5f9; text-align: left; font-size: 0.85rem; line-height: 1.4; font-family: monospace;">
   [ Practice Attempt ]
           │
     Correct?  Incorrect?
     ┌─────┴─────┐
     ▼           ▼
[Streak +1]  [Error Logged]
     │           │
Streak >= 3?  Mistake?
     │           │
     ▼           ▼
[Level UP ⬆️] [Level DOWN ⬇️]
 (Hard)       (Easy)
            </pre>
        </div>
        """, unsafe_allow_html=True)

elif page == "Feature: Spaced Repetition Memory":
    col_back, _ = st.columns([1, 6])
    with col_back:
        if st.button("⬅️ Back to Home", key="back_spaced"):
            st.session_state.current_page = "🏠 Home"
            st.rerun()
            
    st.markdown('<div class="main-header">💾 Spaced Repetition Memory</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">How our database engines model and track knowledge retention.</div>', unsafe_allow_html=True)
    
    col_desc, col_vis = st.columns([3, 2])
    with col_desc:
        st.markdown("""
        ### SQLite-Backed Knowledge Modeling
        Spaced repetition uses chronic session tracking to determine when you are most likely to forget a concept:
        * **Granular Logs:** Every time you submit an answer, the topic, correctness status, and exact timestamp are recorded in an SQLite database.
        * **Retention Profiling:** The dashboard pulls these logs to construct a rolling accuracy timeline and calculate your topic-by-topic analytics.
        * **Smart Biasing:** The quiz generator checks this memory, and automatically biases **60% of all future quiz questions** toward your weakest topics.
        
        This prevents you from wasting study time on concepts you have already mastered, focusing your effort on reinforcement.
        """)
        if st.button("🚀 Try it now", key="try_spaced"):
            st.session_state.current_page = "📝 Upload & Study"
            st.rerun()
            
    with col_vis:
        st.markdown("""
        <div style="background-color: #131b2e; padding: 24px; border-radius: 12px; border: 1px solid #1e293b; text-align: center;">
            <h4 style="color: #06b6d4; margin-top:0; font-weight:700;">Memory Engine Pipeline</h4>
            <pre style="color: #f1f5f9; text-align: left; font-size: 0.85rem; line-height: 1.4; font-family: monospace;">
[Answer Logs (SQLite)]
         │
         ▼
[Retention Calculator]
         │
         ▼
[Biased Selection] (60% weight)
         │
         ▼
[New Quiz Generation]
            </pre>
        </div>
        """, unsafe_allow_html=True)

elif page == "Feature: Multi-Agent Review":
    col_back, _ = st.columns([1, 6])
    with col_back:
        if st.button("⬅️ Back to Home", key="back_multi"):
            st.session_state.current_page = "🏠 Home"
            st.rerun()
            
    st.markdown('<div class="main-header">🤖 Multi-Agent Review</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Dual-agent cooperation for grading and explanation refinement.</div>', unsafe_allow_html=True)
    
    col_desc, col_vis = st.columns([3, 2])
    with col_desc:
        st.markdown("""
        ### Collaborative Explanation Critique
        When you submit an incorrect answer, a two-agent team is deployed in the background to ensure you receive a high-quality explanation:
        * **Agent 1 (Drafting):** Analyzes the question and correct response to draft a detailed tutoring explanation.
        * **Agent 2 (Critique & Refiner):** Reviews the draft explanation for accuracy, clarity, tone, and conciseness, correcting and polishing it as needed.
        * **Transparency Expander:** You can view both the draft and final versions under the "See how this explanation was generated" expander to inspect the agent dialogue.
        
        For short-answer questions, a third evaluation agent is used to grade conceptual correctness, accepting typos and synonyms.
        """)
        if st.button("🚀 Try it now", key="try_multi"):
            st.session_state.current_page = "📝 Upload & Study"
            st.rerun()
            
    with col_vis:
        st.markdown("""
        <div style="background-color: #131b2e; padding: 24px; border-radius: 12px; border: 1px solid #1e293b; text-align: center;">
            <h4 style="color: #06b6d4; margin-top:0; font-weight:700;">Multi-Agent Review Loop</h4>
            <pre style="color: #f1f5f9; text-align: left; font-size: 0.85rem; line-height: 1.4; font-family: monospace;">
    [Incorrect Answer]
            │
            ▼
    [Agent 1: Drafting]
            │ (draft_explanation)
            ▼
  [Agent 2: Critique & Polish]
            │ (final_explanation)
            ▼
 [Collapsible UI Diff Expander]
            </pre>
        </div>
        """, unsafe_allow_html=True)

elif page == "Feature: Revision Sheets":
    col_back, _ = st.columns([1, 6])
    with col_back:
        if st.button("⬅️ Back to Home", key="back_sheet"):
            st.session_state.current_page = "🏠 Home"
            st.rerun()
            
    st.markdown('<div class="main-header">📋 Revision Sheets</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Automated targeted concept summaries for weak topics.</div>', unsafe_allow_html=True)
    
    col_desc, col_vis = st.columns([3, 2])
    with col_desc:
        st.markdown("""
        ### Personalized Revision Summary
        Revision sheets compile your weakest areas into a single study document:
        * **Topic Filtering:** Queries SQLite to pull topics with accuracy below 70%.
        * **AI Compilation:** Gemini acts as a senior tutor to generate a concise summary covering only those weak topics (key points, common mistakes, and one example per topic).
        * **Downloadable (.md):** An interactive download button compiles the markdown text into a `.md` file for offline study.
        
        This prevents you from having to look through long slides or textbooks, summarizing exactly what you missed.
        """)
        if st.button("🚀 Try it now", key="try_sheet"):
            st.session_state.current_page = "📈 Progress Dashboard"
            st.rerun()
            
    with col_vis:
        st.markdown("""
        <div style="background-color: #131b2e; padding: 24px; border-radius: 12px; border: 1px solid #1e293b; text-align: center;">
            <h4 style="color: #06b6d4; margin-top:0; font-weight:700;">Revision Sheet Flow</h4>
            <pre style="color: #f1f5f9; text-align: left; font-size: 0.85rem; line-height: 1.4; font-family: monospace;">
 [SQLite DB] ──► [Identify Weak Topics]
                          │
                          ▼
            [Gemini: Compiles Summary]
                          │
                          ▼
            [Interactive Markdown UI]
                          │
                          ▼
            [Downloadable Markdown File]
            </pre>
        </div>
        """, unsafe_allow_html=True)

# ----------------- PAGE: My Decks -----------------
elif page == "🗂️ My Decks":
    st.markdown('<div class="main-header">🗂️ My Subject Decks</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Manage all study decks, view overall performance statistics, and sort subjects by study history or accuracy.</div>', unsafe_allow_html=True)
    
    # Load all decks with stats
    decks_stats = memory.get_all_decks_with_stats()
    
    if not decks_stats:
        st.info("No decks found. Please go to the Home page to create a new study deck.")
        if st.button("➡️ Go to Home Page", key="mydecks_go_home"):
            st.session_state.current_page = "🏠 Home"
            st.rerun()
        st.stop()
        
    # Sort Selector
    st.markdown("### Filter & Sort Decks")
    col_sort1, col_sort2 = st.columns([1, 2])
    with col_sort1:
        sort_by = st.selectbox(
            "Sort Decks By:",
            ["Name (A-Z)", "Name (Z-A)", "Highest Accuracy", "Lowest Accuracy", "Recently Studied", "Oldest Studied"],
            key="mydecks_sort_select"
        )
        
    # Apply sorting
    if sort_by == "Name (A-Z)":
        decks_stats.sort(key=lambda d: d["name"].lower())
    elif sort_by == "Name (Z-A)":
        decks_stats.sort(key=lambda d: d["name"].lower(), reverse=True)
    elif sort_by == "Highest Accuracy":
        decks_stats.sort(key=lambda d: d["accuracy"], reverse=True)
    elif sort_by == "Lowest Accuracy":
        decks_stats.sort(key=lambda d: d["accuracy"])
    elif sort_by == "Recently Studied":
        decks_stats.sort(key=lambda d: d["last_studied"] or "", reverse=True)
    elif sort_by == "Oldest Studied":
        decks_stats.sort(key=lambda d: d["last_studied"] or "")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Render table list / grid view of decks
    for d in decks_stats:
        d_id = d["id"]
        name = d["name"]
        created = d["created_at"]
        total_q = d["total_questions"]
        accuracy = d["accuracy"]
        last_std = d["last_studied"]
        
        is_active = (st.session_state.get("active_deck_id") == d_id)
        border_c = "#06b6d4" if is_active else "#1e293b"
        active_label = "🟢 Currently Active" if is_active else "📁 Click to Activate"
        
        # Display deck card
        st.markdown(f"""
        <div style="background-color: #131b2e; padding: 20px; border-radius: 10px; border: 1px solid {border_c}; margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="color: #ffffff; margin: 0; font-weight:700;">📂 {name}</h3>
                <span style="color: #94a3b8; font-size: 0.8rem;">Created: {created[:10] if created else "N/A"}</span>
            </div>
            <div style="margin-top: 10px; display: flex; gap: 30px;">
                <div><span style="color: #94a3b8; font-size: 0.85rem;">Questions Logged:</span> <b style="color: #ffffff;">{total_q}</b></div>
                <div><span style="color: #94a3b8; font-size: 0.85rem;">Overall Accuracy:</span> <b style="color: #06b6d4;">{accuracy}%</b></div>
                <div><span style="color: #94a3b8; font-size: 0.85rem;">Last Studied:</span> <b style="color: #ffffff;">{last_std[:16] if last_std else "Never"}</b></div>
            </div>
            <div style="margin-top: 10px; color: #06b6d4; font-size: 0.85rem; font-weight: 700;">
                {active_label}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action Buttons: Activate and Delete
        col_act1, col_act2, col_act3 = st.columns([2, 2, 4])
        with col_act1:
            if not is_active:
                if st.button(f"Activate {name}", key=f"mydeck_act_{d_id}", use_container_width=True):
                    st.session_state.active_deck_id = d_id
                    st.session_state.active_deck_name = name
                    st.session_state.quiz_active = False
                    st.session_state.quiz_questions = []
                    st.session_state.filter_topic = None
                    st.rerun()
            else:
                st.button("Active Subject", key=f"mydeck_act_disabled_{d_id}", disabled=True, use_container_width=True)
        with col_act2:
            with st.popover("Delete Deck 🗑️", key=f"pop_del_{d_id}", use_container_width=True):
                st.warning(f"Delete '{name}'?")
                st.caption("This action is permanent and deletes all history logs and revision sheets.")
                if st.button("Yes, Delete", key=f"mydeck_del_{d_id}", use_container_width=True):
                    try:
                        memory.delete_deck(d_id)
                        if st.session_state.get("active_deck_id") == d_id:
                            st.session_state.active_deck_id = None
                            st.session_state.active_deck_name = None
                        st.success(f"Deck '{name}' deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

# ----------------- PAGE: Revision Sheets Library -----------------
elif page == "📚 Revision Sheets":
    st.markdown('<div class="main-header">📚 Revision Sheets Library</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Access and download your complete historical library of custom revision sheets generated by the Multi-Agent Review model.</div>', unsafe_allow_html=True)
    
    # Check if a deck is active
    active_deck_id = st.session_state.get("active_deck_id")
    if not active_deck_id:
        st.warning("Please select or create a subject deck to access revision sheets.")
        st.stop()
        
    # Option to generate a new sheet right here
    st.subheader("Generate New Revision Guide")
    weak_topics_to_review = memory.get_weak_topics(threshold=0.7, deck_id=active_deck_id)
    if not weak_topics_to_review:
        st.info("ℹ️ You currently have no weak topics to review (accuracy < 70% in active deck). Keep practicing quizzes to track weaknesses!")
    else:
        st.write(f"Detected {len(weak_topics_to_review)} weak concepts: **{', '.join(weak_topics_to_review)}**")
        if st.button("🚀 Generate New Revision Sheet", key="lib_sheet_generate"):
            with st.spinner("Compiling revision guide..."):
                try:
                    sheet_md = agent.generate_revision_sheet(weak_topics_to_review)
                    memory.save_revision_sheet(active_deck_id, sheet_md)
                    st.success("New revision sheet generated and saved to your library!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating sheet: {e}")
                    
    st.markdown("---")
    
    # Load all sheets for active deck
    saved_sheets = memory.get_revision_sheets(deck_id=active_deck_id)
    
    if not saved_sheets:
        st.info("No saved revision sheets found for this deck. Generate one above to get started!")
    else:
        st.subheader("Your Revision Guide Library")
        
        # Display list of sheets
        for idx, s in enumerate(saved_sheets):
            created_time = s["created_at"]
            sheet_id = s["id"]
            
            with st.expander(f"📄 Revision Sheet - Generated on {created_time[:16]}", expanded=(idx == 0)):
                st.markdown(s["content"])
                
                col_down1, col_down2, col_down3 = st.columns([3, 3, 4])
                with col_down1:
                    st.download_button(
                        label="📥 Download Markdown (.md)",
                        data=s["content"],
                        file_name=f"revision_sheet_{created_time[:10]}.md",
                        mime="text/markdown",
                        key=f"dl_btn_{sheet_id}"
                    )
                with col_down2:
                    if st.button("🗑️ Delete from Library", key=f"del_sheet_btn_{sheet_id}", use_container_width=True):
                        memory.delete_revision_sheet(sheet_id)
                        st.success("Revision sheet deleted.")
                        st.rerun()

# ----------------- PAGE: Achievements -----------------
elif page == "🏆 Achievements":
    st.markdown('<div class="main-header">🏆 Your Achievements & Badges</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Track your learning achievements and unlock unique master badges by practicing quizzes regularly and mastering complex concepts.</div>', unsafe_allow_html=True)
    
    # Load calculated achievements
    badges = memory.get_achievements()
    
    # Display in a beautiful grid
    col_badge1, col_badge2, col_badge3 = st.columns(3)
    
    # Badge 1: 7-Day Streak
    with col_badge1:
        streak_earned = badges["streak_7_day"]["earned"]
        opacity = "1.0" if streak_earned else "0.3"
        filter_gray = "" if streak_earned else "filter: grayscale(100%);"
        border_color = "#f59e0b" if streak_earned else "#334155"
        
        st.markdown(f"""
        <div style="background-color: #131b2e; padding: 25px; border-radius: 12px; border: 2px solid {border_color}; text-align: center; opacity: {opacity}; {filter_gray}">
            <div style="font-size: 3.5rem; margin-bottom: 10px;">🔥</div>
            <h3 style="color: #ffffff; margin: 0; font-weight:700;">7-Day Streak</h3>
            <p style="color: #94a3b8; font-size: 0.85rem; min-height: 50px; margin-top: 8px;">
                {badges['streak_7_day']['detail']}
            </p>
            <div style="margin-top: 15px; font-weight: 700; color: {'#10b981' if streak_earned else '#64748b'};">
                {'🔓 UNLOCKED' if streak_earned else '🔒 LOCKED'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Badge 2: Topic Master
    with col_badge2:
        master_earned = badges["topic_master"]["earned"]
        opacity = "1.0" if master_earned else "0.3"
        filter_gray = "" if master_earned else "filter: grayscale(100%);"
        border_color = "#10b981" if master_earned else "#334155"
        
        st.markdown(f"""
        <div style="background-color: #131b2e; padding: 25px; border-radius: 12px; border: 2px solid {border_color}; text-align: center; opacity: {opacity}; {filter_gray}">
            <div style="font-size: 3.5rem; margin-bottom: 10px;">👑</div>
            <h3 style="color: #ffffff; margin: 0; font-weight:700;">Topic Master</h3>
            <p style="color: #94a3b8; font-size: 0.85rem; min-height: 50px; margin-top: 8px;">
                {badges['topic_master']['detail']}
            </p>
            <div style="margin-top: 15px; font-weight: 700; color: {'#10b981' if master_earned else '#64748b'};">
                {'🔓 UNLOCKED' if master_earned else '🔒 LOCKED'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Badge 3: Comeback Kid
    with col_badge3:
        comeback_earned = badges["comeback_kid"]["earned"]
        opacity = "1.0" if comeback_earned else "0.3"
        filter_gray = "" if comeback_earned else "filter: grayscale(100%);"
        border_color = "#3b82f6" if comeback_earned else "#334155"
        
        st.markdown(f"""
        <div style="background-color: #131b2e; padding: 25px; border-radius: 12px; border: 2px solid {border_color}; text-align: center; opacity: {opacity}; {filter_gray}">
            <div style="font-size: 3.5rem; margin-bottom: 10px;">🚀</div>
            <h3 style="color: #ffffff; margin: 0; font-weight:700;">Comeback Kid</h3>
            <p style="color: #94a3b8; font-size: 0.85rem; min-height: 50px; margin-top: 8px;">
                {badges['comeback_kid']['detail']}
            </p>
            <div style="margin-top: 15px; font-weight: 700; color: {'#10b981' if comeback_earned else '#64748b'};">
                {'🔓 UNLOCKED' if comeback_earned else '🔒 LOCKED'}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ----------------- PAGE: Study Coach -----------------
elif page == "💬 Study Coach":
    st.markdown('<div class="main-header">💬 AI Study Coach</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Chat with your AI Coach to ask questions, clarify confusing concepts, or get quizzed on your notes.</div>', unsafe_allow_html=True)
    
    # Check if a deck is active
    active_deck_id = st.session_state.get("active_deck_id")
    active_deck_name = st.session_state.get("active_deck_name")
    
    if not active_deck_id:
        st.warning("Please select or create a subject deck first to chat with your Study Coach.")
        st.stop()
        
    # Get active deck details
    active_deck = memory.get_deck(active_deck_id)
    if not active_deck or not active_deck.get("source_text"):
        st.warning("No notes found for the active deck. Please go to the Upload & Study page to add notes first.")
        st.stop()
        
    st.info(f"📚 **Coach context preloaded with deck:** `{active_deck_name}`")
    
    # Initialize chat history key specific to active deck
    chat_key = f"coach_chat_history_{active_deck_id}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = [
            {"role": "assistant", "content": f"Hi! I'm your Study Coach for **{active_deck_name}**. Ask me any questions about your notes, or tell me to quiz you on key concepts!"}
        ]
        
    # Clear conversation button in a neat column alignment
    col_chat1, col_chat2 = st.columns([8, 2])
    with col_chat2:
        if st.button("Clear Chat 🗑️", use_container_width=True):
            st.session_state[chat_key] = [
                {"role": "assistant", "content": f"Hi! I'm your Study Coach for **{active_deck_name}**. Ask me any questions about your notes, or tell me to quiz you on key concepts!"}
            ]
            st.rerun()
            
    # Render chat messages from history
    for msg in st.session_state[chat_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Check if last message is from user (which triggers coach generation loop)
    if st.session_state[chat_key][-1]["role"] == "user":
        user_msg_text = st.session_state[chat_key][-1]["content"]
        with st.chat_message("assistant"):
            with st.spinner("Coach is thinking..."):
                try:
                    coach_response = agent.chat_with_coach(
                        user_message=user_msg_text,
                        deck_context=active_deck["source_text"],
                        chat_history=st.session_state[chat_key][:-1]
                    )
                except Exception as e:
                    coach_response = f"Sorry, I had trouble thinking of a response: {e}"
            st.markdown(coach_response)
        st.session_state[chat_key].append({"role": "assistant", "content": coach_response})
        st.rerun()
            
    # Chat input for user message
    user_input = st.chat_input(f"Ask your coach about {active_deck_name}...")
    if user_input:
        st.session_state[chat_key].append({"role": "user", "content": user_input})
        st.rerun()
