// =============================================================================
// Fotos Jacky — Admin Panel JavaScript
// =============================================================================

// URL relativa: el panel llama al backend que lo sirve, sin importar
// si entrás por localhost, 127.0.0.1 o tu dominio en producción.
const API = '';
let TOKEN = localStorage.getItem('admin_token') || '';

// --- API Helper ---
async function api(path, opts = {}) {
    const headers = { 'Content-Type': 'application/json' };
    if (TOKEN) headers['Authorization'] = `Bearer ${TOKEN}`;
    const res = await fetch(`${API}${path}`, { ...opts, headers });
    if (res.status === 401) { logout(); throw new Error('Sesión expirada'); }
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error del servidor');
    return data;
}

// --- Toast ---
function toast(msg, type = 'success') {
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.textContent = msg;
    document.getElementById('toast-container').appendChild(el);
    setTimeout(() => el.remove(), 4000);
}

// --- Modal ---
function openModal(title, html) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = html;
    document.getElementById('modal-overlay').style.display = 'flex';
}
function closeModal() { document.getElementById('modal-overlay').style.display = 'none'; }

// --- Auth ---
async function handleLogin(e) {
    e.preventDefault();
    const btn = document.getElementById('login-btn');
    btn.disabled = true; btn.textContent = 'Ingresando...';
    try {
        const data = await api('/api/admin/login', {
            method: 'POST',
            body: JSON.stringify({
                username: document.getElementById('login-user').value,
                password: document.getElementById('login-pass').value,
            }),
        });
        TOKEN = data.access_token;
        localStorage.setItem('admin_token', TOKEN);
        showApp();
    } catch (err) {
        const errEl = document.getElementById('login-error');
        errEl.textContent = err.message; errEl.style.display = 'block';
    }
    btn.disabled = false; btn.textContent = 'Iniciar sesión';
}

function logout() {
    TOKEN = ''; localStorage.removeItem('admin_token');
    document.getElementById('app').style.display = 'none';
    document.getElementById('login-screen').style.display = 'flex';
}

function showApp() {
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('app').style.display = 'flex';
    navigate(location.hash.slice(1) || 'dashboard');
}

// --- Navigation ---
function navigate(section) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const el = document.getElementById(`section-${section}`);
    const nav = document.querySelector(`[data-section="${section}"]`);
    if (el) el.classList.add('active');
    if (nav) nav.classList.add('active');
    if (section === 'dashboard') loadDashboard();
    if (section === 'products') loadProducts();
    if (section === 'categories') loadCategories();
    if (section === 'orders') loadOrders();
}

// --- Status helpers ---
const STATUS_BADGE = {
    pending_payment: '<span class="badge badge-warning">⏳ Pend. pago</span>',
    paid: '<span class="badge badge-success">💳 Pagado</span>',
    preparing: '<span class="badge badge-info">📦 Preparando</span>',
    shipped: '<span class="badge badge-info">🚚 Enviado</span>',
    delivered: '<span class="badge badge-success">✅ Entregado</span>',
    cancelled: '<span class="badge badge-danger">❌ Cancelado</span>',
    refunded: '<span class="badge badge-neutral">↩️ Reembolsado</span>',
};

