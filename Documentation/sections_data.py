# sections_data.py - Structured Content for AthleteShield Thesis Report

TITLE = "A WEARABLE SENSOR DRIVEN MACHINE LEARNING SYSTEM FOR PREDICTING NON-CONTACT MUSCULOSKELETAL INJURY RISK IN ATHLETES"
SHORT_TITLE = "ATHLETESHIELD: PREDICTIVE ATHLETIC INJURY & PERFORMANCE ANALYTICS"
SECTOR = "Sports Science & Athletic Performance Analytics"
AUTHORS = [
    ("SRI SAATWIK NALLURI", "23MID0438"),
    ("PAKALA PUNEETH", "23MID0291")
]
DEGREE = "INTEGRATED MASTER OF TECHNOLOGY IN DATA SCIENCE"
DEPARTMENT = "DEPARTMENT OF DATA SCIENCE\nSCHOOL OF COMPUTER SCIENCE AND ENGINEERING"
INSTITUTION = "VELLORE INSTITUTE OF TECHNOLOGY, VELLORE"
SUBMISSION_DATE = "OCTOBER 2026"
GUIDE = "Prof. Raghul J"
GUIDE_DESIGNATION = "Assistant Professor (Senior Grade)\nSchool of Computer Science and Engineering\nVellore Institute of Technology, Vellore"
HOD_DESIGNATION = "Head of the Department\nDepartment of Data Science\nSchool of Computer Science and Engineering\nVellore Institute of Technology, Vellore"

ABSTRACT_EN = [
    "Non-contact musculoskeletal injuries such as anterior cruciate ligament (ACL) tears, hamstring strains, and adductor ruptures represent the single largest controllable cause of lost athlete availability in elite and collegiate sports. Despite the catastrophic financial, competitive, and physical toll of these occurrences, conventional sports medicine workflows remain overwhelmingly reactive. Modern team performance staff rely predominantly on subjective self-report wellness questionnaires, static post-session GPS summary reports, and intuitive clinical judgement, an approach that lacks scalability across large squads, suffers from high inter-practitioner subjectivity, and inherently flags fatigue only after neuromuscular damage and tissue overload have already manifested.",
    "This work presents AthleteShield, an end-to-end, edge-deployable, wearable sensor-driven predictive analytics system designed to continuously estimate multi-horizon injury risk from raw inertial measurement unit (IMU), GPS/GNSS kinematics, and heart-rate-variability (HRV) autonomic physiological telemetry streams. Multi-modal sensor streams are ingested via edge gateways, denoised using 4th-order low-pass Butterworth filtering, time-aligned, and aggregated into a rolling per-athlete feature store spanning sport-science-validated kinetic and physiological indices, including the acute:chronic workload ratio (ACWR), training monotony, session strain, PlayerLoad, jerk dynamics, and recovery deficits.",
    "To address heterogeneous data availability and distinct clinical decision horizons, a purpose-built three-model predictive architecture was engineered: (1) Model A (Next-Season Injury Risk Classification) achieves an outstanding 0.9815 ROC-AUC and 93% test accuracy across 800 physical screening and recovery profiles using a tuned tree ensemble; (2) Model B (Acute Short-Term Injury Risk Classification) operates on multi-sensor IMU, wearable telemetry, and workload features (7% positive class prevalence), utilizing SMOTE oversampling and 5-fold Platt sigmoid probability calibration to achieve 0.9820 ROC-AUC and a sport-science-optimized threshold of 0.8044 that balances false alarms with zero missed injuries; and (3) Model C (Sidelined-Days Regression) predicts post-injury rehabilitation downtime with R² = 0.324 and RMSE = 78.51 days under strict group-aware splitting preventing player-identity leakage.",
    "First-class explainability is embedded via TreeSHAP game-theoretic feature attributions, delivering individual waterfall risk ledgers that empower medical clinicians to trace every elevated probability directly to actionable biomechanical or workload drivers. Finally, the framework is operationalized as an interactive full-stack web application featuring real-time IMU oscilloscope waveform visualization, an interactive tactical squad pitch whiteboard, what-if load simulation, and automated clinical PDF reporting, keeping athlete biometric telemetry secure on local team infrastructure while transforming reactive sports medicine into proactive injury prevention."
]

