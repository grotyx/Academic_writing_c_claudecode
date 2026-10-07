<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.png">
    <img src="assets/logo.png" width="220" alt="manuwright, the careful senior author">
  </picture>
</p>

<h1 align="center">manuwright</h1>

<p align="center">
  <em>登録していない論文は、決して引用させない人。</em>
</p>

<p align="center">
  <a href="https://github.com/grotyx/Academic_writing_c_claudecode/actions/workflows/tests.yml"><img src="https://img.shields.io/github/actions/workflow/status/grotyx/Academic_writing_c_claudecode/tests.yml?style=flat-square&color=111111&label=tests" alt="Tests"></a>
  <img src="https://img.shields.io/github/v/tag/grotyx/Academic_writing_c_claudecode?style=flat-square&color=111111&label=release" alt="Release">
  <img src="https://img.shields.io/badge/python-3.10%2B-111111?style=flat-square" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/works%20with-5%20agents-111111?style=flat-square" alt="Works with 5 agents">
  <img src="https://img.shields.io/badge/license-CC%20BY%204.0-111111?style=flat-square" alt="CC BY 4.0">
</p>

<p align="center">
  <strong>計画が先 &middot; 引用はすべて登録済みの根拠から &middot; 数値はすべてデータから &middot; 投稿前にゲート</strong><br>
  <sub>AI エージェント向けの医学論文執筆ワークフロー。Claude Code、Codex、Antigravity、opencode、Muse が 1 つの検証エンジンを共有。</sub>
</p>

<p align="center">
  <sub><a href="README.md">English</a> &middot; <a href="README.ko.md">한국어</a> &middot; <a href="README.zh.md">中文</a></sub>
</p>

---

どの研究室にも一人はいる、あの先輩著者を思い浮かべてほしい。ペンを手に草稿を読む。一文に丸をつけて静かに尋ねる。*「これはどの論文に書いてある？」* 数値に丸をつける。*「どの表？」* 彼が署名するまで、何も研究室の外には出ない。

manuwright は、その人を AI エージェントの中に入れる。

## 導入前 / 導入後

計画が固まる前に、エージェントに Results を書かせたとする。

manuwright がなければ、エージェントは滑らかな文章を書き、もっともらしいが存在しない論文を引用し、読んでもいない平均値を丸めて書き込む。

manuwright があれば：

```text
BLOCKED by workflow gate (Rule 8): drafts/draft_plan.md has not been approved.
Create the draft plan first, get author approval, then draft sections.
```

計画が承認された後も、すべての主張はチェッカーを通過しなければならない。

```text
$ manuwright citations drafts/03_introduction.md
GATE FAIL
citation: EVID:smith_2021
reason: citation id not found in knowledge/evidence.md

$ manuwright numbers drafts/05_results.md
GATE FAIL
number: 54.3
reason: number not found in results CSV files
```

## 仕組み

```text
 evidence.md   ┐
 results/*.csv ┼──▶ approved plan ──▶ draft ──▶ gates ──▶ QC ×3 ──▶ signed build
 style spec    ┘                                  ├ citations
                          ▲                       ├ numbers
                    hooks block                   └ semantic review (independent)
                    writes without it
```

| 保証すること | 強制する場所 |
|---|---|
| 承認済み draft plan の前にセクションを、承認済み analysis plan の前に解析コードを書けない | エージェントの hook（Claude Code、Codex）と `manuwright verify` |
| すべての `[EVID:id]` が検証済みの出典として `knowledge/evidence.md` に登録されている | `manuwright citations` |
| 報告するすべての数値が `results/*.csv` に存在する | `manuwright numbers` と result binding |
| 出典・計画・エンジンが変わるとレビューは stale になる | すべての記録に sha256 スナップショット |
| 投稿には人の署名、AI 使用の開示、完了したチェックリストが必要 | `manuwright verify --profile submission` |
| 文章がチャットボットではなく high-impact 臨床誌のように読める | 学術文体モード: 草稿ごとのスタイルカード、編集ごとの文章チェック（`strict` はブロック） |

