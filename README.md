# AthleteShield

**A wearable-sensor-driven machine learning system for predicting non-contact musculoskeletal injury risk in athletes.**

AthleteShield fuses IMU, GPS/GNSS, HRV, and wellness-screening data into a per-athlete feature store and uses tree-ensemble models (Random Forest, XGBoost, LightGBM) to flag elevated injury risk early enough for coaching and medical staff to intervene — with SHAP-based explainability so every risk score can be traced back to specific, clinically meaningful load factors.

This repo contains the full implementation notebook and the accompanying project report.

---

## Contents

| File | Description |
|---|---|
| `AthleteShield.ipynb` | End-to-end notebook: data ingestion, EDA, feature engineering, model training, tuning, calibration, and SHAP interpretation. |
| `AthleteShield_Report.docx` | Full project report — design, literature survey, architecture, and detailed implementation/results (36 pages). |

---

## Problem

Non-contact injuries (ACL tears, hamstring strains) are the leading controllable cause of lost athlete availability, yet most teams still rely on reactive, subjective judgement rather than the sensor data they already collect. AthleteShield asks: **can wearable biomechanical and physiological signals be fused and modelled to flag elevated injury risk before it happens, not after?**

## Approach

Rather than one model for every problem, AthleteShield trains three purpose-built models across four data sources:

| Model | Task | Data | Result |
|---|---|---|---|
| **Model A** | Next-season injury risk (classification) | University football screening + lifestyle data (800 rows, balanced) | Random Forest, ROC-AUC **0.982**, 93% accuracy |
| **Model B** | Acute/near-term injury risk (classification) | Collegiate athlete data fused with wearable + IMU features (200 rows, 7% positive) | Calibrated XGBoost, ROC-AUC **0.982** |
| **Model C** | Sidelined-days prediction (regression) | Professional football workload/injury-history data (1,301 rows, 604 players) | Random Forest Regressor, R² **0.324**, RMSE 78.5 days |

Full methodology, EDA, and caveats for each model are in the report (Sections 9–14).

## Pipeline

```
Raw sensors (IMU, GPS/GNSS, HRV, wellness screening)
        │
        ▼
Data ingestion & quality audit  (missingness, duplicates, leakage checks)
        │
        ▼
Exploratory data analysis  (per-dataset distributions, correlations, PCA)
        │
        ▼
Feature engineering & sensor fusion
  · ACWR, monotony, strain, workload/recovery ratios
  · IMU signal processing (Butterworth filter → step detection → jerk/FFT)
  · Wearable telemetry aggregation
  · VIF-based multicollinearity pruning
        │
        ▼
Model training & tuning  (Optuna + 5-fold CV, SMOTE for class imbalance)
        │
        ▼
Calibration & threshold optimisation  (Platt scaling, F1/F2-optimal thresholds)
        │
        ▼
SHAP explainability  (global summary + per-athlete waterfall)
```

## Key libraries

`pandas`, `numpy`, `scikit-learn`, `xgboost`, `lightgbm`, `imbalanced-learn` (SMOTE), `optuna`, `statsmodels` (VIF), `shap`, `scipy` (signal processing), `matplotlib`, `seaborn`, `joblib`.

## Getting started

```bash
pip install pandas numpy scikit-learn xgboost lightgbm imbalanced-learn \
            optuna statsmodels shap scipy matplotlib seaborn joblib jupyter
jupyter notebook AthleteShield.ipynb
```

Run all cells top to bottom — the notebook is self-contained and seeded (`random_state=42`) for reproducibility.

## Known limitations

- Model B's test set has only 3 positive cases — reported metrics are directional, not statistically robust.
- `ACL_Risk_Score` (Model B's dominant feature) has unverified provenance and was flagged as a possible leakage risk.
- Wearable/IMU features are only real for 10 of 200 collegiate athletes; the rest are mean-imputed.
- All models are evaluated retrospectively — none has been validated prospectively on live, unseen-outcome data yet.

Full discussion: Report, Section 16.

## Future work

- Prospective, silent-logging trial across a full season
- Full-cohort wearable coverage (remove the imputation gap)
- Independent re-derivation/verification of `ACL_Risk_Score`
- Federated learning across clubs; richer sensor fusion (EMG, force plates)

Full discussion: Report, Section 17.

## Authors

Sri Saatwik Nalluri (23MID0438) · Pakala Puneeth (23MID0291)
