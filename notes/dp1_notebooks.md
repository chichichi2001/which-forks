# DP1 — ノートブックの記録

PRIVATE UNPUBLISHED RESEARCH.

- ゲート：`notes/dp1_entropy_vs_forks_gate.md`（凍結 2026-10-05 15:53 JST、sha fed70f6b…）。
- コード：`pork/dp1_forks.py`・`pork/dp1_forks_runner.py`・`pork/dp1_forks_audit.py`・`tests/test_dp1_forks.py`（6件、すべて通過）・`scripts/build_dp1_notebook.py`。
- **2026-10-05 16:25 JST 移動**：オーナーの指摘（「つよい関連性はあるの？…そうじゃないなら新しい研究テーマ用のフォルダ」）を受けて、DP1をQuality-Porkから切り離した。
  - 理由：DP1の問いはQuality-Porkとは別物。共通なのは問題集・実験の仕組みと、副次のサインの1つ（委員会の候補数）だけ。
  - Drive：新しいフォルダ `MyDrive/DECISION_POINTS`（id 19aV-ByUyAwaSplyGMZsbUZTOw8r61_sD）にノートブックを置き、出力は `DECISION_POINTS/dp1/`。`ULTIMAPORK/quality_pork` は、問題の重なりの確認のために前の研究の記録を**読むだけ**。
  - GitHub：同じリポジトリに、DP1用のブランチ `decision-points` を作った（Quality-Porkの共通部品を使うため、リポジトリは同じ）。
  - 最初に `quality_pork` に上げた4本（head 8a841a6）は、実行される前にゴミ箱へ移した。
- 新しいノートブック（`DECISION_POINTS` に直接アップロード、2026-10-05 16:29〜16:37 JST）。head `9e896e1606f6708b46e7117c722125c505f255b8`（ブランチ `decision-points`）。セル1以外は最初の版と同じ（OTHER_CELLS_SHA `4d1deec59e5d…`）。サイズはローカルと一致：

| ノートブック | Drive id | バイト |
|---|---|---|
| DP1_1B_A.ipynb | 1Ft8mloIYNHobHf8xxrlo7rZW_aoZq9yE | 43592 |
| DP1_1B_B.ipynb | 1L4k5gMqsUf1k_bhubyICweLmrFxTIXah | 43593 |
| DP1_7B_A.ipynb | 1Zu4EDDu1SarvxsY4GfiREPktktqpgZU4 | 43573 |
| DP1_7B_B.ipynb | 1L70fHOiMi5N0mKwHs9gOo-rolIS-bNal | 43573 |

- 出力：Drive `DECISION_POINTS/dp1/`。1Bだけ終わると `*_DP1_INTERIM_1B.json`、両方終わると `RESULT_DP1.json`・`AUDIT_DP1.json`・`FINAL_DP1.json`。

## 実装で決めたこと（ゲートが種だけを決めていた部分。データを見る前に固定）

- S5の位置と監査の位置：行ごとに `random.Random(種 + (行+1) × 1,000,003)` で選ぶ（行の土台の道ができてから位置を選ぶため）。
- 監査の問題：1Bは `Random(202610051557).sample(range(100), 10)`、7Bは `Random(202610051557).sample(7Bの50行, 5)`。
- 土台の道の1位・2位：確率の降順、同じなら番号の小さい順（GPUのargmaxと一致することをセル5bで確認）。
- S2の区切り：位置の割合で最初の10%／真ん中／最後の10%。
- 見積もりの「最悪の場合」：土台の道が512トークン、すべての位置の続きが上限まで伸びる場合（1行あたり約13万トークン）。7Bでは48時間の線に近くなる可能性がある（セル6が止めたら、ゲートの規則どおりそこで止めてオーナーと相談する）。

## DP1-X（探索・1B）のノートブック（2026-10-06 05:0x JST）

