# 变更记录

### v1.8.24 (261003)

- `manuwright setup`：在 Windows（以及没有方向键菜单的终端）上，主模型改为从编号列表中选择，而不是空白输入。列表和方向键菜单都会标明运行各模型的代理 CLI 是否已安装（"Claude Code installed"、"Codex not installed"），并把可运行的模型排在前面；仍可直接输入模型 id。输入 `claude` 这样的代理名称会被拒绝并给出提示，因为它不是模型 id，无法标记使用同一模型的评审者。代理评审者输入前会列出每个代理的安装状态。

### v1.8.23 (261003)

- Windows：`manuwright agents update`（以及 Obsidian 连接步骤、代理检查、`opencode models`）按 PATH 中的完整路径运行代理 CLI。`muse` 等通过 npm 安装的 CLI 是 `.cmd` 包装文件，`shutil.which` 能找到，但 Windows CreateProcess 仅凭名称找不到，导致 `FileNotFoundError: [WinError 2]` 中断。仍无法启动的程序会作为该代理的错误报告，其余代理继续执行。

### v1.8.22 (261003)

- `manuwright agents update` 不再刷新已登记的路径，而是从当前引擎文件夹重新添加 Claude、Codex marketplace。重装时选中了另一个 Python（`python3.11` → `python3.12` site-packages）会使其指向已删除的文件夹而失败（Claude `ENOENT`，Codex `marketplace root does not contain a supported manifest`）。Codex 的 `marketplace upgrade` 只刷新 Git marketplace，本地 marketplace 从未被更新。
- 手册：如何检查更新是否成功（`manuwright --version`、`update --check`、`claude|codex plugin marketplace list`）。

### v1.8.21 (261002)

- Windows（uv 安装）：`manuwright update` 不再在运行中的 `manuwright.exe` 内执行 `uv tool install --force`。Windows 无法替换正在运行的 exe，重装失败会留下被删一半的安装（`ModuleNotFoundError: No module named 'manuwright'`）。现在会输出命令，需关闭代理会话后在新终端运行；同一命令也能修复损坏的安装。
- 没有新版本时，`manuwright update` 显示 "up to date"，不再重装当前版本（指定 `--to` 时仍会重装）。

### v1.8.20 (261002)

- Windows（非 UTF-8 代码页，例如韩文 Windows 的 cp949）：修复 `manuwright setup` 检查 Obsidian 库连接时后台线程打印 `UnicodeDecodeError` 回溯的问题。代理 CLI（`claude`/`codex`/`agy mcp`、`opencode models`）、`git ls-remote`、`uv pip freeze` 及 `doctor` 钩子检查的输出改为按 UTF-8 读取（无法解码的字节被替换），不再使用系统代码页。

### v1.8.19 (261001)

- `manuwright init --refresh-rules`（在已有论文文件夹内）：仅把代理规则文件（AGENTS.md、CLAUDE.md、GEMINI.md）更新到已安装引擎版本，旧文件保存为 `.bak`；`manuwright update` 会提示。模板仓库文件夹请用 `git pull`。

### v1.8.18 (261001)

- 补充材料：`project.json` 新增 `supplements` 列表（如 `drafts/supp_table_1.md`），像表格一样检查，并单独生成 `supplementary_<名称>` 文件。若在 `tables` 中放入 `supp…` 文件或同一表号出现两次则拒绝（否则会覆盖正文 Table N）。

### v1.8.17 (261001)

- `manuwright verify`（以及 status、packet、build）自动使用当前论文文件夹的 project.json；仅在其他位置需要 `--project`。

### v1.8.16 (261001)

- 聊天批准：作者在聊天中批准计划（"승인"）时，代理用 `manuwright approve <plan> --kind analysis|draft --approved-by 姓名 --quote "..."` 记录；勾选框写明谁、何时、以何话批准并生成哈希回执，plan-first 钩子随即放行。代理仍不得自行批准。
- 每篇论文的分析环境：`manuwright env` 用 `data/requirements.txt`（pandas、numpy、scipy、statsmodels、matplotlib、openpyxl）在论文文件夹外建立 uv 管理的 Python 3.12，并写入 `data/environment.lock.txt`；`manuwright run <script>` 用它运行分析脚本。系统、Homebrew 或 pyenv 的 Python 损坏也不影响分析。
- `manuwright setup` 输入 OpenRouter 密钥时每输入或粘贴一个字符显示一个 `*`（可退格），输入后以 `sk-or-v1...abcd (N characters)` 形式显示收到的密钥再进行校验。

