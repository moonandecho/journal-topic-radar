from __future__ import annotations
from datetime import date, timedelta
from typing import Any, Iterable
import html
import re
import urllib.parse

import requests

USER_AGENT = "journal-topic-radar/0.1 (+https://example.invalid; mailto:radar@example.invalid)"
DEFAULT_TIMEOUT = 25


class SourceError(RuntimeError):
    def __init__(self, source: str, message: str, tried: list[str] | None = None):
        self.source = source
        self.message = message
        self.tried = tried or []
        super().__init__(f"[{source}] {message}")


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"})
    return s


_SESSION = session()


def http_get(url: str, *, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None,
             timeout: int = DEFAULT_TIMEOUT, allow_redirects: bool = True) -> requests.Response:
    try:
        r = _SESSION.get(url, params=params, headers=headers, timeout=timeout,
                         allow_redirects=allow_redirects)
    except requests.RequestException as e:
        raise SourceError("http", f"请求失败 {url}: {e}", [url]) from e
    if r.status_code >= 400:
        raise SourceError("http", f"HTTP {r.status_code} {url}", [url])
    return r


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    s = html.unescape(str(value))
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def normalize_url(base: str, href: str) -> str:
    if not href:
        return ""
    if href.startswith("//"):
        return "https:" + href
    return urllib.parse.urljoin(base, href)


def extract_doi(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"10\.\d{4,9}/[^\s,;\)\]\}]+", text, flags=re.I)
    return m.group(0).rstrip(".") if m else ""


def date_after(months: int = 18) -> str:
    d = date.today()
    # simple month subtraction sufficient for API lower bound
    y = d.year
    m = d.month - months
    while m <= 0:
        m += 12
        y -= 1
    return f"{y:04d}-{m:02d}-{d.day:02d}"


def abstract_from_inverted(inv: Any) -> str:
    if not isinstance(inv, dict) or not inv:
        return ""
    positions: list[tuple[int, str]] = []
    for word, pos_list in inv.items():
        for p in pos_list or []:
            positions.append((int(p), word))
    positions.sort(key=lambda x: x[0])
    return " ".join(w for _, w in positions)


def first(seq: Iterable[Any], default: Any = None) -> Any:
    for x in seq:
        return x
    return default


def unique_keep_order(items: Iterable[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for x in items:
        x = clean_text(x)
        if not x or x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out
