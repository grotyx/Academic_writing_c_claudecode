# 変更履歴

### v1.8.24 (261003)

- `manuwright setup`：Windows（および矢印キーメニューのない端末）ではメインモデルを空の入力欄ではなく番号付きリストから選ぶ。リストと矢印メニューの両方で、各モデルを実行するエージェント CLI のインストール状況（"Claude Code installed"、"Codex not installed"）を表示し、実行できるモデルを先に並べる。モデル id の直接入力も可能。`claude` のようなエージェント名はモデル id ではなく、同じモデルのレビュアーを検出できないため、案内付きで再入力を求める。エージェントレビュアーの入力前にエージェントごとのインストール状況を表示する。

### v1.8.23 (261003)

- Windows：`manuwright agents update`（および Obsidian 接続ステップ、エージェント確認、`opencode models`）はエージェント CLI を PATH 上のフルパスで実行する。`muse` など npm でインストールした CLI は `.cmd` シムで、`shutil.which` は見つけるが Windows の CreateProcess は名前だけでは見つけられず、`FileNotFoundError: [WinError 2]` で停止していた。それでも起動できないプログラムはそのエージェントのエラーとして表示し、残りのエージェントは続行する。

### v1.8.22 (261003)

- `manuwright agents update` は登録済みのパスを更新せず、Claude・Codex の marketplace を現在のエンジンフォルダから再登録する。再インストールで別の Python が選ばれると（`python3.11` → `python3.12` site-packages）削除済みフォルダを指して失敗していた（Claude `ENOENT`、Codex `marketplace root does not contain a supported manifest`）。Codex の `marketplace upgrade` は Git marketplace しか更新しないため、ローカルの marketplace は更新されなかった。
- マニュアル：更新の確認方法（`manuwright --version`、`update --check`、`claude|codex plugin marketplace list`）。

### v1.8.21 (261002)

- Windows（uv インストール）：`manuwright update` は実行中の `manuwright.exe` の中から `uv tool install --force` を実行しない。Windows は実行中の exe を置き換えられず、再インストールの失敗で半分削除されたインストールが残った（`ModuleNotFoundError: No module named 'manuwright'`）。エージェントセッションを閉じて新しいターミナルで実行するコマンドを表示し、同じコマンドで壊れたインストールも修復できる。
- 新しいリリースがなければ `manuwright update` は現在のバージョンを再インストールせず "up to date" と表示する（`--to` 指定時は再インストール）。

### v1.8.20 (261002)

- Windows（非 UTF-8 コードページ、例：韓国語 Windows の cp949）：`manuwright setup` の Obsidian ライブラリ接続確認中にバックグラウンドスレッドから `UnicodeDecodeError` のトレースバックが表示される問題を修正。エージェント CLI（`claude`/`codex`/`agy mcp`、`opencode models`）、`git ls-remote`、`uv pip freeze`、`doctor` のフック確認の出力をシステムのコードページではなく UTF-8 で読む（デコード不能なバイトは置換）。

### v1.8.19 (261001)

- `manuwright init --refresh-rules`（既存の論文フォルダ内で）：エージェント規則ファイル（AGENTS.md、CLAUDE.md、GEMINI.md）だけをインストール済みエンジンに合わせて更新、旧ファイルは `.bak` に保存。`manuwright update` が案内。テンプレートのチェックアウトは `git pull` で。

### v1.8.18 (261001)

- 補足資料：`project.json` に `supplements` リストを追加（例：`drafts/supp_table_1.md`）。表と同様に検査し、`supplementary_<名前>` として別ファイルで出力。`tables` に `supp…` ファイルを入れる、または同じ表番号が 2 回出る場合は拒否（本文の Table N を上書きするため）。

### v1.8.17 (261001)

- `manuwright verify`（status、packet、build も）が現在の論文フォルダの project.json を自動で使用。別の場所でのみ `--project` が必要。

### v1.8.16 (261001)

- チャット承認：著者がチャットで計画を承認（「승인」）すると、エージェントが `manuwright approve <plan> --kind analysis|draft --approved-by 名前 --quote "..."` で記録。チェックボックスに誰が・いつ・どの言葉で承認したかを書き、ハッシュ付き記録を残すので plan-first フックが進行を許可。エージェント自身の判断での承認は引き続き禁止。
- 論文ごとの解析環境：`manuwright env` が `data/requirements.txt`（pandas、numpy、scipy、statsmodels、matplotlib、openpyxl）で uv 管理の Python 3.12 を論文フォルダ外に作り `data/environment.lock.txt` を記録。`manuwright run <script>` で解析スクリプトを実行。システム・Homebrew・pyenv の Python が壊れていても解析可能。
- `manuwright setup` の OpenRouter キー入力で、入力・貼り付けた文字ごとに `*` を表示（Backspace 可）、入力後 `sk-or-v1...abcd (N characters)` の形で受け取ったキーを示してから確認。

### v1.8.15 (261001)

- 個人ライブラリ（`manuwright library`、`~/.manuwright/library/`）：投稿先ジャーナル用・チーム用・個人用に保存する Word スタイルと Word テンプレート（`manuwright target` でそのジャーナル用を推奨）（`docx.reference` でビルド原稿の土台になる）、新しい論文ごとにコピーされるチーム情報、新しい論文の `Style/` にコピーされる文体（自分・landmark・投稿先のアンカー、用語集、style spec）。文体抽出とチーム情報の入力は manuwright skill のエージェント作業。
- Word スタイルと参考文献形式は論文ごと：新しい `manuwright target`（論文フォルダ内で実行）が投稿先ジャーナルとその論文の Word スタイルをメニューで選び、その `project.json` に保存。`manuwright setup` は Word スタイルを尋ねなくなった。`manuwright init` が案内。
- `manuwright setup` で OpenRouter レビュアーを選ぶと API キーを入力（非表示、OpenRouter で確認、`~/.manuwright/secrets.json` に本人のみ読める形で保存、config.json には保存しない）。`OPENROUTER_API_KEY` がなければ `critical_review.py` がこのキーを使用。
- レビュー後の強化：`--replace` は新しいテンプレートを先に準備してから置換、テンプレートが本物の .docx か確認、テンプレートの行・ページ番号を重複させない、`docx.reference` は論文フォルダ内のみ許可し `build.json` に相対パスで記録、`target` で Enter がスタイルを勝手に変えない、OpenRouter キーは本人専用ファイルに原子的に保存、`doctor` が保存済みキーを認識、`writing import` はエンジンの案内・例ファイルを除外。

### v1.8.14 (261001)

- `manuwright setup` にレビュアーごとの課金方式を表示：エージェントは "Claude Code (subscription)" など、OpenRouter は "pay per use"、opencode は "opencode Go subscription"。レビュアーの役割とメインモデルが執筆モデルであることを 1 行で案内。

### v1.8.13 (261001)

