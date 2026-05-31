import { cartManager } from '../cart-manager.js';
import { checkoutService } from '../checkout-service.js';

const money = (n) => '$' + Number(n || 0).toLocaleString('es-AR');

document.addEventListener('DOMContentLoaded', () => {
  const itemsEl = document.getElementById('checkoutItems');
  const subtotalEl = document.getElementById('checkoutSubtotal');
  const shippingEl = document.getElementById('checkoutShipping');
  const totalEl = document.getElementById('checkoutTotal');
  const form = document.getElementById('checkoutForm');
  if (!form) return;

  const items = cartManager.getItems();

  // Carrito vacío → volver
  if (items.length === 0) {
    window.location.href = 'carrito.html';
    return;
  }

  // --- Render resumen ---
  itemsEl.innerHTML = items.map(item => `
    <div class="summary-item">
      <div>
        <div class="summary-item-name">${item.name}</div>
        <div class="summary-item-qty">${item.variantName ? item.variantName + ' · ' : ''}x${item.quantity}</div>
      </div>
      <div class="summary-item-price">${money(item.price * item.quantity)}</div>
    </div>
  `).join('');

  const subtotal = cartManager.getTotalPrice();
  subtotalEl.textContent = money(subtotal);
  totalEl.textContent = money(subtotal);

  // --- Selector de método de entrega ---
  const cards = document.querySelectorAll('.delivery-card');
  const addressSection = document.getElementById('addressSection');
  const pickupInfo = document.getElementById('pickupInfo');
  const addrFields = addressSection.querySelectorAll('[data-addr]');

  function setMethod(method) {
    cards.forEach(c => c.classList.toggle('selected', c.dataset.method === method));

    if (method === 'envio_domicilio') {
      addressSection.classList.remove('hidden');
      pickupInfo.classList.add('hidden');
      addrFields.forEach(f => f.setAttribute('required', 'required'));
      shippingEl.textContent = 'A coordinar';
    } else {
      addressSection.classList.add('hidden');
      pickupInfo.classList.remove('hidden');
      addrFields.forEach(f => f.removeAttribute('required'));
      shippingEl.textContent = 'Gratis';
    }
    // El total no cambia (envío a coordinar/gratis se suma luego si aplica)
    totalEl.textContent = money(subtotal);
  }

  cards.forEach(card => {
    card.addEventListener('click', () => {
      const radio = card.querySelector('input[type="radio"]');
      radio.checked = true;
      setMethod(card.dataset.method);
    });
  });

  // Estado inicial: retiro en local
  setMethod('retiro_local');

  // --- Envío del formulario ---
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('submitBtn');
    const original = btn.textContent;
    btn.textContent = 'Procesando...';
    btn.disabled = true;
    try {
      const formData = new FormData(form);
      await checkoutService.processOrder(formData);
    } catch (err) {
      btn.textContent = original;
      btn.disabled = false;
    }
  });
});
