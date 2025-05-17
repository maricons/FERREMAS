from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import Schema, fields, validate
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
from datetime import datetime   


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
class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    # Relación bidireccional con Product
    products = db.relationship('Product', back_populates='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'

class SubCategory(db.Model):
    __tablename__ = 'subcategory'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    # Relación bidireccional con Category (una subcategoría pertenece a una categoría)
    category = db.relationship('Category', back_populates='subcategories') # 'subcategories' será el atributo en Category
    
    # Relación bidireccional con Product
    products = db.relationship('Product', back_populates='subcategory', lazy='dynamic')

    def __repr__(self):
        category_name = self.category.name if self.category else "N/A"
        return f'<SubCategory {self.id}: {self.name} (Category: {category_name})>'

# Completar la relación inversa en Category para subcategories
Category.subcategories = db.relationship('SubCategory', order_by=SubCategory.name, back_populates='category', lazy='dynamic')


class PriceHistory(db.Model):
    __tablename__ = 'price_history'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relación bidireccional con Product
    product = db.relationship('Product', back_populates='price_history')

    def __repr__(self):
        return f'<PriceHistory ProductID: {self.product_id} Value: {self.value} Date: {self.date}>'

# --- MODELO PRODUCT ACTUALIZADO ---
class Product(db.Model):
    __tablename__ = 'product' # Buena práctica definir explícitamente el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(50), unique=True, nullable=True) # Código SKU/visible al usuario
    name = db.Column(db.String(150), nullable=False) # Incrementado el largo por si acaso
    brand = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True) # Para descripciones más largas
    
    # El campo 'price' original se convierte en 'current_price'
    # Este es el precio que se usa para ventas, carrito, etc.
    # Debería actualizarse cuando se añade un nuevo precio al historial.
    current_price = db.Column(db.Float, nullable=False)
    
    image = db.Column(db.String(200), nullable=True)

    # Claves foráneas para las nuevas relaciones
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True) # Un producto puede no tener categoría al inicio
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'), nullable=True) # O subcategoría

    # Relaciones SQLAlchemy usando back_populates para claridad
    category = db.relationship('Category', back_populates='products')
    subcategory = db.relationship('SubCategory', back_populates='products')
    
    price_history = db.relationship('PriceHistory', back_populates='product', lazy='dynamic', order_by="desc(PriceHistory.date)")

    # La relación con CartItem se define en CartItem usando backref, así que no se necesita aquí si usas backref.
    # Si quisieras usar back_populates también para CartItem:
    # cart_items = db.relationship('CartItem', back_populates='product', lazy='dynamic')

    def __repr__(self):
        return f'<Product ID: {self.id} Name: {self.name}>'

# --- MODELOS USER Y CARTITEM (CON PEQUEÑOS AJUSTES SI USAS back_populates EN PRODUCT) ---
class User(db.Model):
    __tablename__ = 'user' # Buena práctica
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # cart_items se define por el backref en CartItem
    def __repr__(self):
        return f'<User {self.username}>'

class CartItem(db.Model):
    __tablename__ = 'cart_item' # Buena práctica
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    
    # Relaciones
    user = db.relationship('User', backref=db.backref('cart_items', lazy='dynamic')) # lazy='dynamic' es bueno aquí
    
    # Si Product usa back_populates para cart_items, esto cambiaría a:
    # product = db.relationship('Product', back_populates='cart_items')
    # Si Product NO define explícitamente cart_items, el backref está bien:
    product = db.relationship('Product', backref=db.backref('cart_items', lazy='dynamic'))
    
    def __repr__(self):
        return f'<CartItem UserID: {self.user_id} ProductID: {self.product_id} Qty: {self.quantity}>'


# --- ESQUEMAS MARSHMALLOW ACTUALIZADOS ---

