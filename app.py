"""Assignment Submission Portal (Flask)."""
import json
import os
from urllib.parse import urlparse

from flask import Flask, redirect, render_template, request, url_for


def is_valid_url(url):
    """A valid submission link is an http(s) URL with a host and no spaces."""
    parts = urlparse(url)
    return parts.scheme in ("http", "https") and bool(parts.netloc) and " " not in url


def validate(form):
    """Return a dict of field -> error message (empty dict means valid)."""
    errors = {}
    if not form["name"]:
        errors["name"] = "Name is required."
    if not form["reg_no"]:
        errors["reg_no"] = "Registration number is required."
    if not form["title"]:
        errors["title"] = "Assignment title is required."
    if not form["url"]:
        errors["url"] = "Submission URL is required."
    elif not is_valid_url(form["url"]):
        errors["url"] = "Enter a valid URL starting with http:// or https://"
    return errors


def load_submissions(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_submissions(path, items):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def create_app(data_file=None):
    app = Flask(__name__)
    app.config["DATA_FILE"] = data_file or os.environ.get("DATA_FILE", "submissions.json")

    @app.get("/")
    def index():
        subs = load_submissions(app.config["DATA_FILE"])
        return render_template("index.html", errors={}, form={}, submissions=subs)

    @app.post("/submit")
    def submit():
        form = {k: request.form.get(k, "").strip() for k in ("name", "reg_no", "title", "url")}
        errors = validate(form)
        path = app.config["DATA_FILE"]
        if errors:
            subs = load_submissions(path)
            return render_template("index.html", errors=errors, form=form, submissions=subs), 400
        items = load_submissions(path)
        items.append(form)
        save_submissions(path, items)
        return redirect(url_for("index"), code=303)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
