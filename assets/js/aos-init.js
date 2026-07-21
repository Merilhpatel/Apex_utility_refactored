/**
 * aos-init.js
 * ------------
 * Lightweight "Animate On Scroll" implementation, dependency-free
 * (no AOS CDN library is used - this is a small IntersectionObserver
 * polyfill of the same idea).
 *
 * Any element with a `data-aos="fade-up|fade-left|fade-right|zoom-in"`
 * attribute starts hidden/offset (see the `[data-aos]` rules in
 * assets/css/style.css) and receives the `.aos-animate` class the
 * first time it scrolls into view, which triggers the CSS transition.
 *
 * An optional `data-aos-delay="150"` (milliseconds) staggers the
 * animation start per element.
 *
 * Previously this exact block was duplicated as an inline <script> at
 * the bottom of every page's <body>. It now lives here once.
 */
(function () {
  function initAOS() {
    var els = document.querySelectorAll("[data-aos]");

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("aos-animate");
          }
        });
      },
      { threshold: 0.08, rootMargin: "0px 0px -40px 0px" }
    );

    els.forEach(function (el) {
      var delay = parseInt(el.getAttribute("data-aos-delay") || 0, 10);
      if (delay) {
        el.style.transitionDelay = delay + "ms";
      }
      observer.observe(el);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAOS);
  } else {
    initAOS();
  }
})();
