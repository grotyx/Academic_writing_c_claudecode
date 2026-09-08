# Journal Reference Formats (Template)

> Copy this file to `profile/journals.md` and adapt it to the journals you submit to.
> `profile/journals.md` is gitignored; only this `example_` template is tracked.
>
> Referenced when building a bibliography (WORKFLOW.md Phase 7,
> `Format references for [journal]`) to get citation style, author cutoff and
> page-range formatting right per journal.
>
> ✓ = format confirmed against the official Instructions for Authors or a published
> article. Sections carry a "Verified examples" block where a real published
> reference was used to check the rule.
>
> The 13 journals below are spine/orthopaedics and digital-health titles, kept as
> **worked examples**: replace or extend them with your own target journals. The
> value is the per-journal checklist shape — in-text citation style, author cutoff,
> page range, ORCID policy, submission requirements — not this particular list.
>
> Keep a dated review note here when you re-verify a journal's rules against its
> current IFA; journal requirements change.

---

## 공통 원칙

- **Author name format:** LastnameFM (성+이니셜, 공백 없음). 예: Park SM, Kim HJ — ⚠️ 예외: npj Digital Medicine은 `Lastname, F. M.` (쉼표+마침표 이니셜, Nature style)
- **한국 저자 hyphen:** 일부 저널은 S-M. Park 형식 (BJJ 등) — 저널별 확인
- **제목:** Sentence case (첫 글자만 대문자, 고유명사 제외)
- **Journal abbreviation:** NLM Catalog 공식 약어 사용
- **Page range:** 저널별 상이 — en-dash+전체 숫자(TSJ own-paper·BJJ·Neurospine·ESJ) / hyphen+뒷자리 축약(JBJS·Spine·JAMIA·TSJ 가이드 예시) / hyphen+전체 숫자(CORR·npj 예시). 각 섹션 Verified example 우선.

---

## The Spine Journal (Spine J) ✓

**Publisher:** Elsevier (NASS) | **Style:** Numbered brackets [N]
**In-text:** [1], [2,3], [4–6]
**Author cutoff:** ✅ **원문 직접 확인 완료(2026-07-24, 사용자 제공 PDF "Information for Authors: The Spine Journal", thespinejournalonline.com/content/authorinfo, 34p, 2026-07-23 접속본)** — *"for more than 6 authors the first 6 should be listed followed by 'et al.'"* — 기존 "6명" 기재 정확함, 최종 확정.
**DOI:** ⚠️ **소스 간 불일치:** 가이드의 범용 Elsevier 예시(reference 1)는 DOI 포함(`https://doi.org/...`)이나, **own paper 실제 게재분(아래 Verified examples)은 DOI 미포함** — TSJ는 후자가 실제 하우스 스타일로 보임(범용 예시는 Elsevier 전 저널 공용 boilerplate).

**Format:**
```
[N] LastnameFM, LastnameFM, LastnameFM, LastnameFM, LastnameFM, LastnameFM, et al. Title sentence case. Spine J. Year;Vol:pages.
    # ≤6명 전원 나열; 7명+면 첫 6명 + et al.
```

**Verified examples (실제 게재 논문):**
```
[1] Park SM, Lee HJ, Park HJ, Choi JY, Kwon O, Lee S, et al. Biportal endoscopic versus
    microscopic discectomy for lumbar herniated disc: a randomized controlled trial.
    Spine J. 2023;23:18–26.

[2] Park SM, Park J, Jang HS, Heo YW, Han H, Kim HJ, et al. Biportal endoscopic versus
    microscopic lumbar decompressive laminectomy in patients with spinal stenosis:
    a randomized controlled trial. Spine J. 2020;20:156–165.
```

**가이드 자체 예시 (Reference style, PDF p.28, 범용 Elsevier boilerplate — 참고용):**
```
[1] Van der Geer J, Hanraads JAJ, Lupton RA. The art of writing a scientific article.
    J Sci Commun 2020;163:51-9. https://doi.org/10.1016/j.sc.2020.00372.
```

**Notes:**
- Volume:pages 형식 (issue number 미표기)
- 저자 6명 초과 시 "6저자 et al." — 6번째까지 모두 나열 후 et al. — ✅ 원문 verbatim 확정(위 참조)
- ⚠️ **Page range 표기 불일치:** 가이드 원문은 *"note the shortened form for last page number, e.g., 51-9"*(hyphen+뒷자리 축약, JBJS류) 명시하나, **실제 own paper 게재분은 en-dash+전체 숫자**("18–26", "156–165"). ScienceDirect 프로덕션 단계에서 저널별 실제 하우스스타일로 변환되는 것으로 추정 — **원고 제출 시엔 own-paper 검증 예시(en-dash+전체 숫자)를 따르고**, 가이드의 "51-9"는 Elsevier 범용 지침(전 저널 공용, 실제 적용 여부 저널마다 다름)으로 간주.
- Reference 순서: 본문 첫 언급 순서로 번호(알파벳순 아님) — ✅ 확정("Number the references in the reference list in the order in which they appear in the text").
- In-text bracket 인용 시 저자명 언급 가능하나 반드시 번호 병기: *"as demonstrated [3,6]. Barnaby and Jones [8] obtained a different result…"*

**Submission Checklist (✅ 2026-07-24 사용자 제공 PDF로 원문 전체 34페이지 직접 확인 — thespinejournalonline.com/content/authorinfo, 2026-07-23 접속본. 이전 2023 archived snapshot 기반 기재를 아래 내용으로 전면 갱신):**

1. **Title page** — 별도 파일(본문은 완전 anonymize — "Double anonymized peer review": 저자명·소속·acknowledgements 본문에 넣지 않음). 필수 항목: Article title, **Author names**(given name + family name만, **학위 표기 요구 없음**, 제출시스템 순서와 일치), **Affiliations**(저자명 뒤에 **소문자 위첨자**로 표기, 대응 주소 앞에도 동일 문자 — 이전 "번호" 기재는 오류, **문자(letter)가 맞음**; 소속별 전체 postal address+country 필수, email은 "if available"), **Corresponding author**(전 과정 연락 담당자 명시, 연락처 최신 유지), **Present/permanent address**(이동한 저자용, 위첨자 아라비아 숫자 footnote — affiliation 문자와는 별개 체계). Title page에 추가: **Acknowledgements**(언어/작성/교정 도움만, 본문·footnote·다른 위치 금지), **Declaration of competing interests**(별도 파일 미제출 시), **Corresponding author address(전체 주소 필수)+email**.
2. Structured Abstract — ✅ **word limit 확정: ≤250 words**(이전 "명시적 확인 안 됨" 정정). Clinical Studies는 **8개 구조화 subheading 필수**: background context/purpose/**design**/patient sample/outcome measures/methods/results/conclusions(이전 "Study Design·Setting"으로 뭉쳐 기재했던 것 정정 — "design"이 별도 항목). Basic science는 Discussion에 clinical significance 별도 문단 필수(abstract heading 아님, 정정). Narrative Review는 unstructured.
3. Highlights(Key Points) — 여전히 **encouraged(선택)**, 3–5 bullet, **bullet당 공백포함 최대 85자** — 상동 확정.
4. 본문 word limit(article type 갱신) — Clinical/Basic Science study 명시적 words 범위는 원문에 재확인 안 됨(⚠️); **Research Letters ≤700 words**(무abstract, ≤10 refs, fig/table 1–2개, **≤6명 저자** — 저자상한 명시), Narrative Review **≥50 refs, 20–30 double-spaced pp, 3–5 explanatory tables**, Letters to Editor **≤500 words**(회신도 500 단어 제한), **✅ 신규 확인 — Commentaries**(요청형, **~1500 words**[tables/figs/refs 제외], **≤30 refs**), **✅ 신규 확인 — Perspectives**(요청·비요청 의견 기고, TSJ Editorial Board 한정인 Editorial과 달리 **누구나 기고 가능**, 별도 word cap 명시 안 됨). Case report/technical report/small case series는 "rare exceptions" 외 **미접수** 확정.
5. Line & page numbering — ✅ **원문 verbatim 확정**: "Line numbers (each page starts with 1)" / "Page numbers (lower right corner)" / "1.5 or double line spacing" — 이전 기재 정확함.
6. References — "This journal does not set strict requirements on reference formatting at submission"(제출 시 엄격한 포맷 불요) 확정. 인용 순서·author cutoff는 위 Notes 참조. Reference list 언급 항목(저자명/저널명·챕터명/연도/volume/article number 또는 pagination)만 있으면 accept 후 저널 스타일로 자동 변환.
7. Tables — **편집 가능 텍스트로 제출(이미지 금지)**. 배치는 **본문 관련 위치 옆 또는 원고 끝 별도 페이지 중 선택 가능**(이전 "반드시 별도 파일, 한 번에 하나씩" 기재는 과도 — 실제로는 유연). 캡션 필수, 표 안 vertical rule/shading 지양, 결과 본문과 중복 지양.
8. Figure legends — Caption 필수(그림 자체엔 표시 안 함, 상세 설명 별도 첨부), 그림 앞뒤 배치 관련 명시적 "Figure Captions 섹션" 문구는 이번 원문에선 별도 확인 안 됨(⚠️, 이전 기재와 약간 다름 — 실제로는 "artwork instructions" 링크 경유).
9. Figures — ✅ **원문 verbatim 수치 확정**: 컬러/그레이스케일 사진(halftone) **min 300dpi**(단컬럼 ≥1063px, 전폭 ≥2244px); bitmap line drawing **min 1000dpi**(단컬럼 ≥3543px, 전폭 ≥7480px); combination **min 500dpi**(단컬럼 ≥1772px, 전폭 ≥3740px). Vector는 EPS/PDF(폰트 내장 또는 텍스트를 "graphics"로 저장). 컬러 온라인 게재 무료. Video: 파일당 ≤150MB, 총 ≤1GB.
10. **제출 양식** — ✅ **원문 확정, 정정:** Submission checklist엔 *"Each author is required to submit **the ICMJE form**, and every page of every form must be uploaded by the corresponding author"* + *"Include a completed **FDA Device/Drug Approval Status Form**, if applicable"* — **범용 ICMJE Disclosure Form이 현재 공식 요구 양식**(이전 "TSJ Author Disclosure"·"TSJ Affirmation of Authorship Form"이라는 NASS 전용 양식명은 이 최신 가이드 본문엔 등장하지 않음 — legacyfileshare.elsevier.com에서 확인된 구버전 PDF들이 여전히 실제 업로드 링크일 가능성은 있으나, **현재 공식 문서상 명칭은 "the ICMJE form"으로 단순화됨**, 제출 시 실제 링크 재확인 권장). **Copyright/Publishing agreement**는 accept 후 처리(상동).

**Author-related requirements (✅ 2026-07-24, thespinejournalonline.com/content/authorinfo 원문 PDF 34페이지 전체 직접 확인 — 이전 403 차단으로 인한 모든 "not found" 항목이 이번에 해소됨):**

1. **저자명/학위 표기 — ✅ 확정:** *"Author names. Provide the given name(s) and family name(s) of each author. The order of authors should match the order in the submission system."* — **학위(MD/PhD) 표기 요구 자체가 없음**(타 저널과 달리 title page에 학위 필드 없음, 확정).
2. **Affiliation 형식·번호 매김 — ✅ 확정, 정정(번호 아니라 문자):** *"Indicate affiliations using a lower-case superscript letter immediately after the author's name and in front of the corresponding address."* 전체 postal address+국가명 필수, email은 있으면 포함("if available" — 필수 아님).
3. **교신저자 필수 필드 — ✅ 확정(전화 포함, 이전 미확인 해소):** Submission checklist verbatim: *"One author has been designated as the corresponding author and their full contact details (**email address, full postal address, and phone numbers**) have been provided."* 추가: **교신저자 소속만이 publishing agreement/OA 할인 자격 결정**("Only the corresponding author's affiliation will be used to determine eligibility for a publishing agreement... other co-authors are not relevant for eligibility").
4. **저자 수 제한 — ✅ 확정(Research Letters만):** 일반 Original Article/Review는 상한 없음(불변); Research Letters **최대 6명**.
5. **ORCID — ✅ 확정 부재(34페이지 전체 스캔, "ORCID" 문자열 자체가 존재하지 않음):** TSJ는 ORCID를 언급·요구하지 않음 — 필수도 권장도 아닌 **완전 무관**(다른 Elsevier 계열지와 다른 지점).
6. **CRediT — ✅ 확정 필수:** *"Corresponding authors are required to acknowledge co-author contributions using CRediT (Contributor Roles Taxonomy) roles"* — Conceptualization/Data curation/Formal analysis/Funding acquisition/Investigation/Methodology/Project administration/Resources/Software/Supervision/Validation/Visualization/Writing–original draft/(Writing–review & editing, 표준 CRediT 14종). *"Not all CRediT roles will apply to every manuscript and some authors may contribute through multiple roles."*
7. **저자 변경 정책 — ✅ 확정, 대폭 상세화(가장 엄격한 축에 속함):** *"The editors of this journal generally will not consider changes to authorship once a manuscript has been submitted."* 절차: 전 저자가 제출 시점에 시스템에 등록 완료되어야 함 → accept 전에만, Editor 승인 시에만 변경 가능 → 반드시 **"Authorship Change Request form"** 사용, 교신저자가 사유+추가/삭제 대상 포함 **전 저자 서면동의** 제출 → **"This journal does not allow authorship changes after acceptance"**(추가/삭제/순서변경/교신저자변경 전부 불허, 예외 없음) → 검토 대상 기간엔 심사 일시정지 → **양식 없이 요청 시 원고 반려, 이미 게재된 경우 retraction 가능**(가장 강경한 페널티 조항).
8. **그룹/공동 저자 — ⚠️ 이번 원문엔 확인 안 됨**(이전 기재 "Jameson RK... on behalf of" 예시는 archived 2023 스냅샷 근거 — 현재 라이브 가이드 34페이지엔 그룹저자 조항 자체가 없음, 삭제되었거나 다른 페이지로 이동한 것으로 추정).
9. **Author contribution statement — ✅ 확정:** CRediT(§6)로 갈음, 별도 자유서술 섹션 요구 없음.
10. **Blinding/anonymization — ✅ 확정, 상세:** "Double anonymized peer review" — title page(저자정보 포함)와 anonymized manuscript(저자정보 제외)를 **별도 파일**로 제출. Acknowledgements/Declaration of competing interests/교신저자 주소는 **title page에만** 기재(본문·footnote 어디에도 넣지 말 것). 본문·supplementary material 전체에서 저자명/소속/acknowledgements 식별정보 전부 제거.
11. **하이픈/비서구권 이름 규정** — ⚠️ **여전히 not found**(34페이지 전체에 관련 조항 없음, 확정 부재).
12. **ICMJE form + FDA Device/Drug Form — ✅ 확정(위 Submission Checklist §10과 동일):** 저자 전원 개별 ICMJE form 작성, 전 페이지를 교신저자가 업로드.
13. **✅ 신규 확인 — Declaration of generative AI use(필수):** AI 도구 사용 시 References 앞 새 섹션("Declaration of generative AI and AI-assisted technologies in the manuscript preparation process")에 정형 문구로 공개 필수(문법/철자 검사, 장애인 보조기술은 예외). AI는 저자·공저자로 등재 불가.

---

## Spine (Phila Pa 1976) ✓

**Publisher:** Wolters Kluwer / LWW | **Style:** Numbered, cited in order of appearance (not alphabetical)
**In-text:** ¹, ², ³ (superscript numbers; do not link references to text)
**Author cutoff:** ✅ **3명까지 나열, 이후 et al.** (공식 확인 — Instructions for Authors, edmgr.ovid.com/spine/accounts/ifauth.htm, **2026-07-24 curl+UA로 라이브 재확인(HTTP 200, 이전 402 우회 성공)**: *"If there are more than three authors, name only the first three authors and then use et al."*) — 이전 기재된 "6명"은 오류, 수정함. ⚠️ **페이지 구조 특이사항:** 현재 화면엔 Research Letter 섹션만 렌더링되고, 일반 원고용 상세 서술은 HTML 소스 내 주석처리(`<!-- -->`)로만 남아있음(비표시, 텍스트 내용은 Research Letter와 거의 동일) — 육안으로는 안 보이니 페이지 소스를 봐야 전체 규정 확인 가능.
**DOI:** 저널 자체 예시에는 미포함 (journal name abbreviation은 *List of Journals Indexed in Index Medicus* 기준)

**Format (저널 자체 Sample reference, journal article):**
```
LastnameFM, LastnameFM, LastnameFM, et al. Title sentence case.
Spine Year;Vol:startpage-endpage(truncated).
```

**Journal's own sample (verbatim from Instructions for Authors):**
```
1. Guiot BH, Khoo LT, Fessler RG. A minimally invasive technique for
decompression of the lumber spine. Spine 2002;27:432-8.
```

