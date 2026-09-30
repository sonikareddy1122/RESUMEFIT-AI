# =================================================
# RESUME SCORE CALCULATOR
# =================================================


def calculate_resume_score(
    candidate_skills,
    education,
    experience_years,
    skill_match_percentage
):

    # =================================================
    # SKILLS SCORE - 40 MARKS
    # =================================================

    skill_count = len(candidate_skills)

    if skill_count >= 10:
        skills_score = 40

    elif skill_count >= 7:
        skills_score = 32

    elif skill_count >= 5:
        skills_score = 25

    elif skill_count >= 3:
        skills_score = 18

    elif skill_count >= 1:
        skills_score = 10

    else:
        skills_score = 0


    # =================================================
    # EDUCATION SCORE - 20 MARKS
    # =================================================

    if education in [
        "M.Tech CSE",
        "MCA"
    ]:

        education_score = 20

    elif education in [
        "B.Tech CSE",
        "B.Tech IT"
    ]:

        education_score = 18

    elif education == "B.Sc Computer Science":

        education_score = 15

    else:

        education_score = 10


    # =================================================
    # EXPERIENCE SCORE - 20 MARKS
    # =================================================

    if experience_years >= 5:

        experience_score = 20

    elif experience_years >= 3:

        experience_score = 16

    elif experience_years >= 1:

        experience_score = 12

    else:

        experience_score = 8


    # =================================================
    # JOB MATCH SCORE - 20 MARKS
    # =================================================

    skill_match_percentage = max(
        0,
        min(
            100,
            skill_match_percentage
        )
    )


    job_match_score = (
        skill_match_percentage / 100
    ) * 20


    # =================================================
    # TOTAL SCORE
    # =================================================

    total_score = (
        skills_score
        + education_score
        + experience_score
        + job_match_score
    )


    total_score = max(
        0,
        min(
            100,
            total_score
        )
    )


    # =================================================
    # SCORE CATEGORY
    # =================================================

    if total_score >= 80:

        category = "Excellent Resume"

    elif total_score >= 65:

        category = "Strong Resume"

    elif total_score >= 50:

        category = "Average Resume"

    else:

        category = "Needs Improvement"


    # =================================================
    # RESUME IMPROVEMENT SUGGESTIONS
    # =================================================

    suggestions = []


    # Skill suggestions

    if skill_count < 5:

        suggestions.append(
            "Add more relevant technical skills to your resume."
        )

    elif skill_count < 10:

        suggestions.append(
            "Consider adding more job-relevant technical skills."
        )


    # Education suggestion

    if education_score < 18:

        suggestions.append(
            "Clearly highlight your highest educational qualification."
        )


    # Experience suggestions

    if experience_years == 0:

        suggestions.append(
            "Add internships, academic projects, certifications, or practical experience to strengthen the resume."
        )

    elif experience_years < 3:

        suggestions.append(
            "Highlight measurable achievements and responsibilities from your experience."
        )


    # Job matching suggestions

    if skill_match_percentage < 60:

        suggestions.append(
            "Improve the match between your skills and the target job requirements."
        )

    elif skill_match_percentage < 80:

        suggestions.append(
            "Add a few more skills relevant to your target job role."
        )


    # If no suggestions

    if not suggestions:

        suggestions.append(
            "Your resume has good coverage of the defined scoring criteria. Keep your skills and projects updated."
        )


    # =================================================
    # RETURN ALL RESULTS
    # =================================================

    return {

        "Total Score": round(
            total_score,
            2
        ),

        "Skills Score": skills_score,

        "Education Score": education_score,

        "Experience Score": experience_score,

        "Job Match Score": round(
            job_match_score,
            2
        ),

        "Category": category,

        "Suggestions": suggestions
    }