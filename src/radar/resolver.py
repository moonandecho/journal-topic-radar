from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from radar import config
from radar.models import IssueResult
from radar.pipeline import fetch_issue
from radar import online as online_sources


@dataclass
class ResolveResult:
    """Result of resolving a live journal name against config and a source adapter."""
    name: str
    journal: dict[str, Any] | None = None
    issue: IssueResult | None = None
    ok: bool = False
    candidates: list[str] = field(default_factory=list)
    tried_sources: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    online_attempted: bool = False
    online_candidates: list[Any] = field(default_factory=list)
    online_selected: Any | None = None
    online_works: Any | None = None
    online_tried_sources: list[str] = field(default_factory=list)
    online_failures: list[str] = field(default_factory=list)
    online_boundary_message: str = ""

    def identifiers(self) -> dict[str, str]:
        j = self.journal or {}
        return {
            "name": str(j.get("name") or self.name),
            "issn": str(j.get("issn") or ""),
            "slug": str(j.get("slug") or ""),
            "official_site": str(j.get("official_site") or j.get("site_url") or ""),
            "country": str(j.get("country") or ""),
        }


def _config_candidates(js: list[dict[str, Any]]) -> list[str]:
    candidates = []
    for j in js:
        aliases = ", ".join(j.get("aliases") or [])
        candidates.append(
            f"{j.get('name')} | ISSN={j.get('issn') or '-'} | slug={j.get('slug')} | aliases={aliases}"
        )
    return candidates


def _online_journal_stub(selected: Any) -> dict[str, Any]:
    from radar import config as config_module

    return {
        "name": selected.name,
        "aliases": [selected.name],
        "country": config_module.infer_country(selected.name, selected.publisher),
        "issn": selected.issn,
        "official_site": selected.homepage,
        "site_url": selected.homepage,
        "slug": config_module.unique_slug(selected.name),
        "source_priority": ["crossref", "openalex"],
        "publisher": selected.publisher,
        "online_source": selected.source,
    }


def resolve_journal(name: str, *, offline: bool = False,
                    journals: list[dict[str, Any]] | None = None,
                    online: bool = False) -> ResolveResult:
    js = journals if journals is not None else config.load_journals()
    journal = config.find_journal(name, js)
    if not journal:
        candidates = _config_candidates(js)
        if offline or not online:
            return ResolveResult(
                name=name,
                ok=False,
                candidates=candidates,
                failures=["配置中不存在该期刊；现场新增期刊请参考 README 的“三步操作”。"],
            )

        discovery = online_sources.resolve_online(name)
        failures = list(discovery.failures)
        issue: IssueResult | None = None
        stub: dict[str, Any] | None = None
        if discovery.selected is not None and discovery.selected.issn:
            stub = _online_journal_stub(discovery.selected)
            if discovery.works is not None:
                issue = IssueResult(
                    journal=discovery.selected.name,
                    ref=discovery.selected.issn,
                    issue=discovery.works.issue,
                    published=discovery.works.published,
                    papers=discovery.works.papers,
                    source="crossref",
                    diagnostics=list(discovery.works.error and [discovery.works.error] or []),
                    ok=discovery.works.ok,
                    degraded=not discovery.works.ok,
                )
        if discovery.boundary_message and discovery.boundary_message not in failures:
            failures.append(discovery.boundary_message)
        return ResolveResult(
            name=name,
            journal=stub,
            issue=issue,
            ok=bool(issue is not None and issue.ok),
            candidates=candidates,
            tried_sources=list(discovery.tried_sources),
            failures=failures,
            online_attempted=True,
            online_candidates=list(discovery.candidates),
            online_selected=discovery.selected,
            online_works=discovery.works,
            online_tried_sources=list(discovery.tried_sources),
            online_failures=list(discovery.failures),
            online_boundary_message=discovery.boundary_message,
        )
    tried = config.source_priority(journal)
    issue = fetch_issue(journal, offline=offline)
    failures: list[str] = []
    if not issue.ok:
        failures = list(issue.diagnostics) or ["没有配置可用数据源"]
    return ResolveResult(
        name=name,
        journal=journal,
        issue=issue,
        ok=issue.ok,
        tried_sources=tried,
        failures=failures,
    )
