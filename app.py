import os
import secrets
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for

from data_loader import get_workbook_path, load_dashboard_payload

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

LOGIN_EMAIL = "priyapriya86127@gmail.com"
LOGIN_PASSWORD = "8531844041"


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def _safe_redirect_target(target: str | None) -> str | None:
    if not target or not isinstance(target, str):
        return None
    if target.startswith("/") and not target.startswith("//"):
        return target
    return None


@app.context_processor
def inject_auth():
    return {
        "logged_in": bool(session.get("logged_in")),
        "user_email": session.get("user_email"),
    }


@app.route("/")
def index():
    return render_template("index.html", year=datetime.now().year)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(_safe_redirect_target(request.args.get("next")) or url_for("dashboard"))

    message = None
    expected_email = LOGIN_EMAIL.strip().lower()
    expected_password = LOGIN_PASSWORD

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        if secrets.compare_digest(
            email.encode("utf-8"), expected_email.encode("utf-8")
        ) and secrets.compare_digest(
            password.encode("utf-8"), expected_password.encode("utf-8")
        ):
            session["logged_in"] = True
            session["user_email"] = email
            nxt = _safe_redirect_target(
                request.form.get("next") or request.args.get("next")
            )
            return redirect(nxt or url_for("dashboard"))
        message = "Invalid email or password."

    return render_template(
        "login.html",
        year=datetime.now().year,
        message=message,
        prefilled_email=LOGIN_EMAIL.strip(),
        next_url=request.form.get("next") or request.args.get("next") or "",
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    payload = load_dashboard_payload()
    updated = datetime.fromtimestamp(payload["data_updated"])
    return render_template(
        "dashboard.html",
        year=datetime.now().year,
        dashboard_data=payload,
        last_updated=updated.strftime("%b %d, %Y %I:%M %p"),
        user_email=session.get("user_email"),
    )


@app.route("/dashboard/statistics")
@login_required
def dashboard_statistics():
    payload = load_dashboard_payload()
    updated = datetime.fromtimestamp(payload["data_updated"])
    return render_template(
        "statistics.html",
        year=datetime.now().year,
        dashboard_data=payload,
        last_updated=updated.strftime("%b %d, %Y %I:%M %p"),
        user_email=session.get("user_email"),
    )


@app.route("/dashboard/map")
@login_required
def dashboard_map():
    payload = load_dashboard_payload()
    updated = datetime.fromtimestamp(payload["data_updated"])
    return render_template(
        "map.html",
        year=datetime.now().year,
        dashboard_data=payload,
        last_updated=updated.strftime("%b %d, %Y %I:%M %p"),
        user_email=session.get("user_email"),
    )


@app.route("/dashboard/trends")
@login_required
def dashboard_trends():
    payload = load_dashboard_payload()
    updated = datetime.fromtimestamp(payload["data_updated"])
    return render_template(
        "trends.html",
        year=datetime.now().year,
        dashboard_data=payload,
        last_updated=updated.strftime("%b %d, %Y %I:%M %p"),
        user_email=session.get("user_email"),
    )


@app.route("/dashboard/vaccination")
@login_required
def dashboard_vaccination():
    payload = load_dashboard_payload()
    updated = datetime.fromtimestamp(payload["data_updated"])
    return render_template(
        "vaccination.html",
        year=datetime.now().year,
        dashboard_data=payload,
        last_updated=updated.strftime("%b %d, %Y %I:%M %p"),
        user_email=session.get("user_email"),
    )


@app.route("/dashboard/news")
@login_required
def dashboard_news():
    payload = load_dashboard_payload()
    updated = datetime.fromtimestamp(payload["data_updated"])
    return render_template(
        "news.html",
        year=datetime.now().year,
        dashboard_data=payload,
        last_updated=updated.strftime("%b %d, %Y %I:%M %p"),
        user_email=session.get("user_email"),
    )


@app.route("/dashboard/about")
@login_required
def dashboard_about():
    payload = load_dashboard_payload()
    updated = datetime.fromtimestamp(payload["data_updated"])
    return render_template(
        "about.html",
        year=datetime.now().year,
        dashboard_data=payload,
        last_updated=updated.strftime("%b %d, %Y %I:%M %p"),
        user_email=session.get("user_email"),
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
