from radar import config
from radar.pipeline import run_match
from radar.report import render_markdown, render_json, render_table
from radar.web import PAGE, render_form, render_results


def test_web_renders_cards_without_third_party_framework():
    report = run_match("知识图谱", offline=True, matcher_prefer="lexical")
    html = render_results(report)
    assert "<div class='grid'>" in html
    assert "命中数" in html
    assert "matcher" in html
    page = PAGE.format(form=render_form(), content="")
    # stdlib server module is imported; this test avoids binding a socket.
    assert "期刊选题雷达" in page
    assert '<form method="post" action="/match">' in page


def test_web_form_echoes_actual_run_params():
    """结果页必须回显本次真实生效的参数。

    否则输入框回到空状态、勾选框回到默认值，用户会误判"参数没生效 / 没查过"
    （真实踩过：在线跑完的截图看起来像离线默认态）。
    """
    html = render_form("知识图谱补全", "embedding", offline=False)
    assert 'value="知识图谱补全"' in html
    assert '<option value="embedding" selected>' in html
    assert '<input type="checkbox" name="offline" value="1">' in html  # 未勾选 = 在线
    assert html.count(" selected>") == 1

    html2 = render_form("知识图谱补全", "lexical", offline=True)
    assert '<option value="lexical" selected>' in html2
    assert 'value="1" checked' in html2  # 勾选 = 离线
    assert html2.count(" selected>") == 1

    # 主题里的 HTML 必须转义，不能注入页面
    escaped = render_form("<script>alert(1)</script>")
    assert "<script>" not in escaped
    assert "&lt;script&gt;" in escaped
