import pandas as pd
import matplotlib.pyplot as plt

from scipy.sparse import hstack, csr_matrix

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB

from sklearn.metrics import accuracy_score


# ==========================================
# ML STEP 7 - MODEL COMPARISON
# ==========================================

df = pd.read_csv("data/cleaned_resume_dataset.csv")

print("=" * 60)
print("MACHINE LEARNING - STEP 7")
print("MODEL COMPARISON")
print("=" * 60)


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
# TF-IDF FOR SKILLS
# ==========================================

skills_vectorizer = TfidfVectorizer(
    lowercase=True,
    token_pattern=r"(?u)\b\w+\b"
)

skills_train = skills_vectorizer.fit_transform(
    X_train["Skills"]
)

skills_test = skills_vectorizer.transform(
    X_test["Skills"]
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

encoded_test = encoder.transform(
    X_test[categorical_features]
)


# ==========================================
# EXPERIENCE YEARS
# ==========================================

experience_train = csr_matrix(
    X_train[["Experience_Years"]].values
)

experience_test = csr_matrix(
    X_test[["Experience_Years"]].values
)


# ==========================================
# COMBINE FEATURES
# ==========================================

X_train_final = hstack([
    skills_train,
    encoded_train,
    experience_train
]).tocsr()

X_test_final = hstack([
    skills_test,
    encoded_test,
    experience_test
]).tocsr()


print("\nFinal Training Shape:")
print(X_train_final.shape)

print("\nFinal Testing Shape:")
print(X_test_final.shape)


# ==========================================
# MODEL 1 - LOGISTIC REGRESSION
# ==========================================

logistic_model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=42
)

logistic_model.fit(
    X_train_final,
    y_train
)

logistic_pred = logistic_model.predict(
    X_test_final
)

logistic_accuracy = accuracy_score(
    y_test,
    logistic_pred
)


# ==========================================
# MODEL 2 - RANDOM FOREST
# ==========================================

random_forest_model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

random_forest_model.fit(
    X_train_final,
    y_train
)

random_forest_pred = random_forest_model.predict(
    X_test_final
)

random_forest_accuracy = accuracy_score(
    y_test,
    random_forest_pred
)


# ==========================================
# MODEL 3 - NAIVE BAYES
# ==========================================

naive_bayes_model = MultinomialNB()

naive_bayes_model.fit(
    X_train_final,
    y_train
)

naive_bayes_pred = naive_bayes_model.predict(
    X_test_final
)

naive_bayes_accuracy = accuracy_score(
    y_test,
    naive_bayes_pred
)


# ==========================================
# DISPLAY RESULTS
# ==========================================

print("\n" + "=" * 60)
print("MODEL ACCURACY COMPARISON")
print("=" * 60)

print(
    f"\nLogistic Regression : "
    f"{logistic_accuracy * 100:.2f}%"
)

print(
    f"Random Forest      : "
    f"{random_forest_accuracy * 100:.2f}%"
)

print(
    f"Naive Bayes        : "
    f"{naive_bayes_accuracy * 100:.2f}%"
)


# ==========================================
# CREATE COMPARISON DATA
# ==========================================

model_names = [
    "Logistic Regression",
    "Random Forest",
    "Naive Bayes"
]

accuracies = [
    logistic_accuracy * 100,
    random_forest_accuracy * 100,
    naive_bayes_accuracy * 100
]


# ==========================================
# VISUALIZATION
# ==========================================

plt.figure(figsize=(9, 6))

bars = plt.bar(
    model_names,
    accuracies
)

plt.title("ML Model Accuracy Comparison")
plt.xlabel("Machine Learning Model")
plt.ylabel("Accuracy (%)")

plt.ylim(0, 100)

for bar, accuracy in zip(bars, accuracies):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 1,
        f"{accuracy:.2f}%",
        ha="center"
    )

plt.xticks(rotation=15)
plt.tight_layout()

plt.show()


# ==========================================
# FINAL MESSAGE
# ==========================================

print("\n" + "=" * 60)
print("ML STEP 7 COMPLETED")
print("=" * 60)

