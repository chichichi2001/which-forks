<!-- 2026-10-06: 計画 notes/dp2_side_analyses_plan.md の C。論文の存在は arXiv/会議ページで確認（別エージェントによる検索）。Cliff Tokens は本セッションでも arXiv ページを直接確認し、Zur et al. 2025 を関連研究として引用していることも確認。投稿前に [要確認] の項目を本文で確かめる。-->
# DP2 関連研究ノート（2026-10-06）

対象: DP2（OLMo-2 1B / GSM-Symbolic、greedy CoT 上で8トークンごとに T=1.0 で16本サンプル → q(t)、q が次点までに ≥0.25 落ちる窓を「real fork」と定義。(1) 窓内最大エントロピーが fork 窓を当てるか（item 内 AUROC）、(2) layer-12 残差ストリームの線形プローブが安価な特徴量（位置・数字トークン・エントロピー・p2）を超えるか）

凡例: [確認済] = arXiv/会議ページで存在・著者・ID を確認。[要確認] = 会場・年など一部が二次情報のみ。

---

## A. 「分岐点」をリサンプリングで定義する系（DP2 の直系）

### 1. Forking Paths in Neural Text Generation [確認済]
- Bigelow, Holtzman, Tanaka, Ullman. ICLR 2025. arXiv:2412.07961
- 方法: base 応答の各位置で代替トークンに差し替え → 続きを再サンプル → 最終回答の分布の時系列。ベイズ変化点検出・生存分析で「forking token」を特定。GPT-3.5、GSM8K/AQuA など7タスク。
- 所見: 変化点確率とトークン確率の相関は小さい＝分岐はエントロピー/低確率トークンでは説明しきれない、と報告。
- DP2 との差: Bigelow は「強制差し替え（forced swap）」型で、DP1 に近い。DP2 は prefix からの自由サンプリングで定義した q(t) の段差。API モデル（GPT-3.5）で内部状態なし→ DP2 は open 1B で残差プローブまで行う。エントロピー vs fork の関係を item 内 AUROC で事前登録的に検定する点が追加。

### 2. Are language models aware of the road not taken? Token-level uncertainty and hidden state dynamics [確認済（会場は要確認）]
- Zur, Geiger, Lubana, Bigelow. arXiv:2511.04527（2025-11）。取得ページに ICML 表記あり、年は要確認。
- 方法: Forking Paths で各トークン位置の結果分布 o_t を推定。中間層（6–10層）の残差に線形プローブを当て o_t を予測（KL 損失）。difference-in-means ステアリングも。Llama-3.2 3B / Gemma-2 2B、GSM8K/AQuA/GPQA（多肢選択化）。
- 所見: 「不確かなときほどステアしやすい」。自モデルの活性は他モデル埋め込みより o_t をよく予測。
- DP2 との差: **最も近い先行研究（ノベルティリスク高）**。「隠れ状態から分岐/結果分布を線形に読める」はここで既に示されている。ただし、確認できた範囲では baseline は一様分布・多数派・他モデル埋め込みで、**エントロピー・位置・数字トークン・p2 といった安価特徴量を超えるか**、**item 内（問題固定）での識別**は主題になっていない模様（本文全体は未精読、要確認）。DP2 は「fork の“位置”を当てる」タスク、DP1 の「digit/位置で説明された」という負の結果を踏まえた統制が差分。

### 3. Thought Anchors: Which LLM Reasoning Steps Matter? [確認済]
- Bogdan, Macar, Nanda, Conmy. arXiv:2506.19143（v4: 2025-10）。会場は未確認（プレプリント扱い）。
- 方法: 文単位で100回リサンプルし、最終回答分布の変化（KL）で counterfactual importance を測る。+ receiver heads、attention 抑制。R1-Distill-Qwen-14B ほか、MATH（正答率25–75%の20問）。
- 所見: 計算文より「計画」「不確実性処理」の文が重要。
- DP2 との差: 粒度が文、対象は長い推論モデル。DP2 はトークン窓（8トークン刻み）で、非推論 1B・短い CoT。安価特徴量 vs プローブの比較はない。

