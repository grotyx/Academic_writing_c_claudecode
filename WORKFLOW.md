# Academic Paper Writing Project (v1.9.7)

## Shared Engine (v1.9.7)

This file contains the runtime-independent workflow. Read `docs/harness_guide.md` for manifest-based draft/revision/submission checks, plan approval hashes, numerical bindings, review packets and gated builds. Its explicit profile rules supersede legacy command examples below. Legacy phase/model examples remain descriptive, not model requirements. Human approvals must reflect an actual decision; never generate an approval to bypass a gate. The public template is not a safe place for private manuscript work: use a separate private project.

## Research Configuration
**Topic:** [INSERT YOUR SPECIFIC RESEARCH TOPIC]
**Target Journal:** [INSERT TARGET JOURNAL]
**Study Design:** [RCT / Cohort / Case-Control / Case Series / Meta-analysis / etc.]

> ⚠️ Update this section for each new paper project

---

## Project Structure & File Roles

Folder tree (single/multi-paper, revision layout) and the per-file role table: `docs/workflow_reference.md`. Key locations: rules `WORKFLOW.md`; guides `docs/`; references `knowledge/evidence.md` (+ `knowledge/pdf/`, gitignored); style anchors `Style/`; data `data/` + `data/analysis_plan.md`; outputs `results/*.csv`; manuscript `drafts/` + `drafts/draft_plan.md`; gates `review/gates/`; DOCX `output/`. Multi-paper: `paper{N}_{keyword}/` subfolders in data/results/drafts/output/review (Rule 6). Revision: `revision/REV{N}/` (Rule 6).

---

## Critical Rules (MUST FOLLOW)

### 1. Citation Integrity

- **NEVER fabricate or hallucinate references**
- **ALWAYS check `knowledge/evidence.md` first** before searching (avoid duplicate work)
- **medical-kag MCP is discovery/analysis only, not a citation source:** register anything it surfaces in `knowledge/evidence.md` as `[EVID:id]` (verify PMID/DOI) **before** citing. evidence.md stays the canonical ledger; fall back to `scripts/search_pubmed.py` if the MCP is unavailable. (`docs/medical_kag_protocol.md`)
- **Reference PDFs are local only:** store PDFs under `knowledge/pdf/`; do not commit copyrighted PDFs.
- **Style anchors are separate from references:** keep writing-style material under `Style/`, not `knowledge/`.
- **Style anchor mirror rule:** use matching basenames between PDF and md (e.g., `Style/PDF/landmark/weber_2007_sciatica.pdf` ↔ `Style/landmark/weber_2007_sciatica.md`).
- **Terminology enforcement:** use `Style/terminology.md` as the vocabulary registry. Preferred terms are required; forbidden terms must be replaced unless an exception is documented in `drafts/draft_plan.md`.
- **New reference workflow:** (상세: `docs/evidence_guide.md`)
  1. Search → verify paper exists
  2. Save PDF to `knowledge/pdf/author_year_keyword.pdf`
  3. Register in `knowledge/evidence.md` with summary & key points
  4. 핵심 논문은 `knowledge/summaries/`에 상세 요약 추가
  5. Then cite in manuscript

### 2. Redundancy Prevention

**Section Content Rules:**

| Section | Contains | Does NOT Contain |
|---------|----------|------------------|
| Introduction | Background, gap, rationale | Your results interpretation |
| Discussion | Your findings interpretation | Repeated background info |
| Results (text) | Key findings, primary effect and confidence interval | Exhaustive repetition of tables |
| Tables | All numerical data | Narrative interpretation |

**Avoid Triple Duplication**
> 동일 데이터가 Results 본문 + Table + Figure 세 곳에 모두 나타나는 것은 지양

| Recommended | Avoid (지양) |
|-------------|--------------|
| Table only | Text에 상세 숫자 + Table에 같은 숫자 |
| Figure only | Table + Figure에 동일 데이터 |
| Table + brief text reference | Results 본문에 Figure 내용 상세 기술 |

**Results Text Writing:**
- ✅ "Baseline characteristics are shown in Table 1"
- ✅ "Group A showed significantly better outcomes (Table 2, *p*=0.023)"
- ❌ "Mean age was 54.3±12.1 years in Group A and 52.1±11.8 in Group B..."

**Table vs Figure Decision (물어보기):**
> "이 데이터는 Table로 할까요, Figure로 할까요?"
- 정확한 수치 필요 → Table
- 추세/분포 강조 → Figure
- 둘 다 만들지 않음 (중복)

**Standard Table Structure:**

| Table # | Content |
|---------|---------|
| Table 1 | Baseline Characteristics (demographics) |
| Table 2 | Main Results (primary + key secondary) |
| Table 3+ | Additional Analyses (subgroup, regression) |

