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

# Esquema para serialización
class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    image = fields.Str()

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# rutas
# HOME
@app.route('/')
def home():
    user = session.get("user")
    products = Product.query.all()  # retrieve all products
    return render_template('index.html', products=products, user=user)

# PRODUCT DETAIL
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

#LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
         username = request.form.get('username')
         password = request.form.get('password')
         user = User.query.filter_by(username=username).first()
         if user and check_password_hash(user.password, password):
             session['user'] = user.username
             flash('Login successful!', 'success')
             return redirect(url_for('home'))
         else:
             flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

#LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
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

# SIEMPRE DEBE ESTAR AL FINAL O EL PROGRAMA NO FUNCIONA
if __name__ == '__main__':
    app.run(debug=True)