### 4. Critical Tokens Matter (cDPO) [確認済]
- Lin, Liang, Xu, Wang, Luo, Shi, Li, Yang, Tu. ICML 2025（PMLR v267）. arXiv:2411.19943
- 方法: 誤答軌跡上で各トークンを固定して64回ロールアウト、正答率0になる最初のトークンを critical token とする。実用上は正誤軌跡で学習した2モデルの尤度比で推定 → cDPO。Llama-3 8B/70B, DeepSeek-math-7B、GSM8K/MATH500。
- DP2 との差: 目的は学習（DPO）。critical の定義は「正答確率」で、DP2 は「greedy 答えとの不一致率」。エントロピーや隠れ状態での予測可能性は主題外。

### 5. Phi-4 Technical Report — Pivotal Token Search [確認済]
- Abdin ほか（Microsoft）. 2024-12. arXiv:2412.08905
- 方法: 各トークン前後の成功確率をサンプリングで推定し、差が閾値を超えるトークンを pivotal として DPO データ化。
- 所見: pivotal token は必ずしも低確率ではない、という記述。
- DP2 との差: 定義（成功確率のジャンプ）は q(t) の段差とほぼ同型。ただしデータ生成手法の紹介で、エントロピーやプローブによる予測評価はない。

### 6. Cliff Tokens: Identifying Single-Token Failure Triggers in LLM Mathematical Reasoning [確認済（年要確認）]
- Ko, Kang, Lee. arXiv:2606.25524（ID 上は 2026-06。取得要約は「2025」と記載、要確認）
- 方法: N=64 ロールアウトでトークン単位の「正答到達確率」を推定、z 検定的な適応閾値で ≥0.1 の急落を cliff と定義。Qwen3 0.6B–8B, Llama-3.2 1B/3B, Llama-3.1-8B, Gemma-3-4B、GSM1K/MATH500/AIME25。
- 所見: cliff をエントロピーで分類（決定論的 cliff＝低エントロピー、不確実 cliff、サンプル外れ cliff）。決定論的 cliff はスケール不変。
- DP2 との差: **1B 級を含みエントロピーとの関係にも触れる点で近い（ノベルティリスク中）**。ただし隠れ状態プローブはなく、数字トークンの分析もない（取得要約による）。「低エントロピーなのに分岐する点」が存在するという報告は DP2 の (1) の予想に直接関係する。

### 7. Enhancing LLM Reasoning via Selective Critical Token Fine-Tuning (CFT) [確認済]
- Ruan, Li, Zhu, Chen, Li, Liu, Chen. arXiv:2510.10974（2025-10）
- 方法: 正答の greedy 解の各トークンを top-2/3 代替に差し替えて再生成、全差し替えで誤答になれば critical。
- DP2 との差: DP1 の「forced top-2 swap」とほぼ同じ設計。学習目的で、予測可能性の評価なし。DP1→DP2 で swap 定義からサンプリング定義へ移った理由づけに引用可。

---

## B. エントロピー＝分岐点という仮定を使う系

### 8. Beyond the 80/20 Rule: High-Entropy Minority Tokens Drive Effective RL for LLM Reasoning [確認済]
- Shenzhi Wang ほか（Qwen Team / Tsinghua LeapLab）. NeurIPS 2025. arXiv:2506.01939
- 方法/所見: CoT の約20%の高エントロピートークンを「forking tokens」と呼び、RLVR でそこだけ勾配を通しても同等以上。高エントロピーは "wait", "however", "thus", "suppose" 等の接続語、低エントロピーは数式の構成要素など。
- DP2 との差: 「高エントロピー＝fork」は**仮定**であり、リサンプリングで定義した fork との一致は直接検証していない。DP2 の (1) はまさにこの仮定の検証。さらに彼らの「数式成分は低エントロピー」と DP1 の「swap fork は数字に集中」の食い違いは DP2 で論点にできる。

### 9. Entropy-Aware Branching for Improved Mathematical Reasoning [確認済]
- Li, Callanan, Zhu, Sibue ほか（Queen's / JPMorgan）. arXiv:2503.21961（2025-03）。会場は要確認。
- 方法: エントロピーと varentropy が閾値超えのとき K 分岐、PRM 等で選択。小型 LLM で最大 +4.6%。
- DP2 との差: エントロピーを分岐トリガーとして使うが、トリガーが実際の答え分岐を当てているかは測っていない。

