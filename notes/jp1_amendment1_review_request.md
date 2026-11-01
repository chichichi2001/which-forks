# JP-1 変更1（A-2）の独立レビューの依頼

PRIVATE UNPUBLISHED RESEARCH — REVIEW REQUEST ONLY.

## 読むもの

- リポジトリ・ブランチ：`chichichi2001/Pork`、`decision-points`。この依頼ファイルと同じコミットを読む。
- 主：`notes/jp1_amendment1.md`（変更の中身。レビュー前）。
- 背景：
  - 凍結した計画 `notes/jp1_sarashina_gate.md`（凍結 `3198152`、書き換えない）。特に「G0 下準備」の 5.（本番前の確認は DP5 と同じ）と「G2 分析と監査」の事後再生監査、「計算の見積もり」の止める線。
  - `notes/jp1_after_freeze.md`（G0 の1回目、G1 診断、先頭1回の確認の数と、オーナーの言葉の原文）。
  - `notes/jp1_lock_pre_g0.md` のいちばん下「G0 のあとの追記」（G0 の1回目の数）。
- コード（読むだけでよい）：
  - `pork/jp1_shared_prefix.py` と `tests/test_jp1_shared_prefix.py`（新しい step。まだ本番の作業プロセスには差し込んでいない）。
  - 比べる相手：`pork/ct1_runner.py` の `torch_fns`（古い step）、`pork/ct1_forks_replacement.py` の `generate_batch`、`pork/jp1_runner.py` の `compute_point`・`audit_row`・`_main`。
  - 確認に使ったノートブックのビルダー：`scripts/build_jp1_g1diag_notebook.py`、`scripts/build_jp1_prefix_check_notebook.py`。
- 結果の数は、Drive の JSON をClaude が写して `notes/jp1_after_freeze.md` と `notes/jp1_amendment1.md` に書いたもの。Drive の元のファイルの sha256 も書いてある。

## 守ること

- レビューだけ。計画書・変更ファイル・コードは書き換えない。承認の判断もしない（承認はオーナー）。
- ベンチマークの問題の中身、トークンや単語の中身は書かない。
- 実行したこと・読んだだけのことを分けて書く。
- 結果は同じブランチに `notes/jp1_amendment1_review_<YYYYMMDD>_<名前>.md` として push する。

## 見てほしいこと（`notes/jp1_amendment1.md` の「レビューで見てほしいこと」と同じ）

- **R1**：精度（float32）のほうを変えて、G1 の合格の線（DP5 と同じ、64 トークンの完全一致）はそのまま、という判断でよいか。凍結した計画の意図を崩していないか。
- **R2**：新しい step で引き直しが古い step と最後の桁で違う（48 歩で 32 本のうち 1〜3 本が分かれた）ことが、q と A・B のラベルの意味を変えないか。本番と事後再生監査が同じ新しい step を使う、という作りで足りるか。
- **R3**：G0 を最初からやり直し、正解率を float32 で測り直して切り替えの決まりを2回目の数に当てはめる扱いでよいか。
- **R4**：G0 の2回目に足す確かめ（B2：新しい step の再現性、M1：作業2つを同時に、いちばん長い列で）と、新しい止まり方 `JP1_STOPPED_PRECHECK`。M1 の余裕（約 2.5 GB）で足りるか。
- **R5**：開示（報告に書くこと）に足りないものがないか。新しい矛盾がないか。

## 書き方

- 先頭に：読んだファイルと SHA、判定（PASS / PASS WITH REPAIRS / NOT READY）、実装と G0 の2回目を止める点があればその一番早いもの。
- 指摘ごとに：重さ（実装を止める／直したほうがよい／好みの範囲）、場所、理由、直し方の案。
