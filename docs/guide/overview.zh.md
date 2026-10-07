# 完整指南（从 README 移出）

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
- **学术写作风格系统** — Style Reference Tables（Voice/Tense、Transition、Verb Choice、Common Corrections、Statistical Notation、Hedging）+ Writing Principles（Clarity/Conciseness/Objectivity/Consistency）
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
├── WORKFLOW.md                   # 核心规则与配置（Claude/Codex/Gemini 共享）
├── CLAUDE.md                     # Claude Code 引导文件；通过 @WORKFLOW.md 导入 WORKFLOW.md
├── AGENTS.md                     # Codex/agent 启动规则；以 WORKFLOW.md 为 source of truth
├── GEMINI.md                     # Gemini 引导文件；指向 WORKFLOW.md
├── README.md                     # 英文 README
├── .gitattributes                # 换行符策略 (text=auto eol=lf；防止 OneDrive/Windows 同步导致的 CRLF 变更)
├── docs/                         # 参考指南
│   ├── workflow_reference.md     # Tree, file roles, command catalog (moved from WORKFLOW.md)
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
│   └── hooks/                    # 强制执行 hooks（enforce_gates、session_contract、lint_on_edit、style_intent）+ run.sh 启动器（py→python3 自动选择）
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

## 安装：两种方式

| | A. 模板（无需安装） | B. 安装式引擎 |
|---|---|---|
| 获取 | `git clone` / "Use this template" | `uv tool install git+https://github.com/grotyx/Academic_writing_c_claudecode@vX.Y.Z` |
| 开始论文 | 在复制的文件夹中工作 | `manuwright init my-paper` |
| 智能体 | Claude Code 用 `.claude/`，Codex/Gemini 用 `AGENTS.md`/`GEMINI.md` | `manuwright agents install`（Claude Code、Codex、Antigravity、opencode、Muse） |
| 更新 | `git pull`（clone）或替换公开引擎文件 | `manuwright update`；可选 `manuwright config set auto-update on`（仅 patch，不会让有效评审变为 stale） |

两种方式使用相同的引擎与规则。详情：[docs/harness_guide.md](../../docs/harness_guide.md)，迁移：[docs/migration_guide.md](../../docs/migration_guide.md)，设计：[docs/distribution_plan.md](../../docs/distribution_plan.md)。

## 快速开始

1. **设置**：在 `WORKFLOW.md` 中填写研究主题、目标期刊和研究设计
2. **参考文献**：使用 `/search-evidence [关键词]` 或 `python scripts/search_pubmed.py` 搜索 PubMed 并注册到 `knowledge/evidence.md`
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
- **STOP 信号。** WORKFLOW.md 中的 anti-rationalization 表格捕捉 verifier 无法发现的、人类层面的偷懒（「这个数字大概没问题」→ 去查 CSV；「我已经通过了」→ 产出物已变更即为 stale）。
- **苏格拉底式 draft-plan 头脑风暴。** `docs/draft_plan_template.md` 中的「Step 0」在填写计划之前，每次一个问题地厘清论文意图 — 与 `/paper-debate` 不同，它作为 R0 准备为后者提供输入。
- **审稿人回复分诊。** `docs/revision_guide.md` 为每条审稿人意见指定 accept / partial / rebut 立场，并映射到 `[CHANGE]` 标记和 ghost-revision 门。
- **命令 `use-when` 指引。** 现在每个 `.claude/commands/*.md` 都声明了应触发它的情境。

### Author Response DOCX Workflow

Reviewer response 应按照 `docs/response_letter_template.md` 格式撰写，每一处稿件修改都记录为 `[CHANGE]` block。最终 response letter 可用以下命令编译：

```powershell
python scripts/compile_response_docx.py drafts/revision/REV1/response_letter_REV1.md
```

compiler 会复现 `Author_response_220803_Final.docx` 的 house style — Times New Roman 11 pt，response/位置/修改文本行为 bold，正文为 justified。它不会将该 .docx 文件作为模板读取，格式是内置的。

### PubMed 搜索工具

无需 MCP 即可搜索参考文献的内置 Python 脚本（`scripts/search_pubmed.py`）：

```bash
python scripts/search_pubmed.py search "endoscopic spine surgery"  # 搜索
python scripts/search_pubmed.py fetch 35486828                     # 按 PMID 获取
python scripts/search_pubmed.py doi 10.1016/j.spinee.2023.01.005  # 按 DOI 获取
python scripts/search_pubmed.py related 35486828                   # 相关论文
```

Claude 集成斜杠命令：

- `/search-evidence [关键词]` - 搜索、选择并注册到 evidence.md
- `/import-doi [doi]` - 通过 DOI 获取并注册到 evidence.md

---

## 文档列表

