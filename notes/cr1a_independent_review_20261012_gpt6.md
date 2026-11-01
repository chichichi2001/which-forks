# CR-1a / PARA-1a：独立 adversarial review（2026-10-12、GPT-6）

**Verdict：NOT READY**（修理後の **narrow re-review** を要する）。  
**Earliest failing point：R7 / CR-1a G1 実行経路。** 新旧promptを選択できるヘルパーは追加されたが、現存の `CR1_G1` 実行ノートブック／生成器は **studyを指定せず既定の旧CR-1を使用**する。旧G1の再開ファイルを同じ場所で使えば **100テンプレートを完了済みとしてゼロ呼び出しで通過する**。第1版の改訂手順「同じ候補で**新しい頼み方から全件やり直す**」を満たす実行契約が現時点ではない。修理は局所的だが、G1を再開する前に必須。**凍結代行はしない。**

## 固定ソースと監査した範囲

- **対象repo/branch/commit：** `chichichi2001/Pork` / `decision-points` / **`d9a6db50028bf9ad52ec606621f0c26b6d9cdd1a`**。
- **依頼：** `notes/cr1a_review_request.md` — blob `3ee11163143ae8b17dd2245189223f039843a83a`（全文）。
- **未凍結の改訂：** `notes/cr1a_amendment.md` — blob `9275188aa4ba1c5a60b65ecc401e0d63324443f5`／`notes/para1a_amendment.md` — blob `b8a7ba426d5a3619d861ea15fa37d41898277ad4`（各全文）。
- **元の凍結計画：** `notes/cr1_claude_resample_gate.md` — blob `dccad5ec470017690f06fe98eaf7e21bff4c3ee2`（CR-1凍結commit `7001163dc2072c7929ca93041bc60b195477acee`）；`notes/para1_paraphasia_plan.md` — blob `ab817e900200739f7356bb460dfb5494a6b98932`（PARA-1凍結commit `69dd041b6d07699e7ae42ce055c494c54d3270fb`）。関連する定義、G1/G1b、段2/3、部A、凍結記録を照合。いずれの凍結commitも対象commitの**祖先**（GitHub compareのahead、behind=0で確認）。
- **過程と数値：** `notes/cr1_prompt_record.md` — blob `2c6c1ddd17a2c8316188e4a6466d5263a9e59982`；`notes/cr1_g1_result.md` — `d5177cf2816c2ff3bd433d4023c7e70e190a1c24`；`reports/cr1_g1_result.json` — `801bca4e01c4d2f06ab81662ee90453ea43534a4`；`reports/cr1_g1_lengths.json` — `4db28a2b915b22c6f57d20d42af26704a2d7603a`；`notes/cr1_lock_pre_g0.md` — `a4e5a9925932af08ea026752acd0178866a1ca77`。
- **コード：** `pork/cr1_requests.py` — blob `939c91607bc4a954bf86092659d08bbf4d565f94`；`tests/test_cr1_requests.py` — `7a47519152c38002e37dc7f172561f27788f089c`；`scripts/build_cr1_g1_notebook.py` — `914ade8f06625052544b3fe3d38332ff806b58c9`；`notebooks/CR1_G1.ipynb` — `fd8ad127b2e123420024c8e27ef9b3d80921285b`。
- **段2と照合：** `pork/cr1_analysis.py`、`pork/cr1_reference.py`、`pork/cr1_audit.py`、`pork/cr1_items.py` のGit blobsが段2の記録値 **4件すべて完全一致**。
- **Evidence class：** リポジトリのテキスト・diff・ノートブックの呼び出しを**読んで静的監査**。二つのpromptテンプレート文字列のSHA256は無害な文字列を使って**ローカルで独立計算**し、記録どおり `CR-1=c2e04c90…`、`CR-1a=0140527f…` を確認した。**pytest、Colab、Claude API、本番データ、G2は実行していない。** 私が確認したのはGitHubにある記録とコードであって、非公開Drive内の応答や実送信履歴の独立検証ではない。ベンチマーク問題、実応答、単語・トークン文字列は記載しない。