### v1.8.15 (261001)

- 个人库（`manuwright library`，`~/.manuwright/library/`）：按目标期刊、团队或个人保存的 Word 样式与 Word 模板（`manuwright target` 推荐该期刊的样式）（通过 `docx.reference` 作为生成稿件的基础）、复制到每篇新论文的团队信息、复制到新论文 `Style/` 的写作风格（本人/经典/目标期刊锚点、术语表、style spec）。风格提取和团队信息填写由 manuwright skill 中的代理完成。
- Word 样式与参考文献格式按论文设置：新命令 `manuwright target`（在论文文件夹内运行）通过菜单选择目标期刊和该论文的 Word 样式并保存到其 `project.json`；`manuwright setup` 不再询问 Word 样式；`manuwright init` 会提示。
- `manuwright setup` 选择 OpenRouter 审稿者时询问 API 密钥（隐藏输入，经 OpenRouter 校验，以仅本人可读方式保存在 `~/.manuwright/secrets.json`，不写入 config.json）；未设置 `OPENROUTER_API_KEY` 时 `critical_review.py` 使用该密钥。
- 审查后加固：`--replace` 先准备新模板再替换（避免丢失原文件）；确认模板为真正的 .docx；不重复模板自带的行号/页码；`docx.reference` 只允许在论文文件夹内，`build.json` 记录相对路径；`target` 中回车不会擅自更换样式；OpenRouter 密钥以仅本人可读方式原子写入；`doctor` 识别已保存的密钥；`writing import` 跳过引擎说明和示例文件。

### v1.8.14 (261001)

- `manuwright setup` 标明各审稿者的计费方式：代理审稿者标为 "Claude Code (subscription)" 等，OpenRouter 为 "pay per use"，opencode 为 "opencode Go subscription"；并用一行说明审稿者的作用及主模型即写作模型。

### v1.8.13 (261001)

- `manuwright setup` 改为菜单选择模型而非手动输入：主模型从列表选，代理审稿者、OpenRouter 与 opencode 模型用方向键勾选清单（空格勾选，数字键套用推荐组合，Esc 保持当前）。无 POSIX 终端时按编号选择。"非独立"判定将 `claude-opus-5-5` 与 `anthropic/claude-opus-5.5` 视为同一模型。

### v1.8.12 (261001)

- 审稿推荐模型：`manuwright setup` 以编号提供 OpenRouter（balanced、budget、strong）和 opencode（Go、Go budget）推荐组合，包含 GLM、Kimi、MiniMax、DeepSeek、Qwen、小米 MiMo、美团 LongCat 最新模型，按实时列表核对并显示单次审稿估算费用；手动输入的 ID 会提示相近名称。`manuwright models` 列出组合。默认 OpenRouter 模型改为 balanced 组合。免费与 contributor 版本因可能保留提示词而排除。

### v1.8.11 (261001)

- 修复连接 Obsidian 时终端卡住：代理状态检查（`codex`/`claude`/`agy mcp …`）与终端分离运行，代理 CLI 不再让终端停留在 raw 模式导致回车无效；提问前恢复终端，Ctrl-C/Ctrl-D 视为"否"。

### v1.8.10 (260930)

- 期刊参考文献格式：`project.json` 中的 `"journal"`（或 `format-references --journal`）支持 14 个预设 — ICMJE/Vancouver、AMA（JAMA）、NEJM、Lancet、Spine、The Spine Journal、BJJ、JBJS、Neurospine、J Neurosurg Spine、Global Spine J、CORR、Asian Spine J、Eur Spine J。作者截断、页码/期号/月份/DOI 格式、CORR 按字母排序、相邻引用合并（`[1–3]`、Word 上标）。`--fetch` 缓存 PubMed 完整书目。

### v1.8.9 (260930)

合并发布：

