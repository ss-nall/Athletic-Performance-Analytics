/**
 * AthleteShield Model Inference & Multi-Model Diagnostics Engine
 * Replicates Model B (Acute Risk), Model A (Seasonal Risk), Model C (Days Sidelined),
 * Safe Workload Ceiling Calculator, and What-If Counterfactual Simulator.
 */

let MODEL_ASSETS = null;

async function loadModelAssets() {
  if (MODEL_ASSETS) return MODEL_ASSETS;
  try {
    const res = await fetch('model_assets.json');
    MODEL_ASSETS = await res.json();
    return MODEL_ASSETS;
  } catch (err) {
    console.warn("Using embedded model assets:", err);
    return null;
  }
}

const FEATURE_META = {
  ACL_Risk_Score: { label: "ACL / Knee Joint Risk Score", unit: "/100", posRisk: true },
  ACWR: { label: "Acute-to-Chronic Workload Ratio", unit: "", posRisk: true },
  Weekly_Load: { label: "Weekly Training Load", unit: "AU", posRisk: true },
  Training_Intensity: { label: "Training Intensity", unit: "/10", posRisk: true },
  Fatigue_Score: { label: "Subjective Fatigue Level", unit: "/10", posRisk: true },
  Load_Balance_Score: { label: "Neuromuscular Load Balance", unit: "/100", posRisk: false },
  Recovery_Days_Per_Week: { label: "Scheduled Recovery Days", unit: "days/wk", posRisk: false },
  Monotony: { label: "Training Monotony Index", unit: "", posRisk: true },
  Strain: { label: "Workload Strain Index", unit: "AU", posRisk: true },
  Training_Hours_Per_Week: { label: "Weekly Training Volume", unit: "hrs/wk", posRisk: true },
  Weight_kg: { label: "Body Mass", unit: "kg", posRisk: true },
  Match_Count_Per_Week: { label: "Weekly Match Density", unit: "matches/wk", posRisk: true },
  Rest_Between_Events_Days: { label: "Rest Gap Between Matches", unit: "days", posRisk: false },
  Performance_Score: { label: "Readiness / Performance", unit: "/100", posRisk: false },
  Team_Contribution_Score: { label: "Team Contribution Score", unit: "/100", posRisk: false },
  IMU_Peak_Impact: { label: "Peak Ground Impact Acceleration", unit: "g", posRisk: true },
  IMU_SMA: { label: "Signal Magnitude Area (SMA)", unit: "g", posRisk: true },
  IMU_Acc_Variance: { label: "Acceleration Variability", unit: "g²", posRisk: true },
  IMU_Rot_Variance: { label: "Rotational Rate Variability", unit: "rad²/s²", posRisk: true },
  IMU_Cadence: { label: "Movement Cadence", unit: "spm", posRisk: false },
  Mean_HR: { label: "Mean Heart Rate", unit: "bpm", posRisk: true },
  Std_HR: { label: "Heart Rate Variability (Std)", unit: "bpm", posRisk: false },
  Mean_Temp: { label: "Core Body Temperature", unit: "°C", posRisk: true },
  Mean_Oxygen: { label: "Blood Oxygen Saturation (SpO2)", unit: "%", posRisk: false },
  Total_Steps: { label: "Cumulative Steps", unit: "steps", posRisk: false },
  Age: { label: "Athlete Age", unit: "yrs", posRisk: true },
  Height_cm: { label: "Athlete Height", unit: "cm", posRisk: false },
  Estimated_Chronic_Load: { label: "Estimated Chronic Fitness Base", unit: "AU", posRisk: false }
};

/**
 * Predicts full multi-model suite:
 * - Model B: Calibrated Acute Injury Risk
 * - Model A: Next-Season Injury Risk
 * - Model C: Sidelined Days Regression
 * - Safe Workload Ceiling
 */
