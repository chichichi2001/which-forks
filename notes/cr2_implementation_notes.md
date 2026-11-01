# CR-2 の実装メモ（凍結した計画 第10版に合わせた実装）

PRIVATE UNPUBLISHED RESEARCH.

- 2026-10-13 20:30〜 JST、Claude。凍結した計画 `notes/cr2_plan.md`（第10版、凍結 7949d74、記録 `notes/cr2_freeze_record.md`）に合わせて、第5版の形のコードを書き直した。**API には 1 件も送っていない**（試験はすべて作り物のデータ）。
- 第5版の実装メモ（演算・一様な抜き出しの形）は、このファイルの前の版（Git の履歴）に残す。
- ここに書くのは「計画に書いていない細かい決め方」。どれも計画の決まりを変えるものではない、と Claude は判断した。計画を変えないと実装できないことは見つからなかった。

## コードの場所

| 段階 | ファイル |
|---|---|
| 定数・段2（証跡・重複・下見 3・候補）・リクエストの一覧・探す段の数え方・確かめる段の表・分析（主0〜主3、C1〜C4、S8〜S12、感度） | `pork/cr2.py` |
| 定義 17・18 の共通の関数（格子・同点・二分探索・比べ用の単語） | `pork/cr2_search.py` |
| 探す段の回のたどり直し・先の件数の上限・段3b の記録と三つの照合 | `pork/cr2_stage3b.py` |
| G1・G1b・段3 の材料 | `pork/cr2_run.py` |
| G2s・G2c のバッチの仕組み（1 つのリクエストの一覧ごとに 1 つの状態ファイル） | `pork/cr2_g2.py` |
| G3（分析と監査）、監査用の別の実装（探す段も） | `pork/cr2_g3.py`、`pork/cr2_reference.py` |
| ノートブック（段2・受け入れ 1・G0G1・G2s・G2c・G3） | `scripts/build_cr2_notebooks.py` |
| 人工データの確かめ | `scripts/cr2_s2_recalibration.py`（9 世界）、`scripts/cr2_chase_power.py`（回帰確認の 3 世界） |
| 試験 | `tests/test_cr2.py`、`tests/test_cr2_runs.py`、`tests/test_cr2_search.py` |

CR-1・CR-1a・下見 3 のコード（`pork/cr1_*.py`、`pork/alt_prelook.py`）は変えていない。

## 試験（a）〜（p）の対応

| 計画の試験 | 主な試験 |
|---|---|
| （a）（b）（c） | `test_a_b_manifest_only_confirmation_cuts_and_shared_once`、`test_b_shared_cut_used_by_both_words`、`test_c_unselected_cuts_not_missing` |
| （d） | `test_d_missing_rule_and_stops`（5/6・16/18、N_MIN 60、探す段で外れた問題も「外れた問題」に数える、ちょうど 10%） |
| （e）（f） | `test_e_halves_nine_each`、`test_f_*`（文字どおりの並べ替え、全部数えられる小さな例、X と q を変えない） |
| （g） | G2 の仕組みの試験（`test_g2_*`、送ったか分からないバッチ・出し直し・結果ファイルの確かめ） |
| （h） | `test_constants_and_prompt` と、CR-1・CR-1a・下見 3 の試験を全部 |
| （i） | `test_i_definition10_boundaries`、`test_i_disagreement_counts` |
| （j） | `tests/test_cr2_search.py` の `test_j_*`・`test_f1_*` |
| （k1）（k2）（k3） | `test_k1_confirmation_quantities_ignore_search_responses`、`test_k2_rerun_search_changes_window_and_g2c_sends_nothing`、`test_k3_custom_ids_and_records_separate` |
| （l） | `test_l_controls_fixed_and_disjoint`、`test_l_every_window_and_length`、`test_stage3b_record_and_three_way_check` |
| （m） | `test_m_replay_is_deterministic_and_reuses_measured_cuts`、`test_m_search_rounds_replay_and_windows` |
| （n） | `test_n_early_stop_counts_future_stages`、`test_early_stop_examples` |
| （o） | `test_o_window_width_and_cut_zero`、`test_j_bounds_over_all_lengths_and_random_counts`、`test_o_search_drop_boundaries`（27/32 で外れ、ちょうど 28 は残る）、`test_o_confirmation_missing_and_report` |
| （p） | `test_p_*`（証跡：git の blob の SHA-1 と LFS の SHA-256、列・行・ID、重複・下見 3・同じ文・MATH の文・読めない正解、固定した順、ハッシュ）、`test_g1b_*`（固定した順の先頭、N の境目 59・60・90・90 超、深さの書き換えで採る ID が変わらない）、`test_seed_*`（I1・I2） |

