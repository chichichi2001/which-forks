"""Build the public release tree for "Which forks?" (owner decision 2026-10-18 21:2x JST: a new public repository
with only the decision-points materials; code MIT, paper CC BY 4.0).

Copies files byte-for-byte (frozen documents keep their SHA-256), selects Python modules by import closure, and
writes MANIFEST.json (path, size, SHA-256, last private commit that changed the file) and COMMITS.md (every commit
hash cited in the paper, mapped to the files it changed that are in the release).

usage: python scripts/build_public_release.py OUT_DIR
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SEED = re.compile(r"^(dp|cr[0-9]|ct1|jp1|para1|hr1|rk1|ex1|r1_|alt_prelook|hard_prelook|infinite_prelook)")
NOTE_SEED = re.compile(r"^(dp|cr[0-9]|ct1_|ct_feasibility|jp1|para1|r1_|hr1|rk1|ex1|alt_prelook|hard_prelook|"
                       r"infinite_prelook|decision_points_|appendix_stratified|paper_forks|paper_review|"
                       r"next_theme_decision_points|next_hard_items)")
NOTE_EXCLUDE = {"raais_proposal_draft.md", "README.md", "colab_cu_rates.md"}
REPORT_EXCLUDE = {"cr0_smoke_v1.json"}          # holds five short model responses; numbers-only rule
SCRIPT_SEED = re.compile(r"^(build_(dp|cr|ct|jp1|para1|hr1|ex1|r1|alt_prelook|hard_prelook|infinite_prelook|place)"
                         r"|build_paper_latex|make_paper_figures|paper_latex_|notebook_notify|cr1_|cr2_|dp2_|dp2x2_|"
                         r"dp6_stage2|para1_|build_public_release)")
NB_SEED = re.compile(r"^(DP|CR|JP1|PARA1A|HR1|RK1_EX1|ALT_PRELOOK|HARD_PRELOOK|INFINITE_PRELOOK|PLACE_DP)")


def tracked() -> list[str]:
    return subprocess.check_output(["git", "-C", str(REPO), "ls-files"], text=True).split("\n")[:-1]


def module_name(path: str) -> str | None:
    if path.startswith("pork/") and path.endswith(".py"):
        return path[:-3].replace("/", ".")
    return None


def imports_of(path: Path, pkg: str | None) -> set[str]:
    """pork.* modules imported by a file (absolute or relative)."""

    out: set[str] = set()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name == "pork" or a.name.startswith("pork."):
                    out.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                parts = (pkg or "pork").split(".")
                parts = parts[: len(parts) - (node.level - 1)]
                base = ".".join(parts + ([base] if base else []))
            if base == "pork" or base.startswith("pork."):
                out.add(base)
                for a in node.names:
                    out.add(base + "." + a.name)
        # importlib.import_module("pork." + name) with a literal prefix
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "import_module" and node.args:
            a0 = node.args[0]
            if isinstance(a0, ast.Constant) and isinstance(a0.value, str) and a0.value.startswith("pork."):
                out.add(a0.value)
    return out


def text_mentions(path: Path) -> set[str]:
    """Module names mentioned as strings like "dp4_weighting" inside notebook builders (spec dicts)."""

    try:
        t = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return set()
    return {"pork." + m for m in re.findall(r"[\"']((?:dp|cr[0-9]|jp1|para1|ct1|hr1|rk1|ex1)[a-z0-9_]*)[\"']", t)}


def select(files: list[str]) -> list[str]:
    mods = {module_name(f): f for f in files if module_name(f)}
    for f in list(mods.values()):
        if f.endswith("__init__.py"):
            mods[f[:-12].replace("/", ".")] = f
    keep: set[str] = set()

    def add_module(name: str):
        while name and name not in mods and "." in name:
            name = name.rsplit(".", 1)[0]
        if name in mods and mods[name] not in keep:
            f = mods[name]
            keep.add(f)
            pkg = name if f.endswith("__init__.py") else name.rsplit(".", 1)[0]
            for m in imports_of(REPO / f, pkg):
                add_module(m)
            parent = name.rsplit(".", 1)[0]
            if parent != name:
                add_module(parent)

    add_module("pork")
    for f in files:
        name = Path(f).name
        if f.startswith("pork/") and SEED.match(name):
            add_module(module_name(f))
    other: set[str] = set()
    for f in files:
        name = Path(f).name
        if f.startswith("scripts/") and "/" not in f[8:] and SCRIPT_SEED.match(name):
            other.add(f)
        elif f.startswith("scripts/sims/"):
            other.add(f)
        elif f.startswith("notes/") and name not in NOTE_EXCLUDE and NOTE_SEED.match(name):
            other.add(f)
        elif f.startswith("reports/") and name not in REPORT_EXCLUDE and NOTE_SEED.match(name):
            other.add(f)
        elif f.startswith("notebooks/") and NB_SEED.match(name):
            other.add(f)
        elif f.startswith("paper/") and not f.startswith("paper/handout/"):
            other.add(f)
    for f in sorted(other):
        if f.endswith(".py"):
            for m in imports_of(REPO / f, None) | text_mentions(REPO / f):
                add_module(m)
            if "notebook_tools" in (REPO / f).read_text(encoding="utf-8"):
                other.update(x for x in files if x.startswith("notebook_tools/") and not x.endswith("test_error_report.py"))
    # tests: every pork import inside the kept set, and at least one seed module
    kept_mods = {(f[:-12].replace("/", ".") if f.endswith("__init__.py") else module_name(f)) for f in keep}
    for f in files:
        if f.startswith("tests/") and f.endswith(".py"):
            imps = {m for m in imports_of(REPO / f, None) if m.count(".") <= 1}
            imps = {m for m in imps if m in mods}
            if imps and imps <= kept_mods and any(SEED.match(m.split(".")[-1]) for m in imps):
                other.add(f)
    return sorted(keep | other)


def last_commit(f: str) -> str:
    return subprocess.check_output(["git", "-C", str(REPO), "log", "-1", "--format=%H", "--", f], text=True).strip()


RECORDS_ONLY_SCRIPTS = {"scripts/build_paper_latex.py", "scripts/paper_latex_tables.lua", "scripts/paper_latex_template.tex",
                        "scripts/make_paper_figures.py", "scripts/build_public_release.py"}


def records_only(chosen: list[str]) -> list[str]:
    """Owner decision 2026-10-18 (option A): paper and records now; code later as a clean, re-verified package."""

    return [f for f in chosen if not f.startswith(("pork/", "tests/", "notebook_tools/"))
            and (not f.startswith("scripts/") or f in RECORDS_ONLY_SCRIPTS)]


def main(out: Path):
    files = [f for f in tracked() if (REPO / f).is_file()]
    chosen = records_only(select(files))
    if out.exists():
        shutil.rmtree(out)
    manifest = []
    for f in chosen:
        dst = out / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / f, dst)
        b = (REPO / f).read_bytes()
        manifest.append({"path": f, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
                         "last_private_commit": last_commit(f)})
    for extra in sorted((REPO / "release").iterdir()):     # README, licences, citation (release-only files)
        shutil.copyfile(extra, out / extra.name)
    (out / "MANIFEST.json").write_text(json.dumps({"source_branch": "decision-points",
                                                   "source_head": subprocess.check_output(
                                                       ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip(),
                                                   "files": manifest}, indent=1, ensure_ascii=False) + "\n")
    # commit hashes cited in the paper and the result notes
    cited = set(re.findall(r"\b[0-9a-f]{7,40}\b", (REPO / "paper/draft_en.md").read_text(encoding="utf-8")))
    for f in chosen:                                   # and every commit cited in the notes
        if f.startswith("notes/") and f.endswith(".md"):
            cited |= set(re.findall(r"\b[0-9a-f]{7,40}\b", (REPO / f).read_text(encoding="utf-8")))
    rows = []
    chosen_set = set(chosen)
    for h in sorted(cited):
        r = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--verify", "-q", h + "^{commit}"],
                           capture_output=True, text=True)
        if r.returncode:
            continue
        full = r.stdout.strip()
        subj = subprocess.check_output(["git", "-C", str(REPO), "log", "-1", "--format=%ad %s", "--date=iso", full],
                                       text=True).strip()
        changed = subprocess.check_output(["git", "-C", str(REPO), "show", "--name-only", "--format=", full],
                                          text=True).split()
        if any(r[1] == full for r in rows):
            continue
        rows.append((h, full, subj, [c for c in changed if c in chosen_set]))
    lines = ["# Commits cited in the paper and the notes", "",
             "The experiments ran from a private repository. This table maps every commit hash cited in "
             "`paper/draft_en.md` (and in the notes) to its full hash, date and subject, and to the files it changed that are in "
             "this release. Each file's SHA-256 is in `MANIFEST.json`; gate documents and result files can be "
             "checked against the SHA-256 values quoted in the paper and the notes.", ""]
    for h, full, subj, ch in rows:
        lines.append(f"- `{h}` → `{full}` — {subj}")
        for c in ch:
            lines.append(f"  - {c}")
    (out / "COMMITS.md").write_text("\n".join(lines) + "\n")
    print(len(chosen), "files;", len(rows), "cited commits resolved")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