エンジンは承認やレビューを作り出さない。人が下した判断を記録するだけである。

## 学術文体モード

手元でモデルをファインチューニングすることはできないため、manuwright は書くたびに次善の策をとる。書き手の前に適切な例文と測定済みの目標値を置き、書かれた文章を検査する。

- **セクションカード。** 各セクション（title、abstract、introduction、methods、results、discussion、conclusion）に、修辞構造（moves）、規則、表現集（phrasebank）、high-impact 臨床誌の文体で書いた模範段落をまとめたカードがある。コアカードは毎セッション開始時に読み込まれ、セクションカードはそのセクションの執筆を頼んだとき（「Discussion を書いて」など）または `manuwright style card <section>` で読み込まれる。
- **推測ではなく測定。** カードの目標値は、2019〜2022 年（生成 AI 以前）の JAMA Surgery、JAMA Network Open、Lancet、BMJ、Nature の公開ライセンス原著 33 本から測定した：セクションごとの文長と受動態の割合、動詞・接続語の頻度、複数誌に共通する表現。配布するのは数値だけで（`docs/academic_style/reference_profile.json`）、論文本文は GitHub に置かない。例："showed" は "demonstrated" の約 5 倍、"used" は 345 回、"utilized" は 1 回だった。
- **常に文脈の中に。** カードはセッション開始時と会話圧縮後に再注入され、サブエージェントにも渡り、論文フォルダではプロンプトごとに 1 行で再確認される。チャットで切り替えられる："academic mode strict" など。
- **自分のコーパス。** `manuwright style learn <論文>` が良い論文の集まり（自分の論文、分野の landmark 論文、投稿先誌の最近の論文。PDF・DOCX・MD・TXT）をセクションごとに測定する：文長、受動態の割合、hedging、よく使う表現、文頭パターン、模範段落。以後すべてのカードにこの目標値と段落が加わる。プロファイルは個人ライブラリにのみ保存され、論文フォルダにはコピーされない。
- **文章チェック。** 原稿セクションを編集するたびに、AI 的な言い回し（delve、pivotal、"it is worth noting"、文末の ", highlighting ..."）、短縮形、本文の太字、長すぎる文、統計値のない "significant" などを行番号付きで報告する。`manuwright mode strict` は書き直すまで書き込み自体をブロックし、`manuwright mode off` でモードを無効にする。
- **書き直しても事実は不変。** `manuwright style preserve old.md new.md` は、文体の書き直しで `[EVID:id]`、数値、*p* 値、Table/Figure 参照が一つでも変わると失敗する。`/style-pass` がセクションごとに実行する。

## インストール

方法は 2 つ、エンジンは 1 つ。どちらかを選ぶ。

**A. テンプレート（インストール不要）。** リポジトリを clone して、その中で書く。Claude Code は `.claude/` を、Codex と Gemini は `AGENTS.md` と `GEMINI.md` を読む。

```sh
git clone https://github.com/grotyx/Academic_writing_c_claudecode my-paper
```

**B. インストール型エンジン。** すべての論文で使う CLI 1 つと、エージェントごとのアダプター。

```sh
uv tool install git+https://github.com/grotyx/Academic_writing_c_claudecode@v1.9.0
manuwright agents install --dry-run     # preview, then run without --dry-run
manuwright setup                        # models, reviewers, Word style, updates, Obsidian
manuwright init my-paper
manuwright target                      # inside the paper: target journal + Word style
```

| エージェント | `manuwright agents install` が追加するもの | plan-first の強制 |
|---|---|---|
| Claude Code | plugin `manuwright@manuwright`：skill + hook | hook が書き込みを止める |
| Codex | plugin `manuwright@manuwright`：skill + hook（初回に一度信頼） | hook が `apply_patch` を止める |
| Antigravity（`agy`） | skill 入りの plugin | `manuwright verify` |
| opencode | `~/.config/opencode/skills` の skill | `manuwright verify` |
| Muse | ユーザー skill | `manuwright verify` |

