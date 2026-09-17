from __future__ import annotations
from pathlib import Path
import argparse
import logging
import os
import sys

from radar import config
from radar.pipeline import run_match, select_journals
from radar.resolver import resolve_journal
from radar.report import render_json, render_markdown, render_table

log = logging.getLogger("radar.cli")


def _setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("jieba").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def _print_config_candidates(candidates: list[str]) -> None:
    print("配置内候选：")
    for c in candidates:
        print(f"  - {c}")


def _print_online_candidates(candidates: list[object]) -> None:
    print("在线候选（名称 / ISSN / 出版方 / 命中源）：")
    if not candidates:
        print("  - （无）")
        return
    for idx, c in enumerate(candidates, 1):
        print(
            f"  {idx}. {getattr(c, 'name', '')} | "
            f"ISSN={getattr(c, 'issn', '') or '-'} | "
            f"出版方={getattr(c, 'publisher', '') or '-'} | "
            f"命中源={getattr(c, 'source', '') or '-'}"
        )


def _print_online_works(works: object | None) -> None:
    if works is None:
        print("在线最近记录: 未抓取（未获得可用 ISSN）")
        return
    if getattr(works, "ok", False):
        print(
            f"在线最近记录: 期号={getattr(works, 'issue', '') or '-'} | "
            f"发布日期={getattr(works, 'published', '') or '-'}"
        )
        for p in list(getattr(works, "papers", []) or [])[:3]:
            print(f"  - {getattr(p, 'title', '')}")
        return
    print(f"在线最近记录抓取失败: {getattr(works, 'error', '未知错误')}")


def _cmd_resolve_online(args: argparse.Namespace, res) -> int:
    print("==" * 20)
    print(f"期刊名: {res.name}")
    print("配置命中: 否（已继续在线解析）")
    print(f"在线尝试源: {res.online_tried_sources or res.tried_sources}")
    _print_config_candidates(res.candidates)
    _print_online_candidates(list(res.online_candidates or []))

    selected = res.online_selected
    if selected is not None:
        selected_issn = getattr(selected, "issn", "") or ""
        label = "在线解析成功" if selected_issn else "在线解析候选（无 ISSN，未成功抓取）"
        print(
            f"{label}: {getattr(selected, 'name', '')} | "
            f"ISSN={selected_issn or '-'} | "
            f"出版方={getattr(selected, 'publisher', '') or '-'} | "
            f"命中源={getattr(selected, 'source', '') or '-'}"
        )
    else:
        print("在线解析未成功: 没有名称精确匹配的在线候选")
    _print_online_works(res.online_works)

    failures = list(res.online_failures or [])
    if res.online_boundary_message:
        failures = [f for f in failures if f != res.online_boundary_message]
    if failures:
        print("在线失败/边界原因：")
        for f in failures:
            print(f"  - {f}")
    if res.online_boundary_message:
        print(res.online_boundary_message)

    append_requested = bool(getattr(args, "append_config", False))
    if append_requested:
        if selected is None or not getattr(selected, "issn", ""):
            print(
                "--append-config 失败: 在线解析未获得 ISSN，无法自动追加；"
                "请按 README 三步手工添加（提供官网 URL + parser）",
                file=sys.stderr,
            )
            return 2
        try:
            entry = config.append_journal(
                getattr(selected, "name", res.name),
                getattr(selected, "issn", ""),
                publisher=getattr(selected, "publisher", "") or "",
                official_site=getattr(selected, "homepage", "") or "",
            )
        except config.JournalConfigConflict as e:
            print(f"--append-config 失败: {e}", file=sys.stderr)
            return 3
        except Exception as e:
            print(f"--append-config 失败: {type(e).__name__}: {e}", file=sys.stderr)
            return 2
        print(
            f"[append-config] 已追加: {entry['name']} | ISSN={entry['issn']} | "
            f"slug={entry['slug']} | country={entry['country']}"
        )

    if selected is not None and getattr(selected, "issn", ""):
        if res.online_works is not None and getattr(res.online_works, "ok", False):
            return 0
        return 1
    return 2


