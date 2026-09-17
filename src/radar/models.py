from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any

@dataclass
class Paper:
    title: str
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    keywords: list[str] = field(default_factory=list)
    published: str = ""
    url: str = ""
    doi: str = ""
    issue: str = ""
    text_source: str = "unknown"
    source: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class IssueResult:
    journal: str
    ref: str = ""
    issue: str = ""
    published: str = ""
    papers: list[Paper] = field(default_factory=list)
    source: str = ""
    diagnostics: list[str] = field(default_factory=list)
    ok: bool = False
    degraded: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d

@dataclass
class PaperMatch:
    paper: Paper
    score: float
    level: str  # strong / weak / irrelevant

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.paper.title,
            "authors": self.paper.authors,
            "score": round(self.score, 4),
            "level": self.level,
            "url": self.paper.url,
            "doi": self.paper.doi,
            "published": self.paper.published,
            "text_source": self.paper.text_source,
            "issue": self.paper.issue,
        }


@dataclass
class JournalMatch:
    journal: str
    source: str = ""
    issue: str = ""
    published: str = ""
    fetch_ok: bool = False
    similar: bool = False
    hit_count: int = 0
    strong_count: int = 0
    weak_count: int = 0
    top_papers: list[PaperMatch] = field(default_factory=list)
    thresholds: dict[str, float] = field(default_factory=dict)
    matcher: str = ""
    degraded: bool = False
    degradation_reasons: list[str] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "journal": self.journal,
            "source": self.source,
            "issue": self.issue,
            "published": self.published,
            "fetch_ok": self.fetch_ok,
            "similar": self.similar,
            "hit_count": self.hit_count,
            "strong_count": self.strong_count,
            "weak_count": self.weak_count,
            "top_papers": [p.to_dict() for p in self.top_papers],
            "thresholds": self.thresholds,
            "matcher": self.matcher,
            "degraded": self.degraded,
            "degradation_reasons": self.degradation_reasons,
            "diagnostics": self.diagnostics,
        }


@dataclass
class MatchReport:
    topic: str
    matcher: str = ""
    backend: str = ""
    thresholds: dict[str, float] = field(default_factory=dict)
    generated_at: str = ""
    offline: bool = False
    degraded: bool = False
    degradation_reasons: list[str] = field(default_factory=list)
    journals: list[JournalMatch] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic": self.topic,
            "matcher": self.matcher,
            "backend": self.backend,
            "thresholds": self.thresholds,
            "generated_at": self.generated_at,
            "offline": self.offline,
            "degraded": self.degraded,
            "degradation_reasons": self.degradation_reasons,
            "journals": [j.to_dict() for j in self.journals],
        }
