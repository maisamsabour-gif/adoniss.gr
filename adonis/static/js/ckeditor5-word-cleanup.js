/**
 * CKEditor5 Word Content Cleanup - Manual Button Only
 * 
 * This script provides a manual cleanup button for content pasted from Microsoft Word.
 * It does NOT intercept the paste event - CKEditor5's native paste handling is preserved.
 * 
 * Usage: Paste content normally, then click the "پاکسازی فرمت" button to clean it.
 * 
 * Allowed tags: p, h2, h3, h4, ul, ol, li, strong, b, em, i, br, a
 */

(function() {
    'use strict';

    // ─────────────────────────────────────────────────────────────────────────────
    // Configuration
    // ─────────────────────────────────────────────────────────────────────────────
    
    const ALLOWED_TAGS = ['p', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'strong', 'b', 'em', 'i', 'br', 'a', 'div', 'blockquote'];
    const ALLOWED_ATTRS = {
        'a': ['href', 'target'],
    };
    
    // ─────────────────────────────────────────────────────────────────────────────
    // HTML Cleanup Functions
    // ─────────────────────────────────────────────────────────────────────────────
    
    /**
     * Clean HTML that was pasted from Word
     */
    function cleanWordHTML(html) {
        if (!html) return '';
        
        // Create a temporary div to parse the HTML
        const temp = document.createElement('div');
        temp.innerHTML = html;
        
        // Remove Word-specific tags completely
        const wordTags = temp.querySelectorAll('style, xml, meta, link, title, script');
        wordTags.forEach(el => el.remove());
        
        // Remove elements with Word namespaces (o:p, w:sdt, etc.)
        const nsElements = temp.querySelectorAll('*');
        nsElements.forEach(el => {
            if (el.tagName && el.tagName.includes(':')) {
                el.remove();
            }
        });
        
        // Remove comments (including Word conditional comments)
        removeComments(temp);
        
        // Process all elements - clean attributes and unwrap spans
        processElement(temp);
        
        // Get cleaned HTML
        let cleanedHtml = temp.innerHTML;
        
        // Additional regex-based cleanup for stubborn Word markup
        cleanedHtml = cleanedHtml
            // Remove empty spans and fonts
            .replace(/<span[^>]*>\s*<\/span>/gi, '')
            .replace(/<font[^>]*>\s*<\/font>/gi, '')
            // Remove mso comments
            .replace(/<!--\[if[^>]*>[\s\S]*?<!\[endif\]-->/gi, '')
            .replace(/<!--[\s\S]*?-->/gi, '')
            // Remove empty paragraphs with only nbsp
            .replace(/<p[^>]*>\s*(&nbsp;|\u00A0)+\s*<\/p>/gi, '<p><br></p>')
            // Normalize multiple nbsp to single space
            .replace(/(&nbsp;)+/gi, ' ')
            // Clean up any remaining mso attributes in style
            .replace(/mso-[^:]+:[^;"]+;?/gi, '')
            // Remove Mso classes
            .replace(/\s*class="[^"]*Mso[^"]*"/gi, '')
            .replace(/\s*class='[^']*Mso[^']*'/gi, '')
            // Remove empty style attributes
            .replace(/\s*style="\s*"/gi, '')
            .replace(/\s*style='\s*'/gi, '')
            .replace(/\s*class="\s*"/gi, '')
            .replace(/\s*class='\s*'/gi, '');
        
        return cleanedHtml.trim();
    }
    
    /**
     * Remove HTML comments from an element
     */
    function removeComments(element) {
        const iterator = document.createNodeIterator(
            element,
            NodeFilter.SHOW_COMMENT,
            null,
            false
        );
        const comments = [];
        let comment;
        while (comment = iterator.nextNode()) {
            comments.push(comment);
        }
        comments.forEach(c => {
            if (c.parentNode) {
                c.parentNode.removeChild(c);
            }
        });
    }
    
    /**
     * Process an element and its children - clean up Word formatting
     */
    function processElement(element) {
        const children = Array.from(element.childNodes);
        
        children.forEach(child => {
            if (child.nodeType === Node.ELEMENT_NODE) {
                const tagName = child.tagName.toLowerCase();
                
                // Remove Word-specific namespace elements
                if (tagName.includes(':')) {
                    // Preserve text content
                    const text = child.textContent;
                    if (text && text.trim()) {
                        const textNode = document.createTextNode(text);
                        child.parentNode.replaceChild(textNode, child);
                    } else {
                        child.remove();
                    }
                    return;
                }
                
                // Handle span and font tags - unwrap them but keep content
                if (tagName === 'span' || tagName === 'font') {
                    unwrapElement(child);
                    return;
                }
                
                // Clean all attributes except allowed ones
                cleanAttributes(child, tagName);
                
                // Process children recursively
                processElement(child);
            }
        });
    }
    
    /**
     * Clean attributes on an element, keeping only allowed ones
     */
    function cleanAttributes(element, tagName) {
        const allowed = ALLOWED_ATTRS[tagName] || [];
        const attrs = Array.from(element.attributes);
        
        attrs.forEach(attr => {
            const attrName = attr.name.toLowerCase();
            // Remove all style and class attributes, and any mso-* attributes
            if (attrName === 'style' || attrName === 'class' || attrName.startsWith('mso')) {
                element.removeAttribute(attr.name);
            } else if (!allowed.includes(attrName)) {
                // Remove other non-allowed attributes
                element.removeAttribute(attr.name);
            }
        });
    }
    
    /**
     * Unwrap an element, keeping its children
     */
    function unwrapElement(element) {
        const parent = element.parentNode;
        if (!parent) return;
        
        // Process children first
        processElement(element);
        
        // Move all children to parent
        while (element.firstChild) {
            parent.insertBefore(element.firstChild, element);
        }
        
        // Remove the now-empty element
        parent.removeChild(element);
    }
    
    // ─────────────────────────────────────────────────────────────────────────────
    // Manual Cleanup Functions (for toolbar button)
    // ─────────────────────────────────────────────────────────────────────────────
    
    /**
     * Clean the content of all CKEditor5 instances on the page
     */
    window.cleanAllEditors = function() {
        const editables = document.querySelectorAll('.ck-editor__editable');
        let cleanedCount = 0;
        
        editables.forEach(editable => {
            const original = editable.innerHTML;
            const cleaned = cleanWordHTML(original);
            if (original !== cleaned) {
                editable.innerHTML = cleaned;
                // Trigger input event so CKEditor knows content changed
                editable.dispatchEvent(new Event('input', { bubbles: true }));
                cleanedCount++;
            }
        });
        
        console.log(`Cleaned ${cleanedCount} editor(s)`);
        return cleanedCount;
    };
    
    /**
     * Clean content of a specific editor element
     */
    window.cleanEditorContent = function(editorElement) {
        if (!editorElement) return false;
        
        const editable = editorElement.querySelector('.ck-editor__editable');
        if (editable) {
            const original = editable.innerHTML;
            const cleaned = cleanWordHTML(original);
            if (original !== cleaned) {
                editable.innerHTML = cleaned;
                editable.dispatchEvent(new Event('input', { bubbles: true }));
                return true;
            }
        }
        return false;
    };
    
    // ─────────────────────────────────────────────────────────────────────────────
    // UI - Cleanup Button
    // ─────────────────────────────────────────────────────────────────────────────
    
    /**
     * Add cleanup button to the page (for Persian admin pages)
     */
    function addCleanupButton() {
        // Only add on pages with CKEditor5
        if (!document.querySelector('.ck-editor')) return;
        
        // Check if button already exists
        if (document.querySelector('#word-cleanup-btn')) return;
        
        // Create button container
        const container = document.createElement('div');
        container.style.cssText = 'position: fixed; bottom: 20px; left: 20px; z-index: 9999;';
        
        const btn = document.createElement('button');
        btn.id = 'word-cleanup-btn';
        btn.type = 'button';
        btn.innerHTML = '🧹 پاکسازی فرمت Word';
        btn.title = 'بعد از paste کردن متن از Word، این دکمه را بزنید تا استایل‌های اضافی پاک شوند';
        btn.style.cssText = `
            background: linear-gradient(135deg, #059669 0%, #047857 100%);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-family: 'Vazirmatn', Tahoma, sans-serif;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
            transition: all 0.2s ease;
            direction: rtl;
        `;
        btn.onmouseover = function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 6px 16px rgba(5, 150, 105, 0.4)';
        };
        btn.onmouseout = function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 12px rgba(5, 150, 105, 0.3)';
        };
        btn.onclick = function() {
            const count = window.cleanAllEditors();
            // Show feedback
            const originalText = this.innerHTML;
            if (count > 0) {
                this.innerHTML = '✓ پاکسازی شد!';
                this.style.background = 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)';
            } else {
                this.innerHTML = '✓ تمیز بود!';
                this.style.background = 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)';
            }
            setTimeout(() => {
                this.innerHTML = originalText;
                this.style.background = 'linear-gradient(135deg, #059669 0%, #047857 100%)';
            }, 2000);
        };
        
        container.appendChild(btn);
        document.body.appendChild(container);
    }
    
    // ─────────────────────────────────────────────────────────────────────────────
    // Initialization
    // ─────────────────────────────────────────────────────────────────────────────
    
    function init() {
        addCleanupButton();
        
        // Watch for dynamically added editors
        const observer = new MutationObserver((mutations) => {
            let shouldCheck = false;
            mutations.forEach(mutation => {
                if (mutation.addedNodes.length) {
                    shouldCheck = true;
                }
            });
            if (shouldCheck) {
                setTimeout(addCleanupButton, 500);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Also run after a short delay to catch late-loaded editors
    setTimeout(init, 1000);
    setTimeout(init, 3000);
    
})();
