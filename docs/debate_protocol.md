# Debate Protocol (Claude–Codex Co-Author 토론)

> 논문 작성의 사고 단계에서 Claude와 Codex가 **co-author**로 작성 전에 방향을 토론·합의하는 절차의 단일 기준 문서. `/paper-debate` command와 Phase 가이드는 이 문서를 참조한다.
> 공개 운영 기준은 이 문서가 원본입니다. 내부 설계 노트 경로는 런타임 의존성으로 두지 않습니다.

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