> **Table 개수 가이드:** 가급적 5개 이하 권장. 꼭 필요하지 않은 세부 분석은 Supplement로 분리. 단, 논문 흐름상 필수적인 경우 5개 초과도 가능.

### 3. Consistency Requirements
These must match across **Abstract ↔ Methods ↔ Results ↔ Tables**:
- Patient/sample numbers
- Statistical values (p-values, CIs, means, SDs)
- Time periods and follow-up duration
- Outcome measure names and definitions

### 4. QC Process (MANDATORY)
- Run **minimum 3 QC rounds** before submission
- Follow `docs/qc_guide.md` for detailed procedures
- Document all checks in `review/qc_log.md`
- **진행 추적(선택):** QC 라운드·게이트 항목을 TodoWrite로 추적해 가시성을 높일 수 있다. 단 이는 **세션용 보조 도구일 뿐 정본(authoritative record)이 아니다** — 영속 기록은 `review/qc_log.md`와 `review/gates/`가 담당한다.

### 5. File Versioning (파일 버전 관리)

> 최종본, revision, 대규모 변경 시 파일명에 버전을 표기해야 함

**기본 규칙:** 저자가 별도 스타일을 지정하지 않으면 **날짜(YYMMDD)** 를 기본으로 사용

**버전 표기 형식:**

| 형식 | 용도 | 예시 |
|------|------|------|
| `_YYMMDD` | 기본 (날짜 기반) | `manuscript_260414.docx` |
| `_v1`, `_v2` | 저자 요청 시 (순차 버전) | `manuscript_v1.docx` |
| `_REV1`, `_REV2` | Revision 제출본 | `manuscript_REV1_260414.docx` |
| `_FINAL` | 최종 제출본 | `manuscript_FINAL_260414.docx` |

**적용 시점:**
- **Phase 7 (Finalize):** 최초 제출본에 날짜 또는 버전 부여
- **Revision:** `_REV1`, `_REV2` 표기 필수 (+ 날짜 병기 권장)
- **대규모 변경:** 기존 파일 덮어쓰지 않고 새 버전으로 저장
- **Minor 수정:** 동일 파일명 유지 가능 (git으로 추적)

**파일명 패턴:**
```
{내용}_{버전}_{날짜}.{확장자}
```
- 예: `manuscript_REV1_260414.docx`, `table_1_v2.docx`, `response_letter_REV1_260414.docx`
- 저자가 원하는 스타일이 있으면 그에 따름 (저자 지시 우선)

### 6. Multi-Paper Organization (멀티 논문 정리)

> 하나의 데이터에서 여러 논문을 작성할 때 반드시 서브폴더로 분리

**규칙:**
- `data/`, `results/`, `drafts/`, `output/`, `review/` 각각에 논문별 서브폴더 생성
- `docs/`, `knowledge/`, `scripts/`는 공유 (서브폴더 불필요)
- 서브폴더명: `paper{N}_{keyword}` 또는 저자가 지정한 이름
- 원본 데이터는 `data/` 루트에, 논문별 필터링 데이터는 서브폴더에 배치

**Revision 시:**
- 각 논문 서브폴더 안에 `revision/REV1/`, `revision/REV2/` 생성
- 수정된 섹션만 revision 폴더에 저장 (변경 없는 파일은 복사하지 않음)
- Response letter도 해당 revision 폴더에 포함
- output도 동일하게 `output/{paper}/revision/REV1/` 구조

### 7. Analysis Plan Mandatory (분석 계획 필수)

> **통계 분석 전에 반드시 analysis_plan.md를 작성하고 확인받아야 한다**

**규칙:**

- **NEVER run statistical analysis without first creating `analysis_plan.md`**
- `Analyze data` 명령 시 반드시 analysis_plan.md를 먼저 생성
- 사용자가 analysis_plan.md를 확인한 후에만 스크립트 생성/실행 진행
- analysis_plan.md가 존재하지 않으면 분석 스크립트 생성을 거부

**논문별 개별 작성:**

- **Single paper:** `data/analysis_plan.md`
- **Multi-paper:** 각 논문 서브폴더에 개별 작성
  - `data/paper1_xxx/analysis_plan.md`
  - `data/paper2_yyy/analysis_plan.md`
- 같은 데이터라도 논문마다 연구 질문·대상·분석이 다르므로 **반드시 별도 작성**
- 공유 데이터(`data/raw_data.csv`)에 대한 공통 analysis_plan은 만들지 않음

**analysis_plan.md 필수 포함 내용:**

