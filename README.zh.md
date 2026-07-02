🇺🇸 [English](README.md) | 🇰🇷 [한국어](README.ko.md) | 🇯🇵 [日本語](README.ja.md) | 🇨🇳 [中文](README.zh.md)

# 基于 Claude 的医学学术论文写作工作流

基于 Claude AI 辅助的医学学术论文写作系统化工作流。

## 版本

**v1.6.3** (2026-07-02)

[![tests](https://github.com/grotyx/Academic_writing_c_claudecode/actions/workflows/tests.yml/badge.svg)](https://github.com/grotyx/Academic_writing_c_claudecode/actions/workflows/tests.yml)

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
- **可靠的风格转换**（`/style-pass`）— 将粗糙初稿转换为契合的期刊风格：逐项目的 Style Spec（选定一篇范例）+ 逐章节转换 + 一个独立的 Style-Conformance verifier（自动修复循环）+ 一个可度量的 `scripts/check_style.py` 门（句长、引用密度、模糊化措辞）+ 在“make it academic”意图下自动触发（`docs/style_transform_protocol.md`）
- **引用质量控制** — Claim→Citation Mapping（写作前将关键 claim 与证据文献对应）
- **Style anchor library**（`Style/`）— own、landmark、target-journal anchors，用于术语、语气、论证结构和期刊 house style
- **术语 registry**（`Style/terminology.md`）— preferred/forbidden terms、定义和使用 context
- **Drafting protocol**（`docs/drafting_protocol.md`）— outline → evidence-bound draft → style pass → QC
- **Manuscript linting**（`scripts/lint_manuscript.py`）— 自动检查术语、placeholder、过度声明和分节问题
- **Citation evidence checking**（`scripts/check_citations.py`）— 将 `[EVID:id]` 标签与 `knowledge/evidence.md` 对照
- **Data number checking**（`scripts/check_numbers.py`）— 将稿件/表格中的数字与 `results/*.csv` 对照
- **Phase gate ledger checking**（`scripts/check_gate.py`）— 如果 `review/gates/*.GATE.md` 没有必要的 PASS，则阻止进入下一步
- **门时效性 / provenance**（`scripts/check_gate.py --verify-hash`）— PASS 时记录被验证产出物（以及 evidence/results）的 sha256；之后的编辑会使该门变为 **stale** 并强制重新验证，从而堵住 parallel-verifier 漏洞
- **门交叉校验**（`scripts/check_gate.py --cross-check`）— 对确定性维度（`citation` / `numbers` / `revision_claims`）就地重跑正本 checker，若台账记录的状态与实际不一致则使门 FAIL — 捕捉未实际运行而写入的伪 PASS 或 stale PASS（源不可达时 loud FAIL）
- **Revision claim checking**（`scripts/check_revision_claims.py`）— 将 response letter 中的 `[CHANGE]` claim 与 revised manuscript 对照
- **LLM verifier prompt templates**（`docs/verifier_prompt_templates.md`）— constraint、semantic citation、data、logic/redundancy、style-conformance、citation-stance、revision-alignment 验证 prompt/schema
- **引用辅助** — `/suggest-citation`（为某条 claim 找到最匹配的 `[EVID:id]`）、`/verify-claims`（通过 `scripts/extract_claims.py` 生成逐句的 SUPPORTED/PARTIAL/UNSUPPORTED claim 地图）、`/cite-stance`（支持/反驳/仅提及，Scite 风格），以及 `/evidence-table`（通过 `scripts/evidence_table.py` 生成一张“纳入研究汇总”表，Elicit 风格）（`docs/citation_assist_protocol.md`）
- **知识图谱集成**（可选）— medical-kag MCP（GraphRAG）作为上游的发现 / 冲突 / GRADE 综合 / 参考文献引擎，同时 `knowledge/evidence.md` 保持权威正本，`scripts/search_pubmed.py` 作为回退（`docs/medical_kag_protocol.md`）
- **流程强制执行 hooks**（`scripts/hooks/`）— SessionStart 契约注入、PreToolUse 计划优先门、PostToolUse 风格/术语 lint，以及 UserPromptSubmit 风格自动触发
- **一键验证**（`/verify`、`scripts/verify_all.py`）— 一并运行 citation + number + gate 检查
- **Author response DOCX generation**（`scripts/compile_response_docx.py`）— 将 DOCX-ready Markdown 转换为 `Author_response_220803_Final.docx` house style
- **Author response Markdown template**（`docs/response_letter_template.md`）— 对齐 reviewer response、修改位置和 machine-readable `[CHANGE]` block
- **PubMed 搜索工具** — 内置 Python 脚本（无需 MCP 或外部包）
- **合著者辩论**（`/paper-debate`）— 写作前的 Claude–Codex 讨论，用于分析计划、draft plan、论证结构与审稿人回应（`docs/debate_protocol.md`）
- **多模型批判性评审**（`/critical-review`）— 写作后由 Claude 子代理、Codex、OpenRouter 模型进行 senior reviewer/editor 级别的对抗性评审，按共识度 × 严重度排序（`docs/critical_review_protocol.md`）
- **主编 desk-screen**（`/editor-review`）— 超越机械式 QC 的 high-impact 期刊主编实质评估：识别论文所属领域，并以该领域 high-impact 期刊的实际刊文水准进行基准比较，判定临床有效性、scope 契合度与分析充分性 → `SEND FOR PEER REVIEW`/`BORDERLINE`/`DESK REJECT` 结论 + 为具备竞争力需补充的内容（或现实的下层期刊）。单个 Opus 子代理或多模型 panel；可选 medical-kag 基准（`docs/critical_review_protocol.md` §5）
- **AI-Draft De-bloat** — 去除 AI 痕迹（空洞的 `-ing` 分析、AI 词汇、signposting）的 writing-guide 流程，在保留 disclosure 的同时让文本读起来自然（`docs/writing_guide.md`）
- **斜杠命令** — 证据文献注册（`/search-evidence`、`/import-doi`）

---

## 项目结构

```text
project/
├── CLAUDE.md                     # 核心规则与配置
├── AGENTS.MD                     # agent 启动规则；以 CLAUDE.md 为 source of truth
├── README.md                     # 英文 README
├── .gitattributes                # 换行符策略 (text=auto eol=lf；防止 OneDrive/Windows 同步导致的 CRLF 变更)
├── docs/                         # 参考指南
│   ├── writing_guide.md          # 分节写作指南
│   ├── drafting_protocol.md      # 必须遵循的 drafting sequence
│   ├── section_templates.md      # 分节 sentence patterns
│   ├── expert_roles.md           # 专家团队角色与职责
│   ├── checklist_guide.md        # 研究类型专用清单
│   ├── qc_guide.md               # 质量控制流程
│   ├── verification_protocol.md  # 验证门·4 Verifier·自主循环·门台账
│   ├── verifier_prompt_templates.md  # LLM verifier prompts and output schema
│   ├── statistical_analysis_guide.md  # 统计分析指南
│   ├── evidence_guide.md         # 证据文献编写指南
│   ├── revision_guide.md        # 审稿人回复指南
│   ├── response_letter_template.md  # DOCX-ready author response template
│   ├── figure_guide.md          # 图表生成指南
│   ├── docx_guide.md            # DOCX 转换指南
│   ├── draft_plan_template.md    # Draft plan template
│   ├── debate_protocol.md        # Claude–Codex 合著者辩论流程
│   ├── critical_review_protocol.md  # 外部多模型对抗性评审
│   ├── style_transform_protocol.md  # /style-pass 转换 + Style verifier
│   ├── style_spec_template.md       # Style Spec 模板（绑定一篇范例）
│   ├── citation_assist_protocol.md  # 引用推荐 / 核验 / 立场 / 表格
│   └── medical_kag_protocol.md      # medical-kag MCP（GraphRAG）；evidence.md 为正本
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
│   ├── search_pubmed.py          # PubMed 搜索工具（无外部依赖）
│   ├── check_style.py            # 对照 Style Spec 的可度量风格门
│   ├── extract_claims.py         # 抽取带 [EVID:id] 标记的句子（claim 核验）
│   ├── evidence_table.py         # 结构化研究记录 → markdown 对比表
│   ├── verify_all.py             # /verify —— 一次运行 citation + number（+ gate）
│   ├── critical_review.py        # OpenRouter multi-model adversarial caller
│   ├── critical_models.txt       # OpenRouter model list (externalized)
│   ├── critical_prompts/         # Adversarial prompt single-source (manuscript.txt, response.txt)
│   └── hooks/                    # 强制执行 hooks（enforce_gates、session_contract、lint_on_edit、style_intent）
├── tests/                        # 验证脚本的 pytest 测试套件
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
2. **参考文献**：使用 `/search-evidence [关键词]` 或 `py scripts\search_pubmed.py` 搜索 PubMed 并注册到 `knowledge/evidence.md`
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

### 合著者协作（v0.9.3 新增）

两个互补的 Codex/多模型功能分别置于写作过程的前后：

- **`/paper-debate <主题>`** — 写作*之前*。Claude 与 Codex 作为合著者，在有界的若干轮内（共识上限 3）就分析方法、draft-plan 核心信息、论证结构或审稿人回应策略展开辩论。辩论日志保存于 `review/debates/`，达成一致的结论作为下一步产出的输入。Codex 不可用时回退为 Claude 单独执行。参见 `docs/debate_protocol.md`。
- **`/critical-review <对象>`** — 写作*之后*。完成的稿件（或 response letter）由全新的 Claude 子代理、Codex 和 OpenRouter 模型（默认 `minimax/minimax-m3`、`z-ai/glm-5.2`）的任意组合并行攻击。每位评审者均以 **senior peer-reviewer / editor-in-chief 级别** 受提示 — 越过表层缺陷，追问设计是否稳健、数据是否支持结论、是否值得发表。发现结果按 **共识度 × 严重度**（Critical / Important / Minor）合并排序，保存于 `review/critical/`。参见 `docs/critical_review_protocol.md`。

对抗性提示作为单一正本置于 `scripts/critical_prompts/`（`manuscript.txt`、`response.txt`）；OpenRouter 脚本、Claude 子代理和 Codex 均读取同一组文件。OpenRouter 访问使用 `OPENROUTER_API_KEY`（设置于 `.claude/settings.local.json`，gitignored）；缺失时跳过 OpenRouter，其余评审者继续。

### AI-Draft De-bloat（v0.9.3 新增）

`docs/writing_guide.md` 中的一道流程（在 Phase 5 对 AI 撰写的初稿应用），用于去除 AI 文风的痕迹 — 空洞的 `-ing`「表层分析」从句、AI 偏好的词汇以及过度的 signposting — 同时明确 **排除** 那些会合理冲突的模式（必要的 hedging、copula、被动语态）。AI 参与仍会被声明；此流程只是让已声明的 AI 协助不至于读起来臃肿乏味。

### 验证加固（v1.0.0 新增）

借鉴 "superpowers" skills 框架、聚焦于验证门的改进：

- **并行 verifier + Constraint 优先。** 四个章节门 verifier（Constraint / Citation / Data / Logic）针对冻结的产出物并发执行；验证过程中不编辑该产出物，FAIL 时优先修复 Constraint（spec 合规性）发现的问题。参见 `docs/verification_protocol.md`（v0.3.0）。
- **门时效性 / provenance**（`scripts/check_gate.py`）。PASS 时，门台账记录被验证产出物的 sha256（对于承载 citation 和 number 的门，还记录 `evidence` / `results`；revision 时必需）。`check_gate.py --verify-hash LABEL=PATH` 会重新计算哈希，若文件在 PASS 之后发生变更，则将该门判定为 **stale** 并失败 — 从而堵住「PASS 之后的编辑悄无声息地通过重新检查」的漏洞。`--compute-hash PATH` 用于填充 provenance 字段。在工具层面为可选启用，在文档化的门命令中为标准用法。
- **STOP 信号。** CLAUDE.md 中的 anti-rationalization 表格捕捉 verifier 无法发现的、人类层面的偷懒（「这个数字大概没问题」→ 去查 CSV；「我已经通过了」→ 产出物已变更即为 stale）。
- **苏格拉底式 draft-plan 头脑风暴。** `docs/draft_plan_template.md` 中的「Step 0」在填写计划之前，每次一个问题地厘清论文意图 — 与 `/paper-debate` 不同，它作为 R0 准备为后者提供输入。
- **审稿人回复分诊。** `docs/revision_guide.md` 为每条审稿人意见指定 accept / partial / rebut 立场，并映射到 `[CHANGE]` 标记和 ghost-revision 门。
- **命令 `use-when` 指引。** 现在每个 `.claude/commands/*.md` 都声明了应触发它的情境。

### Author Response DOCX Workflow

Reviewer response 应按照 `docs/response_letter_template.md` 格式撰写，每一处稿件修改都记录为 `[CHANGE]` block。最终 response letter 可用以下命令编译：

```powershell
py scripts\compile_response_docx.py drafts\revision\REV1\response_letter_REV1.md
```

compiler 会复现 `Author_response_220803_Final.docx` 的 house style — Times New Roman 11 pt，response/位置/修改文本行为 bold，正文为 justified。它不会将该 .docx 文件作为模板读取，格式是内置的。

### PubMed 搜索工具

无需 MCP 即可搜索参考文献的内置 Python 脚本（`scripts/search_pubmed.py`）：

```bash
py scripts\search_pubmed.py search "endoscopic spine surgery"  # 搜索
py scripts\search_pubmed.py fetch 35486828                     # 按 PMID 获取
py scripts\search_pubmed.py doi 10.1016/j.spinee.2023.01.005  # 按 DOI 获取
py scripts\search_pubmed.py related 35486828                   # 相关论文
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
| [docs/verification_protocol.md](docs/verification_protocol.md) | 验证门·4 Verifier 章程·自主修正循环·门台账 |
| [docs/verifier_prompt_templates.md](docs/verifier_prompt_templates.md) | LLM semantic verifier prompts and structured output schema |
| [docs/statistical_analysis_guide.md](docs/statistical_analysis_guide.md) | 统计分析指南（节约原则、MCID、亚组分析） |
| [docs/evidence_guide.md](docs/evidence_guide.md) | 证据文献编写指南（格式、摘要方法、工作流） |
| [docs/revision_guide.md](docs/revision_guide.md) | 审稿人回复指南（回复信撰写、外交措辞、QC 重跑清单） |
| [docs/response_letter_template.md](docs/response_letter_template.md) | DOCX-ready author response Markdown template |
| [docs/figure_guide.md](docs/figure_guide.md) | 图表生成指南（DPI、调色板、Python模板） |
| [docs/docx_guide.md](docs/docx_guide.md) | DOCX 转换指南（格式、表格样式、命名规则） |
| [docs/draft_plan_template.md](docs/draft_plan_template.md) | Draft plan template — 10项内容、claim→citation tables、approval checklist |
| [docs/debate_protocol.md](docs/debate_protocol.md) | Claude–Codex 合著者辩论流程（轮次、角色、日志、fallback） |
| [docs/critical_review_protocol.md](docs/critical_review_protocol.md) | 外部多模型对抗式评审（评审者池、共识度 × 严重度、fallback） |
| [Style/style_guide.md](Style/style_guide.md) | Style anchor workflow、extraction framework、PDF-to-MD mirror rules |
| [Style/terminology.md](Style/terminology.md) | Preferred/forbidden terminology registry |
| [Style/own/example_YYYY_Journal_keyword.md](Style/own/example_YYYY_Journal_keyword.md) | Own-paper style-anchor template |
| [scripts/lint_manuscript.py](scripts/lint_manuscript.py) | Manuscript lint script |
| [scripts/check_citations.py](scripts/check_citations.py) | 将 `[EVID:id]` citations 与 `knowledge/evidence.md` 对照 |
| [scripts/check_coverage.py](scripts/check_coverage.py) | 引用 coverage 审计 — **过度引用**（单一主张引用过多）·**未登记引用**为质量信号，各章节引用密度；未引用/未实现 claim 中立报告（属策展，非浪费） |
| [scripts/format_references.py](scripts/format_references.py) | `[EVID:id]` → 期刊格式参考文献列表（numbered/author-year）+ 将正文标签转换到同级 `*_formatted.md`；**不依赖 MCP**（Phase 7） |
| [scripts/check_abstract.py](scripts/check_abstract.py) | abstract↔正文数字一致性 — 标记 abstract 中存在但正文缺失的数字（Rule 3；默认排除 p 值）（Phase 6 QC Round 1） |
| [scripts/check_crossrefs.py](scripts/check_crossrefs.py) | Table/Figure 交叉引用检查 — 正文 "Table N"/"Figure N" 提及 ↔ 实际 `table_*.md`·figure legends：**broken reference**（主要信号）·未被引用项·首次提及顺序；默认 advisory，`--fail-on-*` 可门禁化（Phase 6 QC） |
| [scripts/check_abbreviations.py](scripts/check_abbreviations.py) | 缩写首次使用定义检查 — abstract/正文独立 scope（UNDEFINED / DEFINED_AFTER_USE / REDEFINED / SINGLE_USE）；以误报为前提的 advisory，`--allow`·`--strict`（Phase 6 QC） |
| [scripts/check_response_coverage.py](scripts/check_response_coverage.py) | 审稿意见回复覆盖检查 — 每个 `Comment N)` 必须有真实 `Response:`（拦截缺失/空/placeholder），`--comments` 与原始意见文件交叉核对；与 ghost-revision 门禁互补（Phase 8） |
| [scripts/check_numbers.py](scripts/check_numbers.py) | 将稿件/表格中的数字与 `results/*.csv` 对照 |
| [scripts/check_gate.py](scripts/check_gate.py) | 验证 `review/gates/*.GATE.md` 的 status 和必要 check |
| [scripts/check_revision_claims.py](scripts/check_revision_claims.py) | 将 response-letter `[CHANGE]` claims 与 revised manuscript files 对照 |
| [scripts/compile_response_docx.py](scripts/compile_response_docx.py) | 将 `response_letter_REV*.md` 转换为 Author_response-style DOCX |
| [scripts/search_pubmed.py](scripts/search_pubmed.py) | PubMed 搜索脚本（NCBI E-utilities，无需外部包） |
| [scripts/critical_review.py](scripts/critical_review.py) | OpenRouter 多模型对抗式评审调用（单个模型失败不会中断整体） |

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

### v1.6.3 (2026-07-02)

**三个机械性投稿错误检查器（advisory 优先）**

- **`scripts/check_crossrefs.py`** — 将正文 "Table N"/"Figure N" 提及与实际 `table_*.md`·figure legend 条目对照：broken reference（此前无任何机制捕捉的 desk-reject 诱因）·未被引用的 table/figure·首次提及顺序。支持 "Tables 1 and 2"·"Figure 2-4"·"Fig. 1A"；忽略代码围栏/HTML 注释；inventory 缺失时 loud 跳过而非全部误报。默认 advisory，`--fail-on-broken`/`--fail-on-unreferenced`/`--fail-on-order` 门禁化。
- **`scripts/check_abbreviations.py`** — 缩写首次使用定义 audit，abstract/正文独立 scope（期刊两者都要求）。发出 `ABBREV_UNDEFINED`/`ABBREV_DEFINED_AFTER_USE`/`ABBREV_REDEFINED`/始终 advisory 的 `ABBREV_SINGLE_USE`。刻意 advisory — 仅检测大写（2-6 字母、`-数字`、复数 s），统计缩写默认允许（CI、SD、OR、HR...）+ `--allow` 扩展；`--strict` 仅门禁定义问题。
- **`scripts/check_response_coverage.py`** — ghost-revision 门禁的另一面：回复信是否回答了**所有**审稿意见？解析 `Reviewer #N:`/`Comment N)`/`Response:` 结构，拦截缺失/空/`[placeholder]` 回复，`--comments` 与原始意见文件交叉核对（`COMMENT_UNANSWERED` 失败；原文件不可解析则警告，`--strict` 下失败）。默认 fail — 漏答意见是二值性缺陷。
- 设计原则（吸纳作者反馈）：机械化仅用于二值事实，判断留给人+LLM。文档更新（`CLAUDE.md`、`docs/qc_guide.md` §3.7/§4.2、`docs/revision_guide.md`）。40 个测试（共 262）。

### v1.6.2 (2026-07-02)

**Abstract Keywords 强制**

- `drafts/02_abstract.md` 末尾的 `**Keywords:**` 行既无 lint 也无明确规则，容易漏填。三层强制：(1) 模板中说明要求与示例；(2) `docs/writing_guide.md` § 02. Abstract 增加 Keywords 规则（3–6 个 MeSH 首选，分号分隔）；(3) `scripts/lint_manuscript.py` 识别 abstract 文件并触发 `KEYWORDS_MISSING`/`KEYWORDS_EMPTY`/`KEYWORDS_TOO_FEW`/`KEYWORDS_TOO_MANY` —— PostToolUse `lint_on_edit` 钩子已经在编辑时暴露 lint，因此一旦触碰 abstract，空 Keywords 立即被捕获。`;` 与 `,` 均可作为分隔符。7 个测试（共 222）。

### v1.6.1 (2026-06-30)

**`/editor-review` 使用与 `/critical-review` 相同的评审者选择器**

- editorial desk-screen 现在提供与 `/critical-review` 相同的模型选择 UX：对同一池（OpenRouter 4 个 `scripts/critical_models.txt` + 本地 Claude + Codex）的 `AskUserQuestion` 评审者选择器，仅 role 不同（`--role editor`，提示 `editor.txt`）。仅选 `Claude` 即单个 Opus 子代理（无需密钥）。Codex 通过 `codex:codex-rescue` 编排（并非 critical_review.py 的模型 —— 该脚本仅处理 OpenRouter + 本地 Claude）。更新命令 + protocol §5；同时修正 v1.6.0 中 changelog 已列而头部仍为 v1.5.10 的 ja/zh README。

### v1.6.0 (2026-06-29)

**Editorial desk-screen — high-impact 期刊主编评估（`/editor-review`）**

- 超越机械式 QC 与 reviewer 批判的新评估：**high-impact tier 主编 / 临床编辑 desk-screen**。识别论文所属领域，并以该领域 high-impact 期刊实际刊文水准做基准，判定 **临床有效性**（能否改变实践？是 MCID/effect 而非仅 p？）、**scope/novelty 契合度**、**方法与分析充分性** → `SEND FOR PEER REVIEW`/`BORDERLINE`/`DESK REJECT` + 为具备竞争力的 **具体补充验证**，或当门槛不现实时给出现实的下层期刊。
- 正本提示 `scripts/critical_prompts/editor.txt`（single source）。单个 Opus 子代理（无需密钥）**或** `scripts/critical_review.py --role editor` 多模型 panel；可选 medical-kag/PubMed 对真实 high-impact 文献做基准。以 `/editor-review` 暴露，记录于 `docs/critical_review_protocol.md` §5。判定型（advisory）— 不替代 grounded 门。新增测试。

### v1.5.10 (2026-06-28)

**测试覆盖强化 第二轮（MEDIUM 缺口）**

- 为全量审查的剩余覆盖缺口补充测试：`search_pubmed.py` 纯格式化函数（`format_citation` 作者数分支、`guess_study_design` 阶梯）；`check_abstract.py`（abstract 比正文更精确 → fail、整数匹配、多文件 body 聚合、issue 保留 comparator）；`check_numbers.py`（p 值 `>` comparator 的 pass/fail、对 heading/`Table N`/`Figure N`/年份的 `is_structural_number`）；`check_style.py`（`mean_sentence_length`/`paragraph_count` 容差、`split_sentences` 缩写/小数保护）；`check_citations.py`（`require_citations`、`fail_abstract_only` 开关）；`format_references.py`（`smith_2020a` 消歧、`--convert` 写入路径）；`check_coverage.py`（`--fail-on-unrealized`）。共 214 个测试（此前 170）。

### v1.5.9 (2026-06-28)

**enforcement 路径的测试覆盖强化**

- 全量审查的覆盖分析发现若干 *enforcement 契约* 没有测试，回归时可能被悄然停用。新增测试：`verify_all.py` 顶层 `OVERALL: PASS` 判定及其 `--cross-check`（以及 `--evidence`/`--results`）向 `check_gate.py` 的转发；`check_coverage.py` 的 `--fail-on-over-citation`/`--fail-on-unknown`/`--fail-on-uncited-verified` 退出码（默认 advisory vs 阻塞）；`check_revision_claims.py` 的 `--strict` 升级（缺失 original 默认为 warning，`--strict` 下为 failure）。共 170 个测试（此前 163）。

### v1.5.8 (2026-06-28)

**统一 `[EVID:id]` 正则（全量审查一致性修复）**

- `extract_claims.py` 使用了自有的宽松模式 `[EVID:([^\]]+)]`，而 `check_citations.py`（及复用它的 `check_coverage.py`、`format_references.py`）使用受限模式 `[A-Za-z0-9_.-]+`。有效的 slugified id 在两者下匹配一致，但该 drift 意味着畸形标签可能被抽取却未被校验/转换。现在 `extract_claims.py` 从 `check_citations.py` 导入正本 `EVID_RE`，四个脚本共享单一来源。对有效 id 无行为变化；163 tests green。

### v1.5.7 (2026-06-28)

**全量代码审计发现的缺陷修复**

- **Gate cross-check 在任何 live FAIL 时都使门 FAIL**（`check_gate.py`）— 此前若某 cross-check 维度在 live 重跑中 FAIL 且台账也记录 FAIL，门会视为"一致"而不追加失败，于是在该维度未同时作为 `--require-check` 时，**已损坏的产出物仍可能通过**。现在 live 确定性失败始终使门 FAIL，与台账无关。
- **plan-first 钩子不再在相对 cwd 下 fail-open**（`hooks/enforce_gates.py`、`hooks/lint_on_edit.py`）— 相对/缺失 `cwd` 会把路径归一化为 `drafts/05_results.md`（无前导斜杠），导致 `"/drafts/"`/`"/data/.../py/"` 检查不匹配而跳过 Rule 7/8 门。现在在检查前强制加前导斜杠。（latent：生产环境始终发送绝对 cwd。）
- 回归测试 +2（共 163）。

### v1.5.6 (2026-06-28)

**Abstract↔正文数字一致性 + medical-kag synthesis 工作流**

- **`scripts/check_abstract.py`** — 检查 abstract 中陈述的每个数字是否也出现在正文章节中（允许四舍五入），捕捉审稿人常指出的"仅出现在摘要"的数字。与 `check_numbers.py`（数字↔`results/*.csv`）互补；默认排除 p 值标记（`--include-p-values` 可纳入）。将 Rule 3 / QC Round 1 的 Abstract↔Methods↔Results↔Tables 一致性自动化。5 个测试。
- **medical-kag synthesis → Discussion/Limitations 工作流**（`docs/medical_kag_protocol.md`）— `compare_interventions` / `conflict synthesize` 输出丰富但 noisy（文献计量 outcome、空值、KG 归一化名称）→ 记录如何过滤到临床 outcome、为每个数字/引用做 grounding、并通过门，附 Discussion/Limitations 骨架。

### v1.5.5 (2026-06-28)

**CI：每次 push/PR 运行测试**

- **`.github/workflows/tests.yml`** — GitHub Actions 在每次 push 到 `main` 及 PR 时运行完整 pytest 套件，覆盖 Python 3.10/3.11/3.12，从而在合并前捕获破坏验证脚本的更改。README 顶部显示状态徽章。

### v1.5.4 (2026-06-28)

**不依赖 MCP 的 reference formatter（Phase 7）**

- **`scripts/format_references.py`** — 将撰写时的 `[EVID:id]` 标签转换为可投稿的参考文献列表与正文引用，仅读取 `knowledge/evidence.md`（无需 medical-kag）。两种风格：**numbered**（Vancouver — `[EVID:id]` → `[N]` 按首次出现顺序，列表同序编号）与 **author-year**（`(Author, Year)`，按字母排序列表）。`--convert` 将替换标签后的内容写入同级 `*_formatted.md`（不就地修改）；evidence.md 中不存在的引用保持不变并报告（且使退出码非零）。在已连接时与 medical-kag `reference` 工具互补。7 个测试（共 156）。

### v1.5.3 (2026-06-28)

**Coverage 审计重新聚焦于过度引用（弃用 orphan=浪费 的框定）**

- **过度引用检测** — `check_coverage.py` 现在标记单句中 `[EVID:id]` 引用数超过 `--max-citations-per-sentence`（默认 4）的情况（引用堆砌/padding）。它与**未登记引用**才是真正的质量信号 → `--fail-on-over-citation` / `--fail-on-unknown` 是有意义的阻塞标志。
- **将 orphan/未引用 重新定义为中立** — 已登记但未引用的参考是正常策展（只引用必要的），**并非浪费**。移除原先 "verified work unused" 的措辞；未引用 ref 与未实现 draft_plan 项作为中立信息报告。`--fail-on-uncited-verified` / `--fail-on-unrealized` 仅用于严格 full-use 策略，默认关闭。coverage 测试共 8 个（套件 149）。

### v1.5.2 (2026-06-27)

**引用 coverage / orphan 审计**

- **`scripts/check_coverage.py`** — 针对 `knowledge/evidence.md` 的 Phase 6 QC 审计：报告 **orphan reference**（已登记但从未被引用；verified-but-uncited 标记为"浪费的工作"）、各章节**引用密度**、**unknown citation**（被引用但未登记），以及在使用 `--draft-plan` 时报告**未实现 claim**（在 Claim→Citation 映射中计划但正文未引用）。默认 advisory，`--fail-on-orphan-verified` / `--fail-on-unrealized` / `--fail-on-unknown` 可使各维度变为阻塞。复用 `check_citations.py` 解析器以保持二者 lockstep。7 个测试（共 148）。

### v1.5.1 (2026-06-26)

**翻译 README 文档表对齐**

- 在韩文/日文/中文 README 的 File Roles 表中补齐缺失行，使其与 `README.md` 一致：`docs/debate_protocol.md`、`docs/critical_review_protocol.md`（三种语言均补），以及 `scripts/critical_review.py`（ja/zh）。仅文档变更，无代码变更。

### v1.5.0 (2026-06-26)

**门交叉校验（台账 ↔ live）+ 文档/版本自动同步策略**

- **门交叉校验**（`scripts/check_gate.py --cross-check LABEL=PATH`）— 对确定性维度（`citation` / `numbers` / `revision_claims`）就地重跑正本 checker，若台账记录的状态在任一方向上与实际不一致则使门 FAIL — 捕捉 stale/伪 `PASS`，源不可达时 loud FAIL。由 `scripts/verify_all.py` 转发，并接入正本门命令（`review/gates/_TEMPLATE.GATE.md`、`docs/verification_protocol.md` v0.3.0、CLAUDE.md）。新增 6 个回归测试（共 141）。
- **文档/版本同步 + 自动 commit-push 策略**（CLAUDE.md Rule 12）— harness 代码/缺陷变更时 bump 版本、更新受影响文档并自动提交/推送（对敏感或破坏性情形给出 STOP 条件）。

### v1.4.1 (2026-06-24)

**Template gate 加固 + `/verify` freshness 转发**

- **Template-aware plan gates** — `scripts/hooks/enforce_gates.py` 不再把未完成的 `analysis_plan.md` / `draft_plan.md` 模板或未勾选的审批项视为已批准 plan，并覆盖 `Write|Edit|MultiEdit`。合法的 citation-style `[N]` 文本会被保守处理，避免误报。
- **Fresh `/verify` gate checks** — `scripts/verify_all.py` 会把 `--verify-hash` 转发给 `check_gate.py`；README/CLAUDE/slash-command 示例也加入了 freshness 输入。
- **Windows/template hygiene** — PubMed 命令示例统一为 `py scripts\search_pubmed.py`，根目录生成的 DOCX 产物加入 ignore，并用回归测试覆盖新的 hook 与 freshness 转发行为。

### v1.4.0 (2026-06-24)

**引用立场 + 证据对比表（基于 GraphRAG）**

- **引用立场**（`/cite-stance [claim|section]`）—— 对每一个被引用的来源进行分类，判断它与某条 claim 的关系（支持 / 反驳 / 仅提及），从而让 Discussion 保持论证均衡；当存在反驳性证据却未被引用时，标记为“一边倒”（防止因遗漏而过度宣称的护栏）。新增 Citation-Stance verifier（`docs/verifier_prompt_templates.md`）；medical-kag 的 `conflict` 用于浮现缺失的反方证据，evidence.md 作为回退。Scite 风格，针对具体 claim。
- **证据对比表**（`/evidence-table [topic|ids]`）—— 汇总生成一张“纳入研究汇总”表（研究 / 设计 / n / 干预 / 结局 / 结果 / LoE），可用于 Discussion 或 PRISMA 补充材料。`scripts/evidence_table.py` 为确定性格式化工具；以 medical-kag 的结构化数据为主，evidence.md 作为回退。Elicit 风格。已补充测试。

### v1.3.0 (2026-06-24)

**引用辅助 —— 推荐 + 逐条 claim 核验（基于 GraphRAG）**

- **引用推荐**（`/suggest-citation [claim]`）—— 给定一条草稿 claim，通过 medical-kag 知识图谱（GraphRAG）检索出最匹配的 `[EVID:id]` 候选；当 MCP 不可用时，回退到 `knowledge/evidence.md` + `scripts/search_pubmed.py`。最终由作者选定，且新的来源必须先注册进 evidence.md（经 PMID/DOI 核验）才能被引用，从而保持 grounding 不被破坏。
- **逐条 claim 核验报告**（`/verify-claims [section]`）—— `scripts/extract_claims.py` 会抽取每一句带 `[EVID:id]` 标记的句子，随后由 Semantic-Citation Verifier 将每条分类为 SUPPORTED / PARTIAL / UNSUPPORTED，写入 `review/claim_verification.md`（一份 Phase 6 QC 阶段的“claim 地图”，比 `check_citations.py` 仅做存在性检查更为深入）。新增 `docs/citation_assist_protocol.md`；两项操作均可优雅降级到 evidence.md。已补充测试。

### v1.2.0 (2026-06-22)

**medical-kag MCP 集成 —— 知识图谱与 evidence.md 并行**

- **保持 grounding 的 KAG 集成** —— `medical-kag-remote` MCP（一个面向脊柱外科的知识增强图谱）作为上游的发现/分析/格式化引擎接入，而 `knowledge/evidence.md` 仍然是唯一权威的引用台账：图谱检索到的任何内容，都必须先注册为 `[EVID:id]`（经 PMID/DOI 核验）才能被引用，因此 `check_citations.py` 依然对所有引用进行把关。新增的 `docs/medical_kag_protocol.md` 将各工具映射到对应阶段 —— 发现 + 结构化抽取（Phase 1），用于 claim 和 Discussion 的证据链 / 干预对比 / GRADE 综合（Phase 3-4），冲突 / 过度声明防护（Phase 6），以及符合期刊格式的参考文献列表（Phase 7）。
- **附加式 + 回退机制** —— 该 MCP 绝不构成依赖：当它不可用时（例如未认证的远程会话），工作流会降级为 `scripts/search_pubmed.py` + 手动维护 evidence.md。已接入 CLAUDE.md（Rule 1、STOP 信号、Phase 1、Quick Commands）+ AGENTS.MD，以保持与 Codex 的一致性。

### v1.1.2 (2026-06-21)

**修复 —— hooks 以 UTF-8 读取 stdin（Windows 上的韩语意图）**

- `UserPromptSubmit` / `PreToolUse` / `PostToolUse` hooks 现在会将 stdin 重新配置为 UTF-8。在 Windows 上（默认 cp949），Claude Code 输出的 JSON 负载会被错误解码，因此非 ASCII 的提示词 —— 例如韩语自动触发语句“학술적으로 바꿔줘” —— 会静默地匹配失败。新增了一个端到端的 UTF-8 stdin 测试。

### v1.1.1 (2026-06-21)

**风格强制执行 —— 可度量的门 + 与 Codex 对齐**

- **确定性风格度量** —— `scripts/check_style.py`（`extract` / `check --spec`）测量字数、平均句长、段落数、引用密度和模糊化措辞，并标记出与 Style Spec 目标值的偏差 —— 即“面向风格的 check_numbers”。它已接入 `lint_on_edit.py`（当存在 Style Spec 时，在每次初稿编辑时浮现 `[STYLE-METRIC]` 偏差）以及 Phase 5/6 的门。已新增测试。
- **与 Codex 对齐 + 校准** —— `AGENTS.MD` 现在会指示非 Claude 的运行时显式运行风格转换流程（`check_style.py` + Style-Conformance verifier），因为这些 hooks 仅在 Claude Code 中可用。Style Spec 模板新增了一个 before→after 的校准示例（相比抽象规则，少量示例能更好地引导转换）。

### v1.1.0 (2026-06-21)

**风格转换 —— 粗糙初稿 → 契合期刊风格，稳定可靠**

- **Style Spec + Style-Conformance Verifier** —— 将一篇范例（`Style/own/` 或 `Style/target_journal/`）绑定为一份紧凑、始终加载的 `drafts/style_spec.md`（`docs/style_spec_template.md`），随后逐章节转换，并由一个独立的 **Style-Conformance Verifier** 对照该规范逐章节核验（自动修复循环，最多 2 次；`docs/verifier_prompt_templates.md` + `verification_protocol.md`）。这触及 lint 无法覆盖的整体风格层面（结构、句长、模糊化措辞、论断强度、参考文献格式）。新增 `/style-pass` 命令 + `docs/style_transform_protocol.md`。
- **按意图自动触发** —— 一个 `UserPromptSubmit` hook（`scripts/hooks/style_intent.py`）会识别“make it academic / 学术化改写”一类意图并注入 style-pass 协议，使转换无需记住命令即可触发。SessionStart 现在还会显示当前生效的 Style Spec。建议性 + fail-open（出错时放行）。已新增测试。

### v1.0.3 (2026-06-20)

**跨运行时 critical review + 模型选择**

- **Claude-CLI 评审者** — `scripts/critical_review.py --include-claude` 会调用本地的 `claude -p`（headless 模式），使得非 Claude-Code 的调用方（Codex 或普通 shell）也能引入 Claude 的对抗式评审。`OPENROUTER_API_KEY` 现在仅在实际请求某个 OpenRouter 模型时才需要。相关说明见 `docs/critical_review_protocol.md` 与 `AGENTS.MD`。
- **更大的模型池 + 选约 2 个** — `scripts/critical_models.txt` 现在提供 MiniMax M3、GLM 5.2、Qwen3-Max 和 DeepSeek V4 Pro；`/critical-review` 将它们作为各自独立的 `AskUserQuestion` 选项呈现，并建议选择约 2 个（兼顾成本与盲点多样性），随后运行 `--models <selected>`。

### v1.0.2 (2026-06-20)

**流程强制执行 + CLAUDE.md 精简**

- **计划优先强制执行（hooks）** — `.claude/settings.json` 新增已提交的 hooks：一个 PreToolUse 的 `Write|Edit|MultiEdit` 门（`scripts/hooks/enforce_gates.py`），在缺少已完成/已批准的 `drafts/.../draft_plan.md` 时**阻止**撰写章节（Rule 8），在缺少已完成/已批准的 `data/.../analysis_plan.md` 时**阻止**创建分析脚本（Rule 7）；以及一个 SessionStart hook（`scripts/hooks/session_contract.py`），在每次会话注入工作流契约。Revision 不受限制；支持多论文子文件夹；fail open（出错时放行）；UTF-8 安全。（Windows 用 `py`；macOS/Linux 用 `python3`。）
- **`/verify`** — `scripts/verify_all.py` 在记录门 PASS 之前，用单条命令运行 check_citations + check_numbers（+ 可选的 check_gate），并转发 `--verify-hash` 以保持文档化的 freshness 检查生效。hook 行为与 freshness 转发均由回归测试覆盖。
- **CLAUDE.md 精简 808 → 696 行（约 14%）** — 将 Multi-Paper/Revision 结构树以及 Phase-2 Notes / 检验选择 / 风格优先级 / 门布置等重复内容收缩为指向其正本文档的指针；未移除任何 MUST-FOLLOW 规则。

### v1.0.1 (2026-06-20)

**发布后加固 + 精简工具**

- **当日加固（代码评审 + 项目审计）** — `check_gate.py` 的时效性检查现在对非文件路径（目录/缺失）会干净地失败而不再崩溃，将相对路径锚定到仓库 `ROOT`，以清晰的提示拒绝空白/占位的摘要值，并在 PASS 输出中报告 `provenance_verified` / `provenance_unverified`；Phase 8 的 verifier 集合已对齐（Logic 仅用于 Draft；Revision 增加 Revision-claims + Response-alignment），门命令中加入 `--require-check constraint`；“3 个 verifier”更正为“4 个”；Critical Rules 重新编号为 9/10/11；`lint_manuscript.py` 会跳过不存在的 `.md` 参数（新增首批 lint 测试）；`check_numbers.py` 要求显式的 p 值（而非任意 0–1 之间的比例）；`search_pubmed.py` 的 evidence 条目新增 Evidence ID 与 Source Status；checker 的 FAIL 输出新增 `failure_code`；测试扩展至 77 个。
- **精简通道（Concision Pass）** — `docs/writing_guide.md` 新增面向期刊字数限制的压缩通道（Phase 5）：从资深英文编辑提炼出的 10 组 Before→After 模式，外加一条过度压缩的护栏（将主要结局定义、统计规格、入选标准与关键局限保留在正文中或移至 Supplement——切勿无声删除）。

### v1.0.0 (2026-06-20)

**验证加固（受 superpowers 启发）**

- **门时效性 / provenance** — `check_gate.py` 新增 `provenance:` 区块（产出物/evidence/results 的 sha256）、`--verify-hash LABEL=PATH`（当被验证文件在 PASS 之后发生变更时，将该门判定为 *stale* 并失败）以及 `--compute-hash PATH`。堵住了并行验证所打开的 stale-PASS 漏洞；向后兼容（可选启用的 flag）。`review/gates/_TEMPLATE.GATE.md` 与 `docs/verification_protocol.md`（v0.2.0）对其进行了文档化；pytest 覆盖扩展至 70 个测试。
- **并行 verifier + Constraint 优先** — 四个章节门 verifier 针对冻结的产出物并发执行；修复时优先处理 Constraint（spec）违规；任何编辑之后，所有 PASS 均作废并重新执行（`docs/verification_protocol.md`）。
- **STOP 信号** — CLAUDE.md anti-rationalization 表格（§10），防范 verifier 遗漏的、人类层面的偷懒。
- **苏格拉底式 draft-plan 头脑风暴** — `docs/draft_plan_template.md` Step 0（每次一个问题；与 `/paper-debate` 不同，作为其 R0 准备提供输入），并接入 CLAUDE.md Phase 3 + Rule 8。
- **审稿人回复分诊** — `docs/revision_guide.md` 为每条意见指定 accept/partial/rebut 立场，绑定到 `[CHANGE]` + ghost-revision；Phase 8 的 verifier 集合对齐为包含 Constraint。
- 为 `.claude/commands/*.md` 添加 **命令 `use-when` 行**；将 TodoWrite 文档化为非权威的 QC/门追踪手段（CLAUDE.md Rule 4）。

### v0.9.3 (2026-06-19)

**合著者协作与多模型批判性评审**

- 新增 **`/paper-debate`**（`docs/debate_protocol.md`、`.claude/commands/paper-debate.md`）— 写作前的 Claude–Codex 合著者辩论（分析计划、draft plan、论证结构、审稿人回应）。共识上限 3，辩论日志位于 `review/debates/`，Codex 不可用时回退为 Claude 单独执行。
- 新增 **`/critical-review`**（`docs/critical_review_protocol.md`、`.claude/commands/critical-review.md`）— 写作后由 Claude 子代理、Codex、OpenRouter 模型（默认 `minimax/minimax-m3`、`z-ai/glm-5.2`）进行对抗性评审。按共识度 × 严重度合并排序，报告位于 `review/critical/`。
- 新增 `scripts/critical_review.py`（OpenRouter 调用；单个模型失败则跳过，不致命）、`scripts/critical_models.txt`（模型列表外部化）、`scripts/critical_prompts/`（脚本、Claude 子代理与 Codex 共享的单一正本提示 `manuscript.txt`/`response.txt`）。
- 将 critical-review 提示提升至 **senior reviewer / editor-in-chief 级别** — 追问设计是否稳健、数据是否支持结论、是否值得发表，而非仅停留在表层缺陷。
- `build_prompt` 由 `str.format` 改为 `str.replace` — 提示或目标文本中的花括号（JSON、LaTeX 示例）不会破坏替换。新增回归测试。
- 在 `docs/writing_guide.md` 新增 **AI-Draft De-bloat** 章节 — 去除 AI 痕迹（空洞的 `-ing` 分析、AI 词汇、signposting），排除会冲突的模式（hedging/copula/passive）。
- OpenRouter 访问通过 `.claude/settings.local.json` 中的 `OPENROUTER_API_KEY`（gitignored）；缺少密钥时仅跳过 OpenRouter，其余评审者继续。
- CLAUDE.md 集成两个命令（Collaboration 命令、Phase 2/3/4/8 辩论、Round 6 双层批判性评审、File Roles、结构树）。

### v0.9.2 (2026-06-18)

**验证哈尼斯加固**（错误修复 + 文档一致性）

- `check_numbers.py`：不再因百分比（例如 42.5%）而崩溃；拒绝仅由无关值（例如 count 0）支撑的 p 值；处理千位分隔符（1,234），并忽略 ISO 日期和内联 `code` 区段。
- `check_gate.py`：剥离内联 `# ...` 注释，使文档化的 gate 模板能够通过，且 round-overflow 升级机制正常工作。
- 新增 `requirements.txt`（python-docx）和 `tests/` pytest 测试套件（用 `pytest` 运行）。
- 文档：将 verifier 集合更正为 Constraint / Citation / Data / Logic（Revision 增加 Revision-claims 与 Response-alignment）；更正 response compiler 描述（它复现格式，不读取参考 .docx）。

### v0.9.1 (2026-06-18)

**多语言 README 与 Author Response DOCX 完成**

- 将英文、韩文、日文、中文 README 与验证哈尼斯 scripts 和 DOCX response workflow 同步。
- 添加 Author response Markdown template 与 `compile_response_docx.py` 用法。
- 文档化 citation evidence、numeric grounding、phase gate、revision claim 的 deterministic checker。
- 文档化用于 hallucination control、redundancy control、logic check、revision alignment 的 LLM verifier prompt-template。

### v0.9.0 (2026-06-16)

**验证哈尼斯** — 在每个 produce step 后执行 inline produce→verify→fix→re-verify gate

- 在每个 produce step 后设置 inline 验证 gate（Phase 3/4/8）— 以 produce→verify→fix→re-verify 循环取代集中于末端的手动 QC。
- Verifier 子代理：Constraint（指令合规性）、Citation（与 evidence.md 对照的 citation grounding）、Data（与 results CSV 对照的数字）、Logic（跨章节逻辑/冗余）；Revision gate 增加 Revision-claims 与 Response-alignment。
- 自主修正循环（最多 2 次重试），之后升级给用户。
- `[EVID:author_year]` citation tags 与「results CSV 作为单一正本」的 grounding。
- gate ledger（`review/gates/`）在记录 `status: PASS` 之前阻止进度推进。
- `evidence.md` 条目新增 Source Status 字段；Phase 6 QC 减轻为一次最终确认 pass。
- 程序化 citation checker：`py scripts\check_citations.py drafts\03_introduction.md --evidence knowledge\evidence.md`
- 程序化 number checker：`py scripts\check_numbers.py drafts\05_results.md drafts\table_1.md --results results`
- 程序化 phase gate checker：`py scripts\check_gate.py review\gates\phase_04_draft.GATE.md --artifact drafts\05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic --verify-hash artifact=drafts\05_results.md`
- 程序化 ghost-revision checker：`py scripts\check_revision_claims.py drafts\revision\REV1\response_letter_REV1.md --strict`
- LLM semantic verifier schema：`docs/verifier_prompt_templates.md`，用于 logic、redundancy、semantic citation support 与 revision-response alignment。

### v0.8.1 (2026-06-16)

**Response Letter 格式规则** — `docs/revision_guide.md` 内部版本 v0.3.0 → v0.4.0

- 将 response letter 格式改为最小化格式标准：
  - 仅对 **"Comment x.x"** 与 **"Response"** 加粗；移除其他所有格式（无标题、颜色、缩进、表格或项目符号/编号列表）
  - 引用的修改后稿件文本以 *斜体* 呈现
  - response 以连续散文撰写（无编号/逐项要点），在单一段落中按 致谢 → 立场 → 理由 → 行动 的顺序展开
  - 修改位置采用前置说明 — 先陈述位置，再引用修改后文本（不再使用结尾的「(See ...)」）
  - 不使用连字符或破折号
  - 具说服力、能说服审稿人的语气
- 为稿件修改新增 **最小改动原则** — 仅做应对每条意见所需的最小句子改动，使修订简洁而非冗长
- 更新「during writing」检查清单以匹配新的格式规则

### v0.8.0 (2026-06-16)

**Style Workflow、Linting 与 Agent Instructions**

- 将 writing-style 材料提升至顶层 `Style/` workflow，与 `knowledge/` 下的 reference evidence 分离。
- 新增 `Style/style_guide.md`，用于 style-anchor 提取规则、PDF-to-MD mirror rules，以及出版商通用文件名处理。
- 将 `Style/terminology.md` 扩展为项目术语 registry，涵盖脊柱外科、试验、AI/radiomics 与报告语境中的 preferred/forbidden terms。
- 新增 `docs/drafting_protocol.md` 与 `docs/section_templates.md`，以强制执行 outline → evidence-bound draft → style pass → QC 的撰写流程。
- 新增 `scripts/lint_manuscript.py` 并更新 draft/table 模板，使 manuscript linting 在 Windows 上以 `py scripts/lint_manuscript.py drafts --quiet` 通过。
- 新增 `AGENTS.MD` 作为 agent 启动指令，以 `CLAUDE.md` 为权威的 source of truth。
- 更新 `.gitignore`，使受版权保护的 PDF 和私有 style-anchor 摘要保持 local，而公开的 workflow 文件与示例仍可提交。

### v0.7.1 (2026-05-15)

**术语与模板**

- 新增 `Style/terminology.md` — 面向 BESS/脊柱外科的领域标准术语 registry
  - 涵盖术式名称、器械、评价指标、研究设计、统计、并发症等 60+ 术语的正确 vs 错误用法
  - 常见错误清单（creatine phosphokinase vs creatinine kinase；assessor-blind vs double-blind；VAS vs NRS 等）
- 新增 `docs/draft_plan_template.md` — 完整的 10 项 draft plan 模板
  - Claim→Citation Mapping 表（Introduction/Methods/Discussion）
  - Approval checklist（进入 Phase 4 之前 10 项必须全部完成）
- CLAUDE.md Phase 1：在项目设置时新增 journals 格式检查与 Style anchor 复查
- CLAUDE.md：更新 File Roles 表、Phase 3 workflow 与 Quick Commands 以引用模板
- 修复：更正 `profile/journals.md` 的 citation 示例 — TSJ 现为 et al. 前列出 6 位作者（而非 3 位）；BJJ 现按 BJJ 政策列出全部 8 位作者且不加 et al.

### v0.7.0 (2026-05-14)

**Citation 质量与风格一致性**

- 新增 `Style/` — own、landmark 与 target-journal style anchors
  - 2018 Spine — Depression & chronic LBP 横断面研究（KNHANES）
  - 2020 Spine J — Biportal endoscopic vs microscopic laminectomy RCT
  - 2023 Spine J — Biportal endoscopic vs microscopic discectomy RCT
  - 2024 Neurospine — BESS safety profile：2 项 RCT 的 pooled analysis
  - 2025 Bone Joint J — ENDOBH 多中心 RCT（6 家医院）
  - 每个文件：完整 citation、关键术语表、methods boilerplate、带数据的 key claims
- CLAUDE.md Rule 8：将 **Claim→Citation Mapping** 作为 draft_plan.md 的必需第 10 项
  - 写作开始前将约 20 个 key claims 与 citations 对应
  - Intro background（5–8）、methods rationale（2–3）、discussion comparisons（5–8）
- CLAUDE.md：更新 Phase Completion Criteria 3→4（draft_plan 必需项由 9 → 10）
- 新增 `profile/journals.md`（local only，gitignored）— 8 种目标期刊的已验证 citation 格式
  - The Spine Journal：bracket [N]，6 位作者后加 et al.
  - Spine (Phila Pa 1976)：superscript，citation 中需包含「(Phila Pa 1976)」
  - Bone Joint J：列出全部作者，Vol-B(issue) 格式
  - Neurospine：superscript，3 位作者后加 et al.
  - 另含：J Neurosurg Spine、Global Spine J、Clin Orthop Relat Res、Asian Spine J
- 在 `profile/authors.md`（local only，gitignored）中为 5 位合著者新增 ORCID

### v0.6.0 (2026-04-18)

**Writing Guide 重大重构** — `docs/writing_guide.md` 内部版本 v0.3.0 → v0.4.0

- CLAUDE.md（orchestrator）与 writing_guide.md（rules）之间的 **角色分离**
  - CLAUDE.md「Natural Academic Writing Style」章节收缩为仅指针（移除约 115 行）
  - 所有写作风格规则、表格与示例统一整合至 writing_guide.md
- **新章节：Style Reference Tables**（位于 writing_guide.md）
  - Voice & Tense by Section（6 个章节：Abstract/Intro/Methods/Results/Discussion/Conclusion）
  - Transition Words（but → nonetheless）
  - Verb Upgrades（showed → demonstrated）
  - Common Corrections（elderly → older adult 等）
  - Statistical Notation（斜体 *p*、范围用 en-dash、绝不使用 *p* = 0.000）
  - Hedging Language（4 级指南：Discussion 的 Strong/Moderate/Weak/Very weak）
- **新章节：Writing Principles (4 Pillars)**（位于 writing_guide.md）
  - Clarity、Conciseness、Objectivity、Consistency，并配以扩充的示例
- **General Principles 扩充** 6 条新规则：
  - 稿件正文不使用粗体
  - 缩写仅定义一次规则
  - 以临床发现而非统计方法作为句子主语
  - 不混用同义词（dural tear ↔ durotomy 等），并在 draft_plan.md 中进行术语选择
  - 数值格式一致性（小数、单位）
  - 句首不使用数字（拼写或重构）
- **Results 章节**：新增非显著 p 值省略指南（primary outcome 例外）
- **Discussion 章节**：三个新子章节
  - 不使用具体数字/p 值（文献比较例外）
  - 非显著结果不使用方向性趋势表述
  - 中性语气，并附被禁止的夸张用语清单
- **Tables 章节**：2 条新 Tips
  - Methods Statistics 与 Table footnote 的角色分离
  - 预设敏感性分析使用 Supplementary Table

**跨文件一致性修复**

- CLAUDE.md Phase 2：显式引用 `docs/statistical_analysis_guide.md` + `analysis_plan.md` 必需项（endpoint hierarchy、tests、multiple comparison、missing data）
- CLAUDE.md Phase 6 QC：逐轮责任标注（Claude / Dr. Editor / Dr. Statistician），并标记 CRITICAL vs RECOMMENDED
- CLAUDE.md Phase 3→4 Completion Criteria：扩充为列出全部 9 个 `draft_plan.md` 必需项
- `docs/revision_guide.md`：新增「QC Re-run for Revision」章节，含逐轮 re-run 清单与提交前清单
- `docs/evidence_guide.md`：Search Log 查询示例更新为实际 PubMed 语法（field tags `[tiab]`/`[MeSH]`、boolean AND/OR/NOT、带引号短语）

### v0.5.2 (2026-04-15)

- 修复所有文档之间的跨文件不一致
- 更新 figure 格式 workflow：draft 用 PNG（300 DPI），最终提交用带 LZW 压缩的 TIFF（600+ DPI），PPT/vector 作为可选
- 更新 `save_figure()` 模板：拆分为 `draft=True`（PNG）/ `final=True`（TIFF LZW）参数
- 在 CLAUDE.md revision 结构与 File Roles 表中新增 `review/reviewer_comments_REV{N}.md`
- 将 `analysis_plan.md` 占位符由 `[FROM CLAUDE.md]` 改为更友好的 `[연구 설계 입력]`
- 使 `revision_guide.md` 文件结构与 CLAUDE.md 对齐（R1→REV1 命名约定）
- 在 `qc_guide.md` 的 QC log 与 Final Sign-off 中新增 Round 4 模板
- 更新 `statistical_analysis_guide.md` 的 figure 输出格式以包含 TIFF
- 更新 `checklist_guide.md` 的 figure 提交要求（TIFF LZW 600+ DPI）

### v0.5.1 (2026-04-15)

- 新增 Analysis Plan Mandatory（Critical Rule #7）— 运行任何统计分析前必须创建并批准 `analysis_plan.md`
  - 多论文项目的逐篇 analysis plan（`data/paper{N}_xxx/analysis_plan.md`）
  - 必需内容：研究问题、纳入/排除标准、变量定义、检验选择理由、显著性水平
- 新增 Draft Plan Mandatory（Critical Rule #8）— 撰写任何章节前必须创建并批准 `drafts/draft_plan.md`
  - 必需内容：核心信息、tone/voice、必要参考文献、证据缺口、table/figure 计划、introduction/discussion 大纲、limitation 要点
  - 多论文项目的逐篇 draft plan
- 新增 Model Selection by Phase（Critical Rule #9）— 经济高效的模型指引
  - 推荐 Opus：Analysis Plan、Draft Plan、Revision（战略性阶段）
  - 默认 Sonnet、可选 Opus：Drafting、Style Polish、QC（基于计划的执行）
  - 推荐使用 Plan Mode（`/plan`）创建 Draft Plan
- workflow 阶段重新编号（7 → 8 个阶段）：在 Analysis 与 Drafting 之间新增 Phase 3（Draft Plan）
- 更新 Phase Completion Criteria，加入 draft_plan.md 批准 gate

### v0.5.0 (2026-04-14)

- 增强 QC Round 2（Reference Verification），新增 4 项子检查：
  - 2.5 Placeholder Reference Detection — 检测假/临时 citation（[ref1]、[TBD]、[X] 等）
  - 2.6 Order of Appearance Check — 验证 citation 编号是否遵循 Vancouver 风格顺序
  - 2.7 Reference Format Consistency — 检查所有 reference 的书目风格一致性
  - 2.8 Citation Distribution Check — 分节 citation 平衡、self-citation 率、时效性
- 强化 Reference List Integrity（2.4）— 新增编号连续性与重复编号检查
- 更新 QC Log 模板，加入 Round 2 增强章节
- 新增 File Versioning 规则（Critical Rule #5）— 日期默认（`_YYMMDD`）、`_v1`、`_REV1`、`_FINAL`
- 新增 Multi-Paper Organization（Critical Rule #6）— data、results、drafts、output、review 的逐篇子文件夹
- 新增 Multi-Paper Project 结构图（共享 docs/knowledge/scripts，逐篇独立文件夹）
- 新增 Revision 文件夹结构 — `drafts/revision/REV{N}/`、`output/revision/REV{N}/`
- 在 Recommended Workflow 中新增 Phase 7（Revision），含 QC re-run 要求
- 更新 Phase Completion Criteria，加入 Submit → Revision 路径
- 更新 File Roles 表，加入 revision 文件夹条目

### v0.4.0 (2026-04-09)

- 新增 `docs/revision_guide.md` - 审稿人回复与 revision 指南
- 新增 `docs/figure_guide.md` - 出版级 figure 生成指南
- 新增 `drafts/00_cover_letter.md` - 简洁的 cover letter 模板
- 更新 CLAUDE.md：项目结构、file roles、revision 与 figures 的 Quick Commands
- 从项目结构中移除 Spine GraphRAG 项目专属引用

### v0.3.0 (2026-03-09)

- 重大重写 `docs/statistical_analysis_guide.md`（v0.2.1 → v0.3.0）
  - Statistical Parsimony、Analysis Hierarchy、Clinical Significance、Subgroup Analysis、Sensitivity Analysis
  - Methods Statistical Section Checklist（依 ICMJE/SAMPL 的 10 项必需内容）
- 更新 `docs/writing_guide.md`、`docs/expert_roles.md`、`docs/qc_guide.md` 以保持统计一致性

### v0.2.5 (2026-03-09)

- 新增 `scripts/search_pubmed.py` - 使用 NCBI E-utilities API 的 PubMed 搜索工具（无 MCP、无外部包）
- 新增斜杠命令：`/search-evidence [query]`、`/import-doi [doi]`

### v0.2.4 (2026-03-04)

- 新增 `.gitattributes`，用于 LF 行尾规范化
- 新增针对 `.DS_Store`、本地设置、IDE config 的 `.gitignore` 规则

### v0.2.3 (2026-02-15)

- 新增 `docs/docx_guide.md`，用于 DOCX 转换规则
- 日期后缀的输出文件，分离的 title page 与 table DOCX 文件

### v0.2.2 (2026-02-10)

- 将 evidence guide 与 evidence registry 分离
- 新增 `docs/evidence_guide.md`，含详细的摘要撰写说明

### v0.2.1 (2026-02-07)

- 各类结构修复与模板改进

### v0.2 (2026-02-03)

- 新增 Statistical Analysis Guide
- 新增 Table/Figure/Results 冗余预防规则

### v0.1 (Initial)

- 基础项目结构
- writing guide、expert roles、checklists、QC guide
