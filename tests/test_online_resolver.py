from __future__ import annotations

from pathlib import Path

import pytest

from radar import cli, config
from radar.online import (
    CROSSREF_JOURNAL_SEARCH,
    CROSSREF_JOURNAL_WORKS,
    MANUAL_BOUNDARY_MESSAGE,
    OPENALEX_SOURCE_SEARCH,
    resolve_online,
)


class FakeResponse:
    def __init__(self, data):
        self._data = data
        self.status_code = 200

    def json(self):
        return self._data


def _crossref_search(*titles_with_issns):
    return {
        "status": "ok",
        "message": {
            "items": [
                {
                    "title": title,
                    "ISSN": [issn] if issn else [],
                    "publisher": publisher,
                }
                for title, issn, publisher in titles_with_issns
            ]
        },
    }


def _openalex_search(*titles_with_issns):
    return {
        "meta": {"count": len(titles_with_issns)},
        "results": [
            {
                "display_name": title,
                "issn_l": issn,
                "host_organization_name": publisher,
            }
            for title, issn, publisher in titles_with_issns
        ],
    }


def _works_item(title, volume="12", issue="3", published=(2026, 1, 2), doi="10.1234/x"):
    return {
        "title": [title],
        "volume": volume,
        "issue": issue,
        "published": {"date-parts": [list(published)]},
        "DOI": doi,
    }


def test_online_resolution_crossref_exact_and_works(monkeypatch):
    calls: list[str] = []

    def fake_http_get(url, *, params=None, **kwargs):
        calls.append(url)
        if url == CROSSREF_JOURNAL_SEARCH:
            return FakeResponse(_crossref_search(
                ("Journal of Machine Learning Research", "1532-4435", "Unmaintained records"),
                ("Unrelated Journal", "9999-9999", "Other Publisher"),
            ))
        if url == CROSSREF_JOURNAL_WORKS.format(issn="1532-4435"):
            return FakeResponse({
                "message": {
                    "total-results": 3,
                    "items": [
                        _works_item("Paper One", volume="12", issue="3"),
                        _works_item("Paper Two", volume="12", issue="3", published=(2026, 1, 1)),
                        _works_item("Paper Three", volume="12", issue="3", published=(2026, 1, 3)),
                    ],
                }
            })
        raise AssertionError(f"unexpected URL: {url} params={params}")

    monkeypatch.setattr("radar.online.http_get", fake_http_get)
    result = resolve_online("Journal of Machine Learning Research")

    assert [c.name for c in result.candidates][0] == "Journal of Machine Learning Research"
    assert result.selected is not None
    assert result.selected.issn == "1532-4435"
    assert result.selected.source == "crossref"
    assert result.tried_sources == ["crossref"]
    assert result.works is not None and result.works.ok
    assert result.works.issue == "12(3)"
    assert result.works.published == "2026-01-03"
    assert result.works.titles() == ["Paper One", "Paper Two", "Paper Three"]
    assert result.failures == []
    assert CROSSREF_JOURNAL_WORKS.format(issn="1532-4435") in calls


def test_online_resolution_openalex_fallback(monkeypatch):
    def fake_http_get(url, *, params=None, **kwargs):
        if url == CROSSREF_JOURNAL_SEARCH:
            return FakeResponse({"message": {"items": []}})
        if url == OPENALEX_SOURCE_SEARCH:
            return FakeResponse(_openalex_search(
                ("New International Journal", "2222-3333", "Example Publisher"),
            ))
        if url == CROSSREF_JOURNAL_WORKS.format(issn="2222-3333"):
            return FakeResponse({
                "message": {
                    "total-results": 1,
                    "items": [_works_item("Fallback Works Paper")],
                }
            })
        raise AssertionError(f"unexpected URL: {url} params={params}")

    monkeypatch.setattr("radar.online.http_get", fake_http_get)
    result = resolve_online("New International Journal")

    assert result.selected is not None
    assert result.selected.source == "openalex"
    assert result.selected.issn == "2222-3333"
    assert result.tried_sources == ["crossref", "openalex"]
    assert result.works is not None and result.works.ok
    assert result.works.titles() == ["Fallback Works Paper"]


def test_online_resolution_chinese_boundary_never_fakes_success(monkeypatch):
    works_called = False

    def fake_http_get(url, *, params=None, **kwargs):
        nonlocal works_called
        if url == CROSSREF_JOURNAL_SEARCH:
            return FakeResponse({"message": {"items": []}})
        if url == OPENALEX_SOURCE_SEARCH:
            return FakeResponse(_openalex_search(
                ("Journal of Computer Science and Technology", "1000-9000", "Springer"),
                ("某中文期刊", "", ""),
            ))
        if url.startswith("https://api.crossref.org/journals/"):
            works_called = True
        raise AssertionError(f"unexpected URL: {url} params={params}")

    monkeypatch.setattr("radar.online.http_get", fake_http_get)
    result = resolve_online("某中文期刊")

    assert result.selected is not None
    assert result.selected.name == "某中文期刊"
    assert result.selected.issn == ""
    assert result.works is None
    assert not works_called
    assert result.boundary_message == MANUAL_BOUNDARY_MESSAGE
    assert MANUAL_BOUNDARY_MESSAGE in result.failures