**更新。** `manuwright update` が最新リリースをインストールし、続けてエージェントアダプターも更新する（`manuwright agents update`、省略は `--no-agents`）。続けて登録済みのすべての論文のエージェント規則を更新するか尋ねる（`manuwright init --refresh-rules --all`、AGENTS/CLAUDE/GEMINI.md だけを変更し .bak を保存）。`manuwright check` はバージョン、エージェントごとのプラグイン、メインモデル、OpenRouter キー、自動更新、論文の規則が最新かを 1 画面で示し、✗ ごとに直すコマンドを表示する。`manuwright config set auto-update on` で patch の自動更新を有効にできる。1 日 1 回確認し、論文の現在のレビューを無効にする更新は適用しない。Windows（uv インストール）では実行中の `manuwright.exe` を置き換えられないため、`manuwright update` は新しい PowerShell ウィンドウに貼り付ける 1 行（`uv tool install --force ...; if ($?) { manuwright agents update }`）を表示する。テンプレート利用者は `git pull`、または[移行ガイド](docs/migration_guide.md)を参照。

**アンインストール。** `claude plugin uninstall manuwright@manuwright`、`codex plugin remove manuwright@manuwright`、`agy plugin uninstall manuwright`、`muse skills uninstall manuwright`、最後に `uv tool uninstall manuwright`。

## コマンド

