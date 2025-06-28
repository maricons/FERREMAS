import json
import logging
import os
from datetime import datetime
from decimal import Decimal

from dotenv import load_dotenv
from flasgger import Swagger
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_mail import Mail, Message
from flask_migrate import Migrate
from marshmallow import Schema, fields
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

#from .auth import auth_bp
from .currency_converter import CurrencyConverter
from .extensions import db
from .models import (
    CartItem,
    Category,
    Order,
    OrderItem,
    Product,
    User,
    WebpayTransaction,
)
from .webpay_plus import WebpayPlus

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")

# Registrar el blueprint de autenticación
#app.register_blueprint(auth_bp)

# Configuración para subida de archivos
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gi"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Asegurarse de que el directorio de uploads existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configuración de correo electrónico
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

# Inicializar Flask-Mail
mail = Mail(app)

# Definición del template Swagger
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Ferremas API",
        "description": "Documentación de la API de Ferremas",
        "version": "1.0",
    },
    "definitions": {
        "Product": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "price": {"type": "number"},
                "image": {"type": "string"},
                "description": {"type": "string"},
                "stock": {"type": "integer"},
                "is_featured": {"type": "boolean"},
                "is_promotion": {"type": "boolean"},
                "promotion_price": {"type": "number"},
                "category_id": {"type": "integer"},
            },
        },
        "CartItem": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "user_id": {"type": "integer"},
                "product_id": {"type": "integer"},
                "quantity": {"type": "integer"},
                "product": {"$re": "#/definitions/Product"},
            },
        },
        "Category": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "icon": {"type": "string"},
            },
        },
    },
}

# Inicializar Flasgger para documentación Swagger
swagger = Swagger(app, template=swagger_template)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Configuración de la base de datos
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")


#CADENA DE CONEXIÓN SQL SERVER AZURE:
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mssql+pyodbc://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?driver=ODBC+Driver+18+for+SQL+Server"
)
'''
#CADENA DE CONEXIÓN POSTGRES:
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)

'''
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 86400  # 24 horas

# Configuración de la URL base para Webpay
app.config["BASE_URL"] = os.getenv("BASE_URL", "http://localhost:5000")

# Inicializar extensiones
db.init_app(app)
migrate = Migrate(app, db)

# Inicializar Webpay Plus
webpay = WebpayPlus()

# Inicializar el conversor de monedas
currency_converter = CurrencyConverter()

# Esquemas para serialización
class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    image = fields.Str()
    is_promotion = fields.Bool()
    promotion_price = fields.Float()

class CartItemSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True)
    product = fields.Nested(ProductSchema)


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
cart_item_schema = CartItemSchema()
cart_items_schema = CartItemSchema(many=True)

# rutas
# HOME
@app.route("/")
def home():
    # Obtener información del usuario desde la sesión
    user = session.get("user") if "user" in session else None

    # Obtener todas las categorías
    categories = Category.query.all()

    # Obtener productos destacados
    featured_products = Product.query.filter_by(is_featured=True).limit(8).all()

    # Obtener productos en promoción
    promotion_products = Product.query.filter_by(is_promotion=True).limit(6).all()

    return render_template(
        "index.html",
        user=user,
        categories=categories,
        featured_products=featured_products,
        promotion_products=promotion_products,
    )

# Ruta para ver productos por categoría
@app.route("/categoria/<int:category_id>")
def category_products(category_id):
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category_id).all()
    user = session.get("user") if "user" in session else None

    return render_template(
        "category_products.html", category=category, products=products, user=user
    )

# PRODUCT DETAIL
@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    # Obtener información del usuario desde la sesión
    user = session.get("user") if "user" in session else None
    return render_template("product_detail.html", product=product, user=user)

# CART
@app.route("/carrito")
def carrito():
    # Obtener información del usuario desde la sesión
    user = session.get("user") if "user" in session else None
    return render_template("cart.html", user=user)

