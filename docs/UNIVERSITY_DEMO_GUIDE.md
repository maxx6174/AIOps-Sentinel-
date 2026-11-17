# University Demonstration Guide & Evaluation Script

**Project Title**: AIOps Sentinel: Explainable AI-Powered Infrastructure Failure Prediction and Intelligent Root Cause Analysis Platform  
**Target Evaluation**: Vel Tech University Engineering Project Review & Evaluation Committee

---

## 1. Executive Presentation Script (2-Minute Elevator Pitch)

> *"Good morning, respected evaluation committee members. Today, modern distributed software architectures and microservices face catastrophic downtime costing millions per hour. Traditional monitoring tools like Prometheus and Datadog tell engineers that a threshold has breached after the failure occurs.*
>
> *Our project, **AIOps Sentinel**, provides predictive foresight and explainability. Instead of reacting to outages, it combines unsupervised Anomaly Detection via **Isolation Forests** with supervised Failure Prediction via **Random Forest ensembles**.*
>
> *Crucially, it answers four critical questions before the system collapses:*
> 1. *What is happening in the infrastructure?*
> 2. *Why is the abnormal behaviour occurring?*
> 3. *What could happen next?*
> 4. *What action should be taken?*
>
> *Let us walk you through a live demonstration."*

---

## 2. 10-Step Interactive Judge Demonstration Flow

Follow this exact sequential path to demonstrate full system capabilities to the judges:

### Step 1: Dashboard Overview
1. Open the application.
2. Point out the clean, professional, human-designed light interface.
3. Show the **Infrastructure Health: HEALTHY** banner, the **5 Monitored Microservices** (API Gateway, Auth, Payment, DB, Cache), and the real-time rolling telemetry stream.
4. Show the **Risk Score (12/100)** indicating low ambient risk under nominal load.

### Step 2: Show Machine Learning Verification
1. Click the **"ML Benchmarks"** button in the top navigation bar.
2. Show the judges the comparative evaluation table:
   - **Random Forest Classifier**: **98.87% Accuracy, 100% Recall, 0.9952 ROC-AUC**.
   - **Logistic Regression (Baseline)**: 98.73% Accuracy, 98.43% Recall.
   - **Isolation Forest**: 95.67% Accuracy, 0.9876 ROC-AUC.
3. Explain the **Global Feature Importances** chart (Network Latency ~44.6%, Error Rate ~39.4%, CPU ~9.5%).
4. Explain the **Leakage Prevention**: Standard scaler was fitted strictly on the 75% train partition without data leakage.

### Step 3: Navigate to Live Simulation
1. Click **"Live Simulation"** in the left sidebar.
2. Explain that the platform contains **5 distinct, reproducible failure scenarios**:
   - Normal Operation
   - CPU Overload & Thread Starvation
   - Memory Leak & GC Thrashing
   - Network Latency & Packet Loss
   - Combined Infrastructure Failure

### Step 4: Run Scenario 1 &mdash; CPU Overload
1. Click the **"CPU Overload & Thread Starvation"** scenario card.
2. Click the **"Start Simulation"** button.
3. Observe the live telemetry dials and continuous chart:
   - Notice CPU utilization climbing progressively: $42\% \to 65\% \to 80\% \to 96\%$.
   - Point out that memory remains stable ($~55\%$), isolating the root cause.
4. Watch the AI verdict transition in real time:
   - **Anomaly Detected**: YES (Isolation Forest flags path length deviation).
   - **Failure Probability**: Climbs from $5\% \to 85\% \to 95\%$.
   - **Risk Level**: Transitions from Low $\to$ High $\to$ **Critical**.
5. Show the **Explainable AI (XAI)** cards:
   - Question 1: Notes sustained CPU compute saturation at $96\%$.
   - Question 2: Explains thread pools consuming clock cycles without yielding.
   - Question 3: Warns of impending HTTP 504 Gateway Timeouts.
   - Question 4: Recommends thread dump inspection and scaling horizontal worker replicas.