## 判定の要約

| 問い | 判定 | 凍結上の重要度 |
| --- | --- | --- |
| **R1 開示と順番** | **おおむね解消** | nonblocking補足 |
| **R2 60語だけでN≥70・予算を満たすか** | **実測前には判定不能** | nonblocking、結果の過大主張禁止 |
| **R3 改訂一回限り** | **PASS** | 一度きりの停止契約を維持 |
| **R4 段2の継承** | **PASS** | 段2で固定した4モジュールのblob不変 |
| **R5 PARA-1aのデータ・停止・時系列** | **概ねPASS** | nonblockingのラベル表記・履歴補足 |
| **R6 DPとの比較可能性** | **PASS WITH SCOPE** | 条件の異なる記述的対比に限定 |
| **R7 study切替とテスト** | **FAIL：blocking** | CR-1aの新promptでG1を走らせる経路／新旧checkpoint隔離が未接続 |

### R7 — **BLOCKING**：旧G1が新promptを使わず、旧stateを継承する

**場所：** `pork/cr1_requests.py` の `baseline_params(question, study="CR-1")` および `resample_params(..., study="CR-1")`；`scripts/build_cr1_g1_notebook.py` **109–120、156–160、190行**；既存 `notebooks/CR1_G1.ipynb` の対応セル。

1. **新promptの未選択。** 新しいヘルパー群が新旧 `PROMPTS` を受け取る実装なのは正しい。しかし現在のG1ノートブックは `RQ.baseline_params(question)` と呼ぶので、**既定の`CR-1`のまま**。集計の `RQ.prompt_sha256()` も旧CR-1のSHAとなる。コードを最新版に更新するだけではCR-1a G1にはならない。
2. **旧stateの再使用。** 既存G1ノートブックは保存先を `DECISION_POINTS/cr1/G1`、state名を `CR1_G1_state.json` 等に固定し、`todo = [c ... if template not in S["templates"]]` で完了済みをスキップする。元G1の100テンプレートが記録されている場合、**新promptを一件も送らず、旧57件の選択結果をCR-1aと誤認し得る**。state読込でstudyやprompt SHAを照合する検査は現存しない。
3. **G2経路にも同種の危険。** `resample_params` の既定が旧CR-1なので、将来G2のリクエスト生成で `study="CR-1a"` を渡さなければ、土台と引き直しの頼み方がずれる。現時点のリポジトリでCR-1a専用G1/G2ジョブや段3manifestは確認できなかった。**まだ未実装であって誤送信したとは主張しない。**

**最小修理（凍結前の実行契約を別記すればよい）：**
- CR-1a専用ノートブック／生成器で `STUDY="CR-1a"` を一度だけ明示し、G1の `baseline_params(...,study=STUDY)`、`prompt_sha256(STUDY)`、将来のG2の `resample_params(...,study=STUDY)` へ**必ず伝える**。API送信前に `STUDY` と凍結した新prompt SHA `0140527f…` をfail-closedで照合する。
- 保存先・state・private responses・数値結果を**旧CR-1と完全に分離**（例：`DECISION_POINTS/cr1a/G1`）。途中再開では、`study`・prompt SHA・候補SHA・code SHA・model・SDKを一致照合してから既存stateを採用。不一致なら既存stateを読み込まず停止する。旧CR-1の57問/100テンプレート完了フラグを流用しない。
- 同じ候補順序で全100テンプレートを**新しいpromptで新規計測**した事実、試行数・選んだ候補の番号・(N)・費用・hashを新結果に記録。G2も新promptで構築した全リクエストmanifestと段3lockを照合する。
- 既存の4件のユニットテストは**関数にstudyを明示した場合と旧既定値**の確認であり、実際のG1/G2ノートブックが正しいstudyを選ぶことやstate隔離はテストしていない。**end-to-endの小さい人工データ**で「CR-1aのG1呼出し、新旧stateを混ぜたら停止、G2で新promptとprefillを選択」を確かめること。

この問題は**本研究の仮説ではなく、実行経路の具体的な欠落**。独立性を守るため、G1を実行するより先に修理と監査が必要。

