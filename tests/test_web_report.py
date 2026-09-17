from radar import config
from radar.pipeline import run_match
from radar.report import render_markdown, render_json, render_table
from radar.web import PAGE, render_results


def test_web_renders_cards_without_third_party_framework():
    report = run_match("知识图谱", offline=True, matcher_prefer="lexical")
    html = render_results(report)
    assert "<div class='grid'>" in html
    assert "命中数" in html
    assert "matcher" in html
    page = PAGE.format(content="")
    # stdlib server module is imported; this test avoids binding a socket.
    assert "期刊选题雷达" in page