class BaseCategorySchema(Schema): # Esquema base sin 'subcategories' ni 'products' para anidamiento
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class BaseSubCategorySchema(Schema): # Esquema base sin 'category' ni 'products' para anidamiento
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class SubCategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category_id = fields.Int(required=True, load_only=True) # Para crear/actualizar

    # Al mostrar una Subcategoría, queremos ver su Categoría padre (pero no las subcategorías de esa categoría)
    category = fields.Nested(BaseCategorySchema, dump_only=True) 

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

    # Al mostrar una Categoría, queremos ver sus Subcategorías
    # Cada subcategoría anidada no debería volver a mostrar su categoría padre para evitar bucles infinitos.
    subcategories = fields.Nested(BaseSubCategorySchema, many=True, dump_only=True) # Usar el esquema base

# Definición de subcategories en CategorySchema después de que SubCategorySchema está definido
CategorySchema.subcategories = fields.Nested(SubCategorySchema, many=True, dump_only=True, exclude=('category',))

class PriceHistorySchema(Schema):
    id = fields.Int(dump_only=True)
    value = fields.Float(required=True)
    date = fields.DateTime(dump_only=True, format='%Y-%m-%dT%H:%M:%S')

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    product_code = fields.Str(allow_none=True)
    name = fields.Str(required=True)
    brand = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    current_price = fields.Float(required=True, data_key="price", validate=validate.Range(min=0))
    image = fields.Str(allow_none=True)

    category_id = fields.Int(load_only=True, allow_none=True)
    subcategory_id = fields.Int(load_only=True, allow_none=True)
    
    # Al mostrar un Producto, queremos ver su Categoría y Subcategoría
    category = fields.Nested(BaseCategorySchema, dump_only=True) # Usar BaseCategorySchema
    subcategory = fields.Nested(BaseSubCategorySchema, dump_only=True) # Usar BaseSubCategorySchema
    



class CartItemSchema(Schema):
    id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    product = fields.Nested(ProductSchema) # ProductSchema ya maneja su propia anidación de categoría/subcategoría

# Instancias de esquemas
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
category_schema = CategorySchema() # Esquema completo para listar categorías con sus subcategorías (base)
categories_schema = CategorySchema(many=True)
subcategory_schema = SubCategorySchema() # Esquema completo para listar subcategorías con su categoría (base)
subcategories_schema = SubCategorySchema(many=True)
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
    categories = Category.query.order_by(Category.name).all()
    subcategories = SubCategory.query.order_by(SubCategory.name).all()
    return render_template('index.html', products=products, user=user, categories=categories, subcategories=subcategories)

# NUEVA RUTA API para obtener subcategorías
@app.route('/api/categories/<int:category_id>/subcategories', methods=['GET'])
def get_subcategories_for_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        return jsonify({"error": "Categoría no encontrada"}), 404
    
    subcategories = category.subcategories.order_by(SubCategory.name).all() # Usar .all() si lazy='dynamic'
    return jsonify(subcategories_schema.dump(subcategories))

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
    # Los datos vienen de FormData, no de request.json
    name = request.form.get('name')
    product_code = request.form.get('product_code')
    brand = request.form.get('brand')
    current_price_str = request.form.get('price') # 'price' es el name del input
    description = request.form.get('description')
    category_id_str = request.form.get('category_id')
    subcategory_id_str = request.form.get('subcategory_id')

    if not name or not current_price_str:
        return jsonify({"error": "Nombre y precio son requeridos"}), 400

    try:
        current_price = float(current_price_str)
        if current_price < 0:
            return jsonify({"error": "El precio no puede ser negativo"}), 400
    except ValueError:
        return jsonify({"error": "Precio inválido"}), 400

    category_id = int(category_id_str) if category_id_str else None
    subcategory_id = int(subcategory_id_str) if subcategory_id_str else None

    # Validar que la subcategoría pertenezca a la categoría si ambas están presentes
    if category_id and subcategory_id:
        subcategory_obj = db.session.get(SubCategory, subcategory_id)
        if not subcategory_obj or subcategory_obj.category_id != category_id:
            return jsonify({"error": "La subcategoría no pertenece a la categoría seleccionada"}), 400
    elif subcategory_id and not category_id: # Si se envía subcategoría, la categoría es implícita
        subcategory_obj = db.session.get(SubCategory, subcategory_id)
        if subcategory_obj:
            category_id = subcategory_obj.category_id
        else:
            return jsonify({"error": "Subcategoría inválida"}), 400


    # Manejar la imagen
    image_path = None # Inicializar
    if 'imageFile' in request.files:
        file = request.files['imageFile']
        if file and allowed_file(file.filename): # Asegúrate que allowed_file esté definida
            filename = secure_filename(file.filename)
            # UPLOAD_FOLDER debe estar configurado en app.config
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = f'uploads/{filename}' # Ruta relativa a 'static'
    elif 'imageUrl' in request.form and request.form.get('imageUrl'):
        image_path = request.form.get('imageUrl')
    
    new_product = Product(
        name=name,
        product_code=product_code if product_code else None,
        brand=brand if brand else None,
        description=description if description else None,
        current_price=current_price,
        image=image_path,
        category_id=category_id,
        subcategory_id=subcategory_id
    )
    
    db.session.add(new_product)
    db.session.flush() # Para obtener el ID del producto si lo necesitas para PriceHistory

    # Añadir al historial de precios
    price_entry = PriceHistory(
        product_id=new_product.id,
        value=current_price,
        date=datetime.utcnow() # Asegúrate de importar datetime
    )
    db.session.add(price_entry)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error al guardar producto: {e}")
        return jsonify({"error": "Error interno al guardar el producto"}), 500
        
    return jsonify(product_schema.dump(new_product)), 201