# LOGIN

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            flash("Todos los campos son requeridos", "danger")
            return render_template("login.html")
        user = User.query.filter_by(email=email).first()
        if user and user.password and check_password_hash(user.password, password):
            session["user"] = {
                "email": user.email,
                "name": user.username,
                "auth_type": "local",
            }
            session["user_id"] = user.id
            flash("¡Inicio de sesión exitoso!", "success")
            return redirect(url_for("home"))
        else:
            flash("Credenciales inválidas. Por favor, intenta de nuevo.", "danger")
    return render_template("login.html")

# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("user_id", None)
    flash("Has cerrado sesión exitosamente.", "success")
    return redirect(url_for("home"))

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            username = request.form.get("username")
            password = request.form.get("password")
            email = request.form.get("email")

            # Validar campos requeridos
            if not username or not password or not email:
                flash("Todos los campos son requeridos", "danger")
                return redirect(url_for("register"))

            # Validar formato de email
            if "@" not in email or "." not in email:
                flash("Por favor, ingrese un email válido", "danger")
                return redirect(url_for("register"))

            # Validar longitud de contraseña
            if len(password) < 6:
                flash("La contraseña debe tener al menos 6 caracteres", "danger")
                return redirect(url_for("register"))

            # Check if the username already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash(
                    "El nombre de usuario ya existe. Por favor, elija otro.", "danger"
                )
                return redirect(url_for("register"))

            # Check if the email already exists
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash("El email ya está registrado. Por favor, use otro.", "danger")
                return redirect(url_for("register"))

            # Hash the password and create a new user
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
            new_user = User(username=username, password=hashed_password, email=email)

            try:
                db.session.add(new_user)
                db.session.commit()
                flash("¡Registro exitoso! Ahora puede iniciar sesión.", "success")
                return redirect(url_for("login"))
            except Exception:
                db.session.rollback()
                logger.error("Error al crear usuario")
                flash(
                    "Error al crear la cuenta. Por favor, intente nuevamente.", "danger"
                )
                return redirect(url_for("register"))

        except Exception:
            logger.error("Error en el registro")
            flash(
                "Error al procesar el registro. Por favor, intente nuevamente.",
                "danger",
            )
            return redirect(url_for("register"))

    return render_template("register.html")

# Rutas de la API
@app.route("/api/products", methods=["GET"])
def get_products():
    """
    Obtener todos los productos
    ---
    tags:
      - Productos
    responses:
      200:
        description: Lista de productos
        schema:
          type: array
          items:
            $ref: '#/definitions/Product'
    """
    products = Product.query.all()
    return jsonify(products_schema.dump(products))

@app.route("/api/products/<int:id>", methods=["GET"])
def get_product(id):
    """
    Obtener un producto por ID
    ---
    tags:
      - Productos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID del producto
    responses:
      200:
        description: Producto encontrado
        schema:
          $ref: '#/definitions/Product'
      404:
        description: Producto no encontrado
    """
    product = Product.query.get_or_404(id)
    return jsonify(product_schema.dump(product))

@app.route("/api/products", methods=["POST"])
def create_product():
    name = request.form.get("name")
    price_str = request.form.get("price")
    if not name or not price_str:
        return jsonify({"error": "Nombre y precio son requeridos"}), 400
    try:
        price = float(price_str)
    except (TypeError, ValueError):
        return jsonify({"error": "Precio inválido"}), 400

    # Manejar la imagen
    image_path = ""
    if "imageFile" in request.files:
        file = request.files["imageFile"]
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Asegurarse de que el directorio existe
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            image_path = f"uploads/{filename}"
    elif "imageUrl" in request.form and request.form.get("imageUrl"):
        image_path = request.form.get("imageUrl")

    new_product = Product(name=name, price=price, image=image_path)

    db.session.add(new_product)
    db.session.commit()

    return jsonify(product_schema.dump(new_product)), 201