function fmtPrice(n) { return `$${Number(n).toLocaleString('es-AR', {minimumFractionDigits:0})}`; }
function fmtDate(d) { return new Date(d).toLocaleDateString('es-AR', {day:'2-digit',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'}); }

// --- DASHBOARD ---
async function loadDashboard() {
    try {
        const d = await api('/api/admin/dashboard');
        document.getElementById('metric-products').textContent = d.total_products;
        document.getElementById('metric-categories').textContent = d.total_categories;
        document.getElementById('metric-orders').textContent = d.total_orders;
        document.getElementById('metric-pending').textContent = d.pending_dispatch;

        const orders = await api('/api/admin/orders?page_size=5');
        const cont = document.getElementById('dashboard-recent-orders');
        if (!orders.data.length) { cont.innerHTML = '<p class="text-muted">No hay órdenes aún</p>'; return; }
        cont.innerHTML = `<table><thead><tr><th>#</th><th>Cliente</th><th>Total</th><th>Estado</th><th>Fecha</th></tr></thead><tbody>${
            orders.data.map(o => `<tr><td><strong>#${String(o.order_number).padStart(4,'0')}</strong></td><td>${o.customer_name||'—'}</td><td class="price">${fmtPrice(o.total)}</td><td>${STATUS_BADGE[o.status]||o.status}</td><td class="text-muted">${fmtDate(o.created_at)}</td></tr>`).join('')
        }</tbody></table>`;
    } catch(e) { toast(e.message, 'error'); }
}

// --- PRODUCTS ---
async function loadProducts() {
    try {
        const d = await api('/api/admin/products');
        const cont = document.getElementById('products-list');
        if (!d.data.length) { cont.innerHTML = '<div class="empty-state"><span class="empty-icon">📦</span><p>No hay productos. ¡Creá el primero!</p></div>'; return; }
        cont.innerHTML = `<table><thead><tr><th>Producto</th><th>Categoría</th><th>Precio</th><th>Variantes</th><th>Estado</th><th>Acciones</th></tr></thead><tbody>${
            d.data.map(p => `<tr>
                <td><strong>${p.name}</strong><br><span class="text-muted" style="font-size:12px">${p.slug}</span></td>
                <td>${p.category_name||'—'}</td>
                <td class="price">${fmtPrice(p.base_price)}</td>
                <td>${p.variants?.length||0}</td>
                <td>${p.active?'<span class="badge badge-success">Activo</span>':'<span class="badge badge-neutral">Inactivo</span>'}</td>
                <td class="actions-cell">
                    <button class="btn btn-secondary btn-sm" onclick="editProduct('${p.id}')">✏️</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteProduct('${p.id}','${p.name}')">🗑️</button>
                </td></tr>`).join('')
        }</tbody></table>`;
    } catch(e) { toast(e.message, 'error'); }
}

function showProductForm(product = null) {
    const isEdit = !!product;
    openModal(isEdit ? 'Editar producto' : 'Nuevo producto', `
        <form id="product-form">
            <div class="form-row">
                <div class="form-group"><label>Nombre</label><input type="text" id="pf-name" value="${product?.name||''}" required></div>
                <div class="form-group"><label>Slug</label><input type="text" id="pf-slug" value="${product?.slug||''}" required></div>
            </div>
            <div class="form-group"><label>Descripción</label><textarea id="pf-desc">${product?.description||''}</textarea></div>
            <div class="form-row">
                <div class="form-group"><label>Precio base ($)</label><input type="number" id="pf-price" value="${product?.base_price||''}" min="1" required></div>
                <div class="form-group"><label>SKU</label><input type="text" id="pf-sku" value="${product?.sku||''}"></div>
            </div>
            <div class="form-row">
                <div class="form-group"><label>Peso (gramos)</label><input type="number" id="pf-weight" value="${product?.weight_grams||500}"></div>
                <div class="form-group"><label>Categoría</label><select id="pf-cat"><option value="">Sin categoría</option></select></div>
            </div>
            <div class="form-group"><label><input type="checkbox" id="pf-featured" ${product?.featured?'checked':''}> Producto destacado</label></div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancelar</button>
                <button type="submit" class="btn btn-primary">${isEdit?'Guardar cambios':'Crear producto'}</button>
            </div>
        </form>
    `);
    // Auto-slug
    const nameEl = document.getElementById('pf-name');
    const slugEl = document.getElementById('pf-slug');
    if (!isEdit) nameEl.addEventListener('input', () => { slugEl.value = nameEl.value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/(^-|-$)/g,''); });
    // Load categories
    api('/api/categories?active_only=false').then(cats => {
        const sel = document.getElementById('pf-cat');
        cats.data.forEach(c => { const o = document.createElement('option'); o.value = c.id; o.textContent = c.name; if(product?.category_id===c.id) o.selected=true; sel.appendChild(o); });
    });
    document.getElementById('product-form').onsubmit = async (e) => {
        e.preventDefault();
        const body = { name: document.getElementById('pf-name').value, slug: document.getElementById('pf-slug').value, description: document.getElementById('pf-desc').value, base_price: parseFloat(document.getElementById('pf-price').value), sku: document.getElementById('pf-sku').value||null, weight_grams: parseInt(document.getElementById('pf-weight').value), category_id: document.getElementById('pf-cat').value||null, featured: document.getElementById('pf-featured').checked };
        try {
            if (isEdit) await api(`/api/admin/products/${product.id}`, { method: 'PUT', body: JSON.stringify(body) });
            else await api('/api/admin/products', { method: 'POST', body: JSON.stringify(body) });
            closeModal(); toast(isEdit?'Producto actualizado':'Producto creado'); loadProducts();
        } catch(e) { toast(e.message, 'error'); }
    };
}

async function editProduct(id) {
    try {
        const products = await api('/api/admin/products');
        const p = products.data.find(x => x.id === id);
        if (p) showProductForm(p);
    } catch(e) { toast(e.message, 'error'); }
}

async function deleteProduct(id, name) {
    if (!confirm(`¿Desactivar "${name}"?`)) return;
    try { await api(`/api/admin/products/${id}`, { method: 'DELETE' }); toast('Producto desactivado'); loadProducts(); } catch(e) { toast(e.message, 'error'); }
}

// --- CATEGORIES ---
async function loadCategories() {
    try {
        const d = await api('/api/categories?active_only=false');
        const cont = document.getElementById('categories-list');
        cont.innerHTML = `<table><thead><tr><th>Nombre</th><th>Slug</th><th>Posición</th><th>Estado</th><th>Acciones</th></tr></thead><tbody>${
            d.data.map(c => `<tr><td><strong>${c.name}</strong></td><td class="text-muted">${c.slug}</td><td>${c.position}</td><td>${c.active?'<span class="badge badge-success">Activa</span>':'<span class="badge badge-neutral">Inactiva</span>'}</td><td class="actions-cell"><button class="btn btn-secondary btn-sm" onclick="editCategory('${c.id}','${c.name}','${c.slug}','${c.description||''}',${c.position})">✏️</button></td></tr>`).join('')
        }</tbody></table>`;
    } catch(e) { toast(e.message, 'error'); }
}

function showCategoryForm(cat = null) {
    const isEdit = !!cat;
    openModal(isEdit ? 'Editar categoría' : 'Nueva categoría', `
        <form id="cat-form">
            <div class="form-row"><div class="form-group"><label>Nombre</label><input type="text" id="cf-name" value="${cat?.name||''}" required></div><div class="form-group"><label>Slug</label><input type="text" id="cf-slug" value="${cat?.slug||''}" required></div></div>
            <div class="form-group"><label>Descripción</label><textarea id="cf-desc">${cat?.description||''}</textarea></div>
            <div class="form-group"><label>Posición</label><input type="number" id="cf-pos" value="${cat?.position||0}" min="0"></div>
            <div class="modal-actions"><button type="button" class="btn btn-secondary" onclick="closeModal()">Cancelar</button><button type="submit" class="btn btn-primary">${isEdit?'Guardar':'Crear'}</button></div>
        </form>
    `);
    document.getElementById('cat-form').onsubmit = async (e) => {
        e.preventDefault();
        const body = { name: document.getElementById('cf-name').value, slug: document.getElementById('cf-slug').value, description: document.getElementById('cf-desc').value, position: parseInt(document.getElementById('cf-pos').value) };
        try {
            if (isEdit) await api(`/api/admin/categories/${cat.id}`, { method: 'PUT', body: JSON.stringify(body) });
            else await api('/api/admin/categories', { method: 'POST', body: JSON.stringify(body) });
            closeModal(); toast(isEdit?'Categoría actualizada':'Categoría creada'); loadCategories();
        } catch(e) { toast(e.message, 'error'); }
    };
}

function editCategory(id, name, slug, desc, pos) { showCategoryForm({id, name, slug, description: desc, position: pos}); }

// --- ORDERS ---
async function loadOrders() {
    try {
        const filter = document.getElementById('order-status-filter').value;
        const url = filter ? `/api/admin/orders?status=${filter}` : '/api/admin/orders';
        const d = await api(url);
        const cont = document.getElementById('orders-list');
        if (!d.data.length) { cont.innerHTML = '<div class="empty-state"><span class="empty-icon">🛒</span><p>No hay órdenes con este filtro</p></div>'; return; }
        cont.innerHTML = `<table><thead><tr><th>#</th><th>Cliente</th><th>Email</th><th>Total</th><th>Estado</th><th>Fecha</th><th>Acciones</th></tr></thead><tbody>${
            d.data.map(o => `<tr>
                <td><strong>#${String(o.order_number).padStart(4,'0')}</strong></td>
                <td>${o.customer_name||'—'}</td>
                <td class="text-muted">${o.customer_email||'—'}</td>
                <td class="price">${fmtPrice(o.total)}</td>
                <td>${STATUS_BADGE[o.status]||o.status}</td>
                <td class="text-muted">${fmtDate(o.created_at)}</td>
                <td class="actions-cell">
                    <button class="btn btn-secondary btn-sm" onclick="viewOrder('${o.id}')">👁️</button>
                    <button class="btn btn-secondary btn-sm" onclick="updateOrderStatus('${o.id}',${o.order_number},'${o.status}')">📝</button>
                </td></tr>`).join('')
        }</tbody></table>`;
    } catch(e) { toast(e.message, 'error'); }
}

async function viewOrder(id) {
    try {
        const o = await api(`/api/admin/orders/${id}`);
        const addr = o.shipping_address || {};
        openModal(`Orden #${String(o.order_number).padStart(4,'0')}`, `
            <div style="display:grid;gap:16px">
                <div><strong>Estado:</strong> ${STATUS_BADGE[o.status]||o.status}</div>
                <div><strong>Cliente:</strong> ${o.customer_name||'—'} (${o.customer_email||'—'})</div>
                <div><strong>Teléfono:</strong> ${o.customer_phone||'—'}</div>
                <div><strong>Dirección:</strong> ${addr.street||''} ${addr.street_number||''} ${addr.floor_apt||''}, ${addr.city||''}, ${addr.province||''} (${addr.postal_code||''})</div>
                ${o.shipping_tracking?`<div><strong>Tracking:</strong> ${o.shipping_tracking}</div>`:''}
                <div><strong>Notas:</strong> ${o.notes||'—'}</div>
                <hr style="border-color:var(--border)">
                <table><thead><tr><th>Producto</th><th>Cant.</th><th>Precio</th></tr></thead><tbody>${
                    (o.items||[]).map(i => `<tr><td>${i.product_name}${i.variant_name?' - '+i.variant_name:''}</td><td>${i.quantity}</td><td class="price">${fmtPrice(i.unit_price)}</td></tr>`).join('')
                }</tbody></table>
                <div class="text-right"><span class="text-muted">Subtotal:</span> <strong>${fmtPrice(o.subtotal)}</strong><br><span class="text-muted">Envío:</span> <strong>${fmtPrice(o.shipping_cost)}</strong><br><span style="font-size:18px">Total: <strong class="text-accent">${fmtPrice(o.total)}</strong></span></div>
            </div>
        `);
    } catch(e) { toast(e.message, 'error'); }
}

function updateOrderStatus(id, num, current) {
    openModal(`Actualizar orden #${String(num).padStart(4,'0')}`, `
        <form id="status-form">
            <div class="form-group"><label>Nuevo estado</label>
                <select id="sf-status">
                    <option value="pending_payment" ${current==='pending_payment'?'selected':''}>⏳ Pendiente de pago</option>
                    <option value="paid" ${current==='paid'?'selected':''}>💳 Pagado</option>
                    <option value="preparing" ${current==='preparing'?'selected':''}>📦 Preparando</option>
                    <option value="shipped" ${current==='shipped'?'selected':''}>🚚 Enviado</option>
                    <option value="delivered" ${current==='delivered'?'selected':''}>✅ Entregado</option>
                    <option value="cancelled" ${current==='cancelled'?'selected':''}>❌ Cancelado</option>
                </select>
            </div>
            <div class="form-group"><label>Número de tracking (si aplica)</label><input type="text" id="sf-tracking" placeholder="Ej: 360000012345678"></div>
            <div class="form-group"><label>Nota</label><textarea id="sf-note" placeholder="Nota opcional..."></textarea></div>
            <div class="modal-actions"><button type="button" class="btn btn-secondary" onclick="closeModal()">Cancelar</button><button type="submit" class="btn btn-primary">Actualizar</button></div>
        </form>
    `);
    document.getElementById('status-form').onsubmit = async (e) => {
        e.preventDefault();
        try {
            await api(`/api/admin/orders/${id}/status`, { method: 'PUT', body: JSON.stringify({ status: document.getElementById('sf-status').value, shipping_tracking: document.getElementById('sf-tracking').value||null, note: document.getElementById('sf-note').value||null }) });
            closeModal(); toast('Orden actualizada'); loadOrders();
        } catch(e) { toast(e.message, 'error'); }
    };
}

// --- Init ---
document.getElementById('login-form').addEventListener('submit', handleLogin);
document.getElementById('logout-btn').addEventListener('click', logout);
document.getElementById('modal-close').addEventListener('click', closeModal);
document.getElementById('modal-overlay').addEventListener('click', (e) => { if (e.target === e.currentTarget) closeModal(); });
document.getElementById('btn-new-product').addEventListener('click', () => showProductForm());
document.getElementById('btn-new-category').addEventListener('click', () => showCategoryForm());
document.getElementById('order-status-filter').addEventListener('change', loadOrders);
window.addEventListener('hashchange', () => navigate(location.hash.slice(1) || 'dashboard'));

// Auto-login if token exists
if (TOKEN) showApp(); 
