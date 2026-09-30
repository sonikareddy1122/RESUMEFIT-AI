import pandas as pd

# ==========================================
# LOAD CLEANED DATASET
# ==========================================

df = pd.read_csv("data/cleaned_resume_dataset.csv")

print("=" * 60)
print("EXPLORATORY DATA ANALYSIS - STEP 1")
print("=" * 60)


# ==========================================
# 1. DATASET SHAPE
# ==========================================

print("\n1. Dataset Shape:")
print(df.shape)


# ==========================================
# 2. COLUMN NAMES
# ==========================================

print("\n2. Column Names:")
print(df.columns.tolist())


# ==========================================
# 3. FIRST 10 RECORDS
# ==========================================

print("\n3. First 10 Records:")
print(df.head(10).to_string())


# ==========================================
# 4. DATA TYPES
# ==========================================

print("\n4. Data Types:")
print(df.dtypes)


# ==========================================
# 5. BASIC STATISTICS
# ==========================================

print("\n5. Basic Statistics:")
print(df.describe())


# ==========================================
# 6. DATASET INFORMATION
# ==========================================

print("\n6. Dataset Information:")
print(df.info())


print("\n" + "=" * 60)
print("EDA STEP 1 COMPLETED")
print("=" * 60)
# ==========================================
# EDA STEP 2 - CATEGORICAL ANALYSIS
# ==========================================

print("\n" + "=" * 60)
print("EDA STEP 2 - CATEGORICAL ANALYSIS")
print("=" * 60)


# ------------------------------------------
# 1. EDUCATION DISTRIBUTION
# ------------------------------------------

print("\n1. Education Distribution:")
print(df["Education"].value_counts())


# ------------------------------------------
# 2. EXPERIENCE LEVEL DISTRIBUTION
# ------------------------------------------

print("\n2. Experience Level Distribution:")
print(df["Experience_Level"].value_counts())


# ------------------------------------------
# 3. TARGET JOB DISTRIBUTION
# ------------------------------------------

print("\n3. Target Job Distribution:")
print(df["Target_Job"].value_counts())


# ------------------------------------------
# 4. LOCATION DISTRIBUTION
# ------------------------------------------

print("\n4. Location Distribution:")
print(df["Location"].value_counts())


# ------------------------------------------
# 5. RECOMMENDATION DISTRIBUTION
# ------------------------------------------

print("\n5. Recommendation Distribution:")
print(df["Recommendation"].value_counts())


print("\n" + "=" * 60)
print("EDA STEP 2 COMPLETED")
print("=" * 60)
# ==========================================
# EDA STEP 3 - NUMERICAL ANALYSIS
# ==========================================

print("\n" + "=" * 60)
print("EDA STEP 3 - NUMERICAL ANALYSIS")
print("=" * 60)

numerical_columns = [
    "Experience_Years",
    "Skill_Match_Percentage",
    "Resume_Score"
]

# ------------------------------------------
# 1. SUMMARY STATISTICS
# ------------------------------------------

print("\n1. Numerical Summary:")
print(df[numerical_columns].describe())


# ------------------------------------------
# 2. MINIMUM VALUES
# ------------------------------------------

print("\n2. Minimum Values:")
print(df[numerical_columns].min())


# ------------------------------------------
# 3. MAXIMUM VALUES
# ------------------------------------------

print("\n3. Maximum Values:")
print(df[numerical_columns].max())


# ------------------------------------------
# 4. MEAN VALUES
# ------------------------------------------

print("\n4. Mean Values:")
print(df[numerical_columns].mean())


# ------------------------------------------
# 5. MEDIAN VALUES
# ------------------------------------------

print("\n5. Median Values:")
print(df[numerical_columns].median())


# ------------------------------------------
# 6. STANDARD DEVIATION
# ------------------------------------------

print("\n6. Standard Deviation:")
print(df[numerical_columns].std())


print("\n" + "=" * 60)
print("EDA STEP 3 COMPLETED")
print("=" * 60)
# ==========================================
# EDA STEP 4 - VISUALIZATION
# RECOMMENDATION DISTRIBUTION
# ==========================================

import matplotlib.pyplot as plt

