import joblib
import pandas as pd
# Load Trained Model
model = joblib.load("ml/model.pkl")

# Mapping
mapping = {
    "rock": 0,
    "paper": 1,
    "scissors": 2
}

reverse_mapping = {
    0: "rock",
    1: "paper",
    2: "scissors"
}


def predict_next_move(player_move):

    # Convert move to number
    player = mapping[player_move]

    # Predict next move
    prediction = model.predict(
    pd.DataFrame(
        {"player_move": [player]}
    )
)[0]

    # Convert number back to text
    return reverse_mapping[prediction]