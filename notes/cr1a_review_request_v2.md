# CR-1a / PARA-1a 確認レビューの依頼（第2版、直したところだけ）

PRIVATE UNPUBLISHED RESEARCH — REVIEW REQUEST ONLY.

## 読むもの

- リポジトリ・ブランチ：`chichichi2001/Pork`、`decision-points`。この依頼ファイルと同じコミットを読む。
- 主：`notes/cr1a_amendment.md`（第2版、**未凍結**）の「実行の決まり」「止める決まり」「時間の順」と改訂の記録。`notes/para1a_amendment.md`（第2版、**未凍結**）。
- コード：`pork/cr1_run.py`（新規）、`tests/test_cr1_run.py`（新規）、`scripts/build_cr1a_g1_notebook.py`（新規）。`scripts/build_cr1_g1_notebook.py` は説明の 1 行だけ追加。
- 前のレビュー：`notes/cr1a_independent_review_20261012_gpt6.md`（1eeca82、NOT READY、R7）。

## 守ること（前回と同じ）

- レビューだけ。計画書・コードは書き換えない。凍結の判断もしない。
- ベンチマークの問題の中身、トークンや単語の中身は書かない。
- 実行したこと・読んだだけのことを分けて書く。
- 結果は同じブランチに `notes/cr1a_independent_review_v2_<YYYYMMDD>_<名前>.md` として push する。

## 見てほしいこと（短くてよい）

- **V1（R7）**：CR-1a の G1 の経路で、(a) 送る前に頼み方の sha256 を照合して止める側に倒れているか、(b) 保存先が CR-1 と完全に分かれているか、(c) 見出しが一致しない状態（見出しのない古い CR-1 の状態を含む）を読まずに止まるか、(d) G2 のリクエストが study の頼み方とプリフィルで作られ、段3 の一覧に必要なハッシュが出るか。
- **V2**：`tests/test_cr1_run.py` の人工データ・偽の API による端から端までの試験で、前回の指摘（新しい study の選択・新旧の状態の混在で停止・G2 の頼み方）が足りているか。Claude の手元では CR-1 系のテスト 21 件が通った（pytest、人工データのみ。API なし）。
- **V3**：止めない指摘への対応（開示の限界、成功の保証がないこと、G1b・期限で止まるときの一度きり、比べやすさの範囲、PARA-1a のラベルの名前の場所、凍結をやり直しの G1 より前に）に新しい矛盾がないか。

## 書き方

- 先頭に：読んだファイルと SHA、判定（PASS / PASS WITH REPAIRS / NOT READY）、凍結を止める点があればその一番早いもの。
