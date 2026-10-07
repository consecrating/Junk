/* ============ PULSE — interactions ============ */
(function () {
  'use strict';

  /* ---------- preloader ---------- */
  var loader = document.getElementById('loader');
  function hideLoader() { if (loader) loader.classList.add('done'); }
  window.addEventListener('load', function () { setTimeout(hideLoader, 350); });
  setTimeout(hideLoader, 3500); // safety net

  /* ---------- nav state + burger ---------- */
  var nav = document.getElementById('nav');
  var toTop = document.getElementById('toTop');
  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    nav.classList.toggle('scrolled', y > 40);
    toTop.classList.toggle('show', y > 700);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  toTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });

  var burger = document.getElementById('burger');
  var navLinks = document.getElementById('navLinks');
  burger.addEventListener('click', function () {
    var open = navLinks.classList.toggle('open');
    burger.classList.toggle('open', open);
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  });
  navLinks.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () {
      navLinks.classList.remove('open');
      burger.classList.remove('open');
      burger.setAttribute('aria-expanded', 'false');
    });
  });

  /* ---------- reveal on scroll ---------- */
  var revealEls = document.querySelectorAll('.rv');
  if ('IntersectionObserver' in window) {
    var ro = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); ro.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function (el) { ro.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- animated counters ---------- */
  function animateCount(el) {
    var target = parseInt(el.getAttribute('data-count'), 10) || 0;
    var dur = 1600, start = null;
    function frame(t) {
      if (!start) start = t;
      var p = Math.min((t - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased);
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  var counters = document.querySelectorAll('[data-count]');
  if ('IntersectionObserver' in window) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { animateCount(e.target); co.unobserve(e.target); }
      });
    }, { threshold: 0.5 });
    counters.forEach(function (el) { co.observe(el); });
  } else {
    counters.forEach(animateCount);
  }

  /* ---------- countdown ---------- */
  // Next headline show — 18 Dec 2026, 8:00 PM IST
  var target = new Date('2026-12-18T20:00:00+05:30').getTime();
  var cdD = document.getElementById('cdD'),
      cdH = document.getElementById('cdH'),
      cdM = document.getElementById('cdM'),
      cdS = document.getElementById('cdS');
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function setCell(el, val) {
    var v = pad(val);
    if (el.textContent !== v) {
      el.textContent = v;
      el.classList.remove('tick');
      void el.offsetWidth; // restart animation
      el.classList.add('tick');
    }
  }
  function tickCountdown() {
    var diff = target - Date.now();
    if (diff < 0) diff = 0;
    setCell(cdD, Math.floor(diff / 864e5));
    setCell(cdH, Math.floor(diff / 36e5) % 24);
    setCell(cdM, Math.floor(diff / 6e4) % 60);
    setCell(cdS, Math.floor(diff / 1e3) % 60);
  }
  if (cdD) { tickCountdown(); setInterval(tickCountdown, 1000); }

  /* ---------- testimonial slider ---------- */
  var slidesBox = document.getElementById('slides');
  if (slidesBox) {
    var slides = slidesBox.children.length;
    var dotsBox = document.getElementById('dots');
    var idx = 0, timer = null;

    for (var i = 0; i < slides; i++) {
      (function (n) {
        var b = document.createElement('button');
        b.setAttribute('aria-label', 'Show testimonial ' + (n + 1));
        b.addEventListener('click', function () { go(n); restart(); });
        dotsBox.appendChild(b);
      })(i);
    }
    var dots = dotsBox.children;

    function go(n) {
      idx = (n + slides) % slides;
      slidesBox.style.transform = 'translateX(-' + (idx * 100) + '%)';
      for (var j = 0; j < dots.length; j++) dots[j].classList.toggle('active', j === idx);
    }
    function restart() { clearInterval(timer); timer = setInterval(function () { go(idx + 1); }, 6500); }

    document.getElementById('prevBtn').addEventListener('click', function () { go(idx - 1); restart(); });
    document.getElementById('nextBtn').addEventListener('click', function () { go(idx + 1); restart(); });

    var slider = document.getElementById('slider');
    slider.addEventListener('mouseenter', function () { clearInterval(timer); });
    slider.addEventListener('mouseleave', restart);

    // touch swipe
    var startX = 0;
    slider.addEventListener('touchstart', function (e) { startX = e.touches[0].clientX; }, { passive: true });
    slider.addEventListener('touchend', function (e) {
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 40) { go(idx + (dx < 0 ? 1 : -1)); restart(); }
    }, { passive: true });

    go(0); restart();
  }

  /* ---------- booking form ---------- */
  var form = document.getElementById('bookForm');
  if (form) {
    var okMsg = document.getElementById('formOk');
    // sensible minimum: today
    var dateInput = document.getElementById('fDate');
    dateInput.min = new Date().toISOString().split('T')[0];

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var valid = true;
      form.querySelectorAll('[required]').forEach(function (input) {
        var field = input.closest('.field');
        var bad = !input.value.trim() ||
          (input.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value));
        field.classList.toggle('error', bad);
        if (bad) valid = false;
      });
      if (!valid) return;
      okMsg.classList.add('show');
      okMsg.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      form.querySelectorAll('input, textarea').forEach(function (i) { i.value = ''; });
      setTimeout(function () { okMsg.classList.remove('show'); }, 8000);
    });
    form.querySelectorAll('[required]').forEach(function (input) {
      input.addEventListener('input', function () {
        input.closest('.field').classList.remove('error');
      });
    });
  }

  /* ---------- footer year ---------- */
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();
})();
