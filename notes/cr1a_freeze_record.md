# CR-1a / PARA-1a 凍結の記録

PRIVATE UNPUBLISHED RESEARCH.

- 凍結：**2026-10-12 19:50 JST**、オーナーの承認（「承認する！よろしくね！」）。CR-1a と PARA-1a を同時に凍結。
- 凍結した中身：コミット **d41e649**（CR-1a 第4版・PARA-1a 第2版・コード）。この記録のコミットで変えたのは、2 つのファイルの状態の行（「下書き」→「凍結」）と、この記録ファイルの追加だけ。
- 凍結したファイル（この記録のコミットでの Git blob）：
  - `notes/cr1a_amendment.md` — `e036e39527b126ad8ab804f6ef28c346332c74bc`
  - `notes/para1a_amendment.md` — `ad8d4e4cda62539ecbcf3a785ea9765d005cb0bd`
- 実行のコード（Git blob）：
  - `pork/cr1_run.py` — `cd73565712cf1f790dcb2b52884b7a2802cbb51f`
  - `pork/cr1_requests.py` — `939c91607bc4a954bf86092659d08bbf4d565f94`
  - `scripts/build_cr1a_g1_notebook.py` — `d522d8bb445e8c349afff1f0234ff11f6da9e1c6`
  - `tests/test_cr1_run.py` — `61947ee7e15096f6db77c17dccd5c4a3843fda3d`
  - 段2 で固定したもの（変更なし）：`pork/cr1_analysis.py` — `f0af24088e8e179312fb755fd21bd4d6ccc901c9`、`pork/cr1_items.py` — `c72ac7739f1ff20e845a48526290d14f4600b358`、`pork/cr1_reference.py` — `45e3a4805d2aec5fd367ea34e0c172a7cd18e2bf`、`pork/cr1_audit.py` — `60c94214f815288694df3c1d988c1611dd67750c`
- CR-1a の頼み方の sha256：`0140527fa8e9db6ed25d71cd6d950dd1e77fe6e7c4fee206a5c6ed2411432740`。候補の一覧の sha256（段2）：`b6f6375aed95831de0098a5138bb87f4101fe9c6670598f23e5e8055eaac8511`。
- 独立レビュー：`notes/cr1a_independent_review_20261012_gpt6.md`（1eeca82、NOT READY）→ `notes/cr1a_independent_review_v2_20261012_gpt6.md`（5eb6356、NOT READY）→ `notes/cr1a_independent_review_v3_20261012_gpt6.md`（73252cf、**PASS**、a301e1c を対象）。d41e649 は PASS のあとの止めない指摘だけ（判定の決まりは変えていない。この差分はレビューに出し直していない）。
- 凍結の時点：CR-1a の G1（やり直し）・G2 のリクエストは **1 件も送っていない**。CR-1a の Drive のフォルダ（`DECISION_POINTS/cr1a/G1`）もまだ作っていない。最初の CR-1 の G1（STOPPED、57 問）と PARA-1 の部A（`NOT_RUN_CR1_STOPPED`）の記録はそのまま。
- 時間の順の確かめ：CR-1a の G1 のノートブックは、この記録のコミット（またはその子孫）に固定する。結果には、このコミットが G1 のノートブックの固定したコミット・段3 のロックのコミットの祖先であること（`git merge-base --is-ancestor`）と、G1 の実行の時刻・最初の G2 の送信の時刻とバッチ ID を並べる。