print("\n" + "=" * 60)
print("EDA STEP 4 - VISUALIZATION")
print("=" * 60)

# Recommendation counts
recommendation_counts = df["Recommendation"].value_counts()

print("\nRecommendation counts:")
print(recommendation_counts)

# Create bar chart
plt.figure(figsize=(8, 5))

recommendation_counts.plot(kind="bar")

plt.title("Resume Recommendation Distribution")
plt.xlabel("Recommendation")
plt.ylabel("Number of Resumes")
plt.xticks(rotation=0)

plt.tight_layout()
plt.show()
# ==========================================
# TARGET JOB DISTRIBUTION
# ==========================================

target_job_counts = df["Target_Job"].value_counts()

print("\nTarget Job Distribution:")
print(target_job_counts)

plt.figure(figsize=(9, 5))

target_job_counts.plot(kind="bar")

plt.title("Target Job Distribution")
plt.xlabel("Target Job")
plt.ylabel("Number of Resumes")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
# ==========================================
# EDUCATION DISTRIBUTION
# ==========================================

education_counts = df["Education"].value_counts()

print("\nEducation Distribution:")
print(education_counts)

plt.figure(figsize=(9, 5))

education_counts.plot(kind="bar")

plt.title("Education Distribution")
plt.xlabel("Education")
plt.ylabel("Number of Resumes")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
# ==========================================
# EXPERIENCE LEVEL DISTRIBUTION
# ==========================================

experience_level_counts = df["Experience_Level"].value_counts()

print("\nExperience Level Distribution:")
print(experience_level_counts)

plt.figure(figsize=(8, 5))

experience_level_counts.plot(kind="bar")

plt.title("Experience Level Distribution")
plt.xlabel("Experience Level")
plt.ylabel("Number of Resumes")
plt.xticks(rotation=0)

plt.tight_layout()
plt.show()
# ==========================================
# LOCATION DISTRIBUTION
# ==========================================

location_counts = df["Location"].value_counts()

print("\nLocation Distribution:")
print(location_counts)

plt.figure(figsize=(9, 5))

location_counts.plot(kind="bar")

plt.title("Resume Distribution by Location")
plt.xlabel("Location")
plt.ylabel("Number of Resumes")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
# ==========================================
# EXPERIENCE YEARS DISTRIBUTION
# ==========================================

plt.figure(figsize=(8, 5))

plt.hist(df["Experience_Years"], bins=10)

plt.title("Experience Years Distribution")
plt.xlabel("Experience Years")
plt.ylabel("Number of Resumes")

plt.tight_layout()
plt.show()
# ==========================================
# SKILL MATCH PERCENTAGE DISTRIBUTION
# ==========================================

plt.figure(figsize=(8, 5))

plt.hist(df["Skill_Match_Percentage"], bins=10)

plt.title("Skill Match Percentage Distribution")
plt.xlabel("Skill Match Percentage")
plt.ylabel("Number of Resumes")

plt.tight_layout()
plt.show()
# ==========================================
# RESUME SCORE DISTRIBUTION
# ==========================================

plt.figure(figsize=(8, 5))

plt.hist(df["Resume_Score"], bins=10)

plt.title("Resume Score Distribution")
plt.xlabel("Resume Score")
plt.ylabel("Number of Resumes")

plt.tight_layout()
plt.show()
# ==========================================
# BOX PLOT - NUMERICAL FEATURES
# ==========================================

plt.figure(figsize=(9, 6))

df[
    ["Experience_Years",
     "Skill_Match_Percentage",
     "Resume_Score"]
].boxplot()

plt.title("Box Plot of Numerical Features")
plt.xlabel("Features")
plt.ylabel("Values")

plt.tight_layout()
plt.show()
# ==========================================
# CORRELATION ANALYSIS
# ==========================================

import seaborn as sns

correlation = df[
    ["Experience_Years",
     "Skill_Match_Percentage",
     "Resume_Score"]
].corr()

print("\nCorrelation Matrix:")
print(correlation)

plt.figure(figsize=(8, 6))

sns.heatmap(
    correlation,
    annot=True,
    cmap="coolwarm",
    fmt=".2f"
)

plt.title("Correlation Heatmap")

plt.tight_layout()
plt.show()