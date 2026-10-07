# 詳細ガイド（README から移動）

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
- **学術執筆スタイルシステム** — Style Reference Tables（Voice/Tense、Transition、Verb Choice、Common Corrections、Statistical Notation、Hedging）＋ Writing Principles（Clarity/Conciseness/Objectivity/Consistency）
- **確実なスタイル変換**（`/style-pass`）— 粗削りの草稿を、束ねられたジャーナルスタイルへ変換する：プロジェクトごとの Style Spec（選んだ手本 1 つ）＋セクション単位の変換＋独立した Style-Conformance verifier（auto-fix ループ）＋計測可能な `scripts/check_style.py` ゲート（文長、引用密度、hedging）＋「make it academic」意図での自動トリガー（`docs/style_transform_protocol.md`）
- **引用品質管理** — Claim→Citation Mapping（執筆前に主要 claim と根拠文献を対応付け）
- **Style アンカーライブラリ**（`Style/`）— own、landmark、target-journal アンカーで用語・トーン・論証構造を管理
- **用語 registry**（`Style/terminology.md`）— preferred/forbidden 用語、定義、使用 context
- **Drafting protocol**（`docs/drafting_protocol.md`）— outline → evidence-bound draft → style pass → QC
- **Manuscript linting**（`scripts/lint_manuscript.py`）— 用語、placeholder、過大主張、セクション別違反の自動確認
- **Citation evidence checking**（`scripts/check_citations.py`）— `[EVID:id]` タグを `knowledge/evidence.md` と照合
- **Data number checking**（`scripts/check_numbers.py`）— 原稿・表の数値を `results/*.csv` と照合
- **Phase gate ledger checking**（`scripts/check_gate.py`）— `review/gates/*.GATE.md` に必要な PASS がない場合は進行を停止
- **Gate freshness / provenance**（`scripts/check_gate.py --verify-hash`）— PASS 時に検証済み成果物（および evidence/results）の sha256 を記録し、その後の編集でゲートを **stale** にして再検証を強制 — parallel-verifier の抜け穴を塞ぐ
- **Gate cross-check**（`scripts/check_gate.py --cross-check`）— 決定的な次元（`citation` / `numbers` / `revision_claims`）について正本 checker をその場で再実行し、台帳の記録ステータスが実際と一致しない場合はゲートを FAIL にする — 実行せずに書いた偽の PASS や stale な PASS を検出（ソース到達不可なら loud FAIL）
- **Revision claim checking**（`scripts/check_revision_claims.py`）— response letter の `[CHANGE]` claim を revised manuscript と照合
- **LLM verifier prompt templates**（`docs/verifier_prompt_templates.md`）— constraint、semantic citation、data、logic/redundancy、style-conformance、citation-stance、revision-alignment の検証 prompt/schema
- **Citation assist** — `/suggest-citation`（claim に最適な `[EVID:id]` を見つける）、`/verify-claims`（`scripts/extract_claims.py` 経由で文ごとに SUPPORTED/PARTIAL/UNSUPPORTED の claim マップを作成）、`/cite-stance`（支持/対立/言及、Scite 流）、`/evidence-table`（`scripts/evidence_table.py` 経由で「組み入れた研究のまとめ」表を作成、Elicit 流）（`docs/citation_assist_protocol.md`）
- **ナレッジグラフ統合**（任意）— medical-kag MCP（GraphRAG）を上流の探索／conflict／GRADE 統合／参考文献エンジンとして利用し、`knowledge/evidence.md` を正典に保ち、`scripts/search_pubmed.py` をフォールバックとする（`docs/medical_kag_protocol.md`）
- **プロセス強制 hooks**（`scripts/hooks/`）— SessionStart の contract 注入、PreToolUse の plan-first ゲート、PostToolUse の style/terminology lint、UserPromptSubmit の style 自動トリガー
- **ワンショット検証**（`/verify`、`scripts/verify_all.py`）— citation ＋ number ＋ gate のチェックをまとめて実行
- **Author response DOCX generation**（`scripts/compile_response_docx.py`）— DOCX-ready Markdown を `Author_response_220803_Final.docx` house style に変換
- **Author response Markdown template**（`docs/response_letter_template.md`）— reviewer response、修正箇所、machine-readable `[CHANGE]` block を整合
- **PubMed 検索ツール** — 内蔵 Python スクリプト（MCP・外部パッケージ不要）
- **共著者ディベート**（`/paper-debate`）— 執筆前の Claude–Codex 議論で分析計画・draft plan・論証構造・査読者応答を設計（`docs/debate_protocol.md`）
- **マルチモデル批判的レビュー**（`/critical-review`）— 執筆後に Claude サブエージェント・Codex・OpenRouter モデルで senior reviewer/editor レベルの敵対的レビュー、合意度 × 重大度で順位付け（`docs/critical_review_protocol.md`）
- **編集長 desk-screen**（`/editor-review`）— 機械的 QC を越えた high-impact ジャーナル編集長の実質評価: 論文の分野を特定し、その分野の high-impact ジャーナルが実際に掲載する水準でベンチマークして臨床的妥当性・scope fit・分析の妥当性を判定 → `SEND FOR PEER REVIEW`/`BORDERLINE`/`DESK REJECT` 判定 + 競争力のために追加すべき点（あるいは現実的な下位ジャーナル）。単一 Opus サブエージェントまたはマルチモデル panel；medical-kag ベンチマークは任意（`docs/critical_review_protocol.md` §5）
- **AI-Draft De-bloat** — AI の痕跡（表層的な `-ing` 分析・AI 語彙・signposting）を除去し、disclosure を保ちつつ自然に読ませる writing-guide パス（`docs/writing_guide.md`）
- **スラッシュコマンド** — エビデンス登録（`/search-evidence`、`/import-doi`）

