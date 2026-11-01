# CR-1a G2 本番送信コード：独立・送信前 adversarial review（GPT-6）

**Verdict：NOT READY — DO NOT SEND G2 BATCHES.**  
**Earliest blocking point: Q1-L（段3ロックの費用数値が、凍結計画およびG1b結果と不一致）。**  
**Independent high-severity sending blocker: Q3-R（`create()`の結果不明時、「recent一覧で0件」だけで送信中マークを消すため、二重送信・二重課金の可能性を排除できない）。**  
**Further integrity blocker: Q4-I（収集済みと記録した結果ファイルの存在・SHA256を再開時に再検証しない）。**

計画書・コードの編集、G2送信、実APIを使った試験、オーナー凍結は**一切実施していない**。修理後はこの3点に絞ったnarrow再監査でよい。

## 固定証拠と監査範囲

- **Repository / branch / fixed review commit：** `chichichi2001/Pork` / `decision-points` / **`83f9bf001b0e1ba92fbf5411e1fd596345fe015f`**。
- 依頼書 `notes/cr1a_g2_review_request.md`、Git blob **`5f4778ad9b80279f071158ac2116c34c10f6577b`**。
- 主実装 `pork/cr1_g2.py`、blob **`4ad0362c8142285853f7414b440c12092fd86117`**。
- G2ノートブック生成器 `scripts/build_cr1a_g2_notebook.py`、blob **`dc8738fc8c15e7197abd43afc7fbae3e68f60dd6`**。
- 生成済み `notebooks/CR1A_G2.ipynb`、blob **`984205833b6aa332b4892faf676b2bab3b6923b4`**。ノートブックは **`dcdb1fde42c4cd538b32423411049544cb772871` をcheckout**し、元の凍結コミットと段3ロックコミットの祖先関係を送信前に検査する。
- 人工試験 `tests/test_cr1_g2.py`、blob **`6788c693aa614b6c858743406d1ec6e311e80162`**。
- 元の凍結CR-1 `notes/cr1_claude_resample_gate.md`、blob **`dccad5ec470017690f06fe98eaf7e21bff4c3ee2`**（とくに定義6・7、G2、決定4）。
- 凍結CR-1a `notes/cr1a_amendment.md`、blob **`e036e39527b126ad8ab804f6ef28c346332c74bc`**；段3ロック `notes/cr1a_lock_pre_g2.md`、blob **`549fee56602ffa09ee176911bae5b811811368a7`**；G1bの結果 `notes/cr1a_g1_result.md`、blob **`c51c2c833752d03f6338a84405a3fb966510d36e`**。
- 参照 `pork/cr1_run.py`、blob **`8c499a8ba60a7331fb7bc6b793efb0339d662436`**；`pork/cr1_requests.py`、blob **`939c91607bc4a954bf86092659d08bbf4d565f94`**。
- 監査方法は **SOURCE-LOCKED STATIC CODE/CONTRACT INSPECTION**。Claude側のfake API試験を読んだが、独立pytestは**未実行**。実トークン・問題文・API結果・非公開Driveファイル内容は取得も表示もしていない。こちらから送金・本番API呼出しはしていない。公開API仕様に関してはAnthropic公式 [List Message Batches](https://platform.claude.com/docs/en/api/http/messages/batches/list) を参照。公式文書はバッチ一覧・ページング・返却カウントを説明しているが、**作成直後の0件を「絶対に作成されていない」と断定できる強い整合性保証は確認できない**。遅延発生自体を観測したわけではない。

## 判定表（Q1〜Q6）

| 対象 | 判定 | 要点 |
| --- | --- | --- |
| **Q1 preflight / manifest** | **大筋PASS / ロック整合BLOCKING** | 226,704リクエストのmanifest再構築とDriveのcanonical SHA照合、各位置のuser/prefill SHA照合は実装。しかし**段3ロック費用欄**が他の凍結記録と衝突 |
| **Q2 budget** | **計画の計算式に対してPASS** | paid+inflight worst+new batch worst+remaining×estimate×1.2。0 inflightで超過ならstop、有ればwait。初期210/60、回収後成功数による平均。ただし「入力600」のworstは**計画上の仮定**であり全requestの厳密上界と検証されていない |
| **Q3 duplicates/reconciliation** | **BLOCKING** | create用clientがSDK再試行0、成功ID非再送、最大2回再試行、3同時制限はよい。**create結果不明の0件判定がfail-open**、1件一致も件数・時刻だけ |
| **Q4 collection** | **回収処理PASS / resume integrity BLOCKING** | 返却custom_idを多重集合として完全照合、PRIVATE JSONLに可逆保存しその場でSHA再読込。だが回収済stateを再開するとPRIVATEファイルを照合しない |
| **Q5 expiry** | **PASS** | JST 2026-11-07 00:00以降に新規バッチを発行しない |
| **Q6 fake API tests** | **PARTIAL** | 通常送信、3同時、成功除外、再試行2回、予算待機/停止、期限、0/1/2候補の再接続、戻りID、stateヘッダー、再開を検査。**一覧の一時的な欠落・単一の別バッチ衝突・PRIVATEファイル消失／改変**は未検証 |

### Q1-L — 費用のロックに実際の矛盾（**earliest blocking**）

固定された段3の `notes/cr1a_lock_pre_g2.md` には、G1bの欄に文字どおり **「本番の見込み 5.84（上限 0）」**、末尾にも **「上限 0」** とある。一方、凍結CR-1の［決定4］とCR-1a amendmentは **上限$90**、`notes/cr1a_g1_result.md` は **本番見込み$65.84**、実行コードの `RQ.BUDGET_USD` は **90.0**。これは小さな数字の書き間違いの可能性が高いが、**凍結ロックの数値を査読側が勝手に$90と補完して「完全一致」と宣言することはできない**。

G2 Notebook Cell 1は、ロック文面に**manifest SHAが含まれるか**を検査するだけで、費用欄と上位の予算契約の整合性は検査しない。したがって、現在の不一致のままでも**有料のバッチを発行可能**。

**最小修理：** 元の凍結ファイルを無断変更するのではなく、オーナーが**別の訂正/確認記録**に「見込み$65.84、上限$90が正式な値」と明示し、段3ロックと訂正記録のSHA/コミットを送信前チェックに接続する。契約の変更なのか転記修正なのかも明記。修理後に監査。**$0が意図された値なら、このG2は送信不可**。

### Q3-R — API一覧で0件＝未作成、とは証明できない（**sending blocker**）

**箇所：** `pork/cr1_g2.py` の `submit_ready`・`resolve_submitting`・`AnthropicBatchAPI.recent`、Notebook Cell 2 / Cell 3。

**反例的シナリオ（実送信ではなく条件付き故障シナリオ）：**

1. `submit_ready` が `st["submitting"]` をcheckpointに保存してから、`create()`を呼ぶ。
2. サーバーはバッチを**受理**するが、ネットワークが切れAPI応答のbatch_idがアプリに届かない。
3. 再開直後の `recent()` が何らかの理由で**一時的にそのバッチを一覧に含めない**（可視化遅延、ページング／取得範囲、取得中の外部変更等）。現在の`resolve_submitting`はこの**1回の0件**で`submitting`を解除し、次のループで**同じcustom_id集合を再送できる**。
4. 元のバッチが後から見えると、**同じリクエストが二つの独立したバッチで課金されうる**。`create_client.max_retries=0`でも、この**アプリ側再送**は防げない。

また、候補が**1件**の場合も、照合条件は「既知ID以外・記録時刻の120秒前以降・同じ件数」だけ。**同じ件数の別実験バッチ**がこの時間帯にある場合、誤採用しうる。`custom_id`の集合またはrequest-set digestまでAPIから即座に検証したわけではない。

**最小修理（安全側）：**
- 0件なら**不確定を保持し、新規送信を止める**。ポーリングによる再確認や、必要ならオーナーによる既存バッチの手動照合を経てから状態を確定する。単一の0件で**自動clear→再submitしない**。「一定時間待てば絶対に未作成」という保証がない場合は、期限切れまで不確定として停止する選択を許す。
- 1件なら可能な範囲で**バッチ内のcustom_id集合または対応する結果のID集合と想定値**を検証し、一致が検証できない間は誤採用の可能性を明示し保留（特に他の実験も同一APIキー/workspaceで動く場合）。2件以上は従来どおりfail-closed。
- 新しい人工試験に、**「createは実際に受理したが例外→recentが最初は0件、後に1件」を加え、再送数がゼロ**であることを確認。同時期の無関係な同件数バッチ1件のケースも追加。SDKのauto retry 0は維持。

これは「実APIで実際に一覧遅延を観測した」という主張ではない。**高額バッチ送信の安全性証明に必要な前提がAPI公式資料からは確認できない**という保守的な監査結果である。

### Q4-I — 回収済みPRIVATE結果のresume時の存在・SHA未確認（**integrity blocker**）

**箇所：** `collect`の`b.update(status="collected", results_file, results_sha256, ...)`、`open_state`、Notebook Cell 2。

正常回収時は**送信ID集合と返却ID集合の厳密一致→PRIVATE JSONLの原子的置換→再読込SHA照合→stateに回収済みを保存**という順序で、これは正しい。

しかし、次回再開時の `G.open_state` は`schema`と`header`の一致だけ確認し、`st["batches"]`の`status=="collected"`には**PRIVATEファイルが存在するか、記録SHAと一致するか**を確認しない。さらに`collect`は回収済みbatchを即スキップし、`tallies`は保存済み`failed_ids`以外を成功とみなす。従って**stateだけ残り、JSONLが失われた／一部破損した**場合でも「成功・完了」と誤報し得る。G3で実際の応答データが回収不能になる。

**最小修理：** G2再開時、未送信の次バッチを出す前にすべての`collected`レコードの結果ファイルを検査し、**存在・SHA256・ID集合・件数・成功/失敗集計**を照合する。欠損・不一致なら`G2Stop`、バッチIDで安全に再ダウンロード可能な場合だけ元ID集合とSHAを検証のうえ復旧する。**保存済みstateを信用して未確認の結果を成功扱いしない**。人工の欠損・破損PRIVATEファイル試験を追加。

## すでに正しく実装された重要箇所

- **Q1**: G1 checkpointを固定ヘッダー／候補SHA／G1b=GOで検証、全manifestを再計算し段3のSHAとDriveコピーのSHAの両方へ照合。`Requests`が各行のuser/prefill SHAを実際のリクエストパラメータと突き合わせる。バッチはmanifestから定まるID順・同じmodel/上限400・CR-1aのstudy・c=0ではプリフィルなし、c>0では指定したassistantプリフィル。件数 **99問・4,723位置・226,704リクエスト**。
- **Q2**: 凍結計画の費用式はコードへほぼ忠実に翻訳されている。「次に送るバッチ」をworstへ含めたことは支出に保守的。1バッチ10,000上限、3同時まで、初期210/60→観測平均、流れていれば待ち・なければ停止。**ただし計画が仮定する入力600はすべての実際のprompt入力の数学的上界と証明されたわけではない**ため、$90を絶対保証するとは書かない。
- **Q3**: 確定した成功IDは再送対象から除外、失敗IDは初回＋最大2回の全3試行、`custom_id`は不変。create SDKの自動retryを0にし、読み取り側だけ既定retryを使う。
- **Q4**: API結果は順不同を許し、返却IDの重複・欠落も厳密比較で拒否。PRIVATE本文は状態/通知には出さない。結果ファイルのSHAを保存。
- **Q5**: `LAST_START = 2026-11-07 00:00 JST`を境に**新規**バッチ送信禁止、進行中の回収は続けられる。
- **Q6**: FakeAPI試験は通常送信、バッチ並行数、正常終了、欠落ID、2再送、予算に応じた待機と停止、期限、0/1/2件のcreate結果不明、別ヘッダーのstate、途中再開を網羅。ただし**「0件は永久に0件」前提の偽APIでは、Q3-Rの危険は見えない**。Claude側のpytest完了はこのレビューで独立確認していない。

## 修理後の最短ルート

1. **Q1-L**：上限0/見込み5.84の段3ロック転記問題を、オーナーの明示的な訂正記録で解消。凍結ファイルそのものを勝手に書き換えない。
2. **Q3-R**：不確定createで最近の一覧が0件でも自動クリアせず、**APIへの同一リクエスト再送を保留**。1件誤認を防ぐ照合と人工テストを追加。
3. **Q4-I**：回収済みPRIVATE成果物を再開前に実ファイルSHA・ID・件数で照合し、欠損・破損で停止する。人工試験追加。
4. **Nonblocking運用上の注意**：同じDriveのG2 stateに複数のColabランタイムが**並行書込／並行送信**する場合の排他・leaseも明示すると安全。予算のworst入力600を実際の各送信単位の上界として扱いたいなら、送信前のtoken長の確認／上界の根拠が必要。新しいGPU実験は不要。

**最終判定：NOT READY。** 現時点で22万件超の有料G2送信を承認してはならない。上記修理を確認するだけのnarrow reviewで十分で、実験全体の分析計画を再検討する必要はない。

**Audit label:** GPT-6 / CR-1a G2 PRE-MONEY INDEPENDENT ADVERSARIAL AUDIT / SOURCE-LOCKED `83f9bf001b0e1ba92fbf5411e1fd596345fe015f` / **NOT READY** / Q1-L LOCK-CONTRACT DISCREPANCY + Q3-R UNCERTAIN-CREATE REPLAY + Q4-I RESULT-INTEGRITY / NO G2 EXECUTION / NO OWNER FREEZE.