- `manuwright setup` でモデルを入力せずメニューで選択：メインモデルは一覧、エージェント・OpenRouter・opencode のモデルは矢印キーのチェックリスト（Space で選択、数字キーで推奨セット、Esc で現状維持）。POSIX 端末がない場合は番号選択。「独立でない」判定が `claude-opus-5-5` と `anthropic/claude-opus-5.5` を同一モデルとして扱う。

### v1.8.12 (261001)

- レビュアー推奨モデル：`manuwright setup` が OpenRouter（balanced、budget、strong）と opencode（Go、Go budget）の推奨セットを番号で提示。GLM、Kimi、MiniMax、DeepSeek、Qwen、Xiaomi MiMo、Meituan LongCat の最新モデルを実際の一覧で確認し、レビュー 1 回の概算費用を表示。入力した ID には近い候補を提案。`manuwright models` でセットを表示。既定の OpenRouter モデルは balanced セットに変更。無料・contributor 版はプロンプト保存の可能性があるため除外。

### v1.8.11 (261001)

- Obsidian 接続時の端末フリーズを修正：エージェントの状態確認（`codex`/`claude`/`agy mcp …`）を端末から切り離して実行。エージェント CLI が端末を raw モードのまま残し Enter が効かなくなる問題を解消。質問前に端末を復元し、Ctrl-C/Ctrl-D は「いいえ」として扱う。

### v1.8.10 (260930)

- ジャーナル別参考文献形式：`project.json` の `"journal"`（または `format-references --journal`）で 14 プリセット — ICMJE/Vancouver、AMA（JAMA）、NEJM、Lancet、Spine、The Spine Journal、BJJ、JBJS、Neurospine、J Neurosurg Spine、Global Spine J、CORR、Asian Spine J、Eur Spine J。著者数の打ち切り、ページ・号・月・DOI 形式、CORR のアルファベット順、隣接引用のまとめ（`[1–3]`、Word 上付き）。`--fetch` が PubMed の完全な書誌をキャッシュ。

### v1.8.9 (260930)

一括リリース：

- `manuwright setup`：メインモデル、レビュアーとそのモデル、Word スタイル、自動更新、Obsidian ライブラリを一度に設定する対話型コマンド。
- DOCX スタイルを設定可能に：`manuwright config set docx.<キー> <値>` で既定スタイルを保存（フォント、サイズ、見出し・小見出しサイズ、行間、余白、行番号 continuous/page/off、ページ番号 center/right/off）。`project.json` の `"docx"` ブロックが論文（投稿先ジャーナル）ごとに上書き。適用スタイルは `build.json` に記録。どちらもなければ出力は従来どおり。
- `manuwright obsidian install`：Obsidian プラグインを GitHub の最新リリースから選択した vault にインストール（先に確認、有効化、MCP アクセスは任意、上書きしない）。プラグインがなければ `agents install` が提案。
- Obsidian 連携を任意（推奨）と明記。プラグインがない場合、`agents install` は 1 行の推奨案内のみ表示。
- v1.8.8 後の CI 修正：ホームディレクトリのない環境でもレビュアー設定を読めるように。Windows で POSIX パス文字列を比較していたテストを修正。

### v1.8.8 (260930)

1 つのまとめリリース（著者の要望により、修正ごとではなくまとめてバージョンを上げる）：

- **任意のレビュアー、任意のモデル。** `critical_review.py --reviewers agent[:model]` が `openrouter:<id>`、`claude`、`codex`、`opencode`、`muse`、`agy` を受け付け、それぞれモデルを指定可能。ローカル CLI は空の一時フォルダで読み取り専用/plan モードで動作し、テキストのみで回答するよう指示（そうしないと Antigravity がシェルツールを使おうとして headless で自動拒否され、出力が空になった）。デモ原稿で試験：Codex、opencode（kimi-k3）、Muse、Antigravity、OpenRouter の 4 モデルがすべて完全なレビューを返した。
- **設定。** `manuwright config set main-model|review.reviewers|review.openrouter-models|review.<agent>-model ...`（および `unset`）。レビューは既定でこの設定を使う。main モデルと同じモデルのレビュアーは `not_independent` と表示。
- **Obsidian 連携。** `manuwright obsidian status|connect` が「Academic Paper Citation Manager」の MCP サーバー（`rag-obsidian`）を Claude Code、Codex、opencode、Antigravity、Muse に登録（先に確認し、接続済みはスキップ、編集する JSON はバックアップ）。プラグインがあれば `manuwright agents install` が接続を提案。`manuwright evidence import-obsidian <citekey>` は vault ノート（CSL 項目と AI 要約）を `abstract-only` の根拠項目にする。この Mac で確認：Codex、Muse、opencode が MCP でライブラリを呼び出した。Claude Code は接続済み、Antigravity は初回の MCP 呼び出しを対話的に許可する必要がある。
- マニュアル：投稿段階（バインディング、チェックリスト、レビュー回数、stale、ビルド）、Obsidian・レビュアーの節を追加。
- 414 tests 通過。

### v1.8.7 (260930)

- **PubMed 取り込みの参考文献文字列**：`search_pubmed.py` が "et al.." と書き、タイトルと誌名の間のピリオドが抜けていた（"...: A meta-analysis J Back Musculoskelet Rehabil"）ため、ビルドされたすべての参考文献リストに現れていた。修正しテストを追加（旧テストは二重ピリオドを前提にしていた）。合成デモ論文の最初の DOCX パッケージを目視確認中に発見。

### v1.8.6 (260930)

2 回目のエンドツーエンド試験：4 つのエージェントがセクションを分担（Codex が Methods、Antigravity が Results、Muse が Introduction、opencode が Discussion）。Claude が Title/Abstract/Conclusion を書き、draft profile は PASS。Codex が独立した semantic reviewer を担当（1 回目 13 件、2 回目に 12 件解決、1 件は Rule 9 に従いユーザーへ）。途中で見つけて直したエンジンの問題：

- 編集時の lint hook が論文独自の用語集を無視し、承認済み計画が選んだ用語（"MIS"）を禁止語として指摘し続けた。最も近い `project.json` の `terminology` を `verify` と同様に読むよう修正。
- `init` で作る manifest には `ai_usage.json`/`checklist.json` が含まれ、これら投稿用の記録ができる前は `verify --profile draft` と `packet` が "No such file" で停止していた。存在するまでスキップするよう修正。submission profile は引き続きブロック。
- `manuwright search "<query>"` がドキュメントどおり動作（`search` サブコマンドを省略可）。
- スクリーンショット付きユーザーマニュアルを新設：`docs/manual.md`、`docs/manual.ko.md`。
- 406 tests 通過。

### v1.8.5 (260930)

合成臨床試験データでのエンドツーエンド試験（init、解析計画、承認、解析、表、検査）で発見：

