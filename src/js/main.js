export function initNavigation() {
  // Header scroll behavior
  const header = document.getElementById('mainHeader');
  let lastScroll = 0;
  window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    if (currentScroll > 60) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
    lastScroll = currentScroll;
  });

  // Mobile menu
  const hamburger = document.getElementById('hamburgerBtn');
  const mobileNav = document.getElementById('mobileNav');
  const navOverlay = document.getElementById('navOverlay');
  const mobileNavClose = document.getElementById('mobileNavClose');

  function openNav() {
    mobileNav.classList.add('open');
    navOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
  function closeNav() {
    mobileNav.classList.remove('open');
    navOverlay.classList.remove('active');
    document.body.style.overflow = '';
  }
  if (hamburger) hamburger.addEventListener('click', openNav);
  if (navOverlay) navOverlay.addEventListener('click', closeNav);
  if (mobileNavClose) mobileNavClose.addEventListener('click', closeNav);
  document.querySelectorAll('.mobile-nav-links a').forEach(link => {
    link.addEventListener('click', closeNav);
  });
}

export function initScrollReveal() {
  // Scroll Reveal (IntersectionObserver)
  const revealElements = document.querySelectorAll('.reveal');
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

  revealElements.forEach(el => revealObserver.observe(el));
}

export function initSmoothScroll() {
  // Smooth scroll for anchor links
  const header = document.getElementById('mainHeader');
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        const headerHeight = header ? header.offsetHeight : 0;
        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;
        window.scrollTo({ top: targetPosition, behavior: 'smooth' });
      }
    });
  });
}

// Initialize all
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initScrollReveal();
  initSmoothScroll();
});
