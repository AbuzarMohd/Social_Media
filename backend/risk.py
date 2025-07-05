import numpy as np

def compute_risk_score(df):
    """Very simple risk: mean sadness+anxiety+suicide * 100."""
    sadness = df.get("sadness", 0)
    anxiety = df.get("fear", 0)  # GoEmotions uses "fear" for anxiety‑like
    sui = df.get("suicide_score", 0)
    score = np.clip(((sadness + anxiety) / 2 + sui) * 100, 0, 100)
    return float(score.mean())