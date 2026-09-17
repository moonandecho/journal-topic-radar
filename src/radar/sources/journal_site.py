from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from radar.models import IssueResult, Paper
from .common import SourceError, clean_text, extract_doi, http_get, normalize_url, unique_keep_order

SOURCE = "journal_site"


def _looks_like_cover(title: str) -> bool:
    t = clean_text(title)
    if not t:
        return True
    bad = ("目录", "封面", "封底", "征稿", "投稿", "编委会", "版权", "广告", "启事", "摘要页", "目次")
    if any(b in t for b in bad) and len(t) <= 30:
        return True
    return len(t) < 4


def _published_year(text: str) -> str:
    m = re.search(r"(19|20)\d{2}", text or "")
    return m.group(0) if m else ""


def _issue_label_from_text(text: str, parser: str) -> str:
    t = clean_text(text)
    if parser == "jos":
        m = re.search(r"(20\d{2})\s*年\s*第?\s*(\d+)\s*期", t)
        if m:
            return f"{m.group(1)}({m.group(2)})"
        m = re.search(r"(20\d{2})[_\-/](\d+)", t)
        if m:
            return f"{m.group(1)}({m.group(2)})"
    m = re.search(r"(20\d{2})\s*年.*?第?\s*(\d+)\s*卷.*?第?\s*(\d+)\s*期", t)
    if m:
        return f"{m.group(1)}, {m.group(2)}({m.group(3)})"
    m = re.search(r"(20\d{2})[^\d]{0,8}(\d+)[^\d]{0,8}(\d+)", t)
    if m:
        return f"{m.group(1)}, {m.group(2)}({m.group(3)})"
    m = re.search(r"(20\d{2})\s*年\s*第?\s*(\d+)\s*期", t)
    if m:
        return f"{m.group(1)}({m.group(2)})"
    return ""


def _discover_current_url(ref: dict[str, Any]) -> str:
    direct = clean_text(ref.get("current_url") or "")
    if direct:
        return direct
    base = clean_text(ref.get("site_url") or ref.get("official_site") or "")
    if not base:
        raise SourceError(SOURCE, f"{ref.get('name')}: 未配置 site_url/current_url", [])
    r = http_get(base, timeout=25)
    soup = BeautifulSoup(r.text, "html.parser")
    parser = ref.get("parser") or "generic"
    if parser == "jos":
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            m = re.search(r"/jos/article/issue/(20\d{2})_(\d+)", href)
            if m:
                links.append((int(m.group(1)), int(m.group(2)), normalize_url(base, href)))
        if links:
            return sorted(links)[-1][2]
    candidates: list[tuple[int, str]] = []
    for a in soup.find_all("a", href=True):
        text = clean_text(a.get_text(" ", strip=True))
        href = a["href"]
        url = normalize_url(base, href)
        score = 0
        if "当期" in text or "current" in href.lower():
            score += 5
        if "latest" in href.lower() or "最新" in text:
            score += 2
        if "/article/" in href and "issue" in href.lower():
            score += 3
        if score:
            candidates.append((score, url))
    if candidates:
        return sorted(candidates, key=lambda x: -x[0])[0][1]
    raise SourceError(SOURCE, f"{ref.get('name')}: 官网首页未发现当期目录链接 ({base})", [base])


def _parse_magtech_list(soup: BeautifulSoup, base: str, ref: dict[str, Any]) -> list[Paper]:
    papers: list[Paper] = []
    for block in soup.select("div.article-list"):
        title_el = block.select_one(".article-list-title a")
        if not title_el:
            continue
        title = clean_text(title_el.get_text(" ", strip=True))
        if _looks_like_cover(title):
            continue
        href = clean_text(title_el.get("href") or "")
        if not href or href.startswith("javascript"):
            # try any abstract/doi link
            alt = block.find("a", href=re.compile(r"/article/(doi|abstract)/"))
            href = clean_text(alt.get("href") if alt else "")
        url = normalize_url(base, href) if href else ""
        authors = [clean_text(x.get_text(" ", strip=True)) for x in block.select(".article-list-author a")]
        authors = unique_keep_order(authors)
        pos_text = clean_text(block.select_one(".article-list-time").get_text(" ", strip=True)) if block.select_one(".article-list-time") else ""
        doi = ""
        doi_href = block.find("a", href=re.compile(r"doi\.org|/doi/", re.I))
        if doi_href:
            doi = extract_doi(doi_href.get_text(" ", strip=True) or doi_href.get("href") or "")
        if not doi:
            doi = extract_doi(pos_text)
        abstract = ""
        kw: list[str] = []
        az = block.select_one(".article-list-zy")
        if az:
            raw = clean_text(az.get_text(" ", strip=True))
            abstract = _abstract_from_blob(raw)
            kw = _keywords_from_blob(raw)
        papers.append(Paper(
            title=title, authors=authors, abstract=abstract, keywords=kw,
            published=_published_year(pos_text), url=url, doi=doi,
            issue="", source=SOURCE,
        ))
    return papers


