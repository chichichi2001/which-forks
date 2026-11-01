# Which forks?

**The definition of a forking token can flip its relation to entropy.**
Chisa Honda, independent researcher. Draft, November 2026.

Token-level entropy is widely used to find the "forking tokens" of chain-of-thought reasoning. A fork can be
measured by forcing a different token at a position, or by resampling from it. On arithmetic (GSM-Symbolic), in
three open models from three families (OLMo-2 1B, Gemma-2-2b-it, Qwen2.5-7B-Instruct), entropy relates to these
two definitions in opposite directions: it marks the positions where resampling changes the answer, largely by
construction, yet points away from the positions where a forced swap does. Confident digit tokens carry a
substantial part of the forced-swap side, not all of it.

- **Paper:** [`paper/latex/main.pdf`](paper/latex/main.pdf) (source: [`paper/draft_en.md`](paper/draft_en.md)).
- **The experiments were pre-registered; later analyses are labelled post hoc.** Definitions, seeds and decision
  rules were frozen, and their files hashed, before each run. The plans of the post hoc analyses were frozen before
  computing.

## What is in this repository

| Folder | Contents |
|---|---|
| `paper/` | The paper (Markdown source, LaTeX, PDF, figures, references). |
| `notes/` | Gate documents (frozen plans), amendments, implementation notes, independent reviews and result notes for every experiment in the paper (DP1–DP9, R1, DP8-X, HR-1, RK-1, EX-1, CT-1, CR-0–CR-5, PARA-1/1a, JP-1, and the pre-looks). Mostly in Japanese. |
| `reports/` | Result files of the runs (see the exceptions below). |
| `notebooks/` | The Colab notebooks as they were run, saved without outputs (see below). |
| `scripts/` | The scripts that build the paper, its figures and this release. |
| `MANIFEST.json` | Every file with its size, SHA-256, and the last commit that changed it in the private working repository. Files revised or added here for the release (paper rev. 9 and the Table 2 script) carry a `note` instead of a commit; the five redacted notes keep the SHA-256 of their originals (see below). |
| `COMMITS.md` | Every commit hash cited in the paper and the notes, with its full hash, date, subject and the files it changed. |

### How to check the records

- **Recompute Table 2 in one command.** `python scripts/recompute_table2.py` (standard library only, about a
  second) recomputes entropy's within-item AUROC for DP3–DP6 from the per-position records in
  `reports/r1_TABLES.json`, using the frozen labelling rule (top 15% of positions pooled across items, count
  rounded down, ties broken by item order and then position), and checks every value against Table 2 of the
  paper. All eight values match. `--boot` adds 95% intervals (2,000 resamples of templates); they agree with the
  paper's to within about 0.005, the difference coming from the random-number generator. The per-position records
  of DP7 and DP9 are not in this repository, so those rows are not recomputed.

- The paper and the notes quote SHA-256 values of frozen gate documents and result files. `MANIFEST.json`
  gives the SHA-256 of every file here, so each quoted value can be checked:
  `sha256sum notes/<file>` or `python -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" notes/<file>`.
- Result files carry an internal `result_sha256`: the SHA-256 of the file's JSON with that field removed,
  serialised with sorted keys.
- Files are copied byte for byte from the private working repository, except the five notes listed below. Frozen
  files were never edited, so the heading "PRIVATE UNPUBLISHED RESEARCH" that most notes carry is historical: they
  were private when written.
- The owner's approvals and instructions are quoted verbatim, with their times, on purpose, including casual
  ones: a record that is never rewritten is the point of pre-registration.
- Five notes are published as redacted copies. In each, one quoted remark of the owner names a real person who
  has no part in this research; that name is replaced by 人物1 ("person 1"). Nothing else in these files is
  changed. Their SHA-256 values therefore differ from the ones quoted elsewhere and in `MANIFEST.json`, which are
  the values of the unredacted originals. The originals are kept unchanged in the private working repository and
  can be shown on request.

  | File | Names replaced | SHA-256 of the original (quoted elsewhere) | SHA-256 of the published copy |
  |---|---|---|---|
  | `notes/dp7_matched_swap_gate.md` | 1 | `fa30c6ef7dac63a5fb45778a482c1fea55f3d6454da3c2e7831034a2c41ec0f5` | `dbcefb17f4c3eb046138faf54ac50899ceb4cd8142254e5353f86ed7fbdb9c18` |
  | `notes/ex1_feature_sweep_spec.md` | 1 | `92305b689ab41a96aab76a54fd72b15248a2e56b7f26648de6a909b88a437e37` | `94752e7dfe8bd1bdf5025ef96d34cae3f6ea8c5b89dbf5aa78df0950388d8afa` |
  | `notes/cr3_plan.md` | 1 | `cea76f19abe9d7c9c9b2fe653ed7ed28833e7bf4df342e3774569744b4ee9692` | `d9c47f974d7c0af68fa1cb7a83453bb0e84ec723e73db08ba1809c48e2380be0` |
  | `notes/cr3_explore_spec.md` | 1 | `8330ddbf0770d6473efec5ed07b1debb069ef834920c66fbebc13afe109e7f65` | `7165b92ba029c6cf7d0a0ea18da0df20648dade0bc14e76c76cc1e18f6fffc0e` |
  | `notes/cr4_plan.md` | 1 | `ed9b3e44397ef8c60d28816a05a59573b4f1107df31351f0c2b969affd795fbc` | `05ac9029f44f74f3191f3810318a456898e5ff5cdd5e2a40d3da5b765529193d` |
- Exceptions in `reports/`:
  - `jp1_ja_only_RESULT.json` (JP-1, Appendix F) was produced on Kaggle and kept in the author's Dropbox; it is
    copied here. Its `result_sha256` was computed before the JSON round trip, with integer item keys, so convert
    the digit-only keys of `per_item` back to integers before recomputing it.
  - `cr3_explore_result.json` is missing its final closing brace (as written by the run); add it before parsing.
  - `cr0_smoke_v1.json` (an API smoke test) is not included, because it holds five short model responses.

### What is not here yet

- **The analysis code.** The experiments' code lives in a larger private sandbox, together with code from
  other, unpublished lines of work. It will be released as a separate, self-contained package, with tests that
  reproduce the published numbers from the frozen inputs, rather than as an extract of that sandbox.
- **The notebooks cannot be rerun as they are.** They clone the private repository at fixed commits; they are
  included as an exact record of what ran (models, revisions, settings, checks, stop lines).

### What is never here

No benchmark problem text and no model output appears in this repository, by design: the records hold numbers,
labels, IDs and hashes. The only other strings are a few hand-written test inputs (made-up word pairs and token
pieces in `reports/para1_g0_dryrun_v*.txt`, nine made-up probe prefixes and an API error string in
`reports/cr1_g0_result.json`, and example sentences written for a check in `notes/jp1_sarashina_gate.md`,
appendix C), and our own prose. The independent reviews in `notes/*_gpt6.md` were written by another language
model (GPT-6) acting as a reviewer. The benchmarks (GSM-Symbolic, MGSM, CHASE-Math, GSM-Infinite and others,
see the paper) are used under their own terms and are not redistributed.

## Licence

- Paper, notes and result files: [CC BY 4.0](LICENSE-CC-BY-4.0.md).
- Scripts and notebooks: [MIT](LICENSE), except `scripts/paper_latex_template.tex`, which is pandoc's default
  LaTeX template with one line changed and keeps pandoc's terms (see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)).

## Citation

See [`CITATION.cff`](CITATION.cff).

## Contact

Chisa Honda — chichichi2001@gmail.com
