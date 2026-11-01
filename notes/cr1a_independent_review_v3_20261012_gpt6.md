# CR-1a 第3版：独立・狭域修理確認レビュー（GPT-6）

**Verdict: PASS（今回の W1〜W3 の計画・ソースレベルの修理）**  
**Earliest freeze-blocking point: NONE within the requested narrow scope.** 前回 V1(c)/V2 の**保存済み採択とPRIVATE応答の食い違い**は、単一チェックポイント＋内容検証で実質的に閉じた。候補単位の復旧規則も、「保存済みは再送しない／不明な結果は再送し記録／exactly-onceとは呼ばない」で整合する。**Google Driveマウントでの実動作やClaude APIでの実送信は、未検証。** 凍結の代行ではない。

## 固定したソースと証拠区分

- **固定リポジトリ・ブランチ・コミット:** `chichichi2001/Pork` / `decision-points` / **`a301e1cb5367cf4e3bcbb505c17a10fddddfee10`**。
- **依頼書:** `notes/cr1a_review_request_v3.md`、blob **`1c6a7b06275490d0714ab354591b261c6786a9f8`**。
- **未凍結の改訂:** `notes/cr1a_amendment.md` 第3版、blob **`2f148373051a0c0b20c69525b8714701d7f32b05`**。 `notes/para1a_amendment.md` は変更なし、blob **`7fe2c7c5891d98983596cc5ea6fda232ff3d7112`**。
- **主実装:** `pork/cr1_run.py`、blob **`a2d0ac5fe6b87dac3fb01e214500ce93d5a82a6a`**。
- **人工テスト:** `tests/test_cr1_run.py`、blob **`f7f7360dd96547f6af215d1780e64f241969298e`**。
- **Colab生成器:** `scripts/build_cr1a_g1_notebook.py`、blob **`8e89333636147a8975ecb0d8b2509577300ee0b5`**（とくにCell 2）。前版から変更された5ファイルのGit差分を確認。
- **前回の独立レビュー:** `notes/cr1a_independent_review_v2_20261012_gpt6.md`、blob **`f9b852dfab44d78612f405fc18b815acf2919bf6`、保存コミット `5eb63561aa54b2e91cc54aca1a2044ba1d9a7b9c`**。
- **証拠の種類:** 上記固定ソース、diff、テストを**静的に読み、各分岐の人工反例が止まるか論理検証**した。Claudeによる「CR-1系 pytest 38件PASS」は**依頼書の申告**であり、私が独立にpytestを実行した結果ではない。Colab、実Google Driveマウント、API、本番ベンチマーク、G2は**実行していない**。問題文・生応答・トークンや単語の中身は記録・引用していない。

## W1（旧V1(c)） — **PASS**

**場所:** `pork/cr1_run.py` の `new_checkpoint`、`validate`、`open_checkpoint`、`save_files`、`load_files`、および生成器Cell 2。

- 旧版の独立した`state`と`PRIVATE`を廃止し、**PRIVATE checkpointを再開の唯一の一次資料**にした。`CR1A_G1_state.json`は文字列のないコピーで、再開には読まない。**checkpointなし＋numbersコピーあり→停止**。旧CR-1の保存先とstudyの照合も維持。
- `validate`はテンプレートID、候補index・IDとinstanceの順、初回成功後に次候補を呼ばないこと、`done`と`partial`の排他、`pending`位置、採択済みテンプレート集合と`items`集合の**厳密一致**、採択IDとPRIVATEテキストSHAを照合する。**同じヘッダーなのに採択済みPRIVATEテキストが欠ける**前回の反例は、`set(items) != used`で送信前に`ContractError`となる。採択されなかったテンプレートへの不要なPRIVATEテキスト、ID/文字列SHAの不一致、未知テンプレート等も拒否。
- `save_files`はまず同じディレクトリ内の一時ファイルを`os.replace`してcheckpointを確定し、そのあとnumbersコピーを更新。**numbersコピーの更新だけが失敗しても、次の再開はcheckpointだけを読む**ので旧版の2ファイル世代不一致を主解析へ持ち込まない。書込み途中でcheckpointの置換前に失敗した場合、以前のcheckpointを残す方針もコードと人工テストに整合。

