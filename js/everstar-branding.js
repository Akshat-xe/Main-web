/**
 * Re-apply EVERSTAR copy after EVERSTAR hydration (bundles still contain original site strings).
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
    [
      /Every part connected, every move effortless\./g,
      "One pipeline from signal to action—fewer hand-offs, less drift.",
    ],
  ];

  function applyTitle() {
    var t = document.title;
    var n = t;
    for (var i = 0; i < PAIRS.length; i++) {
      n = n.replace(PAIRS[i][0], PAIRS[i][1]);
    }
    if (n !== t) document.title = n;
  }

  function applyTextNode(node) {
    if (!node || !node.nodeValue) return;
    var v = node.nodeValue;
    var n = v;
    for (var i = 0; i < PAIRS.length; i++) {
      n = n.replace(PAIRS[i][0], PAIRS[i][1]);
    }
    if (n !== v) node.nodeValue = n;
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

  var running = false;
  function run() {
    if (running) return;
    running = true;
    try {
      walk(document.body);
      applyTitle();
      var al = document.querySelectorAll("[aria-label],[title]");
      for (var i = 0; i < al.length; i++) {
        var el = al[i];
        if (el.getAttribute("aria-label")) {
          var lab = el.getAttribute("aria-label");
          var nl = lab;
          for (var j = 0; j < PAIRS.length; j++) nl = nl.replace(PAIRS[j][0], PAIRS[j][1]);
          if (nl !== lab) el.setAttribute("aria-label", nl);
        }
        if (el.title) {
          var tt = el.title;
          var nt = tt;
          for (var k = 0; k < PAIRS.length; k++) nt = nt.replace(PAIRS[k][0], PAIRS[k][1]);
          if (nt !== tt) el.title = nt;
        }
      }
    } finally {
      running = false;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
  setTimeout(run, 0);
  setTimeout(run, 500);
  setTimeout(run, 2000);

  try {
    var mo = new MutationObserver(function () {
      run();
    });
    mo.observe(document.documentElement, { subtree: true, characterData: true, childList: true });
  } catch (e) { }
})();
