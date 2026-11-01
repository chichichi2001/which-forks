# CR-1a G2 第3版：独立・送信前狭域修理確認（GPT-6、2026-10-12）

**Verdict: PASS WITH REPAIRS（W4-L: PASS under explicit owner single-runtime contract; V2: nonblocking limitation）**  
**Earliest remaining W4-L freeze-blocking issue: NONE within the agreed human-controlled, non-atomic scope.**  
**G2 operational readiness: NOT YET AUTHORIZED** — 別件の段3訂正記録はこの固定コミットで**オーナー確認待ち**。明示確認・保存コミット・新Notebook再生成と前提照合を完了するまでは、有料バッチを1件も送らないこと。

この判定は**固定ソースの静的監査**のみ。G2、本物のAPI、Colab、Google Drive、pytestは実行していない。コード・計画・ベンチマーク内容を変更・公開していない。オーナー凍結／承認を代行していない。

## 読んだ固定資料とGit SHA

- repo `chichichi2001/Pork`、branch `decision-points`、依頼対象固定コミット **`d7f332ff868b62c0236db648add9675fac2e212b`**（前回レビュー保存コミット `a23e46520116c0113cae981b3fadd782e7830f06` の子孫であることを確認）。
- 依頼 `notes/cr1a_g2_review_request_v3.md`、blob **`b9025a0304a2f1e793f5a63dfea6988203bf63e6`**（全文）。
- 修理後 `pork/cr1_g2.py`、blob **`94342730d84d1c5f06974794725171ace44a1aec`**。
- 修理後 `tests/test_cr1_g2.py`、blob **`67d20f7caf843a3011d1381407fd5944f029b568`**。
- 修理後 `scripts/build_cr1a_g2_notebook.py`、blob **`c2dcdade97788f200336c40252efbb223369facc`**。
- 前回 `notes/cr1a_g2_independent_review_v2_20261012_gpt6.md`、blob **`b75eeef856c31bd7f167f39e15f2013590c8dc56`**。以前のQ1-L/Q3-R/Q4-Iについての広範再監査は今回の対象外。
- 送信前の別途必須記録 `notes/cr1a_lock_pre_g2_erratum.md`、blob **`ee74119c7a7ead33b94dddbf5a89239da41d9943`**。このコミットでは文面に「（確認待ち）」が残り、**未承認**。
- **証拠の区別**：コードと人工テストを読んで分岐・順序・反例を独立に検討した。`tests/test_cr1_g2.py`にテストが存在することは確認したが、**テストが自分の環境でPASSしたという証拠ではない**。レビュー対象の人工テストが扱う文字列・問題文・生応答は本レポートには記載しない。

## 対象範囲の判定

| 観点 | 判定 | 意味 |
|---|---|---|
| **V1 / W4-L: 自動takeoverの撤廃** | **PASS（オーナー保証つき）** | leaseに別runtime IDがあれば、時間経過だけでは絶対に奪取しない。旧IDと一致する明示的確認文字列のみ許可しepochを増加 |
| **V1: stale-runtime / same-start / successive create検知** | **PASS（非原子的な見張りとして）** | generationを各saveで増やし、Cell3のループ開始と各create前に共有ファイルのruntime・epoch・generationを照合。人工負試験あり |
| **V1: Drive CAS／完全な排他保証** | **NOT CLAIMED / NOT PROVEN** | check→save→createの競合窓と、独立した二プロセスによる同時初期claimは残る。**単一ランタイムの人間による保証**が安全性の必要条件 |
| **V2: G1由来の目安とAPI token counter** | **USEFUL / NONBLOCKING REPAIR SUGGESTED** | 各問題の`c=L`だけをcountする実装は、全`c`のtoken数の厳密な最大値を保証しない。600の厳密な認証ではなく補助的preflight |
| **Q1-L前回から持ち越し：訂正記録の承認** | **PENDING OWNER ACTION** | 認証済み訂正blobを固定して新Notebookを生成する前提条件はまだ満たされていない。現時点でのG2送信承認ではない |

### V1：W4-L の直接修理 — **PASS under an explicit manual single-runtime contract**

**実装** `pork/cr1_g2.py` `claim_lease`、`save_state`、`fence`、`submit_ready(fence_check=...)`；Notebook生成器Cell2/Cell3。

1. **旧版の危険な自動takeoverを削除**。`LEASE_TTL`がなくなり、別runtimeのleaseがある限り古さに関係なく`G2Stop`。新runtimeに変更できるのは、表示された旧runtime IDに合致する `OWNER_CONFIRMS_OLD_RUNTIME_STOPPED` をオーナーが、**本当に旧runtimeが停止したことを確認した後に**入力した場合のみ。`epoch`を1増やして引継ぎ履歴を残す。単に一致文字列を入力しただけでは旧runtimeの停止を機械的に証明できないので、停止の確認はオーナーの負担として明示される。
2. **見張りの実装と使用箇所はつながっている**。`save_state`が書込み世代`generation`を増やし、`fence`がDriveのJSONを再読込して`runtime`・`epoch`・`generation`を比較。`Cell3`では各ループの最初に`fence`、`submit_ready`では各`create()`前に`fence_check`を実行。既存の`submitting` checkpoint保存・不確定create停止規則も維持。`/content/g2_runtime_id`へのID保存は同じVMでのカーネル再起動時の不用意なtakeoverを避ける意図として整合する。
3. **人工テスト** `test_second_runtime_cannot_start_without_owner`、`test_stale_runtime_never_sends_after_owner_takeover`、`test_simultaneous_start_one_runtime_stops_before_sending`、`test_fence_before_every_create` は、それぞれ無断takeover、古いメモリの再開、初期書込みの競合、複数`create`の間にDrive stateが書き換わる場合を覆う。テストコード上では、変更を検出した側が**次のAPI create前に停止**することをassertしている。

