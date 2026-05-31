{# ===== ASYNC CSS — Loaded non-blocking ===== #}

/* === Section Base === */
.section { padding: 80px 0; }
.section-white { background: var(--white); }
.section-title { text-align: center; margin-bottom: 16px; }
.section-subtitle { text-align: center; max-width: 560px; margin: 0 auto 3rem; color: var(--piedra); }

/* === Mobile Nav === */
.mobile-nav { position: fixed; top: 0; left: -100%; width: 85%; max-width: 360px; height: 100vh; background: var(--crema); z-index: 2000; padding: 32px; transition: left 0.4s cubic-bezier(0.4, 0, 0.2, 1); overflow-y: auto; }
.mobile-nav.open { left: 0; }
.mobile-nav-close { position: absolute; top: 20px; right: 20px; background: none; font-size: 1.6rem; color: var(--carbon); }
.mobile-nav .logo { margin-bottom: 40px; }
.mobile-nav-links { display: flex; flex-direction: column; gap: 24px; }
.mobile-nav-links a { font-size: 1rem; font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase; color: var(--carbon); }
.mobile-nav-links a:hover { color: var(--terracota); }
.nav-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(44,44,42,0.4); z-index: 1999; opacity: 0; visibility: hidden; transition: var(--transition); }
.nav-overlay.active { opacity: 1; visibility: visible; }

/* Search Modal */
.search-modal { position: fixed; top: 0; left: 0; width: 100%; z-index: 3000; background: var(--crema); padding: 24px 0; box-shadow: var(--shadow-soft); }
.search-form { display: flex; align-items: center; gap: 16px; }
.search-input { flex: 1; padding: 14px 20px; border: 2px solid transparent; border-radius: var(--radius); background: var(--white); font-size: 1.1rem; font-family: var(--font-body); outline: none; transition: var(--transition); }
.search-input:focus { border-color: var(--terracota); }
.search-close { background: none; font-size: 1.8rem; color: var(--piedra); cursor: pointer; }

/* Ad bar */
.ad-bar { background: var(--terracota); padding: 8px 0; text-align: center; }
.ad-bar-text { color: var(--crema); font-size: 0.82rem; font-weight: 500; letter-spacing: 0.04em; margin: 0; }

/* === Categories Grid === */
.categories-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.category-card { position: relative; border-radius: var(--radius-lg); overflow: hidden; aspect-ratio: 3/4; cursor: pointer; display: block; }
.category-card img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1); }
.category-card:hover img { transform: scale(1.08); }
.category-overlay { position: absolute; inset: 0; background: linear-gradient(180deg, transparent 40%, rgba(44,44,42,0.65) 100%); display: flex; align-items: flex-end; padding: 28px; transition: var(--transition); }
.category-card:hover .category-overlay { background: linear-gradient(180deg, transparent 20%, rgba(44,44,42,0.75) 100%); }
.category-name { font-family: var(--font-body); text-transform: uppercase; letter-spacing: 0.14em; font-size: 0.85rem; font-weight: 600; color: var(--white); }

/* === Value Props === */
.value-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 40px; text-align: center; }
.value-item { padding: 20px; }
.value-icon { width: 48px; height: 48px; margin: 0 auto 20px; color: var(--carbon); }
.value-icon svg { width: 100%; height: 100%; }
.value-item h3 { font-family: var(--font-display); font-size: 1.15rem; margin-bottom: 10px; }
.value-item p { font-size: 0.9rem; }

/* === Featured Product === */
.featured-split { display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: center; }
.featured-image { border-radius: var(--radius-lg); overflow: hidden; }
.featured-image img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.6s ease; }
.featured-image:hover img { transform: scale(1.03); }
.featured-content .text-accent { margin-bottom: 16px; display: block; }
.featured-content h2 { margin-bottom: 16px; }
.featured-content p { margin-bottom: 12px; }
.featured-price { font-family: var(--font-display); font-size: 1.8rem; color: var(--terracota); margin-bottom: 28px; display: block; }

/* === Testimonials === */
.testimonials-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; }
.testimonial-card { background: var(--white); border-radius: var(--radius-lg); padding: 36px 32px; box-shadow: var(--shadow-soft); transition: var(--transition); }
.testimonial-card:hover { box-shadow: var(--shadow-hover); transform: translateY(-4px); }
.testimonial-stars { display: flex; gap: 3px; margin-bottom: 20px; }
.testimonial-stars svg { width: 16px; height: 16px; color: var(--terracota); fill: var(--terracota); }
.testimonial-text { font-family: var(--font-display); font-style: italic; font-size: 1.05rem; color: var(--carbon); line-height: 1.6; margin-bottom: 24px; }
.testimonial-author { font-weight: 600; font-size: 0.9rem; color: var(--carbon); }
.testimonial-role { font-size: 0.8rem; color: var(--piedra); margin-top: 2px; }

