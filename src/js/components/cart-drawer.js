/* =============================================================================
   CART DRAWER — Panel lateral fluido (actualización incremental del DOM)
   No redibuja todo en cada cambio: parchea solo lo que cambió y anima la salida.
   ============================================================================= */
import { cartManager } from '../cart-manager.js';

const FALLBACK_IMG =
  'https://images.unsplash.com/photo-1554048612-b6a482bc67e5?auto=format&fit=crop&q=80&w=400';
const money = (n) => '$' + Number(n || 0).toLocaleString('es-AR');

const STYLE = `
.fjcd-overlay{position:fixed;inset:0;background:rgba(22,18,38,.45);backdrop-filter:blur(3px);
  -webkit-backdrop-filter:blur(3px);z-index:998;opacity:0;visibility:hidden;
  transition:opacity .3s ease,visibility .3s ease}
.fjcd-overlay.open{opacity:1;visibility:visible}
.fjcd{position:fixed;top:0;right:0;height:100dvh;width:420px;max-width:92vw;background:#fff;
  z-index:999;transform:translate3d(100%,0,0);transition:transform .42s cubic-bezier(.22,1,.36,1);
  display:flex;flex-direction:column;box-shadow:-30px 0 60px -30px rgba(22,18,38,.5);
  font-family:'Inter',sans-serif;will-change:transform}
.fjcd.open{transform:translate3d(0,0,0)}
.fjcd-head{display:flex;align-items:center;justify-content:space-between;padding:24px 26px;
  border-bottom:1px solid rgba(22,18,38,.06);flex-shrink:0}
.fjcd-head h3{font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:800;color:#161226;
  margin:0;display:flex;align-items:center;gap:10px}
.fjcd-head .cnt{font-size:.72rem;font-weight:700;background:#6C3EAE;color:#fff;border-radius:100px;
  padding:2px 10px;transition:transform .25s cubic-bezier(.34,1.56,.64,1)}
.fjcd-head .cnt.bump{transform:scale(1.35)}
.fjcd-close{background:none;border:none;cursor:pointer;color:#5C5670;width:36px;height:36px;
  border-radius:50%;display:flex;align-items:center;justify-content:center;transition:.2s}
.fjcd-close:hover{background:#F1ECFB;color:#161226}
.fjcd-close svg{width:20px;height:20px}
.fjcd-body{flex:1;overflow-y:auto;padding:6px 26px;-webkit-overflow-scrolling:touch}
.fjcd-item{display:flex;gap:14px;padding:18px 0;border-bottom:1px solid rgba(22,18,38,.06);
  overflow:hidden;will-change:height,opacity}
.fjcd-item.removing{animation:fjcdOut .32s cubic-bezier(.4,0,.2,1) forwards}
@keyframes fjcdOut{to{opacity:0;height:0;padding-top:0;padding-bottom:0;margin-top:0;transform:translateX(24px)}}
.fjcd-item.adding{animation:fjcdIn .4s cubic-bezier(.22,1,.36,1)}
@keyframes fjcdIn{from{opacity:0;transform:translateX(24px)}to{opacity:1;transform:none}}
.fjcd-item img{width:68px;height:68px;object-fit:cover;border-radius:10px;flex-shrink:0;background:#F1ECFB}
.fjcd-info{flex:1;min-width:0}
.fjcd-name{font-weight:600;font-size:.92rem;color:#161226;margin:0 0 2px}
.fjcd-var{font-size:.76rem;color:#9A93AC;margin:0 0 8px}
.fjcd-row{display:flex;align-items:center;justify-content:space-between}
.fjcd-price{font-weight:700;color:#161226;font-size:.95rem;font-variant-numeric:tabular-nums;
  transition:color .2s}
.fjcd-price.flash{color:#6C3EAE}
.fjcd-step{display:inline-flex;align-items:center;gap:10px}
.fjcd-step button{width:28px;height:28px;border:1px solid rgba(22,18,38,.12);background:#F6F3EE;
  border-radius:8px;cursor:pointer;color:#161226;font-size:1rem;line-height:1;
  display:flex;align-items:center;justify-content:center;transition:background .15s,color .15s,transform .1s}
.fjcd-step button:hover{background:#6C3EAE;color:#fff;border-color:#6C3EAE}
.fjcd-step button:active{transform:scale(.88)}
.fjcd-step .v{font-size:.9rem;font-weight:600;min-width:20px;text-align:center;
  font-variant-numeric:tabular-nums}
.fjcd-rm{background:none;border:none;color:#9A93AC;font-size:.72rem;cursor:pointer;padding:0;
  margin-top:6px;transition:color .2s}
.fjcd-rm:hover{color:#E5484D}
.fjcd-empty{text-align:center;padding:70px 24px;color:#5C5670}
.fjcd-empty svg{width:54px;height:54px;color:#9A93AC;margin-bottom:16px}
.fjcd-empty p{margin:0 0 4px;font-weight:600;color:#161226}
.fjcd-empty span{font-size:.85rem}
.fjcd-foot{border-top:1px solid rgba(22,18,38,.06);padding:22px 26px;flex-shrink:0}
.fjcd-sub{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px}
.fjcd-sub .lbl{color:#5C5670;font-size:.9rem}
.fjcd-sub .val{font-family:'Playfair Display',serif;font-weight:800;font-size:1.5rem;color:#161226;
  font-variant-numeric:tabular-nums}
.fjcd-note{font-size:.76rem;color:#9A93AC;margin:0 0 16px}
.fjcd-btn{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:16px;
  border:none;border-radius:100px;background:linear-gradient(135deg,#6C3EAE,#4361EE);color:#fff;
  font-family:'Inter',sans-serif;font-size:.96rem;font-weight:700;text-decoration:none;cursor:pointer;
  box-shadow:0 12px 30px -10px rgba(108,62,174,.55);transition:transform .25s,box-shadow .25s}
.fjcd-btn:hover{transform:translateY(-2px);box-shadow:0 18px 40px -10px rgba(108,62,174,.65)}
.fjcd-link{display:block;text-align:center;width:100%;padding:13px;margin-top:10px;border-radius:100px;
  border:1px solid rgba(22,18,38,.12);background:transparent;color:#161226;font-family:'Inter',sans-serif;
  font-size:.88rem;font-weight:600;text-decoration:none;cursor:pointer;transition:.25s}
.fjcd-link:hover{border-color:#6C3EAE;color:#6C3EAE}
.fjcd-toast{position:fixed;bottom:28px;left:50%;transform:translate3d(-50%,140%,0);
  background:#161226;color:#fff;padding:14px 24px;border-radius:100px;font-family:'Inter',sans-serif;
  font-size:.9rem;font-weight:600;display:flex;align-items:center;gap:10px;z-index:1000;opacity:0;
  box-shadow:0 16px 40px -12px rgba(22,18,38,.6);
  transition:transform .42s cubic-bezier(.22,1,.36,1),opacity .42s;will-change:transform}
.fjcd-toast.show{transform:translate3d(-50%,0,0);opacity:1}
.fjcd-toast svg{width:18px;height:18px;color:#06D6A0}
@media (prefers-reduced-motion:reduce){.fjcd,.fjcd-toast,.fjcd-item{transition:none!important;animation:none!important}}
`;