### 10. Reasoning with Sampling: Cutting at Decision Points (Entropy-Cut MH) [確認済]
- Zhou, Mehrotra, Liu（Yale/Stanford）. arXiv:2605.30327（2026-05）
- 方法/所見: 正のエントロピージャンプ位置で MH の切断点を選ぶ。高エントロピー切断は低エントロピー切断より distinct-answer 率が約1.36倍、と**リサンプリングでの粗い妥当性検証**あり。Qwen2.5-7B ほか。
- DP2 との差: 検証は「高 vs 低エントロピーの平均比較」で、item 内 AUROC・位置/数字の統制・プローブ比較はない。DP2 は「エントロピーがどこまで当てるか」をより厳密に定量化する位置づけ。

### 11. Chain-of-Thought Reasoning Without Prompting [確認済]
- Xuezhi Wang, Denny Zhou. NeurIPS 2024. arXiv:2402.10200
- 方法: 最初のトークンで top-k 分岐 → greedy 継続。答えトークンの top-1/top-2 確率差（confidence margin）で CoT 経路を選ぶ。
- DP2 との差: p2 / margin を信頼度指標に使う先例。DP2 の安価特徴量「p2」の根拠として引用。分岐は第1トークンのみで、途中位置の fork 予測ではない。

---

## C. 隠れ状態から最終答え・正誤を読むプローブ系

### 12. Reasoning Models Know When They're Right: Probing Hidden States for Self-Verification [確認済]
- Anqi Zhang, Yulin Chen, Jane Pan ほか（NYU）. arXiv:2504.05419（2025-04）。会場要確認。
- 方法/所見: 中間答えの正誤を隠れ状態の2層 MLP で予測。答えが出る前から予測可能（look-ahead）。早期終了で最大24%トークン削減。
- DP2 との差: 予測対象は「正誤」で「分岐の位置」ではない。安価特徴量 baseline との比較は主目的でない。

### 13. Temporal Predictors of Outcome in Reasoning Language Models [確認済（査読なし）]
- Joey David（独立研究者）. arXiv:2511.14773（2025-11）
- 方法/所見: CoT 先頭 t トークン後の隠れ状態（PCA128 + L2 ロジスティック）で正誤を予測。t=4 で AUC 0.84。エントロピー・長さ baseline（AUC 0.59）を大きく上回る。難易度で層別しても残る。
- DP2 との差: 「プローブ > エントロピー」の先例だが、item 間で正誤を当てる設定で、**難易度などの item 交絡が効きやすい**。DP2 は item 内 AUROC で交絡を潰す点が差分（＝この論文の弱点に対する改善として書ける）。

### 14. Think-to-Talk or Talk-to-Think? When LLMs Come Up with an Answer in Multi-Step Arithmetic Reasoning [確認済（会場要確認）]
- Kudo, Aoki, Kuribayashi, Sone, Taniguchi, Brassard, Sakaguchi, Inui. arXiv:2412.01113
- 所見: 合成算術で、単一ステップの部分問題は CoT 前に決まり、多段計算は CoT 中に決まる（10モデル、線形プローブ + activation patching）。
- DP2 との差: 「答えがいつ決まるか」を変数値プローブで見る。DP2 の fork が計算（数字）位置に集中するなら、この「多段計算は CoT 中に決まる」と整合的と議論できる。

### 15. How Far Ahead Do LLMs Plan? Uncovering the Latent Horizon in CoT Reasoning [確認済（会場は取得ページ表記）]
- Liyan Xu, Mo Yu, Fandong Meng, Jie Zhou. arXiv:2602.02103。取得ページに ICML 2026 表記。
- 所見: Tele-Lens（低ランクアダプタのプローブ）で、隠れ状態は直近の遷移しか予見せず「近視眼的」。重要な pivot 位置に絞ると不確実性推定が改善（"Wooden Barrel Principle"）。
- DP2 との差: 「プローブは先を読めない」側の証拠。DP2 のプローブが安価特徴量を超えなければ、これと整合する結果として位置づけられる。

