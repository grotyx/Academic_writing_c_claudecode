🇺🇸 [English](README.md) | 🇰🇷 [한국어](README.ko.md) | 🇯🇵 [日本語](README.ja.md) | 🇨🇳 [中文](README.zh.md)

# 基于 Claude 的医学学术论文写作工作流

一套利用 Claude AI 进行医学学术论文写作的系统化工作流框架。

## 版本

**v0.3.0** (2026-03-09)

---

## 概述

本项目提供了一套利用 Claude AI 进行医学学术论文写作的综合框架：

- **系统化项目结构** — 稿件、数据、参考文献管理
- **专家团队模拟** — 临床专家、方法学专家、统计学家、编辑
- **统计分析工作流** — 自动生成 Python 分析脚本
- **质量控制流程** — 最少3轮（推荐6轮）验证
- **研究类型专用清单** — STROBE、CONSORT、PRISMA、CARE 等
- **PubMed 检索工具** — 内置 Python 脚本（无需 MCP 或外部包）
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
│   ├── evidence_guide.md         # 证据撰写指南
│   └── docx_guide.md            # DOCX 转换指南
├── knowledge/                    # 参考资料
│   ├── evidence.md               # 参考文献摘要汇编
│   ├── pdf/                      # 原始 PDF 文件
│   └── summaries/                # 单篇论文详细摘要
├── data/                         # 统计分析
│   ├── raw_data.csv              # 原始数据集
│   ├── analysis_plan.md          # 自动生成的分析计划
│   └── py/                       # Python 分析脚本
├── scripts/                      # 工具脚本
│   └── search_pubmed.py          # PubMed 检索工具（无需外部包）
├── results/                      # 分析输出
├── drafts/                       # 稿件章节、表格与图表
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

1. **配置**: 在 `CLAUDE.md` 中填写研究课题、目标期刊和研究设计
2. **参考文献**: 使用 `/search-evidence [关键词]` 或 `python3 scripts/search_pubmed.py` 检索 PubMed 并注册到 `knowledge/evidence.md`
3. **数据分析**: 将数据放入 `data/` 文件夹并运行统计分析
4. **撰写初稿**: 按推荐顺序撰写各节（Methods → Results → Introduction → Discussion）
5. **质量控制**: 提交前至少进行3轮 QC（推荐6轮）
6. **定稿**: 将稿件编译为 DOCX（参见 `docs/docx_guide.md`）

---

## 主要功能

### 专家团队模拟

- **Dr. Researcher A**: 临床视角（Introduction、Discussion）
- **Dr. Researcher B**: 方法学（Methods、Results、Tables）
- **Dr. Statistician**: 统计验证
- **Dr. Editor**: 终稿润色、一致性检查

### 防止重复

- 避免三重重复（Results 正文 + Table + Figure）
- Table 与 Figure 选择的明确指南
- 标准表格结构（Table 1: 人口统计、Table 2: 主要结果）

### PubMed 检索工具

无需 MCP 的内置 Python 脚本（`scripts/search_pubmed.py`）：

```bash
python3 scripts/search_pubmed.py search "endoscopic spine surgery"  # 检索
python3 scripts/search_pubmed.py fetch 35486828                     # 按 PMID 获取
python3 scripts/search_pubmed.py doi 10.1016/j.spinee.2023.01.005  # 按 DOI 获取
python3 scripts/search_pubmed.py related 35486828                   # 相关文献
```

Claude 集成斜杠命令：

- `/search-evidence [关键词]` - 检索、选择并注册到 evidence.md
- `/import-doi [doi]` - 按 DOI 获取并注册到 evidence.md

---

## 文档列表

| 文档 | 用途 |
| ---- | ---- |
| [CLAUDE.md](CLAUDE.md) | 核心规则与项目配置 |
| [docs/writing_guide.md](docs/writing_guide.md) | 分节写作指南 |
| [docs/expert_roles.md](docs/expert_roles.md) | 专家团队说明 |
| [docs/checklist_guide.md](docs/checklist_guide.md) | STROBE、CONSORT、PRISMA、CARE 清单 |
| [docs/qc_guide.md](docs/qc_guide.md) | 质量控制流程（6轮） |
| [docs/statistical_analysis_guide.md](docs/statistical_analysis_guide.md) | 统计分析工作流 |
| [docs/evidence_guide.md](docs/evidence_guide.md) | 证据撰写指南（格式、摘要方法、工作流） |
| [docs/docx_guide.md](docs/docx_guide.md) | DOCX 转换指南（格式、表格样式、命名规则） |
| [scripts/search_pubmed.py](scripts/search_pubmed.py) | PubMed 检索脚本（NCBI E-utilities，无需外部包） |

---

## 系统要求

- Claude AI（Claude Code CLI 或 VSCode 扩展）
- Python 3.x（用于统计分析和 PubMed 检索）
- Python 包（统计分析）: pandas、numpy、scipy、statsmodels、python-docx
- PubMed 检索脚本（`scripts/search_pubmed.py`）仅使用 Python 标准库（无需额外包）

---

## 作者

**朴相敏 教授, 医学博士**

首尔大学盆唐医院 骨科,
首尔大学 医学院

<https://sangmin.me/>

---

## 许可证

本作品采用 **知识共享署名 4.0 国际许可协议（CC BY 4.0）** 进行许可。

Copyright (c) 2026 Sang-Min Park, Seoul National University Bundang Hospital

### 您可以自由地

- **共享** — 以任何媒介或格式复制和再分发本材料
- **演绎** — 以任何目的重新混合、转换和基于本材料进行创作

### 须遵守以下条款

- **署名** — 您必须给出适当的署名，提供许可证链接，并标明是否进行了修改

[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

许可证全文: <https://creativecommons.org/licenses/by/4.0/legalcode>