ABSTRACT_TA = [
    "விளையாட்டு வீரர்களின் தசைநார் மற்றும் மூட்டு காயங்கள் (ACL கிழிசல், தொடை தசைநார் காயங்கள்) தொழில்முறை விளையாட்டுகளில் வீரர்களின் இருப்பை குறைக்கும் முதன்மையான காரணியாக உள்ளன. தற்போதுள்ள விளையாட்டு மருத்துவ முறைகள் பெரும்பாலும் உடலியல் சோர்வு ஏற்பட்ட பின்னரே கண்டறியும் செயலற்ற முறைகளையே நம்பியுள்ளன. தற்போதைய அணுகுமுறைகள் தனிப்பட்ட வினாத்தாள்கள் மற்றும் முந்தைய அனுபவங்களையே சார்ந்துள்ளதால், ஒரு பெரிய அணியில் தொடர்ச்சியான மற்றும் துல்லியமான கணிப்புகளை வழங்க முடிவதில்லை.",
    "இப்பணி 'AthleteShield' என்ற நவீன அணியக்கூடிய சென்சார் மற்றும் இயந்திரக் கற்றல் (Machine Learning) அடிப்படையிலான அமைப்பை அறிமுகப்படுத்துகிறது. இது முடுக்கமானி (Accelerometer), சுழற்சிமானி (Gyroscope) அடங்கிய IMU சென்சார்கள், GPS மற்றும் இதயத் துடிப்பு மாறுபாடு (HRV) தரவுகளை உடனுக்குடன் பகுப்பாய்வு செய்து, வீரர்களின் காய அபாயத்தை முன்கூட்டியே கணிக்கிறது. சிக்னல் செயலாக்கம் (Butterworth filter), படிநிலைக் கண்டறிதல் மற்றும் அதிர்வெண் பகுப்பாய்வு (FFT) மூலம் பயோமெக்கானிக்கல் அம்சங்கள் பிரித்தெடுக்கப்பட்டு, தீவிர மற்றும் நாள்பட்ட பணிச்சுமை விகிதம் (ACWR) போன்ற விளையாட்டு அறிவியல் அளவீடுகளுடன் இணைக்கப்படுகின்றன.",
    "இவ்வமைப்பு மூன்று தனித்துவமான மாதிரிகளைக் கொண்டுள்ளது: (1) மாதிரி A (அடுத்த பருவ காயக் கணிப்பு) 98.15% ROC-AUC துல்லியத்தை அடைகிறது; (2) மாதிரி B (உடனடி காய அபாய வகைப்பாடு) SMOTE மற்றும் பிளாட் சிக்மாய்டு அளவுத்திருத்தத்தைப் பயன்படுத்தி 98.20% ROC-AUC மற்றும் உகந்த வரம்புடன் இயங்குகிறது; (3) மாதிரி C (காயத்தினால் விலகியிருக்கும் நாட்கள் பின்னடைவு) வீரர்-அடிப்படையிலான குழுப் பிரிவின் கீழ் R² = 0.324 துல்லியத்துடன் செயல்படுகிறது.",
    "SHAP (Shapley Additive Explanations) மூலமாக ஒவ்வொரு வீரரின் காய அபாயத்திற்கான உடலியல் காரணங்களை மருத்துவர்கள் மற்றும் பயிற்சியாளர்கள் தெளிவாக அறிந்துகொள்ளும் வசதியும், நேரடி IMU அலைவரிசை கண்காணிப்பு மற்றும் அணி நிர்வாகத்துடன் கூடிய முழுமையான வலைப் பயன்பாடும் (Web Application) வெற்றிகரமாக உருவாக்கப்பட்டுள்ளது."
]

ACKNOWLEDGEMENT = [
    "We take this opportunity to express our profound sense of gratitude and respect to our project guide, Prof. Raghul J, Assistant Professor (Senior Grade), School of Computer Science and Engineering, Vellore Institute of Technology, for his invaluable guidance, technical insight, continuous encouragement, and meticulous supervision throughout the duration of this research.",
    "We also extend our sincere gratitude to the members of our project review panel for their constructive feedback, rigorous scrutiny, and thoughtful critiques that helped elevate the technical and methodological quality of this thesis.",
    "We express our heartfelt appreciation to the Head of the Department and the Dean, School of Computer Science and Engineering, Vellore Institute of Technology, for providing the state-of-the-art computational infrastructure, academic environment, and departmental resources essential for carrying out this research.",
    "Special thanks are owed to the global open-source and sports biomechanics research communities, whose publicly curated datasets, benchmark frameworks, and analytical libraries enabled rigorous validation of our multi-modal signal processing pipelines.",
    "Finally, we express our deepest love and gratitude to our parents, family members, and peers whose steadfast belief, patience, and unwavering moral support served as our greatest foundation of strength."
]