- **テンプレートの hook が `cd` 後に黙って無効になる問題**：`.claude/settings.json` が `sh scripts/hooks/run.sh ...` を相対パスで呼んでいた。エージェントがシェルで移動するとすべての hook が exit 127 で失敗し、Claude Code はこれを非ブロッキングのエラーとして扱うため、plan-first の書き込みが許可されていた。hook コマンドを `$CLAUDE_PROJECT_DIR` 基準に固定。無関係なフォルダから gate を実行する回帰テストを追加。
- `verify` が "one or more declared artifacts are missing" の代わりに欠けているファイル名を表示。
- 同じ試験で確認：計画承認前は解析スクリプトをブロック、`record-approval` 後は許可。draft plan 未承認で Results セクションをブロック。表の数値 50 個が結果 CSV と一致。誤った平均（61.2）を最も近い実際の値（60.4）とともに検出。
- 403 tests 通過。

### v1.8.4 (260930)

- **新しい README**：人気のエージェントツールのリポジトリ形式に刷新。ロゴ、一行紹介、バッジ、導入前/導入後、仕組み、エージェント別インストール、コマンド、ワークフロー、FAQ（英・韓・日・中）。旧 README の内容はそのまま `docs/guide/overview*.md` へ、変更履歴は `CHANGELOG*.md` へ移動。
- **ロゴ**：チェックマークで切り抜いた万年筆のペン先（職人 + 検証）。Antigravity で制作。`assets/logo.png`（メイン）、`assets/logo-alt.png`（ペン先からチェックが伸びる版）。それぞれ透明なダークモード版と元画像を同梱。
- WORKFLOW Rule 12 のバージョン・変更履歴の更新先を plugin manifest、README のインストールタグ、`CHANGELOG*.md` に変更。

### v1.8.3 (260930)

- テスト分離：インストール版テストが一時プロジェクトを実際の `~/.manuwright/projects.json` に登録していた。一時的な `MANUWRIGHT_HOME` を使うよう修正。エンジン変更なし。

### v1.8.2 (260930)

- **`paperflow` を `manuwright` に改名**（"manuscript" + "-wright"、playwright のように「作る職人」）。`paperflow` は PyPI と GitHub で既に使われていた。コマンド `manuwright`、パッケージ `manuwright/`、plugin `manuwright@manuwright`、skill `manuwright`・`manuwright-verify`、設定フォルダ `~/.manuwright`、環境変数 `MANUWRIGHT_*`。以下の過去の項目はリリース当時の名前のまま。
- v1.8.0/1.8.1 からの移行：旧インストール（各エージェントの `paperflow` plugin・skill、`uv tool uninstall paperflow`）を先に削除し、`manuwright` をインストールして `manuwright agents install` を実行。プロジェクト一覧と設定を残すには `~/.paperflow` を `~/.manuwright` に移動。

### v1.8.1 (260930)

- **Codex の強制を修正**：Codex は `apply_patch` でファイルを書き、patch を `tool_input.command` に入れる（`file_path` なし）。そのため plan-first ゲートが Codex で動作していなかった。gate・lint hook が patch 内のすべてのファイルパスを読むよう修正し、hook matcher に `apply_patch` を明記。v1.8.0 インストール後の実際の Codex セッションで発見。
- `doctor` の pytest 警告はソース checkout でのみ表示。`paperflow agents` の出力が子プロセスの出力と混ざらないように修正。
- 401 tests 通過（Codex patch テスト +3）。

### v1.8.0 (260930)

マイルストーン：**2 方式の配布**。同じエンジンを clone して使うテンプレート（A、従来どおり）としても、Claude Code・Codex・Antigravity・opencode・Muse 用アダプター付きのインストール型 `paperflow` CLI（B）としても使える。v1.7.6〜v1.7.10 をまとめ、以下を追加：

- README「インストール：2 つの方式」節、`docs/migration_guide.md`（コピーしたフォルダの任意・非破壊移行、A 方式の更新ファイル一覧）。
- `docs/distribution_plan.md` を実装済みに更新。
- `paperflow update` はリリースタグ `vX.Y.Z` を更新チャネルとして使う。

### v1.7.10 (260930)

- **フェーズ 4、エージェントアダプター**：1 つのインストールに Claude Code・Codex 用 plugin（skill `paperflow`・`paperflow-verify`、セッション規則・plan-first ゲート・lint・style の hook）、Antigravity（`agy`）用のルート `plugin.json`、Muse・opencode 用 skill を同梱。`paperflow agents install|update [--only ...] [--dry-run]` が各エージェントのネイティブコマンドを実行。インストール済みエンジンフォルダを plugin ルートとして使うため、アダプターは常に CLI と同じバージョン。plugin hook は `paperflow hook <name>` を呼び、独自 hook を持つテンプレート checkout では何もしない。plugin と CLI のバージョン差を警告し、自動更新が有効ならバックグラウンドでアダプターを更新。
- `paperflow init` が共通の `docs/agent_bootstrap.md` の規則を `CLAUDE.md`/`AGENTS.md`/`GEMINI.md` に書き込む。
- 398 tests 通過（アダプター +8）。`claude plugin validate`・`agy plugin validate`・`muse skills validate` で検証。

### v1.7.9 (260930)

- **フェーズ 3、セットアップと更新**：`paperflow init`（エンジンのテンプレートから論文フォルダを作成、上書き・承認チェックなし）、`paperflow rules [keyword]`、`paperflow update [--check|--to]`（タグ付きリリースを再インストール、ログ記録、1 コマンドでロールバック）、任意の `paperflow config set auto-update on`。自動更新は patch リリースのみ・1 日 1 回まで。登録済みプロジェクトがエンジンを固定しているか、有効な semantic review / human signoff がある場合は適用せず待機。
- manifest の `engine` 固定（例：`">=1.8,<1.9"`）。不一致なら `verify` が `engine_pin` BLOCKED。
- 390 tests 通過（lifecycle +10）。

### v1.7.8 (260930)

- Windows CI 修正：v1.7.5 のテスト 2 件がスナップショットキーを `/` で比較していた。キーは OS の区切り文字を使う。期待値を `Path` で生成するよう修正。エンジン変更なし。

### v1.7.7 (260930)

- **インストール型 CLI、フェーズ 2（プレビュー）**：`pyproject.toml` でエンジンを `paperflow` としてパッケージ化（`uv tool install git+...@tag`）。`paperflow doctor|status|verify|packet|build|record-approval` は `python -m harness` と同等。`paperflow citations|numbers|gate|lint|verify-all|search|...` は各スクリプトを同じオプションで実行し、省略されたプロジェクトパスを現在のフォルダから補う。wheel は許可リストのみ（コード・用語集・WORKFLOW・docs・gate テンプレート）。PDF・profile・原稿・データは含まない。
- `check_gate.py` / `verify_all.py`：プロジェクトルート用 `--base-dir` を追加（既定値は変更なし）。
- CI が wheel をビルド・インストールし、パッケージ外でインストール版テストを実行。380 tests 通過（インストール専用 +3）。

