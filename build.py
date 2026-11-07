"""Build the static site for the SNU Statistics curriculum-reform proposal.

Pages: index.html (summary and proposal), roadmaps.html (20 interactive roadmaps), programs.html (non-course
programs and institutional systems), syllabi.html (syllabus drafts). Text of the earlier report comes from
data/report_source.html; roadmap data from data/roadmaps.json; programs content from content_programs.py.
usage: python build.py
"""
import html
import json
import random
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SITE = Path(__file__).resolve().parent
sys.path.insert(0, str(SITE))
DATA = SITE / "data"
KST = timezone(timedelta(hours=9))
SRC = (DATA / "report_source.html").read_text(encoding="utf-8")
REPO = "https://github.com/Yu-Jusang/snu-stat-curriculum"

PAGES = [("index.html", "개편안"), ("roadmaps.html", "대학별 로드맵"), ("programs.html", "프로그램·제도"),
         ("syllabi.html", "강의계획서안")]


def esc(s):
    return html.escape(str(s))


def sec(n, sid, title, body):
    return (f'<section id="{sid}" aria-labelledby="{sid}-h"><div class="sec-head"><span class="n">{n:02d}</span>'
            f'<h2 id="{sid}-h">{title}</h2></div>\n{body}\n</section>')


def hero_art(seed=7):
    """Abstract eight-column roadmap: course boxes per semester joined by curves (drawn in currentColor)."""
    rnd = random.Random(seed)
    cols, w, h = 8, 600, 400
    parts, boxes = [], []
    for c in range(cols):
        x = 40 + c * 70
        for r in range(rnd.randint(2, 5)):
            y = 60 + r * 62 + rnd.randint(-8, 8)
            boxes.append((c, x, y))
            op = round(rnd.uniform(.25, .7), 2)
            parts.append(f'<rect x="{x}" y="{y}" width="46" height="24" rx="3" fill="none" stroke="currentColor" '
                         f'stroke-width="1.2" opacity="{op}"/>')
    for c, x, y in boxes:
        nxt = [b for b in boxes if b[0] == c + 1]
        for _, x2, y2 in rnd.sample(nxt, min(len(nxt), rnd.randint(0, 2))):
            dash = ' stroke-dasharray="4 3"' if rnd.random() < .5 else ""
            parts.append(f'<path d="M{x + 46} {y + 12} C{x + 58} {y + 12} {x2 - 12} {y2 + 12} {x2} {y2 + 12}" fill="none" '
                         f'stroke="currentColor" stroke-width="1" opacity=".35"{dash}/>')
    return (f'<div class="hero-art"><svg viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
            + "".join(parts) + "</svg></div>")