1. 연구 질문 및 가설
2. 대상 선정/제외 기준 (해당 논문에 맞게)
3. 변수 정의 (primary/secondary/exploratory endpoints)
4. 통계 검정법 선택 및 근거
5. 유의수준 및 다중비교 보정 계획
6. 문서 말미 승인 체크박스 `- [ ] 사용자 승인 완료` — 체크되어야 훅이 분석 스크립트 생성을 허용(체크박스 부재·미체크 = 미승인). 저자가 직접 `[x]`로 체크하거나, 채팅에서 이 계획을 명시적으로 승인("승인", "approve")하면 에이전트가 `manuwright approve <plan> --kind analysis|draft --approved-by "<저자>" --quote "<저자의 말 그대로>"`로 기록한다(체크 + 누가·언제·무슨 말로 승인했는지 + 해시 영수증). 에이전트가 스스로 판단해 승인하는 것은 금지.

### 8. Draft Plan Mandatory (원고 구성 계획 필수)

> **원고 작성 전에 반드시 draft_plan.md를 작성하고 확인받아야 한다**

**규칙:**

- **NEVER start drafting sections without first creating `draft_plan.md`**
- 분석 결과(results/)를 확인한 후, 원고 작성 전에 전체 구성을 먼저 계획
- **Step 0 (Socratic 브레인스토밍):** 항목을 채우기 전, 사용자에게 **한 번에 하나씩** 질문해 의도를 정제한다 (`docs/draft_plan_template.md` 상단). 이 답변은 `/paper-debate`의 R0 준비자료로 쓰되 토론 자체와는 별개다.
- 사용자가 draft_plan.md를 확인한 후에만 섹션 작성 진행 (승인 기록 방법은 Rule 7 의 6번과 같음: 직접 체크 또는 채팅 승인을 `manuwright approve` 로 기록)
- draft_plan.md가 존재하지 않으면 섹션 작성을 거부

**저장 위치:**

- **Single paper:** `drafts/draft_plan.md`
- **Multi-paper:** 각 논문 서브폴더에 개별 작성
  - `drafts/paper1_xxx/draft_plan.md`
  - `drafts/paper2_yyy/draft_plan.md`

**draft_plan.md 필수 포함 내용:**

1. **Key message** — 이 논문의 핵심 메시지 (1-2문장)
2. **Tone & voice** — 논문의 논조/어조 설정
   - 예: "conservative & evidence-based", "novel technique 강조", "기존 방법과 동등성 주장"
   - 전체 원고에서 일관되게 유지할 톤 명시
3. **Essential references** — 반드시 인용해야 할 핵심 참고문헌 목록
   - evidence.md에서 선별하거나, 추가 검색이 필요한 주제 명시
   - 각 reference의 인용 목적 기재 (배경, 방법론 근거, 비교 대상 등)
4. **Evidence gap** — 추가로 필요한 근거 자료 (아직 evidence.md에 없는 것)
   - 검색 키워드 또는 필요한 논문 유형 명시
5. **Table/Figure plan** — 몇 개, 각각 어떤 내용, Table vs Figure 결정
6. **Introduction outline** — Background → Gap → Purpose 흐름
7. **Discussion outline** — 주요 논점 3-5개, 비교할 선행연구 목록
8. **Limitation points** — 예상 한계점 및 대응 논리
9. **Target word count** — 저널 기준에 맞춘 섹션별 목표 분량 (선택)
10. **Claim→Citation mapping** — 핵심 주장 ~20개와 그 근거 논문 매핑 (쓰기 전에 확인 필수)
    - Introduction background: 5–8 claims (배경 지식의 근거)
    - Methods rationale: 2–3 claims (방법론 선택 근거)
    - Discussion comparisons: 5–8 claims (선행연구와의 비교 및 contextualisation)
    - 형식: `[Claim 요약] → Author Year (evidence.md 번호)`
    - **규칙:** claim을 작성하기 전에 citation을 먼저 확보할 것 — 없으면 Phase 1로 돌아가 검색

### 9. Verification Gates Mandatory (검증 게이트 필수)

> **각 산출 단계 뒤에 검증 게이트를 통과해야 다음으로 진행할 수 있다.**
> 상세: `docs/verification_protocol.md`

**규칙:**

