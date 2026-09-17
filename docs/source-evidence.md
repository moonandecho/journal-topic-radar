# 数据源真实抓取证据

- 生成方式：使用项目 adapter 对 10 本运行时期刊逐一真实联网抓取。
- 生成时间：2026-09-17T19:03:27+08:00
- 每刊 `fixtures/<slug>.json` 是本次响应标准化后的可离线样本；`fixtures/raw/<slug>.txt` 保留真实响应片段。

## 1. 汇总表

| # | 期刊 | 国别 | 主源 | HTTP | 期号 | 发布日期 | 抓取论文数 | 前 3 条标题 |
|---:|---|---|---|---:|---|---:|---:|---|
| 1 | 软件学报 | 国内 | `journal_site` | 200 | 2026(9) | 2026-09-06 | 12 | 形式化方法与应用专题前言<br>AWTaint: 面向Web应用漏洞检测的增量静态分析框架<br>基于按需切片计算的并行化程序分析框架 |
| 2 | 自动化学报 | 国内 | `journal_site` | 200 | 2026, 52(8) | 2026-09-01 | 12 | 人工智能大模型及单点技术专题序言<br>面向大模型时代的持续学习方法论演变<br>大模型参数高效微调方法综述: 技术、趋势与挑战 |
| 3 | 计算机研究与发展 | 国内 | `journal_site` | 200 | 2026, 63(9) | 2026-09-01 | 12 | 大语言模型的齿状回：基于模式分离的场景认知能力诊断及增强框架<br>多视图增强图注意力网络的多模态知识图谱补全<br>语义对齐与自适应回放增强的动态多模态知识图谱持续补全 |
| 4 | 中文信息学报 | 国内 | `journal_site` | 200 | 2026, 40(8) | 2026-08-31 | 12 | 多级正例约束的无监督句子表示<br>利用大语言模型生成语料的跨语言方位词对语义衍化模式研究<br>CCKB：面向中文泛领域的大规模因果知识库构建与评价 |
| 5 | 电子与信息学报 | 国内 | `journal_site` | 200 | 2026, 48(7) | 2026-07-04 | 12 | 处理器芯片安全综述<br>非侵入式连续运动控制脑-机接口技术综述<br>TTSPD: 一种融合轮胎数据的多模态交通场景感知数据集 |
| 6 | IEEE Transactions on Pattern Analysis and Machine Intelligence | 国外 | `crossref` | 200 | 48(10) | 2026-10 | 15 | A Variational Mean-Field Control Framework for Graph Representation Learning<br>Feature-Space Planes Searcher: A Universal Domain Adaptation Framework for Interpretability and Computational Efficiency<br>Multi-Domain Feature Integration Based Trusted Partial Multi-View Incomplete Multi-Label Learning |
| 7 | Pattern Recognition | 国外 | `crossref` | 200 | 183 | 2027-03 | 15 | Complementary recommendation with abductive correction in incremental development<br>Structured sparse representation learning with locality-preserving strict sparsity and spatially adaptive geometry<br>Historical document restoration via an Adversarial Frequency-aware Guidance Network |
| 8 | Information Sciences | 国外 | `crossref` | 200 | 761 | 2027-02 | 15 | An empirical study of retrieval-augmented diffusion language models for generative commonsense reasoning<br>An integrated analytical framework for natural gas pricing: combining multi-source drivers, forecast enhancement, and model interpretability<br>Class-incremental feature selection based on neighborhood probabilistic rough sets |
| 9 | IEEE Transactions on Knowledge and Data Engineering | 国外 | `crossref` | 200 | 38(10) | 2026-10 | 15 | Large Language Model Empowered Recommendation Meets All-Domain Continual Pre-Training<br>BPO: Backdoor Purification via Overwriting<br>Coalition-Based Knowledge Graph Learning for Actual Controller Disclosure |
| 10 | IEEE Transactions on Neural Networks and Learning Systems | 国外 | `crossref` | 200 | 37(9) | 2026-09 | 15 | Incomplete Multimodal Federated Learning via Masking and Contrasting Prototypes<br>Topology-Optimal Multiple Gossip Steps for Decentralized Federated Learning via Gossip Tensor<br>Prompt Then Refine: Prompt-Free SAM-Enhanced Collaborative Learning Network for Detecting Salient Objects in Underwater Images |

