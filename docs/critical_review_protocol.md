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

프롬프트 본문은 `scripts/critical_prompts/<role>.txt`에 **단일 정본**으로 둔다 (`manuscript.txt`, `response.txt`). OpenRouter 스크립트·Claude 서브·Codex 모두 이 파일을 출처로 쓴다. 프롬프트를 바꾸려면 이 파일만 수정한다.

- `manuscript.txt` — 원고를 적대적으로 공격 (overclaiming·방법론·논리 비약·일반화·재현성).
- `response.txt` — reviewer rebuttal 검토 (만족 여부·재반박 지점).

(스크립트: `--role manuscript|response`로 해당 파일 선택. Claude/Codex 호출 시에도 같은 `.txt` 본문을 프롬프트로 사용.)

## 3. 종합 — 합의도 × 심각도

통합 리포트는 각 허점을 **심각도(Critical/Important/Minor)** 와 **합의도(몇 명의 리뷰어가 지적했는지)** 로 정렬한다. 여러 리뷰어가 동의한 허점을 위로. 단독 지적은 "다양성 참고"로 표기.

## 4. 에러 / 폴백

| 상황 | 처리 |
|------|------|
| `OPENROUTER_API_KEY` 없음 | OpenRouter만 skip, 나머지 리뷰어로 진행 + 알림 |
| 특정 모델 실패 | 그 모델만 skip (스크립트가 처리), 나머지 계속 |
| Codex 실패 | Codex skip, 나머지 계속 |
| 리뷰어 0개 | 에러(최소 1개 필요) |