### 補助的に引用可能（確認済）
- Kadavath et al. 2022, "Language Models (Mostly) Know What They Know", arXiv:2207.05221 — 自己評価・P(IK) の古典。
- Orgad et al., "LLMs Know More Than They Show", ICLR 2025, arXiv:2410.02707 — 正誤情報は特定トークン（exact answer tokens）に集中。プローブ位置の選び方の根拠。
- Kossen et al., "Semantic Entropy Probes", arXiv:2406.15927（ICML 2024 関連ページあり, 要確認）— サンプリング由来の意味的エントロピーを隠れ状態から安価に予測。DP2 の「q(t) をプローブで代替できるか」の発想の祖。
- Ashok & May, "Language Models Can Predict Their Own Behavior", arXiv:2502.13329, NeurIPS 2025 — 入力の内部状態から出力挙動を予測し早期終了。
- ERPO (Yu, Li, Zhao, Yang), arXiv:2603.28204 — 高エントロピーを "Critical Decision Pivots" とみなす RL。B 群と同じ仮定の例。
- GSM-Symbolic: Mirzadeh et al., arXiv:2410.05229（データセット出典。今回は ID のみ二次情報で確認）。

---

## ノベルティリスク（正直な評価）

- **高: Zur et al. 2025 (arXiv:2511.04527)**。「forking 由来の結果分布を中間層の線形プローブで予測できる」は既出。DP2 の (2) を「隠れ状態に fork 情報がある」とだけ主張すると新規性はほぼない。差分として主張できるのは:
  - 予測対象が「fork の位置（段差窓）」であり、結果分布の値ではない
  - 安価特徴量（位置・数字トークン・エントロピー・p2）を明示的 baseline にした増分評価
  - item 内 AUROC による問題レベル交絡の除去
  - 1B の open モデル、事前登録ゲート
  - ※ Zur et al. 本文で entropy baseline を使っているかは未精読。投稿前に必ず本文確認。
- **中: Cliff Tokens (arXiv:2606.25524)**。ロールアウト急落の定義 + エントロピー分類 + 1B 級モデル。DP2 の (1)「エントロピーは fork を当てるか」に部分的に答えている可能性（低エントロピー cliff の存在）。ただし AUROC 的な識別評価・プローブはない模様。
- **中: Bigelow et al. 2025**。「分岐はトークン確率と相関が小さい」はすでに報告済み（GPT-3.5, swap 型）。DP2 の (1) が否定的結果なら「open 1B・サンプリング定義・item 内で再現」という確認的位置づけになる。
- **低〜中: Entropy-Cut MH (arXiv:2605.30327)**。エントロピー位置でのリサンプリングが答えを変えやすいという粗い肯定的証拠。DP2 が肯定的結果なら「どの程度か」を厳密化した位置づけ。
- **低: Temporal Predictors (2511.14773)**。プローブ > エントロピーを示すが item 間設定。DP2 の item 内設計はその交絡批判として書ける。
- 総じて「エントロピー vs サンプリング定義の fork を、item 内 AUROC と安価特徴量統制で比較し、プローブの増分を問う」組み合わせ自体をそのまま行った論文は今回の検索では見つからなかった。ただし検索は網羅的ではない（特に 2026 年のプレプリント）。

## DP2 の書き方への示唆
- Wang et al.（80/20）の「高エントロピー＝forking token」仮定と、DP1 の「fork は数字に集中」（Wang 側では数式成分は低エントロピー）の食い違いを動機として前面に出せる。
- DP1 の swap 型定義は Bigelow / CFT 型、DP2 のサンプリング定義は Phi-4 PTS / Cliff Tokens / Thought Anchors 型、と系譜を整理できる。

