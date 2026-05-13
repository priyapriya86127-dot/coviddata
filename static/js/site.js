(function () {
  const inner = document.querySelector(".nav-inner");
  const btn = document.getElementById("nav-menu-btn");
  const panel = document.getElementById("site-nav-panel");
  if (!inner || !btn || !panel) return;

  function isCollapsedNav() {
    return window.matchMedia("(max-width: 767px)").matches;
  }

  function setOpen(open) {
    if (!isCollapsedNav()) {
      inner.classList.remove("nav-menu-open");
      document.body.classList.remove("site-nav-locked");
      btn.setAttribute("aria-expanded", "false");
      btn.setAttribute("aria-label", "Open menu");
      return;
    }
    inner.classList.toggle("nav-menu-open", open);
    document.body.classList.toggle("site-nav-locked", open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    btn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  }

  function closeMenu() {
    setOpen(false);
  }

  btn.addEventListener("click", function () {
    setOpen(!inner.classList.contains("nav-menu-open"));
  });

  panel.querySelectorAll("a").forEach(function (a) {
    a.addEventListener("click", function () {
      if (isCollapsedNav()) closeMenu();
    });
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && inner.classList.contains("nav-menu-open")) {
      closeMenu();
    }
  });

  window.matchMedia("(min-width: 768px)").addEventListener("change", function (e) {
    if (e.matches) closeMenu();
  });
})();
