/* Lead Scoring JS */

let currentLeads = [];
let filteredLeads = [];
let currentLeadHistoryId = null;
let selectedFile = null;
let currentSortField = 'lead_score';
let sortAscending = false;

document.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  setupUploadZone();
  setupManualForm();
  setupTableControls();
});

function setupTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(btn => {
    btn.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const target = document.getElementById(btn.dataset.tab);
      if (target) target.classList.add('active');
    });
  });
}

function setupUploadZone() {
  const zone = document.getElementById('uploadZone');
  const fileInput = document.getElementById('csvFile');
  const uploadBtn = document.getElementById('uploadBtn');

  if (!zone || !fileInput) return;

  zone.addEventListener('click', () => fileInput.click());

  zone.addEventListener('dragover', (e) => {
    e.preventDefault();
    zone.classList.add('drag-over');
  });

  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));

  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    if (e.dataTransfer.files.length) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
      handleFileSelection(e.target.files[0]);
    }
  });

  if (uploadBtn) {
    uploadBtn.addEventListener('click', uploadAndScoreCSV);
  }
}

function handleFileSelection(file) {
  if (!file.name.endsWith('.csv')) {
    showToast('Please select a valid CSV file', 'error');
    return;
  }
  selectedFile = file;
  const zone = document.getElementById('uploadZone');
  zone.classList.add('has-file');
  zone.querySelector('h3').textContent = `Selected: ${file.name}`;
  zone.querySelector('p').textContent = `${(file.size / 1024).toFixed(1)} KB`;
  document.getElementById('uploadBtn').disabled = false;
}

async function uploadAndScoreCSV() {
  if (!selectedFile) return;

  const btn = document.getElementById('uploadBtn');
  btn.disabled = true;
  showLoadingState();

  const formData = new FormData();
  formData.append('file', selectedFile);

  try {
    const response = await fetch('/api/leads/upload', {
      method: 'POST',
      body: formData
    });
    const res = await response.json();
    if (!response.ok || !res.success) {
      throw new Error(res.error?.message || 'CSV processing failed');
    }

    currentLeads = res.data.scored_leads || [];
    currentLeadHistoryId = res.data.history_id;
    filteredLeads = [...currentLeads];

    renderSummary(res.data.summary);
    renderLeadsTable();
    if (res.data.batch_insights) {
      renderBatchInsights(res.data.batch_insights);
    }
    showToast('Leads scored successfully!', 'success');
  } catch (err) {
    showToast(err.message || 'Failed to process CSV', 'error');
  } finally {
    hideLoadingState();
    btn.disabled = false;
  }
}

function setupManualForm() {
  const form = document.getElementById('manualLeadForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const payload = {};
    formData.forEach((val, key) => payload[key] = val);

    showLoadingState();

    try {
      const res = await apiFetch('/api/leads/score', {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      const scoredLead = res.data.lead;
      currentLeads = [scoredLead];
      currentLeadHistoryId = res.data.history_id;
      filteredLeads = [...currentLeads];

      renderSummary({
        total_leads: 1,
        high_priority: scoredLead.priority === 'High' ? 1 : 0,
        medium_priority: scoredLead.priority === 'Medium' ? 1 : 0,
        low_priority: scoredLead.priority === 'Low' ? 1 : 0,
        avg_score: scoredLead.lead_score
      });
      renderLeadsTable();
      showToast('Lead scored successfully!', 'success');
    } catch (err) {
      showToast(err.message || 'Failed to score lead', 'error');
    } finally {
      hideLoadingState();
    }
  });
}

function showLoadingState() {
  document.getElementById('leadResults').classList.add('hidden');
  const loading = document.getElementById('loadingState');
  loading.classList.remove('hidden');

  const msgs = [
    'Parsing lead dataset & extracting features...',
    'Running deterministic scoring algorithm...',
    'Evaluating AI contextual conversion probability...',
    'Generating prioritized lead recommendations...'
  ];
  let idx = 0;
  const msgEl = document.getElementById('loadingMessages');
  msgEl.textContent = msgs[0];
  window.leadLoadingTimer = setInterval(() => {
    idx = (idx + 1) % msgs.length;
    msgEl.textContent = msgs[idx];
  }, 2500);
}

function hideLoadingState() {
  clearInterval(window.leadLoadingTimer);
  document.getElementById('loadingState').classList.add('hidden');
  document.getElementById('leadResults').classList.remove('hidden');
}

function renderSummary(summary) {
  const el = document.getElementById('leadSummary');
  if (!el || !summary) return;

  el.innerHTML = `
    <div class="summary-card primary">
        <div class="summary-card-value">${summary.total_leads || 0}</div>
        <div class="summary-card-label">Total Leads</div>
    </div>
    <div class="summary-card danger">
        <div class="summary-card-value">${summary.high_priority || 0}</div>
        <div class="summary-card-label">🔥 High Priority</div>
    </div>
    <div class="summary-card warning">
        <div class="summary-card-value">${summary.medium_priority || 0}</div>
        <div class="summary-card-label">⚡ Medium Priority</div>
    </div>
    <div class="summary-card info">
        <div class="summary-card-value">${summary.low_priority || 0}</div>
        <div class="summary-card-label">❄️ Low Priority</div>
    </div>
    <div class="summary-card success">
        <div class="summary-card-value">${summary.avg_score || 0}</div>
        <div class="summary-card-label">Avg AI Score</div>
    </div>
  `;
}

function setupTableControls() {
  const searchInput = document.getElementById('leadSearch');
  const priorityFilter = document.getElementById('priorityFilter');
  const exportBtn = document.getElementById('exportLeadsBtn');

  if (searchInput) {
    searchInput.addEventListener('input', filterLeads);
  }
  if (priorityFilter) {
    priorityFilter.addEventListener('change', filterLeads);
  }
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      if (currentLeadHistoryId) {
        window.location.href = `/api/leads/${currentLeadHistoryId}/export`;
      } else {
        showToast('No lead session to export', 'warning');
      }
    });
  }

  // Sortable headers
  document.querySelectorAll('.sortable').forEach(th => {
    th.addEventListener('click', () => {
      const field = th.dataset.sort;
      if (currentSortField === field) {
        sortAscending = !sortAscending;
      } else {
        currentSortField = field;
        sortAscending = false;
      }
      sortLeads();
      renderLeadsTable();
    });
  });
}

