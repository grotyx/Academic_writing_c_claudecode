# Paper-Debate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Claude와 Codex가 co-author로 작성 **전**에 논문 결정(통계 계획·논문 계획·논리 구조·revision 대응)을 토론·합의하고, 그 합의로 산출물을 작성하는 기능을 구현한다.

**Architecture:** Claude(메인 루프)가 토론 오케스트레이터. Codex는 `codex:codex-rescue` 에이전트로 **read-only** 호출(의견 생성), 2라운드+는 `--resume`. 단일 기준 문서 `docs/debate_protocol.md` + slash command + Phase 통합. Codex 실패·미합의 시 **항상 Claude 단독 폴백**.

**Tech Stack:** Markdown 문서, Claude Code slash command(frontmatter + 본문), `codex:codex-rescue` 에이전트(Agent tool), git. 신규 런타임 코드·의존성 **없음**.

**Source spec:** `docs/superpowers/specs/2026-06-19-paper-debate-design.md`

## Global Constraints

- 토론은 **품질 보조** — 통과 필수 게이트가 아니다. Codex 실패·미합의해도 워크플로는 막히지 않고 **Claude 단독으로 폴백**한다.
- Codex 호출은 **read-only**(논문 의견 생성용, 파일 수정 X), `codex:codex-rescue` 에이전트 경유. 2라운드부터 `--resume`.
- 토론은 **작성 전**에 수행 → 합의 → 산출물 작성.
- 깊이: 합의까지 **상한 3라운드**. 미합의 시 차이점 표 + Claude 추천 → 사용자 결정.
- 모든 토론 로그: `review/debates/YYYYMMDD_<slug>.debate.md` (slug 규칙은 Task 1에서 정의).
- 토론 로직은 `docs/debate_protocol.md` 한 곳에만 둔다. command·Phase 가이드는 **참조만** 한다(단일 기준).
- 기존 repo 컨벤션 준수: docs 가이드 + command + 게이트 원장 패턴, 한/영 혼용 서술 스타일.

---

## File Structure

**신규:**
- `docs/debate_protocol.md` — 단일 기준. 라운드·수렴 판정·단계별 역할·프롬프트 템플릿·Codex 호출법·로그 형식·에러 처리.
- `review/debates/.gitkeep` — 디렉토리 유지.
- `review/debates/_TEMPLATE.debate.md` — 로그 템플릿.
- `.claude/commands/paper-debate.md` — `/paper-debate <주제>` 진입점(프로토콜을 가리킴).

**수정:**
- `CLAUDE.md` — Quick Commands·Phase 2/3/4/8 자동 제안·File Roles·구조 트리.
- `docs/statistical_analysis_guide.md` · `docs/draft_plan_template.md` · `docs/revision_guide.md` — 해당 단계에 토론 훅 1줄.

각 task는 독립적으로 의미 있는 커밋을 만든다. Task 1(키스톤)을 먼저 한다.

---

### Task 1: 키스톤 문서 `docs/debate_protocol.md`

**Files:**
- Create: `docs/debate_protocol.md`

**Interfaces (Produces):** 이후 task가 참조하는 이름 — 로그 파일 규칙 `review/debates/YYYYMMDD_<slug>.debate.md`(slug = 주제를 소문자·하이픈, 최대 6단어); 역할 키워드 `통계 담당 공동 저자`·`전략 담당 공동 저자`·`논리 담당 공동 저자`·`공동 저자(co-author)`·`균형 비평자`.

- [ ] **Step 1: `docs/debate_protocol.md` 작성 (아래 전체 내용)**

````markdown
# Debate Protocol (Claude–Codex Co-Author 토론)

> 논문 작성의 사고 단계에서 Claude와 Codex가 **co-author**로 작성 전에 방향을 토론·합의하는 절차의 단일 기준 문서. `/paper-debate` command와 Phase 가이드는 이 문서를 참조한다.
> 설계 근거: `docs/superpowers/specs/2026-06-19-paper-debate-design.md`.

## 0. 원칙

- 토론은 **대립이 아니라 두 co-author의 협력**이다. 건설적 반론은 하되 목표는 합의된 더 나은 결과물.
- 토론은 **작성 전**에 한다. 합의 → 그 합의로 산출물(plan/draft/response) 작성.
- 토론은 **품질 보조**다. Codex 실패·미합의해도 워크플로는 막히지 않고 **Claude 단독으로 진행**한다.

## 1. 라운드 흐름 (합의까지, 상한 3)

