/**
 * flipbook.js  –  Issuu-like flipbook viewer
 *
 * Depends on: page-flip.browser.js (StPageFlip), Font Awesome icons
 * Data contract (window.FLIPBOOK_DATA):
 *   { pageUrls: string[], pageCount: int, pageWidth: int, pageHeight: int,
 *     slug: string, pagesApiUrl: string, pdfUrl: string,
 *     status: 'ready'|'processing'|'pending'|'failed' }
 */
(function () {
    'use strict';

    // ── Guard ─────────────────────────────────────────────────────────────
    if (typeof window.FLIPBOOK_DATA === 'undefined') return;

    const D = window.FLIPBOOK_DATA;

    // ── DOM refs ──────────────────────────────────────────────────────────
    const $ = id => document.getElementById(id);
    const wrapper       = $('fbWrapper');
    const stage         = $('fbStage');
    const zoomWrap      = $('fbZoomWrap');
    const bookEl        = $('fb-book');
    const btnPrev       = $('fbPrev');
    const btnNext       = $('fbNext');
    const btnZoomIn     = $('fbZoomIn');
    const btnZoomOut    = $('fbZoomOut');
    const btnFullscreen = $('fbFullscreen');
    const btnThumb      = $('fbThumbToggle');
    const btnDownload   = $('fbDownload');
    const pageNumEl     = $('fbPageNum');
    const thumbstrip    = $('fbThumbstrip');

    // ── Pan overlay ───────────────────────────────────────────────────────
    // Sits above the book (z-index 8), below arrows (10) and controls (20).
    // Intercepts all pointer/touch events when zoomed so StPageFlip never
    // sees drag gestures – we use them exclusively for panning.
    const panOverlay = document.createElement('div');
    panOverlay.id = 'fbPanOverlay';
    stage.appendChild(panOverlay);

    // ── State ─────────────────────────────────────────────────────────────
    let pageFlip  = null;
    let zoom      = 1;
    let panX      = 0;
    let panY      = 0;
    const loaded      = new Set();
    const thumbLoaded = new Set();

    const MIN_ZOOM   = 0.4;
    const MAX_ZOOM   = 2.5;
    const ZOOM_STEP  = 0.2;
    const PRELOAD_RADIUS = 2;

    // ── Status / fallback handling ────────────────────────────────────────
    if (D.status !== 'ready') {
        renderStatusOverlay();
        return;
    }

    // ── Transform helpers ─────────────────────────────────────────────────
    /**
     * Apply the current zoom + pan to zoomWrap.
     * @param {boolean} animated – use CSS transition (true for button-clicks / zoom)
     */
    function applyTransform(animated) {
        zoomWrap.style.transition = animated
            ? 'transform .3s cubic-bezier(.25,.46,.45,.94)'
            : 'none';
        zoomWrap.style.transform = `translate(${panX}px,${panY}px) scale(${zoom})`;
    }

    /**
     * Clamp panX/panY so the book never scrolls out of the stage viewport.
     */
    function clampPan() {
        const sw = stage.clientWidth;
        const sh = stage.clientHeight;
        // offsetWidth/Height are the un-transformed dimensions
        const bw = zoomWrap.offsetWidth  * zoom;
        const bh = zoomWrap.offsetHeight * zoom;
        const maxX = Math.max(0, (bw - sw) / 2);
        const maxY = Math.max(0, (bh - sh) / 2);
        panX = Math.max(-maxX, Math.min(maxX, panX));
        panY = Math.max(-maxY, Math.min(maxY, panY));
    }

    // ── Build page dimensions ─────────────────────────────────────────────
    function calcPageSize() {
        const stageW = stage.clientWidth  || window.innerWidth;
        const stageH = stage.clientHeight || (window.innerHeight - 104);
        const mobile  = stageW < 680;
        const arrowRoom = mobile ? 50 : 70;
        const maxBookW  = stageW - arrowRoom * 2;
        const maxBookH  = stageH - 20;
        const aspect  = D.pageWidth && D.pageHeight ? D.pageHeight / D.pageWidth : 1.414;
        let pageW, pageH;
        if (mobile) {
            pageW = Math.min(maxBookW, 480);
        } else {
            pageW = Math.min(Math.floor(maxBookW / 2) - 4, 600);
        }
        pageH = Math.min(Math.round(pageW * aspect), maxBookH);
        pageW = Math.round(pageH / aspect);
        return { width: pageW, height: pageH, mobile };
    }

    // ── Create page elements and inject into DOM ──────────────────────────
    function buildPageElements() {
        bookEl.innerHTML = '';
        for (let i = 0; i < D.pageCount; i++) {
            const div = document.createElement('div');
            div.className = 'fb-page-leaf';
            div.dataset.idx = i;
            div.innerHTML = `
                <div class="fb-page-placeholder">
                    <div class="fb-spinner"></div>
                    <span>${i + 1}</span>
                </div>`;
            bookEl.appendChild(div);
        }
        return bookEl.querySelectorAll('.fb-page-leaf');
    }

    // ── Lazy image loading ────────────────────────────────────────────────
    function loadPage(idx) {
        if (idx < 0 || idx >= D.pageCount || loaded.has(idx)) return;
        loaded.add(idx);
        const leaf = bookEl.querySelector(`[data-idx="${idx}"]`);
        if (!leaf) return;
        const img = new Image();
        img.decoding = 'async';
        img.src = D.pageUrls[idx];
        img.onload = () => { leaf.innerHTML = ''; leaf.appendChild(img); };
        img.onerror = () => {
            leaf.querySelector('.fb-page-placeholder').innerHTML =
                `<i class="fas fa-image" style="font-size:2rem;color:#ccc;"></i><span>Page ${idx + 1}</span>`;
        };
    }

    function preloadAround(centerIdx) {
        for (let i = Math.max(0, centerIdx - PRELOAD_RADIUS);
             i <= Math.min(D.pageCount - 1, centerIdx + PRELOAD_RADIUS + 1);
             i++) {
            loadPage(i);
        }
    }

    // ── Initialise StPageFlip ─────────────────────────────────────────────
    function initFlipBook() {
        const dim = calcPageSize();
        if (pageFlip) {
            try { pageFlip.destroy(); } catch (e) {}
            pageFlip = null;
        }
        // Clear any stale inline styles StPageFlip left on the host element
        bookEl.style.cssText = '';
        buildPageElements();
        pageFlip = new St.PageFlip(bookEl, {
            width:               dim.width,
            height:              dim.height,
            size:                'fixed',
            usePortrait:         dim.mobile,
            showCover:           false,
            mobileScrollSupport: false,
            disableFlipByClick:  false,
            drawShadow:          true,
            flippingTime:        700,
            autoSize:            false,
            startPage:           0,
            maxShadowOpacity:    0.5,
            showPageCorners:     !dim.mobile,
            swipeDistance:       30,
        });
        pageFlip.loadFromHTML(bookEl.querySelectorAll('.fb-page-leaf'));
        pageFlip.on('flip',        e  => onPageChange(e.data));
        pageFlip.on('init',        ()  => { preloadAround(0); updateUI(0); buildThumbnails(); });
        pageFlip.on('changeState', ()  => updateUI(pageFlip.getCurrentPageIndex()));
    }

    // ── UI update ─────────────────────────────────────────────────────────
    function onPageChange(idx) {
        updateUI(idx);
        preloadAround(idx);
        syncThumbActive(idx);
        scrollThumbIntoView(idx);
    }

    function updateUI(idx) {
        const spread  = pageFlip ? !pageFlip.getOrientation || pageFlip.getOrientation() !== 'portrait' : false;
        const display = spread
            ? `${idx + 1}–${Math.min(idx + 2, D.pageCount)} / ${D.pageCount}`
            : `${idx + 1} / ${D.pageCount}`;
        pageNumEl.textContent = display;
        btnPrev.disabled = idx <= 0;
        btnNext.disabled = idx >= D.pageCount - 1;
    }

    // ── Thumbnails ────────────────────────────────────────────────────────
    function buildThumbnails() {
        thumbstrip.innerHTML = '';
        for (let i = 0; i < D.pageCount; i++) {
            const t = document.createElement('div');
            t.className = 'fb-thumb';
            t.dataset.idx = i;
            t.innerHTML = `<div class="fb-page-placeholder"><div class="fb-spinner"></div></div><span class="fb-thumb-num">${i + 1}</span>`;
            t.addEventListener('click', () => { if (pageFlip) pageFlip.flip(i); });
            thumbstrip.appendChild(t);
        }
        lazyLoadThumbs();
    }

    function lazyLoadThumbs() {
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;
                const t = entry.target;
                const idx = +t.dataset.idx;
                if (thumbLoaded.has(idx)) return;
                thumbLoaded.add(idx);
                observer.unobserve(t);
                const img = new Image();
                img.src = D.pageUrls[idx];
                img.onload = () => {
                    t.querySelector('.fb-page-placeholder').remove();
                    t.insertBefore(img, t.querySelector('.fb-thumb-num'));
                };
            });
        }, { root: thumbstrip, rootMargin: '0px 300px 0px 300px' });
        thumbstrip.querySelectorAll('.fb-thumb').forEach(t => observer.observe(t));
    }

    function syncThumbActive(idx) {
        thumbstrip.querySelectorAll('.fb-thumb').forEach(t => {
            t.classList.toggle('active', +t.dataset.idx === idx || +t.dataset.idx === idx + 1);
        });
    }

    function scrollThumbIntoView(idx) {
        const t = thumbstrip.querySelector(`[data-idx="${idx}"]`);
        if (t) t.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    }

    // ── Zoom ──────────────────────────────────────────────────────────────
    function setZoom(val, animated) {
        zoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, val));

        // When at or below 1× reset pan so the book re-centres
        if (zoom <= 1) { panX = 0; panY = 0; }
        else           { clampPan(); }

        applyTransform(animated !== false);

        btnZoomOut.disabled = zoom <= MIN_ZOOM;
        btnZoomIn.disabled  = zoom >= MAX_ZOOM;

        // Show overlay (and grab cursor) only when actually zoomed in
        const zoomed = zoom > 1.001;
        panOverlay.classList.toggle('active', zoomed);
    }

    // ── Fullscreen ────────────────────────────────────────────────────────
    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            (wrapper.requestFullscreen || wrapper.webkitRequestFullscreen).call(wrapper);
        } else {
            (document.exitFullscreen || document.webkitExitFullscreen).call(document);
        }
    }

    function onFullscreenChange() {
        const active = !!document.fullscreenElement;
        btnFullscreen.innerHTML = active
            ? '<i class="fas fa-compress"></i>'
            : '<i class="fas fa-expand"></i>';
        btnFullscreen.title = active ? 'Exit Fullscreen' : 'Fullscreen';
    }

    // ── Status overlay ────────────────────────────────────────────────────
    function renderStatusOverlay() {
        let html = '';
        if (D.status === 'processing' || D.status === 'pending') {
            html = `
                <div class="fb-status-overlay" id="fbStatusOverlay">
                    <div class="fb-spinner"></div>
                    <h3>Preparing your brochure…</h3>
                    <p>Pages are being converted. This usually takes under a minute. The page will refresh automatically.</p>
                </div>`;
            setTimeout(function poll() {
                fetch(D.pagesApiUrl)
                    .then(r => r.json())
                    .then(data => {
                        if (data.status === 'ready' || data.status === 'failed') location.reload();
                        else setTimeout(poll, 4000);
                    })
                    .catch(() => setTimeout(poll, 6000));
            }, 4000);
        } else if (D.status === 'failed') {
            html = `
                <div class="fb-status-overlay">
                    <i class="fas fa-exclamation-triangle" style="font-size:2.5rem;color:#ef4444;"></i>
                    <h3>Conversion Failed</h3>
                    <p>We couldn't convert this PDF to images. You can still download the original PDF.</p>
                    ${D.pdfUrl ? `<a href="${D.pdfUrl}" target="_blank" class="fb-pdf-link"><i class="fas fa-file-pdf"></i> Open PDF</a>` : ''}
                </div>`;
        }
        stage.innerHTML = html;
    }

    // ── Keyboard navigation ───────────────────────────────────────────────
    function onKeyDown(e) {
        if (!pageFlip) return;
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); pageFlip.flipNext(); }
        if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')   { e.preventDefault(); pageFlip.flipPrev(); }
        if (e.key === 'Escape' && document.fullscreenElement) toggleFullscreen();
    }

    // ── Mouse-wheel zoom (Ctrl/Cmd + scroll) ──────────────────────────────
    function onWheel(e) {
        if (!e.ctrlKey && !e.metaKey) return;
        e.preventDefault();
        setZoom(zoom + (e.deltaY < 0 ? ZOOM_STEP : -ZOOM_STEP));
    }

    // ══════════════════════════════════════════════════════════════════════
    //  PAN  –  mouse drag
    // ══════════════════════════════════════════════════════════════════════
    let _mouseDown    = false;
    let _didDrag      = false;
    let _mouseStartX  = 0;
    let _mouseStartY  = 0;
    let _panStartX    = 0;
    let _panStartY    = 0;

    function onPanMouseDown(e) {
        if (e.button !== 0) return;
        _mouseDown   = true;
        _didDrag     = false;
        _mouseStartX = e.clientX;
        _mouseStartY = e.clientY;
        _panStartX   = panX;
        _panStartY   = panY;
        panOverlay.classList.add('grabbing');
        e.preventDefault();   // stop text-selection / StPageFlip bubbling
    }

    function onPanMouseMove(e) {
        if (!_mouseDown) return;
        const dx = e.clientX - _mouseStartX;
        const dy = e.clientY - _mouseStartY;
        if (!_didDrag && (Math.abs(dx) > 4 || Math.abs(dy) > 4)) _didDrag = true;
        if (!_didDrag) return;
        panX = _panStartX + dx;
        panY = _panStartY + dy;
        clampPan();
        applyTransform(false);
    }

    function onPanMouseUp(e) {
        if (!_mouseDown) return;
        _mouseDown = false;
        panOverlay.classList.remove('grabbing');

        // If no meaningful drag occurred treat it as a click:
        // left 30% of stage → prev, right 30% → next
        if (!_didDrag && pageFlip) {
            const rect = stage.getBoundingClientRect();
            const relX = (e.clientX - rect.left) / rect.width;
            if      (relX < 0.3) pageFlip.flipPrev();
            else if (relX > 0.7) pageFlip.flipNext();
        }
    }

    // ══════════════════════════════════════════════════════════════════════
    //  PAN + PINCH  –  touch
    // ══════════════════════════════════════════════════════════════════════
    let pinchDist0    = null;
    let pinchZoom0    = 1;
    let _touchPan     = false;
    let _touchStartX  = 0;
    let _touchStartY  = 0;
    let _touchPanX0   = 0;
    let _touchPanY0   = 0;
    let _touchMoved   = false;

    function resetTouchState() {
        pinchDist0  = null;
        pinchZoom0  = 1;
        _touchPan   = false;
        _touchMoved = false;
    }

    function onTouchStart(e) {
        if (e.touches.length === 2) {
            // Two-finger pinch zoom
            pinchDist0 = Math.hypot(
                e.touches[0].clientX - e.touches[1].clientX,
                e.touches[0].clientY - e.touches[1].clientY
            );
            pinchZoom0 = zoom;
            _touchPan  = false;
        } else if (e.touches.length === 1 && zoom > 1.001) {
            // Single-finger pan (only when zoomed in)
            _touchPan    = true;
            _touchMoved  = false;
            _touchStartX = e.touches[0].clientX;
            _touchStartY = e.touches[0].clientY;
            _touchPanX0  = panX;
            _touchPanY0  = panY;
            // Don't call preventDefault here so the initial tap still works
        }
    }

    function onTouchMove(e) {
        if (e.touches.length === 2 && pinchDist0 !== null) {
            // Pinch zoom
            const dist = Math.hypot(
                e.touches[0].clientX - e.touches[1].clientX,
                e.touches[0].clientY - e.touches[1].clientY
            );
            setZoom(pinchZoom0 * (dist / pinchDist0), false);
            e.preventDefault();   // stop browser pinch-zoom / scroll
        } else if (e.touches.length === 1 && _touchPan) {
            const dx = e.touches[0].clientX - _touchStartX;
            const dy = e.touches[0].clientY - _touchStartY;
            if (!_touchMoved && (Math.abs(dx) > 4 || Math.abs(dy) > 4)) _touchMoved = true;
            if (!_touchMoved) return;
            panX = _touchPanX0 + dx;
            panY = _touchPanY0 + dy;
            clampPan();
            applyTransform(false);
            e.preventDefault();   // stop page scroll while panning
        }
    }

    function onTouchEnd(e) {
        if (e.touches.length === 0) {
            // All fingers lifted – fully reset pinch state
            pinchDist0 = null;
        }
        // Single-tap (no drag) on overlay edges → flip page
        if (_touchPan && !_touchMoved && e.changedTouches.length === 1 && pageFlip) {
            const rect = stage.getBoundingClientRect();
            const relX = (e.changedTouches[0].clientX - rect.left) / rect.width;
            if      (relX < 0.3) pageFlip.flipPrev();
            else if (relX > 0.7) pageFlip.flipNext();
        }
        _touchPan   = false;
        _touchMoved = false;
    }

    function onTouchCancel() {
        // Touch cancelled (e.g. iOS back-swipe gesture took over)
        resetTouchState();
        panOverlay.classList.remove('grabbing');
    }

    // ── Window resize ─────────────────────────────────────────────────────
    let resizeTimer;
    function onResize() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            const curIdx = pageFlip ? pageFlip.getCurrentPageIndex() : 0;
            // Reset pan on resize so the book re-centres
            panX = 0; panY = 0;
            initFlipBook();
            if (pageFlip) pageFlip.flip(curIdx);
        }, 300);
    }

    // ══════════════════════════════════════════════════════════════════════
    //  TEARDOWN  –  runs on pagehide (back/forward nav) and bfcache restore
    // ══════════════════════════════════════════════════════════════════════

    /**
     * Full teardown: destroy StPageFlip, reset visual state.
     * Called on pagehide so that if the browser puts this page into the
     * back-forward cache (bfcache), it is in a clean neutral state when
     * restored.
     */
    function teardown() {
        clearTimeout(resizeTimer);
        resetTouchState();
        _mouseDown = false;
        panOverlay.classList.remove('grabbing', 'active');

        if (pageFlip) {
            try { pageFlip.destroy(); } catch (e) {}
            pageFlip = null;
        }

        // Reset transform so restored page doesn't flash with stale zoom/pan
        zoom = 1; panX = 0; panY = 0;
        zoomWrap.style.transition = 'none';
        zoomWrap.style.transform  = '';

        // Collapse thumbnail strip
        thumbstrip.classList.add('hidden');
        btnThumb.classList.remove('active');

        // Remove body class so if bfcache restores the list/other pages,
        // the class is not accidentally carried across
        document.body.classList.remove('fb-page');
    }

    /**
     * Re-enter: called when bfcache restores this page via the
     * pageshow event (event.persisted === true) or when navigating
     * forward to the page after a teardown.
     */
    function reenter() {
        // Re-apply body class (may have been removed by teardown)
        document.body.classList.add('fb-page');

        // Re-clear any stale loaded-set so pages re-render at correct size
        loaded.clear();
        thumbLoaded.clear();
        bookEl.style.cssText = '';
        bookEl.innerHTML = '';

        zoom = 1; panX = 0; panY = 0;

        initFlipBook();
        setZoom(1);
    }

    // ── pagehide / pageshow (bfcache) ─────────────────────────────────────
    window.addEventListener('pagehide', () => {
        teardown();
    });

    window.addEventListener('pageshow', (e) => {
        if (e.persisted) {
            // Page was restored from bfcache – full reinitialisation needed
            reenter();
        }
    });

    // ── Bind events ───────────────────────────────────────────────────────

    // Navigation buttons
    btnPrev.addEventListener('click', () => pageFlip && pageFlip.flipPrev());
    btnNext.addEventListener('click', () => pageFlip && pageFlip.flipNext());

    // Zoom buttons
    btnZoomIn.addEventListener('click',  () => setZoom(zoom + ZOOM_STEP));
    btnZoomOut.addEventListener('click', () => setZoom(zoom - ZOOM_STEP));

    // Fullscreen
    btnFullscreen.addEventListener('click', toggleFullscreen);
    document.addEventListener('fullscreenchange',       onFullscreenChange);
    document.addEventListener('webkitfullscreenchange', onFullscreenChange);

    // Thumbnail strip
    btnThumb.addEventListener('click', () => {
        thumbstrip.classList.toggle('hidden');
        btnThumb.classList.toggle('active');
    });

    // Download
    if (btnDownload && D.pdfUrl) {
        btnDownload.addEventListener('click', () => {
            const a = document.createElement('a');
            a.href = D.pdfUrl; a.download = ''; a.target = '_blank';
            a.click();
        });
    }

    // Keyboard
    document.addEventListener('keydown', onKeyDown);

    // Ctrl+Wheel zoom
    stage.addEventListener('wheel', onWheel, { passive: false });

    // Mouse pan – overlay captures mousedown; move/up on document so we
    // don't lose the drag when the cursor leaves the overlay briefly
    panOverlay.addEventListener('mousedown', onPanMouseDown);
    document.addEventListener('mousemove',  onPanMouseMove);
    document.addEventListener('mouseup',    onPanMouseUp);

    // Touch – non-passive so we can preventDefault during pan/pinch
    stage.addEventListener('touchstart',  onTouchStart,  { passive: true  });
    stage.addEventListener('touchmove',   onTouchMove,   { passive: false });
    stage.addEventListener('touchend',    onTouchEnd,    { passive: true  });
    stage.addEventListener('touchcancel', onTouchCancel, { passive: true  });

    window.addEventListener('resize', onResize);

    // ── Boot ──────────────────────────────────────────────────────────────
    initFlipBook();
    setZoom(1);

})();