/* === Process Steps === */
.process-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px; text-align: center; position: relative; }
.process-grid::before { content: ''; position: absolute; top: 40px; left: 20%; right: 20%; height: 2px; background: linear-gradient(90deg, var(--durazno), var(--terracota), var(--durazno)); opacity: 0.3; }
.process-step { position: relative; z-index: 1; }
.step-number { width: 72px; height: 72px; border-radius: 50%; background: var(--white); border: 2px solid var(--terracota); display: flex; align-items: center; justify-content: center; margin: 0 auto 24px; font-family: var(--font-display); font-size: 1.5rem; color: var(--terracota); transition: var(--transition); }
.process-step:hover .step-number { background: var(--terracota); color: var(--white); }
.process-step h3 { margin-bottom: 10px; }
.process-step p { font-size: 0.9rem; max-width: 260px; margin: 0 auto; }

/* === Newsletter === */
.newsletter { background: var(--carbon); padding: 80px 0; text-align: center; }
.newsletter h2 { color: var(--crema); margin-bottom: 12px; }
.newsletter p { color: var(--piedra); margin-bottom: 32px; }
.newsletter-form { display: flex; gap: 12px; max-width: 480px; margin: 0 auto; }
.newsletter-form input { flex: 1; padding: 14px 20px; border: 1px solid rgba(250,245,239,0.2); border-radius: var(--radius); background: rgba(250,245,239,0.08); color: var(--crema); font-family: var(--font-body); font-size: 0.95rem; outline: none; transition: var(--transition); }
.newsletter-form input::placeholder { color: var(--piedra); }
.newsletter-form input:focus { border-color: var(--terracota); }

/* === Footer === */
.footer { background: var(--carbon); padding: 60px 0 32px; border-top: 1px solid rgba(250,245,239,0.08); }
.footer-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 48px; margin-bottom: 48px; }
.footer-brand p { color: var(--piedra); font-size: 0.9rem; margin-top: 16px; max-width: 280px; line-height: 1.6; }
.footer-brand .logo-fotos, .footer-brand .logo-jacky { color: var(--crema); }
.footer h4 { font-family: var(--font-body); text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.75rem; font-weight: 600; color: var(--crema); margin-bottom: 20px; }
.footer-links { display: flex; flex-direction: column; gap: 12px; }
.footer-links a { color: var(--piedra); font-size: 0.88rem; }
.footer-links a:hover { color: var(--crema); }
.footer-newsletter-text { color: var(--piedra); font-size: 0.88rem; margin-bottom: 16px; }
.footer-newsletter-form { display: flex; flex-direction: column; gap: 10px; }
.footer-newsletter-form input { padding: 10px 14px; border: 1px solid rgba(250,245,239,0.2); border-radius: var(--radius); background: rgba(250,245,239,0.08); color: var(--crema); font-size: 0.88rem; outline: none; }
.footer-newsletter-form input::placeholder { color: var(--piedra); }
.footer-social { display: flex; gap: 16px; margin-top: 24px; }
.footer-social a { width: 36px; height: 36px; border-radius: 50%; border: 1px solid rgba(250,245,239,0.15); display: flex; align-items: center; justify-content: center; color: var(--piedra); transition: var(--transition); }
.footer-social a:hover { border-color: var(--terracota); color: var(--terracota); }
.footer-social svg { width: 16px; height: 16px; }
.footer-bottom { border-top: 1px solid rgba(250,245,239,0.08); padding-top: 28px; display: flex; justify-content: space-between; align-items: center; }
.footer-bottom p { color: var(--piedra); font-size: 0.8rem; }
.footer-payments { display: flex; gap: 12px; }
.payment-icon { width: 40px; height: 26px; background: rgba(250,245,239,0.08); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 0.55rem; color: var(--piedra); font-weight: 700; }

