import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
import pickle

# Load the dataset
df = pd.read_csv('loan_prediction_dataset.csv')

# Inspect the dataset
print(df.head())
print(df.columns)

# Data Preprocessing
df.ffill(inplace=True)  # Use ffill() method instead of fillna with 'method'

# Encode categorical features
label_encoders = {}
for column in df.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    df[column] = le.fit_transform(df[column])
    label_encoders[column] = le

# Handle missing values using SimpleImputer
imputer = SimpleImputer(strategy='mean')
df_imputed = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)

# Splitting the dataset
X = df_imputed.drop(columns=['loan_status'])  # Correct column name
y = df_imputed['loan_status']  # Correct column name
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model Training
model = LogisticRegression()
model.fit(X_train, y_train)

# Save the model
with open('loan_model.pkl', 'wb') as file:
    pickle.dump(model, file)

# Save the label encoders
with open('label_encoders.pkl', 'wb') as file:
    pickle.dump(label_encoders, file)