### R1 — 開示・時系列：**概ねPASS／nonblocking**

**場所：** `cr1a_amendment.md`「何を見たあとに決めたか」、凍結CR-1末尾「凍結と、実行前の2つの固定」。

修正は**元G1の長さと採択数、トークン使用量、stop reason、**および土台の正解率57/57を見た**後に選んだことが文書化され、元CR-1のG2はG1で停止したとの記録。主0〜主3の観測が無いという**保存済み記録上の主張**と整合。元のCR-1を改訂せず、新しい未凍結amendmentにし、オーナーが「案1」を選択した経緯は、元の凍結ルールの精神に沿う。

**限界と最小追記：** ここでの改訂は完全なpilot-independent preregistrationではない。**eligibility（長さ）に適応した再設計**であり、57/57の正解率も観測済み。最終結果では「CR-1aは元G1のaggregateなeligibility / baseline accuracyを見て設計」と明記する。非公開応答内容を見ていないとの申告はGitHub上の報告であって独立に立証していない。CR-1a・PARA-1aの**実際のowner freeze commit**がCR-1a G1再実行・段3・最初のG2送信より前であることを、後のtimestamp/IDおよびcommit ancestryで示す。元のCR-1/PARA-1の停止ログは上書きしない。

### R2 — 60語で長さ・費用・Nを満たせるか：**未立証／nonblocking（one-shot停止つき）**

**場所：** `cr1a_amendment.md`「ひとことで」「60語の理由」、`reports/cr1_g1_lengths.json`。

旧G1は **193候補を呼出し、長さ条件失敗134（すべて長すぎ）、答え読取失敗2、採択57**。長さ失敗134件の分布は81–100が58、101–120が44、121–150が25、151–200が7。長さ範囲を30–100に広げると**N=81だが全件見積$105.77、予算内にtrimするとN=69**；30–120ではN=94、全件見積$142.78、trim後N=56。以上は**旧prompt**での集計であり60語版の予測値ではない。

「60語」という**モデルへの指示**は応答長の保証ではない。最大60の「語」と、CR-1の`\s*\S+`による30–80の**単位**は必ずしも一致せず、式・数式・記号・行区切りで差が生じる。短すぎ（30未満）、無視されて80超、読取不能、正解率低下、新たな費用の変化はいずれもあり得る。**新promptのG1を走らせる前にN≥70・G1b後N≥70・総費用≤$90を保証することは、この数値資料からは不可能**。

**最小修理：** 60語の選択を「旧G1の数字から採用した、成功保証のない**一度限りの設計変更**」と明示。新G1とG1bの旧閾値を**結果にかかわらず適用し、満たさなければ停止**。事後の60→70→50語等の追加チューニングをしない。文章「外れた候補134件はすべて長すぎ」は**長さで外れた134件**という意味に限定（別にunreadable2件あり）。旧G1の「60語版ならどうなるか」の推定統計は作らない。

### R3 — 一度きりルール：**PASS／nonblocking備考**

**場所：** `cr1a_amendment.md`「止める決まり」。

G1でN<70なら`STOPPED_BEFORE_MAIN_RUN`、再度promptを変更しないという方針は**合うまで繰返す選択バイアス**の軽減として明確。N≥70でもG1bの$90判定や期限で止まるときは**元計画どおり停止し、そこで改めてpromptを変更しない**ことを1文補足するとより堅牢。

### R4 — 段2の固定の継承：**PASS**

**場所：** `notes/cr1_lock_pre_g0.md` とコード。

段2で固定した `pork/cr1_analysis.py`／`cr1_reference.py`／`cr1_audit.py`／`cr1_items.py` は**現commitのblobが4件とも段2記録と同じ**。候補SHAは`b6f6375aed95831de0098a5138bb87f4101fe9c6670598f23e5e8055eaac8511`でG1レポートにも一致。readoutの`cr1-readout-v1`を変更した痕跡は今回差分にはない。**prompt選択だけを別途新しい段3に明記し、旧prompt/SHAを使い回さなければ**段2の解析・候補固定を継承する整理は妥当。元G0は**APIの実行可能性の確認**として有効であり、**新しい60語promptのG1成功を保証する証拠ではない**。