TOC_ITEMS = [
    ("", "ABSTRACT (ENGLISH)", "iii"),
    ("", "ABSTRACT (TAMIL)", "iv"),
    ("", "ACKNOWLEDGEMENT", "vi"),
    ("", "LIST OF FIGURES", "viii"),
    ("", "LIST OF TABLES", "x"),
    ("", "LIST OF ABBREVIATIONS", "xi"),
    ("", "LIST OF EQUATIONS", "xii"),
    ("1.", "INTRODUCTION", "1"),
    ("1.1", "Need for Wearable AI in Injury Prevention", "1"),
    ("1.2", "Project Objectives", "2"),
    ("1.3", "Problem Statement", "3"),
    ("1.4", "Technical & Practical Challenges", "4"),
    ("1.5", "Contributions and Impact", "5"),
    ("2.", "LITERATURE REVIEW", "6"),
    ("2.1", "Comprehensive Literature Survey", "6"),
    ("2.2", "Core Themes from Contemporary Literature", "9"),
    ("2.2.1", "Dominance of Tree-Ensemble Architectures", "9"),
    ("2.2.2", "Superiority of Multimodal Sensor Fusion", "9"),
    ("2.2.3", "Clinical Interpretability as a First-Class Requirement", "10"),
    ("2.2.4", "Class Imbalance Mitigation and Metric Selection", "10"),
    ("2.2.5", "Data Heterogeneity, Vendor Calibration & Privacy", "11"),
    ("3.", "SYSTEM ARCHITECTURE AND DESIGN", "12"),
    ("3.1", "System Architecture & End-to-End Data Flow", "12"),
    ("3.2", "Layer-by-Layer Architectural Modules", "13"),
    ("3.2.1", "Edge Sensing & Telemetry Ingestion Layer", "13"),
    ("3.2.2", "Biomechanical Signal Processing & IMU Feature Extraction", "14"),
    ("3.2.3", "Temporal Workload Modeling & Recovery Dynamics", "15"),
    ("3.2.4", "Multimodal Joint Prediction Engine (Models A, B, C)", "16"),
    ("3.2.5", "Decision Support & Classification Threshold Optimization", "17"),
    ("3.3", "Mathematical Formulation & Governing Equations", "18"),
    ("3.4", "Algorithmic Pipeline Specification", "20"),
    ("3.5", "System Design Considerations & Trade-offs", "21"),
    ("4.", "IMPLEMENTATION DETAILS, EXPERIMENTAL RESULTS AND EVALUATION", "23"),
    ("4.1", "Datasets & Experimental Setup", "23"),
    ("4.2", "Data Ingestion & Quality Audit", "25"),
    ("4.2.1", "Class-Balance Audit", "25"),
    ("4.2.2", "Composite-Score Leakage Audit", "26"),
    ("4.3", "Exploratory Data Analysis (EDA)", "27"),
    ("4.3.1", "Collegiate Athlete Injury Cohort", "27"),
    ("4.3.2", "University Football Screening Cohort", "29"),
    ("4.3.3", "Professional Football Longitudinal Cohort", "31"),
    ("4.3.4", "Wearable Telemetry & Raw IMU Signal Processing", "33"),
    ("4.4", "Feature Engineering & Multi-Sensor Fusion", "36"),
    ("4.4.1", "IMU Feature Extraction & Wearable Aggregation", "36"),
    ("4.4.2", "Collegiate & University Workload Features", "37"),
    ("4.4.3", "Professional Football Career & History Features", "38"),
    ("4.5", "Model A — Next-Season Injury Risk Classification", "39"),
    ("4.6", "Model B — Acute Injury Risk Classification & Threshold Optimization", "42"),
    ("4.7", "Model C — Sidelined-Days / Injury-Duration Regression", "45"),
    ("4.8", "Model Interpretability — SHAP Explainability", "47"),
    ("4.9", "Interactive Web Application & Real-Time Decision Support Platform", "50"),
    ("4.9.1", "Full-Stack Software Architecture & Execution Stack", "50"),
    ("4.9.2", "Clinical Diagnostics & Kinetic Screening Module", "51"),
    ("4.9.3", "Congested Match Micro-Cycle High Acute Risk State", "52"),
    ("4.9.4", "High-Precision 50Hz IMU Oscilloscope & Scope", "53"),
    ("4.9.5", "Tactical Squad Pitch & Position Fatigue Whiteboard", "54"),
    ("4.9.6", "What-If Workload & Recovery Simulator", "55"),
    ("4.9.7", "Batch Wearable Telemetry & CSV Ingestion", "56"),
    ("4.10", "Model Evaluation Strategy & Benchmarking", "57"),
    ("5.", "CONCLUSION AND FUTURE DIRECTIONS", "59"),
    ("5.1", "Conclusion", "59"),
    ("5.2", "Challenges & Limitations", "60"),
    ("5.2.1", "Design-Level Challenges", "60"),
    ("5.2.2", "Implementation-Level Limitations", "60"),
    ("5.3", "Future Directions", "62"),
    ("", "REFERENCES", "64")
]

