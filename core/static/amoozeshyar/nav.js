(function () {
  "use strict";

  var PATH_TO_NAV_HREF = {
    "/dashboard/": "/dashboard/",
    "/teachers/": "/teachers/",
    "/course-selection/": "/course-selection/",
    "/course-search/": "/course-search/",
    "/add-drop/": "/add-drop/",
    "/emergency-removal/": "/emergency-removal/",
    "/full-transcript/": "/full-transcript/",
    "/semester-transcript/": "/full-transcript/",
    "/grades/": "/full-transcript/",
    "/grade-objection/": "/grade-objection/",
    "/grade-objection-form/": "/grade-objection/",
    "/financial/": "/financial/",
    "/debts/": "/financial/",
    "/payment-history/": "/financial/",
    "/loan-request/": "/financial/",
    "/student-requests/": "/emergency-removal/",
    "/leave-request/": "/emergency-removal/",
  };

  function normalizePath(path) {
    if (!path) return "/";
    if (path.indexOf("http") === 0) {
      try {
        path = new URL(path).pathname;
      } catch (e) {
        return path;
      }
    }
    if (path.charAt(path.length - 1) !== "/") path += "/";
    return path;
  }

  function resolveActiveHref() {
    var path = normalizePath(window.location.pathname);
    return PATH_TO_NAV_HREF[path] || path;
  }

  function hrefMatches(linkHref, activeHref) {
    if (!linkHref) return false;
    var link = linkHref;
    var active = activeHref;

    if (link.indexOf("http") === 0 || link.indexOf("//") === 0) {
      try {
        link = new URL(link, window.location.origin).pathname + new URL(link, window.location.origin).search;
      } catch (e) {
        return false;
      }
    }

    if (active.indexOf("?") >= 0) {
      return link === active;
    }

    var linkPath = link.split("?")[0];
    var activePath = active.split("?")[0];
    return normalizePath(linkPath) === normalizePath(activePath);
  }

  window.setActiveNav = function () {
    var activeHref = resolveActiveHref();
    document.querySelectorAll(".menu ul li").forEach(function (li) {
      li.classList.remove("active");
    });

    var matched = false;
    document.querySelectorAll(".menu a[href]").forEach(function (anchor) {
      if (hrefMatches(anchor.getAttribute("href"), activeHref)) {
        var li = anchor.closest("li");
        if (li && !matched) {
          li.classList.add("active");
          matched = true;
        }
      }
    });
  };
})();