/* === Product Card === */
.products-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin-top: 32px; }
.product-card { border-radius: var(--radius-lg); overflow: hidden; background: var(--white); box-shadow: var(--shadow-soft); transition: var(--transition); }
.product-card:hover { box-shadow: var(--shadow-hover); transform: translateY(-4px); }
.product-card-image { position: relative; aspect-ratio: 1; overflow: hidden; display: block; }
.product-card-image img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s ease; }
.product-card:hover .product-card-image img { transform: scale(1.05); }
.product-badge { position: absolute; top: 12px; left: 12px; background: var(--terracota); color: var(--white); font-size: 0.65rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; letter-spacing: 0.06em; }
.product-card-hover { position: absolute; inset: 0; background: rgba(44,44,42,0.3); display: flex; align-items: center; justify-content: center; opacity: 0; transition: var(--transition); }
.product-card:hover .product-card-hover { opacity: 1; }
.product-card-info { padding: 16px 20px; }
.product-card-name { font-family: var(--font-body); font-size: 0.92rem; font-weight: 500; margin-bottom: 6px; }
.product-card-name a { color: var(--carbon); }
.product-card-price { display: flex; align-items: center; gap: 8px; }
.price-compare { color: var(--piedra); text-decoration: line-through; font-size: 0.85rem; }
.price-current { color: var(--terracota); font-weight: 600; font-size: 1rem; }

