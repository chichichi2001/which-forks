# PARA-1 第5版：独立・狭域修理再レビュー（GPT-6）

**Verdict: PASS WITH REPAIRS（狭域の主要3指摘は解消。実行仕様の局所修理2件を条件とし、現時点ではオーナー凍結を推奨しない）**  
**Earliest remaining freeze-blocking point:** **T1／部Bの「除外位置の (M_S) 合計を報告する」契約と、G1b/G2の除外位置にlogit・samplerを計算するかの実行契約が未接続**（計画書149行、230–236行）。除外位置をG2で評価しないなら、その (M_S) は算出できない。軽量修理で済むが、凍結前に明記すること。  
**Second local contract gap:** G1b→G2で必要な**実トークンID系列の保存場所・SHA256のロード時照合**が未指定（233–235行）。「一覧にはハッシュだけ」「G2はG1bのIDを読み込む」を一貫させる必要がある。

## 監査対象と証拠の区別

- 日付：2026-10-12（JST）
- リポジトリ：`chichichi2001/Pork`、対象ブランチ：`decision-points`。
- **固定ソースコミット：`65963539735761ba2a41876e60d2c86565ffbfe4`**（着手時のbranch HEAD）。
- 依頼書 `notes/para1_review_request_v5.md`、Git blob **`ea8fba6040fe46accbf5d4ad8802338f9d2fd7d9`**：全文読了。
- 計画 `notes/para1_paraphasia_plan.md`（第5版・未凍結）、Git blob **`e920f0ab4311305344c715ff140a3ffc21dc381e`**：前版からの差分と T1/T2/T3 の関連節を確認。
- 試作 `scripts/para1_typing.py`、Git blob **`9c0eae53b81a83a3df87b7f72e1d643cf8f5cfd0`**：`decode_candidate`, `decode_target`, `type_position_candidates`, `ToyTokenizer`, `G0_DECODE` のコードとテストデータを読解。
- 事前dry-run `reports/para1_g0_dryrun_v5.txt`、Git blob **`b5e5048a038712b665a071f660ff5c071665acd3`**：記録上は通常30/30、追加境界15/15、部B19/19、接続D1–D4の4/4で不一致0。**これは作者側の保存済み実行記録。私の独立実行による再現PASSではない。**
- 前回レビュー `notes/para1_independent_review_v4_20261012_gpt6.md`、Git blob **`27a843222b55f141dfca60a7c557cdb8bbd93918`**、保存コミット `dd1e74e593a9a28f13dde2427b7dfd37ea478cfe`：前回blockingの根拠・修理要請を再照合。
- 対象は**第4版→第5版の変更箇所だけ**（T1＝旧S1、T2＝旧S3-A、T3＝旧S3-B）と、その変更に直接依存する契約の整合性。S2の統計設計、S4の66比較、旧P2の全範囲、CR-1の全面監査は**再実行・再監査していない**。
- **SOURCE-READ / STATIC-ANALYSIS：** GitHubでコード・文章・既存ログを読んだ。WordNet 3.0の独立テスト、実OLMo/Gemma tokenizer、G0c、G1/G1b/G2/G3、GPU推論は未実行。無害な人工例以外、ベンチマーク文面・生成トークン文字列は表示・収集していない。計画・試作は一切変更しない。

## 前回指摘の対応判定

| 観点 | 今回の判定 | 理由 |
| --- | --- | --- |
| **旧S1／T1：wデコード不一致の位置除外とコード接続** | **本体解消／PASS WITH LOCAL REPAIR** | `decode_target`でprefix mismatchを検出、`type_position_candidates`で候補より先に位置除外、D1–D4の仕様とコード整合。ただし**除外位置の別勘定の (M_S) 計算経路**は明文化が必要 |
| **旧S3-A／T2：G1b→G2固定の工程** | **本体解消／PASS WITH LOCAL REPAIR** | G1bで土台を生成し監査manifestをコミット、G2はteacher-forced固定IDを用いる。**固定ID実体の永続保存・ハッシュ照合**を追加すべき |
| **旧S3-B／T3：ゼロtail・負tail・logsumexp** | **解消／PASS** | 絶対/相対の許容を統一し、ゼロの除算が不要。負tailのfailとfloat64計算法も具体化 |
| 前回の旧S2（G0c）・S4（比較ラベル） | **今回の再監査対象外** | 第4版で計画上の修理は概ね受理済み。G0cの実行PASSではない |

## T1 — デコード接続と位置除外

### 合格：前回の主要blockingは解消

