# ==========================================
# STEP 10.4 - JOB RECOMMENDATION ENGINE
# ==========================================


JOB_SKILLS = {

    "Data Analyst": [
        "Python",
        "SQL",
        "Pandas",
        "NumPy",
        "Power BI",
        "Excel",
        "Matplotlib",
        "Seaborn"
    ],

    "Data Scientist": [
        "Python",
        "SQL",
        "Pandas",
        "NumPy",
        "Machine Learning",
        "Scikit-learn",
        "Matplotlib",
        "Seaborn"
    ],

    "ML Engineer": [
        "Python",
        "Machine Learning",
        "Scikit-learn",
        "TensorFlow",
        "PyTorch",
        "NumPy",
        "Pandas"
    ],

    "Web Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "React"
    ],

    "Backend Developer": [
        "Python",
        "Java",
        "SQL",
        "Flask",
        "Django",
        "Node.js"
    ],

    "Cloud Engineer": [
        "Python",
        "Azure",
        "AWS",
        "Google Cloud",
        "Git",
        "GitHub"
    ]
}


def calculate_skill_match(
    candidate_skills,
    required_skills
):

    candidate_skills_lower = {
        skill.lower()
        for skill in candidate_skills
    }

    matched_skills = []

    for skill in required_skills:

        if skill.lower() in candidate_skills_lower:

            matched_skills.append(skill)

    if len(required_skills) == 0:
        percentage = 0

    else:
        percentage = (
            len(matched_skills)
            / len(required_skills)
        ) * 100

    return percentage, matched_skills


def recommend_jobs(candidate_skills):

    recommendations = []

    for job_role, required_skills in JOB_SKILLS.items():

        percentage, matched_skills = calculate_skill_match(
            candidate_skills,
            required_skills
        )

        recommendations.append({
            "Job Role": job_role,
            "Skill Match": round(percentage, 2),
            "Matched Skills": matched_skills
        })

    recommendations.sort(
        key=lambda x: x["Skill Match"],
        reverse=True
    )

    return recommendations


# ==========================================
# TEST PROGRAM
# ==========================================

if __name__ == "__main__":

    from resume_parser import extract_resume_text
    from skill_extractor import extract_skills

    print("=" * 60)
    print("JOB RECOMMENDATION ENGINE")
    print("=" * 60)

    pdf_path = input(
        "\nEnter the path of your resume PDF: "
    ).strip().strip('"')

    resume_text = extract_resume_text(
        pdf_path
    )

    candidate_skills = extract_skills(
        resume_text
    )

    print("\nCandidate Skills:")
    print(candidate_skills)

    recommendations = recommend_jobs(
        candidate_skills
    )

    print("\n" + "=" * 60)
    print("JOB RECOMMENDATIONS")
    print("=" * 60)

    for index, recommendation in enumerate(
        recommendations,
        start=1
    ):

        print(
            f"\n{index}. "
            f"{recommendation['Job Role']}"
        )

        print(
            f"   Skill Match: "
            f"{recommendation['Skill Match']:.2f}%"
        )

        print(
            f"   Matched Skills: "
            f"{', '.join(recommendation['Matched Skills'])}"
        )

    print("\n" + "=" * 60)
    print("STEP 10.4 COMPLETED")
    print("=" * 60)

