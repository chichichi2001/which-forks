# PARA-1 確認レビューの依頼（第7版の下書き、直したところだけ）

PRIVATE UNPUBLISHED RESEARCH — REVIEW REQUEST ONLY.

## 読むもの

- リポジトリ・ブランチ：`chichichi2001/Pork`、`decision-points`。この依頼ファイルと同じコミットを読む。
- 主：`notes/para1_paraphasia_plan.md`（第7版の下書き。**未凍結**）。末尾の「改訂の記録」の第7版と、「ゲート」の G2 の項。
- 前のレビュー：`notes/para1_independent_review_v6_20261012_gpt6.md`（コミット ae20bef、PASS WITH REPAIRS）。
- 試作のコードは第5版から変えていない。

## 守ること（前回と同じ）

- レビューだけ。計画書・コードは書き換えない。凍結の判断もしない。
- ベンチマークの問題の中身、トークンや単語の中身は書かない。
- 実行したこと・読んだだけのことを分けて書く。
- 結果は同じブランチに `notes/para1_independent_review_v7_<YYYYMMDD>_<名前>.md` として push する。

## 見てほしいこと（直したところだけ。短くてよい）

- **V1（U2-B）**：logit の位置の式（t = 0 の扱いを含む）と、G1 での「1 つずつ取った logit と一括で取った logit のベクトルごとの比べ」（許容 1e-3、上位 20 個の ID と順位、負の対照、同じトークンが続く人工の例）で、位置のずれを検知できるか。最大のトークンの一致率を補助の診断に下げた書き方。
- **V2**：止めない指摘への対応（revision とテンプレートの照合、SHA256 の対象、診断の M_S の分離、NaN・無限大の試し）に新しい矛盾がないか。

## 書き方

- 先頭に：読んだファイルと SHA、判定（PASS / PASS WITH REPAIRS / NOT READY）、凍結を止める点があればその一番早いもの。
