/**
 * Funciones para el carrito de compras de Ferremas
 */

// Función helper para formatear moneda
function formatCurrency(amount) {
    return `$${amount.toFixed(2)}`;
}

// Controlador para la cantidad en la página de detalle del producto
function setupQuantityControlsProductDetail() {
    const quantityInput = document.getElementById('quantity');
    if (!quantityInput) return; // Solo en página de detalle
    
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
            if (currentValue < 99) { // Límite máximo de cantidad
                quantityInput.value = currentValue + 1;
            }
        });
    }
    
    quantityInput.addEventListener('input', function() { // 'input' es mejor que 'change' para validación en tiempo real
        let currentValue = parseInt(quantityInput.value);
        if (isNaN(currentValue) || currentValue < 1) {
            quantityInput.value = 1;
        } else if (currentValue > 99) {
            quantityInput.value = 99;
        }
    });
}

// Añadir al carrito desde la página de detalle del producto
async function addToCartFromDetail() {
    const addToCartBtn = document.getElementById('add-to-cart-btn');
    if (!addToCartBtn) return; // Solo en página de detalle

    const addResult = document.getElementById('add-result');
    const isLoggedIn = document.getElementById('user-status').value === 'true';
    const productIdInput = document.getElementById('product-id');
    const quantityInput = document.getElementById('quantity');

    if (!productIdInput || !quantityInput) {
        console.error("Faltan elementos product-id o quantity en la página de detalle.");
        return;
    }
    const productId = parseInt(productIdInput.value);
    
    addToCartBtn.addEventListener('click', async function() {
        if (!isLoggedIn) {
            if (addResult) addResult.innerHTML = '<div class="alert alert-warning">Debes <a href="/login">iniciar sesión</a> para añadir productos al carrito.</div>';
            // Opcionalmente, redirigir a login: window.location.href = '/login';
            return;
        }
        
        const quantity = parseInt(quantityInput.value);
        
        addToCartBtn.disabled = true;
        addToCartBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Añadiendo...';

        try {
            const response = await fetch('/api/cart/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: quantity
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: 'Error desconocido' }));
                throw new Error(errorData.error || 'Error al añadir al carrito');
            }
            
            const result = await response.json();
            
            if (addResult) addResult.innerHTML = `<div class="alert alert-success"><i class="fas fa-check-circle me-2"></i>Producto añadido correctamente. <a href="/carrito" class="alert-link ms-2">Ver carrito (${result.quantity} en total)</a></div>`;
            
            await updateCartCount(); // Actualizar contador global del carrito

        } catch (error) {
            console.error('Error al añadir al carrito:', error);
            if (addResult) addResult.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>Error: ${error.message}</div>`;
        } finally {
            addToCartBtn.disabled = false;
            addToCartBtn.innerHTML = '<i class="fas fa-cart-plus me-2"></i>Añadir al Carrito';
        }
    });
}

// Cargar el carrito completo en la página del carrito
async function loadCartPage() {
    const cartItemsContainer = document.getElementById('cart-items');
    const isLoggedIn = document.getElementById('user-status').value === 'true';

    if (!cartItemsContainer) return; // Solo ejecutar en la página del carrito

    if (!isLoggedIn) {
        // No se muestra el contenedor del carrito si no está logueado, el HTML ya lo maneja.
        // Solo aseguramos que el botón de pago esté deshabilitado.
        const checkoutBtn = document.getElementById('checkout-btn');
        if (checkoutBtn) checkoutBtn.disabled = true;
        updateCartTotals(0,0,0); // Mostrar totales en cero
        return;
    }

    try {
        const response = await fetch('/api/cart');
        
        if (!response.ok) {
            // Podría ser un 401 si la sesión expiró entre la carga de la página y esta llamada.
            // O cualquier otro error del servidor.
            console.error('Error al cargar el carrito:', response.status);
            updateCartUI([]); // Mostrar carrito vacío en caso de error
            return;
        }
        
        const cartItems = await response.json();
        updateCartUI(cartItems);
        
    } catch (error) {
        console.error('Error de red o parseo al cargar el carrito:', error);
        updateCartUI([]); // Mostrar carrito vacío en caso de error
    }
}

// Actualizar la interfaz del carrito (lista de items y totales)
function updateCartUI(cartItems) {
    const cartItemsContainer = document.getElementById('cart-items');
    if (!cartItemsContainer) return;
    
    const emptyCartMessage = document.getElementById('empty-cart-message');
    const checkoutBtn = document.getElementById('checkout-btn');
    const webpayCheckoutForm = document.getElementById('webpay-checkout-form'); // El formulario de Webpay

    if (!cartItems || cartItems.length === 0) {
        cartItemsContainer.innerHTML = ''; // Limpiar items existentes si los hubiera
        if (emptyCartMessage) emptyCartMessage.style.display = 'block';
        if (checkoutBtn) checkoutBtn.disabled = true;
        if (webpayCheckoutForm) webpayCheckoutForm.style.display = 'none'; // Ocultar formulario si no hay items
        updateCartTotals(0, 0, 0);
        return;
    }
    
    if (emptyCartMessage) emptyCartMessage.style.display = 'none';
    if (checkoutBtn) checkoutBtn.disabled = false;
    if (webpayCheckoutForm) webpayCheckoutForm.style.display = 'block'; // Mostrar formulario
    
    let cartHTML = '';
    let subtotal = 0;
    
    cartItems.forEach(item => {
        const itemTotal = item.quantity * item.product.price;
        subtotal += itemTotal;
        
        let imgSrc = item.product.image.startsWith('http') ? item.product.image : `/static/${item.product.image}`;
        
        cartHTML += `
            <div class="cart-item border-bottom py-3" data-id="${item.id}">
                <div class="row align-items-center">
                    <div class="col-md-2 col-3">
                        <img src="${imgSrc}" class="img-fluid rounded" alt="${item.product.name}" style="max-height: 75px; object-fit: contain;">
                    </div>
                    <div class="col-md-4 col-9">
                        <h6 class="mb-1">${item.product.name}</h6>
                        <p class="text-muted small mb-1">Precio: ${formatCurrency(item.product.price)}</p>
                    </div>
                    <div class="col-md-3 col-8 mt-2 mt-md-0">
                        <div class="input-group input-group-sm" style="max-width: 120px;">
                            <button class="btn btn-outline-secondary" type="button" onclick="updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                            <input type="number" class="form-control text-center quantity-input" value="${item.quantity}" min="1" max="99" 
                                   aria-label="Cantidad" onchange="handleQuantityInputChange(this, ${item.id})">
                            <button class="btn btn-outline-secondary" type="button" onclick="updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                        </div>
                    </div>
                    <div class="col-md-2 col-4 mt-2 mt-md-0 text-md-end">
                        <strong>${formatCurrency(itemTotal)}</strong>
                    </div>
                    <div class="col-md-1 col-12 text-md-center mt-2 mt-md-0">
                        <button class="btn btn-sm btn-outline-danger" title="Eliminar item" onclick="removeItem(${item.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    cartItemsContainer.innerHTML = cartHTML;
    
    const taxRate = 0.19; // Asumimos IVA del 19%
    const tax = subtotal * taxRate;
    const total = subtotal + tax;
    updateCartTotals(subtotal, tax, total);
}