### 1. 软件学报

- 国别：国内
- 标识：ISSN=1000-9825；slug=jos；官网=https://www.jos.org.cn
- 主目标 URL：https://www.jos.org.cn
- HTTP/大小：200；1351750 bytes
- adapter 源：`journal_site`；期号：2026(9)；发布日期：2026-09-06；论文数：12
- 诊断：官网列表: https://www.jos.org.cn/jos/article/issue/2026_9
- 诊断：原始解析 12 篇，保留 12 篇
- Top1：形式化方法与应用专题前言 | 2026-09-06 | https://www.jos.org.cn/jos/article/abstract/7610
- Top2：AWTaint: 面向Web应用漏洞检测的增量静态分析框架 | 2026-09-06 | https://www.jos.org.cn/jos/article/abstract/7600
- Top3：基于按需切片计算的并行化程序分析框架 | 2026-09-06 | https://www.jos.org.cn/jos/article/abstract/7602
- 标准化离线样本：`fixtures/jos.json`
- 原始响应片段：`fixtures/raw/jos.txt`

### 2. 自动化学报

- 国别：国内
- 标识：ISSN=0254-4156；slug=aas；官网=https://www.aas.net.cn
- 主目标 URL：https://www.aas.net.cn/cn/article/current
- HTTP/大小：200；198958 bytes
- adapter 源：`journal_site`；期号：2026, 52(8)；发布日期：2026-09-01；论文数：12
- 诊断：官网列表: https://www.aas.net.cn/cn/article/current
- 诊断：原始解析 12 篇，保留 12 篇
- 诊断：有 7 篇未获取到摘要，文本使用标题+关键词
- Top1：人工智能大模型及单点技术专题序言 | 2026-09-01 | https://www.aas.net.cn/cn/article/doi/10.16383/j.aas.c202608
- Top2：面向大模型时代的持续学习方法论演变 | 2025-05-20 | https://www.aas.net.cn/cn/article/doi/10.16383/j.aas.c240805
- Top3：大模型参数高效微调方法综述: 技术、趋势与挑战 | 2026-03-19 | https://www.aas.net.cn/cn/article/doi/10.16383/j.aas.c250451
- 标准化离线样本：`fixtures/aas.json`
- 原始响应片段：`fixtures/raw/aas.txt`

### 3. 计算机研究与发展

- 国别：国内
- 标识：ISSN=1000-1239；slug=crad；官网=https://crad.ict.ac.cn
- 主目标 URL：https://crad.ict.ac.cn/cn/article/current
- HTTP/大小：200；205694 bytes
- adapter 源：`journal_site`；期号：2026, 63(9)；发布日期：2026-09-01；论文数：12
- 诊断：官网列表: https://crad.ict.ac.cn/cn/article/current
- 诊断：原始解析 12 篇，保留 12 篇
- 诊断：有 6 篇未获取到摘要，文本使用标题+关键词
- Top1：大语言模型的齿状回：基于模式分离的场景认知能力诊断及增强框架 | 2026-09-01 | https://crad.ict.ac.cn/article/doi/10.7544/issn1000-1239.202660437
- Top2：多视图增强图注意力网络的多模态知识图谱补全 | 2026-09-01 | https://crad.ict.ac.cn/article/doi/10.7544/issn1000-1239.202660438
- Top3：语义对齐与自适应回放增强的动态多模态知识图谱持续补全 | 2026-09-01 | https://crad.ict.ac.cn/article/doi/10.7544/issn1000-1239.202660445
- 标准化离线样本：`fixtures/crad.json`
- 原始响应片段：`fixtures/raw/crad.txt`

