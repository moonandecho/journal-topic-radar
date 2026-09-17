# DESIGN — 期刊选题雷达

## 1. 目标与硬约束映射

| 约束 | 设计落点 |
|---|---|
| R1 运行时配置 | `config/journals.yaml` 是唯一期刊名单；代码只读配置，测试会检查 `src/radar/**/*.py` 不含期刊名字符串 |
| R2 现场解析 | `python -m radar resolve "<期刊名>"` 走 `resolver` + `pipeline.fetch_issue`；成功打印 ISSN/slug/官网/命中源/期号/发布日期，失败打印候选源与真实原因 |
| R3 最近一期 | `sources/journal_site.py` 解析国内官网当期目录；`sources/crossref.py` / `openalex.py` 按卷/期分组抓取，至少 5 篇，字段标准化为 `Paper` |
| R4 语义匹配 | `matcher.py` 提供 embedding / lexical 两种后端，`pipeline.run_match` 逐刊评分并输出 Top-3 |
| R5 三档判定 | `config/thresholds.yaml` + `report.py`；每个 `JournalMatch` 带 `matcher` 和 `thresholds` |
| R6 三种输出 | `report.py` 的 `render_table` / `render_json` / `render_markdown`；CLI `--format table|json|markdown|all` |
| R7 离线演示 | `sources/offline.py` 读取 `fixtures/<slug>.json`；`--offline` 时不创建任何真实网络请求 |
| R8 5 分钟 / smoke | `README.md` 首条代码块三条命令；`scripts/smoke.sh` 输出 PASS/FAIL 表 |
| R9 Web UI | `web.py` 只用 stdlib `http.server`；默认 8099，页面内联 CSS/HTML，无模板依赖 |
| R10 显式降级 | `IssueResult.diagnostics` + `JournalMatch.degradation_reasons` + `MatchReport.degradation_reasons`，同时进入终端/Markdown/JSON/日志；没有静默空结果路径 |

## 2. 文字版架构图

```text
                    +---------------------------+
 config/*.yaml ---> | config.py                 |
                    | - 10 journals             |
                    | - thresholds              |
                    +-------------+-------------+
                                  |
          +-----------------------+----------------------+
          |                                              |
  +-------v--------+                           +---------v---------+
  | cli.py         |                           | web.py            |
  | resolve/match  |                           | stdlib http.server|
  +-------+--------+                           +---------+---------+
          |                                              |
          +----------------------+-----------------------+
                                 |
                        +--------v---------+
                        | pipeline.py      |
                        | fetch + match    |
                        +---+----------+---+
                            |          |
              +-------------v--+   +---v----------------------+
              | sources/*.py  |   | matcher.py               |
              | crossref      |   | embedding (BGE)          |
              | openalex      |   | lexical (jieba+ngram)    |
              | journal_site  |   +--------------------------+
              | sciengine     |
              | wanfang       |
              | offline       |
              +-------+-------+
                      |
              +-------v--------+
              | models.py      |
              | Paper/Issue/   |
              | MatchReport    |
              +-------+--------+
                      |
              +-------v--------+
              | report.py      |
              | table/json/md  |
              +----------------+
```

抓取路径：
- 国内 5 刊：`source_priority: [journal_site]`，`journal_site` 先发现当期目录，再按 `parser=magtech|jos` 解析标题/作者/日期/DOI/链接；对摘要或关键词缺失的前若干篇并发抓取详情页补全。
- 国外 5 刊：`source_priority: [crossref, openalex]`，Crossref 首选按 `/journals/{issn}/works` 取最近卷期；成功后再调用 OpenAlex 按刊补摘要/关键词。Crossref 若失败则整体降级到 OpenAlex，并在 `diagnostics` 中写“主路径不可用”。
- `sciengine.py`、`wanfang.py` 是显式“未验证不伪装” adapter：首页连通可探测，但缺少可验证的期刊级响应映射时会抛出 `SourceError`，不会返回空成功。
- CNKI 未作为主路径；当前实现不依赖 CNKI。

## 3. 数据源矩阵