// Manejar cambio manual en input de cantidad en el carrito
function handleQuantityInputChange(inputElement, itemId) {
    let newQuantity = parseInt(inputElement.value);
    if (isNaN(newQuantity) || newQuantity < 1) {
        newQuantity = 1;
        inputElement.value = 1; // Corregir visualmente
    } else if (newQuantity > 99) {
        newQuantity = 99;
        inputElement.value = 99; // Corregir visualmente
    }
    updateQuantity(itemId, newQuantity);
}


// Actualizar totales del carrito en la UI
function updateCartTotals(subtotal, tax, total) {
    const subtotalElement = document.getElementById('cart-subtotal');
    const taxElement = document.getElementById('cart-tax');
    const totalElement = document.getElementById('cart-total');

    if (subtotalElement) subtotalElement.textContent = formatCurrency(subtotal);
    if (taxElement) taxElement.textContent = formatCurrency(tax);
    if (totalElement) totalElement.textContent = formatCurrency(total);
}

// Actualizar cantidad de un producto en el carrito (llamada a API)
async function updateQuantity(itemId, newQuantity) {
    if (newQuantity < 1) { // Si la cantidad es 0 o menos, tratar como eliminación
        removeItem(itemId);
        return;
    }
    if (newQuantity > 99) newQuantity = 99; // Límite
    
    // Feedback visual temporal mientras se actualiza (opcional)
    const itemRow = document.querySelector(`.cart-item[data-id="${itemId}"]`);
    if(itemRow) itemRow.style.opacity = '0.5';

    try {
        const response = await fetch(`/api/cart/update/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ quantity: parseInt(newQuantity) }),
        });
        
        if (!response.ok) {
            throw new Error('Error al actualizar la cantidad');
        }
        
        // Solo recargar si estamos en la página del carrito.
        // Si no, solo actualizamos el contador.
        if (document.getElementById('cart-items')) {
            await loadCartPage(); // Recargar toda la UI del carrito para consistencia
        }
        await updateCartCount();

    } catch (error) {
        console.error('Error al actualizar cantidad:', error);
        // Podrías mostrar un mensaje al usuario aquí.
    } finally {
        if(itemRow) itemRow.style.opacity = '1';
    }
}

// Eliminar un producto del carrito
async function removeItem(itemId) {
    // No se necesita confirmación si updateQuantity con 0 llama a removeItem.
    // Si se llama directamente, la confirmación es buena idea:
    // if (!confirm('¿Estás seguro de eliminar este producto del carrito?')) {
    //     return;
    // }
    
    const itemRow = document.querySelector(`.cart-item[data-id="${itemId}"]`);
    if (itemRow) {
        itemRow.style.transition = 'opacity 0.3s ease-out, max-height 0.3s ease-out, margin 0.3s ease-out, padding 0.3s ease-out';
        itemRow.style.opacity = '0';
        itemRow.style.maxHeight = '0px';
        itemRow.style.marginTop = '0px';
        itemRow.style.marginBottom = '0px';
        itemRow.style.paddingTop = '0px';
        itemRow.style.paddingBottom = '0px';
        itemRow.style.overflow = 'hidden';
    }

    try {
        const response = await fetch(`/api/cart/remove/${itemId}`, {
            method: 'DELETE',
        });
        
        if (!response.ok) {
            throw new Error('Error al eliminar el producto');
        }
        
        // Esperar a que termine la animación antes de recargar/actualizar.
        setTimeout(async () => {
            if (itemRow) itemRow.remove(); // Eliminar del DOM
            
            // Actualizar totales y contador después de la eliminación exitosa
            // No es necesario recargar toda la lista si solo se actualizan los totales
            // Pero para asegurar consistencia, especialmente si el carrito queda vacío:
            if (document.getElementById('cart-items')) {
                 // Re-evaluar si el carrito está vacío para mostrar el mensaje correcto
                const currentItems = document.querySelectorAll('#cart-items .cart-item');
                if (currentItems.length === 0) {
                    updateCartUI([]); // Esto mostrará el mensaje de carrito vacío y deshabilitará el pago
                } else {
                    // Si aún hay items, recalcular totales desde el backend para precisión
                    const cartData = await fetch('/api/cart').then(res => res.json());
                    updateCartUI(cartData); // Esto recalculará totales
                }
            }
            await updateCartCount();
        }, 300); // Coincidir con la duración de la animación

    } catch (error) {
        console.error('Error al eliminar item:', error);
        if (itemRow) { // Restaurar visibilidad si la API falla
            itemRow.style.opacity = '1';
            itemRow.style.maxHeight = '200px'; // Un valor aproximado
            // Restaurar otros estilos si es necesario
        }
        // Podrías mostrar un mensaje al usuario.
    }
}

// Actualizar el contador del carrito en el navbar
async function updateCartCount() {
    const cartCountElement = document.getElementById('cart-count');
    if (!cartCountElement) return;
    
    const isLoggedIn = document.getElementById('user-status').value === 'true';
    if (!isLoggedIn) {
        cartCountElement.style.display = 'none';
        return;
    }

    try {
        const response = await fetch('/api/cart');
        if (!response.ok) { // Si hay un error del servidor (ej. 401 si la sesión expiró)
            cartCountElement.style.display = 'none';
            return;
        }
        
        const cartItems = await response.json();
        // Contar la cantidad total de productos, no solo la cantidad de tipos de productos.
        // const count = cartItems.reduce((sum, item) => sum + item.quantity, 0); 
        // O si prefieres contar solo los tipos de productos diferentes:
        const count = cartItems.length; 
        
        if (count > 0) {
            cartCountElement.textContent = count > 99 ? '99+' : count; // Ajustar límite visual
            cartCountElement.style.display = 'inline-flex'; // 'flex' o 'inline-flex' según tu CSS
        } else {
            cartCountElement.style.display = 'none';
        }
    } catch (error) {
        // Error de red, etc.
        console.error('Error al cargar el conteo del carrito:', error);
        cartCountElement.style.display = 'none';
    }
}

// Inicializar funcionalidades cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', async function() {
    // Configurar controles de cantidad en la página de detalle del producto
    setupQuantityControlsProductDetail();
    
    // Configurar botón de añadir al carrito en la página de detalle
    addToCartFromDetail();
    
    // Si estamos en la página del carrito, cargar los items
    if (document.getElementById('cart-items')) {
        await loadCartPage();
        
        // El botón de checkout (`#checkout-btn`) ahora es parte de un formulario.
        // El `cart.html` ya tiene el <form action="{{ url_for('iniciar_pago_webpay') }}" method="POST">
        // No necesitamos un event listener aquí para el pago, el submit del form lo maneja.
        // Solo nos aseguramos que el botón se habilite/deshabilite correctamente en updateCartUI.
    }
    
    // Actualizar el contador del carrito en el navbar (se llama en todas las páginas)
    await updateCartCount();
});