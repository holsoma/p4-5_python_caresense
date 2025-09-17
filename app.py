"""CareSense – Flask entry point.
Demonstrates: modules, functions, control flow, string formatting, dictionaries, file I/O use through helpers.
"""
# - Clear separation of concerns via modules (Lec 4: Modules).
# - Functions with docstrings (Lec 5), control flow (Lec 2), dict/list ops (Lec 3).
# - Small lambda used to prettify labels (Lec 6).

from flask import Flask, render_template, request, redirect, url_for

from data_loader import load_reviews_csv
from metrics import monthly_sentiment_trend, monthly_card_metrics
from sentiment_engine import analyze_review, label_to_color

app = Flask(__name__)

# ---- In-memory "state" (simple for Fundamentals; no DB) ---------------------
REVIEWS = []  # list[dict]


def init_data():
    """Load a small demo dataset once at startup.
    Uses CSV and plain Python lists/dicts to emphasize fundamentals.
    """
    global REVIEWS
    if not REVIEWS:
        REVIEWS = load_reviews_csv("data/sample_reviews_300.csv")
        # Attach sentiment labels if missing
        for r in REVIEWS:
            if not r.get("Label"):
                r["Label"], r["Score"] = analyze_review(r.get("Review Text", ""))


@app.route("/")
def dashboard():
    init_data()
    # Read filters from query parameters (simple examples)
    year = request.args.get("year", "2024")
    state = request.args.get("state", "All States")

    metrics = monthly_card_metrics(REVIEWS, year_filter=year, state_filter=state)
    trend = monthly_sentiment_trend(REVIEWS, year)

    return render_template(
        "index.html",
        year=year,
        state=state,
        metrics=metrics,
        trend=trend,
    )


@app.route("/reviews")
def reviews():
    init_data()
    labeled = [
        {
            **r,
            "LabelColor": label_to_color(r.get("Label", "neutral")),
            "Snippet": (r.get("Review Text", "")[:140] + "…") if len(r.get("Review Text", "")) > 140 else r.get("Review Text", ""),
        }
        for r in REVIEWS
    ]
    # Sort by sentiment score (lambda demo) – highest first
    labeled.sort(key=lambda x: x.get("Score", 0), reverse=True)
    return render_template("reviews.html", reviews=labeled)


@app.route("/analyze", methods=["POST"])
def analyze_text():
    """Analyze a single free‑text review from a form submission."""
    text = request.form.get("text", "").strip()
    if not text:
        return redirect(url_for("reviews"))
    label, score = analyze_review(text)
    # Simple flash‑less feedback via query params
    return redirect(url_for("reviews") + f"?new_label={label}&new_score={score}")


if __name__ == "__main__":
    app.run(debug=True)


