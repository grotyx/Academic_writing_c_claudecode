🇺🇸 [English](README.md) | 🇰🇷 [한국어](README.ko.md) | 🇯🇵 [日本語](README.ja.md) | 🇨🇳 [中文](README.zh.md)

# Claude を活用した医学学術論文執筆ワークフロー

Claude AI を活用した医学学術論文執筆のための体系的なワークフローシステムです。

## バージョン

**v1.0.1** (2026-06-20)

---

## 概要

本プロジェクトは、Claude AI の支援による医学学術論文執筆のための包括的なフレームワークを提供します：

- **体系的なプロジェクト構成** — 原稿、データ、参考文献の管理
- **マルチ論文プロジェクト対応** — 論文ごとのサブフォルダ整理
- **ファイルバージョン管理システム** — 日付ベースのデフォルト、_v1、_REV1 スタイル
- **Revision ワークフロー** — 専用 revision フォルダとファイル命名規則
- **専門家チームシミュレーション** — 臨床専門家、方法論専門家、統計学者、編集者
- **統計分析ワークフロー** — Python スクリプトの自動生成
- **品質管理手順** — 最低3ラウンドの検証（6ラウンド推奨）＋ Revision QC 再実行ワークフロー
- **研究タイプ別チェックリスト** — STROBE、CONSORT、PRISMA、CARE 等
- **学術執筆スタイルシステム** — Style Reference Tables（Voice/Tense、Transition、Verb Upgrades、Common Corrections、Statistical Notation、Hedging）＋ Writing Principles（Clarity/Conciseness/Objectivity/Consistency）
- **引用品質管理** — Claim→Citation Mapping（執筆前に主要 claim と根拠文献を対応付け）
- **Style アンカーライブラリ**（`Style/`）— own、landmark、target-journal アンカーで用語・トーン・論証構造を管理
- **用語 registry**（`Style/terminology.md`）— preferred/forbidden 用語、定義、使用 context
- **Drafting protocol**（`docs/drafting_protocol.md`）— outline → evidence-bound draft → style pass → QC
- **Manuscript linting**（`scripts/lint_manuscript.py`）— 用語、placeholder、過大主張、セクション別違反の自動確認
- **Citation evidence checking**（`scripts/check_citations.py`）— `[EVID:id]` タグを `knowledge/evidence.md` と照合
- **Data number checking**（`scripts/check_numbers.py`）— 原稿・表の数値を `results/*.csv` と照合
- **Phase gate ledger checking**（`scripts/check_gate.py`）— `review/gates/*.GATE.md` に必要な PASS がない場合は進行を停止
- **Gate freshness / provenance**（`scripts/check_gate.py --verify-hash`）— PASS 時に検証済み成果物（および evidence/results）の sha256 を記録し、その後の編集でゲートを **stale** にして再検証を強制 — parallel-verifier の抜け穴を塞ぐ
- **Revision claim checking**（`scripts/check_revision_claims.py`）— response letter の `[CHANGE]` claim を revised manuscript と照合
- **LLM verifier prompt templates**（`docs/verifier_prompt_templates.md`）— constraint、semantic citation、data、logic/redundancy、revision-alignment の検証 prompt/schema
- **Author response DOCX generation**（`scripts/compile_response_docx.py`）— DOCX-ready Markdown を `Author_response_220803_Final.docx` house style に変換
- **Author response Markdown template**（`docs/response_letter_template.md`）— reviewer response、修正箇所、machine-readable `[CHANGE]` block を整合
- **PubMed 検索ツール** — 内蔵 Python スクリプト（MCP・外部パッケージ不要）
- **共著者ディベート**（`/paper-debate`）— 執筆前の Claude–Codex 議論で分析計画・draft plan・論証構造・査読者応答を設計（`docs/debate_protocol.md`）
- **マルチモデル批判的レビュー**（`/critical-review`）— 執筆後に Claude サブエージェント・Codex・OpenRouter モデルで senior reviewer/editor レベルの敵対的レビュー、合意度 × 重大度で順位付け（`docs/critical_review_protocol.md`）
- **AI-Draft De-bloat** — AI の痕跡（表層的な `-ing` 分析・AI 語彙・signposting）を除去し、disclosure を保ちつつ自然に読ませる writing-guide パス（`docs/writing_guide.md`）
- **スラッシュコマンド** — エビデンス登録（`/search-evidence`、`/import-doi`）

---

## プロジェクト構成

