# Stage 4 Model Validation — Hardening Report

**Project:** Telecom Customer Churn (Maven Analytics) · **Date:** 2026-09-15
**Source data:** `data/processed/clean_customers.csv` (7,043 × 43)
**Companion artifact:** `reports/figures/stage4_model_cv_auc.png`

---

## 1. Method

Stage 4 (`notebooks/04_feature_importance.ipynb`) evaluated the churn model on a
single stratified 80/20 holdout (RF ROC-AUC 0.9206, LR ROC-AUC 0.9122). This
hardening pass replaces that single split with **5-fold stratified
cross-validation** and adds a **model-agnostic permutation-importance** ranking
to complement the Gini/coefficient rankings.

### 1.1 Population

- `customer_status != 'Joined'` — **n = 6,589 existing customers**.
- Target = `churn` (bool) — **1,869 positives, 28.37% prevalence** (matches the
  Stage-4 population exactly).

### 1.2 Feature matrix (rebuilt identically to Stage 4 — 37 features)

Leakage/target exclusions: `customer_id`, `customer_status`, `churn`,
`churn_category`, `churn_reason`. `total_revenue` dropped (r = 0.97 with
`total_charges`); `total_charges` retained. `internet_type` is represented by
the engineered `is_fiber` + `internet_service` flags (avoids perfect
collinearity in the logistic model).

| Group | Count | Features |
|---|---|---:|---|
| Numeric | 13 | `age`, `num_dependents`, `num_referrals`, `tenure_months`, `avg_monthly_long_distance_charges`, `avg_monthly_gb_download`, `monthly_charge`, `total_charges`, `total_refunds`, `total_extra_data_charges`, `total_long_distance_charges`, `contract_commitment`, `bundle_count` |
| Boolean → {0,1} | 14 | `married`, `phone_service`, `multiple_lines`, `internet_service`, `online_security`, `online_backup`, `device_protection_plan`, `premium_tech_support`, `streaming_tv`, `streaming_movies`, `streaming_music`, `unlimited_data`, `paperless_billing`, `is_fiber` |
| One-hot (`drop_first=True`) | 10 | `offer` (5), `payment_method` (2), `contract` (2), `gender` (1) |

**Total: 37 features** (13 + 14 + 10), matching Stage 4 exactly.

### 1.3 Cross-validation

`StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` over the 37-feature
matrix. Two models, each refit per fold:

- **LogisticRegression** — `max_iter=2000, class_weight='balanced'`,
  `random_state=42`, on standardized features (`StandardScaler` fitted within
  each training fold only — no leakage).
- **RandomForestClassifier** — `n_estimators=300, class_weight='balanced'`,
  `random_state=42`.

Per-fold metrics: ROC-AUC, precision and recall at the default **0.5 threshold**.

### 1.4 Permutation importance

`sklearn.inspection.permutation_importance` on a RandomForestClassifier
(`n_estimators=300, class_weight='balanced', random_state=42`) fit to the **full
non-Joined population**, `scoring='roc_auc'`, `n_repeats=10`,
`random_state=42`. Importance = mean drop in ROC-AUC when a feature's values are
shuffled (holding all others fixed).

---

## 2. Results

### 2.1 5-fold stratified cross-validation

| Model | ROC-AUC (mean ± std) | Precision@0.5 (mean ± std) | Recall@0.5 (mean ± std) |
|---|---:|---:|---:|
| **RandomForest** | **0.9267 ± 0.0052** | **0.7479 ± 0.0184** | **0.7817 ± 0.0236** |
| **LogisticRegression** | **0.9135 ± 0.0048** | **0.6276 ± 0.0171** | **0.8700 ± 0.0063** |

Per-fold ROC-AUC:

| Fold | RandomForest | LogisticRegression |
|---|---:|---:|
| 1 | 0.9344 | 0.9144 |
| 2 | 0.9302 | 0.9131 |
| 3 | 0.9258 | 0.9145 |
| 4 | 0.9231 | 0.9202 |
| 5 | 0.9198 | 0.9052 |