### v1.7.6 (260930)

- **配布計画**（`docs/distribution_plan.md`）：1 つのリポジトリで 2 方式。A は従来どおり clone して使うテンプレート。B（v1.8.0 予定）はインストール型 `paperflow` CLI と Claude Code・Codex・Antigravity（`agy`）・opencode・Muse 向けの薄いアダプター。更新は自動で確認し、適用は明示的に行う。任意の自動更新は論文の有効なレビューを stale にしない。Codex（gpt-6-astra）とレビューし、Spec Kit・OpenSpec・caveman・ponytail と比較。
- **フェーズ 1 互換性契約**（`tests/test_compat_contract.py`、22 tests）：全スクリプトがインストールなし・無関係な cwd（空白・非 ASCII パス）・`PYTHONPATH` なしで動作。従来の citation/number の既定パスはエンジン基準のまま。gate hook はイベント cwd から編集ファイルを解決。1 プロセス内の 2 つの manifest は独立。
- 379 tests 通過。

### v1.7.5 (260929)

Claude + Codex（gpt-6-astra）共同レビューによる改善。

- **提出記録をフィールド単位で検証**：チェックリスト項目ごとに一意の id が必要、PASS には原稿内の位置、NOT_APPLICABLE には理由が必要、その他のステータスは失敗。以前は `{"status":"PASS"}` だけで通過していた。AI 使用時は `tools` の各項目に `tool` と `role` が必要。
- **abstract の同一性**：manifest の `abstract` は公開 `artifacts` に含まれる必要があり、公開される abstract ファイルは必ず宣言する。別ファイルの検査や無言のスキップを防ぐ。
- **プロジェクト用語集・Style Spec**：manifest に任意キー `terminology`・`style_spec` を追加。lint はプロジェクト用語集を使い、`style_metrics` が `check_style.py` を実行し、両ファイルが review snapshot に入る。
- **失敗理由の表示**：harness の `detail` に `False` ではなく最初の問題（ファイル・行・値）を表示。packet にチェックリスト・AI 記録を含め、ハッシュのみの `omitted_sources` を一覧表示。
- **事前点検**：`doctor` が `python_supported` を報告し、Claude gate hook を実際に実行し（`hooks.ok`）、`warnings` を出力。hook のエラーは黙って通過せず WARNING を出力。Python がない場合 `run.sh` が警告。`requirements-dev.txt` を新設（CI で使用）。
- **コンテキスト削減**：フォルダツリー・ファイル役割表・コマンド一覧・PubMed オプションを毎セッション読み込まれる `WORKFLOW.md`（56 KB → 30 KB）から `docs/workflow_reference.md` へ移動。コマンド例は `python scripts/...` 形式に統一。`/verify` の例に `--cross-check` を追加。
- 357 tests 通過。`docs/harness_guide.md` v1.0.5。

### v1.7.4 (260908)

- **`profile/` テンプレートを同梱**：`profile/example_authors.md`（責任著者・共著者・funding 定型文・IRB/臨床試験登録の placeholder 骨格）と `profile/example_journals.md`（13 誌の完成例 — 本文引用形式、著者 cutoff、page range、ORCID 方針、投稿チェックリスト）。コピーして `profile/authors.md`・`profile/journals.md` として使い、その 2 ファイルは引き続き gitignored。
- `.gitignore`：`profile/` → `profile/*` と否定パターン。git は親ディレクトリが除外されているとその配下のファイルを再包含できないため、従来のパターンではテンプレートを追加できなかった。実際の profile ファイルは引き続き無視される（実証確認済み）。
- **テスト移植性の修正**：`test_cli_verify_hash_resolves_relative_paths_from_project_root` がこのテンプレートリポジトリにしか存在しない `drafts/05_results.md` をハッシュしていたため、`drafts/` を論文ごとに分ける実プロジェクトでは常に失敗していた。ハーネス自身が同梱するファイルをハッシュするよう変更。

### v1.7.3 (260908)

- 韓国語 Windows で v1.7.2 を検証：344 テスト、CI 9/9、実 CLI による合成エラー注入シナリオ 37 件 — v1.7.1 の draft/revision 25 件に加え、`numeric_scope`（numeric_artifacts/除外なしで結果以外のセクションに数値、空の理由、結果ファイルの除外試行、バインド済みファイルの除外試行）・`revision_scope`（REVn があるのに元セクションを列挙、CHANGE 対象が artifacts にない、REV2 レターに REV1 artifacts）の新規 12 件。すべて設計どおりブロック/通過。
- `docs/project.example.json`：v1.7.2 の新フィールド `numeric_exemptions` キーをテンプレート manifest に追加。
- README ko/ja/zh：v1.7.2 の changelog 項目をローカライズ（英語のみだった）。ヘッダー → v1.7.3；`harness/__init__.py`（doctor）→ 1.7.3；`docs/harness_guide.md` → v1.0.3。

### v1.7.2 (260907)

- revision claim と各セクションの最新版を実際の投稿ファイルにバインド（`revision_scope`）。
- 数値チェック対象から漏れた原稿ファイルを拒否；結果以外のセクションの除外は `numeric_exemptions` に明示的な理由が必要（`numeric_scope`）。
- ヘッダーに数字が含まれていても p 値の表カラムを区切り行から認識；ヘッダーの数字チェックは維持。
- doctor のバージョンを同期し、submission scope の回帰テストを追加。

### v1.7.1 (260908)

**v1.7.0（PR #1）merge 後の検証 — 欠陥 4 件修正、ドキュメント同期**

- **v1.7.0 では CI が一度も実行されていなかった。** `.github/workflows/tests.yml` の OS マトリクス行が setup-python の `with:` 配下に誤って入り、すべての実行が YAML 解析段階で失敗（0 秒）。3 OS × 3 Python のマトリクスが実際に実行されるようになった（main で 9/9 成功）。
- **Windows cp949:** 新規の `test_harness.py` / `test_review_regressions.py` が `encoding='utf-8'` なしでファイルを読み、韓国語 Windows で 3 件失敗 — 停止していた CI に隠れていた。修正；333 テスト成功。
- **ビルドのファイル名:** `harness build` が UTC 日付を付与し（KST 00〜09 時は前日の `_YYMMDD`）、revision パッケージに `_REVn` も付けていなかった（Rule 5）。初回投稿は `manuscript_YYMMDD.docx`、revision は `manuscript_REV1_YYMMDD.docx` / `response_letter_REV1_…` / `table_N_REV1_…` に。合成 REV1 ビルドテストを追加；`docs/harness_guide.md` v1.0.1。
- **`CLAUDE.md` が `WORKFLOW.md` を import**（`@WORKFLOW.md`）— 「先に読め」という指示に頼らず、Claude Code が共有ルールを自動読み込み。`WORKFLOW.md`/README に残っていた「CLAUDE.md がコアルールファイル」という参照を `WORKFLOW.md` に修正。
- 合成プロジェクトで実 CLI によるエンドツーエンド検証：draft プロファイル 12 件・revision プロファイル 13 件のエラー注入シナリオ（未登録引用、`todo` evidence、CSV にない数値、承認後の plan 変更、ghost revision、未回答/placeholder 回答、REV2↔REV1 baseline）がすべて設計どおりブロックされた；DOCX 構造は `docs/docx_guide.md` と一致。