```
project/
├── CLAUDE.md                     # コアルール・設定
├── AGENTS.MD                     # agent 起動ルール；CLAUDE.md を source of truth とする
├── README.md                     # 英語版 README
├── docs/                         # 参照ガイド
│   ├── writing_guide.md          # セクション別執筆ガイド
│   ├── drafting_protocol.md      # 必須 drafting sequence
│   ├── section_templates.md      # セクション別 sentence patterns
│   ├── expert_roles.md           # 専門家チームの役割と責任
│   ├── checklist_guide.md        # 研究タイプ別チェックリスト
│   ├── qc_guide.md               # 品質管理手順
│   ├── verification_protocol.md  # 検証ゲート・4 Verifier・自律ループ・ゲート台帳
│   ├── verifier_prompt_templates.md  # LLM verifier prompts and output schema
│   ├── statistical_analysis_guide.md  # 統計分析ガイド
│   ├── evidence_guide.md         # エビデンス作成ガイド
│   ├── revision_guide.md        # リビジョン・レビュアー対応ガイド
│   ├── response_letter_template.md  # DOCX-ready author response template
│   ├── figure_guide.md          # Figure作成ガイド
│   ├── docx_guide.md            # DOCX 変換ガイド
│   └── draft_plan_template.md    # Draft plan template
├── knowledge/                    # 参考資料
│   ├── evidence.md               # 参考文献要約集
│   ├── pdf/                      # 原本 PDF ファイル（gitignored, local only）
│   └── summaries/                # 個別論文の詳細要約
├── Style/                        # 参考文献とは分離した writing-style アンカー
│   ├── PDF/                      # style analysis source PDFs（gitignored, local only）
│   ├── own/                      # 自分の論文 style anchors
│   ├── landmark/                 # 論証・framing anchors
│   ├── target_journal/           # journal house-style anchors
│   ├── style_guide.md            # style anchor workflow and extraction rules
│   └── terminology.md            # preferred/forbidden terminology registry
├── data/                         # 統計分析
│   ├── raw_data.csv              # 元データセット
│   ├── analysis_plan.md          # 分析計画（分析前に必須作成）
│   └── py/                       # Python 分析スクリプト
├── scripts/                      # ユーティリティスクリプト
│   ├── lint_manuscript.py        # manuscript terminology/style lint checks
│   ├── check_citations.py        # evidence citation gate
│   ├── check_numbers.py          # results CSV number gate
│   ├── check_gate.py             # phase gate ledger check
│   ├── check_revision_claims.py  # revision claim gate
│   ├── compile_response_docx.py  # Author response DOCX compiler
│   ├── search_pubmed.py          # PubMed 検索ツール（外部依存なし）
│   ├── critical_review.py        # OpenRouter マルチモデル敵対的レビュー呼び出し
│   ├── critical_models.txt       # OpenRouter モデルリスト（外部化）
│   └── critical_prompts/         # 敵対的プロンプト単一正本（manuscript.txt, response.txt）
├── tests/                        # 検証スクリプト用 pytest スイート
├── results/                      # 分析結果
├── drafts/                       # 原稿セクション、表、図
│   ├── draft_plan.md             # 原稿構成計画（執筆前必須）
│   ├── table_*.md
│   └── figures/
├── review/                       # QC 文書
│   ├── qc_log.md
│   └── gates/                    # 検証ゲート台帳 (phase_NN_*.GATE.md)
└── output/                       # 最終原稿
    ├── title_page_YYMMDD.docx
    ├── manuscript_YYMMDD.docx
    └── table_N_YYMMDD.docx
```

---

## クイックスタート

1. **設定**：`CLAUDE.md` に研究テーマ、対象ジャーナル、研究デザインを入力します
2. **参考文献**：`/search-evidence [クエリ]` または `python3 scripts/search_pubmed.py` で PubMed を検索し、`knowledge/evidence.md` に登録します
3. **データ分析**：`data/` フォルダにデータを配置 → `analysis_plan.md` 作成（必須）→ 統計分析実行
4. **原稿計画**：`docs/draft_plan_template.md` を `drafts/draft_plan.md` にコピーし、Claim→Citation Mapping を含む10項目を作成（Opus 推奨）
5. **執筆**：`docs/drafting_protocol.md` に従い、推奨順序でセクションを作成
6. **検証ゲート**：citation、number、phase-gate、revision-claim checker を実行し、`review/gates/` に PASS を記録します
7. **Revision response**：レビュアー回答が必要な場合は `docs/response_letter_template.md` で作成し、`scripts/compile_response_docx.py` で DOCX に変換します
8. **品質管理**：投稿前に最低3ラウンドの QC を実施します（6ラウンド推奨）
9. **最終化**：原稿を DOCX にコンパイルします（`docs/docx_guide.md` 参照）

---

## 主な機能

### 専門家チームシミュレーション
- **Dr. Researcher A**：臨床的視点（Introduction、Discussion）
- **Dr. Researcher B**：方法論（Methods、Results、Tables）
- **Dr. Statistician**：統計検証、節約原則、MCID/NNT 評価
- **Dr. Editor**：最終校正、一貫性チェック

### 執筆前必須計画（Planning Before Writing）

- **分析計画**（`data/analysis_plan.md`）：統計分析前に必須 — 研究課題、評価変数、検定法選択を定義
- **原稿計画**（`drafts/draft_plan.md`）：セクション執筆前に必須 — キーメッセージ、トーン/ボイス、必須参考文献、エビデンスギャップ、Table/Figure 計画、セクション別アウトライン
- 両計画ともユーザー承認後に次フェーズへ進行
- マルチ論文の場合、論文ごとに個別計画を作成

### フェーズ別モデル選択（Model Selection by Phase）

- **Opus 推奨**：Analysis Plan、Draft Plan、Revision — 戦略的判断が必要なフェーズ
- **Sonnet デフォルト（Opus 可能なら使用）**：執筆、Style Polish、QC — 計画ベースの実行
- 核心原則：「Plan は Opus で → 執筆は Sonnet でも OK」

### 重複防止
- 三重重複の回避（Results 本文 + Table + Figure）
- Table vs Figure 判断のための明確なガイドライン
- 標準テーブル構成（Table 1：人口統計、Table 2：主要結果）

### 統計分析ガイド（v0.3.0）
- 統計的節約原則（Statistical Parsimony）— RCT Table 1 の p 値省略
- 分析階層 — Primary > Secondary > Exploratory
- 臨床的有意性 — Effect size、MCID、NNT
- サブグループ分析ルール — Interaction test 必須
- 非有意結果の報告ガイド

### 品質管理（6ラウンド）
- Round 1：数値の一貫性
- Round 2：参考文献の検証（+ 出現順番号、プレースホルダー検出、書誌形式の一貫性、引用分布）
- Round 3：論理的フロー
- Round 4：用語・略語・時制の一貫性
- Round 5：統計的品質
- Round 6：批判的レビュー（過大主張、論理的誤謬、バイアス、一般化可能性）