- 計画書：`notes/dp1x_probe_exploratory_plan.md`（sha256 `60ad4b45…80ce`）。分析の前にコミット済み。
- 実行コード：`04e259d`。ビルダー：`scripts/build_dp1x_notebook.py`。OTHER_CELLS_SHA `ef007fd4d7f6…`。
- Drive `DECISION_POINTS/DP1X_1B_PROBE.ipynb`（id `17UoY1RkHq_x0juV6x9VzbtlUJqHA7Ag-`、13,301 B）。
- 出力先：`DECISION_POINTS/dp1x/`。`dp1/` は読むだけ。

## DP1-X2（事後の追加探索・1B）のノートブック（2026-10-06 05:4x JST）

- 計画書：`notes/dp1x2_followup_plan.md`（sha256 `e709307e…5183`）。走らせる前にコミット済み。
- 実行コード：`24f01cc`。ビルダー：`scripts/build_dp1x2_notebook.py`。OTHER_CELLS_SHA `4668b5563883…`。
- Drive `DECISION_POINTS/DP1X2_1B_FOLLOWUP.ipynb`（id `11e_at_BzZRxdnIUPzfQex4v_i_4k7aQV`、14,698 B）。
- 出力先：`DECISION_POINTS/dp1x/DP1X2_1B_RESULT.json`。
- 差し替え（2026-10-06 06:2x JST）：セル3の `KeyError: 'top1'` を直した版（実行コード `2199f31`、計画書 sha256 `04a1d075…9cce`、追記のみ）。Drive id `19ENTUKWqkyuY_MXFbV1hArbE2jxSFc6q`。古い版（`11e_at_…`）はゴミ箱へ。

## DP2（本番・1B）のノートブック（2026-10-06 17:1x JST）

- ゲート：`notes/dp2_real_forks_gate.md`（凍結 sha256 `15249f22…8579`、`0fff4f7`）。実装メモ：`notes/dp2_implementation_notes.md`。
- 実行コード：`9f4129c`。ビルダー：`scripts/build_dp2_notebook.py`。OTHER_CELLS_SHA `96be83ead102…`（A・B共通）。
- 独立レビュー済み（ラベルを決める部分のゲートからのずれなし。指摘は直してから作った）。

| ノートブック | Drive id | サイズ | sha256 |
|---|---|---|---|
| DP2_1B_A.ipynb | 1Y1EaT6THglxqsKiniYchAdupOEbzC-v7 | 47,856 | a87bf090…122c5e |
| DP2_1B_B.ipynb | 1uqcPEQZ6pbFiBSTLzKbWRLMBSH8se2Bv | 47,857 | e934fe16…482a9d0 |

- アップロード後にダウンロードして、手元のファイルとバイト単位で一致することを確認した。
- 出力：Drive `DECISION_POINTS/dp2/DP2_1B_{A,B}_20261006/`（単位ファイルは `units/`）。集計は `dp2/RESULT_DP2.json`・`AUDIT_DP2.json`・`FINAL_DP2.json`・`HIDDEN_DP2.json`。

## DP2-X1（事後の追加探索、2026-10-07）
- ビルダー `scripts/build_dp2x1_notebook.py`、実行コード `58023f9`（`58023f92126d3991631f340e6c80db166b46874e`）。計画 `notes/dp2x1_where_it_breaks_plan.md`（sha256 `7635002c…21f7`、コミット `b3fbc3b`）。
- Drive `DECISION_POINTS/DP2X1_WHERE.ipynb`（id `158PzWL40AzufiukliBKFtFPk78arLAsF`、10,361 B、sha256 `5a955360…e7e0`）。読み戻してバイト単位で一致。出力：`DECISION_POINTS/dp2/DP2X1_20261007/`。

## DP2-X2（事後の追加探索、2026-10-07）
- ビルダー `scripts/build_dp2x2_notebook.py`、実行コード `2d0c806`（`2d0c8062ba0de01da8b91bac5a3f3b1e91be0255`）。計画 `notes/dp2x2_definition_flip_plan.md`（sha256 `69d96dbc…0be`）。
- Drive `DECISION_POINTS/DP2X2_FLIP.ipynb`（id `1QAz_Px-vjehJmHZQMbA2cZRUl5zTRGNJ`、7,746 B、sha256 `3268aac2…e1fe`）。読み戻してバイト単位で一致。出力：`DECISION_POINTS/dp2/DP2X2_20261007/`。

