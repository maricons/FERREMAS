from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .extensions import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for("main.home"))
        else:
            flash("Credenciales inválidas", "error")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("El email ya existe", "error")
            return render_template("register.html")

        user = User(
            username=username, email=email, password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        flash("Registro exitoso", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Has cerrado sesión", "success")
    return redirect(url_for("main.home"))


# Google OAuth routes
@auth_bp.route("/google/login")
def google_login():
    # Mock para pruebas
    return redirect(url_for("auth.google_authorized"))


@auth_bp.route("/google/authorized")
def google_authorized():
    if "error" in request.args:
        flash("Error en la autenticación con Google")
        return redirect(url_for("auth.login"))

    # Mock para pruebas
    session["user_id"] = 1
    session["user"] = {
        "email": "test@test.com",
        "name": "Test User",
        "auth_type": "google",
    }
    flash("Login con Google exitoso")
    return redirect(url_for("main.home"))
