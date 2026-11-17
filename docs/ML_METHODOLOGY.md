# Machine Learning Methodology & Model Architecture

## 1. Overview & Problem Formulation

The core predictive objective of **AIOps Sentinel** is to transform raw multivariate time-series infrastructure telemetry into actionable operational foresight.

Given an input telemetry vector:
$$X = [x_{\text{cpu}}, x_{\text{mem}}, x_{\text{disk}}, x_{\text{lat}}, x_{\text{err}}]^T \in \mathbb{R}^5$$

The system solves two distinct machine learning tasks:
1. **Unsupervised Anomaly Detection**: Estimate anomaly score $s(X) \in [0, 1]$ without requiring labeled ground truth in production.
2. **Supervised Failure Prediction**: Estimate the conditional probability of operational failure:
   $$P(Y = 1 \mid X) \in [0, 1]$$
   where $Y \in \{0, 1\}$ represents system availability or failure state.

---

## 2. Dataset Synthesis & Physical Grounding

### 2.1 Synthetic Telemetry Description
The dataset was synthetically synthesized to provide a reproducible, statistically grounded benchmark of cloud infrastructure behavior. A total of **6,000 observations** were synthesized using a fixed random seed (`seed = 42`) spanning nominal traffic and four characteristic failure signatures:

1. **Nominal Operational Baseline (~76% of samples)**:
   - CPU: $\mu = 44.0\%, \sigma = 12.0\%$
   - Memory: $\mu = 54.0\%, \sigma = 10.0\%$
   - Disk: $\mu = 60.0\%, \sigma = 8.0\%$
   - Latency: $\mu = 48.0\text{ ms}, \sigma = 18.0\text{ ms}$
   - Error Rate: Exponential distribution ($\lambda = 0.8\%$)
2. **Benign Transient Load Spikes (~6% of samples)**:
   - Elevated CPU (72&ndash;84%) and latency without system failure. Tests model specificity against false positives.
3. **Compute Saturation & Thread Starvation (~5% of samples)**:
   - CPU: $\mu = 93.0\%, \sigma = 3.5\%$; Latency elevation: $+160\text{ ms}$; Error rate elevation: $+4.5\%$.
4. **Memory Leak & Garbage Collection Thrashing (~5% of samples)**:
   - Memory: $\mu = 94.0\%, \sigma = 3.0\%$; Periodic CPU spikes during garbage collection pauses.
5. **Network Degradation & Packet Loss (~4% of samples)**:
   - Round-trip latency: $\mu = 380\text{ ms}, \sigma = 90\text{ ms}$; Error rate: $\mu = 7.5\%, \sigma = 2.5\%$.
6. **Cascading Multi-Resource Collapse (~4% of samples)**:
   - Concurrent exhaustion across all metrics ($>90\%$ CPU, $>90\%$ Memory, $>500\text{ ms}$ Latency, $>10\%$ Error Rate).

*Notice: This dataset is synthetic and explicitly documented as such. No fabricated or artificial numbers are used.*

---

## 3. Data Preprocessing & Leakage Prevention

### 3.1 Stratified Train/Test Partition
The 6,000 records are partitioned using stratified sampling:
- **Training Set**: 4,500 samples ($75\%$)
- **Testing Holdout**: 1,500 samples ($25\%$)

Stratification guarantees identical target balance ($18.3\%$ failure incidence) across both splits.

### 3.2 Feature Standardization
Features exhibit different physical scales (utilization in %, latency in ms). We apply standard z-score normalization:
$$z = \frac{x - \mu_{\text{train}}}{\sigma_{\text{train}}}$$

**Leakage Prevention Guarantee**:
The `StandardScaler` parameters ($\mu_{\text{train}}, \sigma_{\text{train}}$) are computed **strictly on the training partition**. The test set is transformed using these frozen training statistics without re-estimation.

---

## 4. Model Architectures

### 4.1 Primary Model: Random Forest Classifier
- **Ensemble Size**: $B = 120$ decision trees
- **Max Tree Depth**: 9 levels (balances expressiveness and prevents memorization)
- **Min Samples Split**: 4
- **Class Weight**: Balanced (inversely proportional to class frequencies)
- **Splitting Criterion**: Gini Impurity:
  $$I_G(p) = 1 - \sum_{k=0}^1 p_k^2$$
- **Predictive Inference**:
  $$P(Y = 1 \mid X) = \frac{1}{B} \sum_{b=1}^B P_b(Y = 1 \mid X)$$

### 4.2 Baseline Model: Regularized Logistic Regression
Included for empirical comparison against the non-linear ensemble:
- **Optimization**: L-BFGS solver with L2 weight regularization ($C = 1.0$)
- **Model Formulation**:
  $$P(Y = 1 \mid X) = \sigma(w^T X + b) = \frac{1}{1 + e^{-(w^T X + b)}}$$

### 4.3 Anomaly Detection: Isolation Forest
Unsupervised tree-based anomaly isolation:
- **Estimators**: 150 isolation trees
- **Subsampling**: 256 samples per tree
- **Contamination Parameter**: $\alpha = 0.20$
- **Anomaly Score Formulation**:
  $$s(X, n) = 2^{-\frac{\mathbb{E}(h(X))}{c(n)}}$$
  where $h(X)$ is path length and $c(n) = 2 \ln(n - 1) + 0.5772 - \frac{2(n - 1)}{n}$.

---

## 5. Local Feature Attribution & XAI Engine

Global feature importances from Random Forest quantify how informative each telemetry dimension is across the entire population. To provide instance-level explanations, AIOps Sentinel computes **Local Metric Attribution**:

$$\text{Attr}_i(X) = \text{Imp}_i \times \max\left(0, \frac{x_i - \mu_{i, \text{baseline}}}{\sigma_{i, \text{baseline}}}\right)$$

This guarantees that an alert highlights the metric driving the current deviation rather than generic static averages.
