"""
CareSense Metrics + Plots (matplotlib)

What this module does:
1) Compute lightweight, rule-based aggregates from review rows (accumulate_counts).
2) Turn those aggregates into bar charts saved under static/plots/ (make_plots).

Fundamentals shown:
- Control flow & loops (Lec 2), dict/list operations & comprehensions (Lec 3),
- Functions w/ docstrings, modules & file I/O (Lec 4, Lec 5),
- A small lambda for label formatting (Lec 6),
- Matplotlib for graphs (as suggested in course materials).

References: Project brief & PF lectures. 
"""

from typing import Dict, Iterable, Tuple, List, Optional
from collections import defaultdict
import os

# Use a non-interactive backend for server environments
import matplotlib
matplotlib.use("Agg")  # render to files
import matplotlib.pyplot as plt  # allowed plotting library

from sentiment_engine import analyze_text
from tiny_lexicon import LEXICON


# -------------------------- METRICS (unchanged API) --------------------------

def bucket_rating(raw: str) -> str:
    """Map free-form rating to '1'..'5' buckets (strings)."""
    try:
        r = int(float(raw))
        return str(min(max(r, 1), 5))
    except Exception:
        return "NA"

def accumulate_counts(rows: Iterable[Dict[str, str]]) -> Dict:
    """
    One pass over rows → label counts, rating histogram, issues by state,
    issue buckets, and frequent negative terms (from lexicon).
    """
    label_counts: Dict[str, int] = defaultdict(int)
    rating_hist: Dict[str, int] = defaultdict(int)
    issues_by_state: Dict[str, int] = defaultdict(int)  # count negatives per state
    neg_terms: Dict[str, int] = defaultdict(int)

    ISSUE_KEYS = {
        "wait": ["wait", "waiting", "delay", "delayed", "queue"],
        "staff": ["rude", "unfriendly", "dismissive", "attitude"],
        "cleanliness": ["dirty", "unclean", "filthy"],
        "billing": ["billing", "charge", "charges", "expensive"]
    }
    issue_buckets: Dict[str, int] = defaultdict(int)

    for row in rows:
        text = (row.get("Review Text", "") or "").strip()
        if not text:
            continue

        result = analyze_text(text, LEXICON)
        label = result["label"]
        label_counts[label] += 1

        rating_hist[bucket_rating(row.get("Review Rating", ""))] += 1

        state = (row.get("state", "") or "Unknown").strip() or "Unknown"
        if label == "negative":
            issues_by_state[state] += 1
            t = text.lower()

            # naive keyword buckets
            for k, vocab in ISSUE_KEYS.items():
                if any(v in t for v in vocab):
                    issue_buckets[k] += 1

            # top negative tokens from lexicon
            for w in t.replace(",", " ").replace(".", " ").split():
                if w in LEXICON and LEXICON[w] < 0:
                    neg_terms[w] += 1

    def top_k(d: Dict[str, int], k: int = 10) -> List[Tuple[str, int]]:
        return sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))[:k]

    return {
        "label_counts": dict(label_counts),
        "rating_hist": dict(rating_hist),
        "issues_by_state_top": top_k(issues_by_state, 10),
        "issue_buckets": dict(issue_buckets),
        "neg_terms_top": top_k(neg_terms, 15)
    }


# -------------------------- PLOTTING HELPERS (PRETTIER) --------------------------

def _ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)