### 4. 中文信息学报

- 国别：国内
- 标识：ISSN=1003-0077；slug=jcip；官网=http://jcip.cipsc.org.cn
- 主目标 URL：http://jcip.cipsc.org.cn/cn/article/current
- HTTP/大小：200；178789 bytes
- adapter 源：`journal_site`；期号：2026, 40(8)；发布日期：2026-08-31；论文数：12
- 诊断：官网列表: http://jcip.cipsc.org.cn/cn/article/current
- 诊断：原始解析 12 篇，保留 12 篇
- 诊断：有 6 篇未获取到摘要，文本使用标题+关键词
- Top1：多级正例约束的无监督句子表示 | 2026-08-31 | http://jcip.cipsc.org.cn/article/doi/10.3969/j.issn.1003-0077.2026.08.001
- Top2：利用大语言模型生成语料的跨语言方位词对语义衍化模式研究 | 2026-08-31 | http://jcip.cipsc.org.cn/article/doi/10.3969/j.issn.1003-0077.2026.08.002
- Top3：CCKB：面向中文泛领域的大规模因果知识库构建与评价 | 2026-08-31 | http://jcip.cipsc.org.cn/article/doi/10.3969/j.issn.1003-0077.2026.08.003
- 标准化离线样本：`fixtures/jcip.json`
- 原始响应片段：`fixtures/raw/jcip.txt`

### 5. 电子与信息学报

- 国别：国内
- 标识：ISSN=1009-5896；slug=jeit；官网=https://jeit.ac.cn
- 主目标 URL：https://jeit.ac.cn/article/current
- HTTP/大小：200；364737 bytes
- adapter 源：`journal_site`；期号：2026, 48(7)；发布日期：2026-07-04；论文数：12
- 诊断：官网列表: https://jeit.ac.cn/article/current
- 诊断：原始解析 12 篇，保留 12 篇
- 诊断：有 6 篇未获取到摘要，文本使用标题+关键词
- Top1：处理器芯片安全综述 | 2026-04-19 | https://jeit.ac.cn/cn/article/doi/10.11999/JEIT260026
- Top2：非侵入式连续运动控制脑-机接口技术综述 | 2026-04-06 | https://jeit.ac.cn/cn/article/doi/10.11999/JEIT260011
- Top3：TTSPD: 一种融合轮胎数据的多模态交通场景感知数据集 | 2026-02-27 | https://jeit.ac.cn/cn/article/doi/10.11999/JEIT260022
- 标准化离线样本：`fixtures/jeit.json`
- 原始响应片段：`fixtures/raw/jeit.txt`

### 6. IEEE Transactions on Pattern Analysis and Machine Intelligence

- 国别：国外
- 标识：ISSN=0162-8828；slug=tpami；官网=https://www.computer.org/csdl/journal/tp
- 主目标 URL：https://api.crossref.org/journals/0162-8828/works
- HTTP/大小：200；55867 bytes
- adapter 源：`crossref`；期号：48(10)；发布日期：2026-10；论文数：15
- 诊断：OpenAlex 补全: 摘要 15 篇, 关键词 15 篇
- Top1：A Variational Mean-Field Control Framework for Graph Representation Learning | 2026-10 | https://doi.org/10.1109/tpami.2026.3696154
- Top2：Feature-Space Planes Searcher: A Universal Domain Adaptation Framework for Interpretability and Computational Efficiency | 2026-10 | https://doi.org/10.1109/tpami.2026.3703974
- Top3：Multi-Domain Feature Integration Based Trusted Partial Multi-View Incomplete Multi-Label Learning | 2026-10 | https://doi.org/10.1109/tpami.2026.3692653
- 标准化离线样本：`fixtures/tpami.json`
- 原始响应片段：`fixtures/raw/tpami.txt`

### 7. Pattern Recognition

