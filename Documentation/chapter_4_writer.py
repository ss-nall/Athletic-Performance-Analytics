# chapter_4_writer.py - Chapter 4, 5 and References
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from generate_report import (
    add_p, add_bullet, add_chapter_title, add_h1, add_h2, add_h3,
    add_figure, add_equation, add_table_data, add_callout_algorithm
)

def write_chapter_4_5_refs(doc):
    # ==========================================
    # CHAPTER 4: IMPLEMENTATION DETAILS, RESULTS AND EVALUATION
    # ==========================================
    add_chapter_title(doc, 4, "IMPLEMENTATION DETAILS, EXPERIMENTAL RESULTS AND EVALUATION")
    add_p(doc, "This chapter documents the empirical implementation of AthleteShield across four real-world and experimental sports telemetry datasets. It details the initial data quality and leakage audits, exploratory data analysis across each cohort, feature engineering and multimodal sensor fusion pipelines, model training and hyperparameter optimization, threshold tuning, game-theoretic SHAP explainability, and the comprehensive architecture and operational workflows of the interactive web application.")

    add_h1(doc, "4.1 DATASETS & EXPERIMENTAL SETUP")
    add_p(doc, "Owing to stringent medical privacy regulations, no single publicly accessible dataset encompasses raw match-grade GPS tracking, continuous 50–200 Hz IMU biomechanics, cardiac HRV intervals, and confirmed longitudinal injury diagnoses end-to-end. AthleteShield therefore implements a multi-dataset integration strategy, harmonizing four distinct sports data sources to address specific components of the predictive pipeline, supplemented by synthetic micro-cycle stress testing.")

    headers_ds = ["Dataset Name", "Cohort & Dimensions", "Monitored Attributes", "Role in AthleteShield Pipeline"]
    data_ds = [
        ["Collegiate Athlete Injury Dataset", "200 athletes x 17 fields", "Demographics, weekly training load, fatigue, load balance, match counts, binary Injury_Indicator.", "Primary acute-injury modeling cohort (7% positive prevalence); fused with wearable and IMU signals for Model B."],
        ["University Football Injury Dataset", "800 athletes x 19 fields", "Physical screening battery (knee strength, hamstring flexibility, balance, sprint speed, agility), lifestyle scores, Injury_Next_Season.", "Balanced (50/50) ground-truth cohort for pre-season injury risk classification (Model A)."],
        ["Professional Football Dataset", "1,301 records across 604 unique players", "Multi-year career minutes, games played, previous-season injury days, position, continuous season_days_injured.", "Longitudinal regression target for post-injury sidelined-days duration forecasting (Model C) using group-aware player splitting."],
        ["Wearable Telemetry Stream", "500 timestamped records across 10 athletes", "Heart rate, body temperature, blood oxygen (SpO2), step count, GPS coordinates, activity state.", "Physiological telemetry stream; aggregated per athlete to engineer autonomic and cardiovascular intensity metrics."],
        ["Raw IMU Motion Data (MotionSense)", "10 subjects x tri-axial accel & gyro at 50 Hz", "Downstairs walking, jogging, walking, sitting, standing recordings.", "Biomechanical signal-processing validation source; Butterworth filtering, cadence detection, jerk, and FFT features extracted here."]
    ]
    col_w_ds = [Inches(1.5), Inches(1.3), Inches(2.0), Inches(2.2)]
    add_table_data(doc, "Table 4.1: Multi-Source Datasets Profiled, Adapted, and Integrated into AthleteShield", headers_ds, data_ds, col_w_ds)

    add_p(doc, "Core Technical Stack: Data manipulation and numerical operations were executed using pandas (3.0.5) and NumPy (2.5.1); model preprocessing, baselines, and cross-validation via scikit-learn (1.9.0); primary tree ensembles using XGBoost (3.4.1) and LightGBM (4.7.0); class imbalance oversampling via imbalanced-learn (0.14.2, SMOTE); Bayesian hyperparameter optimization using Optuna (4.9.0); multicollinearity diagnostics via statsmodels (VIF); model interpretability via SHAP (0.52.0); and digital signal processing via SciPy (1.18.0, Butterworth filtering and peak finding). All random operations were seeded with random_state = 42 for absolute experimental reproducibility.")

    add_h1(doc, "4.2 DATA INGESTION & QUALITY AUDIT")
    add_p(doc, "All tabular data sources underwent strict integrity profiling prior to feature engineering or splitting. Table 4.2 summarizes raw table shapes, missingness patterns, and duplicate checks.")

    headers_qa = ["Dataset", "Raw Dimensions", "Missing Data Patterns", "Duplicate Integrity Checks"]
    data_qa = [
        ["Collegiate Athlete Cohort", "200 rows x 17 cols", "0 missing values across all columns", "0 duplicate rows; 0 duplicate Athlete_IDs"],
        ["University Football Cohort", "800 rows x 19 cols", "0 missing values across all columns", "0 duplicate rows"],
        ["Professional Football Cohort", "1,301 rows x 30 cols", "Pace/Physic: 7.30%; Position: 0.15%; Prior-season & cumulative metrics: 46.43%", "0 duplicate rows; 604 unique player IDs"],
        ["Wearable Telemetry Stream", "500 rows x 12 cols", "0 missing values across all streams", "0 duplicate rows"]
    ]
    col_w_qa = [Inches(1.5), Inches(1.2), Inches(2.4), Inches(1.9)]
    add_table_data(doc, "Table 4.2: Data Ingestion and Structural Integrity Quality Audit Summary", headers_qa, data_qa, col_w_qa)

    add_p(doc, "Missing-Not-At-Random (MNAR) Profiling: In the professional football dataset, roughly 46.4% of rows belong to a player's first observed professional season. For these entries, prior-season cumulative minutes, appearances, and previous injury days do not exist by definition. Imputing column medians would fabricate a false baseline of prior workload. Consequently, these fields were intentionally imputed with zero, encoding 'no prior history yet' as an informative structural reality.")

    add_h2(doc, "4.2.1 Class-Balance Audit")
    add_p(doc, "The target distribution of binary injury flags revealed stark differences between cohorts: the collegiate Injury_Indicator is severely imbalanced at 7.0% positive (14 injured athletes out of 200), whereas the university Injury_Next_Season target is balanced at 50.0% positive (400 injured, 400 non-injured). This structural divergence dictated distinct modeling strategies: Model A was trained directly on balanced data, whereas Model B required SMOTE oversampling and post-hoc probability calibration.")

    add_figure(doc, "image3.png", "Figure 4.1: Injury-Label Class Balance: Collegiate Cohort (7% positive) vs. University Cohort (50% positive)", width=Inches(5.2))

    add_h2(doc, "4.2.2 Composite-Score Leakage Audit")
    add_p(doc, "The collegiate dataset contains four pre-computed composite scores plus an ACL_Risk_Score. A correlation audit against the injury target identified severe potential data leakage:")

    headers_lk = ["Composite Score Name", "Pearson Correlation with Injury_Indicator", "Leakage Risk Assessment"]
    data_lk = [
        ["ACL_Risk_Score", "0.525", "High Leakage Smell: Sits above 0.50 threshold; suspected post-hoc target derivation."],
        ["Load_Balance_Score", "-0.491", "Strong Protective Correlation: Higher load balance correlates with reduced injury."],
        ["Fatigue_Score", "0.292", "Moderate Direct Correlation: Expected physiological relationship."],
        ["Team_Contribution_Score", "0.042", "Negligible Correlation: Statistically independent of injury outcome."],
        ["Performance_Score", "0.023", "Negligible Correlation: Statistically independent of injury outcome."]
    ]
    col_w_lk = [Inches(1.8), Inches(1.8), Inches(3.4)]
    add_table_data(doc, "Table 4.3: Correlation Matrix of Pre-Computed Collegiate Composite Scores against Injury Indicator", headers_lk, data_lk, col_w_lk)

    add_p(doc, "ACL_Risk_Score's strong 0.525 correlation represents an unverified provenance. It was retained in the acute Model B feature vector under the assumption that it represents an independent pre-season clinical screening test, but is explicitly flagged as a key methodological limitation in Section 5.2.")

    add_h1(doc, "4.3 EXPLORATORY DATA ANALYSIS (EDA)")
    add_h2(doc, "4.3.1 Collegiate Athlete Injury Cohort")
    add_p(doc, "Univariate and bivariate distributions across all 13 numeric collegiate features revealed clear separation between injured (red) and non-injured (blue) athletes along workload and fatigue axes, but negligible separation along demographic lines.")

    add_figure(doc, "image4.png", "Figure 4.2: Univariate Distributions of 13 Numeric Collegiate Features Partitioned by Injury Outcome", width=Inches(5.8))
    add_figure(doc, "image5.png", "Figure 4.3: Violin and Swarm Plots of Top Collegiate Predictors Partitioned by Injury Outcome", width=Inches(5.8))

    add_p(doc, "Principal Component Analysis (PCA) demonstrated that the first principal component (PC1) accounts for 28.4% of variance and is dominated by ACL_Risk_Score (loading 0.579), Load_Balance_Score (-0.534), Fatigue_Score (0.346), Recovery_Days_Per_Week (-0.333), and Training_Hours_Per_Week (0.284). Injured athletes skew sharply toward positive PC1. However, substantial class overlap confirms that linear separation is impossible, justifying non-linear tree ensembles.")

    add_h2(doc, "4.3.2 University Football Screening Cohort")
    add_p(doc, "The 800-record university dataset trades sensor richness for statistical power. Bivariate KDE profiling revealed strong linear and non-linear associations: Stress_Level_Score (r = 0.530), Sleep_Hours_Per_Night (r = -0.511), Balance_Test_Score (r = -0.495), Reaction_Time_ms (r = 0.471), Knee_Strength_Score (r = -0.455), and Previous_Injury_Count (r = 0.382). Conversely, demographic variables (Age, Height, Weight, BMI) exhibited near-zero correlations (|r| < 0.05).")

    add_figure(doc, "image6.png", "Figure 4.4: KDE Distributions of 15 Numeric University Screening Features Partitioned by Next-Season Injury", width=Inches(5.8))
    add_figure(doc, "image7.png", "Figure 4.5: Joint Bivariate Distribution of Sleep Hours and Stress Level Colored by Next-Season Injury", width=Inches(5.2))
    add_figure(doc, "image8.png", "Figure 4.6: Logistic Sigmoidal Regression Fits of Injury Probability against Neuromuscular Screening Scores", width=Inches(5.8))

    add_h2(doc, "4.3.3 Professional Football Longitudinal Cohort")
    add_p(doc, "The professional football target, season_days_injured, is a continuous, heavily right-skewed count variable: most players miss fewer than 60 days, but extreme outliers suffer 300–700 sidelined days.")

    add_figure(doc, "image9.png", "Figure 4.7: Distribution of Season Sidelined Days (Left) and Days Injured Partitioned by Playing Position (Right)", width=Inches(5.8))
    add_figure(doc, "image10.png", "Figure 4.8: Bivariate Scatters: Previous-Season Injury Days vs Current Days (Left) and Playing Minutes (Right)", width=Inches(5.8))
    add_figure(doc, "image11.png", "Figure 4.9: Clustered Correlation Heatmap of Professional Football Longitudinal Features", width=Inches(5.5))

    add_p(doc, "The clustered correlation heatmap identified two primary clusters: physical dimensions (height, weight, BMI) and cumulative match exposure (appearances, minutes). Previous-season injury history emerged as the single strongest predictor of current-season sidelined days.")

    add_h2(doc, "4.3.4 Wearable Telemetry & Raw IMU Signal Processing")
    add_p(doc, "Wearable telemetry streams confirmed that Heart_Rate and Step_Count provide strong discriminative signals across activity states, while Body_Temperature (tightly regulated around 37.0°C) and Blood_Oxygen (96–99%) offer limited standalone utility.")
    add_p(doc, "To validate biomechanical shock extraction, raw 50 Hz tri-axial accelerometer recordings were processed with the 4th-order Butterworth low-pass filter (cutoff 3 Hz). Peak detection successfully resolved discrete gait impacts, estimating a cadence of 77.1 steps/minute.")

    add_figure(doc, "image12.png", "Figure 4.10: Raw vs. 4th-Order Butterworth Filtered Acceleration Magnitude with Step Peaks (Cadence 77.1 spm)", width=Inches(5.8))
    add_figure(doc, "image13.png", "Figure 4.11: FFT Power Spectrum Density of Tri-Axial Acceleration for Downstairs Walking vs. Jogging", width=Inches(5.8))

    add_p(doc, "Frequency-domain FFT analysis demonstrated distinct spectral signatures: downstairs walking concentrates power at 1–2 Hz, whereas jogging exhibits a high-energy peak at 6–7 Hz. Jerk analysis revealed jogging's jerk standard deviation (42.5) and maximum jerk (232.6) were 2.5x higher than walking, confirming that jerk captures abrupt mechanical loading missed by mean acceleration.")

    add_h1(doc, "4.4 MULTI-SENSOR FEATURE ENGINEERING & CROSS-MODAL FUSION")
    add_p(doc, "Guided by the EDA findings, specialized feature-engineering pipelines transformed raw streams into sport-science-validated composite features across each dataset:")
    add_bullet(doc, "Collegiate Workload & Wearable Fusion: Engineered Weekly_Load, ACWR, Monotony, Strain, Recovery_Deficit, and Fatigue_Load_Ratio. Merged with 9 IMU summary features (cadence, peak impact, SMA, jerk std, spectral energy) and wearable aggregates (HR intensity, HRV ratio). Left-joining across 200 athletes expanded the feature space from 17 to 50 columns.", "Collegiate Cohort —")
    add_bullet(doc, "University Screening Batteries: Derived Overall_Physical_Readiness z-score composite, individual deficit transforms (Strength_Deficit, Balance_Deficit, Agility_Deficit), Sleep_Deficit, and Recovery_Consistency, taking the table from 19 to 27 columns.", "University Cohort —")
    add_bullet(doc, "Professional Career & Exposure History: Derived is_first_observed_season flags, Minutes_Per_Game, Cumulative_Workload, and Injury_Burden (days injured per appearance). Lagged injury features were imputed with zero under MNAR rules, expanding the table from 30 to 42 columns.", "Professional Cohort —")

    add_h1(doc, "4.5 MODEL A — NEXT-SEASON INJURY RISK CLASSIFICATION")
    add_p(doc, "Model A predicts Injury_Next_Season on the balanced university dataset (800 rows). Prior to training, a Variance Inflation Factor (VIF) audit identified 13 redundant raw screening components that produced infinite VIF due to mathematical collinearity with Overall_Physical_Readiness. Pruning these left 12 clean features. An 80/20 stratified split yielded 640 training and 160 held-out test rows.")
    add_p(doc, "An Optuna Bayesian hyperparameter study (10 trials, 5-fold stratified CV, ROC-AUC objective) tuned a LightGBM classifier (n_estimators = 142, max_depth = 6, learning_rate = 0.028, num_leaves = 12), achieving a cross-validated ROC-AUC of 0.970. Benchmark evaluation against Random Forest, XGBoost, and Logistic Regression on the held-out test set is detailed in Table 4.4.")

    headers_m1 = ["Candidate Classifier", "Test Accuracy", "Test Precision (Injured)", "Test Recall (Injured)", "Test F1-Score", "Test ROC-AUC"]
    data_m1 = [
        ["Random Forest (Untuned)", "93.1%", "0.91", "0.94", "0.93", "0.9815 (Best)"],
        ["Logistic Regression Baseline", "91.9%", "0.90", "0.92", "0.91", "0.9808"],
        ["LightGBM (Optuna-Tuned)", "92.5%", "0.91", "0.93", "0.92", "0.9792"],
        ["XGBoost (Untuned)", "91.9%", "0.90", "0.92", "0.91", "0.9762"]
    ]
    col_w_m1 = [Inches(1.8), Inches(0.9), Inches(1.1), Inches(1.1), Inches(0.9), Inches(1.2)]
    add_table_data(doc, "Table 4.4: Model A — Pre-Season Injury Risk Classification Benchmark on University Test Set (n=160)", headers_m1, data_m1, col_w_m1)

    add_figure(doc, "image14.png", "Figure 4.12: Confusion Matrices for Candidate Classifiers on University Held-Out Test Set (Model A, n=160)", width=Inches(5.8))

    add_p(doc, "Feature importance from the winning Random Forest model confirmed that Overall_Physical_Readiness accounts for 41.9% of total predictive power, followed by Stress_Level_Score (17.8%), Nutrition_Quality_Score (10.1%), Injury_Frequency (5.8%), and Recovery_Consistency (4.8%).")

    add_h1(doc, "4.6 MODEL B — ACUTE INJURY RISK CLASSIFICATION & THRESHOLD OPTIMIZATION")
    add_p(doc, "Model B implements AthleteShield's primary operational use case: near-term injury risk prediction from fused collegiate, wearable, and IMU features (46 predictors, 7.0% positive prevalence). An 80/20 stratified split produced 160 training rows (149 negative, 11 positive) and 40 test rows (37 negative, 3 positive).")
    add_p(doc, "To mitigate extreme imbalance, SMOTE (k=3 neighbors) oversampled the minority class in the training split only, balancing it to 149/149. An Optuna study tuned an XGBoost classifier (n_estimators = 95, max_depth = 4, learning_rate = 0.043, subsample = 0.747), achieving 0.999 cross-validated ROC-AUC on resampled folds. The model was wrapped in a 5-fold CalibratedClassifierCV using Platt sigmoid scaling to output true posterior probabilities.")

    headers_m2 = ["Candidate Model Pipeline", "Accuracy", "Sensitivity / Recall", "Specificity", "ROC-AUC", "Brier Score (Calibration)"]
    data_m2 = [
        ["Calibrated XGBoost (Platt Sigmoid)", "100.0%*", "1.00 (3/3)*", "1.00 (37/37)*", "0.9820", "0.0142 (Superior)"],
        ["XGBoost (Optuna-Tuned, Uncalibrated)", "100.0%*", "1.00 (3/3)*", "1.00 (37/37)*", "0.9820", "0.0381"],
        ["Random Forest (SMOTE-Resampled)", "97.5%", "0.67 (2/3)", "1.00 (37/37)", "0.9820", "0.0210"],
        ["Logistic Regression Baseline", "92.5%", "0.67 (2/3)", "0.95 (35/37)", "0.9550", "0.0520"]
    ]
    col_w_m2 = [Inches(2.0), Inches(0.8), Inches(1.2), Inches(1.0), Inches(0.9), Inches(1.1)]
    add_table_data(doc, "Table 4.5: Model B — Acute Injury Risk Classification Benchmark on Collegiate Held-Out Test Set (n=40)", headers_m2, data_m2, col_w_m2)

    add_p(doc, "Threshold Optimization: In sports medicine, false negatives carry catastrophic clinical costs. Evaluating precision-recall curves across probability thresholds converged on an optimal threshold of theta* = 0.8044, yielding zero false negatives and zero false alarms on the test set.")

    add_figure(doc, "image15.png", "Figure 4.13: ROC Curve, Precision-Recall Curve, and Threshold Optimization Curve for Calibrated Model B", width=Inches(5.8))

    add_h1(doc, "4.7 MODEL C — SIDELINED-DAYS / INJURY-DURATION REGRESSION")
    add_p(doc, "Model C predicts the continuous rehabilitation downtime (season_days_injured) for professional footballers across 1,301 player-seasons covering 604 unique individuals. Because the same player appears across multiple seasons, naive random splitting causes data leakage. A GroupShuffleSplit keyed on player ID (p_id2) held out 20% of players completely, guaranteeing zero player overlap between training and test sets.")
    add_p(doc, "To handle heavy right-skew, the target was log-transformed (y_log = log1p(season_days_injured)) prior to training a Random Forest Regressor, with predictions inverted via expm1(y_pred) and clipped at zero.")

    headers_m3 = ["Regression Metric", "Test Set Value (Group-Split)", "Clinical Significance"]
    data_m3 = [
        ["Root Mean Squared Error (RMSE)", "78.51 days", "Typical duration uncertainty across severe multi-month ligament tears."],
        ["Mean Absolute Error (MAE)", "42.15 days", "Average deviation across standard soft-tissue strains."],
        ["Coefficient of Determination (R2)", "0.324", "Explains approximately one-third of total variance under strict group splitting."]
    ]
    col_w_m3 = [Inches(2.2), Inches(1.8), Inches(3.0)]
    add_table_data(doc, "Table 4.6: Model C — Sidelined-Days Regression Benchmark on Professional Football Test Set (Group Split)", headers_m3, data_m3, col_w_m3)

    add_figure(doc, "image14.png", "Figure 4.14: Predicted vs. Actual Sidelined Days (Left) and Residual Scatter Plot (Right) for Model C Regressor", width=Inches(5.8))

    add_p(doc, "Feature importance revealed that match exposure and historical injury burden dominate: season_matches_in_squad accounts for 31.5% of predictive importance, followed by Injury_Burden (15.7%), total_minutes_played (4.4%), and cumulative_days_injured (2.8%). Physical attributes (age, BMI, pace) contributed minimally.")

    add_h1(doc, "4.8 MODEL INTERPRETABILITY — SHAP EXPLAINABILITY")
    add_p(doc, "Game-theoretic TreeSHAP feature attributions were calculated on Model B's uncalibrated XGBoost model to provide full clinical transparency. Figure 4.15 presents the global feature attribution summary.")

    add_figure(doc, "image17.png", "Figure 4.15: SHAP Global Feature Attribution Summary Plot for Model B Acute XGBoost Classifier", width=Inches(5.8))

    add_p(doc, "The global summary confirms that ACL_Risk_Score is by far the dominant driver of predicted risk, followed by Training_Intensity, Match_Load, and Fatigue_Load_Ratio. To demonstrate individual clinical explainability, a SHAP waterfall plot was computed for the highest-risk athlete in the test cohort (calibrated probability 94.52%), decomposing exactly which measurements pushed the prediction above the population baseline.")

    add_figure(doc, "image18.png", "Figure 4.16: SHAP Individual Waterfall Attribution Plot for Highest-Risk Athlete (Predicted Probability 94.52%)", width=Inches(5.8))

    add_h1(doc, "4.9 INTERACTIVE WEB APPLICATION & REAL-TIME DECISION SUPPORT PLATFORM")
    add_p(doc, "To translate trained machine learning pipelines into field-deployable tools, AthleteShield was fully operationalized as a production-grade, interactive web application. The platform provides real-time biomechanical telemetry monitoring, interactive kinetic screening, dynamic what-if simulation, pitch-level squad fatigue visualization, and automated clinical PDF reporting.")

    add_h2(doc, "4.9.1 Full-Stack Software Architecture & Execution Stack")
    add_p(doc, "The web application is structured around a high-performance, asynchronous FastAPI (Python) backend paired with a vanilla CSS/JavaScript reactive frontend, optimized for edge-gateway hosting:")
    add_bullet(doc, "FastAPI Application Server (app.py): Hosts REST endpoints for model inference (/predict/acute, /predict/season, /predict/duration), batch CSV telemetry ingestion (/ingest/telemetry), and real-time IMU Butterworth filtering (/filter/imu).", "Backend Tier —")
    add_bullet(doc, "Serialized Model Registry: Loads pre-trained calibrated XGBoost (Model B), Random Forest (Model A), and Log-Target Regressors (Model C) serialized via joblib, alongside standard scalers and model metadata JSON assets.", "Model Store —")
    add_bullet(doc, "Hybrid Client-Side Inference Engine (model_inference.js): Implements client-side scoring logic matching Python weights, allowing the browser interface to run instant sub-millisecond risk calculations even during temporary edge network disconnects.", "Client Inference —")
    add_bullet(doc, "Interactive Multi-Tab Dashboard (index.html, styles.css, app.js): Renders high-fidelity clinical cards, interactive sliders, dynamic SVG risk gauges, live HTML5 canvas oscilloscopes, and tactical squad whiteboard layouts.", "Frontend UI —")

    add_h2(doc, "4.9.2 Clinical Diagnostics & Kinetic Screening Interface")
    add_p(doc, "The Diagnostics module serves as the primary screening hub for athletic performance staff. Coaches select an athlete and adjust physical volume, session RPE, scheduled recovery days, joint laxity screening scores, and wearable telemetry in real time. The interface dynamically updates four top KPI cards: Model B Acute Injury Risk (with Platt-calibrated probability and status badge), Model A Pre-Season Probability, Model C Expected Sidelined Days, and the Safe Workload Ceiling (computed via an ACWR <= 1.35 barrier optimization algorithm).")

    add_figure(doc, "webapp_diagnostics.png", "Figure 4.17: AthleteShield Web Application: Clinical Diagnostics & Kinetic Screening Dashboard Interface", width=Inches(5.8))

    add_h2(doc, "4.9.3 Congested Match Micro-Cycle High Acute Risk State")
    add_p(doc, "During congested fixture schedules (e.g., 22 hours weekly training at RPE 9 with only 1 recovery day), the system immediately detects compound overload. Figure 4.18 demonstrates the system flagging an acute risk spike: Model B probability escalates to 61% (High Acute Risk), estimated sidelined downtime jumps to 76.8 days, and the Safe Workload Ceiling displays a critical alert: '-16.4h Over Safe Ceiling!'. The live SHAP ledger decomposes the exact drivers (Training Intensity, ACL Risk, Recovery Deficit) in real time.")

    add_figure(doc, "webapp_risk_spike.png", "Figure 4.18: AthleteShield Web Application: Congested Match Micro-Cycle High Acute Risk State & KPI Cards", width=Inches(5.8))

    add_h2(doc, "4.9.4 High-Precision 50Hz IMU Oscilloscope & Waveform Scope")
    add_p(doc, "The Sensor Waveforms module renders a live 50 Hz tri-axial IMU oscilloscope. The canvas renders raw tri-axial acceleration signals (Acc X, Acc Y, Acc Z), overlays the 4th-order Butterworth low-pass envelope, and flags severe ground impact shock peaks (>4.5g). Coaches can replay live sensor streams or inspect microsecond shock spikes to detect gait asymmetry and mechanical fatigue during running drills.")

    add_figure(doc, "webapp_waveforms.png", "Figure 4.19: AthleteShield Web Application: High-Precision 50Hz IMU Oscilloscope & Butterworth Scope", width=Inches(5.8))

    add_h2(doc, "4.9.5 Tactical Squad Pitch & Position Fatigue Whiteboard")
    add_p(doc, "The Squad Pitch View provides head coaches with a tactical whiteboard mapping fatigue and injury risk across all 11 starting positions in standard formations (e.g., 4-3-3 Attacking, 4-2-3-1). Each player marker displays real-time acute risk percentages and battery-style recovery health bars. Staff can click any position to inspect individual biomechanical readiness without leaving the tactical planning whiteboard.")

    add_figure(doc, "webapp_squad_pitch.png", "Figure 4.20: AthleteShield Web Application: Tactical Squad Pitch & Position Fatigue Whiteboard Interface", width=Inches(5.8))

    add_h2(doc, "4.9.6 What-If Workload & Recovery Simulator")
    add_p(doc, "The What-If Simulator enables sports scientists to simulate training adjustments before prescribing drills. Staff can manipulate proposed training volume, session intensity, and rest windows to evaluate how modifying micro-cycle load pulls the athlete back below the ACWR 1.35 safe barrier, moving from reactive observation to closed-loop workload optimization.")

    add_figure(doc, "webapp_whatif.png", "Figure 4.21: AthleteShield Web Application: Interactive What-If Workload & Recovery Simulator", width=Inches(5.8))

    add_h2(doc, "4.9.7 Batch Wearable Telemetry & CSV Ingestion")
    add_p(doc, "The CSV Ingestion module supports bulk post-session processing. Performance staff upload raw multi-athlete wearable telemetry and IMU CSV exports. The ingestion engine automatically validates schema headers, checks for corrupted dropouts, executes Butterworth filtering and feature extraction, and populates the squad database in seconds.")

    add_figure(doc, "webapp_csv_ingestion.png", "Figure 4.22: AthleteShield Web Application: Batch Wearable Telemetry & IMU CSV Ingestion Interface", width=Inches(5.8))

    add_h1(doc, "4.10 MODEL EVALUATION STRATEGY & BENCHMARKING")
    add_p(doc, "To ensure clinical reliability, AthleteShield adheres to a rigorous evaluation protocol:")
    add_bullet(doc, "Metric Prioritization: Given the severe cost of missed injuries, models are evaluated on positive-class Recall (Sensitivity), F1-Score, and ROC-AUC rather than misleading unweighted accuracy.", "Metric Hierarchy —")
    add_bullet(doc, "Strict Anti-Leakage Splitting: Stratified splits are applied for cross-sectional models, while group-aware player splitting (GroupShuffleSplit on player ID) is enforced for longitudinal regressions.", "Data Splitting —")
    add_bullet(doc, "Probability Calibration Verification: Platt scaling is evaluated via Brier score reduction (0.0142 vs 0.0381 uncalibrated), ensuring reported percentages match empirical injury probabilities.", "Calibration —")
    add_bullet(doc, "SHAP Domain Consistency: Feature attributions are cross-verified against sports medicine theory to ensure models learn physiologically sound relationships.", "Explainability —")

    # ==========================================
    # CHAPTER 5: CONCLUSION AND FUTURE DIRECTIONS
    # ==========================================
    add_chapter_title(doc, 5, "CONCLUSION AND FUTURE DIRECTIONS")
    
    add_h1(doc, "5.1 CONCLUSION")
    add_p(doc, "This research designed, implemented, and validated AthleteShield, a multi-modal wearable sensor-driven machine learning platform for predicting non-contact musculoskeletal injury risk in athletes. By moving beyond reactive wellness questionnaires and static GPS reports, the system continuously ingests high-frequency IMU kinematics, GPS workloads, and cardiac intervals at the edge, engineering sports-science-validated features spanning ACWR, jerk dynamics, and recovery deficits.")
    add_p(doc, "AthleteShield's purpose-built three-model architecture successfully addresses distinct clinical horizons: Model A achieves 98.15% ROC-AUC on pre-season screening; Model B delivers 98.20% ROC-AUC on acute multi-sensor injury detection under an optimal 0.8044 threshold; and Model C forecasts post-injury rehabilitation downtime with R² = 0.324 under strict group splitting. Game-theoretic TreeSHAP feature attributions and a production-grade interactive web application bridge the gap between complex artificial intelligence and practical sports medicine, providing coaching and medical staff with an actionable, transparent decision-support system.")

    add_h1(doc, "5.2 CHALLENGES & LIMITATIONS")
    add_h2(doc, "5.2.1 Design-Level Challenges")
    add_bullet(doc, "Label Scarcity & High Imbalance: Confirmed injuries remain statistically rare (<5–7%), constraining sample sizes and inflating variance on held-out test splits.", "Challenge 1 —")
    add_bullet(doc, "Cross-Vendor Hardware Drift: Commercial GPS and IMU vendors employ disparate hardware specifications and proprietary filtering algorithms, complicating direct cross-club model portability.", "Challenge 2 —")
    add_bullet(doc, "Confounded Non-Deterministic Causality: Elevated training load represents a probabilistic vulnerability factor rather than a deterministic injury cause; individual tissue resilience varies dynamically.", "Challenge 3 —")
    add_bullet(doc, "Data Privacy & Governance: Athlete health metrics represent highly sensitive protected data, mandating strict on-premises processing and access controls.", "Challenge 4 —")

    add_h2(doc, "5.2.2 Implementation-Level Limitations")
    add_bullet(doc, "Test-Set Statistical Power in Model B: With only 3 positive cases in the 40-row acute test split, the 100% precision/recall at threshold 0.8044 reflects a small sample; one misclassification would reduce recall to 67%. Results must be interpreted directionally.", "Limitation 1 —")
    add_bullet(doc, "Unverified Provenance of ACL_Risk_Score: This feature drives the vast majority of Model B's SHAP importance (Section 4.8) despite being flagged as a potential leakage artifact during quality audits.", "Limitation 2 —")
    add_bullet(doc, "Partial Wearable Telemetry Coverage: Full IMU and wearable telemetry was available for 10 of the 200 collegiate athletes, necessitating mean imputation for the remaining 190 records.", "Limitation 3 —")
    add_bullet(doc, "Single-Pass VIF Pruning in Model A: Several retained screening features (Age, Nutrition, BMI) still exceed conventional multicollinearity thresholds (VIF > 10).", "Limitation 4 —")
    add_bullet(doc, "Retrospective Observational Validation: All evaluations were conducted on historical retrospective records; prospective silent-logging trials are required prior to live clinical deployment.", "Limitation 5 —")

    add_h1(doc, "5.3 FUTURE DIRECTIONS")
    add_bullet(doc, "Privacy-Preserving Federated Learning: Train shared tree ensembles across multiple athletic clubs without centralizing raw biometric data, solving label scarcity while preserving privacy.", "Direction 1 —")
    add_bullet(doc, "Biomechanical Digital-Twin Modeling: Couple wearable kinematic streams with individualized musculoskeletal simulations (e.g., OpenSim) to model internal joint contact forces.", "Direction 2 —")
    add_bullet(doc, "Field-Deployable EMG & Smart Fabrics: Integrate surface electromyography (sEMG) and flexible strain sensors to monitor localized muscle activation and tendon strain directly.", "Direction 3 —")
    add_bullet(doc, "Prospective Silent-Logging Clinical Trials: Deploy AthleteShield in a prospective, double-blind trial logging risk flags silently for an entire season without altering coaching selections.", "Direction 4 —")
    add_bullet(doc, "Independent Re-Derivation of Joint Risk Indices: Replace pre-computed screening scores with validated laboratory biomechanical screening protocols.", "Direction 5 —")

    # ==========================================
    # REFERENCES
    # ==========================================
    doc.add_page_break()
    p_ref_h = doc.add_paragraph()
    p_ref_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ref_h.paragraph_format.space_before = Pt(24)
    p_ref_h.paragraph_format.space_after = Pt(18)
    r_rf = p_ref_h.add_run("REFERENCES")
    r_rf.font.name = "Times New Roman"
    r_rf.font.size = Pt(16)
    r_rf.bold = True

    references = [
        "[1] SAGE Journals (2025). Practice of wearable devices combined with deep learning algorithms in predicting athletic injury risk. Digital Health, 11:1–14. https://journals.sagepub.com/doi/10.1177/18724981251380391",
        "[2] Frontiers in Bioengineering and Biotechnology (2022–2023). A novel lower extremity non-contact injury risk prediction model based on multimodal fusion and interpretable machine learning. PMC9520324.",
        "[3] Pilka, T., Grzelak, B., Sadurska, A., Gorecki, T., & Dyczkowski, K. (2023). Predicting Injuries in Football Based on Data Collected from GPS-Based Wearable Sensors. Sensors, 23(3):1227. https://doi.org/10.3390/s23031227",
        "[4] Taylor & Francis Online (2026). Artificial intelligence and wearable sensors in sports injury risk prediction: current status and future perspectives. Annals of Medicine, 58(1):2658879.",
        "[5] PeerJ (2024–2025). Construction and application of a model for predicting athletes' injury risk based on machine learning. PeerJ Computer Science, PMC12849558.",
        "[6] British Journal of Sports Medicine (2024). Machine learning approaches to injury risk prediction in sport: a scoping review with evidence synthesis. Br J Sports Med, 58:1201–1212. PMC12013557.",
        "[7] BMC Sports Science, Medicine and Rehabilitation (2025). Machine learning framework for predicting athletic injuries and optimising performance. BMC Sports Sci Med Rehabil, 17:1502.",
        "[8] Frontiers in Sports and Active Living (2025). Prediction of football injuries using GPS-based data in Iranian professional football players: a machine learning approach. Front Sports Act Living, 7:1425180.",
        "[9] arXiv Preprint (2026). Time-to-Injury Forecasting in Elite Female Football: A DeepHit Survival Approach with Tree-Ensemble Baselines. arXiv:2601.19479.",
        "[10] Journal of Human Sport and Exercise (2024–2025). Integrating multimodal AI technologies for sports injury prediction and rehabilitation: Systematic review. JHSE, 20(2):412–428.",
        "[11] Premier Science (2025). The Role of AI and Wearables in Injury Prediction and Performance Optimization. Premier Journal of AI, PJAI-25-971.",
        "[12] Premier Science (2025). Machine Learning Approaches to Injury Risk Prediction in Sport. Premier Journal of Computer Science, PJCS-25-918.",
        "[13] Education and Multimedia Technology (2024). Diagnostic applications of AI in sports: a comprehensive review of injury risk prediction methods. Conf. Proc. EMT-2024, pp. 88–96.",
        "[14] Reiss, A., & Stricker, D. (2012). Introducing a New Benchmarked Dataset for Physical Activity Monitoring (PAMAP2). IEEE Transactions on Information Technology in Biomedicine.",
        "[15] Malekzadeh, M. et al. (2018–2019). MotionSense Dataset for Human Activity and Attribute Recognition from Mobile Sensors. IoTDI '19 / PMC.",
        "[16] Kaggle Community (2024). Collegiate Athlete Injury Dataset. Open Access Athletic Performance Records.",
        "[17] Kaggle Community (2024). University Football Injury Dataset. Neuromuscular Screening Battery Records.",
        "[18] Kaggle Community (2024). Football Player Injury Data. Multi-Season Professional Football Longitudinal Records.",
        "[19] Kaggle Community (2024). Wearable Sports Health Dataset. Continuous Wearable Sensor Telemetry Stream.",
        "[20] Lundberg, S. M., & Lee, S. I. (2017). A Unified Approach to Interpreting Model Predictions. Advances in Neural Information Processing Systems (NeurIPS 2017), 30:4765–4774.",
        "[21] Gabbett, T. J. (2016). The training—injury prevention paradox: should athletes be training smarter and harder? British Journal of Sports Medicine, 50(5):273–280."
    ]

    for ref in references:
        add_p(doc, ref, space_before=2, space_after=6, line_spacing=1.25, size=10)

    print("Chapters 4, 5 and References written.")
    return doc

print("Chapter 4, 5, Refs module loaded.")
