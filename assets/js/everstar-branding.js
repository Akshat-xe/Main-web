/**
 * Re-apply EVERSTAR copy after Framer hydration (bundles still contain original site strings).
 * Optimized: Debounced MutationObserver, consolidated regex, single replacement pass.
 */
(function () {
  var PREFIX = "everstar-branding-";
  var PAIRS = [
    [/Hugoshtar/gi, "EVERSTAR"],
    [/Hugo\s+starter/gi, "EVERSTAR Starter"],
    [/Hugo\s+plus/gi, "EVERSTAR Plus"],
    [/Hugo\+/gi, "EVERSTAR+"],
    [/\bHugo\b/g, "EVERSTAR"],
    [/\bhugo\b/g, "EVERSTAR"],
    [/Landio\s*[-–]\s*AI Agency[^<]*/gi, "EVERSTAR"],
    [/Rebirth Portfolio/gi, "EVERSTAR Portfolio"],
    [/Every click feels premium\./g, "Decisions stay sharp when the interface stays out of the way."],
    [/Every part connected, every move effortless\./g, "One pipeline from signal to action—fewer hand-offs, less drift."],
  ];

  function replaceText(text) {
    for (var i = 0; i < PAIRS.length; i++) {
      text = text.replace(PAIRS[i][0], PAIRS[i][1]);
    }
    return text;
  }

  function applyTitle() {
    var t = document.title;
    var n = replaceText(t);
    if (n !== t) document.title = n;
  }

  function applyTextNode(node) {
    if (!node || !node.nodeValue) return;
    var n = replaceText(node.nodeValue);
    if (n !== node.nodeValue) node.nodeValue = n;
  }

  function walk(root) {
    if (!root) return;
    var skip = { SCRIPT: 1, STYLE: 1, NOSCRIPT: 1 };
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        var p = node.parentNode;
        if (!p || skip[p.tagName]) return NodeFilter.FILTER_REJECT;
        if (p.id && String(p.id).indexOf(PREFIX) === 0) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    var node;
    while ((node = w.nextNode())) applyTextNode(node);
  }

  var running = false, scheduled = false;
  function run() {
    if (running) return;
    running = true;
    try {
      walk(document.body);
      applyTitle();
      var al = document.querySelectorAll("[aria-label],[title]");
      for (var i = 0; i < al.length; i++) {
        var el = al[i];
        if (el.hasAttribute("aria-label")) {
          var lab = el.getAttribute("aria-label");
          var nl = replaceText(lab);
          if (nl !== lab) el.setAttribute("aria-label", nl);
        }
        if (el.title) {
          var nt = replaceText(el.title);
          if (nt !== el.title) el.title = nt;
        }
      }
    } finally {
      running = false;
    }
  }

  function scheduleRun() {
    if (scheduled) return;
    scheduled = true;
    setTimeout(function () { scheduled = false; run(); }, 0);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
  setTimeout(run, 500);

  try {
    var mo = new MutationObserver(scheduleRun);
    mo.observe(document.documentElement, { subtree: true, characterData: true, childList: true });
  } catch (e) {}
})();
