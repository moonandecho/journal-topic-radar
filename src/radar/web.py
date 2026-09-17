from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import argparse
import html
import json
import logging

from radar.pipeline import run_match
from radar.report import render_json

log = logging.getLogger("radar.web")

PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>期刊选题雷达</title>
<style>
:root {{ --bg:#f5f7fb; --card:#fff; --accent:#1e5eff; --ok:#0a8f4d; --warn:#b45f06; --bad:#b42318; --muted:#667085; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; background:var(--bg); color:#1f2937; }}
header {{ background:linear-gradient(135deg,#153a8a,#1e5eff); color:#fff; padding:28px 5vw 24px; }}
header h1 {{ margin:0 0 6px; font-size:28px; }}
header p {{ margin:0; opacity:.88; }}
main {{ padding:24px 5vw 60px; max-width:1280px; margin:0 auto; }}
form {{ background:var(--card); border-radius:14px; padding:18px; box-shadow:0 8px 24px rgba(16,24,40,.08); display:flex; gap:12px; flex-wrap:wrap; align-items:center; }}
input[type=text] {{ flex:1 1 420px; padding:12px 14px; border:1px solid #d0d5dd; border-radius:9px; font-size:16px; }}
select {{ padding:11px 12px; border:1px solid #d0d5dd; border-radius:9px; background:#fff; }}
button {{ padding:12px 22px; border:0; border-radius:9px; background:var(--accent); color:#fff; font-size:16px; cursor:pointer; }}
button:hover {{ filter:brightness(.95); }}
label.check {{ color:#344054; font-size:14px; white-space:nowrap; }}
.meta {{ margin:18px 0 10px; color:var(--muted); font-size:14px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(360px,1fr)); gap:16px; }}
.card {{ background:var(--card); border-radius:14px; padding:16px; box-shadow:0 6px 18px rgba(16,24,40,.07); border-top:5px solid #98a2b3; }}
.card.hit {{ border-top-color:var(--ok); }}
.card.miss {{ border-top-color:#98a2b3; }}
.card.fail {{ border-top-color:var(--bad); }}
.card h3 {{ margin:0 0 6px; font-size:17px; }}
.badge {{ display:inline-block; padding:3px 9px; border-radius:999px; font-size:12px; font-weight:700; margin-right:6px; }}
.badge.yes {{ background:#d1fadf; color:#05603a; }}
.badge.no {{ background:#eaecf0; color:#344054; }}
.badge.fail {{ background:#fee4e2; color:#912018; }}
.badge.warn {{ background:#fef0c7; color:#93370d; }}
.small {{ color:var(--muted); font-size:12.5px; }}
ul.papers {{ list-style:none; padding:0; margin:10px 0 0; }}
ul.papers li {{ border-top:1px dashed #e4e7ec; padding:9px 0; }}
ul.papers li:first-child {{ border-top:0; }}
.score {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-weight:700; }}
a {{ color:#175cd3; text-decoration:none; }}
details {{ margin-top:8px; color:var(--muted); }}
pre {{ white-space:pre-wrap; background:#f2f4f7; padding:12px; border-radius:10px; overflow:auto; }}
</style>
</head>
<body>
<header>
  <h1>📡 期刊选题雷达</h1>
  <p>抓取 10 本期刊最近一期论文，用语义匹配判断你的主题是否有相似论文。</p>
</header>
<main>
  <form method="post" action="/match">
    <input type="text" name="topic" placeholder="例如：大语言模型驱动的代码生成与漏洞检测" required>
    <select name="matcher">
      <option value="auto">matcher: auto</option>
      <option value="embedding">matcher: embedding</option>
      <option value="lexical">matcher: lexical</option>
    </select>
    <label class="check"><input type="checkbox" name="offline" value="1" checked> 离线 fixtures</label>
    <button type="submit">开始匹配</button>
  </form>
  {content}
</main>
</body>
</html>
"""


def _fmt_score(x: float) -> str:
    return f"{x:.4f}"


def render_results(report) -> str:
    d = report.to_dict()
    th = d["thresholds"]
    head = f"<div class='meta'>matcher=<b>{html.escape(d['matcher'])}</b> | strong≥{th.get('strong')} / weak≥{th.get('weak')} | {'离线样本' if d['offline'] else '在线抓取'} | {html.escape(d['generated_at'])}</div>"
    if d["degraded"]:
        reasons = "".join(f"<li>{html.escape(r)}</li>" for r in d["degradation_reasons"])
        head += f"<details open><summary><span class='badge warn'>降级</span>显式降级原因</summary><ul>{reasons}</ul></details>"
    cards = []
    for j in d["journals"]:
        if not j["fetch_ok"]:
            reasons = "".join(f"<li>{html.escape(r)}</li>" for r in j["degradation_reasons"])
            cards.append(f"<div class='card fail'><h3>{html.escape(j['journal'])}</h3><span class='badge fail'>抓取失败</span><details open><summary>失败/降级原因</summary><ul>{reasons}</ul></details></div>")
            continue
        yes = j["similar"]
        cls = "hit" if yes else "miss"
        badge = "<span class='badge yes'>是</span>" if yes else "<span class='badge no'>否</span>"
        notes = ""
        if j["degraded"]:
            notes = "<details><summary><span class='badge warn'>降级/限制</span></summary><ul>" + "".join(f"<li>{html.escape(r)}</li>" for r in j["degradation_reasons"]) + "</ul></details>"
        papers = []
        for pm in j["top_papers"]:
            mark = {"strong": "强相关", "weak": "弱相关", "irrelevant": "不相关"}.get(pm["level"], pm["level"])
            link = pm.get("url") or (f"https://doi.org/{pm.get('doi')}" if pm.get("doi") else "")
            link_html = f' <a href="{html.escape(link)}" target="_blank" rel="noopener">链接</a>' if link else ""
            papers.append(f"<li><span class='score'>{_fmt_score(pm['score'])}</span> <span class='small'>{mark}</span> {html.escape(pm['title'])}{link_html}<div class='small'>text_source={html.escape(pm.get('text_source',''))}</div></li>")
        cards.append(
            f"<div class='card {cls}'><h3>{html.escape(j['journal'])}</h3>"
            f"<div>{badge}<span class='small'>命中数 {j['hit_count']}（强 {j['strong_count']} / 弱 {j['weak_count']}）</span></div>"
            f"<div class='small'>source={html.escape(j['source'])} | 期号={html.escape(j['issue'] or '-')} | 发布={html.escape(j['published'] or '-')}</div>"
            f"{notes}<ul class='papers'>{''.join(papers) or '<li class=small>无论文记录</li>'}</ul></div>"
        )
    return head + "<div class='grid'>" + "".join(cards) + "</div>"


class Handler(BaseHTTPRequestHandler):
    server_version = "JournalTopicRadar/0.1"

    def log_message(self, fmt: str, *args) -> None:
        log.info("%s - %s", self.address_string(), fmt % args)

    def _send(self, code: int, body: str, ctype: str = "text/html; charset=utf-8") -> None:
        raw = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        try:
            p = urlparse(self.path)
            if p.path == "/":
                self._send(200, PAGE.format(content=""))
            elif p.path == "/api/match":
                qs = parse_qs(p.query)
                topic = (qs.get("topic") or [""])[0]
                offline = (qs.get("offline") or ["1"])[0] not in ("0", "false", "False")
                matcher = (qs.get("matcher") or ["auto"])[0]
                if not topic:
                    self._send(400, json.dumps({"error": "missing topic"}, ensure_ascii=False), "application/json")
                    return
                report = run_match(topic, offline=offline, matcher_prefer=matcher)
                self._send(200, render_json(report), "application/json; charset=utf-8")
            else:
                self._send(404, "not found")
        except Exception as e:
            log.exception("GET failed")
            self._send(500, f"server error: {html.escape(str(e))}")

    def do_POST(self) -> None:
        try:
            p = urlparse(self.path)
            if p.path != "/match":
                self._send(404, "not found")
                return
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length).decode("utf-8", errors="replace")
            form = parse_qs(body)
            topic = (form.get("topic") or [""])[0].strip()
            offline = (form.get("offline") or ["0"])[0] not in ("0", "false", "False", "")
            matcher = (form.get("matcher") or ["auto"])[0]
            if not topic:
                self._send(200, PAGE.format(content="<div class='meta'>请输入主题。</div>"))
                return
            report = run_match(topic, offline=offline, matcher_prefer=matcher)
            self._send(200, PAGE.format(content=render_results(report)))
        except Exception as e:
            log.exception("POST failed")
            self._send(500, PAGE.format(content=f"<div class='meta'>服务器错误：{html.escape(str(e))}</div>"))


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="期刊选题雷达 Web UI (stdlib http.server)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8099)
    args = ap.parse_args(argv)
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"journal-topic-radar web UI: http://{args.host}:{args.port} (port 8099 by default)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
