/**
 * EVERSTAR — atmosphere parallax via CSS vars (Framer-friendly).
 * Fine pointer + wide viewport only; tab hidden stops RAF; minimal DOM writes.
 */
(function () {
  var root = document.documentElement;
  root.classList.add("everstar-next");

  var file = (location.pathname.split("/").pop() || "").toLowerCase();
  var isSubpage =
    file === "contact.html" ||
    file === "imprint.html" ||
    file === "privacy.html" ||
    file === "terms.html" ||
    file === "404.html";
  var isPortfolio = file === "portfolio.html" || file === "portfolio-works.html";
  if (isSubpage) {
    root.classList.add("everstar-subpage");
  }
  if (isPortfolio) {
    root.classList.add("everstar-portfolio");
  }

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var minParallaxW = 900;
  var parallaxAmp = isPortfolio ? 16 : isSubpage ? 20 : 36;
  var smooth = isPortfolio || isSubpage ? 0.09 : 0.08;

  var atmo = document.createElement("div");
  atmo.id = "everstar-atmo";
  atmo.setAttribute("aria-hidden", "true");
  if (document.body.firstChild) {
    document.body.insertBefore(atmo, document.body.firstChild);
  } else {
    document.body.appendChild(atmo);
  }

  var enableParallax = false;

  function syncParallaxGate() {
    enableParallax =
      !reduce && window.matchMedia("(pointer: fine)").matches && window.innerWidth >= minParallaxW;
  }

  if (!reduce) {
    var mx = 0;
    var my = 0;
    var tx = 0;
    var ty = 0;
    var raf = 0;
    var running = false;
    var lastSX = null;
    var lastSY = null;

    function loop() {
      if (!running) return;
      if (enableParallax) {
        tx += (mx - tx) * smooth;
        ty += (my - ty) * smooth;
        var sx = tx.toFixed(2);
        var sy = ty.toFixed(2);
        if (sx !== lastSX || sy !== lastSY) {
          lastSX = sx;
          lastSY = sy;
          root.style.setProperty("--ever-mx", sx);
          root.style.setProperty("--ever-my", sy);
        }
      } else {
        if (lastSX !== "0" || lastSY !== "0") {
          tx = ty = 0;
          lastSX = lastSY = "0";
          root.style.setProperty("--ever-mx", "0");
          root.style.setProperty("--ever-my", "0");
        }
      }
      raf = requestAnimationFrame(loop);
    }

    function startLoop() {
      if (running) return;
      running = true;
      raf = requestAnimationFrame(loop);
    }

    function stopLoop() {
      running = false;
      cancelAnimationFrame(raf);
    }

    window.addEventListener(
      "mousemove",
      function (e) {
        if (!enableParallax) return;
        var w = window.innerWidth || 1;
        var h = window.innerHeight || 1;
        mx = (e.clientX / w - 0.5) * parallaxAmp;
        my = (e.clientY / h - 0.5) * parallaxAmp;
      },
      { passive: true }
    );

    window.addEventListener(
      "resize",
      function () {
        syncParallaxGate();
      },
      { passive: true }
    );

    document.addEventListener(
      "visibilitychange",
      function () {
        syncParallaxGate();
        if (document.visibilityState === "hidden") {
          stopLoop();
        } else {
          startLoop();
        }
      },
      { passive: true }
    );

    syncParallaxGate();
    if (document.visibilityState !== "hidden") {
      startLoop();
    }

    window.addEventListener(
      "pagehide",
      function () {
        stopLoop();
      },
      { passive: true }
    );
  }

  function markHiddenSections() {
    if (isSubpage || isPortfolio) return;
    ["founder-note", "hero-3"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) {
        el.setAttribute("aria-hidden", "true");
        el.setAttribute("inert", "");
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", markHiddenSections);
  } else {
    markHiddenSections();
  }
})();