- **NEVER proceed past a gate without a recorded PASS.** `review/gates/`의 해당 산출물 항목에 `status: PASS`가 없으면 다음 섹션/단계 진행을 거부한다.
- 검증은 **Verifier 서브에이전트**로 수행한다 (Draft: Constraint / Citation / Data / Logic 4종. Revision: Logic을 빼고 Revision-claims·Response-alignment를 더해 Constraint / Citation / Data / Revision-claims / Response-alignment). 외부지식 금지, 소스 오브 트루스(draft_plan·analysis_plan·evidence.md·results CSV)와만 대조.
- FAIL 시 **자율 수정 루프**: 지적사항을 고쳐 재검증. 최대 **2회(N=2)**, 이후 사용자에게 에스컬레이션.
- **Verifier 모델:** 사용 가능한 독립 reviewer 또는 인간 검토자. 특정 모델의 우위를 가정하지 않는다.
- **인용 grounding:** 초안에서 모든 인용은 `[EVID:author_year]` 태그로 표기 (Phase 7에서 저널 형식 변환).
- **수치 grounding:** 원고 결과 수치는 `results/*.csv`에 존재하는 값만 사용.
- **Hook 강제 (결정적):** `.claude/settings.json`의 PreToolUse 훅(`Write/Edit/MultiEdit`)이 plan-first를 강제 — 완료·승인된 `draft_plan.md` 없이 섹션 작성, 완료·승인된 `analysis_plan.md` 없이 분석 스크립트 생성을 **차단**한다(Rule 7·8, fail-open). 미완성 템플릿/미체크 승인 plan은 plan으로 인정하지 않는다 — 승인 체크박스(`- [x] 사용자 승인 완료`)가 **없어도** 미승인. 훅은 `scripts/hooks/run.sh` 런처로 실행(`py` 있으면 py, 없으면 `python3` — macOS/Linux에서도 강제 유지). SessionStart 훅이 본 계약(+활성 Style Spec)을 매 세션 주입. PostToolUse 훅(`lint_on_edit.py`)이 draft 편집마다 용어·표기 lint를 표면화하고, UserPromptSubmit 훅(`style_intent.py`)이 "학술적으로 바꿔줘" 류 입력에 style-pass protocol을 자동 주입한다. **학술 문체 모드**(`manuwright mode academic|strict|off`, 기본 academic): SessionStart 훅이 핵심 스타일 카드를, UserPromptSubmit 훅이 "서론 써줘" 류 섹션 작성 요청에 해당 섹션 카드(`docs/academic_style/`, `manuwright style card <section>`)를 주입하고, PostToolUse 훅이 편집마다 AI 말투·축약형·긴 문장 등 학술 문장 검사 결과를 표면화한다. `strict` 는 고위험 문장이 든 원고 쓰기를 PreToolUse 에서 차단한다. SubagentStart 훅이 서브에이전트에도 핵심 카드를 주고, 논문 폴더에서는 매 프롬프트에 한 줄 리마인더가 붙으며, "학술 모드 꺼줘"·"academic mode strict" 로 대화 중 전환한다. 목표치는 고급 저널 공개 원저 33편의 실측값(`docs/academic_style/reference_profile.json`, 숫자만)이다. 결정적 검증은 `/verify`(`scripts/verify_all.py`)로 일괄 실행.

**게이트 배치·병렬·freshness:** Phase별 게이트(3 Claim→Citation 사전검증 · 4 섹션 게이트 · 6 경량 · 8 응답 게이트), 병렬 검출, freshness 해시 규칙은 `docs/verification_protocol.md` §7/§3.1/§6 참조. PASS 시 산출물 sha256를 `provenance:`에 기록하고, 산출물이 바뀌면 stale로 보고 재검증(`check_gate.py --verify-hash`). **결정적 차원(citation/numbers/revision_claims)은 `check_gate.py --cross-check`로 원장의 `PASS`를 정본 checker 즉석 재실행과 대조** — 안 돌리고 적은 가짜 PASS나 stale PASS를 모순으로 차단(소스 미도달 시 loud FAIL).

### 10. STOP Signals (자기기만 차단)

> Verifier가 잡는 것은 산출물의 결함이다. 이 표는 그 **앞단** — 사람·에이전트가 검증을 건너뛰려는 *합리화의 순간*을 차단한다. 아래 생각이 들면 멈추고(STOP) 오른쪽 행동을 한다.

| 머릿속 생각 (STOP) | 현실 / 해야 할 행동 |
|---|---|
| "이 숫자는 대충 맞을 거야" | `results/*.csv`와 대조. CSV에 없으면 쓰지 않는다. (`check_numbers.py`) |
| "이 인용 어디서 본 것 같은데" | `knowledge/evidence.md`에서 `[EVID:id]` 확인. 없으면 인용 금지. (`check_citations.py`) |
| "medical-kag가 찾았으니 바로 인용해도 돼" | 아니다. evidence.md에 `[EVID:id]`로 등록·PMID/DOI 확인 후에만 인용. (`docs/medical_kag_protocol.md`) |
| "한 번만 더 보면 통과겠지" | 게이트 먼저. `status: PASS` 없이는 다음 섹션 진행 금지. |
| "고친 김에 이 문장도 손봤어" | 검증 중 산출물 수정 금지. 판정을 모두 모은 뒤 한 번에, 그리고 전체 재검증. |
| "리뷰어 말이 맞지만 반박하고 싶다" | 근거 없는 반박 금지. 반박은 1-2개로 제한하고 문헌으로 뒷받침. |
| "이 정도면 novel하다고 써도 돼" | draft_plan의 tone·claim 범위 확인. 데이터가 지지하지 않는 주장 금지. |
| "Constraint는 나중에 봐도 돼" | 명세(scope/tone/forbidden) 위반은 1순위. 곧 폐기될 문장을 다듬지 않는다. |
| "PASS 받았으니 이제 안전해" | 산출물을 바꿨다면 그 PASS는 stale. `provenance` 해시로 재검증. |

