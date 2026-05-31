(function () {
  "use strict";

  function getCookie(name) {
    var value = document.cookie || "";
    var parts = value.split(";").map(function (v) { return v.trim(); });
    for (var i = 0; i < parts.length; i++) {
      if (parts[i].slice(0, name.length + 1) === name + "=") {
        return decodeURIComponent(parts[i].slice(name.length + 1));
      }
    }
    return "";
  }

  var manager = document.querySelector("[data-fa-section-manager]");
  if (!manager) return;

  var saveButton = manager.querySelector("[data-fa-save-order]");
  var cards = Array.prototype.slice.call(manager.querySelectorAll(".fa-sec-card"));
  var dragging = null;

  function refreshCards() {
    cards = Array.prototype.slice.call(manager.querySelectorAll(".fa-sec-card"));
  }

  function markDirty(dirty) {
    if (!saveButton) return;
    saveButton.disabled = !dirty;
  }

  cards.forEach(function (card) {
    card.addEventListener("dragstart", function () {
      dragging = card;
      card.classList.add("is-dragging");
    });

    card.addEventListener("dragend", function () {
      card.classList.remove("is-dragging");
      dragging = null;
    });

    card.addEventListener("dragover", function (event) {
      event.preventDefault();
      if (!dragging || dragging === card) return;
      var bounds = card.getBoundingClientRect();
      var isAfter = event.clientY > bounds.top + bounds.height / 2;
      if (isAfter) {
        card.parentNode.insertBefore(dragging, card.nextSibling);
      } else {
        card.parentNode.insertBefore(dragging, card);
      }
      markDirty(true);
    });
  });

  if (!saveButton) return;

  saveButton.addEventListener("click", function () {
    refreshCards();
    var ids = cards
      .map(function (card) { return parseInt(card.getAttribute("data-section-id"), 10); })
      .filter(function (v) { return !isNaN(v); });

    saveButton.disabled = true;
    saveButton.textContent = "Saving...";

    fetch(manager.getAttribute("data-reorder-url"), {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken")
      },
      body: JSON.stringify({ ids: ids })
    })
      .then(function (res) {
        if (!res.ok) throw new Error("Save failed");
        return res.json();
      })
      .then(function (payload) {
        if (!payload.ok) throw new Error(payload.error || "Save failed");
        window.location.reload();
      })
      .catch(function () {
        saveButton.disabled = false;
        saveButton.textContent = "Save drag & drop order";
        window.alert("خطا در ذخیره ترتیب سکشن‌ها. دوباره تلاش کنید.");
      })
      .finally(function () {
        if (!saveButton.disabled) return;
        if (saveButton.textContent === "Saving...") {
          saveButton.textContent = "Save drag & drop order";
        }
      });
  });
})();
