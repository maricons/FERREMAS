from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Product, Category, CartItem, Order, WebpayTransaction
from .extensions import db
from .currency_converter import CurrencyConverter
from flask_mail import Message
from .webpay_plus import WebpayPlus
from decimal import Decimal
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('index.html')

@main_bp.route('/categoria/<int:category_id>')
def category_products(category_id):
    category = Category.query.get_or_404(category_id)
    return render_template('category_products.html', category=category)

@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@main_bp.route('/carrito')
def cart():
    return render_template('cart.html')

@main_bp.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuario no autenticado'}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    cart_item = CartItem(
        user_id=session['user_id'],
        product_id=product_id,
        quantity=quantity
    )
    db.session.add(cart_item)
    db.session.commit()
    
    return jsonify({
        'product_id': product_id,
        'quantity': quantity
    }), 201

@main_bp.route('/api/cart/update/<int:item_id>', methods=['PUT'])
def update_cart(item_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuario no autenticado'}), 401
    
    cart_item = CartItem.query.get_or_404(item_id)
    data = request.get_json()
    cart_item.quantity = data.get('quantity', cart_item.quantity)
    db.session.commit()
    
    return jsonify({
        'quantity': cart_item.quantity
    })

@main_bp.route('/api/cart/remove/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuario no autenticado'}), 401
    
    cart_item = CartItem.query.get_or_404(item_id)
    db.session.delete(cart_item)
    db.session.commit()
    
    return '', 204

@main_bp.route('/conversor-moneda')
def currency_converter():
    return render_template('currency_converter.html')

@main_bp.route('/contacto')
def contact():
    return render_template('contact.html')

@main_bp.route('/api/contact', methods=['POST'])
def send_contact_email():
    data = request.get_json()
    # Aquí iría la lógica para enviar el email
    return jsonify({'message': 'Mensaje enviado correctamente'})

@main_bp.route('/api/categories')
def get_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': cat.id,
        'name': cat.name
    } for cat in categories])

@main_bp.route('/iniciar-pago', methods=['POST'])
def start_payment():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuario no autenticado'}), 401
    
    # Crear orden
    order = Order(
        user_id=session['user_id'],
        total_amount=Decimal('0'),
        status='pending'
    )
    db.session.add(order)
    db.session.commit()
    
    # Crear transacción Webpay
    webpay = WebpayPlus()
    response = webpay.create_transaction(order.id, order.total_amount)
    
    transaction = WebpayTransaction(
        order_id=order.id,
        token=response.token,
        status='pending'
    )
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'token': response.token,
        'url': response.url
    })

@main_bp.route('/checkout')
def checkout():
    if 'user_id' not in session:
        flash('Debe iniciar sesión para continuar')
        return redirect(url_for('auth.login'))
    
    cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
    if not cart_items:
        flash('Su carrito está vacío')
        return redirect(url_for('main.cart'))
    
    return render_template('checkout.html', cart_items=cart_items) 