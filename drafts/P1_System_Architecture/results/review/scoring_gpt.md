# Scoring Log by GPT

## 사용 목적

이 문서는 `scoring_all_29_gpt.csv`에 입력한 점수의 근거를 문항별로 누적 기록하는 로그다.

기록 원칙:

- 각 문항마다 `B1`부터 `B4`까지 왜 그 점수를 줬는지 짧게 남긴다.
- `Best`와 `Worst`를 정한 이유를 문항 단위로 명확히 적는다.
- 이후 `DG-006` 이후 문항도 같은 형식으로 계속 추가한다.

권장 템플릿:

```md
## DG-XXX

- 질문:
- Best:
- Worst:

### B1
- 총점:
- 평가 이유:

### B2
- 총점:
- 평가 이유:

### B3
- 총점:
- 평가 이유:

### B4
- 총점:
- 평가 이유:

### 추가 메모
- 
```

## 파일 변경

- 기존 점수 파일명을 `scoring_all_29.csv`에서 `scoring_all_29_gpt.csv`로 변경함.

## DG-001

- 질문: 요추 척추관 협착증에서 `UBE vs 기존 TLIF`의 `ODI 개선` 및 `합병증 비교` 근거는?
- Best: `B4`
- Worst: `B3`

### B1
- 총점: `14/25`
- 평가 이유: 근거 부족을 정직하게 인정한 점은 좋았지만, retrieval 자체가 질문에 잘 맞지 않았다. `UBE vs TLIF` 직접 비교 근거가 거의 없고, ODI와 합병증의 head-to-head 비교를 실질적으로 제시하지 못했다.

### B2
- 총점: `18/25`
- 평가 이유: `meta-analysis`와 비교연구를 일부 활용해 `B1`보다 훨씬 질문에 가깝게 접근했다. 다만 `open TLIF` 직접 비교보다는 `MIS-TLIF`나 간접 근거가 중심이어서 완전한 답변은 아니었다.

### B3
- 총점: `11/25`
- 평가 이유: 겉보기에는 가장 풍부했지만, `Youn`, `Kim`, `Soliman`, `Adogwa` 등 인용의 검증 가능성이 매우 낮았다. ODI 개선폭과 합병증 수치를 구체적으로 제시했으나 현재 comparison 파일 안의 citation 체계와 연결되지 않아 hallucination 가능성이 높다고 판단했다.

### B4
- 총점: `19/25`
- 평가 이유: 직접 근거 부재를 분명히 밝히면서도, 관련성 있는 고수준 간접 근거를 가장 안정적으로 정리했다. `pubmed_XXXXX` 형식이라 검증 가능성도 높았다. 다만 여전히 질문 핵심인 `UBE vs conventional open TLIF` 직접 비교는 부족했다.

### 추가 메모
- 이 문항은 전체적으로 retrieval mismatch가 심했다.
- `B4 best`는 강한 직접 근거가 있어서가 아니라, 제한점을 가장 정확히 인정하면서도 가장 덜 무리한 결론을 냈기 때문이다.

## DG-002

- 질문: `2-level cervical disc disease`에서 `CDR vs ACDF`의 `adjacent segment degeneration` 비교 근거는?
- Best: `B3`
- Worst: `B1`

### B1
- 총점: `10/25`
- 평가 이유: 대부분의 검색 결과가 질문과 직접 관련이 없는 cervical 수술 일반 논문이었다. 실제로 중요한 `CDR vs ACDF ASD` 비교 근거를 거의 잡지 못했고, 답변도 "자료 없음" 수준에 머물렀다.

### B2
- 총점: `14/25`
- 평가 이유: `network meta-analysis` 등 고수준 논문은 포함했지만, 실제 질문과 맞는 `2-level CDR vs ACDF ASD` 직접 근거는 여전히 부족했다. `noncontiguous ACDF`, `return-to-work` 같은 주변 주제가 섞여 있어 질문 적합성이 떨어졌다.

### B3
- 총점: `15/25`
- 평가 이유: 네 답변 중 유일하게 `symptomatic ASD`, `radiographic ASD`, `2-level subgroup limitation`을 나눠 설명하면서 질문 자체에는 가장 직접적으로 답했다. mixed cohort와 post-hoc 자료를 쓴 한계, 저자-연도 citation의 낮은 검증성 때문에 높은 점수는 아니지만, 상대평가상 가장 쓸 수 있는 답변이었다.

### B4
- 총점: `12/25`
- 평가 이유: citation 형식은 가장 안정적이었지만, 실제 답변은 대부분 `근거 부족` 선언에 머물렀다. 게다가 질문과 무관한 `lumbar laminectomy` 논문까지 포함되어 retrieval 품질 자체가 좋지 않았다.

### 추가 메모
- `B3 best`는 절대평가상 우수라기보다, 다른 답변들이 질문을 더 못 맞춘 결과다.
- 이 문항에서 `R4`와 `질문 적합성`의 균형이 특히 어려웠다.

## DG-003

- 질문: `MIS-TLIF` 후 `cage subsidence`의 위험인자와 임상 결과에 대한 영향은?
- Best: `B4`
- Worst: `B1`