```
R0 준비   Claude가 주제에 대한 접근·골격(입장)+근거를 작성 (완성 산출물 아님)
R1        Codex 호출(역할 부여) → Codex 입장 + Claude 안 비판 → Claude 수렴 판정
            ├ 수렴   → 합의 확정
            └ 미수렴 → R2
R2        Claude 재반박/수정안 → Codex(--resume) 재응답 → 수렴 판정
R3        동일 (상한)
상한 후 미합의 → 차이점 표 + Claude 추천 → 사용자 결정
합의 확정 → 합의를 바탕으로 산출물 작성 → 로그 저장
```

## 2. 수렴 판정 (매 라운드 끝, Claude 수행)

- **완전 합의** — 양측 같은 결론·근거 → 종료, 산출물 반영.
- **부분 합의** — 핵심 합의 + 세부 차이 → 합의분 채택 + 차이 명시.
- **미합의** — 핵심 입장 갈림 → 다음 라운드, 상한 시 사용자 에스컬레이션.

## 3. 단계별 Codex 역할

| 단계 | 역할 | 토론 초점 |
|------|------|-----------|
| Planning / 논문 계획 | 전략 담당 공동 저자 | 연구 질문 약점, framing, novelty |
| 통계 계획 | 통계 담당 공동 저자 | 검정 선택 타당성, 가정 위반, 다중비교, 대안 |
| 논리/문단 구조 | 논리 담당 공동 저자 | 논리 비약, 순서, 응집성, 중복 |
| Reviewer response | 공동 저자(co-author) | 코멘트별 최선 대응 + 예상 reviewer 반박 점검 |
| 일반(수동) | 균형 비평자 | 주제에 맞게 자동 설정 |

## 4. Codex 호출 방법

각 라운드에서 Claude는 `codex:codex-rescue` 에이전트(Agent tool)를 **read-only**로 호출한다.

- 1라운드 프롬프트에 `--fresh`, 2라운드+는 `--resume`을 포함한다.
- read-only이므로 `--write`를 쓰지 않는다(Codex는 의견만, 파일 수정 X). 프롬프트에 "read-only: 의견만 제시, 파일 수정 금지"를 명시한다.
- 프롬프트 템플릿:

```
[--fresh|--resume] read-only.
You are a {ROLE}, a co-author on a medical research paper. We are deciding
"{TOPIC}" together BEFORE writing. Give opinion only; do not edit any files.

My current position:
{CLAUDE_POSITION}

As a co-author, give your independent view: where you agree, where you
disagree and why, and what you would do differently. Focus on {FOCUS}.
Be specific and constructive. If my approach has a weakness, say so plainly
rather than just agreeing.
```

`{ROLE}`·`{FOCUS}`는 §3 표에서, `{TOPIC}`·`{CLAUDE_POSITION}`은 현재 토론에서 채운다.

## 5. 로그 형식

`review/debates/YYYYMMDD_<slug>.debate.md` (slug = 주제 소문자·하이픈, 최대 6단어). `_TEMPLATE.debate.md`를 복사해 채운다.

## 6. 에러 처리 / 폴백

| 상황 | 처리 |
|------|------|
| Codex 호출 실패(빈 출력) | 토론 중단 → Claude 단독 진행 폴백 + 사용자 알림 |
| 상한 3라운드 미합의 | 차이점 표 + Claude 추천 → 사용자 결정 |
| Codex 응답 주제 이탈/무의미 | Claude 1회 재요청, 그래도 안 되면 폴백 |
| 사용자 도중 중단 | 현재까지 합의분만 반영 또는 폐기(사용자 선택) |
````

- [ ] **Step 2: 작성 검증**

Run: `ls docs/debate_protocol.md && grep -cE "라운드 흐름|수렴 판정|단계별 Codex 역할|Codex 호출 방법|로그 형식|에러 처리" docs/debate_protocol.md`
Expected: 파일 존재 + 매치 카운트 `6`

- [ ] **Step 3: 커밋**

```bash
git add docs/debate_protocol.md
git commit -m "feat: add debate_protocol.md (Claude-Codex co-author debate spec)"
```

---

### Task 2: 토론 로그 디렉토리 + 템플릿

**Files:**
- Create: `review/debates/.gitkeep`
- Create: `review/debates/_TEMPLATE.debate.md`

**Interfaces (Consumes):** Task 1의 로그 파일 규칙·역할 키워드.

- [ ] **Step 1: `review/debates/.gitkeep` 생성 (빈 파일)**

- [ ] **Step 2: `review/debates/_TEMPLATE.debate.md` 작성 (아래 전체 내용)**