- `manuwright setup`：一次交互式设置主模型、审稿者及其模型、Word 样式、自动更新和 Obsidian 库。
- DOCX 样式可配置：用 `manuwright config set docx.<键> <值>` 保存默认样式（字体、字号、标题/小标题字号、行距、页边距、行号 continuous/page/off、页码 center/right/off）；`project.json` 中的 `"docx"` 块按论文（目标期刊）覆盖。实际样式记录在 `build.json`。两者都没有时输出不变。
- `manuwright obsidian install`：从 GitHub 最新版本将 Obsidian 插件安装到所选 vault（先询问、启用插件、MCP 访问可选、不覆盖）。缺少插件时 `agents install` 会提示安装。
- Obsidian 集成标注为可选（推荐）；无插件时 `agents install` 仅打印一行建议。
- v1.8.8 之后的 CI 修复：在没有主目录的环境中也能读取评审设置；修复在 Windows 上比较 POSIX 路径字符串的测试。

### v1.8.8 (260930)

一次合并发布（按作者要求，修复合并后再升版本，而非每次修复都升）：

- **任意评审者、任意模型。** `critical_review.py --reviewers agent[:model]` 接受 `openrouter:<id>`、`claude`、`codex`、`opencode`、`muse`、`agy`，均可指定模型。本地 CLI 在空的临时目录中以只读/plan 模式运行，并被要求仅以文字作答（否则 Antigravity 会尝试调用 shell 工具，在 headless 模式下被自动拒绝并返回空输出）。在示例稿件上测试：Codex、opencode（kimi-k3）、Muse、Antigravity 与 4 个 OpenRouter 模型均返回完整评审。
- **设置。** `manuwright config set main-model|review.reviewers|review.openrouter-models|review.<agent>-model ...`（及 `unset`）。评审默认使用这些设置；与 main 写作模型相同的评审者被标记为 `not_independent`。
- **Obsidian 集成。** `manuwright obsidian status|connect` 为 Claude Code、Codex、opencode、Antigravity、Muse 注册「Academic Paper Citation Manager」的 MCP 服务器（`rag-obsidian`）（先询问，跳过已连接者，修改 JSON 前备份）。检测到插件时 `manuwright agents install` 会提示连接。`manuwright evidence import-obsidian <citekey>` 将 vault 笔记（CSL 字段与 AI 摘要）转为 `abstract-only` 证据条目。本机已验证：Codex、Muse、opencode 通过 MCP 调用了文献库；Claude Code 已连接；Antigravity 需在交互会话中允许首次 MCP 调用。
- 手册：新增投稿阶段（绑定、检查清单、评审轮次、stale、构建）以及 Obsidian 与评审者章节。
- 414 个测试通过。

### v1.8.7 (260930)

- **PubMed 导入的参考文献字符串**：`search_pubmed.py` 会写出 "et al.."，且标题与期刊名之间缺少句点（"...: A meta-analysis J Back Musculoskelet Rehabil"），导致所有构建出的参考文献列表都带有该问题。已修复并添加测试（旧测试曾以双句点为前提）。在目视检查合成示例论文首个 DOCX 包时发现。

### v1.8.6 (260930)

第二次端到端测试：四个智能体分写章节（Codex 写 Methods、Antigravity 写 Results、Muse 写 Introduction、opencode 写 Discussion），Claude 写 Title/Abstract/Conclusion，draft profile 达到 PASS，Codex 担任独立 semantic reviewer（第一轮 13 条意见，第二轮解决 12 条，1 条按 Rule 9 交给用户）。过程中发现并修复的引擎问题：

- 编辑时的 lint hook 忽略论文自己的术语表，持续把获批计划选定的术语（"MIS"）判为禁用词。现与 `verify` 一样读取最近的 `project.json` 中的 `terminology`。
- `init` 生成的 manifest 包含 `ai_usage.json`/`checklist.json`；在这些投稿记录生成之前，`verify --profile draft` 与 `packet` 会以 "No such file" 中止。现在在文件出现前跳过它们；submission profile 仍会阻止。
- `manuwright search "<query>"` 按文档工作（可省略 `search` 子命令）。
- 新增带截图的用户手册：`docs/manual.md`、`docs/manual.ko.md`。
- 406 个测试通过。

### v1.8.5 (260930)

在合成临床试验数据上的端到端测试（init、分析计划、批准、分析、表格、检查）中发现：

