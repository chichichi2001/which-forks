# CR-2 コードの固定（G1 の前の受け入れ 1 の記録）

PRIVATE UNPUBLISHED RESEARCH.

- 凍結した計画 `notes/cr2_plan.md`（第10版、凍結 7949d74）の「凍結のあとのコード」の記録（`notes/cr2_freeze_record.md`）。
- **固定したコード**：コミット **a9fd5344084cdec8c402f1768cdf993056a7b86f**（独立のコードの点検の指摘を直したあと）。G0・G1 以降のノートブックは、このコミットから `pork`・`scripts`・`tests` が変わっていないことを送る前に確かめる（`git diff`）。
- **受け入れ 1 の実行**：2026-10-13 21:5x〜23:51 JST ごろ、Colab CPU、`notebooks/CR2_PREG1.ipynb`（コード a9fd534、numpy 2.1.3、Python 3.13.16）。API もデータも使っていない。6,392 秒（見込みの 30〜50 分より長かった）。
- 結果のファイル：`reports/cr2_preg1_result.json`（Drive の `DECISION_POINTS/cr2/PREG1/CR2_preg1_result.json` とバイト単位で同じ。sha256 **`920544a3476205c2285b35739ef12724e9779c773b7933bcec3118fcea20c0c5`**）。

## 結果

- **試験**：CR-2 の試験（a）〜（p）と CR-1・CR-1a・下見 3 の回帰試験、すべて合格（終了コード 0）。注：結果ファイルの `tests` の欄には、pytest の最後の行として進み具合の行が入った（合計の行ではない）。合否は終了コードで判定している。Claude の作業環境でも、同じコードで全 3,109 件の試験が通った。
- **人工データの安全診断（9 世界、合否を決める）**：すべて合格。全試行の `BEYOND_*` は 3〜97 / 2,000、片側 95% の上側の限界は 0.0039〜0.0572（決まりは 0.07 以下）。**9 世界とも記録（`reports/cr2_s2_recalibration.txt`）と 1 文字も違わない。**
- **既知の合格例の回帰確認（3 世界。独立の確かめではない）**：CHASE-Math に寄せた差なしの 3 世界で、`BEYOND_*` 108・44・16 / 2,000、上側の限界 0.0631・0.0282・0.0121。合格が再現し、記録（`reports/cr2_chase_power.txt`）と 1 文字も違わない。

## 固定したファイル（a9fd534 の Git blob）

  - `pork/cr2.py` — `e948b657b1e72e3da3f307196f2f3b61da8c17d8`
  - `pork/cr2_search.py` — `68ff28c0166bc839e2d57f70852faa201b9ba143`
  - `pork/cr2_stage3b.py` — `0bb5656d7429c0f570b94394e272eabeb357a745`
  - `pork/cr2_run.py` — `640b79ae4d4736227b7f9dcfe3823c9ebb15e9fe`
  - `pork/cr2_g2.py` — `677512051e42c6120a05c49095c6e436f5b0a1c6`
  - `pork/cr2_g3.py` — `d2b1bdf679f704055cdf838262a4b0b69935ef2f`
  - `pork/cr2_reference.py` — `e73915becc1b39f1c34ea5c24adf3169ca80b981`
  - `scripts/build_cr2_notebooks.py` — `d7abee39beda9b18b842ecc004998ea26b873a82`
  - `scripts/cr2_s2_recalibration.py` — `a908f800498ae5efd754a9971761439ca7ba88ef`
  - `scripts/cr2_chase_power.py` — `4a853fc6f872518aef3acb18a1de0883a3c7ff46`
  - `tests/test_cr2.py` — `caceba4702f6cef91b69f03397a00c02bfbe8fb4`
  - `tests/test_cr2_runs.py` — `9300e710bc11c7127c4a9470007c7764b24344e8`
  - `tests/test_cr2_search.py` — `e5c0eefdd9838b9cea5eca47a96dfb3cbc784d20`
