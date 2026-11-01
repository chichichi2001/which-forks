# 回路追跡の「回るかどうか」確認（CT-0）の計画

作成：2026-10-06 22:4x JST。テーマ案1（分かれ道は、読める部品で説明しきれない場所か）に入る前の、技術的な確認だけ。
**研究の問いには答えない。ベンチマーク（GSM-Symbolic）は使わない。** 判定ラベルもない。

## 使うもの
- circuit-tracer（safety-research/circuit-tracer、コミット `7f66876689f59e92fc3641650d38b8bd41749ec4`）。
- モデルと読める部品（トランスコーダー）の組（どれが動くかを見る）：
  1. Llama-3.2 1B（`meta-llama/Llama-3.2-1B`、`llama`）— 要：Hugging Face で利用規約に同意＋トークン
  2. Gemma-2 2B（`google/gemma-2-2b`、`gemma`）— 同上
  3. Qwen3 1.7B（`Qwen/Qwen3-1.7B`、`mwhanna/qwen3-1.7b-transcoders-lowl0`）— 規約の同意は不要
- 入力：作りものの算数の文章（決まった種 202610062241 で数字を選ぶテンプレート文。ベンチマークの問題ではない）。長さ 200・400・600 トークンで切る。

## 測ること（モデル × 長さごと）
- 図1枚を作る時間、GPUの最大メモリ、メインメモリ（RSS）。
- 置き換えスコア（replacement score）と完全性スコア（completeness score）。`compute_graph_scores` の値。どちらも「説明しきれない部分（エラー）」が少ないほど1に近い。
- 選ばれた部品の数。
- 再現性：200トークンで同じ図を2回作り、2つのスコアが一致するか（差の絶対値）。
- 失敗したとき：メモリ不足なら、部品の数を減らす・まとめて処理する数を減らす・CPUに逃がす（offload）の順に1回ずつ試し、記録する。1枚に20分を超えたら、そのモデルの長い入力は飛ばす。

## 次に進む条件（目安。ゲートではない）
- どれか1つのモデルで、400トークンの図が10分以内に、L4かA100で作れる。
- 2回作ったスコアの差が 0.01 未満。
- 満たさなければ、テーマ案1は捨てるか、短い入力に絞る形で考え直す。

## アップロードの記録
- ビルダー `scripts/build_ct0_notebook.py`（コミット `6b6f108`）。Drive `DECISION_POINTS/CT0_FEASIBILITY.ipynb`（id `1Cm_LagfX8OoS-41ESKQrKFLzTSrj6E_d`、11,259 B、手元の sha256 `641dabfb…331c4`）。読み戻したサイズは手元と一致（確認用のノートブックなので、セルの自己照合は入れていない）。
- 出力先：`DECISION_POINTS/ct0/CT0_RESULTS.json`。

## 実行時のメモ（2026-10-06 22:50 JST）
- オーナーは、Llama-3.2 1B の利用申請が承認待ちのまま CT-0 を回した（Gemma-2 2B は承認済み、Qwen3 は申請不要）。そのため、Llama は「読み込めなかった（load_failed）」と記録される見込み。これは技術的な失敗ではなく、申請待ちによるもの。
- **テーマ案1に進む場合のやること**：Llama の承認後に、Llama だけを測り直す（`CT0_RESULTS.json` の `runs["llama-3.2-1b"]` を消すか別ファイルにして、セル3を再実行）。本番でどのモデルを使うかは、Llama の結果も見てから決める。

## 第1版の結果と第2版（2026-10-06 23:1x JST、本番の前の技術的な手直し）
- 第1版（`CT0_RESULTS.json`、Drive に残す）：
  - Llama・Gemma：Hugging Face のトークンが読めず、利用許可の確認で 401（gated）。モデルの問題ではない。
  - Qwen3 1.7B：TransformerLens での読み込みで GPU メモリ不足（L4 22GB）。nnsight では読めたが、200トークンでも3段階すべてメモリ不足。部品（low-L0 トランスコーダー）が大きすぎるため。