| 源 / adapter | 角色 | 真实连通性 | 默认是否使用 | 关键失败/边界 |
|---|---|---|---|---|
| 官网 `journal_site` | 国内主路径 | 软件学报、自动化学报、计算机研究与发展、中文信息学报、电子与信息学报均 HTTP 200 | 是，国内 5 刊 | 网站改版、详情页 403/超时；缺摘要时标 `text_source` |
| Crossref | 国外首选 | 5 刊 `/journals/{issn}/works` HTTP 200 | 是，国外 5 刊 | Elsevier 部分新文章没有 `abstract`/`issue`；issue 为空时以 volume 为标签 |
| OpenAlex | 国外备选 / 补摘要 | 5 刊 `primary_location.source.issn` 查询 HTTP 200 | 是，交叉补充 | 新文章 `abstract_inverted_index` 可能为空；匹配不到时显式写诊断 |
| SciEngine | 官方站候选 | 首页 HTTP 200 / SPA | 否 | 未找到经验证的期刊目录 API，若配置为路由会失败并列出 URL |
| 万方 | 中文检索候选 | 首页 HTTP 200 | 否 | JS 壳页面；无经验证的当期目录/摘要 JSON，不允许冒充成功 |
| CNKI | 明确排除 | `navi.cnki.net` 空响应需 JS/cookie | 否 | 不作为主路径 |
| `offline` | 离线演示 | 读取 `fixtures/*.json` | 是（`--offline`） | 缺 fixture 时返回 `ok=False` 并显式失败 |

国内刊替换记录详见 `docs/source-evidence.md`：
计算机学报 → 计算机研究与发展；电子学报 → 电子与信息学报；中国科学:信息科学 → 中文信息学报；
JMLR（Crossref total=0）与 IJCV（同卷期不足 5 篇）替换为 IEEE TKDE。最终保持国内 5 + 国外 5。

## 4. 文档标准化与文本来源

`Paper` 字段：`title / authors / abstract / keywords / published / url / doi / issue / source / text_source`。
匹配文本构造严格按需求：

1. 有摘要：`title + keywords + abstract`（有关键词时 `title+keywords+abstract`，无关键词时 `title+abstract`）。
2. 无摘要、有关键词：`title + keywords`，`text_source=title+keywords`。
3. 只有标题：`title`，`text_source=title`。

示例：Pattern Recognition 的 Elsevier 新文章 Crossref/OpenAlex 都缺摘要，离线样本中仍保留标题和 OpenAlex 关键词，
报告显示 `text_source=title+keywords` 与“有 N 篇未获取到摘要”诊断。

## 5. Matcher 设计

### 5.1 后端 B：embedding（优先）

- 模型：`sentence-transformers` + `BAAI/bge-small-zh-v1.5`。
- 下载：强制默认 `HF_ENDPOINT=https://hf-mirror.com`；模型缓存写入项目内 `models/`。
  `models/bge-small-zh-v1.5` 是指向 HF 缓存快照的软链，断网时可复用。
- 查询侧使用 BGE v1.5 推荐检索指令：`为这个句子生成表示以用于检索相关文章：`。
- 论文侧直接编码；全部向量 `normalize_embeddings=True`，相似度=余弦。
- 阈值：`config/thresholds.yaml` 中 `strong=0.75`、`weak=0.60`。

### 5.2 后端 A：lexical（显式降级兜底）

- 分词：jieba 中文词 + 中文 unigram/bigram + 英文/数字词，过滤常见停用词。
- 加权：BM25 风格 `idf * tf*(k1+1)/(tf+k1*(1-b+b*dl/avgdl))`，`k1=1.5, b=0.75`。
- 相似度：查询向量与文档向量做余弦，限制在 `[0,1]`。
- 当 B 不可加载时自动降级；`MatchReport.degradation_reasons` 和输出头部都会出现
  `matcher=lexical (degraded: 原因)`。词法后端绝不写成 embedding 后端。

### 5.3 三档判定

```text
score >= strong  -> strong
score >= weak    -> weak
otherwise        -> irrelevant

命中数 = count(strong or weak)
期刊是否相似 = 命中数 >= 1
```

每个期刊结论都携带 `matcher`、`strong`、`weak`；Markdown 每刊单独一行，JSON 每刊 `thresholds/matcher` 字段，终端表格每行下方打印“判定基线”。

## 6. 阈值标定过程

### 6.1 Lexical 标定

脚本：`scripts/calibrate_lexical.py`；样本来自真实 `fixtures/*.json`。
流程：

1. 造 9 组强正例：主题与真实论文标题明确同义，例如
   `大语言模型的源代码漏洞检测` ↔ `基于大语言模型的源代码漏洞检测方法`。
2. 另造 10 组强负例：主题与选中的真实论文标题来自完全不同方向，例如
   `量子计算硬件设计` ↔ `基于大语言模型的源代码漏洞检测方法`。
