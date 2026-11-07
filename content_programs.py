"""Content of programs.html: non-course programs and institutional systems, evidence, research trends, and the author's
own proposals (course reforms and programs). Data in data/: programs.json (17 universities), snu_programs.json (SNU audit),
lit.json (verified studies and guidelines), trends.json (2019–2026 research trends).
"""
import json
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"


def load(name, default):
    p = DATA / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


PROGS = load("programs.json", {"programs": []})["programs"]
LIT = {i["id"]: i for i in load("lit.json", {"items": []})["items"]}
TRENDS = load("trends.json", {"trends": [], "declining": [], "reports": [], "jobs": []})
SNU = load("snu_programs.json", {"items": [], "not_found": []})

CAT = {"research": "학부 연구", "reading_program": "지도 읽기 모임(DRP)", "honors_thesis": "우등 졸업·졸업논문",
       "combined_degree": "학·석사 연계", "consulting_practicum": "통계 상담 실습", "industry_capstone": "산학 캡스톤",
       "industry_placement": "인턴십·현장실습", "peer_teaching": "학부 조교·튜터링·연습반", "mentoring_advising": "동료 상담·멘토링",
       "career": "진로 지원", "competition": "경진대회", "community": "학생 공동체", "seminar": "학부 세미나",
       "writing_communication": "글쓰기·발표", "interdisciplinary_major": "연계·연합전공", "other": "기타"}
ORDER = ["research", "reading_program", "honors_thesis", "combined_degree", "peer_teaching", "seminar",
         "writing_communication", "mentoring_advising", "consulting_practicum", "industry_capstone", "industry_placement",
         "competition", "career", "community", "other"]
UNI_KO = {"Stanford": "Stanford", "UC Berkeley": "UC Berkeley", "Harvard": "Harvard", "University of Chicago": "Chicago",
          "University of Pennsylvania": "Penn", "Carnegie Mellon": "CMU", "Duke": "Duke", "University of Michigan": "Michigan",
          "University of Washington": "Washington", "Columbia": "Columbia", "Yale": "Yale", "University of Oxford": "Oxford",
          "University of Cambridge": "Cambridge", "ETH Zürich": "ETH Zürich", "University of Toronto": "Toronto",
          "연세대학교": "연세대", "고려대학교": "고려대"}
UNI_ORDER = list(UNI_KO)


def short(u):
    return UNI_KO.get(u, u)


def link(url):
    return url if url.startswith("http") else "https://doi.org/" + url


def cite(esc, *ids):
    """(Surname 외, 2014; …) with each item linked to its DOI/URL."""
    out = []
    for i in ids:
        it = LIT[i]
        first = it["authors"].split(";")[0].split(",")[0].strip()
        if not any("가" <= ch <= "힣" for ch in first) and ";" in it["authors"]:
            first += " 외"
        out.append(f'<a href="{esc(link(it["doi_or_url"]))}" target="_blank" rel="noopener">{esc(first)}, {it["year"]}</a>')
    return '<span class="cite">(' + "; ".join(out) + ")</span>"


