# chapters_writer_3_4_5.py - Chapters 3, 4, 5 and References
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from generate_report import (
    add_p, add_bullet, add_chapter_title, add_h1, add_h2, add_h3,
    add_figure, add_equation, add_table_data, add_callout_algorithm
)

def write_chapters_3_4_5(doc):
    # ==========================================
    # CHAPTER 3: SYSTEM ARCHITECTURE AND DESIGN
    # ==========================================
    add_chapter_title(doc, 3, "SYSTEM ARCHITECTURE AND DESIGN")
    add_p(doc, "The AthleteShield platform is architected as an end-to-end, edge-deployable, multi-tier intelligence pipeline designed to ingest raw, high-velocity multi-modal sensor streams, compute sport-science-validated kinetic and physiological features, score multi-horizon injury probabilities, and deliver transparent, explainable recommendations to team performance and medical staff.")

    add_h1(doc, "3.1 SYSTEM ARCHITECTURE & END-TO-END DATA FLOW")
    add_p(doc, "The architecture operates across five synchronized functional tiers: (1) Body-Area Sensing, (2) Edge Ingestion and Clock Synchronization, (3) Signal Processing and Rolling Feature Engineering, (4) Multi-Model Machine Learning Ensemble, and (5) Clinical Decision Support. Figure 3.1 illustrates the end-to-end data flow topology.")

    add_figure(doc, "image2.png", "Figure 3.1: AthleteShield Multi-Layer System Architecture and End-to-End Data Flow Pipeline", width=Inches(5.0))

    headers_arch = ["Architectural Layer", "Primary Function", "Underlying Technology & Protocols"]
    data_arch = [
        ["1. Sensing Layer", "Continuous capture of raw tri-axial IMU kinematics, GPS coordinates, and cardiac intervals.", "10-18 Hz GPS/GNSS vests, 50-200 Hz shank/chest IMU pods, 1 Hz chest-strap heart rate monitors."],
        ["2. Edge Gateway Layer", "Aggregate multi-athlete wireless streams, synchronize common clocks, buffer during connectivity dropouts.", "Local BLE / ANT+ receiver hubs, on-premises Linux edge gateway, circular ring buffer."],
        ["3. Preprocessing Layer", "Denoise raw waveforms, interpolate packet drops, and segment into multi-scale sliding windows.", "4th-order low-pass Butterworth filter, cubic spline interpolation, 30s to 28-day sliding windows."],
        ["4. Feature Store Layer", "Maintain per-athlete rolling matrices of workload, recovery, and biomechanical shock indices.", "ACWR rolling window, PlayerLoad, jerk std, spectral energy, recovery deficit index."],
        ["5. Model Layer", "Multi-horizon classification and regression scoring across clinical risk windows.", "Model A (Random Forest), Model B (Optuna-tuned Calibrated XGBoost), Model C (RF Regressor)."],
        ["6. Explainability Layer", "Compute game-theoretic feature attributions and map risk scores to empirical probabilities.", "TreeSHAP kernel, Platt sigmoid probability calibration, local risk factor attribution."],
        ["7. Decision Support Layer", "Translate continuous probabilities into actionable load management advice and alerts.", "Interactive web dashboard, dynamic threshold alarms, safe workload barrier optimizer."],
        ["8. Feedback Loop Layer", "Log confirmed clinical outcomes, near-misses, and injury occurrences for periodic retraining.", "Outcome tagging ledger, scheduled nightly/weekly offline batch retraining pipeline."]
    ]
    col_w_arch = [Inches(1.6), Inches(2.7), Inches(2.2)]
    add_table_data(doc, "Table 3.1: Layer-by-Layer Architectural Specifications and Technology Stack", headers_arch, data_arch, col_w_arch)

    add_h1(doc, "3.2 LAYER-BY-LAYER ARCHITECTURAL MODULES")
    add_h2(doc, "3.2.1 Edge Sensing & Telemetry Ingestion Layer")
    add_p(doc, "Raw multi-modal data streams are captured directly on the athlete's body via miniature wearable sensor nodes. High-frequency tri-axial accelerometer and gyroscope data (50–200 Hz) captures fine-grained impact shocks and angular rotational velocities. Concurrently, GPS/GNSS receivers capture high-speed running and sprint displacement at 10–18 Hz, while chest straps capture cardiac RR-intervals at 1 Hz. These streams transmit via low-latency Bluetooth Low Energy (BLE) and ANT+ protocols to a pitch-side edge gateway, ensuring zero raw health data leaves the team's local physical perimeter.")

    add_h2(doc, "3.2.2 Biomechanical Signal Processing & IMU Feature Extraction")
    add_p(doc, "Raw inertial data contains high-frequency noise from sensor vibration and soft-tissue movement artifacts. The ingestion module applies a zero-phase 4th-order digital low-pass Butterworth filter with a 3 Hz cutoff frequency. Peak detection algorithms segment filtered acceleration into discrete foot-strike cycles, computing real-time cadence and peak ground impact. Fast Fourier Transform (FFT) algorithms project acceleration into the frequency domain, extracting dominant movement frequencies and spectral power densities that differentiate smooth running from erratic, high-impact fatigue patterns.")

    add_h2(doc, "3.2.3 Temporal Workload Modeling & Recovery Dynamics")
    add_p(doc, "Injury risk does not emerge from instantaneous exertion alone, but from the cumulative dynamics of workload accumulation versus physiological restitution. The temporal engine constructs multi-scale sliding windows spanning within-session fatigue (30 seconds to 10 minutes) and longitudinal micro-cycles (7-day acute to 28-day chronic windows). From these windows, the engine computes the Acute:Chronic Workload Ratio (ACWR), training monotony (workload variability), training strain, and recovery deficits.")

    add_h2(doc, "3.2.4 Multimodal Joint Prediction Engine (Models A, B, C)")
    add_p(doc, "Rather than forcing heterogeneous data sources into a single compromised model, AthleteShield decouples predictive intelligence into three specialized, purpose-built models:")
    add_bullet(doc, "Model A (Next-Season Injury Risk Classification): Predicts long-term macro-cycle vulnerability from pre-season physical screening batteries, neuromuscular baseline tests, and lifestyle recovery profiles.", "Model A —")
    add_bullet(doc, "Model B (Acute Short-Term Injury Risk Classification): Predicts acute session-to-session injury probability from fused IMU biomechanics, GPS workload metrics, and cardiac telemetry, optimized for extreme class imbalance.", "Model B —")
    add_bullet(doc, "Model C (Sidelined-Days / Injury-Duration Regression): Predicts the exact number of days an athlete will be incapacitated following an injury, using longitudinal career exposure and historical injury severity under group-aware player splitting.", "Model C —")

    add_h2(doc, "3.2.5 Decision Support & Classification Threshold Optimization")
    add_p(doc, "The decision layer converts uncalibrated model outputs into clinically meaningful guidance. Raw decision scores are transformed into true empirical probabilities using 5-fold Platt sigmoid calibration. Furthermore, the decision engine abandons default 0.5 classification cutoffs, dynamically evaluating precision-recall curves to establish a clinical threshold (0.8044) that maximizes injury recall while preventing alert fatigue.")

    add_h1(doc, "3.3 MATHEMATICAL FORMULATION & GOVERNING EQUATIONS")
    add_p(doc, "The signal processing, workload quantification, and predictive modeling layers are governed by the following mathematical formulations:")
    
    add_p(doc, "1. 4th-Order Butterworth Low-Pass Filter Transfer Function: To isolate human locomotor dynamics (0–3 Hz) from high-frequency vibration noise:")
    add_equation(doc, "|H(jω)| = 1 / sqrt(1 + (ω / ω_c)^(2n)),  where n = 4, ω_c = 2π(3 Hz)", "3.1")

    add_p(doc, "2. Tri-Axial Instantaneous Acceleration Magnitude: Derived from orthogonal accelerometer channels:")
    add_equation(doc, "a_mag(t) = sqrt(a_x(t)^2 + a_y(t)^2 + a_z(t)^2)", "3.2")

    add_p(doc, "3. Tri-Axial Jerk Standard Deviation: Quantifying the abruptness and shock rate of mechanical movement:")
    add_equation(doc, "jerk(t) = da_mag(t) / dt;   Jerk_Std = sqrt( (1/N) * sum_{t=1}^N (jerk(t) - μ_jerk)^2 )", "3.3")

    add_p(doc, "4. Fast Fourier Transform Power Spectral Density: Energy distribution across frequency bins:")
    add_equation(doc, "PSD(f_k) = (1/N) * | sum_{t=0}^{N-1} a_mag(t) * e^(-j 2π k t / N) |^2", "3.4")

    add_p(doc, "5. Weekly Training Workload: The product of exposure volume and perceived exertion intensity:")
    add_equation(doc, "Weekly_Load = Training_Hours_Per_Week * Training_Intensity", "3.5")

    add_p(doc, "6. Acute-to-Chronic Workload Ratio (ACWR) Proxy: Balancing short-term fatigue against historical fitness:")
    add_equation(doc, "Estimated_Chronic_Load = Weekly_Load * (1.2 - Fatigue_Score * 0.05);   ACWR = Weekly_Load / Estimated_Chronic_Load", "3.6")

    add_p(doc, "7. Training Monotony: Measuring daily load invariance:")
    add_equation(doc, "Monotony = Weekly_Load / ( std(Load_Balance_Score) * 0.1 + 1 )", "3.7")

    add_p(doc, "8. Training Strain: Compound stress induced by sustained high monotony and volume:")
    add_equation(doc, "Strain = Weekly_Load * Monotony", "3.8")

    add_p(doc, "9. Recovery Deficit Index: Ratio of perceived fatigue to allocated scheduled rest days:")
    add_equation(doc, "Recovery_Deficit = Fatigue_Score / (Recovery_Days_Per_Week + 1)", "3.9")

    add_p(doc, "10. Overall Physical Readiness Normalized Score: Standardized composite screening index:")
    add_equation(doc, "Overall_Physical_Readiness = (1/M) * sum_{m=1}^M ( (Score_m - μ_m) / σ_m )", "3.10")

    add_p(doc, "11. SMOTE Synthetic Feature Interpolation: Generating synthetic minority injury vectors:")
    add_equation(doc, "x_synthetic = x_i + λ * (x_k - x_i),  where λ ~ U(0, 1), x_k in k-NN(x_i)", "3.11")

    add_p(doc, "12. Platt Sigmoid Probability Calibration: Converting raw tree margin outputs into true posterior probabilities:")
    add_equation(doc, "P(Injury = 1 | f(x)) = 1 / ( 1 + exp(A * f(x) + B) )", "3.12")

    add_h1(doc, "3.4 ALGORITHMIC PIPELINE SPECIFICATION")
    add_p(doc, "Algorithm 3.1 details the complete computational sequence executed by the edge platform during a live match or training session:")

    algo_lines = [
        "Algorithm 3.1: Multi-Sensor Ingestion, Feature Fusion, and Calibrated Inference Pipeline",
        "Input : Raw IMU stream {ax, ay, az, gx, gy, gz}, Telemetry {HR, Steps, SpO2}, Athlete Metadata",
        "Output: Calibrated Acute Risk P_acute, Season Risk P_season, Downtime D_est, SHAP Ledger",
        "1.  // Step 1: Biomechanical Signal Filtering",
        "2.  a_mag <- sqrt(ax^2 + ay^2 + az^2)",
        "3.  a_filt <- butterworth_lowpass(a_mag, cutoff=3Hz, order=4)",
        "4.  peaks, cadence <- detect_step_peaks(a_filt, sampling_rate=50Hz)",
        "5.  jerk_std <- std(diff(a_mag) / dt)",
        "6.  freq_dom, spectral_energy <- compute_fft_psd(a_mag)",
        "7.  // Step 2: Temporal Workload & Recovery Dynamics",
        "8.  weekly_load <- hours_per_week * session_rpe",
        "9.  acwr <- weekly_load / (weekly_load * (1.2 - fatigue_score * 0.05))",
        "10. monotony <- weekly_load / (std_load_balance * 0.1 + 1)",
        "11. strain <- weekly_load * monotony",
        "12. recovery_deficit <- fatigue_score / (recovery_days + 1)",
        "13. // Step 3: Feature Assembly & Normalization",
        "14. X_fused <- concatenate([biomechanical_features, workload_features, telemetry_features])",
        "15. X_scaled <- standard_scaler_transform(X_fused)",
        "16. // Step 4: Multi-Model Inference & Probability Calibration",
        "17. f_raw <- xgboost_boosted_margin(X_scaled)",
        "18. P_acute <- platt_sigmoid_calibration(f_raw, A_param, B_param)",
        "19. P_season <- random_forest_predict_proba(X_screening)",
        "20. D_est <- expm1(rf_regressor_predict(X_career_history))",
        "21. // Step 5: Clinical Thresholding & Explainability",
        "22. if P_acute >= 0.8044 then status <- 'CRITICAL HIGH RISK (FLAGGED FOR REST)'",
        "23. else if P_acute >= 0.4500 then status <- 'MODERATE CAUTION (TAPER WORKLOAD)'",
        "24. else status <- 'OPTIMAL LOW RISK (CLEARED FOR PLAY)'",
        "25. shap_ledger <- compute_treeshap_contributions(X_scaled, xgboost_model)",
        "26. return P_acute, P_season, D_est, status, shap_ledger"
    ]
    add_callout_algorithm(doc, "ALGORITHM 3.1: MULTI-SENSOR INGESTION, FUSION, AND INFERENCE", algo_lines)

    add_h1(doc, "3.5 SYSTEM DESIGN CONSIDERATIONS & TRADE-OFFS")
    add_p(doc, "The system architecture embodies five strategic design principles:")
    add_bullet(doc, "Edge-First On-Premises Architecture: Running feature computation and inference locally prevents high-bandwidth raw biometric data from leaving club boundaries, ensuring zero network-dependent latency and compliance with data governance standards.", "Principle 1 —")
    add_bullet(doc, "Asymmetric Cost-Sensitive Optimization: In athletic health monitoring, the clinical cost of a false negative (failing to flag an athlete who suffers an ACL rupture) is catastrophic, whereas the cost of a false positive is minor (an extra recovery session). Consequently, all optimization prioritizes sensitivity and recall.", "Principle 2 —")
    add_bullet(doc, "Multi-Horizon Decoupling: Acute near-term micro-cycle risk is driven by recent workload spikes and biomechanical shock spikes, whereas season-long macro-cycle risk is dictated by neuromuscular screening baselines. Decoupling these into Model A and Model B prevents feature masking.", "Principle 3 —")
    add_bullet(doc, "Explainability as a Core Dependency: Clinical staff will not accept uninterpretable model outputs. SHAP force and waterfall ledgers are integrated into the core prediction payload, allowing clinicians to inspect exact feature contributions.", "Principle 4 —")
    add_bullet(doc, "Human-in-the-Loop Governance: AthleteShield acts as an objective decision-support aid. The system provides risk stratifications and workload ceilings, but final benching or training modifications remain strictly under the authority of medical and coaching staff.", "Principle 5 —")

    print("Chapter 3 written.")
    return doc

print("Chapters 3, 4, 5 module loaded.")
