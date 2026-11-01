# CR-1 第5版 — 独立・凍結前監査（GPT-6）

PRIVATE UNPUBLISHED RESEARCH. REVIEW ONLY. NO OWNER FREEZE.

- Source: `chichichi2001/Pork`, branch `decision-points`, `notes/cr1_claude_resample_gate.md`
- Audited source blob SHA: `7c70a5416d41d6721c78d30d1bc67bc9f4d60b2b`
- Source label: Draft v5, 2026-10-11 03:20 JST, explicitly **unfrozen**.
- Additional reviewed artifacts: `scripts/cr1_null_calibration.py` (blob `8f22c09cbb56585e82ff464ef2b84506eb344d85`), `reports/cr1_null_calibration.txt` (blob `ce6e2d6040948f6fb1cac0902962a3d231d9eebf`), and previous P1–P5 / A1–A5 reviews.
- **Verdict: PASS WITH REPAIRS — NOT FREEZE-READY**. Earliest material issue: introductory/主0/主1 statements identify two *different null hypotheses* as one "zero-effect world" (detailed Q1). Followed by an undefined permutation statistic and incomplete calibration (Q2–Q3).
- Scope: mathematical and preregistration design review; synthetic calibration sources read, **not independently rerun**; no real Claude API runs or result audit, no direct amendment or owner decision.

## I. Repair accounting against previous independent reports

- P1 (high AUROC under true no-effect from heteroskedastic noise): **major genuine advance**. New within-cut conditional permutation (hypergeometric) fixes the group membership and total changed answers, redoes `d_s`, pooled positive top-15% labels and within-item AUROC each iteration. Correct conditioning can account for m-dependent sampling variance *under its stated exchangeability null*. Synthetic report shows null-case AUROC ~0.69–0.74 and rejection frequencies roughly near nominal; this is relevant negative-control evidence but not a general proof of calibration after all gates.
- P2 (u ties / MH strata): **resolved in design** with value-based bins and explicit undefined test route.
- P3 (request terminal statuses vs 90% coverage): **resolved in design**. Missing results, max_tokens responses, retry bookkeeping separated.
- P4 (主2 conditional set): **resolved with explicit scope**; report comparison set and original AUROC on both supports.
- P5 (protocol/software/parser/seed/priority): **largely resolved**. Exact model ID, regex, SHA and numeric seeds; actual parser and API execution still require G0–G3 checks.
- A1 (tail label stability): **resolved as diagnostic** (two-half kappa/Jaccard).
- A2 (readout failure): **resolved in design** (20% fail guard, >5% caveat, S8 sensitivity).
- A3 (audit fails): **resolved in design** (fail/no confirmatory verdict, extra re-audit sample).
- A4 (cost): **substantially improved**, G1b preflight and bounded batches; actual token/cost estimate is still uncertain.
- A5 (whitespace/empty/ties): **substantially improved**, explicit parser and deterministic ties.

## II. Remaining load-bearing repairs

### Q1 [BLOCKING: semantic identification] 主0の「効果ゼロ」と主1の陰性対照の帰無仮説が違う

For position w, let q_diff(w) be the probability of changed final answer given a diverging next prefix from P_(w−1); q_same(w) the analogous probability given startswith(s_w); and q_keep(w) the probability on **independent regeneration conditioned by API assistant prefill P_w**.

- The primary stratified estimand is `d_s = m (q_diff − q_keep)`, and 主0 checks an aggregate of `g = q_diff − q_keep`.
- The new **within-cut permutation** null is `H_perm: q_diff = q_same` (changed flags exchangeable between diff/same within cut), **not** `H_g: q_diff = q_keep` or `d_s=0`.

The discrepancy is precisely the original prefix-conditioned-law problem acknowledged by v3/v4: `q_same` need not equal `q_keep` because startswith-on-completion and directly forced prefix are not proven to induce the same distribution.

Numerical counterexample: `m=0.4, q_diff=q_same=0.5, q_keep=0.1`. Then `H_perm` holds yet `g=0.4`, `d_s=0.16`, `r=0.24` and `d=0.40`. Main0 could pass while the permutation rejects nothing. Conversely, `q_diff=q_keep=0.5, q_same=0.1` gives `g=0` but `H_perm` is false. Therefore the claims "effect zero world" and "no divergent-token effect" cannot silently swap between these comparators.

**Minimal repair**: precisely name two hypotheses and separate results. E.g., 主0: observational difference `q_diff−q_keep`, without causal claim; 主1 control: *within-cut exchangeability of changed-answer flags between diff/same groups, conditional on observed counts and the cutoff prefixes*. State that rejecting permutation H0 **does not by itself** prove `d_s` measures a causal effect of forced prefix or that `u` knows the outcome-sensitive part rather than only m. Modify opening plain-language, labels `BEYOND_NO_EFFECT_NULL` (or add unambiguous gloss), synthetic-report interpretation and discussion accordingly. Optionally treat `q_same−q_keep` mismatch in C1 as the scope boundary, without reasserting zero residual.

