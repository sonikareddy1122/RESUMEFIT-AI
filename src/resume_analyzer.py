import re


SECTION_HEADERS = {
    "contact": r"(contact|personal details|profile)",
    "education": r"(education|qualification|academics)",
    "skills": r"(skills|technical skills|core skills)",
    "projects": r"(projects?|academic projects?|personal projects?)",
    "experience": r"(experience|work experience|employment|internship)",
    "certifications": r"(certifications?|certificates?|achievements)",
}

RELATED_SKILLS = {
    "tableau": ["power bi", "matplotlib", "seaborn", "data visualization", "chart.js"],
    "power bi": ["tableau", "excel", "matplotlib", "data visualization"],
    "excel": ["pandas", "csv", "spreadsheet"],
    "data visualization": ["matplotlib", "seaborn", "tableau", "power bi", "chart.js"],
    "statistics": ["numpy", "pandas", "scikit-learn", "machine learning"],
    "sql": ["mysql", "postgresql", "sqlite"],
    "mysql": ["sql"],
}

MUST_HAVE_SKILLS = {"sql", "python", "excel"}
GOOD_TO_HAVE_SKILLS = {
    "power bi",
    "tableau",
    "data visualization",
    "pandas",
    "mysql",
}

LOCATION_CITIES = [
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
    "Ahmedabad",
]


def extract_location(resume_text, fallback="Hyderabad"):
    text = resume_text.lower()
    for city in LOCATION_CITIES:
        if city.lower() in text:
            return "Bangalore" if city == "Bengaluru" else city
    return fallback


def extract_candidate_name(resume_text, fallback="Candidate"):
    lines = [
        line.strip()
        for line in resume_text.splitlines()
        if line.strip()
    ]

    skip_words = {
        "resume",
        "curriculum",
        "vitae",
        "cv",
        "email",
        "phone",
        "linkedin",
        "github",
        "objective",
        "summary",
    }

    for line in lines[:8]:
        clean = re.sub(r"[^A-Za-z .]", "", line).strip()
        words = clean.split()
        if 1 < len(words) <= 4 and all(word.lower() not in skip_words for word in words):
            if all(len(word) > 1 for word in words):
                return " ".join(word.capitalize() for word in words)

    return fallback


def _split_sections(resume_text):
    lines = resume_text.splitlines()
    sections = {key: [] for key in SECTION_HEADERS}
    current = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        matched_header = None
        for key, pattern in SECTION_HEADERS.items():
            if re.fullmatch(pattern, stripped.lower().strip(":")):
                matched_header = key
                break
            if re.match(rf"^{pattern}\s*[:\-]", stripped.lower()):
                matched_header = key
                break

        if matched_header:
            current = matched_header
            continue

        if current:
            sections[current].append(stripped)

    return {key: "\n".join(values) for key, values in sections.items()}


