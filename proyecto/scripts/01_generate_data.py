from pathlib import Path
import pandas as pd

from src.config import SimConfig
from src.data_generation import generate_projects, generate_issuance, generate_prices

def main():
    cfg = SimConfig()

    base = Path(__file__).resolve().parents[1]
    raw_dir = base / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    projects = generate_projects(cfg.n_projects, cfg.start_month, cfg.n_months, seed=cfg.seed)
    prices = generate_prices(cfg.start_month, cfg.n_months, seed=cfg.seed)
    issuance = generate_issuance(projects, cfg.start_month, cfg.n_months, seed=cfg.seed)

    projects.to_csv(raw_dir / "projects.csv", index=False)
    prices.to_csv(raw_dir / "prices.csv", index=False)
    issuance.to_csv(raw_dir / "issuance.csv", index=False)

    print("OK: data/raw generado:", raw_dir)

if __name__ == "__main__":
    main()