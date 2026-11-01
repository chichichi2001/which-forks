# JP-1 確認レビューの依頼（v4 の指摘を直したところ）

PRIVATE UNPUBLISHED RESEARCH — REVIEW REQUEST ONLY.

計画の C0 の 4. による依頼です（C0 のあとに決まりを直したため）。

## 読むもの

- リポジトリ・ブランチ：`chichichi2001/Pork`、`decision-points`。この依頼ファイルと同じコミットを読む。
- 主：`notes/jp1_sarashina_gate.md`（**未凍結**）。「改訂の記録」の「第3版のまま追記（2026-10-15 朝、…X1-R1・X2-B1・X2-R2 を受けて）」、定義 5. の「語」（日本語は行ごと）と `MORPH_ALIGN_FAIL`、付録B、付録C の J18。
- コード：`pork/jp1_text.py`（`ja_words`・`classify`・`CALC_JA`・`APPENDIX_C`）、`tests/test_jp1_text.py`（17個）。差分は `git diff 486ee4d 5dfbf0e -- pork/ tests/ notes/jp1_sarashina_gate.md`。
- C0 の記録：`notes/jp1_c0_record.md` の「3回目」（コード 5dfbf0e で全部合格）。
- 前のレビュー：`notes/jp1_independent_review_v4_20261015_gpt6.md`（NOT READY、X2-B1）。

## 守ること（前回と同じ）

- レビューだけ。計画書・コードは書き換えない。凍結の判断もしない。
- ベンチマークの問題の中身、トークンや単語の中身は書かない（付録C・付録D の例は引用してよい）。
- 実行したこと・読んだだけのことを分けて書く。
- 結果は同じブランチに `notes/jp1_independent_review_v5_<YYYYMMDD>_<名前>.md` として push する。

## 見てほしいこと（直したところだけ。短くてよい）

- **Y1（X2-B1）**：計画をコードに合わせて「日本語は行ごとに解析し、位置を全体に戻す」と書いた直し方で、計画とコードの食い違いが閉じたか。J18 とテスト（`test_ja_multiline_offsets_and_newline_tokens`）で足りるか。
- **Y2（X2-R2）**：位置を合わせられなかった応答は、トークンをすべて `MORPH_ALIGN_FAIL` で分類できないとし、実験は止めない（分類できた割合の線 0.90 に入る）、という決め方とコード・テスト（`test_morph_align_fail_marks_whole_response`）。
- **Y3（X1-R1）**：「割れる」を外したこと。外したあとも J3・J17 が通ったこと（C0 の3回目）。
- **Y4**：直したことで生まれた新しい矛盾がないか。

## 書き方

- 先頭に：読んだファイルと SHA、判定（PASS / PASS WITH REPAIRS / NOT READY）、凍結を止める点があればその一番早いもの。
- 指摘ごとに：重さ（凍結を止める／直したほうがよい／好みの範囲）、場所、理由、直し方の案。
