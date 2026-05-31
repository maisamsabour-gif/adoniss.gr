(function () {
    "use strict";

    var section = document.querySelector(".adonis-fa-new-hero");
    var video   = document.querySelector(".adonis-fa-new-video");
    var scenes  = document.querySelectorAll(".hero-scene");
    var hint    = document.querySelector(".hero-scroll-hint");

    if (!section || !video) return;

    /* Show scene 1 immediately while video loads */
    if (scenes.length) scenes[0].classList.add("is-active");

    var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reducedMotion) return;

    var isMobile = window.matchMedia("(max-width: 900px)").matches;

    /* ── Strip autoplay/loop so browser never auto-plays ─────────────────── */
    video.removeAttribute("autoplay");
    video.removeAttribute("loop");
    video.loop  = false;
    video.muted = true;
    video.setAttribute("muted", "");

    /* Desktop: tell the browser to preload the full file for smooth scrubbing.
       Mobile: keep metadata-only to save bandwidth.                          */
    if (!isMobile) {
        video.setAttribute("preload", "auto");
        video.preload = "auto";
    }

    /* ── State ─────────────────────────────────────────────────────────── */
    var metaReady = false;   // duration is known
    var unlocked  = false;   // decoder has been warmed up via play→pause
    var lastSeek  = -1;

    /* ── Scroll progress 0–1 ────────────────────────────────────────────── */
    function getProgress() {
        var rect   = section.getBoundingClientRect();
        var runway = section.offsetHeight - window.innerHeight;
        if (runway <= 0) return 0;
        return Math.max(0, Math.min(1, -rect.top / runway));
    }

    /* ── Main tick: seek video + activate the correct overlay ───────────── */
    function tick() {
        var p   = getProgress();
        var dur = video.duration;

        if (metaReady && dur && dur > 0 && !isNaN(dur)) {
            /* Clamp: never seek to exactly 0 (avoids poster re-show in iOS/Safari) */
            var t = Math.max(0.001, Math.min(dur - 0.05, p * dur));
            if (Math.abs(t - lastSeek) > 0.04) {
                lastSeek = t;
                try { video.currentTime = t; } catch (e) {}
            }
        }

        /* Activate the scene whose [data-start, data-end) range covers pct */
        var pct = p * 100;
        for (var i = 0; i < scenes.length; i++) {
            var s     = scenes[i];
            var start = parseFloat(s.getAttribute("data-start") || 0);
            var end   = parseFloat(s.getAttribute("data-end")   || 30);
            s.classList.toggle("is-active", pct >= start && pct < end);
        }
        /* Always keep scene 1 active at the very top */
        if (p === 0 && scenes.length) scenes[0].classList.add("is-active");

        if (hint) hint.style.opacity = p > 0.04 ? "0" : "1";
    }

    /* ── Unlock the video decoder with one play→pause cycle ─────────────
       Without this, Safari and many mobile browsers won't render individual
       frames when you set currentTime on a never-played video.
       After this single cycle the video stays paused; we drive it via
       currentTime only.                                                    */
    function unlockDecoder() {
        if (unlocked) return;
        unlocked = true;

        var promise = video.play();
        if (promise && typeof promise.then === "function") {
            promise.then(function () {
                video.pause();
                try { video.currentTime = 0.001; } catch (e) {}
                metaReady = true;
                tick();
            }).catch(function () {
                /* Autoplay blocked by browser policy — mark ready anyway;
                   scrubbing will still attempt currentTime updates.        */
                metaReady = true;
                tick();
            });
        } else {
            /* Legacy browsers without Promise-based play() */
            try { video.pause(); } catch (e) {}
            metaReady = true;
            tick();
        }
    }

    /* After unlock, prevent any subsequent stray playback (e.g. user taps
       video on mobile). We only needed the one unlock play→pause.         */
    video.addEventListener("play", function () {
        if (!unlocked) return;
        /* Use setTimeout to avoid reentrancy with the initial promise     */
        setTimeout(function () {
            try { video.pause(); } catch (e) {}
        }, 0);
    });

    /* ── Metadata ready ─────────────────────────────────────────────────── */
    function onMetadata() {
        if (metaReady) return;
        metaReady = true;
        try { video.pause(); } catch (e) {}
        tick();
    }

    video.addEventListener("loadedmetadata", function () {
        try { video.pause(); } catch (e) {}
        onMetadata();
    }, { once: true });

    /* canplay = browser has enough data to start playing → unlock decoder */
    video.addEventListener("canplay", function () {
        if (!unlocked) unlockDecoder();
    }, { once: true });

    /* loadeddata = first frame decoded → also attempt unlock             */
    video.addEventListener("loadeddata", function () {
        if (!unlocked) unlockDecoder();
        else { metaReady = true; tick(); }
    }, { once: true });

    /* ── Bootstrap from current readyState ──────────────────────────────── */
    if (video.readyState >= 3) {
        /* HAVE_FUTURE_DATA — enough data, try unlock immediately           */
        unlockDecoder();
    } else if (video.readyState >= 1) {
        /* HAVE_METADATA — duration known                                   */
        onMetadata();
    }

    /* 5 s safety net for slow networks */
    setTimeout(function () {
        if (!metaReady) { metaReady = true; tick(); }
        if (!unlocked)  unlockDecoder();
    }, 5000);

    /* ── RAF-throttled scroll / resize listeners ─────────────────────────── */
    var ticking = false;
    function onScroll() {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(function () { tick(); ticking = false; });
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", tick,     { passive: true });
    window.addEventListener("load",   tick);

    /* Re-tick as more video data arrives */
    video.addEventListener("progress", onScroll);

    tick();
})();