### R5 — PARA-1a：**概ねPASS／nonblocking修理**

**場所：** `para1a_amendment.md` 全文、凍結PARA-1の背景/部A/凍結記録。

元CR-1はG1で終了 → 元PARA-1部Aは不変の`NOT_RUN_CR1_STOPPED`を記録。新CR-1aが停止したなら**PARA-1a側だけ**`NOT_RUN_CR1A_STOPPED`を追加し理由を示す。新CR-1aが`INSUFFICIENT_FORK_SIGNAL`でも部A分析を進めるという例外は、元PARA-1のAがCR-1の主ラベルに依存しないことと一致。元のCR-1定義10/11/14とPARA-1のA1–A3/G0cを変えないので、**分析対象はCR-1aから導いた問題・切れ目・応答**に置き換えるだけというscopeは守れる。

**最小の明瞭化：** `CR-1a:`だけをPARA-1a Aラベルに付けるとCR-1a本体ラベルとの区別が曖昧。例えば`PARA-1a:<A-label> [source=CR-1a]`等、CR本体と追加分析を**別の名前空間**で表示する。元PARA-1 Aは無結果のまま残す。両改訂を**CR-1aのG2より前にowner freeze**し、凍結SHAが段3lockの祖先であることと最初の送信時刻/IDを記録。できればCR-1aの新G1再実行前にも凍結し、eligibilityの追加観測後の調整でないことを示す。

### R6 — 比較可能性：**PASS WITH SCOPE**

**場所：** `cr1a_amendment.md`「予想される影響」。

60語という条件変更で土台の書き方、選抜集合、推論長・答え読み取り率・コストが変化し得る。オープンモデルDPとpromptが異なるだけでなく、**旧CR-1とも異なる研究条件**となる。論文等の記述対比では`prompt`／長さ・モデル／sample-selectionの違いを明記し、**同一条件でのモデル比較・語数上限の因果効果とは言わない**方針なら妥当。判定式を変更しないことはPASS。

### R7 — 単体テストと既定値について補足

`prompt_sha256()`・`baseline_params()`・`resample_params()`の既定が`CR-1`のままなのは**旧CR-1の再現のため正しい**。新旧テンプレートは文字列置換以外一致し、**両sha256を独立計算で一致確認**した。追加テストはヘルパーの新旧選択・prefill末尾空白の拒否を確認する作りだが、**テストが実際に実行済みという証拠はこのレビューにはない**。最大の不足は、ヘルパーのテストだけでは本番ノートブックが新studyを選択した事実を証明できないこと。実行ジョブへの配線とresume保護を**修理・テスト**するまでCR-1a G1を始めない。

## 修理の最短順序・最終判断

1. **blocking 1件（R7）:** CR-1a専用G1/G2構築経路と、API送信前のstudy/prompt SHA検査を定義。G1の**旧保存状態からの独立**とresume時のhash検査を追加。テストは人工データのみ。凍結後の実験経路を新しい成果物として確認する。
2. **nonblocking:** 60語の成功不確実性の表現、CR-1aとPARA-1aのlabel namespacing、全owner-freeze/G1/G2の時系列、G1bで止まった場合のone-shot明示を加える。
3. 旧CR-1計画・旧PARA-1計画・元データは上書きしない。二つの未凍結amendmentをどちらも**オーナー自身が別途凍結承認**するまでは凍結済みと扱わない。今回の評価は**計画とコードの静的レビュー**であり、G1改訂版のNや主効果の成否を証明しない。

**Audit label:** GPT-6 / CR-1a PARA-1a PRE-FREEZE INDEPENDENT ADVERSARIAL REVIEW / SOURCE-LOCKED `d9a6db50028bf9ad52ec606621f0c26b6d9cdd1a` / **NOT READY** / EARLIEST R7-G1 STUDY/RESUME CONTRACT / NO OWNER FREEZE / NO API RUN.
