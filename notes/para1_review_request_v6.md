# PARA-1 再レビューの依頼（第6版の下書き、直したところだけ）

PRIVATE UNPUBLISHED RESEARCH — REVIEW REQUEST ONLY.

## 読むもの

- リポジトリ・ブランチ：`chichichi2001/Pork`、`decision-points`。この依頼ファイルと同じコミットを読む。
- 主：`notes/para1_paraphasia_plan.md`（第6版の下書き。**未凍結**）。末尾の「改訂の記録」の第6版。
- 前のレビュー：`notes/para1_independent_review_v5_20261012_gpt6.md`（コミット dbe77ad、PASS WITH REPAIRS）。
- 試作のコードは第5版から変えていない。

## 守ること（前回と同じ）

- レビューだけ。計画書・コードは書き換えない。凍結の判断もしない。
- ベンチマークの問題の中身、トークンや単語の中身は書かない。
- 実行したこと・読んだだけのことを分けて書く。
- 結果は同じブランチに `notes/para1_independent_review_v6_<YYYYMMDD>_<名前>.md` として push する。

## 見てほしいこと（直したところだけ）

- **U1（T1-L1）**：除外した位置の M_S を、G2 で計算する診断だけの値にした書き方で、本解析（型分け・分母・被覆・帳尻・監査）と混ざらないか。
- **U2（T2-L1）**：G1b のトークン ID の実体の保存（Drive のファイル、SHA256・並び・型を一覧に記録）と、G2 の読み込みの照合（`G2_MANIFEST_MISMATCH`）、logit の位置と g の対応の確かめ。
- **U3**：NaN・無限大で止める規則、`BASELINE_ARGMAX_MISMATCH` の報告。
- 直したことで新しく生まれた矛盾があれば書く。

## 書き方

- 先頭に：読んだファイルと SHA、判定（PASS / PASS WITH REPAIRS / NOT READY）、凍結を止める点があればその一番早いもの。
- 前回の T1-L1・T2-L1 に、解消・一部解消・未解消を書く。
