# CR-1a G2 第2版：独立・送信前の狭域修理再監査（GPT-6）

**Verdict: NOT READY — do not send any paid G2 batch yet.**  
**Earliest remaining implementation blocker: W4-L（lease の非原子的取得・期限切れ自動奪取によって、2つの実行環境が同じG2を送信できる）。**

前回6c339aeの **Q1-L・Q3-R・Q4-I の直接修理は、それぞれ条件付きPASS／PASS／PASS**。ただし追加した W4 の「二重ランタイム防止」はコードが宣言する保証を満たさず、バッチ重複・状態上書き・二重課金に関係するため局所blocking。G2コード・計画書・ロック・データは**変更していない**。凍結承認、G2送信、実APIアクセスは**していない**。

## 固定ソース・証拠クラス

- Repository: `chichichi2001/Pork`、branch `decision-points`、**source-lock `720c369ef897fcc325f90e282b6ecb26a30e2406`**。
- 指示: `notes/cr1a_g2_review_request_v2.md`、Git blob **`a27cc8cadb5ea53050cee90b497fe9bca2fc5960`**。
- 前回: `notes/cr1a_g2_independent_review_20261012_gpt6.md`、blob **`777b4f767207217da25a7e6fdfec4434ebfc06b7`**、commit `6c339aef8265aa093a18f0aa17b25386d3d4a8a2`。
- G2実装: `pork/cr1_g2.py`、blob **`f5cfc61eee39b4e2e74c977aa46a52fa367fe17a`**。
- 人工試験: `tests/test_cr1_g2.py`、blob **`1b0be2ef3dbb88099f797b2a11ed8b40eb145d32`**。
- ノートブック生成器: `scripts/build_cr1a_g2_notebook.py`、blob **`ff67158da04e2e5d373f5ddaeb22ca70211be900`**。
- **未承認訂正記録**: `notes/cr1a_lock_pre_g2_erratum.md`、blob **`ee74119c7a7ead33b94dddbf5a89239da41d9943`**。文面は現時点で「オーナーの確認待ち」。
- 元の段3ロック: `notes/cr1a_lock_pre_g2.md`、blob **`549fee56602ffa09ee176911bae5b811811368a7`**（未変更）。
- 背景契約として前回レビューが固定した、凍結CR-1 `notes/cr1_claude_resample_gate.md`、CR-1a `notes/cr1a_amendment.md`、`notes/cr1a_g1_result.md`、`pork/cr1_run.py` と関連ノートを参照（それらの全面再監査はしていない）。
- `notebooks/CR1A_G2.ipynb`は依頼書の指定どおり**オーナーが訂正記録を確認したあとに再生成する予定**であり、今回の合否は新しい生成器のソースを対象とする。現在の生成済みnotebookが訂正blobにピン留め済み・実行可能であるとの主張はしない。
- **証拠種別は静的な固定コミットのコード・差分・人工試験のソース読解のみ**。Claude側のpytest合格を独立再現したものではない。実Drive、Colab、バッチAPI、G2を実行していない。ベンチマークの問題本文・実単語・トークン列・非公開レスポンスは閲覧も転記もしていない。下の競合はコードの読み書き順序から構成した**人工故障シナリオ**で、実際に事故が起きたという主張ではない。

## 判定表

| 依頼項目 | Verdict | 送信前の扱い |
| --- | --- | --- |
| **W1／Q1-L：訂正記録、ロックblob、予算90** | **CONDITIONAL PASS** | 旧ロックは温存、別訂正の原因・根拠は妥当。ただし**オーナーの確認と確定コミット・ノートブック再生成は未実施** |
| **W2／Q3-R：create結果不明の安全停止** | **PASS** | recent=0で消さず保留、1件は未検証採用・回収ID照合まで次を送らない、2件以上で停止。manual clearには人間の確認が必須 |
| **W3／Q4-I：回収済PRIVATE結果の監査** | **PASS** | 再開時と終了時の存在・SHA・IDs・counts・failed_ids・token集計を照合、復旧時も整合条件で停止する |
| **W4：単一runtime lease** | **FAIL — BLOCKING** | leaseの所有権は共有ストレージ上で排他的／原子的に確定されず、10分後の期限切れ取得で旧runtimeが並走しうる |
| **W4：入力600の目安確認** | **PASS as conservative diagnostic, NOT formal bound** | G1 prompt+output最大値 `<=580`をAPI前に確認。ただし切断位置の再tokenization差を厳密に20以下と証明したものではない |

