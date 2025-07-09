import sys
import subprocess

try:
    import openpyxl
except ImportError:
    print("openpyxl not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
    import openpyxl

import pandas as pd

# Load the dataset
file_path = '5-CobotOps/data/dataset_02052023.xlsx'
df = pd.read_excel(file_path)

# Print the first few rows and info to inspect structure
print('First 5 rows:')
print(df.head())
print('\nColumns:')
print(df.columns)
print('\nInfo:')
df.info()
print('\nMissing values per column:')
print(df.isnull().sum())

# --- ML Pipeline ---
# Clean up column names (remove trailing spaces)
df = df.rename(columns=lambda x: x.strip())

# Drop rows where the target is NaN
df = df.dropna(subset=['Robot_ProtectiveStop'])

# Drop columns not useful for ML
X = df.drop(columns=['Robot_ProtectiveStop', 'Timestamp', 'Num'])
y = df['Robot_ProtectiveStop']

# For simplicity, drop non-numeric columns (if any)
X = X.select_dtypes(include=['number', 'bool'])

# Fill missing values with column means (for numeric) or mode (for bool)
for col in X.columns:
    if X[col].dtype == 'bool':
        X[col] = X[col].fillna(X[col].mode().iloc[0])
    else:
        X[col] = X[col].fillna(X[col].mean())

# Train/test split
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a RandomForestClassifier
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)

# Predict and evaluate
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
y_pred = clf.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Print overall accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy:.4f}")

# Feature importances
importances = clf.feature_importances_
feature_names = X.columns
print("\nFeature Importances:")
for name, importance in zip(feature_names, importances):
    print(f"{name}: {importance:.4f}")
