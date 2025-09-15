# """
# Flask app that wires the engine to a tiny UI.

# Why this design (tying to your brief & lectures)?
# - Clear separation of concerns via modules (Lec 4: Modules).
# - Functions with docstrings (Lec 5), control flow (Lec 2), dict/list ops (Lec 3).
# - Small lambda used to prettify labels (Lec 6).
# """

# from flask import Flask, render_template, request, redirect, url_for, flash
# from werkzeug.utils import secure_filename
# import os

# from tiny_lexicon import LEXICON
# from sentiment_engine import analyze_text
# from data_loader import dataset_path, sample_reviews, extract_text, ensure_data_dir, DATA_DIR
# from metrics import accumulate_counts

# app = Flask(__name__)
# os.makedirs(os.path.join(app.root_path, "static", "plots"), exist_ok=True)
# app.secret_key = "dev-only"  # for flash messages

# # --- Config for uploads (lightweight, built-ins only) ---
# ALLOWED_EXT = {".csv", ".tsv"}
# def _allowed(filename: str) -> bool:
#     _, ext = os.path.splitext(filename.lower())
#     return ext in ALLOWED_EXT

# # --- Home page: single review analyzer + small metrics snapshot ---
# @app.route("/", methods=["GET", "POST"])
# def index():
#     result = None
#     snapshot = None
#     ds = dataset_path()

#     if request.method == "POST":
#         user_text = (request.form.get("review_text") or "").strip()
#         if user_text:
#             result = analyze_text(user_text, LEXICON)
#             # add emoji without importing emoji libs (lambda demo)
#             to_emoji = lambda l: "😃" if l == "positive" else "☹️" if l == "negative" else "😐"
#             result["emoji"] = to_emoji(result["label"])

#     # show a tiny snapshot if a dataset is available
#     if ds:
#         # Only scan a subset for speed in demo; tune as needed.
#         rows = list(sample_reviews(ds, limit=500, delimiter=","))  # adjust if TSV
#         snapshot = accumulate_counts(rows)

#     return render_template("index.html", result=result, snapshot=snapshot, has_dataset=bool(ds))

# # --- Metrics: manager view with simple tables ---
# @app.route("/metrics")
# def metrics():
#     ds = dataset_path()
#     if not ds:
#         flash("No dataset uploaded yet. Please upload your CSV first.")
#         return redirect(url_for("dataset_admin"))

#     # Ensure static/plots exists inside the app folder
#     plots_dir = os.path.join(app.root_path, "static", "plots")
#     os.makedirs(plots_dir, exist_ok=True)

#     # Pick delimiter from file extension (prevents empty data)
#     delim = "," if ds.lower().endswith(".csv") else "\t"

#     # Keep a cap for demo speed; raise/remove for full dataset
#     rows = sample_reviews(ds, limit=20000, delimiter=delim)

#     # Compute metrics and write PNGs *under* app.static_folder
#     from metrics import compute_and_plot
#     metrics_payload = compute_and_plot(rows, static_dir=plots_dir)

#     # Cache-busting for the <img> tags
#     import time
#     metrics_payload["plots_version"] = int(time.time())

#     return render_template("metrics.html", metrics=metrics_payload)

# # --- Admin: upload CSV/TSV and save as data/reviews.csv ---
# @app.route("/admin/dataset", methods=["GET", "POST"])
# def dataset_admin():
#     ensure_data_dir()
#     current = dataset_path()
#     if request.method == "POST":
#         file = request.files.get("file")
#         if not file or file.filename == "":
#             flash("Please choose a CSV/TSV file.")
#             return redirect(request.url)
#         if not _allowed(file.filename):
#             flash("Only .csv or .tsv files are allowed.")
#             return redirect(request.url)

#         fname = secure_filename(file.filename)
#         target = os.path.join(DATA_DIR, "reviews.csv" if fname.endswith(".csv") else "reviews.tsv")
#         file.save(target)
#         flash(f"Uploaded and saved as {os.path.basename(target)}.")
#         return redirect(url_for("metrics"))

#     return render_template("dataset_admin.html", current=os.path.basename(current) if current else None)

# if __name__ == "__main__":
#     app.run(debug=True)


"""CareSense – Flask entry point.
Demonstrates: modules, functions, control flow, string formatting, dictionaries, file I/O use through helpers.
"""
from flask import Flask, render_template, request, redirect, url_for

from data_loader import load_reviews_csv
from metrics import compute_dashboard_metrics, monthly_sentiment_trend
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
        REVIEWS = load_reviews_csv("data/sample_reviews.csv")
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

    metrics = compute_dashboard_metrics(REVIEWS, year_filter=year, state_filter=state)
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