def shell(fname, title, crumb, eyebrow, status, h1, summary, metrics, note, secs, extra_head="", extra_tail=""):
    t = datetime.now(KST)
    toc = "".join(f'<li><a href="#{sid}"><span class="n">{i:02d}</span>{t_}</a></li>' for i, (sid, t_, _) in enumerate(secs, 1))
    body = "\n".join(sec(i, sid, t_, b) for i, (sid, t_, b) in enumerate(secs, 1))
    nav = "".join(f'<a href="{f}"{" aria-current=\"page\"" if f == fname else ""}>{n}</a>' for f, n in PAGES)
    mets = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in metrics)
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{esc(title)}</title>
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/jetbrains-mono@5.0.20/400.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/jetbrains-mono@5.0.20/500.css">
<link rel="stylesheet" href="assets/style.css">
<link rel="stylesheet" href="assets/site.css">
{extra_head}
</head>
<body data-project="curri">
<nav class="topbar" aria-label="주 메뉴"><div class="wrap wide"><a class="brand" href="./"><span class="mark" aria-hidden="true"></span><span class="brand-name">통계학과 커리큘럼 개편안</span></a><div class="nav-links">{nav}</div></div></nav>
<header class="hero">{hero_art()}<div class="wrap wide"><div class="hero-text"><nav class="crumbs" aria-label="경로"><span>서울대학교 통계학과</span><span aria-hidden="true"> / </span><span aria-current="page">{esc(crumb)}</span></nav><div class="meta-row"><p class="eyebrow">{esc(eyebrow)}</p><span class="status">{esc(status)}</span></div><h1>{esc(h1)}</h1><p class="summary">{summary}</p><dl class="metrics">{mets}</dl><p class="note">{note}</p></div></div></header>
<div class="wrap wide layout"><nav class="toc" aria-label="목차"><ol>{toc}</ol></nav><main class="content">
{body}
</main></div>
<footer class="wrap wide"><p class="small muted">학생 제안 자료 · 마지막 갱신 {t:%Y-%m-%d} · <a href="{REPO}">원본 저장소</a></p></footer>
{extra_tail}
</body>
</html>
"""


# ---------- fragments of the earlier report ----------
def frag(start, end):
    a = SRC.index(start)
    b = SRC.index(end, a + len(start)) if end else len(SRC)
    return SRC[a:b]


def clean(s, drop_heading=True):
    if drop_heading:
        s = re.sub(r"^\s*<h[23][^>]*>.*?</h[23]>", "", s, count=1, flags=re.S)
    s = re.sub(r'<div class="scroll"><table[^>]*>', '<div class="table-wrap"><table>', s)
    s = s.replace('<div class="prose">', "")
    s = re.sub(r'<(h3|p)( id="[^"]*")? style="[^"]*">', r"<\1\2>", s)
    s = re.sub(r"</div>\s*(?=<div class=\"table-wrap\">)", "", s)
    s = s.replace('href="#snu-proposal"', 'href="roadmaps.html#snu-proposal"')
    s = s.replace('href="#syllabi"', 'href="syllabi.html"')
    s = s.replace('<div class="toc" id="toc"></div>', "")
    # drop unmatched closing divs (left over from the report's prose wrappers)
    out, depth = [], 0
    for tok in re.split(r"(<div[^>]*>|</div>)", s):
        if tok.startswith("<div"):
            depth += 1
        elif tok == "</div>":
            if depth == 0:
                continue
            depth -= 1
        out.append(tok)
    return "".join(out).strip() + "</div>" * depth


def index_page(prog_summary):
    summary = clean(frag('<div class="callout">', '<h2 id="compare">'), drop_heading=False)
    compare = clean(frag('<h2 id="compare">', '<div class="prose"><h2 id="roadmaps">'))
    final = clean(frag('<h2 id="final">', '<h3 id="overlap"'))
    overlap = clean(frag('<h3 id="overlap"', '<h3 id="adv-theory"'))
    theory = clean(frag('<h3 id="adv-theory"', '<h2 id="proposal">'))
    proposal = clean(frag('<h2 id="proposal">', '<h2 id="method">'))
    method = clean(frag('<h2 id="method">', "<!--APPX-->"))
    compare = compare.replace("<table>", '<table class="wide-table">')
    secs = [("s-summary", "요약", summary),
            ("s-compare", "국내외 비교표", compare),
            ("s-final", "최종 커리큘럼 제안", final + '<p><a href="roadmaps.html#snu-proposal">최종 제안 로드맵 보기 →</a></p>'),
            ("s-overlap", "과목 간 중복 조정", overlap),
            ("s-theory", "이론 경로와 대학원 통계이론 1", theory),
            ("s-programs", "학생 역량 프로그램·제도", prog_summary),
            ("s-detail", "개편안 세부 제언", proposal),
            ("s-method", "조사 방법과 한계", method)]
    return shell("index.html", "통계학과 커리큘럼 개편안", "개편안", "학생 제안 · 국내외 17개 대학 비교", "제안",
                 "서울대 통계학과 커리큘럼 개편안",
                 "US News 통계학 Top 10과 해외·국내 대학의 학부 과정, 학생 역량 프로그램을 조사해 서울대 통계학과 로드맵과 제도 개편안을 정리했습니다.",
                 [("비교 대학", "17개"), ("제안 강의 과목", "20개"), ("전공필수", "5과목")],
                 "현행 로드맵 2025학년도 2학기 기준 · 화살표는 렉노·강의계획서·요람 근거", secs)


# ---------- roadmaps ----------
RM_JS = r"""
const DATA=__DATA__;
const TERMS=["Y1S1","Y1S2","Y2S1","Y2S2","Y3S1","Y3S2","Y4S1","Y4S2"];
const TERM_KO=t=>`${t[1]}학년 ${t[3]}학기`;
const LANES=[["core","통계 핵심","핵심"],["computing","전산·데이터","전산"],["applied","응용 통계","응용"],["ml","기계학습","ML"],["math","수학 (수리과학부 개설)","수학"],["capstone","연구·캡스톤","연구"]];
const W=136,H=54,G=30,VG=10,LG=22,LEFT=34,TOP=14,HEAD=30;
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
document.getElementById("legend").innerHTML=LANES.map(([k,l])=>`<span><i class="sw" style="border-color:var(--${k});background:var(--${k}-t)"></i>${l}</span>`).join("")+
 `<span><i class="sw" style="border-color:var(--applied);background:var(--surface)"></i>테두리만: 선택</span><span><i class="sw" style="border-color:var(--applied);background:var(--applied-t)"></i>채움: 필수</span><span><svg width="34" height="10"><path d="M2 5H30" stroke="var(--edge)" stroke-width="1.5"/></svg>공식 선수과목</span><span><svg width="34" height="10"><path d="M2 5H30" stroke="var(--text)" stroke-opacity=".7" stroke-width="1.5" stroke-dasharray="7 3"/></svg>강한 권장 (서울대)</span><span><svg width="34" height="10"><path d="M2 5H30" stroke="var(--edge)" stroke-width="1.4" stroke-dasharray="1.5 3.5"/></svg>약한 권장 (서울대)</span><span><svg width="34" height="10"><path d="M2 5H30" stroke="var(--edge)" stroke-width="1.5" stroke-dasharray="4 3"/></svg>추정 순서 (연세대·고려대)</span>`;