@app.route("/api/products/<int:id>", methods=["PUT"])
def update_product(id):
    product = Product.query.get_or_404(id)

    name = request.form.get("name", product.name)
    price_str = request.form.get("price", str(product.price))
    try:
        price = float(price_str)
    except (TypeError, ValueError):
        price = product.price

    product.name = name
    product.price = price

    # Manejar la imagen
    if "imageFile" in request.files:
        file = request.files["imageFile"]
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Asegurarse de que el directorio existe
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            product.image = f"uploads/{filename}"
    elif "imageUrl" in request.form and request.form.get("imageUrl"):
        product.image = request.form.get("imageUrl")

    db.session.commit()
    return jsonify(product_schema.dump(product))

@app.route("/api/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return "", 204


# API para el Carrito de Compras
@app.route("/api/cart", methods=["GET"])
def get_cart():
    print("\n[GET CART] Iniciando obtención del carrito")
    if not session.get("user_id"):
        print("[GET CART] Usuario no autenticado")
        return jsonify({"error": "Usuario no autenticado"}), 401

    user_id = session.get("user_id")
    print(f"[GET CART] user_id: {user_id}")
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    print(f"[GET CART] Items encontrados: {len(cart_items)}")

    result = []
    for item in cart_items:
        print(f"[GET CART] Procesando item: {item.id}")
        item_data = cart_item_schema.dump(item)
        product = Product.query.get(item.product_id)
        item_data["product"] = product_schema.dump(product)
        result.append(item_data)

    print("[GET CART] Retornando carrito")
    return jsonify(result)

@app.route("/api/cart/add", methods=["POST"])
def add_to_cart():
    print("\n[ADD TO CART] Iniciando proceso de añadir al carrito")
    if not session.get("user_id"):
        print("[ADD TO CART] Usuario no autenticado")
        return jsonify({"error": "Usuario no autenticado"}), 401

    try:
        data = request.get_json()
        print(f"[ADD TO CART] Datos recibidos: {data}")

        if not data:
            print("[ADD TO CART] No se recibieron datos JSON")
            return jsonify({"error": "No se recibieron datos"}), 400

        if "product_id" not in data:
            print("[ADD TO CART] Falta product_id en la solicitud")
            return jsonify({"error": "Se requiere product_id"}), 400

        user_id = session.get("user_id")
        product_id = int(data["product_id"])
        quantity = int(data.get("quantity", 1))

        print(f"[ADD TO CART] user_id: {user_id}, product_id: {product_id}, quantity: {quantity}")

        product = Product.query.get(product_id)
        if not product:
            print(f"[ADD TO CART] Producto {product_id} no encontrado")
            return jsonify({"error": "Producto no encontrado"}), 404

        if product.stock < quantity:
            print(f"[ADD TO CART] Stock insuficiente para el producto {product_id}")
            return jsonify({"error": "No hay suficiente stock disponible"}), 400

        cart_item = CartItem.query.filter_by(
            user_id=user_id, product_id=product_id
        ).first()

        if cart_item:
            print(f"[ADD TO CART] El producto ya está en el carrito, actualizando cantidad")
            cart_item.quantity += quantity
        else:
            print(f"[ADD TO CART] Añadiendo nuevo producto al carrito")
            cart_item = CartItem(
                user_id=user_id, product_id=product_id, quantity=quantity
            )
            db.session.add(cart_item)

        db.session.commit()
        print(f"[ADD TO CART] Commit realizado")

        item_data = cart_item_schema.dump(cart_item)
        item_data["product"] = product_schema.dump(product)

        print(f"[ADD TO CART] Producto añadido exitosamente al carrito")
        return jsonify(item_data), 201

    except ValueError as ve:
        print(f"[ADD TO CART] Error de valor: {ve}")
        return jsonify({"error": "Datos inválidos"}), 400
    except Exception as e:
        print(f"[ADD TO CART] Error inesperado: {e}")
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route("/api/cart/update/<int:item_id>", methods=["PUT"])
def update_cart_item(item_id):
    print(f"\n[UPDATE CART ITEM] Iniciando actualización del item {item_id}")
    if not session.get("user_id"):
        print("[UPDATE CART ITEM] Usuario no autenticado")
        return jsonify({"error": "Usuario no autenticado"}), 401

    data = request.json
    print(f"[UPDATE CART ITEM] Datos recibidos: {data}")
    if not data or "quantity" not in data:
        print("[UPDATE CART ITEM] Falta quantity")
        return jsonify({"error": "Se requiere quantity"}), 400

    user_id = session.get("user_id")
    quantity = data["quantity"]

    cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if not cart_item:
        print("[UPDATE CART ITEM] Item no encontrado en el carrito")
        return jsonify({"error": "Item no encontrado en el carrito"}), 404

    if quantity <= 0:
        print("[UPDATE CART ITEM] Cantidad <= 0, eliminando item")
        db.session.delete(cart_item)
        db.session.commit()
        return "", 204

    print(f"[UPDATE CART ITEM] Actualizando cantidad a {quantity}")
    cart_item.quantity = quantity
    db.session.commit()

    product = Product.query.get(cart_item.product_id)
    item_data = cart_item_schema.dump(cart_item)
    item_data["product"] = product_schema.dump(product)

    print("[UPDATE CART ITEM] Item actualizado correctamente")
    return jsonify(item_data)

@app.route("/api/cart/remove/<int:item_id>", methods=["DELETE"])
def remove_from_cart(item_id):
    print(f"\n[REMOVE FROM CART] Iniciando eliminación del item {item_id}")
    if not session.get("user_id"):
        print("[REMOVE FROM CART] Usuario no autenticado")
        return jsonify({"error": "Usuario no autenticado"}), 401

    user_id = session.get("user_id")
    cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if not cart_item:
        print("[REMOVE FROM CART] Item no encontrado en el carrito")
        return jsonify({"error": "Item no encontrado en el carrito"}), 404

    print("[REMOVE FROM CART] Eliminando item del carrito")
    db.session.delete(cart_item)
    db.session.commit()
    print("[REMOVE FROM CART] Item eliminado correctamente")
    return "", 204

@app.route("/api/cart/clear", methods=["DELETE"])
def clear_cart():
    print("\n[CLEAR CART] Iniciando limpieza del carrito")
    if not session.get("user_id"):
        print("[CLEAR CART] Usuario no autenticado")
        return jsonify({"error": "Usuario no autenticado"}), 401

    user_id = session.get("user_id")
    print(f"[CLEAR CART] user_id: {user_id}")
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    print("[CLEAR CART] Carrito limpiado correctamente")
    return "", 204

# Rutas de Webpay
@app.route("/iniciar-pago", methods=["POST"])
def iniciar_pago():
    try:
        # Verificar si el usuario está autenticado
        if not session.get("user_id"):
            return jsonify({"error": "Usuario no autenticado"}), 401

        user_id = session["user_id"]
        print("\n=== INICIANDO PROCESO DE PAGO ===")
        print(f"Usuario autenticado: {user_id}")

        # Obtener items del carrito
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        if not cart_items:
            return jsonify({"error": "Carrito vacío"}), 400

        # Calcular total
        print("Calculando total de la compra...")
        total = Decimal("0")
        for item in cart_items:
            product = Product.query.get(item.product_id)
            if product:
                total += Decimal(str(product.price)) * Decimal(str(item.quantity))

        print(f"Total calculado: {total}")

        # Crear orden
        print("Creando orden en la base de datos...")
        order = Order(user_id=user_id, total_amount=total, status="pending")
        db.session.add(order)
        db.session.commit()
        print(f"Orden creada con ID: {order.id}")

        # Crear items de la orden
        print("Creando items de la orden...")
        for item in cart_items:
            product = Product.query.get(item.product_id)
            print(f"Procesando item: {item.id}, producto: {product}")
            if product:
                try:
                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        price_at_time=product.price,
                    )
                    db.session.add(order_item)
                except Exception as e:
                    print(f"Error al agregar OrderItem: {e}")
        db.session.commit()
        print("Items de la orden creados exitosamente")

        # Generar número de orden
        buy_order = f"OC-{order.id}"
        print(f"Número de orden generado: {buy_order}")

        # Crear transacción en la base de datos
        print("Creando transacción en la base de datos...")
        transaction = WebpayTransaction(
            order_id=order.id,
            buy_order=buy_order,
            amount=int(total),
            session_id=str(user_id),
            status="pending",
        )
        db.session.add(transaction)
        db.session.commit()
        print("Transacción creada en la base de datos")

        # Configurar URL de retorno
        return_url = url_for("retorno_webpay", _external=True)
        print(f"URL de retorno configurada: {return_url}")

        print("\n=== INICIANDO TRANSACCIÓN EN WEBPAY ===")
        print("Datos que se enviarán a Webpay:")
        print("- Monto: {int(total)}")
        print(f"- Orden de compra: {buy_order}")
        print(f"- ID de sesión: {user_id}")
        print(f"- URL de retorno: {return_url}")

        # Crear transacción en Webpay usando la instancia
        response = webpay.create_transaction(
            amount=int(total),
            buy_order=buy_order,
            session_id=str(user_id),
            return_url=return_url,
        )

        print("\nRespuesta de Webpay:")
        print(json.dumps(response, indent=2))

        # Guardar token en la base de datos
        transaction.token_ws = response["token"]
        db.session.commit()
        print("Token guardado en la base de datos")

        # Vaciar carrito
        CartItem.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        print("Carrito vaciado")

        print("\n=== PROCESO DE INICIO DE PAGO COMPLETADO ===")

        # DEVOLVER SOLO EL CAMPO URL QUE EL FRONTEND ESPERA
        return jsonify({
            "url": response.get("url") or response.get("redirect_url") or response.get("url_webpay"),
            "token": response.get("token")
        })

    except Exception:
        print("\nError en el proceso de pago")
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor"}), 500