const ICON_CART = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>';
const ICON_CLOSE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>';
const ICON_CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>';

let overlay, drawer, toastEl, bodyEl, footEl, countEl;
const pendingRemoval = new Set(); // ids que están animando su salida

function build() {
  const style = document.createElement('style');
  style.textContent = STYLE;
  document.head.appendChild(style);

  overlay = document.createElement('div');
  overlay.className = 'fjcd-overlay';

  drawer = document.createElement('aside');
  drawer.className = 'fjcd';
  drawer.innerHTML = `
    <div class="fjcd-head">
      <h3>${ICON_CART} Tu carrito <span class="cnt" id="fjcdCount">0</span></h3>
      <button class="fjcd-close" aria-label="Cerrar">${ICON_CLOSE}</button>
    </div>
    <div class="fjcd-body" id="fjcdBody"></div>
    <div class="fjcd-foot" id="fjcdFoot"></div>
  `;

  toastEl = document.createElement('div');
  toastEl.className = 'fjcd-toast';
  toastEl.innerHTML = `${ICON_CHECK} <span id="fjcdToastMsg">Agregado al carrito</span>`;

  document.body.append(overlay, drawer, toastEl);
  bodyEl = drawer.querySelector('#fjcdBody');
  footEl = drawer.querySelector('#fjcdFoot');
  countEl = drawer.querySelector('#fjcdCount');

  overlay.addEventListener('click', close);
  drawer.querySelector('.fjcd-close').addEventListener('click', close);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });

  fullRender();
}

/* Crea el nodo de un ítem (una sola vez por ítem) */
function makeItemEl(it) {
  const el = document.createElement('div');
  el.className = 'fjcd-item';
  el.dataset.id = it.id;
  el.innerHTML = `
    <img src="${it.image || FALLBACK_IMG}" alt="${it.name}" onerror="this.src='${FALLBACK_IMG}'">
    <div class="fjcd-info">
      <p class="fjcd-name">${it.name}</p>
      ${it.variantName ? `<p class="fjcd-var">${it.variantName}</p>` : ''}
      <div class="fjcd-row">
        <div class="fjcd-step">
          <button type="button" data-act="dec" aria-label="Restar">−</button>
          <span class="v">${it.quantity}</span>
          <button type="button" data-act="inc" aria-label="Sumar">+</button>
        </div>
        <span class="fjcd-price">${money(it.price * it.quantity)}</span>
      </div>
      <button type="button" class="fjcd-rm">Quitar</button>
    </div>`;

  el.querySelector('[data-act="inc"]').addEventListener('click', () => {
    const cur = cartManager.getItems().find(x => x.id === it.id);
    if (cur) cartManager.updateQuantity(it.id, cur.quantity + 1);
  });
  el.querySelector('[data-act="dec"]').addEventListener('click', () => {
    const cur = cartManager.getItems().find(x => x.id === it.id);
    if (!cur) return;
    if (cur.quantity <= 1) animateRemove(it.id);
    else cartManager.updateQuantity(it.id, cur.quantity - 1);
  });
  el.querySelector('.fjcd-rm').addEventListener('click', () => animateRemove(it.id));
  return el;
}