### Q2 [BLOCKING: formal p-value] Undefined/null AUROC handling is missing

Definition 主1 resamples **all labels**, and reselects AUROC-eligible items for each null permutation. Some permutations can leave no eligible items (or below the nominal 30-item gate), particularly if effects are sparse and ties are large. Neither the paper nor the calibration script specifies an appropriate statistic in those cases. The calibration script's `item_mean_auroc` returns `np.nan` if no eligible items, and compares `null >= obs`; `np.nan >= obs` is false, incorrectly counting such null replicates as *not* exceeding observed, and can make p anti-conservative. The gate of ≥30 eligible observed items does **not** guarantee ≥30 eligible null items.

**Minimal repair**: prespecify a **finite scalar test statistic for every possible rearrangement** (including zero eligible items) or an exact conditional randomization scheme with a well-defined admissible sample space. Make the synthetic calibration code fail loudly on undefined values until policy is fixed. If the null statistic uses an eligibility count or a minimum N threshold, specify this identically for observed and null replicates, and verify conditional calibration. Do not silently drop NaNs or treat them as non-exceedances. Clarify whether the post hoc eligibility gate is ancillary to the conditional randomization test and whether the p-value is to be read unconditionally (selection may alter the conditional-on-pass reference law).

### Q3 [IMPORTANT: control simulation scope] Calibration script does not simulate the full gating/adjacent-cut pipeline

`scripts/cr1_null_calibration.py` simulates `qkeep = Binomial(B,q)/B` independently of each cut's `xd, X` (whereas in the real protocol `q_keep(w)=q(w)` is calculated from the **same** batch of samples as the total-changed count `X(w)` for the adjacent cut). It also simulates only the main1 AUROC/permutation, not 主0's bootstrap lower-CI gate, >5% positive proportion, min30 eligible items, readout guard, missingness rules, or sample-dependent G1b selection. Thus the displayed rates ~0.033–0.067 are evidence for the scripted **simplified null experiment**, not a demonstrated type-I error for the *entire* pre-registered CR-1 decision flow.

**Minimal repair**: avoid saying full-protocol type-I error has been validated. If exact pipeline validity is claimed, run a small synthetic end-to-end check with adjacent q(c)/qkeep sharing and all selection/eligibility rules. Existing script can remain as an independent unit-test for the within-cut permutation but cannot certify the whole confirmatory procedure.

### Q4 [IMPORTANT: scope / interpretation] The current significance is for **association in the sampled continuation**, not evidence of causal token intervention

Even if Q1 is fixed, `starts_with(s_w)` is a post-generation classification, while `q_keep` is conditional on a forced assistant prefill. The conditional permutation can test whether the endpoint label is associated with that observed prefix event under within-cut exchangeability. It does not randomize the initial string; hidden states, tokenization and prefix-content correlations can explain association. `BEYOND_NO_EFFECT_NULL` needs a glossary avoiding stronger causal claims. This is a clarification, not a demand for costly new models.

### Q5 [OPERATIONAL] Priority and feasibility details

- Null permutation RNG, tie-breaking included-all, and fixed eligibility rules are mostly clear. In G3, two runs of the **same** seeded null routine verify determinism but not independent correctness; add a small reference implementation (hypergeometric counting vs literal permutation) or known toy exact-enumeration case.
- G1b dynamically drops high-number templates if cost estimate exceeds $90, which is predefined and based on baseline-output lengths, not main outcomes. Record the actual selected N, which templates were dropped and that inference is conditional on preflight eligibility; no post-G2 resize.
- C2 half-split positive-label kappa and null-control calibration are complementary: neither is a substitute for the other.
- Freeze checklist should include generated requests manifest (IDs and prefix hashes), calibration implementation version, and explicit auditor coverage for x_diff/ X and randomized test null statistic; consider privacy of private benchmarks.

## III. Recommendation

1. Resolve **Q1** by distinguishing `H_perm` vs `H_g` and narrowing claims. No additional paid experiment needed.
2. Resolve **Q2** formally (defined scalar permutation statistic and calibration including degeneracy).
3. Correct **Q3** synthetic-validation wording or add a modest synthetic end-to-end test.
4. Polish Q4/Q5, then seek separate owner decisions and authorization to freeze. **Do not let iterations become infinite**: Q4/Q5 are mostly scope and operational notes once Q1/Q2 are fixed.

**Final: PASS WITH REPAIRS, earliest failing design point = prose "zero effect" / 主0 vs 主1 null mismatch, plus Q2 undefined randomization statistic. NOT OWNER FROZEN.** No API experiments were conducted by this reviewer. No edits to the gate draft.
