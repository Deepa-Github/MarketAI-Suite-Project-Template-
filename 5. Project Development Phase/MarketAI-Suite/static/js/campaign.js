/* Campaign Generator JS */

let currentCampaignData = null;
let currentCampaignInputs = null;

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('campaignInputForm');
  if (form) {
    form.addEventListener('submit', handleCampaignSubmit);
  }
});

async function handleCampaignSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  
  // Extract channels multi-select checkboxes
  const channels = [];
  form.querySelectorAll('input[name="channels"]:checked').forEach(cb => {
    channels.push(cb.value);
  });

  const payload = {
    product_name: formData.get('product_name'),
    product_description: formData.get('product_description'),
    key_features: formData.get('key_features'),
    benefits: formData.get('benefits'),
    target_audience: formData.get('target_audience'),
    age_range: formData.get('age_range'),
    location: formData.get('location'),
    industry: formData.get('industry'),
    brand_tone: formData.get('brand_tone'),
    pain_points: formData.get('pain_points'),
    campaign_objective: formData.get('campaign_objective'),
    channels: channels,
    campaign_duration: formData.get('campaign_duration'),
    budget: formData.get('budget'),
    competitors: formData.get('competitors'),
    additional_requirements: formData.get('additional_requirements')
  };

  currentCampaignInputs = payload;
  showLoadingState();

  try {
    const res = await apiFetch('/api/campaigns/generate', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    currentCampaignData = res.data.campaign;
    renderCampaignResult(res.data.campaign, res.data.loaded_from_history);
    showToast('Campaign generated successfully!', 'success');
  } catch (err) {
    showToast(err.message || 'Failed to generate campaign', 'error');
    hideLoadingState();
  }
}

function showLoadingState() {
  document.getElementById('resultsPlaceholder').classList.add('hidden');
  document.getElementById('campaignResult').classList.add('hidden');
  const loading = document.getElementById('loadingState');
  loading.classList.remove('hidden');
  
  const msgs = [
    'Analyzing target audience & positioning...',
    'Generating creative campaign slogans...',
    'Writing social media captions & email sequences...',
    'Structuring content calendar & KPIs...'
  ];
  let idx = 0;
  const msgEl = document.getElementById('loadingMessages');
  msgEl.textContent = msgs[0];
  window.campaignLoadingTimer = setInterval(() => {
    idx = (idx + 1) % msgs.length;
    msgEl.textContent = msgs[idx];
  }, 3000);
}

function hideLoadingState() {
  clearInterval(window.campaignLoadingTimer);
  document.getElementById('loadingState').classList.add('hidden');
}

