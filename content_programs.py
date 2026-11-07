"""Content of programs.html: non-course programs and institutional systems, evidence, trends, and the author's proposals.
Data: data/programs.json (overseas/domestic programs), data/snu_programs.json (SNU audit), data/lit.json (studies),
data/trends.json (research trends). Prose sections live in this file.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"


def load(name, default):
    p = DATA / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


PROGS = load("programs.json", {"programs": []})["programs"]

CAT = {"research": "학부 연구", "reading_program": "지도 읽기 모임(DRP)", "honors_thesis": "우등 졸업·졸업논문",
       "combined_degree": "학·석사 연계", "consulting_practicum": "통계 상담 실습", "industry_capstone": "산학 캡스톤",
       "industry_placement": "인턴십·현장실습", "peer_teaching": "학부 조교·튜터링·연습반", "mentoring_advising": "동료 상담·멘토링",
       "career": "진로 지원", "competition": "경진대회", "community": "학생 공동체", "seminar": "학부 세미나",
       "writing_communication": "글쓰기·발표", "other": "기타"}
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


def case_table(esc):
    """One row per program type: how many of the 17 universities have it, and the named examples."""
    by = defaultdict(lambda: defaultdict(list))
    for p in PROGS:
        by[p["category"]][p["university"]].append(p)
    rows = []
    for c in ORDER:
        if c not in by:
            continue
        unis = [u for u in UNI_ORDER if u in by[c]]
        ex = " · ".join(f'{esc(short(u))} <a href="{esc(by[c][u][0]["url"])}" target="_blank" rel="noopener">{esc(by[c][u][0]["program_name"].split(" (")[0])}</a>'
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


def summary():
    return '<p>조사 중입니다.</p>'


def page(shell, esc):
    n_ver = sum(p["verified"] for p in PROGS)
    secs = [("p-cases", "해외·국내 사례: 유형별",
             f'<p>17개 대학의 학과·단과대·대학 단위 프로그램 {len(PROGS)}개를 유형별로 묶었습니다(공식 페이지에서 확인 {n_ver}개). '
             '대학 수는 그 유형을 하나 이상 운영하는 대학의 수입니다.</p>' + case_table(esc)),
            ("p-list", "대학별 프로그램 전체 목록", '<p class="small muted">대학 이름을 누르면 펼쳐집니다. \'미확인\'은 공식 페이지에서 직접 확인하지 못한 항목입니다.</p>' + full_list(esc))]
    return shell("programs.html", "학생 역량 프로그램·제도", "프로그램·제도", "17개 대학 사례 · 효과 연구 · 연구 동향", "작성 중",
                 "학생 역량 프로그램·제도", "해외·국내 대학의 학부 연구, 지도 읽기 모임, 학·석사 연계, 연습반 같은 제도와 관련 연구를 바탕으로 서울대 통계학과에 필요한 제도와 교과목 변화를 제안합니다.",
                 [("조사 프로그램", f"{len(PROGS)}개"), ("대학", "17개")], "작성 중인 페이지입니다", secs)
