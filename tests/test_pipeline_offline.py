import json

from radar import config
from radar.pipeline import fetch_all, run_match, select_journals
from radar.report import render_json, render_markdown, render_table


def test_offline_fetch_all_returns_ten_issues():
    js = config.load_journals()
    issues = fetch_all(js, offline=True, workers=4)
    assert len(issues) == 10
    assert all(i.ok for i in issues)
    assert all(len(i.papers) >= 5 for i in issues)
    assert all(p.text_source for i in issues for p in i.papers)


def test_offline_match_lexical_and_outputs():
    report = run_match("大语言模型驱动的代码生成与漏洞检测", offline=True, matcher_prefer="lexical")
    assert report.topic
    assert report.matcher
    assert len(report.journals) == 10
    assert all(j.thresholds for j in report.journals)
    table = render_table(report)
    js = json.loads(render_json(report))
    md = render_markdown(report)
    assert "期刊选题雷达" in table
    assert "matcher" in table
    assert len(js["journals"]) == 10
    assert "matcher" in md
    assert "strong" in md


def test_select_journal_unknown_raises():
    js = config.load_journals()
    try:
        select_journals(["不存在的期刊"], js)
    except ValueError as e:
        assert "config/journals.yaml" in str(e)
    else:
        raise AssertionError("should raise")
