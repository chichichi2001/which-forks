"""Build the LaTeX version of the paper from paper/draft_en.md (the Markdown draft stays the source of truth).

PRIVATE UNPUBLISHED RESEARCH.

Usage: python3 scripts/build_paper_latex.py        (writes paper/latex/main.tex and, with XeLaTeX, paper/latex/main.pdf)

Steps: a pre-pass on the Markdown (variables to math, figure and table captions, abstract, appendix, headings without
hand-written numbers), pandoc to LaTeX with scripts/paper_latex_tables.lua (table column widths), a small post-pass
(label names may break at underscores), then latexmk -xelatex. The private HTML comment at the top of the draft is
dropped. Figures are the PDF versions written by scripts/make_paper_figures.py.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "paper" / "draft_en.md"
OUT = REPO / "paper" / "latex"
AUTHOR = "Chisa Honda"
AFFIL = "Independent researcher"

L, R = "⟦", "⟧"          # math sentinels during the pre-pass; become \( \) at the end
SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
NAMES = {"keep", "swap", "swapτ", "free", "alt", "plain"}

# Display equations and dense formulas, replaced verbatim before the token pass.
DISPLAY = {
    "  q_free = p₁·q_keep + (1 − p₁)·q_alt,  so  d = (1 − p₁)(q_alt − q_keep),":
        r"$$q_{\mathrm{free}} = p_1\,q_{\mathrm{keep}} + (1-p_1)\,q_{\mathrm{alt}},\qquad\text{so}\qquad"
        r" d = (1-p_1)\,(q_{\mathrm{alt}}-q_{\mathrm{keep}}),$$",
    "q_free = Σ_v p(v)·q_v = p₁·q_keep + Σ_{v≠w₁} p(v)·q_v":
        r"⟦q_{\mathrm{free}} = \sum_v p(v)\,q_v = p_1\,q_{\mathrm{keep}} + \sum_{v\neq w_1} p(v)\,q_v⟧",
    "d = p₂·e + Σ_{v∉{w₁,w₂}} p(v)(q_v − q_keep)":
        r"⟦d = p_2\,e + \sum_{v\notin\{w_1,w_2\}} p(v)\,(q_v - q_{\mathrm{keep}})⟧",
    "Var(d_plain) ≈ [q_free(1 − q_free) + q_keep(1 − q_keep)]/K":
        r"⟦\operatorname{Var}(d_{\mathrm{plain}}) \approx [q_{\mathrm{free}}(1-q_{\mathrm{free}})"
        r" + q_{\mathrm{keep}}(1-q_{\mathrm{keep}})]/K⟧",
    "Var(d_s) ≈ (1 − p₁)²[q_alt(1 − q_alt) + q_keep(1 − q_keep)]/K":
        r"⟦\operatorname{Var}(d_s) \approx (1-p_1)^2[q_{\mathrm{alt}}(1-q_{\mathrm{alt}})"
        r" + q_{\mathrm{keep}}(1-q_{\mathrm{keep}})]/K⟧",
    "e(t) = q_swap(t) − q_keep(t)": r"⟦e(t) = q_{\mathrm{swap}}(t) - q_{\mathrm{keep}}(t)⟧",
    "e_τ(t) = q_swapτ(t) − q_keep(t)": r"⟦e_\tau(t) = q_{\mathrm{swap}\tau}(t) - q_{\mathrm{keep}}(t)⟧",
    "d(t) = q_free(t) − q_keep(t)": r"⟦d(t) = q_{\mathrm{free}}(t) - q_{\mathrm{keep}}(t)⟧",
    "q(t) − q(t+8)": r"⟦q(t) - q(t+8)⟧",
    "p₁ ≈ exp(−0.9·entropy)": r"⟦p_1 \approx \exp(-0.9\cdot\mathrm{entropy})⟧",
    "|d| ≤ 1 − p₁": r"⟦|d| \le 1-p_1⟧",
    "e ≤ 1 − q_keep": r"⟦e \le 1-q_{\mathrm{keep}}⟧",
}

# Table column widths: scripts/paper_latex_tables.lua


def var_math(m: re.Match) -> str:
    base, sub = m.group(1), m.group(2)
    if sub in NAMES:
        s = r"\mathrm{" + sub.replace("τ", "") + "}" + (r"\tau" if "τ" in sub else "")
        return f"{L}{base}_{{{s}}}{R}"
    return f"{L}{base}_{{{sub.replace('τ', chr(92) + 'tau')}}}{R}"


def outside(text: str, fn) -> str:
    """Apply fn only to the parts of text that are not already math (between the sentinels)."""
    parts = re.split(f"({L}[^{R}]*{R}|@@D\\d+@@)", text)
    return "".join(p if (p.startswith(L) or p.startswith("@@D")) else fn(p) for p in parts)


def mathify(text: str) -> str:
    stash = []
    for k, v in DISPLAY.items():
        if k in text:
            stash.append(v)
            text = text.replace(k, f"@@D{len(stash) - 1}@@")
    rules = [
        (r"log₁₀", lambda m: f"{L}\\log_{{10}}{R}"),
        (r"(\d+)([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)", lambda m: f"{L}{m.group(1)}^{{{m.group(2).translate(SUP)}}}{R}"),
        (r"(?<![A-Za-z])([pw])([₀₁₂₃₄₅₆₇₈₉]+)", lambda m: f"{L}{m.group(1)}_{m.group(2).translate(SUB)}{R}"),
        (r"(?<![A-Za-z_])([qedw])_(swapτ|keep|swap|free|alt|plain|s|v|τ)(?![A-Za-z])", var_math),
        (r"(?<![A-Za-z\\])τ", lambda m: f"{L}\\tau{R}"),
        (r"(?<![A-Za-z\\])γ", lambda m: f"{L}\\gamma{R}"),
        (r"(?<![\w.\-/`'’])([edqtKv])(?![\w.\-'’(`])", lambda m: f"{L}{m.group(1)}{R}"),
        (r"(?<![\w.\-/`])p(?=\()", lambda m: f"{L}p{R}"),
    ]
    for pat, fn in rules:
        text = outside(text, lambda t, pat=pat, fn=fn: re.sub(pat, fn, t))
    ops = {"−": "-", "+": "+", "=": "=", "·": r"\cdot ", "×": r"\times ", "≥": r"\ge ", "≤": r"\le ",
           "≈": r"\approx ", "≠": r"\neq "}
    for _ in range(6):
        text = re.sub(rf"{R}\s*([−+=·×≥≤≈≠])\s*{L}", lambda m: " " + ops[m.group(1)] + " ", text)
        text = re.sub(rf"\(1 − {L}([^{R}]*){R}\)", lambda m: f"{L}(1-{m.group(1)}){R}", text)
        text = re.sub(rf"\({L}([^{R}]*){R} − {L}([^{R}]*){R}\)", lambda m: f"{L}({m.group(1)}-{m.group(2)}){R}", text)
        text = re.sub(rf"{R}{L}", " ", text)
        text = re.sub(rf"{R}·([a-z])(?![\w])", lambda m: rf" \cdot {m.group(1)}{R}", text)
        text = re.sub(rf"(\d(?:\.\d+)?) × {L}", lambda m: f"{L}{m.group(1)}\\times ", text)
        text = re.sub(rf"{R} = (\d+(?:\.\d+)?)(?![\d,])", lambda m: f" = {m.group(1)}{R}", text)
    for i, v in enumerate(stash):
        text = text.replace(f"@@D{i}@@", v)
    return text


def protect_code(line: str, fn) -> str:
    parts = line.split("`")
    return "`".join(fn(p) if i % 2 == 0 else p for i, p in enumerate(parts))


def prepass(md: str) -> str:
    md = re.sub(r"\A<!--.*?-->\s*", "", md, flags=re.S)                     # private comment
    # a list needs a blank line before it in pandoc Markdown
    lines, fixed = md.split("\n"), []
    for i, line in enumerate(lines):
        is_item = bool(re.match(r"(- |\d+\. )", line))
        prev = fixed[-1] if fixed else ""
        if is_item and prev.strip() and not re.match(r"(\s*- |\s*\d+\. |\s{2,}\S)", prev) and not prev.startswith("|"):
            fixed.append("")
        fixed.append(line)
    md = "\n".join(fixed)
    # figures: merge image + bold caption paragraph; PDF versions
    def fig(m):
        cap = protect_code(" ".join(m.group(3).split()), mathify)
        width = {"fig3_weighting": "0.72\\linewidth"}.get(m.group(2), "\\linewidth")
        return f"![{cap}](../figures/{m.group(2)}.pdf){{width={width}}}\n\n"
    md = re.sub(r"!\[Figure (\d)\]\(figures/(\S+?)\.png\)\n\n\*\*Figure \1\.\*\* (.*?)\n\n", fig, md, flags=re.S)
    # table captions: pandoc's "Table:" paragraph right after the table
    md = re.sub(r"\n\n\*\*Table \d+\.\*\* (.*?)\n\n", lambda m: "\n\nTable: " + " ".join(m.group(1).split()) + "\n\n",
                md, flags=re.S)
    # abstract and appendix
    md = md.replace("## Abstract\n", "```{=latex}\n\\begin{abstract}\n```\n", 1)
    md = md.replace("## 1 Introduction", "```{=latex}\n\\end{abstract}\n```\n\n## 1 Introduction", 1)
    md = md.replace("## References", "## References {.unnumbered}", 1)
    md = md.replace("## Appendix A:", "```{=latex}\n\\appendix\n```\n\n## Appendix A:", 1)
    md = re.sub(r"^## Appendix [A-Z]: (\w)", lambda m: "## " + m.group(1).upper(), md, flags=re.M)
    md = re.sub(r"^(#{2,3}) \d+(?:\.\d+)? ", r"\1 ", md, flags=re.M)        # LaTeX numbers sections itself
    # references: plain list in a smaller font (citations in the text are author-year prose)
    md = md.replace("## References {.unnumbered}\n", "## References {.unnumbered}\n\n```{=latex}\n\\begingroup\\small\n```\n", 1)
    md = md.replace("```{=latex}\n\\appendix\n```", "```{=latex}\n\\endgroup\n\\appendix\n```", 1)
    out = []
    in_refs = False
    for line in md.split("\n"):
        if line.startswith("## References"):
            in_refs = True
        elif line.startswith("```{=latex}") and in_refs:
            pass
        elif line.startswith("## ") and in_refs:
            in_refs = False
        if line.startswith("![") or line.startswith("```") or line.startswith("$$") or in_refs:
            out.append(line if not line.startswith("$$") else line)
            continue
        out.append(protect_code(line, mathify))
    md = "\n".join(out)
    md = md.replace(L, r"\(").replace(R, r"\)")
    return md


HEADER = r"""
\usepackage{unicode-math}
\setmathfont{Latin Modern Math}
\usepackage{newunicodechar}
\newunicodechar{≥}{\ensuremath{\ge}}
\newunicodechar{≤}{\ensuremath{\le}}
\newunicodechar{≈}{\ensuremath{\approx}}
\newunicodechar{≠}{\ensuremath{\neq}}
\newunicodechar{∉}{\ensuremath{\notin}}
\newunicodechar{→}{\ensuremath{\rightarrow}}
\newunicodechar{×}{\ensuremath{\times}}
\newunicodechar{±}{\ensuremath{\pm}}
\newunicodechar{·}{\ensuremath{\cdot}}
\newunicodechar{Σ}{\ensuremath{\Sigma}}
\newunicodechar{τ}{\ensuremath{\tau}}
\newunicodechar{γ}{\ensuremath{\gamma}}
\usepackage{booktabs}
\usepackage{microtype}
\usepackage{xurl}
\setlength{\LTcapwidth}{\linewidth}
\usepackage[font=small,labelfont=bf]{caption}
\usepackage{etoolbox}
\AtBeginEnvironment{longtable}{\small\renewcommand{\arraystretch}{1.12}}
\renewcommand{\floatpagefraction}{0.8}
\renewcommand{\topfraction}{0.9}
\newcommand{\lbl}[1]{\texttt{#1}}
"""


def postpass(tex: str) -> str:
    # label names (\texttt{A\_B\_C}) may break after underscores
    tex = re.sub(r"\\texttt\{([^{}]*)\}", lambda m: r"\texttt{" + m.group(1).replace(r"\_", r"\_\allowbreak{}") + "}", tex)
    return tex


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    md = prepass(SRC.read_text(encoding="utf-8"))
    (OUT / "main.md").write_text(md, encoding="utf-8")
    (OUT / "header.tex").write_text(HEADER, encoding="utf-8")
    (OUT / "meta.yaml").write_text(
        f"author: '`{AUTHOR}\\\\[2pt] {{\\small {AFFIL}}}`{{=latex}}'\ndate: 'Draft, November 2026'\n", encoding="utf-8")
    cmd = ["pandoc", str(OUT / "main.md"), "-f", "markdown+tex_math_single_backslash+raw_tex-implicit_figures+implicit_figures",
           "-t", "latex", "-s", "--template", str(REPO / "scripts" / "paper_latex_template.tex"),
           "--shift-heading-level-by=-1", "--number-sections", "--lua-filter", str(REPO / "scripts" / "paper_latex_tables.lua"),
           "-H", str(OUT / "header.tex"), "--metadata-file", str(OUT / "meta.yaml"),
           "-V", "documentclass=article", "-V", "fontsize=10pt", "-V", "papersize=a4",
           "-V", "geometry=margin=2.3cm", "-V", "mainfont=Latin Modern Roman", "-V", "colorlinks=true",
           "-V", "linkcolor=blue", "-V", "urlcolor=blue", "--columns=200", "-o", str(OUT / "main.tex")]
    subprocess.run(cmd, check=True)
    tex = postpass((OUT / "main.tex").read_text(encoding="utf-8"))
    (OUT / "main.tex").write_text(tex, encoding="utf-8")
    (OUT / "main.md").unlink()
    (OUT / "meta.yaml").unlink()
    (OUT / "header.tex").unlink()          # pandoc -H already copied it into main.tex
    if "--no-pdf" not in sys.argv:
        r = subprocess.run(["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=OUT,
                           capture_output=True, text=True)
        log = (OUT / "main.log").read_text(errors="replace") if (OUT / "main.log").exists() else ""
        missing = sorted(set(re.findall(r"Missing character: There is no (\S+)", log)))
        overfull = len(re.findall(r"Overfull \\hbox", log))
        print("latexmk exit", r.returncode, "| missing glyphs:", missing or "none", "| overfull boxes:", overfull)
        if r.returncode != 0:
            print(r.stdout[-3000:])
            return 1
        for f in OUT.glob("main.*"):
            if f.suffix not in (".tex", ".pdf"):
                f.unlink()
    return 0


if __name__ == "__main__":
    sys.exit(main())
