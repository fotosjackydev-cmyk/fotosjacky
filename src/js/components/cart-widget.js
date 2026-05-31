import { cartManager } from '../cart-manager.js';

export function initCartWidget() {
  const cartBadge = document.getElementById('cartCountBadge');
  if (!cartBadge) return;

  function updateBadge() {
    const total = cartManager.getTotalItems();
    cartBadge.textContent = total;
    if (total > 0) {
      cartBadge.style.display = 'flex';
      cartBadge.classList.add('pop');
      setTimeout(() => cartBadge.classList.remove('pop'), 300);
    } else {
      cartBadge.style.display = 'none';
    }
  }

  // Escuchar eventos globales de carrito
  window.addEventListener('cart-updated', updateBadge);
  
  // Update initial state
  updateBadge();
}

document.addEventListener('DOMContentLoaded', initCartWidget);