/* Saca un ítem con animación y luego lo elimina del carrito */
function animateRemove(id) {
  const el = bodyEl.querySelector(`.fjcd-item[data-id="${id}"]`);
  if (!el || pendingRemoval.has(id)) { cartManager.removeItem(id); return; }
  pendingRemoval.add(id);
  el.style.height = el.offsetHeight + 'px';
  // forzar reflow para que la animación de height arranque desde el valor fijo
  void el.offsetHeight;
  el.classList.add('removing');
  el.addEventListener('animationend', () => {
    pendingRemoval.delete(id);
    cartManager.removeItem(id); // dispara cart-updated → sync
  }, { once: true });
}

/* Sincroniza el DOM con el estado del carrito SIN redibujar todo */
function sync() {
  const items = cartManager.getItems();

  // Vacío
  if (!items.length) {
    if (!bodyEl.querySelector('.fjcd-empty')) fullRender();
    else { updateFooter(); updateCount(); }
    return;
  }

  // Si veníamos de vacío, construir desde cero
  if (bodyEl.querySelector('.fjcd-empty')) { fullRender(); return; }

  const seen = new Set();
  items.forEach(it => {
    seen.add(it.id);
    let el = bodyEl.querySelector(`.fjcd-item[data-id="${it.id}"]`);
    if (!el) {
      el = makeItemEl(it);
      el.classList.add('adding');
      bodyEl.appendChild(el);
    } else {
      // Parchear solo lo que cambió
      const qtyEl = el.querySelector('.fjcd-step .v');
      const priceEl = el.querySelector('.fjcd-price');
      if (qtyEl.textContent !== String(it.quantity)) qtyEl.textContent = it.quantity;
      const newPrice = money(it.price * it.quantity);
      if (priceEl.textContent !== newPrice) {
        priceEl.textContent = newPrice;
        priceEl.classList.add('flash');
        setTimeout(() => priceEl.classList.remove('flash'), 220);
      }
    }
  });

  // Quitar nodos que ya no están (y que no estén animando)
  bodyEl.querySelectorAll('.fjcd-item').forEach(el => {
    if (!seen.has(el.dataset.id) && !pendingRemoval.has(el.dataset.id)) el.remove();
  });

  updateFooter();
  updateCount();
}

function updateCount() {
  const n = cartManager.getTotalItems();
  if (countEl.textContent !== String(n)) {
    countEl.textContent = n;
    countEl.classList.add('bump');
    setTimeout(() => countEl.classList.remove('bump'), 260);
  }
}

function updateFooter() {
  const items = cartManager.getItems();
  if (!items.length) {
    footEl.innerHTML = `<a href="index.html" class="fjcd-link">Ir a la tienda</a>`;
    return;
  }
  let sub = footEl.querySelector('.fjcd-sub .val');
  if (!sub) {
    footEl.innerHTML = `
      <div class="fjcd-sub"><span class="lbl">Subtotal</span><span class="val"></span></div>
      <p class="fjcd-note">El envío se calcula en el siguiente paso.</p>
      <a href="checkout.html" class="fjcd-btn">Finalizar compra →</a>
      <a href="carrito.html" class="fjcd-link">Ver carrito completo</a>`;
    sub = footEl.querySelector('.fjcd-sub .val');
  }
  sub.textContent = money(cartManager.getTotalPrice());
}

/* Render completo (solo en estados grandes: vacío ↔ con ítems, o init) */
function fullRender() {
  const items = cartManager.getItems();
  if (!items.length) {
    bodyEl.innerHTML = `
      <div class="fjcd-empty">
        ${ICON_CART}
        <p>Tu carrito está vacío</p>
        <span>Agregá productos para empezar</span>
      </div>`;
    updateFooter();
    updateCount();
    return;
  }
  bodyEl.innerHTML = '';
  items.forEach(it => bodyEl.appendChild(makeItemEl(it)));
  updateFooter();
  updateCount();
}

function open() {
  overlay.classList.add('open');
  drawer.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function close() {
  overlay.classList.remove('open');
  drawer.classList.remove('open');
  document.body.style.overflow = '';
}

let toastTimer;
function toast(msg) {
  document.getElementById('fjcdToastMsg').textContent = msg || 'Agregado al carrito';
  toastEl.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toastEl.classList.remove('show'), 2400);
}

function init() {
  build();
  window.addEventListener('cart-updated', sync);

  document.querySelectorAll('[data-open-cart], .cart-badge, .shop-cart-btn, #cartLink').forEach(el => {
    el.addEventListener('click', (e) => { e.preventDefault(); open(); });
  });

  window.addEventListener('cart:open', open);
  window.addEventListener('cart:added', (e) => {
    sync();
    open();
    toast(e.detail && e.detail.name ? `${e.detail.name} agregado` : 'Agregado al carrito');
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

export { open as openCartDrawer, close as closeCartDrawer };
