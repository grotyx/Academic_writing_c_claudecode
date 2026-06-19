# Critical-Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 완성된 원고/response를 여러 리뷰어(Claude 서브에이전트·Codex·OpenRouter 모델)가 적대적으로 공격해 허점을 발굴하고, 합의도 기반 통합 리포트로 종합하는 `/critical-review` 기능을 구현한다.

**Architecture:** OpenRouter 멀티 모델 호출은 결정론적 Python 스크립트(`scripts/critical_review.py`, requests, env key)로 격리해 pytest로 검증. Claude(새 서브에이전트)·Codex(codex-rescue)·종합은 에이전트/메인 Claude가 담당. 절차는 `docs/critical_review_protocol.md` 한 곳에 모은다.

**Tech Stack:** Python 3.12(stdlib + `requests`), Claude Code 서브에이전트(Agent tool)·codex-rescue·slash command, OpenRouter chat completions API, git.

**Source spec:** `docs/superpowers/specs/2026-06-19-critical-review-design.md`

## Global Constraints

- OpenRouter 모델 ID **하드코딩 금지** — `scripts/critical_models.txt`로 외부화(한 줄에 하나, `#` 주석 무시).
- 기본 모델: **MiniMax M3, GLM 5.2** (정확한 OpenRouter slug는 Task 2에서 카탈로그로 확정).
- OpenRouter 호출: `requests`, env `OPENROUTER_API_KEY`. key 없으면 명확한 에러로 exit 2.
- **review-only**: 발견 허점을 자동 수정하지 않는다.
- **종합은 메인 Claude**(스크립트가 아님). 스크립트는 모델 호출·파싱·실패 skip까지만.
- **폴백**: OpenRouter/Codex 실패해도 Claude 서브에이전트 단독으로 가능 → 막히지 않음.
- 기존 컨벤션 준수: docs 가이드 + command + 게이트 원장, `requirements.txt` 의존성 선언, 한/영 혼용.

---

## File Structure

**신규:** `scripts/critical_review.py`(OpenRouter 호출), `scripts/critical_models.txt`(모델 목록), `tests/test_critical_review.py`, `docs/critical_review_protocol.md`(절차 단일 기준), `.claude/commands/critical-review.md`, `review/critical/_TEMPLATE.critical.md`, `review/critical/.gitkeep`
**수정:** `requirements.txt`(requests), `CLAUDE.md`, `docs/qc_guide.md`

Task 1이 핵심 코드(TDD), Task 2가 모델 목록, 나머지는 문서. 각 task는 독립 커밋.

---

### Task 1: `scripts/critical_review.py` (OpenRouter 멀티모델 호출)

**Files:**
- Modify: `requirements.txt`
- Create: `scripts/critical_review.py`
- Test: `tests/test_critical_review.py`

**Interfaces (Produces):**
- `build_prompt(role: str, target_text: str) -> str`
- `call_model(model_id: str, prompt: str, api_key: str, timeout: int = 120) -> str`
- `run_critical_review(target_text: str, models: list[str], role: str, api_key: str) -> dict[str, str]`
- `load_models(path: str | Path) -> list[str]`

- [ ] **Step 1: `requirements.txt`에 requests 추가**

`python-docx>=1.1.0` 줄 아래에 추가:
```
requests>=2.31.0     # OpenRouter calls in scripts/critical_review.py
```

- [ ] **Step 2: 실패 테스트 작성 — `tests/test_critical_review.py`**

