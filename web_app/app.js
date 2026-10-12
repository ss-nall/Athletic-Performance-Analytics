/**
 * AthleteShield: Bespoke Sports Science & Tactical Controller
 */

let currentPrediction = null;
let batchAthletesData = [];
let longitudinalHistory = [];
let sampleIMUData = null;
let isStreamSimulating = false;
let streamAnimationId = null;
let streamOffset = 0;

document.addEventListener("DOMContentLoaded", async () => {
  setupDragAndDrop();
  updateTactilePill("hours", document.getElementById("inp-Training_Hours_Per_Week")?.value || 11, "hrs", "Training_Hours_Per_Week", 2, 30);
  updateTactilePill("intensity", document.getElementById("inp-Training_Intensity")?.value || 5, "/10", "Training_Intensity", 1, 10);
  updateTactilePill("fatigue", document.getElementById("inp-Fatigue_Score")?.value || 5, "/10", "Fatigue_Score", 1, 10);
  updateTactilePill("acl", document.getElementById("inp-ACL_Risk_Score")?.value || 45, "/100", "ACL_Risk_Score", 0, 100);
  updateTactilePill("balance", document.getElementById("inp-Load_Balance_Score")?.value || 98, "/100", "Load_Balance_Score", 40, 100);
  updateCompletionMeter();
  loadStoredHistory();
  await recalculatePrediction();
  initWaveforms();
  renderTacticalPitch("4-3-3");
  runSimulation();
});

/* ==========================================================================
   Tab Navigation & Workspaces
   ========================================================================== */

function switchMainTab(tab) {
  document.querySelectorAll(".nav-tab-btn").forEach(b => b.classList.remove("active"));
  const activeBtn = document.getElementById(`tab-${tab}`);
  if (activeBtn) activeBtn.classList.add("active");

  const views = ["questionnaire", "simulator", "waveform", "pitch", "history", "csv"];
  views.forEach(v => {
    const el = document.getElementById(`view-${v}`);
    if (el) el.style.display = (v === tab) ? (v === "questionnaire" ? "grid" : "block") : "none";
  });

  if (tab === "waveform") drawWaveforms();
  if (tab === "history") drawACWRTrendChart();
  if (tab === "questionnaire" && currentPrediction) drawRadarChart(currentPrediction);
}

function switchStep(stepNum) {
  document.querySelectorAll(".step-tab").forEach((t, idx) => {
    const isTarget = idx + 1 === stepNum;
    t.classList.toggle("active", isTarget);
    const numEl = t.querySelector(".step-number");
    if (idx + 1 < stepNum) {
      t.classList.add("completed");
      if (numEl) numEl.textContent = "✓";
    } else {
      if (numEl && !t.classList.contains("completed")) {
        numEl.textContent = idx + 1;
      }
    }
  });
  document.querySelectorAll(".form-section").forEach((s, idx) => {
    s.classList.toggle("active", idx + 1 === stepNum);
  });
}

function selectLoadPreset(hours, intensity, btn) {
  setInputValue("Training_Hours_Per_Week", hours);
  setInputValue("Training_Intensity", intensity);
  updateTactilePill("hours", hours, "hrs", "Training_Hours_Per_Week", 2, 30);
  updateTactilePill("intensity", intensity, "/10", "Training_Intensity", 1, 10);
  highlightSiblingPill(btn);
  handleInputChange();
}

function selectRecoveryDays(days, btn) {
  setInputValue("Recovery_Days_Per_Week", days);
  const hint = document.getElementById("recovery-hint");
  if (hint) {
    if (days >= 3) {
      hint.textContent = "Protected Buffer";
      hint.style.color = "var(--color-low)";
    } else if (days === 2) {
      hint.textContent = "Safe Buffer";
      hint.style.color = "var(--color-low)";
    } else if (days === 1) {
      hint.textContent = "Caution (Fatigue Debt)";
      hint.style.color = "var(--color-moderate)";
    } else {
      hint.textContent = "Severe Acute Risk!";
      hint.style.color = "var(--color-high)";
    }
  }
  highlightSiblingPill(btn);
  handleInputChange();
}

function selectMatchCount(matches, btn) {
  setInputValue("Match_Count_Per_Week", matches);
  const hint = document.getElementById("match-hint");
  if (hint) {
    if (matches <= 1) {
      hint.textContent = "Low Density";
      hint.style.color = "var(--color-low)";
    } else if (matches === 2) {
      hint.textContent = "Standard Density";
      hint.style.color = "var(--primary)";
    } else {
      hint.textContent = "Congested Schedule";
      hint.style.color = "var(--color-high)";
    }
  }
  highlightSiblingPill(btn);
  handleInputChange();
}

function selectFatiguePreset(score, btn) {
  setInputValue("Fatigue_Score", score);
  updateTactilePill("fatigue", score, "/10", "Fatigue_Score", 1, 10);
  highlightSiblingPill(btn);
  handleInputChange();
}

function selectACLPreset(score, btn) {
  setInputValue("ACL_Risk_Score", score);
  updateTactilePill("acl", score, "/100", "ACL_Risk_Score", 0, 100);
  highlightSiblingPill(btn);
  handleInputChange();
}

function selectBalancePreset(score, btn) {
  setInputValue("Load_Balance_Score", score);
  updateTactilePill("balance", score, "/100", "Load_Balance_Score", 40, 100);
  highlightSiblingPill(btn);
  handleInputChange();
}

function selectBiometricsPreset(type, btn) {
  if (type === "recovery") {
    setInputValue("Mean_HR", 68.0);
    setInputValue("Std_HR", 62.0);
    setInputValue("Mean_Temp", 36.8);
    setInputValue("Mean_Oxygen", 99.0);
  } else if (type === "aerobic") {
    setInputValue("Mean_HR", 120.6);
    setInputValue("Std_HR", 34.8);
    setInputValue("Mean_Temp", 37.0);
    setInputValue("Mean_Oxygen", 97.4);
  } else if (type === "match") {
    setInputValue("Mean_HR", 165.0);
    setInputValue("Std_HR", 18.5);
    setInputValue("Mean_Temp", 38.2);
    setInputValue("Mean_Oxygen", 95.5);
  }
  updateBiometricsBadges();
  highlightSiblingPill(btn);
  handleInputChange();
}

function selectImpactPreset(type, btn) {
  if (type === "soft") {
    setInputValue("IMU_Peak_Impact", 3.20);
    setInputValue("IMU_Cadence", 95.0);
    setInputValue("IMU_SMA", 1.05);
    setInputValue("IMU_Acc_Variance", 0.22);
  } else if (type === "firm") {
    setInputValue("IMU_Peak_Impact", 4.61);
    setInputValue("IMU_Cadence", 99.7);
    setInputValue("IMU_SMA", 1.32);
    setInputValue("IMU_Acc_Variance", 0.37);
  } else if (type === "hard") {
    setInputValue("IMU_Peak_Impact", 6.80);
    setInputValue("IMU_Cadence", 112.0);
    setInputValue("IMU_SMA", 1.88);
    setInputValue("IMU_Acc_Variance", 0.65);
  }
  updateImpactBadges();
  highlightSiblingPill(btn);
  handleInputChange();
}

