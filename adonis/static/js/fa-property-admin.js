/**
 * FA Property Admin — Enhanced UX for Luxury Real Estate Management
 * پنل ادمین حرفه‌ای املاک فارسی
 */

(function() {
    'use strict';

    // Wait for DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        initImagePreviews();
        initCharacterCounters();
        initSeoPreview();
        initAmenityHelper();
        initCollapsibleSections();
    });

    /**
     * Initialize image preview on file select
     */
    function initImagePreviews() {
        for (let i = 1; i <= 15; i++) {
            const input = document.getElementById(`id_image_${i}`);
            if (input) {
                input.addEventListener('change', function(e) {
                    previewImage(e.target, i);
                });
            }
        }
    }

    /**
     * Preview image before upload
     */
    function previewImage(input, index) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                // Find or create preview container
                let preview = input.parentElement.querySelector('.image-preview');
                if (!preview) {
                    preview = document.createElement('div');
                    preview.className = 'image-preview';
                    preview.style.cssText = 'margin-top:10px;';
                    input.parentElement.appendChild(preview);
                }
                
                preview.innerHTML = `
                    <img src="${e.target.result}" 
                         style="max-height:150px;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.15);"
                         alt="پیش‌نمایش عکس ${index}">
                    <p style="color:#059669;font-size:12px;margin-top:5px;">
                        ✓ عکس آماده آپلود
                    </p>
                `;
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    /**
     * Add character counters to SEO fields
     */
    function initCharacterCounters() {
        const seoFields = [
            { id: 'id_meta_title', max: 70 },
            { id: 'id_meta_description', max: 160 },
            { id: 'id_focus_keyword', max: 100 },
            { id: 'id_tagline', max: 300 },
            { id: 'id_short_description', max: 500 }
        ];

        seoFields.forEach(function(field) {
            const input = document.getElementById(field.id);
            if (input) {
                addCharCounter(input, field.max);
            }
        });
    }

    /**
     * Add character counter to a field
     */
    function addCharCounter(input, maxChars) {
        const counter = document.createElement('div');
        counter.className = 'char-counter';
        counter.style.cssText = 'font-size:11px;color:#6b7280;margin-top:4px;text-align:left;direction:ltr;';
        
        function updateCounter() {
            const length = input.value.length;
            const remaining = maxChars - length;
            
            if (remaining < 0) {
                counter.style.color = '#dc2626';
                counter.innerHTML = `<strong>${length}</strong> / ${maxChars} (${Math.abs(remaining)} کاراکتر اضافی ⚠️)`;
            } else if (remaining < 20) {
                counter.style.color = '#d97706';
                counter.innerHTML = `<strong>${length}</strong> / ${maxChars} (${remaining} کاراکتر باقی‌مانده)`;
            } else {
                counter.style.color = '#059669';
                counter.innerHTML = `<strong>${length}</strong> / ${maxChars}`;
            }
        }

        input.addEventListener('input', updateCounter);
        input.parentElement.appendChild(counter);
        updateCounter();
    }

    /**
     * Live SEO preview
     */
    function initSeoPreview() {
        const titleInput = document.getElementById('id_meta_title');
        const descInput = document.getElementById('id_meta_description');
        const nameInput = document.getElementById('id_name');

        if (!titleInput || !descInput) return;

        // Create preview container
        const fieldset = titleInput.closest('fieldset');
        if (!fieldset) return;

        const previewContainer = document.createElement('div');
        previewContainer.id = 'seo-preview';
        previewContainer.style.cssText = `
            background: #fff;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            direction: ltr;
            text-align: left;
        `;
        previewContainer.innerHTML = `
            <div style="color:#6b7280;font-size:11px;margin-bottom:10px;text-align:right;direction:rtl;">
                👁️ پیش‌نمایش نتیجه گوگل:
            </div>
            <div id="seo-preview-title" style="color:#1a0dab;font-size:18px;font-weight:normal;margin-bottom:4px;cursor:pointer;">
                عنوان صفحه
            </div>
            <div id="seo-preview-url" style="color:#006621;font-size:14px;margin-bottom:4px;">
                adonisgreece.com › fa-new › properties › ...
            </div>
            <div id="seo-preview-desc" style="color:#545454;font-size:13px;line-height:1.5;">
                توضیحات صفحه...
            </div>
        `;

        fieldset.insertBefore(previewContainer, fieldset.querySelector('.form-row'));

        function updatePreview() {
            const title = titleInput.value || nameInput?.value || 'عنوان پروژه';
            const desc = descInput.value || 'توضیحات پروژه در نتایج گوگل نمایش داده می‌شود...';
            
            document.getElementById('seo-preview-title').textContent = title;
            document.getElementById('seo-preview-desc').textContent = desc;
        }

        [titleInput, descInput, nameInput].forEach(function(input) {
            if (input) {
                input.addEventListener('input', updatePreview);
            }
        });

        updatePreview();
    }

    /**
     * Amenity input helper
     */
    function initAmenityHelper() {
        const amenitiesInput = document.getElementById('id_amenities');
        if (!amenitiesInput) return;

        const suggestions = [
            '🏊 استخر',
            '🧖 سونا و جکوزی',
            '🏋️ باشگاه ورزشی',
            '🛗 آسانسور',
            '🔒 امنیت ۲۴/۷',
            '🅿️ پارکینگ خصوصی',
            '🌅 ویو دریا',
            '🏔️ ویو کوهستان',
            '🌳 باغ اختصاصی',
            '☀️ تراس روف‌تاپ',
            '❄️ سیستم سرمایش',
            '🔥 شومینه',
            '🍳 آشپزخانه مدرن',
            '🛁 حمام مستر',
            '👔 اتاق لباس',
            '🏠 انباری',
            '📡 اینترنت پرسرعت',
            '🎬 سینمای خانگی'
        ];

        const helperDiv = document.createElement('div');
        helperDiv.style.cssText = 'margin-top:10px;';
        helperDiv.innerHTML = `
            <div style="color:#6b7280;font-size:12px;margin-bottom:8px;">
                💡 پیشنهادات (کلیک کنید تا اضافه شود):
            </div>
            <div id="amenity-suggestions" style="display:flex;flex-wrap:wrap;gap:6px;"></div>
        `;

        amenitiesInput.parentElement.appendChild(helperDiv);

        const suggestionsContainer = document.getElementById('amenity-suggestions');
        suggestions.forEach(function(suggestion) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = suggestion;
            btn.style.cssText = `
                background: #f3f4f6;
                border: 1px solid #e5e7eb;
                padding: 4px 10px;
                border-radius: 16px;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.2s ease;
            `;
            btn.onmouseover = function() {
                this.style.background = '#c9a227';
                this.style.color = '#1a1a2e';
                this.style.borderColor = '#c9a227';
            };
            btn.onmouseout = function() {
                this.style.background = '#f3f4f6';
                this.style.color = '#374151';
                this.style.borderColor = '#e5e7eb';
            };
            btn.onclick = function() {
                if (amenitiesInput.value && !amenitiesInput.value.endsWith('\n')) {
                    amenitiesInput.value += '\n';
                }
                amenitiesInput.value += suggestion;
                amenitiesInput.focus();
            };
            suggestionsContainer.appendChild(btn);
        });
    }

    /**
     * Enhanced collapsible sections
     */
    function initCollapsibleSections() {
        const collapsibles = document.querySelectorAll('fieldset.collapse');
        
        collapsibles.forEach(function(fieldset) {
            const header = fieldset.querySelector('h2');
            if (header) {
                header.style.cursor = 'pointer';
                header.addEventListener('click', function() {
                    fieldset.classList.toggle('collapsed');
                });
            }
        });
    }

})();
