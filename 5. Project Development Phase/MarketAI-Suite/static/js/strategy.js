/* Strategy & Recommendations JS */

let currentStrategyData = null;
let currentStrategyInputs = null;

document.addEventListener('DOMContentLoaded', () => {
  const stratForm = document.getElementById('strategyForm');
  if (stratForm) {
    stratForm.addEventListener('submit', handleStrategySubmit);
  }

  const recBtn = document.getElementById('recommendationsBtn');
  if (recBtn) {
    recBtn.addEventListener('click', handleRecommendationsSubmit);
  }
});

async function handleStrategySubmit(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);

  const channels = [];
  form.querySelectorAll('input[name="channels"]:checked').forEach(cb => channels.push(cb.value));

  const payload = {
    business_name: formData.get('business_name'),
    industry: formData.get('industry'),
    target_market: formData.get('target_market'),
    unique_selling_points: formData.get('unique_selling_points'),
    current_situation: formData.get('current_situation'),
    marketing_objective: formData.get('marketing_objective'),
    business_goals: formData.get('business_goals'),
    budget: formData.get('budget'),
    timeframe: formData.get('timeframe'),
    competitors: formData.get('competitors'),
    customer_pain_points: formData.get('customer_pain_points'),
    channels: channels
  };

  currentStrategyInputs = payload;
  showLoadingState();

  try {
    const res = await apiFetch('/api/strategies/generate', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    currentStrategyData = res.data.strategy;
    renderStrategyResult(res.data.strategy, res.data.loaded_from_history);
    showToast('Strategy generated successfully!', 'success');
  } catch (err) {
    showToast(err.message || 'Failed to generate strategy', 'error');
    hideLoadingState();
  }
}

async function handleRecommendationsSubmit(e) {
  e.preventDefault();
  const context = document.getElementById('rec_context')?.value || '';
  const objective = document.getElementById('business_objective')?.value || '';

  showLoadingState();

  try {
    const res = await apiFetch('/api/recommendations/generate', {
      method: 'POST',
      body: JSON.stringify({ context, business_objective: objective })
    });
    renderRecommendationsResult(res.data.recommendations, res.data.loaded_from_history);
    showToast('Recommendations generated successfully!', 'success');
  } catch (err) {
    showToast(err.message || 'Failed to generate recommendations', 'error');
    hideLoadingState();
  }
}

function showLoadingState() {
  document.getElementById('resultsPlaceholder').classList.add('hidden');
  document.getElementById('strategyResult').classList.add('hidden');
  const loading = document.getElementById('loadingState');
  loading.classList.remove('hidden');

  const msgs = [
    'Evaluating market opportunity & competitive landscape...',
    'Formulating brand positioning & channel mix...',
    'Designing acquisition, retention, and content strategies...',
    'Building implementation roadmap & risk mitigations...'
  ];
  let idx = 0;
  const msgEl = document.getElementById('loadingMessages');
  msgEl.textContent = msgs[0];
  window.strategyLoadingTimer = setInterval(() => {
    idx = (idx + 1) % msgs.length;
    msgEl.textContent = msgs[idx];
  }, 3000);
}

function hideLoadingState() {
  clearInterval(window.strategyLoadingTimer);
  document.getElementById('loadingState').classList.add('hidden');
}