### v1.7.0 (260906)

- F01–F09 を修正：引用 status/重複 ID、p 値の境界、placeholder、ゲート identity、plan の完全性、revision baseline、reviewer fallback。
- 共有 WORKFLOW.md と標準 AGENTS.md・GEMINI.md ブートストラップを追加。
- manifest ベースの検証プロファイル、context-bound な結果値、content-bound な承認、review packet/state、ゲート付き DOCX パッケージングを追加。
- セットアップ・移行・残る制限は [shared engine guide](docs/harness_guide.md) を参照。

### v1.6.4 (2026-08-30)

**ハーネス全体レビュー（Claude Fable）— 欠陥 16 件修正、回帰テスト 33 件**

- **ゲートの false-PASS / false-FAIL / クラッシュ（HIGH）:** `check_citations.py` が不正・非 ASCII の `[EVID:…]` タグ（`o'brien_2021`、`müller_2020`）をトークン 0 件で PASS させていたのを FAIL に；`search_pubmed.py` は生成 id を slugify し姓全体を使用。`check_numbers.py`：results CSV 行の余剰フィールドでクラッシュしない；原稿の `p<0.001` が CSV セル `<0.001` と一致（同等またはより緩い bound）；大文字 `P<0.05` も p 比較として認識；`L4-5`・`C5-6`・`COVID-19`・`ICD-10` の接尾数字は構造表記として除外；ROUND_HALF_UP も許容（2.675 → 2.68）。
- **強制 hook が実際に有効に:** hook を新設 `scripts/hooks/run.sh`（`py` があれば py、無ければ `python3`）経由で実行 — 従来 macOS/Linux では全 hook が exit 127 となり Rule 7・8 の強制が無音で無効だった。`enforce_gates.py` は承認チェックボックスが**存在しない** plan も未承認扱い（Rule 9 の文言が実際には強制されていなかった）。
- **`check_gate.py`:** artifact パスをスラッシュ非依存で比較（`drafts\05_results.md` == `drafts/05_results.md`、`--verify-hash`/`--cross-check` 含む）；複数ブロックの gate ファイルを `artifact:` 単位で分割し `--artifact` で選択 — 前ブロックの FAIL が後ブロックの PASS に隠れない；複数ブロックで `--artifact` 無しなら loud FAIL。`_TEMPLATE.GATE.md` に記載。
- **`check_response_coverage.py`:** 引用形の角括弧（`[12]`、`[3-5]`、`[EVID:id]`）を placeholder として扱わない — 文献引用付きの反論が通る。
- **細部:** `check_abstract.py` half-up 丸め；`format_references.py` の author-year モードで `author_year_keyword` id を許容（`evidence_guide.md` v0.3.1 と整合）；`compile_response_docx.py` が "# Response to Reviewers" を "Response: to Reviewers" に壊さない；`check_citations`/`check_numbers`/`check_coverage` でコードフェンス後の行番号が正確；`check_coverage.py` は markdown 表の行を個別集計；`check_abbreviations.py` の allowlist が `COVID-19` を語幹で一致；`lint_manuscript.py` はイタリック `*p* = .02` を捕捉し "group = 30" は誤検出しない。
- テスト 262 → 295。

### v1.6.3 (2026-07-02)

**機械的な投稿エラーチェッカー 3 種（advisory 優先）**

- **`scripts/check_crossrefs.py`** — 本文の "Table N"/"Figure N" 言及を実際の `table_*.md`・figure legend 項目と照合：broken reference（これまで何も捕捉できなかった desk-reject 要因）・未引用 table/figure・初出順序。"Tables 1 and 2"・"Figure 2-4"・"Fig. 1A" に対応；コードフェンス/HTML コメントは無視；inventory が無い場合は全件誤検出せず loud にスキップ。既定 advisory、`--fail-on-broken`/`--fail-on-unreferenced`/`--fail-on-order` でゲート化。
- **`scripts/check_abbreviations.py`** — 略語の初出定義 audit。abstract/本文は独立 scope（ジャーナルは両方要求）。`ABBREV_UNDEFINED`/`ABBREV_DEFINED_AFTER_USE`/`ABBREV_REDEFINED`/常時 advisory の `ABBREV_SINGLE_USE`。意図的に advisory — 検出は大文字のみ（2-6 字、`-数字`、複数形 s）、統計略語は既定許可（CI、SD、OR、HR...）+ `--allow` で拡張；`--strict` は定義問題のみゲート化。
- **`scripts/check_response_coverage.py`** — ghost-revision ゲートの裏面：response letter は**すべての**査読コメントに答えたか？ `Reviewer #N:`/`Comment N)`/`Response:` 構造を解析し、未回答・空回答・`[placeholder]` を遮断、`--comments` で元コメントファイルと照合（`COMMENT_UNANSWERED` は失敗；元が解析不能なら警告、`--strict` で失敗）。既定 fail — コメント漏れは二値的欠陥。
- 設計原則（著者フィードバック反映）：機械化は二値的事実のみ、判断は人間+LLM。ドキュメント更新（`CLAUDE.md`、`docs/qc_guide.md` §3.7/§4.2、`docs/revision_guide.md`）。テスト 40 件（計 262）。

### v1.6.2 (2026-07-02)

**Abstract Keywords の強制**

- `drafts/02_abstract.md` 末尾の `**Keywords:**` 行が lint も規則もなく見落とされやすかった。3 層で強制: (1) テンプレートに要件と例を明示、(2) `docs/writing_guide.md` § 02. Abstract に Keywords ルール（3–6 個 MeSH 推奨、セミコロン区切り）を追加、(3) `scripts/lint_manuscript.py` が abstract ファイルを検出し `KEYWORDS_MISSING`/`KEYWORDS_EMPTY`/`KEYWORDS_TOO_FEW`/`KEYWORDS_TOO_MANY` を発火 — PostToolUse の `lint_on_edit` フックが既に編集時に lint を表面化するため、abstract に触れた瞬間に空の Keywords が検出される。`;` と `,` の両方を区切りとして許容。テスト 7 件（計 222）。

### v1.6.1 (2026-06-30)

**`/editor-review` が `/critical-review` と同じレビュアーピッカーを使用**

