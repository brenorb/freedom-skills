(function () {
  "use strict";

  const buttons = Array.from(document.querySelectorAll(".stage-button"));
  const stages = Array.from(document.querySelectorAll(".stage-block"));
  const status = document.querySelector(".filter-status");
  const resetButton = document.querySelector("[data-filter-reset]");
  const noResults = document.querySelector(".no-results");
  const poster = document.querySelector(".hero-poster");

  if (!buttons.length || !stages.length || !status) return;

  const labels = {
    all: "all 15 skills across the commons",
    signal: "2 skills in the Signal Garden",
    spark: "5 skills in the Spark Pavilion",
    shelter: "3 skills in the Shelter Tent",
    archive: "4 skills in the Memory Grove",
    workshop: "1 skill in the Makers’ Yard"
  };

  function selectStage(filter, focusButton) {
    let visibleCount = 0;

    buttons.forEach(function (button) {
      const selected = button.dataset.filter === filter;
      button.classList.toggle("is-active", selected);
      button.setAttribute("aria-pressed", String(selected));
      if (selected && focusButton) button.focus();
    });

    stages.forEach(function (stage) {
      const visible = filter === "all" || stage.dataset.category === filter;
      stage.hidden = !visible;
      if (visible) visibleCount += 1;
    });

    status.innerHTML = "<span>Now showing:</span> " + labels[filter];
    noResults.hidden = visibleCount > 0;

    if (window.history && window.history.replaceState) {
      const url = new URL(window.location.href);
      if (filter === "all") url.searchParams.delete("stage");
      else url.searchParams.set("stage", filter);
      window.history.replaceState({}, "", url);
    }
  }

  buttons.forEach(function (button, index) {
    button.addEventListener("click", function () {
      selectStage(button.dataset.filter, false);
    });

    button.addEventListener("keydown", function (event) {
      if (event.key !== "ArrowRight" && event.key !== "ArrowLeft" && event.key !== "Home" && event.key !== "End") return;
      event.preventDefault();

      let nextIndex = index;
      if (event.key === "ArrowRight") nextIndex = (index + 1) % buttons.length;
      if (event.key === "ArrowLeft") nextIndex = (index - 1 + buttons.length) % buttons.length;
      if (event.key === "Home") nextIndex = 0;
      if (event.key === "End") nextIndex = buttons.length - 1;
      selectStage(buttons[nextIndex].dataset.filter, true);
    });
  });

  if (resetButton) {
    resetButton.addEventListener("click", function () {
      selectStage("all", true);
    });
  }

  const initialFilter = new URLSearchParams(window.location.search).get("stage");
  if (labels[initialFilter]) selectStage(initialFilter, false);

  const allowsMotion = window.matchMedia("(prefers-reduced-motion: no-preference)").matches;
  const hasFinePointer = window.matchMedia("(pointer: fine)").matches;

  if (poster && allowsMotion && hasFinePointer) {
    poster.addEventListener("pointermove", function (event) {
      const bounds = poster.getBoundingClientRect();
      const x = (event.clientX - bounds.left) / bounds.width - 0.5;
      const y = (event.clientY - bounds.top) / bounds.height - 0.5;
      poster.style.transform = "rotateX(" + (-y * 4).toFixed(2) + "deg) rotateY(" + (x * 5).toFixed(2) + "deg) rotateZ(3.5deg)";
    });

    poster.addEventListener("pointerleave", function () {
      poster.style.transform = "rotate(3.5deg)";
    });
  }
}());