## Sources
- https://arxiv.org/abs/2412.07961 ／ https://iclr.cc/virtual/2025/poster/30769
- https://arxiv.org/html/2511.04527v1
- https://arxiv.org/html/2506.19143v4
- https://arxiv.org/abs/2411.19943 ／ https://proceedings.mlr.press/v267/lin25j.html
- https://arxiv.org/pdf/2412.08905
- https://arxiv.org/pdf/2606.25524
- https://arxiv.org/pdf/2510.10974v1
- https://arxiv.org/html/2506.01939v2 ／ https://neurips.cc/virtual/2025/poster/115123
- https://arxiv.org/html/2503.21961v1
- https://arxiv.org/pdf/2605.30327
- https://arxiv.org/abs/2402.10200v2 ／ https://proceedings.neurips.cc/paper_files/paper/2024/hash/7a8e7fd295aa04eac4b470ae27f8785c-Abstract.html
- https://arxiv.org/html/2504.05419v1
- https://arxiv.org/pdf/2511.14773
- https://arxiv.org/html/2412.01113v2
- https://arxiv.org/pdf/2602.02103
- https://arxiv.org/pdf/2207.05221
- https://arxiv.org/abs/2410.02707v2
- https://arxiv.org/abs/2406.15927
- https://arxiv.org/html/2502.13329v2 ／ https://neurips.cc/virtual/2025/poster/116590
- https://arxiv.org/pdf/2603.28204
- https://hyper.ai/ko/papers/2410.05229/resources (GSM-Symbolic ID の二次確認)

---

## 追記（2026-10-06 19:0x）：Zur et al. 2025 の本文確認（v1）

arXiv HTML v1（2025-11-06）を読んだ（取得ツールの要約経由。引用はほぼ原文。v2以降があるかは確認できず）。
- **プローブが当てるもの**：各トークン位置の結果分布 o_t（KL損失）。分かれ道かどうかの判定や、変化点ではない。変化点は別にベイズ変化点検出で出し、ステアリングの成否と比べるだけ。
- **比較相手**：一様分布（KL 1.53）、多数派（0.85）、別モデル（Gemma-2 2B）の活性（Llamaの自分の活性 0.11 vs Gemma 0.19、8層）。**エントロピー・トークン確率・p2・位置などの安い特徴量は比較相手にしていない。** エントロピーと分かれ道の関係も扱っていない。
- **評価の単位**：AQuAの10問。検証は「保留したトークン位置」で、問題をまたいだ分割か問題内かは不明。問題内の評価や難しさの統制はない。
- **先読み**：なし。プローブは同じ位置の o_t を同じ位置の状態から当てる。プロンプト末からの予測もない。
- 数字などの語の種類の分析もない。
- **DP2で新しいと言えること**：
  - (a) サンプリングで決めた分かれ道の区間に対するエントロピーの問題内AUROC：新しい。
  - (b) 安い特徴量（位置・数字・区間の最大エントロピー・最大p2）への上乗せ：新しい。いちばん近い先行として引用する。
  - (c) 16トークン前の状態（S1）：新しい。
  - (d) プロンプト末の状態から q(0) を当てる（S2）：新しい。「どこで落ちるか」は、彼らの変化点検出と考え方が近いので、関連づけて書く。
- **譲るべき点**：「中間層の隠れ状態から、トークンごとの結果分布を線形に読める」は既出。DP2の新しさは、統制（問題内・安い特徴量・先読み）にある。
- 会場は未確認（ページのメタ情報に ICML とあるが、テンプレートの可能性）。

---

## 追記（2026-10-07 13:1x）：DP2 の本筋の知見（「分かれ道の定義でエントロピーとの関係が逆になる」）の新しさの確認

DP2 の結果（`notes/dp2_result.md`）を受けて、本筋の知見について追加で検索した（WebSearch extended ×4、本文の取得 ×3）。

### 新しく見つけた／位置づけ直した関連研究
- **Thought Branches: Interpreting LLM Reasoning Requires Resampling**（Macar, Bogdan ほか, arXiv:2510.27484, ICLR 2026）[確認済]
  - 文の単位で、強制的な書き換え（off-policy）と、モデル自身からの引き直し（on-policy）を比べ、強制的な書き換えは「効果なし」が多く（24.5〜27.6% 対 7.1〜11.4%）、分布のずれや自己修正で因果の重要度を誤らせる、と主張。題材は安全系のシナリオ（恐喝・内部告発）。**エントロピーとの関係は扱っていない**。
  - → DP1→DP2 の「強制入れ替えの分かれ道は実際には起きない」は、考え方としてはここで既に言われている。**必ず引用し、DP2 はトークン単位・算数・エントロピーとの関係で具体的に示した、と位置づける。**
