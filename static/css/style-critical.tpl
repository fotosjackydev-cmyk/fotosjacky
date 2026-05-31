{# ===== CRITICAL CSS — Inlined in <head> ===== #}
{# This CSS loads immediately for fast first paint #}

:root {
  --terracota: #C96A2E;
  --durazno: #E8A87C;
  --crema: #FAF5EF;
  --carbon: #2C2C2A;
  --piedra: #888780;
  --white: #FFFFFF;
  --shadow-soft: 0 2px 20px rgba(0,0,0,0.06);
  --shadow-hover: 0 8px 32px rgba(0,0,0,0.10);
  --radius: 10px;
  --radius-lg: 16px;
  --transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  --font-display: Georgia, 'Times New Roman', serif;
  --font-body: -apple-system, 'Inter', 'Segoe UI', Roboto, sans-serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; -webkit-font-smoothing: antialiased; }
body { font-family: var(--font-body); color: var(--carbon); background: var(--crema); line-height: 1.6; overflow-x: hidden; }
img { max-width: 100%; height: auto; display: block; }
a { color: var(--terracota); text-decoration: none; transition: var(--transition); }
a:hover { color: var(--durazno); }
ul { list-style: none; }
button { cursor: pointer; border: none; font-family: inherit; }

h1, h2, h3, h4 { font-family: var(--font-display); color: var(--carbon); line-height: 1.2; font-weight: 400; }
h1 { font-size: clamp(2.2rem, 5vw, 3.8rem); }
h2 { font-size: clamp(1.6rem, 3.5vw, 2.6rem); }
h3 { font-size: clamp(1.2rem, 2vw, 1.5rem); }
p { color: var(--piedra); line-height: 1.7; font-size: 1rem; }

.text-accent { font-family: var(--font-body); text-transform: uppercase; letter-spacing: 0.12em; font-size: 0.8rem; font-weight: 600; color: var(--piedra); }
.container { width: 100%; max-width: 1200px; margin: 0 auto; padding: 0 24px; }
.hidden { display: none !important; }

/* Buttons */
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 14px 36px; border-radius: var(--radius); font-size: 0.95rem; font-weight: 600; letter-spacing: 0.04em; transition: var(--transition); }
.btn-primary { background: var(--terracota); color: var(--crema); }
.btn-primary:hover { background: var(--durazno); color: var(--white); transform: translateY(-2px); box-shadow: 0 6px 24px rgba(201,106,46,0.3); }
.btn-outline { background: transparent; color: var(--carbon); border: 2px solid var(--carbon); }
.btn-outline:hover { background: var(--carbon); color: var(--crema); }
.btn-sm { padding: 10px 24px; font-size: 0.85rem; }
.btn-full { width: 100%; }

/* Header — critical for LCP */
.header { position: fixed; top: 0; left: 0; width: 100%; z-index: 1000; transition: var(--transition); }
.header-inner { display: flex; align-items: center; justify-content: space-between; padding: 18px 0; transition: var(--transition); }
.header.scrolled { background: rgba(250,245,239,0.95); backdrop-filter: blur(20px); box-shadow: 0 1px 20px rgba(0,0,0,0.06); }
.header.scrolled .header-inner { padding: 12px 0; }

.logo { display: flex; align-items: baseline; gap: 4px; }
.logo-fotos { font-family: var(--font-body); font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.16em; color: var(--carbon); }
.logo-jacky { font-family: var(--font-display); font-size: 1.8rem; font-weight: 400; color: var(--carbon); line-height: 1; }

.nav-desktop { display: flex; gap: 32px; align-items: center; }
.nav-desktop a { font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: var(--carbon); position: relative; }
.nav-desktop a::after { content: ''; position: absolute; bottom: -4px; left: 0; width: 0; height: 2px; background: var(--terracota); transition: var(--transition); }
.nav-desktop a:hover { color: var(--terracota); }
.nav-desktop a:hover::after { width: 100%; }

.header-utils { display: flex; align-items: center; gap: 20px; }
.header-icon { width: 22px; height: 22px; color: var(--carbon); cursor: pointer; transition: var(--transition); background: none; padding: 0; display: inline-flex; }
.header-icon:hover { color: var(--terracota); }
.header-icon svg { width: 100%; height: 100%; }
.cart-badge { position: relative; }
.cart-count { position: absolute; top: -6px; right: -8px; background: var(--terracota); color: var(--white); font-size: 0.6rem; font-weight: 700; width: 16px; height: 16px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }

.hamburger { display: none; flex-direction: column; gap: 5px; cursor: pointer; background: none; padding: 4px; }
.hamburger span { width: 22px; height: 2px; background: var(--carbon); transition: var(--transition); }

/* Hero — critical for LCP */
.hero { position: relative; width: 100%; height: 100vh; min-height: 600px; max-height: 900px; overflow: hidden; display: flex; align-items: center; }
.hero-bg { position: absolute; inset: 0; z-index: 0; }
.hero-bg img { width: 100%; height: 100%; object-fit: cover; }
.hero-overlay { position: absolute; inset: 0; background: linear-gradient(135deg, rgba(250,245,239,0.85) 0%, rgba(250,245,239,0.4) 50%, rgba(250,245,239,0.1) 100%); z-index: 1; }
.hero-content { position: relative; z-index: 2; max-width: 580px; padding-left: 6%; }
.hero h1 { margin-bottom: 20px; opacity: 0; transform: translateY(30px); animation: fadeUp 0.8s 0.3s forwards; }
.hero p { font-size: 1.15rem; margin-bottom: 32px; max-width: 440px; opacity: 0; transform: translateY(30px); animation: fadeUp 0.8s 0.5s forwards; }
.hero-buttons { display: flex; gap: 16px; flex-wrap: wrap; opacity: 0; transform: translateY(30px); animation: fadeUp 0.8s 0.7s forwards; }
@keyframes fadeUp { to { opacity: 1; transform: translateY(0); } }

@media (max-width: 768px) {
  .nav-desktop { display: none; }
  .hamburger { display: flex; }
  .hero { min-height: 500px; max-height: 700px; }
  .hero-content { padding: 0 24px; max-width: 100%; }
  .hero h1 { font-size: 2rem; }
  .hero-overlay { background: linear-gradient(180deg, rgba(250,245,239,0.9) 0%, rgba(250,245,239,0.6) 60%, rgba(250,245,239,0.2) 100%); }
}