### 検証ハーネス

このハーネスは、決定論的 checker と制約付き LLM verifier prompt を組み合わせます：

- `scripts/check_citations.py`：すべての `[EVID:id]` citation を `knowledge/evidence.md` と照合し、未確認または不明な evidence を失敗として扱います。
- `scripts/check_numbers.py`：原稿と表の数値を `results/*.csv` と照合します。
- `scripts/check_gate.py`：phase gate ledger に `status: PASS` と必要な check があるか確認します。
- `scripts/check_revision_claims.py`：reviewer response の `[CHANGE]` block を revised manuscript files と照合します。
- `docs/verifier_prompt_templates.md`：semantic support、logic、redundancy、revision-response alignment の検証 prompt/schema を提供します。

### 共著者コラボレーション（Co-author Collaboration, NEW in v0.9.3）

執筆プロセスを挟み込む、相補的な 2 つの Codex/マルチモデル機能です：

- **`/paper-debate <topic>`** — 執筆の *前*。Claude と Codex が共著者として、分析アプローチ、draft-plan のキーメッセージ、論証構造、査読者応答戦略を、上限付きのラウンド（合意上限 3）で議論します。ディベートログは `review/debates/` に保存され、合意された結論が次の産出ステップに供給されます。Codex が利用できない場合は Claude 単独にフォールバックします。`docs/debate_protocol.md` を参照。
- **`/critical-review <target>`** — 執筆の *後*。完成した原稿（または response letter）を、新しい Claude サブエージェント・Codex・OpenRouter モデル（既定 `minimax/minimax-m3`、`z-ai/glm-5.2`）の任意の組み合わせで並行して攻撃します。各レビュアーは **senior peer-reviewer / editor-in-chief レベル** でプロンプトされ、表層的欠陥を越えて設計の妥当性・データが結論を支持するか・出版価値まで踏み込みます。指摘は統合され、**合意度 × 重大度**（Critical / Important / Minor）で順位付けされ、`review/critical/` に保存されます。`docs/critical_review_protocol.md` を参照。

敵対的プロンプトは `scripts/critical_prompts/`（`manuscript.txt`、`response.txt`）の単一正本として存在します。OpenRouter スクリプト・Claude サブエージェント・Codex はすべて同じファイルを読み込みます。OpenRouter アクセスには `OPENROUTER_API_KEY`（`.claude/settings.local.json` に設定、gitignored）を使用します。キーが無い場合は OpenRouter を skip し、他のレビュアーで続行します。

### AI-Draft De-bloat（NEW in v0.9.3）

`docs/writing_guide.md` のパス（AI が執筆した draft に対して Phase 5 で適用）で、AI 文章の痕跡 — 中身のない `-ing`「表層分析」節、AI が好む語彙、過剰な signposting — を除去します。一方で、正当に衝突するパターン（必要な hedging、copula、受動態）は明示的に **除外** します。AI の関与は引き続き開示されます。これは開示された支援が冗長で退屈に読まれないようにするだけのものです。

### 検証の堅牢化（Verification Hardening, NEW in v1.0.0）

「superpowers」スキルフレームワークから取り入れた改善で、検証ゲートに焦点を当てています：

- **Parallel verifiers + Constraint-first.** 4 つのセクションゲート verifier（Constraint / Citation / Data / Logic）は、凍結された成果物に対して並行してディスパッチされます。成果物は検証の途中で編集されず、FAIL 時には Constraint（仕様適合性）の指摘を最優先で修正します。`docs/verification_protocol.md`（v0.2.0）を参照。
- **Gate freshness / provenance**（`scripts/check_gate.py`）。PASS 時にゲート台帳へ検証済み成果物の sha256 を記録します（citation・numbers を伴うゲートでは `evidence` / `results` も；revision では必須）。`check_gate.py --verify-hash LABEL=PATH` は再ハッシュを行い、PASS 以降にファイルが変更されていればゲートを **stale** として失敗させます — PASS 後の編集が再チェックを静かにすり抜ける抜け穴を塞ぎます。`--compute-hash PATH` は provenance フィールドを埋めます。ツールレベルでは opt-in、文書化されたゲートコマンドでは標準で有効です。
- **STOP signals.** CLAUDE.md の anti-rationalization テーブルが、verifier では捉えられない人間レベルのショートカット（「この数値はたぶん大丈夫」→ CSV を確認；「もう PASS した」→ 変更された成果物は stale）を捕捉します。
- **Socratic draft-plan brainstorming.** `docs/draft_plan_template.md` の「Step 0」が、計画を埋める前に論文の意図を一度に 1 問ずつ研ぎ澄まします — `/paper-debate` とは別物で、その R0 準備として供給されます。
- **Reviewer-response triage.** `docs/revision_guide.md` は各査読コメントに accept / partial / rebut の姿勢を割り当て、`[CHANGE]` マーカーと ghost-revision ゲートに対応付けます。
- **Command `use-when` guidance.** 各 `.claude/commands/*.md` が、それを起動すべき状況を明示するようになりました。

### Author Response DOCX Workflow

Reviewer response は `docs/response_letter_template.md` 形式で作成し、各原稿修正は `[CHANGE]` block として記録します。最終 response letter は次のコマンドでコンパイルします：

```powershell
py scripts\compile_response_docx.py drafts\revision\REV1\response_letter_REV1.md
```

compiler は `Author_response_220803_Final.docx` の house style を再現します — Times New Roman 11 pt、response・位置・修正テキストの行は bold、本文は justified。この .docx ファイルをテンプレートとして読み込むことはなく、書式はコードに組み込まれています。

### PubMed 検索ツール