function render(u){
  const byLane={};LANES.forEach(([k])=>byLane[k]=TERMS.map(()=>[]));
  u.courses.forEach(c=>{const ln=byLane[c.category]?c.category:"applied";const ti=TERMS.indexOf(c.term);if(ti>=0)byLane[ln][ti].push(c)});
  const pos={};let y=TOP+HEAD+16;const lanesOut=[];
  LANES.forEach(([k,,label])=>{
    const n=Math.max(...byLane[k].map(a=>a.length));if(!n)return;
    lanesOut.push({label,y,h:n*(H+VG)-VG});
    byLane[k].forEach((arr,ti)=>arr.forEach((c,i)=>pos[c.id]={x:LEFT+ti*(W+G),y:y+i*(H+VG),c}));
    y+=n*(H+VG)-VG+LG;
  });
  const width=LEFT+8*W+7*G+14,height=y-LG+16;
  let h=`<div class="board" style="width:${width}px;height:${height}px">`;
  TERMS.forEach((t,i)=>h+=`<div class="term" style="left:${LEFT+i*(W+G)}px;top:${TOP}px;width:${W}px">${TERM_KO(t)}</div>`);
  lanesOut.forEach(l=>h+=`<div class="lane" style="top:${l.y}px;height:${l.h}px">${l.label}</div>`);
  const snu=u.id.startsWith("snu"),dash=!snu&&u.edge_style==="recommended";
  let paths="";
  u.courses.forEach(c=>(c.prereqs||[]).forEach(p=>{
    const a=pos[p],b=pos[c.id];if(!a||!b)return;
    let d;
    if(a.x===b.x){const x=a.x+W,y1=a.y+H/2,y2=b.y+H/2;d=`M${x} ${y1} C${x+16} ${y1} ${x+16} ${y2} ${x+2} ${y2}`}
    else if(a.x<b.x){const x1=a.x+W,y1=a.y+H/2,x2=b.x-2,y2=b.y+H/2,dx=Math.max(18,(x2-x1)*.5);d=`M${x1} ${y1} C${x1+dx} ${y1} ${x2-dx} ${y2} ${x2} ${y2}`}
    else{const x1=a.x,y1=a.y+H/2,x2=b.x+W+2,y2=b.y+H/2;d=`M${x1} ${y1} C${x1-30} ${y1} ${x2+30} ${y2} ${x2} ${y2}`}
    const cls=snu?((c.weak||[]).includes(p)?" weak":" strong"):(dash?" dash":"");
    paths+=`<path class="e${cls}" data-f="${esc(p)}" data-t="${esc(c.id)}" d="${d}" marker-end="url(#ah-${u.id})"/>`;
  }));
  h+=`<svg width="${width}" height="${height}"><defs><marker id="ah-${u.id}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8z" fill="var(--edge)"/></marker></defs>${paths}</svg>`;
  Object.values(pos).forEach(({x,y,c})=>{
    const k=byLane[c.category]?c.category:"applied";
    const title=[c.code,c.name,c.name_ko].filter(Boolean).join(" · ");
    h+=`<div class="c${c.required?"":" opt"}" tabindex="0" data-id="${esc(c.id)}" title="${esc(title)}" style="left:${x}px;top:${y}px;width:${W}px;height:${H}px;border-color:var(--${k});background:var(--${k}-t)"><span class="nm">${esc(c.name_ko||c.name)}</span>${c.code?`<span class="k">${esc(c.code)}</span>`:""}</div>`;
  });
  return h+"</div>";
}
const HOST={"서울대학교":"host-snu","미국 (US News 통계학 Top 10)":"host-us","미국 외 해외":"host-intl","국내":"host-kr"};
DATA.forEach(u=>{
  const host=document.getElementById(HOST[u.group]);
  const sec=document.createElement("div");sec.className="uni";sec.id=u.id;
  const head=`<div class="uni-head"><h3>${esc(u.name)}</h3><span class="prog">${esc(u.program)}</span>${u.rank?`<span class="rtag rank">${esc(u.rank)}</span>`:""}${u.prov?`<span class="rtag">${esc(u.prov)}</span>`:""}</div>`;
  const body=(u.total_requirements?`<p class="uni-req">${esc(u.total_requirements)}</p>`:"")+
   `<div class="rm-scroll">${render(u)}</div>`+
   (u.notes&&u.notes.length?`<ul class="uni-notes">${u.notes.map(n=>`<li>${esc(n)}</li>`).join("")}</ul>`:"")+
   (u.sources&&u.sources.length?`<p class="uni-src">출처: ${u.sources.map(s=>`<a href="${esc(s)}" target="_blank" rel="noopener">${esc(s.replace(/^https?:\/\//,""))}</a>`).join(" · ")}</p>`:"");
  sec.innerHTML=u.id.startsWith("snu")?head+body:`<details class="uni-d"><summary>${head}<span class="fold">로드맵 펼치기</span></summary>${body}</details>`;
  host.appendChild(sec);
  const board=sec.querySelector(".board"),edges=[...board.querySelectorAll("path.e")];
  const set=id=>{
    board.classList.add("focus");board.querySelectorAll(".c.on,path.e.on").forEach(e=>e.classList.remove("on"));
    const on=new Set([id]);
    edges.forEach(e=>{if(e.dataset.f===id||e.dataset.t===id){e.classList.add("on");on.add(e.dataset.f);on.add(e.dataset.t)}});
    board.querySelectorAll(".c").forEach(c=>{if(on.has(c.dataset.id))c.classList.add("on")});
  };
  const clear=()=>board.classList.remove("focus");
  board.querySelectorAll(".c").forEach(c=>{c.addEventListener("mouseenter",()=>set(c.dataset.id));c.addEventListener("focus",()=>set(c.dataset.id));c.addEventListener("mouseleave",clear);c.addEventListener("blur",clear)});
});
document.querySelectorAll(".uni-d").forEach(dt=>{const f=dt.querySelector(".fold");dt.addEventListener("toggle",()=>{f.textContent=dt.open?"로드맵 접기":"로드맵 펼치기"})});
const openTarget=()=>{const el=location.hash&&document.getElementById(location.hash.slice(1));const dt=el&&el.querySelector(".uni-d");if(dt&&!dt.open)dt.open=true;if(el)el.scrollIntoView()};
window.addEventListener("hashchange",openTarget);openTarget();
"""


def roadmaps_page():
    data = json.loads((DATA / "roadmaps.json").read_text(encoding="utf-8"))
    intro = ('<p>각 대학의 공식 요람·학과 안내를 바탕으로 8학기 격자에 과목을 배치했습니다. 과목에 마우스를 올리거나 '
             '탭하면 그 과목의 선수·후속 과목만 강조됩니다. 쿼터제·텀제 대학은 가장 가까운 학기 칸으로 옮겼습니다. '
             '서울대 로드맵은 펼쳐 두고, 다른 대학은 이름을 누르면 펼쳐집니다.</p>'
             '<p>서울대 로드맵의 화살표는 공식 선수과목이 아닙니다. <strong>강한 권장</strong>(굵은 점선)은 후속 과목의 핵심 내용이 '
             '직접 전제하는 관계로 사실상 선수이고, <strong>약한 권장</strong>(가는 점선)은 일부 단원에서만 쓰여 복습으로 보완할 수 있는 관계입니다. '
             '근거는 작성자가 정리한 각 과목 강의노트에서 실제로 쓰이는 개념과 담당 교수 강의 페이지·강의계획서의 선수 요건입니다.</p>'
             '<div class="rm-legend" id="legend"></div>')
    n_us = sum(u["group"].startswith("미국 (") for u in data)
    secs = [("s-legend", "읽는 법", intro),
            ("s-snu", "서울대학교 (현행·개편안·최종 제안)", '<div id="host-snu"></div>'),
            ("s-us", f"미국 · US News 통계학 Top 10 ({n_us}개교)", '<p class="small muted">US News 2026 Best Graduate Schools 통계학 순위. 공동 10위까지 포함.</p><div id="host-us"></div>'),
            ("s-intl", "미국 외 해외", '<div id="host-intl"></div>'),
            ("s-kr", "국내", '<div id="host-kr"></div>')]
    js = "<script>" + RM_JS.replace("__DATA__", json.dumps(data, ensure_ascii=False)) + "</script>"
    return shell("roadmaps.html", "대학별 전공 로드맵", "대학별 로드맵", "8학기 격자 · 선수과목 화살표", f"{len(data)}개 로드맵",
                 "대학별 전공 로드맵", "서울대 현행·개편안·최종 제안과 해외 15개, 국내 2개 대학의 통계 학부 과정을 같은 형식으로 비교합니다.",
                 [("로드맵", f"{len(data)}개"), ("해외 대학", "15개"), ("국내 대학", "2개")],
                 "과목에 마우스를 올리면 선수·후속 과목이 강조됩니다", secs, extra_tail=js)


# ---------- syllabi ----------
def syllabi_page():
    appx = frag("<!--APPX-->", "<!--/APPX-->")
    intro = re.search(r"<p>(.*?)</p>", appx, re.S).group(1)
    cards = re.findall(r'<div class="syl"><h3>(.*?)</h3><div class="syl-meta">(.*?)</div><p class="syl-goal">(.*?)</p>'
                       r'<table class="syl-t">(.*?)</table></div>', appx, re.S)
    groups = [("s-y12", "1·2학년", lambda m: m.startswith(("1학년", "2학년"))),
              ("s-y3", "3학년", lambda m: m.startswith("3학년")),
              ("s-y4", "4학년", lambda m: m.startswith("4학년")),
              ("s-res", "연구 과목 (매 학기)", lambda m: m.startswith("매 학기"))]
    secs = [("s-intro", "작성 기준", f"<p>{intro}</p>")]
    for sid, title, pred in groups:
        body = "".join(f'<div class="syl" id="c-{i}"><h3>{name}</h3><p class="syl-meta">{meta}</p><p class="syl-goal">{goal}</p>'
                       f'<div class="table-wrap"><table class="syl-t">{tbl}</table></div></div>'
                       for i, (name, meta, goal, tbl) in enumerate(cards) if pred(meta))
        secs.append((sid, title, body))
    return shell("syllabi.html", "강의계획서안", "강의계획서안", "최종 제안 로드맵의 통계학과 개설 과목", f"{len(cards)}과목",
                 "강의계획서안", "최종 제안의 통계학과 개설 과목 전부에 대한 주차별 강의계획서안입니다. 과목 간 중복 조정 결과를 반영했습니다.",
                 [("과목", f"{len(cards)}개"), ("강의 과목", "20개"), ("연구 과목", "2개")],
                 "실제 개설 시 담당 교수가 조정 · (이관)(보강)(보완) 표시는 작성자 제안", secs)


def programs_page():
    try:
        import content_programs as cp
    except ImportError:
        wait = '<p class="muted">해외·국내 대학의 학생 역량 프로그램·제도와 관련 연구, 최신 연구 동향을 조사하고 있습니다. 곧 이 페이지에 정리됩니다.</p>'
        page = shell("programs.html", "학생 역량 프로그램·제도", "프로그램·제도", "조사 중", "작성 중",
                     "학생 역량 프로그램·제도", "해외·국내 대학의 학부 연구, 멘토링, 실무 프로그램과 관련 연구를 바탕으로 서울대 통계학과에 필요한 제도를 제안합니다.",
                     [("상태", "조사 중")], "", [("s-wait", "작성 중", wait)])
        return page, wait
    return cp.page(shell, esc), cp.summary()


def build():
    prog_html, prog_summary = programs_page()
    out = {"index.html": index_page(prog_summary), "roadmaps.html": roadmaps_page(), "syllabi.html": syllabi_page()}
    if prog_html:
        out["programs.html"] = prog_html
    for f, s in out.items():
        (SITE / f).write_text(s, encoding="utf-8")
        print("built", f, len(s))


if __name__ == "__main__":
    build()
