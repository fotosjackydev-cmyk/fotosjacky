/**
 * Capa de comunicación con el backend (FastAPI)
 * ------------------------------------------------------------------
 * La URL base se puede sobreescribir definiendo window.API_URL antes
 * de cargar este módulo, o con la variable de entorno de Vite
 * VITE_API_URL al hacer build. Por defecto apunta a localhost:8000.
 */

const API_URL =
  (typeof window !== 'undefined' && window.API_URL) ||
  (import.meta && import.meta.env && import.meta.env.VITE_API_URL) ||
  'http://localhost:8000/api';

/** Normaliza un producto del backend al formato que usa el frontend. */
function mapProduct(p) {
  const firstImage =
    p.images && p.images.length > 0
      ? p.images[0].url
      : '/static/img/placeholder.jpg';
  return {
    id: p.id,
    slug: p.slug,
    name: p.name,
    price: p.base_price,
    description: p.description || '',
    image: firstImage,
    images: p.images || [],
    category: p.category || null,
    featured: p.featured,
    variants: p.variants || [],
  };
}

export const api = {
  base: API_URL,

  /** Lista productos. Soporta filtros: { category, search, sort, page }. */
  getProducts: async (filters = {}) => {
    try {
      // El backend filtra por categoría vía /categories/{slug}/products
      if (filters.category && filters.category !== 'all') {
        const res = await fetch(
          `${API_URL}/categories/${encodeURIComponent(filters.category)}/products`
        );
        if (!res.ok) throw new Error('Error fetching category products');
        const data = await res.json();
        return (data.data || []).map(mapProduct);
      }

      const params = {};
      if (filters.search) params.search = filters.search;
      if (filters.sort) params.sort = filters.sort;
      if (filters.page) params.page = filters.page;
      const query = new URLSearchParams(params).toString();

      const res = await fetch(`${API_URL}/products${query ? '?' + query : ''}`);
      if (!res.ok) throw new Error('Error fetching products');
      const data = await res.json();
      return (data.data || []).map(mapProduct);
    } catch (error) {
      console.error('[api.getProducts]', error);
      return [];
    }
  },

  /** Obtiene un producto por su slug (endpoint dedicado del backend). */
  getProductBySlug: async (slug) => {
    try {
      const res = await fetch(`${API_URL}/products/${encodeURIComponent(slug)}`);
      if (!res.ok) return null;
      const product = await res.json();
      return mapProduct(product);
    } catch (error) {
      console.error('[api.getProductBySlug]', error);
      return null;
    }
  },

  /** Alias retrocompatible: acepta slug o id. */
  getProductById: async (idOrSlug) => {
    return api.getProductBySlug(idOrSlug);
  },

  /** Lista las categorías activas. */
  getCategories: async () => {
    try {
      const res = await fetch(`${API_URL}/categories`);
      if (!res.ok) throw new Error('Error fetching categories');
      const data = await res.json();
      return data.data || [];
    } catch (error) {
      console.error('[api.getCategories]', error);
      return [];
    }
  },

  /** Valida el carrito (precios y stock) contra el backend. */
  validateCart: async (items) => {
    const res = await fetch(`${API_URL}/cart/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error validando el carrito');
    }
    return res.json();
  },

  /** Crea la orden y la preferencia de pago de Mercado Pago. */
  createCheckoutPreference: async (payload) => {
    const res = await fetch(`${API_URL}/checkout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al crear el checkout');
    }
    return res.json();
  },
};
