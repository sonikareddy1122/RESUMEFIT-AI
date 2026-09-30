import re


# ==========================================
# STEP 10.3 - CANDIDATE PROFILE EXTRACTION
# ==========================================


EDUCATION_KEYWORDS = [
    "B.Tech CSE",
    "B.Tech",
    "B.E",
    "B.Sc Computer Science",
    "B.Sc",
    "MCA",
    "M.Tech CSE",
    "M.Tech",
    "Computer Science"
]


JOB_ROLES = [
    "Data Analyst",
    "Data Scientist",
    "ML Engineer",
    "Web Developer",
    "Backend Developer",
    "Cloud Engineer"
]


def extract_education(resume_text):

    text = resume_text.lower()

    if "b.tech" in text and "computer science" in text:
        return "B.Tech CSE"

    if "b.tech" in text:
        return "B.Tech"

    if "b.e" in text:
        return "B.E"

    if "mca" in text:
        return "MCA"

    if "m.tech" in text and "computer science" in text:
        return "M.Tech CSE"

    if "m.tech" in text:
        return "M.Tech"

    if "b.sc" in text and "computer science" in text:
        return "B.Sc Computer Science"

    if "b.sc" in text:
        return "B.Sc"

    return "Not Detected"


def extract_experience_level(resume_text):

    text = resume_text.lower()

    if "fresher" in text:
        return "Fresher"

    if "entry level" in text:
        return "Fresher"

    # Look for experience in years
    matches = re.findall(
        r"(\d+)\+?\s*(?:years?|yrs?)",
        text
    )

    if matches:

        years = max(
            int(value)
            for value in matches
        )

        if years >= 6:
            return "Senior"

        elif years >= 3:
            return "Mid-Level"

        else:
            return "Junior"

    return "Fresher"


def extract_job_roles(resume_text):

    text = resume_text.lower()

    found_roles = []

    for role in JOB_ROLES:

        if role.lower() in text:
            found_roles.append(role)

    return found_roles


def extract_candidate_profile(resume_text):

    education = extract_education(
        resume_text
    )

    experience_level = extract_experience_level(
        resume_text
    )

    job_roles = extract_job_roles(
        resume_text
    )

    return {
        "Education": education,
        "Experience_Level": experience_level,
        "Job_Roles": job_roles
    }


# ==========================================
# TEST PROGRAM
# ==========================================

if __name__ == "__main__":

    from resume_parser import extract_resume_text

    print("=" * 60)
    print("CANDIDATE PROFILE EXTRACTION")
    print("=" * 60)

    pdf_path = input(
        "\nEnter the path of your resume PDF: "
    ).strip().strip('"')

    resume_text = extract_resume_text(
        pdf_path
    )

    profile = extract_candidate_profile(
        resume_text
    )

    print("\nCandidate Profile")
    print("-" * 60)

    print(
        "Education:",
        profile["Education"]
    )

    print(
        "Experience Level:",
        profile["Experience_Level"]
    )

    print(
        "Job Roles Found:",
        profile["Job_Roles"]
    )

    print("-" * 60)

    print("\nProfile extraction completed.")