計画書139–149行の`decode(window + w_tokens)`が`decode(window)`をprefixとして持たなければ、対象位置をまるごと`EXCLUDED_TARGET_DECODE_MISMATCH`として捨てる契約は明確。対応する`decode_target`は`("",True)`を返し、`type_position_candidates`は候補を一つも分類せず**すべて同じ除外ラベル**にする。空wなら`classify_candidate`の最初で`EXCLUDED_EMPTY_TARGET`。これにより、従来の「special/byteが位置除外より先」事故は再発しない。

D1（通常候補5種）、D2（候補のcontext decode mismatch）、D3（target decode mismatchによる候補全除外）、D4（バイト片）の4つは、試作ソースの`ToyTokenizer`の定義を追う限り規則と期待が一致する。保存されたrunは4/4 OK。ただし`ToyTokenizer`は正式なトークナイザーの代替証拠ではなく、**real-tokenizer G0bを実行済みと解釈してはならない**。計画自身もこの限界を開示している。

### T1-L1 — 除外位置の (M_S) の別勘定（**blocking: 軽い仕様契約の欠落**）

**衝突する記述：**
- 計画書149行：除外した位置では全型量・裾・(M_S)・被覆分母・G1/G3から外し、**「除外の理由ごとに、位置の数と (M_S) の合計だけを別に報告する」**。
- 計画書230–236行：G1bで除外位置を確定し、G2では**固定した対象位置**でlogitとサンプラーを計算する。

位置をG2対象から完全に外す場合、**その位置の各サンプラー (M_S) は未計算**。G1bは土台の生成と位置特定のみを明記し、全12条件の (M_S) を算出するとは書いていない。従って計画どおりの出力項目を埋める経路が明確でない。一般に (M_S) はsampler依存なので単なる除外位置数からは求められない。

**最小修理・選択式：**
1. **推奨：** G2で除外位置にもlogit/全12 samplersを計算し、**除外質量の診断専用**にのみ`M_S`を記録。型分け・本解析の分母・G3監査対象には含めない。対象／除外位置をG1b manifestで固定する。
2. またはG1bで12条件の診断用 (M_S) だけを計算・保存し、条件とログをG2に含めず一意に固定。
3. 負担軽減が優先なら**除外位置は数と理由のみ**と定め、 (M_S) 合計の報告要求を削除（どちらを採ったか凍結前に明記）。

この問題は中心の「基準語のデコード不一致は一律除外する」という修理の正しさを覆さない。**工程とレポート項目の接続だけを直せばよい。**

### T1-L2 — 補足（nonblocking）

- 除外位置の数と理由が必ず示されるのはよい。ただしG3は除外後の位置から抽選されるので、**除外判定そのものの独立な実tokenizer確認はG0bに依存**する。G0bを通さず有効計測と呼ばない。
- 候補の`decode`が空でも空型で扱い、U+FFFDはbyte片として扱う規則は一意。**型が語全体の置換ではなく次トークンproxyである**限定は維持する。

## T2 — G1b→G2固定と `BASELINE_ARGMAX_MISMATCH`

### 合格：G1b導入は前回の工程矛盾を解いた

計画書229–243行は G1（2題の試行）→**G1b**（全候補題の貪欲土台、採点、基準語復号・除外位置、監査対象選択、モデルごとのmanifest commit）→ **G2**（固定土台によるteacher forcing、全位置logit/サンプラー）→ G3（サンプル監査）の順。土台を作る前に監査位置番号を決めようとした第4版の矛盾は**解消**。

5%の問題選択はモデル番号込みの固定seed、各問題から除外後の最大32位置。今回の修理はモデル間で異なる土台を前提とし、位置の再選択をG2結果からしない。監査用の生float32全語彙logitは選択した位置だけ本番時にSHA付き可逆保存する。この運用は整合的。

`BASELINE_ARGMAX_MISMATCH`では**G1bの固定IDを変えず**、G2のargmaxとの不一致率を報告し、全対象位置の1%超ならBのラベルを出さない。これは保守的な品質ゲートとして使える。ただし不一致が0でない場合、G2時点のgは厳密には「その再計算logitのgreedy token」とは限らない。結果に**凍結済み貪欲土台のtoken gとの比較**と明示すること。1%以下なら自動で不一致を隠してよい、という意味ではない。

### T2-L1 — G1bの実トークンIDとG2の入力データの永続契約（**blocking: 軽い工程欠落**）

**記述：** G1b manifest（233行）は「土台のトークンIDの**SHA256**」を記録し、内容はハッシュのみをcommit。一方、G2（235行）は「**G1bのトークンIDを読み込む**」とする。

