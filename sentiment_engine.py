"""Rule‑based, lexicon sentiment analyzer (no heavy NLP libs).
Shows: strings, lists, dicts, functions, control flow, docstrings.
"""

# - Strings, lists, dicts, tuples, slicing, list comprehensions (Lec 3). 
# - Control flow: if/elif/else, loops (Lec 2).
# - Functions, default args, docstrings, modules (Lec 4 & 5).
# - Lambda for a small mapping convenience (Lec 6).

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
