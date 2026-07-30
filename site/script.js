(() => {
  "use strict";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const navToggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".primary-nav");

  const closeNav = () => {
    if (!navToggle || !nav) return;
    nav.classList.remove("is-open");
    navToggle.setAttribute("aria-expanded", "false");
  };

  navToggle?.addEventListener("click", () => {
    const willOpen = !nav?.classList.contains("is-open");
    nav?.classList.toggle("is-open", willOpen);
    navToggle.setAttribute("aria-expanded", String(willOpen));
  });

  nav?.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeNav));
  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeNav();
  });

  const copyButton = document.querySelector("[data-copy]");
  copyButton?.addEventListener("click", async () => {
    const label = copyButton.querySelector(".copy-label");
    const original = label?.textContent || "clone the library";

    try {
      await navigator.clipboard.writeText(copyButton.dataset.copy || "");
      if (label) label.textContent = "command copied";
    } catch {
      if (label) label.textContent = copyButton.dataset.copy || original;
    }

    window.setTimeout(() => {
      if (label) label.textContent = original;
    }, 2200);
  });

  const nodes = [...document.querySelectorAll(".network-node")];
  const nodeReadout = document.querySelector(".node-readout");

  nodes.forEach((node) => {
    node.addEventListener("click", () => {
      nodes.forEach((item) => item.classList.remove("is-active"));
      node.classList.add("is-active");
      if (nodeReadout) nodeReadout.textContent = node.dataset.nodeMessage || "Signal selected";
    });
  });

  const filters = [...document.querySelectorAll(".filter")];
  const skillRows = [...document.querySelectorAll(".skill-row")];

  filters.forEach((filter) => {
    filter.addEventListener("click", () => {
      const selected = filter.dataset.filter;
      filters.forEach((item) => {
        const isCurrent = item === filter;
        item.classList.toggle("is-active", isCurrent);
        item.setAttribute("aria-pressed", String(isCurrent));
      });

      skillRows.forEach((row) => {
        const visible = selected === "all" || row.dataset.category === selected;
        row.classList.toggle("is-hidden", !visible);
        row.setAttribute("aria-hidden", String(!visible));
        row.tabIndex = visible ? 0 : -1;
      });
    });
  });

  const revealTargets = document.querySelectorAll(
    ".manifesto > *, .section-heading, .skill-row, .protocol-flow article, .code-window, .trust-copy, .trust-radar, .trust-principles li, .impact-grid p, .impact-statement, .cta-section > *"
  );

  if ("IntersectionObserver" in window && !reducedMotion.matches) {
    revealTargets.forEach((element) => element.classList.add("reveal"));
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -5%" });
    revealTargets.forEach((element) => observer.observe(element));
  }

  const network = document.querySelector(".hero-network");
  network?.addEventListener("pointermove", (event) => {
    if (reducedMotion.matches) return;
    const bounds = network.getBoundingClientRect();
    const x = (event.clientX - bounds.left) / bounds.width - 0.5;
    const y = (event.clientY - bounds.top) / bounds.height - 0.5;
    network.style.setProperty("--tilt-x", `${x * 8}px`);
    network.style.setProperty("--tilt-y", `${y * 8}px`);
  });

  network?.addEventListener("pointerleave", () => {
    network.style.setProperty("--tilt-x", "0px");
    network.style.setProperty("--tilt-y", "0px");
  });
})();
