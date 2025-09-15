# """
# CareSense: A fundamentals-first, lexicon-based sentiment engine.

# Key Python concepts used (per INF1002):
# - Strings, lists, dicts, tuples, slicing, list comprehensions (Lec 3). 
# - Control flow: if/elif/else, loops (Lec 2).
# - Functions, default args, docstrings, modules (Lec 4 & 5).
# - Lambda for a small mapping convenience (Lec 6).
# """

# from typing import List, Tuple, Dict

# # A minimal stopword set – handcrafted to avoid external deps
# STOPWORDS = {
#     "a","an","the","and","or","but","if","so","to","of","for","in","on","at","with",
#     "this","that","these","those","it","is","are","was","were","be","been","being",
#     "i","you","he","she","they","we","me","him","her","them","my","your","our","their"
# }

# # Simple punctuation set for cleaning
# PUNCT = set(",.!?:;\"'()[]{}-/\\")

# NEGATIONS = {"not", "no", "never", "n't"}
# INTENSIFIERS = {"very": 1.5, "really": 1.3, "so": 1.2, "extremely": 1.8}
# DEINTENSIFIERS = {"slightly": 0.7, "somewhat": 0.8, "barely": 0.6}

# def normalize(text: str) -> str:
#     """Lowercase and strip leading/trailing whitespace."""
#     return text.lower().strip()

# def remove_punct(text: str) -> str:
#     """Remove basic punctuation characters."""
#     cleaned_chars = []
#     for ch in text:
#         if ch not in PUNCT:
#             cleaned_chars.append(ch)
#     return "".join(cleaned_chars)

# def tokenize(text: str) -> List[str]:
#     """
#     Split into tokens by whitespace. 
#     (We avoid external tokenizers to emphasize fundamentals.)
#     """
#     return [t for t in text.split() if t]

# def drop_stopwords(tokens: List[str]) -> List[str]:
#     """Remove common stopwords (very simple list)."""
#     return [t for t in tokens if t not in STOPWORDS]

# def split_sentences(text: str) -> List[str]:
#     """
#     Simple sentence splitter based on ., !, ?.
#     Keeps it lightweight for the module.
#     """
#     sentences = []
#     buff = []
#     enders = {'.', '!', '?'}
#     for ch in text:
#         buff.append(ch)
#         if ch in enders:
#             sentences.append("".join(buff).strip())
#             buff = []
#     if buff:
#         sentences.append("".join(buff).strip())
#     return sentences

# def score_tokens(tokens: List[str], lexicon: Dict[str, float]) -> float:
#     """
#     Score a token list with:
#       - basic lexicon lookup,
#       - single-word negation (flip next sentiment),
#       - degree modifiers (intensifiers/deintensifiers) scaling the next word,
#     Example: "not good" => flip 'good'; "very good" => boost 'good'.
#     """
#     score = 0.0
#     i = 0
#     while i < len(tokens):
#         t = tokens[i]
#         # Negation: invert next sentiment-bearing word
#         if t in NEGATIONS and i + 1 < len(tokens):
#             nxt = tokens[i + 1]
#             base = lexicon.get(nxt, 0.0)
#             score += -base  # flip
#             i += 2
#             continue

#         # Intensifiers/de-intensifiers: scale next sentiment-bearing word
#         if t in INTENSIFIERS and i + 1 < len(tokens):
#             nxt = tokens[i + 1]
#             base = lexicon.get(nxt, 0.0)
#             score += base * INTENSIFIERS[t]
#             i += 2
#             continue

#         if t in DEINTENSIFIERS and i + 1 < len(tokens):
#             nxt = tokens[i + 1]
#             base = lexicon.get(nxt, 0.0)
#             score += base * DEINTENSIFIERS[t]
#             i += 2
#             continue

#         # Default: add token sentiment if known
#         score += lexicon.get(t, 0.0)
#         i += 1

#     return score

# def analyze_text(text: str, lexicon: Dict[str, float]) -> Dict:
#     """
#     Full pipeline for one review:
#     1) Normalize, 2) sentence split, 3) per-sentence scoring with simple preprocessing.
#     Returns total score, label, top positive/negative sentences, and a sliding-window peak.
#     """
#     norm = normalize(text)
#     sents = split_sentences(norm)
#     sent_scores: List[Tuple[str, float]] = []

