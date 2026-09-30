import re


# ==========================================
# STEP 10.2 - SKILL EXTRACTION
# ==========================================

SKILLS = [
    "Python",
    "Java",
    "C++",
    "SQL",
    "MySQL",
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Seaborn",
    "Scikit-learn",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "AI",
    "NLP",
    "Generative AI",
    "Power BI",
    "Excel",
    "Tableau",
    "Streamlit",
    "Azure",
    "AWS",
    "Google Cloud",
    "Git",
    "GitHub",
    "HTML",
    "CSS",
    "JavaScript",
    "React",
    "Node.js",
    "Flask",
    "Django",
    "TensorFlow",
    "PyTorch",
    "Chart.js",
    "Data Visualization",
    "Statistics",
]


def extract_skills(resume_text):

    found_skills = []

    text = resume_text.lower()

    for skill in SKILLS:

        skill_lower = skill.lower()

        if re.search(
            r"(?<!\w)" + re.escape(skill_lower) + r"(?!\w)",
            text
        ):
            found_skills.append(skill)

    return found_skills


if __name__ == "__main__":

    from resume_parser import extract_resume_text

    print("=" * 60)
    print("RESUME SKILL EXTRACTION")
    print("=" * 60)

    pdf_path = input(
        "\nEnter the path of your resume PDF: "
    ).strip().strip('"')

    resume_text = extract_resume_text(pdf_path)

    skills = extract_skills(resume_text)

    print("\nSkills Found:")

    print("-" * 60)

    for skill in skills:
        print("?", skill)

    print("-" * 60)

    print(
        "\nTotal Skills Found:",
        len(skills)
    )

    print("\nSkill extraction completed.")
