/**
 * Persian Admin Enhancements
 * تنظیمات فارسی پنل ادمین
 */

(function() {
    'use strict';

    /**
     * Translate search placeholders to Persian
     */
    function translatePlaceholders() {
        // Search field
        const searchInputs = document.querySelectorAll(
            '#searchbar, input[type="search"], input[name="q"], .search-input'
        );
        
        searchInputs.forEach(input => {
            if (input.placeholder === 'Type to search' || 
                input.placeholder === 'Search' ||
                input.placeholder === '' ||
                input.placeholder.toLowerCase().includes('search')) {
                input.placeholder = 'جستجو کنید...';
            }
        });
        
        // Search button
        const searchButtons = document.querySelectorAll(
            'input[type="submit"][value="Search"], input[type="submit"][value="Go"]'
        );
        
        searchButtons.forEach(btn => {
            if (btn.value === 'Search' || btn.value === 'Go') {
                btn.value = 'جستجو';
            }
        });
        
        // Filter title
        const filterHeaders = document.querySelectorAll('#changelist-filter h2, .filter-title');
        filterHeaders.forEach(h => {
            if (h.textContent.trim() === 'Filter') {
                h.textContent = 'فیلتر';
            }
        });
        
        // "All" in filters
        document.querySelectorAll('#changelist-filter a').forEach(a => {
            if (a.textContent.trim() === 'All') {
                a.textContent = 'همه';
            }
        });
        
        // Action dropdown
        const actionLabel = document.querySelector('label[for="action-toggle"]');
        if (actionLabel && actionLabel.textContent.includes('Select all')) {
            actionLabel.textContent = 'انتخاب همه';
        }
        
        // Go button for actions
        const goButtons = document.querySelectorAll('button[title="Run the selected action"]');
        goButtons.forEach(btn => {
            if (btn.textContent.trim() === 'Go') {
                btn.textContent = 'اجرا';
            }
        });
    }

    /**
     * Add RTL direction to specific elements
     */
    function applyRTL() {
        const rtlSelectors = [
            '#content-main',
            '.form-row',
            '.field-box',
            'fieldset',
            '.help',
            '.helptext',
            'label',
            '.readonly'
        ];
        
        rtlSelectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
                if (!el.classList.contains('ltr-field')) {
                    el.style.direction = 'rtl';
                    el.style.textAlign = 'right';
                }
            });
        });
    }

    /**
     * Initialize
     */
    function init() {
        translatePlaceholders();
        applyRTL();
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Re-run after dynamic content loads
    setTimeout(init, 500);
    setTimeout(init, 1500);

    // Watch for dynamic content
    const observer = new MutationObserver(() => {
        setTimeout(translatePlaceholders, 100);
    });

    if (document.body) {
        observer.observe(document.body, { childList: true, subtree: true });
    }

})();