### 11. Runtime and Role Selection

Claude Code, Codex and Gemini CLI can coordinate the same workflow. Select available models by task capability and user preference, not a fixed brand ranking. Run deterministic checks through `python -m harness`; see `docs/harness_guide.md`.

Use a capable planner for design, a shell-capable analyst for reproducible analysis, an evidence-bound writer, and a separate semantic reviewer. If independent review is unavailable, record BLOCKED for required submission review; self-review is useful but must not be recorded as independent. Slash commands, hooks, MCPs and `codex:codex-rescue` are optional runtime-specific facilities, not portable requirements. Claude hooks only cover their configured tool events; shell writes and other runtimes require explicit checks.

### 12. Documentation & Version Sync + Auto Commit-Push (문서·버전 동기화 + 자동 커밋·푸시)

> **harness(scripts/·hooks/·docs/) 코드·버그·기능 변경 시 항상: (1) 영향받는 문서 갱신 → (2) 버전 bump → (3) 자동 commit+push.** 매번 사용자에게 묻지 않는다.

**규칙:**

- **문서 동기화 (코드 ↔ 문서 동시 변경):** 동작·CLI 플래그·스크립트를 바꾸면 **같은 변경 안에서** 관련 문서를 갱신한다 — `WORKFLOW.md`(명령 예시·규칙), `docs/`(해당 protocol), `review/gates/_TEMPLATE.GATE.md`, `AGENTS.md`, `README.md`/`.ko`/`.ja`/`.zh`(기능·설치 안내) + `CHANGELOG.md`/`.ko`/`.ja`/`.zh`. **문서 없는 코드 변경 금지.**
- **버전 bump (semver):**
  - **프로젝트 버전** = `WORKFLOW.md`·`CLAUDE.md`·`GEMINI.md` 헤더 + `harness/__init__.py` + plugin manifest 4종(`.claude-plugin/`·`.codex-plugin/`·`plugin.json`·`gemini-extension.json`, 테스트가 일치 확인) + README 4종 설치 예시의 태그(`@vX.Y.Z`). **cadence 느리게:** 개별 스크립트/플래그 추가·개선·문서·버그는 **patch**(1.5.3→1.5.4). minor는 **큰 마일스톤**(여러 기능 묶음, phase 단위 신규 역량, 워크플로 구조 변경)에만. 호환성 깨짐 = major. 작은 기능 하나마다 minor 올리지 말 것.
  - 변경된 **개별 doc**은 자체 헤더 semver도 올린다 (예: `verification_protocol.md` 0.2.0→0.3.0).
  - `CHANGELOG.md`·`.ko`·`.ja`·`.zh` 에 `### vX.Y.Z (YYMMDD)` 항목 추가 (오늘 날짜). 릴리스 태그(`manuwright update` 의 채널)는 `main` 의 tests 가 통과하면 `.github/workflows/release.yml` 이 `harness/__init__.py` 버전으로 `vX.Y.Z` 태그와 GitHub Release 를 자동 생성한다(이미 있으면 건너뜀). 수동으로 만들 필요 없음.
- **자동 commit+push:** 변경이 **검증(테스트 green)되면** 사용자 확인 없이 commit + push 한다. 표준 커밋 메시지 형식 사용. protected 파일(`.gitignore`의 PDF/`profile/`/Style 앵커)은 자동 제외됨.
- **STOP — 자동 push 금지, 먼저 확인:** ① 비공개/민감 데이터가 staged될 위험, ② 대규모 파괴적 변경, ③ 사용자 manuscript 본문(`drafts/` WIP)이 함께 휩쓸릴 때, ④ history 재작성·force-push·revert(명시 요청 시에만). 이 경우 멈추고 사용자에게 확인한다.

---

## Natural Academic Writing Style

> **상세 가이드: `docs/writing_guide.md`**
> **학술 문체 모드 (v1.9.0):** 섹션 카드 `docs/academic_style/` (`manuwright style card <section>`), 코퍼스 학습 `manuwright style learn <papers>`, 모드 `manuwright mode academic|strict|off`.
> **개인 라이브러리 기억 (v1.9.4):** "기억해"·"앞으로는 X 대신 Y"·"공동저자 추가해줘" 는 `~/.manuwright/library` 에 추가만 한다 (`manuwright library term|note|sync`, 승인된 수정 규칙은 자동 반영, 논문 세션 시작 때 라이브러리 추가분 자동 수신; `config set library-sync auto|ask|off`).
> 규칙·표·예시는 writing_guide.md에 있음. WORKFLOW.md는 워크플로·Phase 조정만 담당 (중복 방지).

