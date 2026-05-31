import { api } from '../api.js';

const UNSPLASH_FALLBACKS = {
  fotolibros: 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&q=80&w=800',
  cuadros:    'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&q=80&w=800',
  impresiones:'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&q=80&w=800',
  regalos:    'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?auto=format&fit=crop&q=80&w=800',
  default:    'https://images.unsplash.com/photo-1554048612-b6a482bc67e5?auto=format&fit=crop&q=80&w=800',
};

function getImage(product) {
  if (product.image && !product.image.includes('placeholder')) return product.image;
  return UNSPLASH_FALLBACKS[product.category] || UNSPLASH_FALLBACKS.default;
}

function renderProductCard(product) {
  const img = getImage(product);
  const cat = product.category || 'fotografía';
  return `
    <a href="producto.html?id=${product.slug}" class="product-card">
      <div class="product-image-wrapper">
        <img src="${img}" alt="${product.name}" loading="lazy">
      </div>
      <div class="product-info">
        <div>
          <div class="product-category-tag">${cat}</div>
          <h3>${product.name}</h3>
        </div>
        <div class="product-price-wrap">
          <span class="product-price">$${Number(product.price).toLocaleString('es-AR')}</span>
        </div>
      </div>
      <div class="product-cta">Ver producto →</div>
    </a>
  `;
}

document.addEventListener('DOMContentLoaded', async () => {
  const productsGrid = document.getElementById('productsGrid');
  const filterBtns = document.querySelectorAll('.filter-pill');

  if (!productsGrid) return;

  // Scroll del header
  const header = document.getElementById('shopHeader');
  if (header) {
    window.addEventListener('scroll', () => {
      header.classList.toggle('scrolled', window.scrollY > 40);
    });
  }

  async function loadProducts(category = 'all') {
    productsGrid.innerHTML = `<div class="shop-empty">Cargando colección...</div>`;
    const products = await api.getProducts(category !== 'all' ? { category } : {});
    
    if (!products.length) {
      productsGrid.innerHTML = `<div class="shop-empty">No hay productos en esta categoría aún.</div>`;
      return;
    }
    productsGrid.innerHTML = products.map(p => renderProductCard(p)).join('');
  }

  // URL Params
  const urlParams = new URLSearchParams(window.location.search);
  const initialCategory = urlParams.get('category') || 'all';

  filterBtns.forEach(btn => {
    if (btn.dataset.category === initialCategory) btn.classList.add('active');
    btn.addEventListener('click', (e) => {
      filterBtns.forEach(b => b.classList.remove('active'));
      e.currentTarget.classList.add('active');
      const cat = e.currentTarget.dataset.category;
      const newUrl = new URL(window.location);
      cat === 'all' ? newUrl.searchParams.delete('category') : newUrl.searchParams.set('category', cat);
      window.history.pushState({}, '', newUrl);
      loadProducts(cat);
    });
  });

  // Cart count badge
  try {
    const cart = JSON.parse(localStorage.getItem('fotosjacky_cart') || '[]');
    const count = cart.reduce((acc, item) => acc + (item.quantity || 1), 0);
    const badge = document.getElementById('cartCountBadge');
    if (badge && count > 0) {
      badge.textContent = count;
      badge.style.display = 'flex';
    }
  } catch(e) {}

  loadProducts(initialCategory);
});
