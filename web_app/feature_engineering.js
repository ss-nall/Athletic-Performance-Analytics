/**
 * AthleteShield Feature Engineering Module
 * Replicates the exact formulas and baseline imputations from AthleteShield.ipynb
 * Strictly trained and calibrated on real collegiate, wearable, and IMU datasets.
 */

const POPULATION_BASELINES = {
  features: [
    "Age", "Height_cm", "Weight_kg", "Training_Intensity", "Training_Hours_Per_Week",
    "Recovery_Days_Per_Week", "Match_Count_Per_Week", "Rest_Between_Events_Days",
    "Fatigue_Score", "Performance_Score", "Team_Contribution_Score", "Load_Balance_Score",
    "ACL_Risk_Score", "Weekly_Load", "Estimated_Chronic_Load", "ACWR", "Monotony",
    "Strain", "Mean_HR", "Std_HR", "Mean_Temp", "Mean_Oxygen", "Total_Steps",
    "IMU_Cadence", "IMU_Peak_Impact", "IMU_SMA", "IMU_Acc_Variance", "IMU_Rot_Variance"
  ],
  medians: {
    Age: 21.0,
    Height_cm: 182.5,
    Weight_kg: 77.5,
    Training_Intensity: 5.0,
    Training_Hours_Per_Week: 11.0,
    Recovery_Days_Per_Week: 2.0,
    Match_Count_Per_Week: 2.0,
    Rest_Between_Events_Days: 2.0,
    Fatigue_Score: 5.0,
    Performance_Score: 74.0,
    Team_Contribution_Score: 72.0,
    Load_Balance_Score: 98.0,
    ACL_Risk_Score: 45.0,
    Weekly_Load: 57.3625,
    Estimated_Chronic_Load: 54.7309,
    ACWR: 1.0673,
    Monotony: 30.7401,
    Strain: 2588.34,
    Mean_HR: 120.6179,
    Std_HR: 34.8309,
    Mean_Temp: 37.0009,
    Mean_Oxygen: 97.4382,
    Total_Steps: 32360.8,
    IMU_Cadence: 99.6761,
    IMU_Peak_Impact: 4.6127,
    IMU_SMA: 1.3249,
    IMU_Acc_Variance: 0.3675,
    IMU_Rot_Variance: 1.6628
  },
  load_balance_std: 8.734162 // From collegiate dataset
};

/**
 * Computes complete 28-feature vector from raw or partial input.
 * Missing features are filled with population medians (strictly real data).
 * Engineered features (Weekly_Load, Chronic_Load, ACWR, Monotony, Strain)
 * are calculated dynamically whenever raw components are provided.
 */
function engineerFeatures(rawInputs) {
  const merged = { ...POPULATION_BASELINES.medians };

  // Overlay user-provided inputs if valid numeric values
  for (const [key, val] of Object.entries(rawInputs)) {
    if (val !== undefined && val !== null && val !== "" && !isNaN(Number(val))) {
      merged[key] = Number(val);
    }
  }

  // Workload and Periodization Metrics (Notebook Section 3)
  const trainingHours = merged.Training_Hours_Per_Week;
  const trainingIntensity = merged.Training_Intensity;
  const fatigue = merged.Fatigue_Score;

  // 1. Weekly Acute Load
  merged.Weekly_Load = trainingHours * trainingIntensity;

  // 2. Estimated Chronic Load: Weekly_Load * (1.2 - Fatigue_Score * 0.05)
  merged.Estimated_Chronic_Load = merged.Weekly_Load * Math.max(0.2, (1.2 - fatigue * 0.05));

  // 3. Acute-to-Chronic Workload Ratio (ACWR)
  merged.ACWR = merged.Weekly_Load / (merged.Estimated_Chronic_Load + 1e-5);

  // 4. Monotony: Weekly_Load / (Load_Balance_Score_std * 0.1 + 1)
  merged.Monotony = merged.Weekly_Load / (POPULATION_BASELINES.load_balance_std * 0.1 + 1);

  // 5. Training Strain: Weekly_Load * Monotony
  merged.Strain = merged.Weekly_Load * merged.Monotony;

  // Derived Secondary Sports Science Metrics (for dashboard feedback)
  const recoveryDays = merged.Recovery_Days_Per_Week;
  merged.Recovery_Deficit = fatigue / (recoveryDays + 1);
  merged.Workload_to_Recovery_Ratio = merged.Weekly_Load / (recoveryDays + 1);
  merged.Movement_Intensity = (merged.IMU_SMA || 1.32) * (merged.IMU_Cadence || 99.6);
  merged.Combined_Motion_Intensity = (merged.IMU_Acc_Variance || 0.36) + (merged.IMU_Rot_Variance || 1.66);

  return merged;
}

/**
 * Extracts biomechanical features from raw 50Hz DeviceMotion IMU timeseries.
 * Replicates low-pass filtering, cadence peak detection, and SMA calculation.
 */
