// Candidate scoring helpers shared by dashboard.html and shortlisted.html.
// Plain static file (not Jinja-templated) — talks to the jd_prototype
// scoring backend on localhost:6001.

function toggleBreakdown(id) {
  const el = document.getElementById('breakdown-' + id);
  if (el) el.style.display = el.style.display === 'none' ? '' : 'none';
}

// Auto-score unscored candidates on page load
async function autoScorePending() {
  try {
    const res = await fetch('http://localhost:6001/api/candidates/score-pending', {credentials:'include'}).then(r=>r.json());
    if (res.queued > 0) {
      const banner = document.getElementById('scoringBanner');
      if (banner) {
        banner.textContent = `⏳ Scoring ${res.queued} candidate(s) in background…`;
        banner.style.display = '';
      }
      // Auto-refresh once scoring is likely done (3s per candidate, min 8s)
      const wait = Math.max(8000, res.queued * 4000);
      setTimeout(() => location.reload(), wait);
    }
  } catch(e) { /* Flask may not be reachable, ignore */ }
}

async function rescoreCandidate(candidateId, jobId, btn) {
  btn.disabled = true;
  btn.textContent = '↻ Scoring…';
  try {
    const res = await fetch('http://localhost:6001/api/candidates/rescore', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      credentials: 'include',
      body: JSON.stringify({candidate_id: candidateId, darwinbox_job_id: jobId}),
    }).then(r => r.json());
    if (res.success) {
      btn.textContent = '✓ Done';
      setTimeout(() => location.reload(), 800);
    } else {
      btn.textContent = '✗ Failed';
      btn.disabled = false;
    }
  } catch {
    btn.textContent = '✗ Error';
    btn.disabled = false;
  }
}
