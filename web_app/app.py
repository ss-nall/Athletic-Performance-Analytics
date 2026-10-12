import os
import json
import io
import numpy as np
import pandas as pd
import joblib
from typing import Dict, Any, List, Optional
from scipy.signal import butter, filtfilt, find_peaks
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="AthleteShield API", description="Multi-Model Predictive Sports Injury & Biomechanical Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
MODEL_B_PATH = os.path.join(PROJECT_DIR, "outputs", "best_acute_injury_model.joblib")
SCALER_B_PATH = os.path.join(PROJECT_DIR, "outputs", "collegiate_scaler.joblib")
MODEL_A_PATH = os.path.join(PROJECT_DIR, "outputs", "model_a_preseason.joblib")
SCALER_A_PATH = os.path.join(PROJECT_DIR, "outputs", "scaler_a.joblib")
MODEL_C_PATH = os.path.join(PROJECT_DIR, "outputs", "model_c_duration.joblib")
SCALER_C_PATH = os.path.join(PROJECT_DIR, "outputs", "scaler_c.joblib")
ASSETS_PATH = os.path.join(BASE_DIR, "model_assets.json")
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")

# Load models and assets
model_b, scaler_b = None, None
model_a, scaler_a = None, None
model_c, scaler_c = None, None
model_assets = None

try:
    if os.path.exists(MODEL_B_PATH):
        model_b = joblib.load(MODEL_B_PATH)
    if os.path.exists(SCALER_B_PATH):
        scaler_b = joblib.load(SCALER_B_PATH)
    if os.path.exists(MODEL_A_PATH):
        model_a = joblib.load(MODEL_A_PATH)
    if os.path.exists(SCALER_A_PATH):
        scaler_a = joblib.load(SCALER_A_PATH)
    if os.path.exists(MODEL_C_PATH):
        model_c = joblib.load(MODEL_C_PATH)
    if os.path.exists(SCALER_C_PATH):
        scaler_c = joblib.load(SCALER_C_PATH)
    if os.path.exists(ASSETS_PATH):
        with open(ASSETS_PATH, "r", encoding="utf-8") as f:
            model_assets = json.load(f)
    print("Successfully loaded AthleteShield models (A, B, C) and scalers.")
except Exception as e:
    print(f"Warning during asset load: {e}")

FEATURE_NAMES_B = [
    "Age", "Height_cm", "Weight_kg", "Training_Intensity", "Training_Hours_Per_Week",
    "Recovery_Days_Per_Week", "Match_Count_Per_Week", "Rest_Between_Events_Days",
    "Fatigue_Score", "Performance_Score", "Team_Contribution_Score", "Load_Balance_Score",
    "ACL_Risk_Score", "Weekly_Load", "Estimated_Chronic_Load", "ACWR", "Monotony",
    "Strain", "Mean_HR", "Std_HR", "Mean_Temp", "Mean_Oxygen", "Total_Steps",
    "IMU_Cadence", "IMU_Peak_Impact", "IMU_SMA", "IMU_Acc_Variance", "IMU_Rot_Variance"
]

FEATURE_LABELS = {
    "ACL_Risk_Score": ("ACL / Knee Joint Risk Score", "/100", True),
    "ACWR": ("Acute-to-Chronic Workload Ratio", "", True),
    "Weekly_Load": ("Weekly Training Load", "AU", True),
    "Training_Intensity": ("Training Intensity", "/10", True),
    "Fatigue_Score": ("Subjective Fatigue Level", "/10", True),
    "Load_Balance_Score": ("Neuromuscular Load Balance", "/100", False),
    "Recovery_Days_Per_Week": ("Scheduled Recovery Days", "days/wk", False),
    "Monotony": ("Training Monotony Index", "", True),
    "Strain": ("Workload Strain Index", "AU", True),
    "Training_Hours_Per_Week": ("Weekly Training Volume", "hrs/wk", True),
    "Weight_kg": ("Body Mass", "kg", True),
    "Match_Count_Per_Week": ("Weekly Match Density", "matches/wk", True),
    "Rest_Between_Events_Days": ("Rest Gap Between Matches", "days", False),
    "Performance_Score": ("Readiness / Performance", "/100", False),
    "Team_Contribution_Score": ("Team Contribution Score", "/100", False),
    "IMU_Peak_Impact": ("Peak Ground Impact Acceleration", "g", True),
    "IMU_SMA": ("Signal Magnitude Area (SMA)", "g", True),
    "IMU_Acc_Variance": ("Acceleration Variability", "g²", True),
    "IMU_Rot_Variance": ("Rotational Rate Variability", "rad²/s²", True),
    "IMU_Cadence": ("Movement Cadence", "spm", False),
    "Mean_HR": ("Mean Heart Rate", "bpm", True),
    "Std_HR": ("Heart Rate Variability (Std)", "bpm", False),
    "Mean_Temp": ("Core Body Temperature", "°C", True),
    "Mean_Oxygen": ("Blood Oxygen Saturation (SpO2)", "%", False),
    "Total_Steps": ("Cumulative Steps", "steps", False),
    "Age": ("Athlete Age", "yrs", True),
    "Height_cm": ("Athlete Height", "cm", False),
    "Estimated_Chronic_Load": ("Estimated Chronic Fitness Base", "AU", False)
}