## W1：ロックの転記訂正 — CONDITIONAL PASS

訂正記録は、元の凍結ロックに文字どおり残った「本番の見込み 5.84（上限 0）」「上限 0」について、未引用ヒアドキュメント内で `$6` と `$9` がシェル位置引数として展開されて消えたという**文字列に整合する原因説明**を示す。参照元のG1b見込み **$65.84**、凍結済み上限 **$90**、既存のmanifest SHA／件数不変も互いに整合。ロック原本は書き換えていない。

生成器はロックGit blob `549fee56…`を固定し、訂正記録に「（確認待ち）」が残っている場合または「オーナーの確認：済」がなければ**ノートブックを作らない**。作成時に訂正記録のblob SHAを埋め込み、実行時に両Git blobと `RQ.BUDGET_USD == 90.0` を照合してからAPIクライアントを作る。**ただし、現コミットの訂正記録は未承認のまま**で、今すぐ新notebookを生成してG2送信可とすることはできない。

**オーナー確認後の必要な順序:** 確認日と言葉を追記して別コミット化 → **その承認済みコミットのファイル**で生成器を実行 → 生成されたnotebookの `EXPECTED_HEAD`・`ERRATUM_BLOB` と実Git blobが一致することを確認。blob値は生成時のローカルファイルから動的に取るので、**SHA一致は記録本文の独立したオーナー承認そのものを証明するわけではない**。その部分はオーナーの明示記録とcommitで保証する。

## W2：不確かなcreateの扱い — PASS

`resolve_submitting`は記録中のpending-createに対し、最近の候補が**0件ならマークを消さず**、連続0件の最初の確認から30分で `G2Stop`。**自動で再送しない**。1件なら`unverified=True`で採用し、`submit_ready`はそのバッチが回収・正しい`custom_id`全件との照合を終えるまで**別のバッチを出さない**。2件以上では停止。`owner_clear_submitting`は時刻の完全一致を要するが、**Consoleを人間が実際に確認した証明をコードが自動で取得するわけではない**ため、誤操作でクリアしない運用が必要。

`test_uncertain_create_found_later_is_adopted_and_never_resent`は受理済みバッチが一覧の最初の2回に現れない人工ケースで**再送0件**を確認する意図がある。`test_wrongly_adopted_batch_stops_at_collection`は同じ件数の無関係なバッチを一旦採用しても回収ID不一致で停止する。過去のQ3-R「一覧で一回0件→pending削除→同じバッチ再送」は**この修理で解消**。

**非blocking注意:** 1件候補の一致は本体のrequest集合一致ではなく件数と時刻による暫定採用で、正否確認は回収後。もし外部バッチが偶然同じ`custom_id`集合まで持つ場合は完全な識別にはならない。同じアカウントで他の送信ジョブを平行実行しない運用が望ましい。

## W3：PRIVATE結果の再検証 — PASS

`verify_collected`は、回収済みbatchのID集合を期待送信集合と照合し、結果ファイルの実存在・SHA256・読み取った各rowの`custom_id`多重集合・件数（`counts`）・失敗ID・入力/出力token合計を、stateに記録したものと確認する。破損・消失の場合は、同じbatch IDから再ダウンロードし、同じ集計とID集合を再現した時だけ修復して新SHAを記録する。比較不能なら停止。`Cell 2`で再開直後、`Cell 3`で結果summary確定直前に実行。以前の「stateだけあると成功扱いになる」穴は**修理された**。

人工試験に削除・切詰め・本文改変と復旧、再ダウンロード時の集計変化による停止を追加した。`cost_usd`は照合するキーの一つには入っていないが、成功分のtoken合計と固定価格から再計算できるので、**追加の診断比較はnonblocking**。非公開レスポンス本文の全バイト同一性は復旧前後で要求せず、要件どおりIDと集計が一致した復旧を新SHAで記録する。

## W4-L：leaseの所有権は共有状態に対して排他的ではない — **BLOCKING**

**コード位置:** `pork/cr1_g2.py` **236–243行** `claim_lease`、`scripts/build_cr1a_g2_notebook.py` **Cell 2（143–153行）、Cell 3（161–167行）**、`tests/test_cr1_g2.py` **266–272行**。

