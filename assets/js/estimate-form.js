/* ==========================================================================
   Bright Flow Services — Request an Estimate form
   Client-side validation, honeypot check, and submission to the endpoint set
   in BRIGHT_FLOW_CONTACT.formEndpoint (assets/js/main.js) or in the form's
   data-endpoint attribute. No endpoint = no pretend success: the visitor is
   told online requests are not connected yet and their entries are kept.
   ========================================================================== */
(function () {
  "use strict";

  var form = document.querySelector("[data-estimate-form]");
  if (!form) return;

  var config = window.BRIGHT_FLOW_CONTACT || {};
  var endpoint = String(form.getAttribute("data-endpoint") || config.formEndpoint || "").trim();

  var summary = form.querySelector("[data-form-summary]");
  var summaryList = summary ? summary.querySelector("ul") : null;
  var submitBtn = form.querySelector("[type=submit]");
  var panel = form.closest("[data-form-panel]") || form.parentElement;
  var states = {
    success: panel.querySelector('[data-form-state="success"]'),
    error: form.querySelector('[data-form-state="error"]'),
    offline: form.querySelector('[data-form-state="unconfigured"]')
  };

  /* ------------------------------------------------------------------------
     Service dropdown: filter by service type, keep a copy of every option
     ------------------------------------------------------------------------ */
  var typeSelect = form.elements.service_type;
  var serviceSelect = form.elements.service;
  var groups = {};
  Array.prototype.forEach.call(serviceSelect.querySelectorAll("optgroup"), function (g) {
    groups[g.getAttribute("data-type")] = g.cloneNode(true);
  });
  var tailOptions = Array.prototype.filter.call(serviceSelect.children, function (el) {
    return el.tagName === "OPTION" && el.value !== "";
  }).map(function (o) { return o.cloneNode(true); });

  function rebuildServices() {
    var type = typeSelect.value;
    var keep = serviceSelect.value;
    while (serviceSelect.children.length > 1) serviceSelect.removeChild(serviceSelect.lastChild);
    Object.keys(groups).forEach(function (key) {
      if (!type || type === "not-sure" || type === key) serviceSelect.appendChild(groups[key].cloneNode(true));
    });
    tailOptions.forEach(function (o) { serviceSelect.appendChild(o.cloneNode(true)); });
    serviceSelect.value = keep;
    if (serviceSelect.value !== keep) serviceSelect.value = "";
  }
  typeSelect.addEventListener("change", rebuildServices);

  // Prefill from links such as contact.html?service=ev-charger-installation#booking
  var params = new URLSearchParams(window.location.search);
  var wantedType = params.get("type");
  var wantedService = params.get("service");
  if (wantedService) {
    Object.keys(groups).forEach(function (key) {
      if (groups[key].querySelector('option[value="' + wantedService.replace(/"/g, "") + '"]')) wantedType = key;
    });
  }
  if (wantedType && typeSelect.querySelector('option[value="' + wantedType.replace(/"/g, "") + '"]')) {
    typeSelect.value = wantedType;
  }
  rebuildServices();
  if (wantedService) {
    serviceSelect.value = wantedService;
    if (serviceSelect.value !== wantedService) serviceSelect.value = "";
  }

  /* ------------------------------------------------------------------------
     Character counter
     ------------------------------------------------------------------------ */
  var description = form.elements.description;
  var counter = form.querySelector("[data-char-count]");
  function updateCount() {
    if (!counter) return;
    var max = parseInt(description.getAttribute("maxlength"), 10);
    counter.textContent = description.value.length + " / " + max;
  }
  description.addEventListener("input", updateCount);
  updateCount();

  /* ------------------------------------------------------------------------
     Validation
     ------------------------------------------------------------------------ */
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  var rules = {
    name: function (v) {
      if (!v) return "Please enter your full name.";
      if (v.length < 2) return "Please enter at least 2 characters.";
      return "";
    },
    email: function (v) {
      if (!v) return "Please enter your email address.";
      if (!EMAIL_RE.test(v)) return "Please enter a valid email address, like name@example.com.";
      return "";
    },
    phone: function (v) {
      if (!v) return "Please enter your phone number.";
      var digits = v.replace(/\D/g, "");
      if (digits.length === 11 && digits.charAt(0) === "1") digits = digits.slice(1);
      if (digits.length !== 10) return "Please enter a 10-digit phone number, like (555) 555-0123.";
      return "";
    },
    location: function (v) {
      if (v && v.length < 3) return "Please enter a city name or a 5-digit ZIP code.";
      if (/^\d+$/.test(v) && !/^\d{5}$/.test(v)) return "ZIP codes have 5 digits.";
      return "";
    }
  };

  function fieldWrap(input) { return input.closest(".field"); }

  function setError(input, message) {
    var wrap = fieldWrap(input);
    if (!wrap) return;
    var errorEl = wrap.querySelector(".field__error");
    wrap.classList.toggle("is-invalid", !!message);
    input.setAttribute("aria-invalid", message ? "true" : "false");
    if (errorEl) {
      errorEl.textContent = message;
      errorEl.hidden = !message;
    }
  }

  function validateField(input) {
    var rule = rules[input.name];
    if (!rule) return "";
    var message = rule(input.value.trim());
    setError(input, message);
    return message;
  }

  Object.keys(rules).forEach(function (name) {
    var input = form.elements[name];
    if (!input) return;
    // Validate on leaving a field, then live once it has been flagged.
    input.addEventListener("blur", function () {
      if (input.value.trim() || input.getAttribute("aria-invalid") === "true") validateField(input);
    });
    input.addEventListener("input", function () {
      if (input.getAttribute("aria-invalid") === "true") validateField(input);
    });
  });

  function validateAll() {
    var problems = [];
    Object.keys(rules).forEach(function (name) {
      var input = form.elements[name];
      if (!input) return;
      var message = validateField(input);
      if (message) problems.push({ input: input, message: message });
    });
    return problems;
  }

  function showSummary(problems) {
    if (!summary) return;
    summaryList.innerHTML = "";
    problems.forEach(function (p) {
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = "#" + p.input.id;
      a.textContent = p.message;
      a.addEventListener("click", function (e) {
        e.preventDefault();
        p.input.focus();
      });
      li.appendChild(a);
      summaryList.appendChild(li);
    });
    summary.hidden = false;
    summary.focus();
  }

  /* ------------------------------------------------------------------------
     States
     ------------------------------------------------------------------------ */
  function hideStates() {
    if (summary) summary.hidden = true;
    if (states.error) states.error.hidden = true;
    if (states.offline) states.offline.hidden = true;
  }

  function setBusy(busy) {
    form.setAttribute("aria-busy", busy ? "true" : "false");
    submitBtn.disabled = busy;
    submitBtn.classList.toggle("is-loading", busy);
  }

  function showSuccess() {
    form.reset();
    rebuildServices();
    updateCount();
    form.hidden = true;
    if (states.success) {
      states.success.hidden = false;
      states.success.focus();
    }
  }

  function showError(message) {
    if (!states.error) return;
    var msg = states.error.querySelector("[data-error-message]");
    if (msg && message) msg.textContent = message;
    states.error.hidden = false;
    states.error.focus();
  }

  var again = panel.querySelector("[data-form-reset]");
  if (again) {
    again.addEventListener("click", function () {
      states.success.hidden = true;
      form.hidden = false;
      form.elements.name.focus();
    });
  }

  /* ------------------------------------------------------------------------
     Submit
     ------------------------------------------------------------------------ */
  var startedAt = Date.now();

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    hideStates();

    var problems = validateAll();
    if (problems.length) {
      showSummary(problems);
      return;
    }

    // Honeypot: real visitors never see or fill this field.
    var trap = form.elements._gotcha;
    if (trap && trap.value) {
      showSuccess();
      return;
    }

    if (!endpoint) {
      states.offline.hidden = false;
      states.offline.focus();
      return;
    }

    var data = new FormData(form);
    data.delete("_gotcha");
    data.append("page", window.location.pathname);
    data.append("seconds_on_page", String(Math.round((Date.now() - startedAt) / 1000)));

    setBusy(true);
    fetch(endpoint, { method: "POST", body: data, headers: { Accept: "application/json" } })
      .then(function (response) {
        if (response.ok) return showSuccess();
        return response.json().catch(function () { return {}; }).then(function (body) {
          var detail = body && (body.error || (body.errors && body.errors[0] && body.errors[0].message));
          showError(detail ? "The request could not be sent: " + detail : null);
        });
      })
      .catch(function () {
        showError("We couldn't reach the server. Please check your connection and try again.");
      })
      .then(function () { setBusy(false); });
  });
})();
