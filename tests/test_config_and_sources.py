from pathlib import Path
import json

from radar import config
from radar.sources import crossref, openalex, journal_site
from radar.sources.common import abstract_from_inverted

ROOT = config.ROOT


def test_journal_count_and_balance():
    js = config.load_journals()
    assert len(js) == 10
    assert sum(1 for j in js if j["country"] == "国内") == 5
    assert sum(1 for j in js if j["country"] == "国外") == 5
    assert len({j["slug"] for j in js}) == 10
    for j in js:
        assert j["name"]
        assert j["issn"]
        assert j["source_priority"]


def test_no_hardcoded_journal_names_in_source_code():
    names = [j["name"] for j in config.load_journals()]
    joined = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "src" / "radar").rglob("*.py"))
    for n in names:
        assert n not in joined, f"代码中出现硬编码期刊名: {n}"


def test_crossref_item_to_paper():
    item = {
        "title": ["测试标题"],
        "author": [{"given": "San", "family": "Zhang"}],
        "subject": ["AI", "Testing"],
        "abstract": "<jats:p>摘要正文</jats:p>",
        "published-print": {"date-parts": [[2026, 1, 2]]},
        "DOI": "10.1234/test",
        "volume": "12",
        "issue": "3",
    }
    p = crossref._item_to_paper(item, "12(3)")
    assert p.title == "测试标题"
    assert p.authors == ["San Zhang"]
    assert p.abstract == "摘要正文"
    assert p.published == "2026-01-02"
    assert p.doi == "10.1234/test"


def test_openalex_abstract_reconstruction():
    inv = {"世界": [0], "你好": [1], "深度学习": [2]}
    assert abstract_from_inverted(inv) == "世界 你好 深度学习"


def test_journal_site_detail_parser():
    html = """
    <html><head>
      <meta name="citation_date" content="2026-03-01">
      <meta name="citation_keywords" content="语义匹配; 期刊雷达">
    </head><body>
      <div class="article-abstract">摘要: 这是用于测试的摘要文本，长度足够以通过解析器的有效性检查。我们在这里继续补充一些字符以确保抽象文本长度达到解析器要求。</div>
    </body></html>
    """
    out = journal_site.parse_detail(html, "https://example.invalid/x")
    assert "用于测试" in out["abstract"]
    assert out["keywords"] == ["语义匹配", "期刊雷达"]
    assert out["published"] == "2026-03-01"


def test_all_fixtures_exist_and_have_min_papers():
    for j in config.load_journals():
        path = ROOT / "fixtures" / f"{j['slug']}.json"
        assert path.exists(), path
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["papers"], path
        assert len(data["papers"]) >= 5, path
        for p in data["papers"]:
            assert p["title"], path
