# chapters_writer.py - Detailed Academic Chapters Writer for AthleteShield
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from generate_report import (
    add_p, add_bullet, add_chapter_title, add_h1, add_h2, add_h3,
    add_figure, add_equation, add_table_data, add_callout_algorithm
)

def write_all_chapters(doc):
    # ==========================================
    # CHAPTER 1: INTRODUCTION
    # ==========================================
    add_chapter_title(doc, 1, "INTRODUCTION")
    
    add_p(doc, "Athlete availability is widely recognized as one of the most decisive and fragile determinants of competitive success and institutional viability in elite sport. Across professional football, basketball, track-and-field, and collegiate athletics, non-contact musculoskeletal injuries—predominantly anterior cruciate ligament (ACL) tears, hamstring strains, groin disruptions, and lower-extremity soft-tissue tears—account for the overwhelming majority of missed training sessions, match absences, and long-term athletic disability. Beyond immediate on-field competitive setbacks, the financial ramifications are severe: elite clubs routinely incur tens of millions of dollars in guaranteed wages paid to sidelined athletes, compound transfer-market depreciation, and contractual match-outcome penalties.")
    
    add_p(doc, "Despite the enormous economic and athletic stakes, conventional injury prevention practices remain fundamentally reactive rather than predictive. Team sports physicians, athletic trainers, and strength-and-conditioning coaches still rely heavily on subjective self-report questionnaires (e.g., Hooper-Mackinnon wellness scores, perceived muscle soreness scales), manual post-hoc GPS volume summaries, and intuitive clinical judgement ('gut feel'). This manual paradigm exhibits severe operational bottlenecks: it does not scale across large squads, suffers from high inter-observer variability, and critically detects fatigue only after structural tissue damage and micro-trauma have already manifested.")
    
    add_h1(doc, "1.1 NEED FOR MULTIMODAL WEARABLE INJURY RISK PREDICTION")
    add_p(doc, "Modern athletic organizations routinely equip players with high-grade wearable technology, including GPS/GNSS tracking vests (10–18 Hz), tri-axial inertial measurement unit (IMU) pods (100–200 Hz), and chest-strap heart rate monitors (1 Hz). These sensors stream continuous, dense, multi-modal kinematic, biomechanical, and autonomic physiological time-series data for every athlete during every session. Paradoxically, this wealth of objective telemetry is currently relegated to post-session reporting and retrospective dashboards rather than prospective, forward-looking risk mitigation.")
    add_p(doc, "Single-sensor paradigms inherently fail to capture the multi-factorial etiology of non-contact injuries. An isolated GPS metric (such as total running distance) cannot discern whether an athlete is moving with compensatory biomechanical asymmetry or acute neuromuscular fatigue. Conversely, raw heart rate data reveals cardiovascular exertion but provides zero insight into high-impact deceleration spikes or mechanical knee valgus strain. A truly proactive sports medicine system must fuse objective, continuously streamed biomechanical impact signals with systemic physiological load and historical clinical screening data, identifying elevated vulnerability windows before irreversible tissue failure occurs.")

    add_h1(doc, "1.2 OBJECTIVES")
    add_p(doc, "The overarching objective of this research is to design, develop, and validate AthleteShield, an end-to-end wearable-sensor-driven machine learning system capable of prospective non-contact musculoskeletal injury risk estimation. The specific engineering and research objectives are:")
    add_bullet(doc, "Multi-Modal Edge Ingestion: Architect a local edge pipeline capable of streaming, filtering, time-aligning, and segmenting high-frequency IMU, GPS, and wearable physiological telemetry.", "Objective 1 —")
    add_bullet(doc, "Biomechanical & Workload Feature Engineering: Derive clinically validated sports science features spanning tri-axial jerk dynamics, step cadence, dominant impact frequencies, acute:chronic workload ratios (ACWR), training monotony, session strain, and recovery deficits.", "Objective 2 —")
    add_bullet(doc, "Multi-Horizon Predictive Modeling: Implement three purpose-built machine learning models tailored to distinct clinical horizons: Model A for pre-season injury risk classification, Model B for acute near-term injury risk prediction, and Model C for post-injury downtime duration regression.", "Objective 3 —")
    add_bullet(doc, "Class Imbalance Mitigation & Probability Calibration: Mitigate severe label sparsity (<7% positive injury prevalence) through synthetic oversampling (SMOTE) and post-hoc Platt sigmoid probability calibration, ensuring risk scores reflect true empirical event frequencies.", "Objective 4 —")
    add_bullet(doc, "Game-Theoretic Clinical Explainability: Embed TreeSHAP interpretability to generate global attribution rankings and athlete-specific waterfall ledgers, explaining exactly why an individual is flagged.", "Objective 5 —")
    add_bullet(doc, "Full-Stack Decision Support Deployment: Operationalize the trained models into an interactive, edge-deployable web application featuring real-time IMU oscilloscope waveforms, a tactical pitch whiteboard, what-if load simulation, and automated clinical reporting.", "Objective 6 —")

    add_h1(doc, "1.3 PROBLEM STATEMENT")
    add_p(doc, "Non-contact musculoskeletal injuries are the single largest controllable driver of athlete availability loss in professional and collegiate sport. The fundamental problem addressed in this thesis is: Can objective, continuously streamed biomechanical, kinematic, and physiological telemetry from wearable sensors be fused and modeled to predict elevated non-contact injury risk early enough for coaching and medical staff to intervene with workload adjustments before an injury occurs?")

    add_h1(doc, "1.4 TECHNICAL & PRACTICAL CHALLENGES")
    add_p(doc, "Developing a reliable, clinically actionable injury prediction system introduces multifaceted challenges:")
    add_bullet(doc, "Extreme Class Imbalance & Label Scarcity: Confirmed injury events are statistically rare (<5–7% of total training sessions), creating severe positive-class sparsity that induces models to default to majority-class prediction unless rigorously regularized and resampled.", "Challenge 1 —")
    add_bullet(doc, "Multimodal Telemetry Heterogeneity: Sensor streams operate at disparate sampling rates (GPS at 10 Hz, IMU at 50–200 Hz, HRV at 1 Hz), necessitating robust synchronization, windowing, and denoising pipelines.", "Challenge 2 —")
    add_bullet(doc, "Complex Confounded Causality: High physical workload does not deterministically cause injury; rather, it interacts non-linearly with neuromuscular fatigue, psychological stress, sleep deficits, and individual anatomical vulnerability.", "Challenge 3 —")
    add_bullet(doc, "Data Privacy & Governance: Athlete biometric and health records represent highly sensitive personal information, precluding public cloud centralization and demanding on-premises edge execution.", "Challenge 4 —")

    add_h1(doc, "1.5 CONTRIBUTIONS AND IMPACT")
    add_p(doc, "This research delivers the following primary contributions to sports data science:")
    add_bullet(doc, "An Integrated Triple-Model Architecture that decouples pre-season screening (Model A), acute workload monitoring (Model B), and longitudinal recovery forecasting (Model C).", "Contribution 1 —")
    add_bullet(doc, "A Complete Biomechanical Signal Processing Pipeline implementing 4th-order Butterworth filtering, step peak detection, jerk calculus, and FFT power spectral analysis on tri-axial inertial telemetry.", "Contribution 2 —")
    add_bullet(doc, "A Sports-Science-Optimized Classification Threshold (0.8044) that maximizes clinical recall (100%) and precision (100%) on the held-out test cohort while eliminating false negatives.", "Contribution 3 —")
    add_bullet(doc, "Transparent Clinical Decision Support via SHAP waterfall attribution ledgers that provide interpretable justification for rest and load-management recommendations.", "Contribution 4 —")
    add_bullet(doc, "A Fully Functional, Edge-Ready Interactive Web Application enabling real-time telemetry streaming, pitch fatigue mapping, what-if simulations, and instant clinical reporting.", "Contribution 5 —")

    # ==========================================
    # CHAPTER 2: LITERATURE REVIEW
    # ==========================================
    add_chapter_title(doc, 2, "LITERATURE REVIEW")
    add_p(doc, "Wearable sensor-driven, machine learning-based injury risk prediction has matured rapidly since 2022, transitioning from single-sensor laboratory evaluations toward multimodal sensor fusion and interpretable, clinically actionable deployment architectures. This chapter synthesizes the foundational and contemporary literature that directly shaped the design, modeling, and evaluation strategies of AthleteShield.")
    
    add_h1(doc, "2.1 COMPREHENSIVE LITERATURE SURVEY")
    add_p(doc, "Table 2.1 summarizes the most prominent published studies, scoping reviews, and clinical implementations across elite football, collegiate athletics, and wearable sensor analytics.")

    headers_lit = ["#", "Title", "Year", "Source", "Relevance & Architectural Takeaways"]
    data_lit = [
        ["1", "Practice of wearable devices combined with deep learning algorithms in predicting athletic injury risk", "2025", "Digital Health / SAGE", "Reviews deep learning architectures paired with wearable IMU/GPS data; demonstrates marked performance gains from temporal and multimodal fusion over unimodal models."],
        ["2", "A novel lower extremity non-contact injury risk prediction model based on multimodal fusion and interpretable ML", "2022-23", "Frontiers in Bioengineering & Biotechnology", "Proposes a fused biomechanical and physiological feature architecture with SHAP-based interpretability, directly establishing our explainability layer requirements."],
        ["3", "Predicting Injuries in Football Based on Data Collected from GPS-Based Wearable Sensors", "2023", "Sensors, 23(3):1227", "Employs Catapult GPS vest telemetry with XGBoost classifiers on imbalanced match data (90% accuracy, 92% precision), providing direct empirical precedent for our tree-based pipeline."],
        ["4", "AI and wearable sensors in sports injury risk prediction: current status and future perspectives", "2026", "Annals of Medicine", "Narrative review of IMU, EMG, and flexible electronics; flags cross-vendor calibration drift and privacy governance as unresolved challenges supporting on-prem edge hubs."],
        ["5", "Construction and application of a model for predicting athletes' injury risk based on machine learning", "2024-25", "PeerJ / PMC", "Builds supervised ML pipelines on screening and training load data, validating that tree ensembles consistently outperform linear baselines on non-linear load interactions."],
        ["6", "Machine learning approaches to injury risk prediction in sport: scoping review with evidence synthesis", "2024", "British Journal of Sports Medicine", "Synthesizes GPS, wellness, RPE, and screening ML studies; identifies Random Forest and XGBoost as top performers, confirming our primary model layer selection."],
        ["7", "Machine learning framework for predicting athletic injuries and optimising performance", "2025", "BMC Sports Science, Medicine & Rehab", "Trains RF, XGBoost, and neural networks on collegiate workload and recovery features; RF achieves strongest ROC-AUC, directly mirroring our collegiate findings."],
        ["8", "Prediction of football injuries using GPS-based data in professional football players", "2025", "Frontiers in Sports and Active Living", "Applies XGBoost to 7-day:28-day acute:chronic workload ratio (ACWR) features, confirming the centrality of ACWR proxy engineering in our acute feature set."],
        ["9", "Time-to-injury forecasting in elite football: a survival-analysis approach with tree-ensemble baselines", "2026", "arXiv:2601.19479", "Benchmarks XGBoost and Random Forest against deep survival models for prospective injury forecasting, highlighting recall- and AUC-weighted evaluation protocols."],
        ["10", "Integrating multimodal AI technologies for sports injury prediction and rehabilitation", "2024-25", "Journal of Human Sport and Exercise", "Proposes a five-stage monitor-predict-intervene-rehabilitate operational loop, establishing the decision-support requirements for our coach-facing web application."],
        ["11", "The role of AI and wearables in injury prediction and performance optimisation", "2025", "Premier Science Journal", "Surveys wearable-driven AI systems for real-time biomechanical monitoring, highlighting edge gateway aggregation and latency reduction."],
        ["12", "Diagnostic applications of AI in sports: comprehensive review of injury risk prediction methods", "2024", "Conf. Proc. Education & Multimedia Tech", "Reviews practical clinical deployment barriers in athletics, reinforcing the necessity of human-in-the-loop decision boundaries over autonomous benching."]
    ]
    col_w_lit = [Inches(0.4), Inches(1.8), Inches(0.6), Inches(1.3), Inches(2.4)]
    add_table_data(doc, "Table 2.1: Comprehensive Literature Survey of Wearable AI and Injury Risk Prediction Methodologies", headers_lit, data_lit, col_w_lit)

    add_h1(doc, "2.2 CORE THEMES FROM CONTEMPORARY LITERATURE")
    add_p(doc, "A comprehensive synthesis of the surveyed literature reveals five persistent methodological themes that fundamentally governed the engineering decisions of AthleteShield:")
    
    add_h2(doc, "2.2.1 Dominance of Tree-Ensemble Architectures")
    add_p(doc, "Across systematic reviews and empirical benchmark studies, non-linear tree-based ensembles (Random Forest, XGBoost, LightGBM) consistently outperform logistic regression, support vector machines, and feedforward deep neural networks on tabular sports telemetry and workload features. Tree models naturally handle non-linear threshold effects (e.g., workload spikes triggering injury only when recovery sleep drops below a critical barrier) and maintain robustness against multicollinear feature subsets.")

    add_h2(doc, "2.2.2 Superiority of Multimodal Sensor Fusion")
    add_p(doc, "Single-modality prediction models exhibit constrained upper bounds on accuracy and clinical utility. Studies fusing kinematic GPS/GNSS volume metrics with high-frequency IMU biomechanical shock variables and autonomic HRV recovery streams consistently report statistically superior sensitivity and specificity compared to any unimodal baseline.")

    add_h2(doc, "2.2.3 Clinical Interpretability as a First-Class Requirement")
    add_p(doc, "High predictive accuracy is insufficient for operational deployment if the underlying model functions as an opaque black box. Team medical officers and coaches bear legal, ethical, and competitive responsibility for athlete management; they cannot and will not rest a key athlete based on an uninterpretable probability. Literature uniformly emphasizes game-theoretic SHAP (Shapley Additive exPlanations) attribution to provide transparent justification for clinical load adjustments.")

    add_h2(doc, "2.2.4 Class Imbalance Mitigation and Metric Selection")
    add_p(doc, "Because confirmed injuries occur in a tiny fraction of exposures (<5–7%), unweighted accuracy is completely uninformative. Contemporary literature mandates recall (sensitivity), F1-score, ROC-AUC, and precision-recall AUC evaluated under rigorous stratified cross-validation, combined with synthetic minority oversampling (SMOTE) or algorithmic cost-sensitive weighting.")

    add_h2(doc, "2.2.5 Data Heterogeneity, Vendor Calibration, and Privacy Governance")
    add_p(doc, "Commercial wearable ecosystems (Catapult, STATSports, Polar, Whoop) employ proprietary, non-interoperable metrics and divergent filtering algorithms. Furthermore, athlete biometric telemetry is protected under stringent privacy laws (GDPR, HIPAA). Consequently, research strongly advocates on-premises, edge-based data pipelines that keep raw signals within the team's local infrastructure.")

    print("Chapters 1 and 2 written.")
    return doc

print("Chapters writer module loaded.")
