# PARA-1 再々レビューの依頼（第4版の下書き、直したところだけ）

PRIVATE UNPUBLISHED RESEARCH — REVIEW REQUEST ONLY.

## 読むもの

- リポジトリ・ブランチ：`chichichi2001/Pork`、`decision-points`。この依頼ファイルと同じコミットを読む。
- 主：`notes/para1_paraphasia_plan.md`（第4版の下書き。**未凍結**）。末尾の「改訂の記録」の第4版に、どの指摘をどう直したかを書いてある。オーナーの選択は「オーナーの選択（16:00〜16:01）」。
- 前のレビュー：`notes/para1_independent_review_v3_20261012_gpt6.md`（コミット 4140ca8、NOT READY）。
- 試作：`scripts/para1_typing.py`（`decode_candidate` を追加、`classify_candidate` の順を修正）、`reports/para1_g0_dryrun_v4.txt`。

## 守ること（前回と同じ）

- レビューだけ。計画書・コードは書き換えない。凍結の判断もしない。
- ベンチマークの問題の中身、トークンや単語の中身は書かない（付録の人工の例は書いてよい）。
- 実行したこと・読んだだけのことを分けて書く。
- 結果は同じブランチに `notes/para1_independent_review_v4_<YYYYMMDD>_<名前>.md` として push する。

## 見てほしいこと（直したところだけ）

- **S1（R1）**：w が空の位置の除外が、計画とコードの両方で先頭になったか。文脈つきの差分によるデコードの決まり（窓 8 トークン、decode の引数、デコード不一致）と、G0b（19 例＋トークナイザーの通しの確かめ、実装直後の事前スモーク）で、ID → 文字列 → 型分けが一意に決まり、検査できるか。
- **S2（R3）**：層の中の完全順列（棄却法）・乱数の作り方と順番、G0c が CR-1 の前方一致と判定の順まで本番のコードで通す設計で、偽陽性の確かめとして筋が通るか。
- **S3（R4）**：案A（監査の位置を G2 の前に決め、本番で全語彙の logit を保存）で、G3 の主の確かめ（保存した本番の logit から計算し直す）と再現性の確かめ（`AUDIT_LOGIT_DRIFT_MINOR`・`_MAJOR`）に矛盾がないか。大きさを抑える工夫（32 位置・可逆圧縮・本番は float32 の logit ＋ float64 の分母、CPU で確率を作り直す）で、正確さが崩れていないか。
- **S4（R5）**：B1 の NA、B2・B3 の共通の集まり、`_AMONG_CLASSIFIED`。
- 前回の blocking が残っていれば最初に書く。直したことで新しく生まれた矛盾があれば、それも書く。

## 書き方

- 先頭に：読んだファイルと SHA、判定（PASS / PASS WITH REPAIRS / NOT READY）、凍結を止める一番早い点。
- 前回の R1・R3・R4・R5 それぞれに、解消・一部解消・未解消を書く。指摘は blocking / nonblocking に分け、最小の直し方を書く。
