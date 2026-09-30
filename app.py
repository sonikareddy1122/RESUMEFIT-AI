import os
import re
import tempfile

import pandas as pd
import streamlit as st
from joblib import load

from src.resume_parser import extract_resume_text
from src.skill_extractor import extract_skills
from src.profile_extractor import extract_candidate_profile
from src.job_recommender import recommend_jobs
from src.resume_score import calculate_resume_score
from src.job_description_matcher import extract_jd_skills, compare_resume_with_jd
from src.resume_analyzer import (
    extract_projects as extract_projects_with_relevance,
    score_breakdown,
)
from database.database import (
    insert_candidates,
    get_all_candidates,
    search_candidates,
    delete_candidate,
    delete_all_candidates,
)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ResumeFit AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

USERS = {
    "admin": "admin123",
    "user": "user123",
}

CITIES = [
    "Hyderabad",
    "Bangalore",
    "Bengaluru",
    "Chennai",
    "Pune",
    "Mumbai",
    "Delhi",
    "Warangal",
    "Kolkata",
    "Noida",
    "Gurgaon",
    "Gurugram",
    "Ahmedabad",
]

COMPLETENESS_SECTIONS = [
    ("Contact Information", r"(email|@|phone|mobile|\+91)"),
    ("Education", r"(education|b\.tech|bachelor|master|university|college|degree)"),
    ("Skills", r"(skills|python|sql|java|technical skills)"),
    ("Projects", r"(project|projects)"),
    ("Certifications", r"(certification|certified|certificate)"),
    ("Work Experience", r"(experience|internship|intern|worked as|employment)"),
]

THEME_CSS = """
<style>
    #MainMenu, footer, header, [data-testid="stSidebar"],
    [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
    }
    .stApp {
        background: #07111f;
        color: #e8eefc;
    }
    .block-container {
        padding: 0.6rem 1.1rem 1rem 1.1rem;
        max-width: 100% !important;
        width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.45rem;
    }
    .login-wrap {
        max-width: 420px;
        margin: 8vh auto 0 auto;
        background: linear-gradient(180deg, #12233a, #0d1b2e);
        border: 1px solid #1f3657;
        border-radius: 18px;
        padding: 28px 28px 18px 28px;
        box-shadow: 0 20px 50px rgba(0,0,0,.35);
    }
    .login-wrap h1 {
        font-size: 1.45rem;
        margin: 0 0 6px 0;
        color: #fff;
    }
    .login-wrap p {
        color: #93a4c7;
        margin: 0 0 18px 0;
        font-size: 0.92rem;
    }
    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #0b1729;
        border: 1px solid #1a2d4a;
        border-radius: 14px;
        padding: 10px 14px;
        margin-bottom: 10px;
    }
    
    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-mark {
        width: 44px;
        height: 44px;
        min-width: 44px;
        border-radius: 10px;
        background: linear-gradient(135deg, #2ee6a6, #1aa8ff);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
    }

    .brand h1 {
        margin: 0;
        padding: 0;
        font-size: 1.6rem;
        font-weight: 800;
        line-height: 1.2;
        color: #fff;
    }

    .brand-name {
        font-size: 30px;
        font-weight: 800;
    }   

    .brand span {
        display: block;
        color: #8ea0c3;
        font-size: 0.75rem;
        font-weight: 400;
        margin-top: 3px;
    }
    /* Keep the navigation compact; do not force it to fill the viewport. */
    .nav-card {
        background: #0b1729;
        border: 1px solid #1a2d4a;
        border-radius: 16px;
        padding: 12px 10px 16px 10px;
        min-height: 0;
        height: auto;
    }
    .hint-box {
        margin-top: 18px;
        background: #10213a;
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 12px;
        color: #9db1d6;
        font-size: 0.82rem;
    }
    .kpi-row, .grid, .two, .three {
        display: grid;
        gap: 12px;
    }
    .kpi-row { grid-template-columns: repeat(4, 1fr); }
    .two { grid-template-columns: 1.1fr 2.2fr; }
    .three { grid-template-columns: 1.15fr 1.15fr 1fr; }
    .card {
        background: #10203a;
        border: 1px solid #1d3558;
        border-radius: 14px;
        padding: 14px 16px;
    }
    .kpi .label { color: #93a4c7; font-size: 0.8rem; }
    .kpi .value { color: #fff; font-size: 1.55rem; font-weight: 700; margin-top: 6px; }
    .kpi .sub { color: #7f93b8; font-size: 0.75rem; margin-top: 4px; }
    .pill {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 3px 10px;
        font-size: 0.72rem;
        font-weight: 700;
        margin-left: 8px;
    }
    .strong { background: #123f33; color: #2ee6a6; }
    .good { background: #16324f; color: #5ec8ff; }
    .partial { background: #3d3014; color: #ffc14d; }
    .low { background: #3d1822; color: #ff6b81; }
    .must { background: #3d1822; color: #ff6b81; }
    .nice { background: #123f33; color: #2ee6a6; }
    .opt { background: #1a2740; color: #93a4c7; }
    .matched { background: #123f33; color: #2ee6a6; }
    .missing { background: #3d1822; color: #ff6b81; }
    .partial-skill { background: #3d3014; color: #ffc14d; }
    .cand {
        width: 100%;
        text-align: left;
        border: 1px solid #1d3558;
        background: #0e1c33;
        color: #d7e3fb;
        border-radius: 12px;
        padding: 10px 12px;
        margin-bottom: 8px;
    }
    .cand.active {
        border-color: #2ee6a6;
        box-shadow: 0 0 0 1px #2ee6a6 inset;
        background: #102c28;
    }
    .rank {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.72rem;
        font-weight: 800;
        margin-right: 8px;
        background: #1a2d4a;
    }
    .r1 { background: #2ee6a6; color: #062018; }
    .r2 { background: #3aa0ff; color: #04121f; }
    .r3 { background: #f0b429; color: #241600; }
    .section-title {
        color: #fff;
        font-size: 1.15rem;
        margin: 0;
    }
    .muted { color: #8ea0c3; font-size: 0.85rem; }
    .bar {
        height: 8px;
        background: #1a2d4a;
        border-radius: 999px;
        overflow: hidden;
        margin-top: 8px;
    }
    .bar > div {
        height: 100%;
        background: linear-gradient(90deg, #2ee6a6, #1aa8ff);
    }
    .heat {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px solid #1a2d4a;
        font-size: 0.86rem;
    }
    .legend { color: #93a4c7; font-size: 0.82rem; margin: 4px 0 8px 0; }
    .empty {
        text-align: center;
        padding: 46px 16px;
        color: #93a4c7;
        background: #10203a;
        border: 1px dashed #27466f;
        border-radius: 16px;
    }
    .donut-wrap {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .donut {
        width: 118px;
        height: 118px;
        border-radius: 50%;
        display: grid;
        place-items: center;
        position: relative;
    }
    .donut::after {
        content: "";
        position: absolute;
        width: 78px;
        height: 78px;
        background: #10203a;
        border-radius: 50%;
    }
    .donut span {
        position: relative;
        z-index: 1;
        font-weight: 800;
        color: #fff;
    }
    .req-row, .ev-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 7px 0;
        border-bottom: 1px solid #1a2d4a;
        font-size: 0.86rem;
    }
    .tiny { font-size: 0.78rem; color: #9db1d6; }
    button[kind="secondary"] {
        background: #12233a !important;
        border: 1px solid #1f3657 !important;
        color: #d7e3fb !important;
    }
    @media (max-width: 1100px) {
        .kpi-row, .two, .three { grid-template-columns: 1fr; }
    }
</style>
"""


