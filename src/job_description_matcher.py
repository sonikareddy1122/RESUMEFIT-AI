import re
from src.skill_extractor import SKILLS


def extract_jd_skills(job_description):
    """
    Extract technical skills from the Job Description.
    """

    detected_skills = []

    text = job_description.lower()

    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"

        if re.search(pattern, text):
            detected_skills.append(skill)

    return detected_skills


def compare_resume_with_jd(resume_skills, jd_skills):
    """
    Compare resume skills with Job Description skills.
    """

    resume_skills_lower = {
        skill.lower(): skill
        for skill in resume_skills
    }

    matched_skills = []
    missing_skills = []

    for skill in jd_skills:

        if skill.lower() in resume_skills_lower:
            matched_skills.append(skill)

        else:
            missing_skills.append(skill)

    # Calculate percentage
    if len(jd_skills) > 0:
        match_percentage = (
            len(matched_skills) / len(jd_skills)
        ) * 100

    else:
        match_percentage = 0

    return {
        "Required Skills": jd_skills,
        "Matched Skills": matched_skills,
        "Missing Skills": missing_skills,

        # IMPORTANT
        "Match Percentage": round(match_percentage, 2)
    }