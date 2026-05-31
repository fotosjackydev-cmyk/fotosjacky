import { cartManager } from '../cart-manager.js';
import { checkoutService } from '../checkout-service.js';

document.addEventListener('DOMContentLoaded', () => {
  const checkoutItems = document.getElementById('checkoutItems');
  const checkoutTotal = document.getElementById('checkoutTotal');
  const checkoutForm = document.getElementById('checkoutForm');

  if (!checkoutItems || !checkoutTotal || !checkoutForm) return;

  const items = cartManager.getItems();

  if (items.length === 0) {
    alert("Tu carrito está vacío.");
    window.location.href = 'carrito.html';
    return;
  }

  // Render summary
  checkoutItems.innerHTML = items.map(item => `
    <div class="summary-item">
      <div>
        <div style="font-weight: 500;">${item.name} (x${item.quantity})</div>
        ${item.variantName ? `<div style="font-size: 0.85rem; color: #ccc;">${item.variantName}</div>` : ''}
      </div>
      <div>$${(item.price * item.quantity).toLocaleString()}</div>
    </div>
  `).join('');

  checkoutTotal.textContent = '$' + cartManager.getTotalPrice().toLocaleString();

  // Handle form submission
  checkoutForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = checkoutForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Procesando...';
    submitBtn.disabled = true;

    try {
      const formData = new FormData(checkoutForm);
      await checkoutService.processOrder(formData);
    } catch (error) {
      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
    }
  });
});
