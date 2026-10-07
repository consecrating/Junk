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

  /* ---------- nav active link ---------- */
  (function () {
    var page = (window.location.pathname.split('/').pop() || 'index.html').toLowerCase();
    if (page === '') page = 'index.html';
    document.querySelectorAll('.nav-links a').forEach(function (a) {
      var href = (a.getAttribute('href') || '').toLowerCase().split('/').pop();
      if (href === page || (page.indexOf('post-') === 0 && href === 'blog.html')) {
        a.classList.add('active');
      }
    });
  })();

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
  // Next headline event — NYE Gala, 31 Dec 2026, 9:00 PM IST
  var target = new Date('2026-12-31T21:00:00+05:30').getTime();
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
    var okMsg = document.getElementById('bookOk');
    // sensible minimum: today
    var dateInput = document.getElementById('bkDate');
    if (dateInput) dateInput.min = new Date().toISOString().split('T')[0];

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var valid = true;
      form.querySelectorAll('[required]').forEach(function (input) {
        var bad = !input.value.trim() ||
          (input.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value)) ||
          (input.type === 'tel' && input.value.replace(/\D/g, '').length < 7);
        input.classList.toggle('input-error', bad);
        if (bad) valid = false;
      });
      if (!valid) return;
      if (okMsg) {
        okMsg.classList.add('show');
        okMsg.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
      form.querySelectorAll('input, textarea').forEach(function (i) { i.value = ''; });
      setTimeout(function () { if (okMsg) okMsg.classList.remove('show'); }, 8000);
    });
    form.querySelectorAll('[required]').forEach(function (input) {
      input.addEventListener('input', function () {
        input.classList.remove('input-error');
      });
    });
  }

  /* ---------- contact form ---------- */
  var cForm = document.getElementById('contactForm');
  if (cForm) {
    cForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var valid = true;
      cForm.querySelectorAll('[required]').forEach(function (input) {
        var bad = !input.value.trim() ||
          (input.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value));
        input.classList.toggle('input-error', bad);
        if (bad) valid = false;
      });
      if (!valid) return;
      var ok = document.getElementById('contactOk');
      if (ok) { ok.classList.add('show'); ok.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
      cForm.querySelectorAll('input, textarea').forEach(function (i) { i.value = ''; });
      setTimeout(function () { if (ok) ok.classList.remove('show'); }, 8000);
    });
    cForm.querySelectorAll('[required]').forEach(function (input) {
      input.addEventListener('input', function () { input.classList.remove('input-error'); });
    });
  }

  /* ---------- blog filter + pagination ---------- */
  (function () {
    var grid = document.getElementById('blogGrid');
    var nav = document.getElementById('pagination');
    var pills = document.getElementById('filterPills');
    var noRes = document.getElementById('noResults');
    if (!grid || !nav) return;
    var cards = Array.prototype.slice.call(grid.querySelectorAll('[data-blog-card]'));
    var per = 6, page = 1, filter = 'all';
    function visible() {
      return cards.filter(function (c) {
        return filter === 'all' || c.getAttribute('data-cat') === filter;
      });
    }
    function go(p) {
      var list = visible();
      var pages = Math.max(1, Math.ceil(list.length / per));
      page = Math.max(1, Math.min(pages, p));
      cards.forEach(function (c) { c.style.display = 'none'; });
      list.forEach(function (c, i) {
        var show = Math.floor(i / per) + 1 === page;
        c.style.display = show ? '' : 'none';
        if (show) c.classList.add('in-view');
      });
      if (noRes) noRes.hidden = list.length > 0;
      nav.innerHTML = '';
      nav.style.display = pages > 1 ? '' : 'none';
      function btn(label, p, active, disabled, aria) {
        var b = document.createElement('button');
        b.textContent = label; b.type = 'button';
        if (active) b.classList.add('active');
        if (disabled) b.disabled = true;
        if (aria) b.setAttribute('aria-label', aria);
        b.addEventListener('click', function () { go(p); grid.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
        nav.appendChild(b);
      }
      btn('\u2039', page - 1, false, page === 1, 'Previous page');
      for (var i = 1; i <= pages; i++) btn(String(i), i, i === page, false, 'Page ' + i);
      btn('\u203A', page + 1, false, page === pages, 'Next page');
    }
    if (pills) pills.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      pills.querySelectorAll('button').forEach(function (x) { x.classList.remove('active'); });
      b.classList.add('active');
      filter = b.getAttribute('data-filter');
      go(1);
    });
    go(1);
  })();

  /* ---------- FAQ accordion ---------- */
  document.querySelectorAll('.faq-item').forEach(function (item) {
    var btn = item.querySelector('.faq-q');
    var panel = item.querySelector('.faq-a');
    if (!btn || !panel) return;
    btn.addEventListener('click', function () {
      var wasOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item.open').forEach(function (o) {
        o.classList.remove('open');
        o.querySelector('.faq-a').style.maxHeight = null;
      });
      if (!wasOpen) {
        item.classList.add('open');
        panel.style.maxHeight = panel.scrollHeight + 'px';
      }
    });
  });

  /* ---------- event lobby filters ---------- */
  var chips = document.querySelectorAll('.chip[data-filter]');
  if (chips.length) {
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        chips.forEach(function (c) { c.classList.remove('active'); });
        chip.classList.add('active');
        var f = chip.getAttribute('data-filter');
        document.querySelectorAll('.ev-row, .ev-gala').forEach(function (row) {
          row.classList.toggle('hidden', f !== 'all' && row.getAttribute('data-cat') !== f);
        });
      });
    });
  }

  /* ---------- 3D hero slider ---------- */
  (function () {
    var slider = document.getElementById('heroSlider');
    if (!slider) return;
    var slides = slider.querySelectorAll('.hslide');
    var dots = slider.querySelectorAll('.hdot');
    var prev = slider.querySelector('.hprev');
    var next = slider.querySelector('.hnext');
    var hCur = document.getElementById('hCur');
    var cur = 0, timer = null, DUR = 6500;
    function go(n) {
      slides[cur].classList.remove('active');
      if (dots[cur]) dots[cur].classList.remove('active');
      cur = (n + slides.length) % slides.length;
      slides[cur].classList.add('active');
      if (dots[cur]) dots[cur].classList.add('active');
      if (hCur) hCur.textContent = ('0' + (cur + 1)).slice(-2);
    }
    function stop() { if (timer) { clearInterval(timer); timer = null; } }
    function auto() { stop(); timer = setInterval(function () { go(cur + 1); }, DUR); }
    if (prev) prev.addEventListener('click', function () { go(cur - 1); auto(); });
    if (next) next.addEventListener('click', function () { go(cur + 1); auto(); });
    dots.forEach(function (d, i) {
      d.addEventListener('click', function () { go(i); auto(); });
    });
    slider.addEventListener('mouseenter', stop);
    slider.addEventListener('mouseleave', auto);
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) stop(); else auto();
    });
    auto();
  })();

  /* ---------- newsletter signup ---------- */
  (function () {
    var nf = document.getElementById('newsForm');
    if (!nf) return;
    nf.addEventListener('submit', function (e) {
      e.preventDefault();
      var em = document.getElementById('newsEmail');
      var ok = em && /.+@.+\..+/.test(em.value.trim());
      if (ok) {
        nf.style.display = 'none';
        document.getElementById('newsOk').classList.add('show');
      } else {
        em.style.borderColor = '#e63956';
        em.focus();
      }
    });
  })();

  /* ---------- booking package pick cards ---------- */
  document.querySelectorAll('.pack-pick').forEach(function (card) {
    card.addEventListener('click', function () {
      var v = card.getAttribute('data-pack');
      var sel = document.getElementById('fPack');
      if (sel) {
        for (var i = 0; i < sel.options.length; i++) {
          if (sel.options[i].text === v) { sel.selectedIndex = i; break; }
        }
      }
      document.querySelectorAll('.pack-pick').forEach(function (c) { c.classList.remove('sel'); });
      card.classList.add('sel');
    });
  });

  /* ---------- hover tracker: cursor-following preview ---------- */
  (function () {
    if (!window.matchMedia('(pointer:fine)').matches) return;
    var list = document.querySelector('.track-list');
    var float = document.querySelector('.track-float');
    if (!list || !float) return;
    var img = float.querySelector('img');
    var tx = 0, ty = 0, x = 0, y = 0, raf = null;
    function loop() {
      x += (tx - x) * 0.14;
      y += (ty - y) * 0.14;
      var tilt = Math.max(-10, Math.min(10, (tx - x) * 0.05));
      float.style.transform = 'translate(' + Math.round(x - 150) + 'px,' + Math.round(y - 190) + 'px) rotate(' + tilt.toFixed(2) + 'deg)';
      if (Math.abs(tx - x) > 0.4 || Math.abs(ty - y) > 0.4) raf = requestAnimationFrame(loop);
      else raf = null;
    }
    list.addEventListener('mousemove', function (e) {
      tx = e.clientX; ty = e.clientY;
      if (!raf) raf = requestAnimationFrame(loop);
    });
    list.querySelectorAll('.track-row').forEach(function (row) {
      row.addEventListener('mouseenter', function () {
        var src = row.getAttribute('data-img');
        if (src && img.getAttribute('src') !== src) img.setAttribute('src', src);
        float.classList.add('on');
      });
    });
    list.addEventListener('mouseleave', function () { float.classList.remove('on'); });
  })();

  /* ---------- 3D scroll section ---------- */
  (function () {
    var sec = document.getElementById('scroll3d');
    if (!sec || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var cards = Array.prototype.slice.call(sec.querySelectorAll('.s3d-card'));
    var bar = sec.querySelector('.s3d-progress i');
    var n = cards.length, ticking = false;
    function ease(t) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }
    function render() {
      ticking = false;
      var rect = sec.getBoundingClientRect();
      var total = sec.offsetHeight - window.innerHeight;
      var p = Math.min(1, Math.max(0, -rect.top / total));
      if (bar) bar.style.width = (p * 100).toFixed(2) + '%';
      cards.forEach(function (card, i) {
        var local = p * n - i, o, txv, rz, ry;
        if (local <= 0 || local >= 1) {
          o = 0; txv = local <= 0 ? 55 : -55; ry = local <= 0 ? -38 : 38; rz = -380;
        } else {
          var e = ease(local);
          o = Math.sin(local * Math.PI);
          txv = (0.5 - e) * 110;
          ry = (e - 0.5) * 76;
          rz = -380 * Math.abs(e - 0.5) * 2;
        }
        card.style.opacity = Math.max(0, Math.min(1, o)).toFixed(3);
        card.style.transform = 'translate(-50%,-50%) translateX(' + txv.toFixed(1) + 'vw) translateZ(' + rz.toFixed(0) + 'px) rotateY(' + ry.toFixed(1) + 'deg)';
      });
    }
    function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(render); } }
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    render();
  })();

  /* ---------- booking: package card select ---------- */
  var packs = document.querySelectorAll('.bpack');
  var packSel = document.getElementById('bkPack');
  var PACK_PRICES = { ideal: 2500, super: 3000, luxury: 4000, supreme: 5500 };
  var PACK_NAMES = { ideal: 'CP Ideal', super: 'CP Super', luxury: 'CP Super Luxury', supreme: 'CP Supreme' };
  function inr(n) { return '\u20B9' + n.toLocaleString('en-IN'); }
  function updateTotal() {
    var totalEl = document.getElementById('bookTotal');
    var noteEl = document.getElementById('bookTotalNote');
    if (!totalEl) return;
    var val = packSel ? packSel.value : 'super';
    var guestsEl = document.getElementById('bkGuests');
    var g = guestsEl ? Math.max(1, parseInt(guestsEl.value, 10) || 1) : 1;
    var total = (PACK_PRICES[val] || 3000) * g;
    totalEl.textContent = inr(total);
    if (noteEl) noteEl.textContent = g + (g === 1 ? ' guest' : ' guests') + ' \u00D7 ' + (PACK_NAMES[val] || val);
  }
  function selectPack(val) {
    packs.forEach(function (c) {
      var on = c.getAttribute('data-pack') === val;
      c.classList.toggle('selected', on);
      c.setAttribute('aria-checked', on ? 'true' : 'false');
    });
    if (packSel) packSel.value = val;
    updateTotal();
  }
  packs.forEach(function (c) {
    c.addEventListener('click', function () { selectPack(c.getAttribute('data-pack')); });
    c.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); selectPack(c.getAttribute('data-pack')); }
    });
  });
  if (packSel) packSel.addEventListener('change', function () { selectPack(packSel.value); });
  var guestsInput = document.getElementById('bkGuests');
  if (guestsInput) guestsInput.addEventListener('input', updateTotal);
  updateTotal();

  /* ---------- cautionary notice ---------- */
  (function () {
    var bar = document.getElementById('notice');
    var btn = document.getElementById('noticeClose');
    if (!bar || !btn) return;
    try {
      if (localStorage.getItem('cpNoticeOff') === '1') document.body.classList.add('notice-off');
    } catch (e) {}
    btn.addEventListener('click', function () {
      document.body.classList.add('notice-off');
      try { localStorage.setItem('cpNoticeOff', '1'); } catch (e) {}
    });
  })();

  /* ---------- respect reduced motion for video ---------- */
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.querySelectorAll('video[autoplay]').forEach(function (v) {
      v.removeAttribute('autoplay');
      v.pause();
    });
  }

  /* ---------- footer year ---------- */
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();
})();
