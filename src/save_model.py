import pandas as pd
import joblib

from scipy.sparse import hstack, csr_matrix

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier


# ==========================================
# ML STEP 9 - SAVE TRAINED MODEL
# ==========================================

print("=" * 60)
print("ML STEP 9 - SAVING TRAINED MODEL")
print("=" * 60)


# ==========================================
# LOAD DATASET
# ==========================================

df = pd.read_csv(
    "data/cleaned_resume_dataset.csv"
)


# ==========================================
# FEATURES AND TARGET
# ==========================================

X = df[
    [
        "Education",
        "Experience_Level",
        "Experience_Years",
        "Skills",
        "Target_Job",
        "Location"
    ]
]

y = df["Recommendation"]


# ==========================================
# TRAIN TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ==========================================
# TF-IDF
# ==========================================

vectorizer = TfidfVectorizer(
    lowercase=True,
    token_pattern=r"(?u)\b\w+\b"
)

skills_train = vectorizer.fit_transform(
    X_train["Skills"]
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

encoder = OneHotEncoder(
    handle_unknown="ignore",
    sparse_output=True
)

encoded_train = encoder.fit_transform(
    X_train[categorical_features]
)


# ==========================================
# EXPERIENCE YEARS
# ==========================================

experience_train = csr_matrix(
    X_train[["Experience_Years"]].values
)


# ==========================================
# COMBINE FEATURES
# ==========================================

X_train_final = hstack([
    skills_train,
    encoded_train,
    experience_train
]).tocsr()


# ==========================================
# TRAIN RANDOM FOREST
# ==========================================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(
    X_train_final,
    y_train
)


# ==========================================
# SAVE MODEL
# ==========================================

joblib.dump(
    model,
    "models/resume_model.pkl"
)

joblib.dump(
    vectorizer,
    "models/tfidf_vectorizer.pkl"
)

joblib.dump(
    encoder,
    "models/encoder.pkl"
)


# ==========================================
# SUCCESS MESSAGE
# ==========================================

print("\nSaved files:")

print("1. models/resume_model.pkl")
print("2. models/tfidf_vectorizer.pkl")
print("3. models/encoder.pkl")

print("\n" + "=" * 60)
print("ML STEP 9 COMPLETED")
print("=" * 60)