LIST_OF_FIGURES = [
    ("3.1", "AthleteShield Multi-Layer System Architecture and End-to-End Data Flow Pipeline", "12"),
    ("4.1", "Injury-Label Class Balance: Collegiate Cohort (7% positive) vs. University Cohort (50% positive)", "26"),
    ("4.2", "Univariate Distributions of 13 Numeric Collegiate Features Partitioned by Injury Outcome", "28"),
    ("4.3", "Violin and Swarm Plots of Top Collegiate Predictors Partitioned by Injury Outcome", "29"),
    ("4.4", "KDE Distributions of 15 Numeric University Screening Features Partitioned by Next-Season Injury", "30"),
    ("4.5", "Joint Bivariate Distribution of Sleep Hours and Stress Level Colored by Next-Season Injury", "31"),
    ("4.6", "Logistic Sigmoidal Regression Fits of Injury Probability against Neuromuscular Screening Scores", "31"),
    ("4.7", "Distribution of Season Sidelined Days (Left) and Days Injured Partitioned by Playing Position (Right)", "32"),
    ("4.8", "Bivariate Scatters: Previous-Season Injury Days vs Current Days (Left) and Playing Minutes (Right)", "33"),
    ("4.9", "Clustered Correlation Heatmap of Professional Football Longitudinal Features", "33"),
    ("4.10", "Raw vs. 4th-Order Butterworth Filtered Acceleration Magnitude with Step Peaks (Cadence 77.1 spm)", "34"),
    ("4.11", "FFT Power Spectrum Density of Tri-Axial Acceleration for Downstairs Walking vs. Jogging", "35"),
    ("4.12", "Confusion Matrices for Candidate Classifiers on University Held-Out Test Set (Model A, n=160)", "41"),
    ("4.13", "ROC Curve, Precision-Recall Curve, and Threshold Optimization Curve for Calibrated Model B", "44"),
    ("4.14", "Predicted vs. Actual Sidelined Days (Left) and Residual Scatter Plot (Right) for Model C Regressor", "46"),
    ("4.15", "SHAP Global Feature Attribution Summary Plot for Model B Acute XGBoost Classifier", "48"),
    ("4.16", "SHAP Individual Waterfall Attribution Plot for Highest-Risk Athlete (Predicted Probability 94.52%)", "49"),
    ("4.17", "AthleteShield Web Application: Clinical Diagnostics & Kinetic Screening Dashboard Interface", "51"),
    ("4.18", "AthleteShield Web Application: Congested Match Micro-Cycle High Acute Risk State & KPI Cards", "52"),
    ("4.19", "AthleteShield Web Application: High-Precision 50Hz IMU Oscilloscope & Butterworth Scope", "53"),
    ("4.20", "AthleteShield Web Application: Tactical Squad Pitch & Position Fatigue Whiteboard Interface", "54"),
    ("4.21", "AthleteShield Web Application: Interactive What-If Workload & Recovery Simulator", "55"),
    ("4.22", "AthleteShield Web Application: Batch Wearable Telemetry & IMU CSV Ingestion Interface", "56")
]