The fold-to-fold spread is tight (RF std 0.005, LR std 0.005), confirming the
Stage-4 holdout estimate was **not** an overfit/underfit artifact of a lucky
split. RF is the higher-accuracy model; LR is the higher-recall model at the
0.5 threshold (87.0% vs 78.2% recall, at the cost of 12 pp precision).

### 2.2 Permutation importance — top 15

| Rank | Feature | Importance (mean) | ± std |
|---:|---:|---:|---:|
| 1 | `num_referrals` | 0.01304 | 0.00088 |
| 2 | `contract_commitment` | 0.00862 | 0.00032 |
| 3 | `tenure_months` | 0.00608 | 0.00048 |
| 4 | `num_dependents` | 0.00345 | 0.00024 |
| 5 | `monthly_charge` | 0.00318 | 0.00020 |
| 6 | `age` | 0.00144 | 0.00022 |
| 7 | `total_long_distance_charges` | 0.00063 | 0.00006 |
| 8 | `total_charges` | 0.00029 | 0.00004 |
| 9 | `is_fiber` | 0.00012 | 0.00002 |
| 10 | `payment_method_Credit Card` | 0.00011 | 0.00003 |
| 11 | `avg_monthly_gb_download` | 0.00009 | 0.00002 |
| 12 | `contract_Two Year` | 0.00006 | 0.00002 |
| 13 | `avg_monthly_long_distance_charges` | 0.00005 | 0.00001 |
| 14 | `online_security` | 0.00002 | 0.00000 |
| 15 | `premium_tech_support` | 0.00001 | 0.00000 |

