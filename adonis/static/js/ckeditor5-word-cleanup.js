/**
 * CKEditor5 Word Paste Fix
 * 
 * Intercepts paste from Word and uses PLAIN TEXT instead of messy HTML
 * This prevents fragmentation and formatting issues
 */

(function() {
    'use strict';
    
    /**
     * Check if content is from Microsoft Word
     */
    function isFromWord(html) {
        if (!html) return false;
        return html.includes('mso-') || 
               html.includes('MsoNormal') ||
               html.includes('schemas-microsoft-com') ||
               html.includes('xmlns:w=') ||
               html.includes('class="Mso') ||
               html.includes('urn:schemas-microsoft');
    }
    
    /**
     * Convert plain text to proper HTML paragraphs
     * Handles Persian/RTL text properly
     */
    function textToHtml(text) {
        if (!text) return '';
        
        // Normalize line endings
        text = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
        
        // Split by double newlines (paragraph breaks)
        // Single newlines within a paragraph should become spaces
        const paragraphs = text.split(/\n\s*\n/);
        
        const htmlParts = paragraphs.map(para => {
            // Clean up the paragraph
            let cleaned = para
                .replace(/\n/g, ' ')  // Single newlines become spaces
                .replace(/\s+/g, ' ') // Multiple spaces become one
                .trim();
            
            if (!cleaned) return '';
            
            return '<p>' + escapeHtml(cleaned) + '</p>';
        }).filter(p => p);
        
        return htmlParts.join('\n');
    }
    
    /**
     * Escape HTML special characters
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Handle paste event
     */
    function handlePaste(event) {
        const clipboardData = event.clipboardData || window.clipboardData;
        if (!clipboardData) return;
        
        const html = clipboardData.getData('text/html');
        const plainText = clipboardData.getData('text/plain');
        
        // Only intercept if it's from Word
        if (!html || !isFromWord(html)) {
            return; // Let normal paste happen
        }
        
        // Prevent default paste
        event.preventDefault();
        event.stopPropagation();
        
        // Convert plain text to clean HTML
        const cleanHtml = textToHtml(plainText);
        
        if (!cleanHtml) return;
        
        // Try to find CKEditor instance and use its API
        const editable = event.target.closest('.ck-editor__editable');
        if (editable) {
            const wrapper = editable.closest('.ck-editor');
            const root = wrapper ? wrapper.closest('.ck') : null;
            
            // Try multiple ways to get the editor instance
            let editor = null;
            
            // Method 1: Check wrapper
            if (wrapper && wrapper.ckeditorInstance) {
                editor = wrapper.ckeditorInstance;
            }
            
            // Method 2: Check root element
            if (!editor && root && root.ckeditorInstance) {
                editor = root.ckeditorInstance;
            }
            
            // Method 3: Look for global editors
            if (!editor && window.CKEDITOR_INSTANCES) {
                const instances = Object.values(window.CKEDITOR_INSTANCES);
                if (instances.length > 0) {
                    editor = instances[0];
                }
            }
            
            // If we found the editor, use its clipboard
            if (editor && editor.model) {
                try {
                    const viewFragment = editor.data.processor.toView(cleanHtml);
                    const modelFragment = editor.data.toModel(viewFragment);
                    editor.model.insertContent(modelFragment);
                    console.log('Word content pasted via CKEditor API');
                    return;
                } catch (e) {
                    console.log('CKEditor API failed:', e);
                }
            }
        }
        
        // Fallback: use execCommand
        try {
            document.execCommand('insertHTML', false, cleanHtml);
            console.log('Word content pasted via execCommand');
        } catch (e) {
            // Last resort: insert as text
            document.execCommand('insertText', false, plainText);
            console.log('Fallback to plain text');
        }
    }
    
    /**
     * Attach paste handlers to CKEditor editables
     */
    function attachPasteHandlers() {
        document.querySelectorAll('.ck-editor__editable').forEach(editable => {
            if (editable.hasAttribute('data-word-paste-handler')) return;
            
            editable.addEventListener('paste', handlePaste, true);
            editable.setAttribute('data-word-paste-handler', 'true');
            console.log('Word paste handler attached');
        });
    }
    
    /**
     * Manual cleanup for already-pasted content
     */
    function cleanExistingContent(html) {
        const temp = document.createElement('div');
        temp.innerHTML = html;
        
        // Remove Word elements
        temp.querySelectorAll('style, xml, meta, link, o\\:p, script').forEach(el => el.remove());
        
        // Unwrap spans and fonts
        let wrappers = temp.querySelectorAll('span, font');
        while (wrappers.length > 0) {
            wrappers.forEach(el => {
                while (el.firstChild) {
                    el.parentNode.insertBefore(el.firstChild, el);
                }
                el.remove();
            });
            wrappers = temp.querySelectorAll('span, font');
        }
        
        // Clean attributes
        temp.querySelectorAll('*').forEach(el => {
            const href = el.tagName === 'A' ? el.getAttribute('href') : null;
            while (el.attributes.length > 0) {
                el.removeAttribute(el.attributes[0].name);
            }
            if (href) el.setAttribute('href', href);
        });
        
        // Clean up HTML
        let cleaned = temp.innerHTML
            .replace(/<p[^>]*>\s*(&nbsp;)?\s*<\/p>/gi, '')
            .replace(/&nbsp;/gi, ' ')
            .replace(/<!--[\s\S]*?-->/gi, '');
        
        return cleaned;
    }
    
    /**
     * Clean all editors on page
     */
    window.cleanAllEditors = function() {
        let count = 0;
        document.querySelectorAll('.ck-editor__editable').forEach(editable => {
            const original = editable.innerHTML;
            const cleaned = cleanExistingContent(original);
            if (original !== cleaned) {
                editable.innerHTML = cleaned;
                editable.dispatchEvent(new Event('input', { bubbles: true }));
                count++;
            }
        });
        return count;
    };
    
    /**
     * Add cleanup button
     */
    function addButton() {
        if (!document.querySelector('.ck-editor')) return;
        if (document.querySelector('#word-fix-btn')) return;
        
        const btn = document.createElement('button');
        btn.id = 'word-fix-btn';
        btn.type = 'button';
        btn.innerHTML = '🧹 پاکسازی';
        btn.title = 'پاکسازی فرمت‌های اضافی';
        btn.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            z-index: 9999;
            background: #dc2626;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-family: Tahoma, sans-serif;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;
        btn.onclick = function() {
            const count = window.cleanAllEditors();
            this.innerHTML = count > 0 ? '✓ انجام شد!' : '✓ تمیز بود';
            this.style.background = '#16a34a';
            setTimeout(() => {
                this.innerHTML = '🧹 پاکسازی';
                this.style.background = '#dc2626';
            }, 2000);
        };
        
        document.body.appendChild(btn);
    }
    
    // Initialize
    function init() {
        attachPasteHandlers();
        addButton();
    }
    
    // Run on load and watch for new editors
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Re-run periodically to catch dynamically added editors
    setInterval(() => {
        attachPasteHandlers();
        addButton();
    }, 2000);
    
    // Also run after short delays
    setTimeout(init, 500);
    setTimeout(init, 1500);
    setTimeout(init, 3000);
    
})();