function renderCampaignResult(campaign, isHistory = false) {
  hideLoadingState();
  const resDiv = document.getElementById('campaignResult');
  resDiv.classList.remove('hidden');

  document.getElementById('resultCampaignName').textContent = campaign.campaign_name || 'Generated Campaign';
  
  const badge = document.getElementById('sourceBadge');
  if (badge) {
    badge.textContent = isHistory ? '📚 Loaded from History' : '✨ Generated from AI';
    badge.className = isHistory ? 'history-badge from-history' : 'history-badge';
  }

  const container = document.getElementById('campaignContent');
  container.innerHTML = `
    <div class="result-section">
        <div class="result-section-header">
            <span class="result-section-title">Tagline & Objective</span>
            <button class="copy-btn" onclick="copyText('${escapeHtml(campaign.tagline || '')}')">📋 Copy</button>
        </div>
        <p class="result-text"><strong>Tagline:</strong> "${escapeHtml(campaign.tagline || '')}"</p>
        <p class="result-text mt-4"><strong>Objective:</strong> ${escapeHtml(campaign.objective || '')}</p>
    </div>

    <div class="result-section">
        <div class="result-section-header">
            <span class="result-section-title">Positioning &amp; Value Proposition</span>
        </div>
        <p class="result-text"><strong>Value Proposition:</strong> ${escapeHtml(campaign.value_proposition || '')}</p>
        <p class="result-text mt-4"><strong>Positioning Statement:</strong> ${escapeHtml(campaign.positioning_statement || '')}</p>
    </div>

    <div class="result-section">
        <div class="result-section-header">
            <span class="result-section-title">Campaign Slogans</span>
            <button class="copy-btn" onclick="copyText('${(campaign.slogans || []).map(s => escapeHtml(s)).join('\\n')}')">📋 Copy All</button>
        </div>
        <ul class="result-list">
            ${(campaign.slogans || []).map(slogan => `<li>"${escapeHtml(slogan)}"</li>`).join('')}
        </ul>
    </div>

    <div class="result-section">
        <div class="result-section-header">
            <span class="result-section-title">Promotional Content</span>
        </div>
        ${(campaign.promotional_content || []).map(promo => `
            <div class="mb-4">
                <span class="tag primary">${escapeHtml(promo.type || 'Ad')}</span>
                <h4 class="fw-bold mt-4">${escapeHtml(promo.headline || '')}</h4>
                <p class="result-text">${escapeHtml(promo.body || '')}</p>
                <p class="result-text mt-4"><strong>CTA:</strong> <span class="tag success">${escapeHtml(promo.cta || '')}</span></p>
            </div>
        `).join('')}
    </div>

    <div class="result-section">
        <div class="result-section-header">
            <span class="result-section-title">Social Media Content</span>
        </div>
        ${(campaign.social_media || []).map(soc => `
            <div class="mb-4 p-3 bg-light border-radius">
                <span class="tag info">${escapeHtml(soc.platform || '')}</span>
                <p class="result-text mt-4"><strong>Caption:</strong> ${escapeHtml(soc.caption || '')}</p>
                <p class="result-text mt-4"><strong>Idea:</strong> ${escapeHtml(soc.content_idea || '')}</p>
                <button class="copy-btn mt-4" onclick="copyText('${escapeHtml(soc.caption || '')}')">📋 Copy Caption</button>
            </div>
        `).join('')}
    </div>

    <div class="result-section">
        <div class="result-section-header">
            <span class="result-section-title">Email Campaign Ideas</span>
        </div>
        ${(campaign.email_campaign || []).map(email => `
            <div class="mb-4">
                <span class="tag warning">${escapeHtml(email.sequence_name || 'Email')}</span>
                <p class="result-text mt-4"><strong>Subject Line:</strong> ${escapeHtml(email.subject_line || '')}</p>
                <p class="result-text mt-4"><strong>Outline:</strong> ${escapeHtml(email.email_body_outline || '')}</p>
            </div>
        `).join('')}
    </div>

    <div class="result-section">
        <div class="result-section-header">
            <span class="result-section-title">Campaign Timeline &amp; KPIs</span>
        </div>
        <h4 class="fw-bold">Timeline</h4>
        <ul class="result-list">
            ${(campaign.campaign_timeline || []).map(t => `<li><strong>${escapeHtml(t.phase)} (${escapeHtml(t.duration)}):</strong> Focus on ${escapeHtml(t.focus)}</li>`).join('')}
        </ul>
        <h4 class="fw-bold mt-4">Key Performance Indicators (KPIs)</h4>
        <ul class="result-list">
            ${(campaign.kpis || []).map(k => `<li><strong>${escapeHtml(k.metric)}:</strong> Target: ${escapeHtml(k.target)}</li>`).join('')}
        </ul>
    </div>
  `;
}

function copyCampaignResult() {
  if (!currentCampaignData) return;
  copyToClipboard(JSON.stringify(currentCampaignData, null, 2), 'Full campaign copied as JSON!');
}

function copyText(str) {
  copyToClipboard(str);
}

async function regenerateCampaign() {
  if (!currentCampaignInputs) return;
  showLoadingState();
  try {
    const res = await apiFetch('/api/campaigns/generate', {
      method: 'POST',
      body: JSON.stringify(currentCampaignInputs)
    });
    currentCampaignData = res.data.campaign;
    renderCampaignResult(res.data.campaign, false);
    showToast('Regenerated campaign successfully!', 'success');
  } catch (err) {
    showToast(err.message || 'Failed to regenerate campaign', 'error');
    hideLoadingState();
  }
}
