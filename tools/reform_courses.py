"""One-off edit: apply the author's trend-based course reforms to the report source (syllabi, final section) and the
final-proposal roadmap. Idempotent: re-running leaves already-reformed text unchanged."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "report_source.html"
RM = ROOT / "data" / "roadmaps.json"
t = SRC.read_text(encoding="utf-8")


def syl(old_name, new_name, meta, goal, rows):
    global t
    m = re.search(rf'<div class="syl"><h3>{re.escape(old_name)}</h3>.*?</table></div>', t, re.S)
    if not m:
        m = re.search(rf'<div class="syl"><h3>{re.escape(new_name)}</h3>.*?</table></div>', t, re.S)
    assert m, old_name
    body = "".join(f"<tr><td>{w}</td><td>{html.escape(c)}</td></tr>" for w, c in rows)
    new = (f'<div class="syl"><h3>{new_name}</h3><div class="syl-meta">{html.escape(meta)}</div><p class="syl-goal">{html.escape(goal)}</p>'
           f'<table class="syl-t"><thead><tr><th>주차</th><th>내용</th></tr></thead><tbody>{body}</tbody></table></div>')
    t = t[:m.start()] + new + t[m.end():]


syl("실험계획 및 실습", "실험계획과 인과추론",
    "3학년 2학기 · 전공선택 · 선수: 선형대수학 1, 회귀분석 및 실습 · 교재·근거: Montgomery, Design and Analysis of Experiments; Hernán & Robins, Causal Inference: What If; Kohavi 외, Trustworthy Online Controlled Experiments (개편은 작성자 제안)",
    "실험의 설계와 분석을 인과추론의 틀에서 익히고, 무작위 실험에서 관찰연구와 온라인 실험까지 인과효과를 식별·추정하는 방법을 다룬다.",
    [("1", "실험의 원리(무작위화, 반복, 블록화), 잠재적 결과와 인과효과"),
     ("2", "무작위화 추론: 순열검정, Fisher·Neyman 관점, 두 표본과 대응비교"),
     ("3–4", "일원배치 분산분석: 모형, 기대평균제곱, 모형 적합성 검토, 사후비교"),
     ("5", "확률화 완전블록설계, 라틴방격"),
     ("6–7", "요인설계, 2^k 요인설계와 교락"),
     ("9", "변량효과·혼합모형 개관 (지분·분할구설계는 축약)"),
     ("10", "온라인 실험: A/B 테스트, 분산감소, 순차검정, 간섭 (신설 단원)"),
     ("11", "관찰연구의 식별: 인과 그래프(DAG), 교란과 백도어 기준 (신설 단원)"),
     ("12", "성향점수: 매칭, 역확률가중, 이중강건 추정 (신설 단원)"),
     ("13", "도구변수, 이중차분 (신설 단원)"),
     ("14", "민감도 분석과 종합")])
syl("시계열분석 및 실습", "시계열 분석과 예측",
    "4학년 1학기 · 전공선택 · 선수: 회귀분석 및 실습, 수리통계 2 · 교재·근거: 시계열분석 교재(작성자 보유 PDF), Hyndman & Athanasopoulos, Forecasting: Principles and Practice (개편은 작성자 제안)",
    "ARIMA·상태공간 모형의 이론과 함께 확률예측, 예측평가, 다수 시계열의 기계학습 예측을 익힌다.",
    [("1", "시계열 자료, 추세·계절 분해, 지수평활"),
     ("2", "확률과정, 정상성, 자기상관·부분자기상관함수"),
     ("3–4", "자기회귀과정, 이동평균과정, 자기회귀이동평균과정"),
     ("5", "비정상 시계열: 정상화, 단위근 검정, ARIMA"),
     ("6–7", "ARIMA 적합: 식별, 최대가능도 추정, 진단"),
     ("9", "예측: 최소평균제곱오차 예측, 예측구간"),
     ("10", "상태공간모형과 칼만 필터"),
     ("11", "확률예측과 예측평가: proper scoring rule, 시계열 교차검증 (신설 단원)"),
     ("12", "다수 시계열의 기계학습 예측: 전역 모형, 그래디언트 부스팅 (신설 단원)"),
     ("13", "변화점 탐지 (신설 단원)"),
     ("14", "벡터자기회귀, Granger 인과, 공적분 개관")])
syl("표본설계 및 조사실습", "표본조사와 자료통합",
    "2학년 1학기 · 전공선택 · 선수: 통계학 · 교재·근거: 작성자 렉노, NASEM(2023) Toward a 21st Century National Data Infrastructure (개편은 작성자 제안)",
    "확률표본 이론을 바탕으로 비확률표본 보정, 행정자료 결합, 소지역추정, 공개제한까지 현대 공식통계의 자료 생산 방법을 익힌다.",
    [("1", "조사자료 수집, 조사오차의 원천"),
     ("2–3", "단순임의추출: 평균·총계·비율의 추정, 표본크기"),
     ("4", "층화임의추출과 표본 배분"),
     ("5", "비추정과 회귀추정"),
     ("6", "계통추출, 집락추출, 확률비례추출"),
     ("7", "이단추출, 무응답과 가중치 보정"),
     ("9", "비확률표본과 보정: 사후층화, 갈퀴 가중, 성향점수 가중 (신설 단원)"),
     ("10", "행정자료·빅데이터와 조사 자료의 결합 (신설 단원)"),
     ("11", "소지역추정 (신설 단원)"),
     ("12", "공개제한: 범주 통합과 억제, 차분 프라이버시, 합성데이터 (신설 단원)"),
     ("13–14", "조사 실습 결과 발표")])
syl("통계적 기계학습", "통계적 기계학습",
    "4학년 1학기 · 전공선택 · 선수: 선형대수학 1, 수리통계 2, 해석개론 1·2 (강한 권장) · 데이터마이닝 (약한 권장) · 교재·근거: 김지수 교수 강의 페이지(2026년 1학기) 일정, Hastie 외 ESL, Mohri 외",
    "통계적 학습 방법의 원리와 이론(커널, 집중부등식, 미니맥스)을 대학원 진입 수준으로 익힌다. 내용을 낮추지 않고 선수와 복습 자료로 진입 장벽을 낮춘다.",
    [("1–2", "통계적 학습 개관, 확률 복습, 지도학습 개관"),
     ("3–4", "선형분류기, 해석학 복습(노름공간, 내적공간, 수렴)"),
     ("5–6", "축소추정의 이론 (방법과 실습은 데이터마이닝을 전제로 축약)"),
     ("7", "기저 확장과 커널 방법"),
     ("9", "앙상블 방법"),
     ("10", "모형 평가와 선택"),
     ("11–12", "재생핵 힐베르트 공간과 표현정리"),
     ("13–14", "측도의 집중: 집중부등식, 라데마허 복잡도와 일반화 한계"),
     ("15", "미니맥스 이론, 고차원 함수추정, 딥러닝 입문"),
     ("과제", "증명형·구현형 과제 중 비중 선택")])

ROWS = [("<tr><td>14</td><td>신뢰구간과 신뢰띠</td></tr>", "<tr><td>14</td><td>신뢰구간과 신뢰띠, 컨포멀 예측과 분포무관 예측구간 (신설 단원)</td></tr>"),
        ("<tr><td>14</td><td>모형 선택과 진단</td></tr>", "<tr><td>14</td><td>모형 선택과 진단, 베이즈 워크플로(사전·사후예측 점검), 변분추론 개관 (보강)</td></tr>"),
        ("<tr><td>12</td><td>변수선택: 탐색 방법과 선택 기준</td></tr>", "<tr><td>12</td><td>변수선택: 탐색 방법과 선택 기준, 선택 후 추론의 문제 (보강)</td></tr><tr><td>과제</td><td>소규모 통계 글쓰기 과제 3–5회 (보강)</td></tr>"),
        ("<tr><td>6</td><td>tibble, 자료 불러오기, tidy data</td></tr>", "<tr><td>6</td><td>tibble, 자료 불러오기, tidy data, SQL로 데이터베이스 다루기 (보강)</td></tr>"),
        ("<tr><td>9</td><td>불확실성 정량화: 예측구간, 컨포멀 예측</td></tr>", "<tr><td>9</td><td>불확실성 정량화: 예측구간, 컨포멀 예측, 예측기반추론(PPI)</td></tr>")]
for a, b in ROWS:
    if b not in t:
        assert a in t, a
        t = t.replace(a, b)
t = re.sub(r"(<tr><td>14</td><td>AI 코딩 도구의 활용과 검증: 생성된 분석 코드의 오류 찾기, 재현성 점검)( \(보강\))(</td></tr>)",
           r"\1, 데이터 윤리 모듈(프라이버시, 공정성, ASA 윤리지침)\2\3", t)

PARA = ('<p><b>최신 연구 동향 반영.</b> 강좌 수를 늘리지 않고 세 과목을 개편·개칭한다. 실험계획 및 실습은 \'실험계획과 인과추론\', 시계열분석 및 실습은 \'시계열 분석과 예측\', '
        '표본설계 및 조사실습은 \'표본조사와 자료통합\'이 된다. 컨포멀 예측(비모수통계), 다중검정·선택 후 추론(수리통계 2·회귀분석), 베이즈 워크플로(베이즈통계), '
        '재현성·SQL·데이터 윤리(전산통계)는 기존 과목의 단원으로 넣는다. 근거와 판단은 <a href="programs.html#p-courses">프로그램·제도 페이지</a>에 정리했다.</p>\n')
if "<b>최신 연구 동향 반영.</b>" not in t:
    anchor = "<p><b>전공필수.</b>"
    assert anchor in t
    t = t.replace(anchor, PARA + anchor, 1)
SRC.write_text(t, encoding="utf-8")

d = json.loads(RM.read_text(encoding="utf-8"))
for u in d:
    if u["id"] != "snu-proposal":
        continue
    for c in u["courses"]:
        if c["id"] == "p_doe":
            c.update(name_ko="실험계획과 인과추론", code="개편: 인과추론·A/B 테스트")
        if c["id"] == "p_ts":
            c.update(name_ko="시계열 분석과 예측", code="개편: 예측 중심")
        if c["id"] == "p_samp":
            c.update(name_ko="표본조사와 자료통합", code="개편, 2-2에서 옮김")
        if c["id"] == "p_np":
            c["code"] = "컨포멀 예측 단원 추가"
        if c["id"] == "p_sml":
            c["code"] = "이론 유지, 해석개론 강한 권장"
            if "p_an2" not in c["prereqs"]:
                c["prereqs"].append("p_an2")
        if c["id"] == "p_bayes":
            c["code"] = "베이즈 워크플로 추가"
    u["notes"] = [n for n in u["notes"] if not n.startswith("최신 연구 동향")] + [
        "최신 연구 동향을 반영해 세 과목을 개편·개칭했다(실험계획과 인과추론, 시계열 분석과 예측, 표본조사와 자료통합). 통계적 기계학습은 이론 내용을 유지하고 해석개론 2를 강한 권장 선수로 둔다."]
RM.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("reformed")