**Notes:**
- Cite references **in the order of appearance** in the text, not alphabetically
- 페이지 범위는 끝자리 축약 표기 (432-8, 432-438 아님) — 저널 자체 예시 기준
- Volume:pages 형식 (issue number 미표기)
- ⚠️ "(Phila Pa 1976)"은 저널 자체 Instructions에는 없음 — **PubMed/NLM 색인 표준 저널명**이며, evidence.md·서지관리 도구(EndNote 등)에서 "Spine"과 Elsevier "The Spine Journal"을 구분하기 위해 사용. 원고 제출용 참고문헌 목록은 저널 자체 규칙(위 예시, "Spine"만) 우선, PubMed/DB 인용 시엔 (Phila Pa 1976) 사용 — 상황별로 구분해서 적용
- Unpublished data/personal communication은 본문 괄호 안에 인용 (참고문헌 목록에 넣지 않음)
- Structured Abstract 300 words (Study Design / Objective / Summary of Background Data / Methods / Results / Conclusion), Key Points 3-5개, Mini Abstract/Précis 50 words, 본문 2700 words (Case Report 750 words)

**Submission Checklist (Manuscript Checklist, edmgr.ovid.com/spine — before submission, 2026-07-09 확인; ✅ 2026-07-24 curl+UA로 라이브 재확인, HTTP 200 — 아래 굵게 표시된 항목이 신규/갱신):**

1. **Title page**
   - Corresponding author 지정 + full mailing address
   - Corresponding author e-mail address
   - Permission to reproduce copyrighted material / signed patient consent forms (해당 시)
   - Acknowledgments: grants, technical support, corporate support
   - IRB approval / Research Ethics Committee (or local equivalent) 명시
2. Structured Abstract 300 words (위 6개 heading) — 상동
3. Key Points 3–5개 — 상동
4. Mini Abstract 50 words — 상동
5. **본문에 line and page numbers 필수** (word count는 위와 동일: 2700 / Case Report 750)
6. **References — double-spaced**, cited in order of appearance (순서는 상동)
7. Tables — Word 또는 WordPerfect 파일로 제출. **✅ 신규 확인: 최대 5개 tables**, 폭 ≤41 picas/17.5cm.
8. Figure legends 별도 섹션
9. Figures — eps, tiff, ppt 파일형식. **✅ 신규 확인: 최대 8개 figures.**
10. **Copyright Form** — 저자 전원 서명 (제출 시 co-author 전원에게 자동 이메일 발송 확인)
    - Author attributions
    - Device Status / Drug statement
    - Financial/benefit disclosure statement(s)

**Author-related requirements (edmgr.ovid.com/spine/accounts/ifauth.htm, ✅ **2026-07-24 curl+UA로 라이브 직접 확인**(HTTP 200, Wayback 불필요) + Wolters Kluwer/Lippincott 일반 ethics 정책):**

1. **저자명/학위 표기 — confirmed(일반):** title page에 "authors' full names, highest academic degrees, and affiliations." 이니셜/하이픈 표기 세부 규정은 없음.
2. **Affiliation 형식·번호 매김** — ⚠️ **not found**. 구체 번호 매김 스타일 미확인(자매지 *Medicine®*는 dept/university/city/state/country 요구하나 Spine 자체 확인 안 됨).
3. **교신저자 필수 필드 — confirmed:** "name and address for correspondence, including fax number, telephone number, and e-mail address"; 체크리스트도 "full mailing address"·email 별도 명시.
4. **저자 수 제한** — 일반 논문은 ⚠️ **not found**. Research Letter만 **최대 4명**으로 제한.
5. **ORCID** — ✅ **라이브 페이지 직접 확인: 언급 자체 없음**(필수/권장 모두 아님). WKH 일반 정책(별도 페이지)만 "recommends... register with ORCID".
6. **CRediT** — ✅ **라이브 페이지 직접 확인 결과 언급 없음 확정**(Spine 자체 페이지 전체 스캔; 자매지 *Medicine®*는 EM에 14-role 옵션 있음 — Spine 적용 여부는 여전히 미확인).
7. **저자 변경 정책** — ✅ **라이브 페이지 직접 확인 결과 조항 없음 확정**(자매지 *Medicine®*는 "극히 예외적 상황만" 허용하나 Spine 고유 정책인지 미확인).
8. **그룹/공동 저자** — ✅ **라이브 페이지 직접 확인 결과 조항 없음 확정**(ICMJE 4기준 일반론만 적용).
9. **Author Attributions statement** — 체크리스트 항목명만 confirmed("Author attributions"), 정확한 필드/서식은 원본 Copyright Form 비공개로 ⚠️ **not found**.
10. **Blinding/anonymization** — 저자 블라인드 정책 ⚠️ **not found**(Spine 동료평가는 저자 비블라인드로 보임). 확인된 것은 환자/기관명 미노출(환자 익명성) 요구뿐.
11. **하이픈/비서구권 이름 규정** — ⚠️ **not found**. 확인된 문구: "The Journal is not responsible for published misspelled names due to author error."
12. **Copyright Form Author attributions 세부 필드** — ⚠️ **not found**(양식 비공개). 일반 ICMJE 4기준(WKH 정책 인용): "substantial contributions... drafted/revised critically... final approval... agreed to be accountable."

---

## Bone Joint J (BJJ) ✓

**Publisher:** British Editorial Society of Bone & Joint Surgery | **Style:** Superscript numbers
**In-text:** ¹, ², ³
**Author cutoff:** ✅ **최종 확정(2026-07-24, 실증 조사) — 저자 ≥7명이면 첫 3명 + et al.** 공식 문서엔 여전히 숫자 규정이 없어서(BJJ 사이트·CSL/EndNote 스타일 모두 부재), 실제 게재된 BJJ 논문 2편(무관한 주제·저자진, Europe PMC full-text XML)의 reference list를 전수 대조: **진짜 저자수 7명 이상인 피인용 논문 25건 이상 확인 결과, 예외 없이 전부 "첫 3명 + et al."**(6명도 전원도 아님 — ASJ/GSJ/CORR/JNS Spine과 같은 패턴). ≤6명 구간은 다소 불일치(전원 나열되기도, 3명+et al.로 축약되기도 — copyeditor가 저자 제출 포맷을 그대로 두는 것으로 추정, 엄격한 규정 아님). **결론: 7명 이상 인용 시 "첫 3명+et al." 사용 확정, 이전 "전원 나열" 기재는 오류였음(단일 사례의 byline을 reference-citation 예시로 오인한 것 — 아래 Verified example 각주 참조).**
**DOI:** doi: 형식으로 참고문헌에 포함

**Format:**
```
LastnameF-M, LastnameF-M, LastnameF-M, et al. Title sentence case.
Bone Joint J. Year;Vol-B(issue):pages.        # ≤6명은 전원 나열; 7명+면 첫 3명 + et al.
```

**Verified example — ⚠️ 이건 이 논문 자신의 byline(8저자 전원)이지, "BJJ가 이 논문을 인용할 때" 어떻게 축약하는지의 예시가 아님(예전에 혼동했던 부분 — 아래 Notes 참조):**
```
Park S-M, Song K-S, Ham D-W, Kang M-S, You K-H, Park C-K, Kim J-S, Park H-J.
Comparing the efficacy and safety of biportal endoscopic discectomy with microscopic
discectomy for lumbar herniated intervertebral disc: a multicentre, prospective,
assessor-blinded, randomized controlled trial. Bone Joint J. 2025;107-B(5):529–539.
```

**실제 reference-list 축약 예시 (2026-07-24 실증조사, 다른 BJJ 논문이 이 논문들을 인용한 방식):**
```
Wilson JE, Mart MF, Cunningham C, et al. [Delirium]. ... (원저자 8명 → 첫 3명+et al.)
Tieges Z, Maclullich AMJ, Anand A, et al. [4AT diagnostic accuracy]. ... (원저자 15명 → 첫 3명+et al.)
Maradit Kremers H, Larson DR, Crowson CS, et al. [THA/TKA prevalence]. ... (원저자 8명 → 첫 3명+et al.)
```

**Notes:**
- ⚠️ Volume format: `Vol-B(issue)` — 예: `107-B(5)` (B가 volume에 붙는 BJJ 특유의 형식)
- Author initials: hyphenated initials — S-M. Park (not SM Park)
- ✅ **저자 ≥7명 인용 시 "첫 3명+et al." 확정**(위 Author cutoff 참조) — 이전 "전원 나열" 기재는 **byline 예시를 reference-citation 예시로 착각한 오류**였음, 실제 인용 축약과는 무관한 사례였음.
- doi: 10.1302/0301-620X.107B5.BJJ-2024-1560.R1 형식 포함
- References: Vancouver style, superscript, **in order of appearance** (not alphabetical)
- ≤8명 저자(byline 자체의 상한, reference cutoff와 별개 개념), ScholarOne으로 제출

**Submission Checklist (boneandjoint.org.uk/journal/BJJ/instructions-for-authors + structure/checklist PDF, 2026-07-09 확인):**

1. **Title page** — 별도 title page에 전저자 정보 기재(본문은 완전 blind). ⚠️ mailing address/email 명시적 필드요구는 확인 안 됨(단, proof/free PDF는 교신저자에게 감). Copyright 자료 재사용 시 **서면 허가 증빙 함께 제출** 필수. Patient consent는 본문에 **명시(statement)** — 서명본은 저자 보관, 저널에 미제출. IRB/ethics: 제출 시 **ethics approval letter** 포함 + 본문에 statement(없으면 사유 설명). Acknowledgements는 본문 요소(title page 필수 아님).
2. Structured Abstract ≤**300 words**, heading **Aims / Methods / Results / Conclusion**. abstract 수치는 본문에도 다 나와야 함.
3. Key Points — **최대 3개** bullet(clinical relevance 요약), abstract 블록의 일부. 별도 word limit 없음.
4. 본문 word limit — **4,000 words (Abstract+본문+References 합산)**, 전 article type 공통 단일 limit. **Case Report 접수 안 함**(무심사 반려). Infographic ~300 words/≤10 refs.
5. Line/page numbering — ⚠️ 공식 가이드라인에 명시 안 됨.
6. References — 순서는 상동(Vancouver, in order of appearance). Double-spacing 명시 안 됨. et al. cutoff — ✅ **확정(위 Author cutoff 참조): 7명 이상이면 첫 3명+et al.**
7. Tables — 최대 **8개**, Word Table 도구로 작성(이미지 삽입 금지), 단문 heading+단위, 단일 Word 파일 안에 포함(word count에서 제외).
8. Figure legends — 별도 섹션, **논문 끝에** 전체 legend 기재
9. Figures — 최대 **10개**(a/b/c 개별 카운트, composite 분리 업로드). 방사선/사진/조직: **TIFF/JPEG ≥300dpi**. 그래프: editable EPS/Excel/PPT, 배경 무지·gridline 없음(폰트 Arial 8pt 대체).
10. Copyright/disclosure — Accept 후 **Assignment of Copyright** 서명. **Conflict-of-interest statement 필수**(accepted article 전체); 전저자 **ICMJE Disclosure form** 업로드; funding statement 3종 중 선택. ⚠️ device/drug 규제 status statement 명시 확인 안 됨(ICMJE form으로 갈음).

**Author-related requirements — 재확인 (boneandjoint.org.uk/journal/BJJ/instructions-for-authors + research-group-authorship + structure/checklist PDF, 2026-07-23 조회):**

1. **저자명/학위 표기 형식** — ⚠️ **재확인해도 not found(2026-07-24, 관련 PDF·페이지 전수 재탐색)**. 이니셜 하이픈 표기(S-M. Park)나 학위(MD/PhD) 표기 규정 어디에도 없음 — "S-M. Park"는 **끝까지 관찰 근거만**. 공식 title page 템플릿·docx 자체가 사이트에 없음(3rd party SciSpace 비공식 템플릿만 존재, 신뢰 불가).
2. **Affiliation 형식·번호 매김** — ⚠️ **재확인해도 not found**. 위첨자 번호 매김 등 구체적 서식 지침 없음.
3. **교신저자 필수 필드(주소/전화/이메일)** — ⚠️ **재확인해도 not found**. "full mailing address, telephone number and e-mail address" 문구가 검색에 나오긴 하나 **2013년판 JBJS / Spine·JAMIA류 일반 템플릿 문구가 섞여든 것으로 추정**(현재 JBJS는 email만 요구) — BJJ 자체 페이지엔 그 목록이 없음. 확정된 것은 여전히 "Proofs... emailed to the corresponding author"뿐.
4. **저자 수 제한 — confirmed:** "There is a limit of eight (8) authors." (Authorship 섹션) — **byline(저자 목록) 자체에 적용되는 상한**, 다른 항목(예: acknowledgements 인원)에는 적용 안 됨. 근거 미충족 기여자는 acknowledgements로 이동.
5. **ORCID — confirmed, 저자 전원 필수 아님(요청 사항):** "We ask that authors add an ORCID ID to their user account, if available, before making a submission." (Authorship 섹션) — 등록 안 된 저자는 https://orcid.org/register 안내. 즉 **강제(mandatory) 아님, 권장(requested)**.
6. **저자 자격 기준(authorship criteria) — confirmed, ICMJE 기반:** "Each author must have contributed significantly to, and take public responsibility for, one or more of the following study aspects: Design / Data acquisition / Analysis and interpretation of data." + "All authors must have been actively involved in the writing and revising of the manuscript, and each must provide final approval of the version to be published." (Authorship 섹션, ICMJE 정의 링크 병기) — **CRediT taxonomy(개별 contributor role 라벨링)는 요구되지 않음** — not found.
7. **제출 후 저자 변경 정책 — confirmed:** "Any change to authorship after peer review needs to be formally requested with a letter to the Editor-in-Chief. Please state the change required and ensure all authors have signed the letter." (Authorship 섹션)
8. **그룹/공동 저자(Research Group Authorship) — confirmed** (별도 정책 페이지 `/research-group-authorship`): 기준 충족 그룹원은 "Author A, Author B, Author C on behalf of the ABC research group" 형식으로 named author 등재 → PubMed에 fully searchable. 기준 미충족 그룹원 + 그룹명은 acknowledgements에 표기. ⚠️ 그룹명이 byline/title page/appendix 중 어디 위치하는지는 정책에 명시 안 됨.
9. **Author contribution statement(별도 섹션 요구)** — ⚠️ **not found**. Authorship 섹션의 기준 충족 여부만 서술할 뿐, 원고 내 별도 "Author Contributions" 문단/CRediT 라벨을 요구하는 문구는 없음.
10. **Blinding/anonymization — confirmed(기존 확인 재검증):** "Your main document should be completely blinded and all identifying information should be on a separate title page." + Preparing-a-paper-checklist PDF General 항목: "The manuscript has been blinded and any institutional or author names removed."
11. **하이픈/한국식 이름 표기 명시 규정** — ⚠️ **not found**. "S-M. Park" 형식이 공식 house style로 명문화된 문서는 끝내 찾지 못함(§1과 동일 결론) — 계속 "관찰 근거"로만 유지 권고.
12. **ICMJE Disclosure form — confirmed, ✅ 신규: 커스텀 양식 아니라 표준 ICMJE form(2026-07-24 재확인):** "The Bone & Joint Journal will publish in each article a summary of the information collected in the author(s)' ICMJE Disclosure of Potential Conflicts of Interest documents. For BJJ articles, all author ICMJE forms are uploaded to the website as supplementary material to the paper." **실제 게재논문 supplementary file로 실물 ICMJE 표준양식 확인됨**(예: `10.1302/0301-620X.103B3.BJJ-2020-1209.R1` supplementary "1209.r1_icmje.pdf") — BJJ 전용 커스텀 양식이 아니라 세계 공통 ICMJE Disclosure Form 그대로 사용. 필드는 표준(신원정보/연구관련 funding/최근 36개월 재정관계/기타 관계·활동/서명).

**참고 링크:** Preparing a paper checklist PDF(`Preparing_a_paper_checklist_1_8c065afb48.pdf`), The structure of a paper PDF(`The_structure_of_a_paper_2022_2_e0a4a15cd2.pdf`), research-group-authorship 정책 페이지(재확인, 그룹저자 자격기준만 다룸·이름표기 없음) — 이름/학위/번호매김/교신저자 연락처 서식은 **BJJ 공식 문서 어디에도 없는 것으로 결론**(2026-07-24, 재탐색 완료).

---

## J Bone Joint Surg Am (JBJS) ✓

**Publisher:** Wolters Kluwer / JBJS, Inc. | **Style:** Superscript numbers (AMA 기반)
**In-text:** ¹, ², ³
**Author cutoff:** ✅ 모든 저자 나열 (ALL authors — no et al. cutoff; 공식 verbatim "must include all authors (not 'et al.')", 아래 Notes; 12저자도 전원 나열 확인) — ⚠️ 타 저널과 반대이니 혼동 주의
**DOI:** 참고문헌 entry에는 미포함 (저널 masthead 자기인용에만 dx.doi.org)