`claim_lease(st, runtime_id, now, save)`は**そのruntimeが持つローカルなdict `st["lease"]`だけ**を見て所有者を確認し、別プロセスの現在のDrive stateをリロードしたり、比較・交換（CAS）で排他ロックしたりしない。`save()`も同じJSONファイルを単純に`os.replace`で上書きするだけで、**先に取得した者だけが書ける排他性はない**。特に「古いheartbeatが10分を超えたら旧ランタイムは停止済み」と断定してleaseを奪えるが、GPU/API待ち・I/O停止などで**古いruntimeが生存中**というケースがある。

**送信二重化の厳密な人工シナリオ:**

1. Runtime A がG2 stateを読み込み、`lease={runtime:A}`を書いて実行する。API処理やColab/Drive通信で**10分超停止しているが、プロセスは終了していない**。
2. Runtime B が同じstateを再読込し、古いleaseなので正当に見える形で `lease={runtime:B}`を書き、次のbatchを送信する。
3. A が復帰する。**Aのメモリ上のstateはまだ `lease={runtime:A}`**。次の `claim_lease(A,...)`は「他ランタイムの新lease」を読まないので通り、Aが旧stateを上書きし、**Bと同じ未送信チャンクをcreateできる**。
4. 初回に両runtimeが**同じ未作成stateを同時に読む**レースでも、どちらも`lease=None`からclaimでき、後勝ちの上書きを検出しない。

つまり `tests/test_lease` は**同じdictの中でA→Bを順番に呼んだケースしか試しておらず、独立にロードしたstateが並走する実際の競合を覆わない**。この欠陥は前回の送信事故と同じく、**バッチ重複＝重複課金**に直結する。新しく追加した安全装置W4が、むしろ「二重実行が防げる」という誤った安心につながる。

**最小修理の選択肢:**
- **強い自動排他を主張する場合:** 同一Drive JSONの読書きだけに依存せず、**原子的な共有ロック取得／CAS**（その保存先で動作することを人工・実Driveの小スモークで証明）を採用し、各バッチの`create`直前に**現在の共有lockのowner/fencing epoch**を確認する。前所有者は一度leaseを失ったら、古いメモリstateで再送しない。旧runtimeが実際に死んだ証拠のない10分後の自動奪取は許さない。
- **簡易のfail-closed運用:** 自動引継ぎをなくし、旧runtimeの停止をオーナーが確認するまで**新runtimeを開始しない**。一度でも同時実行の疑いがあるなら、課金状況・既存batch IDs・Drive stateを突合するまで新しい送信を停止する。「複数runtimeを自動で防止できる」とは表示しない。
- **人工の必須負試験:** A/Bが同じcheckpointを別々にロード→交互にclaim、Aが10分超停止→Bが取得→A復帰、両方が同じchunkを狙うケースで、**create API呼び出しは高々1回**・二つの実行者が同時にsaveしないことを確認。数百件の有料APIテストは不要。

## W4の入力600に関する小さな留保

`input_bound_tokens`はG1の採択土台の`prompt_tokens + output_tokens`の最大を計算し、Cell2は`<=580`だけ送信を許す。予算見張りに**実測由来の安全マージン**を作る改善。ただし、切れ目でassistant prefillを付けたG2 inputの実token化はG1のpromptと出力の単純和とは必ずしも一致しない。**20トークン差以内を形式保証する根拠はこのソースにない**ので、`WORST_IN=600`を数学的に保証済みとは書かない。過大入力が確実にないことを契約にしたい場合は、実際の各requestをtoken-count検査してから送るか、十分に保守的な上界を別に確立する。

## 結論

**W1（オーナー確認待ち）・W2・W3は要求した直接修理として良好。** ただし**W4-Lの共有lease非排他性は新しい送金安全問題**なので、現段階では **NOT READY / G2 SEND PROHIBITED**。次のre-reviewは**leaseをどう安全に直すか（または人間による単一runtime保証へscopeを下げるか）**と、オーナー確認済み訂正blobのピン留めに絞ればよい。実験計画・凍結済みロック自体の再作成は不要。

**Audit label:** GPT-6 / CR-1a G2 V2 PRE-MONEY NARROW INDEPENDENT REPAIR AUDIT / SOURCE SHA `720c369ef897fcc325f90e282b6ecb26a30e2406` / **NOT READY** / W4 LEASE NON-ATOMIC DUPLICATE BILLING RISK / NO G2 / NO OWNER FREEZE / STATIC-ONLY.
