import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, accuracy_score
from xgboost import XGBClassifier
import joblib

# Training/Validation Dataset
df = pd.read_csv("datasets/kaggle_test.csv")
X_text = df["text"].astype(str)
y = df["generated"].astype(int)

# Preprocessing
def remove_tags(text):
    tags = ['\n', '\'']
    for tag in tags:
        text = text.replace(tag, '')
    return text

df['text'] = df['text'].apply(remove_tags)

# Balance to 1:1
sample_df = pd.DataFrame({'text': X_text, 'label': y})

majority_class = sample_df[sample_df['label'] == 0]
minority_class = sample_df[sample_df['label'] == 1]

majority_downsampled = majority_class.sample(n=len(minority_class), random_state=42)

balanced_df = pd.concat([majority_downsampled, minority_class])

balanced_df = balanced_df.sample(frac=1, random_state=42)

X_balanced = balanced_df['text']
y_balanced = balanced_df['label']

# Train/Validation Split
X_train_text, X_val_text, y_train, y_val = train_test_split(
    X_balanced, y_balanced, test_size=0.2, random_state=42, stratify=y_balanced
)

# TF-IDF Vectorization
tfidf = TfidfVectorizer(
    max_features=30000,
    ngram_range=(1, 3),
    sublinear_tf=True,
)

X_train = tfidf.fit_transform(X_train_text)
X_val   = tfidf.transform(X_val_text)

num_ai = y_train.sum()
num_human = len(y_train) - num_ai
ai_weight = num_human / num_ai

# Train XGBoost
model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="binary:logistic",
    eval_metric="logloss",
    tree_method="hist",
    scale_pos_weight=ai_weight,
    early_stopping_rounds=50,
    verbose=True
)

model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)]
)

model.save_model("xgb_model.json")
joblib.dump(model, "xgb_model.joblib")

# Evaluate on training set
y_train_pred = model.predict(X_train)

print("\nTraining Performance")
print("Training Accuracy:", accuracy_score(y_train, y_train_pred))
print("Training Classification Report:\n")
print(classification_report(y_train, y_train_pred))

# Evaluate on validation set
y_val_pred = model.predict(X_val)

print("\nValidation Performance")
print("Validation Accuracy:", accuracy_score(y_val, y_val_pred))
print("Validation Classification Report:\n")
print(classification_report(y_val, y_val_pred))

# Testing Data
df_test = pd.read_csv("datasets/ieee_train.csv")
X_text_test = df_test["processed_text"].astype(str)
y_test = df_test["label"].astype(int)

X_text_test = tfidf.transform(X_text_test) # TF-IDF Vectorization

# Evaluate on test set
y_test_pred = model.predict(X_text_test)
print("\nTest Performance")
print("Test Accuracy:", accuracy_score(y_test, y_test_pred))
print("Test Classification Report:\n")
print(classification_report(y_test, y_test_pred))