function renderStrategyResult(strat, isHistory = false) {
  hideLoadingState();
  const resDiv = document.getElementById('strategyResult');
  resDiv.classList.remove('hidden');

  document.getElementById('strategyTitle').textContent = strat.strategy_title || 'Marketing Strategy';
  const badge = document.getElementById('sourceLabel');
  if (badge) {
    badge.textContent = isHistory ? '📚 Loaded from History' : '✨ Generated from AI';
    badge.className = isHistory ? 'history-badge from-history' : 'history-badge';
  }

  const container = document.getElementById('strategyContent');
  container.innerHTML = `
    <div class="result-section">
        <span class="result-section-title">Executive Summary</span>
        <p class="result-text mt-2">${escapeHtml(strat.executive_summary || '')}</p>
    </div>

    <div class="result-section">
        <span class="result-section-title">Market Positioning</span>
        <p class="result-text"><strong>Positioning Statement:</strong> ${escapeHtml(strat.market_positioning?.positioning_statement || '')}</p>
        <p class="result-text mt-2"><strong>Brand Promise:</strong> ${escapeHtml(strat.market_positioning?.brand_promise || '')}</p>
    </div>

    <div class="result-section">
        <span class="result-section-title">Channel Strategy &amp; Budget Allocation</span>
        <ul class="result-list">
            ${(strat.channel_strategy || []).map(ch => `
                <li>
                    <div>
                        <strong>${escapeHtml(ch.channel)}</strong> (${ch.budget_allocation_pct}% budget) — Role: ${escapeHtml(ch.role)}
                        <br><small class="text-muted">KPI: ${escapeHtml(ch.kpi)}</small>
                    </div>
                </li>
            `).join('')}
        </ul>
    </div>

    <div class="result-section">
        <span class="result-section-title">Implementation Roadmap</span>
        ${(strat.implementation_roadmap || []).map(ph => `
            <div class="mb-4">
                <span class="tag primary">${escapeHtml(ph.phase)} (${escapeHtml(ph.timeline)})</span>
                <p class="result-text mt-2"><strong>Focus:</strong> ${escapeHtml(ph.focus)}</p>
                <ul class="result-list mt-2">
                    ${(ph.key_actions || []).map(act => `<li>${escapeHtml(act)}</li>`).join('')}
                </ul>
            </div>
        `).join('')}
    </div>

    <div class="result-section">
        <span class="result-section-title">Risks &amp; Mitigations</span>
        <ul class="result-list">
            ${(strat.risks || []).map(r => `
                <li>
                    <div>
                        <strong class="text-danger">${escapeHtml(r.risk)}</strong> (Impact: ${escapeHtml(r.impact)})
                        <br><small class="text-muted">Mitigation: ${escapeHtml(r.mitigation)}</small>
                    </div>
                </li>
            `).join('')}
        </ul>
    </div>

    <div class="result-section">
        <span class="result-section-title">Quick Wins (First 30 Days)</span>
        <ul class="result-list">
            ${(strat.quick_wins || []).map(qw => `<li>${escapeHtml(qw)}</li>`).join('')}
        </ul>
    </div>
  `;
}

function renderRecommendationsResult(recs, isHistory = false) {
  hideLoadingState();
  const resDiv = document.getElementById('strategyResult');
  resDiv.classList.remove('hidden');

  document.getElementById('strategyTitle').textContent = '⚡ Next Best Action Recommendations';

  const container = document.getElementById('strategyContent');
  container.innerHTML = `
    <div class="result-section">
        <span class="result-section-title">Priority Actions</span>
        <ul class="result-list">
            ${(recs.priority_actions || []).map(act => `
                <li class="mb-3">
                    <div>
                        <span class="priority-badge ${act.priority === 'Immediate' || act.priority === 'High' ? 'priority-high' : 'priority-medium'}">${escapeHtml(act.priority)}</span>
                        <strong class="ms-2">${escapeHtml(act.action)}</strong>
                        <p class="result-text mt-1">Reason: ${escapeHtml(act.reason)}</p>
                        <small class="text-muted">Channel: ${escapeHtml(act.channel)} | Timing: ${escapeHtml(act.timing)}</small>
                    </div>
                </li>
            `).join('')}
        </ul>
    </div>

    <div class="result-section">
        <span class="result-section-title">Quick Wins</span>
        <ul class="result-list">
            ${(recs.quick_wins || []).map(qw => `<li>${escapeHtml(qw)}</li>`).join('')}
        </ul>
    </div>
  `;
}

function copyStrategyResult() {
  if (!currentStrategyData) return;
  copyToClipboard(JSON.stringify(currentStrategyData, null, 2), 'Full strategy copied as JSON!');
}

async function regenerateStrategy() {
  if (!currentStrategyInputs) return;
  showLoadingState();
  try {
    const res = await apiFetch('/api/strategies/generate', {
      method: 'POST',
      body: JSON.stringify(currentStrategyInputs)
    });
    currentStrategyData = res.data.strategy;
    renderStrategyResult(res.data.strategy, false);
    showToast('Regenerated strategy successfully!', 'success');
  } catch (err) {
    showToast(err.message || 'Failed to regenerate strategy', 'error');
    hideLoadingState();
  }
}