MCP 不要で参考文献を検索できる内蔵 Python スクリプト（`scripts/search_pubmed.py`）：

```bash
python3 scripts/search_pubmed.py search "endoscopic spine surgery"  # 検索
python3 scripts/search_pubmed.py fetch 35486828                     # PMIDで取得
python3 scripts/search_pubmed.py doi 10.1016/j.spinee.2023.01.005  # DOIで取得
python3 scripts/search_pubmed.py related 35486828                   # 関連論文
```

Claude 統合スラッシュコマンド：

- `/search-evidence [クエリ]` - 検索、選択、evidence.md に登録
- `/import-doi [doi]` - DOI から取得し evidence.md に登録

---

## ドキュメント一覧

| ドキュメント | 目的 |
|-------------|------|
| [CLAUDE.md](CLAUDE.md) | コアルールとプロジェクト設定 |
| [docs/writing_guide.md](docs/writing_guide.md) | セクション別執筆ガイド ＋ Style Reference Tables ＋ Writing Principles (4 Pillars) |
| [docs/drafting_protocol.md](docs/drafting_protocol.md) | outline → evidence-bound draft → style/QC pass の必須 drafting workflow |
| [docs/section_templates.md](docs/section_templates.md) | セクション別 paragraph function と sentence patterns |
| [docs/expert_roles.md](docs/expert_roles.md) | 専門家チームの説明 |
| [docs/checklist_guide.md](docs/checklist_guide.md) | STROBE、CONSORT、PRISMA、CARE チェックリスト |
| [docs/qc_guide.md](docs/qc_guide.md) | 品質管理手順（6ラウンド） |
| [docs/verification_protocol.md](docs/verification_protocol.md) | 検証ゲート・4 Verifier 憲章・自律修正ループ・ゲート台帳 |
| [docs/verifier_prompt_templates.md](docs/verifier_prompt_templates.md) | LLM semantic verifier prompts and structured output schema |
| [docs/statistical_analysis_guide.md](docs/statistical_analysis_guide.md) | 統計分析ガイド（節約原則、MCID、サブグループ分析） |
| [docs/evidence_guide.md](docs/evidence_guide.md) | エビデンス作成ガイド（形式、要約方法、ワークフロー） |
| [docs/revision_guide.md](docs/revision_guide.md) | レビュアー対応ガイド（回答書作成、外交的表現、QC 再実行チェックリスト） |
| [docs/response_letter_template.md](docs/response_letter_template.md) | DOCX-ready author response Markdown template |
| [docs/figure_guide.md](docs/figure_guide.md) | Figure作成ガイド（DPI、パレット、Pythonテンプレート） |
| [docs/docx_guide.md](docs/docx_guide.md) | DOCX 変換ガイド（書式、テーブルスタイル、命名規則） |
| [docs/draft_plan_template.md](docs/draft_plan_template.md) | Draft plan template — 10項目、claim→citation tables、approval checklist |
| [Style/style_guide.md](Style/style_guide.md) | Style anchor workflow、extraction framework、PDF-to-MD mirror rules |
| [Style/terminology.md](Style/terminology.md) | Preferred/forbidden terminology registry |
| [Style/own/example_YYYY_Journal_keyword.md](Style/own/example_YYYY_Journal_keyword.md) | Own-paper style-anchor template |
| [scripts/lint_manuscript.py](scripts/lint_manuscript.py) | Manuscript lint script |
| [scripts/check_citations.py](scripts/check_citations.py) | `[EVID:id]` citations を `knowledge/evidence.md` と照合 |
| [scripts/check_numbers.py](scripts/check_numbers.py) | 原稿・表の数値を `results/*.csv` と照合 |
| [scripts/check_gate.py](scripts/check_gate.py) | `review/gates/*.GATE.md` の status と必須 check を検証 |
| [scripts/check_revision_claims.py](scripts/check_revision_claims.py) | response-letter `[CHANGE]` claims を revised manuscript files と照合 |
| [scripts/compile_response_docx.py](scripts/compile_response_docx.py) | `response_letter_REV*.md` を Author_response-style DOCX に変換 |
| [scripts/search_pubmed.py](scripts/search_pubmed.py) | PubMed 検索スクリプト（NCBI E-utilities、外部パッケージ不要） |

---

## 要件

- Claude AI（Claude Code CLI または VSCode 拡張機能）
- Python 3.x（統計分析および PubMed 検索用）
- 統計分析用 Python パッケージ：pandas、numpy、scipy、statsmodels、python-docx
- PubMed 検索スクリプト（`scripts/search_pubmed.py`）は Python 標準ライブラリのみ使用（追加パッケージ不要）

---

## 著者

**朴相旻 教授, M.D., Ph.D.**

整形外科学教室、
ソウル大学校盆唐ソウル大学校病院、
ソウル大学校医科大学

https://sangmin.me/

---

## ライセンス

この著作物は**クリエイティブ・コモンズ 表示 4.0 国際ライセンス（CC BY 4.0）**の下に提供されています。

Copyright (c) 2026 Sang-Min Park, Seoul National University Bundang Hospital

### 許可される行為：
- **共有** — いかなる媒体や形式でも資料を複製・再配布できます
- **翻案** — いかなる目的でも資料のリミックス、変換、追加制作ができます

### 条件：
- **表示** — 適切なクレジットを表示し、ライセンスへのリンクを提供し、変更がある場合はその旨を示す必要があります。