def enviar_comprobante(order, user_email):
    """Envía el comprobante de pago por correo electrónico"""
    try:
        print(f"\n=== ENVIANDO COMPROBANTE POR EMAIL ===")
        print(f"Enviando comprobante a: {user_email}")

        msg = Message("Comprobante de Pago - Ferremas", recipients=[user_email])

        # Renderizar el template HTML con los datos de la orden
        html = render_template(
            "email/comprobante.html", order=order, current_year=datetime.now().year
        )

        msg.html = html
        mail.send(msg)
        print("Correo enviado exitosamente")

    except Exception:
        print("\n=== ERROR AL ENVIAR CORREO ===")
        import traceback

        print("Traceback completo:")
        print(traceback.format_exc())


@app.route("/retorno-webpay", methods=["GET", "POST"])
def retorno_webpay():
    print("\n=== PROCESANDO RETORNO DE WEBPAY ===")
    print("Método:", request.method)
    print("Args:", request.args)
    print("Form:", request.form)

    # Obtener token_ws de POST o GET
    token_ws = request.form.get("token_ws") or request.args.get("token_ws")
    tbk_token = request.form.get("TBK_TOKEN")

    print("Token WS:", token_ws)
    print("TBK Token:", tbk_token)

    if tbk_token:
        print("Pago abortado por el usuario")
        # Pago abortado por el usuario
        transaction = WebpayTransaction.query.filter_by(token_ws=token_ws).first()
        if transaction:
            transaction.status = "cancelled"
            transaction.order.status = "cancelled"
            db.session.commit()
            print("Transacción marcada como cancelada")
        return redirect(url_for("comprobante_pago", status="cancelled"))

    if not token_ws:
        print("Error: No se recibió token_ws")
        return redirect(url_for("comprobante_pago", status="error"))

    try:
        print("\nConsultando resultado de la transacción...")
        # Confirmar transacción con Webpay
        response = webpay.confirm_transaction(token_ws)
        print("Respuesta de commit:", response)

        # Buscar la transacción en la base de datos
        transaction = WebpayTransaction.query.filter_by(token_ws=token_ws).first()
        if not transaction:
            print("Error: Transacción no encontrada en la base de datos")
            raise Exception("Transacción no encontrada")

        # Verificar si la respuesta es un diccionario
        if isinstance(response, dict):
            response_code = response.get("response_code")
            amount = response.get("amount")
        else:
            # Si es un objeto, intentar acceder a los atributos
            response_code = getattr(response, "response_code", None)
            amount = getattr(response, "amount", None)

        print(f"Código de respuesta: {response_code}")
        print(f"Monto: {amount}")

        # Actualizar la transacción con la respuesta
        if response_code == 0:
            print("Transacción exitosa")
            transaction.status = "completed"
            transaction.response_code = response_code
            transaction.amount = amount
            transaction.order.status = "completed"

            # Obtener el correo del usuario
            user = User.query.get(transaction.order.user_id)
            if user:
                # Enviar comprobante por correo
                enviar_comprobante(transaction.order, user.email)

            status = "success"
        else:
            print(f"Transacción fallida con código: {response_code}")
            transaction.status = "failed"
            transaction.response_code = response_code
            transaction.order.status = "failed"
            status = "error"

        db.session.commit()
        print("Base de datos actualizada")

        return redirect(url_for("comprobante_pago", status=status))

    except Exception:
        print("\n=== ERROR EN RETORNO WEBPAY ===")
        import traceback

        print("Traceback completo:")
        print(traceback.format_exc())
        return redirect(url_for("comprobante_pago", status="error"))


