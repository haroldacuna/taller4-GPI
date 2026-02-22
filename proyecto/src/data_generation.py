# proyecto/src/data_generation.py
from __future__ import annotations

import numpy as np
import pandas as pd

PROJECT_TYPES = ["REDD+", "ARR", "Cookstoves", "Renewables"]
COUNTRIES = ["Colombia", "Peru", "Brasil", "Mexico", "Kenya", "Indonesia"]

def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)

def generate_projects(n_projects: int, start_month: str, n_months: int, seed: int = 42) -> pd.DataFrame:
    rng = _rng(seed)
    start = pd.Timestamp(start_month)
    end = start + pd.offsets.MonthBegin(n_months)

    project_id = [f"P{str(i).zfill(4)}" for i in range(1, n_projects + 1)]
    ptype = rng.choice(PROJECT_TYPES, size=n_projects, p=[0.35, 0.20, 0.25, 0.20])
    country = rng.choice(COUNTRIES, size=n_projects)

    # Tamaños y baseline (más altos en REDD+/ARR)
    area_ha = np.where(
        np.isin(ptype, ["REDD+", "ARR"]),
        rng.lognormal(mean=8.5, sigma=0.6, size=n_projects),  # ~ miles de ha
        rng.lognormal(mean=6.0, sigma=0.7, size=n_projects),  # más pequeño
    )
    baseline_tCO2 = np.where(
        ptype == "REDD+",
        rng.lognormal(mean=10.0, sigma=0.6, size=n_projects),
        np.where(
            ptype == "ARR",
            rng.lognormal(mean=9.3, sigma=0.6, size=n_projects),
            rng.lognormal(mean=8.2, sigma=0.7, size=n_projects),
        ),
    )

    # Calidad y riesgos (mrv_quality alto reduce overcrediting esperado)
    additionality_score = rng.beta(a=2.2, b=1.8, size=n_projects)
    mrv_quality = rng.beta(a=2.5, b=1.7, size=n_projects)

    leakage_rate = np.clip(rng.normal(loc=0.12, scale=0.08, size=n_projects), 0, 0.4)
    permanence_risk = np.where(
        np.isin(ptype, ["REDD+", "ARR"]),
        rng.beta(a=2.0, b=2.0, size=n_projects),
        rng.beta(a=1.5, b=3.0, size=n_projects),
    )

    verification_frequency_months = rng.choice([6, 12, 24], size=n_projects, p=[0.45, 0.45, 0.10])

    # Buffer contribution: aumenta con riesgo de permanencia y con leakage
    buffer_contribution_rate = np.clip(
        0.05 + 0.25 * permanence_risk + 0.10 * leakage_rate,
        0.05, 0.35
    )

    # "Verdadera" reducción anualizada (depende de baseline y adicionalidad, penaliza leakage y riesgo)
    true_reduction_tCO2 = baseline_tCO2 * (0.25 + 0.55 * additionality_score) * (1 - leakage_rate) * (1 - 0.25 * permanence_risk)

    df = pd.DataFrame({
        "project_id": project_id,
        "country": country,
        "type": ptype,
        "start_date": start,
        "end_date": end,
        "area_ha": area_ha.round(2),
        "baseline_tCO2": baseline_tCO2.round(2),
        "additionality_score": additionality_score.round(4),
        "mrv_quality": mrv_quality.round(4),
        "leakage_rate": leakage_rate.round(4),
        "permanence_risk": permanence_risk.round(4),
        "verification_frequency_months": verification_frequency_months,
        "buffer_contribution_rate": buffer_contribution_rate.round(4),
        "true_reduction_tCO2": true_reduction_tCO2.round(2),
    })
    return df

def generate_prices(start_month: str, n_months: int, seed: int = 42) -> pd.DataFrame:
    rng = _rng(seed + 1)
    months = pd.date_range(start=start_month, periods=n_months, freq="MS")

    # precio con tendencia suave + volatilidad + shocks
    base = 6.0
    trend = np.linspace(0, 3.0, n_months)  # sube ~3 USD en 5 años
    vol = rng.normal(0, 0.6, size=n_months)
    shocks = np.zeros(n_months)
    shock_idx = rng.choice(np.arange(n_months), size=max(2, n_months // 18), replace=False)
    shocks[shock_idx] = rng.normal(0, 1.8, size=len(shock_idx))

    price = np.clip(base + trend + vol + shocks, 2.0, 25.0)

    return pd.DataFrame({"month": months, "price_usd": price.round(2)})

def generate_issuance(projects: pd.DataFrame, start_month: str, n_months: int, seed: int = 42) -> pd.DataFrame:
    rng = _rng(seed + 2)
    months = pd.date_range(start=start_month, periods=n_months, freq="MS")

    rows = []
    for _, p in projects.iterrows():
        # Distribuye la reducción real anualizada en meses con estacionalidad (sobre todo en REDD+/ARR)
        season = 1.0 + 0.15 * np.sin(np.linspace(0, 2*np.pi, n_months))
        true_monthly = (p["true_reduction_tCO2"] / 12.0) * season
        true_monthly = np.clip(true_monthly, 0, None)

        # Overcrediting esperado: mayor cuando MRV es bajo, adicionalidad baja y verificación menos frecuente
        freq_penalty = {6: 0.00, 12: 0.05, 24: 0.10}[int(p["verification_frequency_months"])]
        expected_bias = (0.35 * (1 - p["mrv_quality"]) + 0.20 * (1 - p["additionality_score"]) + freq_penalty)

        # Ruido + sesgo positivo => reportado >= real en promedio
        noise = rng.normal(0, 0.10, size=n_months)  # 10% ruido
        reported_monthly = true_monthly * (1 + expected_bias + noise)
        reported_monthly = np.clip(reported_monthly, 0, None)

        over = np.clip(reported_monthly - true_monthly, 0, None)

        # Créditos emitidos (1 crédito = 1 tCO2), menos buffer
        issued = reported_monthly
        buffer = issued * p["buffer_contribution_rate"]
        issued_net = np.clip(issued - buffer, 0, None)

        # Retiros: fracción de emitidos netos con variación
        retire_rate = np.clip(rng.normal(loc=0.35, scale=0.12, size=n_months), 0.05, 0.85)
        retired = issued_net * retire_rate

        # Eventos de riesgo: más probables si riesgo de permanencia alto
        risk_prob = 0.01 + 0.04 * p["permanence_risk"]
        risk_flag = rng.random(n_months) < risk_prob

        for m, tr, rr, iss, buf, net, ret, ov, rf in zip(
            months, true_monthly, reported_monthly, issued, buffer, issued_net, retired, over, risk_flag
        ):
            rows.append({
                "project_id": p["project_id"],
                "month": m,
                "true_reduction_tCO2": float(tr),
                "reported_reduction_tCO2": float(rr),
                "issued_credits": float(net),
                "buffer_credits": float(buf),
                "retired_credits": float(ret),
                "overcrediting_tCO2": float(ov),
                "delivery_risk_flag": int(rf),
            })

    df = pd.DataFrame(rows)
    # Redondeos al final
    for c in ["true_reduction_tCO2","reported_reduction_tCO2","issued_credits","buffer_credits","retired_credits","overcrediting_tCO2"]:
        df[c] = df[c].round(3)
    return df