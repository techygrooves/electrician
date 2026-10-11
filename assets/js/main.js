/* ==========================================================================
   Bright Flow Services — Site behavior
   Vanilla JS, no dependencies. Loaded with `defer` on every page.
   ========================================================================== */
/* --------------------------------------------------------------------------
   BUSINESS CONTACT DETAILS: edit here once they are confirmed.
   Every element marked [data-phone] / [data-email] across the site stays
   hidden until a value is set, so no placeholder number is ever published.
   Example: phone: "(407) 555-0100", email: "hello@example.com"
   -------------------------------------------------------------------------- */
var BRIGHT_FLOW_CONTACT = {
  phone: "",
  email: ""
};

(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.remove("no-js");
  root.classList.add("js");

  var prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var desktopQuery = window.matchMedia("(min-width: 1100px)");

  /* ------------------------------------------------------------------------
     Header: solid background once the page scrolls
     ------------------------------------------------------------------------ */
  var header = document.querySelector("[data-header]");
  var callbar = document.querySelector("[data-callbar]");

  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle("is-scrolled", y > 24);
    if (callbar) callbar.classList.toggle("is-visible", y > 480);
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ------------------------------------------------------------------------
     Desktop dropdown (Services)
     Opens on hover with a short close delay, and on click / keyboard.
     ------------------------------------------------------------------------ */
  var dropdownItems = document.querySelectorAll("[data-dropdown]");

  dropdownItems.forEach(function (item) {
    var trigger = item.querySelector("[data-dropdown-trigger]");
    var closeTimer;
    if (!trigger) return;

    function open() {
      clearTimeout(closeTimer);
      dropdownItems.forEach(function (other) { if (other !== item) setOpen(other, false); });
      setOpen(item, true);
    }
    function scheduleClose() {
      clearTimeout(closeTimer);
      closeTimer = setTimeout(function () { setOpen(item, false); }, 160);
    }

    // Hover only for real mice, so a tap on a touch laptop/tablet opens the
    // panel instead of opening and navigating in one go.
    item.addEventListener("pointerenter", function (e) { if (e.pointerType === "mouse" && desktopQuery.matches) open(); });
    item.addEventListener("pointerleave", function (e) { if (e.pointerType === "mouse" && desktopQuery.matches) scheduleClose(); });

    // First tap/click opens the panel (touch, keyboard); once open, the
    // trigger behaves as a normal link to the services overview.
    trigger.addEventListener("click", function (event) {
      if (!item.classList.contains("is-open")) {
        event.preventDefault();
        open();
      }
    });

    trigger.addEventListener("keydown", function (event) {
      if (event.key === "ArrowDown") {
        event.preventDefault();
        open();
        var first = item.querySelector(".dropdown a");
        if (first) first.focus();
      }
    });

    item.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && item.classList.contains("is-open")) {
        setOpen(item, false);
        trigger.focus();
      }
    });

    // Close when focus leaves the menu entirely.
    item.addEventListener("focusout", function (event) {
      if (!item.contains(event.relatedTarget)) setOpen(item, false);
    });
  });

  function setOpen(item, isOpen) {
    item.classList.toggle("is-open", isOpen);
    var trigger = item.querySelector("[data-dropdown-trigger]");
    if (trigger) trigger.setAttribute("aria-expanded", String(isOpen));
  }

  document.addEventListener("click", function (event) {
    dropdownItems.forEach(function (item) {
      if (!item.contains(event.target)) setOpen(item, false);
    });
  });

  /* ------------------------------------------------------------------------
     Mobile menu: off-canvas drawer with focus trap, Esc, and scroll lock
     ------------------------------------------------------------------------ */
  var menu = document.querySelector("[data-mobile-menu]");
  var menuToggle = document.querySelector("[data-menu-toggle]");
  var lastFocused = null;

  function focusables(container) {
    return Array.prototype.filter.call(
      container.querySelectorAll('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'),
      function (el) { return el.offsetParent !== null || el === document.activeElement; }
    );
  }

  function openMenu() {
    if (!menu) return;
    lastFocused = document.activeElement;
    menu.removeAttribute("inert");
    // Next frame so the transition runs after display is restored.
    requestAnimationFrame(function () {
      menu.classList.add("is-open");
    });
    document.body.classList.add("is-locked");
    menuToggle.setAttribute("aria-expanded", "true");
    var closeBtn = menu.querySelector(".mobile-menu__close");
    setTimeout(function () { if (closeBtn) closeBtn.focus(); }, prefersReducedMotion ? 0 : 120);
  }

  function closeMenu(restoreFocus) {
    if (!menu || !menu.classList.contains("is-open")) return;
    menu.classList.remove("is-open");
    menu.setAttribute("inert", "");
    document.body.classList.remove("is-locked");
    menuToggle.setAttribute("aria-expanded", "false");
    if (restoreFocus !== false && lastFocused) lastFocused.focus();
  }

  if (menu && menuToggle) {
    menuToggle.addEventListener("click", openMenu);

    menu.querySelectorAll("[data-menu-close]").forEach(function (el) {
      el.addEventListener("click", function () { closeMenu(); });
    });

    // Close after following an in-page or cross-page link.
    menu.querySelectorAll("a[href]").forEach(function (link) {
      link.addEventListener("click", function () { closeMenu(false); });
    });

    menu.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeMenu();
        return;
      }
      if (event.key !== "Tab") return;
      var items = focusables(menu.querySelector(".mobile-menu__panel"));
      if (!items.length) return;
      var first = items[0];
      var last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });

    // If the viewport grows to desktop width, the drawer is no longer needed.
    var onBreakpoint = function (e) { if (e.matches) closeMenu(false); };
    if (desktopQuery.addEventListener) desktopQuery.addEventListener("change", onBreakpoint);
    else if (desktopQuery.addListener) desktopQuery.addListener(onBreakpoint);
  }

  /* Mobile sub-navigation accordion */
  document.querySelectorAll("[data-subnav-toggle]").forEach(function (toggle) {
    var panel = document.getElementById(toggle.getAttribute("aria-controls"));
    if (!panel) return;
    toggle.addEventListener("click", function () {
      var expanded = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!expanded));
      panel.classList.toggle("is-open", !expanded);
      panel.toggleAttribute("inert", expanded);
    });
  });

  /* ------------------------------------------------------------------------
     Reveal-on-scroll
     ------------------------------------------------------------------------ */
  var revealEls = document.querySelectorAll(".reveal");
  if (prefersReducedMotion || !("IntersectionObserver" in window)) {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  } else {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    revealEls.forEach(function (el) { observer.observe(el); });
  }

  /* ------------------------------------------------------------------------
     Contact details (see BRIGHT_FLOW_CONTACT at the top of this file)
     ------------------------------------------------------------------------ */
  var contact = window.BRIGHT_FLOW_CONTACT || {};
  var phone = String(contact.phone || "").trim();
  var email = String(contact.email || "").trim();

  if (phone) {
    var digits = phone.replace(/[^\d+]/g, "");
    var tel = digits.charAt(0) === "+" ? digits : (digits.length === 10 ? "+1" + digits : digits);
    document.querySelectorAll("[data-phone]").forEach(function (el) {
      if (el.tagName === "A") el.setAttribute("href", "tel:" + tel);
      if (el.hasAttribute("aria-label")) el.setAttribute("aria-label", "Call Bright Flow Services at " + phone);
      el.hidden = false;
    });
    document.querySelectorAll("[data-phone-number]").forEach(function (el) { el.textContent = phone; });
  }
  if (email) {
    document.querySelectorAll("[data-email]").forEach(function (el) {
      if (el.tagName === "A") el.setAttribute("href", "mailto:" + email);
      el.hidden = false;
    });
    document.querySelectorAll("[data-email-address]").forEach(function (el) { el.textContent = email; });
  }

  /* ------------------------------------------------------------------------
     Optional photography: fade in when loaded, remove if the file is missing
     so the designed fallback shows instead of a broken image.
     ------------------------------------------------------------------------ */
  document.querySelectorAll("img[data-optional-img]").forEach(function (img) {
    function loaded() {
      img.classList.add("is-loaded");
      if (img.parentElement) img.parentElement.classList.add("has-media");
    }
    function failed() { img.remove(); }
    if (img.complete) {
      if (img.naturalWidth > 0) loaded(); else failed();
    } else {
      img.addEventListener("load", loaded, { once: true });
      img.addEventListener("error", failed, { once: true });
    }
  });

  /* ------------------------------------------------------------------------
     Footer year
     ------------------------------------------------------------------------ */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
