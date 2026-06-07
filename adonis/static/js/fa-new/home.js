/* ============================================================================
 * ADONIS  /fa-new/  Persian homepage prototype
 * Vanilla JS only — no external libraries.
 *
 * Provides:
 *   1. Sticky-header scroll state.
 *   2. Mobile menu toggle.
 *   3. IntersectionObserver-driven text/card reveal.
 *   4. Parallax for hero layers using a single rAF loop.
 *   5. Lightweight canvas "golden dust" ambient particle field.
 *   6. prefers-reduced-motion + small-screen + Save-Data fallbacks
 *      that disable the heavy effects gracefully.
 * ========================================================================== */

(function () {
    "use strict";

    // ── Luxury section title keyword highlighting (Fa homepage only) ──────
    // Runs only for the redesigned first section title and leaves CMS text
    // untouched in storage. If no known keywords exist, nothing changes.
    (function highlightLuxuryTitle() {
        var title = document.querySelector("[data-fa-luxury-highlight]");
        if (!title) return;

        var raw = (title.textContent || "").trim();
        if (!raw) return;

        function escapeRegExp(text) {
            return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        }

        var html = raw;
        var brandWords = ["آدونیس", "ADONIS", "یونان", "سرمایه‌گذاری"];
        var goldWords = ["لوکس", "اقامت", "اروپا"];

        brandWords.forEach(function (word) {
            var re = new RegExp("(" + escapeRegExp(word) + ")", "g");
            html = html.replace(re, '<span class="is-brand">$1</span>');
        });

        goldWords.forEach(function (word) {
            var re = new RegExp("(" + escapeRegExp(word) + ")", "g");
            html = html.replace(re, '<span class="is-gold">$1</span>');
        });

        title.innerHTML = html;
    })();

    // ── Inline SVG icons for benefits cards ──────────────────────────────
    // Keeps payload tiny and avoids loading heavy icon files/libraries.
    (function hydrateBenefitIcons() {
        var icons = document.querySelectorAll(".fa-benefit-card-icon-graphic[data-icon-key]");
        if (!icons.length) return;

        var pathsByKey = {
            "1": ["M12 24l8 8 16-16", "M24 9c8 0 14 7 14 15"],
            "2": ["M10 25h28", "M24 14v22"],
            "3": ["M8 30c4-7 10-11 16-11s12 4 16 11", "M24 12a6 6 0 1 1 0 12"],
            "4": ["M10 32l10-18 7 9 11-7", "M12 34h24"],
        };

        icons.forEach(function (icon) {
            var key = icon.getAttribute("data-icon-key") || "1";
            var paths = pathsByKey[key] || pathsByKey["1"];
            var p1 = icon.querySelector(".icon-path-1");
            var p2 = icon.querySelector(".icon-path-2");
            if (p1) p1.setAttribute("d", paths[0]);
            if (p2) p2.setAttribute("d", paths[1]);
        });
    })();

    // ── Capability gates ─────────────────────────────────────────────────
    var prefersReducedMotion =
        window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    var connection =
        navigator.connection ||
        navigator.mozConnection ||
        navigator.webkitConnection;

    var saveData = !!(connection && connection.saveData);
    var slowNetwork = !!(
        connection &&
        connection.effectiveType &&
        /^(slow-2g|2g)$/i.test(connection.effectiveType)
    );

    // True only when motion + canvas are safe to run.
    var canAnimate = !prefersReducedMotion && !saveData && !slowNetwork;

    // ── Header scroll state + mobile menu ────────────────────────────────
    var header = document.querySelector("[data-fa-header]");
    var burger = document.querySelector("[data-fa-burger]");
    var mobileMenu = document.querySelector("[data-fa-mobile-menu]");

    function updateHeaderScrollState() {
        if (!header) return;
        if (window.scrollY > 24) {
            header.classList.add("is-scrolled");
        } else {
            header.classList.remove("is-scrolled");
        }
    }

    if (header) {
        updateHeaderScrollState();
        window.addEventListener("scroll", updateHeaderScrollState, {
            passive: true,
        });
    }

    if (burger && header) {
        burger.addEventListener("click", function () {
            header.classList.toggle("is-mobile-open");
        });
    }

    // Close mobile menu when a link inside it is tapped.
    if (mobileMenu && header) {
        mobileMenu.addEventListener("click", function (e) {
            var t = e.target;
            while (t && t !== mobileMenu) {
                if (t.tagName === "A") {
                    header.classList.remove("is-mobile-open");
                    break;
                }
                t = t.parentNode;
            }
        });
    }

    // ── Desktop dropdown: hover-intent with safe close delay ─────────────
    // Pure :hover CSS is fragile when there is any tiny gap/transition
    // between parent link and submenu. We add an explicit `is-open` class
    // on mouseenter and remove it only after a delay on mouseleave, with
    // the delay cancelled the moment the cursor re-enters either the parent
    // li OR the submenu itself. This is how Stripe/Linear/Vercel handle it.
    (function setupNavDropdowns() {
        // Keep dropdown stable while moving from parent link to submenu,
        // but close quickly enough when the pointer truly leaves.
        var HIDE_DELAY = 200;
        var items = document.querySelectorAll(".adonis-fa-new-nav-has-sub");
        if (!items.length) return;

        items.forEach(function (li) {
            var hideTimer = null;
            var subnav = li.querySelector(":scope > .adonis-fa-new-subnav");

            function open() {
                if (hideTimer) {
                    clearTimeout(hideTimer);
                    hideTimer = null;
                }
                li.classList.add("is-open");
            }

            function scheduleClose() {
                if (hideTimer) clearTimeout(hideTimer);
                hideTimer = setTimeout(function () {
                    li.classList.remove("is-open");
                    hideTimer = null;
                }, HIDE_DELAY);
            }

            function onMouseLeave(e) {
                var to = e.relatedTarget;
                if (to && li.contains(to)) {
                    open();
                    return;
                }
                scheduleClose();
            }

            // mouseenter / mouseleave on the <li> itself (non-bubbling,
            // fires when cursor enters/leaves the element and ALL descendants).
            li.addEventListener("mouseenter", open);
            li.addEventListener("mouseleave", onMouseLeave);

            // Extra safety-net: attach mouseenter directly to the subnav so
            // that if the cursor somehow enters the panel without re-triggering
            // the parent li's mouseenter (e.g. jumping over the ::after bridge
            // in a fast diagonal move), we still cancel the close timer.
            if (subnav) {
                subnav.addEventListener("mouseenter", open);
                subnav.addEventListener("mouseleave", onMouseLeave);
                // When the cursor leaves the subnav to somewhere outside the
                // whole <li> subtree, the parent mouseleave already fires.
                // We only need the extra guard for leaving the subnav toward
                // the page (not back to the <a>), which the li mouseleave covers.
            }

            // Also cover keyboard focus
            li.addEventListener("focusin", open);
            li.addEventListener("focusout", function (e) {
                // Only close if focus actually leaves the li subtree
                if (!li.contains(e.relatedTarget)) {
                    scheduleClose();
                }
            });

            // Tap-to-toggle on touch devices
            var trigger = li.querySelector(":scope > a");
            if (trigger) {
                trigger.addEventListener("click", function (e) {
                    var isCoarse =
                        window.matchMedia &&
                        window.matchMedia("(hover: none)").matches;
                    if (isCoarse) {
                        if (!li.classList.contains("is-open")) {
                            e.preventDefault();
                            // Close any other open dropdowns
                            items.forEach(function (other) {
                                if (other !== li) other.classList.remove("is-open");
                            });
                            open();
                        }
                    }
                });
            }
        });

        // Click anywhere outside any dropdown closes all of them
        document.addEventListener("click", function (e) {
            items.forEach(function (li) {
                if (!li.contains(e.target)) li.classList.remove("is-open");
            });
        });
    })();

    // ── Smooth in-page anchor scrolling (RTL-friendly, native) ───────────
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener("click", function (e) {
            var id = anchor.getAttribute("href");
            if (!id || id === "#") return;
            var target = document.querySelector(id);
            if (!target) return;
            e.preventDefault();
            var top =
                target.getBoundingClientRect().top +
                window.scrollY -
                (header ? header.offsetHeight - 4 : 0);
            window.scrollTo({
                top: top,
                behavior: prefersReducedMotion ? "auto" : "smooth",
            });
        });
    });

    // ── Reveal animations via IntersectionObserver ───────────────────────
    var revealEls = document.querySelectorAll("[data-fa-reveal]");

    if (prefersReducedMotion || !("IntersectionObserver" in window)) {
        // Fallback: just show everything immediately.
        revealEls.forEach(function (el) {
            el.classList.add("is-revealed");
        });
    } else {
        revealEls.forEach(function (el) {
            var delay = parseInt(el.getAttribute("data-fa-reveal-delay"), 10);
            if (!isNaN(delay)) {
                el.style.setProperty("--adonis-fa-new-delay", delay + "ms");
            }
        });

        var revealObserver = new IntersectionObserver(
            function (entries, obs) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-revealed");
                        obs.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
        );

        revealEls.forEach(function (el) {
            revealObserver.observe(el);
        });
    }

    // ── Hero parallax (scroll-driven, single rAF loop) ───────────────────
    var hero = document.querySelector("[data-fa-hero]");
    var parallaxNodes = hero
        ? hero.querySelectorAll("[data-fa-parallax]")
        : [];

    if (canAnimate && hero && parallaxNodes.length) {
        var ticking = false;

        function applyParallax() {
            var rect = hero.getBoundingClientRect();
            // Only animate while the hero is roughly on screen.
            if (rect.bottom < -200 || rect.top > window.innerHeight + 200) {
                ticking = false;
                return;
            }
            var scroll = -rect.top; // pixels scrolled past hero top
            for (var i = 0; i < parallaxNodes.length; i++) {
                var node = parallaxNodes[i];
                var speed = parseFloat(
                    node.getAttribute("data-fa-parallax")
                );
                if (isNaN(speed)) speed = 0;
                var translate = scroll * speed;
                node.style.transform =
                    "translate3d(0, " + translate.toFixed(2) + "px, 0)";
            }
            ticking = false;
        }

        function onScrollOrResize() {
            if (!ticking) {
                window.requestAnimationFrame(applyParallax);
                ticking = true;
            }
        }

        applyParallax();
        window.addEventListener("scroll", onScrollOrResize, { passive: true });
        window.addEventListener("resize", onScrollOrResize, { passive: true });
    }

    // ── Canvas ambient "golden dust" field ───────────────────────────────
    // A very light particle field that gives the hero a cinematic 3D feel
    // without needing pre-rendered frame sequences. Designed to be CHEAP:
    //   • <1ms / frame on a mid-range laptop
    //   • capped particle count
    //   • disabled on small screens / reduced-motion / save-data
    var canvas = document.querySelector("[data-fa-canvas]");

    if (canAnimate && canvas && window.innerWidth > 700) {
        var ctx = canvas.getContext("2d", { alpha: true });
        var dpr = Math.min(window.devicePixelRatio || 1, 2);
        var W = 0;
        var H = 0;
        var particles = [];
        var PARTICLE_COUNT_BASE = 70;
        var rafId = null;
        var running = false;

        function resizeCanvas() {
            var rect = canvas.getBoundingClientRect();
            W = Math.max(1, Math.floor(rect.width));
            H = Math.max(1, Math.floor(rect.height));
            canvas.width = Math.floor(W * dpr);
            canvas.height = Math.floor(H * dpr);
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            seedParticles();
        }

        function seedParticles() {
            var count = Math.min(
                PARTICLE_COUNT_BASE,
                Math.floor((W * H) / 22000) // density-based cap
            );
            particles = [];
            for (var i = 0; i < count; i++) {
                particles.push(spawn(true));
            }
        }

        function spawn(initial) {
            // depth z ∈ [0.3, 1.0]: smaller z = farther back, slower + dimmer.
            var z = 0.3 + Math.random() * 0.7;
            return {
                x: Math.random() * W,
                y: initial ? Math.random() * H : H + Math.random() * 30,
                vx: (Math.random() - 0.5) * 0.06,
                vy: -(0.08 + Math.random() * 0.18) * z,
                r: 0.6 + Math.random() * 1.6 * z,
                a: 0.15 + Math.random() * 0.45 * z,
                z: z,
                hue: 38 + Math.random() * 14, // gold range
            };
        }

        function step() {
            ctx.clearRect(0, 0, W, H);
            for (var i = 0; i < particles.length; i++) {
                var p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                if (p.y < -10 || p.x < -10 || p.x > W + 10) {
                    particles[i] = spawn(false);
                    continue;
                }
                ctx.beginPath();
                var grad = ctx.createRadialGradient(
                    p.x,
                    p.y,
                    0,
                    p.x,
                    p.y,
                    p.r * 4
                );
                grad.addColorStop(
                    0,
                    "hsla(" + p.hue + ", 70%, 70%, " + p.a + ")"
                );
                grad.addColorStop(
                    1,
                    "hsla(" + p.hue + ", 70%, 70%, 0)"
                );
                ctx.fillStyle = grad;
                ctx.arc(p.x, p.y, p.r * 4, 0, Math.PI * 2);
                ctx.fill();
            }
            rafId = window.requestAnimationFrame(step);
        }

        function start() {
            if (running) return;
            running = true;
            step();
        }

        function stop() {
            running = false;
            if (rafId) {
                window.cancelAnimationFrame(rafId);
                rafId = null;
            }
        }

        // Pause when the hero is out of view to save battery.
        if ("IntersectionObserver" in window && hero) {
            var heroObserver = new IntersectionObserver(
                function (entries) {
                    entries.forEach(function (entry) {
                        if (entry.isIntersecting) start();
                        else stop();
                    });
                },
                { threshold: 0 }
            );
            heroObserver.observe(hero);
        }

        // Pause when tab is hidden.
        document.addEventListener("visibilitychange", function () {
            if (document.hidden) stop();
            else if (hero) {
                var rect = hero.getBoundingClientRect();
                if (
                    rect.bottom > 0 &&
                    rect.top < window.innerHeight
                ) {
                    start();
                }
            }
        });

        resizeCanvas();
        start();

        var resizeTimeout;
        window.addEventListener("resize", function () {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function () {
                stop();
                dpr = Math.min(window.devicePixelRatio || 1, 2);
                resizeCanvas();
                start();
            }, 150);
        });
    } else if (canvas) {
        // No-animation path: ensure canvas does not affect layout/visuals.
        canvas.style.display = "none";
    }
})();