- editorial desk-screen が `/critical-review` と同一のモデル選択 UX を提供: 同じプール（OpenRouter 4種 `scripts/critical_models.txt` + ローカル Claude + Codex）に対する `AskUserQuestion` レビュアーピッカー、role のみ異なる（`--role editor`、プロンプト `editor.txt`）。`Claude` のみ選択で単一 Opus サブエージェント（キー不要）。Codex は `codex:codex-rescue` で実行（critical_review.py のモデルではない — スクリプトは OpenRouter + ローカル Claude のみ）。コマンド + protocol §5 更新；v1.6.0 で changelog には記載があるのにヘッダーが v1.5.10 のままだった ja/zh README も修正。

### v1.6.0 (2026-06-29)

**Editorial desk-screen — high-impact ジャーナル編集長評価（`/editor-review`）**

- 機械的 QC・reviewer 批判を越えた新評価: **high-impact tier の編集長・臨床編集者による desk-screen**。論文の分野を特定し、その分野の high-impact ジャーナルが実際に掲載する水準でベンチマークして **臨床的妥当性**（practice を変えるか？ p ではなく MCID/effect？）・**scope/novelty fit**・**方法・分析の妥当性** を判定 → `SEND FOR PEER REVIEW`/`BORDERLINE`/`DESK REJECT` + 競争力のための **具体的な追加検証**、または bar が無理なら現実的な下位ジャーナル。
- 正本プロンプト `scripts/critical_prompts/editor.txt`（single source）。単一 Opus サブエージェント（キー不要）**または** `scripts/critical_review.py --role editor` のマルチモデル panel；medical-kag/PubMed で実際の high-impact 文献をベンチマーク（任意）。`/editor-review` で公開、`docs/critical_review_protocol.md` §5 に文書化。判定型（advisory）— grounded ゲートの代替ではない。テスト追加。

### v1.5.10 (2026-06-28)

**テストカバレッジ強化 第2ラウンド（MEDIUM ギャップ）**

- 全レビューの残りカバレッジギャップにテストを追加: `search_pubmed.py` の純粋フォーマッタ（`format_citation` の著者数分岐、`guess_study_design` ラダー）; `check_abstract.py`（abstract が本文より高精度 → fail、整数一致、複数ファイル body 集約、issue に comparator 保持）; `check_numbers.py`（p 値 `>` comparator の pass/fail、heading/`Table N`/`Figure N`/年に対する `is_structural_number`）; `check_style.py`（`mean_sentence_length`/`paragraph_count` tolerance、`split_sentences` の略語/小数保護）; `check_citations.py`（`require_citations`、`fail_abstract_only` トグル）; `format_references.py`（`smith_2020a` の曖昧性解消、`--convert` 書き込みパス）; `check_coverage.py`（`--fail-on-unrealized`）。計 214 テスト（以前 170）。

### v1.5.9 (2026-06-28)

**enforcement パスのテストカバレッジ強化**

- 全レビューのカバレッジ分析で、いくつかの *enforcement 契約* が未テストで、回帰により黙って無効化され得ることが判明。追加したテスト: `verify_all.py` の最上位 `OVERALL: PASS` 判定と `--cross-check`（および `--evidence`/`--results`）の `check_gate.py` への受け渡し; `check_coverage.py` の `--fail-on-over-citation`/`--fail-on-unknown`/`--fail-on-uncited-verified` 終了コード（既定 advisory vs blocking）; `check_revision_claims.py` の `--strict` エスカレーション（original 欠落は既定 warning、`--strict` では failure）。計 170 テスト（以前 163）。

### v1.5.8 (2026-06-28)

**`[EVID:id]` 正規表現の統一（全レビューの整合性修正）**

- `extract_claims.py` は独自の permissive な `[EVID:([^\]]+)]` パターンを使い、`check_citations.py`（およびそれを再利用する `check_coverage.py`・`format_references.py`）は restrictive な `[A-Za-z0-9_.-]+` を使っていた。有効な slugified id は両方とも同一にマッチするが、drift により malformed タグが抽出されても検証/変換されない不整合があった。今後 `extract_claims.py` は `check_citations.py` の正本 `EVID_RE` を import し、4 スクリプトが single source を共有。有効 id の挙動変化なし；163 tests green。

### v1.5.7 (2026-06-28)

**全コード監査で見つかったバグ修正**

- **Gate cross-check が live FAIL なら必ずゲート FAIL**（`check_gate.py`）— 従来は cross-check 次元が live 再実行で FAIL かつ台帳も FAIL を記録していると「一致」とみなして失敗を追加せず、その次元を `--require-check` にしていない場合に**壊れた成果物が通過**し得た。今後 live の決定的失敗は台帳と無関係に常にゲート FAIL。
- **plan-first フックが相対 cwd で fail-open しなくなった**（`hooks/enforce_gates.py`、`hooks/lint_on_edit.py`）— 相対/欠落 `cwd` がパスを `drafts/05_results.md`（先頭スラッシュ無し）に正規化 → `"/drafts/"`/`"/data/.../py/"` チェックが外れ Rule 7/8 ゲートをスキップ。チェック前に先頭スラッシュを強制。（latent: 本番は常に絶対 cwd を送る。）
- 回帰テスト +2（計 163）。

### v1.5.6 (2026-06-28)

**Abstract↔本文の数値整合性 + medical-kag synthesis ワークフロー**

- **`scripts/check_abstract.py`** — abstract に書かれたすべての数値が本文セクションにも現れるか（丸め許容）を確認し、査読者が頻繁に指摘する abstract 限定の数値を検出。`check_numbers.py`（数値↔`results/*.csv`）を補完；p 値トークンは既定で除外（`--include-p-values` で含める）。Rule 3 / QC Round 1 の Abstract↔Methods↔Results↔Tables 整合性を自動化。テスト 5 件。
- **medical-kag synthesis → Discussion/Limitations ワークフロー**（`docs/medical_kag_protocol.md`）— `compare_interventions` / `conflict synthesize` の出力は豊富だが noisy（bibliometric outcome、空値、KG 正規化名）→ 臨床 outcome のフィルタ・全数値/引用の grounding・ゲート通過の方法 + Discussion/Limitations の骨子を文書化。

### v1.5.5 (2026-06-28)

**CI: すべての push/PR でテストを実行**

- **`.github/workflows/tests.yml`** — GitHub Actions が `main` への push と PR ごとに pytest スイート全体を Python 3.10/3.11/3.12 で実行 → 検証スクリプトを壊す変更をマージ前に検出。README 上部にステータスバッジを表示。

### v1.5.4 (2026-06-28)

**MCP 非依存の reference formatter（Phase 7）**

- **`scripts/format_references.py`** — 作成時の `[EVID:id]` タグを投稿用の参考文献リストと本文引用に変換。`knowledge/evidence.md` のみを読む（medical-kag 不要）。2 つのスタイル：**numbered**（Vancouver — `[EVID:id]` → `[N]` を初出順、リストもその順で採番）と **author-year**（`(Author, Year)`、アルファベット順リスト）。`--convert` はタグ置換後を `*_formatted.md` に出力（in-place しない）；evidence.md に無い引用は変換せず報告（さらに exit 非ゼロ）。接続時は medical-kag `reference` ツールと相互補完。テスト 7 件（計 156）。

