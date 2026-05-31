import { cartManager } from '../cart-manager.js';

const FALLBACK_IMG =
  'https://images.unsplash.com/photo-1554048612-b6a482bc67e5?auto=format&fit=crop&q=80&w=400';
const money = (n) => '$' + Number(n || 0).toLocaleString('es-AR');

const ICON_TRASH = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>';
const ICON_BAG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>';
const ICON_LOCK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>';

// Estilos puntuales para animación de salida (la base está en store.css)
const css = document.createElement('style');
css.textContent = `
.cart-item{overflow:hidden;transition:opacity .25s ease}
.cart-item.removing{animation:cartRowOut .32s cubic-bezier(.4,0,.2,1) forwards}
@keyframes cartRowOut{to{opacity:0;height:0;padding-top:0;padding-bottom:0;transform:translateX(20px)}}
.cart-item-price,.summary-total .amount,.summary-row span{font-variant-numeric:tabular-nums}
.cart-item-price.flash{color:var(--violet);transition:color .2s}
.qty-stepper button:active{transform:scale(.88)}
.qty-stepper button{transition:background .15s,color .15s,transform .1s}`;
document.head.appendChild(css);

document.addEventListener('DOMContentLoaded', () => {
  const root = document.getElementById('cartContainer');
  if (!root) return;

  const pendingRemoval = new Set();

  function itemRow(item) {
    return `
      <div class="cart-item" data-id="${item.id}">
        <img class="cart-item-img" src="${item.image || FALLBACK_IMG}" alt="${item.name}" onerror="this.src='${FALLBACK_IMG}'">
        <div class="cart-item-details">
          <div class="cart-item-title">${item.name}</div>
          ${item.variantName ? `<div class="cart-item-variant">${item.variantName}</div>` : ''}
          <div class="cart-item-bottom">
            <div class="qty-stepper">
              <button type="button" data-act="dec" aria-label="Restar">−</button>
              <span class="qty-val">${item.quantity}</span>
              <button type="button" data-act="inc" aria-label="Sumar">+</button>
            </div>
            <div style="text-align:right">
              <div class="cart-item-price">${money(item.price * item.quantity)}</div>
              <button class="cart-remove" data-act="rm">${ICON_TRASH} Quitar</button>
            </div>
          </div>
        </div>
      </div>`;
  }

  // Estructura inicial (una sola vez)
  function buildShell() {
    const items = cartManager.getItems();
    if (!items.length) {
      root.innerHTML = `
        <div class="glass-panel">
          <div class="cart-empty">
            <div class="empty-icon">${ICON_BAG}</div>
            <h2>Tu carrito está vacío</h2>
            <p>Descubrí nuestros productos y empezá a crear tus recuerdos.</p>
            <a href="index.html" class="btn-cta">Ir a la tienda</a>
          </div>
        </div>`;
      return false;
    }
    root.innerHTML = `
      <div class="cart-layout">
        <div class="cart-items-panel" id="cartItemsPanel">${items.map(itemRow).join('')}</div>
        <aside class="cart-summary">
          <div class="summary-title">Resumen</div>
          <div class="summary-row">
            <span id="sumCountLbl"></span>
            <span id="sumSubtotal"></span>
          </div>
          <div class="summary-row">
            <span>Envío</span>
            <span class="muted">Se calcula en el checkout</span>
          </div>
          <div class="summary-total">
            <span>Total</span>
            <span class="amount" id="sumTotal"></span>
          </div>
          <a href="checkout.html" class="btn-cta">Finalizar compra →</a>
          <a href="index.html" class="btn-ghost-cta">Seguir comprando</a>
          <div class="secure-note">${ICON_LOCK} Pago protegido con Mercado Pago</div>
        </aside>
      </div>`;
    bindPanel();
    updateSummary();
    return true;
  }

  function bindPanel() {
    const panel = document.getElementById('cartItemsPanel');
    if (!panel) return;
    panel.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-act]');
      if (!btn) return;
      const row = btn.closest('.cart-item');
      const id = row?.dataset.id;
      if (!id) return;
      const cur = cartManager.getItems().find(x => x.id === id);
      const act = btn.dataset.act;
      if (act === 'inc' && cur) cartManager.updateQuantity(id, cur.quantity + 1);
      else if (act === 'dec' && cur) {
        if (cur.quantity <= 1) removeRow(id);
        else cartManager.updateQuantity(id, cur.quantity - 1);
      }
      else if (act === 'rm') removeRow(id);
    });
  }

  function removeRow(id) {
    const row = document.querySelector(`.cart-item[data-id="${id}"]`);
    if (!row || pendingRemoval.has(id)) { cartManager.removeItem(id); return; }
    pendingRemoval.add(id);
    row.style.height = row.offsetHeight + 'px';
    void row.offsetHeight;
    row.classList.add('removing');
    row.addEventListener('animationend', () => {
      pendingRemoval.delete(id);
      cartManager.removeItem(id);
    }, { once: true });
  }

  function updateSummary() {
    const count = cartManager.getTotalItems();
    const subtotal = cartManager.getTotalPrice();
    const lbl = document.getElementById('sumCountLbl');
    const sub = document.getElementById('sumSubtotal');
    const tot = document.getElementById('sumTotal');
    if (lbl) lbl.textContent = `Subtotal (${count} ${count === 1 ? 'producto' : 'productos'})`;
    if (sub) sub.textContent = money(subtotal);
    if (tot) tot.textContent = money(subtotal);
  }

  // Sincronización incremental al cambiar el carrito
  function sync() {
    const items = cartManager.getItems();
    const panel = document.getElementById('cartItemsPanel');

    // transición vacío ↔ con ítems → reconstruir shell
    if (!panel || items.length === 0) { buildShell(); return; }

    items.forEach(it => {
      const row = panel.querySelector(`.cart-item[data-id="${it.id}"]`);
      if (!row) return; // los nuevos no aplican en esta página
      const qtyEl = row.querySelector('.qty-val');
      const priceEl = row.querySelector('.cart-item-price');
      if (qtyEl.textContent !== String(it.quantity)) qtyEl.textContent = it.quantity;
      const np = money(it.price * it.quantity);
      if (priceEl.firstChild && priceEl.textContent !== np) {
        priceEl.textContent = np;
        priceEl.classList.add('flash');
        setTimeout(() => priceEl.classList.remove('flash'), 220);
      }
    });
    updateSummary();
  }

  buildShell();
  window.addEventListener('cart-updated', sync);
});
