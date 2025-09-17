"""Aggregation helpers for dashboard cards and trend chart.
Shows: loops, conditionals, dictionaries/lists, small lambdas.
"""
from collections import defaultdict
from statistics import mean
from sentiment_engine import analyze_review


def _filter_rows(rows: list[dict], *, year_filter: str, state_filter: str) -> list[dict]:
    def keep(r: dict) -> bool:
        ok_year = (year_filter == "All" or r.get("YearMonth", "").startswith(str(year_filter)))
        ok_state = (state_filter in ("All States", "All") or r.get("State") == state_filter)
        return ok_year and ok_state

    return [r for r in rows if keep(r)]

def monthly_card_metrics(rows: list[dict], *, year_filter: str, state_filter: str) -> dict:
    """Return current-month metrics and deltas vs the previous month.
    - total_reviews: count for latest month
    - total_delta_pct: % change in total count vs previous month
    - pos_pct/neg_pct: % of reviews in latest month
    - pos_delta/neg_delta: percentage-point change vs previous month
    """
    filt = _filter_rows(rows, year_filter=year_filter, state_filter=state_filter)
    # bucket by YearMonth
    buckets: dict[str, dict[str, int]] = defaultdict(lambda: {"positive": 0, "neutral": 0, "negative": 0})

    for r in filt:
        ym = r.get("YearMonth", "")
        if not ym.startswith(str(year_filter)):
            continue
        label = r.get("Label") or analyze_review(r.get("Review Text", ""))[0]
        buckets[ym][label] += 1

    total = len(filt)
    months = sorted(buckets.keys())
    if not months:
        return {
            "total_reviews": 0, "total_delta_pct": 0.0,
            "pos_pct": 0.0, "pos_delta": 0.0,
            "neg_pct": 0.0, "neg_delta": 0.0,
            "avg_rating": 0.0,
        }

    curr_m = months[-1]
    prev_m = months[-2] if len(months) >= 2 else None

    def pct(count, total): return (100.0 * count / total) if total else 0.0

    c_counts = buckets[curr_m]
    c_total = sum(c_counts.values())
    c_pos_pct = pct(c_counts["positive"], c_total)
    c_neg_pct = pct(c_counts["negative"], c_total)

    # previous month stats
    if prev_m:
        p_counts = buckets[prev_m]
        p_total = sum(p_counts.values())
        p_pos_pct = pct(p_counts["positive"], p_total)
        p_neg_pct = pct(p_counts["negative"], p_total)
        total_delta_pct = ((c_total - p_total) / p_total * 100.0) if p_total else 0.0
        pos_delta = c_pos_pct - p_pos_pct  # percentage points
        neg_delta = c_neg_pct - p_neg_pct  # percentage points
    else:
        total_delta_pct = 0.0
        pos_delta = 0.0
        neg_delta = 0.0

    return {
        "total_reviews": total,
        "total_delta_pct": round(total_delta_pct, 1),
        "pos_pct": round(c_pos_pct, 1),
        "pos_delta": round(pos_delta, 1),
        "neg_pct": round(c_neg_pct, 1),
        "neg_delta": round(neg_delta, 1),
        # keep avg_rating simple: average across filtered rows (whole year)
        "avg_rating": round(mean([r.get("Review Rating", 0) for r in filt]) if filt else 0.0, 1),
    }


def monthly_sentiment_trend(rows: list[dict], year: str) -> list[dict]:
    # group by YearMonth then compute pos/neu/neg counts
    buckets: dict[str, dict[str, int]] = defaultdict(lambda: {"positive": 0, "neutral": 0, "negative": 0})

    for r in rows:
        if not r.get("YearMonth", "").startswith(str(year)):
            continue
        label = r.get("Label") or analyze_review(r.get("Review Text", ""))[0]
        ym = r.get("YearMonth")
        buckets[ym][label] += 1

    # return chronologically sorted list of monthly percentages
    months = sorted(buckets.keys())
    trend = []
    for m in months:
        counts = buckets[m]
        total = sum(counts.values()) or 1
        trend.append(
            {
                "month": m,
                "pos": round(100 * counts["positive"] / total, 1),
                "neu": round(100 * counts["neutral"] / total, 1),
                "neg": round(100 * counts["negative"] / total, 1),
            }
        )
    return trend