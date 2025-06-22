import json
import os
from decimal import Decimal
from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .extensions import db
from .models import CartItem, Category, Order, Product, User, WebpayTransaction
from .webpay_plus import WebpayPlus

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("index.html")


@main_bp.route("/categoria/<int:category_id>")
def category_products(category_id):
    category = db.session.get(Category, category_id)
    if category is None:
        abort(404)
    products = Product.query.filter_by(category_id=category_id).all()
    return render_template(
        "category_products.html", category=category, products=products
    )


@main_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404)
    return render_template("product_detail.html", product=product)


@main_bp.route("/carrito")
def cart():
    return render_template("cart.html")


@main_bp.route("/api/cart/add", methods=["POST"])
def add_to_cart():
    if "user_id" not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    cart_item = CartItem(
        user_id=session["user_id"], product_id=product_id, quantity=quantity
    )
    db.session.add(cart_item)
    db.session.commit()

    return jsonify({"product_id": product_id, "quantity": quantity}), 201


@main_bp.route("/api/cart/update/<int:item_id>", methods=["PUT"])
def update_cart(item_id):
    if "user_id" not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    cart_item = db.session.get(CartItem, item_id)
    if cart_item is None:
        return jsonify({"error": "Item no encontrado"}), 404
    data = request.get_json()
    cart_item.quantity = data.get("quantity", cart_item.quantity)
    db.session.commit()

    return jsonify({"quantity": cart_item.quantity})


@main_bp.route("/api/cart/remove/<int:item_id>", methods=["DELETE"])
def remove_from_cart(item_id):
    if "user_id" not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    cart_item = db.session.get(CartItem, item_id)
    if cart_item is None:
        return jsonify({"error": "Item no encontrado"}), 404
    db.session.delete(cart_item)
    db.session.commit()

    return "", 204


@main_bp.route("/conversor-moneda")
def currency_converter():
    return render_template("currency_converter.html")


@main_bp.route("/contacto")
def contact():
    return render_template("contact.html")


@main_bp.route("/api/contact", methods=["POST"])
def send_contact_email():
    data = request.get_json()
    # Aquí iría la lógica para enviar el email
    return jsonify({"message": "Mensaje enviado correctamente"})


@main_bp.route("/api/categories")
def get_categories():
    categories = Category.query.all()
    return jsonify([{"id": cat.id, "name": cat.name} for cat in categories])


@main_bp.route("/iniciar-pago", methods=["POST"])
def start_payment():
    if "user_id" not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    # Calcular el total del carrito
    cart_items = CartItem.query.filter_by(user_id=session["user_id"]).all()
    if not cart_items:
        return jsonify({"error": "Carrito vacío"}), 400

    total_amount = Decimal("0")
    for item in cart_items:
        total_amount += Decimal(str(item.product.price)) * item.quantity
    total_amount_int = int(total_amount)

    # Crear orden
    order = Order(
        user_id=session["user_id"], total_amount=total_amount, status="pending"
    )
    db.session.add(order)
    db.session.commit()

    # Crear transacción Webpay
    webpay = WebpayPlus()
    buy_order = webpay.generate_buy_order()
    session_id = str(session["user_id"])
    return_url = url_for("main.checkout", _external=True)

    response = webpay.create_transaction(
        total_amount_int, buy_order, session_id, return_url
    )

    transaction = WebpayTransaction(
        order_id=order.id,
        token_ws=response["token"],
        status="pending",
        buy_order=buy_order,
        amount=total_amount,
        session_id=session_id,
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({"token": response["token"], "url": response["url"]})


@main_bp.route("/checkout")
def checkout():
    if "user_id" not in session:
        flash("Debe iniciar sesión para continuar")
        return redirect(url_for("auth.login"))

    cart_items = CartItem.query.filter_by(user_id=session["user_id"]).all()
    if not cart_items:
        flash("Su carrito está vacío")
        return redirect(url_for("main.cart"))

    return render_template("checkout.html", cart_items=cart_items)
