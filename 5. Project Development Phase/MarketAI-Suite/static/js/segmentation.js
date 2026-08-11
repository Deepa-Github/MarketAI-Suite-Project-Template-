/* Audience Segmentation JS */

let currentSegmentationData = null;
let currentSegmentationInputs = null;

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('segmentationForm');
  if (form) {
    form.addEventListener('submit', handleSegmentationSubmit);
  }
});

async function handleSegmentationSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);

  const payload = {
    business_description: formData.get('business_description'),
    target_market: formData.get('target_market'),
    demographics: formData.get('demographics'),
    age_range: formData.get('age_range'),
    location: formData.get('location'),
    industry: formData.get('industry'),
    job_roles: formData.get('job_roles'),
    company_size: formData.get('company_size'),
    purchase_history: formData.get('purchase_history'),
    interests: formData.get('interests'),
    pain_points: formData.get('pain_points'),
    engagement_behavior: formData.get('engagement_behavior'),
    product_usage: formData.get('product_usage'),
    purchase_intent: formData.get('purchase_intent')
  };

  currentSegmentationInputs = payload;
  showLoadingState();

  try {
    const res = await apiFetch('/api/segments/generate', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    currentSegmentationData = res.data.segmentation;
    renderSegmentationResult(res.data.segmentation, res.data.loaded_from_history);
    showToast('Audience segments generated successfully!', 'success');
  } catch (err) {
    showToast(err.message || 'Failed to generate segments', 'error');
    hideLoadingState();
  }
}

function showLoadingState() {
  document.getElementById('resultsPlaceholder').classList.add('hidden');
  document.getElementById('segmentationResult').classList.add('hidden');
  const loading = document.getElementById('loadingState');
  loading.classList.remove('hidden');

  const msgs = [
    'Analyzing demographic & psychographic data...',
    'Clustering customer profiles into distinct segments...',
    'Creating buyer personas & messaging angles...',
    'Mapping channel preferences & recommended offers...'
  ];
  let idx = 0;
  const msgEl = document.getElementById('loadingMessages');
  msgEl.textContent = msgs[0];
  window.segmentationLoadingTimer = setInterval(() => {
    idx = (idx + 1) % msgs.length;
    msgEl.textContent = msgs[idx];
  }, 3000);
}

function hideLoadingState() {
  clearInterval(window.segmentationLoadingTimer);
  document.getElementById('loadingState').classList.add('hidden');
}

function renderSegmentationResult(data, isHistory = false) {
  hideLoadingState();
  const resDiv = document.getElementById('segmentationResult');
  resDiv.classList.remove('hidden');

  const badge = document.getElementById('sourceLabel');
  if (badge) {
    badge.textContent = isHistory ? '📚 Loaded from History' : '✨ Generated from AI';
    badge.className = isHistory ? 'history-badge from-history' : 'history-badge';
  }

  const container = document.getElementById('segmentsContent');
  const segments = data.segments || [];

  container.innerHTML = `
    ${data.segmentation_overview ? `
      <div class="result-section mb-4">
          <span class="result-section-title">Segmentation Overview</span>
          <p class="result-text mt-2">${escapeHtml(data.segmentation_overview)}</p>
      </div>
    ` : ''}

    <div class="segments-grid">
        ${segments.map((seg, idx) => `
            <div class="segment-card">
                <div class="segment-priority">
                    <span class="priority-badge ${seg.priority === 'High' ? 'priority-high' : seg.priority === 'Medium' ? 'priority-medium' : 'priority-low'}">
                        ${seg.priority || 'Medium'} Priority (${escapeHtml(seg.segment_size_estimate || 'N/A')})
                    </span>
                </div>
                <div class="segment-header">
                    <div class="segment-num">${idx + 1}</div>
                    <div>
                        <h3 class="segment-name">${escapeHtml(seg.segment_name)}</h3>
                        <p class="segment-description">${escapeHtml(seg.description)}</p>
                    </div>
                </div>
                <div class="segment-body">
                    <div class="segment-subsection">
                        <h4>🎯 Customer Needs &amp; Pain Points</h4>
                        <ul>
                            ${(seg.needs || []).map(n => `<li>${escapeHtml(n)}</li>`).join('')}
                            ${(seg.pain_points || []).map(p => `<li class="text-danger">${escapeHtml(p)}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="segment-subsection">
                        <h4>💬 Recommended Messaging</h4>
                        <p class="result-text"><strong>Headline:</strong> "${escapeHtml(seg.recommended_messaging?.headline || '')}"</p>
                        <p class="result-text mt-2"><strong>Core Message:</strong> ${escapeHtml(seg.recommended_messaging?.key_message || '')}</p>
                    </div>
                </div>
                <div class="mt-4 pt-4 border-top">
                    <h4>📢 Recommended Channels &amp; Offers</h4>
                    <div class="segment-channels">
                        ${(seg.recommended_channels || []).map(c => `<span class="tag primary">${escapeHtml(c.channel || c)}</span>`).join('')}
                        ${(seg.recommended_offers || []).map(o => `<span class="tag success">${escapeHtml(o.offer_type || o)}</span>`).join('')}
                    </div>
                </div>
            </div>
        `).join('')}
    </div>

    ${data.prioritisation_recommendation ? `
      <div class="result-section mt-6">
          <span class="result-section-title">Prioritisation Strategy</span>
          <p class="result-text mt-2">${escapeHtml(data.prioritisation_recommendation)}</p>
      </div>
    ` : ''}
  `;
}