def _hbar_plot(
    pairs: List[Tuple[str, int]],
    title: str,
    xlabel: str,
    ylabel: str,
    savepath: str,
    sort_desc: bool = True,
    figsize=(9, 5),
    dpi=150
) -> str:
    """
    Horizontal bar chart for [(label, value), ...].
    - Sorts by value (desc) by default: best for 'top' lists.
    - Adds value labels and light grid for readability.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if not pairs:
        plt.figure(figsize=(4, 2), dpi=dpi)
        plt.text(0.5, 0.5, "No data", ha="center", va="center")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(savepath, bbox_inches="tight")
        plt.close()
        return savepath

    pairs = sorted(pairs, key=lambda kv: kv[1], reverse=sort_desc)
    labels = [k for k, _ in pairs]
    values = [v for _, v in pairs]

    plt.figure(figsize=figsize, dpi=dpi, constrained_layout=True)
    bars = plt.barh(labels, values, edgecolor="white", alpha=0.9)
    plt.gca().invert_yaxis()  # highest at top
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(axis="x", linestyle=":", alpha=0.4)

    # annotate values at the end of bars
    for bar, v in zip(bars, values):
        plt.text(v + max(values) * 0.01, bar.get_y() + bar.get_height()/2, str(v), va="center")

    plt.savefig(savepath, bbox_inches="tight")
    plt.close()
    return savepath

def _pie_plot(
    d: Dict[str, int],
    title: str,
    savepath: str,
    key_order: List[str] | None = None,
    figsize=(6, 6),
    dpi=150
) -> str:
    """
    Pie chart for a dictionary {label: value}.
    - Auto-percentage formatting
    - Explodes the biggest slice slightly for emphasis
    - Optional key_order to control slice order (e.g., labels)
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if not d or sum(d.values()) == 0:
        plt.figure(figsize=(4, 2), dpi=dpi)
        plt.text(0.5, 0.5, "No data", ha="center", va="center")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(savepath, bbox_inches="tight")
        plt.close()
        return savepath

    if key_order:
        items = [(k, d.get(k, 0)) for k in key_order]
    else:
        items = sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))

    labels = [k for k, _ in items]
    sizes = [v for _, v in items]

    # explode the largest slice a bit
    max_idx = sizes.index(max(sizes))
    explode = [0.06 if i == max_idx else 0.02 for i in range(len(sizes))]

    plt.figure(figsize=figsize, dpi=dpi, constrained_layout=True)
    wedges, texts, autotexts = plt.pie(
        sizes,
        labels=labels,
        autopct=lambda pct: f"{pct:.1f}%",
        startangle=120,
        explode=explode,
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
        textprops={"fontsize": 10}
    )
    plt.title(title)
    plt.savefig(savepath, bbox_inches="tight")
    plt.close()
    return savepath

def make_plots(metrics: Dict, static_dir: str = "static/plots") -> Dict[str, str]:
    """
    Turn computed metrics into prettier PNG charts.
    - Sentiment distribution: PIE (composition)
    - Rating histogram: PIE (composition of ratings)
    - Top negative states: HBAR (ranking)
    - Issue buckets: HBAR (ranking)
    - Frequent negative terms: HBAR (ranking)
    """
    _ensure_dir(static_dir)

    # 1) Sentiment distribution (pie)
    labels_png = os.path.join(static_dir, "labels.png")
    _pie_plot(
        metrics.get("label_counts", {}),
        title="Sentiment Distribution",
        savepath=labels_png
    )

    # 2) Rating histogram (pie) in order 1..5, NA
    ratings_png = os.path.join(static_dir, "ratings.png")
    _pie_plot(
        metrics.get("rating_hist", {}),
        title="Rating Composition",
        savepath=ratings_png,
        key_order=["1", "2", "3", "4", "5", "NA"]
    )

    # 3) Top negative states (horizontal bar)
    neg_states_png = os.path.join(static_dir, "neg_states.png")
    _hbar_plot(
        metrics.get("issues_by_state_top", []),
        title="Top Negative States",
        xlabel="Negative Reviews",
        ylabel="State",
        savepath=neg_states_png
    )

    # 4) Issue buckets (horizontal bar)
    issues_png = os.path.join(static_dir, "issues.png")
    _hbar_plot(
        list(metrics.get("issue_buckets", {}).items()),
        title="Issue Buckets (keyword-based)",
        xlabel="Mentions in Negative Reviews",
        ylabel="Issue",
        savepath=issues_png
    )

    # 5) Frequent negative terms (horizontal bar)
    neg_terms_png = os.path.join(static_dir, "neg_terms.png")
    _hbar_plot(
        metrics.get("neg_terms_top", []),
        title="Frequent Negative Terms",
        xlabel="Count",
        ylabel="Term",
        savepath=neg_terms_png
    )

    return {
        "labels_png": labels_png,
        "ratings_png": ratings_png,
        "neg_states_png": neg_states_png,
        "issues_png": issues_png,
        "neg_terms_png": neg_terms_png
    }

def compute_and_plot(rows, static_dir: str = "static/plots") -> dict:
    """
    Convenience wrapper used by app.py:
      - computes metrics
      - generates plots
      - returns a single dict with metrics + plot paths under ['plots']
    """
    m = accumulate_counts(rows)
    p = make_plots(m, static_dir=static_dir)
    out = dict(m)
    out["plots"] = p
    return out