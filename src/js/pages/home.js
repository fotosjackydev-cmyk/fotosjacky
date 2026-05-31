import { api } from '../api.js';

// Currently home page products are mostly static or in the slider.
// If we want to inject "Featured Products", we do it here.

document.addEventListener('DOMContentLoaded', async () => {
  // Ej: si en index.html tuviéramos un contenedor para destacados:
  // const featuredContainer = document.getElementById('homeFeaturedProducts');
  // if (featuredContainer) {
  //    const products = await api.getProducts({ featured: true });
  //    renderProducts(products, featuredContainer);
  // }
});