## 計画に書いていない決め方

1. **正解が読めない行の扱いの順**：計画の順（1. 重複 → 2. 下見の除外 → 3. 候補）のあと、候補を選ぶ前に「正解が読めない行」を除く。下見 3 では 500 行すべて読めたので、実際には効かない見込み。数は `unreadable_gold`（除外のあと）と `unreadable_gold_all_rows`（全行）として段2 に記録する。
2. **列の名前**：6 列（`ID`・`question`・`answer`・`depth`・`seed question`・`seed answer`）と**完全に同じ集まり**のときだけ通す（多くても少なくても止める）。`ID` は整数として読めて重ならず、0 以上であること。
3. **README のライセンスの表示**：固定した版の README の前書きの `license:` が `mit` でなければ段2 で止める（計画の「表示が固定した版と食い違うときは段2 で止める」の実装）。
4. **深さの層**：3 以下を「2-3」、4・5 を「4-5」、6 以上を「6-8」とする（下見 3 の `depth_bucket` と同じ）。
5. **G1 の正答**：`decimal.Decimal` で比べる（`pork.cr1_analysis.same_answer`）。
6. **G1b の 1 件あたりの見込み**：第5版と同じく、先頭 n 問の土台の道の入出力の平均から出す。件数は各問の `max_requests(L)` の合計。N は、決まった順の先頭から 1 つずつ増やし、**はじめて収まらなくなったところで止める**（計画の「1 つずつ増やし」の字のとおり。第5版の実装は「収まる最大の N」だった。1 件あたりの平均が N で変わるので、まれに結果が違いうる）。
7. **探す段の回ごとの状態**：回ごとに別の状態ファイル（`CR2_G2S_round{r}_state.json`）。回 r の前の使用額（ヘッダーの `prior_spent_usd`）は G0＋G1＋それより前の回の G2s の使用額。回 r の 1 件あたりの見込みは、前の回の実績の平均（まだないときは G1b の見込み）。回 r の一覧のハッシュは、その回の状態のヘッダーに書き、再開のときは作り直した一覧がそれと一致しなければ止める。
8. **途中で止める条件の「先の件数」**：探す段の回 r では、まだ探している問題について「その L の探す段の切れ目の上限 − これまでに測った切れ目 − この回の切れ目」× 32 と、外れていないすべての問題の確かめる段の上限 11 × 24 を足す（`future_requests`）。確かめる段では 0。
9. **探す段の欠けで外れた問題**：ある回の切れ目が 28 本未満（2 回の出し直しのあと）なら、その問題はその回で外れる（次の回のリクエストを作らない）。同じ回に複数あれば、記録する切れ目はいちばん小さいもの。探す段の「解決しない」リクエスト（3 回失敗）は、この 28 本の決まりで扱い、それだけでは `INCOMPLETE` にしない。
10. **確かめる段の「解決しない」リクエスト**（コードの点検 M3 で直した）：2 回の出し直しのあとも失敗したリクエストは、終わった状態が分かっているので「欠け」（CR-1 の定義 8）として切れ目の欠けの決まり（5/6・16/18）で扱う。`INCOMPLETE` にするのは、終わった状態が分からないリクエスト（最後に流れたまま・確かめられないまま）が残ったときだけ。CR-1a の G3 は失敗のリクエストも `INCOMPLETE` に数えていたが、計画の字（「終わった状態が確かめられないもの」）に合わせた。失敗のリクエストの数は G3 の結果に別に書く。
11. **段3b の記録の形**：`pork.cr2_stage3b.canonical`（`json.dumps(sort_keys=True, ensure_ascii=True, separators=(",", ":"))`）の sha256 を段3b のハッシュとする。Git には、この正規の形の JSON（`notes/cr2_lock_stage3b.json`）をそのまま置く。比べ用の単語は記録では小さい順。
12. **G2c の前の受け入れ**：三つ（作り直し・Git の記録・Drive の記録）の正規の形のハッシュが一致し、さらにノートブックに書いた段3b のハッシュと一致すること。段3b のコミットはノートブックの祖先の一覧に入れる。G2c の状態のヘッダーと各バッチの記録に段3b のハッシュを書く。
13. **種を単位にしたブートストラップ**：主の区間と同じ乱数種（SEED_BOOT）と回数。種の並びは、問題の順で最初に出てきた順。問題を単位にした区間は、同じ関数で問題を 1 つずつの塊として計算する（CR-1 の `boot_ratio` と同じ値になることを試験で確かめた）。分母が 0 になった回は、その統計量について NA として数え、残りで区間を出す。
14. **1.5 倍の印**：種を単位にした区間の幅が、問題を単位にした区間の 1.5 倍以上の統計量があれば、注意書き `SEED_CLUSTER_INTERVAL_WIDER_1_5X` をつける（ラベルではない。要約で問題を単位にした区間を主に書かないための印）。
15. **S10・S12・欠けの報告**：S10 は Git の段3b の記録（数）から出す。S12 と欠けの報告は、探す段の生の結果から直接数える（たどり直しをしないので、探す段の結果が壊れていても計算できる。その場合は探す段の監査が落ちる）。S12 は、深さの層ごとと、切れ目の種類（格子・二分探索）ごとに出す。欠けの報告の切れ目の位置は L − c を 8 ごと（第5版の C4 と同じ）。
16. **G1 の前の受け入れを 2 つのノートブックに分けた**：受け入れ 1（`preg1`：試験と人工データ、API もデータも使わない。30〜50 分）と、受け入れ 2（`g0g1` のセル2：受け入れ 1 の結果のハッシュとコードの固定の照合、受け入れ 1 のあとでコードが変わっていないこと、段2 の照合）。受け入れ 1 の結果とコードのコミットは `notes/cr2_code_lock.md` に書く。
17. **人工データのスクリプトの小さな変更**：`scripts/cr2_s2_recalibration.py` と `scripts/cr2_chase_power.py` は、データ数 0 の世界を飛ばすようにした（差ありの世界を回さずに差なしの世界だけを回すため）。乱数種は世界の通し番号で決まるので、ほかの世界の数は変わらない。
18. **コードの点検（独立のエージェント、f2dd689 が対象）を受けて直したこと**：
    - M1：G2s・G2c・G3 のノートブックは、送る前に (1) G1 のあとで `pork`・`scripts`・`tests` が変わっていないこと（`git diff`）、(2) Git に固定した段3 の記録（`notes/cr2_lock_stage3.json`）と、定義 17・18 のコードの blob・numpy と SDK の版・料金・予算・探す段と確かめる段の決まりが一致すること、を確かめる。リクエストの一覧のハッシュに、モデルと最大トークンを入れた。段3b の記録の `rules` に、モデル・最大トークン・欠けの基準・B_stop を足した。numpy の版が段3 と違えば止まる（計画の「照合に落ちたら 0 件で止める」のとおり。そのときは Claude に相談）。
    - M2：G2c のバッチの記録の段3b のハッシュを、送る前の印（送ったか分からないときに使うもの）にも入れた（あとから見つけて採ったバッチにも入る）。
    - M3：上の 10.。
    - m1：AUROC の「問題を単位にした区間」は主1 の区間そのもの（対象の問題のブートストラップ）を使う。
    - m2：途中で止める条件の 1 件あたりの見込みに、G1b の値の × 1.2 が二重にかかっていた。× 1.2 の前の値を渡すようにした。
    - m3：探す段が途中で止まったときは、G2s のノートブックが G3 の出し先（`G3/CR2_G3_result.json`）に同じ形で `INCOMPLETE` を書く。
    - m4：受け入れ 1 は、試験のファイルが 1 つでもなければ止まる。
    - m5：G0G1 は Git に固定した段2 の記録と照合する。G2c は、Git の段3b の記録が段3b のコミットのものと同じことも確かめる。
    - m6：G3 に、深さの層ごとの最終の N・外れた理由・正答率、段2 の種の数（候補・下見と種が同じもの）、S12 の切れ目の役割（格子の 0〜4 番・二分探索）ごとの数、CR-1 の G3 と同じ 2 つの小さな例（全部数えられる例を 2 つの割合で）を足した。

