import { cartManager } from '../cart-manager.js';

const FALLBACK_IMG =
  'https://images.unsplash.com/photo-1554048612-b6a482bc67e5?auto=format&fit=crop&q=80&w=400';
const money = (n) => '$' + Number(n || 0).toLocaleString('es-AR');

const ICON_TRASH = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>';
const ICON_BAG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>';
const ICON_LOCK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>';

document.addEventListener('DOMContentLoaded', () => {
  const cartContainer = document.getElementById('cartContainer');
  if (!cartContainer) return;

  function render() {
    const items = cartManager.getItems();

    if (items.length === 0) {
      cartContainer.innerHTML = `
        <div class="glass-panel">
          <div class="cart-empty">
            <div class="empty-icon">${ICON_BAG}</div>
            <h2>Tu carrito está vacío</h2>
            <p>Descubrí nuestros productos y empezá a crear tus recuerdos.</p>
            <a href="index.html" class="btn-cta">Ir a la tienda</a>
          </div>
        </div>`;
      return;
    }

    const itemsHtml = items.map(item => `
      <div class="cart-item">
        <img class="cart-item-img" src="${item.image || FALLBACK_IMG}" alt="${item.name}" onerror="this.src='${FALLBACK_IMG}'">
        <div class="cart-item-details">
          <div class="cart-item-title">${item.name}</div>
          ${item.variantName ? `<div class="cart-item-variant">${item.variantName}</div>` : ''}
          <div class="cart-item-bottom">
            <div class="qty-stepper">
              <button data-dec="${item.id}" aria-label="Restar">−</button>
              <span class="qty-val">${item.quantity}</span>
              <button data-inc="${item.id}" aria-label="Sumar">+</button>
            </div>
            <div style="text-align:right">
              <div class="cart-item-price">${money(item.price * item.quantity)}</div>
              <button class="cart-remove" data-rm="${item.id}">${ICON_TRASH} Quitar</button>
            </div>
          </div>
        </div>
      </div>
    `).join('');

    const subtotal = cartManager.getTotalPrice();
    const count = cartManager.getTotalItems();

    cartContainer.innerHTML = `
      <div class="cart-layout">
        <div class="cart-items-panel">${itemsHtml}</div>
        <aside class="cart-summary">
          <div class="summary-title">Resumen</div>
          <div class="summary-row">
            <span>Subtotal (${count} ${count === 1 ? 'producto' : 'productos'})</span>
            <span>${money(subtotal)}</span>
          </div>
          <div class="summary-row">
            <span>Envío</span>
            <span class="muted">Se calcula en el checkout</span>
          </div>
          <div class="summary-total">
            <span>Total</span>
            <span class="amount">${money(subtotal)}</span>
          </div>
          <a href="checkout.html" class="btn-cta">Finalizar compra →</a>
          <a href="index.html" class="btn-ghost-cta">Seguir comprando</a>
          <div class="secure-note">${ICON_LOCK} Pago protegido con Mercado Pago</div>
        </aside>
      </div>
    `;

    cartContainer.querySelectorAll('[data-inc]').forEach(b => b.addEventListener('click', () => {
      const it = cartManager.getItems().find(x => x.id === b.dataset.inc);
      if (it) cartManager.updateQuantity(it.id, it.quantity + 1);
    }));
    cartContainer.querySelectorAll('[data-dec]').forEach(b => b.addEventListener('click', () => {
      const it = cartManager.getItems().find(x => x.id === b.dataset.dec);
      if (it) cartManager.updateQuantity(it.id, it.quantity - 1);
    }));
    cartContainer.querySelectorAll('[data-rm]').forEach(b => b.addEventListener('click', () => {
      cartManager.removeItem(b.dataset.rm);
    }));
  }

  render();
  window.addEventListener('cart-updated', render);
});
