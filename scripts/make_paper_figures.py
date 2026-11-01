"""Figures for paper/draft_en.md, drawn only from the frozen result files in reports/.

PRIVATE UNPUBLISHED RESEARCH.

Usage: python3 scripts/make_paper_figures.py            (writes paper/figures/fig{1..6}.{pdf,png} and figure_data.json)

Every plotted number is read from reports/dp3..dp9_RESULT.json and reports/r1_RESULT.json (post hoc); nothing is typed
in by hand. figure_data.json lists
the exact values (and their JSON paths) so the captions can be checked against it.
Palette: reference categorical slots 1-3 (blue #2a78d6, orange #eb6834, aqua #1baf7a), validated with the dataviz skill's
validate_palette.js (light mode, all checks pass); marker shape is a second encoding for grayscale print.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "paper" / "figures"
BLUE, ORANGE = "#2a78d6", "#eb6834"          # resampling side / forced-swap side
AQUA = "#1baf7a"                              # forced swap to a probability-matched token (DP7)
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
NEUTRAL = "#b9b8b3"                           # reference bars ("share of all positions")

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8, "axes.edgecolor": INK2,
    "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.8,
    "savefig.dpi": 300, "pdf.fonttype": 42, "ps.fonttype": 42,
})


def load(name):
    d = json.loads((REPO / "reports" / name).read_text())
    return d.get("analysis", d)


DP3, DP4, DP5, DP6, DP7 = (load(f"dp{i}_RESULT.json") for i in (3, 4, 5, 6, 7))
R1 = load("r1_RESULT.json")                   # post hoc (frozen plan b1646b3a)
DP8 = load("dp8_RESULT.json")                 # pre-registered rarity bridge (gate 0493790)
DP9 = load("dp9_RESULT.json")                 # pre-registered replication in Qwen2.5-7B-Instruct (gate 241a3f6)
DATA = {}


def val(tag, block, path):
    """Record a (value, ci) pair with its JSON path, for figure_data.json."""
    v = block
    for k in path:
        v = v[k]
    if isinstance(v, dict) and "within_item_auroc" in v:
        out = (v["within_item_auroc"], tuple(v["ci"]))
    else:
        out = v
    DATA[tag] = {"value": out, "source": "/".join(str(p) for p in path)}
    return out


def style_auroc_axis(ax, lo=0.2, hi=1.0):
    ax.set_ylim(lo, hi)
    ax.axhline(0.5, color=MUTED, lw=0.9, ls=(0, (4, 3)), zorder=0)
    ax.yaxis.grid(True, color=GRID, lw=0.6, zorder=-1)
    ax.set_axisbelow(True)


def errpoint(ax, x, v, color, marker, filled=True, label=None, z=3):
    m, (lo, hi) = v
    ax.errorbar([x], [m], yerr=[[m - lo], [hi - m]], fmt="none", ecolor=color, elinewidth=1.3, capsize=2.6,
                capthick=1.3, zorder=z)
    ax.plot([x], [m], marker=marker, ms=6.2, color=color, mfc=color if filled else "white", mew=1.6,
            ls="none", zorder=z + 1, label=label)


def null_band(ax, x, tag, R, w=0.13):
    """R1 main 1 (post hoc): entropy AUROC for top d_s with e_alt permuted within items; 95% range (band) and mean."""
    nb = R["MAIN1_weight_baseline"]["null_e_alt_permuted"]
    DATA[tag] = {"value": {"mean": nb["mean"], "q025": nb["q025"], "q975": nb["q975"]},
                 "source": "r1_RESULT/analysis/<DP>/MAIN1_weight_baseline/null_e_alt_permuted"}
    ax.add_patch(plt.Rectangle((x - w, nb["q025"]), 2 * w, nb["q975"] - nb["q025"], fc=NEUTRAL, ec="none", alpha=0.55,
                               zorder=1))
    ax.plot([x - w, x + w], [nb["mean"]] * 2, color=INK2, lw=1.0, zorder=1.5)


# ------------------------------------------------------------------ layout check
def text_overlaps(fig, contain=()):
    """Return pairs of visible texts whose rendered boxes overlap, plus texts that spill out of their box.

    `contain` is a list of (text, patch) pairs whose text must sit inside the patch. Used as a guard against label
    collisions; it checks text against text, not text against data marks (those are checked by eye)."""
    from matplotlib.text import Text
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    texts = [t for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()]
    boxes = [(t, t.get_window_extent(r)) for t in texts]
    bad = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            (t1, b1), (t2, b2) = boxes[i], boxes[j]
            if b1.overlaps(b2) and min(b1.x1, b2.x1) - max(b1.x0, b2.x0) > 1 and min(b1.y1, b2.y1) - max(b1.y0, b2.y0) > 1:
                bad.append(("overlap", t1.get_text(), t2.get_text()))
    for t, patch in contain:
        tb, pb = t.get_window_extent(r), patch.get_window_extent(r)
        if tb.x0 < pb.x0 + 2 or tb.x1 > pb.x1 - 2 or tb.y0 < pb.y0 + 1 or tb.y1 > pb.y1 - 1:
            bad.append(("spill", t.get_text(), "box"))
    return bad


def save(fig, stem, contain=()):
    bad = text_overlaps(fig, contain)
    assert not bad, f"{stem}: text layout problems {bad}"
    # No creation date in the PDF, so re-running the script reproduces the files byte for byte.
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight", metadata={"CreationDate": None})
    fig.savefig(OUT / f"{stem}.png", bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------ Figure 1: the two definitions (schematic)
def fig1():
    # One data unit = 0.1 inch in both directions, so box sizes can be read off the font sizes.
    fig = plt.figure(figsize=(6.9, 2.5))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 69); ax.set_ylim(0, 25); ax.axis("off")
    contain = []

    def box(x, y, w, h, text, ec=INK2, size=7.2):
        patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=0.6", fc="white", ec=ec, lw=0.9)
        ax.add_patch(patch)
        t = ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color=INK, linespacing=1.4)
        contain.append((t, patch))

    def arrow(x0, y0, x1, y1, color=INK2):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=7, lw=0.9, color=color,
                                     shrinkA=0, shrinkB=0))

    yc = 13.5
    box(0.6, yc - 2.2, 6.6, 4.4, "greedy\nprefix")
    arrow(7.6, yc, 9.3, yc)
    box(9.7, yc - 4.2, 12.0, 8.4, "position $t$\nnext-token dist. $p$\ntop token $w_1$ ($p_1$)\nrunner-up $w_2$", size=6.9)
    rows = [("keep", r"keep: fix $w_1$", INK2, 21.0), ("swap", r"swap: force $w_2$", ORANGE, 16.0),
            ("free", r"free: sample from $p$", BLUE, 11.0), ("alt", r"alt: sample, $w_1$ excluded", BLUE, 6.0)]
    for lab, text, col, y in rows:
        arrow(22.1, yc, 24.4, y, color=col)
        box(24.8, y - 1.6, 15.6, 3.2, text, ec=col)
        arrow(40.8, y, 42.6, y, color=col)
        ax.text(43.0, y, rf"$q_\mathrm{{{lab}}}$", fontsize=8, va="center", color=INK)
    ax.text(0.6, 1.3, "q: probability that the final answer differs from the greedy answer, estimated per branch from 32"
            " continuations at T = 1.0.", fontsize=6.6, color=INK2, va="center")
    ax.plot([48.0, 48.0], [3.5, 23.5], color=GRID, lw=1.0)
    cx = 58.5
    ax.text(cx, 21.6, "forced swap", fontsize=8, weight="bold", color=ORANGE, ha="center", va="center")
    ax.text(cx, 18.9, r"$e = q_\mathrm{swap} - q_\mathrm{keep}$", fontsize=8, ha="center", va="center")
    ax.text(cx, 14.0, "resampling", fontsize=8, weight="bold", color=BLUE, ha="center", va="center")
    ax.text(cx, 11.3, r"$d = q_\mathrm{free} - q_\mathrm{keep}$", fontsize=8, ha="center", va="center")
    ax.text(cx, 8.6, r"$\;\;\, = (1 - p_1)\,(q_\mathrm{alt} - q_\mathrm{keep})$", fontsize=8, ha="center", va="center")
    ax.text(cx, 5.4, "estimated from keep + alt\n(the stratified drop $d_s$)", fontsize=6.6, ha="center", va="center",
            color=INK2, linespacing=1.35)
    save(fig, "fig1_definitions", contain)


# ------------------------------------------------------------------ Figure 2: the reversal
def fig2():
    xs = [0, 1.15, 2.3, 3.45, 4.6, 6.1]
    e = [val("fig2/DP3/top_e", DP3, ["MAIN1_entropy_top_d_vs_top_e", "second"]),
         val("fig2/DP4/top_e", DP4, ["MAIN2_entropy_top_e"]),
         val("fig2/DP5/top_e", DP5, ["MAIN2_entropy_top_e"]),
         val("fig2/DP7/top_e2", DP7, ["MAIN2_entropy_top_e2"]),
         val("fig2/DP9/top_e", DP9, ["MAIN1_auroc_top_e"]),
         val("fig2/DP6/top_e", DP6, ["MAIN2_entropy_top_e"])]
    d = {0: val("fig2/DP3/top_d_plain", DP3, ["MAIN1_entropy_top_d_vs_top_e", "first"]),
         1: val("fig2/DP4/top_d_s", DP4, ["MAIN1_entropy_top_ds_vs_top_ealt", "first"]),
         2: val("fig2/DP5/top_d_s", DP5, ["MAIN1_entropy_top_ds_vs_top_ealt", "first"]),
         4: val("fig2/DP9/top_d_s", DP9, ["MAIN2B_auroc_top_d_s"]),
         5: val("fig2/DP6/top_d_s", DP6, ["MAIN1_entropy_top_ds_vs_top_ealt", "first"])}
    et = val("fig2/DP7/top_e_tau", DP7, ["MAIN1_entropy_top_e_tau"])
    fig, ax = plt.subplots(figsize=(6.9, 3.0))
    style_auroc_axis(ax, 0.1, 1.0)
    for i, name in ((1, "DP4"), (2, "DP5"), (5, "DP6")):  # R1 predates DP9: no band there
        null_band(ax, xs[i] - 0.13, f"fig2/{name}/weight_only_null", R1[name])
    for i, x in enumerate(xs):
        if i in d:
            errpoint(ax, x - 0.13, d[i], BLUE, "o", filled=(i > 0))
        errpoint(ax, x + (0.13 if i != 3 else -0.13), e[i], ORANGE, "s")
    errpoint(ax, xs[3] + 0.13, et, AQUA, "^")
    ax.annotate(r"plain $d$", (xs[0] - 0.13, d[0][0]), xytext=(14, 18), textcoords="offset points", fontsize=7,
                color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax.axvline(5.35, color=MUTED, lw=0.8, ls=":")
    ax.text(2.3, 1.005, "arithmetic (GSM-Symbolic)", ha="center", va="bottom", fontsize=7.5, color=INK2,
            transform=ax.get_xaxis_transform())
    ax.text(6.1, 1.005, "name lookup", ha="center", va="bottom", fontsize=7.5, color=INK2,
            transform=ax.get_xaxis_transform())
    # * DP3: the comparison with 0.5 was post hoc (DP3-X1); DP4-DP9 tested top e against 0.5 under pre-registration.
    ax.set_xticks(xs, ["DP3*\nOLMo-2 1B", "DP4\nOLMo-2 1B", "DP5\nGemma-2-2b-it", "DP7\nGemma-2-2b-it",
                       "DP9\nQwen2.5-7B", "DP6\nGemma-2-2b-it"])
    ax.set_xlim(-0.5, 6.6)
    ax.set_ylabel("entropy, within-item AUROC")
    ax.text(5.27, 0.505, "chance", fontsize=7, color=MUTED, ha="right", va="bottom")
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    handles = [Line2D([], [], marker="o", ms=7, color=BLUE, ls="none", label=r"resampling drop, top $d$ (hollow: plain)"),
               Patch(fc=NEUTRAL, ec="none", alpha=0.55, label=r"$e_\mathrm{alt}$ shuffled within items (post hoc)"),
               Line2D([], [], marker="s", ms=7, color=ORANGE, ls="none", label=r"forced swap to $w_2$, top $e$"),
               Line2D([], [], marker="^", ms=7, color=AQUA, ls="none", label=r"forced swap, $p \approx 10^{-6}$, top $e_\tau$")]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.24), frameon=False, ncol=2,
              handletextpad=0.3, columnspacing=1.5)
    save(fig, "fig2_reversal")


# ------------------------------------------------------------------ Figure 3: the weighting
def fig3():
    xs = [0, 1, 2, 3.4]
    names = [("DP4", DP4), ("DP5", DP5), ("DP9", DP9), ("DP6", DP6)]
    fig, ax = plt.subplots(figsize=(5.4, 2.8))
    style_auroc_axis(ax, 0.1, 1.0)
    for i, (n, R) in enumerate(names):
        key = "MAIN2_auroc_top_d_s_minus_top_e_alt" if n == "DP9" else "MAIN1_entropy_top_ds_vs_top_ealt"
        ea = val(f"fig3/{n}/top_e_alt", R, [key, "second"])
        ds = val(f"fig3/{n}/top_d_s", R, [key, "first"])
        val(f"fig3/{n}/diff", R, [key, "first_minus_second"])
        x0, x1 = xs[i] - 0.15, xs[i] + 0.15
        if n != "DP9":  # R1 (post hoc) predates DP9
            null_band(ax, x1, f"fig3/{n}/weight_only_null", R1[n])
        ax.add_patch(FancyArrowPatch((x0 + 0.04, ea[0]), (x1 - 0.04, ds[0]), arrowstyle="-|>", mutation_scale=8,
                                     lw=0.9, color=MUTED, zorder=2))
        errpoint(ax, x0, ea, ORANGE, "D", label=r"effect of a sampled alternative, top $e_\mathrm{alt}$" if i == 0 else None)
        errpoint(ax, x1, ds, BLUE, "o", label=r"weighted by $(1 - p_1)$: top $d_s$" if i == 0 else None)
    ax.axvline(2.7, color=MUTED, lw=0.8, ls=":")
    ax.set_xticks(xs, ["DP4\nOLMo-2 1B", "DP5\nGemma-2-2b-it", "DP9\nQwen2.5-7B", "DP6\nGemma-2-2b-it\n(name lookup)"])
    ax.set_xlim(-0.5, 3.9)
    ax.set_ylabel("entropy, within-item AUROC")
    from matplotlib.patches import Patch
    hs, ls = ax.get_legend_handles_labels()
    hs.append(Patch(fc=NEUTRAL, ec="none", alpha=0.55)); ls.append(r"$e_\mathrm{alt}$ permuted within items (post hoc)")
    ax.legend(hs, ls, loc="upper center", bbox_to_anchor=(0.5, -0.3), frameon=False, ncol=1, handletextpad=0.3)
    save(fig, "fig3_weighting")


# ------------------------------------------------------------------ Figure 5: digits vs names
def figD():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.6, 2.75), gridspec_kw={"width_ratios": [1, 1.5], "wspace": 0.38})
    # (a) share of positions vs share of top-e positions that are digit / name positions
    sd5 = val("fig5a/DP5/share_digit", DP5, ["MAIN3_top_e_share_digit_minus_nondigit", "share_digit"])
    n5, p5 = (val(f"fig5a/DP5/{k}", DP5, [k]) for k in ("digit_positions", "positions"))
    t5 = val("fig5a/DP5/top_e_positives", DP5, ["MAIN2_entropy_top_e", "positives"])
    sn6 = val("fig5a/DP6/share_name", DP6, ["MAIN3_top_e_share_name_minus_nonname", "share_in_mask"])
    n6, p6 = (val(f"fig5a/DP6/{k}", DP6, [k]) for k in ("name_positions", "positions"))
    t6 = val("fig5a/DP6/top_e_positives", DP6, ["MAIN2_entropy_top_e", "positives"])
    all_share = [n5 / p5, n6 / p6]
    top_share = [sd5 * n5 / t5, sn6 * n6 / t6]
    DATA["fig5a/derived"] = {"value": {"DP5_digit_share_of_positions": all_share[0], "DP5_digit_share_of_top_e": top_share[0],
                                       "DP5_top_e_on_digits": sd5 * n5, "DP6_name_share_of_positions": all_share[1],
                                       "DP6_name_share_of_top_e": top_share[1], "DP6_top_e_on_names": sn6 * n6},
                             "source": "rate (share_digit / share_in_mask) × mask positions / MAIN2_entropy_top_e.positives"}
    w = 0.34
    for j, (a, t) in enumerate(zip(all_share, top_share)):
        ax1.bar(j - w / 2 - 0.01, a * 100, w, color=NEUTRAL, edgecolor="white", lw=1.5,
                label="among all positions" if j == 0 else None)
        ax1.bar(j + w / 2 + 0.01, t * 100, w, color=ORANGE, edgecolor="white", lw=1.5,
                label=r"among top-$e$ positions" if j == 0 else None)
        ax1.text(j - w / 2 - 0.01, a * 100 + 1.5, f"{a * 100:.0f}%", ha="center", fontsize=7.2, color=INK2)
        ax1.text(j + w / 2 + 0.01, t * 100 + 1.5, f"{t * 100:.0f}%", ha="center", fontsize=7.2, color=INK)
    ax1.set_xticks([0, 1], ["DP5 digits\n(arithmetic)", "DP6 names\n(name lookup)"])
    ax1.set_ylim(0, 80); ax1.set_ylabel("% that are digit / name positions")
    ax1.yaxis.grid(True, color=GRID, lw=0.6); ax1.set_axisbelow(True)
    ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.27), frameon=False, ncol=1, handlelength=1.0)
    ax1.set_title(r"(a) composition of top-$e$ positions", loc="left", fontsize=8.5)
    # (b) entropy's AUROC for top e, all positions vs digit / name positions removed
    # † DP4: S8 is a secondary analysis listed in the frozen DP4 gate without a decision rule; reading it as a digit
    #   effect came after the run and motivated the DP5 hypothesis.
    rows = [("DP4\ndigits†", DP4, ["MAIN2_entropy_top_e"], ["S8_nondigit", "main2"]),
            ("DP5\ndigits", DP5, ["MAIN2_entropy_top_e"], ["MAIN3_top_e_nondigit_vs_all", "first"]),
            ("DP9\ndigits", DP9, ["MAIN1_auroc_top_e"], ["MAIN3_auroc_top_e_nondigit_vs_all", "first"]),
            ("DP6\nnames", DP6, ["MAIN2_entropy_top_e"], ["MAIN3_top_e_nonname_vs_all", "first"])]
    xs = [0, 1, 2, 3.3]
    style_auroc_axis(ax2, 0.15, 0.8)
    for i, (lab, R, pa, pr) in enumerate(rows):
        n = lab.split("\n")[0]
        allv = val(f"fig5b/{n}/top_e_all", R, pa)
        rem = val(f"fig5b/{n}/top_e_removed", R, pr)
        x0, x1 = xs[i] - 0.14, xs[i] + 0.14
        ax2.add_patch(FancyArrowPatch((x0 + 0.04, allv[0]), (x1 - 0.04, rem[0]), arrowstyle="-|>", mutation_scale=8,
                                      lw=0.9, color=MUTED, zorder=2))
        errpoint(ax2, x0, allv, ORANGE, "s", label="computed on all positions" if i == 0 else None)
        errpoint(ax2, x1, rem, ORANGE, "s", filled=False, label="digit / name positions removed" if i == 0 else None)
    ax2.axvline(2.65, color=MUTED, lw=0.8, ls=":")
    ax2.set_xticks(xs, [r[0] for r in rows]); ax2.set_xlim(-0.5, 3.8)
    ax2.set_ylabel(r"entropy, within-item AUROC (top $e$)")
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.27), frameon=False, ncol=1, handletextpad=0.3)
    ax2.set_title(r"(b) top-$e$ AUROC with them removed", loc="left", fontsize=8.5)
    save(fig, "fig5_digits_names")


# ------------------------------------------------------------------ Figure 4: the probability-matched swap (DP7)
def figM():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.6, 2.75), gridspec_kw={"width_ratios": [1, 1.15], "wspace": 0.36})
    s1 = val("fig4a/DP7/S1", DP7, ["S1_entropy_tertiles"])
    xs = [0, 1, 2]
    e2 = [r["mean_e2"] for r in s1]; et = [r["mean_e_tau"] for r in s1]
    ax1.plot([x - 0.09 for x in xs], e2, marker="s", ms=6.2, color=ORANGE, lw=1.2, label=r"swap to $w_2$: mean $e$")
    ax1.plot([x + 0.09 for x in xs], et, marker="^", ms=6.2, color=AQUA, lw=1.2,
             label=r"swap to $p \approx 10^{-6}$: mean $e_\tau$")
    ax1.set_xticks(xs, ["lowest", "middle", "highest"]); ax1.set_xlim(-0.4, 2.4)
    ax1.set_xlabel("entropy tertile at the position")
    ax1.set_ylim(0, 0.3); ax1.set_ylabel("mean effect on the answer")
    ax1.yaxis.grid(True, color=GRID, lw=0.6); ax1.set_axisbelow(True)
    ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.3), frameon=False, ncol=1, handletextpad=0.3)
    ax1.set_title("(a) effects by entropy tertile", loc="left", fontsize=8.5)
    s4 = val("fig4b/DP7/S4", DP7, ["S4_tau_token_kinds"])
    groups = [("digit_positions", "greedy token:\na digit"), ("non_digit_positions", "greedy token:\nnot a digit")]
    kinds = [("digit", "digit"), ("other", "other"), ("space", "space")]
    w = 0.26
    for g, (gk, glab) in enumerate(groups):
        for k, (kk, klab) in enumerate(kinds):
            r = s4[gk][kk]
            x = g + (k - 1) * (w + 0.03)
            ax2.bar(x, r["top_e_tau_rate"] * 100, w, color=AQUA, edgecolor="white", lw=1.2,
                    alpha=(1.0, 0.7, 0.45)[k])
            ax2.text(x, r["top_e_tau_rate"] * 100 + 2.0, f"{r['top_e_tau_rate'] * 100:.0f}%", ha="center", fontsize=6.8,
                     color=INK)
            ax2.text(x, -4.0, f"{klab}\nn={r['positions']}", ha="center", va="top", fontsize=6.3, color=INK2,
                     linespacing=1.15)
    ax2.set_xticks([0, 1], [""] * 2)
    for g, (gk, glab) in enumerate(groups):
        ax2.text(g, -21, glab, ha="center", va="top", fontsize=7.6, color=INK)
    ax2.set_ylim(0, 90); ax2.set_xlim(-0.55, 1.55)
    ax2.set_ylabel(r"% of positions in top $e_\tau$")
    ax2.yaxis.grid(True, color=GRID, lw=0.6); ax2.set_axisbelow(True)
    ax2.set_title(r"(b) by kind of swapped-in token", loc="left", fontsize=8.5)
    save(fig, "fig4_matched_swap")


def figR():
    """DP8: (a) mean effect of the three alternatives by rarity band; (b) where the natural answer variation comes from."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.6, 2.85), gridspec_kw={"width_ratios": [1.35, 1], "wspace": 0.34})
    s1 = val("fig6a/DP8/S1", DP8, ["S1_by_bin"])
    labs = ["≤10⁻⁴", "≤10⁻³", "≤10⁻²", "≤0.05", "≤0.2", ">0.2"]   # upper edge of each band (lower edge = previous)
    xs = list(range(len(s1)))
    series = [("e_alt", BLUE, "o", r"natural alternative: $e_{alt}$", -0.18),
              ("e2", ORANGE, "s", r"runner-up forced: $e$", 0.0),
              ("e_tau", AQUA, "^", r"$p \approx 10^{-6}$ forced: $e_\tau$", 0.18)]
    for key, col, mk, lab, dx in series:
        for i, row in enumerate(s1):
            r = row["all"][key]
            lo, hi = r["ci"]
            ax1.errorbar(i + dx, r["mean"], yerr=[[r["mean"] - lo], [hi - r["mean"]]], fmt=mk, color=col, ms=5.2,
                         elinewidth=1.0, capsize=0, label=lab if i == 0 else None, zorder=3)
    ax1.axhline(0, color=MUTED, lw=0.7, ls="--", zorder=1)
    ax1.set_xticks(xs, labs, fontsize=7.2)
    ax1.set_xlabel(r"band of $r = 1 - p_1$ (chance that an alternative is sampled)")
    ax1.set_ylabel("mean effect on the answer")
    ax1.set_ylim(-0.05, 0.40)
    ax1.yaxis.grid(True, color=GRID, lw=0.6); ax1.set_axisbelow(True)
    ax1.legend(loc="upper right", frameon=False, handletextpad=0.3, fontsize=7.2)
    ax1.set_title("(a) effect when an alternative occurs", loc="left", fontsize=8.5)
    s6 = val("fig6b/DP8/S6", DP8, ["S6_d_s_by_bin"])
    shares = [r["share"] * 100 for r in s6]
    ax2.bar(xs, shares, 0.62, color=BLUE, edgecolor="white", lw=1.0)
    for i, v in enumerate(shares):
        ax2.text(i, max(v, 0) + 2.5, f"{v:.0f}%" if abs(v) >= 10 else f"{v:.1f}%", ha="center", fontsize=6.8, color=INK)
    ax2.axhline(0, color=MUTED, lw=0.7)
    ax2.set_xticks(xs, labs, fontsize=6.4)
    ax2.set_xlabel(r"band of $r$")
    ax2.set_ylabel(r"share of $\sum d_s$ (%)")
    ax2.set_ylim(-5, 85); ax2.set_yticks([0, 20, 40, 60, 80])
    ax2.yaxis.grid(True, color=GRID, lw=0.6); ax2.set_axisbelow(True)
    ax2.set_title(r"(b) contribution to answer variation", loc="left", fontsize=8.5)
    save(fig, "fig6_rarity")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig1(); fig2(); fig3(); figM(); figD(); figR()
    (OUT / "figure_data.json").write_text(json.dumps(DATA, indent=1, ensure_ascii=False) + "\n")
    print("wrote", sorted(p.name for p in OUT.iterdir()))