- 国别：国外
- 标识：ISSN=0031-3203；slug=pattern_recognition；官网=https://www.sciencedirect.com/journal/pattern-recognition
- 主目标 URL：https://api.crossref.org/journals/0031-3203/works
- HTTP/大小：200；90354 bytes
- adapter 源：`crossref`；期号：183；发布日期：2027-03；论文数：15
- 诊断：OpenAlex 补全: 摘要 0 篇, 关键词 13 篇
- Top1：Complementary recommendation with abductive correction in incremental development | 2027-03 | https://doi.org/10.1016/j.patcog.2026.114785
- Top2：Structured sparse representation learning with locality-preserving strict sparsity and spatially adaptive geometry | 2027-03 | https://doi.org/10.1016/j.patcog.2026.114878
- Top3：Historical document restoration via an Adversarial Frequency-aware Guidance Network | 2027-03 | https://doi.org/10.1016/j.patcog.2026.114828
- 标准化离线样本：`fixtures/pattern_recognition.json`
- 原始响应片段：`fixtures/raw/pattern_recognition.txt`

### 8. Information Sciences

- 国别：国外
- 标识：ISSN=0020-0255；slug=information_sciences；官网=https://www.sciencedirect.com/journal/information-sciences
- 主目标 URL：https://api.crossref.org/journals/0020-0255/works
- HTTP/大小：200；82441 bytes
- adapter 源：`crossref`；期号：761；发布日期：2027-02；论文数：15
- 诊断：OpenAlex 补全: 摘要 2 篇, 关键词 15 篇
- Top1：An empirical study of retrieval-augmented diffusion language models for generative commonsense reasoning | 2027-02 | https://doi.org/10.1016/j.ins.2026.124147
- Top2：An integrated analytical framework for natural gas pricing: combining multi-source drivers, forecast enhancement, and model interpretability | 2027-02 | https://doi.org/10.1016/j.ins.2026.124144
- Top3：Class-incremental feature selection based on neighborhood probabilistic rough sets | 2027-02 | https://doi.org/10.1016/j.ins.2026.124134
- 标准化离线样本：`fixtures/information_sciences.json`
- 原始响应片段：`fixtures/raw/information_sciences.txt`

### 9. IEEE Transactions on Knowledge and Data Engineering

- 国别：国外
- 标识：ISSN=1041-4347；slug=tkde；官网=https://www.computer.org/csdl/journal/tk
- 主目标 URL：https://api.crossref.org/journals/1041-4347/works
- HTTP/大小：200；51023 bytes
- adapter 源：`crossref`；期号：38(10)；发布日期：2026-10；论文数：15
- 诊断：OpenAlex 补全: 摘要 3 篇, 关键词 13 篇
- Top1：Large Language Model Empowered Recommendation Meets All-Domain Continual Pre-Training | 2026-10 | https://doi.org/10.1109/tkde.2026.3717059
- Top2：BPO: Backdoor Purification via Overwriting | 2026-10 | https://doi.org/10.1109/tkde.2026.3717987
- Top3：Coalition-Based Knowledge Graph Learning for Actual Controller Disclosure | 2026-10 | https://doi.org/10.1109/tkde.2026.3721243
- 标准化离线样本：`fixtures/tkde.json`
- 原始响应片段：`fixtures/raw/tkde.txt`

### 10. IEEE Transactions on Neural Networks and Learning Systems

