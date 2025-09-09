"""
Flask app that wires the engine to a tiny UI.

Why this design (tying to your brief & lectures)?
- Clear separation of concerns via modules (Lec 4: Modules).
- Functions with docstrings (Lec 5), control flow (Lec 2), dict/list ops (Lec 3).
- Small lambda used to prettify labels (Lec 6).
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

from tiny_lexicon import LEXICON
from sentiment_engine import analyze_text
from data_loader import dataset_path, sample_reviews, extract_text, ensure_data_dir, DATA_DIR
from metrics import accumulate_counts

app = Flask(__name__)
os.makedirs(os.path.join(app.root_path, "static", "plots"), exist_ok=True)
app.secret_key = "dev-only"  # for flash messages

# --- Config for uploads (lightweight, built-ins only) ---
ALLOWED_EXT = {".csv", ".tsv"}
def _allowed(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXT

# --- Home page: single review analyzer + small metrics snapshot ---
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    snapshot = None
    ds = dataset_path()

    if request.method == "POST":
        user_text = (request.form.get("review_text") or "").strip()
        if user_text:
            result = analyze_text(user_text, LEXICON)
            # add emoji without importing emoji libs (lambda demo)
            to_emoji = lambda l: "😃" if l == "positive" else "☹️" if l == "negative" else "😐"
            result["emoji"] = to_emoji(result["label"])

    # show a tiny snapshot if a dataset is available
    if ds:
        # Only scan a subset for speed in demo; tune as needed.
        rows = list(sample_reviews(ds, limit=500, delimiter=","))  # adjust if TSV
        snapshot = accumulate_counts(rows)

    return render_template("index.html", result=result, snapshot=snapshot, has_dataset=bool(ds))

# --- Metrics: manager view with simple tables ---
@app.route("/metrics")
def metrics():
    ds = dataset_path()
    if not ds:
        flash("No dataset uploaded yet. Please upload your CSV first.")
        return redirect(url_for("dataset_admin"))

    # Ensure static/plots exists inside the app folder
    plots_dir = os.path.join(app.root_path, "static", "plots")
    os.makedirs(plots_dir, exist_ok=True)

    # Pick delimiter from file extension (prevents empty data)
    delim = "," if ds.lower().endswith(".csv") else "\t"

    # Keep a cap for demo speed; raise/remove for full dataset
    rows = sample_reviews(ds, limit=20000, delimiter=delim)

    # Compute metrics and write PNGs *under* app.static_folder
    from metrics import compute_and_plot
    metrics_payload = compute_and_plot(rows, static_dir=plots_dir)

    # Cache-busting for the <img> tags
    import time
    metrics_payload["plots_version"] = int(time.time())

    return render_template("metrics.html", metrics=metrics_payload)

# --- Admin: upload CSV/TSV and save as data/reviews.csv ---
@app.route("/admin/dataset", methods=["GET", "POST"])
def dataset_admin():
    ensure_data_dir()
    current = dataset_path()
    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            flash("Please choose a CSV/TSV file.")
            return redirect(request.url)
        if not _allowed(file.filename):
            flash("Only .csv or .tsv files are allowed.")
            return redirect(request.url)

        fname = secure_filename(file.filename)
        target = os.path.join(DATA_DIR, "reviews.csv" if fname.endswith(".csv") else "reviews.tsv")
        file.save(target)
        flash(f"Uploaded and saved as {os.path.basename(target)}.")
        return redirect(url_for("metrics"))

    return render_template("dataset_admin.html", current=os.path.basename(current) if current else None)

if __name__ == "__main__":
    app.run(debug=True)
