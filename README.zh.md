🇺🇸 [English](README.md) | 🇰🇷 [한국어](README.ko.md) | 🇯🇵 [日本語](README.ja.md) | 🇨🇳 [中文](README.zh.md)

# 基于 Claude 的医学学术论文写作工作流

基于 Claude AI 辅助的医学学术论文写作系统化工作流。

## 版本

**v0.3.0** (2026-03-09)

---

## 概述

本项目提供了一个借助 Claude AI 辅助撰写医学学术论文的综合框架：

- **系统化项目组织** — 稿件、数据、参考文献管理
- **专家团队模拟** — 临床专家、方法学专家、统计学家、编辑
- **统计分析工作流** — Python 脚本自动生成
- **质量控制流程** — 至少3轮验证（推荐6轮）
- **研究类型专用清单** — STROBE、CONSORT、PRISMA、CARE 等
- **PubMed 搜索工具** — 内置 Python 脚本（无需 MCP 或外部包）
- **斜杠命令** — 证据文献注册（`/search-evidence`、`/import-doi`）

---

## 项目结构

```text
project/
├── CLAUDE.md                     # 核心规则与配置
├── README.md                     # 英文 README
├── docs/                         # 参考指南
│   ├── writing_guide.md          # 分节写作指南
│   ├── expert_roles.md           # 专家团队角色与职责
│   ├── checklist_guide.md        # 研究类型专用清单
│   ├── qc_guide.md               # 质量控制流程
│   ├── statistical_analysis_guide.md  # 统计分析指南
│   ├── evidence_guide.md         # 证据文献编写指南
│   └── docx_guide.md            # DOCX 转换指南
├── knowledge/                    # 参考资料
│   ├── evidence.md               # 参考文献摘要汇编
│   ├── pdf/                      # 原始 PDF 文件
│   └── summaries/                # 单篇论文详细摘要
├── data/                         # 统计分析
│   ├── raw_data.csv              # 原始数据集
│   ├── analysis_plan.md          # 自动生成的分析计划
│   └── py/                       # Python 分析脚本
├── scripts/                      # 实用脚本
│   └── search_pubmed.py          # PubMed 搜索工具（无外部依赖）
├── results/                      # 分析输出
├── drafts/                       # 稿件章节、表格、图表
│   ├── table_*.md
│   └── figures/
├── review/                       # QC 文档
│   └── qc_log.md
└── output/                       # 最终稿件
    ├── title_page_YYMMDD.docx
    ├── manuscript_YYMMDD.docx
    └── table_N_YYMMDD.docx
```

---

## 快速开始

1. **设置**：在 `CLAUDE.md` 中填写研究主题、目标期刊和研究设计
2. **参考文献**：使用 `/search-evidence [关键词]` 或 `python3 scripts/search_pubmed.py` 搜索 PubMed 并注册到 `knowledge/evidence.md`
3. **数据分析**：将数据放入 `data/` 文件夹并运行统计分析
4. **撰写初稿**：按推荐顺序撰写各章节（Methods → Results → Introduction → Discussion）
5. **质量控制**：提交前至少进行3轮 QC 检查（推荐6轮）
6. **最终定稿**：将稿件编译为 DOCX（参见 `docs/docx_guide.md`）

---

## 主要功能

### 专家团队模拟

- **Dr. Researcher A**：临床视角（Introduction、Discussion）
- **Dr. Researcher B**：方法学（Methods、Results、Tables）
- **Dr. Statistician**：统计验证、节约原则、MCID/NNT 评估
- **Dr. Editor**：最终润色、一致性检查

### 冗余预防

- 避免三重重复（Results 正文 + Table + Figure）
- Table 与 Figure 选择的明确指南
- 标准表格结构（Table 1：人口统计学、Table 2：主要结果）

### 统计分析指南（v0.3.0）

- 统计节约原则（Statistical Parsimony）— RCT Table 1 省略 p 值
- 分析层级 — Primary > Secondary > Exploratory
- 临床显著性 — Effect size、MCID、NNT
- 亚组分析规则 — 必须进行 Interaction test
- 非显著结果报告指南

### 质量控制（6轮）

- Round 1：数值一致性
- Round 2：参考文献验证
- Round 3：逻辑流程
- Round 4：术语/缩写/时态一致性
- Round 5：统计质量
- Round 6：批判性审查（过度声明、逻辑谬误、偏倚、可推广性）

### PubMed 搜索工具

无需 MCP 即可搜索参考文献的内置 Python 脚本（`scripts/search_pubmed.py`）：

```bash
python3 scripts/search_pubmed.py search "endoscopic spine surgery"  # 搜索
python3 scripts/search_pubmed.py fetch 35486828                     # 按 PMID 获取
python3 scripts/search_pubmed.py doi 10.1016/j.spinee.2023.01.005  # 按 DOI 获取
python3 scripts/search_pubmed.py related 35486828                   # 相关论文
```

Claude 集成斜杠命令：

- `/search-evidence [关键词]` - 搜索、选择并注册到 evidence.md
- `/import-doi [doi]` - 通过 DOI 获取并注册到 evidence.md

---

## 文档列表

| 文档 | 用途 |
| ---- | ---- |
| [CLAUDE.md](CLAUDE.md) | 核心规则与项目配置 |
| [docs/writing_guide.md](docs/writing_guide.md) | 分节写作指导 |
| [docs/expert_roles.md](docs/expert_roles.md) | 专家团队说明 |
| [docs/checklist_guide.md](docs/checklist_guide.md) | STROBE、CONSORT、PRISMA、CARE 清单 |
| [docs/qc_guide.md](docs/qc_guide.md) | 质量控制流程（6轮） |
| [docs/statistical_analysis_guide.md](docs/statistical_analysis_guide.md) | 统计分析指南（节约原则、MCID、亚组分析） |
| [docs/evidence_guide.md](docs/evidence_guide.md) | 证据文献编写指南（格式、摘要方法、工作流） |
| [docs/docx_guide.md](docs/docx_guide.md) | DOCX 转换指南（格式、表格样式、命名规则） |
| [scripts/search_pubmed.py](scripts/search_pubmed.py) | PubMed 搜索脚本（NCBI E-utilities，无需外部包） |

---

## 系统要求

- Claude AI（Claude Code CLI 或 VSCode 扩展）
- Python 3.x（用于统计分析和 PubMed 搜索）
- 统计分析所需 Python 包：pandas、numpy、scipy、statsmodels、python-docx
- PubMed 搜索脚本（`scripts/search_pubmed.py`）仅使用 Python 标准库（无需额外包）

---

## 作者

**朴相旻 教授, M.D., Ph.D.**

骨科学教室，
首尔大学盆唐首尔大学医院，
首尔大学医学院

<https://sangmin.me/>

---

## 许可证

本作品基于**知识共享署名 4.0 国际许可协议（CC BY 4.0）**进行许可。

Copyright (c) 2026 Sang-Min Park, Seoul National University Bundang Hospital

### 您可以自由地

- **共享** — 以任何媒介或格式复制和重新分发材料
- **演绎** — 以任何目的重新混合、转换和基于材料进行创作

### 须遵守以下条件

- **署名** — 您必须给予适当的署名，提供许可协议链接，并注明是否进行了修改。

[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

许可协议全文：<https://creativecommons.org/licenses/by/4.0/legalcode>