def extract_projects(resume_text, jd_skills):
    sections = _split_sections(resume_text)
    project_text = sections.get("projects") or ""

    if not project_text:
        return []

    chunks = re.split(r"\n(?=[A-Z0-9].{3,80}$)", project_text)
    if len(chunks) == 1:
        chunks = re.split(r"[\n•\-]+", project_text)

    projects = []
    jd_lower = {skill.lower() for skill in jd_skills}

    for chunk in chunks:
        title = chunk.strip().split("\n")[0].strip(" •-:")
        title = re.sub(r"^(project\s*\d+\s*[:.\-]?\s*)", "", title, flags=re.I)
        if len(title) < 4 or len(title) > 80:
            continue

        body = chunk.lower()
        hits = sum(1 for skill in jd_lower if skill in body or skill in title.lower())
        relevance = min(95, 35 + hits * 18 + min(len(chunk) // 40, 15))
        projects.append({
            "name": title[:70],
            "relevance": relevance,
        })

        if len(projects) >= 5:
            break

    return projects


def extract_certifications(resume_text):
    sections = _split_sections(resume_text)
    text = sections.get("certifications") or ""
    if not text:
        matches = re.findall(
            r"([A-Za-z0-9][A-Za-z0-9 &/\-]{6,60}(?:certified|certification|certificate))",
            resume_text,
            flags=re.I,
        )
        return [item.strip() for item in matches][:6]

    items = [
        re.sub(r"^[\-•\d.\s]+", "", line).strip()
        for line in text.splitlines()
        if len(line.strip()) > 4
    ]
    return items[:8]


def resume_sections_complete(resume_text, skills, projects, certifications, experience_years):
    text = resume_text.lower()
    has_contact = bool(
        re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", resume_text)
        or re.search(r"\b\d{10}\b", resume_text)
        or "linkedin" in text
    )
    has_education = any(word in text for word in ["b.tech", "btech", "m.tech", "mca", "b.sc", "bachelor", "education"])
    has_skills = bool(skills)
    has_projects = bool(projects) or "project" in text
    has_certs = bool(certifications)
    has_experience = experience_years > 0 or "intern" in text or "experience" in text

    checks = {
        "Contact Information": has_contact,
        "Education": has_education,
        "Skills": has_skills,
        "Projects": has_projects,
        "Certifications": has_certs,
        "Work Experience": has_experience,
    }
    complete = sum(1 for value in checks.values() if value)
    percent = round((complete / len(checks)) * 100)
    return checks, complete, percent


def skill_heatmap_status(skill, resume_skills):
    resume_lower = {item.lower() for item in resume_skills}
    skill_lower = skill.lower()

    if skill_lower in resume_lower:
        return "Matched"

    related = RELATED_SKILLS.get(skill_lower, [])
    if any(item in resume_lower for item in related):
        return "Partial"

    return "Missing"


def skill_priority(skill):
    lower = skill.lower()
    if lower in MUST_HAVE_SKILLS:
        return "Must Have"
    if lower in GOOD_TO_HAVE_SKILLS:
        return "Good to Have"
    return "Optional"


def experience_evidence(skill, resume_text, resume_skills):
    sections = _split_sections(resume_text)
    found_in = []
    skill_lower = skill.lower()

    if skill_lower in {item.lower() for item in resume_skills}:
        found_in.append("Skills")

    if skill_lower in (sections.get("projects") or "").lower():
        found_in.append("Projects")

    if skill_lower in (sections.get("experience") or "").lower():
        found_in.append("Experience")

    if not found_in and skill_lower in resume_text.lower():
        found_in.append("Resume")

    if not found_in:
        return "Not found in resume"

    return "Found in " + " + ".join(found_in) + " section"


def extract_jd_keywords(job_description):
    words = re.findall(r"[A-Za-z][A-Za-z+#.]{2,}", job_description)
    stop = {
        "the", "and", "for", "with", "you", "are", "our", "will", "this",
        "that", "from", "have", "your", "job", "role", "looking", "work",
        "using", "also", "into", "able", "must", "should", "good",
    }
    unique = []
    seen = set()
    for word in words:
        key = word.lower()
        if key in stop or key in seen:
            continue
        seen.add(key)
        unique.append(word)
        if len(unique) >= 20:
            break
    return unique


def keyword_coverage(keywords, resume_text):
    text = resume_text.lower()
    found = [word for word in keywords if word.lower() in text]
    total = len(keywords) or 1
    percent = round((len(found) / total) * 100)
    return found, percent


def score_breakdown(skills_score, experience_score, education_score, project_score, jd_score):
    parts = {
        "Skills": skills_score,
        "Experience": experience_score,
        "Education": education_score,
        "Projects": project_score,
        "JD Match": jd_score,
    }
    total = sum(parts.values()) or 1
    percents = {
        key: round((value / total) * 100)
        for key, value in parts.items()
    }
    drift = 100 - sum(percents.values())
    first_key = next(iter(percents))
    percents[first_key] += drift
    return percents