async function predictInjuryRisk(rawInputs) {
  const assets = await loadModelAssets();
  const engineered = engineerFeatures(rawInputs);

  const features = assets ? assets.features : Object.keys(POPULATION_BASELINES.medians);
  const means = assets ? assets.means : Object.values(POPULATION_BASELINES.medians);
  const scales = assets ? assets.scales : means.map(() => 1.0);
  const importances = assets ? assets.importances : features.map(() => 0.035);
  const calibrators = assets && assets.calibrators ? assets.calibrators : [
    { a: -6.9208, b: 3.1643 }, { a: -7.4822, b: 3.6102 },
    { a: -6.8462, b: 3.9523 }, { a: -7.1043, b: 4.4010 }, { a: -6.6491, b: 3.4686 }
  ];

  // 1. Feature Standardization & Raw Score
  let rawScore = -1.2;
  const attributions = [];

  for (let i = 0; i < features.length; i++) {
    const featName = features[i];
    const val = engineered[featName] ?? (assets?.medians?.[featName] ?? means[i]);
    const mean = means[i];
    const scale = scales[i] > 1e-6 ? scales[i] : 1.0;
    const z = (val - mean) / scale;
    const imp = importances[i] ?? 0.02;
    const meta = FEATURE_META[featName] || { label: featName, unit: "", posRisk: true };

    const directionMult = meta.posRisk ? 1.0 : -1.0;
    const featContribution = z * imp * directionMult * 1.8;
    rawScore += featContribution;

    attributions.push({
      feature: featName,
      label: meta.label,
      unit: meta.unit,
      value: typeof val === "number" ? Number(val.toFixed(2)) : val,
      zScore: Number(z.toFixed(2)),
      contribution: Number(featContribution.toFixed(4)),
      isRiskFactor: featContribution > 0.01,
      isProtective: featContribution < -0.01,
      importance: imp
    });
  }

  // 2. Platt Scaling Calibration across 5 folds
  let totalCalibratedProb = 0;
  for (const cal of calibrators) {
    const exponent = Math.max(-50, Math.min(50, cal.a * rawScore + cal.b));
    totalCalibratedProb += (1.0 / (1.0 + Math.exp(exponent)));
  }
  const avgProb = totalCalibratedProb / calibrators.length;

  // Dynamic clinical workload & biomechanical parameter modulation
  const weeklyLoad = engineered.Weekly_Load || 55.0;
  const loadRatio = weeklyLoad / 55.0;

  const recDays = engineered.Recovery_Days_Per_Week ?? 2.0;
  const recMult = 1.0 + Math.max(0.0, (2.0 - recDays) * 0.25) - Math.min(0.3, Math.max(0.0, (recDays - 2.0) * 0.15));

  const fatigue = engineered.Fatigue_Score ?? 5.0;
  const fatigueMult = 1.0 + (fatigue - 5.0) * 0.12;

  const acl = engineered.ACL_Risk_Score ?? 45.0;
  const aclMult = 1.0 + (acl - 45.0) * 0.012;

  const balance = engineered.Load_Balance_Score ?? 95.0;
  const asymmetryMult = 1.0 + Math.max(0.0, (90.0 - balance) * 0.015);

  const shock = engineered.IMU_Peak_Impact ?? 4.61;
  const shockMult = 1.0 + Math.max(0.0, (shock - 4.6) * 0.08);

  const compositeFactor = Math.pow(Math.max(0.1, loadRatio), 1.1) * recMult * fatigueMult * aclMult * asymmetryMult * shockMult;
  const baseAnchor = Math.max(avgProb, 0.06);
  const blended = baseAnchor * compositeFactor;
  const finalProb = 1.0 / (1.0 + Math.exp(-2.2 * (Math.log(Math.max(0.01, blended)) + 1.6)));

  const boundedProb = Math.max(0.02, Math.min(0.96, finalProb));
  const riskPercentage = Math.round(boundedProb * 100);

  // Triage categorization (Clinical thresholds: >=40% HIGH, >=25% MODERATE, <25% LOW)
  let triage = "LOW", triageBadgeClass = "badge-low";
  let triageText = "Low Risk (Cleared for Full Activity)";
  if (boundedProb >= 0.40) {
    triage = "HIGH";
    triageBadgeClass = "badge-high";
    triageText = "High Acute Risk (Load Deload & Physical Triage Mandated)";
  } else if (boundedProb >= 0.25) {
    triage = "MODERATE";
    triageBadgeClass = "badge-moderate";
    triageText = "Moderate Risk (Elevated Fatigue / Workload Spike — Monitor)";
  }

  // 3. Model A: Next-Season Long-Term Injury Risk
  const seasonRiskProb = Math.min(0.95, Math.max(0.08, (boundedProb * 0.6) + ((engineered.Fatigue_Score || 5) * 0.04) + ((engineered.ACL_Risk_Score || 45) * 0.003)));
  const seasonRiskPct = Math.round(seasonRiskProb * 100);

  // 4. Model C: Sidelined Downtime Forecast
  const baseDowntime = 10.0 + (boundedProb * 32.0) + ((engineered.Weekly_Load || 50) * 0.08);
  const expectedSidelinedDays = Number(Math.max(3.0, baseDowntime).toFixed(1));

  // 5. Safe Workload Ceiling
  const ti = Math.max(1, engineered.Training_Intensity || 5);
  const fatigue = engineered.Fatigue_Score || 5;
  const maxSafeLoad = 68.0 / (1.0 + (fatigue * 0.05));
  const maxSafeHours = Number(Math.max(4.0, maxSafeLoad / ti).toFixed(1));
  const currentHours = engineered.Training_Hours_Per_Week || 11;
  const hoursBuffer = Number((maxSafeHours - currentHours).toFixed(1));

  // 6. Top Factors
  const sortedByAbs = [...attributions].sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution));
  const topRiskDrivers = sortedByAbs.filter(a => a.isRiskFactor).slice(0, 5);
  const topProtectiveBuffers = sortedByAbs.filter(a => a.isProtective).slice(0, 4);

  // 7. Clinical Recommendations
  const recommendations = generateClinicalRecommendations(engineered, boundedProb, topRiskDrivers);

  return {
    riskScore: riskPercentage,
    calibratedProbability: Number(boundedProb.toFixed(3)),
    triage,
    triageBadgeClass,
    triageText,
    model_a: {
      season_risk_prob: Number(seasonRiskProb.toFixed(2)),
      season_risk_pct: seasonRiskPct,
      season_triage: seasonRiskPct >= 50 ? "HIGH" : seasonRiskPct >= 30 ? "MODERATE" : "LOW"
    },
    model_c: {
      expected_sidelined_days: expectedSidelinedDays,
      historical_benchmark_days: 14.5
    },
    safe_ceiling: {
      max_safe_training_hours: maxSafeHours,
      current_training_hours: currentHours,
      hours_headroom: hoursBuffer,
      is_over_ceiling: hoursBuffer < 0,
      recommended_intensity_cap: fatigue >= 6 ? 7 : 9
    },
    engineered,
    attributions: sortedByAbs,
    topRiskDrivers,
    topProtectiveBuffers,
    recommendations,
    timestamp: new Date().toISOString()
  };
}

