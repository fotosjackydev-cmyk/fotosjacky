import { api } from './api.js';
import { cartManager } from './cart-manager.js';

export const checkoutService = {
  processOrder: async (formData) => {
    const items = cartManager.getItems();
    if (items.length === 0) {
      throw new Error("El carrito está vacío.");
    }

    const orderPayload = {
      customer: {
        email: formData.get('email'),
        first_name: formData.get('firstName'),
        last_name: formData.get('lastName'),
        phone: formData.get('phone'),
        dni: formData.get('dni'),
      },
      shipping_address: {
        street: formData.get('street'),
        street_number: formData.get('streetNumber'),
        floor_apt: formData.get('apartment') || null,
        postal_code: formData.get('zipCode'),
        city: formData.get('city'),
        province: formData.get('province'),
        country: "Argentina"
      },
      shipping_method: formData.get('shippingMethod'),
      items: items.map(i => ({
        product_id: i.productId,
        variant_id: i.variantId || null,
        quantity: i.quantity
      }))
    };

    try {
      const result = await api.createCheckoutPreference(orderPayload);
      const payUrl = result && (result.mp_init_point || result.init_point);
      if (payUrl) {
        // Redirigir a MercadoPago
        window.location.href = payUrl;
      } else {
        throw new Error("Error al crear preferencia de pago.");
      }
    } catch (error) {
      console.error("Error en checkout:", error);
      alert("Ocurrió un error al procesar tu pedido. Por favor intenta nuevamente.");
      throw error;
    }
  }
};
