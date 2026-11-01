# PARA-1 第6版・独立狭域修理再レビュー（GPT-6）

**Verdict: PASS WITH REPAIRS** — 前回のT1-L1/T2-L1修理は解消。ただし **U2のlogit位置対応の確認方法に局所blockingが1件残る**。
**Earliest freeze-blocking point:** U2：単純な「logitのargmax = baseline g」の一致率だけでは、teacher-forcingの**1位置ずれを排除できない**。位置の明文契約＋G1内でstepwise-vs-batched logitsの同位置比較が必要。オーナー凍結は行わない。

## 固定した証拠・実行範囲

- 2026-10-12 JST、repo `chichichi2001/Pork` / branch `decision-points`。
- **監査対象コミット：`3f75bb895b2e1036ab2149950c3da243ea1deae3`**。着手時のbranch HEAD。
- 依頼：`notes/para1_review_request_v6.md`、blob `156085a1aba3265837b4000676b500a2cda2d90a`。
- 第6版計画：`notes/para1_paraphasia_plan.md`、blob `ad57c660457d31d21e49a65f6a89943109d32fc3`。
- 前回レビュー：`notes/para1_independent_review_v5_20261012_gpt6.md`、blob `c8fe3033a4befab100fcf2f848692da9384fa4ae`、保存commit `dbe77ada3e1151826fc3d31ece89e6420d1a0630`。
- 試作コード `scripts/para1_typing.py`、blob `9c0eae53b81a83a3df87b7f72e1d643cf8f5cfd0`。**第5版から不変**。
- 今回変更されたのは第6版計画と依頼書の2ファイル。レビュー範囲はその差分に関係する **U1（旧T1-L1）、U2（旧T2-L1）、U3（非有限数とargmax記録）のみ**。P1〜P5、CR-1、WordNetの全面レビューはしない。
- **SOURCE-READ / STATIC-ANALYSIS:** 固定GitHubソースとdiff、前回レビューを読んだ。新しいGPU、API、実OLMo/Gemma tokenizer、G0c、G1/G1b/G2/G3の実行はしていない。第5版のdry-run `reports/para1_g0_dryrun_v5.txt` の30+15+19+4一致は作者側の既存記録で、独立再現PASSではない。ベンチマーク問題文と生成単語・トークン列は見たり表示したりしていない。

## 修理項目の判定

| 修理 | 判定 | 理由 |
| --- | --- | --- |
| **U1 / T1-L1** | **解消・PASS** | 除外位置もG2で12条件のM_Sのみ算出・別保存。本解析の型・分母・被覆・帳尻・G3から排除する契約が明確 |
| **U2 / T2-L1（保存・SHA照合）** | **解消・PASS** | G1bの実token IDsを非公開Drive npzへ保存、場所/ファイルSHA/問題順/dtypeをGit manifestへ、G2読み込み時に照合・不一致停止 |
| **U2（修理で追加した位置対応確認）** | **一部解消、1件BLOCKING** | argmaxの高い一致率だけではlogitsとgの正しい位置対応を確証できない |
| **U3** | **概ね解消・PASS** | NaN/Inf停止、1%以下のargmax不一致件数・同点・gapも報告、固定gというscopeを明示 |

## U1 — 除外位置の診断M_S（PASS）

**根拠：計画149・236行。**

G1bで固定した `EXCLUDED_TARGET_DECODE_MISMATCH` と `EXCLUDED_EMPTY_TARGET` の位置も、G2でlogitsと12 samplerを実行して診断専用の`M_S`を算出する。除外位置に保存するのは除外理由と12条件の`M_S`だけで、候補上位1000、型分け、未分類tail、本解析の分母・被覆・帳尻、G3抽選母集団には含めない。旧版の「M_Sを報告するのに計算経路がない」矛盾は**解消**。

**Nonblocking:** validとexcludedの保存レコードと集計器を分離し、診断M_Sが主解析に混入しないことをG1で人工・小規模検査する。`PROTOCOL_AUDIT_FAIL` のNaN/Inf停止は診断位置にも適用する。除外位置の件数・M_Sは理由別／model別／sampler別を区別。

## U2 — G1b→G2の固定データ契約（保存はPASS、indexチェックにblocking）

**根拠：計画233–240行。**

### U2-A: 実token IDsの保存と照合 — PASS

G1bの数値ID列（prompt＋baseline）をモデル別に問題ID順、int32のnpzとしてDriveへ保存。Git側の事前manifestには場所、ファイル名、SHA256、問題順、dtype、各問題のbaseline SHA、対象/除外位置、G3選択位置を記す。G2は読み込み時にファイルSHA・問題単位baseline SHA・位置集合をすべて突合し、1件でも違えば `G2_MANIFEST_MISMATCH` で停止。**ハッシュだけ記録してもG2でIDを復元できない**という前回の指摘を解消した。

