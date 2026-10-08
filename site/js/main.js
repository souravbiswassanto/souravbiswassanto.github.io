/* Saurov Chandra Biswas — portfolio
   Progressive enhancement only. Every feature here degrades to a working page. */
(function () {
  "use strict";
  document.documentElement.classList.remove("no-js");

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------------------------------------- theme */
  var root = document.documentElement;
  var toggle = document.querySelector("[data-theme-toggle]");

  function current() {
    return root.getAttribute("data-theme") ||
      (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  function apply(mode) {
    root.setAttribute("data-theme", mode);
    if (toggle) toggle.setAttribute("aria-label", "Switch to " + (mode === "dark" ? "light" : "dark") + " theme");
    try { localStorage.setItem("theme", mode); } catch (e) { /* private mode */ }
  }
  if (toggle) toggle.addEventListener("click", function () {
    apply(current() === "dark" ? "light" : "dark");
  });

  /* ------------------------------------------------------------- sticky header */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () { header.setAttribute("data-stuck", String(window.scrollY > 8)); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ------------------------------------------------------------- reveal */
  var revealables = document.querySelectorAll(".reveal");
  if (reduced || !("IntersectionObserver" in window)) {
    revealables.forEach(function (el) { el.classList.add("is-in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-in");
        io.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    revealables.forEach(function (el) { io.observe(el); });
  }

  /* ------------------------------------------------------------- counters */
  var counters = document.querySelectorAll("[data-count]");
  function runCount(el) {
    var target = parseFloat(el.getAttribute("data-count"));
    var prefix = el.getAttribute("data-prefix") || "";
    var suffix = el.getAttribute("data-suffix") || "";
    if (reduced || !isFinite(target)) { el.textContent = prefix + target.toLocaleString("en-US") + suffix; return; }
    el.textContent = prefix + "0" + suffix;
    var start = performance.now(), dur = 1100;
    function step(now) {
      var p = Math.min((now - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = prefix + Math.round(target * eased).toLocaleString("en-US") + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  if ("IntersectionObserver" in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        runCount(e.target);
        cio.unobserve(e.target);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { cio.observe(el); });
  } else {
    counters.forEach(runCount);
  }

  /* ------------------------------------------------------------- command palette */
  var backdrop = document.querySelector("[data-palette]");
  if (!backdrop) return;
  var input = backdrop.querySelector("input");
  var list = backdrop.querySelector("ul");
  var items = [].slice.call(list.querySelectorAll("li"));
  var opener = document.querySelector("[data-palette-open]");
  var lastFocus = null;
  var active = -1;

  function visible() { return items.filter(function (li) { return !li.hidden; }); }

  function setActive(i) {
    var vis = visible();
    if (!vis.length) { active = -1; return; }
    active = (i + vis.length) % vis.length;
    items.forEach(function (li) { li.removeAttribute("data-active"); });
    vis[active].setAttribute("data-active", "true");
    vis[active].scrollIntoView({ block: "nearest" });
  }

  function filter() {
    var q = input.value.trim().toLowerCase();
    items.forEach(function (li) {
      li.hidden = q ? li.getAttribute("data-search").indexOf(q) === -1 : false;
    });
    var empty = backdrop.querySelector(".p-empty");
    if (empty) empty.hidden = visible().length > 0;
    setActive(0);
  }

  function open() {
    lastFocus = document.activeElement;
    backdrop.hidden = false;
    input.value = "";
    filter();
    input.focus();
  }
  function close() {
    backdrop.hidden = true;
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  if (opener) opener.addEventListener("click", open);
  input.addEventListener("input", filter);

  backdrop.addEventListener("click", function (e) { if (e.target === backdrop) close(); });

  document.addEventListener("keydown", function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      backdrop.hidden ? open() : close();
      return;
    }
    if (backdrop.hidden) return;
    if (e.key === "Escape") { e.preventDefault(); close(); }
    else if (e.key === "ArrowDown") { e.preventDefault(); setActive(active + 1); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setActive(active - 1); }
    else if (e.key === "Enter") {
      var vis = visible();
      if (active > -1 && vis[active]) { e.preventDefault(); vis[active].querySelector("a").click(); }
    }
  });
})();
