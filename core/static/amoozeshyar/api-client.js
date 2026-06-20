(function () {
  "use strict";

  window.API = {
    auth: {
      login: "/api/v1/auth/login/",
      logout: "/api/v1/auth/logout/",
      me: "/api/v1/auth/me/",
      passwordReset: "/api/v1/auth/password/reset/",
    },
    pages: {
      dashboard: "/api/v1/pages/dashboard/",
      semesterTranscript: "/api/v1/pages/semester-transcript/",
      fullTranscript: "/api/v1/pages/full-transcript/",
      grades: "/api/v1/pages/grades/",
      courseSelection: "/api/v1/pages/course-selection/",
      addDrop: "/api/v1/pages/add-drop/",
      financial: "/api/v1/pages/financial/",
      paymentHistory: "/api/v1/pages/payment-history/",
      loanRequest: "/api/v1/pages/loan-request/",
      studentRequests: "/api/v1/pages/student-requests/",
      leaveRequest: "/api/v1/pages/leave-request/",
      teachers: "/api/v1/pages/teachers/",
      gradeObjection: "/api/v1/pages/grade-objection/",
    },
  };

  function getToken() {
    return localStorage.getItem("amoozeshyar_token");
  }

  function parseError(data) {
    if (!data) return "خطای ناشناخته";
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) return data.detail.join(" ");
    var parts = [];
    Object.keys(data).forEach(function (key) {
      var val = data[key];
      if (Array.isArray(val)) parts.push(key + ": " + val.join(", "));
      else if (typeof val === "string") parts.push(val);
    });
    return parts.join(" ") || "خطا در انجام عملیات";
  }

  window.apiFetch = async function (url, options) {
    options = options || {};
    var headers = Object.assign({ Accept: "application/json" }, options.headers || {});
    if (options.body && !(options.body instanceof FormData)) {
      headers["Content-Type"] = headers["Content-Type"] || "application/json";
      if (typeof options.body === "object") {
        options.body = JSON.stringify(options.body);
      }
    }
    var token = getToken();
    if (token) headers.Authorization = "Token " + token;

    var response = await fetch(url, Object.assign({}, options, { headers: headers }));
    var data = null;
    var text = await response.text();
    if (text) {
      try {
        data = JSON.parse(text);
      } catch (e) {
        data = { detail: text };
      }
    }

    if (response.status === 401) {
      if (typeof window.clearSession === "function") window.clearSession();
      window.location.href = "/";
      throw new Error("نشست منقضی شده است.");
    }

    if (!response.ok) {
      throw new Error(parseError(data));
    }
    return data;
  };

  window.apiGet = function (url) {
    return apiFetch(url, { method: "GET" });
  };

  window.apiPost = function (url, body) {
    return apiFetch(url, { method: "POST", body: body });
  };
})();
