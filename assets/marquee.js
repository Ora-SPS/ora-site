const marqueeTrack = document.querySelector('[data-marquee-track]');
const reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
const liteMode = new URLSearchParams(window.location.search).get('lite') === '1';

const debounce = (callback) => {
  let frame = 0;
  return () => {
    window.cancelAnimationFrame(frame);
    frame = window.requestAnimationFrame(callback);
  };
};

const resetMarquee = () => {
  if (!marqueeTrack) return;
  marqueeTrack.querySelectorAll('.marquee-generated').forEach((group) => group.remove());
  marqueeTrack.style.removeProperty('--marquee-distance');
  marqueeTrack.style.removeProperty('--marquee-duration');
};

const setupMarquee = () => {
  if (!marqueeTrack) return;

  resetMarquee();

  if (reduceMotionQuery.matches || liteMode) return;

  const sourceGroup = marqueeTrack.querySelector('[data-marquee-group]');
  const shell = marqueeTrack.closest('.marquee-shell');
  if (!sourceGroup || !shell) return;

  const sourceWidth = sourceGroup.getBoundingClientRect().width;
  const shellWidth = shell.getBoundingClientRect().width;
  if (!sourceWidth || !shellWidth) return;

  const minTrackWidth = shellWidth + (sourceWidth * 2);

  while (marqueeTrack.scrollWidth < minTrackWidth) {
    const clone = sourceGroup.cloneNode(true);
    clone.classList.add('marquee-generated');
    clone.setAttribute('aria-hidden', 'true');
    clone.removeAttribute('data-marquee-group');
    marqueeTrack.appendChild(clone);
  }

  const seconds = Math.max(28, Math.round(sourceWidth / 48));
  marqueeTrack.style.setProperty('--marquee-distance', `${sourceWidth}px`);
  marqueeTrack.style.setProperty('--marquee-duration', `${seconds}s`);
};

if (marqueeTrack) {
  const scheduleMarqueeSetup = debounce(setupMarquee);
  window.addEventListener('load', setupMarquee, { once: true });
  window.addEventListener('resize', scheduleMarqueeSetup);
  reduceMotionQuery.addEventListener('change', setupMarquee);
  setupMarquee();
}
