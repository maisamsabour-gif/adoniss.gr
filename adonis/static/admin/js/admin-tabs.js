/**
 * Admin Tabs - Safe tabbed interface using CSS visibility only
 * Never removes elements from DOM - just shows/hides with CSS
 */
(function() {
    'use strict';

    const TAB_CONFIGS = {
        'properties_property': [
            { id: 'basic', label: 'Basic Info', icon: '📝', keywords: ['property details', 'physical details', 'feature badges'] },
            { id: 'location', label: 'Location', icon: '📍', keywords: ['public location', 'neighborhood', 'distances', 'area highlights'] },
            { id: 'pricing', label: 'Pricing', icon: '💰', keywords: ['pricing', 'golden visa', 'availability', 'timeline'] },
            { id: 'amenities', label: 'Amenities', icon: '🏠', keywords: ['amenities'] },
            { id: 'media', label: 'Media', icon: '📷', keywords: ['photos', 'videos'] },
            { id: 'units', label: 'Units', icon: '🏢', keywords: ['units overview'] },
            { id: 'settings', label: 'Settings', icon: '⚙️', keywords: ['visibility', 'whatsapp', 'map circle', 'private address'] },
            { id: 'seo', label: 'SEO', icon: '🔍', keywords: ['seo'] },
        ],
        'core_blogpost': [
            { id: 'content', label: 'Content', icon: '📝', keywords: ['basic information', 'content'] },
            { id: 'image', label: 'Image', icon: '🖼️', keywords: ['featured image'] },
            { id: 'seo', label: 'SEO', icon: '🔍', keywords: ['seo settings'] },
            { id: 'social', label: 'Social', icon: '📣', keywords: ['social', 'open graph'] },
            { id: 'publish', label: 'Publish', icon: '🚀', keywords: ['publishing', 'statistics'] },
        ],
        'core_goldenvisalandingpage': [
            { id: 'hero', label: 'Hero', icon: '🎯', keywords: ['hero'] },
            { id: 'content', label: 'Content', icon: '📝', keywords: ['intro text', 'content section'] },
            { id: 'tiers', label: 'Tiers', icon: '💰', keywords: ['investment tiers'] },
            { id: 'benefits', label: 'Benefits', icon: '✅', keywords: ['benefits', 'process steps'] },
            { id: 'videos', label: 'Videos', icon: '🎬', keywords: ['youtube'] },
            { id: 'faq', label: 'FAQ', icon: '❓', keywords: ['faq'] },
            { id: 'seo', label: 'SEO', icon: '🔍', keywords: ['seo', 'open graph', 'twitter'] },
            { id: 'publish', label: 'Publish', icon: '🚀', keywords: ['publishing'] },
        ],
        'core_event': [
            { id: 'basic', label: 'Basic', icon: '📌', keywords: ['basic info'] },
            { id: 'media', label: 'Media', icon: '🖼️', keywords: ['media'] },
            { id: 'details', label: 'Details', icon: '📅', keywords: ['event details'] },
            { id: 'settings', label: 'Settings', icon: '⚙️', keywords: ['display settings'] },
            { id: 'seo', label: 'SEO', icon: '🔍', keywords: ['seo'] },
        ],
    };

    function getModelKey() {
        const match = window.location.pathname.match(/\/admin\/([^\/]+)\/([^\/]+)\//);
        return match ? match[1] + '_' + match[2] : null;
    }

    function initTabs() {
        const modelKey = getModelKey();
        const config = TAB_CONFIGS[modelKey];
        if (!config) return;

        const form = document.querySelector('form');
        if (!form) return;

        // Get all fieldsets
        const fieldsets = form.querySelectorAll('fieldset');
        if (fieldsets.length < 3) return;

        // Create wrapper for original content
        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'admin-tabs-content';

        // Create tab nav
        const tabNav = document.createElement('div');
        tabNav.className = 'admin-tabs-nav';
        tabNav.innerHTML = '<style>' +
            '.admin-tabs-nav{display:flex;flex-wrap:wrap;gap:8px;padding:16px 20px;background:linear-gradient(135deg,#1e293b,#334155);border-radius:12px;margin:0 0 20px 0;position:sticky;top:60px;z-index:100;box-shadow:0 4px 12px rgba(0,0,0,0.2);}' +
            '.admin-tab-btn{display:inline-flex;align-items:center;gap:6px;padding:10px 16px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);border-radius:8px;color:rgba(255,255,255,0.8);font-size:13px;font-weight:600;cursor:pointer;transition:all 0.2s;}' +
            '.admin-tab-btn:hover{background:rgba(255,255,255,0.15);color:#fff;}' +
            '.admin-tab-btn.active{background:linear-gradient(135deg,#3b82f6,#1d4ed8);color:#fff;border-color:#3b82f6;box-shadow:0 4px 12px rgba(59,130,246,0.4);}' +
            '.admin-tab-btn .tab-icon{font-size:15px;}' +
            '.fieldset-hidden{display:none !important;}' +
            '.inline-hidden{display:none !important;}' +
            '</style>';

        // Add "All" tab first
        const allBtn = document.createElement('button');
        allBtn.type = 'button';
        allBtn.className = 'admin-tab-btn active';
        allBtn.dataset.tab = 'all';
        allBtn.innerHTML = '<span class="tab-icon">📋</span> All';
        tabNav.appendChild(allBtn);

        // Add configured tabs
        config.forEach(tab => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'admin-tab-btn';
            btn.dataset.tab = tab.id;
            btn.dataset.keywords = tab.keywords.join('|');
            btn.innerHTML = `<span class="tab-icon">${tab.icon}</span> ${tab.label}`;
            tabNav.appendChild(btn);
        });

        // Insert tab nav before first fieldset
        const firstFieldset = form.querySelector('fieldset');
        if (firstFieldset) {
            firstFieldset.parentNode.insertBefore(tabNav, firstFieldset);
        }

        // Tab click handler
        tabNav.addEventListener('click', function(e) {
            const btn = e.target.closest('.admin-tab-btn');
            if (!btn) return;

            const tabId = btn.dataset.tab;
            const keywords = btn.dataset.keywords ? btn.dataset.keywords.split('|') : [];

            // Update active state
            tabNav.querySelectorAll('.admin-tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Show/hide fieldsets
            fieldsets.forEach(fs => {
                const h2 = fs.querySelector('h2');
                const title = h2 ? h2.textContent.toLowerCase() : '';

                if (tabId === 'all') {
                    fs.classList.remove('fieldset-hidden');
                } else {
                    const matches = keywords.some(kw => title.includes(kw.toLowerCase()));
                    fs.classList.toggle('fieldset-hidden', !matches);
                }
            });

            // Show/hide inlines
            const inlines = form.querySelectorAll('.inline-group');
            inlines.forEach(inline => {
                const h2 = inline.querySelector('h2');
                const title = h2 ? h2.textContent.toLowerCase() : '';

                if (tabId === 'all') {
                    inline.classList.remove('inline-hidden');
                } else if (tabId === 'media') {
                    const isMedia = title.includes('photo') || title.includes('video') || title.includes('media');
                    inline.classList.toggle('inline-hidden', !isMedia);
                } else if (tabId === 'units') {
                    const isUnit = title.includes('unit');
                    inline.classList.toggle('inline-hidden', !isUnit);
                } else {
                    inline.classList.add('inline-hidden');
                }
            });

            // Scroll to top
            tabNav.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    }

    // Run after DOM ready with small delay for other scripts
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => setTimeout(initTabs, 200));
    } else {
        setTimeout(initTabs, 200);
    }
})();
