"use strict";
// PostHog for the live site, built to get past ad blockers (adapted from the
// posthog-adblock-bypass recipe for a static site):
// - Blockers match PostHog by file name (array.js, recorder.js,
//   dead-clicks-autocapture.js) on any host. posthog-js is self-hosted in _p/
//   under neutral names (jev_bench/scripts/31_posthog_assets.sh), and every
//   /static/<chunk>.js request PostHog makes is rewritten onto those copies.
// - Events, flags and replay uploads go to our CloudFront proxy, so no request
//   names a posthog.com host.
(function () {
  const KEY = "phc_EoMHKFbx6j2wUFsf8ywqgHntY4vEXC3ZzLFoPJVjRRT";   // public project key, safe in page code
  const HOST = "https://d18m0xvdtnkibr.cloudfront.net";             // CloudFront proxy to PostHog US
  const LIVE = location.hostname === "leanmcp.github.io";
  const DRY = window.__PH_DRY === true;                              // local test: load everything, send nothing
  const assets = window.__PH_ASSETS;

  const queue = [];
  window.track = (event, props) => {
    if (window.posthog && window.posthog.__loaded) window.posthog.capture(event, props);
    else queue.push([event, props]);
  };
  if (!assets || !(LIVE || DRY)) { window.track = () => {}; return; }

  const base = new URL("_p/", document.baseURI).href;
  const local = (name) => (assets.files[name] ? base + assets.files[name] + ".js" : null);

  // Rewrite script.src before PostHog sets it: .../static/lazy-recorder.js?v=1.x
  // becomes _p/7b4a5c3f.js?v=1.x, same origin and with no blockable word.
  const desc = Object.getOwnPropertyDescriptor(HTMLScriptElement.prototype, "src");
  if (desc && desc.set && desc.get && !window.__phRewriteInstalled) {
    window.__phRewriteInstalled = true;
    Object.defineProperty(HTMLScriptElement.prototype, "src", {
      configurable: true,
      enumerable: true,
      get() { return desc.get.call(this); },
      set(value) {
        if (typeof value === "string") {
          // posthog-js 1.4xx adds a version folder: /static/1.438.7/lazy-recorder.js
          const m = value.match(/\/static\/(?:[0-9][0-9.]*\/)?([a-z0-9-]+)\.js(\?[^#]*)?$/i);
          const to = m && local(m[1]);
          if (to) value = to + (m[2] || "");
        }
        desc.set.call(this, value);
      },
    });
  }

  const script = document.createElement("script");
  script.async = true;
  script.src = local("array");
  script.onload = () => {
    if (!window.posthog || typeof window.posthog.init !== "function") return;
    window.posthog.init(KEY, {
      api_host: HOST,
      ui_host: "https://us.posthog.com",
      person_profiles: "identified_only",
      // Session replay stays on; it also needs "Record user sessions" enabled
      // in the PostHog project settings, which the SDK reads on load.
      disable_session_recording: false,
      session_recording: { maskAllInputs: true },
      opt_out_capturing_by_default: DRY,
      loaded: (ph) => {
        for (const [event, props] of queue.splice(0)) ph.capture(event, props);
        if (DRY && typeof window.__PH_DRY_LOADED === "function") window.__PH_DRY_LOADED(ph);
      },
    });
  };
  document.head.appendChild(script);
})();
