# DOCX 변환 가이드

drafts/ 폴더의 섹션들을 학술 논문 DOCX 파일로 변환하는 규칙입니다.
python-docx를 사용하여 서식을 정밀하게 제어합니다.

---

## 파일 네이밍 규칙

모든 출력 파일에 **생성 날짜(YYMMDD)**를 붙입니다.

| 파일 | 예시 (2026-02-15 생성 시) |
|------|---------------------------|
| Title page | `output/title_page_260215.docx` |
| 본문 | `output/manuscript_260215.docx` |
| 테이블 | `output/table_1_260215.docx`, `output/table_2_260215.docx`, ... |

날짜는 Python `datetime.now().strftime('%y%m%d')` 로 생성.

---

## 출력 파일 구성

| 파일 | 내용 |
|------|------|
| `output/title_page_YYMMDD.docx` | 타이틀 페이지 (별도 파일) |
| `output/manuscript_YYMMDD.docx` | 본문 전체 (Abstract ~ Figure Legends, 테이블 제외) |
| `output/table_N_YYMMDD.docx` | 각 테이블 별도 파일 (table_1, table_2, ...) |

---

## 실행 순서

### 1단계: 드래프트 파일 스캔

- `drafts/` 폴더에서 번호 붙은 모든 섹션 파일 자동 탐지
- 패턴: `drafts/[0-9]*_*.md` (10번 이상도 포함, 숫자 순서로 정렬)
- `drafts/table_*.md` 파일은 별도 분리
- 누락된 핵심 섹션이 있으면 사용자에게 알림

**섹션 순서 예시** (프로젝트마다 다를 수 있음):

```text
01_title.md          → title_page_YYMMDD.docx (별도)
02_abstract.md       → manuscript_YYMMDD.docx에 포함 (첫 번째 섹션)
03_introduction.md   → manuscript_YYMMDD.docx에 포함
04_methods.md        → manuscript_YYMMDD.docx에 포함
05_results.md        → manuscript_YYMMDD.docx에 포함
06_discussion.md     → manuscript_YYMMDD.docx에 포함
07_conclusion.md     → manuscript_YYMMDD.docx에 포함
08_references.md     → manuscript_YYMMDD.docx에 포함
09_figure_legends.md → manuscript_YYMMDD.docx에 포함
10_appendix.md       → manuscript_YYMMDD.docx에 포함 (있으면)
...                  → 번호 순서대로 계속
table_1.md           → output/table_1_YYMMDD.docx (별도)
table_2.md           → output/table_2_YYMMDD.docx (별도)
```

### 2단계: Title Page 생성 (별도 파일)

`output/title_page_YYMMDD.docx`로 별도 생성:

- `drafts/01_title.md` 내용 사용
- 제목, 저자, 소속, 교신저자 정보
- 폰트: Times New Roman 10pt (제목은 더 크게 가능)
- 페이지 번호 없음

### 3단계: 본문 병합 → manuscript_YYMMDD.docx

Title(01)과 Table을 제외한 **모든 번호 섹션**을 하나의 DOCX로 병합.

#### 핵심 서식 규칙

**기본 설정:**

- 폰트: Times New Roman
- 본문 크기: **10pt**
- 줄간격: 더블스페이스 (2.0)
- 여백: 1인치 (2.54cm)
- 글씨 색상: 검정

**섹션 제목 (확장/축소 방지):**

- **Heading 스타일(Heading 1, 2, 3...)을 사용하지 않음**
- 섹션 제목은 Normal Paragraph + **Bold** 처리
- Word의 Heading 스타일 사용 시 ▷ 확장/축소 화살표가 생기므로 반드시 회피
- 하위 소제목: **Bold + Italic**

**Abstract 구조화 소제목:**

- Purpose, Methods, Results, Conclusion 등 소제목은 **Bold** 처리
- 소제목 뒤에 바로 내용이 이어지는 형태

**페이지 구분:**

- 각 섹션은 **새 페이지에서 시작** (Page Break 삽입)

**줄번호:**

- 전체 문서에 걸쳐 **연속 줄번호** (Continuous line numbering)

**페이지 번호:**

- 각 페이지 하단 중앙에 페이지 번호 표시

### 4단계: 테이블 생성 (각각 별도 파일)

`drafts/table_*.md` 파일마다 `output/table_N_YYMMDD.docx` 생성.

#### 테이블 서식 규칙 (Three-line table)

- **배경색 없음** (모든 셀 투명/흰색)
- **좌우 세로 구분선 없음**
- **가로선: 상단 + 헤더 하단 + 하단만**
- 폰트: Times New Roman 10pt
- 테이블 제목 (Table 1. xxx): 테이블 위에 Bold
- 테이블 하단 footnote: 일반 텍스트

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ← 상단 선
 Variable    Group A    Group B
────────────────────────────────   ← 헤더 하단 선
 Age         54.3±12.1  52.1±11.8
 Sex (M/F)   45/30      42/33
━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ← 하단 선
```

---

## Python 구현 참고 (python-docx)

### 필수 패키지

```bash
pip install python-docx
```

### 날짜 접미사

```python
from datetime import datetime
date_suffix = datetime.now().strftime('%y%m%d')  # e.g. '260215'
```

### 본문 DOCX 핵심 코드

```python
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# --- 기본 스타일 ---
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(10)
font.color.rgb = RGBColor(0, 0, 0)
style.paragraph_format.line_spacing = 2.0

