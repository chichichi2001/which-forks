"""Recompute entropy's within-item AUROC (Table 2 of the paper) from reports/r1_TABLES.json.

Usage:  python scripts/recompute_table2.py            (standard library only; runs in a few seconds)
        python scripts/recompute_table2.py --boot     (adds 95% bootstrap intervals, 2,000 resamples of templates)

Definitions follow paper/draft_en.md, section 2 ("Evaluation"):
- label = top 15% of all positions in an experiment (pooled across items) by the effect
  (e for the forced swap; d_s for the stratified resampling drop, plain d in DP3);
  count rounded down; ties at the cut broken by item order, then position;
- score = next-token entropy at the position;
- within-item AUROC = AUROC computed per item that has both classes, averaged with equal weight per item.

Covers DP3-DP6, the experiments whose per-position records are in r1_TABLES.json. The per-position records
of DP7 and DP9 are not in this repository, so their rows are not recomputed here.
"""
import hashlib
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "reports" / "r1_TABLES.json"

# Values printed in Table 2 of the paper (rounded to 3 decimals).
PAPER = {
    ("DP3", "e"): 0.415, ("DP3", "d"): 0.558,
    ("DP4", "e"): 0.378, ("DP4", "d_s"): 0.887,
    ("DP5", "e"): 0.286, ("DP5", "d_s"): 0.858,
    ("DP6", "e"): 0.574, ("DP6", "d_s"): 0.860,
}


def auroc(scores, labels):
    """Mann-Whitney AUROC with ties counted as 1/2."""
    pos = [s for s, l in zip(scores, labels) if l]
    neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg:
        return None
    wins = 0.0
    for p in pos:
        for n in neg:
            wins += 1.0 if p > n else 0.5 if p == n else 0.0
    return wins / (len(pos) * len(neg))


def top_labels(rows, effect):
    """Top 15% by effect, pooled; ties broken by item order, then position."""
    ok = [i for i, r in enumerate(rows) if r[effect] is not None and r["entropy"] is not None]
    k = math.floor(0.15 * len(ok))  # frozen rule: count rounded down (notes/dp4_weighting_gate.md)
    order = sorted(ok, key=lambda i: (-rows[i][effect], rows[i]["row"], rows[i]["t"]))
    chosen = set(order[:k])
    return ok, chosen


def within_item_auroc(rows, ok, chosen, items=None):
    by_item = {}
    for i in ok:
        by_item.setdefault(rows[i]["row"], []).append(i)
    vals = []
    for item in (items if items is not None else sorted(by_item)):
        idx = by_item.get(item, [])
        a = auroc([rows[i]["entropy"] for i in idx], [i in chosen for i in idx])
        if a is not None:
            vals.append(a)
    return (sum(vals) / len(vals) if vals else None), len(vals)


def main():
    boot = "--boot" in sys.argv
    raw = SRC.read_bytes()
    print(f"source: {SRC.relative_to(ROOT)}  sha256 {hashlib.sha256(raw).hexdigest()}")
    tables = json.loads(raw)["tables"]
    print(f"{'exp':4} {'effect':6} {'items':>5} {'recomputed':>10} {'paper':>6}  {'match':5}" + ("  95% CI" if boot else ""))
    all_ok = True
    for exp in ["DP3", "DP4", "DP5", "DP6"]:
        cols = tables[exp]
        n = len(cols["row"])
        rows = [{c: cols[c][j] for c in ("row", "t", "template", "entropy", "e", "d", "d_s") if c in cols} for j in range(n)]
        for effect in (["e", "d"] if exp == "DP3" else ["e", "d_s"]):
            ok, chosen = top_labels(rows, effect)
            val, n_items = within_item_auroc(rows, ok, chosen)
            paper = PAPER[(exp, effect)]
            match = round(val, 3) == paper
            all_ok &= match
            line = f"{exp:4} {effect:6} {n_items:5d} {val:10.3f} {paper:6.3f}  {'yes' if match else 'NO':5}"
            if boot:
                # resample templates (one item per template in DP3-DP5; DP6 resamples items), labels held fixed
                unit = "row" if exp == "DP6" else "template"
                groups = {}
                for i in ok:
                    groups.setdefault(rows[i][unit], set()).add(rows[i]["row"])
                keys = sorted(groups)
                rng = random.Random(0)
                bs = []
                for _ in range(2000):
                    items = [it for g in (rng.choice(keys) for _ in keys) for it in sorted(groups[g])]
                    v, _ = within_item_auroc(rows, ok, chosen, items)
                    if v is not None:
                        bs.append(v)
                bs.sort()
                line += f"  [{bs[int(0.025 * len(bs))]:.3f}, {bs[int(0.975 * len(bs)) - 1]:.3f}]"
            print(line)
    print("all recomputed values match Table 2" if all_ok else "SOME VALUES DIFFER FROM TABLE 2")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