---

## プロジェクト構成

```
project/
├── WORKFLOW.md                   # コアルール・設定（Claude/Codex/Gemini で共有）
├── CLAUDE.md                     # Claude Code ブートストラップ；@WORKFLOW.md で WORKFLOW.md を import
├── AGENTS.md                     # Codex/agent 起動ルール；WORKFLOW.md を source of truth とする
├── GEMINI.md                     # Gemini ブートストラップ；WORKFLOW.md を参照
├── README.md                     # 英語版 README
├── .gitattributes                # 改行コードポリシー (text=auto eol=lf；OneDrive/Windows 同期による CRLF 変更を防止)
├── docs/                         # 参照ガイド
│   ├── workflow_reference.md     # Tree, file roles, command catalog (moved from WORKFLOW.md)
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
│   ├── draft_plan_template.md    # Draft plan template
│   ├── debate_protocol.md        # Claude–Codex 共著者ディベート手順
│   ├── critical_review_protocol.md  # 外部マルチモデル敵対的レビュー
│   ├── style_transform_protocol.md  # /style-pass 変換 + Style verifier
│   ├── style_spec_template.md    # Style Spec テンプレート（手本を 1 つ束ねる）
│   ├── citation_assist_protocol.md  # 引用候補提示 / 検証 / スタンス / 表
│   └── medical_kag_protocol.md   # medical-kag MCP（GraphRAG）；evidence.md を正典とする
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
│   ├── check_style.py            # Style Spec に対する計測可能なスタイルゲート
│   ├── extract_claims.py         # [EVID:id] タグ付きの文を抽出（claim 検証）
│   ├── evidence_table.py         # 構造化された研究レコード → markdown 比較表
│   ├── verify_all.py             # /verify — citation + number（+ gate）を 1 回で実行
│   ├── critical_review.py        # OpenRouter マルチモデル敵対的レビュー呼び出し
│   ├── critical_models.txt       # OpenRouter モデルリスト（外部化）
│   ├── critical_prompts/         # 敵対的プロンプト単一正本（manuscript.txt, response.txt）
│   └── hooks/                    # プロセス強制 hooks（enforce_gates, session_contract, lint_on_edit, style_intent）+ run.sh ランチャー（py→python3 自動選択）
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

## インストール：2 つの方式

| | A. テンプレート（インストール不要） | B. インストール型エンジン |
|---|---|---|
| 入手 | `git clone` / "Use this template" | `uv tool install git+https://github.com/grotyx/Academic_writing_c_claudecode@vX.Y.Z` |
| 論文の開始 | コピーしたフォルダ内で作業 | `manuwright init my-paper` |
| エージェント | Claude Code は `.claude/`、Codex/Gemini は `AGENTS.md`/`GEMINI.md` | `manuwright agents install`（Claude Code、Codex、Antigravity、opencode、Muse） |
| 更新 | `git pull`（clone）または公開エンジンファイルの置換 | `manuwright update`；任意の `manuwright config set auto-update on`（patch のみ、有効なレビューを stale にしない） |

両方式とも同じエンジンと規則を使う。詳細：[docs/harness_guide.md](../../docs/harness_guide.md)、移行：[docs/migration_guide.md](../../docs/migration_guide.md)、設計：[docs/distribution_plan.md](../../docs/distribution_plan.md)。

## クイックスタート

1. **設定**：`WORKFLOW.md` に研究テーマ、対象ジャーナル、研究デザインを入力します
2. **参考文献**：`/search-evidence [クエリ]` または `python scripts/search_pubmed.py` で PubMed を検索し、`knowledge/evidence.md` に登録します
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

