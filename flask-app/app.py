from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import Schema, fields
import os
from werkzeug.utils import secure_filename
from auth import auth_bp
from dotenv import load_dotenv

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

# SIEMPRE DEBE ESTAR AL FINAL O EL PROGRAMA NO FUNCIONA
if __name__ == '__main__':
    # Crear las tablas si no existen
    with app.app_context():
        db.create_all()
    app.run(debug=True)