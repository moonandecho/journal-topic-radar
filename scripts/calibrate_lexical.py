#!/usr/bin/env python3
"""Calibrate the lexical fallback thresholds on real fixture papers.

We build a small positive/negative set from the *real* fixtures.  The goal is
not to fit the eventual demo query; it is to place boundaries above the best
negative pair and near the weakest clearly-positive pair.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar import config
from radar.matcher import LexicalBackend, build_text
from radar.models import Paper

POSITIVE = [
    ("大语言模型的源代码漏洞检测", "基于大语言模型的源代码漏洞检测方法"),
    ("工业缺陷检测", "视觉工业缺陷检测"),
    ("多模态知识图谱补全", "多视图增强图注意力网络的多模态知识图谱补全"),
    ("无监督句子表示", "多级正例约束的无监督句子表示"),
    ("脑机接口连续运动控制", "非侵入式连续运动控制脑-机接口技术综述"),
    ("大模型参数高效微调", "大模型参数高效微调方法综述"),
    ("处理器芯片安全", "处理器芯片安全综述"),
    ("持续学习方法", "面向大模型时代的持续学习方法论演变"),
    ("知识蒸馏低频词翻译", "基于知识蒸馏的低频词翻译优化策略"),
]
# Ambiguous positives (cross-lingual / loose relation) are deliberately not
# used to set the strong boundary:
EXCLUDED_POSITIVE = [
    ("联邦学习通信压缩", "一种基于单比特通信压缩的大语言模型训练方法"),
    ("异常检测", "视觉工业缺陷检测"),
]
NEGATIVE = [
    ("量子计算硬件设计", "基于大语言模型的源代码漏洞检测方法"),
    ("蛋白质结构预测", "多级正例约束的无监督句子表示"),
    ("音乐生成", "处理器芯片安全综述"),
    ("气候变化建模", "大模型参数高效微调方法综述"),
    ("医学图像分割", "无监督句子表示"),
    ("供应链风险预测", "非侵入式连续运动控制"),
    ("金融时间序列预测", "多视图增强图注意力网络的多模态知识图谱补全"),
    ("法律文书生成", "面向红外手势识别的存内计算神经网络推理系统设计"),
    ("数据库事务调度", "视觉工业缺陷检测"),
    ("机器人路径规划", "处理器芯片安全综述"),
]


def load_papers() -> list[Paper]:
    out: list[Paper] = []
    for path in sorted((config.ROOT / "fixtures").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data.get("papers") or []:
            out.append(Paper(
                title=item.get("title", ""),
                abstract=item.get("abstract", ""),
                keywords=list(item.get("keywords") or []),
            ))
    return out


def find(papers: list[Paper], fragment: str) -> Paper | None:
    for p in papers:
        if fragment in (p.title or ""):
            return p
    return None


def main() -> int:
    papers = load_papers()
    if not papers:
        print("FAIL: fixtures/*.json 为空，请先运行真实抓取。")
        return 1
    backend, reasons = __import__("radar.matcher", fromlist=["make_backend"]).make_backend("lexical")
    pos, neg, missing = [], [], []

    def score(topic: str, fragment: str) -> float | None:
        p = find(papers, fragment)
        if not p:
            missing.append(fragment)
            return None
        text, _ = build_text(p)
        return backend.score(topic, [text])[0]

    print("POSITIVE SAMPLES")
    for topic, frag in POSITIVE:
        s = score(topic, frag)
        if s is not None:
            pos.append(s)
            print(f"  score={s:.4f}  topic={topic}  <-  {frag}")
    print("\nEXCLUDED (loose/cross-lingual, not used for strong boundary)")
    for topic, frag in EXCLUDED_POSITIVE:
        s = score(topic, frag)
        if s is not None:
            print(f"  score={s:.4f}  topic={topic}  <-  {frag}")
    print("\nNEGATIVE SAMPLES")
    for topic, frag in NEGATIVE:
        s = score(topic, frag)
        if s is not None:
            neg.append(s)
            print(f"  score={s:.4f}  topic={topic}  <-  {frag}")
    if missing:
        print("\nMISSING FIXTURE FRAGMENTS:", missing)
        return 1
    if not pos or not neg:
        print("FAIL: not enough samples")
        return 1
    neg_max, pos_min = max(neg), min(pos)
    weak = round(neg_max + 0.10, 2)
    strong = round(pos_min + 0.10, 2)
    print("\nSUMMARY")
    print(f"  negative max = {neg_max:.4f}")
    print(f"  positive min = {pos_min:.4f}")
    print(f"  margin = 0.10 above best negative / weakest positive")
    print(f"  proposed lexical weak   = {weak:.2f}")
    print(f"  proposed lexical strong = {strong:.2f}")
    print("\nCopy these values into config/thresholds.yaml after review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