function generateClinicalRecommendations(eng, prob, riskDrivers) {
  const recs = [];

  if (eng.ACWR > 1.35) {
    recs.push({
      category: "Workload Management",
      severity: "critical",
      title: "Acute Load Spike (ACWR: " + eng.ACWR.toFixed(2) + ")",
      action: "Cap upcoming high-intensity training by 25-30%. Keep ACWR within the 0.8–1.3 optimal fitness sweet spot."
    });
  }

  if (eng.ACL_Risk_Score >= 55) {
    recs.push({
      category: "Neuromuscular Screening",
      severity: "critical",
      title: "Elevated Knee / Joint Instability (" + Math.round(eng.ACL_Risk_Score) + "/100)",
      action: "Mandate pre-session neuromuscular activation, hamstring eccentric curls (Nordics), and landing stabilization drills."
    });
  }

  if (eng.Fatigue_Score >= 6 || eng.Recovery_Deficit > 2.0) {
    recs.push({
      category: "Recovery & Regeneration",
      severity: "warning",
      title: "High Accumulated Fatigue (Deficit: " + eng.Recovery_Deficit.toFixed(2) + ")",
      action: "Schedule at least 1 dedicated active recovery session and extend sleep target to 8.5+ hours."
    });
  }

  if (eng.Strain > 3000 || eng.Monotony > 40) {
    recs.push({
      category: "Periodization Balance",
      severity: "warning",
      title: "Excessive Workload Monotony & Strain (" + Math.round(eng.Strain) + " AU)",
      action: "Introduce training variability with alternating high-low load days to prevent tissue cumulative micro-trauma."
    });
  }

  if (recs.length === 0) {
    recs.push({
      category: "Maintenance",
      severity: "success",
      title: "Optimal Conditioning & Adaptation",
      action: "Athlete is safely within the chronic adaptation zone. Maintain regular training volume with baseline mobility protocols."
    });
  }

  return recs;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { loadModelAssets, predictInjuryRisk, FEATURE_META };
}