- **模板 hook 在 `cd` 后静默失效**：`.claude/settings.json` 用相对路径调用 `sh scripts/hooks/run.sh ...`。智能体在 shell 中切换目录后，所有 hook 以 exit 127 失败，而 Claude Code 将其视为非阻断错误，于是 plan-first 写入被放行。hook 命令现以 `$CLAUDE_PROJECT_DIR` 为基准。新增从无关目录运行 gate 的回归测试。
- `verify` 现在列出缺失的文件名，而不是 "one or more declared artifacts are missing"。
- 同一测试中确认：计划批准前分析脚本被阻止，`record-approval` 后放行；draft plan 未批准时 Results 章节被阻止；表中 50 个数字与结果 CSV 一致；错误均值（61.2）被检出，并给出最接近的真实值（60.4）。
- 403 个测试通过。

### v1.8.4 (260930)

- **全新 README**：采用热门智能体工具仓库的风格：Logo、一句话介绍、徽章、使用前/后、工作方式、按智能体安装、命令、工作流、FAQ（英/韩/日/中）。旧 README 内容原样移至 `docs/guide/overview*.md`，变更记录移至 `CHANGELOG*.md`。
- **Logo**：被对勾切开的钢笔笔尖（工匠 + 验证），由 Antigravity 制作。`assets/logo.png`（主）、`assets/logo-alt.png`（对勾从笔尖延伸出的版本），各含透明深色模式版本与原图。
- WORKFLOW Rule 12 将版本与变更记录的更新对象改为 plugin manifest、README 安装标签与 `CHANGELOG*.md`。

### v1.8.3 (260930)

- 测试隔离：安装版测试曾把临时项目登记到真实的 `~/.manuwright/projects.json`，现改用临时 `MANUWRIGHT_HOME`。引擎无变更。

### v1.8.2 (260930)

- **将 `paperflow` 更名为 `manuwright`**（"manuscript" + "-wright"，如 playwright，意为「制作的工匠」）。`paperflow` 在 PyPI 与 GitHub 上已被占用。命令 `manuwright`、包 `manuwright/`、plugin `manuwright@manuwright`、skill `manuwright` 与 `manuwright-verify`、设置目录 `~/.manuwright`、环境变量 `MANUWRIGHT_*`。以下旧条目保留发布时的名称。
- 从 v1.8.0/1.8.1 升级：先移除旧安装（各智能体中的 `paperflow` plugin 与 skill，`uv tool uninstall paperflow`），再安装 `manuwright` 并运行 `manuwright agents install`。如需保留项目登记与设置，将 `~/.paperflow` 移至 `~/.manuwright`。

### v1.8.1 (260930)

- **Codex 强制修复**：Codex 用 `apply_patch` 写文件，并把 patch 放在 `tool_input.command`（无 `file_path`），因此 plan-first 门禁在 Codex 中从未生效。现在 gate 与 lint hook 会读取 patch 中的所有文件路径，hook matcher 显式包含 `apply_patch`。于安装 v1.8.0 后的真实 Codex 会话中发现。
- `doctor` 仅在源码 checkout 中提示缺少 pytest。`paperflow agents` 的输出不再与子进程输出交错。
- 401 个测试通过（Codex patch 测试 +3）。

### v1.8.0 (260930)

里程碑：**双轨分发**。同一引擎既可作为 clone 即用的模板（A，保持不变），也可作为带有 Claude Code、Codex、Antigravity、opencode、Muse 适配器的安装式 `paperflow` CLI（B）。汇总 v1.7.6 至 v1.7.10，并新增：

- README「安装：两种方式」一节；`docs/migration_guide.md`（复制文件夹的可选、非破坏性迁移，以及 A 方式的更新文件清单）。
- `docs/distribution_plan.md` 标记为已实现。
- `paperflow update` 以发布标签 `vX.Y.Z` 作为更新通道。

### v1.7.10 (260930)

