# 10 刊在线全流程真实输出

- 主题：大语言模型驱动的代码生成与漏洞检测
- matcher：auto（当前环境成功加载 BGE embedding）
- 退出码：0
- 命令：
```bash
HF_ENDPOINT=https://hf-mirror.com python -m radar match --topic "大语言模型驱动的代码生成与漏洞检测" --matcher auto --format all --output docs/run-online-report
```

## 实际耗时

```text
real 50.5s（包含 10 刊真实在线抓取 + 每刊评分 + JSON/Markdown 落盘）
```

## stdout（table + JSON + Markdown）

```text
期刊选题雷达 | 主题: 大语言模型驱动的代码生成与漏洞检测
========================================================================
⚠ matcher=embedding:BAAI/bge-small-zh-v1.5 (degraded: 有 7 篇未获取到摘要，文本使用标题+关键词；有 6 篇未获取到摘要，文本使用标题+关键词)
matcher=embedding:BAAI/bge-small-zh-v1.5 | 阈值: strong≥0.75, weak≥0.6 | offline=False
--------------------------------------------------------------------------------------------------------------
期刊                           命中     命中数    强/弱      最近期号             Top-3 论文
--------------------------------------------------------------------------------------------------------------
软件学报                        否      0      0/0      2026(9)         
    判定基线: matcher=embedding:BAAI/bge-small-zh-v1.5 | strong≥0.75 | weak≥0.6
    [无] 0.566 ██████···· 基于大语言模型的Python到Dafny代码翻译                                               https://www.jos.org.cn/jos/article/abstract/7606
    [无] 0.496 █████····· AWTaint: 面向Web应用漏洞检测的增量静态分析框架                                          https://www.jos.org.cn/jos/article/abstract/7600
    [无] 0.473 █████····· 从设计到安全分析: 异构模型转换与交叉验证                                                  https://www.jos.org.cn/jos/article/abstract/7605
自动化学报                       否      0      0/0      2026, 52(8)     
    判定基线: matcher=embedding:BAAI/bge-small-zh-v1.5 | strong≥0.75 | weak≥0.6
    [无] 0.546 █████····· 一种基于单比特通信压缩的大语言模型训练方法                                                  https://www.aas.net.cn/cn/article/doi/10.16383/j.aas.c250087
    [无] 0.486 █████····· 人工智能大模型及单点技术专题序言                                                       https://www.aas.net.cn/cn/article/doi/10.16383/j.aas.c202608
    [无] 0.456 █████····· 高效提升多模态大语言模型推理能力的级联强化学习策略                                              https://www.aas.net.cn/cn/article/doi/10.16383/j.aas.c250515
    ⚠ 降级/限制: 有 7 篇未获取到摘要，文本使用标题+关键词
计算机研究与发展                    是      1      1/0      2026, 63(9)     
    判定基线: matcher=embedding:BAAI/bge-small-zh-v1.5 | strong≥0.75 | weak≥0.6
    [强] 0.817 ████████·· 基于大语言模型的源代码漏洞检测方法                                                      https://crad.ict.ac.cn/article/doi/10.7544/issn1000-1239.202660229
    [无] 0.552 ██████···· 大语言模型的齿状回：基于模式分离的场景认知能力诊断及增强框架                                         https://crad.ict.ac.cn/article/doi/10.7544/issn1000-1239.202660437
    [无] 0.444 ████······ 基于多智能体辩论的图文交织生成方法                                                      https://crad.ict.ac.cn/article/doi/10.7544/issn1000-1239.202660338
    ⚠ 降级/限制: 有 6 篇未获取到摘要，文本使用标题+关键词
中文信息学报                      否      0      0/0      2026, 40(8)     
    判定基线: matcher=embedding:BAAI/bge-small-zh-v1.5 | strong≥0.75 | weak≥0.6
    [无] 0.542 █████····· 大模型驱动的模块化安全本体构建方案                                                      http://jcip.cipsc.org.cn/article/doi/10.3969/j.issn.1003-0077.2026.08.012
    [无] 0.465 █████····· 基于解耦与组合的大模型知识问答方法                                                      http://jcip.cipsc.org.cn/article/doi/10.3969/j.issn.1003-0077.2026.08.008
    [无] 0.458 █████····· 利用大语言模型生成语料的跨语言方位词对语义衍化模式研究                                            http://jcip.cipsc.org.cn/article/doi/10.3969/j.issn.1003-0077.2026.08.002
    ⚠ 降级/限制: 有 6 篇未获取到摘要，文本使用标题+关键词
电子与信息学报                     是      1      0/1      2026, 48(7)     
    判定基线: matcher=embedding:BAAI/bge-small-zh-v1.5 | strong≥0.75 | weak≥0.6
    [弱] 0.660 ███████··· 大语言模型文献挖掘驱动的网络指标体系与场景差异化分析                                             https://jeit.ac.cn/cn/article/doi/10.11999/JEIT251120
    [无] 0.434 ████······ 多源知识引导的视觉置信度感知的多模态情感分析模型                                               https://jeit.ac.cn/cn/article/doi/10.11999/JEIT260063
    [无] 0.428 ████······ UWF-YOLO: 冗余信息优化的轻量化水下目标检测                                             https://jeit.ac.cn/cn/article/doi/10.11999/JEIT251129
    ⚠ 降级/限制: 有 6 篇未获取到摘要，文本使用标题+关键词
IEEE Transactions on Patte… 否      0      0/0      48(10)          
    判定基线: matcher=embedding:BAAI/bge-small-zh-v1.5 | strong≥0.75 | weak≥0.6
    [无] 0.435 ████······ Dataset Pruning: Reducing Training Data by Examining SGD-Influence     https://doi.org/10.1109/tpami.2026.3703395
    [无] 0.418 ████······ Privacy-Preserving Online Federated Learning for Massive Infinite Str… https://doi.org/10.1109/tpami.2026.3697332
    [无] 0.410 ████······ From Zero to Detail: A Progressive Spectral Decoupling Paradigm for U… https://doi.org/10.1109/tpami.2026.3691530
Pattern Recognition         否      0      0/0      183             
    判定基线: matcher=embedding:BAAI/bge-small-zh-v1.5 | strong≥0.75 | weak≥0.6
    [无] 0.455 █████····· Text Prior-Guided Cell Alignment with Transformer for Robust Table St… https://doi.org/10.1016/j.patcog.2026.114832
    [无] 0.421 ████······ Historical document restoration via an Adversarial Frequency-aware Gu… https://doi.org/10.1016/j.patcog.2026.114828
    [无] 0.417 ████······ Dynamic frequency modulation for controllable text-driven image gener… https://doi.org/10.1016/j.patcog.2026.114880
Information Sciences        否      0      0/0      761             
    判定基线: matcher=embedding:BAAI/bge-small-zh-v1.5 | strong≥0.75 | weak≥0.6
    [无] 0.445 ████······ HIRO: Historical intent reasoning with observation for multi-agent re… https://doi.org/10.1016/j.ins.2026.124125
    [无] 0.433 ████······ An integrated analytical framework for natural gas pricing: combining… https://doi.org/10.1016/j.ins.2026.124144
    [无] 0.411 ████······ UniCSL: A unified federated learning framework with client-specific L… https://doi.org/10.1016/j.ins.2026.124118
IEEE Transactions on Knowl… 否      0      0/0      38(10)          
    判定基线: matcher=embedding:BAAI/bge-small-zh-v1.5 | strong≥0.75 | weak≥0.6
    [无] 0.453 █████····· Data and Knowledge Dual-Driven Text Embedding Approaches: A Survey     https://doi.org/10.1109/tkde.2026.3721883
    [无] 0.436 ████······ Impute On-Demand: Adaptive Correlated Time Series Imputation for Chan… https://doi.org/10.1109/tkde.2026.3717792
    [无] 0.434 ████······ Large Language Model Empowered Recommendation Meets All-Domain Contin… https://doi.org/10.1109/tkde.2026.3717059
IEEE Transactions on Neura… 否      0      0/0      37(9)           
    判定基线: matcher=embedding:BAAI/bge-small-zh-v1.5 | strong≥0.75 | weak≥0.6
    [无] 0.431 ████······ Learning From <i>M</i> -Tuple One-vs-All Confidence Comparison Data    https://doi.org/10.1109/tnnls.2026.3673280
    [无] 0.420 ████······ Incomplete Multimodal Federated Learning via Masking and Contrasting … https://doi.org/10.1109/tnnls.2026.3658522
    [无] 0.416 ████······ CoreKD: A Context-Aware Local Region Structural Contrastive Knowledge… https://doi.org/10.1109/tnnls.2026.3672967
--------------------------------------------------------------------------------------------------------------
降级与数据源说明:
  - 有 7 篇未获取到摘要，文本使用标题+关键词
  - 有 6 篇未获取到摘要，文本使用标题+关键词
生成时间: 2026-09-17T19:07:30+08:00

----- JSON -----
{
  "topic": "大语言模型驱动的代码生成与漏洞检测",
  "matcher": "embedding:BAAI/bge-small-zh-v1.5",
  "backend": "embedding",
  "thresholds": {
    "strong": 0.75,
    "weak": 0.6
  },
  "generated_at": "2026-09-17T19:07:30+08:00",
  "offline": false,
  "degraded": true,
  "degradation_reasons": [
    "有 7 篇未获取到摘要，文本使用标题+关键词",
    "有 6 篇未获取到摘要，文本使用标题+关键词"
  ],
  "journals": [
    {
      "journal": "软件学报",
      "source": "journal_site",
      "issue": "2026(9)",
      "published": "2026-09-06",
      "fetch_ok": true,
      "similar": false,
      "hit_count": 0,
      "strong_count": 0,
      "weak_count": 0,
      "top_papers": [
        {
          "title": "基于大语言模型的Python到Dafny代码翻译",
          "authors": [
            "杜奕成，卢奕函，朱雪阳，张文辉"
          ],
          "score": 0.5664,
          "level": "irrelevant",
          "url": "https://www.jos.org.cn/jos/article/abstract/7606",
          "doi": "10.13328/j.cnki.jos.007606",
          "published": "2026",
          "text_source": "title+abstract",
          "issue": "2026(9)"
        },
        {
          "title": "AWTaint: 面向Web应用漏洞检测的增量静态分析框架",
          "authors": [
            "罗天涵，肖庆，戴嘉润，谭杰"
          ],
          "score": 0.4956,
          "level": "irrelevant",
          "url": "https://www.jos.org.cn/jos/article/abstract/7600",
          "doi": "10.13328/j.cnki.jos.007600",
          "published": "2026-09-06",
          "text_source": "title+keywords+abstract",
          "issue": "2026(9)"
        },
        {
          "title": "从设计到安全分析: 异构模型转换与交叉验证",
          "authors": [
            "吴梦丹，杨顺昆，侯展意，佘志坤，曾福萍，冀振燕"
          ],
          "score": 0.4733,
          "level": "irrelevant",
          "url": "https://www.jos.org.cn/jos/article/abstract/7605",
          "doi": "10.13328/j.cnki.jos.007605",
          "published": "2026",
          "text_source": "title+abstract",
          "issue": "2026(9)"
        }
      ],
      "thresholds": {
        "strong": 0.75,
        "weak": 0.6
      },
      "matcher": "embedding:BAAI/bge-small-zh-v1.5",
      "degraded": false,
      "degradation_reasons": [],
      "diagnostics": [
        "官网列表: https://www.jos.org.cn/jos/article/issue/2026_9",
        "原始解析 12 篇，保留 12 篇"
      ]
    },
    {
      "journal": "自动化学报",
      "source": "journal_site",
      "issue": "2026, 52(8)",
      "published": "2026-09-01",
      "fetch_ok": true,
      "similar": false,
      "hit_count": 0,
      "strong_count": 0,
      "weak_count": 0,
      "top_papers": [
        {
          "title": "一种基于单比特通信压缩的大语言模型训练方法",
          "authors": [
            "陈楚岩",
            "刘烨谞",
            "贾维宸",
            "何雨桐",
            "袁坤",
            "王立威"
          ],
          "score": 0.5462,
          "level": "irrelevant",
          "url": "https://www.aas.net.cn/cn/article/doi/10.16383/j.aas.c250087",
          "doi": "10.16383/j.aas.c250087",
          "published": "2026",
          "text_source": "title",
          "issue": "2026, 52(8)"
        },
        {
          "title": "人工智能大模型及单点技术专题序言",
          "authors": [
            "赖剑煌"
          ],
          "score": 0.4858,
          "level": "irrelevant",
          "url": "https://www.aas.net.cn/cn/article/doi/10.16383/j.aas.c202608",
          "doi": "10.16383/j.aas.c202608",
          "published": "2026-09-01",
          "text_source": "title",
          "issue": "2026, 52(8)"
        },
        {
          "title": "高效提升多模态大语言模型推理能力的级联强化学习策略",
          "authors": [
            "王玮赟",
            "蒲恒骏",
            "景凌林",
            "乔宇"
          ],
          "score": 0.4565,
          "level": "irrelevant",
          "url": "https://www.aas.net.cn/cn/article/doi/10.16383/j.aas.c250515",
          "doi": "10.16383/j.aas.c250515",
          "published": "2026-03-31",
          "text_source": "title+keywords+abstract",
          "issue": "2026, 52(8)"
        }
      ],
      "thresholds": {
        "strong": 0.75,
        "weak": 0.6
      },
      "matcher": "embedding:BAAI/bge-small-zh-v1.5",
      "degraded": true,
      "degradation_reasons": [
        "有 7 篇未获取到摘要，文本使用标题+关键词"
      ],
      "diagnostics": [
        "官网列表: https://www.aas.net.cn/cn/article/current",
        "原始解析 12 篇，保留 12 篇",
        "有 7 篇未获取到摘要，文本使用标题+关键词"
      ]
    },
    {
      "journal": "计算机研究与发展",
      "source": "journal_site",
      "issue": "2026, 63(9)",
      "published": "2026-09-01",
      "fetch_ok": true,
      "similar": true,
      "hit_count": 1,
      "strong_count": 1,
      "weak_count": 0,
      "top_papers": [
        {
          "title": "基于大语言模型的源代码漏洞检测方法",
          "authors": [
            "曹明生",
            "丁桥隆",
            "张文清",
            "李延斌",
            "林迪",
            "许辉"
          ],
          "score": 0.8172,
          "level": "strong",
          "url": "https://crad.ict.ac.cn/article/doi/10.7544/issn1000-1239.202660229",
          "doi": "10.7544/issn1000-1239.202660229",
          "published": "2026",
          "text_source": "title",
          "issue": "2026, 63(9)"
        },
        {
          "title": "大语言模型的齿状回：基于模式分离的场景认知能力诊断及增强框架",
          "authors": [
            "马博翔",
            "李茹",
            "郭少茹",
            "李英豪",
            "VíctorGutiérrez-Basulto"
          ],
          "score": 0.5522,
          "level": "irrelevant",
          "url": "https://crad.ict.ac.cn/article/doi/10.7544/issn1000-1239.202660437",
          "doi": "10.7544/issn1000-1239.202660437",
          "published": "2026-09-01",
          "text_source": "title+keywords+abstract",
          "issue": "2026, 63(9)"
        },
        {
          "title": "基于多智能体辩论的图文交织生成方法",
          "authors": [
            "马杰",
            "张瀚驰",
            "渠宁",
            "薛皓荃",
            "王鑫平",
            "刘均"
          ],
          "score": 0.4435,
          "level": "irrelevant",
          "url": "https://crad.ict.ac.cn/article/doi/10.7544/issn1000-1239.202660338",
          "doi": "10.7544/issn1000-1239.202660338",
          "published": "2026-09-01",
          "text_source": "title+keywords+abstract",
          "issue": "2026, 63(9)"
        }
      ],
      "thresholds": {
        "strong": 0.75,
        "weak": 0.6
      },
      "matcher": "embedding:BAAI/bge-small-zh-v1.5",
      "degraded": true,
      "degradation_reasons": [
        "有 6 篇未获取到摘要，文本使用标题+关键词"
      ],
      "diagnostics": [
        "官网列表: https://crad.ict.ac.cn/cn/article/current",
        "原始解析 12 篇，保留 12 篇",
        "有 6 篇未获取到摘要，文本使用标题+关键词"
      ]
    },
    {
      "journal": "中文信息学报",
      "source": "journal_site",
      "issue": "2026, 40(8)",
      "published": "2026-08-31",
      "fetch_ok": true,
      "similar": false,
      "hit_count": 0,
      "strong_count": 0,
      "weak_count": 0,
      "top_papers": [
        {
          "title": "大模型驱动的模块化安全本体构建方案",
          "authors": [
            "王一琁",
            "吕佳敏",
            "赵波",
            "宋晓芙"
          ],
          "score": 0.5417,
          "level": "irrelevant",
          "url": "http://jcip.cipsc.org.cn/article/doi/10.3969/j.issn.1003-0077.2026.08.012",
          "doi": "10.3969/j.issn.1003-0077.2026.08.012",
          "published": "2026",
          "text_source": "title",
          "issue": "2026, 40(8)"
        },
        {
          "title": "基于解耦与组合的大模型知识问答方法",
          "authors": [
            "施圣泽",
            "秦利",
            "胡军",
            "鲁晶晶",
            "王丹丹"
          ],
          "score": 0.4651,
          "level": "irrelevant",
          "url": "http://jcip.cipsc.org.cn/article/doi/10.3969/j.issn.1003-0077.2026.08.008",
          "doi": "10.3969/j.issn.1003-0077.2026.08.008",
          "published": "2026",
          "text_source": "title",
          "issue": "2026, 40(8)"
        },
        {
          "title": "利用大语言模型生成语料的跨语言方位词对语义衍化模式研究",
          "authors": [
            "王梦焰",
            "安纪元",
            "杨尔弘",
            "杨麟儿"
          ],
          "score": 0.4585,
          "level": "irrelevant",
          "url": "http://jcip.cipsc.org.cn/article/doi/10.3969/j.issn.1003-0077.2026.08.002",
          "doi": "10.3969/j.issn.1003-0077.2026.08.002",
          "published": "2026-08-31",
          "text_source": "title+keywords+abstract",
          "issue": "2026, 40(8)"
        }
      ],
      "thresholds": {
        "strong": 0.75,
        "weak": 0.6
      },
      "matcher": "embedding:BAAI/bge-small-zh-v1.5",
      "degraded": true,
      "degradation_reasons": [
        "有 6 篇未获取到摘要，文本使用标题+关键词"
      ],
      "diagnostics": [
        "官网列表: http://jcip.cipsc.org.cn/cn/article/current",
        "原始解析 12 篇，保留 12 篇",
        "有 6 篇未获取到摘要，文本使用标题+关键词"
      ]
    },
    {
      "journal": "电子与信息学报",
      "source": "journal_site",
      "issue": "2026, 48(7)",
      "published": "2026-07-04",
      "fetch_ok": true,
      "similar": true,
      "hit_count": 1,
      "strong_count": 0,
      "weak_count": 1,
      "top_papers": [
        {
          "title": "大语言模型文献挖掘驱动的网络指标体系与场景差异化分析",
          "authors": [
            "徐祺坤",
            "刘娅汐",
            "韩淑娴",
            "张慧峰",
            "皇甫伟"
          ],
          "score": 0.6598,
          "level": "weak",
          "url": "https://jeit.ac.cn/cn/article/doi/10.11999/JEIT251120",
          "doi": "10.11999/JEIT251120",
          "published": "2026",
          "text_source": "title",
          "issue": "2026, 48(7)"
        },
        {
          "title": "多源知识引导的视觉置信度感知的多模态情感分析模型",
          "authors": [
            "彭菊红",
            "张智",
            "刘朋",
            "葛文慧",
            "柳陈",
            "廖凌鑫",
            "张凯"
          ],
          "score": 0.4337,
          "level": "irrelevant",
          "url": "https://jeit.ac.cn/cn/article/doi/10.11999/JEIT260063",
          "doi": "10.11999/JEIT260063",
          "published": "2026",
          "text_source": "title",
          "issue": "2026, 48(7)"
        },
        {
          "title": "UWF-YOLO: 冗余信息优化的轻量化水下目标检测",
          "authors": [
            "侯国家",
            "马佳琦",
            "王岳川",
            "黄宝香",
            "李坤乾"
          ],
          "score": 0.4277,
          "level": "irrelevant",
          "url": "https://jeit.ac.cn/cn/article/doi/10.11999/JEIT251129",
          "doi": "10.11999/JEIT251129",
          "published": "2026",
          "text_source": "title",
          "issue": "2026, 48(7)"
        }
      ],
      "thresholds": {
        "strong": 0.75,
        "weak": 0.6
      },
      "matcher": "embedding:BAAI/bge-small-zh-v1.5",
      "degraded": true,
      "degradation_reasons": [
        "有 6 篇未获取到摘要，文本使用标题+关键词"
      ],
      "diagnostics": [
        "官网列表: https://jeit.ac.cn/article/current",
        "原始解析 12 篇，保留 12 篇",
        "有 6 篇未获取到摘要，文本使用标题+关键词"
      ]
    },
    {
      "journal": "IEEE Transactions on Pattern Analysis and Machine Intelligence",
      "source": "crossref",
      "issue": "48(10)",
      "published": "2026-10",
      "fetch_ok": true,
      "similar": false,
      "hit_count": 0,
      "strong_count": 0,
      "weak_count": 0,
      "top_papers": [
        {
          "title": "Dataset Pruning: Reducing Training Data by Examining SGD-Influence",
          "authors": [
            "Shuo Yang",
            "Yucheng Huang",
            "Zeke Xie",
            "Ping Li",
            "Min Xu",
            "Liqiang Nie"
          ],
          "score": 0.4351,
          "level": "irrelevant",
          "url": "https://doi.org/10.1109/tpami.2026.3703395",
          "doi": "10.1109/tpami.2026.3703395",
          "published": "2026-10",
          "text_source": "title+keywords+abstract",
          "issue": "48(10)"
        },
        {
          "title": "Privacy-Preserving Online Federated Learning for Massive Infinite Streams",
          "authors": [
            "Liang Shi",
            "Xuebin Ren",
            "Shusen Yang",
            "Cong Zhao",
            "Yijun Hao",
            "Zongben Xu"
          ],
          "score": 0.4182,
          "level": "irrelevant",
          "url": "https://doi.org/10.1109/tpami.2026.3697332",
          "doi": "10.1109/tpami.2026.3697332",
          "published": "2026-10",
          "text_source": "title+keywords+abstract",
          "issue": "48(10)"
        },
        {
          "title": "From Zero to Detail: A Progressive Spectral Decoupling Paradigm for UHD Image Restoration With New Benchmark",
          "authors": [
            "Chen Zhao",
            "Yunzhe Xu",
            "Zhizhou Chen",
            "Enxuan Gu",
            "Kai Zhang",
            "Xiaoming Liu",
            "Jian Yang",
            "Ying Tai"
          ],
          "score": 0.4101,
          "level": "irrelevant",
          "url": "https://doi.org/10.1109/tpami.2026.3691530",
          "doi": "10.1109/tpami.2026.3691530",
          "published": "2026-10",
          "text_source": "title+keywords+abstract",
          "issue": "48(10)"
        }
      ],
      "thresholds": {
        "strong": 0.75,
        "weak": 0.6
      },
      "matcher": "embedding:BAAI/bge-small-zh-v1.5",
      "degraded": false,
      "degradation_reasons": [],
      "diagnostics": [
        "OpenAlex 补全: 摘要 15 篇, 关键词 15 篇"
      ]
    },
    {
      "journal": "Pattern Recognition",
      "source": "crossref",
      "issue": "183",
      "published": "2027-03",
      "fetch_ok": true,
      "similar": false,
      "hit_count": 0,
      "strong_count": 0,
      "weak_count": 0,
      "top_papers": [
        {
          "title": "Text Prior-Guided Cell Alignment with Transformer for Robust Table Structure Recognition",
          "authors": [
            "Jiajie Li",
            "Jiaxin Zhang",
            "Qian Yin",
            "Qiuli Zhang",
            "Xin Zheng",
            "Wenyi Zeng",
            "Ping Guo"
          ],
          "score": 0.4552,
          "level": "irrelevant",
          "url": "https://doi.org/10.1016/j.patcog.2026.114832",
          "doi": "10.1016/j.patcog.2026.114832",
          "published": "2027-03",
          "text_source": "title+keywords",
          "issue": "183"
        },
        {
          "title": "Historical document restoration via an Adversarial Frequency-aware Guidance Network",
          "authors": [
            "Nanfeng Jiang",
            "Ziyu Li",
            "Liqun Lin",
            "Ting Zhang",
            "Shunzhou Wang",
            "Xu-Yao Zhang",
            "Yun Wu",
            "Da-Han Wang"
          ],
          "score": 0.4206,
          "level": "irrelevant",
          "url": "https://doi.org/10.1016/j.patcog.2026.114828",
          "doi": "10.1016/j.patcog.2026.114828",
          "published": "2027-03",
          "text_source": "title+keywords",
          "issue": "183"
        },
        {
          "title": "Dynamic frequency modulation for controllable text-driven image generation",
          "authors": [
            "Tiandong Shi",
            "Chengli Peng",
            "Ji Qi",
            "Jiayi Ma",
            "Ling Zhao"
          ],
          "score": 0.4174,
          "level": "irrelevant",
          "url": "https://doi.org/10.1016/j.patcog.2026.114880",
          "doi": "10.1016/j.patcog.2026.114880",
          "published": "2027-03",
          "text_source": "title+keywords",
          "issue": "183"
        }
      ],
      "thresholds": {
        "strong": 0.75,
        "weak": 0.6
      },
      "matcher": "embedding:BAAI/bge-small-zh-v1.5",
      "degraded": false,
      "degradation_reasons": [],
      "diagnostics": [
        "OpenAlex 补全: 摘要 0 篇, 关键词 13 篇"
      ]
    },
    {
      "journal": "Information Sciences",
      "source": "crossref",
      "issue": "761",
      "published": "2027-02",
      "fetch_ok": true,
      "similar": false,
      "hit_count": 0,
      "strong_count": 0,
      "weak_count": 0,
      "top_papers": [
        {
          "title": "HIRO: Historical intent reasoning with observation for multi-agent reinforcement learning",
          "authors": [
            "Jie Chen",
            "Xiwen Zhang",
            "Ming-gang Gan",
            "Keyi Guan"
          ],
          "score": 0.4454,
          "level": "irrelevant",
          "url": "https://doi.org/10.1016/j.ins.2026.124125",
          "doi": "10.1016/j.ins.2026.124125",
          "published": "2027-02",
          "text_source": "title+keywords",
          "issue": "761"
        },
        {
          "title": "An integrated analytical framework for natural gas pricing: combining multi-source drivers, forecast enhancement, and model interpretability",
          "authors": [
            "Yilin Zhou",
            "Jianzhou Wang",
            "Jialu Gao",
            "Kang Wang",
            "Helen Lu"
          ],
          "score": 0.4329,
          "level": "irrelevant",
          "url": "https://doi.org/10.1016/j.ins.2026.124144",
          "doi": "10.1016/j.ins.2026.124144",
          "published": "2027-02",
          "text_source": "title+keywords",
          "issue": "761"
        },
        {
          "title": "UniCSL: A unified federated learning framework with client-specific LS-DC loss",
          "authors": [
            "Shuvo Saha Roy",
            "Sambhav Jain",
            "Reshma Rastogi"
          ],
          "score": 0.4113,
          "level": "irrelevant",
          "url": "https://doi.org/10.1016/j.ins.2026.124118",
          "doi": "10.1016/j.ins.2026.124118",
          "published": "2027-02",
          "text_source": "title+keywords",
          "issue": "761"
        }
      ],
      "thresholds": {
        "strong": 0.75,
        "weak": 0.6
      },
      "matcher": "embedding:BAAI/bge-small-zh-v1.5",
      "degraded": false,
      "degradation_reasons": [],
      "diagnostics": [
        "OpenAlex 补全: 摘要 2 篇, 关键词 15 篇"
      ]
    },
    {
      "journal": "IEEE Transactions on Knowledge and Data Engineering",
      "source": "crossref",
      "issue": "38(10)",
      "published": "2026-10",
      "fetch_ok": true,
      "similar": false,
      "hit_count": 0,
      "strong_count": 0,
      "weak_count": 0,
      "top_papers": [
        {
          "title": "Data and Knowledge Dual-Driven Text Embedding Approaches: A Survey",
          "authors": [
            "Xiaoyin Chen",
            "Jiaqing Zhan",
            "Jiayi Lin",
            "Han Liu",
            "Qin Zhang",
            "Junyang Chen",
            "Hao Chen"
          ],
          "score": 0.4528,
          "level": "irrelevant",
          "url": "https://doi.org/10.1109/tkde.2026.3721883",
          "doi": "10.1109/tkde.2026.3721883",
          "published": "2026-10",
          "text_source": "title+keywords",
          "issue": "38(10)"
        },
        {
          "title": "Impute On-Demand: Adaptive Correlated Time Series Imputation for Changing Environments",
          "authors": [
            "Zhichen Lai",
            "Huan Li",
            "Dalin Zhang",
            "Dong Gong",
            "Lina Yao",
            "Christian S. Jensen"
          ],
          "score": 0.4364,
          "level": "irrelevant",
          "url": "https://doi.org/10.1109/tkde.2026.3717792",
          "doi": "10.1109/tkde.2026.3717792",
          "published": "2026-10",
          "text_source": "title+keywords",
          "issue": "38(10)"
        },
        {
          "title": "Large Language Model Empowered Recommendation Meets All-Domain Continual Pre-Training",
          "authors": [
            "Haokai Ma",
            "Yunshan Ma",
            "Ruobing Xie",
            "Lei Meng",
            "Jialie Shen",
            "Xingwu Sun",
            "Zhanhui Kang",
            "Tat-Seng Chua"
          ],
          "score": 0.4338,
          "level": "irrelevant",
          "url": "https://doi.org/10.1109/tkde.2026.3717059",
          "doi": "10.1109/tkde.2026.3717059",
          "published": "2026-10",
          "text_source": "title+keywords+abstract",
          "issue": "38(10)"
        }
      ],
      "thresholds": {
        "strong": 0.75,
        "weak": 0.6
      },
      "matcher": "embedding:BAAI/bge-small-zh-v1.5",
      "degraded": false,
      "degradation_reasons": [],
      "diagnostics": [
        "OpenAlex 补全: 摘要 3 篇, 关键词 13 篇"
      ]
    },
    {
      "journal": "IEEE Transactions on Neural Networks and Learning Systems",
      "source": "crossref",
      "issue": "37(9)",
      "published": "2026-09",
      "fetch_ok": true,
      "similar": false,
      "hit_count": 0,
      "strong_count": 0,
      "weak_count": 0,
      "top_papers": [
        {
          "title": "Learning From <i>M</i> -Tuple One-vs-All Confidence Comparison Data",
          "authors": [
            "Jiahe Qin",
            "Junpeng Li",
            "Changchun Hua",
            "Yana Yang"
          ],
          "score": 0.4308,
          "level": "irrelevant",
          "url": "https://doi.org/10.1109/tnnls.2026.3673280",
          "doi": "10.1109/tnnls.2026.3673280",
          "published": "2026-09",
          "text_source": "title+keywords+abstract",
          "issue": "37(9)"
        },
        {
          "title": "Incomplete Multimodal Federated Learning via Masking and Contrasting Prototypes",
          "authors": [
            "Guangyin Bao",
            "Qi Zhang",
            "Duoqian Miao",
            "Zixuan Gong",
            "Chaochao Chen",
            "Liang Hu",
            "Longbing Cao"
          ],
          "score": 0.4197,
          "level": "irrelevant",
          "url": "https://doi.org/10.1109/tnnls.2026.3658522",
          "doi": "10.1109/tnnls.2026.3658522",
          "published": "2026-09",
          "text_source": "title+keywords+abstract",
          "issue": "37(9)"
        },
        {
          "title": "CoreKD: A Context-Aware Local Region Structural Contrastive Knowledge Distillation Framework for Object Detection",
          "authors": [
            "Junfei Yi",
            "Jianxu Mao",
            "Yaonan Wang",
            "Tengfei Liu",
            "Mingjie Li",
            "Kai Zeng",
            "Hui Zhang",
            "Xiaojun Chang"
          ],
          "score": 0.4161,
          "level": "irrelevant",
          "url": "https://doi.org/10.1109/tnnls.2026.3672967",
          "doi": "10.1109/tnnls.2026.3672967",
          "published": "2026-09",
          "text_source": "title+keywords+abstract",
          "issue": "37(9)"
        }
      ],
      "thresholds": {
        "strong": 0.75,
        "weak": 0.6
      },
      "matcher": "embedding:BAAI/bge-small-zh-v1.5",
      "degraded": false,
      "degradation_reasons": [],
      "diagnostics": [
        "OpenAlex 补全: 摘要 14 篇, 关键词 14 篇"
      ]
    }
  ]
}

----- MARKDOWN -----
# 期刊选题雷达报告：大语言模型驱动的代码生成与漏洞检测

> **降级标注**：`matcher=embedding:BAAI/bge-small-zh-v1.5`
> - 有 7 篇未获取到摘要，文本使用标题+关键词
> - 有 6 篇未获取到摘要，文本使用标题+关键词

- 生成时间：2026-09-17T19:07:30+08:00
- matcher 后端：`embedding:BAAI/bge-small-zh-v1.5`（embedding）
- 判定阈值：strong ≥ **0.75**，weak ≥ **0.6**；期刊级命中 = 命中数 ≥ 1
- 数据模式：online

## 期刊结论总览

| 期刊 | 是否命中 | 命中数 | 强/弱 | 最近期号 | 数据源 | 降级 |
|---|---:|---:|---:|---|---|---|
| 软件学报 | 否 | 0 | 0/0 | 2026(9) | journal_site | 否 |
| 自动化学报 | 否 | 0 | 0/0 | 2026, 52(8) | journal_site | 是 |
| 计算机研究与发展 | 是 | 1 | 1/0 | 2026, 63(9) | journal_site | 是 |
| 中文信息学报 | 否 | 0 | 0/0 | 2026, 40(8) | journal_site | 是 |
| 电子与信息学报 | 是 | 1 | 0/1 | 2026, 48(7) | journal_site | 是 |
| IEEE Transactions on Pattern Analysis and Machine Intelligence | 否 | 0 | 0/0 | 48(10) | crossref | 否 |
| Pattern Recognition | 否 | 0 | 0/0 | 183 | crossref | 否 |
| Information Sciences | 否 | 0 | 0/0 | 761 | crossref | 否 |
| IEEE Transactions on Knowledge and Data Engineering | 否 | 0 | 0/0 | 38(10) | crossref | 否 |
| IEEE Transactions on Neural Networks and Learning Systems | 否 | 0 | 0/0 | 37(9) | crossref | 否 |

## 软件学报

- 源：`journal_site`；期号：2026(9)；发布日期：2026-09-06
- 是否相似主题论文：**否**；命中数：0；阈值：strong≥0.75, weak≥0.6；matcher：`embedding:BAAI/bge-small-zh-v1.5`

| 排名 | 标题 | 分数 | 判定 | 链接 |
|---:|---|---:|---|---|
| 1 | 基于大语言模型的Python到Dafny代码翻译 | 0.5664 | 不相关 | https://www.jos.org.cn/jos/article/abstract/7606 |
| 2 | AWTaint: 面向Web应用漏洞检测的增量静态分析框架 | 0.4956 | 不相关 | https://www.jos.org.cn/jos/article/abstract/7600 |
| 3 | 从设计到安全分析: 异构模型转换与交叉验证 | 0.4733 | 不相关 | https://www.jos.org.cn/jos/article/abstract/7605 |

<details><summary>数据源诊断</summary>

- 官网列表: https://www.jos.org.cn/jos/article/issue/2026_9
- 原始解析 12 篇，保留 12 篇

</details>

## 自动化学报

- 源：`journal_site`；期号：2026, 52(8)；发布日期：2026-09-01
- 是否相似主题论文：**否**；命中数：0；阈值：strong≥0.75, weak≥0.6；matcher：`embedding:BAAI/bge-small-zh-v1.5`
- 降级/限制：有 7 篇未获取到摘要，文本使用标题+关键词

| 排名 | 标题 | 分数 | 判定 | 链接 |
|---:|---|---:|---|---|
| 1 | 一种基于单比特通信压缩的大语言模型训练方法 | 0.5462 | 不相关 | https://www.aas.net.cn/cn/article/doi/10.16383/j.aas.c250087 |
| 2 | 人工智能大模型及单点技术专题序言 | 0.4858 | 不相关 | https://www.aas.net.cn/cn/article/doi/10.16383/j.aas.c202608 |
| 3 | 高效提升多模态大语言模型推理能力的级联强化学习策略 | 0.4565 | 不相关 | https://www.aas.net.cn/cn/article/doi/10.16383/j.aas.c250515 |

<details><summary>数据源诊断</summary>

- 官网列表: https://www.aas.net.cn/cn/article/current
- 原始解析 12 篇，保留 12 篇
- 有 7 篇未获取到摘要，文本使用标题+关键词

</details>

## 计算机研究与发展

- 源：`journal_site`；期号：2026, 63(9)；发布日期：2026-09-01
- 是否相似主题论文：**是**；命中数：1；阈值：strong≥0.75, weak≥0.6；matcher：`embedding:BAAI/bge-small-zh-v1.5`
- 降级/限制：有 6 篇未获取到摘要，文本使用标题+关键词

| 排名 | 标题 | 分数 | 判定 | 链接 |
|---:|---|---:|---|---|
| 1 | 基于大语言模型的源代码漏洞检测方法 | 0.8172 | 强相关 | https://crad.ict.ac.cn/article/doi/10.7544/issn1000-1239.202660229 |
| 2 | 大语言模型的齿状回：基于模式分离的场景认知能力诊断及增强框架 | 0.5522 | 不相关 | https://crad.ict.ac.cn/article/doi/10.7544/issn1000-1239.202660437 |
| 3 | 基于多智能体辩论的图文交织生成方法 | 0.4435 | 不相关 | https://crad.ict.ac.cn/article/doi/10.7544/issn1000-1239.202660338 |

<details><summary>数据源诊断</summary>

- 官网列表: https://crad.ict.ac.cn/cn/article/current
- 原始解析 12 篇，保留 12 篇
- 有 6 篇未获取到摘要，文本使用标题+关键词

</details>

## 中文信息学报

- 源：`journal_site`；期号：2026, 40(8)；发布日期：2026-08-31
- 是否相似主题论文：**否**；命中数：0；阈值：strong≥0.75, weak≥0.6；matcher：`embedding:BAAI/bge-small-zh-v1.5`
- 降级/限制：有 6 篇未获取到摘要，文本使用标题+关键词

| 排名 | 标题 | 分数 | 判定 | 链接 |
|---:|---|---:|---|---|
| 1 | 大模型驱动的模块化安全本体构建方案 | 0.5417 | 不相关 | http://jcip.cipsc.org.cn/article/doi/10.3969/j.issn.1003-0077.2026.08.012 |
| 2 | 基于解耦与组合的大模型知识问答方法 | 0.4651 | 不相关 | http://jcip.cipsc.org.cn/article/doi/10.3969/j.issn.1003-0077.2026.08.008 |
| 3 | 利用大语言模型生成语料的跨语言方位词对语义衍化模式研究 | 0.4585 | 不相关 | http://jcip.cipsc.org.cn/article/doi/10.3969/j.issn.1003-0077.2026.08.002 |

<details><summary>数据源诊断</summary>

- 官网列表: http://jcip.cipsc.org.cn/cn/article/current
- 原始解析 12 篇，保留 12 篇
- 有 6 篇未获取到摘要，文本使用标题+关键词

</details>

## 电子与信息学报

- 源：`journal_site`；期号：2026, 48(7)；发布日期：2026-07-04
- 是否相似主题论文：**是**；命中数：1；阈值：strong≥0.75, weak≥0.6；matcher：`embedding:BAAI/bge-small-zh-v1.5`
- 降级/限制：有 6 篇未获取到摘要，文本使用标题+关键词

| 排名 | 标题 | 分数 | 判定 | 链接 |
|---:|---|---:|---|---|
| 1 | 大语言模型文献挖掘驱动的网络指标体系与场景差异化分析 | 0.6598 | 弱相关 | https://jeit.ac.cn/cn/article/doi/10.11999/JEIT251120 |
| 2 | 多源知识引导的视觉置信度感知的多模态情感分析模型 | 0.4337 | 不相关 | https://jeit.ac.cn/cn/article/doi/10.11999/JEIT260063 |
| 3 | UWF-YOLO: 冗余信息优化的轻量化水下目标检测 | 0.4277 | 不相关 | https://jeit.ac.cn/cn/article/doi/10.11999/JEIT251129 |

<details><summary>数据源诊断</summary>

- 官网列表: https://jeit.ac.cn/article/current
- 原始解析 12 篇，保留 12 篇
- 有 6 篇未获取到摘要，文本使用标题+关键词

</details>

## IEEE Transactions on Pattern Analysis and Machine Intelligence

- 源：`crossref`；期号：48(10)；发布日期：2026-10
- 是否相似主题论文：**否**；命中数：0；阈值：strong≥0.75, weak≥0.6；matcher：`embedding:BAAI/bge-small-zh-v1.5`

| 排名 | 标题 | 分数 | 判定 | 链接 |
|---:|---|---:|---|---|
| 1 | Dataset Pruning: Reducing Training Data by Examining SGD-Influence | 0.4351 | 不相关 | https://doi.org/10.1109/tpami.2026.3703395 |
| 2 | Privacy-Preserving Online Federated Learning for Massive Infinite Streams | 0.4182 | 不相关 | https://doi.org/10.1109/tpami.2026.3697332 |
| 3 | From Zero to Detail: A Progressive Spectral Decoupling Paradigm for UHD Image Restoration With New Benchmark | 0.4101 | 不相关 | https://doi.org/10.1109/tpami.2026.3691530 |

<details><summary>数据源诊断</summary>

- OpenAlex 补全: 摘要 15 篇, 关键词 15 篇

</details>

## Pattern Recognition

- 源：`crossref`；期号：183；发布日期：2027-03
- 是否相似主题论文：**否**；命中数：0；阈值：strong≥0.75, weak≥0.6；matcher：`embedding:BAAI/bge-small-zh-v1.5`

| 排名 | 标题 | 分数 | 判定 | 链接 |
|---:|---|---:|---|---|
| 1 | Text Prior-Guided Cell Alignment with Transformer for Robust Table Structure Recognition | 0.4552 | 不相关 | https://doi.org/10.1016/j.patcog.2026.114832 |
| 2 | Historical document restoration via an Adversarial Frequency-aware Guidance Network | 0.4206 | 不相关 | https://doi.org/10.1016/j.patcog.2026.114828 |
| 3 | Dynamic frequency modulation for controllable text-driven image generation | 0.4174 | 不相关 | https://doi.org/10.1016/j.patcog.2026.114880 |

<details><summary>数据源诊断</summary>

- OpenAlex 补全: 摘要 0 篇, 关键词 13 篇

</details>

## Information Sciences

- 源：`crossref`；期号：761；发布日期：2027-02
- 是否相似主题论文：**否**；命中数：0；阈值：strong≥0.75, weak≥0.6；matcher：`embedding:BAAI/bge-small-zh-v1.5`

| 排名 | 标题 | 分数 | 判定 | 链接 |
|---:|---|---:|---|---|
| 1 | HIRO: Historical intent reasoning with observation for multi-agent reinforcement learning | 0.4454 | 不相关 | https://doi.org/10.1016/j.ins.2026.124125 |
| 2 | An integrated analytical framework for natural gas pricing: combining multi-source drivers, forecast enhancement, and model interpretability | 0.4329 | 不相关 | https://doi.org/10.1016/j.ins.2026.124144 |
| 3 | UniCSL: A unified federated learning framework with client-specific LS-DC loss | 0.4113 | 不相关 | https://doi.org/10.1016/j.ins.2026.124118 |

<details><summary>数据源诊断</summary>

- OpenAlex 补全: 摘要 2 篇, 关键词 15 篇

</details>

## IEEE Transactions on Knowledge and Data Engineering

- 源：`crossref`；期号：38(10)；发布日期：2026-10
- 是否相似主题论文：**否**；命中数：0；阈值：strong≥0.75, weak≥0.6；matcher：`embedding:BAAI/bge-small-zh-v1.5`

| 排名 | 标题 | 分数 | 判定 | 链接 |
|---:|---|---:|---|---|
| 1 | Data and Knowledge Dual-Driven Text Embedding Approaches: A Survey | 0.4528 | 不相关 | https://doi.org/10.1109/tkde.2026.3721883 |
| 2 | Impute On-Demand: Adaptive Correlated Time Series Imputation for Changing Environments | 0.4364 | 不相关 | https://doi.org/10.1109/tkde.2026.3717792 |
| 3 | Large Language Model Empowered Recommendation Meets All-Domain Continual Pre-Training | 0.4338 | 不相关 | https://doi.org/10.1109/tkde.2026.3717059 |

<details><summary>数据源诊断</summary>

- OpenAlex 补全: 摘要 3 篇, 关键词 13 篇

</details>

## IEEE Transactions on Neural Networks and Learning Systems

- 源：`crossref`；期号：37(9)；发布日期：2026-09
- 是否相似主题论文：**否**；命中数：0；阈值：strong≥0.75, weak≥0.6；matcher：`embedding:BAAI/bge-small-zh-v1.5`

| 排名 | 标题 | 分数 | 判定 | 链接 |
|---:|---|---:|---|---|
| 1 | Learning From <i>M</i> -Tuple One-vs-All Confidence Comparison Data | 0.4308 | 不相关 | https://doi.org/10.1109/tnnls.2026.3673280 |
| 2 | Incomplete Multimodal Federated Learning via Masking and Contrasting Prototypes | 0.4197 | 不相关 | https://doi.org/10.1109/tnnls.2026.3658522 |
| 3 | CoreKD: A Context-Aware Local Region Structural Contrastive Knowledge Distillation Framework for Object Detection | 0.4161 | 不相关 | https://doi.org/10.1109/tnnls.2026.3672967 |

<details><summary>数据源诊断</summary>

- OpenAlex 补全: 摘要 14 篇, 关键词 14 篇

</details>

[written] docs/run-online-report.json
[written] docs/run-online-report.md
```

## stderr / 运行日志（含显式降级日志）

```text
.venv/lib/python3.12/site-packages/joblib/_multiprocessing_helpers.py:44: UserWarning: [Errno 13] Permission denied.  joblib will operate in serial mode
  warnings.warn("%s.  joblib will operate in serial mode" % (e,))
19:06:48 INFO sentence_transformers.base.model: Loading SentenceTransformer model from models/bge-small-zh-v1.5.

Loading weights:   0%|          | 0/71 [00:00<?, ?it/s]
Loading weights: 100%|██████████| 71/71 [00:00<00:00, 4430.56it/s]
19:07:30 INFO radar.pipeline: topic=大语言模型驱动的代码生成与漏洞检测 matcher=embedding:BAAI/bge-small-zh-v1.5 offline=False journals=10
19:07:30 WARNING radar.cli: DEGRADED: 有 7 篇未获取到摘要，文本使用标题+关键词
19:07:30 WARNING radar.cli: DEGRADED: 有 6 篇未获取到摘要，文本使用标题+关键词
```
