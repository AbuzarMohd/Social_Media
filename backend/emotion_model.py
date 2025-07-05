"""Wraps calls to Hugging Face Inference API for all classifiers."""
import requests, concurrent.futures, os
from typing import List, Dict
from config import get_settings

MODELS = {
    "emotion": "SamLowe/roberta-base-go_emotions",
    "sentiment": "cardiffnlp/twitter-roberta-base-sentiment",
    "suicide": "mental/roberta-suicide-monitor",
}

HF_URL = "https://api-inference.huggingface.co/models/{}"


def _query(model_id: str, inputs: List[str]):
    cfg = get_settings()
    headers = {
        "Authorization": f"Bearer {cfg['HF_TOKEN']}",
        "Content-Type": "application/json",
    }
    response = requests.post(HF_URL.format(model_id), headers=headers, json={"inputs": inputs}, timeout=30)
    response.raise_for_status()
    return response.json()


def analyse_batch(items: List[Dict]):
    texts = [x["text"] for x in items]
    with concurrent.futures.ThreadPoolExecutor() as ex:
        fut_em = ex.submit(_query, MODELS["emotion"], texts)
        fut_sent = ex.submit(_query, MODELS["sentiment"], texts)
        fut_sui = ex.submit(_query, MODELS["suicide"], texts)
        emotions = fut_em.result()
        sentiments = fut_sent.result()
        suicides = fut_sui.result()

    # Flatten into DataFrame‑friendly dicts
    out_rows = []
    for em, se, su in zip(emotions, sentiments, suicides):
        emo_map = {d["label"].lower(): d["score"] for d in em}
        sen_label = se[0]["label"].lower() if isinstance(se[0], dict) else se[0]
        sui_prob = su[0]["score"] if isinstance(su[0], dict) else su[0]
        out_rows.append({**emo_map, "sentiment": sen_label, "suicide_score": sui_prob})
    import pandas as pd
    return pd.DataFrame(out_rows)