## DP3（本番・事前登録、2026-10-07）
- ビルダー `scripts/build_dp3_notebook.py`、実行コード `3c74aa9`（`3c74aa95fe883479013d1ac832c86e146c4b312b`）。ゲート `notes/dp3_definition_flip_gate.md`（sha256 `70999ab3…1b1b`、凍結 2026-10-07 13:38 JST、409c277）。
- Drive `DECISION_POINTS/DP3_1B_A.ipynb`（id `1_tLkOFVYQbOfCTkFLML7cSMVTj4-PnCe`、49,205 B、sha256 `be553979…f4fa`）、`DECISION_POINTS/DP3_1B_B.ipynb`（id `1nX1IL9fEyErJD8AsCjzJxO6Pths6mYmG`、49,206 B、sha256 `1b91ae55…b8af`）。どちらも読み戻してバイト単位で一致。他セルのsha `8de74bcb…3407`。出力：`DECISION_POINTS/dp3/DP3_1B_{A,B}_20261007/`、集計は `DECISION_POINTS/dp3/`。
- 2026-10-07 14:16：セル6が両方とも、見込み記録を書いた直後の読み戻し確認（`atomic_json` のassert）で停止。`units_done` がタプルのため、JSONの読み戻し（リスト）と一致しなかった。記録ファイル自体は正しく書けていた（A 約3.0時間、B 約3.1時間、16時間の基準より下）。そのため同じセッションでセル7a → 7へ進めることにした。ビルダーは1b1bb96で修正済み。実行中のノートブックは差し替えない（再開時はセル6ではなくセルRを使うため）。

## DP3-X1（事後・並べ替えの対照、2026-10-08）
- ビルダー `scripts/build_dp3x1_notebook.py`、実行コード `c197fab`（`c197fab2bb6fd090cc78252918ce1393552f8fad`）。計画 `notes/dp3x1_permutation_plan.md`（sha256 `3c876ec5…a0d`）。
- Drive `DECISION_POINTS/DP3X1_PERM.ipynb`（id `12QkFdZeDoF3k-aTfJhxYcEdG2NJVjQe-`、7,556 B、sha256 `61876b9f…cfce5`）。読み戻してバイト単位で一致。出力：`DECISION_POINTS/dp3/DP3X1_20261008/`。

## DP4（本番・事前登録、2026-10-08）
- ビルダー `scripts/build_dp4_notebook.py`、実行コード `b64a006`（`b64a0065590662c2270d110c80ff095f41f80f5e`）。ゲート `notes/dp4_weighting_gate.md`（sha256 `4a8570c2…7828`、凍結 2026-10-08 09:04 JST、644ef87）。
- Drive `DECISION_POINTS/DP4_1B_A.ipynb`（id `1u99CbpepMesXLnsBPFvbiGwZwkv5u2pI`、49,580 B、sha256 `a39381f6…7906`）、`DECISION_POINTS/DP4_1B_B.ipynb`（id `1MYgsKXqobNwfHxrWkifSzQbORIpy9YKf`、49,581 B、sha256 `78c32788…4c86`）。どちらも読み戻してバイト単位で一致。他セルのsha `b43f462e…a58c`。出力：`DECISION_POINTS/dp4/DP4_1B_{A,B}_20261008/`、集計は `DECISION_POINTS/dp4/`。

## DP5（本番・事前登録・Gemma-2-2b-it、2026-10-08）
- ビルダー `scripts/build_dp5_notebook.py`、実行コード `fd5b175`（`fd5b17566df21a1c0522afa53b97f4af8b42d552`）。ゲート `notes/dp5_gemma_replication_gate.md`（sha256 `5eee532e…71be1`、凍結 2026-10-08 19:03 JST、79b184f）。
- Drive `DECISION_POINTS/DP5_GEMMA_A.ipynb`（id `1hg-ipDRSzSNFqufrsoaOfpZkfGpbI_8g`、53,604 B、sha256 `3763da70…2ef1`）、`DECISION_POINTS/DP5_GEMMA_B.ipynb`（id `1ZcTIt16KP5KBtZZFU0GtWoLAWzraHdB_`、53,591 B、sha256 `b1cf69c7…0280`）、`DECISION_POINTS/DP5_GEMMA_C.ipynb`（id `1r_AAv-fVRGmRUy7DjWWnq5uYhyO6Mz_A`、53,591 B、sha256 `5888a775…860f`）。3本とも読み戻してバイト単位で一致。他セルのsha `f21870e0…3b71`。出力：`DECISION_POINTS/dp5/DP5_GEMMA_{A,B,C}_20261008/`、集計は `DECISION_POINTS/dp5/`。

