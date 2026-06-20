(function () {
  "use strict";

  window.formatNumber = function (n) {
    if (n === null || n === undefined || n === "") return "—";
    var num = Number(n);
    if (isNaN(num)) return String(n);
    return num.toLocaleString("fa-IR");
  };

  window.formatCurrency = function (n) {
    return formatNumber(n) + " تومان";
  };

  window.formatDate = function (iso) {
    if (!iso) return "—";
    try {
      var d = new Date(iso);
      if (isNaN(d.getTime())) return String(iso).slice(0, 10);
      return d.toLocaleDateString("fa-IR");
    } catch (e) {
      return String(iso).slice(0, 10);
    }
  };

  window.setText = function (selector, value) {
    var el = document.querySelector(selector);
    if (el) el.textContent = value != null && value !== "" ? value : "—";
  };

  window.fillTable = function (tbodySelector, rows, renderRow) {
    var tbody = document.querySelector(tbodySelector);
    if (!tbody) return;
    tbody.innerHTML = "";
    if (!rows || !rows.length) {
      var tr = document.createElement("tr");
      tr.innerHTML = '<td colspan="99" class="text-secondary text-center">موردی یافت نشد</td>';
      tbody.appendChild(tr);
      return;
    }
    rows.forEach(function (row, i) {
      tbody.insertAdjacentHTML("beforeend", renderRow(row, i));
    });
  };

  window.showFormError = function (el, message) {
    if (!el) return;
    el.textContent = message || "";
    el.style.display = message ? "block" : "none";
  };

  window.daysUntil = function (endDateStr) {
    if (!endDateStr) return null;
    var end = new Date(endDateStr);
    var now = new Date();
    var diff = Math.ceil((end - now) / (1000 * 60 * 60 * 24));
    return diff > 0 ? diff : 0;
  };
})();