[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

ライセンス全文：https://creativecommons.org/licenses/by/4.0/legalcode

---

## 変更履歴

### v1.0.1 (2026-06-20)

**リリース後の堅牢化＋圧縮ツール**

- **当日中の堅牢化（コードレビュー＋プロジェクト監査）** — `check_gate.py` の freshness 検査が、ファイル以外のパス（ディレクトリ/不存在）でクラッシュせずクリーンに失敗するようになり、相対パスをリポジトリの `ROOT` を基点に解決し、空白/プレースホルダのダイジェストを明確なメッセージで拒否し、PASS 出力に `provenance_verified` / `provenance_unverified` を報告。Phase 8 の verifier セットを整合（Logic は Draft 専用；Revision は Revision-claims ＋ Response-alignment を追加）し、ゲートコマンドに `--require-check constraint` を付与；「3 verifiers」を「4」に修正；Critical Rules を 9/10/11 に再採番；`lint_manuscript.py` が存在しない `.md` 引数をスキップ（最初の lint テストを追加）；`check_numbers.py` が明示的な p 値を要求（0〜1 の任意の割合ではない）；`search_pubmed.py` の evidence エントリに Evidence ID ＋ Source Status を追加；チェッカーの FAIL 出力に `failure_code` を追加；テストを 77 件に拡張。
- **Concision Pass** — `docs/writing_guide.md` にジャーナルの語数制限向け圧縮パス（Phase 5）を追加：シニアの英文校正から抽出した 10 個の Before→After パターンに加え、過剰圧縮を防ぐガードレール（primary-outcome の定義、統計仕様、適格基準、主要な限界は本文に残すか Supplement へ移すこと—決して暗黙に削除しない）。

### v1.0.0 (2026-06-20)

**検証の堅牢化（superpowers に着想）**

- **Gate freshness / provenance** — `check_gate.py` に `provenance:` ブロック（成果物/evidence/results の sha256）、`--verify-hash LABEL=PATH`（検証済みファイルが PASS 後に変更された場合にゲートを *stale* として失敗させる）、`--compute-hash PATH` を追加。並行検証によって生じた stale-PASS の抜け穴を塞ぎ、後方互換（opt-in フラグ）。`review/gates/_TEMPLATE.GATE.md` と `docs/verification_protocol.md`（v0.2.0）が文書化し、pytest カバレッジを 70 テストに拡張。
- **Parallel verifiers + Constraint-first** — 4 つのセクションゲート verifier が凍結された成果物に対して並行実行され、修正は Constraint（仕様）違反を優先し、いずれかの編集後はすべての PASS を破棄して再実行（`docs/verification_protocol.md`）。
- **STOP signals** — verifier が見逃す人間レベルのショートカットを防ぐ CLAUDE.md anti-rationalization テーブル（§10）。
- **Socratic draft-plan brainstorming** — `docs/draft_plan_template.md` の Step 0（一度に 1 問ずつ；`/paper-debate` とは別物で、その R0 準備として供給）、CLAUDE.md Phase 3 と Rule 8 に接続。
- **Reviewer-response triage** — `docs/revision_guide.md` がコメントごとに accept/partial/rebut の姿勢を割り当て、`[CHANGE]` ＋ ghost-revision と連動；Phase 8 の verifier セットを Constraint を含むよう整合。
- **Command `use-when` lines** を `.claude/commands/*.md` に追加；TodoWrite を非権威的な QC/ゲート追跡として文書化（CLAUDE.md Rule 4）。

### v0.9.3 (2026-06-19)

**共著者コラボレーションとマルチモデル批判的レビュー**

- **`/paper-debate`** を追加（`docs/debate_protocol.md`、`.claude/commands/paper-debate.md`）— 執筆前の Claude–Codex 共著者ディベート（分析計画・draft plan・論証構造・査読者応答）。合意上限 3、ディベートログは `review/debates/`、Codex 不可時は Claude 単独フォールバック。
- **`/critical-review`** を追加（`docs/critical_review_protocol.md`、`.claude/commands/critical-review.md`）— 執筆後に Claude サブエージェント・Codex・OpenRouter モデル（既定 `minimax/minimax-m3`、`z-ai/glm-5.2`）による敵対的レビュー。合意度 × 重大度で統合・順位付け、レポートは `review/critical/`。
- `scripts/critical_review.py`（OpenRouter 呼び出し。1 モデルの失敗は skip し致命的でない）、`scripts/critical_models.txt`（モデルリスト外部化）、`scripts/critical_prompts/`（スクリプト・Claude サブ・Codex が共有する単一正本プロンプト `manuscript.txt`/`response.txt`）を追加。
- critical-review プロンプトを **senior reviewer / editor-in-chief レベル** に — 表層的欠陥ではなく設計の妥当性・データが結論を支持するか・出版価値を問う。
- `build_prompt` を `str.format` から `str.replace` に変更 — プロンプトや対象テキストの波括弧（JSON・LaTeX 例）が置換を壊さない。回帰テストを追加。
- `docs/writing_guide.md` に **AI-Draft De-bloat** セクションを追加 — AI の痕跡（表層的 `-ing` 分析・AI 語彙・signposting）を除去、衝突パターン（hedging/copula/passive）は除外。
- OpenRouter アクセスは `.claude/settings.local.json` の `OPENROUTER_API_KEY`（gitignored）。キーが無い場合は OpenRouter のみ skip し他のレビュアーで続行。
- CLAUDE.md に両コマンドを統合（Collaboration コマンド、Phase 2/3/4/8 ディベート、Round 6 二層批判的レビュー、File Roles、構造ツリー）。

### v0.9.2 (2026-06-18)

**検証ハーネスの堅牢化**（バグ修正 + ドキュメント整合性）

- `check_numbers.py`：パーセンテージ（例：42.5%）でクラッシュしなくなった；無関係な値（例：count 0）のみで裏付けられた p 値を拒否；桁区切り（1,234）を処理し、ISO 日付とインライン `code` 区間を無視。
- `check_gate.py`：インライン `# ...` コメントを除去し、文書化された gate テンプレートが通過し、round-overflow エスカレーションが動作するようにした。
- `requirements.txt`（python-docx）と `tests/` pytest スイートを追加（`pytest` で実行）。
- ドキュメント：verifier セットを Constraint / Citation / Data / Logic に修正（Revision は Revision-claims と Response-alignment を追加）；response compiler の説明を修正（書式を再現し、reference .docx を読み込まない）。

### v0.9.1 (2026-06-18)

**多言語 README と Author Response DOCX の完成**

- 英語、韓国語、日本語、中国語 README を検証ハーネス scripts と DOCX response workflow に合わせて同期。
- Author response Markdown template と `compile_response_docx.py` の使用方法を追加。
- citation evidence、numeric grounding、phase gate、revision claim の deterministic checker を文書化。
- hallucination control、redundancy control、logic check、revision alignment のための LLM verifier prompt-template を文書化。

### v0.9.0 (2026-06-16)

**検証ハーネス** — 各 produce step 後の inline produce→verify→fix→re-verify gate（新規 `docs/verification_protocol.md`）

- 各 produce step（Phase 3/4/8）後の inline 検証ゲート — end-loaded の手動 QC を produce→verify→fix→re-verify ループに置き換え。
- Verifier サブエージェント：Constraint（指示遵守）、Citation（evidence.md との citation grounding）、Data（results CSV との数値）、Logic（セクション横断の論理/重複）。Revision gate は Revision-claims と Response-alignment を追加。
- 自律修正ループ（最大 2 回リトライ）後にユーザーへエスカレーション。
- `[EVID:author_year]` citation tags と results-CSV-as-single-source grounding。
- ゲート台帳（`review/gates/`）が `status: PASS` 記録まで進行を停止。
- `evidence.md` エントリに Source Status フィールドを追加；Phase 6 QC を最終確認パスに軽量化。
- プログラム的 citation checker：`py scripts\check_citations.py drafts\03_introduction.md --evidence knowledge\evidence.md`
- プログラム的 number checker：`py scripts\check_numbers.py drafts\05_results.md drafts\table_1.md --results results`
- プログラム的 phase gate checker：`py scripts\check_gate.py review\gates\phase_04_draft.GATE.md --artifact drafts\05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic --verify-hash artifact=drafts\05_results.md`
- プログラム的 ghost-revision checker：`py scripts\check_revision_claims.py drafts\revision\REV1\response_letter_REV1.md --strict`
- LLM semantic verifier schema：logic、redundancy、semantic citation support、revision-response alignment のための `docs/verifier_prompt_templates.md`

### v0.8.1 (2026-06-16)

**Response Letter 書式ルール** — `docs/revision_guide.md` 内部バージョン v0.3.0 → v0.4.0

- response letter 形式を最小限書式の標準に再構成：
  - **「Comment x.x」** と **「Response」** の語のみ bold；その他の書式はすべて除去（見出し、色、インデント、表、箇条書き/番号付きリストなし）
  - 引用した修正原稿テキストは *italic* で表記
  - 応答は散文で記述（番号付き/箇条書きなし）し、感謝 → 立場 → 論拠 → 対応を 1 段落で流す
  - 修正箇所は lead-in 配置を使用 — 先に箇所を述べ、次に修正テキストを引用（末尾の「(See ...)」なし）
  - ハイフン・emダッシュは使用しない
  - 説得力のある、査読者を納得させるトーン
- 原稿修正の **minimal change principle**（最小変更原則）を追加 — 各コメントに対応するために必要な最小限の文修正のみを行い、冗長にならず簡潔に保つ
- 「執筆中」チェックリストを新しい書式ルールに合わせて更新

### v0.8.0 (2026-06-16)

**Style Workflow、Linting、Agent Instructions**

- writing-style 資料を、`knowledge/` 配下の参考エビデンスとは分離したトップレベルの `Style/` ワークフローに昇格。
- style-anchor 抽出ルール、PDF-to-MD mirror ルール、出版社の汎用ファイル名処理のための `Style/style_guide.md` を追加。
- `Style/terminology.md` を、脊椎外科・臨床試験・AI/radiomics・報告コンテキストにわたる preferred/forbidden 用語のプロジェクト用語 registry に拡張。
- outline → evidence-bound draft → style pass → QC の drafting を強制する `docs/drafting_protocol.md` と `docs/section_templates.md` を追加。
- `scripts/lint_manuscript.py` を追加し、Windows 上で `py scripts/lint_manuscript.py drafts --quiet` により manuscript linting が通過するよう draft/table テンプレートを更新。
- agent 起動指示として `AGENTS.MD` を追加し、`CLAUDE.md` を権威ある source of truth とする。
- 著作権付き PDF と非公開の style-anchor 要約をローカルに保ちつつ、公開ワークフローファイルと例は commit 可能なまま残すよう `.gitignore` を更新。

### v0.7.1 (2026-05-15)

**用語 & テンプレート**

- `Style/terminology.md` を追加 — BESS/脊椎外科の分野標準用語 registry
  - 手技名、器具、アウトカム指標、研究デザイン、統計、合併症にわたる 60 以上の用語の正/誤の使い分け
  - よくある誤り一覧（creatine phosphokinase vs creatinine kinase；assessor-blind vs double-blind；VAS vs NRS など）
- `docs/draft_plan_template.md` を追加 — 完全な 10 項目 draft plan テンプレート
  - Claim→Citation Mapping テーブル（Introduction/Methods/Discussion）
  - 承認チェックリスト（Phase 4 の前に全 10 項目が完了している必要あり）
- CLAUDE.md Phase 1：プロジェクト設定時に journals フォーマット確認と Style anchor レビューを追加
- CLAUDE.md：File Roles テーブル、Phase 3 ワークフロー、Quick Commands をテンプレート参照に更新
- 修正：`profile/journals.md` の citation 例を修正 — TSJ は et al. の前に 6 著者を表示（3 ではない）；BJJ は BJJ ポリシーに従い全 8 著者を et al. なしで列挙

### v0.7.0 (2026-05-14)

**Citation 品質 & Style 一貫性**

- `Style/` を追加 — own、landmark、target-journal の style anchors
  - 2018 Spine — うつ病 & 慢性腰痛の横断研究（KNHANES）
  - 2020 Spine J — Biportal endoscopic vs microscopic laminectomy RCT
  - 2023 Spine J — Biportal endoscopic vs microscopic discectomy RCT
  - 2024 Neurospine — BESS safety profile：2 件の RCT のプール解析
  - 2025 Bone Joint J — ENDOBH 多施設 RCT（6 病院）
  - 各ファイル：完全な citation、主要用語テーブル、methods boilerplate、データ付き key claims
- CLAUDE.md Rule 8：draft_plan.md の必須項目 10 として **Claim→Citation Mapping** を追加
  - 執筆開始前に ~20 個の key claims を citations に対応付け
  - Intro background（5–8）、methods rationale（2–3）、discussion comparisons（5–8）
- CLAUDE.md：Phase Completion Criteria 3→4 を更新（draft_plan 必須項目 9 → 10）
- `profile/journals.md`（local only, gitignored）を追加 — 8 つの対象ジャーナルの検証済み citation 形式
  - The Spine Journal：bracket [N]、6 著者の後に et al.
  - Spine (Phila Pa 1976)：superscript、citation に "(Phila Pa 1976)" 必須
  - Bone Joint J：全著者列挙、Vol-B(issue) 形式
  - Neurospine：superscript、3 著者の後に et al.
  - その他：J Neurosurg Spine、Global Spine J、Clin Orthop Relat Res、Asian Spine J
- `profile/authors.md`（local only, gitignored）に 5 名の共著者の ORCID を追加

### v0.6.0 (2026-04-18)

**Writing Guide 大規模リファクタ** — `docs/writing_guide.md` 内部バージョン v0.3.0 → v0.4.0

- CLAUDE.md（orchestrator）と writing_guide.md（rules）の **役割分離**
  - CLAUDE.md「Natural Academic Writing Style」セクションを pointer のみに圧縮（約 115 行を削除）
  - すべての writing style ルール、テーブル、例を writing_guide.md に統合
- **新セクション：Style Reference Tables** を writing_guide.md に
  - Voice & Tense by Section（6 セクション：Abstract/Intro/Methods/Results/Discussion/Conclusion）
  - Transition Words（but → nonetheless）
  - Verb Upgrades（showed → demonstrated）
  - Common Corrections（elderly → older adult など）
  - Statistical Notation（italic *p*、範囲に en-dash、決して *p* = 0.000 としない）
  - Hedging Language（Discussion 向け 4 レベルガイド：Strong/Moderate/Weak/Very weak）
- **新セクション：Writing Principles (4 Pillars)** を writing_guide.md に
  - Clarity、Conciseness、Objectivity、Consistency を拡張した例とともに
- **General Principles を 6 つの新ルールで拡張**：
  - 原稿本文での bold 禁止
  - 略語の define-once ルール
  - 統計手法ではなく臨床所見を文の主語に
  - 同義語の混用禁止（dural tear ↔ durotomy など）と draft_plan.md での用語選択
  - 数値書式の一貫性（小数、単位）
  - 文頭の数字禁止（綴るか再構成する）
- **Results セクション**：非有意 p 値の省略ガイドライン（primary outcome は例外）を追加
- **Discussion セクション**：3 つの新サブセクション
  - 具体的な数値/p 値なし（文献比較は例外）
  - 非有意結果に対する方向性のある trend の枠組み付けなし
  - 中立的トーンと禁止する誇張表現リスト
- **Tables セクション**：2 つの新 Tips
  - Methods Statistics と Table 脚注の役割分離
  - 事前指定された感度分析のための Supplementary Table

**ファイル間の整合性修正**

- CLAUDE.md Phase 2：`docs/statistical_analysis_guide.md` と `analysis_plan.md` 必須項目（endpoint hierarchy、検定、多重比較、欠測データ）への明示的参照
- CLAUDE.md Phase 6 QC：ラウンドごとの責任注記（Claude / Dr. Editor / Dr. Statistician）と CRITICAL vs RECOMMENDED の明記
- CLAUDE.md Phase 3→4 Completion Criteria：`draft_plan.md` の必須 9 項目すべてを列挙するよう拡張
- `docs/revision_guide.md`：ラウンドごとの再実行チェックリストと投稿前チェックリストを備えた新「QC Re-run for Revision」セクション
- `docs/evidence_guide.md`：Search Log のクエリ例を実際の PubMed 構文（field tags `[tiab]`/`[MeSH]`、boolean AND/OR/NOT、引用符付きフレーズ）に更新

### v0.5.2 (2026-04-15)

- すべてのドキュメントにわたるファイル間の不整合を修正
- figure 形式ワークフローを更新：draft は PNG（300 DPI）、最終投稿は LZW 圧縮の TIFF（600+ DPI）、PPT/ベクターをオプションに
- `save_figure()` テンプレートを更新：`draft=True`（PNG）/ `final=True`（TIFF LZW）のパラメータ分割
- CLAUDE.md の revision 構造と File Roles テーブルに `review/reviewer_comments_REV{N}.md` を追加
- `analysis_plan.md` の placeholder を `[FROM CLAUDE.md]` からユーザーフレンドリーな `[연구 설계 입력]` に修正
- `revision_guide.md` のファイル構造を CLAUDE.md に整合（R1→REV1 命名規則）
- `qc_guide.md` の QC log と Final Sign-off に Round 4 テンプレートを追加
- `statistical_analysis_guide.md` の figure 出力形式に TIFF を含めるよう更新
- `checklist_guide.md` の figure 投稿要件を更新（TIFF LZW 600+ DPI）

### v0.5.1 (2026-04-15)

- Analysis Plan Mandatory（Critical Rule #7）を追加 — 統計分析の実行前に `analysis_plan.md` を作成し承認を得る必要あり
  - マルチ論文の場合は論文ごとの analysis plan（`data/paper{N}_xxx/analysis_plan.md`）
  - 必須内容：研究課題、選択/除外基準、変数定義、検定選択の根拠、有意水準
- Draft Plan Mandatory（Critical Rule #8）を追加 — いずれかのセクション執筆前に `drafts/draft_plan.md` を作成し承認を得る必要あり
  - 必須内容：キーメッセージ、トーン/ボイス、必須参考文献、エビデンスギャップ、table/figure 計画、introduction/discussion アウトライン、limitation points
  - マルチ論文の場合は論文ごとの draft plan
- Model Selection by Phase（Critical Rule #9）を追加 — コスト効率的なモデルガイダンス
  - Opus 推奨：Analysis Plan、Draft Plan、Revision（戦略的フェーズ）
  - Sonnet デフォルトで Opus オプション：執筆、Style Polish、QC（計画ベースの実行）
  - Draft Plan 作成には Plan Mode（`/plan`）を推奨
- ワークフローのフェーズを番号付け直し（7 → 8 フェーズ）：Analysis と Drafting の間に Phase 3（Draft Plan）を追加
- Phase Completion Criteria を draft_plan.md 承認ゲートで更新

### v0.5.0 (2026-04-14)

- QC Round 2（Reference Verification）を 4 つの新サブチェックで強化：
  - 2.5 Placeholder Reference Detection — 偽/仮の citation（[ref1]、[TBD]、[X] など）を検出
  - 2.6 Order of Appearance Check — citation 番号が Vancouver スタイルの順序に従うか検証
  - 2.7 Reference Format Consistency — 全参考文献にわたる書誌スタイルの統一性を確認
  - 2.8 Citation Distribution Check — セクション別の citation バランス、自己引用率、新しさ
- Reference List Integrity（2.4）を強化 — 番号の連続性と重複番号チェックを追加
- QC Log テンプレートを Round 2 の強化セクションで更新
- File Versioning ルール（Critical Rule #5）を追加 — 日付ベースのデフォルト（`_YYMMDD`）、`_v1`、`_REV1`、`_FINAL`
- Multi-Paper Organization（Critical Rule #6）を追加 — data、results、drafts、output、review の論文ごとのサブフォルダ
- Multi-Paper Project 構造図を追加（docs/knowledge/scripts は共有、論文ごとに分離フォルダ）
- Revision フォルダ構造を追加 — `drafts/revision/REV{N}/`、`output/revision/REV{N}/`
- Recommended Workflow に Phase 7（Revision）を QC 再実行要件とともに追加
- Phase Completion Criteria に Submit → Revision パスを追加
- File Roles テーブルに revision フォルダのエントリを更新

### v0.4.0 (2026-04-09)

- `docs/revision_guide.md` を追加 — レビュアー対応・revision ガイド
- `docs/figure_guide.md` を追加 — 出版品質の figure 作成ガイド
- `drafts/00_cover_letter.md` を追加 — 簡潔な cover letter テンプレート
- CLAUDE.md を更新：プロジェクト構造、file roles、revision と figures の Quick Commands
- プロジェクト構造から Spine GraphRAG のプロジェクト固有参照を削除

### v0.3.0 (2026-03-09)

- `docs/statistical_analysis_guide.md` の大幅な書き直し（v0.2.1 → v0.3.0）
  - Statistical Parsimony、Analysis Hierarchy、Clinical Significance、Subgroup Analysis、Sensitivity Analysis
  - Methods Statistical Section Checklist（ICMJE/SAMPL 準拠の 10 必須項目）
- 統計的整合性のため `docs/writing_guide.md`、`docs/expert_roles.md`、`docs/qc_guide.md` を更新

### v0.2.5 (2026-03-09)

- `scripts/search_pubmed.py` を追加 — NCBI E-utilities API を使用した PubMed 検索ツール（MCP 不要、外部パッケージ不要）
- スラッシュコマンドを追加：`/search-evidence [query]`、`/import-doi [doi]`

### v0.2.4 (2026-03-04)

- LF 改行正規化のための `.gitattributes` を追加
- `.DS_Store`、ローカル設定、IDE 設定の `.gitignore` ルールを追加

### v0.2.3 (2026-02-15)

- DOCX 変換ルールのための `docs/docx_guide.md` を追加
- 日付サフィックス付き output ファイル、title page と table の DOCX ファイルを分離

### v0.2.2 (2026-02-10)

- evidence guide を evidence registry から分離
- 詳細な要約方法を備えた `docs/evidence_guide.md` を追加

### v0.2.1 (2026-02-07)

- 各種の構造的修正とテンプレート改善

### v0.2 (2026-02-03)

- 統計分析ガイドを追加
- Table/Figure/Results の重複防止ルールを追加

### v0.1 (Initial)

- 基本的なプロジェクト構造
- writing guide、expert roles、checklists、QC guide
