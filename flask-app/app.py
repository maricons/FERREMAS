from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import Schema, fields
import os
from werkzeug.utils import secure_filename
from auth import auth_bp
from dotenv import load_dotenv
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.common.integration_type import IntegrationType
import uuid



# Cargar variables de entorno
load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")

# Registrar el blueprint de autenticación
app.register_blueprint(auth_bp)

# Configuración para subida de archivos
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

WEBPAY_PLUS_COMMERCE_CODE = os.getenv("WEBPAY_PLUS_COMMERCE_CODE", IntegrationCommerceCodes.WEBPAY_PLUS)
WEBPAY_PLUS_API_KEY = os.getenv("WEBPAY_PLUS_API_KEY", IntegrationApiKeys.WEBPAY)
WEBPAY_PLUS_ENVIRONMENT_STR = os.getenv("WEBPAY_PLUS_ENVIRONMENT", "INTEGRATION").upper() # O IntegrationType.PRODUCTION

if WEBPAY_PLUS_ENVIRONMENT_STR == "PRODUCTION":
    options = WebpayOptions(WEBPAY_PLUS_COMMERCE_CODE, WEBPAY_PLUS_API_KEY, IntegrationType.LIVE) # CORRECTO para v6.0.0
else: # Por defecto, o si es "INTEGRATION"
    options = WebpayOptions(WEBPAY_PLUS_COMMERCE_CODE, WEBPAY_PLUS_API_KEY, IntegrationType.TEST) 

tx = Transaction(options)

# Asegurarse de que el directorio de uploads existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#logica de la base de datos
# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas

db = SQLAlchemy(app)

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Product {self.name}>'

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # In production, use hashed passwords

    def __repr__(self):
        return f'<User {self.username}>'

# Cart Item model
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    
    # Relaciones
    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))
    
    def __repr__(self):
        return f'<CartItem {self.product_id} ({self.quantity})>'

# Esquema para serialización
class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    image = fields.Str()

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
@app.route('/')
def home():
    # Obtener información del usuario desde la sesión
    user = None
    if 'user' in session:
        if isinstance(session['user'], dict) and 'email' in session['user']:  # Google OAuth
            user = session['user']
        else:  # Login normal
            user = session.get('user')
    
    products = Product.query.all()  # retrieve all products
    return render_template('index.html', products=products, user=user)

# PRODUCT DETAIL
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Obtener información del usuario desde la sesión
    user = None
    if 'user' in session:
        if isinstance(session['user'], dict) and 'email' in session['user']:  # Google OAuth
            user = session['user']
        else:  # Login normal
            user = session.get('user')
    
    return render_template('product_detail.html', product=product, user=user)

# CART
@app.route('/carrito')
def carrito():
    # Obtener información del usuario desde la sesión
    user = None
    if 'user' in session:
        if isinstance(session['user'], dict) and 'email' in session['user']:  # Google OAuth
            user = session['user']
        else:  # Login normal
            user = session.get('user')
    
    return render_template('cart.html', user=user)

#LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
         username = request.form.get('username')
         password = request.form.get('password')
         user = User.query.filter_by(username=username).first()
         if user and check_password_hash(user.password, password):
             session['user'] = user.username
             session['user_id'] = user.id
             flash('Login successful!', 'success')
             return redirect(url_for('home'))
         else:
             flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

#LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        # Hash the password and create a new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Rutas de la API
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify(products_schema.dump(products))

@app.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify(product_schema.dump(product))

@app.route('/api/products', methods=['POST'])
def create_product():
    name = request.form.get('name')
    price = float(request.form.get('price'))
    
    # Manejar la imagen
    image_path = ''
    if 'imageFile' in request.files:
        file = request.files['imageFile']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Asegurarse de que el directorio existe
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = f'uploads/{filename}'
    elif 'imageUrl' in request.form and request.form.get('imageUrl'):
        image_path = request.form.get('imageUrl')
    
    new_product = Product(
        name=name,
        price=price,
        image=image_path
    )
    
    db.session.add(new_product)
    db.session.commit()
    
    return jsonify(product_schema.dump(new_product)), 201

@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    
    product.name = request.form.get('name', product.name)
    product.price = float(request.form.get('price', product.price))
    
    # Manejar la imagen
    if 'imageFile' in request.files:
        file = request.files['imageFile']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Asegurarse de que el directorio existe
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            product.image = f'uploads/{filename}'
    elif 'imageUrl' in request.form and request.form.get('imageUrl'):
        product.image = request.form.get('imageUrl')
    
    db.session.commit()
    return jsonify(product_schema.dump(product))

@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return '', 204

