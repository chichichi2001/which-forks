# CR-0 — Claude API で「引き直し」が回るかの煙テスト（計画、実行前に凍結）

2026-10-10 作成。DP7 までの研究とは別の、新しい実験の下準備です。DP7 の追加分析ではありません。

## 目的
Claude の API で、決定点研究の「引き直し」（ある位置までを固定して、そこから先を何回も生成し直す）が
**技術的に回るか**だけを確かめる。分かれ道の結果は一切測らない。

## 使うもの
- ベンチマークの問題は使わない。無害な固定のお題だけ（「海について一文」「数を数える」）。
- モデル：`claude-haiku-4-5-20251001`（プリフィルあり）、`claude-haiku-5-5`（プリフィルは弾かれる想定）。
- 費用の上限の目安：全部で $0.05 未満（残高 $2.4 の範囲）。

## 確かめること（判定）
| 番号 | 中身 | 合格の条件 |
|---|---|---|
| T0 | 使えるモデルの一覧 | 一覧が取れる。Haiku 4.5 と 5.5 が入っているかを記録 |
| T1 | Haiku 4.5 + プリフィル（"The sea"）を5回 | 5回とも成功し、続きが空でない |
| T2 | T1 の5本の続きのばらつき | 異なる続きが2本以上（引き直しで違う続きが出る） |
| T3 | Haiku 4.5 + プリフィル（"1, 2, 3,"） | 成功し、続きに "4" が含まれる（プリフィルの続きから書いている） |
| T4 | Haiku 5.5 + プリフィル | 400 で弾かれる（ドキュメントどおり）。通ったら、それも記録 |
| T5 | Haiku 5.5、続けてほしい文を利用者側の発言に入れる代替方式を5回 | 5回とも成功 |

T1〜T3 が合格なら、本番は Haiku 4.5 のプリフィルで設計する。T1 が失敗（4.5 が使えない等）なら、
代替方式（T5）で何が測れて何が測れないかを、本番の計画書で先に書く。

## やらないこと
- 分かれ道・エントロピーの計算。結果を見て本番の設計を変える余地を作らないため。
- API キーの表示・保存。キーは Colab のシークレット `ANTHROPIC_API_KEY` から読むだけ。

## 通知
ntfy（トピックは設定済みのもの）に「スタート・終了・エラーで停止」の3回、名札「CR-0 煙テスト」つき。中身は一言だけ。

## 出力
Drive `MyDrive/DECISION_POINTS/cr0/` に `CR0_SMOKE.json`（モデル名、成否、stop_reason、トークン数、生成された短い文）。

## ノートブック
- Drive: `DECISION_POINTS/CR0_claude_resample_smoke.ipynb`（file id `1i7oNewjPdxIxU7btMQgRmNXwBtQto7n9`）
- ローカル生成物の sha256: `c5e97af1f946c39124737daa1e4fd8312cc4171ff1d75b313e792d7d9b7435b3`（8569 バイト。Drive 側も 8569 バイト）
- 生成：`python3 scripts/build_cr0_notebook.py OUT.ipynb`。偽の API クライアントでセル2を空回しし、表と通知（スタート・終了）が出ることを確認済み。

## 実行記録と修正（実行後に追記）
- v1 実行（2026-10-10 14:25 UTC、費用の見積もり $0.00009）：T0 一覧取得（Haiku 4.5・5.5 とも一覧にあり）。
  **T1〜T3 は API に届く前に失敗**：Colab に入った新しい `anthropic` パッケージの `Messages.create()` が `temperature` 引数を受け付けない（TypeError）。
  T4 は 400 で拒否（「This model does not support assistant message prefill」）。T5 は 5/5 成功だが、1 本は指示についての独り言が混ざり max_tokens で切れた。
- 修正（v3）：T1・T3 は温度を指定せず API の標準で呼ぶ（API の標準の温度は 1 で、計画の意図と同じ）。判定の条件は変えない。
- v2 は通知を GodPork の決まり（`scripts/notebook_notify.py`：名札・最初のセルで開始通知・エラー時通知・終了後に自動でランタイムを切る）に合わせた版だが、同じ temperature の不具合があるので使わない。
- v1 の結果は `reports/cr0_smoke_v1.json`（Drive では `cr0/CR0_SMOKE_v1.json` に改名）。v3 は Drive `DECISION_POINTS/CR0_claude_resample_smoke_v3.ipynb`（file id `1mrUjVr-bu2Nd0nTrG66ga9k9jdrO7uLh`、10996 バイトで手元と一致、sha256 `8c08234019a96039674e7b3baaaf4ee77483de502a9ee4f6f86cd40d30b38f16`）。v1・v2 は Drive で「旧版_使わない」に改名。

## ノートブックの決まり（Pork 側）
これから Pork で作るノートブックは、GodPork の `docs/NOTEBOOK_CONVENTIONS.md` に従う（ntfy の通知に名札、最初のセルで開始通知、エラーで止まったら通知、終わったら Drive を確定してランタイムを切る、Kaggle の使い分け）。通知の部品は `scripts/notebook_notify.py`（GodPork の `notebooks/_build/notify.py` の写し）。

## v3 の結果（2026-10-10 14:36:47〜14:36:55 UTC、約 8 秒、費用の見積もり $0.00069）
Drive `cr0/CR0_SMOKE.json`（file id `1H20m-OAzjmsR7gy-w872OgwhdNrrlHCi`）。

| 番号 | 判定 | 中身 |
|---|---|---|
| T0 | 合格 | Haiku 4.5（`claude-haiku-4-5-20251001`）・Haiku 5.5 とも一覧にある |
| T1 | 合格 | Haiku 4.5 + プリフィル 5/5 成功、すべて end_turn |
| T2 | 合格 | 5 本のうち違う続きが 4 本 |
| T3 | 合格 | "1, 2, 3," の続きが "4, 5, 6, 7, 8, 9, 10"（プリフィルの続きから書いている） |
| T4 | 想定どおり | Haiku 5.5 のプリフィルは 400 で拒否 |
| T5 | 合格 | 代替方式 5/5 成功（今回は独り言なし。ただし v1 で 1 本混ざったので、本番の主方式にはしない） |

**結論（計画の判定どおり）**：本番は Haiku 4.5 のプリフィルで「引き直し」を設計する。速かったのは呼び出しが 12 回だけだったため。
