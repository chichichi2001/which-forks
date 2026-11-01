# CR-2 段2 の固定（記録）

PRIVATE UNPUBLISHED RESEARCH.

- 実行：2026-10-13 22:03 JST ごろ、Colab CPU、`notebooks/CR2_STAGE2.ipynb`（コード a9fd534）。**API には何も送っていない。** 問題文は表示も保存もしていない（数・ID・ハッシュだけ）。
- 記録のファイル：`notes/cr2_lock_stage2.json`（Drive の `DECISION_POINTS/cr2/STAGE2/CR2_stage2_lock.json` とバイト単位で同じ。sha256 `f89fd9e886d632dbe3e7e95cf5be5bfa4a7b594d712010abfb6ee2f924b877fd`）。

## 中身（数だけ）

- データ：`McGill-NLP/CHASE-Math`、版 `a8fb6a26…`、`test_chase_math.json`。
- **ファイルの証跡（H4・I3）**：LFS ではないファイル。Hugging Face が示す git の blob の SHA-1 `4792f0943ebb3b208d1fb141058241f38e701370` と、取ってきたバイト列から計算した値が一致。ファイルの sha256 **`731f2db9a590ac6c49ab7529d08dee0fcb09cc832a6462248e6939919319222c`**（1,544,313 バイト）。以後の照合はこの値を使う。
- **G-L**：固定した版の README の `license` は `mit`（README の sha256 `04f195cb…`）。表示による運用の判断（［決定B'］）で、作者への問い合わせはしていない。
- 行の数 500、正解が読めない行 0、同じ問題文の重複 0。
- 下見 3 の全 96 問の照合：`f52bb374…` と一致。除外 48 問（除外した ID の集まりの sha256 `5323fa0f…`）。残り 452 行。
- 深さ（全 500 行）：2 が 116、3 が 135、4 が 108、5 が 141。**深さ 6〜8 の行はない**（H5 のとおり、その層は「データになし（n = 0）」）。
- 候補 120 問：深さ 2〜3 が 63 問、4〜5 が 57 問。候補の sha256 **`c4bffbfa9632ed51a1222fae0bc65b256b3db0ae7e1b0d12e8bf70ac649f2339`**。
- 種（H3）：全 500 行で異なる種 448（いちばん大きい種 3 問、N_eff の目安 407）。候補 120 問で異なる種 118（2 問の種が 2 つ、N_eff の目安 116.1）。候補のうち下見 3 の 48 問と種が同じものは 2 問。
