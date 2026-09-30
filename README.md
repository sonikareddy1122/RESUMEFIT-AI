# AI Resume Screening System

Streamlit recruiter dashboard for ranking PDF resumes against a job description. The interface follows a dark screening-results layout: ranked candidates, score breakdown, skill match, skill-gap heatmap, JD priorities, insights, resume completeness, project relevance, and keyword coverage.

## Features

- Upload one or more PDF resumes
- Extract skills, education, experience, projects, and certifications
- Match candidates to a pasted job description
- Rank by JD match with Strong / Good / Partial / Low labels
- Recruiter pages: Dashboard, Upload Resumes, Job Description, Screening Results, Comparison, Settings
- Download a CSV screening report
- Optional ML recommendation when `models/*.pkl` files are present

## Project structure

- `app.py` — Streamlit UI
- `src/` — parser, skill extractor, JD matcher, scoring, analyzer
- `database/` — SQLite candidate storage
- `models/` — trained classifier, TF-IDF vectorizer, encoder
- `.streamlit/config.toml` — dark theme

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Open the local URL Streamlit prints (usually `http://localhost:8501`).

## How to use

1. Open **Job Description** and paste the role text (a Data Analyst sample is loaded by default).
2. Open **Upload Resumes** and add PDF files, then click **Screen Resumes**.
3. Open **Screening Results** to inspect the ranked shortlist. Click a candidate to load Overview, Skills, Projects, Experience, Education, and Certifications.
4. Use **Comparison** for a side-by-side view and **Download Report** for CSV export.

Until you screen real PDFs, Screening Results shows sample ranked candidates so the dashboard layout is visible immediately. Restore that sample from **Settings**.