**Nonblocking:** raw npzファイルbytesのSHAかcanonical array-bytesのSHAかを固定。G1b/G2の**model weight revision・tokenizer revision・prompt template identity**が同じこともmanifestで比較するとより堅牢（計画の既存「実行ごとrevision保存」と接続すればよい）。

### U2-B: argmax一致率だけでは位置ずれを検知し尽くせない — **BLOCKING**

第6版の238行には「logitの位置tの最大トークン = 土台のt番目のトークン」の一致率を用いて**位置がずれていないことを確かめる**とある。これは**有用な診断**ではあるが、正しいindex対応の証明ではない。

**人工反例（実データ由来ではない）:** baseline IDsが `[A,A,A,A]` で、各時点の正しいlogitベクトルは異なっていても全時点でargmaxがAなら、logit列を誤って1位置ずらしても、gとargmaxの一致は**100%**。反復がなくても、複数位置で同じargmaxが現れれば同様の偽陰性は成立する。「1位置ずらすと一致率が大きく下がる」は**必ずしも成り立たない**。

**最小修理（G1の2問内だけで可能）:**
1. `input_ids = prompt_ids ++ baseline_ids` とし、0-indexのbaseline `g_t` を予測する**通常のHF causal-LM**出力位置は `outputs.logits[0, len(prompt_ids)+t-1, :]` と明記する。BOSやchat template、モデル固有前処理により例外があればそれも固定。入力のtoken 0を予測する場合のspecial-caseも明示。
2. **G1の2問だけ**、同じprefix IDを使ったstepwise greedy次トークンlogitと、G2方式の一括teacher-forcing logitsを**ベクトル／複数位置で直接比較**する（数値差・top IDs等を保存）。その上で意図的off-by-oneの負対照、反復tokenの無害な人工indexテストを加える。これならargmaxのみでは見えないshift誤りを検知できる。
3. `BASELINE_ARGMAX_MISMATCH`の件数、同点、argmax-vs-g gapは従来どおり**補助診断**として残す。1%というゲートは固定greedy土台への相違の品質基準であり、indexの数学的保証ではない。

以上は計画書に一段落を追加し、既存G1を少し補強するだけで十分。新しい100問GPU実験を要求するものではない。

## U3 — 非有限停止とgreedy不一致ログ（PASS、解釈制限のみ）

**根拠：計画237–240行。**

- logits、logsumexp、M_S、tail_SがNaN/Infなら即 `PROTOCOL_AUDIT_FAIL`。診断用のexcluded M_Sも、無言で除外して本解析だけ続行してよいとは書かれていない。
- `BASELINE_ARGMAX_MISMATCH` は1%超で部Bのラベルを停止、1%以下でも**件数・同点の有無・argmaxと固定gのlogit gap最大値**を保存。出力を「固定した土台のgとの比較」と限定している。
- ちょうど1%は許容、超えればラベル抑制という規則は明確。分母0の場合の表示はG1段階で規定しておくと良い（nonblocking）。
- **位置照合が正しいことはargmax一致率からだけでは導けない**。ここはU2-Bの修理対象であり、U3の記録品質と混同しない。
- 追加のNaN/Inf停止の実装・テストは**まだ書かれておらず**、このPASSは記述された**計画の静的整合性**を指す。

## 狭域結論・最小修理

1. **前回の2つの残件（T1-L1, T2-L1）はいずれも解消**。これは独立にソースdiffから確認した。再修理不要。
2. **新たな局所blockingはU2-Bの1点**：teacher-forcingの正しいlogit indexを明記し、G1に**stepwise vs batchedベクトル一致**を追加。argmax比較は補助診断へ。
3. 非blockingとして、revision等のmanifest突合、除外専用massの集計独立性、NaN/Infの人工入力での停止試験をおすすめする。
4. **Verdict: PASS WITH REPAIRS**。G0（実tokenizer）、G0c、G1、G1b、G2、G3は未実行。オーナーが別途承認する前に**凍結はしない**。計画・コード・既存データは変更していない。

**Audit label:** GPT-6 / PARA-1 V6 NARROW EVIDENCE-BASED INDEPENDENT REPAIR REVIEW / FIXED-SHA `3f75bb895b2e1036ab2149950c3da243ea1deae3` / PASS WITH REPAIRS / 1 INDEX-ALIGNMENT LOCAL BLOCKING / NO OWNER FREEZE.
