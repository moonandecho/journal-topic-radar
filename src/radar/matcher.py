from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import math
import os
import re
from typing import Any, Iterable

from radar.config import ROOT, hf_endpoint, load_thresholds

STOPWORDS = {
    "的", "了", "和", "与", "及", "或", "在", "是", "为", "对", "中", "研究", "分析", "方法",
    "基于", "一种", "及其", "应用", "问题", "模型", "算法", "系统", "数据", "本文", "通过", "提出",
    "a", "an", "the", "of", "and", "or", "for", "in", "on", "with", "to", "from", "by", "is", "are",
    "this", "that", "we", "我们的", "以及", "进行", "得到", "实现", "具有", "可以",
}


def build_text(paper: Any) -> tuple[str, str]:
    """Return (text, text_source) exactly following the requirement."""
    title = getattr(paper, "title", "") or ""
    keywords = getattr(paper, "keywords", None) or []
    abstract = getattr(paper, "abstract", "") or ""
    if abstract:
        text = " ".join(x for x in [title, " ".join(keywords), abstract] if x)
        return text, "title+keywords+abstract" if keywords else "title+abstract"
    if keywords:
        return " ".join(x for x in [title, " ".join(keywords)] if x), "title+keywords"
    return title, "title"


@dataclass
class MatchBackend:
    name: str
    kind: str  # embedding / lexical
    thresholds: dict[str, float]
    reason: str = ""

    def score(self, topic: str, texts: list[str]) -> list[float]:
        raise NotImplementedError


class LexicalBackend(MatchBackend):
    def __init__(self, thresholds: dict[str, float], reason: str = ""):
        super().__init__(name="lexical-bm25-char-ngram", kind="lexical", thresholds=thresholds, reason=reason)
        import logging as _logging
        import jieba  # imported lazily; dependency is in requirements.txt
        try:
            jieba.setLogLevel(_logging.WARNING)
        except Exception:
            pass

        self._jieba = jieba

    def _tokens(self, text: str) -> list[str]:
        text = text or ""
        toks: list[str] = []
        # English / alphanumeric terms
        toks.extend(re.findall(r"[a-zA-Z][a-zA-Z0-9_\-\.\+]{1,}", text.lower()))
        # Chinese words via jieba
        for w in self._jieba.lcut(text):
            w = w.strip().lower()
            if len(w) >= 2 and any("\u4e00" <= c <= "\u9fff" for c in w) and w not in STOPWORDS:
                toks.append(w)
        # Chinese unigrams + bigrams (helps when jieba splits technical compounds)
        chinese = "".join(re.findall(r"[\u4e00-\u9fff]", text))
        for ch in chinese:
            if ch not in STOPWORDS:
                toks.append(ch)
        for i in range(len(chinese) - 1):
            bg = chinese[i:i + 2]
            if bg not in STOPWORDS:
                toks.append(bg)
        return toks

    def score(self, topic: str, texts: list[str]) -> list[float]:
        if not texts:
            return []
        q_toks = self._tokens(topic)
        docs = [self._tokens(t) for t in texts]
        n = len(docs)
        if not q_toks:
            return [0.0] * n
        df: dict[str, int] = {}
        for d in docs:
            for term in set(d):
                df[term] = df.get(term, 0) + 1
        avgdl = sum(len(d) for d in docs) / max(1, n)
        k1, b = 1.5, 0.75
        q_counts: dict[str, int] = {}
        for t in q_toks:
            q_counts[t] = q_counts.get(t, 0) + 1
        q_weights: dict[str, float] = {}
        for t, qtf in q_counts.items():
            idf = math.log(1.0 + (n - df.get(t, 0) + 0.5) / (df.get(t, 0) + 0.5))
            q_weights[t] = (1.0 + math.log(qtf)) * idf
        q_norm = math.sqrt(sum(v * v for v in q_weights.values())) or 1.0
        out: list[float] = []
        for d in docs:
            dl = len(d) or 1
            counts: dict[str, int] = {}
            for t in d:
                counts[t] = counts.get(t, 0) + 1
            dv: dict[str, float] = {}
            for t, tf in counts.items():
                idf = math.log(1.0 + (n - df.get(t, 0) + 0.5) / (df.get(t, 0) + 0.5))
                dv[t] = idf * (tf * (k1 + 1.0)) / (tf + k1 * (1.0 - b + b * dl / avgdl))
            dot = sum(q_weights.get(t, 0.0) * dv.get(t, 0.0) for t in q_weights)
            d_norm = math.sqrt(sum(v * v for v in dv.values())) or 1.0
            out.append(max(0.0, min(1.0, dot / (q_norm * d_norm))))
        return out


class EmbeddingBackend(MatchBackend):
    def __init__(self, thresholds: dict[str, float], model_ref: str, model_path: Path | None = None):
        super().__init__(name="embedding:BAAI/bge-small-zh-v1.5", kind="embedding", thresholds=thresholds)
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(str(model_path or model_ref), cache_folder=str(ROOT / "models"), device="cpu")
        # BGE v1.5 recommends a retrieval instruction for the query side.
        self._query_prefix = "为这个句子生成表示以用于检索相关文章："

    def score(self, topic: str, texts: list[str]) -> list[float]:
        if not texts:
            return []
        q = self._query_prefix + topic
        emb = self._model.encode([q] + list(texts), normalize_embeddings=True, show_progress_bar=False, batch_size=32)
        qv = emb[0]
        return [float(max(0.0, min(1.0, v))) for v in emb[1:] @ qv]


def make_backend(prefer: str = "auto", thresholds: dict[str, dict[str, float]] | None = None,
                 offline: bool = False) -> tuple[MatchBackend, list[str]]:
    """Return a backend plus explicit degradation reasons.

    prefer: auto | embedding | lexical
    offline: if true, never attempt a model download; missing local cache degrades.
    """
    th = thresholds or load_thresholds()
    reasons: list[str] = []
    emb_th = th["embedding"]
    lex_th = th["lexical"]
    # Requirement: always point HuggingFace downloads at the mirror.
    os.environ.setdefault("HF_ENDPOINT", hf_endpoint())
    if offline:
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    if prefer in ("auto", "embedding"):
        model_path = ROOT / "models" / "bge-small-zh-v1.5"
        local_ok = (model_path / "config.json").exists() and (any(model_path.glob("*.bin")) or any(model_path.glob("*.safetensors")))
        try:
            if local_ok:
                return EmbeddingBackend(emb_th, str(model_path), model_path=model_path), reasons
            return EmbeddingBackend(emb_th, "BAAI/bge-small-zh-v1.5"), reasons
        except Exception as e:
            reason = f"sentence-transformers/bge-small-zh-v1.5 不可用，降级为词法后端: {type(e).__name__}: {e}"
            reasons.append(reason)
            if prefer == "embedding":
                reasons.append("用户强制 embedding，但加载失败；按显式降级策略使用 lexical")
            return LexicalBackend(lex_th, reason=reason), reasons
    if prefer == "lexical":
        reasons.append("用户指定 matcher=lexical（非语义 embedding 后端，报告已显式标注）")
        return LexicalBackend(lex_th, reason=reasons[-1]), reasons
    reasons.append(f"未知 matcher={prefer}，降级为 lexical")
    return LexicalBackend(lex_th, reason=reasons[-1]), reasons