**Format:**
```
LastnameFM, LastnameFM, ..., LastnameFM. Title sentence case.
JournalAbbr. Year Mon[ Day];Vol(issue):pages.
```

**Verified examples (2024_JBJS_HamDW_3DCage.pdf reference list):**
```
1. Lee JH, Kong CB, Yang JJ, Shim HJ, Koo KH, Kim J, Lee CK, Chang BS. Comparison of
   fusion rate and clinical results between CaO-SiO2-P2O5-B2O3 bioactive glass ceramics
   spacer with titanium cages in posterior lumbar interbody fusion. Spine J. 2016 Nov;
   16(11):1367-76.

7. Kim YH, Ha KY, Kim YS, Kim KW, Rhyu KW, Park JB, Shin JH, Kim YY, Lee JS, Park HY,
   Ko J, Kim SI. Lumbar Interbody Fusion and Osteobiologics for Lumbar Fusion.
   Asian Spine J. 2022 Dec;16(6):1022-33.
```

**JBJS 자기인용 형식 (article masthead):**
```
J Bone Joint Surg Am. 2024;106:2102-10 · http://dx.doi.org/10.2106/JBJS.xx.xxxxx
```

**Notes:**
- ⚠️ **모든 저자 나열** — et al. cutoff 없음 (ref 7: 12저자 전원 나열 확인)
- ✅ **공식 재확인** (jbjs.org/jbjs-ifa.php, 2026-07-09): "must include all authors (not 'et al.')" — verbatim 명시. 기존 표기 정확함.
- ⚠️ **Page range: hyphen + 뒷자리 축약** (1367-76, 1022-33) — 이 파일 전역 원칙(en-dash 전체)과 **다름**. JBJS는 hyphen·축약 사용.
- 약어에 **마침표 포함** (Spine J. / Clin Spine Surg. / J Bone Joint Surg Am.)
- 날짜에 **월(때로 일) 포함**: "2016 Nov;" / "2015 Aug 1;"
- `Vol(issue):pages` (issue 포함)
- ⚠️ JBJS 자기 volume은 citation에서 **plain "106"** — 표지 "106-A"의 `-A` 접미사는 citation 미사용 (PubMed canonical: 106(22)). **BJJ의 `-B`는 citation에 사용 → JBJS와 반대이니 혼동 주의**

**Submission Checklist (jbjs.org/jbjs-ifa.php, 2026-07-09 확인 — 현재 LWW 플랫폼 live IFA; figure DPI는 2026-07-24 guidelines-figures.php로 재확인):**

1. **Title page** — 필수: 제목, 저자명(순서)+학위, 연구 수행 기관, 각 저자 소속(도시/주/국가, 번호순), 교신저자+**email**. ⚠️ **전체 우편주소+전화는 현재판에서 요구 안 함**(2013년판엔 있었으나 변경됨). Acknowledgments/grant은 title page 아님(acknowledgment footnote). IRB approval은 title page 문구가 아니라 **별도 업로드 필수**(승인서한; 동물실험은 동물위원회 승인서한, 비영어면 번역본). Copyright-permission도 별도 항목(저작권자 서한 또는 Figure Permissions Form). ⚠️ Patient-consent/Helsinki/HIPAA 문구는 메인 IFA에서 확인 안 됨(별도 ethics-policy 페이지로 추정).
2. Structured Abstract 5문단 **≤325 words**(인종/민족 비율 보고 시 350까지). Heading: **Background**(연구질문 명시)/**Methods**/**Results**/**Conclusions**/**Level of Evidence**(clinical) 또는 **Clinical Relevance**(basic science).
3. Précis/mini-abstract/"What This Article Adds" — **과학논문엔 불필요**. 초청 Expert Review/World Report만 3–5개 bullet 요약 사용.
4. 본문 word limit — Scientific article(RCT/Observational/Basic-Science/Survey/Evidence-Based Systematic Review): **2,500 words**, ≤5 table+figure, structured abstract, $299 fee. Innovation/Viewpoint/Ethics/Health Care Rec/Patient Voices: 1,500. Arts&Humanities 1,000; Expert Review 3,000; World Report 2,000(둘 다 초청). ⚠️ 현재 독립 "Case Report" 유형 없음(→ JBJS Case Connector로 이관), "Current Concepts Review"도 없음. 과거 3,500 word limit → 현재 2,500으로 축소.
5. Line/page numbering — ⚠️ 현재 IFA에 명시 안 됨(확인 불가).
6. References — PubMed/Index Medicus 형식, **인용 순서로 번호**(알파벳순 아님), 본문 인용 전부 포함. Author cutoff는 위 참조. Preprint는 참고문헌 불가. Double-spacing 명시 없음.
7. Tables — Word 또는 Excel 형식, 설명적 제목, 표 번호 순으로 인용, 파일명에 번호 포함(예: Table 1.docx), 별도 파일(이미지 아님).
8. Figure legends — 별도: **본문 텍스트 파일 끝, References 다음**, 화살표/MRI 설정/조직사진 배율 등 전부 정의.
9. Figures — **TIFF 또는 EPS**, 순서대로 인용. ✅ **현재판 DPI 재확인 완료(2026-07-24, jbjs.org/guidelines-figures.php 라이브):** 컬러(RGB)·그레이스케일 **300ppi**, 흑백(Bitmap) **1200ppi**. 크기표: 300ppi → 5×7in/1500×2100px(최소폭 3.5in/1050px); 1200ppi → 5×7in/6000×8400px(최소폭 3.5in/4200px). 최대 7in, 최소권장폭 3.5in(89mm). TIFF/EPS만(JPG·Word삽입 불가) — 이전 "2013 archived, 재확인 필요" 각주 해소, 현재판과 수치 동일함 확정.
10. Copyright/disclosure — 현재 양식: **ICMJE Conflict of Interest Form**(저자별), **Figure Permissions Form**, **Open Access License Agreement**. ⚠️ 별도 "Copyright Transfer" 양식은 현재 Required Item에 없음(2013년엔 있었음) — license/COI 워크플로에 통합된 것으로 보임. Device/drug status statement는 별도 항목 아님(ICMJE disclosure에 포함). **CRediT contributor roles**(2018~) + **전저자 ORCID** 필수. Double-blind review(원고 익명화).

**Author-related requirements (jbjs.org/jbjs-ifa.php, 2026-07-23 확인):**

