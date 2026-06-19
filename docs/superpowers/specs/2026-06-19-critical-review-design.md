# Critical-Review: 외부 멀티모델 적대적 검토 (설계)

**Date:** 2026-06-19
**Status:** Designed — pending implementation plan
**Topic:** 완성된 원고/response를 여러 모델(Claude 서브에이전트·Codex·OpenRouter)이 적대적 동료 심사자로 공격해 허점을 발굴하고, 합의도 기반 통합 리포트로 종합한다.

> 이 문서는 `docs/superpowers/specs/2026-06-19-paper-debate-design.md` §7에서 예고된 **Sub-project B**의 설계다. A(paper-debate)는 작성 *전* 협력 토론, B는 작성 *후* 적대적 검토 — 반대 성격의 독립 기능.

---

## 1. Problem / Goal

단일 모델 검토는 그 모델의 blind spot에 갇힌다. 제출 전 원고나 reviewer response의 약점(overclaiming, 방법론 허점, 논리 비약, 재현성)은 **서로 다른 모델이 각자 공격**할 때 더 많이 드러난다. 이 기능은 기존 **QC Round 6 "Critical Review"의 외부 멀티모델 강화판**이다.

**Goal**
- 대상(원고/response)을 여러 리뷰어가 적대적으로 공격해 허점을 발굴한다.
- 여러 결과를 **합의도 = 신뢰도**로 종합한다(여러 모델이 동의한 허점 = 거의 확실한 약점).
- 외부 의존(OpenRouter/Codex)이 없어도 막히지 않는다(Claude 서브 단독 폴백).

**Non-Goals**
- 발견된 허점을 자동 수정하지 않음(review-only; 수정은 사용자/후속 작업).
- paper-debate(작성 전 협력 토론)와 통합하지 않음 — 별개 기능.
- 모델 ID 하드코딩 안 함(설정 외부화).

## 2. Decisions (확정)

| # | 결정 | 값 |
|---|------|-----|
| D1 | 정체 | QC Round 6 Critical Review의 **외부 멀티모델 강화판** |
| D2 | 대상 | 기본 **전체 원고** / 지정 시 부분 / revision: **response letter + 원고** |
| D3 | 리뷰어 풀 | **Claude 서브에이전트** + **Codex**(codex-rescue) + **OpenRouter 모델들**. 실행 시 멀티 선택 |
| D4 | OpenRouter | `scripts/critical_review.py`, env `OPENROUTER_API_KEY`, 기본 모델 **MiniMax M3 + GLM 5.2**, 모델 목록 설정 외부화 |
| D5 | 종합 | 메인 Claude. **합의도 = 신뢰도**. 심각도(Critical/Important/Minor) × 합의도로 정렬 |
| D6 | 출력 | 통합 리포트 + 모델별 원본, `review/critical/`에 저장 |
| D7 | 발동 | 수동 `/critical-review` + 자동 제안(QC Round 6, revision response 완성 후) |
| D8 | 폴백 | OpenRouter/Codex 실패해도 Claude 서브에이전트 단독 가능 → 막히지 않음 |

## 3. Architecture & Components

**오케스트레이션:** 메인 Claude가 대상 선택 → 리뷰어 멀티 선택 → 병렬 공격 수집 → 종합. 메인 Claude는 **리뷰어가 아니다**(자기 글 비판은 fresh 서브에이전트가). 리뷰어 메커니즘: Claude=Agent(새 서브에이전트), Codex=codex-rescue 에이전트, OpenRouter=Python 스크립트.

**신규 파일**

| 파일 | 역할 |
|------|------|
| `scripts/critical_review.py` | OpenRouter **멀티 모델 호출만** (`requests`, env key, 대상+적대 프롬프트 → 모델별 응답 JSON, 실패 모델 skip) |
| `tests/test_critical_review.py` | 단위 테스트 (HTTP mock, key 없으면 skip) |
| `docs/critical_review_protocol.md` | **단일 기준** — 대상·리뷰어 선택·적대 프롬프트·종합·로그·에러 |
| `.claude/commands/critical-review.md` | `/critical-review <대상>` 진입점 |
| `review/critical/_TEMPLATE.critical.md` | 통합 리포트 템플릿 |
| `review/critical/.gitkeep` | 디렉토리 유지 |

**수정 파일**