3. 有 2 组跨语言/弱关联正例不参与 strong 边界，只用于观察：`联邦学习通信压缩`、`异常检测`。
4. 用 lexical 后端对每对打分，取负例最大值与排除弱关联后的正例最小值。
5. 阈值公式：`weak = neg_max + 0.10`，`strong = pos_min + 0.10`。

真实运行结果（运行 `scripts/calibrate_lexical.py` 可复现；完整日志见 `docs/calibration-lexical.txt`）：

| 统计 | 值 |
|---|---:|
| 负例最大分 | 0.0127 |
| 正例最小分（排除弱关联） | 0.2048 |
| 弱相关阈值 | 0.11 |
| 强相关阈值 | 0.30 |
| 未参与 strong 边界的弱关联正例最高分 | 0.0911 |

因此 `config/thresholds.yaml` 中 lexical 使用 `strong=0.30, weak=0.11`。该阈值不是 case-by-case if，也不在代码里写死：
修改 YAML 即可调整，所有输出会跟着显示新阈值。

### 6.2 Embedding 阈值

按需求给定 `strong≥0.75 / weak≥0.60`。BGE 中文模型对跨语言主题-英文论文的余弦通常低于同语言对，
因此在线中文主题命中英文刊时容易出现“不相关”或“弱相关”的诚实结果；报告保留分数，不做后处理抬分。

## 7. 显式降级策略（R10）

1. **数据源级**：`pipeline.fetch_issue` 按 `source_priority` 顺序尝试；每个失败原因写入 `IssueResult.diagnostics`。
   所有源失败时返回 `ok=False`，`JournalMatch` 显示 `fetch_ok=false` 和失败原因，不产生“全部不相关”的假结论。
2. **主/备切换级**：Crossref 失败改用 OpenAlex 时，追加“主路径不可用，已降级到备选源”。
3. **字段级**：摘要/关键词缺失时在 `diagnostics` 写“有 N 篇未获取到摘要，文本使用标题+关键词”，
   `text_source` 记录真实来源；报告顶部/行内均能看见。
4. **Matcher 级**：BGE 加载失败自动降级 lexical，`MatchReport.degraded=true`，
   `degradation_reasons` 出现在终端头部、Markdown 顶部、JSON、stderr 日志。
5. **离线样本级**：`--offline` 下 fixture 缺失即 `ok=False`，不联网回退，不静默。

## 8. 已知边界与误判方向

- **跨语言分数被压缩**：BGE 中文模型对中英对照语义的余弦通常低于中文-中文；lexical 对中英文本基本为 0。
  当前实现选择“忠实展示分数”，不把词法分数伪装成语义分数。
- **Elsevier 新文章缺摘要**：Crossref/OpenAlex 的 `abstract_inverted_index` 可能为空；标题+关键词可用但信息量弱，
  `text_source` 会提示，阈值可能低估真正相关论文。
- **“最近一期”的定义**：Crossref 对部分 Elsevier 刊只给 volume、不给 issue；实现以最新 volume 为“最近一期”标签，
  IJCV 曾因最新 issue 同卷期不足 5 篇被替换为 TKDE。
- **数据库更新延迟**：OpenAlex 与 Crossref 的排序时间不同，很可能补不到少数 DOI 的摘要；诊断会写明补全数量。
- **官网 HTML 结构变化**：`journal_site` 用通用 class 选择器 + 详情页补全；如果官网改版，`resolve` 会失败并给出 URL/原因，
  需要现场维护 parser 或更换可抓刊。
- **反过拟合**：代码没有逐刊 if/白名单，也没有把面试主题原文写进代码；所有刊名、来源和阈值均来自 YAML，
  测试还检查了 `src/radar` 中不含配置中的期刊名。

## 9. 扩展点

1. 新增数据源：实现 `sources/<new>.py` 的 `fetch_latest(ref) -> IssueResult`，在 `sources/__init__.py` 注册，
   在 `journals.yaml` 的 `source_priority` 引用。
2. 新增官网 parser：在 `journal_site.py` 增加 parser 分支，并把 `parser` 字段写进期刊配置。
3. 新 matcher：实现 `MatchBackend.score(topic, texts)` 并接入 `make_backend`；报告会自动输出名称/阈值/降级原因。
4. 新输出格式：在 `report.py` 增加 render 函数，在 `cli.py` 扩展 `--format` 选项。
5. 缓存与增量：可在 `pipeline.fetch_issue` 前加 `fixtures`/SQLite 缓存；当前优先级是现场可解释、失败显式。
