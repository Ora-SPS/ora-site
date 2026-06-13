/* Ora — aura motion engine
   Single rAF loop drives parallax, scroll progress, manifesto word
   reveal, loop-step activation, and card tilt. IntersectionObserver
   handles section reveals. Everything respects prefers-reduced-motion
   and degrades on coarse pointers. */

(() => {
  'use strict';

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = window.matchMedia('(pointer: fine)').matches;

  /* ---------- nav: scrolled state + hide on scroll down ---------- */
  const nav = document.getElementById('nav');
  let lastY = window.scrollY;
  let navTick = false;
  const updateNav = () => {
    const y = window.scrollY;
    nav.classList.toggle('is-scrolled', y > 30);
    if (y > 320 && y > lastY + 6) nav.classList.add('is-hidden');
    else if (y < lastY - 6 || y < 320) nav.classList.remove('is-hidden');
    lastY = y;
    navTick = false;
  };
  window.addEventListener('scroll', () => {
    if (!navTick) { navTick = true; requestAnimationFrame(updateNav); }
  }, { passive: true });

  /* ---------- section reveals ---------- */
  const revealEls = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      }
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.08 });
    revealEls.forEach((el) => io.observe(el));
    // safety net: nothing may stay invisible if observation ever misfires
    setTimeout(() => {
      revealEls.forEach((el) => {
        if (el.getBoundingClientRect().top < window.innerHeight) el.classList.add('in');
      });
    }, 3500);
  } else {
    revealEls.forEach((el) => el.classList.add('in'));
  }

  /* ---------- manifesto: split into words ---------- */
  const manifesto = document.querySelector('[data-words]');
  let words = [];
  if (manifesto) {
    const text = manifesto.textContent.trim().replace(/\s+/g, ' ');
    manifesto.textContent = '';
    const frag = document.createDocumentFragment();
    text.split(' ').forEach((word, i) => {
      const span = document.createElement('span');
      span.className = 'w';
      span.textContent = word;
      frag.appendChild(span);
      frag.appendChild(document.createTextNode(' '));
    });
    manifesto.appendChild(frag);
    words = Array.from(manifesto.querySelectorAll('.w'));
  }

  /* ---------- duplicate marquee rows for seamless loop ---------- */
  document.querySelectorAll('[data-marquee] .track-row').forEach((row) => {
    row.innerHTML += row.innerHTML;
    // 50% translate = one original set
    row.style.animationDuration = `${Math.max(30, row.children.length * 4.5)}s`;
  });

  if (reduceMotion) {
    words.forEach((w) => w.classList.add('lit'));
    document.querySelectorAll('[data-step]').forEach((s) => s.classList.add('active'));
    return; // no parallax / tilt / counters
  }

  /* ---------- single rAF scroll loop ---------- */
  const parallaxEls = Array.from(document.querySelectorAll('[data-parallax]')).map((el) => ({
    el,
    speed: parseFloat(el.dataset.parallax) || 0.2,
    spin: el.hasAttribute('data-spin'),
  }));
  const progressBar = document.querySelector('.scroll-progress span');
  const loopSteps = Array.from(document.querySelectorAll('[data-step]'));
  const loopFill = document.querySelector('[data-loop-fill]');
  const allowParallax = finePointer || window.innerWidth > 900;

  let vh = window.innerHeight;
  window.addEventListener('resize', () => { vh = window.innerHeight; }, { passive: true });

  const frame = () => {
    const y = window.scrollY;
    const doc = document.documentElement;
    const max = doc.scrollHeight - vh;

    if (progressBar) progressBar.style.transform = `scaleX(${max > 0 ? y / max : 0})`;

    if (allowParallax) {
      for (const p of parallaxEls) {
        const r = p.el.getBoundingClientRect();
        if (r.bottom < -200 || r.top > vh + 200) continue;
        const center = r.top + r.height / 2 - vh / 2;
        const shift = -center * p.speed;
        const rot = p.spin ? ` rotate(${(y * 0.012) % 360}deg)` : '';
        p.el.style.transform = `translate3d(0, ${shift.toFixed(1)}px, 0)${rot}`;
      }
    }

    // manifesto word lighting: progress through its viewport pass
    if (words.length) {
      const r = manifesto.getBoundingClientRect();
      const t = (vh * 0.82 - r.top) / (r.height + vh * 0.45);
      const lit = Math.floor(Math.max(0, Math.min(1, t)) * words.length);
      for (let i = 0; i < words.length; i++) {
        words[i].classList.toggle('lit', i < lit);
      }
    }

    // loop steps: activate as they cross the focus band
    if (loopSteps.length) {
      let active = 0;
      for (const step of loopSteps) {
        const r = step.getBoundingClientRect();
        const on = r.top < vh * 0.72;
        step.classList.toggle('active', on);
        if (on) active++;
      }
      if (loopFill) loopFill.style.transform = `scaleX(${active / loopSteps.length})`;
    }

    requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);

  /* ---------- count-up numbers ---------- */
  const counters = document.querySelectorAll('[data-count]');
  if (counters.length && 'IntersectionObserver' in window) {
    const cio = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        cio.unobserve(e.target);
        const target = parseInt(e.target.dataset.count, 10);
        const t0 = performance.now();
        const dur = 1400;
        const tick = (t) => {
          const k = Math.min(1, (t - t0) / dur);
          const eased = 1 - Math.pow(1 - k, 3);
          e.target.textContent = Math.round(target * eased);
          if (k < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      }
    }, { threshold: 0.5 });
    counters.forEach((c) => cio.observe(c));
  }

  if (!finePointer) return;

  /* ---------- magnetic buttons ---------- */
  document.querySelectorAll('.magnetic').forEach((btn) => {
    let raf = 0;
    btn.addEventListener('mousemove', (e) => {
      const r = btn.getBoundingClientRect();
      const dx = (e.clientX - r.left - r.width / 2) * 0.18;
      const dy = (e.clientY - r.top - r.height / 2) * 0.3;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        btn.style.transform = `translate(${dx.toFixed(1)}px, ${dy.toFixed(1)}px)`;
      });
    });
    btn.addEventListener('mouseleave', () => {
      cancelAnimationFrame(raf);
      btn.style.transform = '';
      btn.style.transition = 'transform .5s cubic-bezier(.16,1,.3,1), border-color .3s, background .3s, box-shadow .3s';
      setTimeout(() => { btn.style.transition = ''; }, 500);
    });
  });

  /* ---------- packet card tilt ---------- */
  const tilt = document.querySelector('[data-tilt]');
  if (tilt) {
    const stage = tilt.parentElement;
    let raf = 0;
    stage.addEventListener('mousemove', (e) => {
      const r = tilt.getBoundingClientRect();
      const rx = ((e.clientY - r.top) / r.height - 0.5) * -7;
      const ry = ((e.clientX - r.left) / r.width - 0.5) * 9;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        tilt.style.transform = `rotateX(${rx.toFixed(2)}deg) rotateY(${ry.toFixed(2)}deg)`;
      });
    });
    stage.addEventListener('mouseleave', () => {
      cancelAnimationFrame(raf);
      tilt.style.transition = 'transform .7s cubic-bezier(.16,1,.3,1)';
      tilt.style.transform = '';
      setTimeout(() => { tilt.style.transition = ''; }, 700);
    });
  }
})();
