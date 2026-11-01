# DP5 runtime triage — performance-only candidate (2026-10-08)

PRIVATE UNPUBLISHED. **Not a gate amendment or approval to change owner-frozen DP5.**

## Verified read-only observations

- DP5 is frozen at `notes/dp5_gemma_replication_gate.md`; code identity is part of each unit's envelope. The existing three Colab notebooks are pinned to their committed HEAD.
- `pork/dp5_runner.py:compute_point` calls `generate_batch` separately for keep, swap, alt, and free (i % 3 == 0). It always uses K=32, max 512 total tokens, t=0,8,... below answer.
- `pork/ct1_forks_replacement.py:generate_batch` runs a K-row model forward but then loops over 32 rows in Python and calls `q4b_samplers.pure_sample` separately for each active row.
- Each `pure_sample` converts the 256k-vector logits to float64, computes softmax, performs a stable full-vocabulary sort, normalizes the ranked probabilities, and samples via explicit U. This involves many per-token GPU operations and host synchronization points.
- The independent replay auditor in `pork/dp5_runner.py:audit_row` uses Python `ref_pure` and `ref_alt` for the first four samples per audited branch: that is another large full-vocabulary sort per audited step. The DP5 implementation note itself estimates notebook C's cell 8 at 3-5 hours.

## Implemented prospective change in PR #431

- `pork/dp5_fast_reference.py` computes the same original Python float probabilities and uses NumPy `argsort(..., kind='stable')` instead of a Python-level sort; original `qs._ref_draw` remains unchanged.
- DP5 runner has an opt-in `--audit --fast-audit-reference`; default is unmodified. The current three notebooks do not turn this on and must **not** be silently switched to it.
- Parity tests include ties, temperature variation, extreme U, 256000-word vocabulary, and synthetic audit output equality.
- Provenance (2026-10-08 23:4x JST): `AUDIT_<half>.json` records `audit_reference` (`python_sorted` or `numpy_stable_argsort`); `combine_audits` lists it per half (older files without the field = `python_sorted`). A future gate that uses the fast reference must name it.
- Verified: 144 checks at V = 256,000 on Gemma-like bfloat16 logits with heavy exact ties (incl. tied top, excluded top, u near 0 and 1): 0 mismatches; per call ~0.8 s → ~0.29 s (≈2.8×). Estimated Cell 8: B 2–3 h → ~1 h, C 3–5 h → ~1.2–2 h.
- A single-machine CPU benchmark is not a forecast of the Colab job's total time; the generating GPU pathway remains unchanged.

## Main cell-7 opportunity, not yet implemented

The likely high-leverage future option is a batched GPU sampler: perform K-row probability normalization, stable descending order, cumulative sums, and explicit-U token selection with 2D tensors, rather than 32 serial per-row Python calls each step.

**Do not enable on DP5 or treat it as equivalent yet.** Floating-point reductions, stable tie resolution, last-token fallback, alternate first-token exclusion, bfloat16 batch numerics, and GPU determinism all need proof by tests. Candidate validation sequence:

1. Synthetic logits on the actual L4 GPU: 2k and 256k vocabulary, extensive ties, very small probabilities, U=0, interior U, U nearly 1, alt exclusion, all 32 rows. Require all chosen token IDs equal the frozen reference.
2. Hold generated logits fixed and replay the full per-row sample schedule, checking the token ID and every RNG uniform are unchanged; compare hash of token arrays.
3. Small non-scored Gemma real-prefill smoke: compare memory and throughput over 32-128 steps; repeat across short and long prefixes, EOS-heavy and EOS-light paths.
4. Gate E2, G1, B1; compare prospective 32-row complete token arrays and all audited j=0..3 records. Require exact equality before considering reuse.
5. If any differences remain, treat it as a different execution protocol requiring explicit owner approval / prospective gate; never merge into the ongoing frozen experiment.

## Operation

Continue currently running DP5 under its original `code_commit` and untouched unit files. If a future revision is approved, write it as a *new* prospective protocol with its own commit and record identity. Preserve all held-out questions, random seeds, the number of samples, labels, and all existing audit trails.
