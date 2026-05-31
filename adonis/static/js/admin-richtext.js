(function() {
    function initRichText() {
        var targets = document.querySelectorAll('textarea.rt-target');
        targets.forEach(function(textarea) {
            if (textarea.dataset.rtInit) return;
            textarea.dataset.rtInit = '1';

            var wrapper = document.createElement('div');
            wrapper.className = 'rt-wrapper';

            var toolbar = document.createElement('div');
            toolbar.className = 'rt-toolbar';
            toolbar.innerHTML =
                '<button type="button" class="rt-btn" data-cmd="bold" title="Bold (Ctrl+B)"><i class="fas fa-bold"></i></button>' +
                '<button type="button" class="rt-btn" data-cmd="italic" title="Italic (Ctrl+I)"><i class="fas fa-italic"></i></button>' +
                '<span class="rt-sep"></span>' +
                '<select class="rt-size" title="Font Size">' +
                    '<option value="">Size</option>' +
                    '<option value="0.85em">Small</option>' +
                    '<option value="1em">Normal</option>' +
                    '<option value="1.2em">Large</option>' +
                    '<option value="1.5em">X-Large</option>' +
                '</select>' +
                '<span class="rt-sep"></span>' +
                '<button type="button" class="rt-btn" data-cmd="clear" title="Clear formatting"><i class="fas fa-eraser"></i></button>';

            var preview = document.createElement('div');
            preview.className = 'rt-preview';

            textarea.parentNode.insertBefore(wrapper, textarea);
            wrapper.appendChild(toolbar);
            wrapper.appendChild(textarea);
            wrapper.appendChild(preview);

            function updatePreview() {
                preview.innerHTML = textarea.value || '<span style="color:#adb5bd">Preview appears here</span>';
            }
            updatePreview();
            textarea.addEventListener('input', updatePreview);

            function wrapSel(before, after) {
                var s = textarea.selectionStart, e = textarea.selectionEnd;
                if (s === e) return;
                var v = textarea.value;
                textarea.value = v.substring(0, s) + before + v.substring(s, e) + after + v.substring(e);
                textarea.selectionStart = s + before.length;
                textarea.selectionEnd = e + before.length;
                textarea.focus();
                updatePreview();
            }

            toolbar.addEventListener('click', function(ev) {
                var btn = ev.target.closest('[data-cmd]');
                if (!btn) return;
                ev.preventDefault();
                var cmd = btn.dataset.cmd;
                if (cmd === 'bold') wrapSel('<b>', '</b>');
                else if (cmd === 'italic') wrapSel('<i>', '</i>');
                else if (cmd === 'clear') {
                    textarea.value = textarea.value
                        .replace(/<\/?b>/gi, '')
                        .replace(/<\/?i>/gi, '')
                        .replace(/<\/?strong>/gi, '')
                        .replace(/<\/?em>/gi, '')
                        .replace(/<span[^>]*>/gi, '')
                        .replace(/<\/span>/gi, '')
                        .replace(/<font[^>]*>/gi, '')
                        .replace(/<\/font>/gi, '');
                    textarea.focus();
                    updatePreview();
                }
            });

            var sizeSelect = toolbar.querySelector('.rt-size');
            if (sizeSelect) {
                sizeSelect.addEventListener('change', function() {
                    if (this.value) {
                        wrapSel('<span style="font-size:' + this.value + '">', '</span>');
                    }
                    this.value = '';
                });
            }

            textarea.addEventListener('keydown', function(ev) {
                if (ev.ctrlKey || ev.metaKey) {
                    if (ev.key === 'b' || ev.key === 'B') { ev.preventDefault(); wrapSel('<b>', '</b>'); }
                    else if (ev.key === 'i' || ev.key === 'I') { ev.preventDefault(); wrapSel('<i>', '</i>'); }
                }
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initRichText);
    } else {
        initRichText();
    }
})();