- **阶段 4，智能体适配器**：一次安装即包含 Claude Code 与 Codex 的 plugin（skill `paperflow`、`paperflow-verify`，以及会话规则、plan-first 门禁、lint、style 的 hook）、供 Antigravity（`agy`）使用的根目录 `plugin.json`，以及供 Muse 与 opencode 使用的 skill。`paperflow agents install|update [--only ...] [--dry-run]` 调用各智能体的原生命令，并以已安装的引擎目录作为 plugin 根目录，因此适配器版本始终与 CLI 一致。plugin hook 调用 `paperflow hook <name>`；在已运行自身 hook 的模板 checkout 中保持静默；plugin 与 CLI 版本不一致时发出警告；开启自动更新时在后台刷新适配器。
- `paperflow init` 将共享的 `docs/agent_bootstrap.md` 规则写入 `CLAUDE.md`/`AGENTS.md`/`GEMINI.md`。
- 398 个测试通过（适配器 +8）。已用 `claude plugin validate`、`agy plugin validate`、`muse skills validate` 验证。

### v1.7.9 (260930)

- **阶段 3，设置与更新**：`paperflow init`（用引擎模板创建论文文件夹，不覆盖、不勾选审批）、`paperflow rules [keyword]`、`paperflow update [--check|--to]`（重新安装带标签的版本，记录日志，一条命令回滚），以及可选的 `paperflow config set auto-update on`。自动更新仅应用 patch 版本、每天最多一次；若已登记项目固定了引擎或持有有效的 semantic review / human signoff，则不应用并等待。
- manifest `engine` 固定（例：`">=1.8,<1.9"`），不匹配时 `verify` 报告 `engine_pin` BLOCKED。
- 390 个测试通过（lifecycle +10）。

### v1.7.8 (260930)

- Windows CI 修复：v1.7.5 的两个测试用 `/` 比较快照键，而快照键使用操作系统分隔符。改为用 `Path` 生成期望值。引擎无变更。

### v1.7.7 (260930)

- **安装式 CLI，阶段 2（预览）**：`pyproject.toml` 将引擎打包为 `paperflow`（`uv tool install git+...@tag`）。`paperflow doctor|status|verify|packet|build|record-approval` 等同于 `python -m harness`；`paperflow citations|numbers|gate|lint|verify-all|search|...` 以相同参数运行各脚本，省略项目路径时按当前文件夹补全。wheel 仅含允许清单（代码、术语表、WORKFLOW、docs、gate 模板），不含 PDF、profile、稿件或数据。
- `check_gate.py` / `verify_all.py`：新增项目根目录参数 `--base-dir`（默认值不变）。
- CI 构建并安装 wheel，在包外运行安装版测试。380 个测试通过（另有 3 个仅安装版测试）。

### v1.7.6 (260930)

- **分发计划**（`docs/distribution_plan.md`）：一个仓库提供两种方式。A 保持现有的 clone 即用模板。B（计划 v1.8.0）提供安装式 `paperflow` CLI，以及面向 Claude Code、Codex、Antigravity（`agy`）、opencode、Muse 的轻量适配器。更新自动检查、显式应用；可选的自动更新绝不会让论文的有效评审变为 stale。已与 Codex（gpt-6-astra）评审，并与 Spec Kit、OpenSpec、caveman、ponytail 对比。
- **阶段 1 兼容性契约**（`tests/test_compat_contract.py`，22 个测试）：所有脚本无需安装、在无关 cwd（含空格与非 ASCII 路径）且无 `PYTHONPATH` 时可运行；旧的 citation/number 默认路径仍以引擎为基准；gate hook 按事件 cwd 解析被编辑文件；同一进程中的两个 manifest 互不干扰。
- 379 个测试通过。

### v1.7.5 (260929)

来自 Claude + Codex（gpt-6-astra）联合评审的改进。

- **逐字段校验提交记录**：每个检查清单条目需唯一 id，PASS 需稿件位置，NOT_APPLICABLE 需理由，其他状态判为失败。此前仅有 `{"status":"PASS"}` 即可通过。使用 AI 时，`tools` 每一项需 `tool` 与 `role`。
- **abstract 一致性**：manifest 的 `abstract` 必须属于发布的 `artifacts`，且发布的 abstract 文件必须声明，避免检查错误文件或静默跳过。
- **项目术语表与 Style Spec**：manifest 新增可选键 `terminology`、`style_spec`。lint 使用项目术语表，`style_metrics` 运行 `check_style.py`，两个文件进入 review snapshot。
- **可操作的失败信息**：harness `detail` 显示前几个问题（文件、行、值），而非 `False`。packet 包含检查清单与 AI 记录，并列出仅以哈希存在的 `omitted_sources`。
- **预检**：`doctor` 报告 `python_supported`，实际运行 Claude gate hook（`hooks.ok`），并输出 `warnings`。hook 出错时输出 WARNING 而不是静默通过；无 Python 时 `run.sh` 发出警告。新增 `requirements-dev.txt`（CI 使用）。
- **精简上下文**：目录树、文件角色表、命令目录与 PubMed 选项从每次会话加载的 `WORKFLOW.md`（56 KB → 30 KB）移至 `docs/workflow_reference.md`。命令示例统一为 `python scripts/...`。`/verify` 示例加入 `--cross-check`。
- 357 个测试通过。`docs/harness_guide.md` v1.0.5。

