/**
 * Manejador del Carrito en LocalStorage
 */

export class CartManager {
  constructor() {
    this.storageKey = 'fotosjacky_cart';
    this.items = this.loadCart();
  }

  loadCart() {
    const saved = localStorage.getItem(this.storageKey);
    return saved ? JSON.parse(saved) : [];
  }

  saveCart() {
    localStorage.setItem(this.storageKey, JSON.stringify(this.items));
    this.notifySubscribers();
  }

  addItem(product, quantity = 1, variant = null) {
    const existingItemIndex = this.items.findIndex(item => 
      item.productId === product.id && 
      (variant ? item.variantId === variant.id : !item.variantId)
    );

    let price = product.price;
    if (variant && variant.price_modifier) {
      price += variant.price_modifier;
    }

    if (existingItemIndex > -1) {
      this.items[existingItemIndex].quantity += quantity;
    } else {
      this.items.push({
        id: Date.now().toString(),
        productId: product.id,
        name: product.name,
        image: product.image,
        price: price,
        quantity: quantity,
        variantId: variant ? variant.id : null,
        variantName: variant ? variant.name : null
      });
    }

    this.saveCart();
  }

  removeItem(itemId) {
    this.items = this.items.filter(item => item.id !== itemId);
    this.saveCart();
  }

  updateQuantity(itemId, quantity) {
    if (quantity <= 0) {
      this.removeItem(itemId);
      return;
    }
    
    const item = this.items.find(item => item.id === itemId);
    if (item) {
      item.quantity = quantity;
      this.saveCart();
    }
  }

  clearCart() {
    this.items = [];
    this.saveCart();
  }

  getTotalItems() {
    return this.items.reduce((sum, item) => sum + item.quantity, 0);
  }

  getTotalPrice() {
    return this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  }

  getItems() {
    return this.items;
  }

  // Event system
  subscribe(callback) {
    if (!this.subscribers) this.subscribers = [];
    this.subscribers.push(callback);
  }

  notifySubscribers() {
    if (!this.subscribers) return;
    this.subscribers.forEach(callback => callback(this));
    
    // Also dispatch a custom event on window for loose coupling
    window.dispatchEvent(new CustomEvent('cart-updated', { detail: { cart: this } }));
  }
}

// Export a singleton instance
export const cartManager = new CartManager();
