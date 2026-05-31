import { api } from '../api.js';
import { cartManager } from '../cart-manager.js';

document.addEventListener('DOMContentLoaded', async () => {
  const container = document.getElementById('productDetailContainer');
  if (!container) return;

  const urlParams = new URLSearchParams(window.location.search);
  const productId = urlParams.get('id');

  if (!productId) {
    container.innerHTML = '<h2>Producto no encontrado</h2>';
    return;
  }

  const product = await api.getProductBySlug(productId);

  if (!product) {
    container.innerHTML = '<h2>Producto no encontrado</h2>';
    return;
  }

  // Generar HTML
  let variantsHtml = '';
  if (product.variants && product.variants.length > 0) {
    variantsHtml = `
      <div class="variants-group">
        <label>Variante</label>
        <select id="variantSelect">
          ${product.variants.map(v => 
            `<option value="${v.id}" data-price="${v.price_modifier}">${v.name} ${v.price_modifier > 0 ? '(+$' + v.price_modifier + ')' : ''}</option>`
          ).join('')}
        </select>
      </div>
    `;
  }

  container.innerHTML = `
    <div class="product-gallery">
      <img src="${product.image}" alt="${product.name}">
    </div>
    <div class="product-info">
      <h1>${product.name}</h1>
      <span class="product-price" id="displayPrice">$${product.price.toLocaleString()}</span>
      <p class="product-desc">${product.description}</p>
      
      ${variantsHtml}

      <div class="quantity-selector">
        <label>Cantidad</label>
        <input type="number" id="qtyInput" value="1" min="1" max="99">
      </div>

      <button id="addToCartBtn" class="btn-cta">Agregar al carrito</button>
    </div>
  `;

  updateBadge();

  // Lógica de interactividad
  const addToCartBtn = document.getElementById('addToCartBtn');
  const variantSelect = document.getElementById('variantSelect');
  const displayPrice = document.getElementById('displayPrice');
  const qtyInput = document.getElementById('qtyInput');

  function updatePriceDisplay() {
    let finalPrice = product.price;
    if (variantSelect) {
      const selectedOption = variantSelect.options[variantSelect.selectedIndex];
      finalPrice += parseInt(selectedOption.dataset.price || 0);
    }
    displayPrice.textContent = '$' + finalPrice.toLocaleString();
  }

  if (variantSelect) {
    variantSelect.addEventListener('change', updatePriceDisplay);
  }

  addToCartBtn.addEventListener('click', () => {
    const qty = parseInt(qtyInput.value) || 1;
    let selectedVariant = null;
    
    if (variantSelect && product.variants) {
      selectedVariant = product.variants.find(v => v.id === variantSelect.value);
    }

    cartManager.addItem(product, qty, selectedVariant);
    updateBadge();

    // Abre el cart drawer con aviso
    window.dispatchEvent(new CustomEvent('cart:added', { detail: { name: product.name } }));
  });
});

// Actualiza el contador del ícono del header
function updateBadge() {
  try {
    const cart = JSON.parse(localStorage.getItem('fotosjacky_cart') || '[]');
    const count = cart.reduce((acc, i) => acc + (i.quantity || 1), 0);
    const badge = document.getElementById('cartCountBadge');
    if (badge) {
      badge.textContent = count;
      badge.style.display = count > 0 ? 'flex' : 'none';
    }
  } catch (e) {}
}