def test_append_journal_is_idempotent_and_refuses_conflicts(tmp_path):
    config_path = tmp_path / "journals.yaml"
    config_path.write_text(
        "journals:\n"
        "  - name: \"Existing Journal\"\n"
        "    aliases: [\"Existing Journal\"]\n"
        "    country: \"国外\"\n"
        "    issn: \"1111-1111\"\n"
        "    slug: \"existing-journal\"\n"
        "    source_priority: [\"crossref\"]\n",
        encoding="utf-8",
    )
    before = config_path.read_text(encoding="utf-8")

    entry = config.append_journal(
        "New International Journal",
        "2222-3333",
        publisher="Example Publisher",
        country="国外",
        path=config_path,
    )
    assert entry["slug"] == "new-international-journal"
    assert entry["source_priority"] == ["crossref", "openalex"]
    journals = config.load_journals(config_path)
    assert len(journals) == 2
    assert journals[-1]["name"] == "New International Journal"

    after_first = config_path.read_text(encoding="utf-8")
    with pytest.raises(config.JournalConfigConflict):
        config.append_journal(
            "New International Journal",
            "2222-3333",
            publisher="Example Publisher",
            path=config_path,
        )
    assert config_path.read_text(encoding="utf-8") == after_first

    with pytest.raises(config.JournalConfigConflict):
        config.append_journal(
            "Same ISSN Different Name",
            "2222-3333",
            path=config_path,
        )
    assert config_path.read_text(encoding="utf-8") == after_first
    assert before in after_first


def test_cli_resolve_online_prints_candidates_and_works(monkeypatch, capsys):
    from radar.online import OnlineCandidate, OnlineWorks
    from radar.resolver import ResolveResult

    selected = OnlineCandidate(
        name="New International Journal",
        issn="2222-3333",
        publisher="Example Publisher",
        source="crossref",
    )
    works = OnlineWorks(
        issn="2222-3333",
        ok=True,
        issue="1(1)",
        published="2026-01-01",
        papers=[__import__("radar.models", fromlist=["Paper"]).Paper(title="First Online Paper")],
    )
    result = ResolveResult(
        name="New International Journal",
        candidates=["配置候选"],
        online_attempted=True,
        online_tried_sources=["crossref"],
        online_candidates=[selected],
        online_selected=selected,
        online_works=works,
    )
    monkeypatch.setattr(cli, "resolve_journal", lambda *a, **k: result)
    rc = cli.main(["resolve", "New International Journal"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "在线候选" in out
    assert "2222-3333" in out
    assert "First Online Paper" in out


def test_cli_resolve_known_config_refuses_append(monkeypatch, capsys):
    from radar.resolver import ResolveResult

    result = ResolveResult(
        name="Existing Journal",
        journal={"name": "Existing Journal", "slug": "existing", "issn": "1111-1111"},
        ok=True,
        candidates=[],
    )
    monkeypatch.setattr(cli, "resolve_journal", lambda *a, **k: result)
    rc = cli.main(["resolve", "Existing Journal", "--append-config"])
    captured = capsys.readouterr()
    assert rc == 3
    assert "不覆盖已有项" in captured.err


def test_cli_resolve_online_append_config(monkeypatch, capsys):
    from radar.models import Paper
    from radar.online import OnlineCandidate, OnlineWorks
    from radar.resolver import ResolveResult

    selected = OnlineCandidate(
        name="New International Journal",
        issn="2222-3333",
        publisher="Example Publisher",
        source="crossref",
    )
    works = OnlineWorks(
        issn="2222-3333",
        ok=True,
        issue="1(1)",
        published="2026-01-01",
        papers=[Paper(title="First Online Paper")],
    )
    result = ResolveResult(
        name="New International Journal",
        online_attempted=True,
        online_tried_sources=["crossref"],
        online_candidates=[selected],
        online_selected=selected,
        online_works=works,
    )
    called: dict[str, str] = {}

    def fake_append(name, issn, **kwargs):
        called["name"] = name
        called["issn"] = issn
        called["publisher"] = kwargs.get("publisher", "")
        return {
            "name": name,
            "issn": issn,
            "slug": "new-international-journal",
            "country": "国外",
        }

    monkeypatch.setattr(cli, "resolve_journal", lambda *a, **k: result)
    monkeypatch.setattr(cli.config, "append_journal", fake_append)
    rc = cli.main(["resolve", "New International Journal", "--append-config"])
    out = capsys.readouterr().out
    assert rc == 0
    assert called["name"] == "New International Journal"
    assert called["issn"] == "2222-3333"
    assert "已追加" in out


def test_resolve_journal_online_wraps_discovery(monkeypatch):
    from radar import resolver
    from radar.models import Paper
    from radar.online import OnlineCandidate, OnlineResolution, OnlineWorks

    selected = OnlineCandidate(
        name="New International Journal",
        issn="2222-3333",
        publisher="Example Publisher",
        source="crossref",
    )
    works = OnlineWorks(
        issn="2222-3333",
        ok=True,
        issue="1(1)",
        published="2026-01-01",
        papers=[Paper(title="First Online Paper")],
    )
    discovery = OnlineResolution(
        name="New International Journal",
        candidates=[selected],
        selected=selected,
        works=works,
        tried_sources=["crossref"],
    )
    monkeypatch.setattr(resolver.online_sources, "resolve_online", lambda name, **kwargs: discovery)

    res = resolver.resolve_journal("New International Journal", online=True)
    assert res.online_attempted
    assert res.journal is not None
    assert res.journal["issn"] == "2222-3333"
    assert res.journal["country"] == "国外"
    assert res.issue is not None and res.issue.ok
    assert res.issue.papers[0].title == "First Online Paper"
    assert res.ok
