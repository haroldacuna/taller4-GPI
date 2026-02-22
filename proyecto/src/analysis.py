import pandas as pd
import numpy as np

def project_level_summary(projects: pd.DataFrame, issuance: pd.DataFrame) -> pd.DataFrame:
    agg = issuance.groupby("project_id").agg(
        true_total=("true_reduction_tCO2", "sum"),
        reported_total=("reported_reduction_tCO2", "sum"),
        issued_total=("issued_credits", "sum"),
        retired_total=("retired_credits", "sum"),
        buffer_total=("buffer_credits", "sum"),
        over_total=("overcrediting_tCO2", "sum"),
        risk_events=("delivery_risk_flag", "sum"),
    ).reset_index()

    df = projects.merge(agg, on="project_id", how="left")

    df["over_rate"] = np.where(df["reported_total"] > 0, df["over_total"] / df["reported_total"], 0.0)
    df["retire_rate"] = np.where(df["issued_total"] > 0, df["retired_total"] / df["issued_total"], 0.0)

    # Score simple de “riesgo reputacional / calidad”
    df["integrity_risk_score"] = (
        0.45 * (1 - df["mrv_quality"]) +
        0.25 * (1 - df["additionality_score"]) +
        0.20 * df["permanence_risk"] +
        0.10 * df["leakage_rate"]
    )

    return df.sort_values(["integrity_risk_score", "over_rate"], ascending=False)

def market_revenue(issuance: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    df = issuance.merge(prices, on="month", how="left")
    df["gross_revenue_usd"] = (df["retired_credits"] * df["price_usd"]).round(2)
    return df