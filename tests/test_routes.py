import sys
from pathlib import Path

import json
from decimal import Decimal

# Add parent directory to Python path to find the flask-app package
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)


from flask import session, url_for

from flask_app import CartItem, Category, Order, Product, User, WebpayTransaction, db


def test_home_page(client):
    """Test home page loads successfully"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Ferremas".encode("utf-8") in response.data


def test_product_listing(client, test_product):
    """Test product listing page"""
    response = client.get(f"/categoria/{test_product.category_id}")
    assert response.status_code == 200
    assert test_product.name.encode("utf-8") in response.data
    assert str(test_product.price).encode("utf-8") in response.data


def test_product_detail(client, test_product):
    """Test product detail page"""
    response = client.get(f"/product/{test_product.id}")
    assert response.status_code == 200
    assert test_product.name.encode("utf-8") in response.data
    assert test_product.description.encode("utf-8") in response.data


def test_category_products(client, test_category, test_product):
    """Test category products page"""
    response = client.get(f"/categoria/{test_category.id}")
    assert response.status_code == 200
    assert test_category.name.encode("utf-8") in response.data


def test_login_page(client):
    """Test login page loads"""
    response = client.get("/login")
    assert response.status_code == 200
    assert "iniciar sesion".encode("utf-8") in response.data.lower()


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(
        "/login",
        data={"email": test_user.email, "password": "password123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "exitoso".encode("utf-8") in response.data.lower()


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/login",
        data={"email": "wrong@email.com", "password": "wrongpass"},
        follow_redirects=True,
    )
    assert "Credenciales inválidas".encode("utf-8") in response.data


def test_register_page(client):
    """Test register page loads"""
    response = client.get("/register")
    assert response.status_code == 200
    assert "registro".encode("utf-8") in response.data.lower()


def test_register_success(client, app):
    """Test successful registration"""
    response = client.post(
        "/register",
        data={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "password123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "exitoso".encode("utf-8") in response.data.lower()

    # Verify user was created in database
    with app.app_context():
        user = User.query.filter_by(email="newuser@test.com").first()
        assert user is not None
        assert user.username == "newuser"


def test_register_duplicate_email(client, test_user):
    """Test registration with existing email"""
    response = client.post(
        "/register",
        data={
            "username": "newuser",
            "email": test_user.email,
            "password": "password123",
        },
        follow_redirects=True,
    )
    assert "email ya existe".encode("utf-8") in response.data.lower()


def test_logout(client, test_user):
    """Test logout functionality"""
    with client:  # Esto mantiene el contexto de la sesión
        # First login
        client.post(
            "/login", data={"email": test_user.email, "password": "password123"}
        )

        # Then logout
        response = client.get("/logout", follow_redirects=True)
        assert response.status_code == 200
        assert "has cerrado sesión".encode("utf-8") in response.data.lower()
        assert "user" not in session


def test_cart_page(client):
    """Test cart page loads"""
    response = client.get("/carrito")
    assert response.status_code == 200
    assert "carrito".encode("utf-8") in response.data.lower()


def test_add_to_cart(client, test_user, test_product):
    """Test adding product to cart"""
    # Login first
    client.post("/login", data={"email": test_user.email, "password": "password123"})

    response = client.post(
        "/api/cart/add",
        json={"product_id": test_product.id, "quantity": 1},
        content_type="application/json",
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["product_id"] == test_product.id
    assert data["quantity"] == 1


def test_update_cart(client, test_user, test_product, app):
    """Test updating cart quantity"""
    # Login first
    client.post("/login", data={"email": test_user.email, "password": "password123"})

    # Add item to cart first
    with app.app_context():
        cart_item = CartItem(
            user_id=test_user.id, product_id=test_product.id, quantity=1
        )
        db.session.add(cart_item)
        db.session.commit()

        response = client.put(
            f"/api/cart/update/{cart_item.id}",
            json={"quantity": 2},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["quantity"] == 2


def test_remove_from_cart(client, test_user, test_product, app):
    """Test removing item from cart"""
    # Login first
    client.post("/login", data={"email": test_user.email, "password": "password123"})

    # Add item to cart first
    with app.app_context():
        cart_item = CartItem(
            user_id=test_user.id, product_id=test_product.id, quantity=1
        )
        db.session.add(cart_item)
        db.session.commit()
        item_id = cart_item.id

        response = client.delete(f"/api/cart/remove/{item_id}")
        assert response.status_code == 204

        # Verify item was removed
        assert db.session.get(CartItem, item_id) is None


def test_currency_converter_page(client):
    """Test currency converter page loads"""
    response = client.get("/conversor-moneda")
    assert response.status_code == 200
    assert "conversor".encode("utf-8") in response.data.lower()


def test_contact_page(client):
    """Test contact page loads"""
    response = client.get("/contacto")
    assert response.status_code == 200
    assert "contacto".encode("utf-8") in response.data.lower()


def test_send_contact_email(client):
    """Test sending contact email"""
    response = client.post(
        "/api/contact",
        json={
            "name": "Test User",
            "email": "test@test.com",
            "subject": "Test Subject",
            "message": "Test Message",
        },
        content_type="application/json",
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Mensaje enviado correctamente"


def test_get_categories(client, test_category):
    """Test getting all categories"""
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert any(cat["id"] == test_category.id for cat in data)


def test_webpay_payment_flow(client, test_user, test_product, app):
    """Test Webpay payment flow"""
    # Login first
    client.post("/login", data={"email": test_user.email, "password": "password123"})

    # Add item to cart
    with app.app_context():
        cart_item = CartItem(
            user_id=test_user.id, product_id=test_product.id, quantity=1
        )
        db.session.add(cart_item)
        db.session.commit()

    # Start payment
    response = client.post("/iniciar-pago")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "token" in data
    assert "url" in data

    # Verify order was created
    with app.app_context():
        order = Order.query.filter_by(user_id=test_user.id).first()
        assert order is not None
        assert order.status == "pending"

        # Verify transaction was created
        transaction = WebpayTransaction.query.filter_by(order_id=order.id).first()
        assert transaction is not None
        assert transaction.status == "pending"


def test_checkout_unauthorized(client):
    """Test checkout page requires authentication"""
    response = client.get("/checkout")
    assert response.status_code == 302  # Redirect to login
    assert "/login" in response.headers["Location"]


def test_checkout_empty_cart(client, test_user):
    """Test checkout with empty cart"""
    # Login first
    client.post("/login", data={"email": test_user.email, "password": "password123"})

    response = client.get("/checkout")
    assert response.status_code == 302  # Redirect to cart
    assert "/carrito" in response.headers["Location"]
