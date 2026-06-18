🇺🇸 [English](README.md) | 🇰🇷 [한국어](README.ko.md) | 🇯🇵 [日本語](README.ja.md) | 🇨🇳 [中文](README.zh.md)

# 基于 Claude 的医学学术论文写作工作流

基于 Claude AI 辅助的医学学术论文写作系统化工作流。

## 版本

**v0.9.1** (2026-06-18)

---

## 概述

本项目提供了一个借助 Claude AI 辅助撰写医学学术论文的综合框架：

- **系统化项目组织** — 稿件、数据、参考文献管理
- **多论文项目支持** — 按论文分子文件夹整理
- **文件版本管理系统** — 日期默认、_v1、_REV1 样式
- **Revision 工作流** — 专用 revision 文件夹和文件命名规则
- **专家团队模拟** — 临床专家、方法学专家、统计学家、编辑
- **统计分析工作流** — Python 脚本自动生成
- **质量控制流程** — 至少3轮验证（推荐6轮）+ Revision QC 重跑工作流
- **研究类型专用清单** — STROBE、CONSORT、PRISMA、CARE 等
- **学术写作风格系统** — Style Reference Tables（Voice/Tense、Transition、Verb Upgrades、Common Corrections、Statistical Notation、Hedging）+ Writing Principles（Clarity/Conciseness/Objectivity/Consistency）
- **引用质量控制** — Claim→Citation Mapping（写作前将关键 claim 与证据文献对应）
- **Style anchor library**（`Style/`）— own、landmark、target-journal anchors，用于术语、语气、论证结构和期刊 house style
- **术语 registry**（`Style/terminology.md`）— preferred/forbidden terms、定义和使用 context
- **Drafting protocol**（`docs/drafting_protocol.md`）— outline → evidence-bound draft → style pass → QC
- **Manuscript linting**（`scripts/lint_manuscript.py`）— 自动检查术语、placeholder、过度声明和分节问题
- **Citation evidence checking**（`scripts/check_citations.py`）— 将 `[EVID:id]` 标签与 `knowledge/evidence.md` 对照
- **Data number checking**（`scripts/check_numbers.py`）— 将稿件/表格中的数字与 `results/*.csv` 对照
- **Phase gate ledger checking**（`scripts/check_gate.py`）— 如果 `review/gates/*.GATE.md` 没有必要的 PASS，则阻止进入下一步
- **Revision claim checking**（`scripts/check_revision_claims.py`）— 将 response letter 中的 `[CHANGE]` claim 与 revised manuscript 对照
- **LLM verifier prompt templates**（`docs/verifier_prompt_templates.md`）— constraint、semantic citation、data、logic/redundancy、revision-alignment 验证 prompt/schema
- **Author response DOCX generation**（`scripts/compile_response_docx.py`）— 将 DOCX-ready Markdown 转换为 `Author_response_220803_Final.docx` 参考样式
- **Author response Markdown template**（`docs/response_letter_template.md`）— 对齐 reviewer response、修改位置和 machine-readable `[CHANGE]` block
- **PubMed 搜索工具** — 内置 Python 脚本（无需 MCP 或外部包）
- **斜杠命令** — 证据文献注册（`/search-evidence`、`/import-doi`）

---

## 项目结构

```text
project/
├── CLAUDE.md                     # 核心规则与配置
├── AGENTS.MD                     # agent 启动规则；以 CLAUDE.md 为 source of truth
├── README.md                     # 英文 README
├── docs/                         # 参考指南
│   ├── writing_guide.md          # 分节写作指南
│   ├── drafting_protocol.md      # 必须遵循的 drafting sequence
│   ├── section_templates.md      # 分节 sentence patterns
│   ├── expert_roles.md           # 专家团队角色与职责
│   ├── checklist_guide.md        # 研究类型专用清单
│   ├── qc_guide.md               # 质量控制流程
│   ├── verification_protocol.md  # 验证门·3 Verifier·自主循环·门台账
│   ├── verifier_prompt_templates.md  # LLM verifier prompts and output schema
│   ├── statistical_analysis_guide.md  # 统计分析指南
│   ├── evidence_guide.md         # 证据文献编写指南
│   ├── revision_guide.md        # 审稿人回复指南
│   ├── response_letter_template.md  # DOCX-ready author response template
│   ├── figure_guide.md          # 图表生成指南
│   ├── docx_guide.md            # DOCX 转换指南
│   └── draft_plan_template.md    # Draft plan template
├── knowledge/                    # 参考资料
│   ├── evidence.md               # 参考文献摘要汇编
│   ├── pdf/                      # 原始 PDF 文件（gitignored, local only）
│   └── summaries/                # 单篇论文详细摘要
├── Style/                        # 与参考文献分离的 writing-style anchors
│   ├── PDF/                      # style analysis source PDFs（gitignored, local only）
│   ├── own/                      # 自己论文的 style anchors
│   ├── landmark/                 # 论证/framing anchors
│   ├── target_journal/           # target journal house-style anchors
│   ├── style_guide.md            # style anchor workflow and extraction rules
│   └── terminology.md            # preferred/forbidden terminology registry
├── data/                         # 统计分析
│   ├── raw_data.csv              # 原始数据集
│   ├── analysis_plan.md          # 分析计划（分析前必须创建）
│   └── py/                       # Python 分析脚本
├── scripts/                      # 实用脚本
│   ├── lint_manuscript.py        # manuscript terminology/style lint checks
│   ├── check_citations.py        # evidence citation gate
│   ├── check_numbers.py          # results CSV number gate
│   ├── check_gate.py             # phase gate ledger check
│   ├── check_revision_claims.py  # revision claim gate
│   ├── compile_response_docx.py  # Author response DOCX compiler
│   └── search_pubmed.py          # PubMed 搜索工具（无外部依赖）
├── results/                      # 分析输出
├── drafts/                       # 稿件章节、表格、图表
│   ├── draft_plan.md             # 稿件构成计划（撰写前必须）
│   ├── table_*.md
│   └── figures/
├── review/                       # QC 文档
│   ├── qc_log.md
│   └── gates/                    # 验证门台账 (phase_NN_*.GATE.md)
└── output/                       # 最终稿件
    ├── title_page_YYMMDD.docx
    ├── manuscript_YYMMDD.docx
    └── table_N_YYMMDD.docx
```

