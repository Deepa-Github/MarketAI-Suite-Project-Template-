/* History JS */

let currentHistoryPage = 1;
let currentHistoryType = '';
let currentSearchQuery = '';
let selectedHistoryRecord = null;

document.addEventListener('DOMContentLoaded', () => {
  loadHistory();

  const searchInput = document.getElementById('historySearch');
  const typeFilter = document.getElementById('typeFilter');
  const refreshBtn = document.getElementById('refreshHistoryBtn');

  if (searchInput) {
    let debounceTimer;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        currentSearchQuery = e.target.value;
        currentHistoryPage = 1;
        loadHistory();
      }, 300);
    });
  }

  if (typeFilter) {
    typeFilter.addEventListener('change', (e) => {
      currentHistoryType = e.target.value;
      currentHistoryPage = 1;
      loadHistory();
    });
  }

  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => loadHistory());
  }
});

async function loadHistory() {
  const container = document.getElementById('historyContainer');
  if (!container) return;

  container.innerHTML = '<div class="loading-spinner"></div>';

  let url = `/api/history?page=${currentHistoryPage}&per_page=12`;
  if (currentHistoryType) url += `&type=${encodeURIComponent(currentHistoryType)}`;
  if (currentSearchQuery) url += `&search=${encodeURIComponent(currentSearchQuery)}`;

  try {
    const res = await apiFetch(url);
    const items = res.data.items || [];
    const pagination = res.data.pagination || {};

    if (!items.length) {
      container.innerHTML = `
        <div class="results-placeholder" style="grid-column: 1/-1">
            <div class="placeholder-icon">🕐</div>
            <h3>No History Found</h3>
            <p>${currentSearchQuery || currentHistoryType ? 'No records match your filters. Try resetting the filters.' : 'You haven\'t generated anything yet. Try creating a campaign, sales pitch, or lead analysis.'}</p>
        </div>
      `;
      renderPagination(pagination);
      return;
    }

    container.innerHTML = `
      <div class="history-grid">
          ${items.map(item => renderHistoryCard(item)).join('')}
      </div>
    `;

    renderPagination(pagination);
  } catch (err) {
    showToast(err.message || 'Failed to load history', 'error');
    container.innerHTML = '<p class="text-danger text-center">Failed to load history records.</p>';
  }
}

function renderHistoryCard(item) {
  const typeIcons = {
    campaign: '🎯 Campaign',
    sales_pitch: '💼 Sales Pitch',
    lead_scoring: '📈 Lead Scoring',
    segmentation: '👥 Segmentation',
    strategy: '🗺️ Strategy',
    recommendation: '⚡ Recommendations'
  };

  const typeLabel = typeIcons[item.generation_type] || item.generation_type;

  return `
    <div class="history-item" onclick="openHistoryItem('${item.id}')">
        <div class="history-item-type">${typeLabel}</div>
        <h4 class="history-item-title">${escapeHtml(item.title)}</h4>
        <div class="history-item-date">${formatDate(item.created_at)}</div>
        <div class="history-item-actions">
            <span class="btn btn-ghost btn-sm">📖 View Result (No AI Request)</span>
        </div>
    </div>
  `;
}

async function openHistoryItem(recordId) {
  const modal = document.getElementById('historyModal');
  const body = document.getElementById('modalBody');
  const title = document.getElementById('modalTitle');
  const badge = document.getElementById('modalTypeBadge');

  if (!modal || !body) return;

  modal.classList.remove('hidden');
  body.innerHTML = '<div class="loading-spinner"></div>';

  try {
    // IMPORTANT: This API call loads the saved result from SQLite database.
    // It NEVER calls Groq AI API.
    const res = await apiFetch(`/api/history/${recordId}`);
    selectedHistoryRecord = res.data;

    title.textContent = res.data.title || 'History Item';
    badge.textContent = res.data.generation_type;

    body.innerHTML = renderHistoryDetailContent(res.data);

    // Setup action buttons
    document.getElementById('modalDeleteBtn').onclick = () => deleteHistoryItem(recordId);
    document.getElementById('modalReuseBtn').onclick = () => reuseHistoryInputs(res.data);

  } catch (err) {
    showToast(err.message || 'Failed to load record', 'error');
    closeHistoryModal();
  }
}