#     total = 0.0
#     for s in sents:
#         s_nopunct = remove_punct(s)
#         tokens = drop_stopwords(tokenize(s_nopunct))
#         sc = score_tokens(tokens, lexicon)
#         sent_scores.append((s, sc))
#         total += sc

#     # Label by simple thresholding
#     label = "positive" if total > 0.5 else "negative" if total < -0.5 else "neutral"

#     # Find most ± sentences
#     most_pos = max(sent_scores, key=lambda x: x[1]) if sent_scores else ("", 0.0)
#     most_neg = min(sent_scores, key=lambda x: x[1]) if sent_scores else ("", 0.0)

#     # Sliding window over sentence scores to find strongest segment (window size = 3 or fewer)
#     best_segment = {"start": 0, "end": 0, "score": 0.0, "text": ""}
#     for window in range(1, min(3, len(sent_scores)) + 1):  # window size 1..3
#         for i in range(0, len(sent_scores) - window + 1):
#             seg = sent_scores[i:i+window]
#             seg_score = sum(sc for _, sc in seg)
#             if abs(seg_score) > abs(best_segment["score"]):
#                 best_segment["start"] = i
#                 best_segment["end"] = i + window - 1
#                 best_segment["score"] = seg_score
#                 best_segment["text"] = " ".join(s for s, _ in seg)

#     return {
#         "total_score": total,
#         "label": label,
#         "sentence_scores": sent_scores,
#         "most_positive_sentence": most_pos,
#         "most_negative_sentence": most_neg,
#         "strongest_segment": best_segment
#     }


"""Rule‑based, lexicon sentiment analyzer (no heavy NLP libs).
Shows: strings, lists, dicts, functions, control flow, docstrings.
"""
from tiny_lexicon import POLARITY

NEGATORS = {"not", "no", "never", "n't"}
INTENSIFIERS = {"very": 1.25, "really": 1.2, "extremely": 1.5, "too": 1.15}
DEINTENSIFIERS = {"slightly": 0.8, "somewhat": 0.9, "barely": 0.7}
PUNCT_BOOST = {"!": 1.1, "?": 1.05}


def simple_tokenize(text: str) -> list[str]:
    """Very small tokenizer: lower, split on spaces, strip punctuation at ends.
    Intentionally basic to align with Programming Fundamentals.
    """
    raw = text.lower().split()
    tokens: list[str] = []
    for w in raw:
        # strip common punctuation from ends only
        start, end = 0, len(w)
        while start < end and not w[start].isalnum():
            start += 1
        while end > start and not w[end - 1].isalnum():
            end -= 1
        core = w[start:end]
        if core:
            tokens.append(core)
    return tokens


def analyze_review(text: str) -> tuple[str, float]:
    """Return (label, score) where label∈{positive, neutral, negative}.

    Rules used (kept small & readable):
    * Sum polarities from tiny lexicon.
    * Negation flips the following word's sign.
    * Intensifiers scale the following word.
    * De‑intensifiers shrink the following word.
    * Ending punctuation can slightly boost magnitude.
    """
    tokens = simple_tokenize(text)
    total = 0.0
    negate_next = False
    scale = 1.0

    for i, t in enumerate(tokens):
        # control flow with if/elif – fundamentals
        if t in NEGATORS:
            negate_next = True
            continue
        if t in INTENSIFIERS:
            scale *= INTENSIFIERS[t]
            continue
        if t in DEINTENSIFIERS:
            scale *= DEINTENSIFIERS[t]
            continue

        # lexicon lookup (dict)
        val = POLARITY.get(t, 0.0)
        if negate_next:
            val = -val
            negate_next = False

        total += val * scale
        # decay scale gradually so multiple intensifiers don’t explode
        scale = 1.0 + (scale - 1.0) * 0.5

    # punctuation boost (very small)
    if text.endswith("!"):
        total *= PUNCT_BOOST["!"]
    elif text.endswith("?"):
        total *= PUNCT_BOOST["?"]

    # map to label with simple thresholds
    label = "neutral"
    if total >= 0.5:
        label = "positive"
    elif total <= -0.5:
        label = "negative"

    return label, round(total, 3)


def label_to_color(label: str) -> str:
    return {"positive": "#22c55e", "neutral": "#f59e0b", "negative": "#ef4444"}.get(label, "#6b7280")