/* === Product Page === */
.product-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: start; padding-top: 100px; }
.product-main-image { border-radius: var(--radius-lg); overflow: hidden; margin-bottom: 16px; }
.product-main-image img { width: 100%; }
.product-thumbnails { display: flex; gap: 10px; }
.product-thumb { width: 72px; height: 72px; border-radius: 8px; overflow: hidden; border: 2px solid transparent; cursor: pointer; padding: 0; background: none; transition: var(--transition); }
.product-thumb.active, .product-thumb:hover { border-color: var(--terracota); }
.product-thumb img { width: 100%; height: 100%; object-fit: cover; }
.product-breadcrumb { font-size: 0.8rem; color: var(--piedra); margin-bottom: 16px; display: flex; gap: 8px; flex-wrap: wrap; }
.product-breadcrumb a { color: var(--piedra); }
.product-breadcrumb a:hover { color: var(--terracota); }
.product-title { font-family: var(--font-display); font-size: 2rem; margin-bottom: 16px; }
.product-price-container { margin-bottom: 20px; display: flex; align-items: baseline; gap: 12px; }
.product-compare-price { color: var(--piedra); text-decoration: line-through; font-size: 1.1rem; }
.product-price { font-family: var(--font-display); font-size: 2rem; color: var(--terracota); }
.product-description { color: var(--piedra); line-height: 1.7; margin-bottom: 28px; font-size: 0.95rem; }
.product-variants { margin-bottom: 20px; }
.variant-group { margin-bottom: 16px; }
.variant-label { display: block; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; color: var(--carbon); }
.variant-select { width: 100%; padding: 12px 16px; border: 1px solid #ddd; border-radius: var(--radius); font-family: var(--font-body); font-size: 0.95rem; background: var(--white); color: var(--carbon); outline: none; transition: var(--transition); cursor: pointer; }
.variant-select:focus { border-color: var(--terracota); }
.product-quantity { margin-bottom: 24px; }
.quantity-selector { display: flex; align-items: center; border: 1px solid #ddd; border-radius: var(--radius); width: fit-content; overflow: hidden; }
.qty-btn { width: 44px; height: 44px; background: var(--crema); display: flex; align-items: center; justify-content: center; font-size: 1.2rem; color: var(--carbon); transition: var(--transition); }
.qty-btn:hover { background: var(--durazno); color: var(--white); }
.qty-input { width: 56px; text-align: center; border: none; font-family: var(--font-body); font-size: 1rem; background: var(--white); outline: none; }
.product-benefits { display: flex; flex-direction: column; gap: 12px; margin-top: 28px; padding-top: 28px; border-top: 1px solid #eee; }
.benefit-item { display: flex; align-items: center; gap: 12px; font-size: 0.88rem; color: var(--piedra); }
.benefit-item svg { width: 20px; height: 20px; flex-shrink: 0; }

/* === Category Page === */
.category-header { text-align: center; margin-bottom: 40px; padding-top: 80px; }
.category-title { font-size: clamp(1.8rem, 4vw, 3rem); margin-bottom: 12px; }
.category-description { max-width: 600px; margin: 0 auto; }
.category-layout { display: grid; grid-template-columns: 240px 1fr; gap: 40px; }
.category-filters { position: sticky; top: 100px; }
.filter-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.filter-header h3 { font-size: 1.1rem; }
.filter-clear { background: none; color: var(--terracota); font-size: 0.82rem; cursor: pointer; }
.filter-group { margin-bottom: 24px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
.filter-title { font-family: var(--font-body); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; display: flex; justify-content: space-between; align-items: center; cursor: pointer; margin-bottom: 12px; }
.filter-option { display: flex; align-items: center; gap: 8px; font-size: 0.88rem; color: var(--piedra); cursor: pointer; padding: 4px 0; }
.filter-option input { accent-color: var(--terracota); }
.filter-count { font-size: 0.75rem; color: var(--piedra); }
.category-controls { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.category-count { font-size: 0.88rem; color: var(--piedra); }
.category-sort { display: flex; align-items: center; gap: 10px; }
.sort-select { padding: 8px 12px; border: 1px solid #ddd; border-radius: var(--radius); font-size: 0.85rem; background: var(--white); outline: none; }
.category-empty { text-align: center; padding: 80px 0; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 48px; }
.pagination-info { font-size: 0.88rem; color: var(--piedra); }

/* === Cart Page === */
.cart-layout { display: grid; grid-template-columns: 1fr 380px; gap: 40px; align-items: start; }
.cart-item { display: grid; grid-template-columns: 100px 1fr auto; gap: 20px; padding: 24px 0; border-bottom: 1px solid #eee; align-items: center; }
.cart-item-image { border-radius: var(--radius); overflow: hidden; }
.cart-item-image img { width: 100%; aspect-ratio: 1; object-fit: cover; }
.cart-item-details h3 { font-family: var(--font-body); font-size: 1rem; font-weight: 500; margin-bottom: 4px; }
.cart-item-details h3 a { color: var(--carbon); }
.cart-item-variant { font-size: 0.82rem; color: var(--piedra); margin-bottom: 12px; }
.cart-item-price { text-align: right; }
.cart-item-total { font-weight: 600; font-size: 1.05rem; color: var(--carbon); display: block; margin-bottom: 8px; }
.cart-item-remove { background: none; color: var(--piedra); cursor: pointer; transition: var(--transition); }
.cart-item-remove:hover { color: var(--terracota); }
.cart-summary-card { background: var(--white); border-radius: var(--radius-lg); padding: 32px; box-shadow: var(--shadow-soft); position: sticky; top: 100px; }
.cart-summary-card h3 { font-family: var(--font-body); font-size: 1.1rem; font-weight: 600; margin-bottom: 24px; }
.cart-summary-row { display: flex; justify-content: space-between; padding: 12px 0; font-size: 0.95rem; color: var(--piedra); }
.cart-summary-row.total { border-top: 2px solid var(--carbon); padding-top: 16px; margin-top: 8px; margin-bottom: 24px; font-weight: 700; font-size: 1.15rem; color: var(--carbon); }
.cart-empty { text-align: center; padding: 80px 0 120px; }
.cart-empty h2 { margin-bottom: 12px; }

/* === Scroll Reveal === */
.reveal { opacity: 0; transform: translateY(32px); transition: opacity 0.7s cubic-bezier(0.4, 0, 0.2, 1), transform 0.7s cubic-bezier(0.4, 0, 0.2, 1); }
.reveal.visible { opacity: 1; transform: translateY(0); }
.reveal-delay-1 { transition-delay: 0.1s; }
.reveal-delay-2 { transition-delay: 0.2s; }
.reveal-delay-3 { transition-delay: 0.3s; }
.reveal-delay-4 { transition-delay: 0.4s; }

/* === Responsive === */
@media (max-width: 1024px) {
  .categories-grid { grid-template-columns: repeat(2, 1fr); }
  .value-grid { grid-template-columns: repeat(2, 1fr); gap: 24px; }
  .featured-split { grid-template-columns: 1fr; gap: 40px; }
  .testimonials-grid { grid-template-columns: repeat(2, 1fr); }
  .footer-grid { grid-template-columns: repeat(2, 1fr); gap: 32px; }
  .products-grid { grid-template-columns: repeat(3, 1fr); }
  .product-layout { grid-template-columns: 1fr; gap: 40px; }
  .category-layout { grid-template-columns: 1fr; }
  .cart-layout { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .section { padding: 56px 0; }
  .categories-grid { gap: 12px; }
  .category-card { aspect-ratio: 2/3; }
  .value-grid { grid-template-columns: 1fr 1fr; gap: 20px; }
  .testimonials-grid { grid-template-columns: 1fr; }
  .process-grid { grid-template-columns: 1fr; gap: 32px; }
  .process-grid::before { display: none; }
  .newsletter-form { flex-direction: column; }
  .footer-grid { grid-template-columns: 1fr; gap: 32px; }
  .footer-bottom { flex-direction: column; gap: 16px; text-align: center; }
  .products-grid { grid-template-columns: repeat(2, 1fr); gap: 16px; }
  .cart-item { grid-template-columns: 80px 1fr; }
  .cart-item-price { grid-column: 1 / -1; display: flex; justify-content: space-between; align-items: center; }
}

@media (max-width: 480px) {
  .categories-grid { grid-template-columns: 1fr 1fr; gap: 10px; }
  .hero-buttons { flex-direction: column; }
  .hero-buttons .btn { width: 100%; }
}
