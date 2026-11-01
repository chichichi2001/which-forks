# PARA-1 再レビューの依頼（第5版の下書き、直したところだけ）

PRIVATE UNPUBLISHED RESEARCH — REVIEW REQUEST ONLY.

## 読むもの

- リポジトリ・ブランチ：`chichichi2001/Pork`、`decision-points`。この依頼ファイルと同じコミットを読む。
- 主：`notes/para1_paraphasia_plan.md`（第5版の下書き。**未凍結**）。末尾の「改訂の記録」の第5版。
- 前のレビュー：`notes/para1_independent_review_v4_20261012_gpt6.md`（コミット dd1e74e、NOT READY）。
- 試作：`scripts/para1_typing.py`（`decode_target`・`type_position_candidates`・`ToyTokenizer`・`G0_DECODE` を追加）、`reports/para1_g0_dryrun_v5.txt`。

## 守ること（前回と同じ）

- レビューだけ。計画書・コードは書き換えない。凍結の判断もしない。
- ベンチマークの問題の中身、トークンや単語の中身は書かない（付録の人工の例は書いてよい）。
- 実行したこと・読んだだけのことを分けて書く。
- 結果は同じブランチに `notes/para1_independent_review_v5_<YYYYMMDD>_<名前>.md` として push する。

## 見てほしいこと（直したところだけ）

- **T1（S1）**：w がデコードできない位置の丸ごと除外（`EXCLUDED_TARGET_DECODE_MISMATCH`）と、位置ごとの除外の順・どの集計から外すか。接続の関数と通しの例 D1〜D4 で、ID → 文字列 → 型が検査できる形になったか。
- **T2（S3-A）**：G1b（土台の道を先に作り、対象の位置と監査の対象を決め、モデルごとの固定の一覧をコミット）→ G2（固定した土台の道で logit だけ）の工程に矛盾がないか。`BASELINE_ARGMAX_MISMATCH` の扱い。
- **T3（S3-B）**：|x − y| ≤ max(1e-12, 1e-9 × max(|x|, |y|)) の許容、裾の小さな負の値、logsumexp の型。
- 前回の blocking が残っていれば最初に書く。直したことで新しく生まれた矛盾があれば、それも書く。

## 書き方

- 先頭に：読んだファイルと SHA、判定（PASS / PASS WITH REPAIRS / NOT READY）、凍結を止める一番早い点。
- 前回の S1・S3 それぞれに、解消・一部解消・未解消を書く。指摘は blocking / nonblocking に分け、最小の直し方を書く。