| コマンド | 内容 |
|---|---|
| `manuwright init [folder]` | 論文フォルダを開始：manifest、計画テンプレート（未承認）、根拠リスト、エージェント規則 |
| `manuwright rules [keyword]` | ワークフロー規則の全体または 1 節を表示 |
| `manuwright check` | バージョン・エージェントプラグイン・メインモデル・キー・自動更新・更新が必要な論文をまとめて点検し、修正コマンドを表示 |
| `manuwright mode academic\|strict\|off` | 学術文体モード: スタイルカード + 編集ごとの文章チェック。`strict` は AI 的な文章の書き込みをブロック |
| `manuwright style learn <論文>` / `style card <section>` | 良い論文のコーパス（自分の文体、landmark、投稿先誌）を測定 / セクションのスタイルカードを表示 |
| `manuwright guide [name ...]` | 規則が引用するエンジンのガイド（`docs/<name>.md`）の一覧または内容を表示 |
| `manuwright verify --project project.json --profile draft\|revision\|submission` | その段階のすべての検査を実行 |
| `manuwright citations \| numbers \| abstract \| crossrefs \| lint ...` | 1 つのファイルに 1 つのチェッカーを実行 |
| `manuwright gate` / `verify-all` | フェーズゲートの記録を実際の検査結果と照合 |
| `manuwright search "<query>"` | PubMed を検索し根拠エントリを表示 |
| `manuwright packet` / `build` | ローカルのレビュー packet / ゲート通過が必要な DOCX ビルド |
| `manuwright update`、`agents install\|update`、`config` | リリース、エージェントアダプター、自動更新、main モデルとレビュアーのモデル |
| `manuwright obsidian status\|connect`、`evidence import-obsidian <citekey>` | 任意（推奨）：Obsidian「[Academic Paper Citation Manager](https://github.com/grotyx/rag-obsidian)」ライブラリを全エージェントに接続；vault の文献を `evidence.md` へ取り込み |

テンプレートには Claude Code 用の slash command も含まれる：`/verify`、`/search-evidence`、`/import-doi`、`/style-pass`、`/verify-claims`、`/suggest-citation`、`/cite-stance`、`/evidence-table`、`/paper-debate`、`/critical-review`、`/editor-review`。

## Obsidian ライブラリ（任意・推奨）

文献を Obsidian で管理しているなら、同じ作者のプラグイン **[Academic Paper Citation Manager](https://github.com/grotyx/rag-obsidian)**（[Obsidian コミュニティプラグイン](https://community.obsidian.md/plugins/academic-paper-citation-manager)）を併用してください。PubMed 取り込み、AI 要約、MeSH タグ、`[@citekey]` 引用を備え、ノートそのものがデータベースです。このプラグインの MCP サーバーにより、すべてのエージェントが執筆中にライブラリを検索できます。

```sh
manuwright obsidian install          # plugin into a vault, offers MCP access (skip if installed)
manuwright obsidian connect          # register its MCP server (rag-obsidian) with each agent
manuwright evidence import-obsidian <citekey>
```

vault は文献を探す場所で、引用できるのは `knowledge/evidence.md` に登録した項目だけです。取り込んだノートは CSL フィールドが引用情報に、プラグインの AI 要約が要約欄になり、`[EVID:<citekey>]` として引用し、全文を読むまで `abstract-only` のままです。エージェントが使う間は Obsidian を開き、MCP アクセスをオンにしておいてください。手順：[マニュアル 3b 節](docs/manual.md#3b-your-obsidian-library-optional-recommended)（英語）。

<p align="center"><img src="docs/images/manual/43_obsidian_import_evidence.png" width="720" alt="Obsidian ライブラリの文献を evidence.md に取り込む"></p>

## ワークフロー

| フェーズ | 人とエージェントが行うこと | ゲート |
|---|---|---|
| 1 準備 | テーマ、投稿先、研究デザイン；参考文献の登録 | `evidence.md` で出典を検証 |
| 2 解析 | 解析計画、スクリプト、結果 CSV、表 | スクリプト前に計画を承認 |
| 3 原稿計画 | キーメッセージ、主張と引用の対応、構成 | セクション前に計画を承認 |
| 4 執筆 | Methods、Results、Introduction、Discussion、Conclusion、Abstract | セクションごとに引用・数値・論理・制約を検査 |
| 5 文体 | 自分の論文 exemplar に基づく投稿先の文体 | 測定可能な文体指標 |
| 6 QC | 最低 3 回；チェックリスト（CONSORT、STROBE、PRISMA、CARE） | `review/qc_log.md` に記録 |
| 7 仕上げ | DOCX 原稿、タイトルページ、表 | submission profile PASS + 人の署名 |
| 8 改訂 | 回答書、改訂セクション | すべての変更主張とすべての査読コメントを検査 |

規則の全文：[WORKFLOW.md](WORKFLOW.md)。以前の README にあった内容（機能、プロジェクト構成、文書一覧）：[docs/guide/overview.ja.md](docs/guide/overview.ja.md)。

## FAQ

**論文を代わりに書いてくれる？** 決められた規則の中でエージェントが草稿を書くのを手伝う。メッセージを決め、計画を承認し、署名するのは著者である。人と共著者によるレビューは引き続き必須。

**自分の PC の外に出るものはある？** 検査はすべてローカルで動く。他のモデルに文章を送ること（外部レビュー、PubMed 検索）は、そのコマンドを実行したときだけ起こる。

**実際の原稿はどこに置く？** 非公開のフォルダやリポジトリに置く。このテンプレートの公開 clone には置かない。`manuwright init` がそのフォルダを作る。

**なぜ「manuwright」？** manuscript + *wright*。wright は「作る人」を意味する古い言葉（playwright 劇作家、shipwright 船大工）。原稿を丁寧に組み上げる人。

## ドキュメント

[ユーザーマニュアル（英語）](docs/manual.md) &middot; [Harness ガイド](docs/harness_guide.md) &middot; [Workflow reference](docs/workflow_reference.md) &middot; [検証プロトコル](docs/verification_protocol.md) &middot; [執筆ガイド](docs/writing_guide.md) &middot; [QC ガイド](docs/qc_guide.md) &middot; [配布設計](docs/distribution_plan.md) &middot; [変更履歴](CHANGELOG.ja.md)

## 著者

**Professor Sang-Min Park, M.D., Ph.D.**, Department of Orthopaedic Surgery, Seoul National University Bundang Hospital, Seoul National University College of Medicine. <https://sangmin.me/>

## ライセンス

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。Copyright (c) 2026 Sang-Min Park, Seoul National University Bundang Hospital。出典を明記すれば、どのような目的でも共有・改変できる。
