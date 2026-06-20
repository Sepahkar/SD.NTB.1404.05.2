(function () {
  "use strict";

  var cachedAnnouncements = null;
  var modalEl = null;

  function escapeHtml(text) {
    if (!text) return "";
    var d = document.createElement("div");
    d.textContent = text;
    return d.innerHTML;
  }

  window.renderAnnouncementItems = function (announcements) {
    if (!announcements || !announcements.length) {
      return (
        '<p class="announcements-empty text-secondary text-center py-4 mb-0">' +
        "اطلاعیه‌ای برای نمایش وجود ندارد.</p>"
      );
    }
    return announcements
      .map(function (a) {
        var dateStr =
          a.publish_date && typeof formatDate === "function" ? formatDate(a.publish_date) : "";
        var meta = dateStr
          ? '<span class="announcement-date text-muted small d-block mt-1">' + dateStr + "</span>"
          : "";
        return (
          '<div class="announcement-item' +
          (a.is_urgent ? " urgent" : "") +
          '">' +
          '<div class="announcement-item-head">' +
          "<strong>" +
          escapeHtml(a.title || a.summary || "اطلاعیه") +
          "</strong>" +
          (a.is_urgent ? '<span class="announcement-urgent-badge">فوری</span>' : "") +
          "</div>" +
          meta +
          '<p class="mb-0 text-secondary small mt-2">' +
          escapeHtml(a.body || a.summary || "") +
          "</p></div>"
        );
      })
      .join("");
  };

  window.setAnnouncementsCache = function (announcements) {
    cachedAnnouncements = announcements || [];
    updateBadge();
  };

  function ensureModal() {
    if (modalEl) return modalEl;

    var overlay = document.createElement("div");
    overlay.id = "university-announcements-modal";
    overlay.className = "announcements-modal";
    overlay.innerHTML =
      '<div class="announcements-modal-backdrop" data-dismiss="announcements"></div>' +
      '<div class="announcements-modal-panel" role="dialog" aria-modal="true" aria-labelledby="announcements-modal-title">' +
      '<div class="announcements-modal-header">' +
      '<h4 id="announcements-modal-title"><i class="fas fa-bullhorn"></i> اطلاعیه‌های دانشگاه</h4>' +
      '<button type="button" class="announcements-modal-close" aria-label="بستن">&times;</button>' +
      "</div>" +
      '<div class="announcements-modal-body" id="announcements-modal-list">' +
      '<p class="text-secondary text-center py-4 mb-0">در حال بارگذاری...</p>' +
      "</div></div>";

    document.body.appendChild(overlay);
    modalEl = overlay;

    overlay.querySelector(".announcements-modal-backdrop").addEventListener("click", closeModal);
    overlay.querySelector(".announcements-modal-close").addEventListener("click", closeModal);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && overlay.classList.contains("is-open")) {
        closeModal();
      }
    });

    return overlay;
  }

  function renderModalContent() {
    var list = document.getElementById("announcements-modal-list");
    if (!list) return;
    if (!cachedAnnouncements) {
      list.innerHTML = '<p class="text-secondary text-center py-4 mb-0">در حال بارگذاری...</p>';
      return;
    }
    list.innerHTML = renderAnnouncementItems(cachedAnnouncements);
  }

  function openModal() {
    var modal = ensureModal();
    modal.classList.add("is-open");
    document.body.classList.add("announcements-modal-open");
    document.querySelectorAll(".cancel-icon").forEach(function (el) {
      el.classList.add("is-active");
    });
    renderModalContent();
    loadAnnouncements()
      .then(function () {
        renderModalContent();
      })
      .catch(function (err) {
        var list = document.getElementById("announcements-modal-list");
        if (list) {
          list.innerHTML =
            '<p class="text-danger text-center py-4 mb-0">' + escapeHtml(err.message) + "</p>";
        }
      });
  }

  function closeModal() {
    if (modalEl) {
      modalEl.classList.remove("is-open");
      document.body.classList.remove("announcements-modal-open");
      document.querySelectorAll(".cancel-icon").forEach(function (el) {
        el.classList.remove("is-active");
      });
    }
  }

  function updateBadge() {
    var urgentCount = cachedAnnouncements
      ? cachedAnnouncements.filter(function (a) {
          return a.is_urgent;
        }).length
      : 0;

    document.querySelectorAll(".notification-icon").forEach(function (icon) {
      var existing = icon.querySelector(".notification-badge");
      if (urgentCount > 0) {
        if (!existing) {
          existing = document.createElement("span");
          existing.className = "notification-badge";
          icon.appendChild(existing);
        }
        existing.textContent = urgentCount > 9 ? "9+" : String(urgentCount);
      } else if (existing) {
        existing.remove();
      }
    });
  }

  function loadAnnouncements() {
    if (cachedAnnouncements) {
      return Promise.resolve(cachedAnnouncements);
    }
    return apiGet(API.pages.dashboard).then(function (data) {
      cachedAnnouncements = data.announcements || [];
      updateBadge();
      return cachedAnnouncements;
    });
  }

  window.initNotifications = function () {
    document.querySelectorAll(".notification-icon").forEach(function (icon) {
      if (icon.dataset.notificationsBound) return;
      icon.dataset.notificationsBound = "1";
      icon.setAttribute("role", "button");
      icon.setAttribute("tabindex", "0");
      icon.setAttribute("aria-label", "اطلاعیه‌های دانشگاه");
      icon.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        openModal();
      });
      icon.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          openModal();
        }
      });
    });

    document.querySelectorAll(".cancel-icon").forEach(function (icon) {
      if (icon.dataset.notificationsBound) return;
      icon.dataset.notificationsBound = "1";
      icon.setAttribute("role", "button");
      icon.setAttribute("tabindex", "0");
      icon.setAttribute("aria-label", "بستن اطلاعیه‌ها");
      icon.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        closeModal();
      });
    });

    loadAnnouncements().catch(function () {
      /* badge optional */
    });
  };
})();