**Phase 5 (Style Polish)에서 적용할 writing_guide.md 섹션:**

| 영역 | writing_guide.md 섹션 | 주요 내용 |
|------|----------------------|-----------|
| 전역 규칙 | General Principles | 시제, Bold 금지, 약어 1회 정의, 임상 결과 주어, 동의어 혼용 금지, 숫자 서식, 문두 숫자 |
| 스타일 표 | Style Reference Tables | Voice & Tense / Transition / Verb Choice / Common Corrections / Statistical Notation / Hedging |
| AI 군살빼기 | AI-Draft De-bloat | -ing 피상분석·AI어휘·신호어 제거; 충돌 패턴(hedging/copula/passive) 적용 제외 |
| 작문 원칙 | Writing Principles (4 Pillars) | Clarity / Conciseness / Objectivity / Consistency |
| 섹션별 규칙 | 01. Title ~ 10. Tables | 각 섹션 구조·구체 규칙·예시 |

**Phase 5 워크플로:**
1. `docs/writing_guide.md` Style Reference Tables 읽기
2. 섹션별로 Transition/Verb/Corrections 적용
3. AI 초안인 경우 AI-Draft De-bloat 적용 (-ing 피상분석·AI어휘·신호어 제거; 충돌 패턴 제외)
4. Writing Principles (4 Pillars) 기준으로 검토
5. Dr. Editor 최종 polish

---

## Recommended Workflow

