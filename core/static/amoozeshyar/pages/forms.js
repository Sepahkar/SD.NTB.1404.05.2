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
      var data = await apiGet(API.pages.grades);
      var transcripts = data.transcripts || [];
      var tbody = document.getElementById("tableBody");
      if (!tbody) return;
      if (!transcripts.length) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center">درسی برای اعتراض یافت نشد.</td></tr>';
        return;
      }
      tbody.innerHTML = transcripts
        .map(function (tr, i) {
          var pass = tr.pass_status ? "قبول" : "در حال اخذ";
          return (
            "<tr>" +
            '<td><input type="radio" name="selectedRow" class="row-radio" value="' + tr.id + '" /></td>' +
            "<td>" + tr.id + "</td>" +
            "<td>" + (tr.lesson_title || "—") + "</td>" +
            "<td>" + (tr.lesson_code || "—") + "</td>" +
            "<td>" + (tr.lesson_units || 3) + "</td>" +
            "<td>" + (tr.final_grade != null ? tr.final_grade : "—") + "</td>" +
            "<td>" + (tr.teacher_name || "—") + "</td>" +
            "<td>" + (tr.term_title || "—") + "</td>" +
            "<td>" + pass + "</td></tr>"
          );
        })
        .join("");
    } catch (e) {
      console.error(e);
      var tbody = document.getElementById("tableBody");
      if (tbody) tbody.innerHTML = '<tr><td colspan="9">' + e.message + "</td></tr>";
    }
  };

  window.initGradeObjectionFormPage = async function () {
    var btn = document.getElementById("objection-submit-btn") || document.querySelector("button.btn-accent");
    var textarea = document.getElementById("objectionText") || document.querySelector("textarea");
    var select = document.getElementById("objection-course") || document.querySelector("select");
    var errorBox = document.getElementById("form-error");

    try {
      var grades = await apiGet(API.pages.grades);
      if (select) {
        select.innerHTML = '<option value="">انتخاب درس</option>';
        (grades.transcripts || []).forEach(function (tr) {
          select.innerHTML +=
            '<option value="' + tr.id + '">' + (tr.lesson_title || "—") + " — " + (tr.final_grade != null ? tr.final_grade : "—") + "</option>";
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
          if (textarea) textarea.focus();
          return;
        }
        showFormError(errorBox, "");
        btn.disabled = true;
        try {
          var reqType = await constValueId("grade_objection");
          var reqStatus = await constValueId("req_status_pending");
          var courseLabel = select && select.selectedOptions[0] ? select.selectedOptions[0].text : "";
          await apiPost(API.pages.gradeObjection, {
            request_date: todayISO(),
            description: desc + (courseLabel ? " — درس: " + courseLabel : ""),
            request_type: reqType,
            status: reqStatus,
          });
          var toast = document.getElementById("toast");
          if (toast) {
            toast.classList.add("show");
            setTimeout(function () {
              window.location.href = "/grade-objection/";
            }, 1500);
          } else {
            alert("اعتراض ثبت شد.");
            window.location.href = "/grade-objection/";
          }
        } catch (err) {
          showFormError(errorBox, err.message);
        } finally {
          btn.disabled = false;
        }
      });
    }
  };

  function showPageError(el, msg) {
    if (!el) return;
    el.textContent = msg || "";
    el.classList.toggle("is-visible", !!msg);
  }

  window.initCourseSelectionPage = async function () {
    var errorBox = document.getElementById("form-error");
    try {
      var data = await apiGet(API.pages.courseSelection);
      var enrolled = data.enrolled_offer_ids || [];
      var offers = data.available_offers || [];
      var enrolledOffers = offers.filter(function (o) { return enrolled.indexOf(o.id) >= 0; });
      var available = offers.filter(function (o) { return enrolled.indexOf(o.id) < 0; });

      var list = document.getElementById("available-offers-list");
      if (list) {
        list.innerHTML = available.map(function (offer) {
          return (
            '<div class="offer-row">' +
            "<div><strong>" + (offer.lesson_title || "—") + "</strong></div>" +
            '<div class="text-secondary small">' + (offer.class_number || offer.lesson_code || "") + " — " + (offer.teacher_name || "—") + "</div>" +
            '<button type="button" class="btn-enroll enroll-btn" data-offer-id="' + offer.id + '">اخذ درس</button></div>'
          );
        }).join("") || "<p>درس قابل اخذی باقی نمانده.</p>";
      }

      fillTable("#enrolled-offers-body", enrolledOffers, function (o) {
        return (
          "<tr><td>" + (o.class_number || o.lesson_code || "—") + "</td>" +
          "<td>" + (o.lesson_title || "—") + "</td>" +
          "<td>" + (o.teacher_name || "—") + "</td><td>—</td><td>3</td></tr>"
        );
      });

      var cnt = document.getElementById("enrolled-count");
      if (cnt) cnt.textContent = enrolledOffers.length;
      var termEl = document.getElementById("enrolled-term");
      if (termEl) termEl.textContent = (data.term && data.term.term_title) || "—";

      document.querySelectorAll(".enroll-btn").forEach(function (btn) {
        btn.addEventListener("click", async function () {
          var offerId = btn.getAttribute("data-offer-id");
          btn.disabled = true;
          showPageError(errorBox, "");
          try {
            await apiPost(API.pages.courseSelection, { class_offer_id: parseInt(offerId, 10) });
            initCourseSelectionPage();
          } catch (err) {
            showPageError(errorBox, err.message);
            btn.disabled = false;
          }
        });
      });
    } catch (e) {
      showPageError(errorBox, e.message);
    }
  };

  window.initAddDropPage = async function () {
    var errorBox = document.getElementById("form-error");
    var selectionData;
    var addDropData;

    async function reload() {
      selectionData = await apiGet(API.pages.courseSelection);
      addDropData = await apiGet(API.pages.addDrop);
      render();
    }

    function getAvailable() {
      var enrolled = (selectionData && selectionData.enrolled_offer_ids) || [];
      return ((selectionData && selectionData.available_offers) || []).filter(function (o) {
        return enrolled.indexOf(o.id) < 0;
      });
    }

    function render() {
      var codeQ = (document.getElementById("adddrop-code") || {}).value || "";
      var titleQ = (document.getElementById("adddrop-title") || {}).value || "";
      codeQ = codeQ.trim().toLowerCase();
      titleQ = titleQ.trim().toLowerCase();

      var available = getAvailable().filter(function (o) {
        var code = String(o.class_number || o.lesson_code || "").toLowerCase();
        var title = String(o.lesson_title || "").toLowerCase();
        var okCode = !codeQ || code.indexOf(codeQ) >= 0;
        var okTitle = !titleQ || title.indexOf(titleQ) >= 0;
        return okCode && okTitle;
      });

      fillTable("#adddrop-available-body", available, function (o) {
        return (
          "<tr><td>" + (o.class_number || o.lesson_code || "—") + "</td>" +
          "<td>" + (o.lesson_title || "—") + "</td>" +
          "<td>" + (o.teacher_name || "—") + "</td><td>3</td>" +
          '<td><button type="button" class="btn-enroll adddrop-pick-btn" data-offer-id="' + o.id + '">افزودن</button></td></tr>'
        );
      });

      fillTable("#adddrop-enrolled-body", (addDropData && addDropData.enrolled_courses) || [], function (c) {
        var time = c.class_day || "—";
        if (c.class_time) time += " " + String(c.class_time).slice(0, 5);
        return (
          "<tr data-transcript-id=\"" + c.id + "\">" +
          "<td>" + (c.lesson_code || "—") + "</td>" +
          "<td>" + (c.lesson_title || "—") + "</td>" +
          "<td>" + (c.teacher_name || "—") + "</td>" +
          "<td>" + time + "</td>" +
          '<td><button type="button" class="btn-drop adddrop-drop-btn" data-transcript-id="' + c.id + '">حذف</button></td></tr>'
        );
      });
    }

    try {
      await reload();

      document.querySelectorAll("#adddrop-code, #adddrop-title").forEach(function (input) {
        if (!input.dataset.bound) {
          input.dataset.bound = "1";
          input.addEventListener("input", render);
        }
      });

      if (!window.__addDropClickBound) {
        window.__addDropClickBound = true;
        document.body.addEventListener("click", async function (e) {
        var pick = e.target.closest(".adddrop-pick-btn");
        if (pick) {
          pick.disabled = true;
          showPageError(errorBox, "");
          try {
            await apiPost(API.pages.courseSelection, { class_offer_id: parseInt(pick.getAttribute("data-offer-id"), 10) });
            await reload();
          } catch (err) {
            showPageError(errorBox, err.message);
            pick.disabled = false;
          }
          return;
        }
        var drop = e.target.closest(".adddrop-drop-btn");
        if (drop) {
          if (!confirm("آیا از حذف این درس مطمئن هستید؟")) return;
          drop.disabled = true;
          showPageError(errorBox, "");
          try {
            await apiPost(API.pages.addDrop, { transcript_id: parseInt(drop.getAttribute("data-transcript-id"), 10) });
            await reload();
          } catch (err) {
            showPageError(errorBox, err.message);
            drop.disabled = false;
          }
        }
        });
      }

      var enrollBtn = document.getElementById("adddrop-enroll-btn");
      if (enrollBtn && !enrollBtn.dataset.bound) {
        enrollBtn.dataset.bound = "1";
        enrollBtn.addEventListener("click", async function () {
          var available = getAvailable();
          var codeQ = (document.getElementById("adddrop-code") || {}).value || "";
          var titleQ = (document.getElementById("adddrop-title") || {}).value || "";
          var match = available.find(function (o) {
            if (codeQ && String(o.class_number || o.lesson_code || "").indexOf(codeQ.trim()) >= 0) return true;
            if (titleQ && String(o.lesson_title || "").indexOf(titleQ.trim()) >= 0) return true;
            return false;
          });
          if (!match) {
            showPageError(errorBox, "درسی با این مشخصات در لیست قابل اخذ یافت نشد.");
            return;
          }
          enrollBtn.disabled = true;
          showPageError(errorBox, "");
          try {
            await apiPost(API.pages.courseSelection, { class_offer_id: match.id });
            await reload();
          } catch (err) {
            showPageError(errorBox, err.message);
          } finally {
            enrollBtn.disabled = false;
          }
        });
      }

      var saveBtn = document.querySelector(".save-btn");
      if (saveBtn) {
        saveBtn.addEventListener("click", function () {
          reload();
        });
      }
    } catch (e) {
      showPageError(errorBox, e.message);
    }
  };

  window.initEmergencyRemovalPage = async function () {
    var errorBox = document.getElementById("form-error");
    var reasonInput = document.getElementById("emergency-reason");

    async function submitEmergency(transcriptIds, reason) {
      var reqType = await constValueId("req_type_leave");
      var reqStatus = await constValueId("req_status_pending");
      for (var i = 0; i < transcriptIds.length; i++) {
        await apiPost(API.pages.studentRequests, {
          request_date: todayISO(),
          description: reason + " (transcript:" + transcriptIds[i] + ")",
          request_type: reqType,
          status: reqStatus,
        });
      }
    }

    async function loadRows() {
      var data = await apiGet(API.pages.addDrop);
      var tbody = document.getElementById("emergency-rows");
      if (!tbody) return;
      var courses = data.enrolled_courses || [];
      if (!courses.length) {
        tbody.innerHTML = '<tr><td colspan="7">درسی برای حذف اضطراری یافت نشد.</td></tr>';
        return;
      }
      tbody.innerHTML = courses.map(function (c) {
        var time = c.class_day || "—";
        if (c.class_time) time += " " + String(c.class_time).slice(0, 5);
        return (
          "<tr data-transcript-id=\"" + c.id + "\">" +
          '<td><input type="checkbox" class="row-cb" value="' + c.id + '"></td>' +
          "<td>" + (c.lesson_code || "—") + "</td>" +
          "<td>" + (c.lesson_title || "—") + "</td>" +
          "<td>" + (c.teacher_name || "—") + "</td>" +
          "<td>" + time + "</td>" +
          "<td>" + (c.lesson_units || 3) + "</td>" +
          '<td><button type="button" class="btn-drop emergency-row-btn" data-transcript-id="' + c.id + '">درخواست</button></td></tr>'
        );
      }).join("");
    }

    try {
      await loadRows();

      var masterCheck = document.getElementById("masterCheck");
      if (masterCheck) {
        masterCheck.addEventListener("change", function () {
          document.querySelectorAll(".row-cb").forEach(function (cb) {
            cb.checked = masterCheck.checked;
          });
        });
      }

      var tbody = document.getElementById("emergency-rows");
      if (tbody) {
        tbody.addEventListener("click", async function (e) {
          var btn = e.target.closest(".emergency-row-btn");
          if (!btn) return;
          var tid = btn.getAttribute("data-transcript-id");
          var reason = reasonInput ? reasonInput.value.trim() : "";
          if (!reason) {
            showPageError(errorBox, "لطفاً دلیل حذف اضطراری را وارد کنید.");
            if (reasonInput) reasonInput.focus();
            return;
          }
          if (!confirm("درخواست حذف اضطراری برای این درس ثبت شود؟")) return;
          btn.disabled = true;
          showPageError(errorBox, "");
          try {
            var row = btn.closest("tr");
            var lesson = row && row.children[2] ? row.children[2].textContent : "";
            await submitEmergency([tid], "درخواست حذف اضطراری — " + lesson + " — " + reason);
            alert("درخواست حذف اضطراری ثبت شد.");
            await loadRows();
          } catch (err) {
            showPageError(errorBox, err.message);
            btn.disabled = false;
          }
        });
      }

      var bulkBtn = document.getElementById("emergency-submit-selected");
      if (bulkBtn) {
        bulkBtn.addEventListener("click", async function () {
          var checked = Array.prototype.slice.call(document.querySelectorAll(".row-cb:checked"));
          if (!checked.length) {
            showPageError(errorBox, "حداقل یک درس را انتخاب کنید.");
            return;
          }
          var reason = reasonInput ? reasonInput.value.trim() : "";
          if (!reason) {
            showPageError(errorBox, "لطفاً دلیل حذف اضطراری را وارد کنید.");
            if (reasonInput) reasonInput.focus();
            return;
          }
          if (!confirm("درخواست حذف اضطراری برای " + checked.length + " درس ثبت شود؟")) return;
          bulkBtn.disabled = true;
          showPageError(errorBox, "");
          try {
            var ids = checked.map(function (cb) { return cb.value; });
            await submitEmergency(ids, "درخواست حذف اضطراری — " + reason);
            alert("درخواست‌ها با موفقیت ثبت شد.");
            if (reasonInput) reasonInput.value = "";
            await loadRows();
          } catch (err) {
            showPageError(errorBox, err.message);
          } finally {
            bulkBtn.disabled = false;
          }
        });
      }
    } catch (e) {
      showPageError(errorBox, e.message);
    }
  };

  window.initCourseSearchPage = async function () {
    var errorBox = document.getElementById("form-error");
    var selectionData = null;

    function getAvailable() {
      if (!selectionData) return [];
      var enrolled = selectionData.enrolled_offer_ids || [];
      return (selectionData.available_offers || []).filter(function (o) {
        return enrolled.indexOf(o.id) < 0;
      });
    }

    function runSearch() {
      var codeQ = ((document.getElementById("search-code") || {}).value || "").trim().toLowerCase();
      var titleQ = ((document.getElementById("search-title") || {}).value || "").trim().toLowerCase();
      var teacherQ = ((document.getElementById("search-teacher") || {}).value || "").trim().toLowerCase();

      var results = getAvailable().filter(function (o) {
        var code = String(o.class_number || o.lesson_code || "").toLowerCase();
        var title = String(o.lesson_title || "").toLowerCase();
        var teacher = String(o.teacher_name || "").toLowerCase();
        if (codeQ && code.indexOf(codeQ) < 0) return false;
        if (titleQ && title.indexOf(titleQ) < 0) return false;
        if (teacherQ && teacher.indexOf(teacherQ) < 0) return false;
        return true;
      });

      var countEl = document.getElementById("search-count");
      if (countEl) countEl.textContent = "(" + results.length + " نتیجه)";

      fillTable("#search-results-body", results, function (o) {
        return (
          "<tr><td>" + (o.class_number || o.lesson_code || "—") + "</td>" +
          "<td>" + (o.lesson_title || "—") + "</td>" +
          "<td>" + (o.teacher_name || "—") + "</td>" +
          "<td>3</td>" +
          '<td><span class="status-badge-open">قابل اخذ</span></td>' +
          '<td><button type="button" class="btn-enroll search-enroll-btn" data-offer-id="' + o.id + '">اخذ درس</button></td></tr>'
        );
      });
    }

    try {
      selectionData = await apiGet(API.pages.courseSelection);
      var termInput = document.getElementById("search-term");
      if (termInput && selectionData.term) {
        termInput.value = selectionData.term.term_title || "ترم جاری";
      }
      runSearch();

      ["search-code", "search-title", "search-teacher"].forEach(function (id) {
        var el = document.getElementById(id);
        if (el) el.addEventListener("input", runSearch);
      });

      var searchBtn = document.getElementById("search-run-btn");
      if (searchBtn) searchBtn.addEventListener("click", runSearch);

      if (!window.__courseSearchClickBound) {
        window.__courseSearchClickBound = true;
        document.body.addEventListener("click", async function (e) {
          var btn = e.target.closest(".search-enroll-btn");
          if (!btn) return;
          var offerId = btn.getAttribute("data-offer-id");
          btn.disabled = true;
          showPageError(errorBox, "");
          try {
            await apiPost(API.pages.courseSelection, { class_offer_id: parseInt(offerId, 10) });
            selectionData = await apiGet(API.pages.courseSelection);
            runSearch();
          } catch (err) {
            showPageError(errorBox, err.message);
            btn.disabled = false;
          }
        });
      }
    } catch (e) {
      showPageError(errorBox, e.message);
    }
  };
})();