# --- 여백 1인치 ---
for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

# --- 연속 줄번호 ---
for section in doc.sections:
    sectPr = section._sectPr
    lnNumType = OxmlElement('w:lnNumType')
    lnNumType.set(qn('w:countBy'), '1')
    lnNumType.set(qn('w:restart'), 'continuous')
    sectPr.append(lnNumType)

# --- 페이지 번호 (Footer 중앙) ---
for section in doc.sections:
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    run._element.append(fldChar1)
    run2 = p.add_run()
    instrText = OxmlElement('w:instrText')
    instrText.text = ' PAGE '
    run2._element.append(instrText)
    run3 = p.add_run()
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run3._element.append(fldChar2)

# --- 섹션 제목 (Heading 스타일 대신 Bold Normal) ---
def add_section_title(doc, title_text):
    p = doc.add_paragraph()
    run = p.add_run(title_text.upper())
    run.bold = True
    run.font.size = Pt(10)
    run.font.name = 'Times New Roman'

# --- 페이지 나누기 ---
def add_page_break(doc):
    doc.add_page_break()

# --- Abstract 구조화 소제목 ---
def add_abstract_subheading(doc, heading, content):
    p = doc.add_paragraph()
    run_h = p.add_run(heading + ': ')
    run_h.bold = True
    run_h.font.size = Pt(10)
    run_c = p.add_run(content)
    run_c.font.size = Pt(10)

# --- 저장 ---
doc.save(f'output/manuscript_{date_suffix}.docx')
```

### 테이블 DOCX 핵심 코드

```python
def set_three_line_table(table):
    """Three-line style: 상단, 헤더하단, 하단 선만"""
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement('w:tblPr')

    # 전체 border 제거
    borders = OxmlElement('w:tblBorders')
    for name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        b = OxmlElement(f'w:{name}')
        b.set(qn('w:val'), 'none')
        b.set(qn('w:sz'), '0')
        borders.append(b)
    tblPr.append(borders)

    # 셀별 border 설정
    for i, row in enumerate(table.rows):
        for cell in row.cells:
            tcPr = cell._element.get_or_add_tcPr()
            tcBorders = OxmlElement('w:tcBorders')

            if i == 0:  # 헤더
                top = OxmlElement('w:top')
                top.set(qn('w:val'), 'single')
                top.set(qn('w:sz'), '12')
                top.set(qn('w:color'), '000000')
                tcBorders.append(top)
                bottom = OxmlElement('w:bottom')
                bottom.set(qn('w:val'), 'single')
                bottom.set(qn('w:sz'), '6')
                bottom.set(qn('w:color'), '000000')
                tcBorders.append(bottom)
            elif i == len(table.rows) - 1:  # 마지막
                bottom = OxmlElement('w:bottom')
                bottom.set(qn('w:val'), 'single')
                bottom.set(qn('w:sz'), '12')
                bottom.set(qn('w:color'), '000000')
                tcBorders.append(bottom)

            for side in ['left', 'right']:
                s = OxmlElement(f'w:{side}')
                s.set(qn('w:val'), 'none')
                s.set(qn('w:sz'), '0')
                tcBorders.append(s)

            # 배경 제거
            shading = OxmlElement('w:shd')
            shading.set(qn('w:fill'), 'FFFFFF')
            shading.set(qn('w:val'), 'clear')
            tcPr.append(shading)
            tcPr.append(tcBorders)
```

---

## 서식 체크리스트

### Title Page (title_page_YYMMDD.docx)

- [ ] 별도 파일로 생성
- [ ] 제목, 저자, 소속, 교신저자 정보
- [ ] 파일명에 날짜 포함

### 본문 (manuscript_YYMMDD.docx)

- [ ] 폰트: Times New Roman **10pt**
- [ ] 줄간격: 2.0 (더블스페이스)
- [ ] 여백: 1인치
- [ ] 글씨 색상: 검정
- [ ] 섹션 제목: Bold (Heading 스타일 미사용 → 확장/축소 없음)
- [ ] 하위 제목: Bold + Italic
- [ ] Abstract 구조화 소제목: Bold
- [ ] 각 섹션: 새 페이지에서 시작
- [ ] 연속 줄번호
- [ ] 페이지 번호 (하단 중앙)
- [ ] 테이블 미포함
- [ ] 파일명에 날짜 포함

### 테이블 (table_N_YYMMDD.docx)

- [ ] 각 테이블 별도 파일
- [ ] 배경색 없음
- [ ] 좌우 세로 구분선 없음
- [ ] 가로선: 상단 + 헤더 하단 + 하단만 (Three-line)
- [ ] 폰트: Times New Roman 10pt
- [ ] 테이블 제목: Bold
- [ ] 파일명에 날짜 포함

---

## 주의사항

- `python-docx` 필요 (`pip install python-docx`)
- Markdown `#` 헤딩 → Bold Normal 텍스트로 변환 (Heading 스타일 사용 금지)
- `**bold**` → Bold, `*italic*` → Italic 변환
- 섹션 번호 10 이상도 숫자 순서로 정렬
- Figure는 `drafts/figures/` 이미지 참조
- 변환 전 `output/` 폴더 존재 확인
- 동일 날짜에 재생성 시 기존 파일 덮어쓰기