## DP6 予備（採点しない・h を決める、2026-10-09）
- ビルダー `scripts/build_dp6_calib_notebook.py`、実行コード `ac77535`（`ac775351e4f0fb1a8be64d0777c94e737b1c3ec7`）。ゲート `notes/dp6_lookup_gate.md`（1段目の凍結、sha256 `bc2ff5d0…eae8`、d4d0f4a）。
- Drive `DECISION_POINTS/DP6_CALIB.ipynb`（id `1iDoDUioS2jyQ9B5YVFPcYigIRdCyg6lq`、15,496 B、sha256 `13dc3d16…f956`）。読み戻してバイト単位で一致。他セルのsha `933edca4…8492`。出力：`DECISION_POINTS/dp6/CALIB_20261009/`。
- 手元で、セル3・4をモデルの代わりの偽物で最後まで実行し、再開（記録があるモデルを飛ばす）も確かめた。

## DP6 予備・差し替え（修正 A1 のあと、2026-10-09 11:41 JST）
- 修正 A1（`notes/dp6_amendment_A1_answer_line.md`、sha256 `5e72a69d…e20e`、e8b729e）を入れた版に作り直した。実行コード `e8b729e`（`e8b729e89c41283896e2bc84cd8959c5816dfc4b`）。セル2で修正 A1 のハッシュも確かめる。
- Drive `DECISION_POINTS/DP6_CALIB.ipynb`（**新しい id `1L-7e3WoJhjzH2I8-9G6CZ6nNM-vtE7uh`**、15,737 B、sha256 `99556f80…c34b`）。読み戻してバイト単位で一致。他セルのsha `5a631f73…b19f`。出力先は前と同じ `DECISION_POINTS/dp6/CALIB_20261009/`。
- 修正 A1 の文書には「同じファイルの中身を差し替える（リンクは変わらない）」と書いたが、Drive の接続では既存ファイルの中身を書き換えられなかったので、**新しいファイルとしてアップロードした（リンクが変わった）**。手順の違いだけで、中身・コード・判定には関係しない（修正 A1 の文書はハッシュで固定しているので書き換えず、ここに記録する）。
- 旧版（id `1iDoDUioS2jyQ9B5YVFPcYigIRdCyg6lq`、ac77535）は、名前を `DP6_CALIB_旧版_ac77535_使わない.ipynb` に変えて残した。誤って開いて実行しても、セル1の自己照合が `DP6_CALIB.ipynb`（新版）のセルと食い違って止まる。予備の結果ファイルは、差し替えの時点で Drive に1つもなかった（誰も実行していない）。
- 手元で、セル3・4を偽物のモデルで最後まで実行（`**Answer**:` と `Answer:` の両方の書き方が「読めた」になることも確認）、再開も確認。続けて、その偽物の結果に2段目のスクリプト（`scripts/dp6_stage2.py`、CALIB_COMMIT = e8b729e）を当てて h と長さを書き込み、本番4冊のビルダーが通ることも確かめた（作業用のコピーで。リポジトリには入れていない）。

