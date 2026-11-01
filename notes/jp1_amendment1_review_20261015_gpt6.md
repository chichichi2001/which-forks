# JP-1 変更1（A-2）独立技術レビュー — GPT-6（2026-10-15 JST）

**判定：PASS WITH REPAIRS。実装・G0第2回を止める最初の点：NONE。** ただし以下の改善事項は、実装時の停止条件・結果開示に必ず落とし込むことを推奨。**これはレビュー判定であり、オーナーによる変更承認・凍結変更ではない。**

**監査した固定commit**：`chichichi2001/Pork` / `decision-points` / `7ea84c98a73e4645817cf79309909f2c8f6676a0`。これ以後の別研究のcommitはJP-1の根拠に使用しない。

## 一次資料とGit blob SHA-1

| 資料 | SHA-1 |
| --- | --- |
| `notes/jp1_amendment1_review_request.md` | `9911329497ec8f915181ed91c9c28ab02420a05a` |
| `notes/jp1_amendment1.md` | `4a1565ee6def7da02c9665b92b61d44f5e11b861` |
| `notes/jp1_sarashina_gate.md`（凍結計画） | `d035c49cb66fbe74ec0680cca7ee2bc99d079154` |
| `notes/jp1_after_freeze.md` | `8b94933f08f7bebdf23658c3ef11afbc93b67346` |
| `notes/jp1_lock_pre_g0.md` | `108637c4676c5846808d55210a72dba15346ba96` |
| `pork/jp1_shared_prefix.py` | `5ec0483bb1fad8fcb634a1aeb35fb8f12a5f0bb9` |
| `tests/test_jp1_shared_prefix.py` | `84ee032993e67f0510bf79c3ee39389ffa390335` |
| `pork/ct1_runner.py` | `116c53d22f1c8fe8289e0241edd5738ad59f5650` |
| `pork/ct1_forks_replacement.py` | `8247fce66ffbc10e42489ebefb7e0ac3b4da8d53` |
| `pork/jp1_runner.py` | `27f6eed89d73f73abdcf759f610e2766d54f5dc2` |
| `scripts/build_jp1_g1diag_notebook.py` | `b635af4c343a61f0c39129d5f9c137bb7689be43` |
| `scripts/build_jp1_prefix_check_notebook.py` | `49486d0533905d291d36114d0219c625ccc1e08a` |

**検証範囲・実行区分：** 上記のGitHub固定commitの記述と実装を静的に照合し、純粋な算術で32本中1〜3本の出力不一致の比率（1/32〜3/32）とL4余裕（23.66−21.18＝2.48 GB、約10.5%）を**独立計算**。既存のL4/G0/G1DIAG/PREFIXCHECKの数は、`notes/jp1_after_freeze.md`および変更書に記された**ClaudeによるDrive結果転記**を読み、生成ノートブックの測定手順と照合したのみ。**実GPU/Colab実行、Drive元JSONの新規取得、GitHubのpytest実行、MGSM問題・トークン・単語本文の閲覧、G0再実行はしていない。** `tests/test_jp1_shared_prefix.py`を読んだことをテスト実行と呼ばない。

## R1 — float32へ変更しG1 64-token完全一致を維持：PASS

凍結計画のG0-5は「DP5と同じ合格基準」であり、**dtype自体を変更不可とは固定していない**。bfloat16 G1失敗を理由に基準を緩めるのではなく、より高精度にしてE2/G1/B1を元の基準で再検査する方針は合理的。既存診断はbf16での僅差順位反転とfloat32での一致を支持するが、診断だけからあらゆる入力の数値安定性が証明されたわけではない。

**R1-R1【直したほうがよい／変更C1・C3】** `allow_tf32=False`・`float32_matmul_precision="highest"`の確認は適切。変更後のworker・G0・事後再生監査が**全て同じdtype/attention/TF32条件**を先に確認し、違えば推論前に止めること。既存`jp1_runner._main`には`model.dtype == torch.bfloat16`のハードコードがあるので、改訂C3の修正を落とさない。環境由来の再現性にはPyTorch/CUDA・GPUの版も結果へ記載。

## R2 — shared-prefix stepと推定量q／A・B：PASS WITH REPAIRS

`torch_shared_prefix_batch`は最初の同一prefixを一行でforwardし、`DynamicCache.batch_repeat_interleave(K)`・`logits.repeat(K,1)`を適用し、以後は通常のK行stepへ戻す。呼出し側`generate_batch`の固定stream、EOS、alt draw等は直接変更しない。`compute_point`と`audit_row`は同じbatch factoryを引数で受け取る構造なので、**両方に確実に新factoryを渡せば**監査対象の操作的定義は揃う。偽モデルのunit tests、実GPUの32/32 B1・48step比較の記録は有益な支持材料。