- **Parallel verifiers + Constraint-first.** 4 つのセクションゲート verifier（Constraint / Citation / Data / Logic）は、凍結された成果物に対して並行してディスパッチされます。成果物は検証の途中で編集されず、FAIL 時には Constraint（仕様適合性）の指摘を最優先で修正します。`docs/verification_protocol.md`（v0.3.0）を参照。
- **Gate freshness / provenance**（`scripts/check_gate.py`）。PASS 時にゲート台帳へ検証済み成果物の sha256 を記録します（citation・numbers を伴うゲートでは `evidence` / `results` も；revision では必須）。`check_gate.py --verify-hash LABEL=PATH` は再ハッシュを行い、PASS 以降にファイルが変更されていればゲートを **stale** として失敗させます — PASS 後の編集が再チェックを静かにすり抜ける抜け穴を塞ぎます。`--compute-hash PATH` は provenance フィールドを埋めます。ツールレベルでは opt-in、文書化されたゲートコマンドでは標準で有効です。
- **STOP signals.** WORKFLOW.md の anti-rationalization テーブルが、verifier では捉えられない人間レベルのショートカット（「この数値はたぶん大丈夫」→ CSV を確認；「もう PASS した」→ 変更された成果物は stale）を捕捉します。
- **Socratic draft-plan brainstorming.** `docs/draft_plan_template.md` の「Step 0」が、計画を埋める前に論文の意図を一度に 1 問ずつ研ぎ澄まします — `/paper-debate` とは別物で、その R0 準備として供給されます。
- **Reviewer-response triage.** `docs/revision_guide.md` は各査読コメントに accept / partial / rebut の姿勢を割り当て、`[CHANGE]` マーカーと ghost-revision ゲートに対応付けます。
- **Command `use-when` guidance.** 各 `.claude/commands/*.md` が、それを起動すべき状況を明示するようになりました。

### Author Response DOCX Workflow

Reviewer response は `docs/response_letter_template.md` 形式で作成し、各原稿修正は `[CHANGE]` block として記録します。最終 response letter は次のコマンドでコンパイルします：

```powershell
python scripts/compile_response_docx.py drafts/revision/REV1/response_letter_REV1.md
```

compiler は `Author_response_220803_Final.docx` の house style を再現します — Times New Roman 11 pt、response・位置・修正テキストの行は bold、本文は justified。この .docx ファイルをテンプレートとして読み込むことはなく、書式はコードに組み込まれています。

### PubMed 検索ツール

MCP 不要で参考文献を検索できる内蔵 Python スクリプト（`scripts/search_pubmed.py`）：

```bash
python scripts/search_pubmed.py search "endoscopic spine surgery"  # 検索
python scripts/search_pubmed.py fetch 35486828                     # PMIDで取得
python scripts/search_pubmed.py doi 10.1016/j.spinee.2023.01.005  # DOIで取得
python scripts/search_pubmed.py related 35486828                   # 関連論文
```

Claude 統合スラッシュコマンド：

- `/search-evidence [クエリ]` - 検索、選択、evidence.md に登録
- `/import-doi [doi]` - DOI から取得し evidence.md に登録

---

## ドキュメント一覧

