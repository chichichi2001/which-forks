# JP-1 変更2 の独立レビューの依頼

PRIVATE UNPUBLISHED RESEARCH — REVIEW REQUEST ONLY.

## 読むもの

- リポジトリ・ブランチ：`chichichi2001/Pork`、`decision-points`。この依頼ファイルと同じコミットを読む。
- 主：`notes/jp1_amendment2.md`（変更の中身。レビュー前。F3 の線はオーナーが決める前の案）。
- 背景：
  - 凍結した計画 `notes/jp1_sarashina_gate.md`（凍結 `3198152`、書き換えない）。特に「区間と、組の決め方」（P_A4・P_B の問題数の線 20）、「G2 分析と監査」、「計算の見積もり」の止める線。
  - 変更1 `notes/jp1_amendment1.md`（承認済み）と、そのレビュー `notes/jp1_amendment1_review_20261015_gpt6.md`。
  - `notes/jp1_after_freeze.md` の「本番 日本語A の結果と…」から下（日本語A・長さの数え・抜く確認の数と、オーナーの言葉の原文）。
- コード（読むだけでよい）：
  - `pork/jp1_shrinking_batch.py` と `tests/test_jp1_shrinking_batch.py`（抜く step。まだ本番の作業プロセスには差し込んでいない）。
  - 比べる相手：`pork/ct1_forks_replacement.py` の `generate_batch`、`pork/jp1_shared_prefix.py`（変更1 の step）、`pork/jp1_runner.py` の `compute_point`・`audit_row`。
  - 確認のノートブックのビルダー：`scripts/build_jp1_shrink_check_notebook.py`、`scripts/build_jp1_lengthcount_notebook.py` と `pork/jp1_length_count.py`。
  - 問題数の線：`pork/jp1.py` の `MIN_PAIRED`。
- 結果の数は、Drive の JSON を Claude が写したもの。元のファイルの sha256 も書いてある。

## 守ること

- レビューだけ。計画書・変更ファイル・コードは書き換えない。承認の判断もしない（承認はオーナー）。
- ベンチマークの問題の中身、トークンや単語の中身は書かない。
- 実行したこと・読んだだけのことを分けて書く。
- 結果は同じブランチに `notes/jp1_amendment2_review_<YYYYMMDD>_<名前>.md` として push する。

## 見てほしいこと

- **R1（step が言語で違う）**：日本語A は変更1 の step、英語A は抜く step で計算する。抜く確認の数（上限まで残った1本だけが別の引き直しになる。q は 16組中1組で 1/32）のもとで、開示つきでこれを許してよいか。ほかの道として、(i) 英語A も変更1 の step で回す（約 1/0.62 倍の時間）、(ii) 日本語A を抜く step で計算し直す（約 10 時間増）がある。A4・B2（言語の差）の解釈に対して、どれがよいか。
- **R2（問題を 20 問にすること）**：日本語A の時間と長さを見たあと（量・ラベルを見る前）に問題数を半分にすることが、計画の意図（事前に決めたラベル）を崩さないか。開示 1.〜6. で足りるか。
- **R3（問題数の線、F3）**：P_A4・P_B の線 20 を 15 または 10 に下げること（F3-a／F3-b）、または 20 のまま（F3-c）。日本語A の量も英語の結果も見ていない時点で決めるなら、事後の選び方の問題は小さいと考えてよいか。20 問のブートストラップで、ラベルの線（±0.10、±0.05）をそのままにしてよいか。
- **R4（英語A の前の確認、F5）**：G0 をやり直さず、英語A のノートブックの中で B1（抜く step で）・2回回しての一致・版・コードの違いが2ファイルだけ、を確かめる作りで足りるか。足りないなら何を足すか。
- **R5（監査、F4）**：事後再生監査が言語ごとに3問になる（不合格の線「2問以上ずれたら」はそのまま）。弱くなりすぎないか。英語の監査を英語A と同じ抜く step で作り直す作りでよいか。
- **R6（止める線、F6）**：1冊ごとの線を「2時間ごとに残りの時間を記録する」に替え、全体の線を 45 → 70 CU にすること。英語A の見込み（約 16〜19 時間・約 27〜32 CU）は、英語の本番の長さと作業2つでの倍率をまだ測っていない概算である。

## 返してほしいもの

- R1〜R6 それぞれに：PASS／PASS WITH REPAIRS（直すところを具体的に）／FAIL（理由）。
- 全体の判定：PASS／PASS WITH REPAIRS／FAIL。
