from radar.resolver import resolve_journal


def test_resolve_known_offline_has_identifiers_and_issue():
    res = resolve_journal("软件学报", offline=True)
    assert res.ok
    assert res.journal is not None
    assert res.identifiers()["issn"] == "1000-9825"
    assert res.issue is not None
    assert len(res.issue.papers) >= 5


def test_resolve_unknown_lists_candidates_and_failure_reasons():
    res = resolve_journal("完全不存在的刊名")
    assert not res.ok
    assert res.journal is None
    assert len(res.candidates) == 10
    assert res.failures
