import { cartManager } from '../cart-manager.js';

document.addEventListener('DOMContentLoaded', () => {
  const cartContainer = document.getElementById('cartContainer');
  if (!cartContainer) return;

  function renderCart() {
    const items = cartManager.getItems();
    
    if (items.length === 0) {
      cartContainer.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 40px; background: var(--surface); border-radius: 8px;">
          <h2>Tu carrito está vacío</h2>
          <p style="margin: 16px 0 24px;">¡Agrega algunos productos para continuar!</p>
          <a href="index.html" class="btn btn-primary">Ir a la tienda</a>
        </div>
      `;
      return;
    }

    const itemsHtml = items.map(item => `
      <div class="cart-item">
        <img src="${item.image}" alt="${item.name}">
        <div class="cart-item-details">
          <div class="cart-item-title">${item.name}</div>
          ${item.variantName ? `<div class="cart-item-variant">Variante: ${item.variantName}</div>` : ''}
          <div class="cart-item-price">$${item.price.toLocaleString()}</div>
          
          <div class="cart-item-actions">
            <div>
              <label style="font-size: 0.9rem; margin-right: 8px;">Cant:</label>
              <input type="number" value="${item.quantity}" min="0" class="qty-update" data-id="${item.id}" style="width:60px; padding:4px 8px; border:1px solid var(--border); border-radius:4px;">
            </div>
            <button class="remove-btn" data-id="${item.id}" style="background:none; border:none; color:var(--error, #e53935); cursor:pointer; text-decoration:underline;">Eliminar</button>
          </div>
        </div>
      </div>
    `).join('');

    const subtotal = cartManager.getTotalPrice();

    cartContainer.innerHTML = `
      <div class="cart-items">
        ${itemsHtml}
      </div>
      <div class="cart-summary">
        <h2 style="margin-bottom: 24px; font-size: 1.25rem;">Resumen de Compra</h2>
        <div class="summary-row">
          <span>Subtotal (${cartManager.getTotalItems()} productos)</span>
          <span>$${subtotal.toLocaleString()}</span>
        </div>
        <div class="summary-row">
          <span>Envío</span>
          <span style="color:var(--carbon); font-size:0.9rem;">Se calcula en el checkout</span>
        </div>
        <div class="summary-total">
          <span>Total estimado</span>
          <span>$${subtotal.toLocaleString()}</span>
        </div>
        <a href="checkout.html" class="btn btn-primary btn-checkout">Iniciar Pago</a>
      </div>
    `;

    // Attach events
    document.querySelectorAll('.qty-update').forEach(input => {
      input.addEventListener('change', (e) => {
        cartManager.updateQuantity(e.target.dataset.id, parseInt(e.target.value));
      });
    });

    document.querySelectorAll('.remove-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        cartManager.removeItem(e.target.dataset.id);
      });
    });
  }

  // Initial render
  renderCart();

  // Re-render when cart updates
  window.addEventListener('cart-updated', renderCart);
});
