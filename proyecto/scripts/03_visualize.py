from pathlib import Path
import pandas as pd

from src.analysis import project_level_summary, market_revenue

def main():
    base = Path(__file__).resolve().parents[1]
    raw_dir = base / "data" / "raw"
    proc_dir = base / "data" / "processed"
    tables_dir = base / "results" / "tables"
    proc_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    projects = pd.read_csv(raw_dir / "projects.csv")
    prices = pd.read_csv(raw_dir / "prices.csv", parse_dates=["month"])
    issuance = pd.read_csv(raw_dir / "issuance.csv", parse_dates=["month"])

    summary = project_level_summary(projects, issuance)
    revenue = market_revenue(issuance, prices)

    summary.to_csv(proc_dir / "project_summary.csv", index=False)
    revenue.to_csv(proc_dir / "issuance_with_revenue.csv", index=False)

    # tablas “top”
    summary.head(20).to_csv(tables_dir / "top20_high_risk_projects.csv", index=False)

    print("OK: data/processed y results/tables generados")

if __name__ == "__main__":
    main()