### v1.7.4 (260908)

- **随附 `profile/` 模板**：`profile/example_authors.md`（通讯作者、共同作者、funding 套语、IRB/临床试验注册的 placeholder 骨架）与 `profile/example_journals.md`（13 种期刊的完整示例 — 正文引用格式、作者 cutoff、页码范围、ORCID 政策、投稿清单）。复制为 `profile/authors.md`、`profile/journals.md` 使用，这两个文件仍然 gitignored。
- `.gitignore`：`profile/` → `profile/*` 加否定模式。git 无法重新包含父目录已被排除的文件，因此旧模式下模板根本无法提交。真实的 profile 文件仍被忽略（已实证确认）。
- **测试可移植性修复**：`test_cli_verify_hash_resolves_relative_paths_from_project_root` 此前哈希仅存在于本模板仓库的 `drafts/05_results.md`，导致按论文划分 `drafts/` 的真实项目必然失败。现改为哈希 harness 自身随附的文件。

### v1.7.3 (260908)

- 在韩文 Windows 上验证 v1.7.2：344 个测试、CI 9/9、通过真实 CLI 的 37 个合成错误注入场景 — v1.7.1 的 25 个 draft/revision 场景之外，新增 `numeric_scope`（非结果章节含数字但无 numeric_artifacts/豁免、空理由、试图豁免结果文件、试图豁免已绑定文件）与 `revision_scope`（存在 REVn 却列出原始章节、CHANGE 目标不在 artifacts 中、REV2 信函搭配 REV1 artifacts）12 个。全部按设计拦截/通过。
- `docs/project.example.json`：在模板 manifest 中加入 v1.7.2 新字段 `numeric_exemptions`。
- README ko/ja/zh：本地化 v1.7.2 changelog 条目（此前仅有英文）。页眉 → v1.7.3；`harness/__init__.py`（doctor）→ 1.7.3；`docs/harness_guide.md` → v1.0.3。

### v1.7.2 (260907)

- 将 revision claim 与各节最新版本绑定到实际投稿文件（`revision_scope`）。
- 拒绝未纳入数值检查的稿件文件；非结果章节的排除须在 `numeric_exemptions` 中给出明确理由（`numeric_scope`）。
- 即使表头含数字也能通过分隔行识别 p 值列；表头数字检查保持不变。
- 同步 doctor 版本，并新增 submission scope 回归测试。

### v1.7.1 (260908)

**v1.7.0（PR #1）合并后验证 — 修复 4 项缺陷，文档同步**

- **v1.7.0 的 CI 从未真正运行。** `.github/workflows/tests.yml` 中 OS 矩阵行被错误嵌套在 setup-python 的 `with:` 之下，所有运行在 YAML 解析阶段即失败（0 秒）。现在 3 OS × 3 Python 矩阵真正执行（main 上 9/9 通过）。
- **Windows cp949:** 新增的 `test_harness.py` / `test_review_regressions.py` 读取文件时未指定 `encoding='utf-8'`，在韩文 Windows 上 3 项失败 — 被失效的 CI 掩盖。已修复；333 个测试通过。
- **构建文件名:** `harness build` 使用 UTC 日期（KST 00–09 时会得到前一天的 `_YYMMDD`），且 revision 包缺少 `_REVn`（Rule 5）。现在首次投稿为 `manuscript_YYMMDD.docx`，revision 为 `manuscript_REV1_YYMMDD.docx` / `response_letter_REV1_…` / `table_N_REV1_…`。新增合成 REV1 构建测试；`docs/harness_guide.md` v1.0.1。
- **`CLAUDE.md` 现在导入 `WORKFLOW.md`**（`@WORKFLOW.md`）— Claude Code 自动加载共享规则，而非依赖"先读一遍"的指令。`WORKFLOW.md`/README 中残留的"CLAUDE.md 是核心规则文件"引用已改为 `WORKFLOW.md`。
- 在合成项目上通过真实 CLI 端到端验证：draft 配置 12 个、revision 配置 13 个错误注入场景（未登记引用、`todo` evidence、CSV 中不存在的数值、批准后修改 plan、ghost revision、未回复/占位符回复、REV2↔REV1 基线）均按设计被拦截；DOCX 结构符合 `docs/docx_guide.md`。

