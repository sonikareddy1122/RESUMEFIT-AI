import joblib
import pandas as pd

from scipy.sparse import hstack, csr_matrix

from resume_parser import extract_resume_text
from skill_extractor import extract_skills
from job_recommender import recommend_jobs


# ==========================================
# STEP 10.5 - RESUME SCREENING SYSTEM
# ==========================================

print("=" * 60)
print("AI RESUME SCREENING AND JOB RECOMMENDATION")
print("=" * 60)


# ==========================================
# LOAD SAVED ML COMPONENTS
# ==========================================

model = joblib.load(
    "models/resume_model.pkl"
)

vectorizer = joblib.load(
    "models/tfidf_vectorizer.pkl"
)

encoder = joblib.load(
    "models/encoder.pkl"
)


# ==========================================
# INPUT CANDIDATE DETAILS
# ==========================================

pdf_path = input(
    "\nEnter the path of your resume PDF: "
).strip().strip('"')

education = input(
    "Enter Education (example: B.Tech CSE): "
).strip()

experience_level = input(
    "Enter Experience Level (Fresher/Junior/Mid-Level/Senior): "
).strip()

experience_years = float(
    input("Enter Experience Years: ")
)

target_job = input(
    "Enter Target Job Role: "
).strip()

location = input(
    "Enter Location: "
).strip()


# ==========================================
# EXTRACT RESUME TEXT
# ==========================================

resume_text = extract_resume_text(
    pdf_path
)


# ==========================================
# EXTRACT SKILLS
# ==========================================

candidate_skills = extract_skills(
    resume_text
)


print("\n" + "=" * 60)
print("EXTRACTED SKILLS")
print("=" * 60)

print(
    ", ".join(candidate_skills)
)


# ==========================================
# PREPARE INPUT DATA
# ==========================================

candidate_data = pd.DataFrame([
    {
        "Education": education,
        "Experience_Level": experience_level,
        "Experience_Years": experience_years,
        "Skills": ", ".join(candidate_skills),
        "Target_Job": target_job,
        "Location": location
    }
])


# ==========================================
# TF-IDF
# ==========================================

skills_vector = vectorizer.transform(
    candidate_data["Skills"]
)


# ==========================================
# ONE-HOT ENCODING
# ==========================================

categorical_features = [
    "Education",
    "Experience_Level",
    "Target_Job",
    "Location"
]

encoded_features = encoder.transform(
    candidate_data[categorical_features]
)


# ==========================================
# EXPERIENCE
# ==========================================

experience_feature = csr_matrix(
    candidate_data[
        ["Experience_Years"]
    ].values
)


# ==========================================
# COMBINE FEATURES
# ==========================================

final_features = hstack([
    skills_vector,
    encoded_features,
    experience_feature
]).tocsr()


# ==========================================
# ML PREDICTION
# ==========================================

prediction = model.predict(
    final_features
)[0]


# ==========================================
# PREDICTION PROBABILITY
# ==========================================

probabilities = model.predict_proba(
    final_features
)[0]

class_probabilities = dict(
    zip(
        model.classes_,
        probabilities
    )
)


# ==========================================
# JOB RECOMMENDATIONS
# ==========================================

job_recommendations = recommend_jobs(
    candidate_skills
)


# ==========================================
# FINAL RESULT
# ==========================================

print("\n" + "=" * 60)
print("RESUME SCREENING RESULT")
print("=" * 60)

print(
    "\nML Recommendation:",
    prediction
)


print("\nRecommendation Probabilities:")

for class_name, probability in class_probabilities.items():

    print(
        f"{class_name}: "
        f"{probability * 100:.2f}%"
    )


print("\n" + "=" * 60)
print("JOB RECOMMENDATIONS")
print("=" * 60)


for index, recommendation in enumerate(
    job_recommendations,
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
print("RESUME SCREENING COMPLETED")
print("=" * 60)