- 第2版で変えたこと：
  - トークンの読み込みを、失敗の理由を表示する形にし、モデルごとの利用許可をセル1で確かめて表示する。
  - Qwen3 1.7B → **Qwen3 0.6B**（`mwhanna/qwen3-0.6b-transcoders-lowl0`、`lazy_encoder=True`）。
  - 読み込みでメモリ不足になったら、もう一方の読み込み方は試さない（失敗した読み込みがメモリを残すため）。
  - 結果は `CT0_RESULTS_v2.json` に分けて保存。
- 次に進む条件は変えない。
- 第2版のアップロード：Drive `DECISION_POINTS/CT0_FEASIBILITY_v2.ipynb`（id `1mCkLRjtsGnKDGGMHcASdv35yKl2yE4b6`、13,951 B。手元のサイズと一致）。ビルダーはコミット `a3f74ca`。

## CT-0b（2026-10-06 23:5x JST、第2版の結果を受けた追加の確認）
- 第2版の結果（`notes/ct_feasibility_result.md`）：Qwen3 0.6B は条件を満たしたが、読める部品の質（置き換え 0.34〜0.38）が低い。本命は Gemma-2 2B（置き換え 0.63）にしたいが、L4 では400トークンがメモリ不足。Llama はCPUに逃がす設定でライブラリの不具合。
- CT-0b：**A100**で Gemma-2 2B と Llama-3.2 1B を、CPUに逃がさずに 200・400・600 トークンで測る（まとめて128→32、部品7500→4000の順に軽くする）。200トークンは2回作って再現性を見る。結果は `CT0b_RESULTS.json`。
- 次に進む条件は同じ（400トークンが10分以内、2回の差 0.01 未満）。Gemma が満たせば本命は Gemma、Qwen3 0.6B を再現用にする案。
- CT-0b のアップロード：Drive `DECISION_POINTS/CT0b_A100_GEMMA.ipynb`（id `1GDq7JDBtcJXaj0VH8Tx25bhKfS4Vn63F`、14,350 B。手元のサイズと一致）。ビルダー `scripts/build_ct0_notebook.py OUT b`（コミット `f5296e1`）。
- CT-0b 1回目（2026-10-07 00:0x JST、A100 80GB）：HF_TOKEN のアクセスがOFFのまま回り、両モデルとも no_access で「終わった」扱いになって、やり直しを受け付けなかった。セル3を、no_access と load_failed のモデルはもう一度試す形に直した（前の記録は `earlier_attempts` に残す）。測定の中身は変えていない。
- 直した版のアップロード：Drive `DECISION_POINTS/CT0b_A100_GEMMA_v2.ipynb`（id `1s8SaR0pW__XMG9fccouubEF2-3bKv5Ap`、15,089 B。手元のサイズと一致）。ビルダーはコミット `d42828a`。
- CT-0b 2回目（2026-10-07 00:5x JST）：また両モデルとも GatedRepoError。結果ファイルには「トークンを読めたか」が残っていなかったので原因を切り分けられない。トークンの読み込みと利用許可の確認を関数にして、**セル3の最初でも読み直す**ようにし、読めたか・Hugging Face に受け付けられたか（ユーザー名）を結果に記録する。トークンは有効なのに使えない場合の案内（利用規約の同意、Fine-grained トークンの gated 読み取り権限）も表示する。測定の中身は変えていない。
- 第3版のアップロード：Drive `DECISION_POINTS/CT0b_A100_GEMMA_v3.ipynb`（id `18rXbq96hrI7pFbKCZaaz6tfTkImEA3qc`、16,351 B。手元のサイズと一致）。ビルダーはコミット `4b10409`。
- CT-0b 3回目（2026-10-07 01:0x JST）：結果の記録で原因が分かった。`userdata.get("HF_TOKEN")` が **TimeoutException**（Colab の「シークレットへのアクセスを許可しますか？」の確認に、時間内に応答がなかった）。トークン自体の問題ではない。第4版：シークレットは HF_TOKEN の名前だけを読む（確認が何度も出ないように）。読めなければ、画面に表示されない入力欄（getpass）でトークンを貼ってもらう。セル3では入力欄を出さず、セル1で得たトークンを使う。トークンはファイルにも出力にも残さない。
- 第4版のアップロード：Drive `DECISION_POINTS/CT0b_A100_GEMMA_v4.ipynb`（id `1BglfJ8MltWhemALyEiPfxMhmModYUwsc`、17,640 B。手元のサイズと一致）。ビルダーはコミット `75b9b66`。