```python
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "critical_review.py"


def load_module():
    spec = importlib.util.spec_from_file_location("critical_review", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BuildPromptTests(unittest.TestCase):
    def test_manuscript_prompt_embeds_target_and_adversarial_framing(self) -> None:
        m = load_module()
        out = m.build_prompt("manuscript", "The drug cured everyone.")
        self.assertIn("The drug cured everyone.", out)
        self.assertIn("reviewer", out.lower())

    def test_response_prompt_uses_rebuttal_framing(self) -> None:
        m = load_module()
        out = m.build_prompt("response", "We added a sentence.")
        self.assertIn("We added a sentence.", out)
        self.assertIn("reviewer", out.lower())


class CallModelTests(unittest.TestCase):
    def test_call_model_posts_and_parses_choice(self) -> None:
        m = load_module()
        fake = mock.Mock()
        fake.json.return_value = {"choices": [{"message": {"content": "weak stats"}}]}
        fake.raise_for_status.return_value = None
        with mock.patch.object(m.requests, "post", return_value=fake) as post:
            out = m.call_model("minimax/minimax-m3", "attack this", "KEY")
        self.assertEqual(out, "weak stats")
        args, kwargs = post.call_args
        self.assertEqual(kwargs["json"]["model"], "minimax/minimax-m3")
        self.assertIn("Bearer KEY", kwargs["headers"]["Authorization"])


class RunCriticalReviewTests(unittest.TestCase):
    def test_failed_model_is_skipped_others_kept(self) -> None:
        m = load_module()

        def side_effect(model_id, prompt, api_key, timeout=120):
            if model_id == "bad/model":
                raise RuntimeError("boom")
            return f"findings from {model_id}"

        with mock.patch.object(m, "call_model", side_effect=side_effect):
            out = m.run_critical_review(
                "text", ["good/a", "bad/model", "good/b"], "manuscript", "KEY"
            )
        self.assertEqual(set(out), {"good/a", "good/b"})
        self.assertNotIn("bad/model", out)


class LoadModelsTests(unittest.TestCase):
    def test_load_models_ignores_comments_and_blanks(self, ) -> None:
        m = load_module()
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "models.txt"
            p.write_text(
                "# comment\nminimax/minimax-m3\n\n  z-ai/glm-5.2  \n",
                encoding="utf-8",
            )
            self.assertEqual(
                m.load_models(p), ["minimax/minimax-m3", "z-ai/glm-5.2"]
            )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: 테스트 실패 확인**

Run: `python -m pytest tests/test_critical_review.py -q`
Expected: FAIL (ModuleNotFoundError / `critical_review.py` 없음)

- [ ] **Step 4: `scripts/critical_review.py` 구현**

```python
#!/usr/bin/env python3
"""Call OpenRouter models as adversarial peer reviewers.

Deterministic helper for /critical-review. It only calls the OpenRouter
chat-completions API for each model and returns their raw findings; merging
and severity ranking are done by the main Claude agent, not here.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

PROMPTS = {
    "manuscript": (
        "You are an adversarial peer reviewer for a medical research paper. "
        "Attack the text below: find overclaiming, methodological flaws, "
        "logical leaps, overgeneralization, and reproducibility problems. "
        "Be specific and cite the passage. Do not be polite.\n\n---\n{target}"
    ),
    "response": (
        "You are a peer reviewer reading an author rebuttal. Is it "
        "satisfactory? Where would you push back further, and what would you "
        "still reject? Be specific.\n\n---\n{target}"
    ),
}


def build_prompt(role: str, target_text: str) -> str:
    if role not in PROMPTS:
        raise ValueError(f"unknown role: {role}")
    return PROMPTS[role].format(target=target_text)


def call_model(model_id: str, prompt: str, api_key: str, timeout: int = 120) -> str:
    response = requests.post(
        OPENROUTER_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": model_id, "messages": [{"role": "user", "content": prompt}]},
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def run_critical_review(
    target_text: str, models: list[str], role: str, api_key: str
) -> dict[str, str]:
    prompt = build_prompt(role, target_text)
    results: dict[str, str] = {}
    for model_id in models:
        try:
            results[model_id] = call_model(model_id, prompt, api_key)
        except Exception as exc:  # noqa: BLE001 - one model's failure must not abort
            print(f"warning: model {model_id} failed: {exc}", file=sys.stderr)
    return results


def load_models(path: str | Path) -> list[str]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Adversarial OpenRouter critical review.")
    parser.add_argument("--target", required=True, type=Path, help="Target text file")
    parser.add_argument("--models", help="Comma-separated OpenRouter model IDs")
    parser.add_argument("--models-file", type=Path, help="File with one model ID per line")
    parser.add_argument("--role", choices=sorted(PROMPTS), default="manuscript")
    parser.add_argument("--out", type=Path, help="Directory to write per-model raw responses")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("error: OPENROUTER_API_KEY not set", file=sys.stderr)
        return 2

    if args.models:
        models = [m.strip() for m in args.models.split(",") if m.strip()]
    elif args.models_file:
        models = load_models(args.models_file)
    else:
        print("error: provide --models or --models-file", file=sys.stderr)
        return 2

    target_text = args.target.read_text(encoding="utf-8")
    results = run_critical_review(target_text, models, args.role, api_key)

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        for model_id, text in results.items():
            safe = model_id.replace("/", "_")
            (args.out / f"{safe}.md").write_text(text, encoding="utf-8")

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if results else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: 테스트 통과 확인**

Run: `python -m pytest tests/test_critical_review.py -q`
Expected: PASS (5 tests)

- [ ] **Step 6: 커밋**

```bash
git add requirements.txt scripts/critical_review.py tests/test_critical_review.py
git commit -m "feat: add critical_review.py (OpenRouter multi-model adversarial calls)"
```

---

### Task 2: `scripts/critical_models.txt` (기본 모델 목록 + slug 확정)

**Files:**
- Create: `scripts/critical_models.txt`

- [ ] **Step 1: OpenRouter 카탈로그에서 MiniMax M3 / GLM 5.2 slug 확인**

`https://openrouter.ai/models`에서 두 모델의 정확한 ID를 확인한다(WebFetch 또는 사용자 확인). 확인 전 임시 best-guess: `minimax/minimax-m3`, `z-ai/glm-5.2`. 확정 ID로 아래 파일을 작성한다.

- [ ] **Step 2: `scripts/critical_models.txt` 작성**

```
# OpenRouter model IDs for /critical-review (one per line, # comments ignored).
# Verify slugs at https://openrouter.ai/models before relying on them.
# Defaults: MiniMax M3 + GLM 5.2. Add other families (GPT/Gemini/Llama) for
# more blind-spot diversity.
minimax/minimax-m3
z-ai/glm-5.2
```

- [ ] **Step 3: load_models로 읽히는지 검증**

Run: `python -c "import importlib.util,pathlib; s=pathlib.Path('scripts/critical_review.py'); m=importlib.util.module_from_spec(importlib.util.spec_from_file_location('cr',s)); importlib.util.spec_from_file_location('cr',s).loader.exec_module(m); print(m.load_models('scripts/critical_models.txt'))"`
Expected: 두 모델 ID 리스트 출력(주석 제외)

- [ ] **Step 4: 커밋**

```bash
git add scripts/critical_models.txt
git commit -m "feat: add default OpenRouter model list for critical-review"
```

---

### Task 3: `docs/critical_review_protocol.md` (절차 단일 기준)

**Files:**
- Create: `docs/critical_review_protocol.md`

- [ ] **Step 1: 작성 (아래 전체 내용)**

````markdown
# Critical-Review Protocol (외부 멀티모델 적대적 검토)

> 완성된 원고/response를 여러 리뷰어가 적대적으로 공격해 허점을 발굴하는 절차의 단일 기준. `/critical-review` command와 `qc_guide.md`는 이 문서를 참조한다. QC Round 6 Critical Review의 외부 멀티모델 강화판.
> 설계 근거: `docs/superpowers/specs/2026-06-19-critical-review-design.md`.

## 0. 원칙

- **review-only** — 허점을 발굴만 하고 자동 수정하지 않는다.
- **합의도 = 신뢰도** — 여러 리뷰어가 같은 허점을 지적하면 거의 확실한 약점.
- **폴백** — OpenRouter/Codex가 안 돼도 Claude 서브에이전트 단독으로 가능. 막히지 않는다.

## 1. 절차

```
1. 대상 결정    기본 전체 원고 / 지정 부분 / revision: response letter + 원고
2. 리뷰어 선택  멀티 선택: Claude 서브 / Codex / OpenRouter 모델 N개
3. 병렬 공격
     - Claude     → Agent(새 서브에이전트, fresh context) + §2 적대 프롬프트
     - Codex      → codex-rescue(read-only) + §2 적대 프롬프트
     - OpenRouter → python scripts/critical_review.py --target <file>
                    --models-file scripts/critical_models.txt --role <role>
                    --out review/critical/<run>/
4. 종합(메인)   중복 통합(합의도) + 심각도 분류(Critical/Important/Minor)
5. 저장         review/critical/YYYYMMDD_<slug>.md (통합 리포트) + 모델별 원본
```

## 2. 적대 프롬프트 (대상별)

- 원고(manuscript): "동료 심사자로서 overclaiming·방법론 허점·논리 비약·일반화 오류·재현성 문제를 최대한 공격하라. 구체적으로 해당 구절을 인용하라."
- response: "심사자로서 이 답변이 만족스러운가, 어디를 재반박하겠는가."

(스크립트 호출 시 `--role manuscript|response`로 선택. Claude/Codex 호출 시 같은 취지를 프롬프트에 담는다.)

## 3. 종합 — 합의도 × 심각도

통합 리포트는 각 허점을 **심각도(Critical/Important/Minor)** 와 **합의도(몇 명의 리뷰어가 지적했는지)** 로 정렬한다. 여러 리뷰어가 동의한 허점을 위로. 단독 지적은 "다양성 참고"로 표기.

## 4. 에러 / 폴백

| 상황 | 처리 |
|------|------|
| `OPENROUTER_API_KEY` 없음 | OpenRouter만 skip, 나머지 리뷰어로 진행 + 알림 |
| 특정 모델 실패 | 그 모델만 skip (스크립트가 처리), 나머지 계속 |
| Codex 실패 | Codex skip, 나머지 계속 |
| 리뷰어 0개 | 에러(최소 1개 필요) |
````

- [ ] **Step 2: 검증**

Run: `ls docs/critical_review_protocol.md && grep -cE "절차|적대 프롬프트|합의도|에러" docs/critical_review_protocol.md`
Expected: 파일 존재 + 매치 ≥4

- [ ] **Step 3: 커밋**

```bash
git add docs/critical_review_protocol.md
git commit -m "feat: add critical_review_protocol.md"
```

---

### Task 4: `review/critical/` 디렉토리 + 리포트 템플릿

**Files:**
- Create: `review/critical/.gitkeep`
- Create: `review/critical/_TEMPLATE.critical.md`

- [ ] **Step 1: `review/critical/_TEMPLATE.critical.md` 작성**

````markdown
# Critical Review Report

대상: <원고 전체 | 부분 경로 | revision: response+원고>
리뷰어: <Claude 서브 | Codex | OpenRouter: model1, model2 ...>
날짜: <YYYY-MM-DD>

## 통합 허점 (심각도 × 합의도)

### Critical
- [합의 N/총M] <허점> — 지적: <리뷰어들> — 근거: <인용/위치>

### Important
- [합의 N/총M] <허점> — 지적: <리뷰어들>

### Minor / 단독 지적 (다양성 참고)
- <허점> — 지적: <리뷰어>

## 모델별 원본
<review/critical/<run>/ 의 모델별 파일 경로, 또는 요약 링크>
````

- [ ] **Step 2: `.gitkeep` 생성 + 검증**

Run: `touch review/critical/.gitkeep && ls review/critical/.gitkeep review/critical/_TEMPLATE.critical.md && grep -cE "대상:|리뷰어:|통합 허점|모델별 원본" review/critical/_TEMPLATE.critical.md`
Expected: 두 파일 + 매치 ≥4

- [ ] **Step 3: 커밋**

```bash
git add review/critical/.gitkeep review/critical/_TEMPLATE.critical.md
git commit -m "feat: add review/critical report directory and template"
```

---

### Task 5: `/critical-review` slash command

**Files:**
- Create: `.claude/commands/critical-review.md`

기존 command(`paper-debate.md`)의 `args:` frontmatter 형식을 따른다.

- [ ] **Step 1: `.claude/commands/critical-review.md` 작성**

````markdown
---
description: 외부 멀티모델 적대적 critical review (작성 후, docs/critical_review_protocol.md)
args: target
---

`docs/critical_review_protocol.md`를 기준으로 critical review를 수행한다.

대상: **$ARGUMENTS** (생략 시 전체 원고; revision 맥락이면 response letter + 원고)

절차:

1. 대상 텍스트를 확정한다(프로토콜 §1).
2. 리뷰어를 `AskUserQuestion`으로 멀티 선택: Claude 서브 / Codex / OpenRouter 모델(`scripts/critical_models.txt`). 최소 1개.
3. 병렬 공격(프로토콜 §1·§2):
   - Claude → Agent로 새 서브에이전트(fresh context)에 적대 프롬프트.
   - Codex → `codex:codex-rescue` read-only에 적대 프롬프트.
   - OpenRouter → `python scripts/critical_review.py --target <file> --models-file scripts/critical_models.txt --role <manuscript|response> --out review/critical/<run>/`.
4. 메인 Claude가 종합(§3): 중복 통합 + 심각도 분류.
5. `review/critical/`에 통합 리포트 + 모델별 원본 저장(§1, 템플릿 `_TEMPLATE.critical.md`).
6. 에러·폴백은 §4를 따른다(외부 실패해도 Claude 단독으로 진행).
````

- [ ] **Step 2: 검증**

Run: `ls .claude/commands/critical-review.md && grep -cE "description:|args:|critical_review_protocol.md|critical_review.py" .claude/commands/critical-review.md`
Expected: 파일 존재 + 매치 ≥4

- [ ] **Step 3: 커밋**

```bash
git add .claude/commands/critical-review.md
git commit -m "feat: add /critical-review slash command"
```

---

### Task 6: `CLAUDE.md` 통합

**Files:**
- Modify: `CLAUDE.md` (Collaboration 명령, QC Round 6, File Roles, 트리)

- [ ] **Step 1: Collaboration 표에 `/critical-review` 행 추가**

`### Collaboration (Codex)` 표의 `/paper-debate` 행 다음에 추가:
```
| `/critical-review <대상>` | 외부 멀티모델 적대적 검토 (작성 후, `docs/critical_review_protocol.md`) |
```

- [ ] **Step 2: QC Round 6을 2층 구조로 표기**

`## Recommended Workflow`의 Phase 6 블록에서 `Round 6: Critical review` 줄에 외부 옵션 추가:
```
├── Round 6: Critical review — 내부(Dr. Editor+Statistician) + (선택) /critical-review 외부 멀티모델
```
(기존 Round 6 줄을 위 형태로 수정. 정확한 기존 문구는 `grep -n "Round 6" CLAUDE.md`로 확인 후 해당 줄을 교체.)

- [ ] **Step 3: File Roles 표 + 구조 트리 등록**

File Roles 표에 추가:
```
| `docs/critical_review_protocol.md` | 외부 멀티모델 적대적 검토 절차 (리뷰어 풀·합의도·폴백) | Phase 6 QC·Phase 8 (`/critical-review`) |
```
구조 트리 `scripts/`에 `critical_review.py`·`critical_models.txt`, `docs/`에 `critical_review_protocol.md`, `review/`에 `critical/` 추가.

- [ ] **Step 4: 검증 (참조 무결성)**

Run: `grep -q "critical-review" CLAUDE.md && grep -q "critical_review_protocol.md" CLAUDE.md && miss=0; for f in $(grep -oE 'docs/[a-z_]+\.md' CLAUDE.md | sort -u); do test -f "$f" || { echo "MISSING $f"; miss=1; }; done; [ $miss -eq 0 ] && echo OK`
Expected: `OK`, MISSING 없음

- [ ] **Step 5: 커밋**

```bash
git add CLAUDE.md
git commit -m "docs: integrate /critical-review into CLAUDE.md (command, Round 6, roles)"
```

---

### Task 7: `docs/qc_guide.md` Round 6 연결

**Files:**
- Modify: `docs/qc_guide.md` (Round 6 설명)

- [ ] **Step 1: Round 6 섹션에 외부 옵션 1줄 추가**

`grep -n "Round 6" docs/qc_guide.md`로 Round 6 설명 위치를 찾고, 그 설명 끝에 추가:
```
> 외부 강화: `/critical-review`로 여러 모델(Claude 서브·Codex·OpenRouter)이 적대적으로 공격하게 할 수 있다 (선택). 절차: `docs/critical_review_protocol.md`.
```

- [ ] **Step 2: 검증**

Run: `grep -c "critical-review" docs/qc_guide.md`
Expected: ≥1

- [ ] **Step 3: 커밋**

```bash
git add docs/qc_guide.md
git commit -m "docs: link QC Round 6 to /critical-review external option"
```

---

## Self-Review

**1. Spec coverage:**
- spec §3 Architecture(신규 7파일 + 수정 3) → Task 1·2·3·4 (신규), Task 1·6·7 (수정 requirements/CLAUDE/qc). ✓
- spec §4 Flow → Task 3 프로토콜 §1, Task 5 command 절차. ✓
- spec §5 OpenRouter script → Task 1 (인터페이스·env·실패 skip), Task 2 (모델 외부화). ✓
- spec §6 Activation → Task 5 (수동) + Task 6·7 (Round 6 자동 제안). ✓
- spec §7 Error → Task 1 (모델 skip, key 없음 exit 2), Task 3 §4 (폴백). ✓
- spec §9 Open Questions → Task 2(slug), Task 2(외부화 형식=txt), Task 3(리포트 형식). 동시성은 순차 구현(YAGNI; 모델 수 적음). ✓

**2. Placeholder scan:** 모든 코드·테스트·검증 명령·커밋 메시지 실제 값. slug는 Task 2 Step 1에서 카탈로그 확인(best-guess 명시). "적절히/TODO" 없음. ✓

**3. Type 일관성:** `build_prompt`·`call_model`·`run_critical_review`·`load_models` 시그니처가 Task 1 구현·테스트·Task 5 command 호출에서 일관. 모델 목록 `scripts/critical_models.txt`, 로그 `review/critical/`가 Task 2·3·4·5에서 일관. ✓

---

## 참고: 선행 Sub-Project A

`docs/superpowers/plans/2026-06-19-paper-debate.md` (구현 완료) — 작성 전 협력 토론. 본 plan(B)은 작성 후 적대적 검토로 대칭.
