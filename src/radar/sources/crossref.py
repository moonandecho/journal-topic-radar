from __future__ import annotations
from typing import Any
import re

from radar.models import IssueResult, Paper
from .common import SourceError, clean_text, date_after, extract_doi, http_get, normalize_url, unique_keep_order

SOURCE = "crossref"
API = "https://api.crossref.org/journals/{issn}/works"


def _date_from_item(item: dict[str, Any]) -> str:
    for key in ("published-print", "published-online", "published", "issued", "created"):
        block = item.get(key) or {}
        parts = block.get("date-parts") if isinstance(block, dict) else None
        if parts and parts[0]:
            dp = [p for p in parts[0] if p is not None]
            if len(dp) >= 3:
                return f"{dp[0]:04d}-{dp[1]:02d}-{dp[2]:02d}"
            if len(dp) == 2:
                return f"{dp[0]:04d}-{dp[1]:02d}"
            if len(dp) == 1:
                return f"{dp[0]:04d}"
    return ""


def _authors(item: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for a in item.get("author") or []:
        name = clean_text(a.get("name") or "")
        if not name:
            name = " ".join(x for x in [clean_text(a.get("given")), clean_text(a.get("family"))] if x)
        if name:
            out.append(name)
    return unique_keep_order(out)


def _strip_jats_abstract(value: str) -> str:
    if not value:
        return ""
    s = re.sub(r"<[^>]+>", " ", value)
    s = clean_text(s)
    return s


def _item_to_paper(item: dict[str, Any], issue_label: str, source: str = SOURCE) -> Paper:
    title = clean_text((item.get("title") or [""])[0])
    doi = clean_text(item.get("DOI") or extract_doi(item.get("URL", "")))
    url = normalize_url("https://doi.org/", doi) if doi else clean_text(item.get("URL") or "")
    keywords = unique_keep_order([clean_text(x) for x in (item.get("subject") or [])])[:10]
    return Paper(
        title=title,
        authors=_authors(item),
        abstract=_strip_jats_abstract(item.get("abstract") or ""),
        keywords=keywords,
        published=_date_from_item(item),
        url=url,
        doi=doi,
        issue=issue_label,
        source=source,
    )


def _issue_key(item: dict[str, Any]) -> tuple[str, str]:
    return clean_text(item.get("volume") or ""), clean_text(item.get("issue") or "")


def _label(volume: str, issue: str) -> str:
    if volume and issue:
        return f"{volume}({issue})"
    if volume:
        return volume
    return "latest"


def fetch_latest(ref: dict[str, Any]) -> IssueResult:
    issn = clean_text(ref.get("issn"))
    name = clean_text(ref.get("name") or issn)
    if not issn:
        raise SourceError(SOURCE, f"{name}: 缺少 ISSN，无法请求 Crossref", [])
    min_papers = int(ref.get("min_papers") or 5)
    max_papers = int(ref.get("max_papers") or 15)
    url = API.format(issn=issn)
    params = {
        "filter": f"from-pub-date:{date_after(int(ref.get('months_back') or 30))}",
        "sort": "published",
        "order": "desc",
        "rows": max(50, max_papers * 4),
    }
    try:
        r = http_get(url, params=params, timeout=30)
        data = r.json()
    except SourceError as e:
        raise
    except Exception as e:
        raise SourceError(SOURCE, f"{name}: Crossref 响应解析失败: {e}", [url]) from e
    items = ((data.get("message") or {}).get("items") or [])
    if not items:
        raise SourceError(SOURCE, f"{name}: Crossref 最近 {ref.get('months_back', 30)} 个月无记录", [url])
    first_key = _issue_key(items[0])
    selected = [it for it in items if _issue_key(it) == first_key]
    issue_label = _label(*first_key)
    diagnostics: list[str] = []
    if len(selected) < min_papers:
        selected = items[: max(min_papers, max_papers)]
        issue_label = issue_label + "+adjacent"
        diagnostics.append(f"最新卷期记录不足 {min_papers} 篇，用最近记录补齐；可能跨卷期")
    selected = selected[:max_papers]
    papers: list[Paper] = []
    for it in selected:
        p = _item_to_paper(it, issue_label)
        if p.title:
            papers.append(p)
    if len(papers) < min_papers:
        raise SourceError(SOURCE, f"{name}: Crossref 最新卷期仅解析到 {len(papers)} 篇，< {min_papers}", [url])
    published = max((p.published for p in papers if p.published), default="")
    return IssueResult(journal=name, ref=issn, issue=issue_label, published=published,
                       papers=papers, source=SOURCE, diagnostics=diagnostics, ok=True)