Importance decays sharply after the top 3 features (a 2.1× drop from #1 to #2,
and another 1.4× from #2 to #3), then a long tail — a signature of a small set
of dominant drivers plus many weak, partially redundant signals.

---

## 3. Comparison to Stage 4

Stage-4 rankings (from `analysis_findings.md`) vs the new permutation ranking:

| Feature | Stage-4 RF Gini rank | Stage-4 LR \|coef\| rank | Permutation rank |
|---|---:|---:|---:|
| `num_referrals` | 4 | 2 | **1** |
| `contract_commitment` | **1** | 6 | **2** |
| `tenure_months` | 2 | **1** | **3** |
| `num_dependents` | 11 | 5 | **4** |
| `monthly_charge` | 5 | 7 | **5** |
| `total_charges` | 3 | 3 | **8** |
| `age` | 8 | 13 | **6** |
| `married` | — | 4 | **>15 (absent)** |

### Where they agree

The **same small set of features dominates every ranking** —
`num_referrals`, `contract_commitment`, `tenure_months`, `monthly_charge`, and
`num_dependents` occupy the top-5 of the permutation list and are all top-11 in
both Stage-4 lists. The qualitative churn story — *early tenure, low contract
commitment, few referrals, higher price, fewer dependents* — is robust to the
ranking method.

### Where they diverge, and why

1. **`total_charges` collapses from #3 → #8.** In Stage 4 it sat at #3 in *both*
   the Gini and logistic-coefficient rankings. Permutation importance reveals
   this was **redundancy inflation**: `total_charges` is lifetime spend
   ≈ `tenure_months × monthly_charge`, so once `tenure_months` and
   `monthly_charge` are already in the model, scrambling `total_charges` costs
   almost nothing (0.00029 AUC). Coefficient magnitude and Gini both reward
   *bivariate* association with the target, not *marginal* contribution.

2. **`num_referrals` rises to #1.** Referrals carry **irreplaceable** signal —
   no other column can stand in for the advocacy/loyalty effect it encodes, so
   destroying it is the single most damaging perturbation (ΔAUC −0.013). Gini
   under-weighted it (#4) because trees can partially route around it via
   tenure/commitment splits.

3. **`tenure_months` and `contract_commitment` partially dilute each other.**
   `contract_commitment` (#1 Gini) and `tenure_months` (#1 logistic) both encode
   "how long/committed is this customer," and term contracts are strongly
   correlated with tenure. Permutation correctly splits their marginal credit —
   `contract_commitment` (#2) edges `tenure_months` (#3) — rather than letting
   the linear coefficient double-count the shared variance.

4. **`married` disappears from the top-15.** It was #4 by |logistic
   coefficient| (0.829), but its protective effect is **absorbed** by
   `num_dependents`, `age`, and `contract_commitment` (married customers tend to
   be older, have dependents, and hold term contracts). With those present,
   `married` adds no marginal predictive value.

**Mechanistic takeaway:** coefficient and Gini importance measure how correlated
a feature is with churn (and how often the model splits on it); permutation
importance measures how much the *prediction* degrades when that feature is
destroyed *given everything else*. The latter is the better guide to which
features are truly load-bearing — and it confirms the **actionable** levers
(contract commitment, referrals, tenure-management, price) while stripping out
the mechanical `total_charges` signal.

---

## 4. Limitations

1. **Snapshot, not longitudinal.** The data is a point-in-time cross-section
   (end of fiscal Q2 2022). Stratified CV is a *random* resampling of that
   snapshot; it does **not** simulate deployment to future quarters.
2. **No temporal split.** Because `churn` is a one-shot label (not a dated
   event), an out-of-time holdout is impossible. CV therefore estimates
   *same-distribution* generalization, which is likely optimistic for a live
   model.
3. **Quasi-leakage in tenure/lifetime-spend features.** `tenure_months`,
   `total_charges`, and the `total_*` charge columns are themselves functions of
   the customer's elapsed lifetime, so they partly *encode* the outcome rather
   than purely predict it. They are retained (as in Stage 4) for comparability,
   but the permutation ranking correctly discounts the redundant
   `total_charges`.
4. **Class imbalance.** 28.4% positive class, handled by `class_weight='balanced'`
   and stratified folds. Precision/recall are reported at the default **0.5
   threshold** and are **not** threshold-tuned; the recall/precision trade-off
   (RF 0.78/0.75 vs LR 0.87/0.63) is a tunable business decision, not a fixed
   property.
5. **Permutation importance is RF-specific.** It reflects the fitted RandomForest
   (the modeling choice); a model-agnostic average over both RF and LR would shift
   the tail ranks slightly, but the top-5 would be unchanged.
6. **`num_referrals` magnitude is small in absolute terms** (ΔAUC ≈ 0.013),
   consistent with the many-weak-signals nature of churn; no single feature is a
   decisive predictor.

---

## 5. Conclusion

5-fold stratified CV **confirms** the Stage-4 single-holdout results rather than
overturning them:

- **RandomForest: ROC-AUC 0.9267 ± 0.0052** (Stage-4 holdout 0.9206)
- **LogisticRegression: ROC-AUC 0.9135 ± 0.0048** (Stage-4 holdout 0.9122)

Both CV means land within (actually slightly above) the Stage-4 holdout, with
tight fold-to-fold standard deviations (~0.005), so there is **no evidence of
overfitting** and the earlier headline numbers are trustworthy.

Permutation importance sharpens the driver story: the **actionable** churn
levers — **`num_referrals` (#1)**, **`contract_commitment` (#2)**,
**`tenure_months` (#3)**, **`num_dependents` (#4)**, **`monthly_charge` (#5)** —
are confirmed as the true marginal contributors, while the mechanical
`total_charges` signal is exposed as redundant. This supports the Stage-4
recommendations (convert Month-to-Month → term, lever referrals, price/Fiber
retune, early-tenure intervention) on firmer statistical ground.

---

## Figures

- `reports/figures/stage4_model_cv_auc.png` — mean ± std ROC-AUC (5-fold CV) for
  both models, with per-fold points overlaid.
