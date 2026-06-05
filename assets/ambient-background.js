(function () {
  const params = new URLSearchParams(window.location.search);
  const smallScreen = window.matchMedia('(max-width: 640px)');
  if (params.get('lite') === '1' || smallScreen.matches) {
    document.documentElement.classList.add('ora-lite-motion');
    return;
  }

  const canvas = document.createElement('canvas');
  canvas.className = 'ora-ambient-canvas';
  canvas.setAttribute('aria-hidden', 'true');
  document.body.prepend(canvas);

  const ctx = canvas.getContext('2d', { alpha: true });
  if (!ctx) return;

  const tau = Math.PI * 2;
  const durationMs = 20000;
  const particleColors = ['#9BE7FF', '#8EF4D1', '#D1D9FF'].map(hexToRgb);
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  let width = 0;
  let height = 0;
  let dpr = 1;
  let start = performance.now();
  let frameId = 0;
  let particleCount = 72;

  function hexToRgb(hex) {
    const value = hex.replace('#', '');
    return {
      r: parseInt(value.slice(0, 2), 16),
      g: parseInt(value.slice(2, 4), 16),
      b: parseInt(value.slice(4, 6), 16),
    };
  }

  function colorToCss(color, alpha) {
    return `rgba(${color.r}, ${color.g}, ${color.b}, ${alpha})`;
  }

  function lerpColor(a, b, t) {
    return {
      r: Math.round(a.r + (b.r - a.r) * t),
      g: Math.round(a.g + (b.g - a.g) * t),
      b: Math.round(a.b + (b.b - a.b) * t),
    };
  }

  function timeOfDayAccent() {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 11) return hexToRgb('#FFE0B2');
    if (hour >= 17 && hour < 21) return hexToRgb('#5C7AEA');
    if (hour >= 21 || hour < 5) return hexToRgb('#2C3A6E');
    return hexToRgb('#8CE1FF');
  }

  function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    const mobile = smallScreen.matches;
    particleCount = mobile ? 32 : 72;
    dpr = Math.min(window.devicePixelRatio || 1, mobile ? 1.25 : 2);
    canvas.width = Math.max(1, Math.floor(width * dpr));
    canvas.height = Math.max(1, Math.floor(height * dpr));
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    drawFrame(performance.now());
  }

  function drawBlob(x, y, size, color, alpha) {
    const radius = size / 2;
    const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
    gradient.addColorStop(0, colorToCss(color, alpha));
    gradient.addColorStop(1, colorToCss(color, 0));
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, tau);
    ctx.fill();
  }

  function drawParticles(t) {
    for (let i = 0; i < particleCount; i += 1) {
      const seed = (i * 7 + 3) / particleCount;
      const speedFactor = 0.4 + seed * 0.6;
      const xBase = (i * 0.618033988749895) % 1.0;
      const y = (1.0 - ((t * speedFactor + seed) % 1.0)) * height;
      const x =
        xBase * width +
        Math.sin(t * tau * (0.5 + i * 0.1) + i) * 10;
      const radius = 1.3 + (i % 4) * 0.55;
      const alpha = 0.06 + (i % 5) * 0.012;
      const color = particleColors[i % particleColors.length];
      ctx.fillStyle = colorToCss(color, alpha);
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, tau);
      ctx.fill();
    }
  }

  function drawBlobs(t) {
    const timeAccent = timeOfDayAccent();
    const stateAccent = hexToRgb('#8CE1FF');
    const mobile = smallScreen.matches;

    const topRightSize = mobile ? 210 : 300;
    const topRightTop = -140 + Math.sin(t * tau) * 18;
    const topRightRight = -90 + Math.cos(t * tau * 0.7) * 14;
    const topRightColor = lerpColor(
      lerpColor(hexToRgb('#8CE1FF'), stateAccent, 0),
      timeAccent,
      0.15,
    );
    drawBlob(
      width - topRightRight - topRightSize / 2,
      topRightTop + topRightSize / 2,
      topRightSize,
      topRightColor,
      0.22 + Math.sin(t * tau * 1.3) * 0.06,
    );

    const leftSize = mobile ? 180 : 260;
    const leftTop = 120 + Math.cos(t * tau * 0.6) * 20;
    const leftLeft = -110 + Math.sin(t * tau * 0.4 + 1.2) * 16;
    drawBlob(
      leftLeft + leftSize / 2,
      leftTop + leftSize / 2,
      leftSize,
      lerpColor(hexToRgb('#D7DEFF'), timeAccent, 0.1),
      0.12 + Math.sin(t * tau * 0.9 + 2.0) * 0.04,
    );

    const bottomSize = mobile ? 220 : 320;
    const bottomBottom = -160 + Math.sin(t * tau * 0.5 + 2.5) * 22;
    const bottomLeft = -80 + Math.cos(t * tau * 0.3 + 0.8) * 18;
    drawBlob(
      bottomLeft + bottomSize / 2,
      height - bottomBottom - bottomSize / 2,
      bottomSize,
      lerpColor(hexToRgb('#7EF0D7'), timeAccent, 0.1),
      0.1 + Math.cos(t * tau * 1.1 + 1.5) * 0.04,
    );
  }

  function drawFrame(now) {
    const t = prefersReducedMotion.matches
      ? 0.15
      : ((now - start) % durationMs) / durationMs;
    ctx.clearRect(0, 0, width, height);
    drawParticles(t);
    drawBlobs(t);
  }

  function tick(now) {
    drawFrame(now);
    frameId = requestAnimationFrame(tick);
  }

  function restartAnimation() {
    cancelAnimationFrame(frameId);
    start = performance.now();
    drawFrame(start);
    if (!prefersReducedMotion.matches && !document.hidden) {
      frameId = requestAnimationFrame(tick);
    }
  }

  function onVisibilityChange() {
    if (document.hidden) {
      cancelAnimationFrame(frameId);
      return;
    }
    restartAnimation();
  }

  function listenToMediaQuery(query, callback) {
    if (query.addEventListener) {
      query.addEventListener('change', callback);
      return;
    }
    if (query.addListener) {
      query.addListener(callback);
    }
  }

  window.addEventListener('resize', resize, { passive: true });
  document.addEventListener('visibilitychange', onVisibilityChange);
  listenToMediaQuery(prefersReducedMotion, restartAnimation);
  listenToMediaQuery(smallScreen, () => {
    resize();
    restartAnimation();
  });
  resize();
  restartAnimation();
})();
