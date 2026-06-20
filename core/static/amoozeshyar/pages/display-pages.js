(function () {
  "use strict";

  function formatTime(t) {
    if (!t) return "—";
    var parts = String(t).split(":");
    return parts[0] + ":" + parts[1];
  }

  function scheduleText(row) {
    var day = row.class_day || "—";
    var tm = formatTime(row.class_time);
    return day + (tm !== "—" ? " — " + tm : "");
  }

  function setProgressBar(cardIndex, pct) {
    var fills = document.querySelectorAll(".progress-fill");
    if (fills[cardIndex]) fills[cardIndex].style.width = Math.min(100, pct) + "%";
  }

  window.initDashboardPage = async function () {
    try {
      var data = await apiGet(API.pages.dashboard);
      var student = data.student || {};
      var debt = data.debt_summary || {};
      var enrolled = data.enrolled_courses || [];
      var totalUnitsGoal = 144;
      var termUnitsGoal = 24;
      var termDaysGoal = 120;

      setText(".student-name", student.person_name || "—");
      setText(".student-id", "شماره دانشجویی: " + (student.student_number || "—"));

      var taken = student.taken_units || 0;
      var gpa = student.gpa != null ? student.gpa : "—";
      var termUnits = enrolled.reduce(function (s, c) {
        return s + (c.lesson_units || 3);
      }, 0);

      var cards = document.querySelectorAll(".status-count");
      if (cards[0]) cards[0].innerHTML = "<span>" + taken + "</span><span>/ " + totalUnitsGoal + "</span>";
      if (cards[1]) cards[1].innerHTML = "<span>" + gpa + "</span><span>/ 20</span>";
      if (cards[2]) cards[2].innerHTML = "<span>" + termUnits + "</span><span>/ " + termUnitsGoal + "</span>";

      setProgressBar(0, (taken / totalUnitsGoal) * 100);
      setProgressBar(1, (Number(gpa) / 20) * 100);
      setProgressBar(2, (termUnits / termUnitsGoal) * 100);

      if (data.current_term && data.current_term.end_term) {
        var days = daysUntil(data.current_term.end_term);
        if (days != null && cards[3]) {
          cards[3].innerHTML = "<span>" + days + "</span><span>/ " + termDaysGoal + "</span>";
          setProgressBar(3, ((termDaysGoal - days) / termDaysGoal) * 100);
        }
        var timeBox = document.querySelector(".time-box .text-primary");
        if (timeBox && days != null) timeBox.textContent = days + " روز";
      }

      fillTable(".table tbody", enrolled, function (row, i) {
        return (
          "<tr><th scope=\"row\">" + (i + 1) + "</th>" +
          "<td class=\"px-3\">" + (row.lesson_title || "—") + "</td>" +
          "<td class=\"px-4\">" + (row.teacher_name || "—") + "</td>" +
          "<td class=\"px-4\">" + scheduleText(row) + "</td>" +
          "<td class=\"px-5\">" + (row.class_location || "—") + "</td></tr>"
        );
      });

      var debtEls = document.querySelectorAll(".price-box .fw-bold.fs-5");
      if (debtEls[0]) debtEls[0].textContent = formatCurrency(debt.total_pending_amount || 0);
      if (debtEls[1]) debtEls[1].textContent = formatCurrency(debt.term_tuition || 25000000);

      var histBody = document.querySelector(".history-card tbody");
      if (histBody) {
        fillTable(".history-card tbody", data.recent_payments || [], function (p) {
          var ok = p.is_confirmed;
          var cls = ok ? "bg-success-subtle text-success" : "bg-danger-subtle text-danger";
          var lbl = ok ? "موفق" : "ناموفق";
          return (
            "<tr><td class=\"px-2\"><i class=\"far fa-calendar\"></i> " + formatDate(p.payment_datetime) + "</td>" +
            "<td class=\"px-2\">" + (p.reference_bank || "پرداخت") + "</td>" +
            "<td class=\"px-2\">" + formatNumber(p.amount) + "</td>" +
            "<td class=\"px-2 " + cls + " price-status\"><i class=\"fas fa-caret-left\"></i>" + lbl + "</td></tr>"
          );
        });
      }

      var annRoot = document.getElementById("announcements-list");
      if (annRoot && data.announcements) {
        annRoot.innerHTML =
          typeof renderAnnouncementItems === "function"
            ? renderAnnouncementItems(data.announcements)
            : data.announcements
                .map(function (a) {
                  return (
                    "<div class=\"announcement-item" + (a.is_urgent ? " urgent" : "") + "\">" +
                    "<strong>" + (a.title || a.summary || "اطلاعیه") + "</strong>" +
                    "<p class=\"mb-0 text-secondary small\">" + (a.body || a.summary || "") + "</p></div>"
                  );
                })
                .join("");
        if (typeof setAnnouncementsCache === "function") {
          setAnnouncementsCache(data.announcements);
        }
      }

      document.querySelectorAll(".history-card a.text-decoration-none").forEach(function (a) {
        a.setAttribute("href", "/payment-history/");
      });
      var finBtn = document.querySelector(".payment-card a.btn");
      if (finBtn) finBtn.setAttribute("href", "/financial/");
    } catch (e) {
      console.error(e);
    }
  };

  document.addEventListener("click", function (e) {
    var toggle = e.target.closest("#teachers-filter-toggle");
    if (!toggle) return;
    e.preventDefault();
    var panel = document.getElementById("teachers-filter-panel");
    if (panel) panel.classList.toggle("is-open");
  });

  window.initTeachersPage = async function () {
    var grid = document.querySelector(".cards-grid");
    var allTeachers = [];

    function renderTeachers(list) {
      if (!grid) return;
      grid.innerHTML = list
        .map(function (t, i) {
          var interest = (t.research_interests && t.research_interests[0]) || "مهندسی کامپیوتر";
          var name = t.person_name || t.full_name || "استاد";
          return (
            "<div class=\"instructor-card\">" +
            "<div class=\"card-avatar\"><img src=\"https://api.dicebear.com/7.x/adventurer/svg?seed=" + i + "\" alt=\"avatar\"/></div>" +
            "<h3 class=\"card-name\">" + name + "</h3>" +
            "<p class=\"card-field\">مهندسی کامپیوتر — نرم‌افزار</p>" +
            "<p class=\"card-tag\">" + interest + "</p>" +
            "<div class=\"card-stats\"><span class=\"students-count\">" + ((t.recent_classes || []).length * 15 + 20) + " دانشجو</span>" +
            "<span class=\"rating\">★ 4." + (7 + (i % 3)) + "</span></div></div>"
          );
        })
        .join("") || "<p class=\"text-center\">استادی یافت نشد.</p>";
    }

    function applyFilters() {
      var q = (document.getElementById("teachers-search") || {}).value || "";
      q = q.trim().toLowerCase();
      var field = (document.getElementById("teachers-field-filter") || {}).value || "";
      var filtered = allTeachers.filter(function (t) {
        var name = (t.person_name || t.full_name || "").toLowerCase();
        var interest = ((t.research_interests && t.research_interests[0]) || "").toLowerCase();
        var matchQ = !q || name.indexOf(q) >= 0 || interest.indexOf(q) >= 0;
        var matchField = !field || interest.indexOf(field) >= 0 || name.indexOf(field) >= 0;
        return matchQ && matchField;
      });
      renderTeachers(filtered);
    }

    var toggleBtn = document.getElementById("teachers-filter-toggle");
    var panel = document.getElementById("teachers-filter-panel");
    if (toggleBtn && panel) {
      toggleBtn.addEventListener("click", function (e) {
        e.preventDefault();
        panel.classList.toggle("is-open");
      });
    }
    var searchInput = document.getElementById("teachers-search");
    var fieldSelect = document.getElementById("teachers-field-filter");
    if (searchInput) searchInput.addEventListener("input", applyFilters);
    if (fieldSelect) fieldSelect.addEventListener("change", applyFilters);

    try {
      var data = await apiGet(API.pages.teachers);
      allTeachers = data.teachers || [];
      renderTeachers(allTeachers);
    } catch (e) {
      console.error(e);
    }
  };

  window.initFinancialPage = async function () {
    try {
      var data = await apiGet(API.pages.financial);
      var payments = data.payments || [];
      var confirmed = payments.filter(function (p) { return p.is_confirmed; });
      var pending = payments.filter(function (p) { return !p.is_confirmed; });
      var totalPaid = data.total_paid || 0;
      var totalPending = data.total_pending || 0;

      var stats = document.querySelectorAll(".state .stat-value");
      if (stats[0]) stats[0].textContent = payments.length;
      if (stats[1]) stats[1].textContent = formatNumber(totalPaid);
      if (stats[2]) stats[2].textContent = pending.length + " قسط";
      if (stats[3]) stats[3].textContent = formatNumber(totalPending);

      document.querySelectorAll(".action-card-btn").forEach(function (btn) {
        var card = btn.closest(".action-card");
        if (!card) return;
        if (card.querySelector("h3") && card.querySelector("h3").textContent.indexOf("تاریخچه") >= 0) {
          btn.onclick = function () { window.location.href = "/payment-history/"; };
        } else if (card.querySelector("h3") && card.querySelector("h3").textContent.indexOf("وام") >= 0) {
          btn.onclick = function () { window.location.href = "/loan-request/"; };
        }
      });
    } catch (e) {
      console.error(e);
    }
  };

  window.initPaymentHistoryPage = async function () {
    try {
      var data = await apiGet(API.pages.paymentHistory);
      var payments = data.payments || [];
      var confirmed = payments.filter(function (p) { return p.is_confirmed; });
      var failed = payments.filter(function (p) { return !p.is_confirmed; });
      var totalAmount = payments.reduce(function (s, p) { return s + (p.amount || 0); }, 0);

      var nums = document.querySelectorAll(".stat-number");
      if (nums[0]) nums[0].textContent = payments.length;
      if (nums[1]) nums[1].textContent = formatNumber(totalAmount);
      if (nums[2]) nums[2].textContent = confirmed.length;
      if (nums[3]) nums[3].textContent = failed.length;

      fillTable(".payments-table tbody", payments, function (p) {
        var ok = p.is_confirmed;
        return (
          "<tr><td class=\"title-cell\">پرداخت " + (p.reference_bank || "") + " — " + (p.tracking_code || "") + "</td>" +
          "<td class=\"amount-cell\">" + formatNumber(p.amount) + "</td>" +
          "<td class=\"date-cell\">" + formatDate(p.payment_datetime) + "</td>" +
          "<td class=\"status-cell\"><span class=\"status-badge " + (ok ? "status-badge--success" : "status-badge--danger") + "\">" +
          (ok ? "موفق" : "ناموفق") + "</span></td></tr>"
        );
      });
    } catch (e) {
      console.error(e);
    }
  };

  window.initDebtsPage = async function () {
    try {
      var data = await apiGet(API.pages.financial);
      var pending = (data.payments || []).filter(function (p) { return !p.is_confirmed; });
      var stats = document.querySelectorAll(".stat-value");
      if (stats[0]) stats[0].textContent = pending.length + " قسط";
      if (stats[1]) stats[1].innerHTML = formatNumber(data.total_paid || 0) + ' <span class="currency">تومان</span>';
      if (stats[2]) stats[2].innerHTML = formatNumber(data.total_pending || 0) + ' <span class="currency">تومان</span>';

      fillTable(".table-box table tbody, table tbody", pending, function (p, i) {
        return (
          "<tr><td>" + (i + 1) + "</td><td>بدهی " + (p.reference_bank || "") + "</td>" +
          "<td>" + formatNumber(p.amount) + "</td><td>" + formatDate(p.payment_datetime) + "</td>" +
          "<td><span class=\"status-badge unpaid\">معوق</span></td></tr>"
        );
      });
    } catch (e) {
      console.error(e);
    }
  };

  window.initFullTranscriptPage = async function () {
    try {
      var data = await apiGet(API.pages.fullTranscript);
      var s = data.student || {};
      var name = s.person_name || "—";

      setText("#profile-name", name);
      setText("#profile-student-number", "شماره دانشجویی: " + (s.student_number || "—"));
      setText("#profile-gpa", "معدل کل: " + (data.gpa != null ? data.gpa : "—"));
      setText("#profile-units", "واحد گذرانده: " + (data.taken_units || 0));

      function setField(key, label, value) {
        var el = document.querySelector('[data-field="' + key + '"]');
        if (el) el.textContent = label + " : " + (value != null && value !== "" ? value : "—");
      }

      setField("full-name", "نام و نام خانوادگی", name);
      setField("national-id", "کدملی", s.national_id || "—");
      setField("birth-cert", "شماره شناسنامه", "—");
      setField("birth-date", "تاریخ تولد", "—");
      setField("gender", "جنسیت", "—");
      setField("father-name", "نام پدر", "—");
      setField("military", "وضعیت نظام وظیفه", "—");
      setField("health", "وضعیت جسمانی", "—");
      setField("quota", "سهمیه", "—");
      setField("effective-units", "كل تعداد واحد موثر", data.taken_units || 0);
      setField("passed-units", "كل تعداد گذرانده شده", data.taken_units || 0);
      setField("gpa", "معدل کل", data.gpa != null ? data.gpa : "—");
      setField("student-number", "شماره دانشجویی", s.student_number || "—");
      setField("field", "رشته تحصیلی", "مهندسی نرم‌افزار");
      setField("degree", "مقطع تحصیلی", "کارشناسی");
      setField("faculty", "دانشکده", "مهندسی کامپیوتر");
      setField("admission-term", "نیمسال پذیرش", "—");
      setField("admission-type", "نوع پذیرش", "—");
      setField("education-mode", "شیوه آموزش", "حضوری");
      setField("remaining-terms", "مانده سنوات", "—");
      setField("study-status", "آخرین وضعیت تحصیل", "مشغول به تحصیل");
      setField("start-date", "تاریخ شروع تحصیل", "—");
      setField("taken-units", "كل تعداد واحد اخذ شده", data.taken_units || 0);
      setField("failed-units", "كل تعداد رد شده", 0);
      setField("terms-passed", "سنوات(ترم)گذرانده", "—");

      var byTerm = {};
      (data.transcripts || []).forEach(function (tr) {
        var term = tr.term_title || "سایر";
        if (!byTerm[term]) byTerm[term] = [];
        byTerm[term].push(tr);
      });

      var container = document.getElementById("transcript-terms-root");
      if (!container) {
        container = document.createElement("div");
        container.id = "transcript-terms-root";
        var section = document.querySelector("section:last-of-type");
        if (section) {
          section.querySelector(".bg-white.shadow.rounded-4") &&
            (section.querySelector(".bg-white.shadow.rounded-4").style.display = "none");
          section.appendChild(container);
        }
      }
      container.innerHTML = Object.keys(byTerm)
        .map(function (term) {
          var rows = byTerm[term]
            .map(function (tr, i) {
              return (
                "<tr><td>" + (i + 1) + "</td><td>" + (tr.lesson_code || "—") + "</td><td>—</td>" +
                "<td>" + (tr.lesson_title || "—") + "</td><td>" + (tr.lesson_units || 3) + "</td>" +
                "<td>" + (tr.final_grade != null ? tr.final_grade : "—") + "</td><td>نظری</td><td>—</td><td>" +
                (tr.pass_status ? "قبول" : "اخذ") + "</td></tr>"
              );
            })
            .join("");
          return (
            "<div class=\"bg-white mx-auto shadow rounded-4 p-4 mb-3\">" +
            "<p class=\"fw-bold\">" + term + "</p>" +
            "<table class=\"table table-striped\"><thead><tr><td>#</td><td>کد</td><td>ارائه</td><td>نام درس</td>" +
            "<td>واحد</td><td>نمره</td><td>نوع</td><td>رشته</td><td>وضعیت</td></tr></thead><tbody>" +
            rows + "</tbody></table></div>"
          );
        })
        .join("");
    } catch (e) {
      console.error(e);
    }
  };

  window.initSemesterTranscriptPage = async function () {
    try {
      var data = await apiGet(API.pages.semesterTranscript);
      fillTable("table tbody", data.transcripts || [], function (tr, i) {
        return (
          "<tr><td>" + (i + 1) + "</td><td>" + (tr.lesson_code || "—") + "</td>" +
          "<td>" + (tr.lesson_title || "—") + "</td><td>" + (tr.lesson_units || 3) + "</td>" +
          "<td>" + (tr.final_grade != null ? tr.final_grade : "—") + "</td></tr>"
        );
      });
      var gpaEl = document.querySelector(".gpa-value, .stat-value, h3");
      if (gpaEl && data.current_term_gpa != null) {
        document.querySelectorAll("*").forEach(function (el) {
          if (el.childNodes.length === 1 && el.textContent.indexOf("معدل") >= 0) {
            el.textContent = "معدل نیمسال: " + data.current_term_gpa;
          }
        });
      }
    } catch (e) {
      console.error(e);
    }
  };

  window.initGradesPage = async function () {
    try {
      var data = await apiGet(API.pages.grades);
      var tbody = document.querySelector("table tbody");
      if (tbody) {
        var html = (data.exam_results || [])
          .map(function (e, i) {
            return "<tr><td>" + (i + 1) + "</td><td>" + (e.exam_type || "آزمون") + "</td><td>" + (e.score || "—") + "</td><td>" + (e.status || "—") + "</td></tr>";
          })
          .join("");
        html += (data.transcripts || [])
          .filter(function (t) { return t.final_grade != null; })
          .map(function (t, i) {
            return "<tr><td>" + (i + 1) + "</td><td>" + (t.lesson_title || "—") + "</td><td>" + t.final_grade + "</td><td>نهایی</td></tr>";
          })
          .join("");
        tbody.innerHTML = html || "<tr><td colspan=\"4\">موردی یافت نشد</td></tr>";
      }
    } catch (e) {
      console.error(e);
    }
  };
})();
