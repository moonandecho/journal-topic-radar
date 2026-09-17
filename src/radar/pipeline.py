from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Iterable
import logging
import re

from radar import config
from radar.matcher import MatchBackend, build_text, make_backend
from radar.models import IssueResult, JournalMatch, MatchReport, Paper, PaperMatch
from radar.sources import get_source
from radar.sources.common import SourceError

log = logging.getLogger("radar.pipeline")


def _source_chain(journal: dict[str, Any]) -> list[str]:
    return config.source_priority(journal)


def fetch_issue(journal: dict[str, Any], *, offline: bool = False) -> IssueResult:
    name = journal.get("name") or journal.get("slug") or journal.get("issn")
    if offline:
        try:
            issue = get_source("offline").fetch_latest(journal)
            issue.diagnostics.append("离线模式：未联网；使用 fixtures/ 中真实抓取样本")
            return issue
        except Exception as e:
            msg = f"离线样本不可用: {e}"
            log.error("%s: %s", name, msg)
            return IssueResult(journal=str(name), ref=str(journal.get("issn") or ""), source="offline",
                               diagnostics=[msg], ok=False, degraded=True)

    failures: list[str] = []
    for source_name in _source_chain(journal):
        module = get_source(source_name)
        try:
            issue = module.fetch_latest(journal)
            if not issue.ok:
                failures.append(f"{source_name}: 返回 ok=False")
                continue
            # Cross-source enrichment: OpenAlex abstracts for Crossref primary route.
            if source_name == "crossref" and (journal.get("enrich_openalex", True)):
                try:
                    openalex = get_source("openalex")
                    openalex.enrich_issue(issue, journal, logger=log)
                except Exception as e:
                    msg = f"OpenAlex 摘要补全不可用: {type(e).__name__}: {e}"
                    issue.diagnostics.append(msg)
                    issue.degraded = True
                    log.warning("%s: %s", name, msg)
            # If the primary route itself had to fall back, annotate it.
            if source_name != _source_chain(journal)[0]:
                issue.diagnostics.append(f"主路径不可用，已降级到备选源 {source_name}")
                issue.degraded = True
            issue.diagnostics.extend(failures)
            for p in issue.papers:
                text, text_source = build_text(p)
                p.text_source = text_source
                if not text:
                    p.text_source = "empty"
            return issue
        except Exception as e:
            reason = getattr(e, "message", str(e))
            msg = f"{source_name}: {reason}"
            failures.append(msg)
            log.warning("%s 抓取失败 %s", name, msg)
    return IssueResult(
        journal=str(name), ref=str(journal.get("issn") or ""), source="none",
        diagnostics=failures or ["没有配置可用数据源"], ok=False, degraded=True,
    )


def fetch_all(journals: list[dict[str, Any]], *, offline: bool = False, workers: int = 4) -> list[IssueResult]:
    results: list[IssueResult | None] = [None] * len(journals)
    with ThreadPoolExecutor(max_workers=max(1, min(workers, len(journals)))) as ex:
        futs = {ex.submit(fetch_issue, j, offline=offline): idx for idx, j in enumerate(journals)}
        for fut in as_completed(futs):
            idx = futs[fut]
            try:
                results[idx] = fut.result()
            except Exception as e:
                j = journals[idx]
                results[idx] = IssueResult(journal=str(j.get("name") or ""), source="none",
                                           diagnostics=[f"抓取线程异常: {type(e).__name__}: {e}"],
                                           ok=False, degraded=True)
    return [r for r in results if r is not None]


