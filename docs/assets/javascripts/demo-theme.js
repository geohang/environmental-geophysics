/* Shared canvas palette for SEES:4800 demos.
   Reads the CSS variables defined in demo.css so canvas drawings match the
   page theme (light by default, dark when the browser/OS prefers dark).
   Usage in a demo:
     const P = demoPalette();          // {bg, grid, text, muted, primary, ...}
     onThemeChange(draw);              // redraw when the OS theme flips
*/
function demoPalette() {
  const s = getComputedStyle(document.documentElement);
  const g = (n) => s.getPropertyValue(n).trim();
  return {
    bg: g('--canvas-bg'),
    surface: g('--surface'),
    surface2: g('--surface-2'),
    border: g('--border'),
    grid: g('--grid'),
    text: g('--text'),
    muted: g('--text-muted'),
    primary: g('--c-primary'),
    primaryBright: g('--c-primary-bright'),
    accent: g('--c-accent'),
    accentBright: g('--c-accent-bright'),
    danger: g('--c-danger'),
    success: g('--c-success'),
  };
}

function onThemeChange(cb) {
  if (window.matchMedia) {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = () => cb();
    if (mq.addEventListener) mq.addEventListener('change', handler);
    else if (mq.addListener) mq.addListener(handler);
  }
}