## 運用のメモ（2026-10-14 09:0x JST）

- **同じランタイムでセル1をもう一度実行すると、git clone が 128 で失敗する**（Claude の不具合）。セル1 は最後に `os.chdir(REPO)` するので、2 回目のセル1 の `shutil.rmtree(REPO)` が「いまいるフォルダ」を消し、そのあとの `git clone` が `fatal: Unable to read current working directory` で止まる（Claude の作業環境で再現した）。送信より前なので、API には何も送られない。
- 直すには `scripts/build_cr2_notebooks.py` を変える必要があるが、G2s・G2c・G3 のノートブックは「G1 のあとで `pork`・`scripts`・`tests` が変わっていないこと」を送る前に確かめる（M1）。そのため、この実験の途中では直さない。**回し直すときは、毎回「ランタイムを接続解除して削除」してから、新しいランタイムでセル1 から実行する**（ノートブックの続きからの再開の仕組みは、Drive の記録から再開するので、ランタイムを替えても続きから回る）。

## 運用のメモ 2（2026-10-14 11:3x JST）：エラーを丸ごと通知する

- 経緯：G2c のセル2 がエラーで止まったが、千紗さんの画面にもエラーの文面が出ず、Colab は出力を Drive のノートブックに保存していなかった（Claude が Drive から読んで確かめた）。Drive に `G2C` のフォルダがないので、止まったのは送る前の照合の途中（`R1.drive_smoke` より前）。API には何も送っていない。
- オーナーの依頼（2026-10-14 11:18 JST、原文）：「今後はエラーが出たときエラーをまるごと通知で送れないかな。」
- 作ったもの：`notebook_tools/error_report.py`（試験は `notebook_tools/test_error_report.py`）。エラーが出たら (1) 通知の本文にトレースバックを入れる（API キー・トークンらしい文字は伏せ字、300 字を超える行は切る、本文は 4 KB 未満で末尾を残す。ローカル変数の値は入らない）、(2) 全文を Drive の `DECISION_POINTS/_errors/<名前>_<時刻>.txt` に保存する。あわせて、(3) 通知の仕組みをセル1 の先頭に移し、セル1 自身のエラー（git clone など）も届くようにし、(4) セル1 の rmtree の前に `os.chdir('/content')` を入れて、同じランタイムでのやり直しで clone が 128 で止まる問題（運用のメモ 1）をなくした。
- 置き場所：`scripts/notebook_notify.py` を変えると、CR-2 のノートブックの「G1 のあとで `pork`・`scripts`・`tests` が変わっていないこと」の確かめに落ちる。通知は分析のコードではないので、CR-2 のあいだは、組み立てたノートブックにこのモジュールで差し込む（`python3 -m notebook_tools.error_report <ノートブック> <名前>`）。分析のコード（`pork`・`scripts`・`tests`）は 1 文字も変えていない。CR-2 が終わったら `scripts/notebook_notify.py` に移し、ほかのノートブックの組み立てにも入れる。
- G2c のノートブックは、セル1 だけが変わる（セル2・セル3 は前の版とバイト単位で同じ。コードの head も c2659a5 のまま）。

