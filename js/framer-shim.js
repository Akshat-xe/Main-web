/**
 * framer-shim.js — local stub for the Framer remote bundle.
 *
 * When the site runs offline (or without the Framer CDN), the main bundle
 * at framerusercontent.com fails to load, leaving every page blank.
 * This tiny shim pre-declares the globals Framer's SSR hydration checks
 * for, so the static HTML renders cleanly without console errors.
 *
 * The visual layer (everstar-next.js atmosphere + everstar-branding.js)
 * still runs independently and is unaffected.
 */
(function () {
  // Tell Framer's hydration check that the app is already mounted,
  // so it won't try to re-hydrate (and fail).
  window.MotionIsMounted = true;

  // Stub the motion handoff hooks so no null-ref errors fire.
  window.MotionHandoffAnimation = function () { return null; };
  window.MotionHasOptimisedAnimation = function () { return false; };
  window.MotionHandoffIsComplete = function () { return true; };
  window.MotionHandoffMarkAsComplete = function () {};
  window.MotionCancelOptimisedAnimation = function () {};
  window.MotionCheckAppearSync = function () {};

  // Suppress the "Failed to fetch dynamically imported module" boundary
  // that Framer's GracefullyDegradingErrorBoundary re-throws as a console
  // error — it already hides the broken content, this just keeps it quiet.
  window.addEventListener('unhandledrejection', function (e) {
    var msg = e.reason && (e.reason.message || String(e.reason));
    if (msg && msg.indexOf('framerusercontent.com') !== -1) {
      e.preventDefault();
    }
  });
})();
