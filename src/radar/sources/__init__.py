from .common import SourceError
from . import crossref, openalex, journal_site, sciengine, wanfang, offline


def get_source(name: str):
    mapping = {
        "crossref": crossref,
        "openalex": openalex,
        "journal_site": journal_site,
        "sciengine": sciengine,
        "wanfang": wanfang,
        "offline": offline,
    }
    if name not in mapping:
        raise SourceError(name, f"未知数据源: {name}")
    return mapping[name]