function processIMUTimeseries(rows, fs = 50.0) {
  if (!rows || rows.length < 10) {
    return null;
  }

  const accMags = [];
  const rotMags = [];
  let sumAbsAcc = 0;

  for (let i = 0; i < rows.length; i++) {
    const r = rows[i];
    const ax = Number(r["userAcceleration.x"] ?? r.userAccX ?? r.acc_x ?? 0);
    const ay = Number(r["userAcceleration.y"] ?? r.userAccY ?? r.acc_y ?? 0);
    const az = Number(r["userAcceleration.z"] ?? r.userAccZ ?? r.acc_z ?? 0);
    const rx = Number(r["rotationRate.x"] ?? r.rotRateX ?? r.rot_x ?? 0);
    const ry = Number(r["rotationRate.y"] ?? r.rotRateY ?? r.rot_y ?? 0);
    const rz = Number(r["rotationRate.z"] ?? r.rotRateZ ?? r.rot_z ?? 0);

    const amag = Math.sqrt(ax * ax + ay * ay + az * az);
    const rmag = Math.sqrt(rx * rx + ry * ry + rz * rz);

    accMags.push(amag);
    rotMags.push(rmag);
    sumAbsAcc += (Math.abs(ax) + Math.abs(ay) + Math.abs(az));
  }

  const n = accMags.length;
  const durationSec = n / fs;
  const sma = sumAbsAcc / n;

  // Mean & Variance
  const meanAcc = accMags.reduce((a, b) => a + b, 0) / n;
  const meanRot = rotMags.reduce((a, b) => a + b, 0) / n;
  const varAcc = accMags.reduce((acc, v) => acc + (v - meanAcc) ** 2, 0) / (n - 1 || 1);
  const varRot = rotMags.reduce((acc, v) => acc + (v - meanRot) ** 2, 0) / (n - 1 || 1);
  const peakImpact = Math.max(...accMags);

  // Peak detection on smoothed acceleration signal for step cadence
  // Simple moving average smoother approximating 3Hz low-pass filter
  const windowSize = Math.max(3, Math.round(fs * 0.1));
  const smoothed = [];
  for (let i = 0; i < n; i++) {
    let sum = 0, count = 0;
    for (let j = Math.max(0, i - windowSize); j <= Math.min(n - 1, i + windowSize); j++) {
      sum += accMags[j];
      count++;
    }
    smoothed.push(sum / count);
  }

  let peakCount = 0;
  const minPeakDist = Math.round(fs * 0.3); // at least 300ms apart (max 200 spm)
  let lastPeakIdx = -minPeakDist;
  const threshold = meanAcc + 0.15 * Math.sqrt(varAcc);

  for (let i = 1; i < n - 1; i++) {
    if (smoothed[i] > smoothed[i - 1] && smoothed[i] > smoothed[i + 1] && smoothed[i] > threshold) {
      if (i - lastPeakIdx >= minPeakDist) {
        peakCount++;
        lastPeakIdx = i;
      }
    }
  }

  const cadence = durationSec > 0 ? (peakCount / durationSec) * 60 : 100.0;

  return {
    IMU_Cadence: Number(cadence.toFixed(1)),
    IMU_Peak_Impact: Number(peakImpact.toFixed(3)),
    IMU_SMA: Number(sma.toFixed(3)),
    IMU_Acc_Variance: Number(varAcc.toFixed(4)),
    IMU_Rot_Variance: Number(varRot.toFixed(4)),
    duration_sec: Number(durationSec.toFixed(1)),
    total_steps_detected: peakCount
  };
}

/**
 * Aggregates Wearable telemetry CSV rows into Mean_HR, Std_HR, Mean_Temp, Mean_Oxygen, Total_Steps
 */
function processWearableTimeseries(rows) {
  if (!rows || rows.length === 0) return null;

  const hrVals = [];
  const tempVals = [];
  const o2Vals = [];
  let totalSteps = 0;

  for (const r of rows) {
    const hr = Number(r.Heart_Rate ?? r.heart_rate ?? r.HR);
    const temp = Number(r.Body_Temperature ?? r.body_temperature ?? r.Temp);
    const o2 = Number(r.Blood_Oxygen ?? r.blood_oxygen ?? r.SpO2 ?? r.Oxygen);
    const steps = Number(r.Step_Count ?? r.step_count ?? r.Steps ?? 0);

    if (!isNaN(hr) && hr > 0) hrVals.push(hr);
    if (!isNaN(temp) && temp > 0) tempVals.push(temp);
    if (!isNaN(o2) && o2 > 0) o2Vals.push(o2);
    if (!isNaN(steps)) totalSteps += steps;
  }

  const meanHR = hrVals.length ? hrVals.reduce((a, b) => a + b, 0) / hrVals.length : 120.6;
  const varianceHR = hrVals.length > 1
    ? hrVals.reduce((acc, v) => acc + (v - meanHR) ** 2, 0) / (hrVals.length - 1)
    : 34.8;
  const stdHR = Math.sqrt(varianceHR);
  const meanTemp = tempVals.length ? tempVals.reduce((a, b) => a + b, 0) / tempVals.length : 37.0;
  const meanO2 = o2Vals.length ? o2Vals.reduce((a, b) => a + b, 0) / o2Vals.length : 97.4;

  return {
    Mean_HR: Number(meanHR.toFixed(1)),
    Std_HR: Number(stdHR.toFixed(2)),
    Mean_Temp: Number(meanTemp.toFixed(2)),
    Mean_Oxygen: Number(meanO2.toFixed(1)),
    Total_Steps: totalSteps > 0 ? totalSteps : 32360
  };
}

// Export for browser or node
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    POPULATION_BASELINES,
    engineerFeatures,
    processIMUTimeseries,
    processWearableTimeseries
  };
}