### v1.7.0 (260906)

- 修复 F01–F09：引用 status/重复 ID、p 值边界、占位符、门禁 identity、plan 完整性、revision 基线与 reviewer fallback。
- 新增共享 WORKFLOW.md 以及标准 AGENTS.md、GEMINI.md 引导文件。
- 新增基于 manifest 的验证配置、context-bound 结果值、content-bound 批准、review packet/state 以及带门禁的 DOCX 打包。
- 设置、迁移与剩余限制见 [shared engine guide](docs/harness_guide.md)。

### v1.6.4 (2026-08-30)

**框架全面评审（Claude Fable）— 修复 16 项缺陷，新增 33 个回归测试**

- **门禁 false-PASS / false-FAIL / 崩溃（HIGH）:** `check_citations.py` 此前对畸形或非 ASCII 的 `[EVID:…]` 标签（`o'brien_2021`、`müller_2020`）以 0 token 报 PASS，现改为 FAIL；`search_pubmed.py` 对生成的 id 做 slugify 并使用完整姓氏。`check_numbers.py`：results CSV 行多出字段不再崩溃；正文 `p<0.001` 可匹配 CSV 单元格 `<0.001`（相同或更宽松的界）；大写 `P<0.05` 识别为 p 比较；`L4-5`、`C5-6`、`COVID-19`、`ICD-10` 等后缀数字视为结构标记而非结果；同时接受 ROUND_HALF_UP（2.675 → 2.68）。
- **强制 hook 真正生效:** hook 通过新增 `scripts/hooks/run.sh`（有 `py` 用 py，否则 `python3`）运行 — 此前在 macOS/Linux 上所有 hook 均 exit 127，Rule 7/8 强制被静默关闭。`enforce_gates.py` 现对**完全没有**审批复选框的 plan 也按未审批处理（Rule 9 的措辞此前并未真正执行）。
- **`check_gate.py`:** artifact 路径比较不区分斜杠（`drafts\05_results.md` == `drafts/05_results.md`，含 `--verify-hash`/`--cross-check`）；多块 gate 文件按 `artifact:` 拆分并由 `--artifact` 选择 — 前一块的 FAIL 不再被后一块的 PASS 掩盖；多块且未给 `--artifact` 时 loud FAIL。`_TEMPLATE.GATE.md` 已记录。
- **`check_response_coverage.py`:** 引用形方括号（`[12]`、`[3-5]`、`[EVID:id]`）不再视为 placeholder — 引用文献的反驳可通过。
- **细节:** `check_abstract.py` half-up 舍入；`format_references.py` 的 author-year 模式接受 `author_year_keyword` id（与 `evidence_guide.md` v0.3.1 对齐）；`compile_response_docx.py` 不再把 "# Response to Reviewers" 改写成 "Response: to Reviewers"；`check_citations`/`check_numbers`/`check_coverage` 代码围栏后的行号正确；`check_coverage.py` 对 markdown 表格逐行计数；`check_abbreviations.py` allowlist 以词干匹配 `COVID-19`；`lint_manuscript.py` 能捕获斜体 `*p* = .02` 且不再误报 "group = 30"。
- 测试 262 → 295。

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
- **Windows/template hygiene** — PubMed 命令示例统一为 `python scripts/search_pubmed.py`，根目录生成的 DOCX 产物加入 ignore，并用回归测试覆盖新的 hook 与 freshness 转发行为。

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
- **附加式 + 回退机制** —— 该 MCP 绝不构成依赖：当它不可用时（例如未认证的远程会话），工作流会降级为 `scripts/search_pubmed.py` + 手动维护 evidence.md。已接入 CLAUDE.md（Rule 1、STOP 信号、Phase 1、Quick Commands）+ AGENTS.md，以保持与 Codex 的一致性。

