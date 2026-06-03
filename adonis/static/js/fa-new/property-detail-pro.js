/* ══════════════════════════════════════════════════════════════════════════════
   ADONIS PROPERTY DETAIL - PROFESSIONAL JAVASCRIPT
   Lightbox Gallery, Animations, Unit Filters, Sticky CTA
   ══════════════════════════════════════════════════════════════════════════════ */

(function() {
    'use strict';

    // ══════════════════════════════════════════════════════════════════════════
    // LIGHTBOX GALLERY
    // ══════════════════════════════════════════════════════════════════════════
    
    const lightbox = document.getElementById('fa-prop-lightbox');
    const lightboxImg = lightbox?.querySelector('.fa-prop-lightbox-img');
    const lightboxTag = lightbox?.querySelector('.fa-prop-lightbox-tag');
    const lightboxTitle = lightbox?.querySelector('.fa-prop-lightbox-title');
    const lightboxCaption = lightbox?.querySelector('.fa-prop-lightbox-caption');
    const lightboxCounter = lightbox?.querySelector('.fa-prop-lightbox-counter');
    const lightboxClose = lightbox?.querySelector('.fa-prop-lightbox-close');
    const lightboxPrev = lightbox?.querySelector('.fa-prop-lightbox-prev');
    const lightboxNext = lightbox?.querySelector('.fa-prop-lightbox-next');
    
    let galleryItems = [];
    let currentIndex = 0;
    
    function initLightbox() {
        const items = document.querySelectorAll('.fa-prop-gallery-item');
        if (!items.length || !lightbox) return;
        
        galleryItems = Array.from(items).map(item => ({
            url: item.dataset.imgUrl,
            alt: item.dataset.imgAlt,
            caption: item.dataset.imgCaption,
            tag: item.dataset.imgTag,
            title: item.dataset.imgTitle
        }));
        
        items.forEach((item, index) => {
            item.addEventListener('click', () => openLightbox(index));
        });
        
        lightboxClose?.addEventListener('click', closeLightbox);
        lightboxPrev?.addEventListener('click', showPrev);
        lightboxNext?.addEventListener('click', showNext);
        
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) closeLightbox();
        });
        
        document.addEventListener('keydown', (e) => {
            if (!lightbox.classList.contains('active')) return;
            if (e.key === 'Escape') closeLightbox();
            if (e.key === 'ArrowRight') showPrev();
            if (e.key === 'ArrowLeft') showNext();
        });
    }
    
    function openLightbox(index) {
        currentIndex = index;
        updateLightbox();
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    function closeLightbox() {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    function showPrev() {
        currentIndex = (currentIndex - 1 + galleryItems.length) % galleryItems.length;
        updateLightbox();
    }
    
    function showNext() {
        currentIndex = (currentIndex + 1) % galleryItems.length;
        updateLightbox();
    }
    
    function updateLightbox() {
        const item = galleryItems[currentIndex];
        if (!item) return;
        
        lightboxImg.src = item.url;
        lightboxImg.alt = item.alt;
        
        if (item.tag) {
            lightboxTag.textContent = item.tag;
            lightboxTag.style.display = 'inline-block';
        } else {
            lightboxTag.style.display = 'none';
        }
        
        if (item.title) {
            lightboxTitle.textContent = item.title;
            lightboxTitle.style.display = 'block';
        } else {
            lightboxTitle.style.display = 'none';
        }
        
        if (item.caption) {
            lightboxCaption.textContent = item.caption;
            lightboxCaption.style.display = 'block';
        } else {
            lightboxCaption.style.display = 'none';
        }
        
        lightboxCounter.querySelector('.current').textContent = currentIndex + 1;
        lightboxCounter.querySelector('.total').textContent = galleryItems.length;
    }
    
    // ══════════════════════════════════════════════════════════════════════════
    // SCROLL ANIMATIONS
    // ══════════════════════════════════════════════════════════════════════════
    
    function initScrollAnimations() {
        const animatedElements = document.querySelectorAll('[data-animate]');
        if (!animatedElements.length) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        animatedElements.forEach(el => observer.observe(el));
    }
    
    // ══════════════════════════════════════════════════════════════════════════
    // PROGRESS BAR ANIMATIONS
    // ══════════════════════════════════════════════════════════════════════════
    
    function initProgressBars() {
        const progressBars = document.querySelectorAll('.fa-prop-timeline-progress-fill');
        if (!progressBars.length) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const bar = entry.target;
                    const width = bar.style.width;
                    bar.style.width = '0%';
                    setTimeout(() => {
                        bar.style.width = width;
                    }, 100);
                    observer.unobserve(bar);
                }
            });
        }, { threshold: 0.5 });
        
        progressBars.forEach(bar => observer.observe(bar));
    }
    
    // ══════════════════════════════════════════════════════════════════════════
    // UNIT TABLE FILTERS
    // ══════════════════════════════════════════════════════════════════════════
    
    function initUnitFilters() {
        const statusFilter = document.getElementById('filter-status');
        const bedroomsFilter = document.getElementById('filter-bedrooms');
        const tableRows = document.querySelectorAll('.fa-prop-unit-row');
        const cards = document.querySelectorAll('.fa-prop-unit-card');
        
        if (!statusFilter && !bedroomsFilter) return;
        
        function applyFilters() {
            const statusValue = statusFilter?.value || 'all';
            const bedroomsValue = bedroomsFilter?.value || 'all';
            
            const filterItems = (items) => {
                items.forEach(item => {
                    const status = item.dataset.status;
                    const bedrooms = item.dataset.bedrooms;
                    
                    let show = true;
                    if (statusValue !== 'all' && status !== statusValue) show = false;
                    if (bedroomsValue !== 'all' && bedrooms !== bedroomsValue) show = false;
                    
                    item.style.display = show ? '' : 'none';
                });
            };
            
            filterItems(tableRows);
            filterItems(cards);
        }
        
        statusFilter?.addEventListener('change', applyFilters);
        bedroomsFilter?.addEventListener('change', applyFilters);
    }
    
    // ══════════════════════════════════════════════════════════════════════════
    // STICKY FORM HANDLING
    // ══════════════════════════════════════════════════════════════════════════
    
    function initStickyForm() {
        const form = document.querySelector('.fa-prop-sticky-form');
        if (!form) return;
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = form.querySelector('.fa-prop-sticky-submit');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> در حال ارسال...';
            
            try {
                const formData = new FormData(form);
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                const data = await response.json();
                
                if (data.ok) {
                    submitBtn.innerHTML = '<i class="fas fa-check"></i> درخواست شما ثبت شد';
                    submitBtn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
                    form.reset();
                    
                    setTimeout(() => {
                        submitBtn.innerHTML = originalText;
                        submitBtn.style.background = '';
                        submitBtn.disabled = false;
                    }, 3000);
                } else {
                    throw new Error(data.error || 'خطا در ارسال فرم');
                }
            } catch (error) {
                submitBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> ' + error.message;
                submitBtn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
                
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.style.background = '';
                    submitBtn.disabled = false;
                }, 3000);
            }
        });
    }
    
    // ══════════════════════════════════════════════════════════════════════════
    // SMOOTH SCROLL TO SECTIONS
    // ══════════════════════════════════════════════════════════════════════════
    
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    const headerHeight = document.querySelector('.adonis-fa-new-header')?.offsetHeight || 80;
                    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }
    
    // ══════════════════════════════════════════════════════════════════════════
    // HERO SCROLL INDICATOR
    // ══════════════════════════════════════════════════════════════════════════
    
    function initHeroScroll() {
        const scrollIndicator = document.querySelector('.fa-prop-hero-pro-scroll');
        if (!scrollIndicator) return;
        
        scrollIndicator.addEventListener('click', () => {
            const quickInfo = document.querySelector('.fa-prop-quick-info');
            if (quickInfo) {
                quickInfo.scrollIntoView({ behavior: 'smooth' });
            }
        });
        
        window.addEventListener('scroll', () => {
            if (window.scrollY > 100) {
                scrollIndicator.style.opacity = '0';
            } else {
                scrollIndicator.style.opacity = '1';
            }
        });
    }
    
    // ══════════════════════════════════════════════════════════════════════════
    // IMAGE LAZY LOADING
    // ══════════════════════════════════════════════════════════════════════════
    
    function initLazyLoading() {
        const images = document.querySelectorAll('img[loading="lazy"]');
        
        if ('loading' in HTMLImageElement.prototype) {
            return;
        }
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    }
    
    // ══════════════════════════════════════════════════════════════════════════
    // INITIALIZE ALL
    // ══════════════════════════════════════════════════════════════════════════
    
    function init() {
        initLightbox();
        initScrollAnimations();
        initProgressBars();
        initUnitFilters();
        initStickyForm();
        initSmoothScroll();
        initHeroScroll();
        initLazyLoading();
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
