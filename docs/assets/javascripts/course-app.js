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
    if (document.body.classList.contains('lab-page')) return;
    const match = window.getComputedStyle(document.body).backgroundColor.match(/[\d.]+/g);
    if (!match || match.length < 3) return;
    // A transparent body says nothing about the page's theme.
    if (match.length > 3 && Number(match[3]) === 0) return;
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

  // Module order, app order, and canonical app names for in-app navigation.
  // The module pages (docs/lecture/<id>/index.md) list the same learning path.
  const COURSE_MAP = [
    { id: 'intro', name: 'Introduction', apps: [
      ['demo-depth-resolution.html', 'Depth of Investigation vs. Resolution', 'Demo'],
      ['introduction.html', 'Survey Spacing & Noise Simulator', 'Interactive lecture'],
    ] },
    { id: 'gravity', name: 'Gravity Methods', apps: [
      ['gravity-methods.html', 'Gravity Exploration & Data Reduction', 'Interactive lecture'],
      ['activity-1.html', 'Activity 1 · Drift Correction Loop', 'Activity'],
      ['activity-2.html', 'Activity 2 · Cross-Section Challenge', 'Activity'],
      ['demo-anomaly-modeler.html', 'Buried-Body Gravity Anomaly Modeler', 'Demo'],
      ['activity-3.html', 'Activity 3 · Depth Detective', 'Activity'],
    ] },
    { id: 'magnetic', name: 'Magnetic Methods', apps: [
      ['magnetic-methods.html', 'GeoMag Lab: Rock Magnetism', 'Activity'],
      ['demo-dipole-inclination.html', 'Dipole Anomaly vs. Inclination', 'Demo'],
      ['magnetic-signal.html', 'Geomagnetic Anomaly Simulator', 'Interactive lecture'],
      ['continuation.html', 'Continuation Simulator', 'Interactive lecture'],
      ['depth-estimation.html', 'Magnetic Interpretation Methods', 'Interactive lecture'],
    ] },
    { id: 'seismic', name: 'Seismic Methods', apps: [
      ['stress-and-strain.html', 'Elasticity & Seismic Waves', 'Interactive lecture'],
      ['demo-refraction-traveltime.html', 'Refraction Travel-Time Curve Builder', 'Demo'],
      ['seismic-refraction.html', 'Seismic Refraction Lab', 'Interactive lecture'],
    ] },
    { id: 'electrical', name: 'Electrical Methods', apps: [
      ['electrical-methods.html', 'How Do Rocks Conduct Electricity?', 'Interactive lecture'],
      ['ert.html', 'ERT · Geometric Factor K', 'Interactive lecture'],
      ['ert-2.html', 'ERT · 3-Layer VES Forward Model', 'Interactive lecture'],
      ['demo-pseudosection.html', 'Apparent-Resistivity Pseudosection Builder', 'Demo'],
      ['sp.html', 'SP · Signal Mechanisms', 'Interactive lecture'],
      ['sp-2.html', 'SP · Field Applications', 'Activity'],
      ['ip.html', 'IP · Signal Mechanisms', 'Interactive lecture'],
      ['ip-2.html', 'IP · Cole-Cole Model', 'Interactive lecture'],
    ] },
    { id: 'em', name: 'Electromagnetic Methods', apps: [
      ['electromagnetic-methods.html', 'EM Induction Principle (Whiteboard)', 'Interactive lecture'],
      ['electromagnetic-methods-2.html', 'CW vs. TEM Waveforms', 'Interactive lecture'],
      ['demo-skin-depth.html', 'Skin Depth Calculator & Visualizer', 'Demo'],
      ['fdem-tem.html', '1D EM Response Explorer', 'Interactive lecture'],
    ] },
    { id: 'mt', name: 'Magnetotellurics & Deep EM', apps: [
      ['mt.html', 'Deep EM Visualizer', 'Interactive lecture'],
      ['demo-mt-sounding.html', '1D Magnetotelluric Sounding Explorer', 'Demo'],
    ] },
    { id: 'gpr', name: 'Ground-Penetrating Radar', apps: [
      ['gpr.html', 'Conduction vs. Displacement Currents', 'Interactive lecture'],
      ['gpr-2.html', 'GPR Simulator', 'Interactive lecture'],
      ['demo-hyperbola.html', 'Hyperbola Velocity Estimator', 'Demo'],
    ] },
    { id: 'borehole', name: 'Borehole Geophysics', apps: [
      ['borehole-geophysics.html', 'Borehole Logging Dashboard', 'Interactive lecture'],
      ['demo-log-response.html', 'Wireline Log Response Explorer', 'Demo'],
    ] },
  ];

  function el(tag, attrs, children) {
    const node = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([key, value]) => {
      if (value === null || value === undefined || value === false) return;
      if (key === 'text') node.textContent = value;
      else node.setAttribute(key, value === true ? '' : value);
    });
    (children || []).forEach((child) => node.appendChild(typeof child === 'string' ? document.createTextNode(child) : child));
    return node;
  }

  // Where this page sits in COURSE_MAP; links are relative to lecture/<module>/apps/<file>.
  function locateApp() {
    const match = window.location.pathname.match(/\/lecture\/([^/]+)\/apps\/([^/]+\.html)$/);
    if (!match) return null;
    const moduleIndex = COURSE_MAP.findIndex((module) => module.id === match[1]);
    if (moduleIndex < 0) return null;
    const appIndex = COURSE_MAP[moduleIndex].apps.findIndex((app) => app[0] === match[2]);
    if (appIndex < 0) return null;
    return { moduleIndex, appIndex, module: COURSE_MAP[moduleIndex] };
  }

  function stepTargets(place) {
    const { moduleIndex, appIndex, module } = place;
    const apps = module.apps;
    const prev = appIndex > 0
      ? { href: apps[appIndex - 1][0], label: 'Prev', title: apps[appIndex - 1][1] }
      : { href: '../', label: 'Overview', title: `${module.name} overview` };
    let next;
    if (appIndex < apps.length - 1) {
      next = { href: apps[appIndex + 1][0], label: 'Next', title: apps[appIndex + 1][1], kind: 'Next in this module' };
    } else if (moduleIndex < COURSE_MAP.length - 1) {
      const following = COURSE_MAP[moduleIndex + 1];
      next = { href: `../../${following.id}/`, label: 'Next module', title: following.name, kind: 'Next module' };
    } else {
      next = { href: '../../../', label: 'Home', title: 'Course home', kind: 'You reached the last module' };
    }
    return { prev, next };
  }

  function buildModuleMenu(place) {
    const { appIndex, module } = place;
    const wrapper = el('div', { class: 'cn-menu' });
    const button = el('button', {
      type: 'button', class: 'cn-menu-btn', 'aria-expanded': 'false', 'aria-controls': 'cn-menu-panel',
      'aria-label': `Apps in ${module.name}, app ${appIndex + 1} of ${module.apps.length}`,
    }, [
      el('span', { class: 'cn-menu-long', text: `App ${appIndex + 1} of ${module.apps.length}` }),
      el('span', { class: 'cn-menu-short', text: `${appIndex + 1}/${module.apps.length}` }),
      el('span', { class: 'cn-caret', 'aria-hidden': 'true', text: '▾' }),
    ]);
    const list = el('ol', { class: 'cn-menu-list' }, module.apps.map((app, index) => el('li', {}, [
      el('a', { href: app[0], 'aria-current': index === appIndex ? 'page' : null }, [
        el('span', { class: 'cn-num', text: String(index + 1) }),
        el('span', { class: 'cn-name', text: app[1] }),
        el('span', { class: 'cn-type', text: app[2] }),
      ]),
    ])));
    const panel = el('div', { class: 'cn-menu-panel', id: 'cn-menu-panel', hidden: true }, [
      el('p', { class: 'cn-menu-title', text: `${module.name} · learning path` }),
      list,
      el('div', { class: 'cn-menu-foot' }, [
        el('a', { href: '../', text: 'Module overview' }),
        el('a', { href: `../../../apps/practice-lab.html#${module.id}`, text: 'Practice this module' }),
      ]),
    ]);
    const setOpen = (open) => {
      panel.hidden = !open;
      button.setAttribute('aria-expanded', String(open));
    };
    button.addEventListener('click', (event) => {
      event.stopPropagation();
      setOpen(panel.hidden);
    });
    document.addEventListener('click', (event) => {
      if (!panel.hidden && !wrapper.contains(event.target)) setOpen(false);
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && !panel.hidden) {
        setOpen(false);
        button.focus();
      }
    });
    wrapper.append(button, panel);
    return wrapper;
  }

  // Replace the static "Course Home / Module" bar with breadcrumb, module menu, and prev/next.
  function buildCourseNav(place) {
    const nav = document.querySelector('#course-nav-bar, .course-nav-bar');
    if (!nav || nav.classList.contains('is-enhanced')) return;
    const { appIndex, module } = place;
    const { prev, next } = stepTargets(place);
    const current = module.apps[appIndex];
    nav.replaceChildren(
      el('a', { class: 'cn-home', href: '../../../', text: '← Home' }),
      el('span', { class: 'cn-sep', 'aria-hidden': 'true', text: '›' }),
      el('a', { class: 'cn-module', href: '../', text: module.name }),
      el('span', { class: 'cn-sep cn-sep-current', 'aria-hidden': 'true', text: '›' }),
      el('span', { class: 'cn-current', 'aria-current': 'page', title: current[1], text: current[1] }),
      el('div', { class: 'cn-actions' }, [
        buildModuleMenu(place),
        el('a', { class: 'cn-step cn-prev', href: prev.href, 'aria-label': `${prev.label}: ${prev.title}`, title: prev.title }, [
          el('span', { 'aria-hidden': 'true', text: '‹' }), el('span', { class: 'cn-step-label', text: prev.label }),
        ]),
        el('a', { class: 'cn-step cn-next', href: next.href, 'aria-label': `${next.label}: ${next.title}`, title: next.title }, [
          el('span', { class: 'cn-step-label', text: next.label }), el('span', { 'aria-hidden': 'true', text: '›' }),
        ]),
      ]),
    );
    nav.classList.add('is-enhanced');
  }

  // Closing card: where the student is in the module and where to go next.
  function buildNextCard(place) {
    if (document.querySelector('.course-next-card')) return;
    // Full-viewport dashboards clip the page; the top bar already carries Next there.
    if (window.getComputedStyle(document.body).overflowY === 'hidden') return;
    const { appIndex, module } = place;
    const { next } = stepTargets(place);
    const card = el('nav', { class: 'course-next-card', 'aria-label': 'Continue the course' }, [
      el('div', { class: 'cnc-inner' }, [
        el('p', { class: 'cnc-kicker', text: `${module.name} · App ${appIndex + 1} of ${module.apps.length}` }),
        el('a', { class: 'cnc-next', href: next.href }, [
          el('span', { class: 'cnc-next-kind', text: next.kind }),
          el('span', { class: 'cnc-next-name', text: `${next.title} →` }),
        ]),
        el('div', { class: 'cnc-links' }, [
          el('a', { href: '../', text: `Back to ${module.name}` }),
          el('a', { href: `../../../apps/practice-lab.html#${module.id}`, text: 'Practice this module' }),
        ]),
      ]),
    ]);
    document.body.appendChild(card);
  }

  function enhanceNavigation() {
    const place = locateApp();
    if (place) {
      buildCourseNav(place);
      buildNextCard(place);
    }
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
    let enhancementFrame = 0;
    const observer = new MutationObserver(() => {
      if (enhancementFrame) return;
      enhancementFrame = window.requestAnimationFrame(() => {
        enhancementFrame = 0;
        enhanceControls();
        enhanceCanvases();
        enhanceFeedback();
        updateCanvasReadouts();
      });
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCourseApp, { once: true });
  } else {
    initCourseApp();
  }
}());
