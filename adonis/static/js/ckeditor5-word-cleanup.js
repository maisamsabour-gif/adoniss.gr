/**
 * CKEditor5 Word Content Cleanup - Fixes fragmented Word paste
 * 
 * Problem: When pasting from Word, text gets fragmented into separate lines
 * Solution: This script merges fragmented paragraphs and cleans Word formatting
 */

(function() {
    'use strict';

    /**
     * Clean and merge fragmented Word content
     */
    function cleanWordContent(html) {
        if (!html) return '';
        
        // Create temp container
        const temp = document.createElement('div');
        temp.innerHTML = html;
        
        // Remove Word-specific elements
        temp.querySelectorAll('style, xml, meta, link, title, script, o\\:p').forEach(el => el.remove());
        
        // Remove comments
        const walker = document.createTreeWalker(temp, NodeFilter.SHOW_COMMENT, null, false);
        const comments = [];
        while (walker.nextNode()) comments.push(walker.currentNode);
        comments.forEach(c => c.parentNode && c.parentNode.removeChild(c));
        
        // Unwrap all spans and fonts - keep their text content
        let spans = temp.querySelectorAll('span, font');
        while (spans.length > 0) {
            spans.forEach(span => {
                while (span.firstChild) {
                    span.parentNode.insertBefore(span.firstChild, span);
                }
                span.parentNode.removeChild(span);
            });
            spans = temp.querySelectorAll('span, font');
        }
        
        // Remove namespace elements (o:p, w:sdt, etc)
        temp.querySelectorAll('*').forEach(el => {
            if (el.tagName && el.tagName.includes(':')) {
                const text = el.textContent;
                if (text && text.trim()) {
                    el.replaceWith(document.createTextNode(text));
                } else {
                    el.remove();
                }
            }
        });
        
        // Clean all attributes from elements
        temp.querySelectorAll('*').forEach(el => {
            // Keep href on links
            const href = el.tagName === 'A' ? el.getAttribute('href') : null;
            // Remove all attributes
            while (el.attributes.length > 0) {
                el.removeAttribute(el.attributes[0].name);
            }
            // Restore href if it was a link
            if (href) el.setAttribute('href', href);
        });
        
        // Get HTML and do regex cleanup
        let cleaned = temp.innerHTML;
        
        // Remove empty tags
        cleaned = cleaned
            .replace(/<p[^>]*>\s*<\/p>/gi, '')
            .replace(/<p[^>]*>\s*&nbsp;\s*<\/p>/gi, '')
            .replace(/<div[^>]*>\s*<\/div>/gi, '')
            .replace(/<!--[\s\S]*?-->/gi, '')
            .replace(/&nbsp;/gi, ' ');
        
        // Merge consecutive short paragraphs that are likely one sentence
        // This is the key fix for fragmented Word paste
        temp.innerHTML = cleaned;
        mergeFragmentedParagraphs(temp);
        
        return temp.innerHTML.trim();
    }
    
    /**
     * Merge paragraphs that were incorrectly split by Word
     * Word often creates a new <p> for each line, breaking sentences
     */
    function mergeFragmentedParagraphs(container) {
        const paragraphs = Array.from(container.querySelectorAll('p'));
        
        for (let i = 0; i < paragraphs.length - 1; i++) {
            const current = paragraphs[i];
            const next = paragraphs[i + 1];
            
            if (!current || !next || !current.parentNode || !next.parentNode) continue;
            
            const currentText = current.textContent.trim();
            const nextText = next.textContent.trim();
            
            // Skip empty paragraphs
            if (!currentText || !nextText) continue;
            
            // Check if these should be merged:
            // 1. Current doesn't end with sentence-ending punctuation
            // 2. Next doesn't start with a capital letter or number (for Persian, check other indicators)
            // 3. Current is short (likely a fragment)
            
            const endsWithPunctuation = /[.!?؟،:;]$/.test(currentText);
            const isCurrentShort = currentText.length < 100;
            const startsWithContinuation = /^[a-zا-ی]/.test(nextText); // lowercase or Persian
            
            // Merge if current doesn't end sentence and next looks like continuation
            if (!endsWithPunctuation && isCurrentShort) {
                // Append next content to current
                current.innerHTML = current.innerHTML.trim() + ' ' + next.innerHTML.trim();
                next.remove();
                // Don't increment i, check the merged paragraph again
                i--;
            }
        }
        
        // Also handle divs that should be paragraphs
        container.querySelectorAll('div').forEach(div => {
            if (div.textContent.trim()) {
                const p = document.createElement('p');
                p.innerHTML = div.innerHTML;
                div.replaceWith(p);
            } else {
                div.remove();
            }
        });
    }
    
    /**
     * Clean all CKEditor instances on the page
     */
    window.cleanAllEditors = function() {
        const editables = document.querySelectorAll('.ck-editor__editable');
        let cleanedCount = 0;
        
        editables.forEach(editable => {
            const original = editable.innerHTML;
            const cleaned = cleanWordContent(original);
            
            if (original !== cleaned) {
                // Use CKEditor's data API if available for proper undo support
                const wrapper = editable.closest('.ck-editor');
                if (wrapper && wrapper.ckeditorInstance) {
                    try {
                        wrapper.ckeditorInstance.setData(cleaned);
                        cleanedCount++;
                        return;
                    } catch (e) {
                        console.log('CKEditor setData failed, using innerHTML');
                    }
                }
                
                editable.innerHTML = cleaned;
                editable.dispatchEvent(new Event('input', { bubbles: true }));
                cleanedCount++;
            }
        });
        
        return cleanedCount;
    };
    
    /**
     * Add the cleanup button
     */
    function addCleanupButton() {
        if (!document.querySelector('.ck-editor')) return;
        if (document.querySelector('#word-cleanup-btn')) return;
        
        const container = document.createElement('div');
        container.style.cssText = 'position: fixed; bottom: 20px; left: 20px; z-index: 9999;';
        
        const btn = document.createElement('button');
        btn.id = 'word-cleanup-btn';
        btn.type = 'button';
        btn.innerHTML = '🧹 اصلاح متن Word';
        btn.title = 'بعد از paste کردن متن از Word، این دکمه را بزنید';
        btn.style.cssText = `
            background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
            color: white;
            border: none;
            padding: 14px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-family: 'Vazirmatn', Tahoma, sans-serif;
            font-size: 15px;
            font-weight: 700;
            box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
            transition: all 0.2s ease;
            direction: rtl;
        `;
        btn.onmouseover = function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 6px 16px rgba(220, 38, 38, 0.5)';
        };
        btn.onmouseout = function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 12px rgba(220, 38, 38, 0.4)';
        };
        btn.onclick = function() {
            const count = window.cleanAllEditors();
            const originalText = this.innerHTML;
            const originalBg = this.style.background;
            
            if (count > 0) {
                this.innerHTML = '✓ اصلاح شد!';
                this.style.background = 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)';
            } else {
                this.innerHTML = '✓ نیازی به اصلاح نبود';
                this.style.background = 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)';
            }
            
            setTimeout(() => {
                this.innerHTML = originalText;
                this.style.background = originalBg;
            }, 2500);
        };
        
        container.appendChild(btn);
        document.body.appendChild(container);
    }
    
    // Initialize
    function init() {
        addCleanupButton();
        
        const observer = new MutationObserver(() => {
            setTimeout(addCleanupButton, 500);
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    setTimeout(init, 1000);
    setTimeout(init, 3000);
    
})();