@app.route("/comprobante-pago")
def comprobante_pago():
    status = request.args.get("status", "error")
    return render_template(
        "comprobante_pago.html", status=status, user=session.get("user")
    )


# Rutas para el conversor de monedas
@app.route("/conversor-moneda")
def currency_converter_page():
    try:
        # Obtener información del usuario desde la sesión
        user = session.get("user") if "user" in session else None
        currencies = currency_converter.get_available_currencies()
        return render_template(
            "currency_converter.html", currencies=currencies, user=user
        )
    except Exception:
        logger.error("Error al cargar el conversor de monedas")
        flash("Error al cargar el conversor de monedas", "danger")
        return redirect(url_for("home"))


@app.route("/api/convert", methods=["POST"])
def convert_currency():
    try:
        # Verificar que la solicitud sea JSON
        if not request.is_json:
            logger.error("La solicitud no es JSON")
            return jsonify({"error": "Se requiere formato JSON"}), 400

        data = request.get_json()
        logger.info(f"Datos recibidos en /api/convert: {data}")

        if not data:
            logger.error("No se recibieron datos JSON")
            return jsonify({"error": "No se recibieron datos"}), 400

        amount = data.get("amount")
        from_currency = data.get("currency")

        logger.info(f"Procesando conversión: amount={amount}, currency={from_currency}")

        if not amount or not from_currency:
            logger.error("Faltan datos requeridos")
            return jsonify({"error": "Se requiere monto y moneda"}), 400

        try:
            amount = float(amount)
            if amount <= 0:
                logger.error(f"Monto inválido: {amount}")
                return jsonify({"error": "El monto debe ser mayor que 0"}), 400
        except (TypeError, ValueError):
            logger.error(f"Error al convertir monto a float: {amount}")
            return jsonify({"error": "El monto debe ser un número válido"}), 400

        logger.info(f"Intentando convertir {amount} {from_currency} a CLP")

        try:
            # Verificar que el conversor esté inicializado correctamente
            if not currency_converter:
                logger.error("El conversor de monedas no está inicializado")
                return (
                    jsonify({"error": "Error en la configuración del conversor"}),
                    500,
                )

            result = currency_converter.convert_to_clp(amount, from_currency)
            logger.info("Conversión exitosa: {result}")
            return jsonify(result)
        except ValueError:
            logger.error("Error en la conversión")
            return jsonify({"error": "Error en la conversión"}), 400
        except Exception:
            logger.error("Error inesperado en la conversión")
            return jsonify({"error": "Error al realizar la conversión"}), 500

    except Exception:
        logger.error("Error general en /api/convert")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/currencies", methods=["GET"])