---

## 快速开始

1. **设置**：在 `CLAUDE.md` 中填写研究主题、目标期刊和研究设计
2. **参考文献**：使用 `/search-evidence [关键词]` 或 `python3 scripts/search_pubmed.py` 搜索 PubMed 并注册到 `knowledge/evidence.md`
3. **数据分析**：将数据放入 `data/` 文件夹 → 创建 `analysis_plan.md`（必须）→ 运行统计分析
4. **稿件计划**：将 `docs/draft_plan_template.md` 复制到 `drafts/draft_plan.md`，填写包含 Claim→Citation Mapping 的10项内容（推荐 Opus）
5. **撰写初稿**：遵循 `docs/drafting_protocol.md`，按推荐顺序撰写各章节
6. **验证门**：运行 citation、number、phase-gate、revision-claim checker，并在 `review/gates/` 中记录 PASS
7. **Revision response**：需要审稿人回复时，使用 `docs/response_letter_template.md` 撰写，并用 `scripts/compile_response_docx.py` 转换为 DOCX
8. **质量控制**：提交前至少进行3轮 QC 检查（推荐6轮）
9. **最终定稿**：将稿件编译为 DOCX（参见 `docs/docx_guide.md`）

---

## 主要功能

### 专家团队模拟

- **Dr. Researcher A**：临床视角（Introduction、Discussion）
- **Dr. Researcher B**：方法学（Methods、Results、Tables）
- **Dr. Statistician**：统计验证、节约原则、MCID/NNT 评估
- **Dr. Editor**：最终润色、一致性检查

### 撰写前必须计划（Planning Before Writing）

- **分析计划**（`data/analysis_plan.md`）：统计分析前必须 — 定义研究问题、评价指标、检验方法选择
- **稿件计划**（`drafts/draft_plan.md`）：章节撰写前必须 — 核心信息、论调/语气、必要参考文献、证据缺口、Table/Figure 计划、章节大纲
- 两项计划均需用户确认后方可进入下一阶段
- 多论文项目需为每篇论文单独制定计划

### 分阶段模型选择（Model Selection by Phase）

- **推荐 Opus**：Analysis Plan、Draft Plan、Revision — 需要战略性判断的阶段
- **默认 Sonnet（条件允许则用 Opus）**：撰写、Style Polish、QC — 基于计划的执行
- 核心原则："用 Opus 制定计划 → 用 Sonnet 撰写也 OK"

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
- Round 2：参考文献验证（+ 出现顺序编号、占位符检测、书目格式一致性、引用分布）
- Round 3：逻辑流程
- Round 4：术语/缩写/时态一致性
- Round 5：统计质量
- Round 6：批判性审查（过度声明、逻辑谬误、偏倚、可推广性）

### 验证哈尼斯

该哈尼斯将确定性 checker 与受约束的 LLM verifier prompt 结合使用：

- `scripts/check_citations.py`：将所有 `[EVID:id]` citation 与 `knowledge/evidence.md` 对照，并对未验证或未知 evidence 判定失败。
- `scripts/check_numbers.py`：将稿件和表格中的数字与 `results/*.csv` 对照。
- `scripts/check_gate.py`：确认 phase gate ledger 中存在 `status: PASS` 和必要 check。
- `scripts/check_revision_claims.py`：将 reviewer response 中的 `[CHANGE]` block 与 revised manuscript files 对照。
- `docs/verifier_prompt_templates.md`：提供 semantic support、logic、redundancy、revision-response alignment 的验证 prompt/schema。

