# CR-1 第4版 独立レビュー追補 — tail labels / readout / audit contract（GPT-6）

PRIVATE UNPUBLISHED RESEARCH — INDEPENDENT REVIEW; NO OWNER FREEZE; NO API RUN.

- 対象: `chichichi2001/Pork` branch `decision-points`, `notes/cr1_claude_resample_gate.md`.
- 対象 blob SHA: `ce85d5a7d5244732f38a9651faa1f6c39cdd5a00`（自己申告 Draft v4、2026-10-11 01:10 JST）。
- 併読した既存の同版レビュー: `notes/cr1_independent_review_v4_20261011_gpt6.md`（P1〜P5）。
- この追補は既存レビューと競合する新たな「凍結」や原案編集ではなく、**P1（ゼロ効果 null でも高AUROC）に追加して**、その資料が重点化していない運用上の点を指摘する。

## 監査結果

**VERDICT: PASS WITH REPAIRS; NOT FREEZE-READY.** 既存レビューP1が最優先。現行 `d_s=m\hat g` において同じ真の `q_diff=q_keep=q` のとき、`n_B=36`、`n_diff=k` とすると条件付きの二項モデルでは

```
E[d_s | k] = 0
Var(d_s | k) = q(1-q) [ k/36^2 + k^2/36^3 ].
```

観測上正の `d_s` の上位を選ぶと、分岐効果がなくても高 `m=k/36` の位置が紛れ込み、組Aの `u` が `m` と共変すれば高AUROCが可能。**A/Bの独立性、C2の相関、top15% positivity guardではこれを一般に除外できない**。既存レビューP1のnegative control提案は維持する。上記は簡約二項モデルの数学的性質であり、Claudeの実測結果ではない。

### A1 [IMPORTANT] C2数値相関と実際のtop15%ラベル一致は別

C2 は組Bを二分した `d_s` の Pearson r に Spearman–Brown を適用。しかし真に解析するのは、正値切断・全体上位15%の **binary label**。境界付近で多数の値が接近すれば、数値相関が高くても陽性群の入替え・問題内AUROCの有効問題集合の変更が起こり得る。

**提案**: 二分した `d_s` それぞれに定義13をそのまま適用し、陽性ラベルの一致率/重なり（例：Jaccard、kappa）と、AUROC両クラスのある問題集合の重なりを報告。C2>0.5だけをラベル安定性の証拠としない。これらが低い場合の主結果の留保を事前固定。**ただしラベル安定性が高くてもP1のnoise-induced AUROCを否定できるわけではない。**

### A2 [IMPORTANT] 形式不一致・打切りによる「違う回答」の混入

定義8は unreadable/empty/`max_tokens` without answer を「答えが異なる」と数える。これは規則として明快だが、回答内容の変更と `####` readout failure を区別しない。prefix 位置ごとに形式崩れの割合が違えば `q, d, d_s` の順位や `u` の関連が書式の問題で生じ得る。

**提案**: unreadable rate を、prefix cut、問題、`stop_reason`、陽性/陰性ラベル別に報告。事前固定の感度分析として「unreadable=changed」と「unreadableは除外（分母と欠落数を明記）」で主1・主3・対象問題数を並べる。除外分析にも selection bias があるので真値を確定するものではない。readout failure が高い場合の `READOUT_UNRELIABLE` 注記・verdict停止条件を事前に決める。

### A3 [IMPORTANT] G3監査失敗の判定が未固定

G3 は参照実装との差分ゼロを要求するが、不一致が1件でもあった場合の主ラベル停止規則がない。

**提案**: `PROTOCOL_AUDIT_FAIL_NO_CONFIRMATORY_VERDICT` などを用意し、監査で一つでも不一致があるときの停止・修理後の再監査・成果を未確定とする手順を凍結前に固定する。G1で適格問題<70の停止についても原因・ラベルを明記。tie / permutation / bootstrap / audit の全seed、iteration order、parser version / code SHAを凍結時の必須欄に含める。

### A4 [OPERATIONAL] 実験を始めてから予算尽きで no verdict になるリスク

およそ90問題×56切れ目×48本≈24.2万requestsを、1万件/バッチ、同時1バッチとすると約25バッチ。平均出力が100tokenなら原案試算で約$86、$90停止線に近く、残り件数×平均×1.2という安全係数で実費が$90以内でも停止しうる。これ自体は安全だが、**未完了のため科学的判定なしでAPIクレジットだけ消耗**する可能性がある。バッチには処理待ちもあるので月ごとのクレジット有効期間に注意。

**提案**: 本研究成果を見ないG0の費用・応答長・実行速度診断から、全量がその月の予算/期間内に完遂できそうかの GO/NO-GO 条件を事前固定。モデル料金・付与/失効条件は実行時に別途確認する。主結果に基づいて途中から N/K を削る変更は禁止。

### A5 [REPRODUCIBILITY] 単語分割とタイを機械的に一意化

「先頭空白＋非空白」は文字列によって複数改行/タブ/先頭無空白/末尾空白があり得る。具体的なregex・Unicode whitespace規則・`P_w` の連結恒等性検査を実装前に固定する。各cutで空/空白-onlyのfirst-unit sentinelと実際の文字列との衝突防止も定義する。fixed seedと書かれた箇所は数字・列の順序もfreeze recordに残す。

## 判定・スコープ

旧N1〜N7の多くは v4 で改善している。**最重要は既存レビューP1のゼロ効果negative control**。本追補A1/A2はその問題を補助的に診断するための追加仕様であり、代替策ではない。A3/A4/A5は実験停止や再現性の規則の明文化で、大掛かりな新規実験を要求しない。

独立レビューのみ。原案上書き、凍結、API本番、既存論文への組込みは実施していない。
