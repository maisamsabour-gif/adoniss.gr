(function () {
  "use strict";

  /*
   * CKEditor 5 — helper for Unfold + Alpine.js admin.
   *
   * 1. Sets window.CKEDITOR_GLOBAL_LICENSE_KEY so bundle.js can init properly.
   * 2. Polls until all editors are ready, then force-resizes them.
   * 3. If bundle.js fails, retries initialization ourselves.
   */

  window.CKEDITOR_GLOBAL_LICENSE_KEY = "GPL";

  var MAX_RETRIES = 50;
  var RETRY_INTERVAL = 500;

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      var cookies = document.cookie.split(";");
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function getCSRFToken(cookieName) {
    var token = getCookie(cookieName);
    if (!token) {
      var input = document.querySelector("input[name=csrfmiddlewaretoken]");
      if (input) token = input.value;
    }
    return token;
  }

  function forceResizeAll() {
    var eds = window.editors || {};
    Object.keys(eds).forEach(function (id) {
      var editor = eds[id];
      if (!editor || !editor.editing) return;
      try { editor.editing.view.forceRender(); } catch (_) {}
      var editable = editor.editing.view.getDomRoot();
      if (editable) {
        editable.style.minHeight = "560px";
        editable.style.height = "auto";
      }
    });

    document.querySelectorAll(".ck.ck-editor__editable_inline").forEach(function (el) {
      if (el.getAttribute("contenteditable") === "true") {
        el.style.minHeight = "560px";
        el.style.height = "auto";
      }
    });
  }

  function readEditorConfig(textareaId) {
    var scriptId = textareaId + "_script";
    var configScript = document.getElementById(scriptId);
    var uploadInput = document.getElementById(scriptId + "-ck-editor-5-upload-url");

    if (!configScript || !uploadInput) {
      var span = document.getElementById(scriptId + "-span");
      if (!span) return null;
      configScript = span.querySelector('script[type="application/json"]');
      if (!configScript) return null;
    }

    try {
      var config = JSON.parse(configScript.textContent, function (key, value) {
        if (typeof value === "string") {
          var match = value.match(new RegExp("^/(.*?)/([gimy]*)$"));
          if (match) return new RegExp(match[1], match[2]);
          if (value.startsWith("callback:")) {
            var fn = window[value.substring(9)];
            if (typeof fn === "function") return fn;
          }
        }
        return value;
      });

      var uploadUrl = uploadInput.getAttribute("data-upload-url");
      var fileTypes = JSON.parse(uploadInput.getAttribute("data-upload-file-types") || "[]");
      var csrfCookieName = uploadInput.getAttribute("data-csrf_cookie_name") || "csrftoken";

      config.simpleUpload = {
        uploadUrl: uploadUrl,
        headers: { "X-CSRFToken": getCSRFToken(csrfCookieName) },
      };
      config.fileUploader = { fileTypes: fileTypes };
      config.licenseKey = "GPL";
      return config;
    } catch (e) {
      return null;
    }
  }

  function initEditor(textarea) {
    if (!window.ClassicEditor) return;
    var config = readEditorConfig(textarea.id);
    if (!config) return;

    textarea.setAttribute("data-processed", "1");

    window.ClassicEditor.create(textarea, config)
      .then(function (editor) {
        editor.model.document.on("change:data", function () {
          var ta = document.getElementById(textarea.id);
          if (ta) ta.value = editor.getData();
        });
        if (!window.editors) window.editors = {};
        window.editors[textarea.id] = editor;
        setTimeout(function () {
          try { editor.editing.view.forceRender(); } catch (_) {}
        }, 150);
      })
      .catch(function (err) {
        console.error("[richtext_init] create failed for", textarea.id, err);
        textarea.removeAttribute("data-processed");
      });
  }

  function initMissingEditors() {
    if (!window.ClassicEditor) return 0;
    var textareas = document.querySelectorAll("textarea.django_ckeditor_5");
    var eds = window.editors || {};
    var attempted = 0;

    textareas.forEach(function (ta) {
      if (ta.id.indexOf("__prefix__") !== -1) return;
      if (eds[ta.id]) return;

      var container = ta.closest(".ck-editor-container");
      if (container && container.querySelector(".ck.ck-editor")) return;

      var isProcessed = ta.getAttribute("data-processed") === "1";
      if (isProcessed) {
        ta.removeAttribute("data-processed");
      }
      attempted++;
      initEditor(ta);
    });
    return attempted;
  }

  function poll(attempt) {
    if (attempt >= MAX_RETRIES) return;

    var textareas = document.querySelectorAll("textarea.django_ckeditor_5");
    if (textareas.length === 0) return;

    var eds = window.editors || {};
    var initialized = 0;
    var total = 0;
    textareas.forEach(function (ta) {
      if (ta.id.indexOf("__prefix__") === -1) {
        total++;
        if (eds[ta.id]) initialized++;
      }
    });

    if (initialized >= total && total > 0) {
      forceResizeAll();
      setTimeout(forceResizeAll, 500);
      return;
    }

    if (attempt > 3) {
      initMissingEditors();
    }

    setTimeout(function () { poll(attempt + 1); }, RETRY_INTERVAL);
  }

  function ensureTextareasFallback() {
    var tas = document.querySelectorAll("textarea.django_ckeditor_5");
    var eds = window.editors || {};
    tas.forEach(function (ta) {
      if (ta.id.indexOf("__prefix__") !== -1) return;
      if (eds[ta.id]) return;
      var container = ta.closest(".ck-editor-container");
      if (container && container.querySelector(".ck.ck-editor")) return;
      ta.style.display = "block";
      ta.style.width = "100%";
      ta.style.minHeight = "500px";
      ta.style.fontSize = "14px";
      ta.style.lineHeight = "1.7";
      ta.style.padding = "16px";
      ta.style.borderRadius = "8px";
      ta.style.border = "2px solid #e2e8f0";
    });
  }

  function start() {
    setTimeout(function () { poll(0); }, 600);
    setTimeout(ensureTextareasFallback, 12000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }

  document.addEventListener("alpine:initialized", function () {
    setTimeout(function () {
      initMissingEditors();
      setTimeout(forceResizeAll, 300);
      setTimeout(forceResizeAll, 800);
    }, 200);
  });

  window.addEventListener("load", function () {
    setTimeout(function () {
      initMissingEditors();
      forceResizeAll();
      setTimeout(forceResizeAll, 500);
      setTimeout(forceResizeAll, 2000);
    }, 400);
  });

})();