def get_currencies():
    """
    Obtener las monedas disponibles para el conversor de divisas
    ---
    tags:
      - Conversor de Divisas
    responses:
      200:
        description: Lista de monedas disponibles
        schema:
          type: array
          items:
            type: string
      500:
        description: Error interno del servidor
    """
    try:
        currencies = currency_converter.get_available_currencies()
        return jsonify(currencies)
    except Exception:
        return jsonify({"error": "Error interno del servidor"}), 500


# Rutas para el contacto
@app.route("/contacto")
def contact_page():
    user = session.get("user") if "user" in session else None
    return render_template("contact.html", user=user)


@app.route("/api/contact", methods=["POST"])
def send_contact_email():
    """
    Enviar un mensaje de contacto por email
    ---
    tags:
      - Contacto
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - subject
            - message
          properties:
            name:
              type: string
              example: Juan Pérez
            email:
              type: string
              example: juan@email.com
            subject:
              type: string
              example: Consulta
            message:
              type: string
              example: Hola, tengo una duda sobre un producto.
    responses:
      200:
        description: Mensaje enviado correctamente
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: Datos inválidos o incompletos
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Error al enviar el mensaje
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        required_fields = ["name", "email", "subject", "message"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": "El campo {field} es requerido"}), 400

        # Crear el mensaje
        msg = Message(
            subject=f"Contacto Ferremas: {data['subject']}",
            recipients=[os.getenv("MAIL_DEFAULT_SENDER")],
            reply_to=data["email"],
        )

        # Renderizar el template HTML
        html = render_template(
            "email/contact.html",
            name=data["name"],
            email=data["email"],
            subject=data["subject"],
            message=data["message"],
        )

        msg.html = html
        mail.send(msg)

        return jsonify({"message": "Mensaje enviado correctamente"}), 200

    except Exception:
        logger.error("Error al enviar correo de contacto")
        return jsonify({"error": "Error al enviar el mensaje"}), 500


@app.route("/api/categories", methods=["GET"])
def get_categories():
    """
    Obtener todas las categorías
    ---
    tags:
      - Categorías
    responses:
      200:
        description: Lista de categorías
        schema:
          type: array
          items:
            $ref: '#/definitions/Category'
    """
    categories = Category.query.all()
    result = []
    for cat in categories:
        result.append(
            {
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "icon": cat.icon,
            }
        )
    return jsonify(result)


@app.route("/checkout")
def checkout():
    if not session.get("user_id"):
        flash("Debes iniciar sesión para continuar con la compra.", "warning")
        return redirect(url_for("login"))

    # Verificar si hay items en el carrito
    cart_items = CartItem.query.filter_by(user_id=session["user_id"]).all()
    if not cart_items:
        flash("Tu carrito está vacío. Agrega productos antes de continuar.", "info")
        return redirect(url_for("carrito"))

    # Calcular el total
    total = Decimal("0")
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product:
            total += Decimal(str(product.price)) * Decimal(str(item.quantity))

    return render_template(
        "checkout.html", user=session.get("user"), cart_items=cart_items, total=total
    )


# SIEMPRE DEBE ESTAR AL FINAL O EL PROGRAMA NO FUNCIONA
if __name__ == "__main__":
    # Lee el puerto de la variable de entorno PORT, o usa 8000 por defecto (para local)
    port = int(os.environ.get("PORT", 8000))

    app.run(debug=True, host="0.0.0.0", port=port)