**R2-R1【直したほうがよい／変更C2・影響と開示】** 「同じ数学的サンプラー／同じモデルの目標分布」と「同じ乱数で**同じ有限サンプル結果**」を区別すること。報告上「最後の桁しか違わないのでqやラベルも同じ」と言ってはならない。48stepの実測で1〜3/32経路が変わった以上、その比較対象の最初の48stepに限ればq型の二値応答率に最大で約0.03125〜0.09375の差が**生じ得る**（実際に生じたとの主張ではない）。512step本番の差の上界でもない。A・Bのラベル閾値付近は結果が変わる余地がある。報告は「**固定した新stepが作るqの推定値**」に限定。旧stepとのビット単位一致やラベル不変は主張しない。

**R2-R2【直したほうがよい／実装・G2 replay】** 同じ新stepによるG2 replayは**乱数列・保存データの再現監査**であり、二つとも同じ系統誤差を持つ場合に「分布の正しさ」を単独では証明しない。G0ではB1と、`tests/test_jp1_shared_prefix.py`の偽モデル／固定乱数テストに加えて、**異なるprefix長とalt第一歩**を含む小さな人工GPU比較を事前固定するか、既存のGPU＋Python sampler/reference検査が**新step経路にも適用されることを明記**。事後再生の抽出行・j=0〜3・失敗基準は凍結計画のまま守る。

## R3 — G0の第2回：PASS

変更で貪欲基底の数値経路が変わるので、**初回bf16の正解率ではなく、最初から回し直したfloat32のG0 16問の正解率**に既定の閾値（3/16以下なら3Bへの一度だけの切替）を適用するのが首尾一貫している。旧G0がG1不合格で終了している以上、合格済みG0として扱わない。初回の8/16・6/16および停止理由は記録に残し、同じ問題番号／乱数・固定版を維持。新結果を見た後に別モデル・別閾値・G0集合を再選定しない。

## R4 — B2／M1／`JP1_STOPPED_PRECHECK`：PASS WITH REPAIRS

B2はK=32の**同一prefix・同一乱数に対する新stepの二度の一致**で、決定的再現性検査として妥当。不一致なら`JP1_STOPPED_PRECHECK`で止める。M1も本番同様の**2つの独立プロセス**で最長入力を走らせ、両方完走を前提とするので、変更後のフィージビリティ確認として意義がある。元のプローブ実装は`PROBE_STEPS=16`、先頭長が最長総長744から16を引いたものという**長いprefill＋16step**の試験であり、**長時間／512step／任意のランタイム条件全ての保証とは違う**。

**R4-R1【直したほうがよい／C5 M1・C6・3B切替】** L4での実測GPU使用21.18/23.66 GB、**残り2.48GB（約10.5%）**は小さい。G0第2回でM1を**採用されるモデル自身**（1Bまたは3B）、変更後のdtype・step・実際の同時worker数とメモリ設定で実施すること。3Bへ切り替える場合、1Bでの成功を流用しない。2worker以外の増員は未監査であり、`MAX_WORKERS=3`を理由に実行時に自動で3個起動しない。2workerをハードキャップし、ノートブック/監査等第三のGPUプロセスは並走させない。メモリ不足/タイムアウト/片worker異常終了は`JP1_STOPPED_PRECHECK`、**M1が真でもGPU使用量が空き容量に極端に近い場合には保守的に止まれる**よう空き容量・ピーク・ハードウェア識別子を結果に記録する。M1成功は長時間安定性の証明ではない。

**R4-R2【直したほうがよい／C5 B2とG0再実装】** B2の「K本が全一致」は**少なくとも一つの分岐後にも同じ結果になる検査**として実装し、初手logitsをK行コピーしただけで合格しないようにする。B2・M1の順番／双方合格がG0合格条件であることを明記して、単純な`B1>=29`による代替合格を許さない。

## R5 — 開示・依拠範囲：PASS WITH REPAIRS

旧G0（不合格）→診断→オーナーのfloat32/A-2選択→短いGPUプローブ→独立レビュー→修正G0という時間順と、モデル精度・計算方式の変更を明示する設計は良い。

**R5-R1【直したほうがよい／影響と開示・予算】** 結果には最低限、(a)旧G0の停止と初回正解率、(b)float32再G0正解率とモデル切替、(c)新step採用・旧stepとの48step差と限界、(d)B2・M1の検査方法・使用モデル・GPU/CUDA/precision flags、(e)メモリピーク／空き・所要時間・推定CUと**初回失敗分を含むG0以降の実消費と見込み**、(f)G2 replayの同step依存性を併記。既存の計画／版／問題集合／閾値を変更していない部分と、例外的に計算経路を変更した部分を分けて示す。保存する変更コードのcommit SHAと承認文言を記録する。

## 結論

**PASS WITH REPAIRS / earliest implementation blocker NONE。** 凍結計画のG1合格基準は保持され、G0を最初からfloat32で再実施することにも論理的矛盾はない。shared-prefixは数学的サンプラーの操作定義を維持するが、有限サンプルの値やラベルが不変との保証はない。L4での約2.5GB余裕は安全保証ではないため、採用モデルでの再M1・2worker上限・予算ガード・ログ開示を実装時に守ること。**本レビューでは元計画・変更文書・コード・承認／凍結を変更せず、レビュー文書だけをbranchへpush。**
