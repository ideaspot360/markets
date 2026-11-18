// IdeaSpot360 Markets - Core Interactive Engine
// Dark Mode Toggle, Copy Buttons, and Ultra-Precision Pan-Zoom Lightbox

document.addEventListener("DOMContentLoaded", () => {
  // 1. Dark Mode Management
  const themeToggle = document.getElementById("theme-toggle");
  const currentTheme = localStorage.getItem("theme");

  if (currentTheme) {
    document.documentElement.setAttribute("data-theme", currentTheme);
    updateThemeIcon(currentTheme);
  } else {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    updateThemeIcon(prefersDark ? "dark" : "light");
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      let theme = document.documentElement.getAttribute("data-theme");
      if (!theme) {
        theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      }
      const newTheme = theme === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", newTheme);
      localStorage.setItem("theme", newTheme);
      updateThemeIcon(newTheme);
    });
  }

  function updateThemeIcon(theme) {
    if (!themeToggle) return;
    themeToggle.textContent = theme === "dark" ? "☀️ Light" : "🌙 Dark";
  }

  // 2. Add 'Copy' button to all <pre> blocks
  const preBlocks = document.querySelectorAll("pre");
  preBlocks.forEach((pre) => {
    const button = document.createElement("button");
    button.className = "copy-code-btn";
    button.textContent = "Copy";

    button.addEventListener("click", async () => {
      const code = pre.querySelector("code");
      const textToCopy = code ? code.innerText : pre.innerText;

      try {
        await navigator.clipboard.writeText(textToCopy);
        button.textContent = "Copied!";
        button.style.backgroundColor = "#10b981";
        button.style.color = "#ffffff";
        setTimeout(() => {
          button.textContent = "Copy";
          button.style.backgroundColor = "";
          button.style.color = "";
        }, 2000);
      } catch (err) {
        button.textContent = "Failed";
      }
    });

    pre.appendChild(button);
  });

  // 3. Ultra-Precision Pan-Zoom Lightbox Engine
  initPanZoomLightbox();

  // 4. Responsive Table Wrapper
  const tables = document.querySelectorAll("article.post-content table, .entry-content table");
  tables.forEach((table) => {
    if (!table.parentElement.classList.contains("table-responsive")) {
      const wrapper = document.createElement("div");
      wrapper.className = "table-responsive";
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    }
  });

  // 5. Scrollspy TOC Engine
  const headings = Array.from(document.querySelectorAll(".entry-content h2, .entry-content h3, article.post-content h2, article.post-content h3"));
  const tocNav = document.getElementById("toc-nav");
  if (headings.length > 0 && tocNav) {
    const list = document.createElement("ul");
    list.className = "toc-list";

    headings.forEach((heading, idx) => {
      if (!heading.id) {
        heading.id = `heading-sec-${idx + 1}`;
      }
      const item = document.createElement("li");
      item.className = `toc-item toc-${heading.tagName.toLowerCase()}`;

      const link = document.createElement("a");
      link.href = `#${heading.id}`;
      link.className = "toc-link";
      link.textContent = heading.textContent.replace(/^[#\s]+/, "").trim();

      link.addEventListener("click", (e) => {
        e.preventDefault();
        const target = document.getElementById(heading.id);
        if (target) {
          target.scrollIntoView({ behavior: "smooth", block: "start" });
          history.pushState(null, null, `#${heading.id}`);
        }
      });

      item.appendChild(link);
      list.appendChild(item);
    });

    tocNav.appendChild(list);

    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.id;
            document.querySelectorAll(".toc-link").forEach((l) => {
              l.classList.toggle("active", l.getAttribute("href") === `#${id}`);
            });
          }
        });
      }, {
        rootMargin: "-80px 0px -60% 0px",
        threshold: 0
      });

      headings.forEach((h) => observer.observe(h));
    }
  }

  // 6. Back to Top Button
  const backToTopBtn = document.getElementById("back-to-top-btn");
  if (backToTopBtn) {
    backToTopBtn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // 7. Off-Canvas Drawer Engine
  const menuToggle = document.getElementById("mobile-menu-toggle");
  const drawer = document.getElementById("mobile-drawer");
  const backdrop = document.getElementById("drawer-backdrop");
  const drawerCloseBtn = document.getElementById("drawer-close-btn");

  function openDrawer() {
    if (drawer && backdrop) {
      drawer.classList.add("is-open");
      backdrop.classList.add("is-visible");
      document.body.style.overflow = "hidden";
      if (menuToggle) menuToggle.setAttribute("aria-expanded", "true");
    }
  }

  function closeDrawer() {
    if (drawer && backdrop) {
      drawer.classList.remove("is-open");
      backdrop.classList.remove("is-visible");
      document.body.style.overflow = "";
      if (menuToggle) menuToggle.setAttribute("aria-expanded", "false");
    }
  }

  if (menuToggle) menuToggle.addEventListener("click", openDrawer);
  if (drawerCloseBtn) drawerCloseBtn.addEventListener("click", closeDrawer);
  if (backdrop) backdrop.addEventListener("click", closeDrawer);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && drawer && drawer.classList.contains("is-open")) {
      closeDrawer();
    }
  });

  // Responsive resize: Auto close drawer and restore scroll on desktop viewports
  window.addEventListener("resize", () => {
    if (window.innerWidth >= 1200 && drawer && drawer.classList.contains("is-open")) {
      closeDrawer();
    }
  });

  // 8. Sidebar Scroll Position Restoration (Private Mode Safe)
  const sidebar = document.querySelector(".sidebar-desktop");
  if (sidebar) {
    try {
      const savedPos = sessionStorage.getItem("sidebar_scroll_pos");
      if (savedPos !== null) {
        sidebar.scrollTop = parseInt(savedPos, 10);
      }
      sidebar.addEventListener("scroll", () => {
        try {
          sessionStorage.setItem("sidebar_scroll_pos", sidebar.scrollTop.toString());
        } catch (e) {}
      }, { passive: true });
    } catch (e) {}
  }

  // 9. Category Pills Horizontal Scroll (Active Pill Center Alignment)
  const activePill = document.querySelector(".category-pill.active");
  if (activePill) {
    setTimeout(() => {
      activePill.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
    }, 150);
  }

  // 10. Dual View Mode & Sort Engine (Cards ↔ Compact List & Sort)
  const btnCards = document.getElementById("btn-view-cards");
  const btnCompact = document.getElementById("btn-view-compact");
  const sortSelect = document.getElementById("sort-select");
  const postList = document.querySelector(".post-list, .posts-list, #category-post-list");

  if (postList && (btnCards || btnCompact || sortSelect)) {
    let currentView = "cards";
    try {
      currentView = localStorage.getItem("preferred_view_mode") || "cards";
    } catch (e) {}

    function applyViewMode(mode) {
      if (mode === "compact") {
        postList.classList.add("compact-mode");
        if (btnCompact) btnCompact.classList.add("active");
        if (btnCards) btnCards.classList.remove("active");
      } else {
        postList.classList.remove("compact-mode");
        if (btnCards) btnCards.classList.add("active");
        if (btnCompact) btnCompact.classList.remove("active");
      }
      try {
        localStorage.setItem("preferred_view_mode", mode);
      } catch (e) {}
    }

    applyViewMode(currentView);

    if (btnCards) btnCards.addEventListener("click", () => applyViewMode("cards"));
    if (btnCompact) btnCompact.addEventListener("click", () => applyViewMode("compact"));

    if (sortSelect) {
      sortSelect.addEventListener("change", () => {
        const val = sortSelect.value;
        const cards = Array.from(postList.querySelectorAll(".post-card, article.post-card"));
        if (!cards.length) return;

        cards.sort((a, b) => {
          if (val === "title") {
            const titleA = (a.querySelector("h2, h3") || {}).textContent || "";
            const titleB = (b.querySelector("h2, h3") || {}).textContent || "";
            return titleA.localeCompare(titleB, "en");
          }
          const timeA = (a.querySelector("time") || {}).getAttribute("datetime") || "";
          const timeB = (b.querySelector("time") || {}).getAttribute("datetime") || "";
          if (val === "oldest") {
            return timeA.localeCompare(timeB);
          }
          return timeB.localeCompare(timeA);
        });

        cards.forEach((card) => postList.appendChild(card));
        if (typeof window.recalcPagination === "function") {
          window.recalcPagination();
        }
      });
    }

    // 11. Progressive Slicing Pagination
    window.recalcPagination = function () {
      const allCards = Array.from(postList.querySelectorAll(".post-card, article.post-card"));
      if (allCards.length <= 10) return;

      let existingNav = document.getElementById("post-pagination-nav");
      if (existingNav) existingNav.remove();

      const pageSize = postList.classList.contains("compact-mode") ? 25 : 12;
      const totalPages = Math.ceil(allCards.length / pageSize);
      if (totalPages <= 1) {
        allCards.forEach((c) => (c.style.display = ""));
        return;
      }

      let currentPage = 1;

      function renderPage(page) {
        currentPage = page;
        allCards.forEach((card, idx) => {
          const start = (page - 1) * pageSize;
          const end = page * pageSize;
          card.style.display = idx >= start && idx < end ? "" : "none";
        });

        const nav = document.getElementById("post-pagination-nav");
        if (nav) {
          nav.querySelectorAll(".page-btn").forEach((btn) => {
            const p = parseInt(btn.getAttribute("data-page"), 10);
            btn.classList.toggle("active", p === currentPage);
          });
        }
      }

      const pagContainer = document.createElement("div");
      pagContainer.id = "post-pagination-nav";
      pagContainer.className = "pagination-container";

      for (let p = 1; p <= totalPages; p++) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = `page-btn${p === 1 ? " active" : ""}`;
        btn.setAttribute("data-page", p.toString());
        btn.textContent = p.toString();
        btn.addEventListener("click", () => {
          renderPage(p);
          postList.scrollIntoView({ behavior: "smooth", block: "start" });
        });
        pagContainer.appendChild(btn);
      }

      postList.parentNode.insertBefore(pagContainer, postList.nextSibling);
      renderPage(1);
    };

    window.recalcPagination();
  }

  // 12. In-Sidebar Instant Search & Special Tracks Engine
  const searchInputs = [
    document.getElementById("sidebar-search-input"),
    document.getElementById("drawer-search-input")
  ].filter(Boolean);

  const clearBtn = document.getElementById("sidebar-search-clear");
  let searchIndex = null;
  let isFetchingIndex = false;

  async function loadSearchIndex() {
    if (searchIndex || isFetchingIndex) return searchIndex;
    isFetchingIndex = true;
    try {
      const res = await fetch("/search.json");
      if (res.ok) {
        searchIndex = await res.json();
      }
    } catch (e) {
      console.warn("Failed to load search.json", e);
    } finally {
      isFetchingIndex = false;
    }
    return searchIndex;
  }

  loadSearchIndex();

  function executeSearch(query) {
    if (!query) return;
    const cleanQ = query.trim().toLowerCase();
    if (!cleanQ) return;

    const isHome = window.location.pathname === "/" || window.location.pathname.endsWith("/index.html");
    if (!isHome) {
      window.location.href = `/#search=${encodeURIComponent(cleanQ)}`;
      return;
    }

    loadSearchIndex().then((index) => {
      if (!index || !index.length) return;

      const results = index.filter((item) => {
        const t = (item.title || "").toLowerCase();
        const c = (item.category || "").toLowerCase();
        const s = (item.summary || "").toLowerCase();
        const tags = Array.isArray(item.tags) ? item.tags.join(" ").toLowerCase() : "";
        return t.includes(cleanQ) || c.includes(cleanQ) || s.includes(cleanQ) || tags.includes(cleanQ);
      });

      renderSearchResults(cleanQ, results);
      history.pushState(null, null, `#search=${encodeURIComponent(cleanQ)}`);
    });
  }

  function renderSearchResults(query, results) {
    const mainCol = document.getElementById("main-content") || document.querySelector(".site-main-column");
    if (!mainCol) return;

    let searchSection = document.getElementById("search-results-section");
    if (!searchSection) {
      searchSection = document.createElement("div");
      searchSection.id = "search-results-section";
      searchSection.style.marginBottom = "40px";
      mainCol.insertBefore(searchSection, mainCol.firstChild);
    }

    searchSection.innerHTML = `
      <div class="search-status-bar">
        <span>🔍 Search results for <strong>"${query}"</strong>: <strong>${results.length}</strong> publication(s)</span>
        <button type="button" class="reset-btn" id="btn-search-reset">✕ Reset Search</button>
      </div>
      <div class="posts-list" id="search-post-list">
        ${
          results.length === 0
            ? '<p style="text-align: center; color: var(--text-muted); padding: 30px;">No matching institutional research found.</p>'
            : results
                .map(
                  (r) => `
          <article class="post-card" style="background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 20px; margin-bottom: 16px;">
            <div style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 6px;">
              <time>📅 ${r.date}</time>
              <span>&bull;</span>
              <span class="category-badge">${r.category || "Research"}</span>
            </div>
            <h3 style="margin: 0 0 8px 0; font-size: 1.2rem; font-weight: 700;">
              <a href="${r.url}" style="color: var(--text-color); text-decoration: none;">${r.title}</a>
            </h3>
            <p style="color: var(--text-muted); font-size: 0.92rem; margin: 0; line-height: 1.5;">${r.summary}</p>
          </article>
        `
                )
                .join("")
        }
      </div>
    `;

    const resetBtn = document.getElementById("btn-search-reset");
    if (resetBtn) {
      resetBtn.addEventListener("click", () => {
        searchSection.remove();
        searchInputs.forEach((inp) => (inp.value = ""));
        if (clearBtn) clearBtn.style.display = "none";
        history.pushState(null, null, window.location.pathname);
      });
    }

    searchSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  let debounceTimer = null;
  searchInputs.forEach((input) => {
    input.addEventListener("input", (e) => {
      const val = e.target.value;
      if (clearBtn) clearBtn.style.display = val ? "block" : "none";

      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        if (val.trim().length >= 2) {
          executeSearch(val);
        }
      }, 250);
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        clearTimeout(debounceTimer);
        executeSearch(e.target.value);
      }
    });
  });

  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      searchInputs.forEach((inp) => (inp.value = ""));
      clearBtn.style.display = "none";
      const sec = document.getElementById("search-results-section");
      if (sec) sec.remove();
      history.pushState(null, null, window.location.pathname);
    });
  }

  function handleUrlHash() {
    const hash = window.location.hash;
    if (hash && hash.startsWith("#search=")) {
      const q = decodeURIComponent(hash.replace("#search=", ""));
      searchInputs.forEach((inp) => (inp.value = q));
      if (clearBtn) clearBtn.style.display = "block";
      executeSearch(q);
    }
  }

  window.addEventListener("popstate", handleUrlHash);
  handleUrlHash();
});