function filterLeads() {
  const query = (document.getElementById('leadSearch')?.value || '').toLowerCase();
  const priority = document.getElementById('priorityFilter')?.value || '';

  filteredLeads = currentLeads.filter(lead => {
    const matchesSearch = !query ||
      (lead.name || '').toLowerCase().includes(query) ||
      (lead.company || '').toLowerCase().includes(query) ||
      (lead.email || '').toLowerCase().includes(query) ||
      (lead.industry || '').toLowerCase().includes(query);
    const matchesPriority = !priority || lead.priority === priority;
    return matchesSearch && matchesPriority;
  });

  sortLeads();
  renderLeadsTable();
}

function sortLeads() {
  filteredLeads.sort((a, b) => {
    const valA = a[currentSortField] ?? 0;
    const valB = b[currentSortField] ?? 0;
    if (valA < valB) return sortAscending ? -1 : 1;
    if (valA > valB) return sortAscending ? 1 : -1;
    return 0;
  });
}

function renderLeadsTable() {
  const tbody = document.getElementById('leadsTableBody');
  if (!tbody) return;

  if (!filteredLeads.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No leads match the filters.</td></tr>';
    return;
  }

  tbody.innerHTML = filteredLeads.map(lead => {
    const priorityClass = lead.priority === 'High' ? 'priority-high' :
      lead.priority === 'Medium' ? 'priority-medium' : 'priority-low';
    const priorityIcon = lead.priority === 'High' ? '🔥' : lead.priority === 'Medium' ? '⚡' : '❄️';
    const conversion = lead.ai_conversion_estimate ? `${Math.round(lead.ai_conversion_estimate * 100)}%` : '—';

    return `
      <tr>
          <td>
              <div class="lead-name">${escapeHtml(lead.name || 'Unknown')}</div>
              <div class="lead-email">${escapeHtml(lead.email || '')}</div>
          </td>
          <td>${escapeHtml(lead.company || '—')}</td>
          <td>${escapeHtml(lead.industry || '—')}</td>
          <td>
              <span class="fw-bold">${lead.lead_score || 0}</span>/100
          </td>
          <td>
              <span class="priority-badge ${priorityClass}">${priorityIcon} ${escapeHtml(lead.priority || 'Low')}</span>
          </td>
          <td>${conversion} <small class="text-muted">(Est)</small></td>
          <td>${escapeHtml(lead.recommended_action || 'Follow up')}</td>
      </tr>
    `;
  }).join('');
}

function renderBatchInsights(insights) {
  const card = document.getElementById('batchInsightsCard');
  const content = document.getElementById('batchInsightsContent');
  if (!card || !content || !insights) return;

  card.style.display = 'block';
  content.innerHTML = `
    <div class="result-section">
        <h4 class="fw-bold">Key Insights</h4>
        <ul class="result-list">
            ${(insights.key_insights || []).map(ins => `<li>${escapeHtml(ins)}</li>`).join('')}
        </ul>
        <h4 class="fw-bold mt-4">Immediate Actions</h4>
        <ul class="result-list">
            ${(insights.immediate_actions || []).map(act => `<li>${escapeHtml(act)}</li>`).join('')}
        </ul>
        ${insights.nurture_strategy ? `<p class="mt-4"><strong>Nurture Strategy:</strong> ${escapeHtml(insights.nurture_strategy)}</p>` : ''}
    </div>
  `;
}