def _parse_jos_list(soup: BeautifulSoup, base: str, ref: dict[str, Any]) -> list[Paper]:
    papers: list[Paper] = []
    for li in soup.select("li.article_line"):
        title_el = li.select_one(".article_title a")
        if not title_el:
            continue
        title = clean_text(title_el.get_text(" ", strip=True))
        if _looks_like_cover(title):
            continue
        url = normalize_url(base, clean_text(title_el.get("href") or ""))
        authors = unique_keep_order([clean_text(x.get_text(" ", strip=True)) for x in li.select(".article_author a, .article_author span")])
        pos_text = clean_text(li.select_one(".article_position").get_text(" ", strip=True)) if li.select_one(".article_position") else ""
        doi = extract_doi(pos_text)
        abstract = ""
        body = li.select_one(".abstract_body")
        if body:
            abstract = _abstract_from_blob(clean_text(body.get_text(" ", strip=True)))
        papers.append(Paper(
            title=title, authors=authors, abstract=abstract, keywords=[],
            published=_published_year(pos_text), url=url, doi=doi,
            issue="", source=SOURCE,
        ))
    return papers


def _abstract_from_blob(raw: str) -> str:
    s = clean_text(raw)
    if not s:
        return ""
    # Remove action breadcrumbs that occur on Magtech/RADARS pages.
    s = re.sub(r"\s*(摘要|Abstract)\s*[\(（]?\s*\d*\s*[\)）]?\s*", " ", s, flags=re.I)
    s = re.sub(r"\s*(HTML全文|HTML|PDF[^ ]*|图\s*\([^)]*\)|表\s*\([^)]*\)|参考文献\s*\([^)]*\)|施引文献[^ ]*|资源附件[^ ]*|访问统计|收藏)\s*", " ", s)
    s = re.sub(r"^\s*(摘要|Abstract)\s*[:：]\s*", "", s, flags=re.I)
    # If keywords follow, cut them off.
    s = re.split(r"\s*(关键词|Key\s*words?|关键字)\s*[:：]", s, maxsplit=1, flags=re.I)[0]
    s = clean_text(s)
    if len(s) < 50:
        return ""
    return s


def _keywords_from_blob(raw: str) -> list[str]:
    m = re.search(r"(关键词|关键字|Key\s*words?)\s*[:：]\s*(.*)", clean_text(raw), flags=re.I)
    if not m:
        return []
    return unique_keep_order([x for x in re.split(r"[;,，；/|]", m.group(2)) if clean_text(x)])[:12]


def _parse_generic_list(soup: BeautifulSoup, base: str, ref: dict[str, Any]) -> list[Paper]:
    """Fallback: collect article links with reasonable titles."""
    papers: list[Paper] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        title = clean_text(a.get_text(" ", strip=True))
        href = a["href"]
        if _looks_like_cover(title) or len(title) > 220:
            continue
        if not re.search(r"(article/(doi|abstract)|/doi/|issue/)", href, re.I):
            continue
        if title in seen:
            continue
        seen.add(title)
        url = normalize_url(base, href)
        papers.append(Paper(title=title, url=url, doi=extract_doi(href), source=SOURCE))
    return papers


def _meta_content(soup: BeautifulSoup, *names: str) -> str:
    wanted = {n.lower() for n in names}
    for m in soup.find_all("meta"):
        key = (m.get("name") or m.get("property") or "").strip().lower()
        if key in wanted:
            val = clean_text(m.get("content") or "")
            if val:
                return val
    return ""


