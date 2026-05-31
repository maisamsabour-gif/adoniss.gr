/* ══════════════════════════════════════════════════════════════════════════
 *  ADONIS — FA admin enhancer
 *  - Pairs opacity / intensity / percent numeric inputs with a live slider
 *  - Adds .fa-img-field fallback class to file-input field-lines
 *  - Live preview update on file selection
 * ══════════════════════════════════════════════════════════════════════════ */

(function () {
    "use strict";

    var SLIDER_NAME_PATTERNS = [
        /opacity/i,
        /intensity/i,
        /_percent$/i,
        /brightness/i,
        /blur/i,
    ];

    function shouldGetSlider(input) {
        if (input.type !== "number") return false;
        var name = input.name || "";
        var min = parseFloat(input.min);
        var max = parseFloat(input.max);
        if (isNaN(min) || isNaN(max)) return false;
        if (max - min > 200) return false;
        return SLIDER_NAME_PATTERNS.some(function (re) {
            return re.test(name);
        });
    }

    function enhanceOpacityField(input) {
        if (input.dataset.faSliderEnhanced) return;
        input.dataset.faSliderEnhanced = "1";

        var min = parseFloat(input.min) || 0;
        var max = parseFloat(input.max) || 100;
        var step = parseFloat(input.step) || 1;
        var value = parseFloat(input.value);
        if (isNaN(value)) value = (min + max) / 2;

        // Create wrapper row
        var row = document.createElement("div");
        row.className = "fa-slider-row";

        // Range slider
        var slider = document.createElement("input");
        slider.type = "range";
        slider.min = min;
        slider.max = max;
        slider.step = step;
        slider.value = value;
        slider.className = "fa-num-slider";

        // Suffix label
        var suffix = document.createElement("span");
        suffix.className = "fa-num-suffix";
        suffix.textContent = "%";

        // Move input into the row, then prepend slider
        input.classList.add("fa-num-display");
        var parent = input.parentNode;
        parent.insertBefore(row, input);
        row.appendChild(slider);
        row.appendChild(input);
        row.appendChild(suffix);

        function syncSliderVisual(val) {
            var pct = ((val - min) / (max - min)) * 100;
            slider.style.setProperty("--fa-slider-val", pct + "%");
        }
        syncSliderVisual(value);

        slider.addEventListener("input", function () {
            input.value = slider.value;
            syncSliderVisual(slider.value);
            input.dispatchEvent(new Event("input", { bubbles: true }));
        });

        input.addEventListener("input", function () {
            var v = parseFloat(input.value);
            if (!isNaN(v)) {
                slider.value = v;
                syncSliderVisual(v);
            }
        });
    }

    function enhanceFileFields() {
        var inputs = document.querySelectorAll("#content-main input[type='file']");
        inputs.forEach(function (input) {
            // Climb up to the .field-line container
            var fieldLine = input.closest(".field-line, .form-row, .form-group");
            if (fieldLine && !fieldLine.classList.contains("fa-img-field")) {
                fieldLine.classList.add("fa-img-field");
            }

            // Live filename hint when user picks a file (no upload yet)
            if (!input.dataset.faFileBound) {
                input.dataset.faFileBound = "1";
                input.addEventListener("change", function () {
                    if (input.files && input.files[0]) {
                        var name = input.files[0].name;
                        // Find a visible text input inside the wrapper to update
                        var wrapper = input.closest(".field-line, .form-row, .form-group");
                        if (!wrapper) return;
                        var disp = wrapper.querySelector('input[type="text"][disabled]');
                        if (disp) {
                            disp.value = "✓ " + name;
                            disp.style.color = "#16a34a";
                            disp.style.fontWeight = "600";
                        }

                        // Live thumbnail preview for image files
                        if (input.files[0].type.startsWith("image/")) {
                            var reader = new FileReader();
                            reader.onload = function (e) {
                                var existingPreview = wrapper.querySelector(".mb-4.max-w-48");
                                if (existingPreview) {
                                    var img = existingPreview.querySelector("img");
                                    if (img) img.src = e.target.result;
                                } else {
                                    var preview = document.createElement("div");
                                    preview.className = "mb-4 max-w-48";
                                    preview.innerHTML =
                                        '<img src="' + e.target.result + '" alt="پیش‌نمایش" class="block rounded-default" />';
                                    wrapper.insertBefore(preview, wrapper.firstChild);
                                }
                            };
                            reader.readAsDataURL(input.files[0]);
                        }
                    }
                });
            }
        });
    }

    function enhanceNumericFields() {
        var inputs = document.querySelectorAll("#content-main input[type='number']");
        inputs.forEach(function (input) {
            if (shouldGetSlider(input)) {
                enhanceOpacityField(input);
            }
        });
    }

    function init() {
        try {
            enhanceFileFields();
            enhanceNumericFields();
        } catch (err) {
            // Never break the admin page
            console.warn("[fa-admin-enhancer] init failed:", err);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
