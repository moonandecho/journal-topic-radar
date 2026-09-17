from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import re

from radar.models import Paper
from radar.sources.common import SourceError, clean_text, http_get
from radar.sources.crossref import _issue_key, _item_to_paper, _label

CROSSREF_JOURNAL_SEARCH = "https://api.crossref.org/journals"
OPENALEX_SOURCE_SEARCH = "https://api.openalex.org/sources"
CROSSREF_JOURNAL_WORKS = "https://api.crossref.org/journals/{issn}/works"

MANUAL_BOUNDARY_MESSAGE = (
    "该刊未被国际源收录，请按 README 三步手工添加"
    "（提供官网 URL + parser）"
)

_CJK_RE = re.compile(r"[\u3400-\u9fff]")


@dataclass
class OnlineCandidate:
    """A journal candidate returned by an online bibliographic source."""

    name: str
    issn: str = ""
    publisher: str = ""
    source: str = ""
    homepage: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class OnlineWorks:
    """Result of the Crossref recent-works endpoint for a resolved ISSN."""

    issn: str = ""
    url: str = ""
    ok: bool = False
    issue: str = ""
    published: str = ""
    papers: list[Paper] = field(default_factory=list)
    error: str = ""
    total_results: int = 0

    def titles(self, limit: int = 3) -> list[str]:
        return [p.title for p in self.papers if p.title][:limit]


@dataclass
class OnlineResolution:
    """The complete online resolution chain for a journal name not in config."""

    name: str
    candidates: list[OnlineCandidate] = field(default_factory=list)
    selected: OnlineCandidate | None = None
    works: OnlineWorks | None = None
    tried_sources: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    boundary_message: str = ""


def is_cjk_text(value: str) -> bool:
    return bool(_CJK_RE.search(value or ""))


def normalize_issn(value: Any) -> str:
    """Normalize an ISSN/ISSN-L to the canonical 8-character hyphenated form."""
    raw = re.sub(r"[^0-9Xx]", "", str(value or "")).upper()
    if len(raw) == 8:
        return f"{raw[:4]}-{raw[4:]}"
    return raw


def _normal_name(value: Any) -> str:
    return "".join(ch for ch in clean_text(value).casefold() if ch.isalnum())


