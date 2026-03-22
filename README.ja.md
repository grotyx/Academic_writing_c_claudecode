🇺🇸 [English](README.md) | 🇰🇷 [한국어](README.ko.md) | 🇯🇵 [日本語](README.ja.md) | 🇨🇳 [中文](README.zh.md)

# Claude を活用した医学学術論文執筆ワークフロー

Claude AI を活用した医学学術論文執筆のための体系的ワークフローシステムです。

## バージョン

**v0.3.0** (2026-03-09)

---

## 概要

本プロジェクトは、Claude AI を活用した医学学術論文執筆のための包括的フレームワークを提供します：

- **体系的プロジェクト構造** — 原稿、データ、参考文献の管理
- **専門家チームシミュレーション** — 臨床専門家、方法論専門家、統計学者、編集者
- **統計分析ワークフロー** — Python スクリプト自動生成
- **品質管理手順** — 最低3ラウンド（6ラウンド推奨）の検証
- **研究タイプ別チェックリスト** — STROBE、CONSORT、PRISMA、CARE 等
- **PubMed 検索ツール** — 内蔵 Python スクリプト（MCP・外部パッケージ不要）
- **スラッシュコマンド** — エビデンス登録（`/search-evidence`、`/import-doi`）

---

## プロジェクト構造

```text
project/
├── CLAUDE.md                     # コアルール＆設定
├── README.md                     # 英語 README
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
│   └── summaries/                # 個別論文詳細要約
├── data/                         # 統計分析
│   ├── raw_data.csv              # 元データセット
│   ├── analysis_plan.md          # 自動生成分析計画
│   └── py/                       # Python 分析スクリプト
├── scripts/                      # ユーティリティスクリプト
│   └── search_pubmed.py          # PubMed 検索ツール（外部パッケージ不要）
├── results/                      # 分析結果
├── drafts/                       # 原稿セクション、テーブル＆図
│   ├── table_*.md
│   └── figures/
├── review/                       # QC ドキュメント
│   └── qc_log.md
└── output/                       # 最終原稿
    ├── title_page_YYMMDD.docx
    ├── manuscript_YYMMDD.docx
    └── table_N_YYMMDD.docx
```

---

## クイックスタート

1. **設定**: `CLAUDE.md` に研究テーマ、対象ジャーナル、研究デザインを入力
2. **参考文献**: `/search-evidence [検索語]` または `python3 scripts/search_pubmed.py` で PubMed 検索し `knowledge/evidence.md` に登録
3. **データ分析**: `data/` フォルダにデータを配置し統計分析を実行
4. **原稿執筆**: 推奨順序でセクションを執筆（Methods → Results → Introduction → Discussion）
5. **品質管理**: 投稿前に最低3ラウンドの QC を実施（6ラウンド推奨）
6. **最終作業**: 原稿を DOCX にコンパイル（`docs/docx_guide.md` 参照）

---

## 主な機能

### 専門家チームシミュレーション

- **Dr. Researcher A**: 臨床的視点（Introduction、Discussion）
- **Dr. Researcher B**: 方法論（Methods、Results、Tables）
- **Dr. Statistician**: 統計検証
- **Dr. Editor**: 最終校正、一貫性チェック

### 重複防止

- 三重重複の防止（Results 本文 + Table + Figure）
- Table vs Figure 選択のための明確なガイドライン
- 標準テーブル構造（Table 1: 人口統計、Table 2: 主要結果）

### PubMed 検索ツール

MCP 不要の内蔵 Python スクリプト（`scripts/search_pubmed.py`）：

```bash
python3 scripts/search_pubmed.py search "endoscopic spine surgery"  # 検索
python3 scripts/search_pubmed.py fetch 35486828                     # PMID で取得
python3 scripts/search_pubmed.py doi 10.1016/j.spinee.2023.01.005  # DOI で取得
python3 scripts/search_pubmed.py related 35486828                   # 関連論文
```

Claude 統合スラッシュコマンド：

- `/search-evidence [検索語]` - 検索、選択、evidence.md に登録
- `/import-doi [doi]` - DOI で取得し evidence.md に登録

---

## ドキュメント一覧

| ドキュメント | 用途 |
| ---- | ---- |
| [CLAUDE.md](CLAUDE.md) | コアルール＆プロジェクト設定 |
| [docs/writing_guide.md](docs/writing_guide.md) | セクション別執筆ガイド |
| [docs/expert_roles.md](docs/expert_roles.md) | 専門家チーム説明 |
| [docs/checklist_guide.md](docs/checklist_guide.md) | STROBE、CONSORT、PRISMA、CARE チェックリスト |
| [docs/qc_guide.md](docs/qc_guide.md) | 品質管理手順（6ラウンド） |
| [docs/statistical_analysis_guide.md](docs/statistical_analysis_guide.md) | 統計分析ワークフロー |
| [docs/evidence_guide.md](docs/evidence_guide.md) | エビデンス作成ガイド（形式、要約方法、ワークフロー） |
| [docs/docx_guide.md](docs/docx_guide.md) | DOCX 変換ガイド（書式、テーブルスタイル、命名規則） |
| [scripts/search_pubmed.py](scripts/search_pubmed.py) | PubMed 検索スクリプト（NCBI E-utilities、外部パッケージ不要） |

---

## 要件

- Claude AI（Claude Code CLI または VSCode 拡張機能）
- Python 3.x（統計分析および PubMed 検索用）
- Python パッケージ（統計分析）: pandas、numpy、scipy、statsmodels、python-docx
- PubMed 検索スクリプト（`scripts/search_pubmed.py`）は Python 標準ライブラリのみ使用（追加パッケージ不要）

---

## 著者

**朴相敏 教授, 医学博士**

ソウル大学校盆唐病院 整形外科,
ソウル大学校 医科大学

<https://sangmin.me/>

---

## ライセンス

この著作物は **クリエイティブ・コモンズ 表示 4.0 国際ライセンス（CC BY 4.0）** の下に提供されています。

Copyright (c) 2026 Sang-Min Park, Seoul National University Bundang Hospital

### 許可される利用

- **共有** — いかなる媒体や形式でも資料を複製・再配布できます
- **翻案** — いかなる目的でも資料をリミックス・変形・再加工できます

### 利用条件

- **表示** — 適切なクレジットを表示し、ライセンスへのリンクを提供し、変更があった場合はその旨を示す必要があります

[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

ライセンス全文: <https://creativecommons.org/licenses/by/4.0/legalcode>
