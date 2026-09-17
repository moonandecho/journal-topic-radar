from __future__ import annotations
from typing import Iterable
import io
import json
import textwrap

from radar.models import MatchReport, JournalMatch


def _bar(score: float, width: int = 10) -> str:
    n = max(0, min(width, int(round(score * width))))
    return "█" * n + "·" * (width - n)


def _fit(s: str, width: int) -> str:
    s = (s or "").replace("\n", " ")
    if len(s) <= width:
        return s + " " * (width - len(s))
    return s[: max(1, width - 1)] + "…"


def _degrade_headline(report: MatchReport, prefix: str = "") -> str:
    if not report.degraded:
        return ""
    reasons = "；".join(report.degradation_reasons[:2]) or "存在降级但未记录原因"
    return f"{prefix}matcher={report.matcher} (degraded: {reasons})"


def render_table(report: MatchReport) -> str:
    out = io.StringIO()
    head = f"期刊选题雷达 | 主题: {report.topic}"
    out.write(head + "\n")
    out.write("=" * max(72, len(head)) + "\n")
    if report.degraded:
        out.write(_degrade_headline(report, "⚠ ") + "\n")
    th = report.thresholds
    out.write(f"matcher={report.matcher} | 阈值: strong≥{th.get('strong')}, weak≥{th.get('weak')} | offline={report.offline}\n")
    out.write("-" * 110 + "\n")
    out.write(f"{'期刊':<28} {'命中':<6} {'命中数':<6} {'强/弱':<8} {'最近期号':<16} Top-3 论文\n")
    out.write("-" * 110 + "\n")
    for j in report.journals:
        if not j.fetch_ok:
            out.write(f"{_fit(j.journal,27)} {'FAIL':<6} {'-':<6} {'-':<8} {_fit(j.issue or '-',15)} 抓取失败/降级: {'；'.join(j.degradation_reasons[:1])}\n")
            continue
        hit = "是" if j.similar else "否"
        out.write(f"{_fit(j.journal,27)} {hit:<6} {j.hit_count:<6} {str(j.strong_count)+'/'+str(j.weak_count):<8} {_fit(j.issue or '-',15)} \n")
        out.write(f"    判定基线: matcher={j.matcher} | strong≥{j.thresholds.get('strong')} | weak≥{j.thresholds.get('weak')}\n")
        for pm in j.top_papers:
            mark = {"strong": "强", "weak": "弱", "irrelevant": "无"}.get(pm.level, pm.level)
            out.write(f"    [{mark}] {pm.score:.3f} {_bar(pm.score)} {_fit(pm.paper.title,70)} {pm.paper.url}\n")
        for r in j.degradation_reasons[:2]:
            out.write(f"    ⚠ 降级/限制: {r}\n")
    out.write("-" * 110 + "\n")
    if report.degradation_reasons:
        out.write("降级与数据源说明:\n")
        for r in report.degradation_reasons:
            out.write(f"  - {r}\n")
    out.write(f"生成时间: {report.generated_at}\n")
    return out.getvalue()


def render_json(report: MatchReport) -> str:
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)


def render_markdown(report: MatchReport) -> str:
    lines: list[str] = []
    lines.append(f"# 期刊选题雷达报告：{report.topic}")
    lines.append("")
    if report.degraded:
        lines.append(f"> **降级标注**：`matcher={report.matcher}`")
        for r in report.degradation_reasons:
            lines.append(f"> - {r}")
        lines.append("")
    else:
        lines.append("> 本次运行未触发降级。")
        lines.append("")
    th = report.thresholds
    lines.append(f"- 生成时间：{report.generated_at}")
    lines.append(f"- matcher 后端：`{report.matcher}`（{report.backend}）")
    lines.append(f"- 判定阈值：strong ≥ **{th.get('strong')}**，weak ≥ **{th.get('weak')}**；期刊级命中 = 命中数 ≥ 1")
    lines.append(f"- 数据模式：{'offline fixtures' if report.offline else 'online'}")
    lines.append("")
    lines.append("## 期刊结论总览")
    lines.append("")
    lines.append("| 期刊 | 是否命中 | 命中数 | 强/弱 | 最近期号 | 数据源 | 降级 |")
    lines.append("|---|---:|---:|---:|---|---|---|")
    for j in report.journals:
        deg = "是" if j.degraded else "否"
        lines.append(f"| {j.journal} | {'是' if j.similar else '否'} | {j.hit_count} | {j.strong_count}/{j.weak_count} | {j.issue or '-'} | {j.source} | {deg} |")
    lines.append("")
    for j in report.journals:
        lines.append(f"## {j.journal}")
        lines.append("")
        if not j.fetch_ok:
            lines.append("**抓取失败，未参与相似度判定**。")
            for r in j.degradation_reasons:
                lines.append(f"- 原因：{r}")
            lines.append("")
            continue
        lines.append(f"- 源：`{j.source}`；期号：{j.issue or '-'}；发布日期：{j.published or '-'}")
        lines.append(f"- 是否相似主题论文：**{'是' if j.similar else '否'}**；命中数：{j.hit_count}；阈值：strong≥{j.thresholds.get('strong')}, weak≥{j.thresholds.get('weak')}；matcher：`{j.matcher}`")
        if j.degradation_reasons:
            lines.append(f"- 降级/限制：{'；'.join(j.degradation_reasons)}")
        lines.append("")
        lines.append("| 排名 | 标题 | 分数 | 判定 | 链接 |")
        lines.append("|---:|---|---:|---|---|")
        for i, pm in enumerate(j.top_papers, 1):
            mark = {"strong": "强相关", "weak": "弱相关", "irrelevant": "不相关"}.get(pm.level, pm.level)
            title = (pm.paper.title or "").replace("|", "\\|")
            link = pm.paper.url or (f"https://doi.org/{pm.paper.doi}" if pm.paper.doi else "")
            lines.append(f"| {i} | {title} | {pm.score:.4f} | {mark} | {link} |")
        lines.append("")
        if j.diagnostics:
            lines.append("<details><summary>数据源诊断</summary>")
            lines.append("")
            for d in j.diagnostics:
                lines.append(f"- {d}")
            lines.append("")
            lines.append("</details>")
            lines.append("")
    return "\n".join(lines)
