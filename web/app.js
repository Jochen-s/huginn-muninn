(function () {
  "use strict";

  var currentClaim = "";
  var lastResultId = null;
  var lastResultType = null;

  // --- Utilities ---

  // XSS prevention: all dynamic content passes through this function
  // before DOM insertion. Creates a detached div, sets textContent
  // (which escapes all HTML entities), then returns the safe innerHTML.
  function escapeHtml(str) {
    var div = document.createElement("div");
    div.textContent = String(str);
    return div.innerHTML;
  }

  function $(id) {
    return document.getElementById(id);
  }

  function show(el) { el.classList.remove("hidden"); }
  function hide(el) { el.classList.add("hidden"); }

  function getMethod() {
    var radios = document.querySelectorAll('input[name="method"]');
    for (var i = 0; i < radios.length; i++) {
      if (radios[i].checked) return radios[i].value;
    }
    return "check";
  }

  // --- Model management ---

  function loadModels() {
    fetch("/api/models")
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var container = $("model-checkboxes");
        container.textContent = "";
        var models = data.models || [];
        for (var i = 0; i < models.length; i++) {
          var label = document.createElement("label");
          label.className = "model-checkbox-label";
          var cb = document.createElement("input");
          cb.type = "checkbox";
          cb.value = models[i];
          cb.className = "model-cb";
          label.appendChild(cb);
          label.appendChild(document.createTextNode(" " + models[i]));
          container.appendChild(label);
        }
      })
      .catch(function () {});
  }

  function getSelectedModels() {
    var cbs = document.querySelectorAll(".model-cb:checked");
    var models = [];
    for (var i = 0; i < cbs.length; i++) {
      models.push(cbs[i].value);
    }
    return models;
  }

  function toggleCompareOptions() {
    var method = getMethod();
    var opts = $("compare-options");
    if (method === "compare") {
      show(opts);
    } else {
      hide(opts);
    }
  }

  // --- API calls ---

  function checkHealth() {
    fetch("/api/health")
      .then(function (r) {
        var dot = $("status-indicator");
        if (r.ok) {
          dot.className = "status-dot ok";
          dot.title = "Ollama connected";
        } else {
          dot.className = "status-dot down";
          dot.title = "Ollama unavailable";
        }
      })
      .catch(function () {
        var dot = $("status-indicator");
        dot.className = "status-dot down";
        dot.title = "API unreachable";
      });
  }

  function loadHistory() {
    fetch("/api/history?limit=10")
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var list = $("history-list");
        list.textContent = "";
        var items = data.verdicts || [];
        for (var i = 0; i < items.length; i++) {
          var item = items[i];
          var verdict = (item.data && item.data.verdict) || "unknown";
          var li = document.createElement("li");
          var textSpan = document.createElement("span");
          textSpan.textContent = item.claim;
          var verdictSpan = document.createElement("span");
          verdictSpan.className = "history-verdict";
          verdictSpan.textContent = verdict;
          li.appendChild(textSpan);
          li.appendChild(document.createTextNode(" "));
          li.appendChild(verdictSpan);
          li.setAttribute("data-claim", item.claim);
          li.addEventListener("click", function () {
            $("claim-input").value = this.getAttribute("data-claim");
          });
          list.appendChild(li);
        }
      })
      .catch(function () {});
  }

  // --- Analysis ---

  function analyze() {
    var claim = $("claim-input").value.trim();
    if (!claim) return;

    currentClaim = claim;
    lastResultId = null;
    lastResultType = null;
    var method = getMethod();
    var noCache = $("no-cache").checked;
    var btn = $("analyze-btn");

    var endpoint = "/api/check";
    var body = { claim: claim, no_cache: noCache };

    if (method === "analyze") {
      endpoint = "/api/analyze";
    } else if (method === "escalate") {
      endpoint = "/api/check-and-escalate";
    } else if (method === "compare") {
      endpoint = "/api/compare";
      var models = getSelectedModels();
      if (models.length < 2) {
        $("error-message").textContent = "Select at least 2 models to compare";
        show($("error"));
        return;
      }
      body = { claim: claim, models: models, method: "check", reconcile: $("reconcile").checked };
    }

    btn.disabled = true;
    hide($("error"));
    hide($("result"));
    show($("loading"));
    $("loading-message").textContent = method === "analyze"
      ? "Running deep analysis (this may take a minute)..."
      : method === "compare"
        ? "Comparing models (this may take a minute)..."
        : "Analyzing claim...";

    fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
      .then(function (r) {
        if (!r.ok) {
          return r.json().then(function (err) {
            throw new Error(err.detail || "Request failed (" + r.status + ")");
          });
        }
        return r.json();
      })
      .then(function (data) {
        hide($("loading"));
        if (data.verdict_id) {
          lastResultId = data.verdict_id;
          lastResultType = "verdict";
        } else if (data.analysis_id) {
          lastResultId = data.analysis_id;
          lastResultType = "analysis";
        }
        renderResult(data, method);
        show($("result"));
        updateSessionAddVisibility();
        loadHistory();
      })
      .catch(function (err) {
        hide($("loading"));
        $("error-message").textContent = err.message || "An error occurred";
        show($("error"));
      })
      .finally(function () {
        btn.disabled = false;
      });
  }

  // --- Renderers ---
  // All user-facing data is escaped via escapeHtml() before insertion.
  // Only static markup strings (tags, classes) are unescaped.

  function renderResult(data, method) {
    var container = $("result-content");
    // All dynamic content is escaped via escapeHtml() in each render function
    if (method === "compare") {
      container.innerHTML = renderComparison(data);
    } else if (method === "escalate" && data.escalated) {
      container.innerHTML = renderVerdict(data.method_1) +
        '<hr><h3 style="margin:1rem 0">Escalated: Deep Analysis</h3>' +
        renderAnalysis(data.method_2);
    } else if (method === "escalate" && !data.escalated) {
      container.innerHTML = renderVerdict(data.method_1);
    } else if (method === "analyze") {
      container.innerHTML = renderAnalysis(data);
    } else {
      container.innerHTML = renderVerdict(data);
    }

    var btns = document.querySelectorAll(".feedback-btn");
    for (var i = 0; i < btns.length; i++) {
      btns[i].classList.remove("selected");
    }
  }

  function renderVerdict(v) {
    var verdict = escapeHtml(v.verdict || "unknown");
    var conf = v.confidence != null ? (v.confidence * 100).toFixed(0) + "%" : "N/A";
    var html = '<div class="verdict-header verdict-' + escapeHtml(v.verdict || "unknown") + '">';
    html += "<h2>" + verdict.replace(/_/g, " ") + "</h2>";
    html += '<p class="confidence">Confidence: ' + escapeHtml(conf) + "</p>";
    html += "</div>";

    if (v.evidence_for && v.evidence_for.length > 0) {
      html += '<div class="evidence-section"><h3>Evidence For</h3>';
      for (var i = 0; i < v.evidence_for.length; i++) {
        html += '<div class="evidence-item">' + escapeHtml(v.evidence_for[i].text) + "</div>";
      }
      html += "</div>";
    }
    if (v.evidence_against && v.evidence_against.length > 0) {
      html += '<div class="evidence-section"><h3>Evidence Against</h3>';
      for (var j = 0; j < v.evidence_against.length; j++) {
        html += '<div class="evidence-item">' + escapeHtml(v.evidence_against[j].text) + "</div>";
      }
      html += "</div>";
    }

    if (v.common_ground) {
      html += renderCommonGround(v.common_ground, false);
    }

    if (v.escalation && v.escalation.should_escalate) {
      html += '<p style="margin-top:1rem;color:var(--accent)">This claim may benefit from deeper analysis.</p>';
    }

    return html;
  }

  function renderAnalysis(a) {
    var html = "";
    var conf = a.overall_confidence != null ? (a.overall_confidence * 100).toFixed(0) + "%" : "N/A";
    html += '<div class="analysis-section"><h3>Method 2 Analysis</h3>';
    html += "<p>Confidence: " + escapeHtml(conf) + "</p>";
    if (a.degraded) {
      html += '<p style="color:var(--error)">Degraded: ' + escapeHtml(a.degraded_reason || "unknown") + "</p>";
    }
    html += "</div>";

    var decomp = a.decomposition || {};
    if (decomp.sub_claims && decomp.sub_claims.length > 0) {
      html += '<div class="analysis-section"><h3>Sub-Claims (' + escapeHtml(decomp.complexity || "unknown") + ")</h3>";
      for (var i = 0; i < decomp.sub_claims.length; i++) {
        var sc = decomp.sub_claims[i];
        html += '<p><span class="tag">' + escapeHtml(sc.type || "?") + "</span> " + escapeHtml(sc.text || "") + "</p>";
      }
      html += "</div>";
    }

    var intel = a.intelligence || {};
    if (intel.actors && intel.actors.length > 0) {
      html += '<div class="analysis-section"><h3>Actors</h3>';
      for (var j = 0; j < intel.actors.length; j++) {
        var act = intel.actors[j];
        html += "<p>" + escapeHtml(act.name || "?") + " (" + escapeHtml(act.type || "?") + ") -- " + escapeHtml(act.motivation || "") + "</p>";
      }
      html += "</div>";
    }

    var ttps = a.ttps || {};
    if (ttps.ttp_matches && ttps.ttp_matches.length > 0) {
      html += '<div class="analysis-section"><h3>DISARM TTPs</h3>';
      for (var k = 0; k < ttps.ttp_matches.length; k++) {
        var t = ttps.ttp_matches[k];
        html += "<p>[" + escapeHtml(t.disarm_id || "?") + "] " + escapeHtml(t.technique_name || "");
        if (t.confidence != null) html += " (" + (t.confidence * 100).toFixed(0) + "%)";
        html += "</p>";
      }
      html += "</div>";
    }

    if (a.bridge) {
      html += renderCommonGround(a.bridge, true);
    }

    var audit = a.audit || {};
    if (audit.verdict) {
      html += '<div class="analysis-section"><h3>Audit: ' + escapeHtml(audit.verdict).toUpperCase() + "</h3>";
      if (audit.findings) {
        for (var m = 0; m < audit.findings.length; m++) {
          var f = audit.findings[m];
          html += "<p>[" + escapeHtml(f.severity || "?") + "] " + escapeHtml(f.description || "") + "</p>";
        }
      }
      html += "</div>";
    }

    return html;
  }

  function renderCommonGround(cg, isMethod2) {
    var html = '<div class="common-ground"><h3>Common Ground</h3>';
    if (isMethod2) {
      if (cg.universal_needs && cg.universal_needs.length > 0) {
        html += '<p><span class="label">Shared Needs:</span> ' + escapeHtml(cg.universal_needs.join(", ")) + "</p>";
      }
      if (cg.issue_overlap) {
        html += '<p><span class="label">Overlap:</span> ' + escapeHtml(cg.issue_overlap) + "</p>";
      }
      if (cg.perception_gap) {
        html += '<p><span class="label">Perception Gap:</span> ' + escapeHtml(cg.perception_gap) + "</p>";
      }
      if (cg.reframe) {
        html += '<p><span class="label">Reframe:</span> ' + escapeHtml(cg.reframe) + "</p>";
      }
      if (cg.socratic_dialogue && cg.socratic_dialogue.length > 0) {
        html += '<p><span class="label">Socratic Dialogue:</span></p>';
        for (var i = 0; i < cg.socratic_dialogue.length; i++) {
          html += "<p>Round " + (i + 1) + ": " + escapeHtml(cg.socratic_dialogue[i]) + "</p>";
        }
      }
    } else {
      if (cg.shared_concern) {
        html += '<p><span class="label">Shared Concern:</span> ' + escapeHtml(cg.shared_concern) + "</p>";
      }
      if (cg.framing_technique && cg.framing_technique !== "none_detected") {
        html += '<p><span class="label">Framing Technique:</span> ' +
          escapeHtml(cg.framing_technique.replace(/_/g, " ")) + "</p>";
        if (cg.technique_explanation) {
          html += "<p>" + escapeHtml(cg.technique_explanation) + "</p>";
        }
      }
      if (cg.reflection) {
        html += '<p><span class="label">Reflection:</span> ' + escapeHtml(cg.reflection) + "</p>";
      }
    }
    html += "</div>";
    return html;
  }

  // --- Comparison renderer ---
  // All dynamic content escaped via escapeHtml() before DOM insertion.

  function renderComparison(data) {
    var comp = data.comparison || {};
    var agree = comp.verdict_agreement;
    var agreeClass = agree ? "agreement-yes" : "agreement-no";
    var agreeText = agree ? "AGREEMENT" : "DIVERGENT";

    var html = '<div class="comparison-header ' + agreeClass + '">';
    html += "<h2>Model Comparison: " + escapeHtml(agreeText) + "</h2>";
    if (comp.confidence_spread != null) {
      html += '<p class="confidence">Confidence spread: ' + escapeHtml((comp.confidence_spread * 100).toFixed(1) + "%") + "</p>";
    }
    html += "</div>";

    // Side-by-side results
    var models = data.models || [];
    var results = data.results || {};
    html += '<div class="comparison-grid">';
    for (var i = 0; i < models.length; i++) {
      var name = models[i];
      var r = results[name] || {};
      html += '<div class="comparison-card">';
      html += '<h3 class="model-name">' + escapeHtml(name) + "</h3>";
      if (r.error) {
        html += '<p class="model-error">Error: ' + escapeHtml(r.error) + "</p>";
      } else if (r.verdict) {
        html += '<div class="verdict-header verdict-' + escapeHtml(r.verdict) + '" style="padding:0.5rem;margin-bottom:0.5rem">';
        html += "<p>" + escapeHtml(r.verdict.replace(/_/g, " ")).toUpperCase() + "</p>";
        if (r.confidence != null) {
          html += '<p class="confidence">' + escapeHtml((r.confidence * 100).toFixed(0) + "%") + "</p>";
        }
        html += "</div>";
      } else if (r.overall_confidence != null) {
        html += "<p>Confidence: " + escapeHtml((r.overall_confidence * 100).toFixed(0) + "%") + "</p>";
      }
      html += "</div>";
    }
    html += "</div>";

    // Key differences
    var diffs = comp.key_differences || [];
    if (diffs.length > 0) {
      html += '<div class="analysis-section"><h3>Key Differences</h3>';
      for (var j = 0; j < diffs.length; j++) {
        html += "<p>" + escapeHtml(diffs[j]) + "</p>";
      }
      html += "</div>";
    }

    // Reconciliation
    if (data.reconciliation && !data.reconciliation.error) {
      var rec = data.reconciliation;
      html += '<div class="common-ground"><h3>Reconciliation</h3>';
      if (rec.meta_verdict) {
        html += '<p><span class="label">Meta-verdict:</span> ' + escapeHtml(rec.meta_verdict.replace(/_/g, " ")).toUpperCase() + "</p>";
      }
      if (rec.meta_confidence != null) {
        html += '<p><span class="label">Confidence:</span> ' + escapeHtml((rec.meta_confidence * 100).toFixed(0) + "%") + "</p>";
      }
      if (rec.reasoning) {
        html += '<p><span class="label">Reasoning:</span> ' + escapeHtml(rec.reasoning) + "</p>";
      }
      html += "</div>";
    }

    return html;
  }

  // --- Feedback ---

  function sendFeedback(type) {
    if (!currentClaim) return;
    fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ claim: currentClaim, type: type }),
    }).catch(function () {});

    var btns = document.querySelectorAll(".feedback-btn");
    for (var i = 0; i < btns.length; i++) {
      btns[i].classList.remove("selected");
    }
    var clicked = document.querySelector('.feedback-btn[data-type="' + type + '"]');
    if (clicked) clicked.classList.add("selected");
  }

  // --- Sessions ---

  function loadSessions() {
    fetch("/api/sessions")
      .then(function (r) { return r.json(); })
      .then(function (sessions) {
        var list = $("sessions-list");
        list.textContent = "";
        var select = $("session-select");
        select.textContent = "";
        for (var i = 0; i < sessions.length; i++) {
          var s = sessions[i];
          var li = document.createElement("li");
          li.textContent = s.name;
          li.setAttribute("data-id", s.id);
          li.addEventListener("click", function () {
            viewSession(parseInt(this.getAttribute("data-id"), 10));
          });
          list.appendChild(li);

          var opt = document.createElement("option");
          opt.value = s.id;
          opt.textContent = s.name;
          select.appendChild(opt);
        }
        updateSessionAddVisibility();
      })
      .catch(function () {});
  }

  function createSession() {
    var nameInput = $("session-name");
    var name = nameInput.value.trim();
    if (!name) return;
    fetch("/api/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: name }),
    })
      .then(function (r) { return r.json(); })
      .then(function () {
        nameInput.value = "";
        loadSessions();
      })
      .catch(function () {});
  }

  function viewSession(sessionId) {
    fetch("/api/sessions/" + sessionId)
      .then(function (r) { return r.json(); })
      .then(function (session) {
        hide($("sessions-list"));
        hide(document.querySelector(".session-controls"));
        $("session-detail-name").textContent = session.name;
        var itemsList = $("session-items-list");
        itemsList.textContent = "";
        var items = session.items || [];
        if (items.length === 0) {
          var li = document.createElement("li");
          li.textContent = "No items yet";
          li.style.color = "var(--text-muted)";
          itemsList.appendChild(li);
        } else {
          for (var i = 0; i < items.length; i++) {
            var item = items[i];
            var li2 = document.createElement("li");
            var typeSpan = document.createElement("span");
            typeSpan.className = "tag";
            typeSpan.textContent = item.item_type;
            li2.appendChild(typeSpan);
            li2.appendChild(document.createTextNode(" ID: " + item.item_id));
            itemsList.appendChild(li2);
          }
        }
        show($("session-detail"));
      })
      .catch(function () {});
  }

  function backToSessions() {
    hide($("session-detail"));
    show($("sessions-list"));
    show(document.querySelector(".session-controls"));
  }

  function addToSession() {
    var select = $("session-select");
    var sessionId = select.value;
    if (!sessionId || !lastResultId || !lastResultType) return;
    fetch("/api/sessions/" + sessionId + "/items", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item_type: lastResultType, item_id: lastResultId }),
    })
      .then(function () {
        var btn = $("add-to-session-btn");
        btn.textContent = "Added";
        setTimeout(function () { btn.textContent = "Add"; }, 1500);
      })
      .catch(function () {});
  }

  function updateSessionAddVisibility() {
    var select = $("session-select");
    var addSection = $("session-add");
    if (lastResultId && select.options.length > 0) {
      show(addSection);
    } else {
      hide(addSection);
    }
  }

  // --- Init ---

  function init() {
    $("analyze-btn").addEventListener("click", analyze);

    $("claim-input").addEventListener("keydown", function (e) {
      if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
        analyze();
      }
    });

    var feedbackBtns = document.querySelectorAll(".feedback-btn");
    for (var i = 0; i < feedbackBtns.length; i++) {
      feedbackBtns[i].addEventListener("click", function () {
        sendFeedback(this.getAttribute("data-type"));
      });
    }

    $("create-session-btn").addEventListener("click", createSession);
    $("session-back-btn").addEventListener("click", backToSessions);
    $("add-to-session-btn").addEventListener("click", addToSession);

    $("session-name").addEventListener("keydown", function (e) {
      if (e.key === "Enter") createSession();
    });

    // Compare mode: toggle options on method change, load model list
    var radios = document.querySelectorAll('input[name="method"]');
    for (var j = 0; j < radios.length; j++) {
      radios[j].addEventListener("change", toggleCompareOptions);
    }
    loadModels();

    checkHealth();
    loadHistory();
    loadSessions();
    setInterval(checkHealth, 30000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
