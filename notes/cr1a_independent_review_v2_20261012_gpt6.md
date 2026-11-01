# CR-1a / PARA-1a 第2版：独立・狭域修理確認（GPT-6）

**Verdict: NOT READY.** 第1版のR7（誤study・旧CR-1のG1保存領域の再利用）は**主要部分を解消**。ただし、今回約束した**「状態ファイルと非公開応答ファイルの食い違いで、送信前に停止」**は実装されておらず、凍結前blockingが残る。

**Earliest failing point: V1(c) / V2 — G1再開時の2ファイルの内容整合検査。** 同じヘッダーであっても state に「採択済み」と載るテンプレートの PRIVATE 記録が欠けていれば、正しいG1b/G2に使う土台の道が消えている。現在のコードは**ヘッダーしか比較せず**、完了済みテンプレートをスキップできる。また、1テンプレートの途中で止まると再送し得ることも、現行のテストでは検出されない。これらは**再開契約の局所修理**で対応可能。今回の監査でオーナー凍結は行わない。

## 読んだファイル／固定コミット

- **対象**: `chichichi2001/Pork` / `decision-points` / **`d3cdd56d9e43b15f19fd503978fca11ee7b3a77a`**。
- **依頼** `notes/cr1a_review_request_v2.md` — Git blob `c6b03bde2e66544688f0155f80f882247e1b0f07`。
- **未凍結改訂** `notes/cr1a_amendment.md` — `53a44d2f2e8966c7ffa703eb25c5e972c2e1dcf0`、`notes/para1a_amendment.md` — `7fe2c7c5891d98983596cc5ea6fda232ff3d7112`。
- **新規コード／テスト** `pork/cr1_run.py` — `e18a2c6ef5696249317249fc19d7fee883f0a3b7`、`tests/test_cr1_run.py` — `3320ecc48504b81ae12e98dcc52cb5d9f13f4cb1`、`scripts/build_cr1a_g1_notebook.py` — `7f7cd14d7b6b92f38f541df9f2fe7309cac0ac2a`。
- **旧G1生成器** `scripts/build_cr1_g1_notebook.py` — `0ba28469bb48474fa67a18e1a46c06fd01b96353`（説明の一行だけ追加）。
- **前回レビュー** `notes/cr1a_independent_review_20261012_gpt6.md` — `075b512458df5819febedce45e314c8808edd457`、コミット `1eeca82a79da979add0b9719cbc2ceab9f1a8810`。
- **参照のみ**: 凍結済CR-1計画 `notes/cr1_claude_resample_gate.md`、凍結済PARA-1計画 `notes/para1_paraphasia_plan.md`、元のG1停止・長さの保存記録、`pork/cr1_requests.py`、`pork/cr1_analysis.py`。全面再監査対象ではない。
- **証拠区分**: GitHubの上記コミットのソース・差分・テストを**読んだ静的コード監査**。以下の反例はコードの分岐から演繹した**人工状態**であり、実際の旧研究の非公開データやAPI実行を観測したものではない。Claudeによる「関連pytest 21件PASS」は**依頼書内の申告**であり、こちらではpytest、実API、Colab、実ベンチマークを**実行していない**。問題文・応答・実トークン文字列は出力していない。

## 判定一覧

| 問い | 判定 | 根拠 |
| --- | --- | --- |
| **V1(a) 送信前prompt SHA照合** | **PASS** | `check_study`が許可されたstudyと固定SHAを照合し、CR-1aのNotebook Cell 1→`header`→`run_g1`で再検査 |
| **V1(b) 保存先の分離** | **PASS** | 専用 `DECISION_POINTS/cr1a/G1/CR1A_G1*`。旧 `cr1/G1` と別。旧生成器はコード上不変 |
| **V1(c) 不整合・旧stateで停止** | **PARTIAL / BLOCKING** | 違うstudy/ヘッダーの拒否はPASS。**同じヘッダーだが PRIVATE の採択記録が欠ける／片方だけファイルがない**場合は拒否しない |
| **V1(d) G2 prompt/prefill/manifest row** | **PASS at helper level** | `g2_requests`がstudy明示で`resample_params`を構築、`g2_manifest_row`がcustom ID＋user/prefill SHAを返す。ただしG2の**実送信・段3ロック照合の完成**はこのコミットで実証されていない |
| **V2 人工E2E試験** | **PARTIAL / BLOCKING** | 正常prompt・旧CR既定・ヘッダー不一致・保存後切断・G2構成は検査するが、**同一ヘッダーの内容不一致と書込み途中切断**を検査していない |
| **V3 開示・one-shot・比較scope・PARA-1a** | **PASS** | 成功非保証、旧G1集計閲覧後の変更、G1b/期限で停止、記述比較、PARA-1a名前空間、G1前凍結を適切に記述 |

## V1(c)/V2 — BLOCKING：ヘッダー一致は状態と非公開応答の一致を意味しない

**根拠位置**: `pork/cr1_run.py` 63–82行（`open_state`と`open_private`）、86–94行（`run_g1`は`P["header"] == S["header"]`のみチェック）、124–132行（`P["items"]`／`S["templates"]`の更新とテンプレート単位のskip）。`scripts/build_cr1a_g1_notebook.py` 112–120行（STATE/PRIVをそれぞれ独立にロード・保存）。

**具体的な人工反例**:

1. 同じ`HDR`を使い`S = {"header": HDR, "templates": {"0": {"tried": [採択済の記録], "used": 0}}, "spent_usd": ...}`とする。
2. `P = {"header": HDR, "items": {}}`とする。両ファイルの**ヘッダーは一致**するが、採択したテンプレート0の土台文字列が欠けている。
3. `open_state(S,HDR)`も`open_private(P,HDR)`も通過し、`run_g1`の唯一の横断チェックはヘッダー比較だけ。`todo`は`"0"`をすでに完了として除外する。他のテンプレートが残っていれば**API送信を続行できる**。全100件が完了済みなら**ゼロ送信のまま正常終了し得る**が、後続G2の前提となる採択土台は欠けたまま。

