from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import Schema, fields
import os
from werkzeug.utils import secure_filename
from auth import auth_bp
from dotenv import load_dotenv
from webpay_plus import WebpayPlus
from decimal import Decimal
import json
from extensions import db

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

# Asegurarse de que el directorio de uploads existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas

# Configuración de la URL base para Webpay
app.config['BASE_URL'] = os.getenv('BASE_URL', 'http://localhost:5000')

# Inicializar extensiones
db.init_app(app)

# Inicializar Webpay Plus
webpay = WebpayPlus(app)

# Importar modelos después de inicializar db
from models import Order, OrderItem, WebpayTransaction, Product, User, CartItem

# Esquemas para serialización
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

# Rutas de Webpay
@app.route('/iniciar-pago', methods=['POST'])
def iniciar_pago():
    print("\n=== INICIANDO PROCESO DE PAGO ===")
    if not session.get('user_id'):
        print("Error: Usuario no autenticado")
        return jsonify({'error': 'Usuario no autenticado'}), 401
    
    try:
        print(f"Usuario autenticado: {session['user_id']}")
        # Obtener items del carrito
        cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
        if not cart_items:
            print("Error: Carrito vacío")
            return jsonify({'error': 'Carrito vacío'}), 400
        
        print("Calculando total de la compra...")
        # Calcular total
        total = sum(item.quantity * item.product.price for item in cart_items)
        print(f"Total calculado: {total}")
        
        print("Creando orden en la base de datos...")
        try:
            # Crear orden
            order = Order(
                user_id=session['user_id'],
                total_amount=total,
                status='pending'
            )
            db.session.add(order)
            db.session.flush()
            print(f"Orden creada con ID: {order.id}")
            
            # Crear items de la orden
            print("Creando items de la orden...")
            for cart_item in cart_items:
                order_item = OrderItem(
                    order=order,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    price_at_time=cart_item.product.price
                )
                db.session.add(order_item)
            
            # Generar orden de compra única
            buy_order = f"OC-{order.id}"
            print(f"Número de orden generado: {buy_order}")
            
            print("Creando transacción en la base de datos...")
            # Crear transacción en la base de datos
            transaction = WebpayTransaction(
                order=order,
                buy_order=buy_order,
                amount=total,
                session_id=str(session['user_id'])
            )
            db.session.add(transaction)
            db.session.commit()
            print("Transacción creada en la base de datos")
            
            # Iniciar transacción en Webpay
            return_url = url_for('retorno_webpay', _external=True)
            print(f"URL de retorno configurada: {return_url}")
            
            try:
                print("\n=== INICIANDO TRANSACCIÓN EN WEBPAY ===")
                print("Datos que se enviarán a Webpay:")
                print(f"- Monto: {int(total)}")
                print(f"- Orden de compra: {buy_order}")
                print(f"- ID de sesión: {str(session['user_id'])}")
                print(f"- URL de retorno: {return_url}")
                
                webpay_response = webpay.create_transaction(
                    amount=int(total),
                    buy_order=buy_order,
                    session_id=str(session['user_id']),
                    return_url=return_url
                )
                
                print("\nRespuesta de Webpay recibida:")
                print(webpay_response)
                
                if not webpay_response or 'token' not in webpay_response or 'url' not in webpay_response:
                    raise ValueError("Respuesta inválida de Webpay")
                
                # Actualizar transacción con el token
                transaction.token_ws = webpay_response['token']
                db.session.commit()
                print("Token guardado en la base de datos")
                
                # Vaciar el carrito
                CartItem.query.filter_by(user_id=session['user_id']).delete()
                db.session.commit()
                print("Carrito vaciado")
                
                print("\n=== PROCESO DE INICIO DE PAGO COMPLETADO ===")
                return jsonify(webpay_response)
                
            except Exception as e:
                print("\n=== ERROR AL CREAR TRANSACCIÓN WEBPAY ===")
                print(f"Error: {str(e)}")
                print(f"Tipo de error: {type(e)}")
                import traceback
                print("Traceback completo:")
                print(traceback.format_exc())
                db.session.rollback()
                return jsonify({'error': 'Error al procesar el pago con Webpay'}), 500
            
        except Exception as e:
            print("\n=== ERROR AL CREAR ORDEN ===")
            print(f"Error: {str(e)}")
            print(f"Tipo de error: {type(e)}")
            import traceback
            print("Traceback completo:")
            print(traceback.format_exc())
            db.session.rollback()
            return jsonify({'error': 'Error al crear la orden'}), 500
            
    except Exception as e:
        print("\n=== ERROR GENERAL ===")
        print(f"Error: {str(e)}")
        print(f"Tipo de error: {type(e)}")
        import traceback
        print("Traceback completo:")
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': 'Error al procesar el pago'}), 500

