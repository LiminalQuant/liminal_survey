import pandas as pd
from pathlib import Path
from datetime import datetime

DATA_PATH = Path("data/responses.csv")
DATA_PATH.parent.mkdir(exist_ok=True)

def load_data():
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH)
    return pd.DataFrame(columns=["timestamp", "survey_id", "answers"])

def save_response(survey_id, answers_dict):
    df = load_data()
    new = pd.DataFrame([{
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "survey_id": survey_id,
        "answers": str(answers_dict)
    }])
    df = pd.concat([df, new], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)
