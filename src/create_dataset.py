import pandas as pd
import random
import os

# Make results reproducible
random.seed(42)

# Job roles and related skills
job_roles = {
    "Data Analyst": [
        "Python", "SQL", "Excel", "Power BI", "Pandas",
        "NumPy", "Statistics", "Data Visualization"
    ],
    "Data Scientist": [
        "Python", "SQL", "Machine Learning", "Pandas",
        "NumPy", "Scikit-learn", "Statistics", "Deep Learning"
    ],
    "ML Engineer": [
        "Python", "Machine Learning", "Deep Learning",
        "TensorFlow", "PyTorch", "Scikit-learn", "SQL", "Docker"
    ],
    "Web Developer": [
        "HTML", "CSS", "JavaScript", "React", "Node.js",
        "Git", "REST API", "MongoDB"
    ],
    "Backend Developer": [
        "Python", "Java", "SQL", "REST API", "Django",
        "Flask", "MySQL", "Git"
    ],
    "Cloud Engineer": [
        "AWS", "Azure", "Docker", "Kubernetes",
        "Linux", "Python", "Git", "Networking"
    ]
}

education = [
    "B.Tech CSE",
    "B.Tech IT",
    "B.Sc Computer Science",
    "MCA",
    "M.Tech CSE"
]

locations = [
    "Hyderabad",
    "Bangalore",
    "Chennai",
    "Pune",
    "Mumbai",
    "Delhi",
    "Warangal"
]

experience_levels = [
    "Fresher",
    "Junior",
    "Mid-Level",
    "Senior"
]

rows = []

# Generate 1200 resume records
for i in range(1200):

    role = random.choice(list(job_roles.keys()))
    required_skills = job_roles[role]

    # Select skills for candidate
    num_skills = random.randint(4, min(8, len(required_skills)))
    skills = random.sample(required_skills, num_skills)

    # Add some unrelated skills randomly
    all_skills = list(set(
        skill
        for role_skills in job_roles.values()
        for skill in role_skills
    ))

    extra_skills = random.sample(
        [s for s in all_skills if s not in skills],
        min(random.randint(0, 2), len(all_skills))
    )

    skills.extend(extra_skills)

    education_level = random.choice(education)
    experience = random.choice(experience_levels)

    if experience == "Fresher":
        experience_years = 0
    elif experience == "Junior":
        experience_years = random.randint(1, 2)
    elif experience == "Mid-Level":
        experience_years = random.randint(3, 5)
    else:
        experience_years = random.randint(6, 10)

    # Calculate skill match percentage
    matched_skills = len(
        set(skills).intersection(set(required_skills))
    )

    skill_match = round(
        (matched_skills / len(required_skills)) * 100,
        2
    )

    # Generate resume score
    score = (
        skill_match * 0.7
        + min(experience_years * 5, 30)
    )

    score = min(round(score, 2), 100)

    # Recommendation
    if score >= 75:
        recommendation = "Highly Recommended"
    elif score >= 50:
        recommendation = "Recommended"
    else:
        recommendation = "Not Recommended"

    rows.append({
        "Resume_ID": f"RES{i+1:04d}",
        "Education": education_level,
        "Experience_Level": experience,
        "Experience_Years": experience_years,
        "Skills": ", ".join(skills),
        "Target_Job": role,
        "Location": random.choice(locations),
        "Skill_Match_Percentage": skill_match,
        "Resume_Score": score,
        "Recommendation": recommendation
    })


# Create DataFrame
df = pd.DataFrame(rows)

# Create data folder if it doesn't exist
os.makedirs("data", exist_ok=True)

# Save dataset
output_path = "data/resume_dataset.csv"
df.to_csv(output_path, index=False)

print("Dataset created successfully!")
print(f"Total records: {len(df)}")
print(f"Saved to: {output_path}")
print("\nFirst 5 records:")
print(df.head())