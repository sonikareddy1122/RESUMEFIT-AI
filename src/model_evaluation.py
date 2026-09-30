import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.sparse import hstack, csr_matrix

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# ==========================================
# ML STEP 8 - DETAILED MODEL EVALUATION
# ==========================================

df = pd.read_csv("data/cleaned_resume_dataset.csv")

print("=" * 60)
print("ML STEP 8 - DETAILED MODEL EVALUATION")
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
# TF-IDF
# ==========================================

vectorizer = TfidfVectorizer(
    lowercase=True,
    token_pattern=r"(?u)\b\w+\b"
)

skills_train = vectorizer.fit_transform(
    X_train["Skills"]
)

skills_test = vectorizer.transform(
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
# EXPERIENCE
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


# ==========================================
# MODELS
# ==========================================

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    ),

    "Naive Bayes": MultinomialNB()
}


# ==========================================
# EVALUATION
# ==========================================

results = []

for name, model in models.items():

    print("\nTraining:", name)

    model.fit(
        X_train_final,
        y_train
    )

    y_pred = model.predict(
        X_test_final
    )

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    results.append({
        "Model": name,
        "Accuracy": accuracy * 100,
        "Precision": precision * 100,
        "Recall": recall * 100,
        "F1 Score": f1 * 100
    })

    print(f"Accuracy  : {accuracy * 100:.2f}%")
    print(f"Precision : {precision * 100:.2f}%")
    print(f"Recall    : {recall * 100:.2f}%")
    print(f"F1 Score  : {f1 * 100:.2f}%")


# ==========================================
# RESULTS TABLE
# ==========================================

results_df = pd.DataFrame(results)

print("\n" + "=" * 60)
print("FINAL MODEL EVALUATION")
print("=" * 60)

print(
    results_df.to_string(
        index=False,
        formatters={
            "Accuracy": "{:.2f}".format,
            "Precision": "{:.2f}".format,
            "Recall": "{:.2f}".format,
            "F1 Score": "{:.2f}".format
        }
    )
)


# ==========================================
# F1 SCORE COMPARISON
# ==========================================

plt.figure(figsize=(9, 6))

bars = plt.bar(
    results_df["Model"],
    results_df["F1 Score"]
)

plt.title("Model F1 Score Comparison")
plt.xlabel("Machine Learning Model")
plt.ylabel("F1 Score (%)")
plt.ylim(0, 100)

for bar, value in zip(
    bars,
    results_df["F1 Score"]
):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 1,
        f"{value:.2f}%",
        ha="center"
    )

plt.xticks(rotation=15)
plt.tight_layout()
plt.show()


# ==========================================
# RANDOM FOREST CONFUSION MATRIX
# ==========================================

rf_model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

rf_model.fit(
    X_train_final,
    y_train
)

rf_pred = rf_model.predict(
    X_test_final
)

cm = confusion_matrix(
    y_test,
    rf_pred
)

plt.figure(figsize=(8, 6))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    xticklabels=rf_model.classes_,
    yticklabels=rf_model.classes_
)

plt.title("Random Forest Confusion Matrix")
plt.xlabel("Predicted Recommendation")
plt.ylabel("Actual Recommendation")

plt.tight_layout()
plt.show()


print("\n" + "=" * 60)
print("ML STEP 8 COMPLETED")
print("=" * 60)

