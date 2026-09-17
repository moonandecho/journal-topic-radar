from __future__ import annotations
from pathlib import Path
from typing import Any
import json

from radar.models import IssueResult, Paper
from radar.config import ROOT
from .common import SourceError, clean_text

SOURCE = "offline"


def fixture_path(ref: dict[str, Any]) -> Path:
    slug = clean_text(ref.get("slug") or ref.get("name") or ref.get("issn") or "")
    return ROOT / "fixtures" / f"{slug}.json"


def fetch_latest(ref: dict[str, Any]) -> IssueResult:
    path = fixture_path(ref)
    name = clean_text(ref.get("name") or ref.get("slug"))
    if not path.exists():
        raise SourceError(SOURCE, f"{name}: 离线样本不存在 {path}", [str(path)])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise SourceError(SOURCE, f"{name}: 离线样本解析失败 {path}: {e}", [str(path)]) from e
    papers = []
    for item in data.get("papers") or []:
        papers.append(Paper(
            title=clean_text(item.get("title")),
            authors=list(item.get("authors") or []),
            abstract=clean_text(item.get("abstract")),
            keywords=list(item.get("keywords") or []),
            published=clean_text(item.get("published")),
            url=clean_text(item.get("url")),
            doi=clean_text(item.get("doi")),
            issue=clean_text(item.get("issue") or data.get("issue") or ""),
            text_source=clean_text(item.get("text_source") or ""),
            source=clean_text(item.get("source") or "offline-fixture"),
        ))
    if len(papers) < int(ref.get("min_papers") or 5):
        raise SourceError(SOURCE, f"{name}: 离线样本仅 {len(papers)} 篇，< 要求", [str(path)])
    diags = list(data.get("diagnostics") or [])
    diags.append(f"离线样本: {path.relative_to(ROOT)} (captured={data.get('captured_at','unknown')})")
    return IssueResult(
        journal=clean_text(data.get("journal") or name),
        ref=clean_text(data.get("ref") or ref.get("issn")),
        issue=clean_text(data.get("issue") or ""),
        published=clean_text(data.get("published") or ""),
        papers=papers,
        source=SOURCE,
        diagnostics=diags,
        ok=True,
    )
