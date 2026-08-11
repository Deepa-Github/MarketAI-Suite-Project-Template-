/* Sales Pitch Generator JS */

let currentPitchData = null;
let currentPitchInputs = null;

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('salesPitchForm');
  if (form) {
    form.addEventListener('submit', handlePitchSubmit);
  }
});

async function handlePitchSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);

  const payload = {
    product_name: formData.get('product_name'),
    product_description: formData.get('product_description'),
    unique_selling_points: formData.get('unique_selling_points'),
    customer_name: formData.get('customer_name'),
    customer_industry: formData.get('customer_industry'),
    customer_role: formData.get('customer_role'),
    business_challenges: formData.get('business_challenges'),
    pain_points: formData.get('pain_points'),
    customer_goals: formData.get('customer_goals'),
    competitors: formData.get('competitors'),
    desired_outcome: formData.get('desired_outcome'),
    sales_tone: formData.get('sales_tone')
  };

  currentPitchInputs = payload;
  showLoadingState();

  try {
    const res = await apiFetch('/api/sales-pitches/generate', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    currentPitchData = res.data.pitch;
    renderPitchResult(res.data.pitch, res.data.loaded_from_history);
    showToast('Sales pitch generated successfully!', 'success');
  } catch (err) {
    showToast(err.message || 'Failed to generate sales pitch', 'error');
    hideLoadingState();
  }
}

function showLoadingState() {
  document.getElementById('resultsPlaceholder').classList.add('hidden');
  document.getElementById('pitchResult').classList.add('hidden');
  const loading = document.getElementById('loadingState');
  loading.classList.remove('hidden');

  const msgs = [
    'Analyzing customer profile & business challenges...',
    'Crafting tailored value proposition & elevator pitch...',
    'Mapping pain points to product solutions...',
    'Formulating objection handling & discovery questions...'
  ];
  let idx = 0;
  const msgEl = document.getElementById('loadingMessages');
  msgEl.textContent = msgs[0];
  window.pitchLoadingTimer = setInterval(() => {
    idx = (idx + 1) % msgs.length;
    msgEl.textContent = msgs[idx];
  }, 3000);
}

function hideLoadingState() {
  clearInterval(window.pitchLoadingTimer);
  document.getElementById('loadingState').classList.add('hidden');
}

function renderPitchResult(pitch, isHistory = false) {
  hideLoadingState();
  const resDiv = document.getElementById('pitchResult');
  resDiv.classList.remove('hidden');

  const badge = document.getElementById('sourceBadge');
  if (badge) {
    badge.textContent = isHistory ? '📚 Loaded from History' : '✨ Generated from AI';
    badge.className = isHistory ? 'history-badge from-history' : 'history-badge';
  }

  const container = document.getElementById('pitchContent');
  container.innerHTML = `
    <div class="result-section">
        <div class="result-section-header">
            <span class="result-section-title">Executive Summary</span>
            <button class="copy-btn" onclick="copyText('${escapeHtml(pitch.executive_summary || '')}')">📋 Copy</button>
        </div>
        <p class="result-text">${escapeHtml(pitch.executive_summary || '')}</p>
    </div>

    <div class="result-section">
        <div class="result-section-header">
            <span class="result-section-title">Elevator Pitch (30-Sec)</span>
            <button class="copy-btn" onclick="copyText('${escapeHtml(pitch.elevator_pitch || '')}')">📋 Copy Pitch</button>
        </div>
        <p class="result-text"><em>"${escapeHtml(pitch.elevator_pitch || '')}"</em></p>
    </div>

    <div class="result-section">
        <div class="result-section-header">
            <span class="result-section-title">Value Proposition</span>
        </div>
        <p class="result-text">${escapeHtml(pitch.value_proposition || '')}</p>
    </div>

    <div class="result-section">
        <div class="result-section-header">
            <span class="result-section-title">Detailed Sales Pitch</span>
            <button class="copy-btn" onclick="copyText('${escapeHtml(pitch.detailed_pitch || '')}')">📋 Copy</button>
        </div>
        <p class="result-text">${escapeHtml(pitch.detailed_pitch || '')}</p>
    </div>

    <div class="result-section">
        <div class="result-section-header">
            <span class="result-section-title">Key Talking Points</span>
        </div>
        <ul class="result-list">
            ${(pitch.talking_points || []).map(tp => `
                <li>
                    <div>
                        <strong>${escapeHtml(tp.point)}:</strong> ${escapeHtml(tp.detail)}
                        ${tp.proof ? `<br><small class="text-muted">Proof: ${escapeHtml(tp.proof)}</small>` : ''}
                    </div>
                </li>
            `).join('')}
        </ul>
    </div>

    <div class="result-section">
        <div class="result-section-header">
            <span class="result-section-title">Objection Handling</span>
        </div>
        ${(pitch.objection_handling || []).map(obj => `
            <div class="mb-4">
                <span class="tag danger">Objection</span>
                <p class="result-text mt-4"><strong>"${escapeHtml(obj.objection)}"</strong></p>
                <span class="tag success mt-4">Response</span>
                <p class="result-text mt-4">${escapeHtml(obj.response)}</p>
            </div>
        `).join('')}
    </div>

    <div class="result-section">
        <div class="result-section-header">
            <span class="result-section-title">Discovery Questions</span>
        </div>
        <ul class="result-list">
            ${(pitch.discovery_questions || []).map(dq => `
                <li>
                    <div>
                        <strong>"${escapeHtml(dq.question)}"</strong>
                        <br><small class="text-muted">Purpose: ${escapeHtml(dq.purpose)}</small>
                    </div>
                </li>
            `).join('')}
        </ul>
    </div>

    <div class="result-section">
        <div class="result-section-header">
            <span class="result-section-title">Closing Statement &amp; Next Steps</span>
        </div>
        <p class="result-text"><strong>Closing:</strong> ${escapeHtml(pitch.closing_statement || '')}</p>
    </div>

    <div class="result-section">
        <div class="result-section-header">
            <span class="result-section-title">Follow-up Email Template</span>
            <button class="copy-btn" onclick="copyText('${escapeHtml(pitch.follow_up_email?.body || '')}')">📋 Copy Email</button>
        </div>
        <p class="result-text"><strong>Subject:</strong> ${escapeHtml(pitch.follow_up_email?.subject || '')}</p>
        <div class="code-block mt-4">${escapeHtml(pitch.follow_up_email?.body || '')}</div>
    </div>
  `;
}

function copyPitchResult() {
  if (!currentPitchData) return;
  copyToClipboard(JSON.stringify(currentPitchData, null, 2), 'Full pitch copied as JSON!');
}

function copyText(str) {
  copyToClipboard(str);
}

async function regeneratePitch() {
  if (!currentPitchInputs) return;
  showLoadingState();
  try {
    const res = await apiFetch('/api/sales-pitches/generate', {
      method: 'POST',
      body: JSON.stringify(currentPitchInputs)
    });
    currentPitchData = res.data.pitch;
    renderPitchResult(res.data.pitch, false);
    showToast('Regenerated pitch successfully!', 'success');
  } catch (err) {
    showToast(err.message || 'Failed to regenerate pitch', 'error');
    hideLoadingState();
  }
}