### v1.1.2 (2026-06-21)

**修复 —— hooks 以 UTF-8 读取 stdin（Windows 上的韩语意图）**

- `UserPromptSubmit` / `PreToolUse` / `PostToolUse` hooks 现在会将 stdin 重新配置为 UTF-8。在 Windows 上（默认 cp949），Claude Code 输出的 JSON 负载会被错误解码，因此非 ASCII 的提示词 —— 例如韩语自动触发语句“학술적으로 바꿔줘” —— 会静默地匹配失败。新增了一个端到端的 UTF-8 stdin 测试。

### v1.1.1 (2026-06-21)

**风格强制执行 —— 可度量的门 + 与 Codex 对齐**

- **确定性风格度量** —— `scripts/check_style.py`（`extract` / `check --spec`）测量字数、平均句长、段落数、引用密度和模糊化措辞，并标记出与 Style Spec 目标值的偏差 —— 即“面向风格的 check_numbers”。它已接入 `lint_on_edit.py`（当存在 Style Spec 时，在每次初稿编辑时浮现 `[STYLE-METRIC]` 偏差）以及 Phase 5/6 的门。已新增测试。
- **与 Codex 对齐 + 校准** —— `AGENTS.md` 现在会指示非 Claude 的运行时显式运行风格转换流程（`check_style.py` + Style-Conformance verifier），因为这些 hooks 仅在 Claude Code 中可用。Style Spec 模板新增了一个 before→after 的校准示例（相比抽象规则，少量示例能更好地引导转换）。

### v1.1.0 (2026-06-21)

**风格转换 —— 粗糙初稿 → 契合期刊风格，稳定可靠**

- **Style Spec + Style-Conformance Verifier** —— 将一篇范例（`Style/own/` 或 `Style/target_journal/`）绑定为一份紧凑、始终加载的 `drafts/style_spec.md`（`docs/style_spec_template.md`），随后逐章节转换，并由一个独立的 **Style-Conformance Verifier** 对照该规范逐章节核验（自动修复循环，最多 2 次；`docs/verifier_prompt_templates.md` + `verification_protocol.md`）。这触及 lint 无法覆盖的整体风格层面（结构、句长、模糊化措辞、论断强度、参考文献格式）。新增 `/style-pass` 命令 + `docs/style_transform_protocol.md`。
- **按意图自动触发** —— 一个 `UserPromptSubmit` hook（`scripts/hooks/style_intent.py`）会识别“make it academic / 学术化改写”一类意图并注入 style-pass 协议，使转换无需记住命令即可触发。SessionStart 现在还会显示当前生效的 Style Spec。建议性 + fail-open（出错时放行）。已新增测试。

### v1.0.3 (2026-06-20)

**跨运行时 critical review + 模型选择**

- **Claude-CLI 评审者** — `scripts/critical_review.py --include-claude` 会调用本地的 `claude -p`（headless 模式），使得非 Claude-Code 的调用方（Codex 或普通 shell）也能引入 Claude 的对抗式评审。`OPENROUTER_API_KEY` 现在仅在实际请求某个 OpenRouter 模型时才需要。相关说明见 `docs/critical_review_protocol.md` 与 `AGENTS.md`。
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
- 程序化 citation checker：`python scripts/check_citations.py drafts/03_introduction.md --evidence knowledge/evidence.md`
- 程序化 number checker：`python scripts/check_numbers.py drafts/05_results.md drafts/table_1.md --results results`
- 程序化 phase gate checker：`python scripts/check_gate.py review/gates/phase_04_draft.GATE.md --artifact drafts/05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic --verify-hash artifact=drafts/05_results.md`
- 程序化 ghost-revision checker：`python scripts/check_revision_claims.py drafts/revision/REV1/response_letter_REV1.md --strict`
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
- 新增 `scripts/lint_manuscript.py` 并更新 draft/table 模板，使 manuscript linting 在 Windows 上以 `python scripts/lint_manuscript.py drafts --quiet` 通过。
- 新增 `AGENTS.md` 作为 agent 启动指令，以 `CLAUDE.md` 为权威的 source of truth。
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
