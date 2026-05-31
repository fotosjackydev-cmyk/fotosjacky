import { api } from './api.js';
import { cartManager } from './cart-manager.js';

// Dirección del local (para pedidos con retiro)
const STORE_ADDRESS = {
  street: 'Juan José Paso',
  street_number: '5537',
  floor_apt: null,
  postal_code: '2000',
  city: 'Rosario',
  province: 'Santa Fe',
  country: 'Argentina',
};

export const checkoutService = {
  processOrder: async (formData) => {
    const items = cartManager.getItems();
    if (items.length === 0) {
      throw new Error('El carrito está vacío.');
    }

    const method = formData.get('shippingMethod') || 'retiro_local';
    const isPickup = method === 'retiro_local';

    let shipping_address;
    let notes;

    if (isPickup) {
      shipping_address = { ...STORE_ADDRESS };
      notes = 'RETIRO EN EL LOCAL — Juan José Paso 5537, Rosario';
    } else {
      shipping_address = {
        street: formData.get('street'),
        street_number: formData.get('streetNumber'),
        floor_apt: formData.get('apartment') || null,
        postal_code: formData.get('zipCode'),
        city: formData.get('city'),
        province: formData.get('province'),
        country: 'Argentina',
      };
      notes = 'ENVÍO A DOMICILIO';
    }

    const orderPayload = {
      customer: {
        email: formData.get('email'),
        first_name: formData.get('firstName'),
        last_name: formData.get('lastName'),
        phone: formData.get('phone'),
        dni: formData.get('dni'),
      },
      shipping_address,
      shipping_method: method,
      notes,
      items: items.map(i => ({
        product_id: i.productId,
        variant_id: i.variantId || null,
        quantity: i.quantity,
      })),
    };

    try {
      const result = await api.createCheckoutPreference(orderPayload);
      const payUrl = result && (result.mp_init_point || result.init_point);
      if (payUrl) {
        window.location.href = payUrl;
      } else {
        throw new Error('No se pudo generar el link de pago.');
      }
    } catch (error) {
      console.error('Error en checkout:', error);
      alert('Ocurrió un error al procesar tu pedido. Por favor intentá nuevamente.');
      throw error;
    }
  },
};