```
Phase 1: Setup
├── Define topic, journal, study design in WORKFLOW.md
├── Check profile/journals.md — 목표 저널 인용 형식 확인 (et al. 규칙, volume 형식 등)
├── Check Style/own/ — 관련 스타일 앵커 논문 확인 (용어·톤 일관성 참고)
├── Search references: /search-evidence [query] 또는 scripts/search_pubmed.py
├── (선택) medical-kag MCP: search/hybrid_search 발굴 + conflict find로 논쟁 파악 → evidence.md 등록 (docs/medical_kag_protocol.md; evidence.md 정본 유지, 미연결 시 search_pubmed.py로 fallback)
├── Import by DOI: /import-doi [doi]
├── Audit evidence: `manuwright search audit` (PubMed 메타데이터 가중 대조 + 철회·우려 표명·정정 확인) + 항목마다 Claim Strength 기록
├── Save PDFs to knowledge/pdf/
├── Summarize & register in knowledge/evidence.md (docs/evidence_guide.md 참조)
├── 핵심 논문은 knowledge/summaries/에 상세 요약
└── Read docs/writing_guide.md for target sections

Phase 2: Statistical Analysis — Opus 권장 (analysis_plan)
├── Read docs/statistical_analysis_guide.md (분석 설계 원칙·검정 선택·보정)
├── Place raw data (CSV/XLSX) in data/
├── (선택) /paper-debate — 분석 접근을 통계 담당 공동 저자(Codex)와 토론 후 plan 작성
├── Create data/analysis_plan.md (필수, 사용자 승인 후 진행)
│   ├── Claude reads CSV → creates analysis plan → 사용자 확인
│   └── 포함 항목: endpoint hierarchy, 검정법, 다중비교 보정, 결측 처리
├── Generate Python scripts in data/py/
│   ├── 01_descriptive.py (demographics, baseline)
│   ├── 02_comparative.py (group comparisons)
│   └── 03_regression.py (if needed)
├── Run analysis → export results to results/
│   └── table1_demographics.csv, table2_outcomes.csv, etc.
├── Generate drafts/table_*.md from results CSV
└── Generate figures → drafts/figures/

Phase 3: Draft Plan (원고 구성 계획) — Opus 권장
├── Step 0: Socratic 브레인스토밍 — 항목을 채우기 전 사용자에게 한 번에 하나씩 질문해 의도(key message) 정제 (draft_plan_template.md 상단; /paper-debate와 별개, R0 준비자료로 활용)
├── (선택) /paper-debate — key message·구조를 전략 담당 공동 저자(Codex)와 토론 후 plan 작성
├── Copy docs/draft_plan_template.md → drafts/draft_plan.md (또는 논문별 서브폴더)
│   ├── Key message (이 논문의 핵심 메시지 1-2문장)
│   ├── Tone & voice (논조/어조 설정)
│   ├── Essential references (필수 인용 참고문헌 + 인용 목적)
│   ├── Evidence gap (추가 필요 근거 자료)
│   ├── Claim→Citation mapping (핵심 주장 ~20개 + 각 근거 논문 — Style/own/ 참조 가능)
│   ├── Table/Figure plan (어떤 Table/Figure를 몇 개, 어떤 내용으로)
│   ├── Introduction outline (background → gap → purpose 흐름)
│   ├── Discussion outline (주요 논점 3-5개, 비교할 선행연구)
│   ├── Limitation points (예상 한계점)
│   └── Target word count (저널 기준, 선택)
├── 🔒 GATE: Claim→Citation 사전검증 (Citation Verifier) — 근거 없는 claim은 글쓰기 전 차단
├── 사용자 확인 후 Phase 4 진행
└── Multi-paper: drafts/paper{N}_xxx/draft_plan.md

Phase 4: Draft (in this order)
├── Read docs/drafting_protocol.md + docs/section_templates.md before drafting
├── Load the section card before each section: `manuwright style card <section>` (moves, phrasebank, model paragraphs, learned corpus style; auto-injected on "서론 써줘")
├── Apply Style/terminology.md and relevant Style anchors during drafting
├── (선택) /paper-debate — 핵심 섹션 논증 골격을 논리 담당 공동 저자(Codex)와 토론 후 작성
├── 04_methods.md      → establishes framework
│   └── Expert: Dr. Researcher B (methodology)
├── 05_results.md      → narrative (refer to drafts/table_*.md)
│   └── Expert: Dr. Researcher B
├── 03_introduction.md → background & gap
│   └── Expert: Dr. Researcher A (clinical)
├── 06_discussion.md   → interpretation (check vs intro)
│   └── Expert: Dr. Researcher A
├── 07_conclusion.md   → brief takeaway
├── 02_abstract.md     → summary (write LAST)
├── 01_title.md        → finalize (profile/authors.md 참조하여 저자·소속·ORCID·funding 기입)
└── 🔒 GATE (각 섹션마다): Constraint + Citation + Data + Logic Verifier 자율 루프 (최대 2회) → review/gates/ 기록

Phase 5: Style Polish
├── /style-pass — 초안을 bound Style Spec/exemplar에 맞춰 섹션별 변환 + Style Verifier (docs/style_transform_protocol.md; "학술적으로 바꿔줘"에 자동 발동)
├── Academic prose check: `manuwright lint --academic drafts` (또는 `python scripts/academic_style.py check <section>`) 0 high findings; 문체 수정 후 `manuwright style preserve <원문> <수정본>` OK; 좋은 논문 코퍼스는 `manuwright style learn <papers>`; 저자가 고친 뒤 `manuwright style edits --git <rev>` → 저자가 체크한 규칙만 `--apply`
├── Apply writing_guide.md Style Reference Tables
│   ├── Transition Words 업그레이드 (but → nonetheless)
│   ├── Verb Choice (utilized → used, demonstrated → showed; 측정 기반)
│   ├── Voice & Tense by Section 확인
│   ├── Common Corrections 적용
│   ├── Statistical Notation 검증 (*p* italic, en-dash 등)
│   └── Hedging Language 적정성 확인
├── Apply docs/section_templates.md sentence-pattern pass
├── Apply Style/terminology.md terminology pass
├── Run `python scripts/lint_manuscript.py drafts --quiet` and fix high-priority findings
├── Apply writing_guide.md Writing Principles (4 Pillars)
│   └── Clarity / Conciseness / Objectivity / Consistency
└── Expert: Dr. Editor (final polish)

Phase 6: QC (3 rounds CRITICAL, 6 rounds RECOMMENDED)
├── Round 1: Number consistency — Claude 자동 + 사용자 확인 (qc_guide.md)
├── Round 2: Reference verification — Claude + 사용자 (evidence.md 대조)
├── Round 3: Logic & flow check — Dr. Editor (section 간 흐름)
├── Round 4: Terminology/abbreviation/tense + style metrics — Dr. Editor + lint + check_style.py vs Style Spec (권장)
├── (권장) Check crossrefs / Check abbreviations — Table·Figure 참조 정합 + 약어 정의 advisory 점검
├── Round 5: Statistical quality — Dr. Statistician (권장)
├── Round 6: Critical review — 내부(Dr. Editor + Dr. Statistician) + (선택) /critical-review 외부 멀티모델 (overclaiming/bias/일반화, 권장)
├── Round 6.5 (선택): Editorial desk-screen — /editor-review: high-impact 저널 편집장 관점 (임상 타당성·분야 scope fit·추가검증 roadmap·하위저널 추천; advisory, `docs/critical_review_protocol.md` §5)
├── Overclaim check: `manuwright claim-strength drafts` (인용 문장의 동사가 근거의 Claim Strength 보다 센지)
├── Claim verification (선택): /verify-claims — 인용 문장별 SUPPORTED/PARTIAL/UNSUPPORTED 리포트 (docs/citation_assist_protocol.md; GraphRAG 주, evidence.md 보조)
├── Document all rounds in review/qc_log.md
└── Run study-specific checklist (checklist_guide.md — CONSORT/STROBE/PRISMA/CARE)

Phase 7: Finalize
├── Read docs/docx_guide.md (DOCX 변환 규칙 확인)
├── Compile to DOCX (docs/docx_guide.md 규칙대로)
│   ├── output/title_page_YYMMDD.docx (별도)
│   ├── output/manuscript_YYMMDD.docx (본문 병합, 테이블 제외)
│   └── output/table_N_YYMMDD.docx (각 테이블 별도)
├── 파일명에 버전 표기 (기본: _YYMMDD, 저자 지정 시 _v1 등)
├── Co-author review
└── Final read-through

Phase 8: Revision (리뷰어 코멘트 수신 후)
├── Read docs/revision_guide.md
├── 리뷰어 코멘트 저장: review/reviewer_comments_REV1.md
├── Revision 폴더 생성: drafts/revision/REV1/, output/revision/REV1/
├── 수정된 섹션만 _REV1 접미사로 저장
├── (선택) /paper-debate — 대응 전략을 공동 저자(Codex)와 토론 후 response 작성
├── Response letter 작성 → drafts/revision/REV1/response_letter_REV1.md
├── 🔒 GATE (각 응답마다): ghost-revision 검증 (응답 주장 ↔ 원고 diff 대조) 자율 루프
├── Letter-blind re-review: `manuwright blind-review packet ...` → 기대치 → 편지 없이 판정 → 편지 공개 후 근거 있는 변경만 → `blind-review check` PASS 후 response_alignment 기록 (docs/revision_guide.md)
├── Check response coverage — 모든 리뷰어 코멘트에 응답 존재 확인 (check_response_coverage.py --comments)
├── QC re-run (최소 Round 1-2 재수행)
├── Compile revised DOCX → output/revision/REV1/
│   ├── manuscript_REV1_YYMMDD.docx
│   ├── table_N_REV1_YYMMDD.docx (변경된 테이블만)
│   └── response_letter_REV1_YYMMDD.docx
└── 2차 revision 시: REV2/ 폴더에 동일 구조 반복
```