| ドキュメント | 目的 |
|-------------|------|
| [WORKFLOW.md](../../WORKFLOW.md) | コアルールとプロジェクト設定（全ランタイム共有） |
| [CLAUDE.md](../../CLAUDE.md) | Claude Code ブートストラップ；WORKFLOW.md を import |
| [docs/writing_guide.md](../../docs/writing_guide.md) | セクション別執筆ガイド ＋ Style Reference Tables ＋ Writing Principles (4 Pillars) |
| [docs/drafting_protocol.md](../../docs/drafting_protocol.md) | outline → evidence-bound draft → style/QC pass の必須 drafting workflow |
| [docs/section_templates.md](../../docs/section_templates.md) | セクション別 paragraph function と sentence patterns |
| [docs/expert_roles.md](../../docs/expert_roles.md) | 専門家チームの説明 |
| [docs/checklist_guide.md](../../docs/checklist_guide.md) | STROBE、CONSORT、PRISMA、CARE チェックリスト |
| [docs/qc_guide.md](../../docs/qc_guide.md) | 品質管理手順（6ラウンド） |
| [docs/verification_protocol.md](../../docs/verification_protocol.md) | 検証ゲート・4 Verifier 憲章・自律修正ループ・ゲート台帳 |
| [docs/verifier_prompt_templates.md](../../docs/verifier_prompt_templates.md) | LLM semantic verifier prompts and structured output schema |
| [docs/statistical_analysis_guide.md](../../docs/statistical_analysis_guide.md) | 統計分析ガイド（節約原則、MCID、サブグループ分析） |
| [docs/evidence_guide.md](../../docs/evidence_guide.md) | エビデンス作成ガイド（形式、要約方法、ワークフロー） |
| [docs/revision_guide.md](../../docs/revision_guide.md) | レビュアー対応ガイド（回答書作成、外交的表現、QC 再実行チェックリスト） |
| [docs/response_letter_template.md](../../docs/response_letter_template.md) | DOCX-ready author response Markdown template |
| [docs/figure_guide.md](../../docs/figure_guide.md) | Figure作成ガイド（DPI、パレット、Pythonテンプレート） |
| [docs/docx_guide.md](../../docs/docx_guide.md) | DOCX 変換ガイド（書式、テーブルスタイル、命名規則） |
| [docs/draft_plan_template.md](../../docs/draft_plan_template.md) | Draft plan template — 10項目、claim→citation tables、approval checklist |
| [docs/debate_protocol.md](../../docs/debate_protocol.md) | Claude–Codex 共著者ディベート手順（ラウンド、役割、ロギング、fallback） |
| [docs/critical_review_protocol.md](../../docs/critical_review_protocol.md) | 外部マルチモデル敵対的レビュー（レビュアープール、合意度 × 深刻度、fallback） |
| [Style/style_guide.md](../../Style/style_guide.md) | Style anchor workflow、extraction framework、PDF-to-MD mirror rules |
| [Style/terminology.md](../../Style/terminology.md) | Preferred/forbidden terminology registry |
| [Style/own/example_YYYY_Journal_keyword.md](../../Style/own/example_YYYY_Journal_keyword.md) | Own-paper style-anchor template |
| [scripts/lint_manuscript.py](../../scripts/lint_manuscript.py) | Manuscript lint script |
| [scripts/check_citations.py](../../scripts/check_citations.py) | `[EVID:id]` citations を `knowledge/evidence.md` と照合 |
| [scripts/check_coverage.py](../../scripts/check_coverage.py) | 引用 coverage audit — **過剰引用**（1つの主張への過多な引用）・**未登録引用**が品質シグナル、セクション別引用密度；未引用/未実現 claim は中立（キュレーションであり無駄ではない） |
| [scripts/format_references.py](../../scripts/format_references.py) | `[EVID:id]` → ジャーナル形式の参考文献リスト（numbered/author-year）+ 本文タグを `*_formatted.md` に変換；**MCP 非依存**（Phase 7） |
| [scripts/check_abstract.py](../../scripts/check_abstract.py) | abstract↔本文の数値整合性 — abstract にあって本文に無い数値を検出（Rule 3；p 値は既定で除外）（Phase 6 QC Round 1） |
| [scripts/check_crossrefs.py](../../scripts/check_crossrefs.py) | Table/Figure 相互参照チェック — 本文の "Table N"/"Figure N" 言及 ↔ 実際の `table_*.md`・figure legends：**broken reference**（主要シグナル）・未引用項目・初出順序；既定 advisory、`--fail-on-*` でゲート化（Phase 6 QC） |
| [scripts/check_abbreviations.py](../../scripts/check_abbreviations.py) | 略語の初出定義チェック — abstract/本文を別 scope で検査（UNDEFINED / DEFINED_AFTER_USE / REDEFINED / SINGLE_USE）；誤検出前提の advisory、`--allow`・`--strict`（Phase 6 QC） |
| [scripts/check_response_coverage.py](../../scripts/check_response_coverage.py) | 査読コメント回答カバレッジ — すべての `Comment N)` に実際の `Response:` が必須（未回答・空回答・placeholder を遮断）、`--comments` で元コメントファイルと照合；ghost-revision ゲートを補完（Phase 8） |
| [scripts/check_numbers.py](../../scripts/check_numbers.py) | 原稿・表の数値を `results/*.csv` と照合 |
| [scripts/check_gate.py](../../scripts/check_gate.py) | `review/gates/*.GATE.md` の status と必須 check を検証 |
| [scripts/check_revision_claims.py](../../scripts/check_revision_claims.py) | response-letter `[CHANGE]` claims を revised manuscript files と照合 |
| [scripts/compile_response_docx.py](../../scripts/compile_response_docx.py) | `response_letter_REV*.md` を Author_response-style DOCX に変換 |
| [scripts/search_pubmed.py](../../scripts/search_pubmed.py) | PubMed 検索スクリプト（NCBI E-utilities、外部パッケージ不要） |
| [scripts/critical_review.py](../../scripts/critical_review.py) | OpenRouter マルチモデル敵対的レビュアー呼び出し（モデル1個の失敗が全体を中断させない） |

---

## 要件

- Claude AI（Claude Code CLI または VSCode 拡張機能）
- Python 3.10+（古いインタープリタは `python -m harness doctor` が警告；テスト：`pip install -r requirements-dev.txt`）
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