Notebookでは`STATE`が存在して`PRIV`だけ存在しない場合も`open_private(None,HDR)`で空のPRIVATEを**新規作成扱い**にし、拒否しない。逆向き（PRIVATEだけ存在）も新規STATE扱いになる。これは第2版の「状態と非公開ファイルの食い違いでは1件も送らずに止まる」という**明文の契約違反**。

**最小修理（API送信前のfail-closed gateを1本追加）**:
- **二つの保存物の存在整合**：両方なしならfresh、両方ありなら両方のヘッダーと内容を検査。片方だけある場合は**`ContractError`で停止**。復元前に空の側を黙って作らない。
- **内容の双方向照合**：採択済（`S.templates[tid].used != None`）のtid集合が`P.items`のtid集合と一致し、各tidの`id/instance`と`used`が選ぶ候補のID/番号、baselineの`text_sha256`とPRIVATE文字列のSHAに一致することを**保存済stateの読込み直後・API前**に確かめる。未採択テンプレートはPRIVATEに存在しない。未知tid、重複、余剰なども拒否。
- **checkpointの一貫性**：現行の`save()`はSTATEとPRIVATEを**別々に上書き**するので片側成功・片側失敗があり得る。整合検査でfail-closedにするか、共通checkpoint IDを付した世代別ファイル／原子的rename等の方式にする。中断後の自動復元を保証するなら両ファイルが同じ世代か検査。
- **人工の追加試験**：同一HDRかつ採択STATE+空PRIVATE、STATEのみ、PRIVATEのみ、id不一致、本文SHA不一致、保存の片側だけ成功、すべてで **`api.sent == []`** を確認。この範囲だけの狭域修理再レビューで足りる。

### V2補足：切断がテンプレートの途中で起きた場合は「二度と呼ばない」を保証できない

`run_g1`は**テンプレートが最後まで終わってから**`S["templates"][tid]`を書いて保存する。APIが第2・第3候補を呼んだあとに接続断／プロセス停止があれば、そのテンプレートには完了フラグが付かず、再開時は候補1から再度呼び直す。既存の`test_resume_after_disconnect_continues_without_repeating`は「**3テンプレートが完全保存された後**に切断」という正常な回復例しか検査していない。現在の「途中で切れても繰り返さずに続く」は厳密には**完了済みテンプレートに限る**。

**最小修理**: 再実行時に未完了テンプレートの候補ごとの実行履歴を残して再利用するか、送信成功・応答保存の間に落ちた**結果不明リクエストは自動的に再送せずfail-closedで保留**とする。外部APIのidempotency保証なしに全障害でexactly-onceを保証したとは書かない。少なくとも「完了済みテンプレートは再呼出ししない／途中の呼出しは再送しうる」という制限を明示するなら、誇大な保証を避けられる。CR-1aの採択が不明な重複送信結果で変わらないよう、凍結時の方針を先に固定する。

## V1(a,b,d)：前回R7の大部分は合格

- `PROMPT_SHA256["CR-1a"]`を固定した`check_study`と、新ノートブックの単一`STUDY="CR-1a"`は有効。旧CR-1のデフォルトを壊さず、新旧データの保存先も分かれた。
- `tests/test_cr1_run.py`は偽APIでCR-1aだけの依頼、CR-1既定、study/hash不一致、異なるstudyのヘッダー、再開、`g2_requests`のプロンプト/prefill、`g2_manifest_row`を試す。**コードとテストの存在を確認したこと**と**独立にpytestがPASSしたこと**は別。
- G2のヘルパーは段3の必要材料（custom_id/user SHA/prefill SHA）を作れるが、**CR-1aの段3manifestの凍結や実際のバッチ送信前照合**をこのレビューでは確認できていない。後段実装時のstop gateはなお必要。

## V3：非blocking指摘の修理はPASS

- CR-1aは元G1のN、長さ、正解率の**集計を見た後のadaptive design**と正確に開示し、非公開の原文を見ていない点も当事者の申告と明記。60語指示は応答長や`N>=70`を保証せず、G1b費用や期限で止まったら再調整しない。
- 元CR-1、オープンDPとの比較は、条件の異なる**記述的対比**のみで、語数上限の因果効果を主張しない。
- `PARA-1a:<A-label> [source=CR-1a]`という名前空間を独立に設定し、旧PARA-1部Aの`NOT_RUN_CR1_STOPPED`を保持。両amendmentを**CR-1a G1前に**オーナー凍結する時系列規則も追加。旧凍結文書は変更されていない。

## 最終判断と次の再監査範囲

**NOT READY**。今回の前回R7への修理のうち、**studyとprompt SHA、専用保存先、G2ヘルパーは合格**。**最初の凍結阻害点はV1(c)：同一ヘッダーでも内容不整合のresumeを許容すること**。保存ペアの存在/内容/checkpoint整合検査と、その偽API負試験を凍結前に追加すること。途中切断時の再送の扱いも条件を曖昧にしない。G1/G2や凍結自体は実行・承認していない。

**Audit label:** GPT-6 / CR-1a PARA-1a V2 NARROW REPAIR CONFIRMATION / SOURCE SHA `d3cdd56d9e43b15f19fd503978fca11ee7b3a77a` / **NOT READY** / V1C SAME-HEADER PAIR INCONSISTENCY / STATIC CODE REVIEW ONLY / NO OWNER FREEZE.