# ============================================================
# STATE
# ============================================================

def init_state():
    defaults = {
        "authenticated": False,
        "username": "",
        "sidebar_open": True,
        "page": "Dashboard",
        "job_description": "",
        "target_job": "Data Analyst",
        "candidate_location": "Hyderabad",
        "screened_candidates": [],
        "selected_candidate": None,
        "processing_errors": [],
        "detail_tab": "Overview",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================
# MODELS
# ============================================================

MODEL_PATH = os.path.join("models", "resume_model.pkl")
TFIDF_PATH = os.path.join("models", "tfidf_vectorizer.pkl")
ENCODER_PATH = os.path.join("models", "encoder.pkl")


@st.cache_resource
def load_models():
    if not (
        os.path.exists(MODEL_PATH)
        and os.path.exists(TFIDF_PATH)
        and os.path.exists(ENCODER_PATH)
    ):
        return None, None, None
    return load(MODEL_PATH), load(TFIDF_PATH), load(ENCODER_PATH)


def get_models():
    try:
        return load_models()
    except Exception:
        return None, None, None


# ============================================================
# HELPERS
# ============================================================

def match_label(score):
    if score >= 75:
        return "Strong Match", "strong"
    if score >= 60:
        return "Good Match", "good"
    if score >= 45:
        return "Partial Match", "partial"
    return "Low Match", "low"


def extract_location(text, fallback):
    lower = text.lower()
    for city in CITIES:
        if city.lower() in lower:
            return "Bangalore" if city.lower() in {"bengaluru"} else (
                "Gurgaon" if city.lower() == "gurugram" else city
            )
    return fallback


def extract_candidate_name(text, fallback):
    for raw in text.splitlines()[:12]:
        line = re.sub(r"\s+", " ", raw).strip()
        if not line or "@" in line or re.search(r"\d{8,}", line):
            continue
        if re.search(r"(resume|curriculum|objective|profile|skills)", line, re.I):
            continue
        words = line.split()
        if 1 < len(words) <= 4 and all(w.replace(".", "").isalpha() for w in words):
            return line.title()
    return fallback


def section_text(text, heading):
    pattern = rf"{heading}\s*[:\-]?\s*(.*?)(?=\n[A-Z][A-Za-z ]{{2,30}}\s*$|\Z)"
    match = re.search(pattern, text, re.I | re.S | re.M)
    return match.group(1).strip() if match else ""


def extract_projects(text, required_skills=None):
    return extract_projects_with_relevance(text, required_skills or [])

def extract_certifications(text):
    blob = section_text(text, r"certifications?")
    if not blob:
        return []
    items = [re.sub(r"^[\-\*\u2022\d\.\s]+", "", line).strip() for line in blob.splitlines()]
    return [item for item in items if 3 < len(item) < 80][:6]


def resume_completeness(text):
    found = []
    missing = []
    for label, pattern in COMPLETENESS_SECTIONS:
        if re.search(pattern, text, re.I):
            found.append(label)
        else:
            missing.append(label)
    total = len(COMPLETENESS_SECTIONS)
    percent = round(100 * len(found) / total) if total else 0
    return found, missing, percent


def jd_priority(skills):
    rows = []
    for index, skill in enumerate(skills):
        if index < 3:
            level, css = "Must Have", "must"
        elif index < 5:
            level, css = "Good to Have", "nice"
        else:
            level, css = "Optional", "opt"
        rows.append((skill, level, css))
    return rows


def heatmap_status(skill, resume_skills, resume_text):
    lower_skills = {s.lower() for s in resume_skills}
    if skill.lower() in lower_skills:
        return "Matched", "matched"
    token = skill.lower()
    if token in resume_text.lower():
        return "Partial", "partial-skill"
    return "Missing", "missing"


def keyword_coverage(job_description, resume_text):
    words = re.findall(r"[A-Za-z]{4,}", job_description.lower())
    unique = []
    stop = {"with", "from", "that", "this", "have", "will", "your", "about", "into", "using"}
    for word in words:
        if word not in unique and word not in stop:
            unique.append(word)
    unique = unique[:20]
    if not unique:
        return 0, 0, 0
    found = sum(1 for word in unique if word in resume_text.lower())
    return found, len(unique), round(100 * found / len(unique))


def experience_evidence(skills, resume_text):
    rows = []
    lower = resume_text.lower()
    skills_blob = section_text(resume_text, r"skills?")
    projects_blob = section_text(resume_text, r"projects?")
    for skill in skills[:6]:
        token = skill.lower()
        places = []
        if token in skills_blob.lower():
            places.append("Skills")
        if token in projects_blob.lower():
            places.append("Projects")
        if not places and token in lower:
            places.append("Resume")
        if places:
            rows.append((skill, "Found in " + " + ".join(places), True))
        else:
            rows.append((skill, "Not found in resume", False))
    return rows




def recommendation_from_scores(prediction, jd_match, resume_score):
    if prediction:
        return prediction
    blended = (float(jd_match) + float(resume_score)) / 2
    if blended >= 75:
        return "Highly Recommended"
    if blended >= 55:
        return "Recommended"
    return "Not Recommended"


def process_job_recommendations(job_recommendations, target_job):
    top_job_role = target_job
    target_job_match = 0
    items = []

    if isinstance(job_recommendations, dict):
        iterable = job_recommendations.items()
        for role, value in iterable:
            if isinstance(value, dict):
                score = value.get("Skill Match", value.get("Match Percentage", value.get("Score", 0)))
            else:
                score = value
            try:
                score = float(score)
            except Exception:
                score = 0
            items.append((role, score))
    elif isinstance(job_recommendations, list):
        for item in job_recommendations:
            if isinstance(item, dict):
                role = item.get("Job Role") or item.get("Role") or item.get("Job") or target_job
                score = item.get("Skill Match") or item.get("Match Percentage") or item.get("Score") or 0
                try:
                    score = float(score)
                except Exception:
                    score = 0
                items.append((role, score))

    if items:
        items.sort(key=lambda x: x[1], reverse=True)
        top_job_role = items[0][0]
        for role, score in items:
            if role == target_job:
                target_job_match = score
        if target_job_match == 0:
            target_job_match = items[0][1]
    return top_job_role, target_job_match


def screen_resumes(uploaded_files, job_description, target_job, candidate_location):
    model, _tfidf, _encoder = get_models()
    jd_skills = extract_jd_skills(job_description) if job_description.strip() else []
    records = []
    errors = []
    progress = st.progress(0)
    status = st.empty()

    for index, uploaded_file in enumerate(uploaded_files):
        status.write(f"Processing {uploaded_file.name}...")
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                temp_path = temp_file.name

            resume_text = extract_resume_text(temp_path)
            if not resume_text.strip():
                raise ValueError("No readable text found in the PDF.")

            candidate_skills = extract_skills(resume_text)
            profile = extract_candidate_profile(resume_text)
            education = profile.get("Education", "Not Specified")
            experience_level = profile.get("Experience_Level") or profile.get("Experience Level", "Fresher")

            experience_years = 0
            experience_matches = re.findall(r"(\d+)\+?\s*(?:years?|yrs?)", resume_text.lower())
            if experience_matches:
                experience_years = max(int(x) for x in experience_matches)

            location = extract_location(resume_text, candidate_location)
            fallback_name = os.path.splitext(uploaded_file.name)[0]
            candidate_name = extract_candidate_name(resume_text, fallback_name)

            prediction = None
            ai_probability = 0
            if model is not None:
                model_input = pd.DataFrame([{
                    "Education": education,
                    "Experience_Level": experience_level,
                    "Experience_Years": experience_years,
                    "Skills": " ".join(candidate_skills),
                    "Target_Job": target_job,
                    "Location": location,
                }])
                try:
                    prediction = model.predict(model_input)[0]
                    probabilities = model.predict_proba(model_input)[0]
                    ai_probability = round(max(probabilities) * 100, 2)
                except Exception:
                    prediction = None

            job_recommendations = recommend_jobs(candidate_skills)
            top_job_role, target_job_match = process_job_recommendations(
                job_recommendations, target_job
            )

            resume_score_result = calculate_resume_score(
                candidate_skills, education, experience_years, target_job_match
            )
            if isinstance(resume_score_result, dict):
                resume_score = float(resume_score_result.get("Total Score", 0))
                skills_part = float(resume_score_result.get("Skills Score", 0))
                experience_part = float(resume_score_result.get("Experience Score", 0))
                education_part = float(resume_score_result.get("Education Score", 0))
                jd_part = float(resume_score_result.get("Job Match Score", 0))
                suggestions = resume_score_result.get("Suggestions", [])
            else:
                resume_score = float(resume_score_result or 0)
                skills_part = experience_part = education_part = jd_part = 0
                suggestions = []

            jd_result = compare_resume_with_jd(candidate_skills, jd_skills)
            jd_match = float(jd_result.get("Match Percentage", 0))
            matched_skills = jd_result.get("Matched Skills", [])
            missing_skills = jd_result.get("Missing Skills", [])

            found_sections, missing_sections, complete_pct = resume_completeness(resume_text)
            projects = extract_projects(resume_text, jd_skills)
            certifications = extract_certifications(resume_text)
            found_kw, total_kw, kw_pct = keyword_coverage(job_description, resume_text)
            evidence = experience_evidence(jd_skills or candidate_skills, resume_text)
            relevance = [
                (project.get("name", ""), int(project.get("relevance", 0)))
                for project in projects
                if isinstance(project, dict)
            ]
            rec = recommendation_from_scores(prediction, jd_match, resume_score)

            # Match the old score-breakdown behavior without changing the
            # resume score returned by calculate_resume_score.
            project_score = min(12, 4 + len(projects) * 3)
            breakdown = score_breakdown(
                skills_part,
                experience_part,
                education_part,
                project_score,
                jd_part,
            )

            records.append({
                "Candidate": candidate_name,
                "Resume File": uploaded_file.name,
                "Education": education,
                "Experience": experience_years,
                "Experience Level": experience_level,
                "Location": location,
                "Skills": len(candidate_skills),
                "Skill List": candidate_skills,
                "Resume Score": round(resume_score, 2),
                "JD Match": round(jd_match, 2),
                "Recommendation": rec,
                "Top Job Role": top_job_role,
                "AI Probability": ai_probability,
                "Matched Skills": matched_skills,
                "Missing Skills": missing_skills,
                "Score Breakdown": breakdown,
                "Projects": projects,
                "Certifications": certifications,
                "Complete Sections": found_sections,
                "Missing Sections": missing_sections,
                "Completeness": complete_pct,
                "Keyword Found": found_kw,
                "Keyword Total": total_kw,
                "Keyword Coverage": kw_pct,
                "Evidence": evidence,
                "Project Relevance": relevance,
                "Suggestions": suggestions,
                "JD Skills": jd_skills,
                "Resume Text": resume_text,
            })
        except Exception as error:
            errors.append({"Resume": uploaded_file.name, "Error": str(error)})
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
        progress.progress((index + 1) / max(len(uploaded_files), 1))

    status.empty()
    progress.empty()

    if records:
        records.sort(key=lambda item: item["JD Match"], reverse=True)
        try:
            insert_candidates(records)
        except Exception as error:
            errors.append({"Database": "Save failed", "Error": str(error)})

    return records, errors


def ranked_candidates():
    rows = list(st.session_state.screened_candidates)
    rows.sort(key=lambda x: x.get("JD Match", 0), reverse=True)
    return rows


# ============================================================
# UI BUILDING BLOCKS
# ============================================================

def inject_css():
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def render_login():
    st.markdown(
        """
        <div class="login-wrap">
            <div class="brand">
                <div class="brand-mark">📄</div>
                <div>
                    <h2 class="brand-name">ResumeFit AI</h2>
                    <span>Login</span>
                </div>
            </div>
            <h1 style="margin-top:18px">Welcome back</h1>
            <p>Sign in to screen resumes against a job description.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)
        if submitted:
            if USERS.get(username.strip()) == password:
                st.session_state.authenticated = True
                st.session_state.username = username.strip()
                st.rerun()
            st.error("Invalid username or password.")
    st.caption("Demo accounts: `admin` / `admin123`  ·  `user` / `user123`")


def topbar():
    left, mid, right = st.columns([0.12, 0.58, 0.3])
    with left:
        label = "Close menu" if st.session_state.sidebar_open else "Open menu"
        if st.button(label, use_container_width=True):
            st.session_state.sidebar_open = not st.session_state.sidebar_open
            st.rerun()
    with mid:
        st.markdown(
            """
            <div class="brand" style="padding-top:6px">
                <div class="brand-mark">📄</div>
                <div>
                    <h2 class="brand-name">ResumeFit AI</h2>
                    <span>Find the right talent, faster</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        c1, c2 = st.columns(2)
        with c1:
            rows = ranked_candidates()
            if rows:
                csv_data = pd.DataFrame([{
                    "Candidate": r["Candidate"],
                    "JD Match": r["JD Match"],
                    "Resume Score": r["Resume Score"],
                    "Recommendation": r["Recommendation"],
                    "Education": r["Education"],
                    "Location": r["Location"],
                } for r in rows]).to_csv(index=False)
                st.download_button(
                    "Download Report",
                    data=csv_data,
                    file_name="screening_report.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        with c2:
            if st.button("Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.username = ""
                st.rerun()


def nav_button(label, page_key):
    active = st.session_state.page == page_key
    if st.button(("●  " if active else "○  ") + label, use_container_width=True, key=f"nav_{page_key}"):
        st.session_state.page = page_key
        st.rerun()


def sidebar_nav():
    # Use a native Streamlit container instead of opening/closing an HTML
    # div around Streamlit widgets. Streamlit renders each widget in its
    # own element, so raw HTML wrappers do not reliably contain them.
    with st.container():
        nav_button("Dashboard", "Dashboard")
        nav_button("Upload Resumes", "Upload Resumes")
        nav_button("Job Description", "Job Description")
        nav_button("Screening Results", "Screening Results")
        st.markdown(
            """
            <div class="hint-box">
                <b>Smarter Screening</b><br/>
                AI-powered insights.
            </div>
            """,
            unsafe_allow_html=True,
        )


def empty_state(message):
    st.markdown(f'<div class="empty">{message}</div>', unsafe_allow_html=True)


# ============================================================
# PAGES
# ============================================================

def page_dashboard():
    rows = ranked_candidates()
    jd_skills = extract_jd_skills(st.session_state.job_description) if st.session_state.job_description.strip() else []
    total = len(rows)
    top_score = max((r["JD Match"] for r in rows), default=None)
    avg_match = round(sum(r["JD Match"] for r in rows) / total, 1) if total else None
    top_name = rows[0]["Candidate"] if rows else ""

    st.markdown(
        f"""
        <div class="kpi-row">
            <div class="card kpi"><div class="label">Total Candidates</div>
            <div class="value">{total if total else "0"}</div>
            <div class="sub">From this session only</div></div>
            <div class="card kpi"><div class="label">Top Match Score</div>
            <div class="value">{f"{top_score:.0f}%" if top_score is not None else "--"}</div>
            <div class="sub">{top_name or "No candidates screened yet"}</div></div>
            <div class="card kpi"><div class="label">Avg. JD Match</div>
            <div class="value">{f"{avg_match:.0f}%" if avg_match is not None else "--"}</div>
            <div class="sub">Across screened resumes</div></div>
            <div class="card kpi"><div class="label">Required Skills (from JD)</div>
            <div class="value">{len(jd_skills)}</div>
            <div class="sub">{"Paste a job description to detect skills" if not jd_skills else ", ".join(jd_skills[:6])}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")


    chart_df = pd.DataFrame({
        "Candidate": [r["Candidate"] for r in rows],
        "JD Match": [r["JD Match"] for r in rows],
        "Resume Score": [r["Resume Score"] for r in rows],
    })
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### JD Match by candidate")
        st.bar_chart(chart_df.set_index("Candidate")["JD Match"], height=280)
    with c2:
        st.markdown("#### Resume score by candidate")
        st.bar_chart(chart_df.set_index("Candidate")["Resume Score"], height=280)

    st.markdown("#### Recent screening records")
    st.dataframe(
        pd.DataFrame([{
            "Candidate": r["Candidate"],
            "JD Match": r["JD Match"],
            "Resume Score": r["Resume Score"],
            "Recommendation": r["Recommendation"],
            "Education": r["Education"],
            "Experience Level": r["Experience Level"],
            "Location": r["Location"],
        } for r in rows]),
        use_container_width=True,
        hide_index=True,
    )

    # Load persistent database records independently of the current session.
    # This must happen before the session-candidate empty check so previously
    # saved records remain visible after navigation or a fresh session.
    st.markdown("#### Database records")
    try:
        analytics_df = get_all_candidates()
    except Exception as error:
        analytics_df = pd.DataFrame()
        st.error("Unable to load database records.")
        st.code(str(error))

    if analytics_df.empty:
        empty_state("The database is empty until you screen resumes.")
    else:
        st.dataframe(analytics_df, use_container_width=True, hide_index=True)

        ids = analytics_df["id"].tolist() if "id" in analytics_df.columns else []
        if ids:
            selected_id = st.selectbox("Delete candidate ID", ids)
            d1, d2 = st.columns(2)
            with d1:
                if st.button("Delete selected"):
                    delete_candidate(selected_id)
                    st.success(f"Deleted candidate {selected_id}.")
                    st.rerun()
            with d2:
                if st.button("Delete all records"):
                    delete_all_candidates()
                    st.success("All candidate records deleted.")
                    st.rerun()

        search_text = st.text_input("Search database")
        if search_text.strip():
            search_result = search_candidates(search_text)
            st.dataframe(search_result, use_container_width=True, hide_index=True)

    if not rows:
        empty_state("No candidates are shown. Upload PDFs and screen them to populate this dashboard.")
        return




def page_job_description():
    st.markdown('<p class="section-title">Job Description</p>', unsafe_allow_html=True)
    st.caption("Paste a real job description. Skills are detected only from this text.")
    st.session_state.target_job = st.selectbox(
        "Target job role",
        ["Data Analyst", "Data Scientist", "ML Engineer", "Web Developer", "Backend Developer", "Cloud Engineer"],
        index=["Data Analyst", "Data Scientist", "ML Engineer", "Web Developer", "Backend Developer", "Cloud Engineer"].index(
            st.session_state.target_job
        ),
    )
    st.session_state.candidate_location = st.selectbox(
        "Default candidate location (used if a resume has none)",
        ["Hyderabad", "Bangalore", "Chennai", "Pune", "Mumbai", "Delhi", "Warangal"],
        index=["Hyderabad", "Bangalore", "Chennai", "Pune", "Mumbai", "Delhi", "Warangal"].index(
            st.session_state.candidate_location
        ),
    )
    st.session_state.job_description = st.text_area(
        "Job description",
        value=st.session_state.job_description,
        height=280,
        placeholder="Paste the job description here. No example text is prefilled.",
    )
    if st.session_state.job_description.strip():
        skills = extract_jd_skills(st.session_state.job_description)
        if skills:
            st.success(f"Detected {len(skills)} required skills")
            st.write(", ".join(skills))
        else:
            st.warning("No recognized skills were detected in the job description.")
    else:
        empty_state("No job description yet. Screening can still run, but JD match will be 0.")


def page_upload():
    st.markdown('<p class="section-title">Upload Resumes</p>', unsafe_allow_html=True)
    st.caption("Upload one or more PDF resumes, then run screening. Results replace any previous session list.")
    uploaded_files = st.file_uploader("PDF resumes", type=["pdf"], accept_multiple_files=True)
    if st.button("Screen Resumes", type="primary", use_container_width=True):
        if not uploaded_files:
            st.warning("Please upload at least one resume PDF.")
            return
        records, errors = screen_resumes(
            uploaded_files,
            st.session_state.job_description,
            st.session_state.target_job,
            st.session_state.candidate_location,
        )
        st.session_state.processing_errors = errors
        if records:
            st.session_state.screened_candidates = records
            st.session_state.selected_candidate = records[0]["Candidate"]
            st.success(f"Processed {len(records)} resume(s). Open Screening Results to review them.")
            st.session_state.page = "Screening Results"
            st.rerun()
        else:
            st.session_state.screened_candidates = []
            st.session_state.selected_candidate = None
            st.error("No resumes were processed successfully.")
    if st.session_state.processing_errors:
        with st.expander("Processing errors"):
            st.dataframe(pd.DataFrame(st.session_state.processing_errors), use_container_width=True)


def render_candidate_detail(candidate, rank):
    label, css = match_label(candidate["JD Match"])
    jd_skills = candidate.get("JD Skills") or extract_jd_skills(st.session_state.job_description)
    matched = candidate.get("Matched Skills") or []
    missing = candidate.get("Missing Skills") or []
    required = len(jd_skills)
    matched_n = len(matched)
    pct = round(100 * matched_n / required) if required else 0
    breakdown = candidate.get("Score Breakdown") or {}
    skills_p = breakdown.get("Skills", 0)
    exp_p = breakdown.get("Experience", 0)
    edu_p = breakdown.get("Education", 0)
    jd_p = breakdown.get("JD Match", 0)
    projects_p = breakdown.get("Projects", 0)
    donut_total = skills_p + exp_p + edu_p + projects_p + jd_p
    donut = (
        f"conic-gradient(#3b82f6 0 {skills_p}%, "
        f"#22d3ee {skills_p}% {skills_p+exp_p}%, "
        f"#a78bfa {skills_p+exp_p}% {skills_p+exp_p+edu_p}%, "
        f"#f59e0b {skills_p+exp_p+edu_p}% {skills_p+exp_p+edu_p+projects_p}%, "
        f"#34d399 {skills_p+exp_p+edu_p+projects_p}% {donut_total}%)"
    )
    tabs = st.columns(6)
    tab_names = ["Overview", "Skills", "Projects", "Experience", "Education", "Certifications"]
    for col, name in zip(tabs, tab_names):
        with col:
            if st.button(name, use_container_width=True, key=f"tab_{name}"):
                st.session_state.detail_tab = name

    st.markdown(
        f"""
        <div class="card" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <div>
                <div class="muted">Candidate #{rank}</div>
                <h3 style="margin:4px 0 6px 0;color:#fff">{candidate["Candidate"]}
                    <span class="pill {css}">{label}</span>
                </h3>
                <div class="tiny">{candidate["Education"]} · {candidate["Experience Level"]} · {candidate["Location"]}</div>
            </div>
            <div style="text-align:right">
                <div class="muted">Overall Resume Score</div>
                <div style="font-size:1.6rem;font-weight:800;color:#2ee6a6">{candidate["Resume Score"]:.0f}%</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab = st.session_state.detail_tab
    if tab == "Skills":
        st.write("**Extracted skills**")
        st.write(", ".join(candidate.get("Skill List") or []) or "None detected")
        st.write("**Matched vs missing**")
        st.success(", ".join(matched) if matched else "No matched skills")
        st.warning(", ".join(missing) if missing else "No missing skills")
        return
    if tab == "Projects":
        projects = candidate.get("Projects") or []
        if not projects:
            empty_state("No project titles were detected in this resume.")
        else:
            for title, score in candidate.get("Project Relevance") or [(p, 0) for p in projects]:
                st.markdown(
                    f"""<div class="card"><b>{title}</b>
                    <div class="tiny">Relevance {score}%</div>
                    <div class="bar"><div style="width:{score}%"></div></div></div>""",
                    unsafe_allow_html=True,
                )
        return
    if tab == "Experience":
        st.write(f"**Experience:** {candidate['Experience']} years")
        st.write(f"**Level:** {candidate['Experience Level']}")
        for skill, note, ok in candidate.get("Evidence") or []:
            color = "#2ee6a6" if ok else "#ff6b81"
            st.markdown(
                f'<div class="ev-row"><span>{skill}</span><span style="color:{color}">{note}</span></div>',
                unsafe_allow_html=True,
            )
        return
    if tab == "Education":
        st.write(f"**Education:** {candidate['Education']}")
        st.write(f"**Top job role:** {candidate['Top Job Role']}")
        return
    if tab == "Certifications":
        certs = candidate.get("Certifications") or []
        if not certs:
            empty_state("No certifications were detected.")
        else:
            for cert in certs:
                st.markdown(f'<div class="card">{cert}</div>', unsafe_allow_html=True)
        return

    heat_rows = ""
    for skill in jd_skills:
        status, klass = heatmap_status(skill, candidate.get("Skill List") or [], candidate.get("Resume Text", ""))
        heat_rows += f'<div class="heat"><span>{skill}</span><span class="pill {klass}">{status}</span></div>'
    if not heat_rows:
        heat_rows = '<div class="tiny">Add a job description to build the skill-gap heatmap.</div>'

    req_rows = ""
    for skill, level, klass in jd_priority(jd_skills):
        req_rows += f'<div class="req-row"><span>{skill}</span><span class="pill {klass}">{level}</span></div>'
    if not req_rows:
        req_rows = '<div class="tiny">No JD skills to prioritize yet.</div>'

    strengths = []
    if matched:
        strengths.append("Good " + " and ".join(matched[:3]) + " skills")
    if candidate.get("Projects"):
        strengths.append("Relevant project experience")
    gaps = ", ".join(missing[:4]) if missing else "None"
    rec_text = (candidate.get("Suggestions") or ["Keep the resume aligned with the job description."])[0]
    complete = candidate.get("Completeness", 0)
    found_sections = candidate.get("Complete Sections") or []
    checks = ""
    for label, _pattern in COMPLETENESS_SECTIONS:
        mark = "✓" if label in found_sections else "○"
        color = "#2ee6a6" if label in found_sections else "#6d7f9e"
        checks += f'<div class="tiny" style="color:{color}">{mark} {label}</div>'

    evidence_html = ""
    for skill, note, ok in candidate.get("Evidence") or []:
        color = "#2ee6a6" if ok else "#ff6b81"
        evidence_html += f'<div class="ev-row"><span>{skill}</span><span style="color:{color}">{note}</span></div>'
    if not evidence_html:
        evidence_html = '<div class="tiny">No skill evidence to display.</div>'

    rel_html = ""
    for title, score in candidate.get("Project Relevance") or []:
        rel_html += (
            f'<div class="tiny" style="margin-top:8px">{title} · {score}%</div>'
            f'<div class="bar"><div style="width:{score}%"></div></div>'
        )
    if not rel_html:
        rel_html = '<div class="tiny">No projects detected for relevance scoring.</div>'

    kw_found = candidate.get("Keyword Found", 0)
    kw_total = candidate.get("Keyword Total", 0)
    kw_pct = candidate.get("Keyword Coverage", 0)

    matched_html = "".join(f'<span class="pill matched">{s}</span> ' for s in matched) or '<span class="tiny">None</span>'
    missing_html = "".join(f'<span class="pill missing">{s}</span> ' for s in missing) or '<span class="tiny">None</span>'

    st.markdown(
        f"""
        <div class="three">
            <div class="card">
                <b>Score Breakdown</b>
                <div class="donut-wrap" style="margin-top:12px">
                    <div class="donut" style="background:{donut}"><span>{candidate["Resume Score"]:.0f}%</span></div>
                    <div class="tiny">
                        <div style="margin:4px 0;"><span style="color:#3b82f6">●</span> Skills <span style="float:right">{skills_p}%</span></div>
                        <div style="margin:4px 0;"><span style="color:#22d3ee">●</span> Experience <span style="float:right">{exp_p}%</span></div>
                        <div style="margin:4px 0;"><span style="color:#a78bfa">●</span> Education <span style="float:right">{edu_p}%</span></div>
                        <div style="margin:4px 0;"><span style="color:#f59e0b">●</span> Projects <span style="float:right">{projects_p}%</span></div>
                        <div style="margin:4px 0;"><span style="color:#34d399">●</span> JD Match <span style="float:right">{jd_p}%</span></div>
                    </div>
                </div>
            </div>
            <div class="card">
                <b>Skill Match</b>
                <div class="tiny" style="margin-top:6px">{matched_n} / {required or 0} required skills matched</div>
                <div class="bar"><div style="width:{pct}%"></div></div>
                <div class="tiny" style="margin-top:10px">Matched skills</div>
                <div>{matched_html}</div>
                <div class="tiny" style="margin-top:8px">Missing skills</div>
                <div>{missing_html}</div>
            </div>
            <div class="card">
                <b>Skill Gap Heatmap</b>
                {heat_rows}
            </div>
        </div>
        <div style="height:12px"></div>
        <div class="three">
            <div class="card"><b>JD Requirements</b><div class="legend">Priority from the pasted job description</div>{req_rows}</div>
            <div class="card">
                <b>Key Insights</b>
                <div class="tiny" style="margin-top:8px;color:#2ee6a6">Strengths</div>
                <div class="tiny">{" · ".join(strengths) if strengths else "Not enough data yet"}</div>
                <div class="tiny" style="margin-top:8px;color:#ff6b81">Skill Gaps</div>
                <div class="tiny">{gaps}</div>
                <div class="tiny" style="margin-top:8px;color:#5ec8ff">Recommendation</div>
                <div class="tiny">{rec_text}</div>
            </div>
            <div class="card">
                <b>Resume Completeness</b>
                <div class="tiny" style="margin-top:6px">{complete}% · {len(found_sections)} / 6 sections complete</div>
                <div class="bar"><div style="width:{complete}%"></div></div>
                <div style="margin-top:8px">{checks}</div>
            </div>
        </div>
        <div style="height:12px"></div>
        <div class="three">
            <div class="card"><b>Experience Evidence</b>{evidence_html}</div>
            <div class="card"><b>Project Relevance</b>{rel_html}</div>
            <div class="card">
                <b>Keyword Coverage</b>
                <div class="tiny" style="margin-top:8px">{kw_found} / {kw_total} JD keywords detected</div>
                <div class="bar"><div style="width:{kw_pct}%"></div></div>
                <div class="tiny" style="margin-top:6px">{kw_pct}%</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_results():
    rows = ranked_candidates()
    jd_skills = extract_jd_skills(st.session_state.job_description) if st.session_state.job_description.strip() else []
    total = len(rows)
    top_score = max((r["JD Match"] for r in rows), default=None)
    avg_match = round(sum(r["JD Match"] for r in rows) / total, 1) if total else None
    top_name = rows[0]["Candidate"] if rows else ""

    h1, h2 = st.columns([0.72, 0.28])
    with h1:
        st.markdown('<p class="section-title">Screening Results</p>', unsafe_allow_html=True)
        st.caption("Candidates ranked by their match to the job description. This list stays empty until you screen PDFs.")
    with h2:
        st.selectbox("Job Description", [st.session_state.target_job], disabled=True)

    st.markdown(
        f"""
        <div class="kpi-row">
            <div class="card kpi"><div class="label">Total Candidates</div><div class="value">{total}</div></div>
            <div class="card kpi"><div class="label">Top Match Score</div>
            <div class="value">{f"{top_score:.0f}%" if top_score is not None else "--"}</div>
            <div class="sub">{top_name}</div></div>
            <div class="card kpi"><div class="label">Avg. JD Match</div>
            <div class="value">{f"{avg_match:.0f}%" if avg_match is not None else "--"}</div></div>
            <div class="card kpi"><div class="label">Required Skills (from JD)</div>
            <div class="value">{len(jd_skills)}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not rows:
        st.write("")
        empty_state("No screened candidates yet. Go to Upload Resumes after pasting a job description.")
        return

    names = [r["Candidate"] for r in rows]
    if st.session_state.selected_candidate not in names:
        st.session_state.selected_candidate = names[0]

    left, right = st.columns([0.28, 0.72])
    with left:
        st.markdown("**Candidates**")
        for index, row in enumerate(rows, start=1):
            label, css = match_label(row["JD Match"])
            active = row["Candidate"] == st.session_state.selected_candidate
            if st.button(
                f"{index}. {row['Candidate']}  ·  {row['JD Match']:.0f}%  ·  {label}",
                use_container_width=True,
                key=f"cand_{row['Candidate']}_{index}",
                type="primary" if active else "secondary",
            ):
                st.session_state.selected_candidate = row["Candidate"]
                st.rerun()
    with right:
        selected = next(r for r in rows if r["Candidate"] == st.session_state.selected_candidate)
        rank = names.index(selected["Candidate"]) + 1
        render_candidate_detail(selected, rank)


# ============================================================
# APP
# ============================================================

init_state()
inject_css()

if not st.session_state.authenticated:
    render_login()
else:
    topbar()
    if st.session_state.sidebar_open:
        nav_col, main_col = st.columns([0.2, 0.8], gap="medium")
        with nav_col:
            sidebar_nav()
        with main_col:
            page = st.session_state.page
            if page == "Dashboard":
                page_dashboard()
            elif page == "Upload Resumes":
                page_upload()
            elif page == "Job Description":
                page_job_description()
            else:
                page_results()
    else:
        page = st.session_state.page
        if page == "Dashboard":
            page_dashboard()
        elif page == "Upload Resumes":
            page_upload()
        elif page == "Job Description":
            page_job_description()
        else:
            page_results()