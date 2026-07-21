/**
 * main.js
 * --------
 * Shared front-end behaviour for every page of the Apex Utility site:
 *   1. Sticky header shadow + "back to top" button visibility on scroll
 *   2. Mobile hamburger menu open/close
 *   3. FAQ accordion (services detail pages)
 *   4. Animated stat counters (Why Us / Home page)
 *   5. Contact form -> pre-filled WhatsApp deep link
 *
 * This file is loaded on every page via:
 *   <script src="./assets/js/main.js"></script>   (root pages)
 *   <script src="../assets/js/main.js"></script>  (services/*.html pages)
 *
 * All selectors below use `document.getElementById` / `querySelectorAll`
 * and quietly no-op when an element isn't present on the current page,
 * so this single file safely covers every page without modification.
 */
(function () {
  // ---------------------------------------------------------------------
  // 1. Sticky header shadow + back-to-top button visibility
  // ---------------------------------------------------------------------
  var header = document.getElementById("site-hdr");
  var toTopBtn = document.getElementById("toTop");

  function onScroll() {
    var scrolled = window.scrollY;

    if (header) {
      header.classList.toggle("shadow-lg", scrolled > 12);
      header.classList.toggle("border-b", scrolled > 12);
      header.classList.toggle("border-brand-line", scrolled > 12);
    }
    if (toTopBtn) {
      toTopBtn.classList.toggle("show", scrolled > 450);
    }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll(); // set initial state on load

  if (toTopBtn) {
    toTopBtn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // ---------------------------------------------------------------------
  // 2. Mobile hamburger menu
  // ---------------------------------------------------------------------
  var mobileBtn = document.getElementById("mob-btn");
  var mobileMenu = document.getElementById("mob-menu");
  var mobileIcon = document.getElementById("mob-ico");

  if (mobileBtn) {
    mobileBtn.addEventListener("click", function () {
      var isOpen = mobileMenu.classList.toggle("open");
      mobileBtn.setAttribute("aria-expanded", isOpen);
      mobileIcon.className = isOpen
        ? "fa-solid fa-xmark text-xl"
        : "fa-solid fa-bars text-xl";
    });
  }

  // Close the mobile menu whenever any menu link is tapped
  document.querySelectorAll(".mob-lnk").forEach(function (link) {
    link.addEventListener("click", function () {
      if (mobileMenu) mobileMenu.classList.remove("open");
      if (mobileIcon) mobileIcon.className = "fa-solid fa-bars text-xl";
    });
  });

  // ---------------------------------------------------------------------
  // 3. FAQ accordion (service detail pages)
  // ---------------------------------------------------------------------
  document.querySelectorAll(".faq-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var item = btn.closest(".faq-it");
      var wasOpen = item.classList.contains("open");

      // only one FAQ item open at a time
      document.querySelectorAll(".faq-it.open").forEach(function (openItem) {
        openItem.classList.remove("open");
      });
      if (!wasOpen) item.classList.add("open");
    });
  });

  // ---------------------------------------------------------------------
  // 4. Animated stat counters
  // ---------------------------------------------------------------------
  var counters = document.querySelectorAll(".ctr");

  if (counters.length) {
    var runCounters = function () {
      counters.forEach(function (counter) {
        var target = parseInt(counter.dataset.to, 10);
        var suffix = counter.dataset.suf || "";
        var prefix = counter.dataset.pre || "";
        var current = 0;
        var step = target / 110; // ~110 animation frames

        var timer = setInterval(function () {
          current = Math.min(current + step, target);
          counter.textContent =
            prefix + Math.round(current).toLocaleString() + suffix;
          if (current >= target) clearInterval(timer);
        }, 16);
      });
    };

    var counterWrap = document.querySelector(".ctr-wrap");
    if (counterWrap) {
      // start counting only once the stat block scrolls into view
      new IntersectionObserver(
        function (entries) {
          if (entries[0].isIntersecting) {
            counterWrap.classList.add("vis");
            runCounters();
          }
        },
        { threshold: 0.3 }
      ).observe(counterWrap);
    } else {
      runCounters();
    }
  }

  // ---------------------------------------------------------------------
  // 5. Contact form -> WhatsApp deep link
  // ---------------------------------------------------------------------
  var contactForm = document.getElementById("cf");

  if (contactForm) {
    contactForm.addEventListener("submit", function (e) {
      e.preventDefault();

      var name = (document.getElementById("cf-n")?.value || "").trim();
      var company = (document.getElementById("cf-co")?.value || "").trim();
      var email = (document.getElementById("cf-e")?.value || "").trim();
      var phone = (document.getElementById("cf-p")?.value || "").trim();
      var message = (document.getElementById("cf-m")?.value || "").trim();

      var text =
        "Hello Apex Utility,\n\n" +
        "Name: " + name + "\n" +
        (company ? "Company: " + company + "\n" : "") +
        (email ? "Email: " + email + "\n" : "") +
        "Phone: " + phone + "\n\n" +
        "Message:\n" + message;

      window.location.href =
        "https://wa.me/917600176756?text=" + encodeURIComponent(text);
    });
  }
})();
