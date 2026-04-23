# B2B Lead Scoring - TFM Nuclio Data Science & AI

Predictive lead scoring system for B2B outbound prospecting, built on real campaign data from multiple clients across Spain and LATAM.

**The problem:** SDR teams contact hundreds of leads per week without a reliable way to prioritize. Most effort goes to leads that will never reply.

**The solution:** A LightGBM model that scores each contact (0-1) based on seniority, department, company profile, and engagement history, trained on 10,946 contacts with verified reply outcomes.

---

## Results

| Metric | Value |
|---|---|
| ROC-AUC | 0.81 |
| Lift @ top 10% | 3.6x |
| Precision @ top 100 | 38% |
| Clusters identified | 7 |

**Business impact:** Concentrating outreach on the top 10% of scored leads produces 3.6x more replies than random contact, equivalent to ~25 additional sales conversations per week at zero incremental cost.

---

## Structure

```
notebooks/         : end-to-end analysis pipeline
  01_data_loading.ipynb      : data ingestion and validation
  02_eda.ipynb               : exploratory analysis and reply rate by segment
  03_feature_engineering.ipynb: feature construction and NLP processing
  04_models.ipynb            : model competition, Optuna tuning, SHAP analysis
  05_mlops.ipynb             : packaging, versioning, monitoring setup

app/               : production-ready scoring API + dashboard
  api.py           : FastAPI endpoint for real-time scoring
  streamlit_app.py : interactive dashboard for SDR teams
  models/          : trained model artifacts (.pkl)
  Dockerfile       : containerized deployment
  docker-compose.yml
```

---

## Models

Four models competed on PR-AUC (imbalanced dataset, ~8% positive class):

| Model | ROC-AUC | PR-AUC | Lift@10% |
|---|---|---|---|
| Logistic Regression | 0.72 | 0.18 | 2.1x |
| Random Forest | 0.76 | 0.22 | 2.6x |
| CatBoost | 0.79 | 0.26 | 3.1x |
| **LightGBM (Optuna)** | **0.81** | **0.28** | **3.6x** |

Hyperparameter tuning via Optuna (50 trials). Feature importance via SHAP.

**Top features:** seniority level, LinkedIn connection count, department (Sales & MKT scores highest), company size, engagement history.

---

## Running the app

```bash
cd app
docker-compose up
```

- API: `http://localhost:8000/docs`
- Dashboard: `http://localhost:8501`

> Data files are not included in this repo. See `app/data/README.md` for the expected schema.

---

## Stack

Python · LightGBM · scikit-learn · Optuna · SHAP · K-Means · UMAP · FastAPI · Streamlit · Docker