````markdown
# Debate Log

주제: <TOPIC>
단계: <Phase 2/3/4/8 또는 수동>
Codex 역할: <전략/통계/논리 담당 공동 저자 | 공동 저자 | 균형 비평자>
날짜: <YYYY-MM-DD>
결과: <합의 | 부분 합의 | 미합의>

## Claude 초기 입장
<...>

## Codex 초기 입장
<...>

## 라운드별 교환 (요약)
- R1: <...>
- R2: <...>
- R3: <...>

## 최종 합의
<합의 내용>
<미합의 시: 차이점 표 + Claude 추천>

## 반영처
<합의가 반영된 plan/draft/response 파일 경로>
````

- [ ] **Step 3: 검증**

Run: `ls review/debates/.gitkeep review/debates/_TEMPLATE.debate.md && grep -cE "주제:|Codex 역할:|최종 합의|반영처" review/debates/_TEMPLATE.debate.md`
Expected: 두 파일 존재 + 매치 카운트 `4`

- [ ] **Step 4: 커밋**

```bash
git add review/debates/.gitkeep review/debates/_TEMPLATE.debate.md
git commit -m "feat: add review/debates log directory and template"
```

---

### Task 3: `/paper-debate` slash command

**Files:**
- Create: `.claude/commands/paper-debate.md`

**Interfaces (Consumes):** Task 1 `docs/debate_protocol.md`(프로토콜 본문).

기존 command(`.claude/commands/import-doi.md`, `search-evidence.md`)의 frontmatter 형식을 따른다. command는 로직을 중복하지 않고 프로토콜을 가리킨다.

- [ ] **Step 1: `.claude/commands/paper-debate.md` 작성 (아래 전체 내용)**

````markdown
---
description: Claude와 Codex가 co-author로 주제를 토론·합의 (작성 전)
argument-hint: <주제> [단계: planning|stats|logic|revision]
---

`docs/debate_protocol.md`를 기준으로 다음 주제에 대해 Claude–Codex co-author 토론을 수행한다.

주제: $ARGUMENTS

절차:
1. 인자에서 단계를 추론(없으면 균형 비평자). `docs/debate_protocol.md` §3 표에서 역할·초점 결정.
2. R0: 주제에 대한 내 접근·골격(입장)+근거를 작성.
3. 프로토콜 §1·§4에 따라 라운드 진행: 각 라운드에서 `codex:codex-rescue`를 read-only로 호출(§4 프롬프트 템플릿), 1라운드 `--fresh`/이후 `--resume`. 매 라운드 끝에 §2로 수렴 판정.
4. 합의(또는 상한 도달) 시 §5 형식으로 `review/debates/`에 로그를 남기고, 합의를 바탕으로 산출물을 작성/수정.
5. Codex 실패·미합의 시 §6 폴백을 따른다(워크플로 막지 않음).
````

- [ ] **Step 2: 검증**

Run: `ls .claude/commands/paper-debate.md && grep -cE "description:|argument-hint:|debate_protocol.md|codex:codex-rescue" .claude/commands/paper-debate.md`
Expected: 파일 존재 + 매치 카운트 `4`

- [ ] **Step 3: 커밋**

```bash
git add .claude/commands/paper-debate.md
git commit -m "feat: add /paper-debate slash command"
```

---

### Task 4: `CLAUDE.md` 통합

**Files:**
- Modify: `CLAUDE.md` (Quick Commands 표, Phase 2/3/4/8 워크플로, File Roles 표, 구조 트리)

**Interfaces (Consumes):** Task 1·3 (프로토콜·command).

- [ ] **Step 1: Quick Commands에 `/paper-debate` 행 추가**

`### Draft Plan` 또는 새 `### Collaboration` 소제목 표에 추가:
```
| `/paper-debate <주제>` | Claude–Codex co-author 토론 (작성 전, docs/debate_protocol.md) |
```

- [ ] **Step 2: Phase 워크플로에 자동 제안 한 줄씩 삽입**

`## Recommended Workflow`의 해당 Phase 블록에 추가(작성 직전 위치):
- Phase 2: `├── (선택) /paper-debate — 분석 접근을 통계 담당 공동 저자와 토론 후 analysis_plan 작성`
- Phase 3: `├── (선택) /paper-debate — key message·구조를 전략 담당 공동 저자와 토론 후 draft_plan 작성`
- Phase 4: `├── (선택) /paper-debate — 핵심 섹션 논증 골격을 논리 담당 공동 저자와 토론 후 작성`
- Phase 8: `├── (선택) /paper-debate — 대응 전략을 공동 저자와 토론 후 response letter 작성`