### v1.5.3 (2026-06-28)

**Coverage audit を過剰引用中心に再フォーカス（orphan=無駄 フレーミングを廃止）**

- **過剰引用の検出** — `check_coverage.py` が 1 文に `--max-citations-per-sentence`（既定 4）を超える `[EVID:id]` 引用を検出（引用の詰め込み/padding）。これと**未登録引用**が本当の品質シグナル → `--fail-on-over-citation` / `--fail-on-unknown` が意味のあるブロッキングフラグ。
- **orphan/未引用を中立に再定義** — 登録済みだが未引用の参照は通常のキュレーション（必要なものだけ引用）であり、**無駄ではない**。従来の "verified work unused" 表現を削除し、未引用 ref・未実現 draft_plan 項目は中立情報として報告。`--fail-on-uncited-verified` / `--fail-on-unrealized` は strict full-use ポリシー専用で既定 off。coverage テスト 8 件（スイート全体 149）。

### v1.5.2 (2026-06-27)

**引用 coverage / orphan audit**

- **`scripts/check_coverage.py`** — `knowledge/evidence.md` に対する Phase 6 QC 監査：**orphan reference**（登録済みだが一度も引用されない。verified-but-uncited は「無駄になった作業」として表示）、セクション別の**引用密度**、**unknown citation**（引用されているが未登録）、さらに `--draft-plan` 指定時は**未実現 claim**（Claim→Citation マッピングで計画されたが本文で未引用）をレポート。デフォルトは advisory、`--fail-on-orphan-verified` / `--fail-on-unrealized` / `--fail-on-unknown` で各次元をブロッキング化。`check_citations.py` のパーサを再利用し両者を lockstep に維持。テスト 7 件（計 148）。

### v1.5.1 (2026-06-26)

**翻訳 README のドキュメント表パリティ**

- 韓国語/日本語/中国語 README の File Roles 表に欠けていた行を `README.md` と一致するよう追加：`docs/debate_protocol.md`・`docs/critical_review_protocol.md`（3言語すべて）、`scripts/critical_review.py`（ja/zh）。ドキュメントのみの変更、コード変更なし。

### v1.5.0 (2026-06-26)

**Gate cross-check（台帳 ↔ live）+ ドキュメント/バージョン自動同期ポリシー**

- **Gate cross-check**（`scripts/check_gate.py --cross-check LABEL=PATH`）— 決定的な次元（`citation` / `numbers` / `revision_claims`）について正本 checker をその場で再実行し、台帳の記録ステータスがどちらの方向であれ実際と一致しない場合はゲートを FAIL にする — stale/偽の `PASS` を検出し、ソース到達不可なら loud FAIL。`scripts/verify_all.py` が転送し、正本ゲートコマンド（`review/gates/_TEMPLATE.GATE.md`、`docs/verification_protocol.md` v0.3.0、CLAUDE.md）に組み込み。回帰テスト +6（計 141）。
- **ドキュメント/バージョン同期 + 自動 commit-push ポリシー**（CLAUDE.md Rule 12）— harness のコード/バグ変更時にバージョンを bump し、影響を受けるドキュメントを更新し、自動でコミット/プッシュ（機微・破壊的なケースには STOP 条件を明記）。

### v1.4.1 (2026-06-24)

**Template gate の強化 + `/verify` freshness 転送**

- **Template-aware plan gates** — `scripts/hooks/enforce_gates.py` は、未解決の `analysis_plan.md` / `draft_plan.md` テンプレートや未チェックの承認欄を承認済み plan として扱わず、`Write|Edit|MultiEdit` すべてに適用されます。正当な citation-style `[N]` テキストは誤検出しないよう保守的に判定します。
- **Fresh `/verify` gate checks** — `scripts/verify_all.py` が `--verify-hash` を `check_gate.py` に転送します。README/CLAUDE/slash-command の例にも freshness 入力を含めました。
- **Windows/template hygiene** — PubMed コマンド例を `python scripts/search_pubmed.py` に統一し、ルート直下の生成 DOCX 成果物を ignore し、hook と freshness 転送の挙動を回帰テストで保護します。

### v1.4.0 (2026-06-24)

**引用スタンス＋エビデンス比較表（GraphRAG ベース）**

- **引用スタンス**（`/cite-stance [claim|section]`）— 引用された各出典が主張に対してどう関係するか（支持 / 対立 / 言及）を分類し、Discussion のバランスを保つ。対立するエビデンスが存在するのに引用されていない場合は「一方的（one-sided）」としてフラグを立てる（省略によるオーバークレームのガード）。新規の Citation-Stance verifier（`docs/verifier_prompt_templates.md`）を追加し、medical-kag の `conflict` が欠落している対立点を浮かび上がらせ、evidence.md へフォールバックする。Scite 流で、主張ごとに特化している。
- **エビデンス比較表**（`/evidence-table [topic|ids]`）— Discussion または PRISMA supplement 向けに「組み入れた研究のまとめ（summary of included studies）」表（study / design / n / intervention / outcome / result / LoE）を組み立てる。`scripts/evidence_table.py` が決定論的なフォーマッタであり、medical-kag の構造化データを主とし、evidence.md へフォールバックする。Elicit 流。テストを追加。

### v1.3.0 (2026-06-24)

**引用アシスト — 候補提示＋主張ごとの検証（GraphRAG ベース）**

- **引用候補の提示**（`/suggest-citation [claim]`）— ドラフト中の主張を入力すると、medical-kag ナレッジグラフ（GraphRAG）を介して最適な `[EVID:id]` 候補を取得し、MCP が利用できない場合は `knowledge/evidence.md` ＋ `scripts/search_pubmed.py` へフォールバックする。最終的に採用するのは著者であり、新規の出典は引用可能になる前に evidence.md へ（PMID/DOI を検証して）登録されるため、grounding が保たれる。
- **主張ごとの検証レポート**（`/verify-claims [section]`）— `scripts/extract_claims.py` が `[EVID:id]` タグ付きの文をすべて抽出し、続いて Semantic-Citation Verifier が各文を SUPPORTED / PARTIAL / UNSUPPORTED に分類して `review/claim_verification.md` に出力する（`check_citations.py` の存在チェックより踏み込んだ、Phase 6 QC の「主張マップ」）。新規の `docs/citation_assist_protocol.md` を追加。いずれの操作も evidence.md へグレースフルに縮退する。テストを追加。

### v1.2.0 (2026-06-22)

**medical-kag MCP 統合 — evidence.md と並走するナレッジグラフ**