**残る重大な但し書き（意図的に human contract へ移管したもの）**：`fence`はDriveの原子的な排他ロック／CASではない。実際の`create`直前の`fence`と`create`の**間に`submitting`の保存（Drive I/O）が入る**ため、残る窓を一律に「ごく短時間」とは保証できない。ここでBが状態を上書きすると、Aが確認直後の古い認識のままcreateできる可能性は理論上ある。また2runtimeが`lease=None`の状態を同時にreadしたケースでも、双方の最終チェック前に別の書込みが入らなければ同時送信の危険はゼロではない。**これらはオーナーが決して同時にG2を走らせず、旧runtimeの実停止を確認してから引継ぐことを条件としてのみ許容**する。もし**機械だけでの二重送信防止**を求めるなら、今回の修理でもPASSとは言えずCAS/強い排他が必要。

**実運用必須事項**：Colabのセッション管理で旧runtimeが存在しないことを確かめ、旧セッションが送信中か／状態が不明なら**引継ぎを実行せず停止**。別VM/別Notebookで同じDrive G2を同時に操作しない。最初の起動時にも他の実行環境が動いていないことを確認する。共有stateの書換えが発生したら、新しいバッチを送らず、保存済batch IDとConsoleを照合する。これは**単なる注意書きではなくPASSの前提条件**。

### V2：API token count の範囲 — **nonblockingだが「最大値の証明」には不足**

`max_input_tokens`は `Requests.params[(item,cut)]`のうち**各itemの最大cutだけ**（`c=L`）をAPIの`messages.count_tokens`で確認する。Notebook Cell2ではG1実測由来の`IN_BOUND <=580`に加え、この99件のカウント最大が600以下なら続行する。API送信前に無償のトークン計数を置いた改善としては有益。

しかし「テキストとして長いprefixほど**トークン数も必ず単調増加**」という定理は示されていない。BPE等の再tokenizationやメッセージ境界で、`c<L`の方が`c=L`より多く数えられることを一般には排除できない。人工の`count`が短いcutに601、最大cutに590を返す場合、現行の`max_input_tokens`は**短いcutをそもそも照会せず590で合格**する。これは**論理上の反例**であり、今回の実データで600を超えたとの主張ではない。

凍結計画の`WORST_IN=600`は元から予算見張りの仮定であって厳密なtoken証明ではなく、依頼書も入力600を「止めない指摘」に分類している。したがってこの監査では**新しいW4-Lブロッカーとして数を増やさない**。ただし「各requestが必ず600以下とAPIで実証済み」とは表現しない。

**簡単な改善案**：1行`(item,cut)`につき1種類のpromptを数えれば足りるため、**全4,723切れ目**（各48本は同じ入力）を計数し、最大を評価する。件数・API制限は事前に確認し、失敗時は当然G2送信前停止。人工テストでは `c<L`だけが600超という非単調カウンタを与え、必ず検出すること。もしコードを触らない場合は、今回の検査を**保守的な目安**として正確に報告するに留める。

## 送信前に満たすべき、監査外の未完了条件

- `notes/cr1a_lock_pre_g2_erratum.md` は依然 **「オーナーの確認待ち」**。**オーナー自身が明示確認し、日時と言葉を記録してcommitすること**。その承認済みblobから新Notebookを生成し、`EXPECTED_HEAD`・`LOCK_BLOB`・`ERRATUM_BLOB`・`BUDGET_USD=90`の送信前検査を満たす必要がある。
- `notebooks/CR1A_G2.ipynb`を**まだ更新済みとみなさない**。このレビューは変更されたNotebook生成器のソースを見たものであり、オーナー確認後の成果物ではない。
- 初回／再開時とも**オーナーが単一ランタイム運用を守ること**。実Driveの原子的性質やSDKの実送信動作は今回の静的監査で実証されていない。今回は**G2を一切実行していない**。

## 最終結論

**W4-Lの修理を、意図した「人間が単一ランタイムを保証し、コードは不一致を早期検出する」意味論として受理する。V1: PASS（owner-dependent）；V2: PASS WITH NONBLOCKING RECOMMENDATION。総合：PASS WITH REPAIRS（狭域、未承認の送信許可を含まない）。**

**Earliest W4-L freeze-blocking gate: NONE**。それでも**段3訂正記録のオーナー確認＋再生成済Notebookの固定確認が完了するまで、G2本番送信不可**。次に必要なのは研究計画の再設計ではなく、この明示的オーナー手続き。完全な自動排他や全切れ目600保証を主張したい場合には別途修理・検証が必要。

**Audit label:** GPT-6 / CR-1a G2 V3 PRE-MONEY W4-L NARROW INDEPENDENT CONFIRMATION / FIXED SOURCE `d7f332ff868b62c0236db648add9675fac2e212b` / **PASS WITH REPAIRS (OWNER-SINGLE-RUNTIME REQUIRED)** / EARLIEST W4-L BLOCKER NONE / ERRATUM OWNER APPROVAL PENDING / NO G2 / STATIC ONLY / NO OWNER FREEZE.
