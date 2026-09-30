import pandas as pd
import os

input_path = "data/resume_dataset.csv"
df = pd.read_csv(input_path)

print("=" * 50)
print("DATA CLEANING STARTED")
print("=" * 50)

print(f"\nOriginal dataset shape: {df.shape}")

# Missing values before cleaning
print("\nMissing values before cleaning:")
print(df.isnull().sum())

# Remove duplicates
duplicates = df.duplicated().sum()
print(f"\nDuplicate rows found: {duplicates}")

df = df.drop_duplicates()

print(f"Shape after removing duplicates: {df.shape}")

# Fill categorical missing values
categorical_columns = [
    "Education",
    "Experience_Level",
    "Skills",
    "Target_Job",
    "Location",
    "Recommendation"
]

for column in categorical_columns:
    df[column] = df[column].fillna("Unknown")

# Fill numerical missing values
numerical_columns = [
    "Experience_Years",
    "Skill_Match_Percentage",
    "Resume_Score"
]

for column in numerical_columns:
    df[column] = df[column].fillna(df[column].median())

# Validate Experience Years
df = df[
    (df["Experience_Years"] >= 0) &
    (df["Experience_Years"] <= 50)
]

# Validate Skill Match Percentage
df = df[
    (df["Skill_Match_Percentage"] >= 0) &
    (df["Skill_Match_Percentage"] <= 100)
]

# Validate Resume Score
df = df[
    (df["Resume_Score"] >= 0) &
    (df["Resume_Score"] <= 100)
]

# Reset index
df = df.reset_index(drop=True)

# Final checks
print("\nMissing values after cleaning:")
print(df.isnull().sum())

print(f"\nDuplicates after cleaning: {df.duplicated().sum()}")

print("\nFinal dataset shape:")
print(df.shape)

# Save cleaned dataset
os.makedirs("data", exist_ok=True)

output_path = "data/cleaned_resume_dataset.csv"
df.to_csv(output_path, index=False)

print(f"\nCleaned dataset saved to:")
print(output_path)

print("\n" + "=" * 50)
print("DATA CLEANING COMPLETED SUCCESSFULLY")
print("=" * 50)
