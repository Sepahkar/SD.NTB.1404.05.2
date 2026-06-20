(function () {
  "use strict";

  window.initDashboardPage = async function () {
    try {
      var data = await apiGet(API.pages.dashboard);
      var student = data.student || {};
      setText(".student-name", student.person_name || "—");
      setText(".student-id", "شماره دانشجویی: " + (student.student_number || "—"));

      var taken = student.taken_units || 0;
      var gpa = student.gpa != null ? student.gpa : "—";
      var enrolled = data.enrolled_courses || [];
      var termUnits = enrolled.length;

      var cards = document.querySelectorAll(".status-count");
      if (cards[0]) cards[0].innerHTML = "<span>" + taken + "</span><span>/ 144</span>";
      if (cards[1]) cards[1].innerHTML = "<span>" + gpa + "</span><span>/ 20</span>";
      if (cards[2]) cards[2].innerHTML = "<span>" + termUnits + "</span><span>/ 24</span>";

      if (data.current_term && data.current_term.end_term && cards[3]) {
        var days = daysUntil(data.current_term.end_term);
        if (days != null) cards[3].innerHTML = "<span>" + days + "</span><span> روز</span>";
      }

      var timeBox = document.querySelector(".time-box .text-primary");
      if (timeBox && data.current_term && data.current_term.end_term) {
        var d = daysUntil(data.current_term.end_term);
        if (d != null) timeBox.textContent = d + " روز";
      }

      fillTable(".table tbody", enrolled, function (row, i) {
        return (
          "<tr><th scope=\"row\">" + (i + 1) + "</th>" +
          "<td>" + (row.lesson_title || "—") + "</td>" +
          "<td>—</td><td>—</td><td>—</td></tr>"
        );
      });

      var debt = data.debt_summary || {};
      var debtEl = document.querySelector(".price-box .fw-bold.fs-5");
      if (debtEl) debtEl.textContent = formatCurrency(debt.total_paid || 0);

      var payLink = document.querySelector(".history-card a.text-decoration-none");
      if (payLink) payLink.setAttribute("href", "/payment-history/");

      var finLink = document.querySelector(".payment-card a.btn");
      if (finLink) finLink.setAttribute("href", "/financial/");
    } catch (e) {
      console.error(e);
    }
  };
})();