### Phase Completion Criteria

| Phase | Move to Next When |
|-------|-------------------|
| 1 → 2 | Evidence supports planned claims, topic defined, study-specific inputs ready |
| 2 → 3 | analysis_plan.md created & approved, all analyses complete, tables generated |
| 3 → 4 | draft_plan.md created & approved — 10개 필수 항목 완결 (key message, tone/voice, essential refs, evidence gap, claim→citation mapping, table/figure plan, intro/discussion outline, limitation points, target word count) — Rule 8 참조 |
| 4 → 5 | All sections drafted, numbers match tables |
| 5 → 6 | Writing style rules applied, Dr. Editor reviewed |
| 6 → 7 | Minimum 3 QC rounds passed (6 recommended), checklist complete |
| 7 → Submit | Co-author approved, journal requirements met, versioned files in output/ |
| Submit → 8 | Reviewer comments received |
| 8 → Resubmit | Revised manuscript + response letter complete, QC re-run passed |

---

## Quick Commands

Full command catalog (setup, KAG, analysis, drafting, style, QC/verification, revision, finalize): `docs/workflow_reference.md`. Portable entry point: `python -m harness doctor|status|verify|packet|build` (`docs/harness_guide.md`).

---

## Notes

### Key Reminders
- Detailed guides in `docs/` folder - read as needed to save context
- Always verify AI-generated citations against actual sources
- Minimum 3 QC rounds mandatory before submission
- Human expert review mandatory before submission

### PubMed Search Tool

`python scripts/search_pubmed.py search|fetch|doi|related ...` — options in `docs/workflow_reference.md` (Tools).

### Expert Simulation
When drafting, invoke experts from `docs/expert_roles.md`:
- **Dr. Researcher A**: Clinical perspective (Introduction, Discussion)
- **Dr. Researcher B**: Methodology (Methods, Results, Tables)
- **Dr. Statistician**: Statistical validation
- **Dr. Editor**: Final polish, consistency check

### Statistical Analysis (Phase 2)

> 워크플로·검정 선택은 Recommended Workflow Phase 2 + `docs/statistical_analysis_guide.md`(§1 워크플로, §5 검정 선택) 참조. 핵심: 분석 전 `analysis_plan.md` 필수(Rule 7, hook 강제) → `data/py/` 스크립트 → `results/` CSV → table/figure (Table↔Figure 중복 확인).