1. **저자명/학위 표기 — confirmed:** "authors' names, in the order in which they should appear, and academic degrees" (Title Page 항목 #2).
2. **Affiliation 형식·번호 매김 — confirmed:** "institution(s) at which the work was performed" + "institution (and city and state or country) with which each author is affiliated **in numerical order**."
3. **교신저자 필수 필드 — confirmed:** 이름+**email만**(Title Page 항목 #5) — 우편주소 요구 없음(2013년판에서 변경됨).
4. **저자 수 제한** — ⚠️ **재확인해도 not found(2026-07-24)**. jbjs-ifa.php/guidelines-group.php 전수 재탐색 완료 — 총원 상한 없음 확정. 단, 관련 캡: **Arts and Humanities 유형은 저자당 연 2편 상한**(무관 항목), **equal-contribution(공동1저자 등) 표기는 최대 2명까지만** 인정(CORR의 "3명까지"보다 더 엄격; BJJ는 해당 규정 not found).
5. **ORCID — confirmed, 전저자 필수:** "All authors must register with ORCID and include their ORCID identifier in their Editorial Manager profile... it will not be possible to submit an article without such an identifier for each author."
6. **CRediT — confirmed 필수(2018-01-01~):** "each author must indicate his/her contributor roles on the 'Add/Edit/Remove Authors' screen in Editorial Manager in accordance with... (CRediT)." 개별 role 목록은 IFA 페이지에 나열 안 됨(EM 화면 자체 표준 목록 사용).
7. **저자 변경 정책 — confirmed:** "Any change in authorship after the initial review process necessitates a signed letter, generally from all authors, agreeing to the change." 사망 저자는 유족의 서면 허가 필요.
8. **그룹/공동 저자 — confirmed(3단계):** (a) 전원 기준 충족 → byline엔 그룹명만, 개별은 Acknowledgment, 교신저자만 EM 등록; (b) byline에 지명 저자 일부+그룹명 병기; (c) 부분 충족 → "on behalf of the [group name]"(PubMed 미검색).
9. **Author contribution statement — confirmed(ICMJE 서술형, CRediT과 별개):** "actively involved in the drafting and critical revision... final approval" — 비저자 기여자는 acknowledgment footnote.
10. **Blinding — confirmed:** double-blinded, **Editorial Office가** 저자/기관 식별정보 제거 후 리뷰어에게 전달(저자 자체 블라인딩 지침 없음).
11. **하이픈/한국식 이름 규정** — ⚠️ **재확인해도 not found**. jbjs.org 전체(ifa/group/figures 페이지)에 관련 규정 자체가 없음 — 확정 부재.
12. **ICMJE COI form — confirmed:** 저자 개별 "Your Name" 필드 포함 1인 1양식(sites.jbjs.org/jbjs/conflict.docx); 비저자 medical writer도 제출 필요. 별도 "Authorship Responsibility" 양식은 없음(CRediT 화면으로 대체).

---

## Neurospine ✓

**Publisher:** Korean Spinal Neurosurgery Society | **Style:** Superscript numbers
**In-text:** ¹,²
**Author cutoff:** ✅ 공식 재확인(2026-07-09): 3명 이후 et al. (3명까지 나열, 4번째부터 et al.)
**DOI:** 참고문헌에 포함 (https://doi.org/ 형식)

**Format:**
```
LastnameFM, LastnameFM, LastnameFM, et al. Title sentence case.
Neurospine. Year;Vol(issue):pages.
```

**Verified example:**
```
Park SM, Song KS, Ham DW, et al. Safety profile of biportal endoscopic spine surgery
compared to conventional microscopic approach: a pooled analysis of 2 randomized
controlled trials. Neurospine. 2024;21(4):1190–1198.
```

**Notes:**
- Open access (CC BY-NC 4.0)
- Vol(issue):pages 형식 — issue number 포함
- ✅ 저자 cutoff "3명까지 나열, 이후 et al." **공식 재확인** (Instructions for Contributors PDF, Revised 2026-02-05, e-neurospine.org, 2026-07-09 조회)

**Submission Checklist (e-neurospine.org/file/ns_Instructions_for_authors.pdf, Revised 2026-02-05; 2026-07-09 확인 — PDF 원문 직접 대조):**

1. **Title page** — 별도 **external + internal** title page 2종. External: 제목, 전저자 성명+소속, manuscript type, running head ≤65자, 하단에 **교신저자 주소+전화+팩스+email**(주소·email 모두 필수), 학회 발표 이력, funding source(필요 시). Internal: 제목만(저자정보 없음). ⚠️ **IRB approval statement는 title page 아님** — Methods에 기재(승인번호 명시). Patient 사진 사용 시 signed release form 필요(Methods에 기술, title page 아님). Copyright-permission 조항 명시 확인 안 됨. 일반 acknowledgments는 본문 별도 섹션(funding만 title page + copyright form에 중복 기재).
2. Structured Abstract (임상/실험연구만): **Objective / Methods / Results / Conclusion**. ≤250 words(Original/Review), ≤200(Brief Communication), letter/editorial은 제한없음. Keywords 2–6개(MeSH).
3. Key Points/précis — **불필요**(해당 섹션 없음)
4. 본문 word limit: Original 5,000(≤5 table/fig, ≤40 refs) / Review 5,000(≤5, ≤100 refs) / Brief Communication 1,500(≤3, ≤20) / Letter 600 / Editorial 350. ⚠️ **전용 Case Report 유형 없음** — 가장 가까운 것은 Brief Communication(1,500 words).
5. Line numbering — **요구 안 함**. Page numbering: abstract 페이지부터 카운트(그 이후 저자명/소속 노출 금지). 본문 11pt, double-spaced.
6. References — **double-spaced 필수**, 첫 언급 순서로 번호(알파벳순 아님). Footnote 방식 불허. EndNote Neurospine style 제공.
7. Tables — MS Word table 기능으로 작성(이미지 불가), **본문과 별도 파일** 제출, 세로선 없이, 표 제목 명기.
8. Figure legends — **별도 섹션 필수**, 원고 마지막 순서(References → Table → Figure legends).
9. Figures — **JPG 또는 TIF만**, 사진/halftone ≥300dpi, line art ≥1200dpi, **개별 파일**로 제출(멀티패널도 분리, 합치지 않음). 파일명 예: "Fig-1A.tif".
10. Copyright/disclosure form — "Copyright Release, Author Agreement, Human and Animal Right, and Disclosure of Conflict of Interest" 통합 양식. 교신저자가 전저자 대표 서명(전저자 서명도 명시). 필드: 논문 제목, 교신저자명+email, **전저자 성명/순서 목록**(개별 기여 역할 아님 — ICMJE 기여도는 cover letter에 별도 기재). 재정 공개 필수(연구비/자문료/주식보유 → 본문에도 기재). ⚠️ **device/drug 임상시험 status statement는 form에 없음.**

**기타 참고:** APC $700(2026-03-01부터), 중재 임상시험은 data-sharing statement + 등록번호를 abstract 끝에 명기 필수, AI 도구 사용은 Methods/Acknowledgment에 공개(AI 저자 불가). Editorial office: support@e-neurospine.org.

**Author-related requirements (e-neurospine.org/file/ns_Instructions_for_authors.pdf, Revised 2026-02-05, 2026-07-23 재확인 — PDF 11페이지 전문 대조):**

1. **저자명/학위 표기** — confirmed: "full names of all authors with their institutional affiliations" — 학위(MD/PhD) 표기 필드는 ⚠️ **not found**.
2. **Affiliation 형식·번호 매김 — confirmed:** 연구 수행 기관을 첫 소속으로 spell-out, 이후 **위첨자 아라비아 숫자**로 저자명 옆 + 소속 앞에 연속 번호.
3. **교신저자 필수 필드 — confirmed(기존 노트와 일치):** external title page 하단에 **주소+전화+팩스+email 전부**.
4. **저자 수 제한** — ⚠️ **not found**(ICMJE 기여기준만 적용).
5. **ORCID** — ⚠️ **재확인해도 not found(2026-07-24, e-neurospine.org 최신 IFA + submit.e-neurospine.org/about/Author.php 제출포털 페이지까지 확인)**. ORCID 언급 자체가 없음 확정 — 단, **게재 논문 실제 PDF엔 저자 ORCID가 표시됨**(예: ns-19227edi-001.pdf) → 제출 포털 내부적으로는 수집하지만 공개 문서화된 정책은 없는 것으로 결론.
6. **저자 자격 기준/CRediT — confirmed, ICMJE 4기준(narrative), CRediT 미요구:** "conception and design, or acquisition, or analysis and interpretation of data / drafting or revising / final approval / accountability." **"Authors are required to make clear their contribution... in cover letter"** — 구조화된 CRediT role 목록 아님, cover letter 서술형.
7. **저자 변경 정책 — confirmed:** accept 전에만, Editor 승인 필요. 교신저자가 (a) 변경 사유 + (b) **전 저자** 서면동의(이메일/서한) 제출.
8. **그룹/공동 저자 — confirmed:** "accept direct responsibility"하는 개인만 저자 자격; 자금조달/자료수집/총괄감독만으로는 저자자격 미충족 — 나머지는 Acknowledgments.
9. **Contribution statement(cover letter) — confirmed:** ICMJE 기여 진술 + COI 공개("judgments were not influenced"라도 disclose) + 기존 발표자료와의 중복 여부 진술, 3가지 모두 cover letter에 포함.
10. **Blinding — confirmed, double-blind:** internal title page는 제목만(저자/소속 없음), abstract 페이지부터 번호 재시작 후 **저자명/소속이 이후 어디에도 노출 금지**.
11. **하이픈/한국식 이름 규정** — ⚠️ **not found**.
12. **Copyright Release/Author Agreement/Disclosure 통합 양식 — confirmed, 내부 불일치 발견:** 양식 자체(p.ix)는 **교신저자 1인 서명만**(전 저자 목록 나열 + "on behalf of all the co-authors") 요구하나, 본문 §I.3/§I.7은 "All authors must sign their autograph by themselves" / "Every author should sign"라고 서술 — **양식과 본문 규정이 서로 다름**, 제출 전 최신 실제 양식 재확인 권장.

---

## Journal of Neurosurgery: Spine (J Neurosurg Spine) ✓

**Publisher:** AANS / JNS Publishing Group | **Style:** Superscript numbers (AMA Manual of Style 11th ed.)
**In-text:** ¹,²
**Author cutoff:** ✅ **공식 확인 및 수정** (thejns.org/page/guidelines-for-references, 2026-07-09): **≤6명 전원 나열; ≥7명이면 첫 3명 + et al.** — 이전 "3명 이후 et al." 부정확, 수정함
**DOI:** 필수 포함 (PMID는 미사용)

**Format:**
```
LastnameFM, LastnameFM, LastnameFM, et al. Title sentence case.
J Neurosurg Spine. Year;Vol(issue):pages.
```

**Notes:**
- References: 첫 언급 순서로 번호(알파벳순 아님), 위첨자 아라비아 숫자, 괄호/대괄호 없음
- ⚠️ Double-spacing 명시 확인 안 됨
- own papers 중 JNS Spine 제출본에서 reference list 직접 확인 권장

**Submission Checklist (thejns.org — spine-info-for-authors, manuscript-types-and-limits-policy, guidelines-for-references/tables/figures; 2026-07-09 확인, WebFetch 403 → curl+UA로 확보):**

1. **Title page** — 전저자(성+이름, 최고학위만) + 소속(부서/기관/도시/주/국가, 위첨자 번호). 교신저자 = **이름+현재소속+email**. ⚠️ **전체 우편주소는 요구 안 함** — 템플릿에 "Do not include postal information" 명시. Element count(abstract/본문 word count, ref 수, table+figure 수, video 수) + **keyword 3–6개** 필요. Copyright/consent 문구는 title page 아님(업로드 양식으로 별도 처리). Acknowledgments는 본문 섹션(non-author 기여자 감사; funding은 title page/acknowledgments 아니라 제출 사이트에만 기재). **IRB/ethics statement는 title page 아니라 Methods**(동물실험 시 animal-welfare statement 포함).
2. Structured Abstract(clinical article·lab investigation만): **Objective, Methods, Results, Conclusions**. Review/technical note/historical vignette는 unstructured. Abstract 내 인용 금지. Word limit: 375(clinical/lab/review), 200(historical vignette), 없음(Broca's/Letter).
3. Précis/Key Points — ⚠️ **불필요**(템플릿·체크리스트에 없음; keyword 3–6개만 요구)
4. 본문 word limit — Clinical article 4000 본문/375 abstract/45 refs/8 table+fig; Lab investigation 동일; Literature review 4000/375/**75 refs**/8; Historical vignette 3500/200/45/8; Broca's(opinion) 3500 본문/abstract 없음/45/5; Letter 500 본문/10 refs/1개(fig or table or video). ⚠️ **현재 limit 표에 "case report"·"technical note" 없음** — case report는 별도지 **JNS: Case Lessons**로 유도(200 abstract, 3000 본문, 45 refs, 5 table+fig).
5. Line/page numbering — ⚠️ **어디에도 명시 안 됨**(템플릿은 US Letter 크기+단일 Word파일만 지정). 확인 불가.
6. References — AMA Manual of Style 11판, **첫 언급 순서**(알파벳순 아님), 위첨자 아라비아 숫자(괄호 없음). Author cutoff는 위 참조. DOI 필수, PMID 미사용, NLM 저널 약어. ⚠️ Double-spacing 명시 없음.
7. Tables — MS Word Table 도구로 작성, **전체를 하나의 별도 Word 파일**로 제출(테이블마다 별도 페이지), 제목+legend 포함, 약어는 footnote. 이미지/컬러/음영/불릿 금지, 1A/1B식 분할 금지.
8. Figure legends — **본문 텍스트 파일 맨 끝에 별도 섹션**(그림파일 안 아님). 문단 1개씩, 자동번호 없음.
9. Figures — **TIFF/JPEG/고화질 PDF**, ≤50MB, 완전 합성(A/B 분리 불가). **해상도: line art 1200dpi, color·grayscale-with-text 600dpi, grayscale/radiograph 300dpi.** 너비 3.3in(1단)/5–7in(2단), 높이 ≤9in, 폰트 Arial/Helvetica/Times.
10. Copyright/disclosure — ⚠️ **제출 시 전통적 copyright 양도 양식 없음**(AANS가 저작권 보유, accept 후 선택적 CC BY-NC-ND 라이선스 $3000). COI/재정공개는 **제출 사이트에서 ICMJE 스타일로 입력**(다운로드 양식 아님). "Original Material License Agreement"는 **원본 아트워크/비디오/사체표본 사진만** 해당(JNSPG에 비독점 게재권 부여, 저작권은 저자 유지) — device/drug status·재정공개 필드 없음. ⚠️ **device/drug 승인 status statement 확인 안 됨**. 기타 조건부 양식: Patient/Volunteer Consent(식별 가능 환자), Previously Published Permission Request, Change of Authorship Form.

**Author-related requirements (thejns.org: spine-info-for-authors, Manuscript_Template.docx, Submission_Checklist.docx, publishing-policies, Change_in_Authorship_Form.pdf; 2026-07-23 확인, curl+UA로 403 우회):**

1. **저자명/학위 표기 — confirmed·기존 노트 보완:** Manuscript Template 원문 "First Name, Middle Initial(s), if applicable, Last Name, and Highest Academic Degrees (do not include titles or specialties)" — 성만 아니라 **전체 이름(First/Middle/Last) + 최고학위**.
2. **Affiliation 형식·번호 매김 — confirmed:** "Department, Institution, City, State or Province, Country" + **위첨자 번호**로 저자-소속 매칭. "Do not include postal information."
3. **교신저자 필수 필드 — confirmed(기존 노트 일치):** Name/Current Institution/**Email**만 — 우편주소 필드 자체가 템플릿에 없음.
4. **저자 수 제한** — ⚠️ **not found**.
5. **ORCID** — ⚠️ **재확인해도 not found(2026-07-24)**. thejns.org 관련 페이지 재시도는 403 지속(bot차단), WebSearch로도 JNS/JNSPG 전용 ORCID 언급 못 찾음 — 동종 신경외과 저널(Neurosurgical Review, Turkish Neurosurgery 등)은 명시적 ORCID 요구가 있는데 JNS계열만 공개적으로 언급 없음, 확정 부재로 결론.
6. **저자 자격 기준/CRediT — confirmed, ICMJE 4기준 verbatim, CRediT 미요구:** "(1) Substantial contributions... AND (2) Drafting or critically revising; AND (3) Final approval; AND (4) Agreement to be accountable" — **4개 전부 충족 필수**(AND 조건 명시).
7. **저자 변경 정책 — confirmed, 매우 엄격:** accept 후 "no authorship changes will be allowed... adding or removing authors; changing the order of authors; or changing the corresponding author." Accept 전(revision 단계)에는 **Change of Authorship Form**(추가/삭제 대상 저자 포함 전원 서명) 제출 시에만 가능.
8. **그룹/공동 저자 — confirmed:** 그룹명을 저자목록 **마지막 위치**(title page에만, 제출시스템엔 없음)에 표기 가능, 개별 구성원은 본문 in-text Appendix. PubMed collaborator 색인 원할 시 교신저자가 JNSPG에 별도 통보 필요.
9. **Author contribution statement** — ⚠️ **필수 아님**(CRediT류 standalone statement 요구 없음). 비저자 기여자(기술자/자료수집/의학저술가)는 Acknowledgments만.
10. **Blinding/peer review — confirmed, single-blind(사전 가정과 다름):** "Peer review for JNS: Spine is single-blind" — 저자 신원은 편집자/리뷰어/직원에게 공개, 리뷰어 신원만 저자에게 비공개.
11. **하이픈/한국식 이름 규정** — ⚠️ **not found**.
12. **ICMJE COI — confirmed, 저자별 개별 이메일 링크:** "Each author will be sent an email with a link to the JNSPG conflict of interest and financial disclosure form. A completed form is required by each author." 비저자 기여자(통계학자/저술가)도 요청 시 COI statement 제출.

---

## Global Spine Journal (Global Spine J) ✓

**Publisher:** SAGE / AO Spine | **Style:** Superscript numbers (AMA Manual of Style)
**In-text:** ¹,²
**Author cutoff:** ✅ **공식 확인 (journals.sagepub.com/author-instructions/gsj, 2026-07-09):** AMA 기준 — ≤6명 전원 나열; ≥7명이면 첫 3명 + et al. — 이전 "SAGE default: 3 authors then et al." 부정확, 수정함
**DOI:** 포함

**Format:**
```
LastnameFM, LastnameFM, LastnameFM, et al. Title sentence case.
Global Spine J. Year;Vol(issue):pages.
```

**Notes:**
- References: AMA style, **cited in order of appearance** (not alphabetical)
- 2023_GSJ_Kwon O_Handgrip.pdf에서 reference format 직접 확인 권장
- ⚠️ **Case Report 더 이상 접수 안 함** (article type에서 제외됨)

**Submission Checklist (journals.sagepub.com/author-instructions/gsj, 2026-07-09 확인):**

1. **Title page** — corresponding author 필수(name/institutional address/phone/**email** 전부). 전저자+affiliation(연구 수행 기관). 필수 항목: Acknowledgments, Declaration of Conflicting Interests, Funding statement, **ethical approval + informed consent statement**(IRB 필수), Data availability statement. ⚠️ 서명된 patient consent form 원본은 제출 금지("환자 confidentiality 침해") — statement만 기재. **Anonymized peer review** — title page는 별도 파일로 분리, 본문에 식별정보 제거.
2. Structured Abstract **250 words**, heading: Study Design(2–3 단어) / Objectives / Methods / Results / Conclusions. Keywords 4–8개.
3. Key Points/Mini-abstract — 요구 안 함(섹션 없음)
4. 본문 word limit — Original Research/Review: 숫자 상한 규정 자체 없음(✅ 2026-07-24 확정, §13 참조). Letter to Editor: ≤500 words, <8 references, figure 없음.
5. Line/page numbering — 공식 페이지에 명시 안 됨(⚠️ unverified). 확인된 것: 전체 double-spaced, margin ≥3cm 좌우/5cm 상하.
6. References — AMA style(순서는 상동). Double-spacing은 "전체 double-spaced"에서 유추(list 자체 명시 안 됨).
7. Tables — Word DOC/RTF/XLS 허용, references 뒤 별도 업로드(본문에 embed 안 함)
8. Figure legends — 별도 섹션(Word 문서), references 뒤 & figures 앞에 업로드
9. Figures — .tiff 또는 .jpeg, **300dpi**, 별도 파일, 언급 순서대로 번호. Lateral image는 좌측 방향으로. 컬러 그림은 온라인 컬러 게재.
10. Copyright/disclosure — 저자 개별 **ICMJE conflict-of-interest form** 별도 제출. Accept 후 Contributor's Publishing Agreement(OA, 기본 **CC BY-NC-ND**). Declaration of Conflicting Interests + Funding statement 필수. ⚠️ device/drug status statement 명시 확인 안 됨.

**Author-related requirements (journals.sagepub.com/author-instructions/GSJ, 2026-07-23 재확인 — live page 정상 fetch, 403 없음):**

1. **저자명/학위 표기** — ⚠️ **재확인해도 not found(2026-07-24)**. GSJ 페이지도, SAGE 일반 authorship 정책도 학위/이니셜 형식 규정 자체가 없음 — 확정 부재.
2. **Affiliation 형식 — confirmed(번호 매김 규정은 없음):** "The full list of authors including names and affiliations of each"; "The listed affiliation should be the institution where the research was conducted."
3. **교신저자 필수 필드 — confirmed:** "Contact information for the corresponding author: name, institutional address, phone, email."
4. **저자 수 제한** — ⚠️ **재확인해도 not found**. GSJ 페이지엔 page charge/limit 자체가 없다는 서술만 있고 저자수 cap은 어디에도 없음 — 확정 부재(SAGE 일반정책도 상한 미언급).
5. **ORCID — confirmed, "strongly encouraged"(강제 아님, 사실상 준-필수):** "each co-author must log in to the submission system to add their own ORCID ID to their account"; **accept 이후 추가 불가** — 사실상 accept 전까지는 연결해야 함.
6. **CRediT — 명시적 요구 아님, 자유서술 Author Contributions 필수:** "You will be asked to list the contribution of each author... Please include the Author Contributions heading... after the Acknowledgements section." CRediT 표준 role 명칭 자체는 지정 안 됨.
7. **저자 변경 정책 — confirmed:** "All persons eligible for authorship must be included at the time of submission." **Proof 단계에서 저자 변경 불가**("Changes to the author list are not permitted at this stage").
8. **그룹/공동 저자 — ✅ 신규 확인(2026-07-24, SAGE 일반 cross-journal 정책, uk.sagepub.com/en-gb/asi/authorship-guidelines):** GSJ 자체 페이지는 침묵하나 SAGE 공통정책 confirmed: *"Sage supports groups of authors such as those participating in a working group or consortia within our publications. We ask that groups be highlighted on the title page and that group members who can take responsibility for the work as authors are listed clearly."* 기준 미충족 구성원은 Acknowledgments로. AO Spine/GSJ 전용 별도 규정은 없음(SAGE 공통정책 적용으로 간주).
9. **Author contribution statement — confirmed(§6과 동일):** Acknowledgements 뒤 별도 heading, 자유서술형.
10. **Blinding — confirmed, double-anonymized:** "the identity of both the reviewer and author are always concealed from both parties."
11. **한국식 이름 규정** — ⚠️ **재확인해도 not found**.
12. **ICMJE form — confirmed, 저자 개별 제출:** "All authors listed on the manuscript must fill out an individual ICMJE form and submit each one as a separate file." 추가 확인: AI 챗봇은 저자 자격 불가("should not be listed as authors").
13. **✅ 신규 확인 — 본문 word limit(Original Research/Review):** GSJ·SAGE 어디에도 숫자 상한 없음 확정(⚠️ 지속 unverified가 아니라 "규정 자체가 없음"으로 결론). 확인된 유일한 숫자: Abstract ≤250 words, Letter to Editor ≤500 words. Case Report는 접수 안 함(상동).

---

## Clinical Orthopaedics and Related Research (Clin Orthop Relat Res) ✓

**Publisher:** Wolters Kluwer / LWW | **Style:** Numbered brackets [N] (🔴 정정 2026-07-24 — 이전 "위첨자" 기재는 오류; edmgr 포털 예시는 대괄호)
**In-text:** [1], [2,3] — bracket, not superscript
**Author cutoff:** 🔴 **정정 (2026-07-24, edmgr.ovid.com/corr/accounts/ifauth.htm 라이브 포털 curl+UA로 직접 확인, HTTP 200):** *"All authors up to 6 may be included; if more than 6 authors, include the first 3 followed by 'et al.'"* — **이전 기재("모든 저자 나열, et al. 금지")는 2013년 편집장 사설 + LWW 일반 docx 기준이었고, 실제 제출 포털(Editorial Manager IFA, 저자가 실제로 쓰는 문서)의 현재 규정과 다름.** 포털 규정을 house style로 우선 적용 — **6명 이하 전원, 7명 이상이면 첫 3명 + et al.**(JBJS류의 "전원 나열"이 아니라 Spine/ASJ류의 표준 컷오프에 해당).
**DOI:** 불포함(포털 예시 기준) — 참고문헌 예시 4종(저널/챕터/단행본/웹사이트) 어디에도 DOI 필드 없음. 이전 "필수 포함" 기재는 에디토리얼 정책 문서 근거였을 가능성 — ⚠️ 제출 전 재검토

**Format (edmgr.ovid.com/corr/accounts/ifauth.htm 실제 예시, 2026-07-24):**
```
LastnameFM, LastnameFM, LastnameFM, et al. Title sentence case.
Clin Orthop Relat Res. Year;Vol:pages.
```

**저널 자체 예시 (verbatim):**
```
Kaplan FS, August CS, Dalinka MK. Bone densitometry observations of osteopetrosis
in response to bone marrow transplantation. Clin Orthop Relat Res. 1993;294:79-84.
```

**Notes:**
- 🔴 **et al. 컷오프 정정: 6명까지 전원, 7명 이상이면 첫 3명+et al.**(위 Author cutoff 참조) — 종전 "전원 나열" 기재는 오류.
- ⚠️ DOI 포함 여부 재검토 — 포털 예시엔 없음(위 참조)
- ⚠️ **References 순서: 알파벳순(저자 성 기준 A-Z)** — **첫 언급 순서 아님!**(다른 대부분 저널과 반대) — confirmed verbatim: *"The list of References must be in numerical sequence and alphabetized by the first author's last name (A-Z)."* 동일 저자 그룹으로 2편 이상이면 오래된 논문 먼저. In-text는 대괄호 숫자 [N](위첨자 아님, 이전 "위첨자" 기재 오류 — 포털 예시는 "Negotiation research spans many disciplines [3]." 형태).
- 전체 double-spaced (references 포함)

**Submission Checklist (LWW Guidelines for Authors + CLINICAL/BASIC RESEARCH MANUSCRIPTS.docx, Wayback 캡처 2024-05-10/08-13, 2026-07-09 확인; ✅ 2026-07-24 edmgr.ovid.com/corr/accounts/ifauth.htm 라이브 포털 curl+UA로 교차검증 — 아래 굵게 표시된 항목은 포털에서 재확인/추가된 내용):**

1. **Title page** — 제목 <120자, running title <40자, 전저자 성명+최종학위, **전저자의 소속/주소/email**(Editorial Manager 등록정보와 일치 필수) — 교신저자는 1명만 Editorial Manager에서 지정(ICMJE: co-corresponding 불가). **IRB statement 필수**(ethics committee 승인서한 사본 동봉, Declaration of Helsinki + HIPAA 언급). **Funding/재정 COI는 title page**(Conflict-of-Interest statement 일부). 비재정 acknowledgments(technical/corporate)는 **References 앞 별도 섹션**(title page 아님). Copyright 자료 재사용 permission 필수(인쇄+온라인 증빙). 식별 가능한 인물 사진은 **서명 patient consent 필수**.
2. Structured Abstract — **✅ 포털 재확인, heading 갱신:** **Background / Questions-purposes / Patients-Methods / Results / Conclusion** (+ Level of Evidence) — 이전 "METHODS"만 있던 표기를 "Patients-Methods"로 정정. ⚠️ **word limit 의도적으로 명시 안 함**(포털: "We are not overly concerned about word count, within reason." — Leopold 편집장 방침과 일치).
3. Key Points/précis — **불필요**(어느 문서에도 없음, 포털도 동일)
4. 본문 word limit — **article type별 일반 limit 없음**(포털도 재확인, §2 인용 참조). 유일한 예외: follow-up 연구는 **최대 3,500 words**(Intro→Discussion; 구버전 문서는 2,000으로 표기 — ⚠️ 문서 간 불일치). Case report limit 확인 안 됨.
5. Line/page numbering — ⚠️ 어느 문서에도 명시 안 됨(포털도 언급 없음).
6. References — 순서는 위 Notes 참조(**알파벳순**, appearance 아님, ✅ 포털 재확인). In-text **대괄호 숫자**(위첨자 아님, 🔴 정정). "≤6명 전원, 7명 이상 첫 3명+et al." (🔴 정정, 위 Author cutoff 참조). 전체 double-space 적용(references 포함). PubMed 약어, 이탤릭체.
7. Tables — **✅ 포털 세부 확인:** 가로형 최대 10–12열/35–40행, 세로형 최대 6–8열/50–60행, Word .doc/.docx 필수(스프레드시트 금지), 표마다 별도 파일(번호로 파일명), 간단 제목만(legend 없음), 아라비아 숫자.
8. Figure legends — **별도 섹션**, References 뒤 별도 페이지, multipart figure는 각각 legend.
9. Figures — **✅ 포털 재확인:** JPEG/TIFF/PNG, 별도 파일, **HIPAA 준수 마스킹**(환자 식별정보 가림) 명시. 구체 DPI는 여전히 포털에 명시 안 됨(별도 "CORR Artwork Guidelines" 문서 미접근, ⚠️ 재확인 필요). 온라인 컬러 무료, 인쇄 컬러는 유료일 수 있음.
10. Copyright/disclosure — **ICMJE Uniform Disclosure Form 저자 전원 제출 필수**(교신저자가 취합/업로드). Copyright Transfer Agreement: 일반 문서는 "저자 전원이 작성"이라 하나, 별도 CORR 노트는 CORR Insights/Column/Editorial/Letter/Obituary에만 필수라고 함 — ⚠️ **범위 불명확, 확인 필요**. Device/drug: 첫 언급 시 generic name 우선 표기 + 괄호로 **제조사/도시/국가** 명시(약물/기구/장비 전부). 재정공개: title page COI statement에 상세 기재(funding, 기관지원, 개인 지급/혜택), ICMJE form과 일치.

**Author-related requirements (LWW Guidelines for Authors v10.5.21 + "Research is a Team Sport" 편집장 사설, Clin Orthop Relat Res. 2013;471:701-702, Wayback 캡처, 2026-07-23 확인 + edmgr.ovid.com/corr/accounts/ifauth.htm 라이브 포털 2026-07-24 교차검증):**

1. **저자명/학위 표기 — confirmed:** title page에 "Author name(s) and final degree(s)."
2. **Affiliation 형식 — confirmed:** "affiliation, address, and e-mail addresses of all authors... must match those entered into our online submission system." 다기관 연구는 **연구 수행 장소 statement** 별도 필요.
3. **교신저자 필수 필드 — ✅ 정정·확인(2026-07-24, edmgr.ovid.com/corr/accounts/ifauth.htm 라이브 포털):** *"Designated Corresponding Author must include full mailing address"* — **전체 우편주소 명시 필수 확인됨**(이전 "not found" 정정). 이름/주소/이메일은 accept 후 공개됨(public); 교신저자는 **1명만** 지정 가능(co-corresponding 불가, ICMJE 원칙). 이름/이메일이 Editorial Manager 등록정보와 정확히 일치해야 함.
4. **저자 수 제한 — confirmed, 총원 상한 없음(포털도 재확인):** "Some journals have had arbitrary limits on the number of authors permitted. [CORR] will have no such limit as long as every author listed meets the ICMJE authorship criteria." 포털 자체는 총원 상한에 대해 침묵하나, "contributed equally"(공동 1저자/공동 교신저자) 표기는 **최대 3명까지만** 허용(포털 확인: "No more than 3 authors may be identified as having contributed equally in the first or senior author position").
5. **ORCID — confirmed, 필수 아님(포털도 재확인):** *"It is not required that authors register an ORCID before submitting to CORR."* 사설 제목("ORCID is a Wonderful (But Not Required) Tool")과 포털 문구 일치 — Editorial Manager 로그인 옵션일 뿐.
6. **CRediT — ⚠️ 소스 간 불일치, 재탐색해도 해소 안 됨(2026-07-24):** 2013년 편집장 사설은 명시적으로 "We will no longer... ask authors to report their specific contributions" — CRediT형 보고를 **거부**한다고 서술. **2026-07-24 라이브 포털(edmgr ifauth.htm)은 CRediT를 아예 언급하지 않음**(page silent). 2020-2026 사이 이 입장을 갱신·번복한 CORR 사설·LWW 정책 페이지는 **끝내 찾지 못함**(journals.lww.com 자체는 402로 재차 차단) — **2013년 사설이 여전히 공식 최종 입장으로 결론**, 포털 침묵은 단순 미기재로 해석. **CRediT 미요구 유지(신뢰도: 중간 — 13년 된 사설이 유일 근거).**
7. **저자 변경 정책 — confirmed(포털 문구로 교체):** *"Request to add or delete authors at revision stage or after publication... may be considered only after receipt of written approval from all authors and detailed explanation... decision rests with the Editor-in-Chief."* (accept 후 변경은 사실상 불허, 상동)
8. **그룹/공동 저자 — confirmed(포털도 재확인):** 사설: "a subset of authors writes on behalf of a group and the full list of authors is listed separately." 포털 문구: *"CORR® allows group-authorship arrangements under the terms outlined by... (ICMJE)."*
9. **Author contribution statement — confirmed, 요구하지 않음**(§6과 동일 맥락 — percentage/역할 보고 자체를 폐지; 포털도 별도 언급 없음).
10. **Blinding — confirmed, double-blind(포털 문구로 재확인):** *"CORR® utilizes a double-blind peer review system; please remove all author-identifying information from the main text prior to submission."* — **저자 본인이 블라인딩 책임**(JBJS와 달리 편집실이 아님).
11. **비영어/하이픈 이름 규정** — ⚠️ **not found**(포털도 언급 없음).
12. **ICMJE 명시적 채택 — confirmed(포털도 재확인):** *"Completion of the... ICMJE Uniform Disclosure Form... is required at original submission. Each author must complete a separate form."* 사설: "CORR® will use the criteria for authorship outlined by the ICMJE."

---

## Asian Spine Journal (Asian Spine J) ✓

**Publisher:** Korean Society of Spine Surgery | **Style:** Superscript numbers
**In-text:** ¹,²
**Author cutoff:** ✅ **공식 확인 (asianspinejournal.org/authors, 2026-07-09):** 저자 ≤6명이면 전원 나열; ≥7명이면 첫 3명 + et al. — 이전 "6명 이후 et al."은 부정확, 수정함
**DOI:** 포함

**Format:**
```
LastnameFM, LastnameFM, LastnameFM, et al. Title sentence case.
Asian Spine J. Year;Vol(issue):pages.
```

**Notes:**
- Reference cap: Original/Technical Note 30개, Narrative Review 30–100개, Letter 10개
- References: double-spaced, numbered **in order of first appearance** (not alphabetical)
- 2024_ASJ_ParkSM_MIS.pdf 또는 2025_ASJ papers에서 직접 확인 권장

**Submission Checklist (asianspinejournal.org/authors + /authors/checklist.php, 2026-07-09 확인):**

1. **Title page** — corresponding author 필수(full mailing address + tel + fax + email 전부); article title, running head(<10 words), 전저자 성명, affiliation(superscript), ORCID(선택). **Conflict-of-interest + funding은 title page에 기재.** IRB/consent: title page 아니라 Methods 서두에 ethics statement로 기술(IRB 번호 예시 제공). Copyright-permission 문구는 명시적으로 확인 안 됨(⚠️ not found). Acknowledgments는 본문 말미 별도 섹션(title page 아님).
2. Structured Abstract ≤300 words: **Study Design / Purpose / Overview of Literature / Methods / Results / Conclusions** (6개 heading — Spine 계열과 유사하나 "Overview of Literature"·"Purpose" 명칭 다름). Case Report는 unstructured ≤150 words. Keywords 최대 5개(MeSH).
3. Key Points 3–5개 필수(bullet, word limit 없음)
4. 본문 word limit: Original 3,000 / Review 4,000 / Technical Note 1,500 / Letter 500 (abstract+본문+figure legend 포함, title/refs/table 제외). ⚠️ Case Report 본문 word limit 명시 안 됨(abstract 150 words만 확인).
5. Page numbering: abstract를 1페이지로 연속 번호, **double-spaced** 전체. ⚠️ line numbering 명시 확인 안 됨(page numbering만 확인).
6. References — double-spaced, 순서는 위 Format 참조
7. Tables — 별도 파일 아님, 본문 MS-Word 파일에 포함; 순서대로 번호, 약어는 footnote 정의
8. Figure legends — 별도 섹션 필수(references 뒤, double-spaced)
9. Figures — 별도 파일 JPG/GIF/PPT 제출. 해상도: 사진/그레이스케일(예 방사선영상) ≥600dpi, line art ≥1200dpi. Accept 후 고화질 TIFF/EPS 요청.
10. Copyright/disclosure — Transfer of Copyright Agreement(양식 실물은 **교신저자 서명/날짜** 필드만 — §12 참조; 전저자 서명 요구 여부 ⚠️ 본문 규정 재확인) + 별도 Conflict of Interest form. 재정지원 전부 명시. Device/drug: 제조사명+지역(도시/주/국가) 명시. 저자 역할은 CRediT taxonomy로 기재. Cover letter는 교신저자 서명 필수.

본문 형식: MS-Word(.doc/.docx), 10pt Arial/Times/Courier, double-spaced, A4 or Letter.

**Author-related requirements (asianspinejournal.org/authors/authors.php, 2026-07-23 재확인 — `/authors`·`/authors/checklist.php` 직접 URL은 403, `authors.php`가 실제 작동 경로):**

1. **저자명/학위 표기** — 부분 confirmed: "Names of authors and addresses of institutions where the study was performed." 학위 접미사 형식은 ⚠️ **not found**.
2. **Affiliation 형식·번호 매김 — confirmed:** "insert superscript Arabic numerals immediately after the author's name and the same superscript numerals in front of the appropriate institution."
3. **교신저자 필수 필드 — confirmed(기존 노트와 일치):** "name, institutional address, telephone and fax numbers, and e-mail address."
4. **저자 수 제한** — ⚠️ **재확인해도 not found(2026-07-24, ethics.php/checklist.php/copyright_transfer_agreement.php/COI PDF 전수 재탐색)**. 숫자 상한 없음 확정. 단, **✅ 신규 확인 — 공동1저자/공동교신저자 허용:** "Description of co-first authors or co-corresponding authors is also accepted if the corresponding author believes that they contributed equally."(인원수 제한 명시 없음, JBJS의 "2명까지"보다 느슨)
5. **ORCID — confirmed, 여전히 선택:** "Open Researchers and Contributors ID (ORCID) of all authors **can be** provided" — "must"가 아닌 "can" — 강제 아님 확인.
6. **CRediT — confirmed 요구, 세부 role 목록은 외부 링크만:** "Role of each author should be declared in accordance with the CRediT Taxonomy initiative (https://credit.niso.org)." 구버전 8항목 서술형 목록(conception/data acquisition/analysis/drafting/critical revision/funding/administrative support/supervision)도 병존.
7. **저자 변경 정책** — ⚠️ **재확인해도 not found**(ethics.php에 "changes in authorship"이 연구부정행위 예시로만 언급, 정상적 변경 절차·양식 자체가 사이트에 없음 — 확정 부재).
8. **그룹/공동 저자** — ⚠️ **재확인해도 not found**(ethics.php/authors.php 어디에도 그룹/컨소시엄 저자 조항 없음 — §4의 공동1저자 허용과는 별개 개념).
9. **Author contribution statement — confirmed, 얇은 요구:** "Each author's role should be addressed on the title page"(§6 CRediT와 연동). 기준 미충족자는 Acknowledgments로.
10. **Blinding — confirmed:** "Neither authors' names nor their affiliations should appear on any of the manuscript pages" + 제출 시 **별도 blinded manuscript 파일** 필수.
11. **한국식 이름 규정** — ⚠️ **재확인해도 not found**.
12. **Copyright/COI 양식 — ✅ 신규: 실제 PDF 원문 확인 완료(2026-07-24, asj-conflict_of_interest.pdf + copyright_transfer_agreement.php 직접 확인):** COI form 필드: 논문제목, 저자명/서명, **9행 표**(저자/no-COI/COI-specify 3열), COI 예시목록(funding source/paid consultant/study investigator funded by sponsor/employee of sponsor/board membership/stock holder/patent inventor/competitor관계/기타), funding source 기재란, 교신저자 attestation+서명/날짜, 제출은 우편/팩스/이메일(spinepjb@catholic.ac.kr). Copyright Transfer Agreement 필드: 논문제목, 저자명, 교신저자 서명/날짜, "all right, title, interest, and copyright ownership" 양도 문구, **원본 손서명 필수**(전자서명 불가 시사).

---

## European Spine Journal (Eur Spine J) ✓

**Publisher:** Springer | **Style:** Springer Basic (numbered, bracketed)
**In-text:** [1], [2, 3], [4–6]
**Author cutoff:** ✅ 공식 확인(2026-07-09): 숫자 cutoff 없음 — 전저자 나열 기본, 긴 저자목록의 'et al' 축약도 허용. own-paper 관찰 두 형태는 아래 Notes
**DOI:** https://doi.org/ 형식으로 참고문헌에 포함 (권장)

**Format:**
```
LastnameFM, LastnameFM, ... (Year) Title sentence case. JournalAbbr Vol:pages. https://doi.org/xxx
```

**Verified examples (2025_ESJ_ParkSM / 2026_ESJ_ParkHJ own papers):**
```
1. Park SM, Park J, Jang HS, Heo YW, Han H, Kim HJ, Chang BS, Lee CK, Yeom JS (2020)
   Biportal endoscopic versus microscopic lumbar decompressive laminectomy in patients
   with spinal stenosis: a randomized controlled trial. Spine J 20:156–165.
   https://doi.org/10.1016/j.spinee.2019.09.015

   Li H, Zou X, Laursen M, Egund N, Lind M, Bünger C (2002) The influence of intervertebral
   disc tissue on anterior spinal interbody fusion: an experimental study on pigs.
   Eur Spine J 11:476–481

   Lowe TG, Hashim S, Wilson LA et al (2004) A biomechanical study of regional endplate
   strength and cage morphology as it relates to structural interbody support.
   Spine (Phila Pa 1976) 29:2389–2394
```

**Notes:**
- ⚠️ **연도가 저자 직후 괄호** 안: `Authors (Year) Title...` (Springer 특유 — AMA/Vancouver와 다름)
- 약어에 **마침표 없음**: "Eur Spine J", "Spine J", "Clin Orthop Relat Res", "Acta Neurochir (Wien)"
- **Vol:pages — issue 미포함** (11:476–481). Supplement: "Eur Spine J 24 Suppl 3:372–377"
- Page range: **en-dash + 전체 숫자** (476–481, 156–165) — JBJS와 반대
- In-text: bracket 번호 [1] (Springer numbered)
- 저자 suffix 유지: "Hurley RK Jr", "Anderson ER 3rd"
- ⚠️ **Author cutoff 불일치 관찰:**
  - 2025_ESJ (own paper): 9저자 **전원 나열**
  - 2026_ESJ (own paper): 7명 이상 시 **첫 3명 + et al**
  - → Springer Basic 공식 = 전저자. 안전하게 **전저자 나열 권장**; reference manager가 truncate하면 "첫 3명 + et al"도 ESJ에서 통용됨
  - ✅ **공식 확인** (link.springer.com/journal/586/submission-guidelines, 2026-07-09): "Ideally, the names of all authors should be provided, but the usage of 'et al' in long author lists will also be accepted." → **숫자 cutoff 자체가 없음** — 전저자 나열이 기본, et al 축약도 허용(정확한 명수 규정 없음)

**Submission Checklist (link.springer.com/journal/586/submission-guidelines, 2026-07-09 확인):**

1. **Title page** — 별도 title page: 제목, 저자명, affiliation(기관/부서/도시/주/국가), **교신저자 명시 + 활성 email 필수**(전체 우편주소 별도 의무는 없음 — affiliation에 포함되면 그게 게재됨), ORCID(가능 시). **Acknowledgments(인물·grant·fund)는 title page 별도 섹션**(funder 전체명 기재). **IRB/ethics approval**은 title page의 **Declarations 블록**(Funding/Competing interests/Consent/Data availability/Author contributions와 함께)에 포함. Copyright 자료 재사용 **permission 필수**(증빙 제출). Patient consent — **Consent-to-publish 양식(docx)** 제공, Declarations에 명시. ⚠️ Double-anonymous review — 식별정보는 시스템 별도 제출, 본문은 anonymize.
2. Structured Abstract 150–250 words: **Purpose / Methods / Results / Conclusion**. Systematic review/original article은 최대 **450 words**까지 확장 가능(reporting guideline 준수 시). Case report abstract ≤350 words.
3. Key Points/précis — ⚠️ **불필요**(keyword 4–6개만 요구)
4. 본문 word limit — Original 2,500(refs ≤25) / Review·Meta-analysis 3,500(refs 50–70) / Case Report 1,500(15 refs, image 5개, figure/table 2개; Intro/Case Presentation/Discussion/Conclusion 구조, Patient Perspective 선택)
5. Page numbering **필수**(자동 페이지 번호 기능 사용). ⚠️ Line numbering 명시 요구 없음.
6. References — 번호형, **첫 언급 순서**(대괄호 Vancouver, 알파벳순 아님). ⚠️ Double-spacing 명시 없음. Author cutoff는 위 참조(숫자 규정 없음). DOI는 full link로 포함.
7. Tables — Word **table 기능** 사용(스프레드시트 붙여넣기 금지), 본문 Word 파일에 포함. 아라비아 숫자, 순서대로 인용, caption 필수, footnote는 위첨자 소문자.
8. Figure legends — **본문 텍스트 파일에 포함**(그림파일 안에 넣지 않음) — 사실상 별도 caption 섹션. "**Fig.**"+번호(볼드), 번호/caption 끝에 마침표 없음.
9. Figures — **EPS(벡터) 선호, TIFF**(halftone), MSOffice 파일도 허용, 폰트 임베드, 파일명 "Fig1.eps". 해상도: line art ≥1200dpi, halftone ≥300dpi, combination ≥600dpi, 컬러는 RGB 8-bit, 레터링 Helvetica/Arial 8–12pt.
10. Copyright/disclosure — **제출 전 별도 copyright 양도 양식 없음**(hybrid 저널, accept 후 처리, Open Choice 가능). 제출 전 의무: **재사용 permission 증빙 + consent-to-publish form**. Disclosure는 **Declarations 블록**(Competing interests(최근 3년 이내 공개)/Funding/Ethics/Consent/Data-Materials-Code/Author contributions). ⚠️ device/drug status statement 요구 없음(미국 정형외과계 저널 특유 관행, Springer 586엔 없음).

**Author-related requirements (link.springer.com/journal/586/submission-guidelines, 2026-07-23 재확인):**

1. **저자명/학위 표기** — ⚠️ **재확인 시도했으나 journal 586 페이지 자체가 idp.springer.com 쿠키인증 redirect loop로 재접근 불가(2026-07-24)** — 진짜 부재인지 재확인 못한 상태(WebFetch는 쿠키jar 없어 무한루프). Springer 일반 가이드(journal 586 전용 아님)엔 학위/직함 미포함 방침만 있음 — 참고만.
2. **Affiliation 형식 — 부분 confirmed:** institution/department/city/state/country 요구; "If address information is provided with the affiliation(s) it will also be published." **✅ 번호매김 신규 단서(Springer 일반 정책, journal 586 재접근 불가로 확정은 아님):** "multiple affiliations should be marked with superscript Arabic numbers, and they should each start on a new line" — ORCID iD도 이름 옆 위첨자 표기 가능. ⚠️ 이 항목은 journal 586 자체 재확인 실패로 "Springer 일반 관행"으로만 취급 권장.
3. **교신저자 필수 필드 — confirmed:** "One author is assigned as Corresponding Author... ensures that questions... are appropriately addressed" + **활성 email 필수**. 별도 우편주소 의무는 없음(affiliation에 포함되면 그대로 게재).
4. **저자 수 제한 — ✅ 정정, 사실상 확정(2026-07-24, Springer Nature Support 공식 페이지 직접 확인):** *"An unlimited number of authors can contribute to a manuscript to be submitted to Springer Nature journals."* — **Springer Nature 전체 정책으로 상한 없음 확정**(journal 586도 이 정책 적용 대상, 개별 재확인 불필요할 만큼 명확).
5. **ORCID — confirmed, 선택(주의: 일반 Springer 관행과 다름):** "If available, the 16-digit ORCID of the author(s)" — **교신저자·공저자 구분 없이 전부 선택사항**(다른 Springer지의 "교신저자 필수" 패턴과 어긋남, ESJ 자체는 강제 아님).
6. **CRediT — confirmed, 템플릿 제공하되 자유서술도 허용:** "Conceptualization: [full name]…; Methodology…; Formal analysis and investigation…; Writing – original draft preparation…; Writing – review and editing…; Funding acquisition…; Resources…; Supervision…" — Declarations 블록에 기재, CRediT 형식이 아닌 자유 서술도 인정.
7. **저자 변경 정책 — confirmed:** accept 후 추가/삭제 불허; revision 중에도 "generally not permitted, but in some cases... may be warranted"(사유 설명 시 예외); "author names will be published exactly as they appear on the accepted submission."
8. **그룹/공동 저자 — ✅ 신규 확인(Springer Nature 일반 authorship-principles 정책, 2026-07-24):** *"A collective of authors can be listed as a consortium... individual authors can be listed in both the main author list and as a member of a consortium... All authors within a consortium must be listed at the end of the paper... to facilitate submission of manuscripts with large author lists, please consult the journal editor before submission."* journal 586 전용 문구는 재확인 불가(위 §1 사유와 동일)했으나 Springer 전체정책 적용 대상으로 간주.
9. **Author contribution statement — confirmed(§6 CRediT 블록 또는 자유서술), Declarations 안에 위치**.
10. **Blinding — confirmed, double-anonymous(상세):** "Author names, affiliations and any other potentially identifying information should be removed from the manuscript text and any accompanying files"; **자기인용으로 신원 노출되는 것도 지양** 지시.
11. **비서구권 이름/접미사 규정** — ⚠️ **재확인해도 not found**(단, Jr/3rd 등 접미사는 citation 표기에서 유지 — 별도 항목, 위 Notes 참조). byline 자체의 이름순서/하이픈 규정은 Springer 어디에도 없음.
12. **ICMJE vs 자체 정의 — confirmed, ICMJE와 사실상 동일(명명은 안 함):** 4기준 내용 일치. **AI 저자 명시적 배제:** "Large Language Models (LLMs)... do not currently satisfy our authorship criteria." 비affiliated 저자는 email 없이 도시/국가만 기재되는 경우 있음(별도 요청 시에만 email).

---

## Journal of Medical Internet Research (JMIR) ✓

**Publisher:** JMIR Publications | **Style:** Numbered brackets, AMA Manual of Style (11th ed.) 기반
**In-text:** [1], [2,3], [4–7] — 첫 언급 순서로 번호 (알파벳순 아님)
**Author cutoff:** ⚠️ **명시적 숫자 규정 없음.** 공식 문서: "References can be in any format, as long as the in-text citations are sequentially numbered... and as long as the reference at the end has a PMID in the format PMID:123456." CSL 예시(Paperpile)는 저자 7명도 **et al. 없이 전원 나열** — 안전하게 전저자 나열 권장, 축약 시 유효한 고유식별자만 확실히 갖추면 "minor variation is acceptable."
**DOI/PMID:** **필수(둘 중 하나 이상 고유식별자)** — 저널 논문은 DOI와 PMID, 도서는 ISBN, 온라인 자료는 접속일 포함 URL. 관행상 `PMID:숫자` 표기.

**Format (공식 예시 기반):**
```
LastnameFM, LastnameFM, ... Title sentence case. JournalAbbr Year Mon Day;Vol(Issue):pages. PMID:xxxxxxx
```

**Verified/official example (JMIR reference-format support article):**
```
Benzi R. Physics. Getting a grip on turbulence. Science 2003 Aug 1;301(5633):605-606.
PMID:12893931
```

**Notes:**
- Article title은 **sentence case**(단어별 대문자화 금지) — 공식 명시.
- Reference list는 **인용 순서(번호순)**로, 알파벳순 아님.
- Minor format 편차는 허용되지만 **정확한 고유식별자(DOI/PMID/ISBN/URL+접속일)는 필수** — 이 부분이 JMIR reference 규정의 핵심(형식보다 식별자 우선).
- ⚠️ 저자명 이니셜 하이픈(S-M.) 등 house style 명시 없음 — 관찰 근거 없음(own paper 게재 이력 없음, 2026-07-23 기준).

**Author-related requirements (✅ 2026-07-24 갱신 — jmir.org 메인 IFA페이지 curl+UA로 라이브 확인 200 성공 + support.jmir.org 개별 FAQ 16개(1차 10 + 2차 심화 6)를 Wayback Machine 스냅샷(2023-2025)으로 원문 직접 확인 — 이전 WebSearch 스니펫 기반 기재를 검증된 verbatim 인용으로 전면 교체. **CRediT 관련 이전 기재는 오류로 정정**):**

1. **저자명/학위 표기 — ✅ 정정·확인(2026-07-24, "Submitting Your Manuscript to JMIR Publications: A Guide for Authors", support.jmir.org, Wayback 2025-07-10):** *"Full names, highest academic degrees, ORCIDs, and affiliations for all authors."* — title page에 전체이름+최종학위+ORCID+소속 전부 요구(이전 "규정 없음" 정정). Author Contributions 섹션 자체는 이니셜만 사용(§9 참조, 이건 유지).
2. **Affiliation 형식·순서 — ✅ 확인:** *"List affiliations in the order: Department, Institute/University, City, Country."* 위첨자 번호/문자 스타일은 여전히 ⚠️ **not found**(소속은 제출시스템 메타데이터 폼으로 입력되는 방식으로 보임, 원고 내 표기 규칙 자체가 없을 수 있음).
3. **교신저자 필수 필드 — ✅ 확인:** *"Complete contact details (email, telephone, full address) for the corresponding author."* — **이메일+전화+전체주소 전부 필수** 확정(이전 "not found" 정정).
4. **저자 수 제한** — ⚠️ **여전히 not found**(신규 소스 6개에도 상한 언급 없음).
5. **ORCID — ✅ 정정된 verbatim(2026-07-24):** *"JMIR Publications requires that all authors / coauthors have an ORCID (a unique researcher identifier) at the time of publication... While they can be added after submission, ORCIDs are required in case of acceptance."* — 전 저자 필수(accept 시), 결론은 기존과 동일.
6. **저자 자격 기준·CRediT — 🔴 정정(2026-07-24, support.jmir.org 원문 직접 확인):** **CRediT taxonomy는 JMIR 정책 어디에도 등장하지 않음**(이전 "encouraged" 기재는 오류 — WebSearch 스니펫 오인). 실제로는 **자유서술 내러티브 + 이니셜만**(§1 참조), CRediT 용어·역할 목록 사용 안 함. 저자 자격 기준은 ICMJE 4criteria verbatim(115004439228): *"Substantial contributions to the conception or design of the work; or the acquisition, analysis, or interpretation of data for the work; AND / Drafting the work or revising it critically for important intellectual content; AND / Final approval of the version to be published; AND / Agreement to be accountable for all aspects of the work."* **서명 확인 — 신규 확정:** *"Authors ultimately confirm that they meet authorship criteria by signing the JMIR License to Publish form."* **그룹저자 관련 신규 확정: "Only authors must sign the form, not individual collaborators (members of a group author)."**(§8 그룹저자 항목의 근거)
7. **저자 변경 정책 — ✅ verbatim 확정(2026-07-24, Guide for Authors):** *"changes to authorship (such as adding or removing authors, or altering the author sequence) after round 1 of peer review are strongly discouraged and are strictly subject to journal approval."* — 기존 기재와 결론 일치, 이제 verbatim 출처 확보.
8. **그룹/공동 저자 — ✅ 신규 근거(115004439228):** License to Publish form은 **저자만 서명**(그룹 구성원/collaborator는 서명 불요) — 즉 그룹저자의 개별 구성원은 공식 authorship 책임 서명 대상이 아님. byline 표기 방식(예: "on behalf of...") 자체는 이번 재검증 FAQ에 없음(⚠️ 미확인 유지).
9. **Author contribution statement — ✅ 정정(115000525871 원문 직접 확인):** **필수 아님**: *"This is not a required section, but is included in the final publication if provided."* CRediT 헤딩 사용 안 함(§6 참조) — **실제 예시 문장**: *"BGM wrote the manuscript and provided data for Table 1, SGH conducted the patient interviews, and KL conducted all statistical analyses. All authors reviewed the final manuscript."*
10. **Blinding/peer review** — ⚠️ 여전히 single/double/open 명시적 용어 확인 안 됨. 신규 확인: "cascading(portable) peer-review" 정책 — 게재거부 후 JMIR 계열 타 저널로 전송 시 **"no new reviewers will be assigned if the review process is complete"**(리뷰 재사용). 리뷰어 익명성 자체의 명시적 규정은 여전히 not found — 이전 "single-anonymized 기본" 기재는 유지하되 신뢰도는 WebSearch 스니펫 수준 그대로.
11. **비서구권 이름 표기 규정** — ⚠️ **not found**(원문 재확인에도 없음, 총 16개 소스 문서 어디에도 없음).
12. **Competing interests/재정 공개 — ✅ verbatim 확정(115001252671):** *"A competing interest / conflict of interest (COI) is anything that interferes with, or could reasonably be perceived as interfering with, the full and objective presentation, peer review, editorial decision-making, or publication of research or non-research articles submitted to a JMIR journal."* **PLOS COI 정책 기반**임을 명시("based on the COI policy of PLOS").
13. **✅ 신규 확인 — Cover letter(360056442251):** 선택이지만 "strongly advised", **최대 500 words**. 포함 권장 내용: 편집장명, 저널명, 논문제목, article type, 배경·방법론·주요결과 요약, COI 공개, 교신저자 연락처(1인만), APF(APC) 인지 확인, 저널전송 선호도, **Case Report는 환자/보호자 동의 확인 문구 추가**. 타 저널 기제출/심사중 이력 및 APF waiver 사유는 공개 필수.
14. **✅ 신규 확인 — 중복게재/사전공개 정책(22084430171163):** COPE 기준(redundant/duplicate publication) 적용. 타 저널 심사중인 원고 이중제출은 **"not acceptable... unethical authorship behavior"**. Conference abstract(약 450-500 words)는 예외적으로 허용 가능. Preprint는 별도 정책 참조.
15. **✅ 신규 확인 — Plagiarism 정의(29759962647195):** *"When somebody presents the work of others (data, words or theories) as if they were his/her own and without proper acknowledgment."* **콘텐츠 중복 10% 이상이면 표절 의심 가능**. AI표절 별도정의: AI가 생성한 문장을 저자 본인 것처럼 제출하는 행위.
16. **✅ 신규 확인 — 게재 후 윤리 문제 처리(37743441611931):** Research Integrity Manager가 게재 전후 윤리·부정행위 이슈 처리 총괄, COPE flowchart 따름. 조치: corrigenda/expression of concern/retraction 가능. 독자 문제제기는 ed-support@jmir.org.

**Submission Checklist (✅ 2026-07-24 갱신 — support.jmir.org FAQ 16개 Wayback 원문 확인으로 다수 항목 신규 확정):**

1. **필수 섹션(본문 구조)** — IMRD + Abstract, Keywords, Acknowledgments(선택; 철자 e 없이, §15), Funding Statement, Conflicts of Interest, Data Availability, Author Contributions(선택, §9 참조), Abbreviations, References — 상동.
2. Structured Abstract — ✅ **재확인(360020341552):** Background/Objectives/Methods/Results/Conclusions, **최대 450 words**(구조화·비구조화 공통 상한). "must NOT include hyperlinks or references/citation numbers." RCT는 **abstract 내 임상시험 등록번호 필수**.
3. Article types — 상동(Original Paper/Viewpoint/Review 등).
4. 본문 word limit — 상동, word count 산정 범위(제목/abstract/references 포함 여부)는 여전히 ⚠️ **not found**.
5. Line/page numbering — ⚠️ **여전히 not found**(신규 소스 6개 포함 전체 16개 문서에도 없음, 확정 부재).
6. References — 상동.
7. Tables — 상동(이미지 제출 불가).
8. Figure legends — ⚠️ **여전히 not found**.
9. Figures — ✅ **verbatim 재확인(Guide for Authors):** *"Submit your figures as high-resolution PNG files with minimal compression."* **구체적 DPI 수치는 재확인에도 끝내 없음** — 수치기준 자체가 없는 것으로 결론(정성적 "high-resolution"만 요구).
10. **Open access / License / APC** — ✅ **CC 라이선스 재확인(115002955531):** *"JMIR Publications publishes all articles under a Creative Common License... (cc-by)... the most liberal cc-license other than CC0."* 예외 없음(TOC 이미지만 별도 CC0/CC-BY 이미지 사용 가능). APC 금액은 여전히 ⚠️ 미확정(Fee Schedule 페이지 별도 확인 필요, 저널별 상이).
11. **✅ 신규 확인 — Article Title(115002943791):** *"All article titles should fit within a 280-character limit (including spaces), should be descriptive of the subject of the research, should not reveal the results of the study... should be understandable to those outside the field."*
12. **✅ 신규 확인 — Keywords(360016786231):** *"Enter multiple (5-12) keywords (separate by a semicolon)"* — 이전 "무제한" 기재 정정, **5–12개** 명시.
13. **✅ 신규 확인 — IRB/Informed Consent(360048970851):** *"authors should indicate IRB (Institutional Research Board, also known as REB) approval/exemption and whether the procedures followed were in accordance with... the Helsinki Declaration of 1975, as revised in 2000."* Informed consent 획득 시 명시 필수. JMIR는 COPE 회원.
14. **✅ 신규 확인 — Reporting Guidelines(115001575267):** 필수 아닌 "recommended," 연구유형별 매칭: PRISMA(체계적 문헌고찰), **CONSORT-EHEALTH**(RCT, e-health 특화), SPIRIT(JMIR Res Protoc 프로토콜), CHERRIES(웹기반 설문), TRIPOD(예측모델). "체크리스트를 supplementary file로 업로드 강력 권장."
15. **✅ 신규 확인 — Acknowledgments(360015982471):** 필수 아님("This is not a required section"). 제목은 정확히 **"Acknowledgments"**(e 없이), **불릿 목록 금지**(서술형만), Discussion 끝에 배치, funder명+역할 명시, **AI/도구 사용 시 disclose 필수**.

---

## J Am Med Inform Assoc (JAMIA) ✓

**Publisher:** Oxford University Press (OUP) / American Medical Informatics Association (AMIA) | **Style:** Numbered brackets (Vancouver-family)
**In-text:** `[6]` immediately after punctuation; multiple: `[1, 4, 39]` or consecutive `[22-25]`
**Author cutoff:** ✅ **confirmed** (academic.oup.com/jamia/pages/General_Instructions, 2026-07-23 조회): *"List the names and initials of all authors if there are 3 or fewer; otherwise list the first 3 and add 'et al.'"*
**DOI:** 일반 저널기사 참고문헌에는 불포함(예시 없음); dataset 인용에는 identifier 포함 필수

**Format (저널 자체 예시, journal article):**
```
N LastnameFM, LastnameFM, LastnameFM, et al. Title sentence case. JournalAbbr Year;Vol:pages.
```

**Journal's own sample (verbatim from General_Instructions):**
```
13 Koziol-Mclain J, Brand D, Morgan D, et al. Measuring injury risk factors: question
   reliability in a statewide sample. Inj Prev 2000;6:148-50.
```

**Book example (verbatim):**
```
15 Howland J. Preventing Automobile Injury: New Findings From Evaluative Research.
   Dover, MA: Auburn House Publishing Company 1988:163-96.
```

**Dataset citation format (verbatim):**
```
[dataset]* Authors, Year, Title, Publisher (repository name), Identifier.
```

**Notes:**
- ⚠️ 위 journal-article/book 예시는 OUP가 다수 저널에 공용으로 쓰는 boilerplate Vancouver 예시로 보이나(예: Koziol-Mclain injury-prevention 인용은 다른 OUP 저널에서도 관찰), **JAMIA 공식 페이지에 실제로 게재된 문구**이므로 confirmed로 표기.
- Vol:pages 형식(issue 미표기), page range hyphen + 뒷자리 축약(148-50, 163-96) — Vancouver 표준.
- Word 초과분(Acknowledgments·References)은 word count에서 제외: *"JAMIA word limits exclude materials in Acknowledgments and in References sections."*

**Author-related requirements (academic.oup.com/jamia/pages/General_Instructions, 2026-07-23 조회):**

1. **저자명/학위 표기 형식 — confirmed:** Title page에 "Full name, department, institution, city, country, and degree of all co-authors" 기재.
2. **Affiliation 형식·번호 매김** — ⚠️ **not found**: 위첨자 숫자 매김 등 구체 서식 지침 없음(단순 나열 서술).
3. **교신저자 필수 필드 — confirmed:** Title page에 "Full name, postal address, e-mail and telephone number of the corresponding author" — **우편주소+전화+이메일 모두 명시적 필수**(Spine J/Spine과 동일 수준으로 엄격, JBJS/JNS Spine보다 강함).
4. **저자 수 제한** — ⚠️ **재확인해도 not found(2026-07-24)**. General_Instructions·For Reviewers·jamia_publishing 전수 재탐색 — 상한 없음 확정.
5. **ORCID 요구 여부 — ✅ 정정(2026-07-24, General_Instructions 재확인):** **교신저자에 한해 권장(recommended)** — 공저자 필수 규정은 없음(이전 "not found" 대비 진전: 완전 부재가 아니라 "교신저자만 권장"으로 구체화). BJJ의 "전 저자 요청"보다도 좁은 범위.
6. **저자 자격 기준 / CRediT — confirmed, CRediT 필수:** *"Authors should choose from the contributor roles outlined on the CRediT website and supply this information upon submission."* (복수 역할 선택 가능) — OUP 계열 특성상 **제출 시점에 CRediT role 필수 지정**. 기준 미충족 기여자는 "non-author contributors with their contributions clearly described"로 본문에 명시.
7. **제출 후 저자 변경 정책 — confirmed:** *"After manuscript submission, no authorship changes (including the authorship list, author order, and who is designated as the corresponding author) should be made unless there is a substantive reason to do so."*
8. **그룹/공동 저자(consortium) 규칙** — ⚠️ **재확인해도 not found**. AMIA 자체 정책·"code of professional and ethical conduct" 문서도 그룹저자 전용 조항 없음(ICMJE 일반원칙만 원용) — 확정 부재.
9. **Author contribution statement 별도 섹션** — CRediT role 제출로 갈음(§6). 원고 내 별도 "Author Contributions" 문단을 명시적으로 요구하는 문구는 확인 안 됨(BJJ와 유사하게 not found).
10. **Blinding/anonymization(peer review) — ⚠️ 재확인해도 not found(2026-07-24, For Reviewers 페이지 직접 확인):** 페이지 원문은 "peer review... critical function to ensure material is reviewed by other experts" 정도만 서술, blind 종류 명시 자체가 없음 — **확정 부재로 결론**(자매지 JAMIA Open만 별도로 single-blind 확인, 본지엔 미적용 — 혼동 주의 유지).
11. **Non-Western/하이픈 이름 표기 규정** — ⚠️ **not found**.
12. **Competing interests / ICMJE — confirmed:** 온라인 제출 시스템에서 COI 신고 필수; *"If the manuscript is published, Conflict of Interest information, including if none was declared, will be communicated in a statement."* ICMJE 양식 자체를 명명하지는 않음(다른 OUP/AMIA 저널처럼 온라인 폼으로 대체 가능성).
13. **AI 사용 공개 — confirmed:** *"The use of AI (for example, to help generate content or images, write code, process data, or for translation) should be disclosed both in cover letters to editors and in the Methods or Acknowledgements section of manuscripts."*
14. **Preprint 정책 — confirmed:** *"Authors retain the right to make an Author's Original Version (preprint) available through various channels, and this does not prevent submission to the journal."* Accept 후 preprint에는 정식 인용정보 포함한 고지문 삽입 요구.
15. **Data Availability Statement — confirmed(필수):** *"The inclusion of a Data Availability Statement is a requirement for articles published in JAMIA."*

**Submission Checklist (academic.oup.com/jamia/pages/General_Instructions, 2026-07-23 확인):**

1. **Title page** — 필수 항목(§1·§3 참조): 제목, 전저자 성명+소속(부서/기관/도시/국가)+학위, **교신저자 우편주소+전화+이메일**, keyword **최대 5개**, word count(title page/abstract/references/figures/tables 제외 기준 명시). Copyright/IRB/patient-consent 문구 위치는 본문 페이지에 명시 안 됨(별도 policy 페이지 추정, 미확인).
2. Structured Abstract — Research and Applications/Reviews(systematic): **Objective, Materials and Methods, Results, Discussion, and Conclusion**; Reviews(tutorial): **Objectives, Target Audience, and Scope**. 나머지 유형(Brief Communications/Case Reports/Perspectives)은 heading 미지정, word limit만 부여. Correspondence/Editorials는 abstract 없음.
3. Key Points/précis — ⚠️ **not found**(해당 섹션 없음).
4. 본문 word limit(표, 저널 표기 그대로):

   | Article type | 본문 | Abstract | Tables | Figures | References |
   |---|---|---|---|---|---|
   | Research and Applications | ≤4000 | ≤250 | ≤4 | ≤6 | unlimited |
   | Reviews | ≤4000 | ≤250 | ≤4 | ≤6 | unlimited |
   | Brief Communications | ≤2000 | ≤150 | ≤2 | ≤3 | unlimited |
   | Case Reports | ≤2000 | ≤150 | ≤2 | ≤3 | unlimited |
   | Perspectives | ≤2000 | ≤150 | ≤2 | ≤3 | unlimited |
   | Correspondence | ≤1000 | — | ≤1 | ≤1 | ≤5 |
   | Editorials/Highlights | ≤1000 | — | ≤1 | ≤1 | ≤5 |

   Supplemental materials(추가 table/figure/data/code)는 online-only 게재로 무제한 첨부 가능.
5. Line/page numbering — ⚠️ **not found**.
6. References — 번호형(Vancouver), author cutoff는 위 참조. Double-spacing 명시 안 됨. DOI는 일반 참고문헌엔 불포함(dataset만 identifier 필수).
7. Tables — **Word 형식, 본문 내 최초 인용 위치에 배치**(별도 파일 아님 — Spine J/JBJS/BJJ 등과 반대 방향).
8. Figure legends — 본문 원고 **맨 끝에 별도 제공**(그림파일에는 미포함).
9. Figures — **별도 파일로 업로드 필수**(본문 삽입 금지), **alt text 필수**(접근성). 구체 파일형식/DPI는 General_Instructions에 명시 안 됨 — OUP 공용 Author Resource Centre 기준(color/halftone ≥300dpi, grayscale halftone ≥600dpi, combination/line art 600–900dpi, monochrome line art ≤1200dpi; .tiff 선호, .jpg/.png 허용) 적용 추정 — ⚠️ **JAMIA 전용 수치로 확인된 것 아님**.
10. Open Access/License/Copyright — **Hybrid 저널**: accept 후 저자가 "standard licence" 또는 "open access licence" 중 선택(*"can publish under either a standard licence or an open access licence"*). ⚠️ **정확한 APC 금액(USD) 및 CC BY/CC BY-NC/CC BY-NC-ND 세부 명칭은 공식 페이지에서 확인 안 됨** — General_Instructions는 "Details of the open access licences and open access charges"로 별도 링크만 제공(링크 대상 페이지 접근 시 저널별 표가 로드되지 않아 본 조사에서 미확보). 참고: 자매지 JAMIA Open은 Gold OA, CC BY 4.0, APC ≈US$3,582로 별도 확인되나 **본지 JAMIA(hybrid)에는 그대로 적용 불가**(별개 요금 체계). 저자는 제출/accept 전 반드시 academic.oup.com/jamia 상 "Open Access" 링크를 직접 재확인할 것.
11. QC/Integrity — **Similarity Check/iThenticate 표절검사** + 이미지 조작·papermill 스크리닝 명시.
12. Cover letter — 관련 논문의 기(旣)게재/심사중 여부, 이전 심사 이력 고지 요구.

⚠️ **Peer review type(single/double-blind)은 2026-07-24 재확인(For Reviewers 페이지 포함)에도 끝내 확인되지 않음 — 확정 부재로 결론.** ORCID는 위 §5 참조(교신저자 권장으로 구체화됨). APC 정확한 금액/CC 라이선스명은 재확인해도 여전히 불명(OUP 자체 오픈액세스 요금 페이지가 저널별 표를 로드하지 않음) — 제출 전 ScholarOne 제출 시스템의 실제 필드로 최종 확인 권장.

---

## npj Digital Medicine (npj Digit Med) ✓

**Publisher:** Springer Nature (Nature Portfolio, npj Series) | **Style:** Nature numbered style (Vancouver-based)
**In-text:** superscript numbers, cited in order of appearance in text/methods/tables/figure legends
**Author cutoff:** ✅ **공식 확인** (nature.com/npjdigitalmed/for-authors-and-referees/submission-guidelines, 2026-07-23): *"All authors should be included in reference lists unless there are more than five, in which case only the first author should be given, followed by 'et al.'"* — **≤5명 전원 나열; 6명 이상이면 첫 저자 1명만 + et al.** (다른 저널의 "3명"·"6명" 컷오프보다 훨씬 제한적 — et al. 앞에 **1명만** 남김)
**DOI:** 포함 (article number 뒤에 `https://doi.org/...` 전체 URL 형태로 표기; 문서 예시 중 구버전 인쇄저널 예시엔 DOI 없음 — npj 시리즈 자체는 online-only이므로 사실상 전부 DOI 포함)

**Format (저널 자체 reference-list 규칙, submission guidelines 원문 예시):**
```
Lastname, F. M., Lastname, F. M. & Lastname, F. M. Title sentence case, ending with full stop.
J. Abbr. Vol, pages/article-number (Year). https://doi.org/...     # 6명+ → Lastname, F. M. et al.
```
- Volume 숫자와 뒤따르는 쉼표는 **bold** 처리
- 저자 성 먼저, 쉼표, 이니셜(마침표 포함); 2명 이상이면 마지막 저자 앞에 `&`
- Article title: Roman체, 첫 단어만 대문자, 원문 그대로, 끝에 마침표
- Journal name: 이탤릭체, 마침표 포함 약어

**저널 자체 예시 (submission guidelines 원문 그대로):**
```
Schott, D. H., Collins, R. N. & Bretscher, A. Secretory vesicle transport velocity in living
cells depends on the myosin V lever arm length. J. Cell Biol. 156, 35-39 (2002).

Bellin, D. L. et al. Electrochemical camera chip for simultaneous imaging of multiple
metabolites in biofilms. Nat. Commun. 7, 10535; 10.1038/ncomms10535 (2016).
```

**npj Digital Medicine 자기 논문 실제 예시 (nature.com/articles 페이지 "Cite this article", 2026-07-23 확인):**
```
Akbarialiabad, H., Pasdar, A. & Murrell, D.F. Digital twins in dermatology, current status,
and the road ahead. npj Digit. Med. 7, 228 (2024). https://doi.org/10.1038/s41746-024-01220-7
```
(https://www.nature.com/articles/s41746-024-01220-7)

**Notes:**
- ⚠️ **Page range 대신 article number 사용** (Nature 계열 특유) — 위 예시 "228"이 페이지가 아니라 article number. npj Digital Medicine은 online-only(인쇄본 없음)이므로 **전 논문이 article-number 체계**.
- `Vol, article-number (Year)` 형식 — issue number 미표기.
- ⚠️ **불일치 관찰:** nature.com 개별 article 페이지의 자동생성 "Cite this article" 위젯은 저자 6명 이상이어도 **첫 3명 + et al.** 로 표시(예: "Wang, Z., Cao, L., Danek, B. et al." — 실제 저자 6명 이상, https://www.nature.com/articles/s41746-025-01840-7 확인). 이는 **UI 자동 인용 스니펫의 관례**이며, 저자가 자기 원고 reference list를 작성할 때 따라야 할 **공식 Submission Guidelines 규정(첫 저자 1명만 + et al.)과 다르다** — 원고 작성 시엔 Submission Guidelines 문구를 house style로 따를 것.
- Reference 순서: 첫 언급 순서 (text/methods/tables/figure legends 전체 통틀어 번호 부여, 알파벳순 아님). Footnote 방식 불허.
- 미발표 데이터(meeting abstract 미출간본, in preparation 논문)는 번호 매긴 목록에 넣지 않고 본문에 저자명(또는 이니셜)과 함께 언급. Published conference abstract·patent·research dataset은 참고문헌에 포함 가능(dataset은 DOI/accession code 포함). Grant 세부사항·acknowledgments는 번호 참고문헌으로 불가.
- URL은 본문에 괄호로 인용(참고문헌 목록 아님); 정식 peer-reviewed online journal 논문만 참고문헌 목록에 포함.

**Author-related requirements (nature.com/npjdigitalmed submission-guidelines + editorial-policies/authorship, 2026-07-23 확인):**

1. **저자명/학위 표기 형식** — ⚠️ **not found**. Title page는 "the full author list"만 요구, 학위(MD/PhD)·이니셜 하이픈 표기 규정 명시 없음. 저자명은 **Roman alphabet 표준** 사용.
2. **Affiliation 형식·번호 매김** — **confirmed:** Title page에 "author affiliation information, including institution, city, and country" 필수. ⚠️ 위첨자 번호 매김 방식 자체는 명시 안 됨(일반 관행상 사용). **Primary affiliation 규칙 confirmed:** "The primary affiliation for each author should be the institution where the majority of their work was done. If an author has subsequently moved, the current address may also be stated."
3. **교신저자 필수 필드 — confirmed, email만:** Title page 필수 항목은 "the corresponding author(s) email address"뿐 — **우편주소·전화번호는 요구 안 됨** (다른 정형외과 계열 저널과 대비되는 지점).
4. **저자 수 제한** — ⚠️ **not found**. 명시적 상한 없음(대형 컨소시엄은 "please consult the journal editor before submission"으로 사전 협의 권장).
5. **ORCID — confirmed, 교신저자만 강제:** "we ask all corresponding authors of accepted papers to provide their...(ORCID) ID, before submitting the final version of the manuscript." **Non-corresponding authors do not have to link their ORCID but are encouraged to do so.** 최종본 제출 전(accept 후)까지 연결하면 됨; proof 단계에서는 추가/수정 불가.
6. **저자 자격 기준 — confirmed, ICMJE 유사(McNutt et al. 2018 PNAS 기반):** "substantial contributions to the conception or design of the work; or the acquisition, analysis, or interpretation of data; or the creation of new software used in the work; or have drafted the work or substantively revised it" AND 제출본 승인 AND 개인적 책임(accountability) 수용. ⚠️ **CRediT taxonomy(개별 contributor role 라벨 목록)는 요구되지 않음** — 이 부분은 사용자 사전 가정과 다름: Nature Portfolio는 CRediT 표준 role 목록이 아니라 **자유서술형 Author Contributions statement**(이니셜 기준)를 사용한다. Medical writer가 저술한 non-primary-research 논문은 게재 거부 가능(writing assistance는 acknowledgement 필수).
7. **저자 변경 정책 — confirmed:** 제출 후 저자 순서 변경·추가·삭제는 **전 저자 승인 필요**. **Accept 후에는 저자 변경·교신저자 변경·저자 순서 변경 전면 불허** ("Changes of authorship...are not permitted after acceptance of a manuscript"). 저자 간 분쟁은 저널이 조정하지 않고 소속 기관으로 이관.
8. **그룹/컨소시엄 저자 — confirmed:** Consortium을 하나의 저자로 등재 가능; 개별 저자가 main author list와 consortium 소속 양쪽에 동시 등재 가능. Consortium 구성원 전원은 **논문 말미에 나열 필수**. 기여하지 않은 구성원 명단은 Supplementary Information으로 이동 가능. 대형 저자 목록은 사전에 편집자와 협의 권장.
9. **Author contribution statement — confirmed, 필수(전 콘텐츠 타입):** "the statement should refer to all authors individually, denoted by their initials." 예시 문구: *"FC analyzed and interpreted the patient data... RH performed the histological examination... All authors read and approved the final manuscript."* 동등 기여(equal contribution)·공동 지도(joint supervision) 표기 허용.
10. **Blinding/anonymization — confirmed, single-anonymized(단일 블라인드):** "The npj Series operate a single-anonymized peer review process. In line with policy, referees are not identified to the authors, except at the request of the referee." → **저자는 블라인드 처리되지 않음**(리뷰어만 익명) — 사용자 사전 가정("single 또는 optional double-blind")과 일치, double-blind 옵션은 명시 안 됨(⚠️ not found).
11. **비서구권 이름 표기 — confirmed:** 표준은 Roman alphabet. **비Roman 문자 병기 지원**(괄호 안, 온라인 HTML판에만 표시): 지원 스크립트 = Arabic, Chinese, Cyrillic, Devanagari, Greek, Hebrew, Hangul, Japanese, Persian. 예시: "Mina Razzak (مينا رزاق)".
12. **경쟁이해관계/재정 공개 — confirmed:** 교신저자가 **전 저자를 대표해 서명된 competing interests statement 제출 의무**(mandatory). 이해관계 없어도 "no competing interests" 선언 필수. financial/non-financial 이해관계 전부 대상.

**Submission Checklist (nature.com/npjdigitalmed/for-authors-and-referees/submission-guidelines + /content-types + /for-authors-and-referees/editorial-process + /open-access, 2026-07-23 확인 — curl+UA로 idp.nature.com 쿠키 리다이렉트 우회, 200 확보):**

1. **Title page** — 필수: 제목(≤15 단어, 구두점·idiom·pun 금지), 전저자 성명, affiliation(institution/city/country), **교신저자 email만**(우편주소·전화 불요). IRB/ethics는 title page 아니라 **Methods에 승인 세부사항 기재 필수**(human/animal 참여·자료 사용 시). Acknowledgments는 별도 섹션(funding은 acknowledgments에만 기재 — **별도 Funding statement 섹션 불허**). Copyright 자료 재사용 permission은 제출 시 확보 필수(명시 문서화는 아님).
2. Abstract — **구조화 안 됨(No subheadings)**: Article ≤150 words; Brief Communication/Comment/Editorial/Matters Arising/News&Views/Perspective/Review ≤70 words(Matters Arising 제외 공통). ⚠️ 임상연구 계열 저널과 달리 **Background/Methods/Results/Conclusion 헤딩 없음** — 단일 문단.
3. Key Points/précis — ⚠️ **불필요**(해당 섹션 없음).
4. 본문 word limit — **Article: 별도 상한 명시 안 됨**(Results엔 subheading, Discussion엔 subheading·limitations·conclusion 섹션 금지); Brief Communication 1,000–1,500 words; Comment 1,000–2,000; Editorial 상한 없음; Matters Arising ≤1,200; Perspective ~3,000; Review 3,000–4,000. Reference 상한(엄격히 적용 안 됨): Article/Editorial/Review ≤60, Perspective ≤70, Brief Communication ~20, Comment/News&Views ~25, Matters Arising ~15(원논문이 첫 인용이어야 함). **Systematic review/scoping review/meta-analysis는 Review 아닌 Article로 제출.**
5. Line/page numbering — ⚠️ 명시 확인 안 됨(초기 제출은 포맷 요건 자체가 면제 — 아래 6 참조).
6. **초기 제출 시 포맷 요건 전면 면제 — confirmed:** "Manuscripts submitted to npj Digital Medicine do not need to adhere to our formatting requirements at the point of initial submission; formatting requirements only apply at the time of acceptance." References는 원고 어디든(text/methods/tables/figure legends) 첫 언급 순서로 번호. Double-spacing 명시 없음.
7. Tables — 본문 Word/TeX/LaTeX 파일 **끝에 포함**(별도 파일 아님); 통계 분석 포함 시 오차분석 방법·범위를 표 legend에 기재.
8. Figure legends — **본문 파일 references 뒤에 추가**; 전체 그림 제목 + 패널별(a/b/c) 설명, **패널당 아니라 그림 1개당 ≤350 단어**. 오차막대 정의 필수, 기호는 문자로 서술(색상 이름 등).
9. Figures — 개별 파일 업로드(figure당 1개, 멀티패널은 하나로 합쳐 업로드). **≥300dpi, RGB color**, Arial/Helvetica 서체(8pt 최종 인쇄 크기 기준), 허용 포맷: .ai/.eps/.pdf/.ps/.svg(벡터), .psd/.tif(레이어), .psd/.tif/.png/.jpg(비트맵), .ppt/.pptx(완전 편집 가능 시), .cdx(화학구조). 적록 대비 지양·색맹 안전 팔레트 권장. Video figure: 개별 ≤150MB, 전체 ≤1GB.
10. Copyright/disclosure/APC — **Data Availability Statement 필수**(Methods 뒤·References 앞, "Data Availability" 헤딩). Code availability는 central한 custom code 있을 시 필수. **Author Contributions statement 필수**(이니셜 기준, 전 콘텐츠 타입). **Competing Interests statement 필수**(없어도 선언). Accept 후 **Licence to Publish 서명 + APC 납부**: Original Research **£3,090/$4,290/€3,390**; Comment/Brief Communication/Perspective/Review **£1,210/$1,735/€1,375** (2026-07-23 기준, VAT/현지세 별도). Open access 라이선스: **CC BY-NC-ND 또는 CC BY** 선택(저자가 저작권 보유). 저소득국 교신저자는 APC waiver/discount 가능(제출 시점에만 신청 가능, accept 후 불가). LLM(ChatGPT 등)은 저자 자격 불충족 — 사용 시 Methods에 명시 필수.

**기타 참고:** ISSN 2398-6352(online only, 인쇄본 없음). Peer review 대상 콘텐츠: Article/Brief Communication/Case Report/Comment/Matters Arising/Meeting Report/Perspective/Protocol/Resource/Review(전형적으로 2–3인 리뷰어). Reporting guideline 준수 권장/의무: RCT는 **CONSORT 체크리스트 필수**(Article/Brief Communication 모두), 동물실험은 ARRIVE Essential 10 권장, 그 외 STROBE/PRISMA/CARE/SPIRIT/COREQ/SRQR/STARD/TRIPOD/CHEERS 등 EQUATOR Network 가이드라인 권장. Nature Portfolio Reporting Summary + Editorial Policy Checklist는 peer review 통과 후(revision 단계) 제출.

---

## NLM 공식 약어 빠른 참조

| 저널 | NLM 약어 | 특이사항 |
|------|---------|---------|
| The Spine Journal | Spine J | bracket [N] 인용; ≤6 전원+et al (✅ 원문 PDF 확정); affiliation=위첨자 문자(숫자 아님); ORCID 확정 부재; CRediT 필수; 저자변경 매우 엄격 |
| Spine | Spine (Phila Pa 1976) | NLM 색인명은 (Phila Pa 1976); 원고 reference list는 'Spine'만(저널 자체 예시), evidence.md/DB엔 (Phila Pa 1976); ≤3 전원, 4+면 첫 3+et al |
| Bone and Joint Journal | Bone Joint J | Vol-B(issue) 형식; ✅ **author cutoff 최종 확정(실증조사, 2026-07-24): 7명+면 첫3명+et al.**(이전 "전원 나열" 오류 정정 — byline 예시 오인이었음); ICMJE COI는 표준양식(BJJ 커스텀 아님, ✅ 확인); 저자명/학위/번호매김/교신저자연락처는 재탐색해도 규정 자체 없음 확정 |
| Journal of Bone & Joint Surgery (Am) | J Bone Joint Surg Am | ✅ 전저자 나열(공식 확인; ⚠️ 타 저널과 반대); hyphen 축약 pages; vol에 -A 미사용; 본문 2,500 words; 저자수상한 없음(확정); figure DPI 현재판 재확인=300/1200ppi |
| Neurospine | Neurospine | ≤3 전원+et al (✅ 공식 재확인) |
| Journal of Neurosurgery: Spine | J Neurosurg Spine | AMA style; **≤6 전원, 7+면 첫 3+et al (2026-07-09 수정 — 이전 "3명 이후" 오류)** |
| Global Spine Journal | Global Spine J | AMA 기반; **≤6 전원, 7+면 첫 3+et al (2026-07-09 수정)**; Case Report 더이상 접수 안함; 그룹저자=SAGE 공통정책 적용(title page 강조); 저자수상한/word limit 규정 자체 없음(확정) |
| Clinical Orthopaedics and Related Research | Clin Orthop Relat Res | 🔴 **정정(2026-07-24): ≤6명 전원, 7+면 첫 3+et al.**(이전 "전원 나열" 오류); 대괄호 [N](위첨자 아님, 정정); DOI 불포함(포털 예시 기준; ⚠️ 재검토); **references는 알파벳순(첫 언급 순서 아님) — 유일한 예외 저널** |
| Asian Spine Journal | Asian Spine J | **≤6 전원, 7+면 첫 3+et al (2026-07-09 공식 확인 — 이전 "6명 이후" 수정)**; 공동1저자/공동교신저자 허용; 저자수상한/그룹저자/저자변경절차는 규정 자체 없음(확정) |
| European Spine Journal | Eur Spine J | ⚠️ Springer Basic; (Year) 괄호; 약어 마침표 X; en-dash; author cutoff 숫자 규정 없음(전저자 기본, et al 허용); 저자수상한 없음(Springer Nature 공식 확정); 그룹저자=consortium listing 허용(Springer 공통정책) |
| Journal of Medical Internet Research | J Med Internet Res | AMA 기반 numbered; author cutoff 숫자 규정 없음(고유식별자 DOI/PMID 필수가 핵심); **ORCID 전저자 필수**; CC BY 4.0 완전 OA(예외 없음); 🔴 **CRediT 미사용**(내러티브+이니셜만, 2026-07-24 정정); Author Contributions/Acknowledgments 둘 다 선택; title page=전체이름+학위+ORCID+소속; 교신저자=email+전화+전체주소 전부 필수; **저자수상한·line/page numbering은 끝내 확인 안 됨** |
| npj Digital Medicine | npj Digit Med | ✅ **≤5 전원, 6+면 첫 저자 1명만+et al (2026-07-23 공식 확인)**; article number(페이지 아님); single-anonymized peer review; ORCID 교신저자만 필수; CRediT 미요구(자유서술 Author Contributions); APC $4,290(Original)/$1,735(기타); CC BY-NC-ND 또는 CC BY |
| Scientific Reports | Sci Rep | Nature style (섹션 없음 — npj Digit Med와 동일 Nature reference style 참조) |
| Journal of the American Medical Informatics Association | J Am Med Inform Assoc | ✅ ≤3 전원+et al; OUP hybrid, APC/license 금액 미확인(재탐색해도); table은 본문 내 배치(별도 파일 아님); ORCID=교신저자만 권장; peer review blind유형 확정 부재 |

---

## 작성 시 체크리스트

- [ ] 저널 약어: NLM 기준 사용 (⚠️ 마침표 유무 — 포함: JBJS·TSJ·Neurospine·BJJ·CORR / 없음: Spine·ESJ·JAMIA·JMIR / npj는 약어 내부 마침표 "J. Cell Biol.")
- [ ] et al. 처리: 저널별 cutoff 확인 (3명? 6명? 전부?) — 2026-07-09 기준 정확한 cutoff는 각 저널 섹션 "Author cutoff" 줄 참조. ✅ **BJJ는 2026-07-24 실증조사로 최종 확정: 7명+면 첫3명+et al.**(이전 "전원 나열" 오류 — byline과 reference-citation 예시를 혼동했던 것으로 정정 완료)
- [ ] Page range: 저널별 상이 — en-dash+전체(TSJ own-paper·BJJ·Neurospine·ESJ) / hyphen+뒷자리 축약(JBJS·Spine·JAMIA) / hyphen+전체(CORR·npj 예시). 각 섹션 Verified example 우선
- [ ] Volume-Issue-Pages 형식: 저널별 상이 (Vol:pages vs Vol(issue):pages)
- [ ] DOI: 포함 여부 저널별 확인 (불포함: TSJ own-paper·CORR·JBJS·JAMIA / 포함: ESJ·BJJ·Neurospine·JNS Spine·GSJ·ASJ·npj / JMIR은 DOI·PMID 중 고유식별자 필수)
- [ ] Spine 저널명: "(Phila Pa 1976)" 포함 여부
- [ ] BJJ volume: "107-B(5)" 형식 (-B 사용) vs JBJS "106(22)" (-A 미사용) 혼동 주의
- [ ] ESJ: 연도 괄호 `(Year)` 위치 + 약어 마침표 없음 확인
- [ ] **CORR references는 알파벳순** — 다른 저널(첫 언급 순서)과 반대이니 반드시 확인
- [ ] **Submission Checklist** (각 저널 섹션 하단 참조): title page 필수항목(교신저자 주소/email/IRB/permission/acknowledgments), abstract 구조+word limit, key points 유무, 본문 word limit + line/page numbering, table/figure 파일형식+legend 위치, copyright/disclosure form 종류 — 저널마다 상이하니 제출 전 반드시 해당 섹션 재확인

---