## DP6 本番（Gemma のみ・2冊、2026-10-09 13:14 JST）
- 2段目の凍結（`notes/dp6_stage2_h.md`、sha256 `2b58182e…0af8`、59a15a6）：Gemma は h = 1（「ふつう」の長さ 79 トークン）。OLMo は予備の正解率がどの h でも 0.20 未満だったので `DP6_NON_DISCRIMINATING_OLMO`（本番なし、ゲートの決まりどおり）。
- ビルダー `scripts/build_dp6_notebook.py`、実行コード `59a15a6`（`59a15a6d421d19587ebff88b11aac8c0ec8e15ef`）。他セルのsha は2冊とも `586c22dd…2222`。
- Drive `DECISION_POINTS/DP6_GEMMA_A.ipynb`（id `1_CIUROFoGuHlxvHmeO_POqAMK_w5P86J`、54,455 B、sha256 `5df8108a…`）、`DECISION_POINTS/DP6_GEMMA_B.ipynb`（id `1mHLRDOONQ3SyPEw01PLlZrpD_C2OjFyI`、54,456 B、sha256 `d1b3251f…`）。2冊とも読み戻してバイト単位で一致。
- 出力：`DECISION_POINTS/dp6/DP6_GEMMA_{A,B}_20261009/`、集計は `DECISION_POINTS/dp6/{RESULT,AUDIT,FINAL}_DP6_GEMMA.json`。
- 確認：DP5・DP6 のテスト36本が通過（2段目の値とハッシュのテストを追加）。ノートブックのセルが使うモジュールの名前がすべて実在することを静的に確認。予備の実行ノートブックのコードのセルは、ビルダーの版と一致していた。

## R1（査読ラウンド1への追加分析・事後・CPU）— 2026-10-09
- 計画：`notes/r1_review_analyses_plan.md`（凍結、sha256 `b1646b3a…f7d5`）。実装のメモ：`notes/r1_implementation_notes.md`。
- ビルダー `scripts/build_r1_notebook.py`、実行コード `ef8def3`（`ef8def31f94f66d582184d634d4e9dd81906a454`）。他セルのsha `0c6753a9…802f`。
- Drive `DECISION_POINTS/R1_REVIEW.ipynb`（id `1rdinha9eo0XmgrAgeKRtayileBHgfhSr`、15,683 B、sha256 `5deed857…5aa0`）。読み戻してバイト単位で一致。
- 入力（読むだけ）：`DECISION_POINTS/dp3〜dp6/` の各実行フォルダ。出力：`DECISION_POINTS/r1/R1_20261009/R1_TABLES.json`（数字だけの位置の表）・`R1_RESULT.json`。
- 確認：テスト14本が通過（DP5 の形の作り物のデータで、DP5 の解析と同じ数字が再現されることを含む）。別のエージェントが計画とコードを照合し「そのまま回してよい」。

## DP7（本番・事前登録・Gemma-2-2b-it・確率をそろえた入れ替え、2026-10-10 未明）
- ゲート `notes/dp7_matched_swap_gate.md`（sha256 `fa30c6ef…ec0f5`、凍結 2026-10-09 23:03 JST、8a9caa4）。実装のメモ：`notes/dp7_implementation_notes.md`。
- ビルダー `scripts/build_dp7_notebook.py`、実行コード `5592aa7`（`5592aa76bdd1d0576af563f241f2e31c96d33511`）。他セルのsha は2冊とも `0b00bfe6…4bdd`。
- Drive `DECISION_POINTS/DP7_GEMMA_A.ipynb`（id `1sXMimr7nhPP8L-omAYtwgOs2honMVOyA`、58,693 B、sha256 `5b0ed3f0…61c9`）、`DECISION_POINTS/DP7_GEMMA_B.ipynb`（id `1fEYobL1sGnb4HN623aBb7TBT2BaQodJR`、58,680 B、sha256 `376638a0…575c`）。2冊とも読み戻してバイト単位で一致。
- 出力：`DECISION_POINTS/dp7/DP7_GEMMA_{A,B}_20261010/`、集計は `DECISION_POINTS/dp7/{RESULT,AUDIT,FINAL}_DP7.json`。
- 確認：DP7 のテスト12本、DP5 の8本、R1 の14本が通過。別のエージェントがゲートとコードを照合し「そのまま回してよい」（細かい4点は直した）。全セルが構文として読め、セルが使うモジュールの名前がすべて実在することを静的に確認。偽物のモデルで作った本番の形の記録に集計をかけ、最後まで通ることも確認。