@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = db.session.get(Product, id) # Usar db.session.get
    if not product:
        return jsonify({"error": "Producto no encontrado"}), 404

    # Actualizar campos básicos
    product.name = request.form.get('name', product.name)
    product.product_code = request.form.get('product_code', product.product_code)
    product.brand = request.form.get('brand', product.brand)
    product.description = request.form.get('description', product.description)
    
    new_price_str = request.form.get('price')
    if new_price_str:
        try:
            new_price = float(new_price_str)
            if new_price < 0:
                 return jsonify({"error": "El precio no puede ser negativo"}), 400
            # Si el precio cambió, actualizar current_price y añadir al historial
            if new_price != product.current_price:
                product.current_price = new_price
                price_entry = PriceHistory(
                    product_id=product.id,
                    value=new_price,
                    date=datetime.utcnow()
                )
                db.session.add(price_entry)
        except ValueError:
            return jsonify({"error": "Precio inválido"}), 400

    # Actualizar categoría y subcategoría
    category_id_str = request.form.get('category_id')
    subcategory_id_str = request.form.get('subcategory_id')

    product.category_id = int(category_id_str) if category_id_str else None
    product.subcategory_id = int(subcategory_id_str) if subcategory_id_str else None
    
    # Validar consistencia de categoría/subcategoría
    if product.category_id and product.subcategory_id:
        subcategory_obj = db.session.get(SubCategory, product.subcategory_id)
        if not subcategory_obj or subcategory_obj.category_id != product.category_id:
            return jsonify({"error": "La subcategoría no pertenece a la categoría seleccionada al actualizar"}), 400
    elif product.subcategory_id and not product.category_id:
         subcategory_obj = db.session.get(SubCategory, product.subcategory_id)
         if subcategory_obj:
            product.category_id = subcategory_obj.category_id
         else:
            return jsonify({"error": "Subcategoría inválida al actualizar"}), 400


    # Manejar la imagen (similar a create_product)
    if 'imageFile' in request.files:
        file = request.files['imageFile']
        if file and allowed_file(file.filename):
            # (Opcional: eliminar imagen anterior del servidor si existe y es diferente)
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            product.image = f'uploads/{filename}'
    elif 'imageUrl' in request.form: # Permitir borrar imagen si se envía imageUrl vacío
        product.image = request.form.get('imageUrl') if request.form.get('imageUrl') else None

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error al actualizar producto {id}: {e}")
        return jsonify({"error": "Error interno al actualizar el producto"}), 500
        
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
            total_amount += product.current_price * item.quantity

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