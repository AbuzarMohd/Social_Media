import plotly.express as px
import pandas as pd

FOCUSED_EMOTIONS = ["joy", "sadness", "anger", "fear", "neutral"]

def emotion_timeline_chart(df):
    # Melt DataFrame for Plotly line chart
    melt_cols = [c for c in df.columns if c in FOCUSED_EMOTIONS]
    if not melt_cols:
        return px.line(title="No emotion columns present")
    long = df[["time", *melt_cols]].melt(id_vars="time", var_name="emotion", value_name="score")
    long["time"] = pd.to_datetime(long["time"])
    fig = px.line(long, x="time", y="score", color="emotion", title="Emotion Trend Over Time")
    fig.update_layout(showlegend=True, height=400)
    return fig