def _first_issn(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        for item in value:
            norm = normalize_issn(item)
            if norm:
                return norm
        return ""
    return normalize_issn(value)


def _json_get(url: str, *, params: dict[str, Any], timeout: int) -> tuple[dict[str, Any] | None, str]:
    try:
        response = http_get(url, params=params, timeout=timeout)
    except SourceError as e:
        # SourceError from http_get includes "HTTP <status> <url>" for non-2xx.
        return None, e.message
    except Exception as e:  # defensive: keep the real reason visible
        return None, f"请求异常 {type(e).__name__}: {e}"
    try:
        data = response.json()
    except Exception as e:
        return None, f"JSON 解析失败 {type(e).__name__}: {e}"
    if not isinstance(data, dict):
        return None, f"响应不是 JSON object: {type(data).__name__}"
    return data, ""


def search_crossref(name: str, *, timeout: int = 30) -> tuple[list[OnlineCandidate], str]:
    data, err = _json_get(
        CROSSREF_JOURNAL_SEARCH,
        params={"query": name, "rows": 5},
        timeout=timeout,
    )
    if err:
        return [], f"Crossref journals?query={name}: {err}"
    items = ((data or {}).get("message") or {}).get("items") or []
    out: list[OnlineCandidate] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        title = clean_text(item.get("title") or "")
        if not title:
            continue
        out.append(OnlineCandidate(
            name=title,
            issn=_first_issn(item.get("ISSN") or item.get("issn")),
            publisher=clean_text(item.get("publisher") or ""),
            source="crossref",
            homepage=clean_text(item.get("URL") or ""),
            raw=item,
        ))
    return out, ""


def search_openalex(name: str, *, timeout: int = 30) -> tuple[list[OnlineCandidate], str]:
    data, err = _json_get(
        OPENALEX_SOURCE_SEARCH,
        params={"search": name, "per-page": 5},
        timeout=timeout,
    )
    if err:
        return [], f"OpenAlex sources?search={name}: {err}"
    results = (data or {}).get("results") or []
    out: list[OnlineCandidate] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        title = clean_text(item.get("display_name") or "")
        if not title:
            continue
        issn = _first_issn(item.get("issn_l") or item.get("issn"))
        out.append(OnlineCandidate(
            name=title,
            issn=issn,
            publisher=clean_text(
                item.get("host_organization_name")
                or (item.get("host_organization") if isinstance(item.get("host_organization"), str) else "")
                or ""
            ),
            source="openalex",
            homepage=clean_text(item.get("homepage_url") or ""),
            raw=item,
        ))
    return out, ""


def _dedupe_candidates(candidates: list[OnlineCandidate]) -> list[OnlineCandidate]:
    out: list[OnlineCandidate] = []
    seen: set[tuple[str, str, str]] = set()
    for c in candidates:
        key = (_normal_name(c.name), normalize_issn(c.issn), c.source)
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


def _exact_candidates(name: str, candidates: list[OnlineCandidate]) -> list[OnlineCandidate]:
    wanted = _normal_name(name)
    if not wanted:
        return []
    return [c for c in candidates if _normal_name(c.name) == wanted]


def _select_candidate(name: str, candidates: list[OnlineCandidate]) -> OnlineCandidate | None:
    exact = _exact_candidates(name, candidates)
    if not exact:
        return None
    # Prefer a candidate that carries an ISSN, then Crossref metadata over OpenAlex.
    rank = {
        ("crossref", True): 0,
        ("openalex", True): 1,
        ("crossref", False): 2,
        ("openalex", False): 3,
    }
    return sorted(exact, key=lambda c: rank.get((c.source, bool(c.issn)), 9))[0]


def _works_error(issn: str, url: str, message: str) -> OnlineWorks:
    return OnlineWorks(issn=issn, url=url, ok=False, error=message)


def fetch_crossref_works(issn: str, *, timeout: int = 30, rows: int = 15) -> OnlineWorks:
    issn = normalize_issn(issn)
    url = CROSSREF_JOURNAL_WORKS.format(issn=issn)
    data, err = _json_get(
        url,
        params={"sort": "published", "order": "desc", "rows": rows},
        timeout=timeout,
    )
    if err:
        return _works_error(issn, url, f"Crossref works 请求失败: {err}")
    message = (data or {}).get("message") or {}
    items = message.get("items") or []
    total = int(message.get("total-results") or 0)
    if not items:
        return _works_error(issn, url, f"Crossref works 返回 0 条（total-results={total}，items=0）")

    first_key = _issue_key(items[0])
    issue = _label(*first_key) or "latest"
    papers: list[Paper] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        paper = _item_to_paper(item, issue)
        if paper.title:
            papers.append(paper)
    if not papers:
        return _works_error(issn, url, f"Crossref works 返回 {len(items)} 条，但均无法解析出标题")
    published = max((p.published for p in papers if p.published), default="")
    return OnlineWorks(
        issn=issn,
        url=url,
        ok=True,
        issue=issue,
        published=published,
        papers=papers,
        error="",
        total_results=total,
    )


def resolve_online(name: str, *, timeout: int = 30) -> OnlineResolution:
    """Resolve a journal name against Crossref and OpenAlex, then try Crossref works."""
    query = clean_text(name)
    resolution = OnlineResolution(name=query)
    if not query:
        resolution.failures.append("期刊名为空，无法在线检索")
        return resolution

    crossref_candidates: list[OnlineCandidate] = []
    openalex_candidates: list[OnlineCandidate] = []

    crossref_candidates, crossref_err = search_crossref(query, timeout=timeout)
    resolution.tried_sources.append("crossref")
    if crossref_err:
        resolution.failures.append(crossref_err)

    # OpenAlex is a fallback when Crossref has no exact match, or its exact match
    # lacks an ISSN and therefore cannot reach the Crossref works endpoint.
    crossref_exact = _exact_candidates(query, crossref_candidates)
    if not crossref_exact or not any(c.issn for c in crossref_exact):
        openalex_candidates, openalex_err = search_openalex(query, timeout=timeout)
        resolution.tried_sources.append("openalex")
        if openalex_err:
            resolution.failures.append(openalex_err)

    resolution.candidates = _dedupe_candidates(crossref_candidates + openalex_candidates)
    resolution.selected = _select_candidate(query, resolution.candidates)
    if resolution.selected is not None:
        if resolution.selected.issn:
            resolution.works = fetch_crossref_works(resolution.selected.issn, timeout=timeout)
            if not resolution.works.ok:
                resolution.failures.append(resolution.works.error)
        else:
            resolution.failures.append(
                "在线候选未提供 ISSN，无法请求 Crossref journals/{issn}/works"
            )
    elif resolution.candidates:
        resolution.failures.append(
            "在线源返回了候选，但没有与输入期刊名精确匹配的名称，未自动抓取 works"
        )
    elif not resolution.failures:
        resolution.failures.append("Crossref 与 OpenAlex 均未返回候选")

    if is_cjk_text(query) and not (resolution.selected and resolution.selected.issn):
        resolution.boundary_message = MANUAL_BOUNDARY_MESSAGE
        if resolution.boundary_message not in resolution.failures:
            resolution.failures.append(resolution.boundary_message)

    return resolution