# API para el Carrito de Compras
@app.route('/api/cart', methods=['GET'])
def get_cart():
    if not session.get('user_id'):
        return jsonify({"error": "Usuario no autenticado"}), 401
    
    user_id = session.get('user_id')
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    # Incluir información del producto en cada item del carrito
    result = []
    for item in cart_items:
        item_data = cart_item_schema.dump(item)
        product = Product.query.get(item.product_id)
        item_data['product'] = product_schema.dump(product)
        result.append(item_data)
    
    return jsonify(result)

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    if not session.get('user_id'):
        return jsonify({"error": "Usuario no autenticado"}), 401
    
    data = request.json
    if not data or 'product_id' not in data:
        return jsonify({"error": "Se requiere product_id"}), 400
    
    user_id = session.get('user_id')
    product_id = data['product_id']
    quantity = data.get('quantity', 1)
    
    # Verificar si el producto existe
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Producto no encontrado"}), 404
    
    # Verificar si el producto ya está en el carrito
    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    if cart_item:
        # Actualizar cantidad si ya existe
        cart_item.quantity += quantity
    else:
        # Crear nuevo item en el carrito
        cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    
    # Incluir información del producto en la respuesta
    item_data = cart_item_schema.dump(cart_item)
    item_data['product'] = product_schema.dump(product)
    
    return jsonify(item_data), 201

