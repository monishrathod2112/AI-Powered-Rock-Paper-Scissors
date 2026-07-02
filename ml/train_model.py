import pandas as pd
import joblib

from sklearn.tree import DecisionTreeClassifier

# Load Dataset
data = pd.read_csv("ml/dataset.csv")

print("Dataset Loaded Successfully")
print(data.head())

# Convert Text to Numbers
mapping = {
    "rock": 0,
    "paper": 1,
    "scissors": 2
}

data["player_move"] = data["player_move"].map(mapping)
data["next_move"] = data["next_move"].map(mapping)

# Features (Input)
X = data[["player_move"]]

# Target (Output)
y = data["next_move"]

# Create Model
model = DecisionTreeClassifier()

# Train Model
model.fit(X, y)

# Save Model
joblib.dump(model, "ml/model.pkl")

print("✅ Model Trained Successfully!")
print("✅ model.pkl Saved Successfully!")