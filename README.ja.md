🇺🇸 [English](README.md) | 🇰🇷 [한국어](README.ko.md) | 🇯🇵 [日本語](README.ja.md) | 🇨🇳 [中文](README.zh.md)

# Claude を活用した医学学術論文執筆ワークフロー

Claude AI を活用した医学学術論文執筆のための体系的なワークフローシステムです。

## バージョン

**v0.3.0** (2026-03-09)

---

## 概要

本プロジェクトは、Claude AI の支援による医学学術論文執筆のための包括的なフレームワークを提供します：

- **体系的なプロジェクト構成** — 原稿、データ、参考文献の管理
- **専門家チームシミュレーション** — 臨床専門家、方法論専門家、統計学者、編集者
- **統計分析ワークフロー** — Python スクリプトの自動生成
- **品質管理手順** — 最低3ラウンドの検証（6ラウンド推奨）
- **研究タイプ別チェックリスト** — STROBE、CONSORT、PRISMA、CARE 等
- **PubMed 検索ツール** — 内蔵 Python スクリプト（MCP・外部パッケージ不要）
- **スラッシュコマンド** — エビデンス登録（`/search-evidence`、`/import-doi`）

---

## プロジェクト構成

```
project/
├── CLAUDE.md                     # コアルール・設定
├── README.md                     # 英語版 README
├── docs/                         # 参照ガイド
│   ├── writing_guide.md          # セクション別執筆ガイド
│   ├── expert_roles.md           # 専門家チームの役割と責任
│   ├── checklist_guide.md        # 研究タイプ別チェックリスト
│   ├── qc_guide.md               # 品質管理手順
│   ├── statistical_analysis_guide.md  # 統計分析ガイド
│   ├── evidence_guide.md         # エビデンス作成ガイド
│   └── docx_guide.md            # DOCX 変換ガイド
├── knowledge/                    # 参考資料
│   ├── evidence.md               # 参考文献要約集
│   ├── pdf/                      # 原本 PDF ファイル
│   └── summaries/                # 個別論文の詳細要約
├── data/                         # 統計分析
│   ├── raw_data.csv              # 元データセット
│   ├── analysis_plan.md          # 自動生成分析計画
│   └── py/                       # Python 分析スクリプト
├── scripts/                      # ユーティリティスクリプト
│   └── search_pubmed.py          # PubMed 検索ツール（外部依存なし）
├── results/                      # 分析結果
├── drafts/                       # 原稿セクション、表、図
│   ├── table_*.md
│   └── figures/
├── review/                       # QC 文書
│   └── qc_log.md
└── output/                       # 最終原稿
    ├── title_page_YYMMDD.docx
    ├── manuscript_YYMMDD.docx
    └── table_N_YYMMDD.docx
```

---

## クイックスタート

1. **設定**：`CLAUDE.md` に研究テーマ、対象ジャーナル、研究デザインを入力します
2. **参考文献**：`/search-evidence [クエリ]` または `python3 scripts/search_pubmed.py` で PubMed を検索し、`knowledge/evidence.md` に登録します
3. **データ分析**：`data/` フォルダにデータを配置し、統計分析を実行します
4. **執筆**：推奨順序に従ってセクションを作成します（Methods → Results → Introduction → Discussion）
5. **品質管理**：投稿前に最低3ラウンドの QC を実施します（6ラウンド推奨）
6. **最終化**：原稿を DOCX にコンパイルします（`docs/docx_guide.md` 参照）

---

## 主な機能

### 専門家チームシミュレーション
- **Dr. Researcher A**：臨床的視点（Introduction、Discussion）
- **Dr. Researcher B**：方法論（Methods、Results、Tables）
- **Dr. Statistician**：統計検証、節約原則、MCID/NNT 評価
- **Dr. Editor**：最終校正、一貫性チェック

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
- Round 2：参考文献の検証
- Round 3：論理的フロー
- Round 4：用語・略語・時制の一貫性
- Round 5：統計的品質
- Round 6：批判的レビュー（過大主張、論理的誤謬、バイアス、一般化可能性）

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
| [docs/writing_guide.md](docs/writing_guide.md) | セクション別執筆指針 |
| [docs/expert_roles.md](docs/expert_roles.md) | 専門家チームの説明 |
| [docs/checklist_guide.md](docs/checklist_guide.md) | STROBE、CONSORT、PRISMA、CARE チェックリスト |
| [docs/qc_guide.md](docs/qc_guide.md) | 品質管理手順（6ラウンド） |
| [docs/statistical_analysis_guide.md](docs/statistical_analysis_guide.md) | 統計分析ガイド（節約原則、MCID、サブグループ分析） |
| [docs/evidence_guide.md](docs/evidence_guide.md) | エビデンス作成ガイド（形式、要約方法、ワークフロー） |
| [docs/docx_guide.md](docs/docx_guide.md) | DOCX 変換ガイド（書式、テーブルスタイル、命名規則） |
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