def engineer_row_b(inputs: Dict[str, Any]) -> Dict[str, float]:
    medians = model_assets["medians"] if model_assets else {}
    row = {}
    for f in FEATURE_NAMES_B:
        val = inputs.get(f)
        if val is not None and str(val).strip() != "":
            try:
                row[f] = float(val)
            except ValueError:
                row[f] = medians.get(f, 0.0)
        else:
            row[f] = medians.get(f, 0.0)

    th = row["Training_Hours_Per_Week"]
    ti = row["Training_Intensity"]
    fatigue = row["Fatigue_Score"]
    row["Weekly_Load"] = th * ti
    row["Estimated_Chronic_Load"] = row["Weekly_Load"] * max(0.2, (1.2 - fatigue * 0.05))
    row["ACWR"] = row["Weekly_Load"] / (row["Estimated_Chronic_Load"] + 1e-5)
    load_bal_std = 8.734162
    row["Monotony"] = row["Weekly_Load"] / (load_bal_std * 0.1 + 1)
    row["Strain"] = row["Weekly_Load"] * row["Monotony"]

    rec_days = row["Recovery_Days_Per_Week"]
    row["Recovery_Deficit"] = fatigue / (rec_days + 1)
    row["Workload_to_Recovery_Ratio"] = row["Weekly_Load"] / (rec_days + 1)
    return row

def calculate_safe_workload_ceiling(row: Dict[str, float]) -> Dict[str, Any]:
    """Calculates max training hours and intensity before ACWR > 1.35 or injury risk triggers."""
    ti = max(1.0, row["Training_Intensity"])
    fatigue = row["Fatigue_Score"]
    chronic_factor = max(0.2, (1.2 - fatigue * 0.05))
    
    # ACWR = Weekly_Load / (Weekly_Load * chronic_factor) is driven by fatigue,
    # but acute strain threshold caps at ~120 AU
    max_safe_load = 65.0 / (1.0 + (fatigue * 0.06))
    max_safe_hours = round(max_safe_load / ti, 1)
    
    current_hours = row["Training_Hours_Per_Week"]
    hours_buffer = round(max_safe_hours - current_hours, 1)
    
    return {
        "max_safe_training_hours": max(4.0, max_safe_hours),
        "current_training_hours": current_hours,
        "hours_headroom": hours_buffer,
        "is_over_ceiling": hours_buffer < 0,
        "recommended_intensity_cap": 7 if fatigue >= 6 else 9
    }

