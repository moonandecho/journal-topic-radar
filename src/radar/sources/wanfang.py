from __future__ import annotations
from typing import Any
from urllib.parse import quote

from radar.models import IssueResult
from .common import SourceError, clean_text, http_get

SOURCE = "wanfang"
HOME = "https://s.wanfangdata.com.cn"
SEARCH = "https://s.wanfangdata.com.cn/paper?q={q}"


def probe() -> tuple[bool, str]:
    try:
        r = http_get(HOME, timeout=15)
        return True, f"HTTP {r.status_code}, {len(r.content)} bytes"
    except SourceError as e:
        return False, e.message
    except Exception as e:
        return False, repr(e)


def fetch_latest(ref: dict[str, Any]) -> IssueResult:
    """Explicitly-unsupported default route.

    Wanfang's public paper search is a JS application and was not a verified
    source for issue tables.  We record the real search URL and refuse to
    fabricate data.
    """
    name = clean_text(ref.get("name") or "")
    q = quote(name)
    url = SEARCH.format(q=q)
    try:
        r = http_get(url, timeout=20)
    except SourceError as e:
        raise SourceError(SOURCE, f"{name}: 万方检索页不可用: {e.message}", [url]) from e
    raise SourceError(
        SOURCE,
        f"{name}: 万方检索页 HTTP {r.status_code}，但返回的是 JS 壳页面；"
        f"没有可验证的当期目录/摘要 JSON 接口，不能作为主路径",
        [url],
    )