### B1
- 총점: `10/25`
- 평가 이유: 검색 결과 대부분이 `subsidence`와 무관한 주제였다. 질문의 핵심인 위험인자, 임상영향, TLIF 맥락을 거의 설명하지 못했다.

### B2
- 총점: `16/25`
- 평가 이유: `bone quality`, `EBQ`, `cage design` 등 위험인자 축은 어느 정도 정리했다. 하지만 `OLIF`, biomechanical study, 간접 자료 비중이 크고, `MIS-TLIF` 직접 근거와 환자 임상 outcome 연결은 약했다.

### B3
- 총점: `15/25`
- 평가 이유: 위험인자와 임상영향을 가장 넓게 다뤘고 실제 읽는 입장에서는 정보량이 많았다. 그러나 제시된 수치와 저자-연도 citation의 검증성이 매우 낮아 `R4`에서 크게 감점했다.

### B4
- 총점: `17/25`
- 평가 이유: `bone quality`, `fixation`, `endplate preparation`처럼 핵심 위험인자 축을 상대적으로 잘 잡았고 citation 검증도 가능했다. 다만 `OLIF`, `BMP`, `stand-alone approach` 등 질문 바깥 자료가 섞여 정확성과 포괄성에서 한계가 있었다.

### 추가 메모
- 이 문항은 네 답변 모두 `MIS-TLIF direct evidence`가 충분하지 않았다.
- `B4 best`는 근거의 검증 가능성과 구조화 덕분에 선택했다.

## DG-004

- 질문: 요추 추간판 탈출증 수술에서 `microdiscectomy vs endoscopic discectomy` 결과 비교 근거는?
- Best: `B2`
- Worst: `B1`

### B1
- 총점: `10/25`
- 평가 이유: retrieval 적합도가 매우 낮았다. `fusion`, 일반 lumbar surgery, 비관련 주제가 많이 섞였고, 결국 직접 비교 근거를 거의 제시하지 못했다.

### B2
- 총점: `22/25`
- 평가 이유: `pubmed_41666862`, `pubmed_34213864`, `pubmed_41482265` 등 질문과 직접 맞닿는 비교 문헌을 실제로 사용했다. `primary herniation`에서는 대체로 동등, `perioperative outcome`은 endoscopic 유리, `recurrent case`에서는 microdiscectomy가 더 나을 수 있다는 식으로 가장 균형 있게 정리했다.

### B3
- 총점: `15/25`
- 평가 이유: 설명은 자연스럽고 개론 정리도 나쁘지 않았다. 하지만 `Katayama`, `Yeung`, `Hwa`, `Ruan`, `Jasper` 등 citation의 즉시 검증이 어렵고, 수치가 많을수록 오히려 hallucination 위험이 커 보였다.

### B4
- 총점: `21/25`
- 평가 이유: 고수준 근거를 많이 가져왔고 전반적인 구조도 좋았다. 다만 `stenosis`, `laminectomy`, `fixation` 계열 논문까지 섞이면서 질문 초점이 일부 흐려졌고, `PED preferred approach`처럼 결론이 다소 과감했다.

### 추가 메모
- `B2`와 `B4`의 차이는 크지 않았다.
- 최종적으로는 `질문 적합성`과 `결론의 절제` 측면에서 `B2`를 더 높게 봤다.

## DG-005

- 질문: 요추 추체간 유합술에서 `BMP-2` 사용의 `유합률`, `합병증`, `암 위험` 근거는?
- Best: `B4`
- Worst: `B3`

### B1
- 총점: `15/25`
- 평가 이유: 관련 BMP-2 논문은 일부 포함했지만, 수치와 outcome synthesis가 부족했다. 특히 `fusion`, `complication`, `cancer risk` 세 축을 통합적으로 정리하는 데 실패했다.

### B2
- 총점: `21/25`
- 평가 이유: fusion 향상과 합병증 이슈를 비교적 잘 요약했고, 관련 systematic review와 cohort를 두루 사용했다. 다만 `cancer risk`는 실질 근거 제시보다 "자료 없음"에 가깝고, procedure-specific 정리는 `B4`보다 덜 정교했다.

### B3
- 총점: `14/25`
- 평가 이유: 가장 포괄적으로 보였지만 `Friedlaender`, `Reuben`, `Burkus`, `Carragee`, FDA 적응증 기술 등에서 세부 사실과 citation 매칭 오류 가능성이 컸다. 정보량은 많아도 검증성에서 크게 밀렸다.

### B4
- 총점: `22/25`
- 평가 이유: procedure-specific fusion effect와 complication meta-analysis를 가장 구조적으로 제시했다. `cancer risk`에 대해서도 억지 결론을 내지 않고 `insufficient`로 제한한 점이 좋았다. citation 형식도 가장 안정적이었다.

### 추가 메모
- 이 문항은 `B2`와 `B4`가 모두 강했다.
- 최종적으로는 `B4`가 가장 구조적이고, 질문의 세 outcome domain을 가장 잘 반영했다.

## 다음 문항 추가용 섹션

아래부터는 같은 형식으로 계속 추가:

## DG-006

- 질문:
- Best:
- Worst:

### B1
- 총점:
- 평가 이유:

### B2
- 총점:
- 평가 이유:

### B3
- 총점:
- 평가 이유:

### B4
- 총점:
- 평가 이유:

### 추가 메모
- 
