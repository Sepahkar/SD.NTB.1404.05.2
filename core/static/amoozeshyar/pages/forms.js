(function () {
  "use strict";

  function todayISO() {
    return new Date().toISOString().slice(0, 10);
  }

  function nextMonthISO() {
    var d = new Date();
    d.setMonth(d.getMonth() + 1);
    return d.toISOString().slice(0, 10);
  }

  async function constValueId(code) {
    var data = await apiGet("/api/v1/const-values/?code=" + encodeURIComponent(code));
    var results = data.results || data;
    return results.length ? results[0].id : null;
  }

  window.initLoanRequestPage = async function () {
    var errorBox = document.getElementById("form-error");
    var submitBtn = document.querySelector(".loan-btn-submit");
    var tbody = document.querySelector(".loan-table tbody");

    async function loadLoans() {
      try {
        var data = await apiGet(API.pages.loanRequest);
        fillTable(".loan-table tbody", data.loans || [], function (loan) {
          return (
            "<tr><td>" + (loan.loan_type || "—") + "</td>" +
            "<td class=\"ltr-text\">" + formatDate(loan.loan_request_date) + "</td>" +
            "<td>" + formatNumber(loan.amount) + "</td>" +
            "<td>" + (loan.number_of_loan_installments || "—") + "</td>" +
            "<td>" + (loan.loan_status || "—") + "</td>" +
            "<td>—</td></tr>"
          );
        });
      } catch (e) {
        if (tbody) tbody.innerHTML = "<tr><td colspan=\"6\">" + e.message + "</td></tr>";
      }
    }

    if (submitBtn) {
      submitBtn.addEventListener("click", async function (e) {
        e.preventDefault();
        showFormError(errorBox, "");
        var selects = document.querySelectorAll(".loan-card select");
        var inputs = document.querySelectorAll(".loan-card input[type=\"text\"]");
        var amount = parseInt((inputs[0] && inputs[0].value || "").replace(/\D/g, ""), 10) || 0;
        var installments = parseInt(selects[3] && selects[3].value, 10) || 4;
        var installmentAmount = installments ? Math.ceil(amount / installments) : amount;

        submitBtn.disabled = true;
        try {
          await apiPost(API.pages.loanRequest, {
            loan_type: (selects[0] && selects[0].value) || "وام شهریه",
            amount: amount,
            loan_status: "pending",
            amount_of_each_loan_installment: installmentAmount,
            loan_repayment_period: installments,
            loan_installment_date: nextMonthISO(),
            number_of_loan_installments: installments,
            how_to_pay_loan_installments: "واریز بانکی",
          });
          await loadLoans();
          alert("درخواست وام ثبت شد.");
        } catch (err) {
          showFormError(errorBox, err.message);
        } finally {
          submitBtn.disabled = false;
        }
      });
    }
    await loadLoans();
  };

  window.initStudentRequestsPage = async function () {
    var btn = document.querySelector(".sr-btn-primary");
    var errorBox = document.getElementById("form-error");
    if (!btn) return;

    btn.addEventListener("click", async function (e) {
      e.preventDefault();
      showFormError(errorBox, "");
      var textarea = document.querySelector(".sr-textarea-row textarea");
      var description = textarea ? textarea.value.trim() : "";
      if (!description) {
        showFormError(errorBox, "متن درخواست الزامی است.");
        return;
      }
      btn.disabled = true;
      try {
        var reqType = await constValueId("req_type_leave");
        var reqStatus = await constValueId("req_status_pending");
        await apiPost(API.pages.studentRequests, {
          request_date: todayISO(),
          description: description,
          request_type: reqType,
          status: reqStatus,
        });
        alert("درخواست ثبت شد.");
        if (textarea) textarea.value = "";
      } catch (err) {
        showFormError(errorBox, err.message);
      } finally {
        btn.disabled = false;
      }
    });
  };

  window.initLeaveRequestPage = async function () {
    var btn = document.querySelector(".sr-btn-primary, .loan-btn-submit, button[type=\"submit\"]");
    var textarea = document.querySelector("textarea");
    var errorBox = document.getElementById("form-error");
    if (!btn) return;

    btn.addEventListener("click", async function (e) {
      e.preventDefault();
      var reason = textarea ? textarea.value.trim() : "";
      if (!reason) {
        showFormError(errorBox, "دلیل مرخصی الزامی است.");
        return;
      }
      btn.disabled = true;
      try {
        await apiPost(API.pages.leaveRequest, { leave_reason: reason });
        alert("درخواست مرخصی ثبت شد.");
        if (textarea) textarea.value = "";
      } catch (err) {
        showFormError(errorBox, err.message);
      } finally {
        btn.disabled = false;
      }
    });
  };

  window.initGradeObjectionPage = async function () {
    try {
      var data = await apiGet(API.pages.gradeObjection);
      fillTable("table tbody, .objection-table tbody", data.objections || [], function (o) {
        return "<tr><td>" + (o.request_type_caption || "—") + "</td><td>" + (o.description || "—") + "</td><td>" + (o.status_caption || "—") + "</td></tr>";
      });
    } catch (e) {
      console.error(e);
    }
  };

  window.initGradeObjectionFormPage = async function () {
    var btn = document.querySelector("button, .btn-primary");
    var textarea = document.querySelector("textarea");
    var errorBox = document.getElementById("form-error");

    try {
      var data = await apiGet(API.pages.gradeObjection);
      var select = document.querySelector("select");
      if (select && data.exam_results) {
        select.innerHTML = "<option value=\"\">انتخاب کنید</option>";
        data.exam_results.forEach(function (e, i) {
          select.innerHTML += "<option value=\"" + i + "\">" + (e.exam_type || "آزمون") + " — " + (e.grade || "—") + "</option>";
        });
      }
    } catch (e) {
      console.error(e);
    }

    if (btn) {
      btn.addEventListener("click", async function (e) {
        e.preventDefault();
        var desc = textarea ? textarea.value.trim() : "";
        if (!desc) {
          showFormError(errorBox, "شرح اعتراض الزامی است.");
          return;
        }
        btn.disabled = true;
        try {
          var reqType = await constValueId("grade_objection");
          var reqStatus = await constValueId("req_status_pending");
          await apiPost(API.pages.gradeObjection, {
            request_date: todayISO(),
            description: desc,
            request_type: reqType,
            status: reqStatus,
          });
          alert("اعتراض ثبت شد.");
          window.location.href = "/grade-objection/";
        } catch (err) {
          showFormError(errorBox, err.message);
        } finally {
          btn.disabled = false;
        }
      });
    }
  };

  window.initCourseSelectionPage = async function () {
    var grid = document.querySelector(".unit-grid");
    var errorBox = document.getElementById("form-error");

    try {
      var data = await apiGet(API.pages.courseSelection);
      var enrolled = data.enrolled_offer_ids || [];
      if (!grid) return;
      var html = "";
      (data.available_offers || []).forEach(function (offer) {
        var isEnrolled = enrolled.indexOf(offer.id) >= 0;
        html +=
          "<div class=\"unit-card\" data-offer-id=\"" + offer.id + "\">" +
          "<h3>" + (offer.lesson_title || "—") + "</h3>" +
          "<p>استاد: " + (offer.teacher_name || "—") + "</p>" +
          "<button class=\"enroll-btn\" " + (isEnrolled ? "disabled" : "") + ">" +
          (isEnrolled ? "اخذ شده" : "اخذ درس") + "</button></div>";
      });
      grid.innerHTML = html || "<p>کلاسی یافت نشد.</p>";

      grid.querySelectorAll(".enroll-btn").forEach(function (btn) {
        btn.addEventListener("click", async function () {
          var card = btn.closest("[data-offer-id]");
          var offerId = card && card.getAttribute("data-offer-id");
          if (!offerId) return;
          btn.disabled = true;
          try {
            await apiPost(API.pages.courseSelection, { class_offer_id: parseInt(offerId, 10) });
            alert("درس با موفقیت اخذ شد.");
            initCourseSelectionPage();
          } catch (err) {
            showFormError(errorBox, err.message);
            btn.disabled = false;
          }
        });
      });
    } catch (e) {
      showFormError(errorBox, e.message);
    }
  };

  window.initAddDropPage = async function () {
    var errorBox = document.getElementById("form-error");
    try {
      var data = await apiGet(API.pages.addDrop);
      var container = document.querySelector(".courses-list, .unit-grid, tbody");
      if (container && container.tagName === "TBODY") {
        fillTable("tbody", data.enrolled_courses || [], function (c) {
          return (
            "<tr data-transcript-id=\"" + c.id + "\">" +
            "<td>" + (c.lesson_title || "—") + "</td>" +
            "<td>" + (c.lesson_code || "—") + "</td>" +
            "<td><button class=\"drop-btn btn btn-danger btn-sm\">حذف</button></td></tr>"
          );
        });
      } else if (container) {
        var html = "";
        (data.enrolled_courses || []).forEach(function (c) {
          html +=
            "<div class=\"unit-card\" data-transcript-id=\"" + c.id + "\">" +
            "<h3>" + (c.lesson_title || "—") + "</h3>" +
            "<button class=\"drop-btn\">حذف درس</button></div>";
        });
        container.innerHTML = html || "<p>درسی اخذ نشده.</p>";
      }

      document.querySelectorAll(".drop-btn").forEach(function (btn) {
        btn.addEventListener("click", async function () {
          var el = btn.closest("[data-transcript-id]");
          var tid = el && el.getAttribute("data-transcript-id");
          if (!tid || !confirm("آیا از حذف این درس مطمئن هستید؟")) return;
          btn.disabled = true;
          try {
            await apiPost(API.pages.addDrop, { transcript_id: parseInt(tid, 10) });
            alert("درس حذف شد.");
            initAddDropPage();
          } catch (err) {
            showFormError(errorBox, err.message);
            btn.disabled = false;
          }
        });
      });
    } catch (e) {
      showFormError(errorBox, e.message);
    }
  };

  window.initEmergencyRemovalPage = async function () {
    var btn = document.querySelector("button.btn-primary, .submit-btn");
    var textarea = document.querySelector("textarea");
    var select = document.querySelector("select");
    var errorBox = document.getElementById("form-error");

    try {
      var data = await apiGet(API.pages.addDrop);
      if (select) {
        select.innerHTML = "<option value=\"\">انتخاب درس</option>";
        (data.enrolled_courses || []).forEach(function (c) {
          select.innerHTML += "<option value=\"" + c.id + "\">" + (c.lesson_title || "—") + "</option>";
        });
      }
    } catch (e) {
      console.error(e);
    }

    if (btn) {
      btn.addEventListener("click", async function (e) {
        e.preventDefault();
        var desc = textarea ? textarea.value.trim() : "درخواست حذف اضطراری";
        var transcriptId = select ? select.value : "";
        btn.disabled = true;
        try {
          var reqType = await constValueId("req_type_leave");
          var reqStatus = await constValueId("req_status_pending");
          await apiPost(API.pages.studentRequests, {
            request_date: todayISO(),
            description: desc + (transcriptId ? " (transcript:" + transcriptId + ")" : ""),
            request_type: reqType,
            status: reqStatus,
          });
          alert("درخواست حذف اضطراری ثبت شد.");
        } catch (err) {
          showFormError(errorBox, err.message);
        } finally {
          btn.disabled = false;
        }
      });
    }
  };
})();
