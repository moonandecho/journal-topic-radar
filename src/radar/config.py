from __future__ import annotations
from pathlib import Path
from typing import Any
import hashlib
import os
import re
import tempfile
import unicodedata
import yaml

ROOT = Path(__file__).resolve().parents[2]

_CJK_RE = re.compile(r"[\u3400-\u9fff]")


class JournalConfigConflict(RuntimeError):
    """Raised when appending a journal would overwrite an existing identity."""


def project_root() -> Path:
    return ROOT


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_journals(path: str | Path | None = None) -> list[dict[str, Any]]:
    p = Path(path) if path else ROOT / "config" / "journals.yaml"
    data = _load_yaml(p)
    journals = data.get("journals") or []
    if not isinstance(journals, list) or not journals:
        raise RuntimeError(f"journals config empty or invalid: {p}")
    for idx, j in enumerate(journals):
        j.setdefault("index", idx)
        j.setdefault("aliases", [])
        j.setdefault("country", "")
        j.setdefault("issn", "")
        j.setdefault("official_site", "")
        j.setdefault("slug", "")
        j.setdefault("source_priority", [])
        j.setdefault("site_url", j.get("official_site", ""))
        j.setdefault("parser", "")
        j.setdefault("enrich_limit", 8)
    return journals


def load_thresholds(path: str | Path | None = None) -> dict[str, dict[str, float]]:
    p = Path(path) if path else ROOT / "config" / "thresholds.yaml"
    data = _load_yaml(p)
    if "embedding" not in data and "lexical" in data:
        data = {"embedding": data.get("lexical", {}), "lexical": data.get("lexical", {})}
    for key in ("embedding", "lexical"):
        data.setdefault(key, {"strong": 0.75, "weak": 0.60})
        data[key].setdefault("strong", 0.75)
        data[key].setdefault("weak", 0.60)
    return data


def find_journal(name: str, journals: list[dict[str, Any]] | None = None) -> dict[str, Any] | None:
    if journals is None:
        journals = load_journals()
    q = "".join((name or "").lower().split())
    best = None
    best_len = -1
    for j in journals:
        names = [j.get("name", ""), j.get("slug", ""), j.get("issn", "")] + list(j.get("aliases") or [])
        for n in names:
            if not n:
                continue
            nn = "".join(str(n).lower().split())
            if q == nn or q in nn or nn in q:
                # Prefer the most specific match (longest configured name)
                if len(nn) > best_len:
                    best = j
                    best_len = len(nn)
    return best


def source_priority(journal: dict[str, Any]) -> list[str]:
    p = journal.get("source_priority") or []
    if p:
        return list(p)
    return ["journal_site"] if journal.get("country") == "国内" else ["crossref", "openalex"]


def is_cjk_text(value: str) -> bool:
    return bool(_CJK_RE.search(value or ""))


def normalize_issn(value: Any) -> str:
    raw = re.sub(r"[^0-9Xx]", "", str(value or "")).upper()
    if len(raw) == 8:
        return f"{raw[:4]}-{raw[4:]}"
    return raw


def _normal_name(value: Any) -> str:
    return "".join(ch for ch in str(value or "").casefold() if ch.isalnum())


def slugify(value: str) -> str:
    """Create a stable ASCII slug; non-ASCII-only names fall back to a short hash."""
    text = unicodedata.normalize("NFKD", value or "")
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if text:
        return text
    digest = hashlib.sha1((value or "").encode("utf-8")).hexdigest()[:10]
    return f"journal-{digest}"


def infer_country(name: str, publisher: str = "") -> str:
    """Best-effort country classification without relying on a hardcoded journal list."""
    if is_cjk_text(name) or is_cjk_text(publisher):
        return "国内"
    return "国外"


def _existing_identity(journal: dict[str, Any]) -> list[str]:
    values = [
        journal.get("name"),
        journal.get("slug"),
        journal.get("issn"),
        *(journal.get("aliases") or []),
    ]
    return [str(v) for v in values if v]


