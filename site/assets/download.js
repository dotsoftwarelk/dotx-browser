/* Public GitHub Actions metadata only. No credentials; artifacts require GitHub sign-in. */
const DOTX_API = 'https://api.github.com/repos/dotsoftwarelk/dotx-browser';
const DOTX_RUNS = DOTX_API + '/actions/workflows/windows-development.yml/runs?status=success&per_page=10';
async function getMetadata(fetcher, url) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 8000);
  try { return await fetcher(url, {headers: {'Accept':'application/vnd.github+json'}, signal:controller.signal}); }
  finally { clearTimeout(timer); }
}
async function latestDevelopmentArtifact(fetcher = fetch, now = Date.now()) {
  const response = await getMetadata(fetcher, DOTX_RUNS);
  if (!response.ok) throw new Error('GitHub metadata unavailable');
  const payload = await response.json();
  if (!payload || !Array.isArray(payload.workflow_runs)) throw new Error('Unexpected metadata');
  for (const run of payload.workflow_runs.slice(0, 10)) {
    if (!Number.isSafeInteger(run.id) || run.id <= 0 || run.conclusion !== 'success' || run.head_branch !== 'main') continue;
    const response = await getMetadata(fetcher, `${DOTX_API}/actions/runs/${run.id}/artifacts`);
    if (!response.ok) throw new Error('Artifact metadata unavailable');
    const data = await response.json();
    if (!data || !Array.isArray(data.artifacts)) continue;
    const artifact = data.artifacts.find(a => a && a.name === 'DOTX-Windows-development-unsigned' && a.expired === false && Number.isFinite(Date.parse(a.expires_at)) && Date.parse(a.expires_at) > now);
    if (artifact) return { runId: run.id, sha: typeof run.head_sha === 'string' && /^[0-9a-f]{40}$/i.test(run.head_sha) ? run.head_sha.slice(0, 7) : null, expiresAt: artifact.expires_at };
  }
  return null;
}
if (typeof module !== 'undefined') module.exports = { latestDevelopmentArtifact };
if (typeof document !== 'undefined') {
  const status = document.getElementById('build-status');
  const link = document.getElementById('build-link');
  if (status && link) {
    status.textContent = 'Checking GitHub for a successful build and unexpired artifact…';
    latestDevelopmentArtifact().then(result => {
      if (!result) { status.textContent = 'No unexpired verified development artifact was found in the latest runs.'; return; }
      const expiry = new Date(result.expiresAt).toUTCString();
      status.textContent = `Verified Windows CI run${result.sha ? ` · source ${result.sha}` : ''}. Temporary artifact expires ${expiry}.`;
      link.href = `https://github.com/dotsoftwarelk/dotx-browser/actions/runs/${result.runId}`;
      link.hidden = false;
    }).catch(() => { status.textContent = 'Could not verify current build metadata. Check the Windows workflows on GitHub.'; });
  }
}
