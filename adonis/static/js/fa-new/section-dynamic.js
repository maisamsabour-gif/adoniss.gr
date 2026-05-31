(function () {
  "use strict";

  function applyInlineStyles(selector, attr) {
    var nodes = document.querySelectorAll(selector);
    nodes.forEach(function (node) {
      var value = node.getAttribute(attr);
      if (!value) return;
      node.style.cssText += ";" + value;
    });
  }

  applyInlineStyles("[data-section-style]", "data-section-style");
  applyInlineStyles("[data-card-style]", "data-card-style");
})();