### Author Response DOCX Workflow

Reviewer response 应按照 `docs/response_letter_template.md` 格式撰写，每一处稿件修改都记录为 `[CHANGE]` block。最终 response letter 可用以下命令编译：

```powershell
py scripts\compile_response_docx.py drafts\revision\REV1\response_letter_REV1.md
```

如果存在 `Author_response_220803_Final.docx`，compiler 会将其作为 reference style document。

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
| [docs/writing_guide.md](docs/writing_guide.md) | 分节写作指南 + Style Reference Tables + Writing Principles (4 Pillars) |
| [docs/drafting_protocol.md](docs/drafting_protocol.md) | outline → evidence-bound draft → style/QC pass 的必须 drafting workflow |
| [docs/section_templates.md](docs/section_templates.md) | 分节 paragraph function 和 sentence patterns |
| [docs/expert_roles.md](docs/expert_roles.md) | 专家团队说明 |
| [docs/checklist_guide.md](docs/checklist_guide.md) | STROBE、CONSORT、PRISMA、CARE 清单 |
| [docs/qc_guide.md](docs/qc_guide.md) | 质量控制流程（6轮） |
| [docs/verification_protocol.md](docs/verification_protocol.md) | 验证门·3 Verifier 章程·自主修正循环·门台账 |
| [docs/verifier_prompt_templates.md](docs/verifier_prompt_templates.md) | LLM semantic verifier prompts and structured output schema |
| [docs/statistical_analysis_guide.md](docs/statistical_analysis_guide.md) | 统计分析指南（节约原则、MCID、亚组分析） |
| [docs/evidence_guide.md](docs/evidence_guide.md) | 证据文献编写指南（格式、摘要方法、工作流） |
| [docs/revision_guide.md](docs/revision_guide.md) | 审稿人回复指南（回复信撰写、外交措辞、QC 重跑清单） |
| [docs/response_letter_template.md](docs/response_letter_template.md) | DOCX-ready author response Markdown template |
| [docs/figure_guide.md](docs/figure_guide.md) | 图表生成指南（DPI、调色板、Python模板） |
| [docs/docx_guide.md](docs/docx_guide.md) | DOCX 转换指南（格式、表格样式、命名规则） |
| [docs/draft_plan_template.md](docs/draft_plan_template.md) | Draft plan template — 10项内容、claim→citation tables、approval checklist |
| [Style/style_guide.md](Style/style_guide.md) | Style anchor workflow、extraction framework、PDF-to-MD mirror rules |
| [Style/terminology.md](Style/terminology.md) | Preferred/forbidden terminology registry |
| [Style/own/example_YYYY_Journal_keyword.md](Style/own/example_YYYY_Journal_keyword.md) | Own-paper style-anchor template |
| [scripts/lint_manuscript.py](scripts/lint_manuscript.py) | Manuscript lint script |
| [scripts/check_citations.py](scripts/check_citations.py) | 将 `[EVID:id]` citations 与 `knowledge/evidence.md` 对照 |
| [scripts/check_numbers.py](scripts/check_numbers.py) | 将稿件/表格中的数字与 `results/*.csv` 对照 |
| [scripts/check_gate.py](scripts/check_gate.py) | 验证 `review/gates/*.GATE.md` 的 status 和必要 check |
| [scripts/check_revision_claims.py](scripts/check_revision_claims.py) | 将 response-letter `[CHANGE]` claims 与 revised manuscript files 对照 |
| [scripts/compile_response_docx.py](scripts/compile_response_docx.py) | 将 `response_letter_REV*.md` 转换为 Author_response-style DOCX |
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

---

## 变更记录

### v0.9.1 (2026-06-18)

**多语言 README 与 Author Response DOCX 完成**

- 将英文、韩文、日文、中文 README 与验证哈尼斯 scripts 和 DOCX response workflow 同步。
- 添加 Author response Markdown template 与 `compile_response_docx.py` 用法。
- 文档化 citation evidence、numeric grounding、phase gate、revision claim 的 deterministic checker。
- 文档化用于 hallucination control、redundancy control、logic check、revision alignment 的 LLM verifier prompt-template。

### v0.9.0 (2026-06-16)

**验证哈尼斯** — 在每个 produce step 后执行 inline produce→verify→fix→re-verify gate

- 在 Phase 3/4/8 的每个产出物后设置验证 gate。
- 引入 Constraint、Citation、Data Verifier 与 gate ledger。
- 标准化 `[EVID:author_year]` citation tags 和 results CSV grounding。
- 通过 ghost-revision checker 检查 revision response 与 manuscript edit 的一致性。
