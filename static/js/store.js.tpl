{# ===== STORE JS ===== #}
{# Main store JavaScript for Fotos Jacky theme #}

(function(){
    'use strict';

    {# ===== Header Scroll Behavior ===== #}
    var header = document.getElementById('mainHeader');
    if (header) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 60) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    {# ===== Mobile Menu ===== #}
    var hamburger = document.querySelector('.js-hamburger');
    var mobileNav = document.querySelector('.js-mobile-nav');
    var navOverlay = document.querySelector('.js-nav-overlay');
    var mobileNavClose = document.querySelector('.js-mobile-nav-close');

    function openMobileNav() {
        if (mobileNav) mobileNav.classList.add('open');
        if (navOverlay) navOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    function closeMobileNav() {
        if (mobileNav) mobileNav.classList.remove('open');
        if (navOverlay) navOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (hamburger) hamburger.addEventListener('click', openMobileNav);
    if (navOverlay) navOverlay.addEventListener('click', closeMobileNav);
    if (mobileNavClose) mobileNavClose.addEventListener('click', closeMobileNav);

    var mobileLinks = document.querySelectorAll('.mobile-nav-links a');
    for (var i = 0; i < mobileLinks.length; i++) {
        mobileLinks[i].addEventListener('click', closeMobileNav);
    }

    {# ===== Search Toggle ===== #}
    var searchToggle = document.querySelector('.js-search-toggle');
    var searchModal = document.querySelector('.js-search-modal');
    var searchClose = document.querySelector('.js-search-close');

    if (searchToggle && searchModal) {
        searchToggle.addEventListener('click', function() {
            searchModal.style.display = 'block';
            var input = searchModal.querySelector('.search-input');
            if (input) input.focus();
        });
    }
    if (searchClose && searchModal) {
        searchClose.addEventListener('click', function() {
            searchModal.style.display = 'none';
        });
    }

    {# ===== Scroll Reveal (IntersectionObserver) ===== #}
    var revealElements = document.querySelectorAll('.reveal');
    if ('IntersectionObserver' in window && revealElements.length > 0) {
        var revealObserver = new IntersectionObserver(function(entries) {
            for (var j = 0; j < entries.length; j++) {
                if (entries[j].isIntersecting) {
                    entries[j].target.classList.add('visible');
                    revealObserver.unobserve(entries[j].target);
                }
            }
        }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

        for (var k = 0; k < revealElements.length; k++) {
            revealObserver.observe(revealElements[k]);
        }
    } else {
        // Fallback: show all elements
        for (var l = 0; l < revealElements.length; l++) {
            revealElements[l].classList.add('visible');
        }
    }

    {# ===== Product Page: Image Gallery ===== #}
    var thumbs = document.querySelectorAll('.product-thumb');
    var mainImage = document.querySelector('.js-product-main-image');

    for (var m = 0; m < thumbs.length; m++) {
        thumbs[m].addEventListener('click', function() {
            var src = this.getAttribute('data-image');
            if (mainImage && src) {
                mainImage.src = src;
            }
            // Update active state
            for (var n = 0; n < thumbs.length; n++) {
                thumbs[n].classList.remove('active');
            }
            this.classList.add('active');
        });
    }

    {# ===== Product Page: Quantity Selector ===== #}
    var qtyMinus = document.querySelector('.js-qty-minus');
    var qtyPlus = document.querySelector('.js-qty-plus');
    var qtyInput = document.querySelector('.js-qty-input');

    if (qtyMinus && qtyPlus && qtyInput) {
        qtyMinus.addEventListener('click', function() {
            var val = parseInt(qtyInput.value) || 1;
            if (val > 1) qtyInput.value = val - 1;
        });
        qtyPlus.addEventListener('click', function() {
            var val = parseInt(qtyInput.value) || 1;
            qtyInput.value = val + 1;
        });
    }

    {# ===== Smooth Scroll for Anchor Links ===== #}
    var anchors = document.querySelectorAll('a[href^="#"]');
    for (var p = 0; p < anchors.length; p++) {
        anchors[p].addEventListener('click', function(e) {
            var href = this.getAttribute('href');
            if (href && href.length > 1) {
                var target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    var headerH = header ? header.offsetHeight : 0;
                    var pos = target.getBoundingClientRect().top + window.pageYOffset - headerH;
                    window.scrollTo({ top: pos, behavior: 'smooth' });
                }
            }
        });
    }

})();