function highlightSiblingPill(btn) {
  if (!btn || !btn.parentElement) return;
  btn.parentElement.querySelectorAll(".stage-chip-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
}

function updateBiometricsBadges() {
  const hr = Number(document.getElementById("inp-Mean_HR")?.value || 120);
  const hrv = Number(document.getElementById("inp-Std_HR")?.value || 35);
  const temp = Number(document.getElementById("inp-Mean_Temp")?.value || 37);
  const spo2 = Number(document.getElementById("inp-Mean_Oxygen")?.value || 97);

  const bHr = document.getElementById("badge-hr-status");
  if (bHr) {
    if (hr < 90) { bHr.textContent = "Rest / Recovery"; bHr.style.color = "var(--primary)"; }
    else if (hr <= 145) { bHr.textContent = "Zone 2 Aerobic"; bHr.style.color = "var(--color-low)"; }
    else { bHr.textContent = "Zone 4–5 Threshold"; bHr.style.color = "var(--color-high)"; }
  }

  const bHrv = document.getElementById("badge-hrv-status");
  if (bHrv) {
    if (hrv >= 45) { bHrv.textContent = "High Parasympathetic"; bHrv.style.color = "var(--color-low)"; }
    else if (hrv >= 25) { bHrv.textContent = "Normal Vagal"; bHrv.style.color = "var(--primary)"; }
    else { bHrv.textContent = "Depressed HRV"; bHrv.style.color = "var(--color-high)"; }
  }

  const bTemp = document.getElementById("badge-temp-status");
  if (bTemp) {
    if (temp <= 37.4) { bTemp.textContent = "Normothermic"; bTemp.style.color = "var(--color-low)"; }
    else if (temp <= 38.0) { bTemp.textContent = "Warm Stimulus"; bTemp.style.color = "var(--color-moderate)"; }
    else { bTemp.textContent = "Heat Strain"; bTemp.style.color = "var(--color-high)"; }
  }

  const bSpo2 = document.getElementById("badge-spo2-status");
  if (bSpo2) {
    if (spo2 >= 96) { bSpo2.textContent = "Optimal (96%+)"; bSpo2.style.color = "var(--color-low)"; }
    else if (spo2 >= 94) { bSpo2.textContent = "Mild Hypoxemia"; bSpo2.style.color = "var(--color-moderate)"; }
    else { bSpo2.textContent = "Desaturated (<94%)"; bSpo2.style.color = "var(--color-high)"; }
  }
}

function updateImpactBadges() {
  const g = Number(document.getElementById("inp-IMU_Peak_Impact")?.value || 4.6);
  const bImp = document.getElementById("badge-impact-status");
  if (bImp) {
    if (g < 4.0) { bImp.textContent = "Protected (<4g)"; bImp.style.color = "var(--color-low)"; }
    else if (g <= 5.5) { bImp.textContent = "Normal Turf (4–5.5g)"; bImp.style.color = "var(--color-low)"; }
    else { bImp.textContent = "Shock Spike (>5.5g)"; bImp.style.color = "var(--color-high)"; }
  }
}

async function triggerManualRecalculation(btn) {
  if (!btn) return;
  const originalHTML = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="spin-icon">
      <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
      <path d="M12 2a10 10 0 0 1 10 10"/>
    </svg>
    Recalculating...
  `;

  await recalculatePrediction();

  btn.classList.add("btn-recalc-success");
  btn.innerHTML = `
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
    ✓ Diagnostics Recalculated
  `;

  document.querySelectorAll(".step-tab").forEach(tab => {
    tab.classList.add("completed");
    const numEl = tab.querySelector(".step-number");
    if (numEl) numEl.textContent = "✓";
  });

  setTimeout(() => {
    btn.classList.remove("btn-recalc-success");
    btn.innerHTML = originalHTML;
    btn.disabled = false;
  }, 1600);
}

function updateTactilePill(type, val, unit, inputId, minVal, maxVal) {
  const badge = document.getElementById(`badge-${type}`);
  if (badge) badge.textContent = `${val} ${unit}`;

  if (inputId && minVal !== undefined && maxVal !== undefined) {
    const num = Number(val);
    const pct = Math.max(0, Math.min(100, ((num - minVal) / (maxVal - minVal)) * 100));
    const fill = document.getElementById(`fill-${inputId}`);
    const pill = document.getElementById(`pill-${inputId}`);
    if (fill) fill.style.width = `${pct}%`;
    if (pill) {
      pill.style.left = `${pct}%`;
      pill.textContent = `${val} ${unit}`;
    }
  }
}

function jumpToJointFeature(jointName) {
  let stepNum = 1;
  let targetGroupId = "group-Training_Hours_Per_Week";

  if (jointName === "knee") {
    stepNum = 2;
    targetGroupId = "group-ACL_Risk_Score";
  } else if (jointName === "hamstring") {
    stepNum = 2;
    targetGroupId = "group-Load_Balance_Score";
  } else if (jointName === "lumbar") {
    stepNum = 2;
    targetGroupId = "group-Fatigue_Score";
  } else if (jointName === "core") {
    stepNum = 1;
    targetGroupId = "group-Training_Intensity";
  } else if (jointName === "ankle") {
    stepNum = 4;
    targetGroupId = "group-IMU_Peak_Impact";
  }

  switchStep(stepNum);
  setTimeout(() => {
    const el = document.getElementById(targetGroupId);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      el.classList.remove("highlight-pulse");
      void el.offsetWidth;
      el.classList.add("highlight-pulse");
    }
  }, 60);
}

let _lastAnimatedRisk = 12;
function animateCounter(element, start, end, duration = 650) {
  if (!element) return;
  const startTime = performance.now();
  const step = (currentTime) => {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easeOut = 1 - Math.pow(1 - progress, 3);
    const currentVal = Math.round(start + (end - start) * easeOut);
    element.textContent = currentVal;
    if (progress < 1) {
      requestAnimationFrame(step);
    } else {
      element.textContent = end;
    }
  };
  requestAnimationFrame(step);
}

/* ==========================================================================
   Feature Completion Meter
   ========================================================================== */

const PRIMARY_INPUT_IDS = [
  "inp-Training_Hours_Per_Week", "inp-Training_Intensity", "inp-Recovery_Days_Per_Week",
  "inp-Match_Count_Per_Week", "inp-Fatigue_Score", "inp-ACL_Risk_Score",
  "inp-Load_Balance_Score", "inp-Mean_HR", "inp-Std_HR", "inp-IMU_Peak_Impact"
];

function updateCompletionMeter() {
  let filledCount = 0;
  PRIMARY_INPUT_IDS.forEach(id => {
    const el = document.getElementById(id);
    if (el && el.value !== "" && !isNaN(Number(el.value))) filledCount++;
  });

  const total = PRIMARY_INPUT_IDS.length;
  const pct = Math.round((filledCount / total) * 100);
  const bar = document.getElementById("completion-bar");
  const txt = document.getElementById("completion-text");

  if (bar) bar.style.width = `${pct}%`;
  if (txt) {
    if (filledCount >= 8) {
      txt.textContent = `${filledCount} / ${total} Features Set (High Clinical Confidence)`;
      txt.style.color = "var(--color-low)";
    } else if (filledCount >= 5) {
      txt.textContent = `${filledCount} / ${total} Features Set (Moderate Confidence)`;
      txt.style.color = "var(--primary)";
    } else {
      txt.textContent = `${filledCount} / ${total} Features Set (Pop. Median Imputation Active)`;
      txt.style.color = "var(--color-moderate)";
    }
  }
}

function handleInputChange() {
  updateCompletionMeter();
  clearTimeout(window._recalcTimeout);
  window._recalcTimeout = setTimeout(() => {
    recalculatePrediction();
  }, 100);
}

/* ==========================================================================
   Clinical Presets
   ========================================================================== */

function applyPreset(name) {
  if (name === "overworked") {
    setInputValue("Training_Hours_Per_Week", 18);
    setInputValue("Training_Intensity", 9);
    setInputValue("Recovery_Days_Per_Week", 1);
    setInputValue("Match_Count_Per_Week", 3);
    setInputValue("Rest_Between_Events_Days", 1);
    setInputValue("Fatigue_Score", 8);
    setInputValue("ACL_Risk_Score", 82);
    setInputValue("Load_Balance_Score", 68);
    setInputValue("Performance_Score", 55);
    setInputValue("Mean_HR", 168);
    setInputValue("Std_HR", 18.2);
    setInputValue("IMU_Peak_Impact", 7.4);
    setInputValue("IMU_SMA", 2.45);
  } else if (name === "rested") {
    setInputValue("Training_Hours_Per_Week", 9);
    setInputValue("Training_Intensity", 4);
    setInputValue("Recovery_Days_Per_Week", 3);
    setInputValue("Match_Count_Per_Week", 1);
    setInputValue("Rest_Between_Events_Days", 4);
    setInputValue("Fatigue_Score", 2);
    setInputValue("ACL_Risk_Score", 18);
    setInputValue("Load_Balance_Score", 99);
    setInputValue("Performance_Score", 88);
    setInputValue("Mean_HR", 112);
    setInputValue("Std_HR", 42.0);
    setInputValue("IMU_Peak_Impact", 3.2);
    setInputValue("IMU_SMA", 1.05);
  } else if (name === "fatigued") {
    setInputValue("Training_Hours_Per_Week", 13.5);
    setInputValue("Training_Intensity", 7);
    setInputValue("Recovery_Days_Per_Week", 1);
    setInputValue("Match_Count_Per_Week", 2);
    setInputValue("Rest_Between_Events_Days", 2);
    setInputValue("Fatigue_Score", 7);
    setInputValue("ACL_Risk_Score", 52);
    setInputValue("Load_Balance_Score", 86);
    setInputValue("Performance_Score", 68);
    setInputValue("Mean_HR", 138);
    setInputValue("Std_HR", 28.5);
    setInputValue("IMU_Peak_Impact", 5.2);
    setInputValue("IMU_SMA", 1.48);
  }

  updateTactilePill("hours", document.getElementById("inp-Training_Hours_Per_Week")?.value || 11, "hrs", "Training_Hours_Per_Week", 2, 30);
  updateTactilePill("intensity", document.getElementById("inp-Training_Intensity")?.value || 5, "/10", "Training_Intensity", 1, 10);
  updateTactilePill("fatigue", document.getElementById("inp-Fatigue_Score")?.value || 5, "/10", "Fatigue_Score", 1, 10);
  updateTactilePill("acl", document.getElementById("inp-ACL_Risk_Score")?.value || 45, "/100", "ACL_Risk_Score", 0, 100);
  updateTactilePill("balance", document.getElementById("inp-Load_Balance_Score")?.value || 98, "/100", "Load_Balance_Score", 40, 100);

  updateCompletionMeter();
  recalculatePrediction();
}

function resetToBaselines() {
  const medians = POPULATION_BASELINES.medians;
  for (const [key, val] of Object.entries(medians)) {
    setInputValue(key, val);
  }
  updateTactilePill("hours", medians.Training_Hours_Per_Week, "hrs", "Training_Hours_Per_Week", 2, 30);
  updateTactilePill("intensity", medians.Training_Intensity, "/10", "Training_Intensity", 1, 10);
  updateTactilePill("fatigue", medians.Fatigue_Score, "/10", "Fatigue_Score", 1, 10);
  updateTactilePill("acl", medians.ACL_Risk_Score, "/100", "ACL_Risk_Score", 0, 100);
  updateTactilePill("balance", medians.Load_Balance_Score, "/100", "Load_Balance_Score", 40, 100);

  updateCompletionMeter();
  recalculatePrediction();
}

function setInputValue(key, val) {
  const el = document.getElementById(`inp-${key}`);
  if (el) el.value = val;
}

function getFormInputs() {
  const inputs = {};
  const allInputs = document.querySelectorAll("[id^='inp-']");
  allInputs.forEach(el => {
    const key = el.id.replace("inp-", "");
    if (el.value !== "" && !isNaN(Number(el.value))) {
      inputs[key] = Number(el.value);
    }
  });
  return inputs;
}

/* ==========================================================================
   Master Prediction & Diagnostics
   ========================================================================== */

async function recalculatePrediction() {
  const rawInputs = getFormInputs();
  let result = null;

  try {
    const res = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(rawInputs)
    });
    if (res.ok) {
      result = await res.json();
    }
  } catch (err) {}

  if (!result) {
    result = await predictInjuryRisk(rawInputs);
  }

  currentPrediction = result;
  renderDashboard(result);
  drawRadarChart(result);
  syncSimulatorWithCurrent();
}

function renderDashboard(res) {
  const risk = res.riskScore;
  const triage = res.triage;
  const eng = res.engineered;
  const modelA = res.model_a || { season_risk_pct: 24 };
  const modelC = res.model_c || { expected_sidelined_days: 14.2 };
  const ceiling = res.safe_ceiling || { max_safe_training_hours: 15.2, hours_headroom: 4.2 };

  // 1. Multi-Model Top Strip
  const kpiAcuteVal = document.getElementById("kpi-acute-val");
  const kpiAcuteSub = document.getElementById("kpi-acute-sub");
  if (kpiAcuteVal) {
    kpiAcuteVal.textContent = `${risk}%`;
    kpiAcuteVal.style.color = triage === "HIGH" ? "var(--color-high)" : triage === "MODERATE" ? "var(--color-moderate)" : "var(--color-low)";
  }
  if (kpiAcuteSub) {
    kpiAcuteSub.textContent = triage === "HIGH" ? "High Acute Risk" : triage === "MODERATE" ? "Moderate Risk" : "Low Risk (Cleared)";
    kpiAcuteSub.style.color = kpiAcuteVal.style.color;
  }

  const kpiSeasonVal = document.getElementById("kpi-season-val");
  if (kpiSeasonVal) kpiSeasonVal.textContent = `${modelA.season_risk_pct}%`;

  const kpiDowntimeVal = document.getElementById("kpi-downtime-val");
  if (kpiDowntimeVal) kpiDowntimeVal.textContent = `${modelC.expected_sidelined_days} d`;

  const kpiCeilVal = document.getElementById("kpi-ceiling-val");
  const kpiCeilSub = document.getElementById("kpi-ceiling-sub");
  if (kpiCeilVal) kpiCeilVal.textContent = `${ceiling.max_safe_training_hours} h`;
  if (kpiCeilSub) {
    const hr = ceiling.hours_headroom;
    kpiCeilSub.textContent = hr >= 0 ? `+${hr}h Safe Buffer` : `${hr}h Over Ceiling!`;
    kpiCeilSub.style.color = hr >= 0 ? "var(--color-low)" : "var(--color-high)";
  }

  // 2. Tachometer Dial & Status Gem with Ease-Out Counter
  const gaugeVal = document.getElementById("risk-score-num");
  const gaugeCircle = document.getElementById("gauge-circle");
  const dialGem = document.getElementById("dial-gem");
  const dialZoneTag = document.getElementById("dial-zone-tag");

  if (gaugeVal) {
    animateCounter(gaugeVal, _lastAnimatedRisk, risk, 650);
    _lastAnimatedRisk = risk;
  }
  if (gaugeCircle) {
    const offset = 471 - (risk / 100) * 471;
    gaugeCircle.style.strokeDashoffset = offset;
  }
  if (dialGem) {
    const gemColor = triage === "HIGH" ? "var(--color-high)" : triage === "MODERATE" ? "var(--color-moderate)" : "var(--color-low)";
    dialGem.style.background = gemColor;
    dialGem.style.boxShadow = `0 0 12px ${gemColor}`;
  }
  if (dialZoneTag) {
    if (risk > 40) {
      dialZoneTag.textContent = "ACUTE DELOAD >40%";
      dialZoneTag.style.color = "var(--color-high)";
    } else if (risk >= 25) {
      dialZoneTag.textContent = "MODERATE 25–40%";
      dialZoneTag.style.color = "var(--color-moderate)";
    } else {
      dialZoneTag.textContent = "OPTIMAL LOW <25%";
      dialZoneTag.style.color = "var(--color-low)";
    }
  }

  // 3. Triage Badge
  const badge = document.getElementById("triage-badge");
  const badgeText = document.getElementById("triage-badge-text");
  const desc = document.getElementById("triage-description");
  if (badge && badgeText) {
    badge.className = `triage-badge ${res.triageBadgeClass || 'badge-low'}`;
    badgeText.textContent = triage === "HIGH" ? "High Acute Risk" : triage === "MODERATE" ? "Moderate Risk" : "Low Risk (Cleared)";
  }
  if (desc) {
    desc.textContent = triage === "HIGH"
      ? "Immediate intervention advised. Workload spike or knee laxity exceeds safety threshold."
      : triage === "MODERATE"
      ? "Elevated workload / fatigue detected. Monitor micro-cycle closely."
      : "Athlete is within optimal chronic adaptation zone with healthy balance and recovery buffers.";
  }

  // 4. Metrics Strip
  const acwrEl = document.getElementById("metric-acwr");
  const acwrSub = document.getElementById("metric-acwr-sub");
  const loadEl = document.getElementById("metric-load");
  const defEl = document.getElementById("metric-deficit");
  if (acwrEl) acwrEl.textContent = eng.ACWR ? eng.ACWR.toFixed(2) : "1.07";
  if (acwrSub) {
    if (eng.ACWR > 1.35) {
      acwrSub.textContent = "Danger Zone (> 1.35)";
      acwrSub.style.color = "var(--color-high)";
    } else if (eng.ACWR < 0.8) {
      acwrSub.textContent = "Under-training (< 0.8)";
      acwrSub.style.color = "var(--color-moderate)";
    } else {
      acwrSub.textContent = "Optimal (0.8–1.3)";
      acwrSub.style.color = "var(--color-low)";
    }
  }
  if (loadEl) loadEl.textContent = eng.Weekly_Load ? eng.Weekly_Load.toFixed(1) : "57.4";
  if (defEl) defEl.textContent = eng.Recovery_Deficit ? eng.Recovery_Deficit.toFixed(2) : "1.67";

  // 5. SHAP Diverging Waterfall
  renderSHAPWaterfall(res.attributions || []);

  // 6. Clinical Recommendations
  const recsContainer = document.getElementById("recs-container");
  if (recsContainer) {
    recsContainer.innerHTML = "";
    (res.recommendations || []).forEach(r => {
      const card = document.createElement("div");
      card.className = `rec-card ${r.severity || 'warning'}`;
      card.innerHTML = `
        <div class="rec-header">
          <span class="rec-category">${r.category}</span>
        </div>
        <div class="rec-title">${r.title}</div>
        <div class="rec-action">${r.action}</div>
      `;
      recsContainer.appendChild(card);
    });
  }
}



/* ==========================================================================
   SHAP Diverging Waterfall
   ========================================================================== */

function renderSHAPWaterfall(attributions) {
  const container = document.getElementById("waterfall-rows");
  if (!container) return;
  container.innerHTML = "";

  const sorted = [...attributions].sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution)).slice(0, 7);

  sorted.forEach(item => {
    const isRisk = item.contribution > 0;
    const mag = Math.min(100, Math.abs(item.contribution) * 180);
    const widthPct = Math.max(8, mag);
    const pctDelta = Math.round(Math.abs(item.contribution) * 100);
    const impactTag = isRisk ? `+${pctDelta}% Acute Stress Spike` : `-${pctDelta}% Neuromuscular Buffer`;

    const row = document.createElement("div");
    row.style.cssText = "display: grid; grid-template-columns: 145px 1fr 65px; align-items: center; gap: 0.85rem; margin-bottom: 0.75rem; font-size: 0.78rem;";
    row.innerHTML = `
      <div>
        <div style="font-weight: 800; color: var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${item.label}">
          ${item.label}
        </div>
        <div class="shap-clinical-badge ${isRisk ? 'risk' : 'protective'}">
          ${impactTag}
        </div>
      </div>
      <div style="height: 18px; background: #E2E8F0; border-radius: 9999px; position: relative; overflow: hidden; display: flex; align-items: center; box-shadow: inset 0 1px 2px rgba(0,0,0,0.06);">
        <!-- Population Datum Center Line (-1.2 log-odds) -->
        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 2px; background: #64748B; z-index: 3;" title="Collegiate Baseline Median (-1.2)"></div>
        <div style="height: 100%; border-radius: 9999px; position: absolute; transition: width 450ms cubic-bezier(0.16, 1, 0.3, 1); ${isRisk ? 'left: 50%; background: linear-gradient(90deg, #F87171, #EF4444); box-shadow: 0 0 8px rgba(239,68,68,0.4);' : 'right: 50%; background: linear-gradient(90deg, #10B981, #059669); box-shadow: 0 0 8px rgba(16,185,129,0.4);'} width: ${widthPct * 0.45}%;"></div>
      </div>
      <div style="font-family: var(--font-mono); font-weight: 800; text-align: right; color: ${isRisk ? 'var(--color-high)' : 'var(--color-low)'}; font-size: 0.82rem;">
        ${isRisk ? '+' : '−'}${Math.abs(item.contribution).toFixed(2)}
      </div>
    `;
    container.appendChild(row);
  });
}

/* ==========================================================================
   6-Axis Spider / Radar Diagram
   ========================================================================== */

function drawRadarChart(res) {
  const canvas = document.getElementById("radar-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  const cx = w / 2, cy = h / 2 + 10;
  const r = Math.min(cx, cy) - 38;
  const eng = res.engineered || {};

  const axes = [
    { label: "Bilateral Balance", val: Math.min(100, (eng.Load_Balance_Score || 90)), bench: 95 },
    { label: "Knee Stability", val: Math.max(10, 100 - (eng.ACL_Risk_Score || 45)), bench: 80 },
    { label: "Recovery Buffer", val: Math.max(10, 100 - (eng.Recovery_Deficit || 2) * 25), bench: 75 },
    { label: "Workload Tolerance", val: Math.min(100, ((eng.Estimated_Chronic_Load || 50) / 75) * 100), bench: 85 },
    { label: "Cardio Resilience", val: Math.min(100, ((eng.Std_HR || 35) / 50) * 100), bench: 70 },
    { label: "Impact Cushioning", val: Math.max(10, 100 - ((eng.IMU_Peak_Impact || 4.5) / 8.0) * 100), bench: 80 }
  ];

  const total = axes.length;
  const angleStep = (Math.PI * 2) / total;

  // Background Webs
  ctx.strokeStyle = "#E2E8F0";
  ctx.lineWidth = 1;
  for (let level = 1; level <= 4; level++) {
    const curR = (r / 4) * level;
    ctx.beginPath();
    for (let i = 0; i < total; i++) {
      const angle = i * angleStep - Math.PI / 2;
      const x = cx + curR * Math.cos(angle);
      const y = cy + curR * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
  }

  // Labels
  ctx.fillStyle = "#64748B";
  ctx.font = "10px Plus Jakarta Sans, sans-serif";
  ctx.textAlign = "center";
  for (let i = 0; i < total; i++) {
    const angle = i * angleStep - Math.PI / 2;
    const x = cx + r * Math.cos(angle);
    const y = cy + r * Math.sin(angle);
    ctx.beginPath();
    ctx.moveTo(cx, cy); ctx.lineTo(x, y); ctx.stroke();

    const lx = cx + (r + 18) * Math.cos(angle);
    const ly = cy + (r + 16) * Math.sin(angle);
    ctx.fillText(axes[i].label, lx, ly);
  }

  // Benchmark Polygon
  ctx.strokeStyle = "rgba(148, 163, 184, 0.6)";
  ctx.fillStyle = "rgba(148, 163, 184, 0.15)";
  ctx.lineWidth = 1.5;
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  for (let i = 0; i < total; i++) {
    const angle = i * angleStep - Math.PI / 2;
    const score = axes[i].bench / 100;
    const x = cx + r * score * Math.cos(angle);
    const y = cy + r * score * Math.sin(angle);
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.stroke();
  ctx.fill();
  ctx.setLineDash([]);

  // Athlete Polygon
  ctx.strokeStyle = "#0284C7";
  ctx.fillStyle = "rgba(2, 132, 199, 0.25)";
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  for (let i = 0; i < total; i++) {
    const angle = i * angleStep - Math.PI / 2;
    const score = Math.max(0.1, Math.min(1.0, axes[i].val / 100));
    const x = cx + r * score * Math.cos(angle);
    const y = cy + r * score * Math.sin(angle);
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.stroke();
  ctx.fill();
}

/* ==========================================================================
   WORKSPACE 2: 2D SCATTER MATRIX & WHAT-IF SIMULATOR
   ========================================================================== */

function syncSimulatorWithCurrent() {
  const hours = Number(document.getElementById("inp-Training_Hours_Per_Week")?.value || 11);
  const rec = Number(document.getElementById("inp-Recovery_Days_Per_Week")?.value || 2);
  const intensity = Number(document.getElementById("inp-Training_Intensity")?.value || 5);
  const fatigue = Number(document.getElementById("inp-Fatigue_Score")?.value || 5);

  setSimSlider("hours", hours);
  setSimSlider("recovery", rec);
  setSimSlider("intensity", intensity);
  setSimSlider("fatigue", fatigue);

  runSimulation();
}

function setSimSlider(id, val) {
  const el = document.getElementById(`sim-slider-${id}`);
  if (el) el.value = val;
}

async function runSimulation() {
  const simHours = Number(document.getElementById("sim-slider-hours")?.value || 11);
  const simRec = Number(document.getElementById("sim-slider-recovery")?.value || 2);
  const simIntensity = Number(document.getElementById("sim-slider-intensity")?.value || 5);
  const simFatigue = Number(document.getElementById("sim-slider-fatigue")?.value || 5);

  document.getElementById("sim-hours-val").textContent = `${simHours} hrs`;
  document.getElementById("sim-recovery-val").textContent = `${simRec} days`;
  document.getElementById("sim-intensity-val").textContent = `${simIntensity} / 10`;
  document.getElementById("sim-fatigue-val").textContent = `${simFatigue} / 10`;

  const simInputs = {
    ...getFormInputs(),
    Training_Hours_Per_Week: simHours,
    Recovery_Days_Per_Week: simRec,
    Training_Intensity: simIntensity,
    Fatigue_Score: simFatigue
  };

  const simResult = await predictInjuryRisk(simInputs);
  const baselineRisk = currentPrediction?.riskScore || 12;
  const simRisk = simResult.riskScore;
  const delta = simRisk - baselineRisk;

  const resRiskEl = document.getElementById("sim-result-risk");
  const deltaBadge = document.getElementById("sim-delta-badge");

  if (resRiskEl) {
    resRiskEl.textContent = `${simRisk}%`;
    resRiskEl.style.color = simResult.triage === "HIGH" ? "var(--color-high)" : simResult.triage === "MODERATE" ? "var(--color-moderate)" : "var(--color-low)";
  }

  if (deltaBadge) {
    if (delta < 0) {
      deltaBadge.className = "delta-pill good";
      deltaBadge.textContent = `${delta}% Risk Drop (Safer)`;
    } else if (delta > 0) {
      deltaBadge.className = "delta-pill bad";
      deltaBadge.textContent = `+${delta}% Risk Increase!`;
    } else {
      deltaBadge.className = "delta-pill good";
      deltaBadge.textContent = `Baseline Match`;
    }
  }

  document.getElementById("sim-result-acwr").textContent = simResult.engineered.ACWR.toFixed(2);
  const daysDiff = (currentPrediction?.model_c?.expected_sidelined_days || 14) - simResult.model_c.expected_sidelined_days;
  const daysSavedEl = document.getElementById("sim-result-days-saved");
  if (daysSavedEl) {
    daysSavedEl.textContent = daysDiff >= 0 ? `+${daysDiff.toFixed(1)} d` : `${daysDiff.toFixed(1)} d`;
    daysSavedEl.style.color = daysDiff >= 0 ? "var(--color-low)" : "var(--color-high)";
  }

  // Update 2D Quad-Matrix with Trajectory Vector Arrow
  updateScatterMatrix(currentPrediction?.engineered || {}, simResult.engineered);
}

function updateScatterMatrix(curEng, simEng) {
  const box = document.getElementById("scatter-matrix-box");
  const nodeCur = document.getElementById("matrix-node-current");
  const nodeSim = document.getElementById("matrix-node-simulated");
  const vectorLine = document.getElementById("matrix-vector-line");
  const deltaBadge = document.getElementById("sim-delta-badge");
  if (!box || !nodeCur || !nodeSim || !vectorLine) return;

  const w = box.clientWidth || 400;
  const h = box.clientHeight || 330;

  // X-axis: Accumulated Acute Fatigue (Fatigue 1..10 -> 12%..88%)
  const curX = Math.max(12, Math.min(88, ((curEng.Fatigue_Score || 5) / 10) * 100));
  const simX = Math.max(12, Math.min(88, ((simEng.Fatigue_Score || 5) / 10) * 100));

  // Y-axis: Chronic Adaptive Buffer (Buffer balance: inverted ACWR & Recovery days -> 88%..12%)
  const curBuff = ((curEng.Recovery_Days_Per_Week || 2) * 12) + (100 - (curEng.ACWR || 1.0) * 45);
  const simBuff = ((simEng.Recovery_Days_Per_Week || 2) * 12) + (100 - (simEng.ACWR || 1.0) * 45);

  const curY = Math.max(14, Math.min(86, 100 - (curBuff / 140) * 100));
  const simY = Math.max(14, Math.min(86, 100 - (simBuff / 140) * 100));

  nodeCur.style.left = `${curX}%`;
  nodeCur.style.top = `${curY}%`;
  nodeSim.style.left = `${simX}%`;
  nodeSim.style.top = `${simY}%`;

  // Draw directed SVG vector line
  const px1 = (curX / 100) * w;
  const py1 = (curY / 100) * h;
  const px2 = (simX / 100) * w;
  const py2 = (simY / 100) * h;

  vectorLine.setAttribute("x1", px1);
  vectorLine.setAttribute("y1", py1);
  vectorLine.setAttribute("x2", px2);
  vectorLine.setAttribute("y2", py2);

  // Trajectory direction tag
  if (deltaBadge) {
    const curRisk = currentPrediction?.riskScore || 12;
    const simRisk = Number(document.getElementById("sim-result-risk")?.textContent?.replace("%", "") || curRisk);
    const delta = simRisk - curRisk;

    if (simX <= 45 && simY <= 50) {
      deltaBadge.className = "delta-pill good";
      deltaBadge.innerHTML = `⚡ In Supercompensation Sweet Spot (${delta <= 0 ? delta : '+' + delta}% Risk)`;
    } else if (simX > 60 || simY > 60) {
      deltaBadge.className = "delta-pill danger";
      deltaBadge.innerHTML = `⚠️ Trajectory Heading into Dangerous Overload (${delta >= 0 ? '+' + delta : delta}%)`;
    } else if (delta < 0) {
      deltaBadge.className = "delta-pill good";
      deltaBadge.innerHTML = `✓ Safe Load Adaptation (${delta}% Risk Drop)`;
    } else {
      deltaBadge.className = "delta-pill warn";
      deltaBadge.innerHTML = `Caution Zone (+${delta}% Risk Surge)`;
    }
  }
}

/* ==========================================================================
   WORKSPACE 3: OSCILLOSCOPE WAVEFORM STUDIO WITH SCRUBBING
   ========================================================================== */

async function initWaveforms() {
  await loadSampleWaveform("imu");
}

async function loadSampleWaveform(type) {
  try {
    const res = await fetch(`/api/timeseries-sample/${type}`);
    if (res.ok) {
      const data = await res.json();
      if (type === "imu") sampleIMUData = data;
      drawWaveforms();
    }
  } catch (err) {}
}

function drawWaveforms() {
  const canvas = document.getElementById("imu-waveform-canvas");
  if (!canvas || !sampleIMUData) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  const n = sampleIMUData.magnitude.length;
  const step = w / (n - 1);
  const midY = h / 2;
  const scale = 38;

  // 1. Telemetry Scope Grid Lines
  ctx.strokeStyle = "rgba(56, 189, 248, 0.08)";
  ctx.lineWidth = 1;
  ctx.beginPath();
  for (let y = 0; y <= h; y += 30) {
    ctx.moveTo(0, y); ctx.lineTo(w, y);
  }
  for (let x = 0; x <= w; x += 50) {
    ctx.moveTo(x, 0); ctx.lineTo(x, h);
  }
  ctx.stroke();

  // Center Zero-G Reference Datum
  ctx.strokeStyle = "rgba(56, 189, 248, 0.25)";
  ctx.lineWidth = 1.2;
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(0, midY); ctx.lineTo(w, midY);
  ctx.stroke();
  ctx.setLineDash([]);

  // 2. Raw 3-Axis Multi-Trace Overlay
  // Acc X (Sky Blue)
  ctx.strokeStyle = "rgba(56, 189, 248, 0.45)";
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  for (let i = 0; i < n; i++) {
    const idx = (i + streamOffset) % n;
    const ax = sampleIMUData.acc_x ? sampleIMUData.acc_x[idx] : Math.sin(idx * 0.1) * 0.8;
    const x = i * step;
    const y = midY - ax * scale;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.stroke();

  // Acc Y (Violet)
  ctx.strokeStyle = "rgba(167, 139, 250, 0.45)";
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  for (let i = 0; i < n; i++) {
    const idx = (i + streamOffset) % n;
    const ay = sampleIMUData.acc_y ? sampleIMUData.acc_y[idx] : Math.cos(idx * 0.1) * 0.9;
    const x = i * step;
    const y = midY - ay * scale;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.stroke();

  // 3. Butterworth 4th-Order Low-Pass Envelope (Amber Gold)
  ctx.strokeStyle = "#FBBF24";
  ctx.lineWidth = 2.8;
  ctx.shadowColor = "rgba(251, 191, 36, 0.5)";
  ctx.shadowBlur = 8;
  ctx.beginPath();
  for (let i = 0; i < n; i++) {
    const idx = (i + streamOffset) % n;
    const x = i * step;
    const y = midY - sampleIMUData.filtered[idx] * scale;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.stroke();
  ctx.shadowBlur = 0;

  // 4. Ground Impact Peaks & Expanding Concentric Shockwave Rings (> 4.5g / 5.5g)
  const animTime = (Date.now() / 25) % 30; // Expanding ring animation factor
  sampleIMUData.peak_indices.forEach(idx => {
    const dispIdx = (idx - streamOffset + n) % n;
    if (dispIdx >= 0 && dispIdx < n) {
      const x = dispIdx * step;
      const y = midY - sampleIMUData.filtered[idx] * scale;
      const peakVal = sampleIMUData.filtered[idx];
      const isSevere = peakVal >= 4.5;

      if (isSevere) {
        // Expanding Concentric Shock Rings
        const r1 = 8 + (animTime % 18);
        const alpha1 = Math.max(0, 1 - r1 / 26);
        ctx.strokeStyle = `rgba(239, 68, 68, ${alpha1 * 0.8})`;
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        ctx.arc(x, y, r1, 0, Math.PI * 2);
        ctx.stroke();

        const r2 = 4 + ((animTime + 8) % 18);
        const alpha2 = Math.max(0, 1 - r2 / 24);
        ctx.strokeStyle = `rgba(245, 158, 11, ${alpha2 * 0.6})`;
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.arc(x, y, r2, 0, Math.PI * 2);
        ctx.stroke();
      }

      // Solid Peak Core
      ctx.fillStyle = isSevere ? "#EF4444" : "#F59E0B";
      ctx.beginPath();
      ctx.arc(x, y, 4.5, 0, Math.PI * 2);
      ctx.fill();
    }
  });
}

function handleOscilloscopeHover(e) {
  const box = document.getElementById("oscilloscope-box");
  const scanline = document.getElementById("oscilloscope-scanline");
  const hud = document.getElementById("oscilloscope-hud");
  if (!box || !scanline || !hud || !sampleIMUData) return;

  const rect = box.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const pct = Math.max(0, Math.min(1, x / rect.width));

  scanline.style.display = "block";
  scanline.style.left = `${x}px`;

  const n = sampleIMUData.magnitude.length;
  const idx = Math.floor(pct * (n - 1));
  const time = (idx / 50.0).toFixed(2);
  const mag = sampleIMUData.filtered[idx] || 1.2;
  const ax = sampleIMUData.acc_x ? sampleIMUData.acc_x[idx].toFixed(2) : (Math.sin(idx * 0.1) * 0.8).toFixed(2);
  const ay = sampleIMUData.acc_y ? sampleIMUData.acc_y[idx].toFixed(2) : (Math.cos(idx * 0.1) * 0.9).toFixed(2);
  const az = sampleIMUData.acc_z ? sampleIMUData.acc_z[idx].toFixed(2) : (1.0 + Math.sin(idx * 0.2) * 0.5).toFixed(2);
  const cadence = Math.round(155 + Math.sin(idx * 0.15) * 18);
  const isShock = mag >= 4.5;

  hud.innerHTML = `
    <span>T+${time}s</span> &bull; 
    <span>ACC X: ${ax}g</span> | <span>Y: ${ay}g</span> | <span>Z: ${az}g</span> &bull; 
    <span>CADENCE: ${cadence} spm</span> &bull; 
    <span style="color: ${isShock ? '#EF4444' : '#10B981'}; font-weight: 800;">
      ${isShock ? '🚨 IMPACT PEAK (' + mag.toFixed(2) + 'G)' : 'MAG: ' + mag.toFixed(2) + 'G'}
    </span>
  `;
}

function hideOscilloscopeScanline() {
  const scanline = document.getElementById("oscilloscope-scanline");
  if (scanline) scanline.style.display = "none";
}

function toggleStreamSimulation() {
  const btn = document.getElementById("btn-play-stream");
  isStreamSimulating = !isStreamSimulating;

  if (isStreamSimulating) {
    btn.textContent = "⏸ Pause Sensor Stream";
    simulateStreamLoop();
  } else {
    btn.textContent = "▶ Replay Sensor Stream";
    cancelAnimationFrame(streamAnimationId);
  }
}

function simulateStreamLoop() {
  streamOffset = (streamOffset + 1) % (sampleIMUData?.magnitude?.length || 100);
  drawWaveforms();
  streamAnimationId = requestAnimationFrame(simulateStreamLoop);
}

/* ==========================================================================
   WORKSPACE 4: STADIUM-GRADE TACTICAL PITCH WITH FORMATIONS
   ========================================================================== */

const SQUAD_PLAYERS = [
  { id: 1, name: "Alisson (GK)", role: "GK", risk: 8, acwr: 0.95, fatigue: 3, shock: 3.2 },
  { id: 2, name: "Robertson (LB)", role: "LB", risk: 62, acwr: 1.38, fatigue: 7, shock: 6.4 },
  { id: 3, name: "Van Dijk (CB)", role: "CB1", risk: 48, acwr: 1.15, fatigue: 6, shock: 4.8 },
  { id: 4, name: "Konate (CB)", role: "CB2", risk: 64, acwr: 1.42, fatigue: 8, shock: 6.8 },
  { id: 5, name: "Trent (RB)", role: "RB", risk: 58, acwr: 1.32, fatigue: 7, shock: 5.9 },
  { id: 6, name: "Mac Allister (CM)", role: "CM1", risk: 28, acwr: 1.05, fatigue: 4, shock: 4.2 },
  { id: 7, name: "Szoboszlai (CM)", role: "CM2", risk: 36, acwr: 1.12, fatigue: 5, shock: 4.6 },
  { id: 8, name: "Elliott (CAM)", role: "CAM", risk: 32, acwr: 1.08, fatigue: 4, shock: 4.1 },
  { id: 9, name: "Diaz (LW)", role: "LW", risk: 22, acwr: 0.98, fatigue: 3, shock: 3.8 },
  { id: 10, name: "Nunez (ST)", role: "ST", risk: 78, acwr: 1.45, fatigue: 8, shock: 7.2 },
  { id: 11, name: "Salah (RW)", role: "RW", risk: 16, acwr: 0.92, fatigue: 2, shock: 3.5 }
];

const FORMATION_COORDS = {
  "4-3-3": [
    { x: 10, y: 50 }, { x: 26, y: 16 }, { x: 24, y: 38 }, { x: 24, y: 62 }, { x: 26, y: 84 },
    { x: 48, y: 32 }, { x: 48, y: 68 }, { x: 62, y: 50 },
    { x: 78, y: 20 }, { x: 86, y: 50 }, { x: 78, y: 80 }
  ],
  "4-2-3-1": [
    { x: 10, y: 50 }, { x: 26, y: 16 }, { x: 24, y: 38 }, { x: 24, y: 62 }, { x: 26, y: 84 },
    { x: 44, y: 36 }, { x: 44, y: 64 }, { x: 64, y: 50 },
    { x: 74, y: 22 }, { x: 86, y: 50 }, { x: 74, y: 78 }
  ],
  "3-5-2": [
    { x: 10, y: 50 }, { x: 24, y: 30 }, { x: 22, y: 50 }, { x: 24, y: 70 }, { x: 48, y: 14 },
    { x: 48, y: 38 }, { x: 48, y: 62 }, { x: 48, y: 86 },
    { x: 65, y: 50 }, { x: 84, y: 38 }, { x: 84, y: 62 }
  ],
  "5-out": [
    { x: 15, y: 50 }, { x: 35, y: 25 }, { x: 35, y: 75 }, { x: 65, y: 20 }, { x: 65, y: 80 },
    { x: 50, y: 40 }, { x: 50, y: 60 }, { x: 55, y: 50 },
    { x: 80, y: 30 }, { x: 85, y: 50 }, { x: 80, y: 70 }
  ]
};

function changeTacticalFormation(formation) {
  renderTacticalPitch(formation);
}

function renderTacticalPitch(formationName) {
  const container = document.getElementById("tactical-pitch-tokens") || document.getElementById("tactical-pitch-field");
  if (!container) return;
  container.innerHTML = "";

  const coords = FORMATION_COORDS[formationName] || FORMATION_COORDS["4-3-3"];

  SQUAD_PLAYERS.forEach((p, idx) => {
    const c = coords[idx] || { x: 50, y: 50 };
    const node = document.createElement("div");
    node.className = "pitch-card-token";
    node.style.left = `${c.x}%`;
    node.style.top = `${c.y}%`;

    const riskClass = p.risk >= 50 ? "high" : p.risk >= 25 ? "mod" : "low";

    node.innerHTML = `
      <div class="token-circle ${riskClass}">
        ${p.id}
      </div>
      <div class="token-name-tag">
        <span>${p.name.split(' ')[0]}</span>
        <span style="color: ${p.risk >= 50 ? '#EF4444' : p.risk >= 25 ? '#F59E0B' : '#10B981'}; font-weight: 800;">${p.risk}%</span>
      </div>
      <div class="token-sparkline-bar">
        <div class="spark-dot" style="background: ${p.acwr > 1.35 ? '#EF4444' : p.acwr < 0.8 ? '#F59E0B' : '#10B981'};" title="ACWR: ${p.acwr}"></div>
        <div class="spark-dot" style="background: ${p.fatigue >= 7 ? '#EF4444' : p.fatigue >= 5 ? '#F59E0B' : '#10B981'};" title="Fatigue: ${p.fatigue}/10"></div>
        <div class="spark-dot" style="background: ${p.shock > 5.5 ? '#EF4444' : '#10B981'};" title="Shock: ${p.shock}g"></div>
      </div>
    `;

    node.onclick = () => openPitchAthleteDrawer(p);
    container.appendChild(node);
  });
}

function openPitchAthleteDrawer(player) {
  const drawer = document.getElementById("pitch-athlete-drawer");
  const backdrop = document.getElementById("pitch-drawer-backdrop");
  const nameEl = document.getElementById("drawer-player-name");
  const posEl = document.getElementById("drawer-player-pos");
  const content = document.getElementById("drawer-content");
  if (!drawer || !backdrop) return;

  nameEl.textContent = player.name;
  posEl.textContent = `Squad #${player.id} • ${player.role}`;

  content.innerHTML = `
    <div style="text-align: center; margin-bottom: 1.5rem;">
      <div class="triage-badge ${player.risk >= 50 ? 'badge-high' : player.risk >= 25 ? 'badge-moderate' : 'badge-low'}" style="font-size: 0.95rem; padding: 0.45rem 1.15rem;">
        ${player.risk >= 50 ? 'HIGH RISK' : player.risk >= 25 ? 'MODERATE RISK' : 'LOW RISK'} (${player.risk}%)
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1.5rem;">
      <div class="metric-box">
        <div class="metric-title">ACWR Ratio</div>
        <div class="metric-val" style="color: ${player.acwr > 1.3 ? 'var(--color-high)' : 'var(--color-low)'};">${player.acwr}</div>
      </div>
      <div class="metric-box">
        <div class="metric-title">Ground Impact</div>
        <div class="metric-val" style="color: ${player.shock > 6.0 ? 'var(--color-high)' : 'var(--color-low)'};">${player.shock} g</div>
      </div>
    </div>

    <div style="margin-bottom: 1.5rem;">
      <button class="btn btn-primary" style="width: 100%; justify-content: center;" onclick="loadPlayerToDiagnostics('${player.name}', ${player.risk})">
        Load Full Profile to Diagnostics →
      </button>
    </div>
  `;

  drawer.classList.add("open");
  backdrop.classList.add("open");
}

function closePitchDrawer() {
  document.getElementById("pitch-athlete-drawer")?.classList.remove("open");
  document.getElementById("pitch-drawer-backdrop")?.classList.remove("open");
}

function loadPlayerToDiagnostics(name, risk) {
  closePitchDrawer();
  if (risk >= 50) applyPreset("overworked");
  else if (risk >= 25) applyPreset("fatigued");
  else applyPreset("rested");
  switchMainTab("questionnaire");
}

/* ==========================================================================
   WORKSPACE 5: MICRO-CYCLE ACWR TRACKER
   ========================================================================== */

function loadStoredHistory() {
  const stored = localStorage.getItem("athleteshield_microcycles");
  if (stored) {
    try { longitudinalHistory = JSON.parse(stored); } catch(e) {}
  }

  if (!longitudinalHistory || longitudinalHistory.length === 0) {
    longitudinalHistory = [
      { week: "Week 1", load: 52, chronic: 54, acwr: 0.96, fatigue: 3, risk: 10, status: "Low" },
      { week: "Week 2", load: 58, chronic: 55, acwr: 1.05, fatigue: 4, risk: 14, status: "Low" },
      { week: "Week 3", load: 68, chronic: 58, acwr: 1.17, fatigue: 5, risk: 22, status: "Low" },
      { week: "Week 4", load: 84, chronic: 62, acwr: 1.35, fatigue: 7, risk: 42, status: "High" },
      { week: "Week 5", load: 60, chronic: 60, acwr: 1.00, fatigue: 4, risk: 16, status: "Low" }
    ];
  }
  renderHistoryTable();
}

function logCurrentWeekSession() {
  if (!currentPrediction) return;
  const eng = currentPrediction.engineered;
  const nextWeekNum = longitudinalHistory.length + 1;

  const entry = {
    week: `Week ${nextWeekNum}`,
    load: Math.round(eng.Weekly_Load),
    chronic: Math.round(eng.Estimated_Chronic_Load),
    acwr: Number(eng.ACWR.toFixed(2)),
    fatigue: eng.Fatigue_Score,
    risk: currentPrediction.riskScore,
    status: currentPrediction.triage
  };

  longitudinalHistory.push(entry);
  localStorage.setItem("athleteshield_microcycles", JSON.stringify(longitudinalHistory));
  renderHistoryTable();
  drawACWRTrendChart();
}

function renderHistoryTable() {
  const tbody = document.getElementById("history-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  longitudinalHistory.forEach(h => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${h.week}</strong></td>
      <td>${h.load} AU</td>
      <td>${h.chronic} AU</td>
      <td><strong style="color: ${h.acwr > 1.35 ? 'var(--color-high)' : 'var(--color-low)'};">${h.acwr}</strong></td>
      <td>${h.fatigue} / 10</td>
      <td><span class="triage-badge ${h.status === 'HIGH' || h.risk >= 40 ? 'badge-high' : 'badge-low'}">${h.status} (${h.risk}%)</span></td>
      <td><button class="btn btn-outline" style="padding: 0.2rem 0.5rem; font-size: 0.72rem;" onclick="loadHistoryWeek('${h.week}')">Review</button></td>
    `;
    tbody.appendChild(tr);
  });
}

function drawACWRTrendChart() {
  const canvas = document.getElementById("acwr-trend-canvas");
  if (!canvas || longitudinalHistory.length < 2) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  const n = longitudinalHistory.length;
  const step = w / (n - 1);
  const minVal = 0.5, maxVal = 1.8;

  // Sweet Spot Corridor
  const ySweetTop = h - ((1.3 - minVal) / (maxVal - minVal)) * h;
  const ySweetBot = h - ((0.8 - minVal) / (maxVal - minVal)) * h;
  ctx.fillStyle = "rgba(16, 185, 129, 0.12)";
  ctx.fillRect(0, ySweetTop, w, ySweetBot - ySweetTop);

  // Danger Spike
  const yDanger = h - ((1.35 - minVal) / (maxVal - minVal)) * h;
  ctx.fillStyle = "rgba(225, 29, 72, 0.08)";
  ctx.fillRect(0, 0, w, yDanger);

  // Corridor guideline labels
  ctx.fillStyle = "#059669";
  ctx.font = "10px Plus Jakarta Sans";
  ctx.fillText("Sweet Spot (1.30)", 15, ySweetTop + 14);
  ctx.fillStyle = "#E11D48";
  ctx.fillText("Danger Barrier (1.35)", 15, yDanger - 6);

  // Line Chart
  ctx.strokeStyle = "#0284C7";
  ctx.lineWidth = 3.5;
  ctx.beginPath();
  for (let i = 0; i < n; i++) {
    const val = longitudinalHistory[i].acwr;
    const x = i * step;
    const y = h - ((val - minVal) / (maxVal - minVal)) * h;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.stroke();

  // Nodes & Week Labels
  for (let i = 0; i < n; i++) {
    const val = longitudinalHistory[i].acwr;
    const x = i * step;
    const y = h - ((val - minVal) / (maxVal - minVal)) * h;
    ctx.fillStyle = val > 1.35 ? "#E11D48" : "#0284C7";
    ctx.beginPath();
    ctx.arc(x, y, 6, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#0F172A";
    ctx.font = "bold 11px Plus Jakarta Sans";
    ctx.textAlign = "center";
    ctx.fillText(`${val}`, x, y - 10);
    ctx.fillText(longitudinalHistory[i].week, x, h - 8);
  }
}

function loadHistoryWeek(weekName) {
  const match = longitudinalHistory.find(h => h.week === weekName);
  if (!match) return;
  setInputValue("Training_Hours_Per_Week", Math.round(match.load / 5));
  setInputValue("Fatigue_Score", match.fatigue);
  recalculatePrediction();
  switchMainTab("questionnaire");
}

/* ==========================================================================
   WORKSPACE 6: CSV INGESTION
   ========================================================================== */

function setupDragAndDrop() {
  const dropzone = document.getElementById("csv-dropzone");
  if (!dropzone) return;

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, e => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, e => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
    }, false);
  });

  dropzone.addEventListener('drop', e => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) processCSVFile(files[0]);
  });
}

function handleFileSelect(e) {
  const files = e.target.files;
  if (files.length > 0) processCSVFile(files[0]);
}

async function processCSVFile(file) {
  showCSVStatus(`Reading and parsing "${file.name}"...`, "info");

  try {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch("/api/upload-csv", { method: "POST", body: formData });
    if (res.ok) {
      const data = await res.json();
      handleParsedCSVResponse(data, file.name);
      return;
    }
  } catch (err) {}

  const reader = new FileReader();
  reader.onload = async (e) => {
    const rows = parseCSVText(e.target.result);
    if (!rows || rows.length === 0) return;
    const keys = Object.keys(rows[0]);

    if (keys.some(k => k.includes("userAcceleration") || k.includes("acc_x"))) {
      const imuFeats = processIMUTimeseries(rows);
      if (imuFeats) {
        populateExtractedFeatures(imuFeats, 4);
        showCSVStatus(`Extracted IMU biomechanics from ${rows.length} rows. Populated in Step 4.`, "success");
      }
    } else {
      batchAthletesData = [];
      for (let i = 0; i < rows.length; i++) {
        const r = rows[i];
        const pred = await predictInjuryRisk(r);
        batchAthletesData.push({
          athlete_id: r.Athlete_ID || `Athlete-${i + 1}`,
          position: r.Position || "Forward",
          risk_score: pred.riskScore,
          season_risk_pct: pred.model_a?.season_risk_pct || 25,
          sidelined_days: pred.model_c?.expected_sidelined_days || 14,
          triage: pred.triage,
          triageBadgeClass: pred.triageBadgeClass,
          acwr: Number(pred.engineered.ACWR.toFixed(2)),
          top_driver: pred.topRiskDrivers[0]?.label || "Balanced",
          raw_data: r,
          full_prediction: pred
        });
      }
      renderBatchRosterTable(batchAthletesData);
      showCSVStatus(`Batch evaluated ${batchAthletesData.length} athletes.`, "success");
    }
  };
  reader.readAsText(file);
}

function handleParsedCSVResponse(data, fileName) {
  if (data.type === "imu_telemetry") {
    populateExtractedFeatures(data.features, 4);
    showCSVStatus(data.message + " — Populated in Step 4.", "success");
  } else if (data.type === "wearable_telemetry") {
    populateExtractedFeatures(data.features, 3);
    showCSVStatus(data.message + " — Populated in Step 3.", "success");
  } else if (data.type === "batch_roster") {
    batchAthletesData = data.athletes;
    renderBatchRosterTable(data.athletes);
    showCSVStatus(data.message, "success");
  }
}

function populateExtractedFeatures(feats, targetStep) {
  for (const [key, val] of Object.entries(feats)) {
    setInputValue(key, val);
  }
  recalculatePrediction();
  switchMainTab("questionnaire");
  switchStep(targetStep);
}

function showCSVStatus(msg, type) {
  const banner = document.getElementById("csv-status-banner");
  if (!banner) return;
  banner.style.display = "block";
  banner.textContent = msg;
  banner.style.backgroundColor = type === "success" ? "var(--color-low-bg)" : "var(--primary-subtle)";
  banner.style.color = type === "success" ? "#065F46" : "var(--primary)";
}

function renderBatchRosterTable(athletes) {
  const area = document.getElementById("batch-results-area");
  const tbody = document.getElementById("batch-table-body");
  if (!area || !tbody) return;

  area.style.display = "block";
  tbody.innerHTML = "";

  athletes.forEach((ath, idx) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${ath.athlete_id}</strong></td>
      <td>${ath.position}</td>
      <td><strong>${ath.risk_score}%</strong></td>
      <td>${ath.season_risk_pct || 24}%</td>
      <td>${ath.sidelined_days || 14} d</td>
      <td><span class="triage-badge ${ath.triageBadgeClass}">${ath.triage}</span></td>
      <td>${ath.acwr}</td>
      <td>${ath.top_driver}</td>
      <td>
        <button class="btn btn-outline" style="padding: 0.2rem 0.55rem; font-size: 0.74rem;" onclick="loadAthleteDetail(${idx})">
          Deep Dive →
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function loadAthleteDetail(idx) {
  const ath = batchAthletesData[idx];
  if (!ath) return;
  const raw = ath.raw_data || ath.full_prediction?.engineered || {};
  for (const [key, val] of Object.entries(raw)) {
    setInputValue(key, val);
  }
  updateCompletionMeter();
  recalculatePrediction();
  switchMainTab("questionnaire");
}

function parseCSVText(text) {
  const lines = text.trim().split(/\r\n|\n/);
  if (lines.length < 2) return [];
  const headers = lines[0].split(",").map(h => h.trim().replace(/^"|"$/g, ''));
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const parts = lines[i].split(",").map(p => p.trim().replace(/^"|"$/g, ''));
    if (!parts[0]) continue;
    const obj = {};
    headers.forEach((h, idx) => { obj[h] = parts[idx]; });
    rows.push(obj);
  }
  return rows;
}

/* ==========================================================================
   WORKSPACE 7: CLINICAL REPORT MODAL EXPORT
   ========================================================================== */

function openReportModal() {
  const modal = document.getElementById("report-modal");
  const content = document.getElementById("report-modal-content");
  if (!modal || !content || !currentPrediction) return;

  const p = currentPrediction;
  const eng = p.engineered;
  const modelA = p.model_a || {};
  const modelC = p.model_c || {};
  const ceil = p.safe_ceiling || {};

  content.innerHTML = `
    <div style="border-bottom: 2px solid var(--glass-border); padding-bottom: 1rem; margin-bottom: 1.25rem;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h2 style="font-size: 1.35rem; font-weight: 800; color: var(--text-main);">ATHLETESHIELD CLINICAL REPORT</h2>
          <div style="font-size: 0.78rem; color: var(--text-subtle);">Certified Multimodal Sports Biomechanics Assessment • ID: AS-${Math.floor(Math.random()*90000+10000)}</div>
        </div>
        <div class="triage-badge ${p.triageBadgeClass}" style="font-size: 0.95rem; padding: 0.45rem 1.15rem;">
          ${p.triage} ACUTE RISK (${p.riskScore}%)
        </div>
      </div>
    </div>

    <!-- 3-Model Summary Box -->
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; margin-bottom: 1.25rem;">
      <div class="metric-box">
        <div class="metric-title">Model B: Acute Injury Risk</div>
        <div class="metric-val" style="color: ${p.triage === 'HIGH' ? 'var(--color-high)' : 'var(--color-low)'};">${p.riskScore}%</div>
        <div class="metric-sub">${p.triageText}</div>
      </div>
      <div class="metric-box">
        <div class="metric-title">Model A: Seasonal Long-Term</div>
        <div class="metric-val" style="color: var(--accent-indigo);">${modelA.season_risk_pct || 24}%</div>
        <div class="metric-sub">Pre-Season Physical Screening</div>
      </div>
      <div class="metric-box">
        <div class="metric-title">Model C: Downtime Forecast</div>
        <div class="metric-val" style="color: var(--color-moderate);">${modelC.expected_sidelined_days || 14.2} d</div>
        <div class="metric-sub">Estimated Sidelined Days</div>
      </div>
    </div>

    <!-- Periodization & Ceiling -->
    <div style="background: var(--bg-subtle); padding: 1rem; border-radius: var(--radius-md); margin-bottom: 1.25rem;">
      <h4 style="font-size: 0.85rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.5rem;">Workload Periodization & Tolerance Ceiling</h4>
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; font-size: 0.8rem;">
        <div>ACWR: <strong>${eng.ACWR?.toFixed(2)}</strong></div>
        <div>Weekly Load: <strong>${eng.Weekly_Load?.toFixed(1)} AU</strong></div>
        <div>Monotony: <strong>${eng.Monotony?.toFixed(2)}</strong></div>
        <div>Safe Ceiling: <strong>${ceil.max_safe_training_hours} hrs</strong></div>
      </div>
    </div>

    <!-- Primary Drivers -->
    <div style="margin-bottom: 1.25rem;">
      <h4 style="font-size: 0.85rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.4rem;">Top Contributory Drivers (SHAP Attribution)</h4>
      <ul style="font-size: 0.8rem; color: var(--text-muted); margin-left: 1.25rem; line-height: 1.6;">
        ${(p.topRiskDrivers || []).map(d => `<li><strong>${d.label}:</strong> Current ${d.value} ${d.unit} (z-score: +${d.zScore})</li>`).join('')}
      </ul>
    </div>

    <!-- Prescriptions -->
    <div style="margin-bottom: 1.5rem;">
      <h4 style="font-size: 0.85rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.4rem;">Clinical Physical Prescriptions</h4>
      ${(p.recommendations || []).map(r => `
        <div style="padding: 0.5rem 0.75rem; background: #FFFFFF; border: 1px solid var(--glass-border); border-radius: var(--radius-sm); font-size: 0.78rem; margin-bottom: 0.4rem;">
          <strong>${r.title}</strong>: ${r.action}
        </div>
      `).join('')}
    </div>

    <!-- Medical Sign-Off Block -->
    <div style="border-top: 1px dashed #CBD5E1; padding-top: 1rem; display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-subtle);">
      <div>
        Physician / Head Physio Sign-off: ___________________________
      </div>
      <div>
        Date: ${new Date().toLocaleDateString()} • Athlete Clearance: <strong>${p.triage === 'HIGH' ? 'RESTRICTED / DELOAD' : 'AUTHORIZED'}</strong>
      </div>
    </div>
  `;

  modal.classList.add("active");
}

function closeReportModal(e) {
  const modal = document.getElementById("report-modal");
  if (modal) modal.classList.remove("active");
}
