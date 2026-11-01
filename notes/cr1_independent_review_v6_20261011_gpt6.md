# CR-1 第6版：最終候補の独立監査（GPT-6）

PRIVATE UNPUBLISHED RESEARCH — REVIEW ONLY; NOT AN OWNER FREEZE.

- Repo/branch: `chichichi2001/Pork`, `decision-points`
- Source: `notes/cr1_claude_resample_gate.md` / blob SHA `b73602237aa81b40567eee8ecc3c307194d2fdd6`
- Source revision: Draft v6, 2026-10-11 12:30 JST; explicitly **unfrozen**
- Additional inputs read: `scripts/cr1_e2e_calibration.py` blob `2c4eaf314c026bd710db73dc60bbfb76e61713db`, `reports/cr1_e2e_calibration.txt` blob `860d5c03ff3053c9e577ac9b75974d571e548898`; v5 audit and v4 reviews.
- **Verdict: PASS WITH ONE LOCAL REPAIR. Mathematical/statistical design judged provisionally PASS within the explicitly limited scope; NOT YET OPERATIONALLY FREEZE-READY due to one chronological contradiction in the freeze checklist.**
- Earliest remaining blocking point: **`凍結時に埋めること` item requiring SHA of the full request/prefix manifest generated only after G0/G1/G1b**.
- This reviewer read code and reported simulation results but **did not independently execute the calibration script**, nor run an API experiment or validate the future notebook implementation. No owner decisions or freeze actions taken.

## 1. Prior Q1–Q5 repair results

- **Q1 PASS.** Hypotheses distinguished: `H_perm` is within-cut exchangeability of endpoint-change labels between generated-branch `starts_with(s_w)` vs not; `g=q_diff−q_keep` compares an entirely different forced-prefix population. The difference `r=(1−m)(q_same−q_keep)` is reported descriptively. No causal claims.
- **Q2 PASS.** Main1 permutation uses a finite scalar `T=(1/N) sum_i A_i` where `A_i` is within-item AUROC if both classes occur and `0.5` otherwise; this is recomputed on every permutation. NaN explicitly halts. Main1 observed-eligible mean is distinguished from T. Conditional randomization p-value based on hypergeometric counts is valid under its **within-cut exchangeability** null, conditional on labels' observed per-cut totals and the partition, assuming independent identically configured replicates within each cut. The optional decision to test only after data-dependent gates cannot increase the *unconditional* probability of a false BEYOND label beyond the level of a valid unconditionally assessed test, though error conditional on passing gates need not be ≤5%.
- **Q3 PASS within scope.** New synthetic end-to-end script reuses the same cut-level samples to form `q(c)` and the adjacent `q_keep`, evaluates 主0, positive-share, min30-eligible gates and T. The reported synthetic `H_perm` cases have rejection rates near .05, including `H_perm` true but `g>0`. No confirmation of all operational modes: G1b, unreadable responses, missing requests and true first-unit heterogeneity are explicitly omitted. This remains a reported simulation outcome, not an independently replayed result.
- **Q4 PASS.** Descriptions of detected associations vs noncausal prefix contrasts appropriately limited.
- **Q5 PASS in design apart from the one freeze-phase dependency below.** Regex/Unicode parse, model ID, seeds, request tracking, exact enumerated toy and separate reference implementation audits, incomplete/stop semantics, budget check and owner choices largely defined. Implementation details are prospective.

## 2. F1 [ONE LOCAL BLOCKER] Impossible ordering of the request-manifest SHA at owner freeze

The protocol explicitly says: owner approves and freezes the full draft, THEN **G0** (technical smoke test) and **G1** (sampled baseline paths) and **G1b** (preflight selection/drop templates), THEN **G2** submits continuation requests. Yet the section `凍結時に埋めること` requires the **SHA of the complete request manifest** (`custom_id`, SHA256 of each assistant-prefill string).

That full manifest cannot ordinarily be generated at owner-freeze time:
1. The precise `P_c` strings depend on **G1's API-generated baseline paths**, which do not exist until after G0/G1.
2. The final chosen item set and request list may shrink at **G1b** due to the precommitted cost reduction rule.
3. The branch between temperature-0 and default-temperature baseline generation is only selected at **G0**.
Thus the checklist imposes a later artifact as an earlier prerequisite. A promise to compute a hash later is not the same as already knowing/filling the hash in the owner-frozen document.

**Minimal repair (no extra paid experiment): establish two phases.**
- **Owner-freeze, pre-G0:** fix algorithm, seeds, sampling/selection rule, comparator definitions, label/verdict rules, cost cap, code/calibration versions (as available), expected input/exclusion source hashes, and a mandatory **future** request-manifest SHA step. Do **not** require the actual `P_c`-dependent hash here.
- **After G1b and BEFORE first G2 submission:** deterministically generate the full request manifest from frozen rules, compute SHA256 of the manifest and item set, record API/SDK version and applied branch, store it in a new immutable `CR1_REQUEST_MANIFEST_LOCK` / pre-G2 provenance artifact with a timestamp, link it from the main trial log; prohibit any G2 submission if lock is absent or has inconsistent hashes. This is a prospective execution/provenance lock, not a retroactive edit to the frozen protocol. This artifact can disclose hashes only, preserving benchmark privacy.
- Any deviation in rules requires an amendment **before seeing main G2 outcomes**, with owner approval; do not edit the frozen original.

If desired, move source/exclusion hashes and code SHA to whichever pre-freeze stage they can actually be computed, with future steps explicitly defined in advance. This fixes the temporal contradiction without additional outcome analysis or widening the study.

## 3. Nonblocking interpretation/implementation notes

- The conditional-exchangeability null presumes exchangeability of B responses **within each identical cut/prompt**. Equality of two marginal changed-answer frequencies alone is weaker without independent identically distributed replicates. Keep this qualification in the report.
- Finite-sample `d_s>0`, top15%, and `u` still have measurement noise, but the new negative control specifically calibrates high observed T under `H_perm`. The null test is NOT a proof `u` is informative beyond m, nor of forced-token causal effects, as v6 now correctly states.
- G1b's reduction of N by template number is prospective and outcome-blind; make its executed selection reproducible and record exactly which templates were dropped.
- G2's max-cost/remaining-cost guard may lead to an honest incomplete run even within nominal $90 total spend; no confirmatory verdict after stopping is an acceptable pre-registered result.
- Step 7 of the "priority order" adds C2 caveats; it is an annotation stage, not a terminal verdict and can be worded as such.
- G3's exact toy verification and Monte Carlo calibration are specified, but will be validated only after implementation.

## 4. Final

**Design PASS conditional on F1 local two-phase lock repair. This is a finite, documentary pre-freeze repair, not a new statistical research problem.** After F1 and the owner's explicit selections [1–5], a controlled freeze is reasonable; subsequent feasibility, implementation and full data audits remain separate gates. Neither source plan nor freeze status changed; no API calls or owner freeze performed.