def select_journals(names: Iterable[str] | None, all_journals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not names:
        return all_journals
    wanted = [n for n in names if str(n).strip()]
    selected: list[dict[str, Any]] = []
    missing: list[str] = []
    for n in wanted:
        j = config.find_journal(n, all_journals)
        if j and j not in selected:
            selected.append(j)
        else:
            missing.append(n)
    if missing:
        raise ValueError(f"期刊不在 config/journals.yaml 中: {missing}; 现场新增期刊请按 README 三步操作")
    return selected


def _level(score: float, thresholds: dict[str, float]) -> str:
    if score >= thresholds.get("strong", 1.0):
        return "strong"
    if score >= thresholds.get("weak", 0.0):
        return "weak"
    return "irrelevant"


def _journal_match(issue: IssueResult, topic: str, backend: MatchBackend, top_k: int = 3) -> JournalMatch:
    thresholds = dict(backend.thresholds)
    reasons: list[str] = []
    if not issue.ok:
        reasons.extend(issue.diagnostics or ["抓取失败，原因未记录"])
        return JournalMatch(
            journal=issue.journal, source=issue.source, issue=issue.issue, published=issue.published,
            fetch_ok=False, similar=False, hit_count=0, strong_count=0, weak_count=0,
            thresholds=thresholds, matcher=backend.name, degraded=True,
            degradation_reasons=reasons, diagnostics=list(issue.diagnostics),
        )
    if not issue.papers:
        reasons.append("抓取成功但论文列表为空（策略不允许静默返回空结果）")
    texts = [build_text(p)[0] for p in issue.papers]
    scores = backend.score(topic, texts)
    pairs: list[PaperMatch] = []
    for p, s in zip(issue.papers, scores):
        lvl = _level(s, thresholds)
        pairs.append(PaperMatch(paper=p, score=s, level=lvl))
    pairs.sort(key=lambda x: x.score, reverse=True)
    hit = sum(1 for p in pairs if p.level in ("strong", "weak"))
    strong = sum(1 for p in pairs if p.level == "strong")
    weak = sum(1 for p in pairs if p.level == "weak")
    if issue.degraded:
        reasons.extend([d for d in issue.diagnostics if any(k in d for k in ("失败", "降级", "不可用", "未匹配", "未获取"))])
    for d in issue.diagnostics:
        if ("未获取到摘要" in d or "未匹配到可补全项" in d) and d not in reasons:
            reasons.append(d)
    if backend.kind != "embedding":
        reasons.append(f"matcher={backend.kind}，非 embedding 语义后端；报告已显式标注降级")
    return JournalMatch(
        journal=issue.journal,
        source=issue.source,
        issue=issue.issue,
        published=issue.published,
        fetch_ok=True,
        similar=hit >= 1,
        hit_count=hit,
        strong_count=strong,
        weak_count=weak,
        top_papers=pairs[:top_k],
        thresholds=thresholds,
        matcher=backend.name,
        degraded=bool(reasons) or issue.degraded,
        degradation_reasons=list(dict.fromkeys(reasons)),
        diagnostics=list(issue.diagnostics),
    )


def run_match(topic: str, *, journal_names: Iterable[str] | None = None, offline: bool = False,
              matcher_prefer: str = "auto", top_k: int = 3) -> MatchReport:
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("--topic 不能为空")
    journals = select_journals(journal_names, config.load_journals())
    backend, backend_reasons = make_backend(matcher_prefer, config.load_thresholds(), offline=offline)
    issues = fetch_all(journals, offline=offline)
    jms = [_journal_match(issue, topic, backend, top_k=top_k) for issue in issues]
    degradation_reasons: list[str] = list(backend_reasons)
    for jm in jms:
        if jm.degraded:
            degradation_reasons.extend(jm.degradation_reasons)
    degradation_reasons = list(dict.fromkeys(degradation_reasons))
    report = MatchReport(
        topic=topic,
        matcher=backend.name,
        backend=backend.kind,
        thresholds=dict(backend.thresholds),
        generated_at=datetime.now().astimezone().isoformat(timespec="seconds"),
        offline=offline,
        degraded=bool(degradation_reasons) or any(not j.fetch_ok for j in jms),
        degradation_reasons=degradation_reasons,
        journals=jms,
    )
    log.info("topic=%s matcher=%s offline=%s journals=%d", topic, backend.name, offline, len(jms))
    return report


def save_fixtures(journals: list[dict[str, Any]], out_dir: str | None = None) -> list[str]:
    """Fetch real online data and write normalized fixtures (used with evidence generation)."""
    from pathlib import Path
    import json
    root = config.ROOT / "fixtures"
    root.mkdir(parents=True, exist_ok=True)
    saved: list[str] = []
    for j in journals:
        issue = fetch_issue(j, offline=False)
        slug = j.get("slug") or str(j.get("name"))
        path = root / f"{slug}.json"
        data = issue.to_dict()
        data["captured_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        data["capture_note"] = "normalized from real online adapter response"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        saved.append(str(path))
    return saved
