/**
 * SEO Preview + Validation Widget
 *
 * Generic — auto-detects fields on any Django admin change form.
 *
 * Features:
 *  - Live Google SERP preview (title + URL + meta description)
 *  - Live OG / Twitter card preview tabs
 *  - Character counters with colour thresholds for title, description, OG, Twitter
 *  - Inline warnings: title >60, description >160, missing ALT
 *  - ALT text warnings on page load AND on file change (including tier images)
 *  - CKEditor content scanning for H2 headings
 *  - Save-time validation banner (non-blocking advisory)
 */
(function () {
  "use strict";

  // ── generic field finders ───────────────────────────────────────────────
  function $(sel) { return document.querySelector(sel); }
  function $$(sel) { return Array.from(document.querySelectorAll(sel)); }

  function findOne(ids) {
    for (const id of ids) {
      const el = $(id);
      if (el) return el;
    }
    return null;
  }

  const seoTitleEl  = () => findOne(["#id_seo_title","#id_meta_title","input[name='seo_title']","input[name='meta_title']"]);
  const metaDescEl  = () => findOne(["#id_meta_description","textarea[name='meta_description']","input[name='meta_description']"]);
  const slugEl      = () => findOne(["#id_slug","input[name='slug']","#id_detail_page_url","input[name='detail_page_url']"]);
  const pageTitleEl = () => findOne(["#id_title","input[name='title']","#id_name","input[name='name']","#id_hero_title","input[name='hero_title']","#id_client_name","input[name='client_name']"]);
  const ogTitleEl   = () => findOne(["#id_og_title","input[name='og_title']"]);
  const ogDescEl    = () => findOne(["#id_og_description","textarea[name='og_description']","input[name='og_description']"]);
  const twTitleEl   = () => findOne(["#id_twitter_title","input[name='twitter_title']"]);
  const twDescEl    = () => findOne(["#id_twitter_description","textarea[name='twitter_description']","input[name='twitter_description']"]);

  // Detect if we're on the GoldenVisaLandingPage admin (singleton — no slug field).
  function getPreviewUrl() {
    var slug = slugEl();
    if (slug && slug.value.trim()) {
      return "https://adonisgroup.gr/" + slug.value.trim() + "/";
    }
    // Golden Visa singleton: check if hero_title field exists with no slug
    var heroTitle = findOne(["#id_hero_title","input[name='hero_title']"]);
    if (heroTitle && !slug) {
      return "https://adonisgroup.gr/greece-golden-visa/";
    }
    return "https://adonisgroup.gr/\u2026/";
  }

  // ── SERP preview widget ─────────────────────────────────────────────────
  function buildPreviewWidget() {
    var d = document.createElement("div");
    d.className = "seo-preview-widget";
    d.innerHTML =
      '<div class="seo-preview-header">' +
        '<span class="seo-preview-icon">&#x1F50D;</span>' +
        '<span>Google / Social Preview</span>' +
        '<div class="seo-preview-tabs" style="margin-left:auto;display:flex;gap:6px;">' +
          '<button type="button" class="seo-tab seo-tab--active" data-tab="google">Google</button>' +
          '<button type="button" class="seo-tab" data-tab="og">OG / Facebook</button>' +
          '<button type="button" class="seo-tab" data-tab="twitter">Twitter / X</button>' +
        '</div>' +
      '</div>' +
      /* Google SERP */
      '<div class="seo-preview-pane" data-pane="google">' +
        '<div class="seo-preview-box">' +
          '<div class="seo-preview-url" id="seoUrl">https://adonisgroup.gr/\u2026/</div>' +
          '<div class="seo-preview-title" id="seoTitle">Page title will appear here</div>' +
          '<div class="seo-preview-desc" id="seoDesc">Meta description will appear here. Keep it 120\u2013160 characters for best results.</div>' +
        '</div>' +
        '<div class="seo-counters">' +
          '<div class="seo-counter-row"><span class="seo-counter-label">Title:</span> <span id="seoCntT" class="seo-count seo-ok">0</span><span class="seo-counter-hint"> / 60 chars</span></div>' +
          '<div class="seo-counter-row"><span class="seo-counter-label">Description:</span> <span id="seoCntD" class="seo-count seo-ok">0</span><span class="seo-counter-hint"> / 160 chars</span></div>' +
        '</div>' +
        '<div id="seoWarnsGoogle" class="seo-warnings" style="display:none"></div>' +
      '</div>' +
      /* OG */
      '<div class="seo-preview-pane" data-pane="og" style="display:none">' +
        '<div class="seo-og-card">' +
          '<div class="seo-og-card__image-placeholder" id="ogImgPreview">&#x1F5BC; No OG image uploaded</div>' +
          '<div class="seo-og-card__body">' +
            '<div class="seo-og-card__url" id="ogUrl">adonisgroup.gr</div>' +
            '<div class="seo-og-card__title" id="ogTitle">OG title will appear here</div>' +
            '<div class="seo-og-card__desc" id="ogDesc">OG description will appear here.</div>' +
          '</div>' +
        '</div>' +
        '<div class="seo-counters">' +
          '<div class="seo-counter-row"><span class="seo-counter-label">OG Title:</span> <span id="seoCntOgT" class="seo-count seo-ok">0</span><span class="seo-counter-hint"> / 100 chars</span></div>' +
          '<div class="seo-counter-row"><span class="seo-counter-label">OG Description:</span> <span id="seoCntOgD" class="seo-count seo-ok">0</span><span class="seo-counter-hint"> / 200 chars</span></div>' +
        '</div>' +
        '<div id="seoWarnsOg" class="seo-warnings" style="display:none"></div>' +
      '</div>' +
      /* Twitter */
      '<div class="seo-preview-pane" data-pane="twitter" style="display:none">' +
        '<div class="seo-twitter-card">' +
          '<div class="seo-twitter-card__image-placeholder" id="twImgPreview">&#x1F5BC; No Twitter image uploaded</div>' +
          '<div class="seo-twitter-card__body">' +
            '<div class="seo-twitter-card__title" id="twTitle">Twitter title will appear here</div>' +
            '<div class="seo-twitter-card__desc" id="twDesc">Twitter description will appear here.</div>' +
            '<div class="seo-twitter-card__url" id="twUrl">adonisgroup.gr</div>' +
          '</div>' +
        '</div>' +
        '<div class="seo-counters">' +
          '<div class="seo-counter-row"><span class="seo-counter-label">Twitter Title:</span> <span id="seoCntTwT" class="seo-count seo-ok">0</span><span class="seo-counter-hint"> / 100 chars</span></div>' +
          '<div class="seo-counter-row"><span class="seo-counter-label">Twitter Description:</span> <span id="seoCntTwD" class="seo-count seo-ok">0</span><span class="seo-counter-hint"> / 200 chars</span></div>' +
        '</div>' +
        '<div id="seoWarnsTw" class="seo-warnings" style="display:none"></div>' +
      '</div>';
    return d;
  }

  function initSERP() {
    var desc = metaDescEl();
    if (!desc) return;
    var title  = seoTitleEl();
    var pTitle = pageTitleEl();

    var row = desc.closest(".form-row") || desc.closest("fieldset");
    if (!row) return;

    var widget = buildPreviewWidget();
    row.insertAdjacentElement("afterend", widget);

    // Tab switching
    widget.querySelectorAll(".seo-tab").forEach(function(btn) {
      btn.addEventListener("click", function() {
        widget.querySelectorAll(".seo-tab").forEach(function(b){ b.classList.remove("seo-tab--active"); });
        btn.classList.add("seo-tab--active");
        widget.querySelectorAll(".seo-preview-pane").forEach(function(p){ p.style.display = "none"; });
        var pane = widget.querySelector('[data-pane="' + btn.dataset.tab + '"]');
        if (pane) pane.style.display = "";
      });
    });

    var elTitle  = widget.querySelector("#seoTitle");
    var elDesc   = widget.querySelector("#seoDesc");
    var elUrl    = widget.querySelector("#seoUrl");
    var cntT     = widget.querySelector("#seoCntT");
    var cntD     = widget.querySelector("#seoCntD");
    var warnsG   = widget.querySelector("#seoWarnsGoogle");

    var elOgTitle = widget.querySelector("#ogTitle");
    var elOgDesc  = widget.querySelector("#ogDesc");
    var elOgUrl   = widget.querySelector("#ogUrl");
    var cntOgT    = widget.querySelector("#seoCntOgT");
    var cntOgD    = widget.querySelector("#seoCntOgD");
    var warnsOg   = widget.querySelector("#seoWarnsOg");

    var elTwTitle = widget.querySelector("#twTitle");
    var elTwDesc  = widget.querySelector("#twDesc");
    var elTwUrl   = widget.querySelector("#twUrl");
    var cntTwT    = widget.querySelector("#seoCntTwT");
    var cntTwD    = widget.querySelector("#seoCntTwD");
    var warnsTw   = widget.querySelector("#seoWarnsTw");

    function countColor(n, ok, warn) {
      return n === 0 ? "seo-muted" : n <= ok ? "seo-ok" : n <= warn ? "seo-warn" : "seo-danger";
    }

    function setWarns(el, msgs) {
      if (msgs.length) {
        el.innerHTML = msgs.map(function(m){ return '<div class="seo-warning-item">' + m + '</div>'; }).join("");
        el.style.display = "";
      } else {
        el.style.display = "none";
      }
    }

    function update() {
      var tv  = (title ? title.value.trim() : "") || (pTitle ? pTitle.value.trim() : "");
      var dv  = desc.value.trim();
      var url = getPreviewUrl();

      // Google tab
      elTitle.textContent = tv || "Page Title";
      elDesc.textContent  = dv || "No meta description set \u2014 Google will auto-generate a snippet.";
      elUrl.textContent   = url;
      elOgUrl.textContent = url.replace("https://", "").replace(/\/$/, "");
      elTwUrl.textContent = url.replace("https://", "").replace(/\/$/, "");

      cntT.textContent = tv.length;
      cntT.className   = "seo-count " + countColor(tv.length, 60, 70);
      cntD.textContent = dv.length;
      cntD.className   = "seo-count " + countColor(dv.length, 140, 160);

      var gMsgs = [];
      if (tv.length > 60)  gMsgs.push("\u26A0\uFE0F Title exceeds 60 characters \u2014 may be truncated by Google.");
      if (tv.length > 0 && tv.length < 30) gMsgs.push("\u2139\uFE0F Title is very short \u2014 aim for 40\u201360 characters.");
      if (dv.length > 160) gMsgs.push("\u26A0\uFE0F Meta description exceeds 160 characters \u2014 will be truncated.");
      if (dv.length > 0 && dv.length < 80) gMsgs.push("\u2139\uFE0F Meta description is short \u2014 aim for 120\u2013160 characters.");
      if (dv.length === 0) gMsgs.push("\u2139\uFE0F Meta description is empty \u2014 Google will auto-generate one.");
      setWarns(warnsG, gMsgs);

      // OG tab
      var ogT = ogTitleEl(), ogD = ogDescEl();
      var ogTv = (ogT && ogT.value.trim()) || tv || "Page Title";
      var ogDv = (ogD && ogD.value.trim()) || dv || "No description set.";
      elOgTitle.textContent = ogTv;
      elOgDesc.textContent  = ogDv;
      cntOgT.textContent = ogT ? ogT.value.trim().length : 0;
      cntOgT.className   = "seo-count " + countColor(ogT ? ogT.value.trim().length : 0, 80, 100);
      cntOgD.textContent = ogD ? ogD.value.trim().length : 0;
      cntOgD.className   = "seo-count " + countColor(ogD ? ogD.value.trim().length : 0, 160, 200);
      var ogMsgs = [];
      if (ogT && ogT.value.trim().length > 100) ogMsgs.push("\u26A0\uFE0F OG title exceeds 100 characters.");
      if (ogD && ogD.value.trim().length > 200) ogMsgs.push("\u26A0\uFE0F OG description exceeds 200 characters.");
      setWarns(warnsOg, ogMsgs);

      // Twitter tab
      var twT = twTitleEl(), twD = twDescEl();
      var twTv = (twT && twT.value.trim()) || ogTv;
      var twDv = (twD && twD.value.trim()) || ogDv;
      elTwTitle.textContent = twTv;
      elTwDesc.textContent  = twDv;
      cntTwT.textContent = twT ? twT.value.trim().length : 0;
      cntTwT.className   = "seo-count " + countColor(twT ? twT.value.trim().length : 0, 80, 100);
      cntTwD.textContent = twD ? twD.value.trim().length : 0;
      cntTwD.className   = "seo-count " + countColor(twD ? twD.value.trim().length : 0, 160, 200);
      var twMsgs = [];
      if (twT && twT.value.trim().length > 100) twMsgs.push("\u26A0\uFE0F Twitter title exceeds 100 characters.");
      if (twD && twD.value.trim().length > 200) twMsgs.push("\u26A0\uFE0F Twitter description exceeds 200 characters.");
      setWarns(warnsTw, twMsgs);
    }

    [title, desc, slugEl(), pTitle, ogTitleEl(), ogDescEl(), twTitleEl(), twDescEl()].forEach(function(el) {
      if (el) el.addEventListener("input", update);
    });
    update();
  }

  // ── ALT text validation ─────────────────────────────────────────────────
  // Maps image field name substring → alt field name (or null if no dedicated alt field)
  var ALT_PAIRS = [
    ["featured_image", "featured_image_alt"],
    ["thumbnail",      "thumbnail_alt"],
    ["cover_image",    "cover_image_alt"],
    ["hero_image",     "hero_image_alt"],
    ["tier_250_image", "tier_250_image_alt"],
    ["tier_400_image", "tier_400_image_alt"],
    ["tier_800_image", "tier_800_image_alt"],
    ["image",          "image_alt"],
    [null,             "caption_en"],
  ];

  function findAltField(imageName) {
    for (var i = 0; i < ALT_PAIRS.length; i++) {
      var imgPattern = ALT_PAIRS[i][0];
      var altName    = ALT_PAIRS[i][1];
      if (imgPattern && imageName.indexOf(imgPattern) !== -1 && altName) {
        return findOne(["#id_" + altName, "input[name='" + altName + "']"]);
      }
    }
    return null;
  }

  function initAltWarnings() {
    $$(".form-row").forEach(function(row) {
      var fileEl = row.querySelector("input[type='file']");
      var existingLink = row.querySelector("a[href*='/media/']");
      if (!fileEl && !existingLink) return;

      // Determine image field name
      var name = "";
      if (fileEl) name = fileEl.name || "";
      if (!name) {
        var label = row.querySelector("label");
        if (label) name = (label.getAttribute("for") || "").replace("id_", "");
      }

      // Skip pure OG/Twitter images — they don't need user-facing alt text
      if (name === "og_image" || name === "twitter_image") return;

      var altInput = findAltField(name);
      if (!altInput) return;

      var hasImage = (fileEl && fileEl.value) || existingLink;
      if (hasImage) injectAltBadge(altInput);

      if (fileEl) {
        fileEl.addEventListener("change", function() {
          injectAltBadge(altInput);
        });
      }
    });

    // Inline rows (PropertyMedia etc.)
    $$(".inline-related, .dynamic-media-set").forEach(function(row) {
      var fileInput = row.querySelector("input[type='file']");
      var existingLink = row.querySelector("a[href*='/media/']");
      if (!fileInput && !existingLink) return;

      var altInput = row.querySelector(
        "input[name*='caption_en'], input[name*='alt_text'], input[name*='featured_image_alt']"
      );
      if (!altInput) return;

      var hasImage = (fileInput && fileInput.value) || existingLink;
      if (hasImage) injectAltBadge(altInput);

      if (fileInput) {
        fileInput.addEventListener("change", function() { injectAltBadge(altInput); });
      }
    });
  }

  function injectAltBadge(altInput) {
    var badge = altInput.parentElement.querySelector(".alt-warning-badge");
    if (!badge) {
      badge = document.createElement("span");
      badge.className = "alt-warning-badge";
      badge.textContent = "\u26A0\uFE0F ALT text required for SEO";
      altInput.insertAdjacentElement("afterend", badge);
    }
    function check() {
      badge.style.display = altInput.value.trim() ? "none" : "";
    }
    altInput.removeEventListener("input", check);
    altInput.addEventListener("input", check);
    check();
  }

  // ── H2 heading detection in CKEditor content ───────────────────────────
  function initH2Check() {
    var contentField = findOne([
      "#id_content", "#id_full_description", "#id_body",
      "textarea[name='content']", "textarea[name='full_description']",
    ]);
    if (!contentField) return;

    var banner = document.createElement("div");
    banner.className = "seo-h2-warning";
    banner.id = "seoH2Warning";
    banner.style.display = "none";
    banner.innerHTML = '\u26A0\uFE0F <strong>No H2 headings found</strong> \u2014 long articles should use H2 sections for better SEO.';

    var row = contentField.closest(".form-row") || contentField.closest("fieldset");
    if (row) row.insertAdjacentElement("afterend", banner);

    function checkContent() {
      var html = "";
      if (window.CKEDITOR && window.CKEDITOR.instances) {
        for (var k in window.CKEDITOR.instances) {
          var inst = window.CKEDITOR.instances[k];
          if (inst.element && (inst.element.$ === contentField || inst.element.getId() === contentField.id)) {
            html = inst.getData(); break;
          }
        }
      }
      if (!html) {
        var ckContainer = contentField.closest(".ck-editor");
        if (ckContainer) {
          var ckEditable = ckContainer.querySelector(".ck-content");
          if (ckEditable) html = ckEditable.innerHTML;
        }
      }
      if (!html) html = contentField.value || "";
      var text = html.replace(/<[^>]+>/g, " ").trim();
      var wordCount = text.split(/\s+/).filter(function(w){ return w.length > 0; }).length;
      banner.style.display = (wordCount >= 300 && !/<h2[\s>]/i.test(html)) ? "" : "none";
    }
    setInterval(checkContent, 3000);
    setTimeout(checkContent, 1500);
  }

  // ── Save-time validation banner (advisory only) ─────────────────────────
  function initSaveValidation() {
    var form = $("form#changelist-form") || $("form");
    if (!form || !form.querySelector("input[name='_save'], input[name='_continue']")) return;

    form.querySelectorAll("input[type='submit'], button[type='submit'], .submit-row input").forEach(function(btn) {
      btn.addEventListener("click", function() {
        var issues = collectIssues();
        if (issues.length === 0) return;
        var old = $("#seoSaveBanner");
        if (old) old.remove();
        var banner = document.createElement("div");
        banner.id = "seoSaveBanner";
        banner.className = "seo-save-banner";
        banner.innerHTML =
          '<div class="seo-save-banner-title">\u26A0\uFE0F SEO Warnings</div>' +
          '<div class="seo-save-banner-body">' +
            issues.map(function(i){ return '<div class="seo-save-banner-item">\u2022 ' + i + '</div>'; }).join("") +
          '</div>' +
          '<div class="seo-save-banner-hint">The form will still save \u2014 please fix these issues for better ranking.</div>';
        var submitRow = $(".submit-row");
        if (submitRow) submitRow.insertAdjacentElement("beforebegin", banner);
        else form.insertAdjacentElement("afterbegin", banner);
        banner.scrollIntoView({ behavior: "smooth", block: "center" });
      });
    });
  }

  function collectIssues() {
    var issues = [];
    var titleEl = seoTitleEl() || pageTitleEl();
    if (titleEl) {
      var tl = titleEl.value.trim().length;
      if (tl > 60) issues.push("Title is " + tl + " chars (max 60).");
    }
    var descEl = metaDescEl();
    if (descEl) {
      var dl = descEl.value.trim().length;
      if (dl > 160) issues.push("Meta description is " + dl + " chars (max 160).");
      if (dl === 0)  issues.push("Meta description is empty.");
    }
    var altBadges = $$(".alt-warning-badge");
    var missingAlt = altBadges.filter(function(b){ return b.style.display !== "none"; }).length;
    if (missingAlt === 1) issues.push("1 image is missing ALT text.");
    else if (missingAlt > 1) issues.push(missingAlt + " images are missing ALT text.");
    var h2warn = $("#seoH2Warning");
    if (h2warn && h2warn.style.display !== "none") {
      issues.push("Long article has no H2 headings \u2014 add section headings for SEO.");
    }
    return issues;
  }

  // ── init ────────────────────────────────────────────────────────────────
  function init() {
    initSERP();
    initAltWarnings();
    initH2Check();
    initSaveValidation();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