| 文档 | 用途 |
| ---- | ---- |
| [WORKFLOW.md](../../WORKFLOW.md) | 核心规则与项目配置（所有运行时共享） |
| [CLAUDE.md](../../CLAUDE.md) | Claude Code 引导文件；导入 WORKFLOW.md |
| [docs/writing_guide.md](../../docs/writing_guide.md) | 分节写作指南 + Style Reference Tables + Writing Principles (4 Pillars) |
| [docs/drafting_protocol.md](../../docs/drafting_protocol.md) | outline → evidence-bound draft → style/QC pass 的必须 drafting workflow |
| [docs/section_templates.md](../../docs/section_templates.md) | 分节 paragraph function 和 sentence patterns |
| [docs/expert_roles.md](../../docs/expert_roles.md) | 专家团队说明 |
| [docs/checklist_guide.md](../../docs/checklist_guide.md) | STROBE、CONSORT、PRISMA、CARE 清单 |
| [docs/qc_guide.md](../../docs/qc_guide.md) | 质量控制流程（6轮） |
| [docs/verification_protocol.md](../../docs/verification_protocol.md) | 验证门·4 Verifier 章程·自主修正循环·门台账 |
| [docs/verifier_prompt_templates.md](../../docs/verifier_prompt_templates.md) | LLM semantic verifier prompts and structured output schema |
| [docs/statistical_analysis_guide.md](../../docs/statistical_analysis_guide.md) | 统计分析指南（节约原则、MCID、亚组分析） |
| [docs/evidence_guide.md](../../docs/evidence_guide.md) | 证据文献编写指南（格式、摘要方法、工作流） |
| [docs/revision_guide.md](../../docs/revision_guide.md) | 审稿人回复指南（回复信撰写、外交措辞、QC 重跑清单） |
| [docs/response_letter_template.md](../../docs/response_letter_template.md) | DOCX-ready author response Markdown template |
| [docs/figure_guide.md](../../docs/figure_guide.md) | 图表生成指南（DPI、调色板、Python模板） |
| [docs/docx_guide.md](../../docs/docx_guide.md) | DOCX 转换指南（格式、表格样式、命名规则） |
| [docs/draft_plan_template.md](../../docs/draft_plan_template.md) | Draft plan template — 10项内容、claim→citation tables、approval checklist |
| [docs/debate_protocol.md](../../docs/debate_protocol.md) | Claude–Codex 合著者辩论流程（轮次、角色、日志、fallback） |
| [docs/critical_review_protocol.md](../../docs/critical_review_protocol.md) | 外部多模型对抗式评审（评审者池、共识度 × 严重度、fallback） |
| [Style/style_guide.md](../../Style/style_guide.md) | Style anchor workflow、extraction framework、PDF-to-MD mirror rules |
| [Style/terminology.md](../../Style/terminology.md) | Preferred/forbidden terminology registry |
| [Style/own/example_YYYY_Journal_keyword.md](../../Style/own/example_YYYY_Journal_keyword.md) | Own-paper style-anchor template |
| [scripts/lint_manuscript.py](../../scripts/lint_manuscript.py) | Manuscript lint script |
| [scripts/check_citations.py](../../scripts/check_citations.py) | 将 `[EVID:id]` citations 与 `knowledge/evidence.md` 对照 |
| [scripts/check_coverage.py](../../scripts/check_coverage.py) | 引用 coverage 审计 — **过度引用**（单一主张引用过多）·**未登记引用**为质量信号，各章节引用密度；未引用/未实现 claim 中立报告（属策展，非浪费） |
| [scripts/format_references.py](../../scripts/format_references.py) | `[EVID:id]` → 期刊格式参考文献列表（numbered/author-year）+ 将正文标签转换到同级 `*_formatted.md`；**不依赖 MCP**（Phase 7） |
| [scripts/check_abstract.py](../../scripts/check_abstract.py) | abstract↔正文数字一致性 — 标记 abstract 中存在但正文缺失的数字（Rule 3；默认排除 p 值）（Phase 6 QC Round 1） |
| [scripts/check_crossrefs.py](../../scripts/check_crossrefs.py) | Table/Figure 交叉引用检查 — 正文 "Table N"/"Figure N" 提及 ↔ 实际 `table_*.md`·figure legends：**broken reference**（主要信号）·未被引用项·首次提及顺序；默认 advisory，`--fail-on-*` 可门禁化（Phase 6 QC） |
| [scripts/check_abbreviations.py](../../scripts/check_abbreviations.py) | 缩写首次使用定义检查 — abstract/正文独立 scope（UNDEFINED / DEFINED_AFTER_USE / REDEFINED / SINGLE_USE）；以误报为前提的 advisory，`--allow`·`--strict`（Phase 6 QC） |
| [scripts/check_response_coverage.py](../../scripts/check_response_coverage.py) | 审稿意见回复覆盖检查 — 每个 `Comment N)` 必须有真实 `Response:`（拦截缺失/空/placeholder），`--comments` 与原始意见文件交叉核对；与 ghost-revision 门禁互补（Phase 8） |
| [scripts/check_numbers.py](../../scripts/check_numbers.py) | 将稿件/表格中的数字与 `results/*.csv` 对照 |
| [scripts/check_gate.py](../../scripts/check_gate.py) | 验证 `review/gates/*.GATE.md` 的 status 和必要 check |
| [scripts/check_revision_claims.py](../../scripts/check_revision_claims.py) | 将 response-letter `[CHANGE]` claims 与 revised manuscript files 对照 |
| [scripts/compile_response_docx.py](../../scripts/compile_response_docx.py) | 将 `response_letter_REV*.md` 转换为 Author_response-style DOCX |
| [scripts/search_pubmed.py](../../scripts/search_pubmed.py) | PubMed 搜索脚本（NCBI E-utilities，无需外部包） |
| [scripts/critical_review.py](../../scripts/critical_review.py) | OpenRouter 多模型对抗式评审调用（单个模型失败不会中断整体） |

---

## 系统要求

- Claude AI（Claude Code CLI 或 VSCode 扩展）
- Python 3.10+（旧版本会由 `python -m harness doctor` 警告；测试：`pip install -r requirements-dev.txt`）
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