- **Grounding を保持した KAG 統合** — `medical-kag-remote` MCP（脊椎外科向けの knowledge-augmented graph）を、上流の探索／分析／整形エンジンとして接続する一方、`knowledge/evidence.md` は唯一の正典となる引用台帳であり続ける。グラフが提示したものは、引用される前に必ず `[EVID:id]`（PMID/DOI を検証済み）として登録されるため、引き続き `check_citations.py` がすべてをゲートする。新規の `docs/medical_kag_protocol.md` が各ツールをフェーズに対応づける — 探索＋構造化抽出（Phase 1）、主張と Discussion のための evidence-chain／intervention-comparison／GRADE 統合（Phase 3-4）、conflict／overclaim ガード（Phase 6）、ジャーナル形式の参考文献リスト（Phase 7）。
- **追加的＋フォールバック** — この MCP は決して依存先ではない。利用できない場合（例：未認証のリモートセッション）、ワークフローは `scripts/search_pubmed.py` ＋手動の evidence.md へとグレースフルに縮退する。CLAUDE.md（Rule 1、STOP signals、Phase 1、Quick Commands）＋ Codex パリティのための AGENTS.md に組み込み済み。

### v1.1.2 (2026-06-21)

**修正 — hook が UTF-8 で stdin を読み取る（Windows での韓国語意図）**

- `UserPromptSubmit` / `PreToolUse` / `PostToolUse` の各 hook が、stdin を UTF-8 に再構成するようになった。Windows（既定は cp949）では Claude Code が出力する JSON ペイロードが誤ってデコードされ、非 ASCII のプロンプト（例：韓国語の自動トリガー「학술적으로 바꿔줘」）がマッチに失敗して何も起きなかった。エンドツーエンドの UTF-8 stdin テストを追加。

### v1.1.1 (2026-06-21)

**スタイルの強制 — 計測可能なゲート＋Codex パリティ**

- **決定論的なスタイルメトリクス** — `scripts/check_style.py`（`extract` / `check --spec`）が単語数、平均文長、段落数、引用密度、hedging を計測し、Style Spec の目標値からの逸脱を検出する — いわば「スタイル版 check_numbers」。`lint_on_edit.py`（Style Spec が存在する場合、各草稿編集時に `[STYLE-METRIC]` の逸脱を提示）および Phase 5/6 のゲートに組み込まれている。テストを追加。
- **Codex パリティ＋キャリブレーション** — hook は Claude Code 専用であるため、`AGENTS.md` は Claude 以外のランタイムに対し、style-pass（`check_style.py` ＋ Style-Conformance verifier）を明示的に実行するよう指示するようになった。Style Spec テンプレートには before→after のキャリブレーション例を追加（few-shot は抽象的なルールよりも変換をうまく導く）。

### v1.1.0 (2026-06-21)

**スタイル変換 — 粗削りの草稿から、整ったジャーナルスタイルへ確実に**

- **Style Spec ＋ Style-Conformance Verifier** — 1 つの手本（`Style/own/` または `Style/target_journal/`）を、常時ロードされるコンパクトな `drafts/style_spec.md`（`docs/style_spec_template.md`）に束ね、セクション単位で変換したうえで、各セクションを独立した **Style-Conformance Verifier** で spec と照合する（auto-fix ループ、最大 2 回；`docs/verifier_prompt_templates.md` ＋ `verification_protocol.md`）。これにより lint では届かない全体的なスタイル層（構造、文の長さ、hedging、主張の強さ、参考文献形式）に到達する。新コマンド `/style-pass` ＋ `docs/style_transform_protocol.md`。
- **意図による自動トリガー** — `UserPromptSubmit` hook（`scripts/hooks/style_intent.py`）が「make it academic / 학술적으로 바꿔줘」を検出して style-pass プロトコルを注入するため、コマンドを覚えていなくても変換が起動する。SessionStart でもアクティブな Style Spec を提示するようになった。Advisory ＋ fail-open。テストを追加。

### v1.0.3 (2026-06-20)

**クロスランタイム批判的レビュー＋モデル選択**

- **Claude-CLI reviewer** — `scripts/critical_review.py --include-claude` はローカルの `claude -p`（ヘッドレス）をシェル経由で呼び出すため、Claude Code 以外の呼び出し元（Codex や素のシェル）でも Claude の敵対的レビューを取り込める。`OPENROUTER_API_KEY` は OpenRouter モデルが実際に要求された場合にのみ必要となった。`docs/critical_review_protocol.md` ＋ `AGENTS.md` に文書化。
- **モデルプールの拡張＋約2個を選択** — `scripts/critical_models.txt` に MiniMax M3、GLM 5.2、Qwen3-Max、DeepSeek V4 Pro を追加；`/critical-review` はこれらを個別の `AskUserQuestion` 選択肢として提示し、約2個の選択（コスト＋盲点の多様性）を推奨したうえで `--models <selected>` を実行する。

### v1.0.2 (2026-06-20)

**プロセス強制＋CLAUDE.md の圧縮**

- **Plan-first 強制（hooks）** — `.claude/settings.json` にコミット済みの hooks を追加：PreToolUse の `Write|Edit|MultiEdit` ゲート（`scripts/hooks/enforce_gates.py`）は、完了・承認済みの `drafts/.../draft_plan.md` なしのセクション執筆（Rule 8）や、完了・承認済みの `data/.../analysis_plan.md` なしの分析スクリプト作成（Rule 7）を **ブロック** し、SessionStart hook（`scripts/hooks/session_contract.py`）は毎セッションでワークフロー contract を注入する。Revision は対象外、マルチ論文サブフォルダにも対応、fail open、UTF-8 セーフ。（Windows は `py`；macOS/Linux は `python3`。）
- **`/verify`** — `scripts/verify_all.py` が check_citations ＋ check_numbers（＋任意で check_gate）を 1 コマンドで実行し、ゲートの PASS を記録する前に確認する。文書化された freshness チェックを維持するため `--verify-hash` を転送し、hook と freshness 転送の挙動は回帰テストで保護されている。
- **CLAUDE.md を 808 → 696 行に圧縮（約 14%）** — マルチ論文/Revision の構造ツリーと、Phase 2 の Notes／検定選択／style-priority／ゲート配置の重複を、各正本ドキュメントへのポインタに集約。MUST-FOLLOW ルールは一つも削除していない。

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
- プログラム的 citation checker：`python scripts/check_citations.py drafts/03_introduction.md --evidence knowledge/evidence.md`
- プログラム的 number checker：`python scripts/check_numbers.py drafts/05_results.md drafts/table_1.md --results results`
- プログラム的 phase gate checker：`python scripts/check_gate.py review/gates/phase_04_draft.GATE.md --artifact drafts/05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic --verify-hash artifact=drafts/05_results.md`
- プログラム的 ghost-revision checker：`python scripts/check_revision_claims.py drafts/revision/REV1/response_letter_REV1.md --strict`
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
- `scripts/lint_manuscript.py` を追加し、Windows 上で `python scripts/lint_manuscript.py drafts --quiet` により manuscript linting が通過するよう draft/table テンプレートを更新。
- agent 起動指示として `AGENTS.md` を追加し、`CLAUDE.md` を権威ある source of truth とする。
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
