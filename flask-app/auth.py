from flask import Blueprint, redirect, url_for, session, flash
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage import MemoryStorage
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración del blueprint de autenticación
auth_bp = Blueprint('auth', __name__)

# Configuración de Google OAuth2 usando variables de .env
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ],
    storage=MemoryStorage(),
    redirect_url="/login/google/authorized"
)

# Configuración para desarrollo local NO USAR EN PRODUCCION
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Registrar el blueprint
auth_bp.register_blueprint(google_bp, url_prefix="/login")

@oauth_authorized.connect_via(google_bp)
def google_logged_in(blueprint, token):
    if not token:
        flash('Error al iniciar sesión con Google', 'danger')
        return False
    
    # Obtener información del usuario
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash('Error al obtener información del usuario', 'danger')
        return False
    
    user_info = resp.json()
    
    # Guardar información en la sesión
    session["user"] = {
        "email": user_info["email"],
        "name": user_info["name"],
        "picture": user_info.get("picture"),
        "auth_type": "google"
    }
    
    # Usar email como identificador único para OAuth users
    # Esto es importante para el carrito
    email_hash = hash(user_info["email"])
    session["user_id"] = email_hash
    
    flash('¡Inicio de sesión exitoso con Google!', 'success')
    return redirect(url_for("home"))

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for("home")) 