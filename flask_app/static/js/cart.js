/**
 * Funciones para el carrito de compras de Ferremas
 */

// Controlador para la cantidad
function setupQuantityControls() {
    const quantityInput = document.getElementById('quantity');
    if (!quantityInput) return;

    const decreaseBtn = document.getElementById('decrease-quantity');
    const increaseBtn = document.getElementById('increase-quantity');

    if (decreaseBtn) {
        decreaseBtn.addEventListener('click', function() {
            let currentValue = parseInt(quantityInput.value);
            if (currentValue > 1) {
                quantityInput.value = currentValue - 1;
            }
        });
    }

    if (increaseBtn) {
        increaseBtn.addEventListener('click', function() {
            let currentValue = parseInt(quantityInput.value);
            if (currentValue < 99) {
                quantityInput.value = currentValue + 1;
            }
        });
    }

    // Validar entrada manual
    quantityInput.addEventListener('change', function() {
        let currentValue = parseInt(quantityInput.value);
        if (isNaN(currentValue) || currentValue < 1) {
            quantityInput.value = 1;
        } else if (currentValue > 99) {
            quantityInput.value = 99;
        }
    });
}

// Añadir al carrito desde botones con clase
function setupAddToCartButtons() {
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', async function() {
            const productId = button.dataset.productId;
            const quantityInput = document.getElementById('quantity');
            const quantity = quantityInput ? parseInt(quantityInput.value) : 1;
            await window.addToCart(productId, quantity);
        });
    });
}

// Función global para añadir al carrito (para uso con onclick)
window.addToCart = async function(productId, quantity = 1) {
    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, quantity: quantity })
        });

        if (!response.ok) {
            let errorData = {};
            try {
                errorData = await response.json();
            } catch (e) {}
            alert(errorData.error || errorData.message || 'Error al añadir al carrito');
            return;
        }

        const data = await response.json();
        alert('Producto añadido al carrito');
        await updateCartCount();
    } catch (error) {
        alert('Error al añadir al carrito');
    }
};

// Cargar el carrito completo
async function loadCart() {
    try {
        const response = await fetch('/api/cart');
        if (!response.ok) {
            updateCartUI([]);
            return;
        }
        const cartItems = await response.json();
        updateCartUI(cartItems);
    } catch (error) {
        updateCartUI([]);
    }
}

// Actualizar la interfaz del carrito
function updateCartUI(cartItems) {
    const cartItemsContainer = document.getElementById('cart-items');
    if (!cartItemsContainer) return;

    const emptyCartMessage = document.getElementById('empty-cart-message');
    const checkoutBtn = document.getElementById('checkout-btn');

    if (cartItems.length === 0) {
        cartItemsContainer.innerHTML = '';
        if (emptyCartMessage) emptyCartMessage.style.display = 'block';
        if (checkoutBtn) checkoutBtn.disabled = true;
        updateCartTotals(0, 0, 0);
        return;
    }

    if (emptyCartMessage) emptyCartMessage.style.display = 'none';
    if (checkoutBtn) checkoutBtn.disabled = false;

    let cartHTML = '';
    let total = 0;

    cartItems.forEach(item => {
        // Si el backend devuelve item.product, usarlo
        const product = item.product || item;
        const itemTotal = product.price * item.quantity;
        total += itemTotal;
        cartHTML += `
            <div class="cart-item">
                <span>${product.name}</span>
                <span>Cantidad: ${item.quantity}</span>
                <span>Precio: $${product.price.toFixed(2)}</span>
                <span>Total: $${itemTotal.toFixed(2)}</span>
                <button onclick="updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                <button onclick="updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                <button onclick="removeItem(${item.id})">Eliminar</button>
            </div>
        `;
    });

    cartItemsContainer.innerHTML = cartHTML;

    // Calcular subtotal e IVA (el precio ya incluye IVA)
    const subtotal = Math.round(total / 1.19);
    const tax = total - subtotal;
    updateCartTotals(subtotal, tax, total);
}

// Actualizar totales del carrito
function updateCartTotals(subtotal, tax, total) {
    const subtotalElement = document.getElementById('cart-subtotal');
    if (!subtotalElement) return;

    subtotalElement.textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('cart-tax').textContent = `$${tax.toFixed(2)}`;
    document.getElementById('cart-total').textContent = `$${total.toFixed(2)}`;
}

// Actualizar cantidad de un producto en el carrito
window.updateQuantity = async function(itemId, newQuantity) {
    if (newQuantity < 1 || newQuantity > 99) return;

    try {
        const response = await fetch(`/api/cart/update/${itemId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quantity: newQuantity })
        });

        if (!response.ok) {
            alert('Error al actualizar la cantidad');
            return;
        }

        await loadCart();
        await updateCartCount();
    } catch (error) {
        alert('Error al actualizar la cantidad');
    }
};

// Eliminar un producto del carrito
window.removeItem = async function(itemId) {
    if (!confirm('¿Estás seguro de eliminar este producto del carrito?')) return;

    try {
        const response = await fetch(`/api/cart/remove/${itemId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            alert('Error al eliminar el producto');
            return;
        }

        await loadCart();
        await updateCartCount();
    } catch (error) {
        alert('Error al eliminar el producto');
    }
};

// Actualizar el contador del carrito
async function updateCartCount() {
    const cartCountElement = document.getElementById('cart-count');
    if (!cartCountElement) return;

    try {
        const response = await fetch('/api/cart');
        if (!response.ok) {
            cartCountElement.textContent = '0';
            return;
        }
        const cartItems = await response.json();
        cartCountElement.textContent = cartItems.length || '0';
    } catch (error) {
        cartCountElement.textContent = '0';
    }
}
// Redirigir a Webpay con POST usando el token recibido
function redirigirAWebpay(url, token) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = url;

    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'token_ws';
    input.value = token;
    form.appendChild(input);

    document.body.appendChild(form);
    form.submit();
}

// Iniciar proceso de pago con Webpay
async function iniciarPago() {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    `;
    loadingOverlay.innerHTML = `
        <div style="background: white; padding: 20px; border-radius: 5px; text-align: center;">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2">Procesando pago...</p>
        </div>
    `;

    document.body.appendChild(loadingOverlay);

    try {
        const response = await fetch('/iniciar-pago', { method: 'POST' });
        if (!response.ok) {
            alert('Error al iniciar el pago');
            document.body.removeChild(loadingOverlay);
            return;
        }
        const data = await response.json();
        redirigirAWebpay(data.url, data.token);
    } catch (error) {
        alert('Error al iniciar el pago');
    } finally {
        if (document.body.contains(loadingOverlay)) {
            document.body.removeChild(loadingOverlay);
        }
    }
}

// Inicializar todas las funcionalidades
document.addEventListener('DOMContentLoaded', async function() {
    setupQuantityControls();
    setupAddToCartButtons();
    if (document.getElementById('cart-items')) {
        await loadCart();
        const checkoutBtn = document.getElementById('checkout-btn');
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', iniciarPago);
        }
    }
    await updateCartCount();
});

