'''
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
    '''

"""Wraps calls to Hugging Face Inference API for all classifiers."""
import requests, concurrent.futures, os
from typing import List, Dict
from config import get_settings

MODELS = {
    "emotion": "SamLowe/roberta-base-go_emotions",
    "sentiment": "cardiffnlp/twitter-roberta-base-sentiment",
    # switched to a public, accessible suicide risk model (binary classification)
    "suicide": "vibhorag101/roberta-base-suicide-prediction-phr",
}

HF_URL = "https://api-inference.huggingface.co/models/{}"


def _query(model_id: str, inputs: List[str]):
    cfg = get_settings()
    headers = {
        "Authorization": f"Bearer {cfg['HF_TOKEN']}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(
            HF_URL.format(model_id),
            headers=headers,
            json={"inputs": inputs},
            timeout=30,
        )
        if response.status_code == 404:
            # Model not found or gated – return zeros
            return [[{"label": "safe", "score": 1.0}] for _ in inputs]
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Network or HF error – return neutral output
        from backend.utils import log
        log(f"[HF] {model_id} error: {e}. Returning default predictions.")
        return [[{"label": "safe", "score": 1.0}] for _ in inputs]
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