| 파일 | 변경 |
|------|------|
| `requirements.txt` | `requests` 추가 |
| `CLAUDE.md` | Collaboration 명령에 `/critical-review`, QC Round 6 2층 구조, File Roles, 트리 |
| `docs/qc_guide.md` | Round 6에 외부 멀티모델 옵션 연결 |

## 4. Flow

```
1. 대상 결정    기본 전체 원고 / 지정 부분 / revision: response + 원고
2. 리뷰어 선택  멀티 선택: Claude 서브 / Codex / OpenRouter 모델 N개
3. 병렬 공격    각 리뷰어가 적대적 심사자로 대상 공격 → 허점 리스트
                ├ Claude     → Agent(새 서브에이전트) + 적대 프롬프트
                ├ Codex      → codex-rescue + 적대 프롬프트
                └ OpenRouter → scripts/critical_review.py (모델별 API)
4. 종합(메인)   중복 통합(합의도) + 심각도 분류 → 통합 리포트
5. 저장         review/critical/YYYYMMDD_<slug>.md (통합 리포트 + 모델별 원본)
```

**적대 프롬프트** (대상별):
- 원고: "동료 심사자로서 overclaiming·방법론 허점·논리 비약·일반화 오류·재현성 문제를 최대한 공격하라."
- response: "심사자로서 이 답변이 만족스러운가, 어디를 재반박하겠는가."

**종합 — 합의도 = 신뢰도:** 여러 리뷰어가 같은 허점 지적 → 신뢰도 높음. 단독 지적 → 다양성 참고. 리포트는 **심각도 × 합의도**로 정렬.

## 5. OpenRouter Script Interface

```
python scripts/critical_review.py
  --target <file>            대상 텍스트 파일
  --models <id1,id2,...>      OpenRouter 모델 ID 목록
  --role manuscript|response  적대 프롬프트 종류
  [--out review/critical/<run>/]  모델별 원본 저장 위치
→ stdout: {model_id: 허점_응답} JSON
env: OPENROUTER_API_KEY  (없으면 명확한 에러로 종료, exit 비0)
실패한 모델은 skip + 경고(stderr), 나머지 계속.
```

- OpenRouter chat completions API를 `requests`로 호출.
- 기본 모델: **MiniMax M3, GLM 5.2** (정확한 OpenRouter slug는 구현 시 카탈로그 확인). 목록은 설정(`scripts/critical_models.txt` 또는 프로토콜 문서)으로 외부화 — 하드코딩 금지.
- 적대 프롬프트 본문은 `docs/critical_review_protocol.md` 기준.

## 6. Activation & Integration

- **수동:** `/critical-review <대상>` (대상 생략 시 전체 원고).
- **자동 제안:** QC **Round 6**(제출 전)과 revision response 완성 후(Phase 8)에 "외부 멀티모델 critical review 할까요?" 제안.
- **Round 6 2층화:** 내부(Claude Dr. Editor/Statistician) + 외부(`/critical-review` 멀티모델). `qc_guide.md`·`CLAUDE.md`에 연결.

## 7. Error Handling

| 상황 | 처리 |
|------|------|
| `OPENROUTER_API_KEY` 없음 | OpenRouter 백엔드만 skip, 가능한 리뷰어로 진행 + 알림 |
| 특정 모델 호출 실패 | 그 모델만 skip, 나머지 계속 |
| Codex 호출 실패 | Codex skip, 나머지 계속 |
| 리뷰어 0개 선택 | 에러(최소 1개 필요) |

**안전장치:** Claude 서브에이전트는 외부 의존 없이 항상 가능 → 외부 백엔드가 다 죽어도 최소 Claude 단독 리뷰는 된다.

## 8. Summary of Files

**신규:** `scripts/critical_review.py`, `tests/test_critical_review.py`, `docs/critical_review_protocol.md`, `.claude/commands/critical-review.md`, `review/critical/_TEMPLATE.critical.md`, `review/critical/.gitkeep`
**수정:** `requirements.txt`, `CLAUDE.md`, `docs/qc_guide.md`

## 9. Open Questions (구현 plan에서 확정)

- MiniMax M3 / GLM 5.2의 정확한 OpenRouter 모델 slug.
- 모델 목록 외부화 형식(`critical_models.txt` vs 프로토콜 문서 내 목록).
- 통합 리포트 정렬·표기의 정확한 마크다운 형식.
- OpenRouter 호출 동시성(thread pool vs 순차).