- [ ] **Step 3: File Roles 표 + 구조 트리에 신규 파일 등록**

File Roles 표에 추가:
```
| `docs/debate_protocol.md` | Claude–Codex co-author 토론 절차 (라운드·역할·로그·폴백) | Phase 2·3·4·8 (토론 시 참조) |
```
구조 트리 `docs/`에 `debate_protocol.md`, `review/`에 `debates/` 추가.

- [ ] **Step 4: 검증 (참조 무결성)**

Run: `grep -q "paper-debate" CLAUDE.md && grep -q "debate_protocol.md" CLAUDE.md && for f in $(grep -oE 'docs/[a-z_]+\.md' CLAUDE.md | sort -u); do test -f "$f" || echo "MISSING $f"; done; echo done`
Expected: `done` 출력, `MISSING` 없음

- [ ] **Step 5: 커밋**

```bash
git add CLAUDE.md
git commit -m "docs: integrate /paper-debate into CLAUDE.md (commands, phases, roles)"
```

---

### Task 5: Phase 가이드 토론 훅

**Files:**
- Modify: `docs/statistical_analysis_guide.md` (분석 설계 시작부)
- Modify: `docs/draft_plan_template.md` (작성 안내 시작부)
- Modify: `docs/revision_guide.md` (응답 작성 시작부)

각 파일에 토론 권장 1줄을 넣되, 로직은 반복하지 않고 프로토콜을 가리킨다.

- [ ] **Step 1: 세 파일에 훅 삽입 (각 파일 도입부)**

`statistical_analysis_guide.md`:
```
> 분석 접근을 확정하기 전에 `/paper-debate <분석 주제> stats`로 통계 담당 공동 저자(Codex)와 토론할 수 있다 (작성 전, 선택). 절차: `docs/debate_protocol.md`.
```
`draft_plan_template.md`:
```
> draft plan을 확정하기 전에 `/paper-debate <논문 방향> planning`으로 전략 담당 공동 저자(Codex)와 토론할 수 있다 (선택). 절차: `docs/debate_protocol.md`.
```
`revision_guide.md`:
```
> 대응 전략을 정하기 전에 `/paper-debate <코멘트 주제> revision`으로 공동 저자(Codex)와 함께 reviewer 대응을 설계할 수 있다 (선택). 절차: `docs/debate_protocol.md`.
```

- [ ] **Step 2: 검증**

Run: `grep -lc "paper-debate" docs/statistical_analysis_guide.md docs/draft_plan_template.md docs/revision_guide.md`
Expected: 세 파일 각각 매치(카운트 ≥1)

- [ ] **Step 3: 커밋**

```bash
git add docs/statistical_analysis_guide.md docs/draft_plan_template.md docs/revision_guide.md
git commit -m "docs: add /paper-debate hooks to stats/draft-plan/revision guides"
```

---

## Self-Review

**1. Spec coverage:**
- spec §3 Architecture(신규 4파일 + 수정) → Task 1·2·3(신규), Task 4·5(수정). ✓
- spec §4 Protocol Flow(라운드·수렴·역할) → Task 1 §1–3. ✓
- spec §5 Activation(수동 command + Phase 자동제안) → Task 3·4. ✓
- spec §6 Logging+Error → Task 1 §5–6, Task 2 템플릿. ✓
- spec §7 Sub-project B → 본 plan 범위 외(별도 spec/plan 예정). 의도된 제외. ✓
- spec §9 Open Questions → Task 1에서 확정: 프롬프트 템플릿(§4), 자동제안 배치(Task 4 Step 2), slug 규칙(Task 1 Interfaces). ✓

**2. Placeholder scan:** 모든 파일 내용·검증 명령·커밋 메시지가 실제 값. "TBD/TODO/적절히" 없음. ✓

**3. Type/이름 일관성:** 역할 키워드(전략/통계/논리 담당 공동 저자, 공동 저자, 균형 비평자), 로그 경로 `review/debates/YYYYMMDD_<slug>.debate.md`, command 이름 `/paper-debate`가 Task 1·2·3·4·5에서 일관. ✓

---

## 참고: 후속 Sub-Project B

`docs/superpowers/specs/2026-06-19-paper-debate-design.md` §7 참조 — adversarial review (codex `/adversarial-review` 응용 + OpenRouter API, 실행 시 백엔드 멀티 선택). 본 plan 완료 후 별도 spec → plan으로 진행.
