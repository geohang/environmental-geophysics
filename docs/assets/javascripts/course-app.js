/* Progressive accessibility for standalone course applications. */
(function () {
  'use strict';

  function nearestText(element) {
    const container = element.closest('.ctrl, .input-group, .control-group, .form-group, .controls, td, section, .panel');
    if (!container) return '';
    const label = container.querySelector('label');
    if (label && label.textContent.trim()) return label.textContent.trim();
    const heading = container.querySelector('h1, h2, h3, h4, .stage-title');
    return heading ? heading.textContent.trim() : '';
  }

  function softenDarkTheme() {
    const match = window.getComputedStyle(document.body).backgroundColor.match(/[\d.]+/g);
    if (!match || match.length < 3) return;
    const rgb = match.slice(0, 3).map(Number).map((value) => value / 255);
    const linear = rgb.map((value) => value <= 0.04045
      ? value / 12.92
      : ((value + 0.055) / 1.055) ** 2.4);
    const luminance = 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
    if (luminance < 0.12) document.body.classList.add('course-soft-dark');
  }

  function enhanceControls() {
    document.querySelectorAll('input, select, textarea').forEach((control, index) => {
      if (!control.id) control.id = `course-control-${index + 1}`;
      if (control.labels && control.labels.length) {
        if (control.type === 'radio' || control.type === 'checkbox') {
          Array.from(control.labels).forEach((label) => label.classList.add('touch-label'));
        }
        return;
      }

      const parentLabel = control.closest('label');
      if (parentLabel) {
        parentLabel.htmlFor = control.id;
        if (control.type === 'radio' || control.type === 'checkbox') parentLabel.classList.add('touch-label');
        return;
      }

      const container = control.closest('.ctrl, .input-group, .control-group, .form-group, td');
      const visibleLabel = container ? container.querySelector('label') : null;
      if (visibleLabel && !visibleLabel.htmlFor) {
        visibleLabel.htmlFor = control.id;
        return;
      }

      const fallback = control.getAttribute('aria-label') || nearestText(control) || control.name || control.id.replace(/[-_]/g, ' ');
      const generatedLabel = document.createElement('label');
      generatedLabel.className = 'sr-only';
      generatedLabel.htmlFor = control.id;
      generatedLabel.textContent = fallback;
      control.insertAdjacentElement('beforebegin', generatedLabel);
    });
  }

  function enhanceCanvases() {
    document.querySelectorAll('canvas').forEach((canvas, index) => {
      if (!canvas.hasAttribute('role')) canvas.setAttribute('role', 'img');
      if (!canvas.hasAttribute('tabindex')) canvas.setAttribute('tabindex', '0');
      if (!canvas.getAttribute('aria-label')) {
        const container = canvas.closest('section, .panel, .stage, .card, .chart-container') || canvas.parentElement;
        const heading = container ? container.querySelector('h1, h2, h3, h4, .stage-title') : null;
        const title = heading ? heading.textContent.trim() : document.title;
        canvas.setAttribute('aria-label', `${title} interactive visualization ${index + 1}`);
      }
      const readoutId = `canvas-readout-${index + 1}`;
      let readout = document.getElementById(readoutId);
      if (!readout) {
        readout = document.createElement('p');
        readout.id = readoutId;
        readout.className = 'sr-only canvas-text-readout';
        readout.setAttribute('aria-live', 'polite');
        canvas.insertAdjacentElement('afterend', readout);
      }
      canvas.setAttribute('aria-describedby', readoutId);
    });

    updateCanvasReadouts();
  }

  function updateCanvasReadouts() {
    document.querySelectorAll('canvas').forEach((canvas, index) => {
      const readout = document.getElementById(`canvas-readout-${index + 1}`);
      if (!readout) return;
      const container = canvas.closest('section, .panel, .stage, .card, .chart-container') || canvas.parentElement;
      const valueNode = container ? container.querySelector('.readout, .result, .value-big, [id*="value"], [id*="result"]') : null;
      const text = valueNode && valueNode.textContent.trim()
        ? `Current plot reading: ${valueNode.textContent.trim()}`
        : 'Interactive plot. Change the adjacent controls to update the visualization.';
      if (readout.textContent !== text) readout.textContent = text;
    });
  }

  function enhanceFeedback() {
    document.querySelectorAll('.result, .feedback, .readout, [id*="result"], [id*="feedback"]').forEach((node) => {
      if (!node.hasAttribute('aria-live')) node.setAttribute('aria-live', 'polite');
    });
  }

  function enhanceNavigation() {
    const nav = document.querySelector('#course-nav-bar, .course-nav-bar');
    if (nav) {
      nav.classList.add('course-nav-bar');
      nav.setAttribute('role', 'navigation');
      nav.setAttribute('aria-label', 'Course navigation');
    }
  }

  function wrapWideTables() {
    document.querySelectorAll('table').forEach((table) => {
      if (table.parentElement && table.parentElement.classList.contains('table-scroll')) return;
      const wrapper = document.createElement('div');
      wrapper.className = 'table-scroll';
      wrapper.setAttribute('tabindex', '0');
      wrapper.setAttribute('role', 'region');
      wrapper.setAttribute('aria-label', 'Scrollable data table');
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    });
  }

  function initCourseApp() {
    softenDarkTheme();
    enhanceNavigation();
    enhanceControls();
    enhanceCanvases();
    enhanceFeedback();
    wrapWideTables();
    const observer = new MutationObserver(() => window.requestAnimationFrame(() => {
      enhanceControls();
      enhanceCanvases();
      enhanceFeedback();
      updateCanvasReadouts();
    }));
    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCourseApp, { once: true });
  } else {
    initCourseApp();
  }
}());
