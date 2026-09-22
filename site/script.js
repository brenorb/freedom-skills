(() => {
  "use strict";

  const search = document.querySelector("#skill-search");
  const skillItems = [...document.querySelectorAll("#skill-list > li")];
  const filterButtons = [...document.querySelectorAll(".filter")];
  const visibleCount = document.querySelector("#visible-count");
  const emptyState = document.querySelector("#empty-state");
  const clock = document.querySelector("#clock");
  const dialog = document.querySelector("#command-dialog");
  const commandTrigger = document.querySelector(".command-trigger");
  const commandSearch = document.querySelector("#command-search");
  const commandResults = document.querySelector("#command-results");

  let activeFilter = "all";
  let activeCommandIndex = 0;
  let commandItems = [];

  const normalize = (value) => value.toLowerCase().trim();

  function applyDirectoryFilters() {
    const query = normalize(search.value);
    let count = 0;

    skillItems.forEach((item) => {
      const categoryMatch = activeFilter === "all" || item.dataset.category.split(" ").includes(activeFilter);
      const searchable = `${item.dataset.search} ${item.textContent}`.toLowerCase();
      const queryMatch = !query || searchable.includes(query);
      const visible = categoryMatch && queryMatch;
      item.hidden = !visible;
      if (visible) count += 1;
    });

    visibleCount.textContent = String(count).padStart(2, "0");
    emptyState.hidden = count !== 0;
  }

  function setFilter(nextFilter) {
    activeFilter = nextFilter;
    filterButtons.forEach((button) => {
      const isActive = button.dataset.filter === nextFilter;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });
    applyDirectoryFilters();
  }

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => setFilter(button.dataset.filter));
  });

  search.addEventListener("input", applyDirectoryFilters);
  search.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      search.value = "";
      setFilter("all");
      search.blur();
    }
  });

  function updateClock() {
    const now = new Date();
    const time = now.toISOString().slice(11, 19);
    clock.textContent = time;
    clock.dateTime = time;
  }

  updateClock();
  window.setInterval(updateClock, 1000);

  const sectionCommands = [
    { code: "01", name: "Service directory", detail: "Browse all skills", href: "#directory" },
    { code: "02", name: "Operating protocol", detail: "How skills work", href: "#protocol" },
    { code: "03", name: "Trust boundary", detail: "Safety and verification", href: "#trust" },
    { code: "04", name: "Community works", detail: "Contribute a skill", href: "#contribute" },
    { code: "↗", name: "Source repository", detail: "GitHub", href: "https://github.com/brenorb/freedom-skills" }
  ];

  const skillCommands = skillItems.map((item) => {
    const link = item.querySelector("a");
    return {
      code: item.querySelector(".skill-code").textContent,
      name: item.querySelector(".skill-name").childNodes[0].textContent.trim(),
      detail: item.querySelector(".skill-route")?.textContent || "SERVICE",
      href: link.getAttribute("href")
    };
  });

  const allCommands = [...sectionCommands, ...skillCommands];

  function selectCommand(index) {
    if (!commandItems.length) return;
    activeCommandIndex = (index + commandItems.length) % commandItems.length;
    commandItems.forEach((item, itemIndex) => {
      item.setAttribute("aria-selected", String(itemIndex === activeCommandIndex));
    });
    commandItems[activeCommandIndex].scrollIntoView({ block: "nearest" });
  }

  function renderCommands() {
    const query = normalize(commandSearch.value);
    const matches = allCommands.filter((command) =>
      !query || `${command.code} ${command.name} ${command.detail}`.toLowerCase().includes(query)
    );

    commandResults.replaceChildren();

    if (!matches.length) {
      const message = document.createElement("p");
      message.className = "empty-state";
      message.textContent = "NO ROUTE FOUND";
      commandResults.append(message);
      commandItems = [];
      return;
    }

    matches.forEach((command) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "command-item";
      button.setAttribute("role", "option");
      button.innerHTML = `<strong>${command.code}</strong><span>${command.name}</span><small>${command.detail}</small>`;
      button.addEventListener("click", () => openCommand(command));
      button.dataset.href = command.href;
      commandResults.append(button);
    });

    commandItems = [...commandResults.querySelectorAll(".command-item")];
    selectCommand(0);
  }

  function openCommand(command) {
    closeCommandDialog();
    window.location.href = command.href;
  }

  function openCommandDialog() {
    if (dialog.open) {
      commandSearch.focus();
      return;
    }
    renderCommands();
    if (typeof dialog.showModal === "function") {
      dialog.showModal();
    } else {
      dialog.setAttribute("open", "");
    }
    window.requestAnimationFrame(() => commandSearch.focus());
  }

  function closeCommandDialog() {
    if (typeof dialog.close === "function" && dialog.open) {
      dialog.close();
    } else {
      dialog.removeAttribute("open");
    }
  }

  commandTrigger.addEventListener("click", openCommandDialog);
  commandSearch.addEventListener("input", renderCommands);
  commandSearch.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      selectCommand(activeCommandIndex + 1);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      selectCommand(activeCommandIndex - 1);
    } else if (event.key === "Enter" && commandItems.length) {
      event.preventDefault();
      commandItems[activeCommandIndex].click();
    }
  });

  dialog.addEventListener("close", () => {
    commandSearch.value = "";
    commandTrigger.focus();
  });

  document.addEventListener("keydown", (event) => {
    const target = event.target;
    const isTyping = target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target.isContentEditable;

    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      openCommandDialog();
      return;
    }

    if (event.key === "/" && !isTyping && !dialog.open) {
      event.preventDefault();
      search.focus();
    }

    if (event.key === "Escape" && dialog.open) {
      closeCommandDialog();
    }
  });
})();