# ---------------------------------------------------------------- tables built from data
def case_table(esc):
    by = defaultdict(lambda: defaultdict(list))
    for p in PROGS:
        by[p["category"]][p["university"]].append(p)
    rows = []
    for c in ORDER:
        if c not in by:
            continue
        unis = [u for u in UNI_ORDER if u in by[c]]

        def nm(p, u):
            n = p["program_name"].split(" (")[0]
            s = short(u)
            return n[len(s):].strip(" -—") if n.startswith(s + " ") else n
        ex = " · ".join(f'{esc(short(u))} <a href="{esc(by[c][u][0]["url"])}" target="_blank" rel="noopener">{esc(nm(by[c][u][0], u))}</a>'
                        for u in unis[:4])
        rows.append(f'<tr><td>{CAT[c]}</td><td class="num">{len(unis)}</td><td>{ex}</td></tr>')
    return ('<div class="table-wrap"><table><thead><tr><th scope="col">유형</th><th scope="col" class="num">대학 수</th>'
            '<th scope="col">대표 사례</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")


def full_list(esc):
    by = defaultdict(list)
    for p in PROGS:
        by[p["university"]].append(p)
    out = []
    for u in UNI_ORDER:
        if u not in by:
            continue
        items = sorted(by[u], key=lambda p: ORDER.index(p["category"]) if p["category"] in ORDER else 99)
        rows = "".join(f'<tr><td>{CAT.get(p["category"], p["category"])}</td><td><a href="{esc(p["url"])}" target="_blank" rel="noopener">'
                       f'{esc(p["program_name"])}</a>{"" if p["verified"] else " <span class=\"pill\">미확인</span>"}</td>'
                       f'<td>{esc(p["description"])}</td></tr>' for p in items)
        out.append(f'<details class="plist"><summary>{esc(short(u))} <span class="muted small">{len(items)}개</span></summary>'
                   '<div class="table-wrap"><table><thead><tr><th scope="col">유형</th><th scope="col">이름</th><th scope="col">내용</th>'
                   f'</tr></thead><tbody>{rows}</tbody></table></div></details>')
    return "".join(out)


# SNU status: (what, state, note) — from data/snu_programs.json (official pages read 2026-11-07)
SNU_STATUS = [
    ("학부 연구 (학점 과목)", "no", "학부 이수규정에 연구·독립연구·캡스톤 과목이 없다. 공대는 '공학연구의 실습 1·2'(1학점)로 학부 연구를 학점화하고 있다."),
    ("학부 연구 (비학점 인턴십)", "yes", "자연대 학부생연구인턴십 통계학과 배정 2026학년도 상반기 17명(+LX 2명), 하반기 12명(+LX 1명). 장려금 60–90만 원, 학점 없음."),
    ("졸업논문", "part", "학사 졸업논문(18쪽 이상, 표절검사) 제출이 졸업 요건이나 학점, 지도교수 배정, 심사 절차는 공개 자료에서 확인되지 않는다."),
    ("학·석사 연계", "yes", "자연대 학사·석사 연계과정으로 통계학과가 선발(2027 전기 4명). 학부 재학 중 대학원 과목 12학점까지 이수 가능."),
    ("전공 피어튜터링", "yes", "학부대학 피어튜터링의 전공 분과로 매 학기 운영(예: 수리통계 2). 학부 조교(UTA) 선발 공지는 확인되지 않는다."),
    ("지도 읽기 모임(DRP)", "no", "학과·단과대 차원의 운영이 확인되지 않는다."),
    ("학부 세미나", "no", "학과세미나는 대학원 교과목이며 학부생 대상 안내·학점이 없다."),
    ("통계 상담 실습", "part", "대학원 '통계상담 및 실습'(3학점)만 있고 학부 과목·참여 제도는 없다."),
    ("인턴십 학점 인정", "no", "학과 이수규정에 현장실습·인턴십 과목이 없다. 대학 경력개발센터 기준은 로그인 문제로 확인하지 못했다."),
    ("동료 상담·졸업생 멘토링·진로 행사", "no", "학과 주관 프로그램이 확인되지 않는다(취업정보 게시판만 운영)."),
    ("교과인증과정", "yes", "'데이터 애널리틱스'·'데이터 컴퓨팅'(각 12학점). 데이터 애널리틱스는 자료분석 및 실습, 자료분석 심화방법론 및 실습을 포함한다."),
]
PILL = {"yes": '<span class="pill yes">있음</span>', "no": '<span class="pill no">없음</span>', "part": '<span class="pill part">부분</span>'}


def snu_table(esc):
    rows = "".join(f"<tr><td>{esc(a)}</td><td>{PILL[s]}</td><td>{esc(n)}</td></tr>" for a, s, n in SNU_STATUS)
    return ('<div class="table-wrap"><table><thead><tr><th scope="col">제도</th><th scope="col">현황</th><th scope="col">내용</th></tr></thead>'
            f"<tbody>{rows}</tbody></table></div>")


# evidence table: (topic, finding in my words, lit ids)
EVIDENCE = [
    ("학부 연구", "학부 연구 참여는 STEM 대학원 진학 계획 확률을 약 15%p 높였다(성향점수 분석). 주 10시간 이상, 두 학기 이상 참여했을 때만 학위 취득·과학 진로 효과가 뚜렷했고 한 번 참여로는 효과가 없었다.", ("UR06", "UR10", "UR03", "UR11")),
    ("멘토링 구조", "대학원생 멘토만으로도 성과가 있지만, 학부생·대학원생·교수가 서로 직접 소통하는 구조에서 성과가 가장 컸다. 멘토링은 의도적으로 설계해야 한다.", ("MA06", "MA08", "MA07")),
    ("능동학습·소그룹", "STEM 225개 연구 메타분석에서 능동학습은 시험 성적을 0.47 SD 높이고 낙제 위험을 크게 줄였다. 대학 통계 과목의 협동 소그룹 학습 효과크기는 0.60이었다.", ("AL01", "AL08", "AL07")),
    ("학습조교·동료주도학습", "관문 과목에서 학습조교(LA) 지원을 받은 학생은 이후 관문 과목 낙제 승산이 55–63% 낮았다. 보충수업(SI)의 성적 효과는 d=0.29–0.60이었다.", ("PT02", "PT06", "PT05")),
    ("국내 튜터링", "국내 대학 동료 튜터링에서 튜터·튜티 모두 학업성취와 메타인지가 향상되었다. 다만 이중차분으로 보면 비교과 효과가 사전-사후 비교보다 작을 수 있다.", ("KR02", "KR03", "KR05")),
    ("인턴십", "가상 이력서 무작위 발송 실험에서 인턴십 경험은 면접 요청률을 12.6–14% 높였고, 의무 인턴십의 임금 수익은 약 6%였다. 국내 대졸자 자료에서도 정규직 취업 확률을 높였다.", ("IN01", "IN02", "IN03", "KR04")),
    ("동료 멘토·코칭", "여성 동료 멘토를 무작위 배정한 실험에서 소속감과 전공 유지가 입학 2년 후까지 개선되었고, 개별 학생 코칭은 재학 유지율을 높였다.", ("PT08", "MA02")),
    ("컨설팅·캡스톤", "실제 의뢰인 프로젝트를 다루는 학부 통계 컨설팅 과목에서 학생들은 수업 범위를 넘는 실제 자료 문제를 멘토링 아래 해결했다. 컨설팅 역할극은 통계적 사고와 문제해결을 개선했다.", ("CC03", "CC02", "CC04")),
    ("글쓰기·소통", "회귀 과목에 소규모 글쓰기 프로젝트를 넣자 글쓰기 태도가 개선되었고, 생성형 AI 시대에도 글쓰기는 통계적 추론을 기르는 수단으로 강조된다.", ("CM03", "CM04", "CM02")),
    ("윤리·재현성", "윤리를 입문부터 캡스톤까지 이식형 모듈로 넣는 방식과 R Markdown·Git을 통계 과목 학습목표로 넣는 방식이 실제 학과에서 운영되었다.", ("ET01", "RP01", "RP03")),
    ("교육과정 지침", "ASA(2014)와 NASEM(2018)은 실제 자료, 계산·재현성, 소통·협업, 윤리, 연구·인턴십·캡스톤 경험을 학부 과정 전반에 넣으라고 권고했다.", ("SD01", "SD07", "SD06")),
]


def evidence_table(esc):
    rows = "".join(f"<tr><td>{esc(t)}</td><td>{esc(f)} {cite(esc, *ids)}</td></tr>" for t, f, ids in EVIDENCE)
    return ('<div class="table-wrap"><table><thead><tr><th scope="col">주제</th><th scope="col">근거</th></tr></thead>'
            f"<tbody>{rows}</tbody></table></div>")


# my decision per trend (keyed by the English area name in trends.json)
DECIDE = {
    "Causal inference": "실험계획을 '실험계획과 인과추론'으로 개편",
    "Conformal prediction": "비모수통계에 컨포멀 예측 단원, 고급데이터마이닝에 보정·예측구간",
    "Statistical machine learning theory": "통계적 기계학습의 이론(RKHS·집중부등식·미니맥스) 유지",
    "Generative AI": "딥러닝의 통계적 이해·고급데이터마이닝의 단원으로 반영, 신설 과목은 두지 않음",
    "AI-assisted data analysis": "전산통계·실습 과목의 평가를 'AI 산출물 검증·해석' 중심으로 조정",
    "Reproducibility": "수리통계 2·회귀분석에 다중검정·선택 후 추론, 전 실습 과목에 재현 가능한 작업 흐름",
    "Data science computing": "전산통계 보강(SQL·Git·윤리 모듈), 윤리·소통은 과목 단원과 세미나로",
    "High-dimensional": "데이터마이닝·통계적 기계학습에서 다룸, 대학원 과목과 연결",
    "Bayesian computation": "베이즈통계에 베이즈 워크플로·변분추론 추가",
    "Differential privacy": "표본조사 과목의 '공개제한' 단원으로",
    "Online experimentation": "'실험계획과 인과추론'에 A/B 테스트·순차검정 단원",
    "Reinforcement learning": "독립 과목 없음, 실험계획(밴딧 개관)과 타 학과 과목 인정",
    "Forecasting": "시계열분석을 '시계열 분석과 예측'으로 개편",
    "Complex data": "독립 과목 없음, 자율 연구·DRP 주제로",
    "Optimal transport": "학부 과목 없음, DRP 주제나 대학원 과목으로",
    "Survey and official statistics": "표본설계를 '표본조사와 자료통합'으로 개편",
}
STRENGTH = {"strong": '<span class="pill yes">강함</span>', "moderate": '<span class="pill part">중간</span>', "weak": '<span class="pill">약함</span>'}


def trend_table(esc):
    rows = []
    for t in TRENDS["trends"]:
        dec = next((v for k, v in DECIDE.items() if t["area"].startswith(k)), "—")
        src = t["sources"][0]
        rows.append(f'<tr><td>{esc(t["area_ko"])}</td><td>{STRENGTH.get(t["strength"], "")}</td>'
                    f'<td>{esc(t["signal_ko"])} <span class="cite">(<a href="{esc(link(src["url_or_doi"]))}" target="_blank" rel="noopener">출처</a>)</span></td>'
                    f"<td>{esc(dec)}</td></tr>")
    return ('<div class="table-wrap"><table class="wide-table"><thead><tr><th scope="col">분야</th><th scope="col">신호</th>'
            '<th scope="col">근거</th><th scope="col">작성자 판단</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")


def refs(esc):
    used = sorted({i for _, _, ids in EVIDENCE for i in ids} | {"HIP01", "HIP02", "SD04", "SD05", "MA05"})
    items = "".join(f'<li>{esc(LIT[i]["authors"])} ({LIT[i]["year"]}). {esc(LIT[i]["title"])}. <i>{esc(LIT[i]["venue"])}</i>. '
                    f'<a href="{esc(link(LIT[i]["doi_or_url"]))}" target="_blank" rel="noopener">{esc(LIT[i]["doi_or_url"])}</a></li>'
                    for i in used if i in LIT)
    reps = "".join(f'<li>{esc(r["org"])} ({r["year"]}). {esc(r["title"])}. <a href="{esc(r["url"])}" target="_blank" rel="noopener">{esc(r["url"])}</a></li>'
                   for r in TRENDS["reports"][:10])
    return (f'<h3>효과 연구·교육과정 지침</h3><ol class="small">{items}</ol>'
            f'<h3>연구 동향 보고서</h3><ol class="small">{reps}</ol>'
            '<p class="small muted">모든 문헌은 조사 시점(2026년 11월)에 출판사 페이지나 DOI로 확인했다. 연구 동향의 논문 수는 arXiv·OpenAlex 제목 검색 결과이며, 각 행의 출처 링크에서 같은 검색을 다시 볼 수 있다.</p>')


# ---------------------------------------------------------------- prose (author's judgement)
def proposals(esc):
    C = lambda *ids: cite(esc, *ids)
    P = []

    def card(title, prio, what, cases, ev, cost):
        P.append(f'<div class="prop"><h3>{title} <span class="pill {"yes" if prio == "1순위" else "part" if prio == "2순위" else ""}">{prio}</span></h3>'
                 f'<dl class="deflist"><div><dt>무엇을</dt><dd>{what}</dd></div><div><dt>사례</dt><dd>{cases}</dd></div>'
                 f'<div><dt>근거</dt><dd>{ev}</dd></div><div><dt>운영·부담</dt><dd>{cost}</dd></div></dl></div>')

    card("학부 연구의 학점화와 발표회", "1순위",
         "통계학 자율 연구 1·2(같은 과목, 반복 수강)를 개설해 이미 있는 자연대 학부생연구인턴십과 함께 수행하면 장려금과 학점을 함께 받게 한다. 해마다 한 번 학과 학부연구 발표회를 연다.",
         "Berkeley 통계학과 학부연구 멘토십(대학원생 멘토, 학기말 포스터), Michigan URPS, Oxford·Cambridge 여름 연구와 발표회, 국내 공대 '공학연구의 실습 1·2'.",
         f"참여 효과는 기간에 비례했다. 주 10시간 이상, 두 학기 이상 연구한 학생에서만 학위·진로 효과가 뚜렷했다 {C('UR10', 'UR03')}. 같은 과목을 두 번 들을 수 있게 한 구조가 이 결과와 맞는다. 대학원 진학 계획 효과는 약 15%p였다 {C('UR06')}.",
         "인턴십 선발 인원(학기 12–19명)이 이미 있어 추가 예산은 발표회 정도다. 지도는 연구실 단위로 이루어진다.")
    card("지도 읽기 모임(Directed Reading Program)", "1순위",
         "박사과정생 멘토 1명과 학부생 1–2명이 한 학기 동안 주 1회 만나 한 주제의 교재·논문을 읽고, 학기말에 10분 발표와 짧은 보고서를 낸다. 주제는 측도론적 확률, 고차원 통계, 인과추론 이론, 최적수송 입문처럼 학부 과목이 다루지 않는 이론 주제를 우선한다. 주제마다 지도교수 1명이 후원해 학부생·대학원생·교수가 함께 만나는 구조로 둔다.",
         "Washington 통계학과 DRP(1학점, 분기말 발표), Chicago 수학과 DRP(전국 DRP의 원형), ETH Reading Course, Toronto STA496/497.",
         f"대학원생 멘토만으로도 성과가 있지만, 세 주체가 모두 직접 소통할 때 '과학자처럼 생각하기' 이득이 가장 컸다 {C('MA06')}. 멘토 연수로 부정적 멘토링 유형을 예방해야 한다 {C('MA07', 'MA08')}.",
         "교수 부담이 가장 작은 제도다. 학점은 학생자율연구(2학점)나 무학점으로 시작할 수 있고, 멘토 박사과정생에게 소액 활동비를 준다.")
    card("핵심 이론 과목의 연습반과 학부 조교", "1순위",
         "확률의 개념 및 응용, 수리통계 1·2, 회귀분석에 주 1회 소그룹 연습반을 둔다. 대학원생 조교와, 그 과목을 우수하게 이수한 학부 조교(UTA)가 함께 진행한다. 조교는 학기 초 교수법 교육을 받는다. 지금의 전공 피어튜터링을 이 구조로 확대한다.",
         "Oxford 튜토리얼(교원 1명당 학생 2–3명), Cambridge supervision, ETH 연습반과 학생 조교 의무 교육, CMU·Duke·Columbia 학부 조교, Toronto 상설 학습지원센터.",
         f"능동학습은 시험 성적을 0.47 SD 높였고 {C('AL01')}, 대학 통계 과목의 협동 소그룹 효과크기는 0.60이었다 {C('AL08')}. 학습조교 지원은 이후 관문 과목 낙제를 크게 줄였다 {C('PT02')}.",
         "조교 인건비가 필요하다. 다만 이론 중심 학과의 핵심 과목 학습에 직접 작용해 효과 대비 비용이 가장 분명하다.")
    card("이론 우등 경로와 졸업논문 정비", "2순위",
         "학과 우등 졸업을 두 경로로 신설한다. 연구 경로는 통계학 자율 연구 두 학기와 논문 심사·발표, 이론 경로는 대학원 과목 2개 이상(예: 통계이론 1)과 해석개론 1·2 이수다. 지금의 졸업논문(18쪽, 학점·지도 미확인)은 지도교수를 지정하고, 자율 연구·고급데이터마이닝 보고서로 대신할 수 있게 정비한다.",
         "Harvard(논문 또는 대학원 과목 포함 심화 과목 경로), Washington(대학원 과목 시퀀스 또는 논문), Michigan 우등(실해석 필수), Duke·Chicago 우등 논문.",
         "우등 제도 자체의 효과를 검증한 연구는 찾지 못했다. 다만 우등 경로가 학생을 학부 연구와 대학원 과목으로 이끄는 통로가 되고, 그 활동들은 근거가 있다.",
         "행정 규정 정비가 중심이고 추가 강좌는 없다. 졸업논문 지도 부담은 자율 연구 지도와 합쳐 줄인다.")
    card("학부 세미나 (1학점, P/F)", "2순위",
         "학과세미나를 학부생에게 열고, 이를 듣고 짧은 요약을 쓰는 1학점 과목을 둔다. 학기 후반에는 학생이 논문 한 편을 골라 발표한다. 글쓰기지원센터의 전공 연계 지도(SNU-WAC)와 묶어 통계적 글쓰기를 훈련한다.",
         "Columbia 학부 세미나(UN1202, 1학점), ETH 학사 세미나와 수학적 글쓰기(필수), Toronto STA492.",
         f"ASA 지침은 소통 훈련을 기술 교육과 직접 연결해 자주 제공하라고 권고했다 {C('SD01')}. 글쓰기는 통계적 추론을 기르는 수단이다 {C('CM04', 'CM03')}.",
         "기존 학과세미나를 쓰므로 부담이 작다. 교수 1명이 학기마다 맡는다(강좌 수에는 넣지 않는 1학점 세미나).")
    card("학·석사 연계 활성화와 대학원 과목 안내", "2순위",
         "이미 있는 학·석사 연계과정과 대학원 과목 수강 허용을 '이론 경로 로드맵'으로 묶어 안내한다. 4학년에 들을 대학원 과목(통계이론 1, 확률론 등)과 선수 조건을 학과 홈페이지에 명시하고 학기마다 설명회를 연다.",
         "Stanford coterm, Harvard AB/AM, Chicago BX/MS, Columbia 4+1, Michigan AMDP, Cambridge Part III.",
         "제도는 이미 있으므로 정보 접근성이 관건이다. HIP를 '제공'하는 것만으로는 성과가 오르지 않고 참여 보장이 중요하다는 분석이 있다 " + C("HIP03") + ".",
         "안내 자료와 설명회 정도의 부담이다.")
    card("동료 상담·졸업생 멘토링·진로 간담회", "3순위",
         "3·4학년 동료 상담가(peer advisor)가 정해진 시간에 수강 계획, 연구, 대학원·취업 상담을 맡는다. 학기마다 졸업생 진로 간담회를 연다.",
         "Stanford·Berkeley·Michigan·Harvard 동료 상담, Toronto 졸업생 멘토링, 고려대 교우회 '2인 3각'.",
         f"동료 멘토 무작위 배정 실험에서 소속감과 전공 유지가 2년 뒤까지 개선되었다 {C('PT08')}. 다만 멘토링 연구 전반은 정의와 방법이 일관되지 않아 근거가 약하다 {C('MA03', 'MA04')}.",
         "학생 근로 장학금 수준의 부담이다.")
    card("인턴십 학점 인정", "3순위",
         "통계 업무가 중심인 인턴십을 사전 승인받으면 1–2학점(P/F, 성찰 보고서)으로 인정한다. 학과 과목으로 두되 강의는 없다.",
         "Washington STAT 497(일정 조건이면 캡스톤 대체), 고려대 현장실습학기제·글로벌통계실무교육인턴십.",
         f"이력서 감사 실험에서 인턴십 경험은 면접 요청률을 12.6–14% 높였고 {C('IN01', 'IN02')}, 국내 대졸자 자료에서도 정규직 취업 확률을 높였다 {C('KR04')}.",
         "보고서 확인 수준의 행정 부담이다.")
    card("학부생의 통계 상담 참여", "3순위",
         "대학원 '통계상담 및 실습'에 학부 4학년이 보조 상담원으로 참여할 수 있게 한다. 대학원생 상담원과 짝을 이루어 실제 의뢰를 맡는다.",
         "Columbia 학부 통계상담 실습(UN2109), Toronto STA490.",
         f"실제 의뢰인 프로젝트는 학부생도 멘토링 아래 수행할 수 있었다 {C('CC03')}. 협업 역량은 별도로 가르쳐야 한다 {C('CC07')}.",
         "기존 대학원 과목에 정원만 더한다.")
    card("교과인증과정 '데이터 애널리틱스' 재편", "필수 후속",
         "폐지하는 자료분석 및 실습, 자료분석 심화 방법론 및 실습 대신 데이터마이닝 방법 및 실습, 고급데이터마이닝, 통계계산으로 구성을 바꾼다.",
         "—", "과목 폐지에 따른 행정 조정이다.", "규정 개정만 필요하다.")
    return "".join(P)


COURSE_CHANGES = [
    ("실험계획 및 실습", "개편·개칭", "실험계획과 인과추론",
     "고전 요인설계·블록설계는 유지하되 라틴방격·지분·분할구 일부를 줄인다. 잠재적 결과, 무작위화 추론, 관찰연구(성향점수·도구변수·이중차분), 온라인 A/B 테스트와 순차검정을 넣는다.",
     "인과추론은 가장 강한 성장 분야이고(2021 노벨경제학상, arXiv 'causal' 2.6배) ASA·NSF가 핵심 전문성으로 꼽았다. 강좌 수를 늘리지 않으려 독립 과목 대신 실험계획과 합친다."),
    ("시계열분석 및 실습", "개편·개칭", "시계열 분석과 예측",
     "ARIMA·상태공간 이론은 유지하고 확률예측과 예측평가(scoring rule), 변화점 탐지, 다수 시계열의 기계학습 예측을 넣는다.",
     "M5 대회에서 LightGBM 기반 방법이 우승했고 'time series forecasting' 논문이 7.6배 늘었다. 고전 시계열만으로는 실무 예측을 대표하기 어렵다."),
    ("표본설계 및 조사실습", "개편·개칭", "표본조사와 자료통합",
     "확률표본 이론은 유지하고 비확률표본 보정, 행정자료 결합, 소지역추정, 공개제한(차분 프라이버시·합성데이터)을 넣는다.",
     "NASEM(2023)과 국내 국가데이터처 출범(2025)이 조사와 행정자료의 결합을 공식통계의 방향으로 제시했다. 'survey sampling'은 정체, 'small area estimation'은 성장했다."),
    ("비모수통계 및 실습", "단원 추가", "(이름 유지)",
     "부트스트랩 뒤에 컨포멀 예측과 분포무관 예측구간 단원을 둔다.",
     "컨포멀 예측은 arXiv 기준 9.2배 늘었고 COPSS 회장상 사유에 두 번 포함되었다. 분포무관 추론이라는 비모수통계의 주제와 자연스럽게 이어진다."),
    ("통계적 기계학습", "이론 유지", "(이름 유지)",
     "RKHS, 집중부등식, 미니맥스를 학부 수준으로 낮추지 않고 유지한다. 해석개론 1·2를 강한 권장 선수로 두고 개강 전 복습 자료를 낸다.",
     "학습이론은 COPSS 회장상(2025·2026)이 나온 분야이고 서울대의 이론 지향과 맞는다. 앞서 후반부를 낮추자고 한 제안을 이 판단으로 바꾼다."),
    ("베이즈통계 및 실습", "단원 추가", "(이름 유지)",
     "MCMC에 더해 베이즈 워크플로(사전예측·사후예측 점검), 변분추론을 넣는다.",
     "MCMC 논문은 정체·감소하고 변분추론은 1.6배 늘었다. 계산 도구가 다변화되고 있다."),
    ("수리통계 2 · 회귀분석 및 실습", "단원 추가", "(이름 유지)",
     "수리통계 2에 다중검정·FDR, 회귀분석에 변수선택 후 추론의 문제와 소규모 글쓰기 과제를 넣는다.",
     "재현성·선택적 추론은 COPSS 회장상 2020·2021·2023의 사유였다. 회귀 과목 글쓰기 과제의 효과가 보고되었다."),
    ("전산통계 및 실험", "단원 추가", "(이름 유지)",
     "Quarto·Git 재현 가능한 작업 흐름, SQL 기초, 데이터 윤리 모듈, AI가 만든 분석 코드의 검증 과제를 넣는다.",
     "NASEM(2018)·ASA(2014)가 재현성·데이터 관리·윤리를 학부 핵심 역량으로 꼽았다. AI 시대 데이터과학 교육은 'AI 분석의 평가·관리'로 옮겨 간다는 분석이 있다."),
    ("고급데이터마이닝", "단원 추가", "(이름 유지)",
     "예측구간·확률 보정에 더해 예측기반추론(PPI)과 모형 평가의 통계적 설계를 넣는다.",
     "RSS(2026)와 PPI 연구(Science 2023)가 AI 평가에 통계적 틀을 요구했다."),
    ("생성형 AI·강화학습·최적수송·복잡자료", "신설하지 않음", "—",
     "독립 과목을 두지 않고 기존 과목의 단원, 자율 연구와 DRP 주제, 타 학과 과목 인정으로 다룬다.",
     "연구 중심이 CS 쪽에 있거나(강화학습·차분 프라이버시의 arXiv stat 비중 감소) 학부 수준을 넘는다(최적수송). 교수 수 제약도 고려했다."),
]


def course_table(esc):
    rows = "".join(f"<tr><td>{esc(a)}</td><td>{esc(k)}</td><td>{esc(n)}</td><td>{esc(w)}</td><td>{esc(y)}</td></tr>"
                   for a, k, n, w, y in COURSE_CHANGES)
    return ('<div class="table-wrap"><table class="wide-table"><thead><tr><th scope="col">과목</th><th scope="col">판단</th>'
            '<th scope="col">새 이름</th><th scope="col">무엇을</th><th scope="col">이유</th></tr></thead>'
            f"<tbody>{rows}</tbody></table></div>")


OPINION = [
    ("자료분석 및 실습·자료분석 심화 방법론 폐지", "동의", "목차 대부분이 전산통계·데이터마이닝·회귀분석과 겹친다. 다만 교과인증과정 재편이 함께 필요하다."),
    ("수리통계(부전공용) 폐지", "동의", "수리통계 1과 같은 내용이다."),
    ("고급통계이론을 두지 않음", "동의", "4학년이 대학원 통계이론 1을 들을 수 있다. 수리통계 2에 결정이론·지수족을 보완하는 편이 비용 대비 낫다."),
    ("통계적 기계학습 후반부 하향 조정", "철회", "앞서 작성자가 제안했던 안이다. 이론 중심 학과라면 RKHS·집중부등식·미니맥스를 유지하고 선수와 복습 장치로 진입 장벽만 낮추는 편이 맞다고 판단을 바꾼다."),
    ("통계학 자율 연구 1·2", "동의, 보완", "같은 과목 반복 수강 구조는 '두 학기 이상' 효과 근거와 맞는다. 기존 자연대 인턴십과 연결하고 발표회를 더하자."),
    ("고급데이터마이닝 팀 프로젝트", "동의, 보완", "프로젝트에 불확실성 정량화와 AI 평가(PPI)를 넣자."),
    ("전공필수 5과목 유지", "동의", "필수를 늘리면 강좌당 수강 인원이 늘어 교수 부담이 커진다. 통계적 기계학습 필수화 제안(연구 동향 보고)도 같은 이유로 따르지 않는다."),
    ("측도론 필수화 여부", "비필수 유지", "해외 15곳 중 ETH만 필수다. 대신 DRP와 우등 이론 경로로 수학적 심화를 원하는 학생에게 길을 열어 준다."),
]


def opinion_table(esc):
    rows = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td></tr>" for a, b, c in OPINION)
    return ('<div class="table-wrap"><table><thead><tr><th scope="col">앞선 결정</th><th scope="col">작성자 판단</th><th scope="col">이유</th>'
            f"</tr></thead><tbody>{rows}</tbody></table></div>")


SUMMARY_P = ("<p><strong>작성자 판단.</strong> 서울대 통계학과에 가장 부족한 것은 교과목보다 <strong>학부생이 연구와 이론을 깊게 경험하는 제도</strong>다. "
             "학부 연구는 비학점 인턴십으로만 있고, 지도 읽기 모임·학부 세미나·연습반·우등 경로가 없다. 조사한 17개 대학 중 16곳이 학부 연구 제도를, 13곳이 우등·졸업논문 제도를 두고 있다. "
             "효과 연구는 기간이 긴 학부 연구, 소그룹 능동학습, 학습조교의 효과를 일관되게 보여 준다.</p>"
             "<p>그래서 1순위로 학부 연구 학점화, 지도 읽기 모임, 핵심 이론 과목 연습반을 제안한다. 셋 다 이론 중심이라는 학과의 정체성을 강화하고 교수 부담이 작다. "
             "교과목은 강좌 수를 늘리지 않고 최신 연구 동향을 반영한다. 실험계획을 '실험계획과 인과추론'으로, 시계열을 '시계열 분석과 예측'으로, 표본설계를 '표본조사와 자료통합'으로 개편한다. "
             "컨포멀 예측, 다중검정, 베이즈 워크플로, 재현성은 기존 과목의 단원으로 넣는다.</p>")


def summary():
    return SUMMARY_P + '<p><a href="programs.html">프로그램·제도와 교과목 개편 전체 보기 →</a></p>'


def page(shell, esc):
    n_ver = sum(p["verified"] for p in PROGS)
    principles = ("<ol><li><strong>이론 중심 정체성.</strong> 서울대 통계학과는 이론 중심 통계학을 지향한다. 해외 사례 중에서도 이론 비중이 큰 Chicago·Oxford·Cambridge·Harvard를 더 무겁게 참고하고, 실무형 프로그램은 보조로 둔다.</li>"
                  "<li><strong>교수 수 제약.</strong> 통계학과 개설 강좌 수를 늘리지 않는다. 새 수요는 기존 과목 개편, 단원 추가, 대학원생 멘토·기존 제도 활용으로 채운다.</li>"
                  "<li><strong>근거 우선.</strong> 효과가 검증된 제도를 우선하고, 근거가 약한 제도는 그렇다고 밝힌다.</li></ol>"
                  "<p>앞서 요청받아 반영한 개편 방향은 참고로 두고, 판단이 다른 곳은 '작성자 의견' 절에 나란히 적었다.</p>")
    secs = [("p-summary", "요약", SUMMARY_P),
            ("p-principle", "판단 기준", principles),
            ("p-snu", "서울대 현황", "<p>통계학과·자연과학대학·대학 본부의 공식 페이지를 2026년 11월에 확인했다. 이미 있는 제도는 새로 제안하지 않고 연결·확대하는 방향으로 다룬다.</p>" + snu_table(esc)),
            ("p-cases", "해외·국내 사례: 유형별",
             f'<p>17개 대학의 학과·단과대·대학 단위 프로그램 {len(PROGS)}개를 유형별로 묶었다(공식 페이지에서 확인 {n_ver}개). '
             '대학 수는 그 유형을 하나 이상 운영하는 대학의 수다.</p>' + case_table(esc)),
            ("p-evidence", "효과 연구", "<p>검증된 문헌 98편 가운데 제안과 직접 관련된 것을 주제별로 정리했다. 근거의 강도는 무작위 실험·준실험이 가장 높고, 자기보고 설문과 사례 연구는 낮다.</p>" + evidence_table(esc)),
            ("p-trends", "최신 연구 동향 (2019–2026)",
             "<p>arXiv·OpenAlex 논문 수, COPSS 회장상 수상 사유, Annual Review of Statistics 목차, NSF·ASA·RSS 보고서로 연구 동향을 확인했다. "
             "강하게 성장하는 분야(인과추론, 컨포멀 예측·불확실성 정량화, 학습이론, 재현성·선택적 추론)는 모두 이론 집약적이어서 이론 중심 학과에 유리하다.</p>" + trend_table(esc)),
            ("p-programs", "제도·프로그램 제안", proposals(esc)),
            ("p-courses", "교과목 신설·개편·폐지",
             "<p>최종 제안 로드맵(20과목, 학기당 10과목)의 강좌 수를 유지한 채 연구 동향을 반영한다. 신설 과목은 두지 않고 세 과목을 개편·개칭하며, 나머지는 단원으로 넣는다. "
             "앞서 폐지한 세 과목(수리통계 부전공용, 자료분석 및 실습, 자료분석 심화 방법론)과 폐지된 통계적품질관리는 연구 동향으로도 뒷받침된다. 품질관리('control chart') 논문 수는 2019–2025년에 거의 늘지 않았다.</p>"
             + course_table(esc) + '<p class="small muted">개편 과목의 주차별 계획은 <a href="syllabi.html">강의계획서안</a>에 반영했다.</p>'),
            ("p-opinion", "작성자 의견: 앞선 결정과 비교", opinion_table(esc)),
            ("p-list", "대학별 프로그램 전체 목록", '<p class="small muted">대학 이름을 누르면 펼쳐진다. \'미확인\'은 공식 페이지에서 직접 확인하지 못한 항목이다.</p>' + full_list(esc)),
            ("p-refs", "참고문헌", refs(esc))]
    return shell("programs.html", "학생 역량 프로그램·제도", "프로그램·제도", "17개 대학 사례 · 효과 연구 · 연구 동향", "작성자 판단",
                 "학생 역량 프로그램·제도와 교과목 개편", "해외·국내 대학의 학생 역량 제도, 효과 연구, 최신 통계학 연구 동향을 바탕으로 서울대 통계학과에 필요한 제도와 교과목 개편을 제안합니다.",
                 [("조사 프로그램", f"{len(PROGS)}개"), ("검증 문헌", f"{len(LIT)}편"), ("연구 동향", f"{len(TRENDS['trends'])}개 분야")],
                 "1순위: 학부 연구 학점화 · 지도 읽기 모임 · 이론 과목 연습반", secs)
