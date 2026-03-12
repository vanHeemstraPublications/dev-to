---
title: "Scuderia Data Ep.12"
published: false
description: "Episode 12: The Wind Tunnel"
part: 12
tags: [mlflow, databricks, machinelearning, mlops]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/azure-data-platform-f1-episode-12.png"
series: "Azure Data Platform & Formula 1"
canonical_url: ""
organization: "the-software-s-journey"
---

# 💨 Episode 12 — The Wind Tunnel

> *"Every aerodynamic setup is a hypothesis: 'This wing angle will be 0.03 seconds faster.' The wind tunnel tests thousands of hypotheses before the team commits to race specification."*

Machine learning is your **wind tunnel**. Every model is a hypothesis. Every training run is an experiment. And like the wind tunnel, the goal is to find the configuration that wins — repeatably, verifiably, and without crashing.

**MLflow** is the measurement system inside that wind tunnel.

---

## 🔬 MLflow: The Wind Tunnel Instruments

MLflow is the open-source MLOps platform built into Databricks. It tracks every experiment with four components:

| Component | F1 Analogy | What It Does |
|---|---|---|
| **Tracking** | Wind tunnel measurement rig | Logs parameters, metrics, artefacts |
| **Projects** | Experiment specification sheet | Reproducible run definitions |
| **Models** | Race-specification blueprint | Model packaging & format |
| **Registry** | Parts catalogue & sign-off | Model versioning & lifecycle |

---

## 🧪 Experiment Tracking: Every Wind Tunnel Run

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

mlflow.set_experiment("/Experiments/tyre_degradation_model")

# Load Gold feature table
df = spark.read.format("delta").load(".../gold/features/tyre_degradation/").toPandas()
X = df[["tyre_age_laps", "tyre_compound_encoded", "fuel_load_kg", "ambient_temp"]]
y = df["lap_delta_seconds"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# MLflow run — log everything
with mlflow.start_run(run_name="GBR_v3_tyre_compound_feature"):
    
    # Parameters — the wing angle settings
    params = {"n_estimators": 200, "max_depth": 5, "learning_rate": 0.05}
    mlflow.log_params(params)
    
    # Train
    model = GradientBoostingRegressor(**params)
    model.fit(X_train, y_train)
    
    # Metrics — the lap time result
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    mlflow.log_metric("mae_seconds", mae)
    mlflow.log_metric("test_r2", model.score(X_test, y_test))
    
    # Log the model itself
    mlflow.sklearn.log_model(model, "tyre_degradation_model")
    
    print(f"MAE: {mae:.3f} seconds")
```

Now every experiment run is recorded. You can compare 50 runs on the MLflow UI — exactly like comparing 50 wind tunnel configurations on the aero team's dashboard.

---

## 🤖 AutoML: The Automated Wind Tunnel

Don't want to manually test 50 configurations? **Databricks AutoML** does it for you — it's the automated wind tunnel test rig.

```python
from databricks import automl

# AutoML regression — find the best model automatically
summary = automl.regress(
    dataset=spark.read.format("delta").load(".../gold/features/tyre_degradation/"),
    target_col="lap_delta_seconds",
    primary_metric="mae",
    timeout_minutes=60,
    exclude_cols=["session_date", "driver_id"]
)

print(f"Best model: {summary.best_trial.model_path}")
print(f"Best MAE: {summary.best_trial.metrics['val_mae']:.3f}")
```

AutoML generates **explainable notebooks** for every trial — you can see exactly what it tried and why it worked. Then register the best model.

---

## 📋 Model Registry: The Parts Catalogue

Once you've found your race-specification model, register it — with a formal approval process:

```python
# Register the model
mlflow.register_model(
    model_uri=f"runs:/{best_run_id}/tyre_degradation_model",
    name="tyre-degradation-predictor"
)

# Promote through lifecycle stages
client = mlflow.tracking.MlflowClient()

# Staging: tested but not yet race-approved
client.transition_model_version_stage(
    name="tyre-degradation-predictor", version=3, stage="Staging"
)

# Production: race-approved, deployed
client.transition_model_version_stage(
    name="tyre-degradation-predictor", version=3, stage="Production"
)
```

Lifecycle stages map perfectly to F1:
- **None**: Just out of the wind tunnel. Promising but untested.
- **Staging**: On the test track. Validated but not race-ready.
- **Production**: Race specification. In the car. Trusted.
- **Archived**: Previous season's aero. Kept for reference.

---

## 🚀 Model Serving: Real-Time Predictions

Databricks Model Serving deploys your registered model as a REST endpoint:

```python
# Score new data using the Production model
import mlflow.pyfunc

model = mlflow.pyfunc.load_model("models:/tyre-degradation-predictor/Production")

# Predict lap delta for current stint conditions
new_data = pd.DataFrame({
    "tyre_age_laps": [12],
    "tyre_compound_encoded": [1],  # Medium
    "fuel_load_kg": [45.2],
    "ambient_temp": [28]
})

prediction = model.predict(new_data)
print(f"Predicted lap delta: {prediction[0]:.3f} seconds")
```

---

## 🏁 Pit Stop Summary

- MLflow **tracks every experiment**: parameters, metrics, model artefacts — like wind tunnel instruments
- **AutoML** automates experimentation — finds the best model without manual tuning
- The **Model Registry** provides versioning and lifecycle management: None → Staging → Production → Archived
- Use **Model Serving** for real-time inference REST endpoints
- The Gold **feature table** is the ML pipeline's fuel — keep it fresh

**Next Episode →** The car is fast, governed, monitored, and intelligent. Now the world gets to watch — **Power BI and the Race Broadcast**.
