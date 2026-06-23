/* Ora — minimal motion.
   Reveals on scroll, nav state, scroll progress, and the sticky
   product-workflow screen swap. Motion only where it clarifies the
   product. Respects prefers-reduced-motion. */

(() => {
  'use strict';
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- nav: scrolled state + hide on scroll down ---------- */
  const nav = document.getElementById('nav');
  let lastY = window.scrollY;
  let tick = false;
  const progressBar = document.querySelector('.scroll-progress span');
  const updateScroll = () => {
    const y = window.scrollY;
    if (nav) {
      nav.classList.toggle('is-scrolled', y > 24);
      if (y > 300 && y > lastY + 6) nav.classList.add('is-hidden');
      else if (y < lastY - 6 || y < 300) nav.classList.remove('is-hidden');
    }
    if (progressBar) {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      progressBar.style.transform = `scaleX(${max > 0 ? y / max : 0})`;
    }
    lastY = y;
    tick = false;
  };
  window.addEventListener('scroll', () => {
    if (!tick) { tick = true; requestAnimationFrame(updateScroll); }
  }, { passive: true });
  updateScroll();

  /* ---------- reveals ---------- */
  const revealEls = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      }
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.12 });
    revealEls.forEach((el) => io.observe(el));
    // safety net: never leave above-the-fold content hidden
    setTimeout(() => {
      revealEls.forEach((el) => {
        if (el.getBoundingClientRect().top < window.innerHeight) el.classList.add('in');
      });
    }, 3000);
  } else {
    revealEls.forEach((el) => el.classList.add('in'));
  }

  /* ---------- sticky workflow: swap the sticky phone per active step ---------- */
  const flow = document.querySelector('[data-flow]');
  if (flow) {
    const screen = flow.querySelector('[data-flow-screen]');
    const steps = Array.from(flow.querySelectorAll('.flow-step'));
    const activate = (step) => {
      if (!step || step.classList.contains('is-active')) return;
      steps.forEach((s) => s.classList.toggle('is-active', s === step));
      const img = step.getAttribute('data-img');
      if (screen && img && screen.getAttribute('src') !== img) {
        if (reduceMotion) {
          screen.setAttribute('src', img);
        } else {
          screen.style.opacity = '0';
          setTimeout(() => { screen.setAttribute('src', img); screen.style.opacity = '1'; }, 180);
        }
      }
    };
    if (screen) screen.style.transition = 'opacity 0.28s var(--ease)';
    steps[0] && steps[0].classList.add('is-active');
    if ('IntersectionObserver' in window) {
      // active = the step crossing the vertical center of the viewport
      const io = new IntersectionObserver((entries) => {
        for (const e of entries) if (e.isIntersecting) activate(e.target);
      }, { rootMargin: '-45% 0px -45% 0px', threshold: 0 });
      steps.forEach((s) => io.observe(s));
    }
  }
})();
