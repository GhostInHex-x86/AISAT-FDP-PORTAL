import math
import sqlite3
from services.logging_service import logger
from config import ROWS_PER_PAGE, SPREADSHEET_ID, SECRET_KEY
from werkzeug.security import check_password_hash
from services.fdp_service import process_submission
from decorators.auth import admin_required, faculty_required
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from services.cache_service import get_dashboard_stats, get_all_submissions, get_submission_count, get_all_faculty

app = Flask(__name__)
app.secret_key = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):

    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role


def get_db_connection():
    conn = sqlite3.connect("database/users.db")
    conn.row_factory = sqlite3.Row
    return conn


@login_manager.user_loader
def load_user(user_id):

    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    conn.close()

    if user:
        return User(
            user["id"],
            user["username"],
            user["role"]
        )

    return None


@app.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:

        if current_user.role == "admin":
            return redirect(url_for("admin"))

        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password_hash"], password):

            login_user(
                User(
                    user["id"],
                    user["username"],
                    user["role"]
                )
            )

            if user["role"] == "admin":
                logger.info(f"Admin {username} logged in successfully.")
                return redirect(url_for("admin"))

            logger.info(f"User {username} logged in successfully.")
            return redirect(url_for("dashboard"))

        logger.warning(f"Failed login attempt for username: {username}")
        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logger.info(
        f"{current_user.role} '{current_user.username}' logged out."
    )
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


@app.errorhandler(403)
def forbidden(error):
    return render_template("403.html"), 403


@app.route("/submit", methods=["POST"])
@login_required
@faculty_required
def submit():
    try:
        process_submission(request)
        flash("Submission received!", "success")
    except Exception as e:
        logger.exception("Submission failed.")
        flash(str(e), "danger")

    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required
@faculty_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/admin")
@login_required
@admin_required
def admin():
    page = request.args.get("page", 1, type=int)
    offset = (page - 1) * ROWS_PER_PAGE

    total_rows = get_submission_count(
        search=request.args.get("search"),
        program_type=request.args.get("program_type")
    )
    total_pages = max(1, math.ceil(total_rows / ROWS_PER_PAGE))

    submissions = get_all_submissions(
        search=request.args.get("search"),
        program_type=request.args.get("program_type"),
        sort=request.args.get("sort", "newest"),
        limit=ROWS_PER_PAGE,
        offset=offset
    )

    faculties = get_all_faculty()
    stats = get_dashboard_stats()
    return render_template(
        "admin.html",
        stats=stats,
        submissions=submissions,
        page=page,
        per_page=ROWS_PER_PAGE,
        total_pages=total_pages,
        spreadsheet_id=SPREADSHEET_ID,
        faculties=faculties
    )


if __name__ == "__main__":
    app.run(debug=True)