/* ============================================================================
 * Why Adonis Stats - Counter Animation
 * Animates numbers from 0 to target value when entering viewport.
 * ========================================================================== */
(function () {
    "use strict";

    var prefersReducedMotion =
        window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    var counters = document.querySelectorAll("[data-counter-target]");
    if (!counters.length) return;

    var DURATION = 2000;

    function easeOutQuart(t) {
        return 1 - Math.pow(1 - t, 4);
    }

    function animateCounter(el) {
        var target = parseInt(el.getAttribute("data-counter-target"), 10);
        if (isNaN(target) || target <= 0) return;

        var valueEl = el.querySelector(".why-adonis-counter") ||
                      el.querySelector(".fa-why-adonis-counter") || 
                      el.querySelector(".fa-stats-counter") || 
                      el.querySelector(".fa-counter-value");
        if (!valueEl) return;

        var startTime = null;

        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            var progress = Math.min((timestamp - startTime) / DURATION, 1);
            var easedProgress = easeOutQuart(progress);
            var current = Math.floor(easedProgress * target);

            valueEl.textContent = current;

            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                valueEl.textContent = target;
            }
        }

        requestAnimationFrame(step);
    }

    if (prefersReducedMotion || !("IntersectionObserver" in window)) {
        counters.forEach(function (el) {
            var target = parseInt(el.getAttribute("data-counter-target"), 10);
            var valueEl = el.querySelector(".why-adonis-counter") ||
                          el.querySelector(".fa-why-adonis-counter") || 
                          el.querySelector(".fa-stats-counter") || 
                          el.querySelector(".fa-counter-value");
            if (valueEl && !isNaN(target)) {
                valueEl.textContent = target;
            }
        });
    } else {
        var counterObserver = new IntersectionObserver(
            function (entries, obs) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        animateCounter(entry.target);
                        obs.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.2, rootMargin: "0px 0px -5% 0px" }
        );

        counters.forEach(function (el) {
            counterObserver.observe(el);
        });
    }
})();
