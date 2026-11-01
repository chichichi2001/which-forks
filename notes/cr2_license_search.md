# GSM-Infinite のライセンスの再調査（G-L の下調べ）

PRIVATE UNPUBLISHED RESEARCH.

- 2026-10-13 15:20 JST、オーナーの「Issue とかメールを送る前に、どっかにライセンスが書いてないかもう一回探してきて」を受けて調べた。
- 見たのは、ライセンスの表示・メタデータだけ。データの中身は開いていない。

## 調べた場所と結果

| 場所 | 結果 |
|---|---|
| GitHub `Infini-AI-Lab/gsm_infinite`（全 53 コミットの履歴） | `LICENSE` のファイルは、どのコミットにも一度も存在しない（消された記録もない） |
| 同 `pyproject.toml` | `license = {file = "LICENSE"}` と書いてあるが、その `LICENSE` のファイルがない |
| 同 `README.md` | MIT のバッジと「This project is licensed under the MIT License」の節が、**コメントアウト**されている（表示されない）。MIT にするつもりだった跡に見えるが、有効な宣言ではない |
| 同 `index.html`（プロジェクトのウェブサイト） | CC BY-SA 4.0 の表示があるが、対象は**ウェブサイト**（ひな形の決まり文句）で、データ・コードではない |
| Hugging Face のデータ（`gsm_infinite_hard_0`・`medium_0`・`symbolic_0`・`symbolic_example_0`） | カードの `license` の欄も `license:` のタグもない。README にも記載なし |
| Hugging Face のリーダーボード（Space） | ライセンスの記載なし |
| arXiv の論文（2502.05252） | 論文は CC BY 4.0。データ・コードのライセンスについての記述はない |
| 第三者のまとめサイト（SOTA2 など） | 記載なし |

## 結論

- データにもコードにも、**有効なライセンスの表示は見つからなかった**。README のコメントアウトから MIT の意図はうかがえるが、それを根拠に「MIT で使える」とは扱えない。
- 計画の G-L のとおり、作者に確かめるまで送信は保留。
- 問い合わせは GitHub の Issue が自然：`pyproject.toml` が参照している `LICENSE` のファイルがないことを伝え、追加をお願いし、あわせて HF のデータにも同じライセンスが当てはまるかを聞く。

## 問い合わせの記録

- 2026-10-13 15:27 JST ごろ：オーナーが GitHub `Infini-AI-Lab/gsm_infinite` に Issue を立てた（種類：Task。タイトル「Missing LICENSE file (pyproject.toml references it)」）。
  - お願いは 2 つ：LICENSE のファイルを足すこと、HF のデータにも同じライセンスが当てはまるかの確認。
  - 使い方の説明：非商用の研究で、数百問を商用の LLM の API に送って評価し、公開するのは数字だけ（問題文は出さない）、論文を引用する。
  - Issue の番号・リンク：未記録（このセッションからはリポジトリの Issue の一覧を読めなかった。分かったら書き足す）。
- 返事が来るまで、CR-2 の送信（G0 の送信・G1・G2）は保留（計画の G-L）。
- 2026-10-27 ごろに返事を確かめ、返事がなければ、論文の筆頭著者か責任著者にメールで Issue を見てもらうようお願いする。
