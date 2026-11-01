# PARA-1 第7版・独立狭域確認レビュー（GPT-6）

**Verdict: PASS（第6版の U2-B 修理に対する計画レベルの確認）**  
**Earliest freeze-blocking point: NONE within V1/V2 narrow scope.** ただし G0/G1 等の実行合格やオーナー凍結を意味しない。

## 読んだ証拠と実行範囲

- 対象：`chichichi2001/Pork`、`decision-points`、固定コミット **`dff35fc61792c58a74f8c5d70388dd9287e0b236`**。
- 依頼書：`notes/para1_review_request_v7.md`、blob **`1d89bf00ee629182b0f719e398b6c19fa48f71ef`**。
- 第7版計画：`notes/para1_paraphasia_plan.md`、blob **`6750972ee526302168d9e9dc0ccf07468d6f833b`**。特に G2（236–243行）と第7版の改訂記録（330–332行）。
- 前回レビュー：`notes/para1_independent_review_v6_20261012_gpt6.md`、blob **`421b6c7fa8060f90ca1b7ff312bbf5643d99719a`、コミット `ae20befe670b5e3a0c01922410f8555cc2bc3c77`。
- 試作：`scripts/para1_typing.py`、blob **`9c0eae53b81a83a3df87b7f72e1d643cf8f5cfd0`（第5版以降不変）。
- **静的監査のみ**：GitHubにある依頼・diff・計画・前回レポート・試作の記述を照合。G0/G1/G1b/G2/G3、実モデル／トークナイザー／GPU、ベクトル照合、負対照、NaN/Inf注入、G0cは**実行していない**。作者側の旧dry-runは独立実験PASSと呼ばない。ベンチマークの非公開問題文／トークン文字列は取り扱わない。計画・コードを書き換えていない。

## V1：位置対応の修理 — **PASS**

- G2の入力IDを、G1b固定の**テンプレート・BOS込みprompt IDs + baseline IDs**と定めた。0-indexのbaseline `g_t` に対応するlogitの位置は、標準的なcausal LMで **`len(prompt_ids)+t-1`**。特に `t=0` はprompt最後の位置であり、境界が明文化された。
- G1の**2問**で、同じprefix IDを用いた逐次推論とteacher-forced一括推論の**logit全ベクトル**を各対象位置で比較し、最大絶対差 `<=1e-3`、top20 ID・順位の一致（同点除外）を要求する。これは前回の「argmaxがAなら1位置ずれを見逃す」反例に対する、実効的な独立確認ルート。
- 意図的な `t±1` の位置ずらしを負対照にし、反復ID8個の人工列も要求する。いずれか失敗なら**G1bへ進まない**。最大トークン一致率はG2で**補助診断**と明記し、位置ずれ不存在の証明から降格した。前回 **U2-B BLOCKING は解消**。
- **nonblocking注意**：`t=0` に存在しない `t-1`、最終位置に存在しない `t+1` は負対照から除外する。負対照の「top20が違う位置が少なくとも1つ」は**データ次第**で、正しいindexでも同じtop20が続く可能性がある。陰性対照の情報不足でG1が止まったら、**実装不正と断定せず `NEGATIVE_CONTROL_UNINFORMATIVE` 等で停止して記録**する。正対照のベクトル比較の合格と、位置ずれの一般的な数学的証明を混同しない。`1e-3` はGPUカーネルの数値差で不合格になる場合があるが、事前に固定した保守的停止条件として問題はない。

## V2：保存・診断・NaNの追加修理 — **PASS**

- G2開始前に**npzファイルの実bytesのSHA256**と、モデル重み／tokenizer revision、prompt template ID、問題別baseline SHA、対象・除外位置集合をG1b manifestと照合。不一致なら `G2_MANIFEST_MISMATCH`。これらを「G1bの一覧」の必須フィールドとして実装する契約と解釈できる。
- 除外位置の12条件 `M_S` は、**別ファイル・別集計**に置き、主の分母、型、被覆、帳尻、G3母集団へ混入しないことをG1で確認する。
- logits、logsumexp、`M_S`、tailのNaN/Infで `PROTOCOL_AUDIT_FAIL`、診断用 `M_S` にも適用。G1に人工NaN/Inf注入の停止テストを明記。第5・6版からの新たな論理矛盾は認めない。
- **nonblocking実装メモ**：G1b manifestにrevision等を実際に保存すること、該当する全位置で同じ0-index定義を使うこと、`1e-3` とtop20順位を数値的タイに対して慎重に扱うことを、G1の記録で明らかにする。

## 結論

**V1: PASS / V2: PASS / 凍結を止める修理上の残件: NONE（今回の狭域）。** 凍結承認は**オーナーの別判断**。実物のトークナイザーのG0b、人工G0c、G1での実ベクトル比較が通るまでは、**実験が検証済み**とは言わない。これまでの非変更箇所を新たに監査したとの主張もしない。

**Audit label:** GPT-6 / PARA-1 V7 NARROW INDEPENDENT CONFIRMATION / FIXED SHA `dff35fc61792c58a74f8c5d70388dd9287e0b236` / **PASS (PLAN ONLY)** / NO OWNER FREEZE / NO NEW EXPERIMENTS.