- 国别：国外
- 标识：ISSN=2162-237X；slug=tnnls；官网=https://cis.ieee.org/publications/t-neural-networks-and-learning-systems
- 主目标 URL：https://api.crossref.org/journals/2162-237X/works
- HTTP/大小：200；50635 bytes
- adapter 源：`crossref`；期号：37(9)；发布日期：2026-09；论文数：15
- 诊断：OpenAlex 补全: 摘要 15 篇, 关键词 15 篇
- Top1：Incomplete Multimodal Federated Learning via Masking and Contrasting Prototypes | 2026-09 | https://doi.org/10.1109/tnnls.2026.3658522
- Top2：Topology-Optimal Multiple Gossip Steps for Decentralized Federated Learning via Gossip Tensor | 2026-09 | https://doi.org/10.1109/tnnls.2026.3670013
- Top3：Prompt Then Refine: Prompt-Free SAM-Enhanced Collaborative Learning Network for Detecting Salient Objects in Underwater Images | 2026-09 | https://doi.org/10.1109/tnnls.2026.3673090
- 标准化离线样本：`fixtures/tnnls.json`
- 原始响应片段：`fixtures/raw/tnnls.txt`

## 2. 候选替换记录

- 原候选 计算机学报（cjc.ict.ac.cn）：HTTPS 被 reset，HTTP 当期页 404；官方站无稳定当期目录 HTML API → 替换为 计算机研究与发展（crd.ict.ac.cn / crad.ict.ac.cn Magtech 当期目录，真实 HTTP 200 且可解析）。
- 原候选 电子学报（ejournal.org.cn）：首页 HTTP 200，但 `/zh/issue/2026/6/` 返回 6189 bytes 的 JS 壳页面，当期目录不可稳定解析 → 替换为 电子与信息学报（jeit.ac.cn/article/current，HTTP 200 且 40 条列表可解析）。
- 原候选 中国科学:信息科学（SciEngine）：官网 SPA，未找到可验证的当期目录/摘要 JSON 映射 → 替换为 中文信息学报（jcip.cipsc.org.cn/cn/article/current，HTTP 200 且 Magtech 目录可解析）。
- 原候选 JMLR：Crossref total=0，无法满足“每刊至少 5 篇最近一期” → 替换为 IEEE TKDE（1041-4347，Crossref 38(10) 可解析 15 篇）。
- 原候选 IJCV：latest issue `134(10)` Crossref 同卷期不足 5 篇，需要跨卷期补足，不满足“该期”要求 → 替换为 IEEE TKDE；保留 TPAMI/TNNLS 等同卷期 ≥5 篇的刊。

## 3. 备注

- 国内刊不依赖 CNKI；主路径是各刊官网当期目录 adapter。
- Crossref 首选、OpenAlex 补摘要；Elsevier 部分新文章 Crossref/OpenAlex 均无摘要，记录中 `text_source` 会标为 `title+keywords` 或 `title+abstract`，不静默伪造。
- 抓取不到或某字段不可用时，`diagnostics`/`degradation_reasons` 在 JSON、Markdown、终端和日志中均有标注。

## 4. 配置外期刊在线解析

本节记录验收要求的两个真实联网样例：一本国际刊 + 一本中文刊。

### 4.1 国际刊：Journal of Machine Learning Research

命令与耗时：

```bash
time .venv/bin/python -m radar resolve "Journal of Machine Learning Research"
# real 2.69s（以本机本次运行为准）
```

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

结论：Crossref 返回精确候选并给出 ISSN=1532-4435；随后立刻请求 `https://api.crossref.org/journals/1532-4435/works?sort=published&order=desc&rows=15`，真实响应 `total-results=0`、`items=0`，因此打印真实失败原因，未伪造最近一期。

### 4.2 中文刊：计算机学报

命令与耗时：

```bash
time .venv/bin/python -m radar resolve "计算机学报"
# real 2.46s（以本机本次运行为准）
```

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

结论：Crossref `journals?query=计算机学报&rows=5` 返回 0 条；OpenAlex 兜底返回模糊候选 `Journal of Computer Science and Technology` 和名称为“计算机学报”但无 ISSN 的记录。程序只把有 ISSN 的候选视为可自动抓取的成功；无 ISSN 的精确候选明确标注“未成功抓取”，不请求 works，最终如实提示“该刊未被国际源收录，请按 README 三步手工添加（提供官网 URL + parser）”。完整对照输出见 `docs/run-online-resolve.md`。
