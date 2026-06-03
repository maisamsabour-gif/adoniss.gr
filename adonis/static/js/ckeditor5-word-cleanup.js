/**
 * CKEditor5 Word Paste Cleanup
 * 
 * This script cleans up content pasted from Microsoft Word into CKEditor5 editors.
 * It removes Word-specific markup, span tags, inline styles, and normalizes the HTML.
 * 
 * Allowed tags: p, h2, h3, h4, ul, ol, li, strong, b, em, i, br, a
 */

(function() {
    'use strict';

    // ─────────────────────────────────────────────────────────────────────────────
    // Configuration
    // ─────────────────────────────────────────────────────────────────────────────
    
    const ALLOWED_TAGS = ['p', 'h2', 'h3', 'h4', 'ul', 'ol', 'li', 'strong', 'b', 'em', 'i', 'br', 'a', 'div'];
    const ALLOWED_ATTRS = {
        'a': ['href', 'target'],
    };
    
    // ─────────────────────────────────────────────────────────────────────────────
    // HTML Cleanup Functions
    // ─────────────────────────────────────────────────────────────────────────────
    
    /**
     * Check if HTML appears to be from Microsoft Word
     */
    function isWordContent(html) {
        return html.includes('mso-') || 
               html.includes('MsoNormal') ||
               html.includes('urn:schemas-microsoft-com') ||
               html.includes('xmlns:w=') ||
               html.includes('class="Mso');
    }
    
    /**
     * Clean HTML pasted from Word
     */
    function cleanWordHTML(html) {
        if (!html) return '';
        
        // Create a temporary div to parse the HTML
        const temp = document.createElement('div');
        temp.innerHTML = html;
        
        // Remove Word-specific tags completely
        const wordTags = temp.querySelectorAll('style, xml, meta, link, o\\:p, w\\:sdt, w\\:sdtpr, w\\:sdtcontent');
        wordTags.forEach(el => el.remove());
        
        // Remove comments (including Word conditional comments)
        removeComments(temp);
        
        // Process all elements
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
            // Remove empty paragraphs (but keep line breaks)
            .replace(/<p[^>]*>\s*(&nbsp;|\u00A0)?\s*<\/p>/gi, '')
            // Fix multiple spaces
            .replace(/&nbsp;/gi, ' ')
            .replace(/\s+/g, ' ')
            // Clean up any remaining mso attributes
            .replace(/\s*mso-[^:]+:[^;"]+;?/gi, '')
            .replace(/\s*class="[^"]*Mso[^"]*"/gi, '')
            // Remove empty style attributes
            .replace(/\s*style="\s*"/gi, '')
            .replace(/\s*class="\s*"/gi, '');
        
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
        comments.forEach(c => c.parentNode.removeChild(c));
    }
    
    /**
     * Process an element and its children
     */
    function processElement(element) {
        const children = Array.from(element.childNodes);
        
        children.forEach(child => {
            if (child.nodeType === Node.ELEMENT_NODE) {
                const tagName = child.tagName.toLowerCase();
                
                // Remove Word-specific elements
                if (tagName.includes(':') || tagName === 'style' || tagName === 'xml') {
                    child.remove();
                    return;
                }
                
                // Convert Word headings
                if (child.classList && (child.classList.contains('MsoTitle') || child.classList.contains('MsoHeading1'))) {
                    replaceWithTag(child, 'h2');
                    return;
                }
                if (child.classList && child.classList.contains('MsoHeading2')) {
                    replaceWithTag(child, 'h3');
                    return;
                }
                if (child.classList && child.classList.contains('MsoHeading3')) {
                    replaceWithTag(child, 'h4');
                    return;
                }
                
                // Handle span and font tags - unwrap them but keep their text content
                if (tagName === 'span' || tagName === 'font') {
                    unwrapElement(child);
                    return;
                }
                
                // Handle div - convert to p if it contains text
                if (tagName === 'div') {
                    if (child.textContent.trim()) {
                        replaceWithTag(child, 'p');
                    } else {
                        child.remove();
                    }
                    return;
                }
                
                // Handle b/strong
                if (tagName === 'b') {
                    replaceWithTag(child, 'strong');
                    return;
                }
                
                // Handle i/em
                if (tagName === 'i') {
                    replaceWithTag(child, 'em');
                    return;
                }
                
                // Check if tag is allowed
                if (!ALLOWED_TAGS.includes(tagName)) {
                    // For non-allowed block elements, try to preserve content
                    if (child.textContent.trim()) {
                        const p = document.createElement('p');
                        p.textContent = child.textContent;
                        child.parentNode.replaceChild(p, child);
                    } else {
                        child.remove();
                    }
                    return;
                }
                
                // Clean attributes for allowed tags
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
            if (!allowed.includes(attr.name.toLowerCase())) {
                element.removeAttribute(attr.name);
            }
        });
    }
    
    /**
     * Replace an element with a new tag, preserving content
     */
    function replaceWithTag(oldElement, newTagName) {
        const newElement = document.createElement(newTagName);
        
        // Move all children
        while (oldElement.firstChild) {
            newElement.appendChild(oldElement.firstChild);
        }
        
        // Replace in DOM
        if (oldElement.parentNode) {
            oldElement.parentNode.replaceChild(newElement, oldElement);
            // Process the new element's children
            processElement(newElement);
        }
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
    // Event Handling
    // ─────────────────────────────────────────────────────────────────────────────
    
    /**
     * Handle paste event on CKEditor5 editable areas
     */
    function handlePaste(event) {
        const clipboardData = event.clipboardData || window.clipboardData;
        if (!clipboardData) return;
        
        // Get HTML content from clipboard
        const html = clipboardData.getData('text/html');
        const text = clipboardData.getData('text/plain');
        
        // Only clean if it looks like Word content
        if (html && isWordContent(html)) {
            event.preventDefault();
            event.stopPropagation();
            
            // Clean the HTML
            const cleanedHtml = cleanWordHTML(html);
            
            // Try to insert via CKEditor5 API if available
            const editorInstance = findCKEditorInstance(event.target);
            if (editorInstance && editorInstance.execute) {
                try {
                    // Use CKEditor's clipboard plugin if available
                    const viewFragment = editorInstance.data.processor.toView(cleanedHtml);
                    const modelFragment = editorInstance.data.toModel(viewFragment);
                    editorInstance.model.insertContent(modelFragment);
                    return;
                } catch (e) {
                    console.log('CKEditor5 insert failed, using fallback:', e);
                }
            }
            
            // Fallback: use execCommand
            try {
                document.execCommand('insertHTML', false, cleanedHtml);
            } catch (e) {
                // Last resort: insert plain text
                document.execCommand('insertText', false, text);
            }
        }
    }
    
    /**
     * Try to find the CKEditor5 instance for an editable element
     */
    function findCKEditorInstance(element) {
        // Look for the editor instance in the element's properties
        let current = element;
        while (current && current !== document) {
            if (current.ckeditorInstance) {
                return current.ckeditorInstance;
            }
            // CKEditor5 often stores instance on the widget wrapper
            const wrapper = current.closest('.ck-editor');
            if (wrapper && wrapper.ckeditorInstance) {
                return wrapper.ckeditorInstance;
            }
            current = current.parentElement;
        }
        return null;
    }
    
    // ─────────────────────────────────────────────────────────────────────────────
    // Manual Cleanup Function (for toolbar button)
    // ─────────────────────────────────────────────────────────────────────────────
    
    /**
     * Clean the content of all CKEditor5 instances on the page
     * Can be called from a button click
     */
    window.cleanAllEditors = function() {
        const editables = document.querySelectorAll('.ck-editor__editable');
        editables.forEach(editable => {
            const original = editable.innerHTML;
            const cleaned = cleanWordHTML(original);
            if (original !== cleaned) {
                editable.innerHTML = cleaned;
                // Trigger input event so CKEditor knows content changed
                editable.dispatchEvent(new Event('input', { bubbles: true }));
                console.log('Editor content cleaned');
            }
        });
    };
    
    /**
     * Clean content of a specific editor element
     */
    window.cleanEditorContent = function(editorElement) {
        if (!editorElement) return;
        
        const editable = editorElement.querySelector('.ck-editor__editable');
        if (editable) {
            const original = editable.innerHTML;
            const cleaned = cleanWordHTML(original);
            if (original !== cleaned) {
                editable.innerHTML = cleaned;
                editable.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    };
    
    // ─────────────────────────────────────────────────────────────────────────────
    // Initialization
    // ─────────────────────────────────────────────────────────────────────────────
    
    /**
     * Attach paste handlers to all CKEditor5 editable areas
     */
    function attachPasteHandlers() {
        const editables = document.querySelectorAll('.ck-editor__editable');
        editables.forEach(editable => {
            if (!editable.hasAttribute('data-word-cleanup-attached')) {
                editable.addEventListener('paste', handlePaste, true);
                editable.setAttribute('data-word-cleanup-attached', 'true');
            }
        });
    }
    
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
        btn.innerHTML = '🧹 پاکسازی فرمت';
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
            window.cleanAllEditors();
            // Show feedback
            const originalText = this.innerHTML;
            this.innerHTML = '✓ پاکسازی شد!';
            this.style.background = 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)';
            setTimeout(() => {
                this.innerHTML = originalText;
                this.style.background = 'linear-gradient(135deg, #059669 0%, #047857 100%)';
            }, 2000);
        };
        
        container.appendChild(btn);
        document.body.appendChild(container);
    }
    
    /**
     * Initialize when DOM is ready
     */
    function init() {
        // Initial attachment
        attachPasteHandlers();
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
                setTimeout(() => {
                    attachPasteHandlers();
                    addCleanupButton();
                }, 500);
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
