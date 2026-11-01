# CR-1 第3版：独立・凍結前レビュー（GPT-6、追補）

PRIVATE UNPUBLISHED RESEARCH — INDEPENDENT REVIEW; NO OWNER FREEZE; NO EXPERIMENT EXECUTION.

- Target: `notes/cr1_claude_resample_gate.md`, branch `decision-points`
- Target blob SHA: `0c60b9384bd3ba45ae743c96adfc500a9ae11aa2`
- Version: Draft v3, 2026-10-11 00:45 JST; **NOT FROZEN**
- Verdict: **PASS WITH REPAIRS / NOT FREEZE-READY**.
- Earliest material issue in reading order: **Definition 13 / C1's inference of proxy validity** (the label-selection defect at Definition 13 arises even if C1's equations are correct). Previous review R1's erroneous *theoretical zero-residual assumption* was withdrawn in v3.
- Scope: design, definitions and statistical decision rules only. No check of hidden data, API outputs, source-code implementation, or pricing. This review does not amend the draft or choose owner decisions.

## A. Status of previous review R1–R6

| Prior item | v3 status |
|---|---|
| R1 prefix/conditional-law mismatch | **Major improvement**: switched to `startswith(s_w)`, acknowledged tokenization ambiguity, defined residual `r`, and stopped assuming `E[r]=0`. The residual can still be systematic; G0's descriptive diagnostics do not establish equality. |
| R2 C1 residual proxy | **PARTIAL**: noise comparison, signed residual CI, abs residual, Spearman and Cohen kappa were added, but C1's *passing* criterion ignores rank/label agreement. |
| R3 missing `g` and null | **Partly resolved**: `n_diff=0` keeps `d_s=0` and is excluded from `g` permutation. Unequal variance of `g` remains confounded with `m`. |
| R4 `u` vs `m_A` | **Improved**: S5 adds an independent-arm comparison. Their definitions now refer to *different* first-unit partitions (see N4 below). |
| R5 cluster independence/reliability | **Improved**: 1 template = 1 analysed problem and bootstrap over templates, C2 specifies correlation. Independence language about attenuation remains too strong. |
| R6 budget, retries and incompleteness | **Improved**: budget cap, custom IDs, bounded retries, incomplete label. Two missingness rules require reconciliation; some costing/retry details to fix before freeze. |

## B. Remaining required repairs (new or still unresolved)

### N1 — [BLOCKING] Definition 13: top 15% need not be positive forks

Always selecting top 15% of `d_s` across all positions can label zero or negative `d_s` positions as "forks" if effects are sparse, zero-heavy or negative. Randomly breaking zero ties manufactures positives even under a no-drop null. This is particularly important for 36 resamples per prefix and an empirical `d_s` concentrated at zero.

**Repair**: freeze the treatment of `d_s <= 0` and near-zero values. Report the 85th-percentile cutoff, fraction of positives with nonpositive `d_s`, share of exact ties at cutoff, fraction of positions with `n_diff=0`, and number of items admitting within-item AUROC. Either (i) relabel the outcome as *relative top-15%-of-estimated-`d_s`* even where it is not an actual positive drop, and never call all selected positions "real forks", or (ii) require positive/minimum-effect thresholds and pre-specify how to handle fewer than 15% qualified positions. Add an explicit uninterpretable/insufficient-variation result when the signal/prevalence is absent.

### N2 — [BLOCKING for proxy interpretation] C1: no connection between pass rule and ranks/labels

The v3 criterion `CIupper(R)<=1.5` and a signed mean-`r` CI within ±0.02 assesses average residual magnitude against a specific binomial null. It **does not imply** `d_s` and `d` select the same top 15%, even if rank correlation and Cohen's kappa are *reported*. Tiny residuals can invert rankings when many `d_s` sit near the selection boundary; positive and negative residuals can also cancel in the signed mean. A 95% interval contained within ±0.02 is an equivalence criterion only for the *mean signed residual* under the chosen resampling scheme, not per-position proxy adequacy.

**Repair**: do not say `RESIDUAL_WITHIN_NOISE` alone authorizes "**d_s は d の代わりになる**". To assert label-level surrogate validity, pre-specify a decision threshold for kappa/top-15% agreement and/or pairwise rank stability with its own CI, plus admissible base-label variation. Alternatively leave C1 as a diagnostic, limit all primary claims to `d_s` as an operational measurement, and never assert interchangeability with `d` from C1 alone. If using the null ratio `R`, specify zero-denominator, `n_same=0`, n-dependent variances, and how simulated null variability is propagated through the bootstrap; 200 simulations may give noisy denominator estimates.

### N3 — [BLOCKING for 主2] Shuffling can remove AUROC-eligible items

The main AUROC is defined only for items that have both classes. Each shuffle recomputes **pooled top-15%** `m * shuffled(g)` labels and hence can move positives across items. An item eligible for the observed AUROC may become all-negative (or all-positive) in some shuffles, making its AUROC undefined. "For each problem take the median of 1,000 shuffle AUROCs, subtract and bootstrap" does not specify how to handle these undefined entries. The observed and shuffled scores can end up averaging over different item populations, a selection artifact.