- **Demystifying Entropy-based Selection for CoT Compression**（Candussio ほか, arXiv:2607.28707, 2026-08）[確認済]
  - 数学の CoT では数字の語のエントロピーが低い（語彙が 0〜9 に限られるため）ことが、エントロピーによる選び方の見かけの効果を作っていた、と報告。高エントロピーが本当の分かれ道かは検証していない。
  - → DP1 で強制入れ替えの分かれ道が数字に集中し、エントロピーが逆向きになった理由の説明として使える（数字＝低エントロピー＝強制入れ替えで壊れやすい）。
- **What Does Chain-of-Thought Entropy Measure?**（Papamichalis, Ruane, arXiv:2609.25039, 2026）[確認済]
  - 分かれ道をエントロピーの閾値で定義（引き直しでは定義していない）。足場の語（接続詞など）と内容の語を分けると、どこが大きな分かれ道かの順位が食い違う。整形と数字の交絡を除くと、エントロピーによる選び方はランダムに勝てない。
  - → 「エントロピー＝分かれ道」の仮定への批判の流れの一つ。引き直しで定義した分かれ道との突き合わせはない。

### 本筋の知見の新しさ（正直な評価）
- **(a) 引き直しで決めた分かれ道を、エントロピーが問題内でどこまで見分けるか（0.660）**：直接測った論文は見つからなかった。近いのは Entropy-Cut MH（高エントロピーの切断点は答えが変わりやすい、平均の比較だけ）と Bigelow ほか（変化点とトークン確率の相関は小さい、強制入れ替え型・GPT-3.5）、Cliff Tokens（低エントロピーの急落もある）。→ **定量化として新しい。驚きは中くらい。**
- **(b) 分かれ道の定義（強制入れ替え vs 引き直し）で、エントロピーとの関係が逆になる（0.43 vs 0.66）、両者の重なりは 7%**：この形で示した論文は見つからなかった。ただし「強制的な介入は誤解を招く」という考え方は Thought Branches（ICLR 2026）が文の単位で既に示している。数字の語のエントロピーの低さ（Candussio ほか）が、逆向きになる仕組みの説明になる。→ **具体的な結果としては新しいが、主張は「方法論上の注意」の位置づけ。** 論文の中心に置くなら、Thought Branches との違い（トークン単位・エントロピー・事前登録・問題内の比較）をはっきり書く。
- 検索は網羅的ではない（特に 2026 年のプレプリント）。投稿前にもう一度確認する。

### Sources（追記分）
- https://arxiv.org/abs/2510.27484 ／ https://iclr.cc/virtual/2026/poster/10008605
- https://arxiv.org/html/2607.28707
- https://arxiv.org/html/2609.25039
- https://anaymehrotra.com/reasoning-with-sampling/

## 追記（2026-10-08）：DP3-X1 の発見「エントロピーは2番目の候補の影響を逆向きに指す」の新規性チェック

調べた範囲（Web 検索、2026-10-08 10:5x JST）では、**「その位置のエントロピーが高いほど、別の候補に入れ替えたときの答えへの影響が小さい（逆向き）」をはっきり報告したものは見つからなかった**。近いものは次のとおり。

- **Bigelow ほか「Forking Paths in Neural Text Generation」（ICLR 2025、arXiv:2412.07961）**：
  - 別の候補ごとに続きを引き、その候補の確率で重みづけして答えの分布を作る（"Forking Paths Analysis"）。これは DP4 の「層別の落ち幅」（最初の1語で分けて引く）と**同じ考え方**。
  - したがって DP4 の測り方そのものは新しくない。論文では Bigelow ほかを引用して、「同じ分け方を、エントロピーとの関係の説明に使った」と書く。
  - 強制入れ替え（どんな語でも入れれば分かれ道になりうる）と、実際に引かれうる分かれ道を区別しているが、両者のエントロピーとの関係は比べていない。エントロピーにも触れていない。
- **Bigelow ほか「Forking Fast」（arXiv:2608.19611、2026-08）**：
  - 引き直しの雑音は本数 S に対しておよそ 1/√S で減ると報告し、変化点検出で平滑化する方法を出した。
  - DP3 の「d の雑音」問題と同じ悩みで、対処のしかたは別。エントロピーには触れていない。
