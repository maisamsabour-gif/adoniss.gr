/**
 * Golden Visa Admin Page Builder
 * جاوااسکریپت صفحه‌ساز ادمین گلدن ویزا
 */

(function() {
    'use strict';
    
    document.addEventListener('DOMContentLoaded', function() {
        initPageBuilder();
    });
    
    function initPageBuilder() {
        // Only run on Golden Visa Landing Page admin
        if (!document.body.classList.contains('model-goldenvisalandingpage')) {
            return;
        }
        
        // Initialize collapsible sections
        initCollapsibleSections();
        
        // Initialize image previews
        initImagePreviews();
        
        // Initialize save button labels
        initSaveButtons();
        
        // Initialize section counts
        initSectionCounts();
    }
    
    /**
     * Make inline sections collapsible with smooth animation
     */
    function initCollapsibleSections() {
        const inlineGroups = document.querySelectorAll('.inline-group');
        
        inlineGroups.forEach(function(group) {
            const header = group.querySelector('h2');
            if (!header) return;
            
            // Add click handler
            header.addEventListener('click', function(e) {
                if (e.target.tagName === 'A') return;
                
                const fieldset = group.querySelector('fieldset, .tabular, .stacked');
                if (!fieldset) return;
                
                if (group.classList.contains('collapsed')) {
                    group.classList.remove('collapsed');
                    fieldset.style.display = '';
                } else {
                    group.classList.add('collapsed');
                    fieldset.style.display = 'none';
                }
            });
            
            // Initially collapse all sections except main settings
            if (group.classList.contains('collapse')) {
                group.classList.add('collapsed');
                const fieldset = group.querySelector('fieldset, .tabular, .stacked');
                if (fieldset) {
                    fieldset.style.display = 'none';
                }
            }
        });
    }
    
    /**
     * Initialize image previews for file inputs
     */
    function initImagePreviews() {
        const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
        
        imageInputs.forEach(function(input) {
            input.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (!file) return;
                
                // Check if it's an image
                if (!file.type.startsWith('image/')) return;
                
                // Create preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    let preview = input.parentNode.querySelector('.gv-image-preview');
                    
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.className = 'gv-image-preview';
                        preview.style.cssText = 'max-width:200px;max-height:120px;margin-top:8px;border-radius:8px;border:2px solid #e5e7eb;display:block;';
                        input.parentNode.appendChild(preview);
                    }
                    
                    preview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            });
        });
    }
    
    /**
     * Initialize Persian labels for save buttons
     */
    function initSaveButtons() {
        const saveBtn = document.querySelector('input[name="_save"]');
        const continueBtn = document.querySelector('input[name="_continue"]');
        const addAnotherBtn = document.querySelector('input[name="_addanother"]');
        
        if (saveBtn) {
            saveBtn.value = 'ذخیره';
        }
        if (continueBtn) {
            continueBtn.value = 'ذخیره و ادامه ویرایش';
        }
        if (addAnotherBtn) {
            addAnotherBtn.value = 'ذخیره و افزودن جدید';
        }
    }
    
    /**
     * Add item counts to section headers
     */
    function initSectionCounts() {
        const inlineGroups = document.querySelectorAll('.inline-group');
        
        inlineGroups.forEach(function(group) {
            const header = group.querySelector('h2');
            const items = group.querySelectorAll('.inline-related:not(.empty-form)');
            const count = items.length;
            
            if (header && count > 0) {
                const badge = document.createElement('span');
                badge.className = 'gv-count-badge';
                badge.textContent = count;
                header.appendChild(badge);
            }
        });
    }
    
})();