**Repair**: before freeze, specify a common support of eligible items per comparison, or a null statistic evaluated on comparable populations per shuffle, and what happens if any shuffle produces too few eligible items. If items are dropped, report counts and pre-specify whether the primary estimand changes. Explicitly decide if the 1,000 permutations are recomputed inside each template bootstrap or frozen once and bootstrapped as a conditional benchmark, and interpret CI accordingly.

### N4 — [IMPORTANT] `u` and `m_A` now use incompatible partitions

`u` groups by the **entire first whitespace-delimited unit** (Definition 14), whereas `m_A` uses **raw startswith(s_w)** (Definition 15). They need not coincide even when the base word is modal. Example: `s_w=" 12"`, six outputs begin `" 12 apples"` and six begin `" 123 apples"`: `u=0.5` (two first-unit types), but `m_A=0` (all strings start with `" 12"`). Thus previous-v2 inequalities/equalities for an exact-unit `m_A` do not transport to v3. S5 is still valuable as a comparator but its interpretation must account for this partition discrepancy.

**Repair**: label S5 a comparison of two *different summaries* of variation; optionally add `u_prefix` or `m_A^{exact}` that uses the same grouping if the intended question is whether entropy-like variation exceeds "not the reference" frequency. Keep separate A/B draws.

### N5 — [IMPORTANT] C2 sample splitting does not guarantee AUROC attenuation

A and B being distinct generation samples avoids *shared random draws*, but does not make the **error in top-15% labels** independent of `u` across positions. Variance of `d_s` can depend on `m`, `q_keep`, true effects and item characteristics correlated with `u`; global thresholding is nonlinear. Therefore "このとき雑音は AUROC を 0.5 側に寄せる" is not guaranteed solely by A/B sample splitting. 

**Repair**: replace with "独立組の採用により共有標本ノイズを避けるが、ラベル雑音がAUROCをどの方向に動かすかは一般には確定しない". C2 reliability is descriptive, and the pre-specified caveat for low reliability should apply to both apparently high and low AUROCs (a high estimate is not automatically a conservative lower bound).

### N6 — [IMPORTANT] G2 missingness and incomplete rules conflict / are underspecified

Verdict section says missing data in G2 means `INCOMPLETE_NO_CONFIRMATORY_VERDICT`, but G2 allows up to 10% missing `B` per cut and up to 10% excluded items without setting incomplete. There is no quantitative limit for missing `A` samples, and no pre-specified denominator/minimum for `u`. If missingness is informative (long/truncated/error responses), allowing variable denominators can bias `q`, `m` and `u`.

**Repair**: specify whether completeness means all requested calls or passing a predefined coverage threshold; explicit per-arm minimum counts, drop/impute rules for missing A/B, which items are eligible, and a unified incomplete condition. Include all failed attempts and costs in the audit log. Distinguish API errors (missingness) from a completed response with `max_tokens` stop, which Definition 8 classifies as "different". A completed empty or whitespace-only result also needs a defined **first-unit sentinel** for `u`.

### N7 — [IMPORTANT] Statistical and operational interpretation details

- For C1, template bootstrap and simulated residual null: specify whether each bootstrap resample draws new binomial simulations, how `p` is estimated under the null, and how `n_same=0` is handled. Avoid interpreting passing C1 as proof of identical conditional generative laws.
- For 主2, `g` is much noisier where `n_diff` is small. Permuting estimated `g` across heterogeneous `m` does **not** cleanly isolate the weight-only contribution unless the error structure is included in the null. Call this a *noisy-effect permutation baseline*, restrict claims accordingly, or prespecify variance-aware controls.
- Candidate selection is based on observed base-path format, length and `end_turn`. Report all 100 templates' acceptance/attrition and state that inferences are about that selected set.
- Pre-freeze G0 remains a feasibility probe only; any diagnostic surprises cannot justify unregistered changes to main outcomes after freeze.
- Budget guard: choose an explicit initial per-call cost prior to observing usage, track input-cache and retry charges as applicable, estimate already-submitted costs appropriately, and specify how a halt interacts with the "no confirmatory verdict" decision. Do not conflate the average output-token forecast with an upper bound.

## C. Prioritized minimum repair plan

1. **N1**: positive-effect/top-15% semantics and no-signal guard.
2. **N2**: tighten C1 surrogate-validity criterion or drop the `d_s≈d` claim entirely.
3. **N3**: handle undefined per-item AUROC under shuffled labels on a comparable population.
4. **N4–N6**: fix proxy-vs-weight interpretation, C2 attenuation claim, and A/B missingness/INCOMPLETE consistency.
5. **N7**: tighten null simulation, heterogeneous-noise baseline, and operational details.

No owner freeze, no implementation, no hidden experiment results, and no alteration of the target plan has been performed. This review is an **independent adversarial reading**, not an approval of data-dependent changes after preregistration.
