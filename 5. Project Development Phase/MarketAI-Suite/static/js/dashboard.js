/* Dashboard JS */

document.addEventListener('DOMContentLoaded', () => {
  loadDashboardData();
});

async function loadDashboardData() {
  try {
    const res = await apiFetch('/api/dashboard/summary');
    const metrics = res.data.metrics || {};
    const recent = res.data.recent_activity || [];

    renderMetrics(metrics);
    renderRecentActivity(recent);
    renderCharts(metrics);
  } catch (err) {
    showToast('Failed to load dashboard metrics', 'error');
  }
}

function renderMetrics(m) {
  setMetric('totalCampaigns', m.total_campaigns || 0);
  setMetric('totalPitches', m.total_sales_pitches || 0);
  setMetric('totalLeads', m.total_leads || 0);
  setMetric('highPriorityLeads', m.high_priority_leads || 0);
  setMetric('mediumPriorityLeads', m.medium_priority_leads || 0);
  setMetric('avgLeadScore', m.avg_lead_score ? `${m.avg_lead_score}/100` : '—');
  setMetric('totalSegments', m.total_segmentations || 0);
  setMetric('totalStrategies', m.total_strategies || 0);

  // Remove skeleton class
  document.querySelectorAll('.loading-skeleton').forEach(el => el.classList.remove('loading-skeleton'));
}

function setMetric(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function renderRecentActivity(activities) {
  const container = document.getElementById('recentActivity');
  if (!container) return;

  if (!activities.length) {
    container.innerHTML = '<p class="text-muted text-center py-4">No recent activity recorded yet.</p>';
    return;
  }

  const icons = {
    campaign: '🎯',
    sales_pitch: '💼',
    lead_scoring: '📈',
    segmentation: '👥',
    strategy: '🗺️',
    recommendation: '⚡'
  };

  container.innerHTML = activities.map(act => `
    <div class="activity-item">
        <div class="activity-icon">${icons[act.generation_type] || '📌'}</div>
        <div class="activity-text">
            <span class="activity-type">${escapeHtml(act.generation_type.replace('_', ' ').toUpperCase())}:</span>
            ${escapeHtml(act.title)}
        </div>
        <div class="activity-time">${formatDate(act.created_at)}</div>
    </div>
  `).join('');
}

function renderCharts(m) {
  // Pure CSS Bar Chart for Lead Priorities
  const priorityChart = document.getElementById('priorityChart');
  if (priorityChart) {
    const high = m.high_priority_leads || 0;
    const med = m.medium_priority_leads || 0;
    const low = m.low_priority_leads || 0;
    const max = Math.max(high, med, low, 1);

    const hPct = Math.round((high / max) * 100);
    const mPct = Math.round((med / max) * 100);
    const lPct = Math.round((low / max) * 100);

    priorityChart.innerHTML = `
      <div class="bar-chart">
          <div class="bar-col">
              <span class="bar-val">${high}</span>
              <div class="bar-fill high" style="height:${hPct}%"></div>
              <span class="bar-label">High Priority</span>
          </div>
          <div class="bar-col">
              <span class="bar-val">${med}</span>
              <div class="bar-fill medium" style="height:${mPct}%"></div>
              <span class="bar-label">Medium Priority</span>
          </div>
          <div class="bar-col">
              <span class="bar-val">${low}</span>
              <div class="bar-fill low" style="height:${lPct}%"></div>
              <span class="bar-label">Low Priority</span>
          </div>
      </div>
    `;
  }

  // Pure CSS Bar Chart for AI Activities
  const activityChart = document.getElementById('activityChart');
  if (activityChart) {
    const c = m.total_campaigns || 0;
    const p = m.total_sales_pitches || 0;
    const s = m.total_segmentations || 0;
    const st = m.total_strategies || 0;
    const maxAct = Math.max(c, p, s, st, 1);

    activityChart.innerHTML = `
      <div class="bar-chart">
          <div class="bar-col">
              <span class="bar-val">${c}</span>
              <div class="bar-fill primary" style="height:${Math.round((c/maxAct)*100)}%"></div>
              <span class="bar-label">Campaigns</span>
          </div>
          <div class="bar-col">
              <span class="bar-val">${p}</span>
              <div class="bar-fill primary" style="height:${Math.round((p/maxAct)*100)}%"></div>
              <span class="bar-label">Pitches</span>
          </div>
          <div class="bar-col">
              <span class="bar-val">${s}</span>
              <div class="bar-fill primary" style="height:${Math.round((s/maxAct)*100)}%"></div>
              <span class="bar-label">Segments</span>
          </div>
          <div class="bar-col">
              <span class="bar-val">${st}</span>
              <div class="bar-fill primary" style="height:${Math.round((st/maxAct)*100)}%"></div>
              <span class="bar-label">Strategies</span>
          </div>
      </div>
    `;
  }
}