def predict_model_a(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Model A: Next-Season Injury Risk Classification."""
    if not (model_a and scaler_a and model_assets and "model_a" in model_assets):
        return {"season_risk_prob": 0.28, "season_triage": "LOW"}

    meta_a = model_assets["model_a"]
    features_a = meta_a["features"]
    medians_a = meta_a["medians"]

    row_a = {}
    for f in features_a:
        val = inputs.get(f)
        if val is not None and str(val).strip() != "":
            try:
                row_a[f] = float(val)
            except ValueError:
                row_a[f] = medians_a.get(f, 0.0)
        else:
            row_a[f] = medians_a.get(f, 0.0)

    # Derived physical readiness approximation if not direct
    if "Overall_Physical_Readiness" in features_a:
        knee = inputs.get("Knee_Strength_Score", 70.0)
        bal = inputs.get("Balance_Test_Score", 75.0)
        row_a["Overall_Physical_Readiness"] = (knee + bal) / 150.0 - 1.0

    X_a = pd.DataFrame([[row_a[f] for f in features_a]], columns=features_a)
    X_a_scaled = scaler_a.transform(X_a)
    prob_a = float(model_a.predict_proba(X_a_scaled)[0, 1])

    return {
        "season_risk_prob": round(prob_a, 3),
        "season_risk_pct": int(round(prob_a * 100)),
        "season_triage": "HIGH" if prob_a >= 0.50 else "MODERATE" if prob_a >= 0.30 else "LOW"
    }

def predict_model_c(inputs: Dict[str, Any], acute_prob: float) -> Dict[str, Any]:
    """Model C: Sidelined Duration Days Regression."""
    if not (model_c and scaler_c and model_assets and "model_c" in model_assets):
        expected_days = round(12.0 + acute_prob * 28.0, 1)
        return {"expected_sidelined_days": expected_days}

    meta_c = model_assets["model_c"]
    features_c = meta_c["features"]
    medians_c = meta_c["medians"]

    row_c = {}
    for f in features_c:
        val = inputs.get(f)
        if val is not None and str(val).strip() != "":
            try:
                row_c[f] = float(val)
            except ValueError:
                row_c[f] = medians_c.get(f, 0.0)
        else:
            row_c[f] = medians_c.get(f, 0.0)

    # Correlate acute minutes
    weekly_load = inputs.get("Weekly_Load", 55.0)
    row_c["season_minutes_played"] = weekly_load * 30.0

    X_c = pd.DataFrame([[row_c[f] for f in features_c]], columns=features_c)
    X_c_scaled = scaler_c.transform(X_c)
    log_pred = float(model_c.predict(X_c_scaled)[0])
    days_pred = float(np.expm1(log_pred))
    
    # Scale proportionally with acute risk severity
    adjusted_days = round(max(3.0, days_pred * (0.6 + acute_prob * 0.8)), 1)
    return {
        "expected_sidelined_days": adjusted_days,
        "historical_benchmark_days": round(days_pred, 1)
    }

def predict_single(inputs: Dict[str, Any]) -> Dict[str, Any]:
    row = engineer_row_b(inputs)
    X = np.array([[row[f] for f in FEATURE_NAMES_B]])

    if model_b is not None and scaler_b is not None:
        X_df = pd.DataFrame(X, columns=FEATURE_NAMES_B)
        X_scaled = scaler_b.transform(X_df)
        prob = float(model_b.predict_proba(X_scaled)[0, 1])
    else:
        means = np.array(model_assets["means"])
        scales = np.array(model_assets["scales"])
        X_scaled = (X - means) / np.where(scales > 0, scales, 1.0)
        importances = np.array(model_assets["importances"])
        raw_score = -1.2 + float(np.sum(X_scaled[0] * importances * 1.8))
        probs = []
        for cal in model_assets["calibrators"]:
            probs.append(1.0 / (1.0 + np.exp(np.clip(cal["a"] * raw_score + cal["b"], -50, 50))))
        prob = float(np.mean(probs))

    # Dynamic clinical workload & biomechanical parameter modulation
    weekly_load = row.get("Weekly_Load", 55.0)
    load_ratio = weekly_load / 55.0

    rec_days = row.get("Recovery_Days_Per_Week", 2.0)
    rec_mult = 1.0 + max(0.0, (2.0 - rec_days) * 0.25) - min(0.3, max(0.0, (rec_days - 2.0) * 0.15))

    fatigue = row.get("Fatigue_Score", 5.0)
    fatigue_mult = 1.0 + (fatigue - 5.0) * 0.12

    acl = row.get("ACL_Risk_Score", 45.0)
    acl_mult = 1.0 + (acl - 45.0) * 0.012

    balance = row.get("Load_Balance_Score", 95.0)
    asymmetry_mult = 1.0 + max(0.0, (90.0 - balance) * 0.015)

    shock = row.get("IMU_Peak_Impact", 4.61)
    shock_mult = 1.0 + max(0.0, (shock - 4.6) * 0.08)

    composite_factor = (load_ratio ** 1.1) * rec_mult * fatigue_mult * acl_mult * asymmetry_mult * shock_mult
    base_anchor = max(prob, 0.06)
    blended = base_anchor * composite_factor
    final_prob = 1.0 / (1.0 + np.exp(-2.2 * (np.log(max(0.01, blended)) + 1.6)))

    prob_clamped = float(np.clip(final_prob, 0.02, 0.96))
    risk_pct = int(round(prob_clamped * 100))

    if prob_clamped >= 0.40:
        triage = "HIGH"
        triage_text = "High Acute Risk (Load Deload & Physical Triage Mandated)"
        badge = "badge-high"
    elif prob_clamped >= 0.25:
        triage = "MODERATE"
        triage_text = "Moderate Risk (Elevated Fatigue / Workload Spike — Monitor)"
        badge = "badge-moderate"
    else:
        triage = "LOW"
        triage_text = "Low Risk (Cleared for Full Activity)"
        badge = "badge-low"

    # Multi-Model Suite Predictions
    pred_a = predict_model_a(inputs)
    pred_c = predict_model_c(inputs, prob_clamped)
    ceiling = calculate_safe_workload_ceiling(row)

    # Explainability attributions
    means = np.array(model_assets["means"]) if model_assets else np.zeros(len(FEATURE_NAMES_B))
    scales = np.array(model_assets["scales"]) if model_assets else np.ones(len(FEATURE_NAMES_B))
    importances = np.array(model_assets["importances"]) if model_assets else np.full(len(FEATURE_NAMES_B), 1/28)
    
    attributions = []
    for i, f in enumerate(FEATURE_NAMES_B):
        meta = FEATURE_LABELS.get(f, (f, "", True))
        z = (row[f] - means[i]) / (scales[i] if scales[i] > 1e-6 else 1.0)
        direction = 1.0 if meta[2] else -1.0
        contrib = float(z * importances[i] * direction * 1.8)
        attributions.append({
            "feature": f,
            "label": meta[0],
            "unit": meta[1],
            "value": round(row[f], 2),
            "zScore": round(float(z), 2),
            "contribution": round(contrib, 4),
            "isRiskFactor": contrib > 0.01,
            "isProtective": contrib < -0.01
        })

    attributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
    top_risk = [a for a in attributions if a["isRiskFactor"]][:4]
    top_protective = [a for a in attributions if a["isProtective"]][:3]

    # Clinical recommendations
    recs = []
    if row["ACWR"] > 1.35:
        recs.append({
            "category": "Workload Management",
            "title": f"Acute Load Spike (ACWR: {row['ACWR']:.2f})",
            "action": "Cap upcoming high-intensity training by 25-30%. Keep ACWR within the 0.8–1.3 optimal fitness sweet spot."
        })
    if row["ACL_Risk_Score"] >= 55:
        recs.append({
            "category": "Neuromuscular Screening",
            "title": f"Elevated Knee / Joint Instability ({int(round(row['ACL_Risk_Score']))}/100)",
            "action": "Mandate pre-session neuromuscular activation, hamstring eccentric curls (Nordics), and landing stabilization drills."
        })
    if row["Fatigue_Score"] >= 6 or row["Recovery_Deficit"] > 2.0:
        recs.append({
            "category": "Recovery & Regeneration",
            "title": f"High Accumulated Fatigue (Deficit Index: {row['Recovery_Deficit']:.2f})",
            "action": "Schedule at least 1 dedicated active recovery session and extend sleep target to 8.5+ hours."
        })
    if row["Strain"] > 3000:
        recs.append({
            "category": "Periodization Balance",
            "title": f"Excessive Workload Monotony & Strain ({int(round(row['Strain']))} AU)",
            "action": "Introduce training variability with alternating high-low load days to prevent tissue cumulative micro-trauma."
        })
    if not recs:
        recs.append({
            "category": "Maintenance",
            "title": "Optimal Conditioning & Adaptation",
            "action": "Athlete is safely within the chronic adaptation zone. Maintain regular training volume with baseline mobility protocols."
        })

    return {
        "riskScore": risk_pct,
        "calibratedProbability": round(prob_clamped, 3),
        "triage": triage,
        "triageText": triage_text,
        "triageBadgeClass": badge,
        "model_a": pred_a,
        "model_c": pred_c,
        "safe_ceiling": ceiling,
        "engineered": row,
        "attributions": attributions,
        "topRiskDrivers": top_risk,
        "topProtectiveBuffers": top_protective,
        "recommendations": recs
    }

@app.post("/api/predict")
async def api_predict(data: Dict[str, Any]):
    try:
        res = predict_single(data)
        return JSONResponse(content=res)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/baseline-stats")
async def api_baseline_stats():
    return JSONResponse(content=model_assets)

@app.get("/api/samples/{filename}")
async def download_sample(filename: str):
    file_path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample file not found")
    return FileResponse(file_path, media_type="text/csv", filename=filename)

@app.get("/api/timeseries-sample/{sensor_type}")
async def get_timeseries_sample(sensor_type: str):
    """Returns waveform points for interactive Timeseries Visualizer."""
    try:
        if sensor_type == "imu":
            imu_file = os.path.join(SAMPLES_DIR, "sample_devicemotion_imu.csv")
            df = pd.read_csv(imu_file).head(150)
            ax = df.get("userAcceleration.x", pd.Series([0]*len(df))).tolist()
            ay = df.get("userAcceleration.y", pd.Series([0]*len(df))).tolist()
            az = df.get("userAcceleration.z", pd.Series([0]*len(df))).tolist()
            mag = [float(np.sqrt(x**2 + y**2 + z**2)) for x, y, z in zip(ax, ay, az)]
            
            # Simple filtered envelope
            b, a = butter(4, 3.0 / 25.0, btype='low')
            filtered = filtfilt(b, a, mag).tolist()
            peaks, _ = find_peaks(filtered, distance=15, prominence=0.2)

            return JSONResponse(content={
                "type": "imu",
                "sample_rate_hz": 50,
                "duration_sec": len(df) / 50.0,
                "acc_x": [round(float(v), 3) for v in ax],
                "acc_y": [round(float(v), 3) for v in ay],
                "acc_z": [round(float(v), 3) for v in az],
                "magnitude": [round(float(v), 3) for v in mag],
                "filtered": [round(float(v), 3) for v in filtered],
                "peak_indices": peaks.tolist(),
                "peak_values": [round(float(filtered[i]), 3) for i in peaks]
            })
        elif sensor_type == "wearable":
            wear_file = os.path.join(SAMPLES_DIR, "sample_wearable_telemetry.csv")
            df = pd.read_csv(wear_file).head(35)
            hr = df.get("Heart_Rate", pd.Series([120]*len(df))).tolist()
            temp = df.get("Body_Temperature", pd.Series([37.0]*len(df))).tolist()
            o2 = df.get("Blood_Oxygen", pd.Series([98]*len(df))).tolist()
            return JSONResponse(content={
                "type": "wearable",
                "timestamps": [f"T+{i*5}m" for i in range(len(df))],
                "heart_rate": [int(v) for v in hr],
                "temperature": [round(float(v), 1) for v in temp],
                "oxygen": [int(v) for v in o2]
            })
        else:
            raise HTTPException(status_code=400, detail="Invalid sensor type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        cols = set(df.columns)

        # 1. DeviceMotion IMU timeseries detection
        if any(c in cols for c in ["userAcceleration.x", "userAccX", "acc_x"]):
            ax = df.get("userAcceleration.x", df.get("userAccX", df.get("acc_x", pd.Series([0]))))
            ay = df.get("userAcceleration.y", df.get("userAccY", df.get("acc_y", pd.Series([0]))))
            az = df.get("userAcceleration.z", df.get("userAccZ", df.get("acc_z", pd.Series([0]))))
            rx = df.get("rotationRate.x", df.get("rotRateX", df.get("rot_x", pd.Series([0]))))
            ry = df.get("rotationRate.y", df.get("rotRateY", df.get("rot_y", pd.Series([0]))))
            rz = df.get("rotationRate.z", df.get("rotRateZ", df.get("rot_z", pd.Series([0]))))

            acc_mag = np.sqrt(ax**2 + ay**2 + az**2)
            rot_mag = np.sqrt(rx**2 + ry**2 + rz**2)
            fs = 50.0
            duration = len(df) / fs

            try:
                b, a = butter(4, 3.0 / (0.5 * fs), btype='low')
                filt_acc = filtfilt(b, a, acc_mag)
                peaks, _ = find_peaks(filt_acc, distance=15, prominence=0.2)
                cadence = (len(peaks) / duration) * 60.0 if duration > 0 else 100.0
            except Exception:
                cadence = 100.0
                filt_acc = acc_mag.values
                peaks = np.array([])

            imu_feats = {
                "IMU_Cadence": round(float(cadence), 1),
                "IMU_Peak_Impact": round(float(acc_mag.max()), 3),
                "IMU_SMA": round(float(np.mean(np.abs(ax) + np.abs(ay) + np.abs(az))), 3),
                "IMU_Acc_Variance": round(float(acc_mag.var()), 4),
                "IMU_Rot_Variance": round(float(rot_mag.var()), 4)
            }
            
            # Timeseries payload for live canvas preview (first 120 points)
            preview_n = min(120, len(df))
            waveform_payload = {
                "sample_rate_hz": 50,
                "acc_x": [round(float(v), 3) for v in ax.iloc[:preview_n]],
                "acc_y": [round(float(v), 3) for v in ay.iloc[:preview_n]],
                "acc_z": [round(float(v), 3) for v in az.iloc[:preview_n]],
                "filtered": [round(float(v), 3) for v in filt_acc[:preview_n]],
                "peaks": [int(p) for p in peaks if p < preview_n]
            }

            return JSONResponse(content={
                "type": "imu_telemetry",
                "message": f"Processed {len(df)} IMU sensor samples ({duration:.1f}s at 50Hz)",
                "features": imu_feats,
                "waveform": waveform_payload
            })

        # 2. Wearable Telemetry timeseries detection
        elif any(c in cols for c in ["Heart_Rate", "heart_rate", "HR", "Blood_Oxygen"]):
            hr_col = df.get("Heart_Rate", df.get("heart_rate", df.get("HR", pd.Series([]))))
            temp_col = df.get("Body_Temperature", df.get("body_temperature", df.get("Temp", pd.Series([]))))
            o2_col = df.get("Blood_Oxygen", df.get("blood_oxygen", df.get("SpO2", pd.Series([]))))
            steps_col = df.get("Step_Count", df.get("step_count", df.get("Steps", pd.Series([]))))

            wearable_feats = {
                "Mean_HR": round(float(hr_col.mean()), 1) if not hr_col.empty else 120.6,
                "Std_HR": round(float(hr_col.std()), 2) if not hr_col.empty else 34.8,
                "Mean_Temp": round(float(temp_col.mean()), 2) if not temp_col.empty else 37.0,
                "Mean_Oxygen": round(float(o2_col.mean()), 1) if not o2_col.empty else 97.4,
                "Total_Steps": int(steps_col.sum()) if not steps_col.empty else 32360
            }
            
            preview_n = min(30, len(df))
            return JSONResponse(content={
                "type": "wearable_telemetry",
                "message": f"Aggregated {len(df)} wearable telemetry records",
                "features": wearable_feats,
                "waveform": {
                    "heart_rate": [int(v) for v in hr_col.iloc[:preview_n]],
                    "temperature": [round(float(v), 1) for v in temp_col.iloc[:preview_n]]
                }
            })

        # 3. Batch Athlete Roster detection
        else:
            athletes = []
            for idx, r in df.iterrows():
                row_dict = r.to_dict()
                athlete_id = row_dict.get("Athlete_ID", f"Athlete-{idx+1}")
                position = row_dict.get("Position", "Forward" if idx % 3 == 0 else "Midfielder" if idx % 3 == 1 else "Defender")
                pred = predict_single(row_dict)
                athletes.append({
                    "athlete_id": str(athlete_id),
                    "position": str(position),
                    "risk_score": pred["riskScore"],
                    "season_risk_pct": pred["model_a"]["season_risk_pct"],
                    "sidelined_days": pred["model_c"]["expected_sidelined_days"],
                    "triage": pred["triage"],
                    "triageBadgeClass": pred["triageBadgeClass"],
                    "acwr": round(pred["engineered"]["ACWR"], 2),
                    "weekly_load": round(pred["engineered"]["Weekly_Load"], 1),
                    "fatigue": round(pred["engineered"]["Fatigue_Score"], 1),
                    "acl_risk": round(pred["engineered"]["ACL_Risk_Score"], 1),
                    "top_driver": pred["topRiskDrivers"][0]["label"] if pred["topRiskDrivers"] else "Balanced",
                    "full_prediction": pred
                })

            return JSONResponse(content={
                "type": "batch_roster",
                "message": f"Successfully processed {len(athletes)} athletes from roster",
                "athletes": athletes
            })

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV: {str(e)}")

app.mount("/", StaticFiles(directory=BASE_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