- **Zur・Geiger・Lubana・Bigelow「Are language models aware of the road not taken?」（arXiv:2511.04527、2025-11）**：
  - 「最終的な答えに一番自信がないときに、一番誘導しやすい」と報告している（R = 0.57）。
  - これは**答えの分布の不確かさ**の話で、1語のエントロピーの話ではない。DP4 の主2とは別の量。
- **Thought Anchors（Bogdan ほか、arXiv:2506.19143）**：
  - 文単位で、「答えを強制させる重要度」と「引き直しの重要度」を比べ、強制のほうが情報が少ないと結論している。
  - 「強制 vs 引き直し」で結論が変わるという**方法上の指摘は先行している**（ただし文単位・答えの強制で、語の入れ替えではない）。エントロピーとの関係は見ていない。
  - 論文の序論で必ず引用する。
- **高エントロピーの語が大事、という系統**：
  - Wang ほか「Beyond the 80/20 Rule」（arXiv:2506.01939）：高エントロピーの少数の語が強化学習の分かれ道。
  - Yang ほか「Less is More」（arXiv:2510.13940）：誘導できるのは主に高エントロピーの語。

  どちらも、高エントロピー＝分かれ道とみなしている。私たちの発見はこれを細かくするもので、次のように言える。高エントロピーの位置は、別の語が**選ばれやすい**から分かれ道になる。選ばれた別の語**1つあたりの影響**は、大きくない（DP3 では逆向き）。
- **Candussio ほか（arXiv:2607.28707）**：数学の CoT では数字の語のエントロピーが低い（既出）。DP3 の主2（数字の語）を支える。

### 論文への含み
- 主2（DP4 で確認待ち）が再現すれば、「高エントロピー＝重要な語」という見方への、**根拠つきの修正**として書ける。具体的には、「重要さ ＝ 選ばれやすさ × 1回あたりの影響」で、エントロピーは前者を表している、という書き方になる。
- 測り方（層別）は Bigelow ほかの Forking Paths Analysis と同じ発想なので、新規性は主張しない。
- 「強制 vs 引き直し」の対比は Thought Anchors が文単位で先にやっている。私たちの新しさは、**語の単位**で、**エントロピーとの関係が逆になる**ことと、**その仕組み**（数字の語・重みづけ）を事前登録で示した点に置く。

---

## 追記（2026-10-09）：論文の下書きに関連研究の節を入れたときの確認

論文の下書き（`paper/draft_en.md` の 5 Related work）と参考文献（`paper/refs.bib`、29件＋3件）を作った。別エージェント3つで、(1) 書誌の確認、(2) 新しい関連研究の検索、(3) 下書きの各文の照合をした。

### 書誌の直し（前の記録からの変更）
- Cliff Tokens（2606.25524）：v3（2026-09-28）で題名と著者が変わった。「Analyzing Failure Trigger Tokens in LLM Mathematical Reasoning」、Ko・Jinu Lee・Kang・Yukyung Lee。
- Entropy-Aware Branching（2503.21961）：題名と著者を変えて **EACL 2026** に載った（「Entropy-Gated Branching for Efficient Test-Time Reasoning」）。
- Critical Tokens Matter（2411.19943）：ICML 2025 は公式のページで**確認できなかった**。arXiv として引用する。
- Thought Branches：ICLR 2026 を確認。著者は Macar・Bogdan・Rajamanoharan・Nanda。
- Less is More（2510.13940）：**ACL 2026**。高エントロピーの語だけに classifier-free guidance をかける方法（活性の誘導ではない）。
- Reasoning with Exploration（Cheng ほか、2506.14758）：**AAAI 2026**。
- Think-to-Talk（Kudo ほか、2412.01113）：題名を変えて **Findings of EACL 2026**。
- Gemma Scope：BlackboxNLP 2024。circuit-tracer のライブラリは Hanna ほか、BlackboxNLP 2025。
- Demystifying Entropy-based Selection（Candussio ほか）：BlackboxNLP 2026 は二次情報だけ（未確認）。