function initPanZoomLightbox() {
  const images = document.querySelectorAll(".entry-content img, article.post-content img");
  if (!images.length) return;

  // Create Modal DOM Elements once
  const modal = document.createElement("div");
  modal.className = "panzoom-modal";
  modal.innerHTML = `
    <div class="panzoom-toolbar">
      <span class="panzoom-scale-badge" id="pz-scale">100%</span>
      <button class="panzoom-btn" id="pz-zoom-out" title="Zoom Out (−)">−</button>
      <button class="panzoom-btn" id="pz-zoom-in" title="Zoom In (+)">+</button>
      <button class="panzoom-btn" id="pz-reset" title="Reset View (R)">↺</button>
      <button class="panzoom-btn" id="pz-close" title="Close (Esc)" style="margin-left: 6px; font-weight: bold;">✕</button>
    </div>
    <div class="panzoom-viewport" id="pz-viewport">
      <img class="panzoom-image" id="pz-image" src="" alt="Zoomable Image">
    </div>
    <div class="panzoom-hint">🖱️ Wheel / +, -: Zoom | Drag / Arrow Keys: Pan | Double-Click: 2.5x | 0 / R: Reset | ESC: Close</div>
  `;
  document.body.appendChild(modal);

  const viewport = modal.querySelector("#pz-viewport");
  const pzImage = modal.querySelector("#pz-image");
  const scaleBadge = modal.querySelector("#pz-scale");
  const btnIn = modal.querySelector("#pz-zoom-in");
  const btnOut = modal.querySelector("#pz-zoom-out");
  const btnReset = modal.querySelector("#pz-reset");
  const btnClose = modal.querySelector("#pz-close");

  let scale = 1.0;
  let translateX = 0;
  let translateY = 0;
  let isDragging = false;
  let hasDragged = false;
  let dragStartX = 0;
  let dragStartY = 0;
  const DRAG_THRESHOLD = 5;
  let startX = 0;
  let startY = 0;
  let lastPinchDist = null;

  const MIN_SCALE = 0.5;
  const MAX_SCALE = 6.0;

  function updateTransform(smooth = false) {
    pzImage.style.transition = smooth ? "transform 0.2s cubic-bezier(0.16, 1, 0.3, 1)" : "none";
    pzImage.style.transform = `translate3d(${translateX}px, ${translateY}px, 0) scale(${scale})`;
    scaleBadge.textContent = `${Math.round(scale * 100)}%`;
  }

  function resetZoom() {
    scale = 1.0;
    translateX = 0;
    translateY = 0;
    updateTransform(true);
  }

  function openModal(src, alt) {
    pzImage.src = src;
    pzImage.alt = alt || "Financial Diagram";
    resetZoom();
    modal.classList.add("active");
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    modal.classList.remove("active");
    document.body.style.overflow = "";
    setTimeout(() => {
      pzImage.src = "";
    }, 250);
  }

  // Bind clicks to all article images
  images.forEach((img) => {
    img.addEventListener("click", () => {
      openModal(img.src, img.alt);
    });
  });

  // Zoom In / Out functions
  function zoomAt(targetScale, focalX = 0, focalY = 0) {
    const clampedScale = Math.min(Math.max(targetScale, MIN_SCALE), MAX_SCALE);
    if (clampedScale === scale) return;

    const ratio = clampedScale / scale;
    translateX = focalX - ratio * (focalX - translateX);
    translateY = focalY - ratio * (focalY - translateY);
    scale = clampedScale;
    updateTransform(false);
  }

  // Mouse Wheel Precision Zoom (Focal Point Centered)
  viewport.addEventListener("wheel", (e) => {
    e.preventDefault();
    const rect = viewport.getBoundingClientRect();
    const mouseX = e.clientX - rect.left - rect.width / 2;
    const mouseY = e.clientY - rect.top - rect.height / 2;

    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.85;
    zoomAt(scale * zoomFactor, mouseX, mouseY);
  }, { passive: false });

  // Mouse Drag Pan
  viewport.addEventListener("mousedown", (e) => {
    if (e.button !== 0) return; // Only left click
    if (e.target.closest(".panzoom-toolbar, .lightbox-toolbar")) return;
    isDragging = true;
    hasDragged = false;
    dragStartX = e.clientX;
    dragStartY = e.clientY;
    startX = e.clientX - translateX;
    startY = e.clientY - translateY;
    viewport.classList.add("dragging");
  });

  window.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    const moveDist = Math.hypot(e.clientX - dragStartX, e.clientY - dragStartY);
    if (moveDist > DRAG_THRESHOLD) {
      hasDragged = true;
    }
    translateX = e.clientX - startX;
    translateY = e.clientY - startY;
    updateTransform(false);
  });

  window.addEventListener("mouseup", () => {
    if (isDragging) {
      isDragging = false;
      viewport.classList.remove("dragging");
      setTimeout(() => {
        hasDragged = false;
      }, 50);
    }
  });

  // Double Click Smart Zoom (2.5x Toggle)
  viewport.addEventListener("dblclick", (e) => {
    if (e.target.closest(".panzoom-toolbar")) return;
    if (scale > 1.2) {
      resetZoom();
    } else {
      const rect = viewport.getBoundingClientRect();
      const mouseX = e.clientX - rect.left - rect.width / 2;
      const mouseY = e.clientY - rect.top - rect.height / 2;
      zoomAt(2.5, mouseX, mouseY);
      updateTransform(true);
    }
  });

  // Mobile Pinch & Pan
  viewport.addEventListener("touchstart", (e) => {
    if (e.touches.length === 1) {
      isDragging = true;
      hasDragged = false;
      dragStartX = e.touches[0].clientX;
      dragStartY = e.touches[0].clientY;
      startX = e.touches[0].clientX - translateX;
      startY = e.touches[0].clientY - translateY;
    } else if (e.touches.length === 2) {
      isDragging = false;
      lastPinchDist = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
    }
  }, { passive: true });

  viewport.addEventListener("touchmove", (e) => {
    if (e.touches.length === 1 && isDragging) {
      const moveDist = Math.hypot(e.touches[0].clientX - dragStartX, e.touches[0].clientY - dragStartY);
      if (moveDist > DRAG_THRESHOLD) {
        hasDragged = true;
      }
      translateX = e.touches[0].clientX - startX;
      translateY = e.touches[0].clientY - startY;
      updateTransform(false);
    } else if (e.touches.length === 2 && lastPinchDist) {
      const dist = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
      const ratio = dist / lastPinchDist;
      zoomAt(scale * ratio, 0, 0);
      lastPinchDist = dist;
    }
  }, { passive: true });

  viewport.addEventListener("touchend", () => {
    isDragging = false;
    lastPinchDist = null;
    setTimeout(() => {
      hasDragged = false;
    }, 50);
  });

  // Toolbar Actions
  btnIn.addEventListener("click", () => {
    zoomAt(scale * 1.3, 0, 0);
    updateTransform(true);
  });

  btnOut.addEventListener("click", () => {
    zoomAt(scale * 0.7, 0, 0);
    updateTransform(true);
  });

  btnReset.addEventListener("click", resetZoom);
  btnClose.addEventListener("click", closeModal);

  // Close on Backdrop Click
  viewport.addEventListener("click", (e) => {
    if (hasDragged) {
      e.stopPropagation();
      return;
    }
    if (e.target === viewport) {
      closeModal();
    }
  });

  // Keyboard Navigation & Shortcuts (+, -, 0, R, Arrow keys, ESC)
  window.addEventListener("keydown", (e) => {
    if (!modal.classList.contains("active")) return;

    if (e.key === "Escape") {
      closeModal();
    } else if (e.key === "+" || e.key === "=") {
      e.preventDefault();
      zoomAt(scale * 1.25, 0, 0);
      updateTransform(true);
    } else if (e.key === "-" || e.key === "_") {
      e.preventDefault();
      zoomAt(scale * 0.8, 0, 0);
      updateTransform(true);
    } else if (e.key === "0" || e.key === "r" || e.key === "R") {
      e.preventDefault();
      resetZoom();
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      translateX += 50;
      updateTransform(true);
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      translateX -= 50;
      updateTransform(true);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      translateY += 50;
      updateTransform(true);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      translateY -= 50;
      updateTransform(true);
    }
  });
}