def _find_conflict(name: str, issn: str, journals: list[dict[str, Any]]) -> str:
    wanted_name = _normal_name(name)
    wanted_issn = normalize_issn(issn)
    for journal in journals:
        j_name = str(journal.get("name") or "")
        j_issn = normalize_issn(journal.get("issn"))
        if wanted_name and any(_normal_name(v) == wanted_name for v in _existing_identity(journal)):
            return f"配置中已存在同名称/别名期刊: {j_name} (ISSN={j_issn or '-'})"
        if wanted_issn and j_issn and wanted_issn == j_issn:
            return f"配置中已存在同 ISSN 期刊: {j_name} (ISSN={j_issn})"
    return ""


def unique_slug(name: str, *, existing: list[dict[str, Any]] | None = None) -> str:
    base = slugify(name)
    journals = existing if existing is not None else load_journals()
    used = {str(j.get("slug") or "") for j in journals}
    if base not in used:
        return base
    for idx in range(2, 1000):
        candidate = f"{base}-{idx}"
        if candidate not in used:
            return candidate
    digest = hashlib.sha1((name or "").encode("utf-8")).hexdigest()[:8]
    return f"{base}-{digest}"


def build_journal_entry(name: str, issn: str, *, publisher: str = "", country: str | None = None,
                        official_site: str = "", source_priority: list[str] | None = None,
                        existing: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Build a config entry for a newly discovered journal."""
    clean_name = str(name or "").strip()
    clean_issn = normalize_issn(issn)
    if not clean_name:
        raise ValueError("追加期刊时 name 不能为空")
    return {
        "name": clean_name,
        "aliases": [clean_name],
        "country": country or infer_country(clean_name, publisher),
        "issn": clean_issn,
        "official_site": str(official_site or "").strip(),
        "site_url": str(official_site or "").strip(),
        "slug": unique_slug(clean_name, existing=existing),
        "parser": "",
        "source_priority": list(source_priority or ["crossref", "openalex"]),
        "publisher": str(publisher or "").strip(),
    }


def _dump_yaml_list_item(entry: dict[str, Any]) -> str:
    text = yaml.safe_dump([entry], allow_unicode=True, sort_keys=False, default_flow_style=False)
    return "\n".join(("  " + line) if line.strip() else line for line in text.rstrip().splitlines())


def append_journal(name: str, issn: str, *, publisher: str = "", country: str | None = None,
                   official_site: str = "", source_priority: list[str] | None = None,
                   path: str | Path | None = None) -> dict[str, Any]:
    """Append one journal to config/journals.yaml without overwriting existing identities.

    Raises JournalConfigConflict when the name/alias/ISSN already exists.
    """
    p = Path(path) if path else ROOT / "config" / "journals.yaml"
    data = _load_yaml(p)
    journals = data.get("journals") or []
    if not isinstance(journals, list):
        raise RuntimeError(f"journals config invalid: {p}")
    conflict = _find_conflict(name, issn, journals)
    if conflict:
        raise JournalConfigConflict(conflict)
    entry = build_journal_entry(
        name,
        issn,
        publisher=publisher,
        country=country,
        official_site=official_site,
        source_priority=source_priority,
        existing=journals,
    )
    original = p.read_text(encoding="utf-8")
    if original and not original.endswith("\n"):
        original += "\n"
    updated = original + "\n" + _dump_yaml_list_item(entry) + "\n"
    # Validate the whole document before replacing the original file.
    try:
        loaded = yaml.safe_load(updated) or {}
        loaded_journals = loaded.get("journals") or []
        if not any(_normal_name(j.get("name")) == _normal_name(entry["name"]) for j in loaded_journals):
            raise ValueError("追加后 YAML 校验未找到新条目")
    except Exception as e:
        raise RuntimeError(f"追加期刊后 YAML 校验失败，未写入: {e}") from e
    p.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(p.parent), delete=False) as f:
        f.write(updated)
        tmp_name = f.name
    Path(tmp_name).replace(p)
    return entry


def hf_endpoint() -> str:
    return os.environ.get("HF_ENDPOINT", "https://hf-mirror.com")
