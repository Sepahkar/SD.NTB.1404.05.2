(function () {
  "use strict";

  var TOKEN_KEY = "amoozeshyar_token";
  var EXPIRES_KEY = "amoozeshyar_token_expires";
  var ACCOUNT_KEY = "amoozeshyar_account";

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  window.clearSession = function () {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(EXPIRES_KEY);
    localStorage.removeItem(ACCOUNT_KEY);
  };

  function setSession(data) {
    localStorage.setItem(TOKEN_KEY, data.token);
    localStorage.setItem(EXPIRES_KEY, data.expires_at || "");
    if (data.account) {
      localStorage.setItem(ACCOUNT_KEY, JSON.stringify(data.account));
    }
  }

  function authHeaders() {
    var token = getToken();
    if (!token) return {};
    return { Authorization: "Token " + token };
  }

  window.login = async function (username, password) {
    var data = await apiPost(API.auth.login, { username: username, password: password });
    setSession(data);
    return data;
  };

  window.logout = async function () {
    var token = getToken();
    if (token) {
      try {
        await apiFetch(API.auth.logout, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "same-origin",
        });
      } catch (e) {
        /* ignore */
      }
    }
    clearSession();
    window.location.replace("/");
  };

  window.requireAuth = function () {
    if (!getToken()) {
      window.location.href = "/";
    }
  };

  window.getMe = async function () {
    var token = getToken();
    if (!token) return null;
    try {
      return await apiGet(API.auth.me);
    } catch (e) {
      clearSession();
      window.location.href = "/";
      return null;
    }
  };

  window.populateUserHeader = async function () {
    var me = await getMe();
    if (!me) return;

    var nameEl = document.querySelector(".student-name");
    var idEl = document.querySelector(".student-id");

    if (nameEl) {
      var person = me.person || {};
      var student = me.student || {};
      nameEl.textContent =
        person.full_name ||
        [person.first_name, person.last_name].filter(Boolean).join(" ") ||
        me.account.username;
    }

    if (idEl && me.student) {
      idEl.textContent = "شماره دانشجویی: " + (me.student.student_number || me.account.username);
    } else if (idEl && me.account) {
      idEl.textContent = "نام کاربری: " + me.account.username;
    }
  };

  window.initLoginPage = function () {
    var loginBtn = document.querySelector("#page-login .btn-primary");
    var usernameInput = document.getElementById("student-id");
    var passwordInput = document.getElementById("password");
    var errorBox = document.getElementById("login-error");
    var resetBtn = document.querySelector("#page-forgot .btn-primary");

    if (getToken()) {
      window.location.href = "/dashboard/";
      return;
    }

    if (loginBtn && usernameInput && passwordInput) {
      loginBtn.addEventListener("click", async function (e) {
        e.preventDefault();
        showFormError(errorBox, "");
        loginBtn.disabled = true;
        loginBtn.textContent = "در حال ورود...";
        try {
          await window.login(usernameInput.value.trim(), passwordInput.value);
          window.location.href = "/dashboard/";
        } catch (err) {
          showFormError(errorBox, err.message);
          loginBtn.disabled = false;
          loginBtn.textContent = "ورود به سیستم";
        }
      });

      passwordInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") loginBtn.click();
      });
    }

    if (resetBtn) {
      resetBtn.addEventListener("click", async function (e) {
        e.preventDefault();
        var userInput = document.querySelector("#page-forgot input[type=\"text\"]");
        var answerInput = document.querySelector("#page-forgot input[placeholder*=\"پاسخ\"]");
        var newPassInput = document.querySelector("#page-forgot input[type=\"password\"]");
        var resetError = document.getElementById("reset-error") || errorBox;
        if (!userInput || !answerInput || !newPassInput) return;
        resetBtn.disabled = true;
        try {
          await apiPost(API.auth.passwordReset, {
            username: userInput.value.trim(),
            security_answer: answerInput.value.trim(),
            new_password: newPassInput.value,
          });
          alert("رمز عبور با موفقیت تغییر کرد.");
          if (typeof showPage === "function") showPage("page-login");
        } catch (err) {
          showFormError(resetError, err.message);
        } finally {
          resetBtn.disabled = false;
        }
      });
    }
  };

  window.initProtectedPage = function () {
    requireAuth();
    populateUserHeader();

    if (typeof setActiveNav === "function") {
      setActiveNav();
    }

    document.querySelectorAll(".logout a, .logout").forEach(function (el) {
      el.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/logout/";
      });
    });

    if (typeof initNotifications === "function") {
      initNotifications();
    }
  };
})();