def parse_detail(html: str, url: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    out: dict[str, Any] = {"url": url}
    abstract = _meta_content(soup, "citation_abstract", "dc.description", "dcterms.abstract", "description", "og:description")
    if not abstract:
        for sel in (".article-abstract", ".abstract-cn", ".article_abstract_main", ".abstract_body", ".abstract", "div.abstract", "#abstract"):
            el = soup.select_one(sel)
            if not el:
                continue
            text = _abstract_from_blob(clean_text(el.get_text(" ", strip=True)))
            if text:
                abstract = text
                break
    if not abstract:
        # Some detail pages embed a paragraph after the literal label 摘要:
        for el in soup.find_all(["div", "p", "section"]):
            txt = clean_text(el.get_text(" ", strip=True))
            if txt.startswith("摘要:") or txt.startswith("摘要："):
                a = _abstract_from_blob(txt)
                if a:
                    abstract = a
                    break
    out["abstract"] = abstract
    kws = _meta_content(soup, "citation_keywords", "dc.keywords", "keywords", "citation_keyword")
    if not kws:
        for sel in (".article-keyword", ".keywords", ".article_keyword", ".keyword"):
            el = soup.select_one(sel)
            if el:
                kws = clean_text(el.get_text(" ", strip=True))
                break
    if kws:
        kws = re.sub(r"^\s*(关键词|关键字|Key\s*words?)\s*[:：]\s*", "", kws, flags=re.I)
        out["keywords"] = unique_keep_order([x for x in re.split(r"[;,，；/|]", kws) if clean_text(x)])[:12]
    else:
        out["keywords"] = []
    date = _meta_content(soup, "citation_publication_date", "citation_date", "citation_online_date", "dc.date", "article:published_time")
    # Prefer explicit 出版日期 / Published on date when present (issue publication date, not just online-first date).
    m = re.search(r"(出版日期|Published\s+on)\s*[:：]?\s*(20\d{2}[-/.]\d{1,2}[-/.]\d{1,2})",
                  clean_text(soup.get_text(" ", strip=True)), flags=re.I)
    if m:
        date = m.group(2).replace('/', '-').replace('.', '-')
    out["published"] = date[:10] if re.match(r"\d{4}-\d{2}-\d{2}", date) else date
    authors = _meta_content(soup, "citation_authors", "dc.contributor", "citation_author")
    if authors:
        out["authors"] = unique_keep_order([x.strip() for x in re.split(r"[;,，；/|]", authors) if x.strip()])
    return out


def _enrich_details(papers: list[Paper], ref: dict[str, Any]) -> list[str]:
    diagnostics: list[str] = []
    limit = int(ref.get("enrich_limit") or 6)
    targets = []
    for p in papers[: max(limit * 3, 15)]:
        if p.url and (not p.abstract or not p.keywords):
            targets.append(p)
        if len(targets) >= limit:
            break
    if not targets:
        return diagnostics
    failed = 0
    def work(p: Paper):
        r = http_get(p.url, timeout=20)
        return p, parse_detail(r.text, p.url)
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(work, p): p for p in targets}
        for fut in as_completed(futs):
            try:
                p, detail = fut.result()
            except Exception:
                failed += 1
                continue
            if not p.abstract and detail.get("abstract"):
                p.abstract = detail["abstract"]
            if not p.keywords and detail.get("keywords"):
                p.keywords = detail["keywords"]
            if detail.get("published") and (not p.published or len(str(p.published)) < len(str(detail["published"]))):
                p.published = detail["published"]
            if detail.get("authors") and not p.authors:
                p.authors = detail["authors"]
    if failed:
        diagnostics.append(f"官网详情页补全失败 {failed} 篇（保留标题/摘要为空的记录，不静默忽略）")
    return diagnostics


def fetch_latest(ref: dict[str, Any]) -> IssueResult:
    name = clean_text(ref.get("name") or ref.get("slug") or "")
    parser = clean_text(ref.get("parser") or "generic")
    base = clean_text(ref.get("site_url") or ref.get("official_site") or "")
    current_url = _discover_current_url(ref)
    try:
        r = http_get(current_url, timeout=30)
    except SourceError:
        raise
    soup = BeautifulSoup(r.text, "html.parser")
    if parser == "jos":
        papers = _parse_jos_list(soup, base or current_url, ref)
        issue_source_text = clean_text((soup.title.get_text(" ", strip=True) if soup.title else ""))
    elif parser == "magtech":
        papers = _parse_magtech_list(soup, current_url, ref)
        issue_el = soup.select_one(".journalIssue") or soup.select_one("h2.journalIssue")
        issue_text = clean_text(issue_el.get_text(" ", strip=True) if issue_el else "")
        if not issue_text:
            issue_text = clean_text(soup.title.get_text(" ", strip=True) if soup.title else "")
        issue_source_text = issue_text
    else:
        papers = _parse_generic_list(soup, current_url, ref)
        issue_source_text = clean_text(soup.title.get_text(" ", strip=True) if soup.title else "")
    # Remove duplicates and keep publication-like records.
    uniq: list[Paper] = []
    seen: set[str] = set()
    for p in papers:
        key = re.sub(r"\W+", "", (p.title or "").lower())
        if not key or key in seen:
            continue
        seen.add(key)
        uniq.append(p)
    papers = uniq
    min_papers = int(ref.get("min_papers") or 5)
    if len(papers) < min_papers:
        raise SourceError(SOURCE, f"{name}: 官网当期目录仅解析到 {len(papers)} 篇，< {min_papers} ({current_url})", [current_url])
    max_papers = int(ref.get("max_papers") or 12)
    papers = papers[:max_papers]
    issue = _issue_label_from_text(issue_source_text, parser) or _issue_label_from_text(" ".join(p.published for p in papers), parser) or "latest"
    diagnostics = [f"官网列表: {current_url}", f"原始解析 {len(papers)} 篇，保留 {len(papers)} 篇"]
    diagnostics.extend(_enrich_details(papers, ref))
    for p in papers:
        p.issue = issue
    published = max((p.published for p in papers if p.published), default="")
    if any((not p.abstract) for p in papers):
        diagnostics.append(f"有 {sum(1 for p in papers if not p.abstract)} 篇未获取到摘要，文本使用标题+关键词")
    return IssueResult(journal=name, ref=clean_text(ref.get("issn")), issue=issue, published=published,
                       papers=papers, source=SOURCE, diagnostics=diagnostics, ok=True)