def cmd_resolve(args: argparse.Namespace) -> int:
    res = resolve_journal(
        args.journal_name,
        offline=getattr(args, "offline", False),
        online=not getattr(args, "offline", False),
    )
    if res.online_attempted:
        return _cmd_resolve_online(args, res)
    if not res.journal:
        print(f"解析失败: 期刊 '{res.name}' 不在 config/journals.yaml")
        _print_config_candidates(res.candidates)
        print("失败原因：")
        for f in res.failures:
            print(f"  - {f}")
        return 2
    if getattr(args, "append_config", False):
        print(
            "--append-config 失败: 该期刊已在 config/journals.yaml 中，不覆盖已有项；"
            "如需修改请手工编辑配置，",
            file=sys.stderr,
        )
        return 3
    ident = res.identifiers()
    print("==" * 20)
    print(f"期刊名: {ident['name']}")
    print(f"可抓取标识: ISSN={ident['issn'] or '-'} | slug={ident['slug']} | 官网={ident['official_site'] or '-'}")
    print(f"配置命中: {ident['country']} | source_priority={res.tried_sources}")
    issue = res.issue
    if res.ok and issue is not None:
        print(f"命中源: {issue.source}")
        print(f"最近一期: 期号={issue.issue or '-'} | 发布日期={issue.published or '-'} | 论文数={len(issue.papers)}")
        for p in issue.papers[:3]:
            print(f"  - {p.title}")
        return 0
    print("命中源: 无（未成功解析）")
    print("尝试过的候选与失败原因：")
    if res.tried_sources:
        for s in res.tried_sources:
            print(f"  - 候选源: {s}")
    for d in res.failures:
        print(f"    失败原因: {d}")
    return 1


def _write_outputs(report, prefix: str) -> None:
    p = Path(prefix)
    p.parent.mkdir(parents=True, exist_ok=True)
    json_path = p.with_suffix(".json")
    md_path = p.with_suffix(".md")
    json_path.write_text(render_json(report), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    print(f"[written] {json_path}")
    print(f"[written] {md_path}")


def cmd_match(args: argparse.Namespace) -> int:
    try:
        report = run_match(
            args.topic,
            journal_names=args.journal,
            offline=args.offline,
            matcher_prefer=args.matcher,
            top_k=args.top_k,
        )
    except Exception as e:
        print(f"匹配失败: {e}", file=sys.stderr)
        return 2
    fmt = args.format
    if fmt in ("table", "all"):
        print(render_table(report), end="")
    if fmt in ("json", "all"):
        if fmt == "all":
            print("\n----- JSON -----")
        print(render_json(report))
    if fmt in ("markdown", "all"):
        if fmt == "all":
            print("\n----- MARKDOWN -----")
        print(render_markdown(report))
    if args.output:
        _write_outputs(report, args.output)
    # Explicit logging of degradations so logs also carry them.
    if report.degraded:
        for r in report.degradation_reasons:
            log.warning("DEGRADED: %s", r)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m radar", description="期刊选题雷达")
    p.add_argument("--verbose", action="store_true", help="打印调试日志")
    sub = p.add_subparsers(dest="command", required=True)

    r = sub.add_parser("resolve", help="解析期刊名并抓取最近一期标识")
    r.add_argument("journal_name", help="期刊名（支持 config 中的别名）")
    r.add_argument("--offline", action="store_true", help="只使用离线样本解析")
    r.add_argument("--append-config", action="store_true",
                   help="在线解析成功后把该刊追加到 config/journals.yaml（不覆盖已有项）")
    r.set_defaults(func=cmd_resolve)

    m = sub.add_parser("match", help="对主题执行逐刊语义匹配")
    m.add_argument("--topic", required=True, help="用户想写的论文主题")
    m.add_argument("--offline", action="store_true", help="使用 fixtures/ 真实样本，全程不联网")
    m.add_argument("--format", choices=["table", "json", "markdown", "all"], default="table", help="输出格式")
    m.add_argument("--output", default="", help="输出文件前缀，例如 docs/demo；会写 .json 与 .md")
    m.add_argument("--matcher", choices=["auto", "embedding", "lexical"], default="auto", help="matcher 后端选择")
    m.add_argument("--journal", action="append", default=[], help="只匹配指定期刊，可重复；缺省为全部 10 本")
    m.add_argument("--top-k", type=int, default=3, help="每刊输出 Top-K 相似论文")
    m.set_defaults(func=cmd_match)
    return p


def main(argv: list[str] | None = None) -> int:
    # Requirement: BGE downloads go through the mirror.
    os.environ.setdefault("HF_ENDPOINT", config.hf_endpoint())
    parser = build_parser()
    args = parser.parse_args(argv)
    _setup_logging(getattr(args, "verbose", False))
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
