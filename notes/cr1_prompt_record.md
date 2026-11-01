# CR-1 頼み方の文の固定（G1 の前の記録）

PRIVATE UNPUBLISHED RESEARCH.

- 凍結した計画 `notes/cr1_claude_resample_gate.md` の定義 2 は、頼み方の中身（「短く考えを書いてから、最後の行に `#### <数>` の形で答えを書く」）だけを決めていて、正確な英文は書いていなかった。G1 で API を呼ぶ前に、ここで固定する。決まりそのものは変えていない。
- 決めた日時：2026-10-12 18:41 JST。オーナーが 3 つの案から案 A を選んだ（「Aでお願い！」）。
- G0 の結果（`notes/cr1_g0_result.md`）は見たが、問題（ベンチマーク）の応答はまだ 1 つも見ていない。

## 頼み方（利用者の発言。システムプロンプトはなし）

```
Solve the following math problem. Think step by step briefly, then write the final line as "#### <number>".

{question}
```

- `{question}` には GSM-Symbolic の問題文をそのまま入れる（前後に何も足さない）。
- コード：`pork/cr1_requests.py` の `PROMPT_TEMPLATE`。テンプレートの文字列（UTF-8）の sha256：`c2e04c90f40c8be8298232ebe968679f8c9d16535a351af5ba7a4daaba834051`。
- 選んだ理由：DP3〜DP7 の頼み方（「Solve the following math problem. Think step by step, then write the final line as "Final answer: <number>".」）と同じ形にそろえ、答えの印を `####` に替え、定義 4 の長さ（答えより前の単位 30〜80 個）に入りやすいよう「briefly」を足した。

## 呼び出しの設定（定義 2・3・6・7。G0 で決まったものを含む）

- モデル：`claude-haiku-4-5-20251001`。思考（extended thinking）は使わない。最大 400 トークン。
- SDK：`anthropic` 1.13.0（G0 で入った版）。G1 以降のノートブックはこの版を入れる。
- 土台の道（定義 3）：`extra_body={"temperature": 0}`（G0 で受け付けられた）。
- 引き直し（定義 7）：温度・top_p を指定しない。プリフィル P_c は最後の assistant の発言（c = 0 はプリフィルなし）。P_c の末尾は空白でない（定義 6。G0 で末尾の空白は 400 で拒否された）。

## G1 の進め方（計画の定義 1・4 と G1 のとおり）

- 段2 の候補の一覧（ハッシュ `b6f6375a…`）を作り直して一致を確かめてから呼ぶ。
- テンプレートごとに、候補を順に土台の道を作り、定義 4（答えが読める・答えより前の単位 30〜80 個・`stop_reason` が `end_turn`）を満たす最初の 1 問を使う。満たしたら、そのテンプレートの残りの候補は呼ばない。
- テンプレートどうしは並べて呼ぶ（結果はテンプレートごとに決まり、並べる順には関係しない）。
- API のエラーは待って呼び直す（最大 5 回）。それでも失敗したら、黙って「外れ」に数えず、ノートブックを止める（あとで続きから回す）。
- G1 の費用の見張り：$3 を超えそうなら止める（見込みは $0.5 前後）。
- N ≥ 70 なら G1b へ。G1b の費用の見込みと、テンプレートを外すかどうかは、計画の式のとおり（`pork/cr1_requests.py` の `g1b_estimate`・`g1b_select`。上限は［決定4］の $90）。
- 保存：問題文・応答の文字列は Drive の非公開のファイルだけに置き、画面・通知・リポジトリには出さない（数・ID・ハッシュだけ）。