LIST_OF_TABLES = [
    ("2.1", "Comprehensive Literature Survey of Wearable AI and Injury Risk Prediction Methodologies", "7"),
    ("3.1", "Layer-by-Layer Architectural Specifications and Technology Stack", "13"),
    ("4.1", "Multi-Source Datasets Profiled, Adapted, and Integrated into AthleteShield", "24"),
    ("4.2", "Data Ingestion and Structural Integrity Quality Audit Summary", "25"),
    ("4.3", "Correlation Matrix of Pre-Computed Collegiate Composite Scores against Injury Indicator", "26"),
    ("4.4", "Model A — Pre-Season Injury Risk Classification Benchmark on University Test Set (n=160)", "40"),
    ("4.5", "Model B — Acute Injury Risk Classification Benchmark on Collegiate Held-Out Test Set (n=40)", "43"),
    ("4.6", "Model C — Sidelined-Days Regression Benchmark on Professional Football Test Set (Group Split)", "45")
]

LIST_OF_ABBREVIATIONS = [
    ("ACL", "Anterior Cruciate Ligament"),
    ("ACWR", "Acute-to-Chronic Workload Ratio"),
    ("AI", "Artificial Intelligence"),
    ("ANT+", "Adaptive Network Topology Wireless Protocol"),
    ("AUC", "Area Under the ROC Curve"),
    ("BLE", "Bluetooth Low Energy"),
    ("BMI", "Body Mass Index"),
    ("CV", "Cross-Validation"),
    ("EDA", "Exploratory Data Analysis"),
    ("FFT", "Fast Fourier Transform"),
    ("GNSS", "Global Navigation Satellite System"),
    ("GPS", "Global Positioning System"),
    ("HAR", "Human Activity Recognition"),
    ("HR", "Heart Rate (Beats Per Minute)"),
    ("HRV", "Heart Rate Variability"),
    ("IMU", "Inertial Measurement Unit (Accelerometer + Gyroscope)"),
    ("IQR", "Interquartile Range"),
    ("KDE", "Kernel Density Estimation"),
    ("LightGBM", "Light Gradient Boosting Machine"),
    ("MNAR", "Missing Not At Random"),
    ("PR-AUC", "Precision-Recall Area Under Curve"),
    ("REST", "Representational State Transfer API"),
    ("RMSSD", "Root Mean Square of Successive RR Interval Differences"),
    ("ROC", "Receiver Operating Characteristic"),
    ("RPE", "Rating of Perceived Exertion (Borg CR-10 Scale)"),
    ("SHAP", "SHapley Additive exPlanations"),
    ("SMA", "Signal Magnitude Area"),
    ("SMOTE", "Synthetic Minority Over-sampling Technique"),
    ("UI / UX", "User Interface / User Experience"),
    ("VIF", "Variance Inflation Factor"),
    ("XGBoost", "eXtreme Gradient Boosting")
]

LIST_OF_EQUATIONS = [
    ("3.1", "4th-Order Butterworth Low-Pass Signal Filter Transfer Function", "18"),
    ("3.2", "Tri-Axial Instantaneous Acceleration Magnitude Calculation", "18"),
    ("3.3", "Tri-Axial Jerk Standard Deviation (Movement Abruptness Metric)", "18"),
    ("3.4", "Fast Fourier Transform Discrete Power Spectral Density", "18"),
    ("3.5", "Weekly Training Workload Product Formulation", "19"),
    ("3.6", "Acute:Chronic Workload Ratio (ACWR) Proxy Formulation", "19"),
    ("3.7", "Training Session Monotony Formulation", "19"),
    ("3.8", "Weekly Training Strain Index Formulation", "19"),
    ("3.9", "Recovery Deficit Composite Index Formulation", "19"),
    ("3.10", "Overall Physical Readiness Normalized Z-Score Index", "20"),
    ("3.11", "SMOTE Minority Class Synthetic Feature Interpolation", "20"),
    ("3.12", "Platt Sigmoidal Probability Calibration Transformation", "20")
]

print("Structured section metadata loaded successfully.")
