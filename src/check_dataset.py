import pandas as pd

# Load dataset
df = pd.read_csv("data/resume_dataset.csv")

print("=" * 50)
print("DATASET QUALITY CHECK")
print("=" * 50)

print("\n1. Dataset Shape:")
print(df.shape)

print("\n2. Columns:")
print(df.columns.tolist())

print("\n3. Missing Values:")
print(df.isnull().sum())

print("\n4. Duplicate Rows:")
print(df.duplicated().sum())

print("\n5. Data Types:")
print(df.dtypes)

print("\n6. Unique Values:")
for column in df.columns:
    print(f"{column}: {df[column].nunique()}")

print("\n7. Numerical Columns Summary:")
print(df.describe())

print("\n" + "=" * 50)
print("QUALITY CHECK COMPLETED")
print("=" * 50)
