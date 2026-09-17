from __future__ import annotations
from typing import Any

from radar.models import IssueResult
from .common import SourceError, clean_text, http_get

SOURCE = "sciengine"
HOME = "https://www.sciengine.com"


def probe() -> tuple[bool, str]:
    try:
        r = http_get(HOME, timeout=15)
        return True, f"HTTP {r.status_code}, {len(r.content)} bytes"
    except SourceError as e:
        return False, e.message
    except Exception as e:
        return False, repr(e)


def fetch_latest(ref: dict[str, Any]) -> IssueResult:
    """Best-effort placeholder adapter.

    SciEngine is a SPA.  We deliberately do not claim it works for a journal
    until a per-journal API/source URL has been verified.  When configured as a
    route this function reports the exact missing piece instead of returning an
    empty IssueResult.
    """
    name = clean_text(ref.get("name") or ref.get("slug") or "")
    api_url = clean_text(ref.get("sciengine_api_url") or "")
    if not api_url:
        raise SourceError(
            SOURCE,
            f"{name}: 未配置经验证的 SciEngine 接口地址 (sciengine_api_url)；"
            f"官网首页可探测但期刊目录为前端 API，不能伪装成功",
            [HOME],
        )
    try:
        r = http_get(api_url, timeout=25)
    except SourceError:
        raise
    # A real adapter needs the journal-specific response schema; fail loudly.
    raise SourceError(SOURCE, f"{name}: SciEngine 接口 {api_url} 返回 HTTP {r.status_code}，但缺少该刊响应映射", [api_url])