### 新しく見つけた関連研究（論文で引用した）
- **Fork Where the Model Changes Its Mind**（Lei ほか、2609.11061、2026-09）：行の区切りで分かれ道を置く強化学習。答えの信念の変化のほうが、次の語のエントロピーより、モンテカルロの価値の変化をよく追う（4B〜32B の推論モデル）。私たちの「引き直しの側ではエントロピーと強く一致」と緊張関係があるので、粒度・モデル・評価の違いを書いた。
- **Where Hindsight Credit Can Reside**（He ほか、2604.11056）：引いた語が報酬について持つ情報（条件つき相互情報量）は、その位置のエントロピーを超えない、と定式化。私たちの恒等式（|d| ≤ 1 − p₁）と同じ向き。強制入れ替えは確率で重みづけされないので小さくならない、という対比に使った。
- **The Last Word Often Wins**（Garcia、2605.10799）：算数の CoT を壊す実験の効果は、最後の答えの行の読み出しでほとんど決まる。数字の語の壊れやすさの一部は「読み出し」かもしれない → 限界の節に「Readout」の項目を足した（切り分けていない）。

### 新しく気づいた、先行研究との緊張
- **Forking Paths（Bigelow ほか）の付録 C.2**：トークンの確率は、答えの分布が変わる位置（変化点）を強くは予測しない（GPT-3.5、7課題）。私たちの「引き直しの落ち幅とエントロピーは強く一致」とは、モデル・課題・指標（生成した語の確率 vs エントロピー）・評価（変化点 vs 問題内の順位）が違う。論文では、違いを書いたうえで「解決していない」と書いた。
- Candussio ほか：数学で低エントロピーの語を残すと効くのは、数字の語のエントロピーが低いせい、と報告 → 私たちの数字の語の話を一部先取りしている、と論文に書いた。

### 新しさの評価（検索の範囲で）
- 主張1（分かれ道の定義でエントロピーとの関係の向きが逆になる）：同じ位置で両方の定義を測って向きの逆転を報告した論文は見つからなかった。
- 主張2a（数字の語）：定性的には一部先行あり（Candussio ほか、介入型の重要度は数字に集まる系の論文）。問題内の逆向きの定量化は新しい。
- 主張2b（恒等式）：全期待値の法則からすぐ出る。Forking Paths の混合と Thought Anchors の文単位の分け方が先祖。新しいのは「エントロピーとの関係の説明に使った」点だけ、と書いた。
- 主張3（名簿の課題）：重なる研究なし。

### 投稿前に確かめること
- **arXiv:2610.11399**「Estimating Great Expectations under Autoregressive Language Models with Potentials」（2026-10）：arXiv の HTTP 429 で読めなかった。題名から、層別の測り方と近い可能性。
- Critical Tokens Matter の会場（ICML 2025）。
- Ko ほかの「決定的な cliff」の定義（低エントロピーかどうかの細部）。

## 追記（2026-10-09 夜）：arXiv:2610.11399 を読んだ
- Re・Ghosh・Vieira・Cotterell「Estimating Great Expectations under Autoregressive Language Models with Potentials」（arXiv:2610.11399v1、2026-10-08、cs.AI）。arXiv がこちらに 429 を返したので、千紗が本文を貼ってくれたものを読んだ（要旨・1〜3節・4.1節の途中まで）。
- 内容：言語モデルのもとでの期待値 E[f(Y)] を、サンプリングのついでに計算される次の語の分布を使って、分散を小さく推定する一般的な枠組み。f を接頭辞ごとの増分（potential の差）に分け、各増分を「次の語についての条件つき期待値」に置き換える。理想の potential（接頭辞のもとでの条件つき期待値）なら分散は0。制御変量として係数を最適化する版もある。応用はエントロピー・KL などの損失、n-gram の数、透かしの検出確率、重要度サンプリング。
- 私たちとの関係：層別の落ち幅 d_s は、「位置 t の最初の1語が1位の語かどうか」を、確率 p₁ で正確に重みづけて平均する。これは、この論文の考え方（次の語についての期待値を、既知の確率で正確にとる）を、1つの位置・2つの層に当てはめた場合に近い。エントロピーと分かれ道の語の関係は扱っていないので、主張の先取りではない。
- 論文では §2（層別の落ち幅の段落）と貢献3で、同時期の関連研究として引用した。
