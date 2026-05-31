# =============================================================================
# Servicio — Emails Transaccionales
# Envío de emails de confirmación de compra, envío, etc.
# Usa Resend.com (free tier: 3.000 emails/mes)
# =============================================================================
import resend
from app.config import settings


def _init_resend():
    """Inicializa Resend con la API key."""
    resend.api_key = settings.RESEND_API_KEY


def send_order_confirmation(
    to_email: str,
    customer_name: str,
    order_number: int,
    items: list[dict],
    subtotal: float,
    shipping_cost: float,
    total: float,
) -> bool:
    """
    Envía email de confirmación de compra al cliente.
    Se dispara cuando el pago se confirma vía webhook.
    """
    if not settings.RESEND_API_KEY:
        print("⚠️  RESEND_API_KEY no configurada, email no enviado")
        return False

    _init_resend()

    # Construir tabla de items en HTML
    items_html = ""
    for item in items:
        variant = f" ({item.get('variant_name', '')})" if item.get('variant_name') else ""
        items_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{item['product_name']}{variant}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center;">{item['quantity']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">${item['unit_price']:,.2f}</td>
        </tr>
        """

    html = f"""
    <div style="max-width: 600px; margin: 0 auto; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        <div style="background: linear-gradient(135deg, #c4956a, #d4a574); padding: 30px; text-align: center; border-radius: 12px 12px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">📸 Fotos Jacky</h1>
            <p style="color: rgba(255,255,255,0.9); margin-top: 8px;">¡Gracias por tu compra!</p>
        </div>

        <div style="padding: 30px; background: #fff; border: 1px solid #eee;">
            <p style="font-size: 16px; color: #333;">Hola <strong>{customer_name}</strong>,</p>
            <p style="color: #666;">Tu orden <strong>#{order_number:04d}</strong> fue confirmada exitosamente.</p>

            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="background: #f8f8f8;">
                        <th style="padding: 10px; text-align: left;">Producto</th>
                        <th style="padding: 10px; text-align: center;">Cant.</th>
                        <th style="padding: 10px; text-align: right;">Precio</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>

            <div style="text-align: right; margin-top: 15px; padding-top: 15px; border-top: 2px solid #c4956a;">
                <p style="color: #666; margin: 5px 0;">Subtotal: <strong>${subtotal:,.2f}</strong></p>
                <p style="color: #666; margin: 5px 0;">Envío: <strong>${shipping_cost:,.2f}</strong></p>
                <p style="font-size: 18px; color: #333; margin: 10px 0;">Total: <strong>${total:,.2f}</strong></p>
            </div>

            <div style="background: #f0f9f0; border-left: 4px solid #4caf50; padding: 15px; margin-top: 20px; border-radius: 4px;">
                <p style="margin: 0; color: #2e7d32;">✅ Pago confirmado. Estamos preparando tu pedido.</p>
            </div>
        </div>

        <div style="padding: 20px; text-align: center; color: #999; font-size: 12px; background: #f8f8f8; border-radius: 0 0 12px 12px;">
            <p>Fotos Jacky — Tus recuerdos, nuestro arte</p>
        </div>
    </div>
    """

    try:
        resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [to_email],
            "subject": f"✅ Orden #{order_number:04d} confirmada — Fotos Jacky",
            "html": html,
        })
        print(f"📧 Email de confirmación enviado a {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error al enviar email: {e}")
        return False


def send_order_shipped(
    to_email: str,
    customer_name: str,
    order_number: int,
    tracking_number: str,
    shipping_method: str,
) -> bool:
    """
    Envía email notificando que el pedido fue enviado.
    Se dispara cuando el admin actualiza el estado a 'shipped'.
    """
    if not settings.RESEND_API_KEY:
        print("⚠️  RESEND_API_KEY no configurada, email no enviado")
        return False

    _init_resend()

    # URL de tracking según carrier
    tracking_urls = {
        "andreani": f"https://www.andreani.com/#!/informacionEnvio/{tracking_number}",
        "oca": f"https://www5.oca.com.ar/ocaepakNet/Views/ConsultaTracking/TrackingConsult.aspx?numberTracking={tracking_number}",
        "correo_argentino": f"https://www.correoargentino.com.ar/formularios/e-commerce?id={tracking_number}",
    }
    tracking_url = tracking_urls.get(shipping_method, "#")

    html = f"""
    <div style="max-width: 600px; margin: 0 auto; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        <div style="background: linear-gradient(135deg, #c4956a, #d4a574); padding: 30px; text-align: center; border-radius: 12px 12px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">📸 Fotos Jacky</h1>
            <p style="color: rgba(255,255,255,0.9); margin-top: 8px;">¡Tu pedido está en camino!</p>
        </div>

        <div style="padding: 30px; background: #fff; border: 1px solid #eee;">
            <p style="font-size: 16px; color: #333;">Hola <strong>{customer_name}</strong>,</p>
            <p style="color: #666;">Tu orden <strong>#{order_number:04d}</strong> ya fue despachada. 🚚</p>

            <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 20px 0; border-radius: 4px;">
                <p style="margin: 0 0 5px 0; color: #1565c0; font-weight: bold;">Número de seguimiento:</p>
                <p style="margin: 0; font-size: 18px; color: #333; font-family: monospace;">{tracking_number}</p>
            </div>

            <div style="text-align: center; margin: 25px 0;">
                <a href="{tracking_url}"
                   style="display: inline-block; background: #c4956a; color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: bold;">
                    📍 Seguir mi pedido
                </a>
            </div>
        </div>

        <div style="padding: 20px; text-align: center; color: #999; font-size: 12px; background: #f8f8f8; border-radius: 0 0 12px 12px;">
            <p>Fotos Jacky — Tus recuerdos, nuestro arte</p>
        </div>
    </div>
    """

    try:
        resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [to_email],
            "subject": f"🚚 Tu pedido #{order_number:04d} fue enviado — Fotos Jacky",
            "html": html,
        })
        print(f"📧 Email de envío enviado a {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error al enviar email: {e}")
        return False


def send_new_order_notification(
    order_number: int,
    customer_name: str,
    total: float,
    items_count: int,
) -> bool:
    """
    Envía email a Jacky notificando una nueva venta.
    Se dispara cuando se confirma un pago.
    """
    if not settings.RESEND_API_KEY or not settings.ADMIN_EMAIL:
        return False

    _init_resend()

    html = f"""
    <div style="max-width: 600px; margin: 0 auto; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        <div style="background: #4caf50; padding: 20px; text-align: center; border-radius: 12px 12px 0 0;">
            <h1 style="color: white; margin: 0;">🎉 ¡Nueva venta!</h1>
        </div>
        <div style="padding: 25px; background: #fff; border: 1px solid #eee;">
            <p style="font-size: 18px; color: #333;">Orden <strong>#{order_number:04d}</strong></p>
            <p>👤 Cliente: <strong>{customer_name}</strong></p>
            <p>📦 Items: <strong>{items_count}</strong></p>
            <p style="font-size: 24px; color: #4caf50; font-weight: bold;">💰 Total: ${total:,.2f}</p>
            <p style="color: #999; margin-top: 20px;">Revisá la orden en el panel de administración.</p>
        </div>
    </div>
    """

    try:
        resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [settings.ADMIN_EMAIL],
            "subject": f"🎉 Nueva venta #{order_number:04d} — ${total:,.2f}",
            "html": html,
        })
        return True
    except Exception:
        return False
