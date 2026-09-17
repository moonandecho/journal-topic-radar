# 配置外期刊在线解析真实输出

- 运行环境：仓库内 `.venv`，Python `3.12.3`
- 运行方式：`python -m radar resolve`（等价于 `.venv/bin/python -m radar resolve`）
- 数据源：Crossref `journals?query=...&rows=5`；Crossref 无精确命中时继续 OpenAlex `sources?search=...&per-page=5`；拿到 ISSN 后请求 Crossref `journals/{issn}/works?sort=published&order=desc&rows=15`
- 时间：2026-09-17（运行环境时间）

## 1. 国际刊：Journal of Machine Learning Research

命令：

```bash
.venv/bin/python -m radar resolve "Journal of Machine Learning Research"
```

退出码：`1`；耗时：`2.69s`。

真实 stdout：

```text
========================================
期刊名: Journal of Machine Learning Research
配置命中: 否（已继续在线解析）
在线尝试源: ['crossref']
配置内候选：
  - 软件学报 | ISSN=1000-9825 | slug=jos | aliases=软件学报, Journal of Software, JOS
  - 自动化学报 | ISSN=0254-4156 | slug=aas | aliases=自动化学报, Acta Automatica Sinica, AAS
  - 计算机研究与发展 | ISSN=1000-1239 | slug=crad | aliases=计算机研究与发展, Journal of Computer Research and Development, JCRD
  - 中文信息学报 | ISSN=1003-0077 | slug=jcip | aliases=中文信息学报, Journal of Chinese Information Processing, JCIP
  - 电子与信息学报 | ISSN=1009-5896 | slug=jeit | aliases=电子与信息学报, Journal of Electronics & Information Technology, JEIT
  - IEEE Transactions on Pattern Analysis and Machine Intelligence | ISSN=0162-8828 | slug=tpami | aliases=IEEE TPAMI, TPAMI, IEEE Transactions on Pattern Analysis and Machine Intelligence
  - Pattern Recognition | ISSN=0031-3203 | slug=pattern_recognition | aliases=Pattern Recognition, PR
  - Information Sciences | ISSN=0020-0255 | slug=information_sciences | aliases=Information Sciences, INS
  - IEEE Transactions on Knowledge and Data Engineering | ISSN=1041-4347 | slug=tkde | aliases=IEEE TKDE, TKDE, IEEE Transactions on Knowledge and Data Engineering
  - IEEE Transactions on Neural Networks and Learning Systems | ISSN=2162-237X | slug=tnnls | aliases=IEEE TNNLS, TNNLS, IEEE Transactions on Neural Networks and Learning Systems
在线候选（名称 / ISSN / 出版方 / 命中源）：
  1. Journal of Machine Learning Research | ISSN=1532-4435 | 出版方=Unmaintained records | 命中源=crossref
  2. Journal of Geophysical Research Machine Learning and Computation | ISSN=2993-5210 | 出版方=Wiley (John Wiley & Sons) | 命中源=crossref
  3. International Journal of Scientific Research in Artificial Intelligence and Machine Learning | ISSN=3139-0811 | 出版方=Technoscience Academy | 命中源=crossref
  4. ISCSITR - INTERNATIONAL JOURNAL OF SCIENTIFIC RESEARCH IN ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING | ISSN=- | 出版方=International Society for Computer Science and Information Technology Research (ISCSITR) | 命中源=crossref
  5. ISCSITR-INTERNATIONAL JOURNAL OF SCIENTIFIC RESEARCH IN ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING | ISSN=3067-753X | 出版方=International Society for Computer Science and Information Technology Research (ISCSITR) | 命中源=crossref
在线解析成功: Journal of Machine Learning Research | ISSN=1532-4435 | 出版方=Unmaintained records | 命中源=crossref
在线最近记录抓取失败: Crossref works 返回 0 条（total-results=0，items=0）
在线失败/边界原因：
  - Crossref works 返回 0 条（total-results=0，items=0）
```

说明：Crossref 能零配置命中名称与 ISSN=1532-4435，程序据此进入 `journals/1532-4435/works`；该 ISSN 对应 Crossref `Unmaintained records`，works 真实返回 `total-results=0`、`items=0`。程序没有伪造最近一期，而是打印真实失败原因并返回非零。

## 2. 中文刊：计算机学报

命令：

```bash
.venv/bin/python -m radar resolve "计算机学报"
```

退出码：`2`；耗时：`2.46s`。

真实 stdout：

```text
========================================
期刊名: 计算机学报
配置命中: 否（已继续在线解析）
在线尝试源: ['crossref', 'openalex']
配置内候选：
  - 软件学报 | ISSN=1000-9825 | slug=jos | aliases=软件学报, Journal of Software, JOS
  - 自动化学报 | ISSN=0254-4156 | slug=aas | aliases=自动化学报, Acta Automatica Sinica, AAS
  - 计算机研究与发展 | ISSN=1000-1239 | slug=crad | aliases=计算机研究与发展, Journal of Computer Research and Development, JCRD
  - 中文信息学报 | ISSN=1003-0077 | slug=jcip | aliases=中文信息学报, Journal of Chinese Information Processing, JCIP
  - 电子与信息学报 | ISSN=1009-5896 | slug=jeit | aliases=电子与信息学报, Journal of Electronics & Information Technology, JEIT
  - IEEE Transactions on Pattern Analysis and Machine Intelligence | ISSN=0162-8828 | slug=tpami | aliases=IEEE TPAMI, TPAMI, IEEE Transactions on Pattern Analysis and Machine Intelligence
  - Pattern Recognition | ISSN=0031-3203 | slug=pattern_recognition | aliases=Pattern Recognition, PR
  - Information Sciences | ISSN=0020-0255 | slug=information_sciences | aliases=Information Sciences, INS
  - IEEE Transactions on Knowledge and Data Engineering | ISSN=1041-4347 | slug=tkde | aliases=IEEE TKDE, TKDE, IEEE Transactions on Knowledge and Data Engineering
  - IEEE Transactions on Neural Networks and Learning Systems | ISSN=2162-237X | slug=tnnls | aliases=IEEE TNNLS, TNNLS, IEEE Transactions on Neural Networks and Learning Systems
在线候选（名称 / ISSN / 出版方 / 命中源）：
  1. Journal of Computer Science and Technology | ISSN=1000-9000 | 出版方=Springer Science+Business Media | 命中源=openalex
  2. 计算机学报 | ISSN=- | 出版方=- | 命中源=openalex
在线解析候选（无 ISSN，未成功抓取）: 计算机学报 | ISSN=- | 出版方=- | 命中源=openalex
在线最近记录: 未抓取（未获得可用 ISSN）
在线失败/边界原因：
  - 在线候选未提供 ISSN，无法请求 Crossref journals/{issn}/works
该刊未被国际源收录，请按 README 三步手工添加（提供官网 URL + parser）
```

说明：Crossref 返回 `total-results=0`，OpenAlex 能模糊检索到 `Journal of Computer Science and Technology`，也能检索到名称为“计算机学报”但没有 ISSN 的记录。程序只把有 ISSN 的候选视为可自动抓取的成功；无 ISSN 的精确候选明确标注“未成功抓取”，不调用 works，也不伪造结果，最终按已知边界提示手工添加并返回非零。