SHA256から元トークンID列は復元できない。G1bが実ID列をメモリに持っていても、G2が別のジョブ/Notebookで行われる場合の入力実体と参照先が書かれていない。ここは**hash-only公開manifest＋別の非公開numeric artifact**にするだけで解決。

**最小修理：** G1bが`baseline_ids`（数値のみ）・tokenizer/prompt revision・model別problem IDを非表示の固定成果物に保存し、保存場所/ファイルID/content SHA256/配列の順序とdtypeをmanifestに記録。G2は読み込み時に全件照合して、1件でも不一致なら **G2を出さず停止**。G2のteacher-forced logitsのindexが `g` と対応しているかを、G1の2題で全位置またはサンプル位置で確認することを推奨。秘密文面・語の文字列を表示する必要はない。

### T2-L2 — 後続確認（nonblocking）

- 大きさを抑える監査位置上限32は運用可能だが、サンプル5% × 最大32位置は**全位置の監査ではない**。結果の監査ラベルもその範囲に限定する。
- `BASELINE_ARGMAX_MISMATCH`の率について、0件対象、同点と数値丸め・argmax tie-break、G2再計算でのtoken indexingのずれをG1で検知する経路を残すと堅牢。1%未満の不一致に対しても原因の件数と規模を記録すべき。
- 事前生成した土台による解析は「土台を固定した**条件付き**の分布」の測定であり、同じ条件でのnext-token logitsを使う限り自己矛盾ではない。

## T3 — 許容・負tail・logsumexp（**PASS**）

計画書167–170行：
- 一般値の比較を `abs(x-y) <= max(1e-12,1e-9*max(abs(x),abs(y)))` に定め、**ゼロにおける0除算を排除**。ID・順位・保持真偽は完全一致。
- `tail=M−top1000のqの合計` から小負値が出たら`[-1e-12,0)`だけ0に丸め、その件数・最小値を報告。`tail<-1e-12`なら`PROTOCOL_AUDIT_FAIL`。
- float32モデルlogitを直ちにfloat64へ変換し、温度で割り、**全語彙float64 `torch.logsumexp`**を採用。`top_k_40`等では真のtail=0を扱える。
- G1の帳尻とG3の独立数値監査は同じ許容式を参照する。第4版で残った「G3の相対誤差だけだとゼロtailを比較できない」矛盾は**解消**。

**nonblocking注意：** tailの負値丸めしきい値1e-12は一般許容式の相対項より厳格になり得るが、「負質量は強く疑う」保守的な停止規則として**論理矛盾ではない**。各段階で丸める前のtailもログに残し、G3では同じ丸めの順と保存値を比較すること。non-finite（NaN/Inf）検出と非有限発生時の停止を実装のG1契約に足すと、比較式がNaNを黙認しないので安全。これらを**新たなfatal theorem bugとはしない**。

## G0の記録と依頼外の範囲

`reports/para1_g0_dryrun_v5.txt`の保存記録：G0通常30/30、境界15/15、部B人工19/19、D1–D4 4/4。追加した接続関数のソース上の順序は、人工expectedと整合する。ただし**WordNetに依存する型の真偽は独立に再実行していない**。モデルの実tokenizerでのbyte境界・round-tripも未試験、G0cの200世界は未実行。ログに「本番G0がPASS」とは書かないこと。

部AのCR-1以前の事前登録と、部BのG1b固定は別問題。今回のreviewを**owner freeze / experiment authorization / manuscript review**へ転用しないこと。

## 優先する最小修理・再レビュー

1. **T1-L1（最初のfreeze-block）：** 除外位置の (M_S) 診断を誰が計算するか（G1b／G2／削除）を明記し、抽出ラベル・被覆・G3と混ざらないようにする。
2. **T2-L1：** G1bのnumeric baseline IDデータ実体をどこへ保存し、G2でmanifestハッシュをどう照合するか定義する。
3. T3は再修理不要。G0bの実tokenizer・G0c・G1の試験は**計画凍結後・本番前の既定ゲート**として引き続き必須。新たな研究課題やGPU campaignを追加しない。
4. 上記2件を凍結前に一行〜一段落程度で補足すれば**狭域再監査のみ**で足りる。オーナーが別に凍結承認するまで、計画は未凍結。

**Audit label:** GPT-6 / PARA-1 V5 NARROW INDEPENDENT REPAIR RE-AUDIT / FIXED-SHA `65963539735761ba2a41876e60d2c86565ffbfe4` / **PASS WITH REPAIRS** / BLOCKING IMPLEMENTATION-CONTRACT DETAILS / NO OWNER FREEZE / NO BENCHMARK/GPU EXECUTION.