## 運用のメモ 3（2026-10-14 11:3x JST）：G2c のセル2 が止まった原因

- 新しいエラーの通知で分かった：`R1.drive_smoke(OUT)` が `FileNotFoundError` で止まった。Drive に `DECISION_POINTS/cr2/G2C` のフォルダがまだなく、`drive_smoke` はフォルダを作らないため（Claude の不具合。G2s のときは `G2S` のフォルダが G0G1 で作られていたので起きなかった）。
- 止まったのはセル2 の 60 行目で、**段3b の三つの照合（作り直したもの・Git・Drive）はその前に通っている**。API には何も送っていない。
- 直し方：G2c のノートブックのセル2 で、`drive_smoke` の前に `OUT.mkdir(parents=True, exist_ok=True)` を足した（v3）。分析のコード（`pork`・`scripts`・`tests`）は変えていない。`scripts/build_cr2_notebooks.py` の同じ箇所は、CR-2 が終わってから直す。

## 運用のメモ 4（2026-10-14 13:3x JST）：CR-2 のあとの変更

- CR-2 は G3 まで終わった（`notes/cr2_g3_result.md`）。CR-2 のノートブックは自分の head に固定されているので（G3 は a49135f）、このあと `pork`・`scripts`・`tests` にファイルを足しても、CR-2 のノートブックの照合には影響しない。
- 足したもの：`pork/cr3_explore.py`・`tests/test_cr3_explore.py`・`scripts/build_cr3_explore_notebook.py`（CR-2 のデータの探索的な見直し、`notes/cr3_explore_spec.md`）。CR-2 の分析のコードは変えていない（見直しのノートブックが `git diff` で確かめる）。
- エラーの全文の通知は、これからの組み立てでは `notebook_tools.error_report.patch_cell1` をセル1 に当てて入れる。
