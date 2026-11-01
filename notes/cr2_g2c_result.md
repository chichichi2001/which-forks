# CR-2 G2c（確かめる段）の結果（記録）

PRIVATE UNPUBLISHED RESEARCH.

- 実行：2026-10-14 11:3x〜12:36 JST、Colab CPU、`notebooks/CR2_G2C.ipynb` の v3（コードの head c2659a5。`pork`・`scripts`・`tests` は G1 の 311e300 と同じ）。
  - v1・v2 はセル2 で止まった（`G2C` のフォルダがなく Drive の試し書きが失敗。`notes/cr2_implementation_notes.md` の運用のメモ 2・3）。どちらも送る前で、API には何も送っていない。
- セル2 の G2c の前の受け入れ：段3b の三つ（G2s の生の結果から作り直したもの・Git・Drive）が一致（`1a70cc32…`）。
- 記録：Drive の `DECISION_POINTS/cr2/G2C/CR2_G2C_summary.json`（6,258 バイト、sha256 **`63c3654f4ec0dab2169db8ad67b2f781bb9e10ec81f390b83b36ae73f1d8faa8`**）。数・ID・ハッシュだけで、応答は見ていない。

## 数

- リクエスト 20,880 件、成功 **20,880**、解決しない 0、流れている 0。バッチ 11 個（2,000 × 10 + 880）、出し直しのバッチ 0。
- 各バッチに段3b のハッシュ：すべて入っている（true）。止まった理由：なし（完了）。
- 費用：G2c **$10.20**（見込み約 $12）。G0・G1・G2s を含む合計 **$19.81**（B_stop $54 の内）。
- 最初の送信 2026-10-14 11:33:35 JST、最後のバッチの送信 12:30:50 JST。

## 次

- G3（分析と監査、API なし）：`notebooks/CR2_G3.ipynb`（head a49135f、エラーの全文を通知する仕組みを差し込んだもの）。
