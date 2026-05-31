import { resolve } from 'path';
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        tienda: resolve(__dirname, 'tienda.html'),
        sesiones: resolve(__dirname, 'sesiones.html'),
        producto: resolve(__dirname, 'producto.html'),
        carrito: resolve(__dirname, 'carrito.html'),
        checkout: resolve(__dirname, 'checkout.html'),
        quince: resolve(__dirname, 'quince.html'),
        bodas: resolve(__dirname, 'bodas.html'),
        estudio: resolve(__dirname, 'estudio.html'),
        ordenConfirmada: resolve(__dirname, 'orden-confirmada.html'),
        ordenPendiente: resolve(__dirname, 'orden-pendiente.html'),
        ordenError: resolve(__dirname, 'orden-error.html')
      }
    }
  }
});