function renderHistoryDetailContent(record) {
  const output = record.ai_output || {};
  const type = record.generation_type;

  let contentHtml = '';

  if (type === 'campaign') {
    contentHtml = `
      <p><strong>Tagline:</strong> "${escapeHtml(output.tagline || '')}"</p>
      <p class="mt-2"><strong>Value Prop:</strong> ${escapeHtml(output.value_proposition || '')}</p>
      <h4 class="fw-bold mt-4">Slogans</h4>
      <ul class="result-list">${(output.slogans || []).map(s => `<li>"${escapeHtml(s)}"</li>`).join('')}</ul>
    `;
  } else if (type === 'sales_pitch') {
    contentHtml = `
      <p><strong>Executive Summary:</strong> ${escapeHtml(output.executive_summary || '')}</p>
      <p class="mt-2"><strong>Elevator Pitch:</strong> "${escapeHtml(output.elevator_pitch || '')}"</p>
    `;
  } else if (type === 'lead_scoring') {
    const leads = output.scored_leads || [];
    contentHtml = `
      <p><strong>Scored Leads:</strong> ${leads.length}</p>
      <ul class="result-list">
          ${leads.slice(0, 10).map(l => `<li><strong>${escapeHtml(l.name)} (${escapeHtml(l.company)}):</strong> Score ${l.lead_score}/100 — Priority: ${l.priority}</li>`).join('')}
      </ul>
    `;
  } else {
    contentHtml = `<pre class="code-block">${escapeHtml(JSON.stringify(output, null, 2))}</pre>`;
  }

  return `
    <div class="result-section">
        <p class="text-muted text-xs mb-4">Saved on: ${formatDate(record.created_at)} | ID: ${record.id}</p>
        ${contentHtml}
    </div>
  `;
}

function closeHistoryModal() {
  const modal = document.getElementById('historyModal');
  if (modal) modal.classList.add('hidden');
}

async function deleteHistoryItem(recordId) {
  if (!confirm('Are you sure you want to delete this history item?')) return;

  try {
    await apiFetch(`/api/history/${recordId}`, { method: 'DELETE' });
    showToast('Record deleted from history', 'success');
    closeHistoryModal();
    loadHistory();
  } catch (err) {
    showToast(err.message || 'Failed to delete record', 'error');
  }
}

function reuseHistoryInputs(record) {
  const type = record.generation_type;
  const typePageMap = {
    campaign: '/campaign',
    sales_pitch: '/sales-pitch',
    lead_scoring: '/lead-scoring',
    segmentation: '/segmentation',
    strategy: '/strategy'
  };
  const targetPage = typePageMap[type];
  if (targetPage) {
    sessionStorage.setItem('reuse_inputs', JSON.stringify(record.user_inputs));
    window.location.href = targetPage;
  }
}

function renderPagination(pagination) {
  const container = document.getElementById('historyPagination');
  if (!container || !pagination || pagination.pages <= 1) {
    if (container) container.innerHTML = '';
    return;
  }

  let html = '';
  if (pagination.page > 1) {
    html += `<button class="page-btn" onclick="goToPage(${pagination.page - 1})">← Previous</button>`;
  }
  for (let i = 1; i <= pagination.pages; i++) {
    html += `<button class="page-btn ${i === pagination.page ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
  }
  if (pagination.page < pagination.pages) {
    html += `<button class="page-btn" onclick="goToPage(${pagination.page + 1})">Next →</button>`;
  }
  container.innerHTML = html;
}

function goToPage(page) {
  currentHistoryPage = page;
  loadHistory();
}