@app.route('/retorno-webpay', methods=['GET', 'POST'])
def retorno_webpay():
    print("\n=== PROCESANDO RETORNO DE WEBPAY ===")
    print("Método:", request.method)
    print("Args:", request.args)
    print("Form:", request.form)
    
    # Obtener token_ws de POST o GET
    token_ws = request.form.get('token_ws') or request.args.get('token_ws')
    tbk_token = request.form.get('TBK_TOKEN')
    
    print("Token WS:", token_ws)
    print("TBK Token:", tbk_token)
    
    if tbk_token:
        print("Pago abortado por el usuario")
        # Pago abortado por el usuario
        transaction = WebpayTransaction.query.filter_by(token_ws=token_ws).first()
        if transaction:
            transaction.status = 'cancelled'
            transaction.order.status = 'cancelled'
            db.session.commit()
            print("Transacción marcada como cancelada")
        return redirect(url_for('comprobante_pago', status='cancelled'))
    
    if not token_ws:
        print("Error: No se recibió token_ws")
        return redirect(url_for('comprobante_pago', status='error'))
    
    try:
        print("\nConsultando resultado de la transacción...")
        # Confirmar transacción con Webpay
        response = webpay.commit_transaction(token_ws)
        print("Respuesta de commit:", response)
        
        # Buscar la transacción en la base de datos
        transaction = WebpayTransaction.query.filter_by(token_ws=token_ws).first()
        if not transaction:
            print("Error: Transacción no encontrada en la base de datos")
            raise Exception('Transacción no encontrada')
        
        # Verificar si la respuesta es un diccionario
        if isinstance(response, dict):
            response_code = response.get('response_code')
            amount = response.get('amount')
        else:
            # Si es un objeto, intentar acceder a los atributos
            response_code = getattr(response, 'response_code', None)
            amount = getattr(response, 'amount', None)
        
        print(f"Código de respuesta: {response_code}")
        print(f"Monto: {amount}")
        
        # Actualizar la transacción con la respuesta
        if response_code == 0:
            print("Transacción exitosa")
            transaction.status = 'completed'
            transaction.response_code = response_code
            transaction.amount = amount
            transaction.order.status = 'completed'
            status = 'success'
        else:
            print(f"Transacción fallida con código: {response_code}")
            transaction.status = 'failed'
            transaction.response_code = response_code
            transaction.order.status = 'failed'
            status = 'error'
        
        db.session.commit()
        print("Base de datos actualizada")
        
        return redirect(url_for('comprobante_pago', status=status))
        
    except Exception as e:
        print(f"\n=== ERROR EN RETORNO WEBPAY ===")
        print(f"Error: {str(e)}")
        print(f"Tipo de error: {type(e)}")
        import traceback
        print("Traceback completo:")
        print(traceback.format_exc())
        return redirect(url_for('comprobante_pago', status='error'))

@app.route('/comprobante-pago')
def comprobante_pago():
    status = request.args.get('status', 'error')
    return render_template('comprobante_pago.html', status=status, user=session.get('user'))

# SIEMPRE DEBE ESTAR AL FINAL O EL PROGRAMA NO FUNCIONA
if __name__ == '__main__':
    # Crear las tablas si no existen
    with app.app_context():
        db.create_all()
    app.run(debug=True)