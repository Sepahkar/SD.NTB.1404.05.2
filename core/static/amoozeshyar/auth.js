(function () {
  "use strict";

  var TOKEN_KEY = "amoozeshyar_token";
  var EXPIRES_KEY = "amoozeshyar_token_expires";
  var ACCOUNT_KEY = "amoozeshyar_account";

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function setSession(data) {
    localStorage.setItem(TOKEN_KEY, data.token);
    localStorage.setItem(EXPIRES_KEY, data.expires_at || "");
    if (data.account) {
      localStorage.setItem(ACCOUNT_KEY, JSON.stringify(data.account));
    }
  }

  function clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(EXPIRES_KEY);
    localStorage.removeItem(ACCOUNT_KEY);
  }

  function authHeaders() {
    var token = getToken();
    if (!token) return {};
    return { Authorization: "Token " + token };
  }

  window.login = async function (username, password) {
    var response = await fetch("/api/v1/auth/login/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username, password: password }),
    });

    var data = await response.json().catch(function () {
      return {};
    });

    if (!response.ok) {
      throw new Error(data.detail || "نام کاربری یا رمز عبور اشتباه است.");
    }

    setSession(data);
    return data;
  };

  window.logout = async function () {
    var token = getToken();
    if (token) {
      try {
        await fetch("/api/v1/auth/logout/", {
          method: "POST",
          headers: Object.assign({ "Content-Type": "application/json" }, authHeaders()),
          credentials: "same-origin",
        });
      } catch (e) {
        /* ignore network errors on logout */
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

    var response = await fetch("/api/v1/auth/me/", {
      headers: authHeaders(),
    });

    if (!response.ok) {
      clearSession();
      window.location.href = "/";
      return null;
    }

    return response.json();
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

    if (!loginBtn || !usernameInput || !passwordInput) return;

    if (getToken()) {
      window.location.href = "/dashboard/";
      return;
    }

    loginBtn.addEventListener("click", async function (e) {
      e.preventDefault();
      if (errorBox) {
        errorBox.textContent = "";
        errorBox.style.display = "none";
      }

      loginBtn.disabled = true;
      loginBtn.textContent = "در حال ورود...";

      try {
        await window.login(usernameInput.value.trim(), passwordInput.value);
        window.location.href = "/dashboard/";
      } catch (err) {
        if (errorBox) {
          errorBox.textContent = err.message;
          errorBox.style.display = "block";
        } else {
          alert(err.message);
        }
        loginBtn.disabled = false;
        loginBtn.textContent = "ورود به سیستم";
      }
    });

    passwordInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") loginBtn.click();
    });
  };

  window.initProtectedPage = function () {
    requireAuth();
    populateUserHeader();

    document.querySelectorAll(".logout a, .logout").forEach(function (el) {
      el.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/logout/";
      });
    });
  };
})();