### Step 5: Run Scenario 2 &mdash; Memory Leak
1. Click the **"Reset Baseline"** button.
2. Select **"Memory Leak & GC Thrashing"** and click **"Start Simulation"**.
3. Watch Memory Utilization climb linearly from $54\% \to 98\%$.
4. Point out the intermittent CPU spikes: explain to judges that this mimics Java/V8 garbage collectors attempting aggressive stop-the-world sweeps.
5. Read Question 3 to the judges:
   - *"Kernel Out-Of-Memory (OOM) Killer invocation predicted with 95% probability (SIGKILL, exit code 137)."*
   - Explains exact operating system mechanics!

### Step 6: Run Scenario 3 &mdash; Network Degradation
1. Reset and click **"Network Latency & Packet Loss"**.
2. Start the simulation.
3. Observe Latency spike to $700+\text{ ms}$ and Error Rate surge to $12\%$, while CPU and Memory stay completely normal.
4. Show how the model attributes the failure to transport-layer connection timeouts rather than compute exhaustion.

### Step 7: Run Scenario 4 &mdash; Combined Multi-Tier Cascade
1. Reset and click **"Combined Infrastructure Failure"**.
2. Start the simulation.
3. Observe all dials turning red: CPU $>95\%$, Memory $>95\%$, Latency $>600\text{ ms}$, Error Rate $>15\%$.
4. Point out that the system risk score reaches **98/100**, and the diagnosis correctly concludes:
   - *"Cascading Resource Exhaustion & System Saturation"*.

### Step 8: Interactive Sliders & Arbitrary Evaluation
1. Navigate to **"AI Analysis"** in the sidebar.
2. Drag the **Latency slider** to $650\text{ ms}$ and click **"Run ML Inference"**.
3. Point out that the machine learning model evaluates live in $<5\text{ ms}$ on the Python backend, computing exact failure probability and updating the 4-question analysis.
4. Show the **Empirical Evidence vs. Hypotheses** table, proving that measured facts are never confused with algorithmic deductions.

### Step 9: Batch CSV Telemetry Ingestion & Audit
1. Navigate to **"Data & Reports"**.
2. Click **"Download Sample CSV"** &mdash; downloads `aiops_sample_telemetry.csv` containing 120 rows.
3. Immediately select and upload this CSV file.
4. Click **"Process Telemetry CSV"**.
5. Observe the batch analytics:
   - Total records evaluated: 120
   - Anomalies detected, predicted failures, and risk breakdown bar chart.
   - Inspect individual rows in the table with anomaly status and predicted failure probability.
6. Click **"Export Audit Report"** to download the plain text diagnostic summary.

### Step 10: Conclusion
1. Summarize:
   - Zero hardcoded heuristics &mdash; actual trained scikit-learn models running in production.
   - Complete leakage prevention and verified 98.87% accuracy.
   - Real-time Explainable AI solving operator cognitive overload.

---

## 3. Anticipated Judge Questions & Recommended Answers

**Q1: How do you prevent data leakage during model training?**  
> *"We apply a strict stratified 75/25 train-test split before preprocessing. All normalization parameters ($\mu, \sigma$) in our `StandardScaler` are computed strictly on the training set and applied as frozen transformations to the test set."*

**Q2: Why use both Isolation Forest and Random Forest?**  
> *"Isolation Forest is unsupervised &mdash; it flags unseen anomalies without prior labels, protecting against zero-day architectural issues. Random Forest is supervised &mdash; it calibrates exact failure probabilities and provides global feature importances based on known failure signatures."*

**Q3: How is this explainable and not just a black-box model?**  
> *"We decompose predictions into: (1) Empirical Evidence (measured z-score deviations from established physical baselines), (2) Local Metric Attribution, and (3) Synthesized Root Cause Playbooks answering the four operational questions."*