**判定範囲の限界（nonblocking）:** `os.replace`がColabのGoogle Driveマウントでも期待どおりの原子的・永続的動作をすることは、**コード読解とローカルtmp_pathのpytestだけでは実証できない**。G1のAPI送信前に、同一マウント内の小さな無害データでwrite→replace→reloadと強制失敗のスモークを実施し、失敗ならG1へ進まないのが安全。

## W2（旧V2補足） — **PASS with disclosed at-least-once retry behavior**

**場所:** `pork/cr1_run.py` `run_g1`、`open_checkpoint`、`summarize_g1`。

- 候補`j`の送信前に`pending[tid]=j`をcheckpointへ**先に保存**、応答が返るとその候補の記録を`partial`または`done`へ保存。`partial`長から再開するので**checkpointに結果が保存済みの候補を再呼出ししない**。旧版の「テンプレート単位でしか保存しない」漏れが解消。
- 送信時に断絶し結果が保存されなければpendingが残る。`open_checkpoint`で全pendingを`unknown_outcome`へ記録してから再開し、当該候補をもう一度送る。`summarize_g1`で`unknown_outcome_resent`件数を報告。同じ実行内の`retry_on`例外を例外型別`retries`に数え、再送に伴う二重API受理の可能性を文書にも開示。`exactly-once`を主張しない点は妥当。
- 例外時の`stop`フラグにより、**例外を検知しフラグが立ったあと**の別workerの次リクエスト開始は抑制。すでに飛んでいるリクエストは取り消せないことに留意する。

**nonblocking注意:** workers=8で同時に実行しているため、クラッシュ時にpendingが**必ず1件だけとは限らない**。コードは複数pendingを記録・再送できる。文書中の「1件」は「**結果不明となった各リクエスト**」と読むべきで、実験記録には全件数を出す。またpendingを送信**直前**に保存するため、実際には未送信だったリクエストもunknownとして過大計数され得る（保守的な不確実性の分類として許容）。

## W3（人工テストの射程） — **主要反例を網羅、PASS（テストコードの確認）**

**場所:** `tests/test_cr1_run.py`。

確認した人工ケース：新studyのprompt・旧study既定値、numbersのみ、旧形式無ヘッダー、別study/commit、採択済PRIVATE欠落、採択indexの改変、PRIVATEのID/文字列SHA不一致、候補のID不一致、未知テンプレート、採択後の余分な候補、done/partial重複、破損JSON、結果がないテンプレートへの余分なPRIVATE、候補途中の切断・再開・unknown記録、置換前例外で前checkpointが残ること、古いnumbersコピーの無視、retry例外回数、G2用prompt/prefill/manifestの生成。実際に悪いcheckpointをロードするテストは、API試行配列が**空のまま**であることを明示的にassertしている。

**追加すると良い小試験（nonblocking、実API不要）:**
1. `test_error_in_one_worker_stops_the_others`は`workers=1`のため、**複数worker並走時の停止フラグの挙動までは検証していない**。`workers=2`以上でイベント同期した偽APIと競合例を試す。既に送信中の呼出しは停止不能という限界を維持する。
2. `test_crash_while_writing_keeps_previous_checkpoint`は`os.replace`直前の人工失敗のみを模擬し、実Driveマウントの原子的保証・電源断の耐久性は示さない。API前の小さなDriveスモークで補う。
3. `unknown_outcome`・`retries`件数は診断ログなので、複数pendingの再開ケースも追加すると監査しやすい。

## 最終判断

**今回求められた W1・W2・W3 はPASS。新たな凍結阻害点は確認しない。** 元CR-1とPARA-1の凍結計画の全面再監査、G1/G1b/G2実験の成功判定は今回の対象外。二つのamendmentは引き続き**未凍結**であり、**オーナー自身の明示承認**が必要。特にG1の最初のAPI呼出しより前に凍結するという時間条件を守ること。計画書・コード・テスト・非公開データを一切変更せず、レビューのみを新規作成した。

**Audit label:** GPT-6 / CR-1a V3 NARROW INDEPENDENT REPAIR CONFIRMATION / SOURCE-LOCKED `a301e1cb5367cf4e3bcbb505c17a10fddddfee10` / **PASS (STATIC ONLY)** / NO OWNER FREEZE / NO API/GPU/BENCHMARK RUN.