@app.route('/api/cart/update/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    if not session.get('user_id'):
        return jsonify({"error": "Usuario no autenticado"}), 401
    
    data = request.json
    if not data or 'quantity' not in data:
        return jsonify({"error": "Se requiere quantity"}), 400
    
    user_id = session.get('user_id')
    quantity = data['quantity']
    
    # Buscar el item en el carrito
    cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if not cart_item:
        return jsonify({"error": "Item no encontrado en el carrito"}), 404
    
    if quantity <= 0:
        # Eliminar el item si la cantidad es 0 o negativa
        db.session.delete(cart_item)
        db.session.commit()
        return '', 204
    
    # Actualizar la cantidad
    cart_item.quantity = quantity
    db.session.commit()
    
    # Incluir información del producto en la respuesta
    product = Product.query.get(cart_item.product_id)
    item_data = cart_item_schema.dump(cart_item)
    item_data['product'] = product_schema.dump(product)
    
    return jsonify(item_data)

@app.route('/api/cart/remove/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    if not session.get('user_id'):
        return jsonify({"error": "Usuario no autenticado"}), 401
    
    user_id = session.get('user_id')
    
    # Buscar el item en el carrito
    cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if not cart_item:
        return jsonify({"error": "Item no encontrado en el carrito"}), 404
    
    # Eliminar el item
    db.session.delete(cart_item)
    db.session.commit()
    
    return '', 204

@app.route('/api/cart/clear', methods=['DELETE'])
def clear_cart():
    if not session.get('user_id'):
        return jsonify({"error": "Usuario no autenticado"}), 401
    
    user_id = session.get('user_id')
    
    # Eliminar todos los items del carrito para este usuario
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    return '', 204
#RUTAS  DE PAGO

@app.route('/iniciar_pago_webpay', methods=['POST'])
def iniciar_pago_webpay():
    # ... (código de validación de usuario, carrito, cálculo de monto) ...
    if 'user_id' not in session:
        flash('Debes iniciar sesión para pagar.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cart_items = CartItem.query.filter_by(user_id=user_id).all()

    if not cart_items:
        flash('Tu carrito está vacío.', 'info')
        return redirect(url_for('carrito'))

    total_amount = 0
    for item in cart_items:
        product = db.session.get(Product, item.product_id)
        if product:
            total_amount += product.price * item.quantity

    if total_amount <= 0:
        flash('El monto del carrito no es válido.', 'danger')
        return redirect(url_for('carrito'))

    buy_order = uuid.uuid4().hex[:26]
    session_id = str(session['user_id']) 
    amount = int(round(total_amount))
    return_url = url_for('retorno_webpay', _external=True)

    try:
        response_data = tx.create(buy_order, session_id, amount, return_url) # Renombrado a response_data
        
        app.logger.info(f"Respuesta de tx.create: {response_data}")
        app.logger.info(f"Tipo de respuesta de tx.create: {type(response_data)}")

        # Verificar si la respuesta es un diccionario y contiene las claves necesarias
        if isinstance(response_data, dict) and 'url' in response_data and 'token' in response_data:
            transbank_url = response_data['url']
            transbank_token = response_data['token']
            
            session['webpay_buy_order'] = buy_order
            # session['webpay_session_id'] = session_id # Ya no lo guardábamos así
            session['webpay_transbank_token'] = transbank_token # Guardar el token correcto

            app.logger.info(f"Transacción creada exitosamente. Redirigiendo a: {transbank_url} con token: {transbank_token}")
            return render_template('webpay_redirect.html', url=transbank_url, token=transbank_token)
        
        # Si no es un dict con url y token, o si es otro tipo de objeto que SÍ tiene atributos .url y .token (poco probable ahora)
        elif hasattr(response_data, 'url') and hasattr(response_data, 'token'):
            # Esto es para el caso en que SÍ fuera un objeto como se esperaba originalmente
            app.logger.info("Respuesta de tx.create es un objeto con atributos .url y .token.")
            session['webpay_buy_order'] = buy_order
            session['webpay_transbank_token'] = response_data.token

            return render_template('webpay_redirect.html', url=response_data.url, token=response_data.token)
        
        else:
            # Si no es ninguna de las anteriores, es un error inesperado
            error_message = "Respuesta inesperada de Transbank al crear la transacción."
            if isinstance(response_data, dict):
                error_message = response_data.get('error_message', str(response_data))
            
            app.logger.error(f"Formato de respuesta de Transbank no reconocido: {response_data}")
            raise Exception(f"Error Transbank: {error_message}")

    except Exception as e:
        app.logger.error(f"Error al procesar creación de transacción Webpay: {e}", exc_info=True) # exc_info=True para más detalle del traceback
        flash(f'Error al iniciar el pago con Webpay: {str(e)}', 'danger')
        return redirect(url_for('carrito'))


@app.route('/retorno_webpay', methods=['GET', 'POST'])
def retorno_webpay():
    token_ws = request.form.get('token_ws') or request.args.get('token_ws')
    
    tbk_token_cancel = request.form.get("TBK_TOKEN") or request.args.get("TBK_TOKEN")
    tbk_orden_compra_cancel = request.form.get("TBK_ORDEN_COMPRA") or request.args.get("TBK_ORDEN_COMPRA")
    tbk_id_sesion_cancel = request.form.get("TBK_ID_SESION") or request.args.get("TBK_ID_SESION")

    original_buy_order_from_session = session.get('webpay_buy_order')

    # 1. Manejo de Cancelación por parte del usuario en la plataforma de Webpay
    if tbk_token_cancel and not token_ws:
        app.logger.warning(f"Webpay: Usuario canceló antes de pagar (TBK_TOKEN: {tbk_token_cancel}). Orden original: {original_buy_order_from_session}")
        flash('Pago cancelado por el usuario en Webpay.', 'warning')
        session.pop('webpay_buy_order', None)
        session.pop('webpay_transbank_token', None)
        return redirect(url_for('pago_fallido', reason='cancelado_antes_de_pago_tbk', buy_order=original_buy_order_from_session or "Desconocida"))

    if tbk_orden_compra_cancel and tbk_id_sesion_cancel and not token_ws:
        app.logger.warning(f"Webpay: Pago interrumpido o cancelado (TBK_ORDEN_COMPRA: {tbk_orden_compra_cancel}). Orden original: {original_buy_order_from_session}")
        if original_buy_order_from_session and tbk_orden_compra_cancel != original_buy_order_from_session:
            app.logger.error(f"Discrepancia en buy_order en cancelación. Sesión: {original_buy_order_from_session}, Recibido de TBK: {tbk_orden_compra_cancel}")
            flash('Error en los datos de retorno de Webpay durante la cancelación.', 'danger')
            return redirect(url_for('pago_fallido', reason='error_datos_retorno_cancelacion_tbk', buy_order=tbk_orden_compra_cancel))
        
        flash('Pago cancelado o interrumpido por el usuario en Webpay.', 'warning')
        session.pop('webpay_buy_order', None)
        session.pop('webpay_transbank_token', None)
        return redirect(url_for('pago_fallido', reason='cancelado_o_interrumpido_tbk', buy_order=tbk_orden_compra_cancel))

    # 2. Flujo normal de Commit: se debe recibir token_ws
    if not token_ws:
        app.logger.warning(f"Retorno de Webpay sin token_ws (y no es cancelación TBK). Orden original: {original_buy_order_from_session}. Data: {request.form or request.args}")
        flash('Error: No se pudo completar el proceso de pago. Intenta nuevamente.', 'danger')
        session.pop('webpay_buy_order', None)
        session.pop('webpay_transbank_token', None)
        return redirect(url_for('pago_fallido', reason='sin_token_ws_commit', buy_order=original_buy_order_from_session or "Desconocida"))

    # 3. Intentar el Commit de la transacción
    try:
        app.logger.info(f"Intentando commit de Webpay con token_ws: {token_ws} para orden original en sesión: {original_buy_order_from_session}")
        response_data = tx.commit(token_ws)
        app.logger.info(f"Respuesta de tx.commit: {response_data}")

        if not isinstance(response_data, dict):
            app.logger.error(f"Respuesta de tx.commit no es un diccionario: {type(response_data)}. Contenido: {response_data}")
            raise Exception("Formato de respuesta de Transbank inesperado tras commit.")

        status = response_data.get('status')
        response_buy_order = response_data.get('buy_order')
        response_amount = response_data.get('amount')
        card_number_last_digits = response_data.get('card_detail', {}).get('card_number', '****')
        authorization_code = response_data.get('authorization_code')
        payment_type_code = response_data.get('payment_type_code')
        response_code = response_data.get('response_code')

        if not original_buy_order_from_session or response_buy_order != original_buy_order_from_session:
            app.logger.error(f"CRÍTICO: Discrepancia de buy_order tras commit. Sesión: {original_buy_order_from_session}, Respuesta TBK: {response_buy_order}. Token_ws: {token_ws}")
            flash('Error de seguridad crítico en la transacción. Contacte a soporte.', 'danger')
            return redirect(url_for('pago_fallido', reason='error_seguridad_buy_order_commit', buy_order=response_buy_order or original_buy_order_from_session))
        
        if status == 'AUTHORIZED' and response_code == 0:
            flash(f'¡Pago Aprobado! Gracias por tu compra. Orden: {response_buy_order}', 'success')
            app.logger.info(f"Pago APROBADO. Orden: {response_buy_order}, Monto: {response_amount}, Tarjeta: ****{card_number_last_digits[-4:]}, AuthCode: {authorization_code}, PaymentType: {payment_type_code}")

            # --- LÓGICA DE POST-PAGO EXITOSO ---
            # 1. Guardar en BBDD (Aquí necesitarás tu modelo `Order` si lo tienes)
            # Por ahora, solo logueamos que se debería guardar.
            app.logger.info(f"Simulando guardado de orden {response_buy_order} como PAGADA en BBDD.")
            # Ejemplo si tuvieras un modelo Order:
            # order = Order.query.filter_by(buy_order=response_buy_order).first()
            # if order:
            #     order.status = "PAGADO"
            #     order.transbank_authorization_code = authorization_code
            #     # ... otros campos ...
            #     db.session.commit()
            # else:
            #     app.logger.error(f"Orden {response_buy_order} no encontrada en BBDD para marcar como pagada.")

            # 2. Vaciar el carrito del usuario
            user_id = session.get('user_id')
            if user_id:
                CartItem.query.filter_by(user_id=user_id).delete()
                db.session.commit()
                app.logger.info(f"Carrito vaciado para usuario {user_id} tras pago de orden {response_buy_order}")
            
            # 3. Limpiar datos de Webpay de la sesión
            session.pop('webpay_buy_order', None)
            session.pop('webpay_transbank_token', None)

            return redirect(url_for('pago_exitoso', buy_order=response_buy_order, amount=response_amount))
        
        else:
            flash(f'Pago Rechazado o Fallido. Orden: {response_buy_order}. Estado: {status}. Código: {response_code}', 'warning')
            app.logger.warning(f"Pago RECHAZADO/FALLIDO. Orden: {response_buy_order}, Estado TBK: {status}, Código Respuesta TBK: {response_code}. Respuesta: {response_data}")
            
            session.pop('webpay_buy_order', None)
            session.pop('webpay_transbank_token', None)
            
            return redirect(url_for('pago_fallido', reason=f"estado_{status}_codigo_{response_code}", buy_order=response_buy_order))

    except Exception as e:
        buy_order_on_error = session.get('webpay_buy_order', 'desconocida_en_excepcion_commit')
        app.logger.error(f"Excepción crítica durante el commit o procesamiento para orden {buy_order_on_error} con token_ws {token_ws}: {e}", exc_info=True)
        flash('Ocurrió un error inesperado al finalizar tu pago. Contacte a soporte.', 'danger')
        
        session.pop('webpay_buy_order', None)
        session.pop('webpay_transbank_token', None)
        
        return redirect(url_for('pago_fallido', reason='excepcion_critica_commit', buy_order=buy_order_on_error))

@app.route('/pago_exitoso')
def pago_exitoso():
    buy_order = request.args.get('buy_order')
    amount = request.args.get('amount')
    # Para obtener el nombre de usuario, si 'user' en sesión es el username:
    user_display_name = session.get('user', 'Cliente') # 'Cliente' como fallback
    # Si 'user' en sesión es un objeto/dict con más info, ajusta cómo obtienes el nombre.
    return render_template('pago_exitoso.html', user=user_display_name, buy_order=buy_order, amount=amount)

@app.route('/pago_fallido')
def pago_fallido():
    reason = request.args.get('reason')
    buy_order = request.args.get('buy_order')
    user_display_name = session.get('user', 'Cliente')
    return render_template('pago_fallido.html', user=user_display_name, reason=reason, buy_order=buy_order)



# SIEMPRE DEBE ESTAR AL FINAL O EL PROGRAMA NO FUNCIONA
if __name__ == '__main__':
    # Crear las tablas si no existen
    with app.app_context():
        db.create_all()
    app.run(debug=True)