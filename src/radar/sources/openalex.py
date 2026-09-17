from __future__ import annotations
from typing import Any
import re

from radar.models import IssueResult, Paper
from .common import SourceError, abstract_from_inverted, clean_text, date_after, extract_doi, http_get, normalize_url, unique_keep_order

SOURCE = "openalex"
API = "https://api.openalex.org/works"


def _looks_paratext(title: str) -> bool:
    t = re.sub(r"\s+", " ", (title or "").strip().lower())
    if not t:
        return True
    return bool(re.match(r"^(table of contents|editorial board|publication information|information for authors|front cover|back cover|index|contents|author index|subject index|erratum|corrigendum|publisher correction|editorial)\b", t))


def _date(w: dict[str, Any]) -> str:
    return clean_text(w.get("publication_date") or w.get("publication_year") or "")


def _keywords(w: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for k in (w.get("keywords") or []):
        if isinstance(k, dict):
            out.append(clean_text(k.get("display_name") or k.get("keyword") or ""))
        else:
            out.append(clean_text(k))
    for c in (w.get("concepts") or []):
        if isinstance(c, dict) and (c.get("score") or 0) >= 0.35:
            out.append(clean_text(c.get("display_name") or ""))
    return unique_keep_order([x for x in out if x])[:10]


def _authors(w: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for a in (w.get("authorships") or []):
        au = a.get("author") or {}
        name = clean_text(au.get("display_name") or "")
        if name:
            out.append(name)
    return unique_keep_order(out)


def _paper(w: dict[str, Any], issue_label: str, source: str = SOURCE) -> Paper:
    doi = clean_text(w.get("doi") or "").replace("https://doi.org/", "").replace("http://doi.org/", "")
    if not doi:
        doi = extract_doi(w.get("id") or "")
    landing = clean_text((w.get("primary_location") or {}).get("landing_page_url") or "")
    url = normalize_url("https://doi.org/", doi) if doi else landing
    return Paper(
        title=clean_text(w.get("title") or ""),
        authors=_authors(w),
        abstract=abstract_from_inverted(w.get("abstract_inverted_index")),
        keywords=_keywords(w),
        published=_date(w),
        url=url,
        doi=doi,
        issue=issue_label,
        source=source,
    )


def _key(w: dict[str, Any]) -> tuple[str, str]:
    b = w.get("biblio") or {}
    return clean_text(b.get("volume") or ""), clean_text(b.get("issue") or "")


def _label(vol: str, issue: str) -> str:
    if vol and issue:
        return f"{vol}({issue})"
    if vol:
        return vol
    return "latest"


def _request(ref: dict[str, Any], per_page: int = 50) -> list[dict[str, Any]]:
    issn = clean_text(ref.get("issn"))
    name = clean_text(ref.get("name") or issn)
    if not issn:
        raise SourceError(SOURCE, f"{name}: 缺少 ISSN，无法请求 OpenAlex", [])
    flt = f"primary_location.source.issn:{issn},from_publication_date:{date_after(int(ref.get('months_back') or 30))}"
    params = {
        "filter": flt,
        "sort": "publication_date:desc",
        "per-page": min(per_page, 200),
        "mailto": "radar@example.invalid",
    }
    try:
        r = http_get(API, params=params, timeout=30)
        data = r.json()
    except SourceError:
        raise
    except Exception as e:
        raise SourceError(SOURCE, f"{name}: OpenAlex 响应解析失败: {e}", [API]) from e
    return [w for w in (data.get("results") or []) if not _looks_paratext(clean_text(w.get("title") or ""))]


def fetch_latest(ref: dict[str, Any]) -> IssueResult:
    name = clean_text(ref.get("name") or ref.get("issn"))
    min_papers = int(ref.get("min_papers") or 5)
    max_papers = int(ref.get("max_papers") or 15)
    works = _request(ref, 50)
    if not works:
        raise SourceError(SOURCE, f"{name}: OpenAlex 最近 {ref.get('months_back', 30)} 个月无记录", [API])
    first_key = _key(works[0])
    selected = [w for w in works if _key(w) == first_key]
    issue_label = _label(*first_key)
    diagnostics: list[str] = []
    if len(selected) < min_papers:
        selected = works[: max(min_papers, max_papers)]
        issue_label += "+adjacent"
        diagnostics.append(f"最新卷期记录不足 {min_papers} 篇，用最近记录补齐；可能跨卷期")
    selected = selected[:max_papers]
    papers: list[Paper] = []
    for w in selected:
        p = _paper(w, issue_label)
        if p.title:
            papers.append(p)
    if len(papers) < min_papers:
        raise SourceError(SOURCE, f"{name}: OpenAlex 最新卷期仅解析到 {len(papers)} 篇，< {min_papers}", [API])
    published = max((p.published for p in papers if p.published), default="")
    return IssueResult(journal=name, ref=clean_text(ref.get("issn")), issue=issue_label, published=published,
                       papers=papers, source=SOURCE, diagnostics=diagnostics, ok=True)


def enrich_issue(issue: IssueResult, ref: dict[str, Any], logger: Any = None) -> IssueResult:
    """Fill missing abstracts/keywords from OpenAlex, without hiding failures."""
    if not issue.papers:
        return issue
    name = issue.journal
    try:
        works = _request(ref, 100)
    except SourceError as e:
        issue.diagnostics.append(f"OpenAlex 摘要补全失败: {e.message}")
        issue.degraded = True
        return issue
    by_doi: dict[str, dict[str, Any]] = {}
    by_title: dict[str, dict[str, Any]] = {}
    for w in works:
        doi = clean_text(w.get("doi") or "").replace("https://doi.org/", "").lower()
        if doi:
            by_doi[doi] = w
        t = re.sub(r"\W+", "", clean_text(w.get("title") or "").lower())
        if t:
            by_title[t] = w
    filled_abs = 0
    filled_kw = 0
    for p in issue.papers:
        w = by_doi.get((p.doi or "").lower()) if p.doi else None
        if not w:
            key = re.sub(r"\W+", "", (p.title or "").lower())
            w = by_title.get(key)
        if not w:
            continue
        if not p.abstract:
            a = abstract_from_inverted(w.get("abstract_inverted_index"))
            if a:
                p.abstract = a
                filled_abs += 1
        if not p.keywords:
            kws = _keywords(w)
            if kws:
                p.keywords = kws
                filled_kw += 1
    if filled_abs or filled_kw:
        issue.diagnostics.append(f"OpenAlex 补全: 摘要 {filled_abs} 篇, 关键词 {filled_kw} 篇")
    else:
        issue.diagnostics.append(f"OpenAlex 未匹配到可补全项（本刊候选 {len(works)} 条）")
    return issue
