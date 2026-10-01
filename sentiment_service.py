import pandas as pd
import numpy as np

def classify_sentiment(rating):
    if rating >= 4:
        return "Positive"
    elif rating == 3:
        return "Neutral"
    else:
        return "Negative"

def calculate_app_statistics(df):
    if df is None or len(df) == 0:
        raise ValueError("No data available.")
    
    df = df.copy()
    if "Sentiment" not in df.columns:
        df["Sentiment"] = df["Rating"].apply(classify_sentiment)
        
    stats = {}
    for app in df["App"].unique():
        app_df = df[df["App"] == app]
        total = len(app_df)
        pos = len(app_df[app_df["Sentiment"] == "Positive"])
        neu = len(app_df[app_df["Sentiment"] == "Neutral"])
        neg = len(app_df[app_df["Sentiment"] == "Negative"])
        
        stats[app] = {
            "total_reviews": total,
            "avg_rating": float(app_df["Rating"].mean()),
            "median_rating": float(app_df["Rating"].median()),
            "std_rating": float(app_df["Rating"].std(ddof=1)),
            "positive_pct": (pos / total) * 100 if total > 0 else 0,
            "neutral_pct": (neu / total) * 100 if total > 0 else 0,
            "negative_pct": (neg / total) * 100 if total > 0 else 0,
            "total_thumbs": int(app_df["#ThumbsUp"].sum())
        }
    return stats, df