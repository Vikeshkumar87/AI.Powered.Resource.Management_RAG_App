/**
 * AI Resource Management RAG App - Frontend JavaScript
 */

const API_BASE = '/api/v1';

// ── Navigation ──────────────────────────────────────────────────────────────

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');
    event.target.classList.add('active');

    // Load data for section
    if (sectionId === 'dashboard') loadDashboard();
    else if (sectionId === 'resources') loadResources();
    else if (sectionId === 'bench') loadBench();
    else if (sectionId === 'projects') loadProjects();
}

// ── API Helpers ──────────────────────────────────────────────────────────────

async function api(path, options = {}) {
    const res = await fetch(`${API_BASE}${path}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || `HTTP ${res.status}`);
    }
    if (res.status === 204) return null;
    return res.json();
}

// ── Dashboard ────────────────────────────────────────────────────────────────

async function loadDashboard() {
    await Promise.all([loadStats(), loadProjectGaps(), loadBenchAging()]);
}

async function loadStats() {
    try {
        const stats = await api('/dashboard/stats');
        const container = document.getElementById('stats-cards');
        container.innerHTML = `
            <div class="stat-card">
                <div class="stat-label">Total Resources</div>
                <div class="stat-value">${stats.resources.total}</div>
                <div class="stat-sub">In the organization</div>
            </div>
            <div class="stat-card bench">
                <div class="stat-label">On Bench</div>
                <div class="stat-value">${stats.resources.on_bench}</div>
                <div class="stat-sub">${stats.resources.bench_percentage}% of total</div>
            </div>
            <div class="stat-card allocation">
                <div class="stat-label">Allocated</div>
                <div class="stat-value">${stats.resources.allocated}</div>
                <div class="stat-sub">Active assignments</div>
            </div>
            <div class="stat-card project">
                <div class="stat-label">Active Projects</div>
                <div class="stat-value">${stats.projects.active}</div>
                <div class="stat-sub">${stats.projects.planning} in planning</div>
            </div>
        `;
    } catch (e) {
        document.getElementById('stats-cards').innerHTML =
            '<div class="stat-card"><div class="stat-value">—</div><div class="stat-label">No data yet. Seed the database!</div></div>';
    }
}

async function loadProjectGaps() {
    try {
        const gaps = await api('/dashboard/project-gaps');
        const el = document.getElementById('project-gaps');
        if (!gaps.length) {
            el.innerHTML = '<p class="empty-state" style="padding:1rem">All projects are fully staffed! 🎉</p>';
            return;
        }
        el.innerHTML = `
            <table class="data-table">
                <thead><tr>
                    <th>Project</th><th>Client</th><th>Gap</th><th>Priority</th>
                </tr></thead>
                <tbody>
                ${gaps.map(g => `
                    <tr>
                        <td><strong>${g.project_name}</strong><br><small>${g.project_code}</small></td>
                        <td>${g.client}</td>
                        <td><span class="gap-badge">+${g.gap} needed</span><br>
                            <small>${g.current_team_size}/${g.team_size_required}</small>
                        </td>
                        <td><span class="priority-badge ${g.priority}">${g.priority}</span></td>
                    </tr>
                `).join('')}
                </tbody>
            </table>`;
    } catch (e) {
        document.getElementById('project-gaps').innerHTML = '<p class="empty-state" style="padding:1rem">No projects found</p>';
    }
}

async function loadBenchAging() {
    try {
        const aging = await api('/dashboard/bench-aging');
        const el = document.getElementById('bench-aging');
        if (!aging.length) {
            el.innerHTML = '<p class="empty-state" style="padding:1rem">No resources on bench 🎉</p>';
            return;
        }
        el.innerHTML = `
            <table class="data-table">
                <thead><tr>
                    <th>Resource</th><th>Dept</th><th>Days on Bench</th><th>Status</th>
                </tr></thead>
                <tbody>
                ${aging.map(r => `
                    <tr>
                        <td><strong>${r.name}</strong><br><small>${r.designation}</small></td>
                        <td>${r.department}</td>
                        <td>${r.days_on_bench !== null ? r.days_on_bench + ' days' : 'Unknown'}</td>
                        <td><span class="aging-${r.aging_category}">${r.aging_category.toUpperCase()}</span></td>
                    </tr>
                `).join('')}
                </tbody>
            </table>`;
    } catch (e) {
        document.getElementById('bench-aging').innerHTML = '<p class="empty-state" style="padding:1rem">No bench data</p>';
    }
}

async function seedDatabase() {
    const btn = event.target;
    const status = document.getElementById('seed-status');
    btn.disabled = true;
    btn.textContent = 'Seeding...';
    status.textContent = '';

    try {
        const result = await api('/admin/seed?clear_existing=false', { method: 'POST' });
        status.textContent = `✅ ${result.message}`;
        status.style.color = '#065f46';
        await loadDashboard();
    } catch (e) {
        status.textContent = `❌ Error: ${e.message}`;
        status.style.color = '#991b1b';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Seed Sample Data';
    }
}

// ── Resources ────────────────────────────────────────────────────────────────

async function loadResources() {
    const searchTerm = document.getElementById('resource-search')?.value || '';
    const container = document.getElementById('resource-list');
    container.innerHTML = '<p class="empty-state loading">Loading...</p>';

    try {
        let url = '/resources/?limit=50';
        if (searchTerm) url += `&skill=${encodeURIComponent(searchTerm)}`;

        const data = await api(url);
        renderResourceCards(data.resources, container);
    } catch (e) {
        container.innerHTML = `<p class="empty-state">Error: ${e.message}</p>`;
    }
}

async function loadBench() {
    const dept = document.getElementById('bench-dept-filter')?.value || '';
    const container = document.getElementById('bench-list');
    container.innerHTML = '<p class="empty-state loading">Loading...</p>';

    try {
        let url = '/resources/bench?limit=50';
        if (dept) url += `&department=${encodeURIComponent(dept)}`;

        const data = await api(url);
        if (!data.resources.length) {
            container.innerHTML = '<p class="empty-state">No resources on bench! Everyone is allocated. 🎉</p>';
            return;
        }
        renderResourceCards(data.resources, container);
    } catch (e) {
        container.innerHTML = `<p class="empty-state">Error: ${e.message}</p>`;
    }
}

function renderResourceCards(resources, container) {
    if (!resources.length) {
        container.innerHTML = '<p class="empty-state">No resources found</p>';
        return;
    }
    container.innerHTML = resources.map(r => `
        <div class="resource-card ${r.is_on_bench ? 'bench' : 'allocated'}" onclick="showResourceDetail(${r.id})">
            <span class="bench-badge ${r.is_on_bench ? 'on-bench' : 'allocated'}">
                ${r.is_on_bench ? '🪑 On Bench' : '✅ Allocated'}
            </span>
            <div class="resource-name">${r.name}</div>
            <div class="resource-designation">${r.designation}</div>
            <div class="resource-meta">
                <span class="meta-badge dept">${r.department}</span>
                ${r.location ? `<span class="meta-badge location">📍 ${r.location}</span>` : ''}
                <span class="meta-badge exp">⭐ ${r.experience_years}y</span>
            </div>
            <div class="skill-tags">
                ${(r.skills || []).slice(0, 5).map(s => `<span class="skill-tag">${s}</span>`).join('')}
                ${r.skills?.length > 5 ? `<span class="skill-tag">+${r.skills.length - 5}</span>` : ''}
            </div>
        </div>
    `).join('');
}

async function showResourceDetail(resourceId) {
    try {
        const r = await api(`/resources/${resourceId}`);
        const modal = document.getElementById('modal');
        const body = document.getElementById('modal-body');
        body.innerHTML = `
            <h2 style="margin-bottom:0.5rem">${r.name}</h2>
            <p style="color:#6b7280;margin-bottom:1.5rem">${r.designation} · ${r.employee_id}</p>

            <div class="modal-detail-row"><span class="modal-label">Department</span><span>${r.department}</span></div>
            <div class="modal-detail-row"><span class="modal-label">Email</span><span>${r.email}</span></div>
            <div class="modal-detail-row"><span class="modal-label">Location</span><span>${r.location || 'N/A'}</span></div>
            <div class="modal-detail-row"><span class="modal-label">Experience</span><span>${r.experience_years} years</span></div>
            <div class="modal-detail-row"><span class="modal-label">Availability</span><span>${r.availability_percentage}%</span></div>
            <div class="modal-detail-row"><span class="modal-label">Status</span>
                <span class="bench-badge ${r.is_on_bench ? 'on-bench' : 'allocated'}">
                    ${r.is_on_bench ? '🪑 On Bench' : '✅ Allocated'}
                </span>
            </div>
            ${r.hourly_rate ? `<div class="modal-detail-row"><span class="modal-label">Hourly Rate</span><span>$${r.hourly_rate}/hr</span></div>` : ''}

            <div style="margin-top:1rem">
                <strong>Skills</strong>
                <div class="skill-tags" style="margin-top:0.5rem">
                    ${(r.skills || []).map(s => `<span class="skill-tag">${s}</span>`).join('')}
                </div>
            </div>

            ${r.certifications?.length ? `
            <div style="margin-top:1rem">
                <strong>Certifications</strong>
                <div class="skill-tags" style="margin-top:0.5rem">
                    ${r.certifications.map(c => `<span class="skill-tag" style="background:#dbeafe;border-color:#93c5fd">📜 ${c}</span>`).join('')}
                </div>
            </div>` : ''}

            ${r.bio ? `<div style="margin-top:1rem"><strong>Bio</strong><p style="margin-top:0.5rem;color:#4b5563;font-size:0.9rem">${r.bio}</p></div>` : ''}

            ${r.bench_start_date ? `
            <div style="margin-top:1rem;padding:0.75rem;background:#fef3c7;border-radius:8px">
                <strong>Bench Since:</strong> ${new Date(r.bench_start_date).toLocaleDateString()}<br>
                ${r.expected_allocation_date ? `<strong>Expected Allocation:</strong> ${new Date(r.expected_allocation_date).toLocaleDateString()}` : ''}
            </div>` : ''}
        `;
        modal.classList.remove('hidden');
    } catch (e) {
        alert(`Error loading resource: ${e.message}`);
    }
}

// ── Projects ─────────────────────────────────────────────────────────────────

async function loadProjects() {
    const status = document.getElementById('project-status-filter')?.value || '';
    const container = document.getElementById('project-list');
    container.innerHTML = '<p class="empty-state loading">Loading...</p>';

    try {
        let url = '/projects/?limit=50';
        if (status) url += `&status=${status}`;

        const data = await api(url);
        renderProjectCards(data.projects, container);
    } catch (e) {
        container.innerHTML = `<p class="empty-state">Error: ${e.message}</p>`;
    }
}

function renderProjectCards(projects, container) {
    if (!projects.length) {
        container.innerHTML = '<p class="empty-state">No projects found</p>';
        return;
    }
    container.innerHTML = projects.map(p => {
        const progress = p.team_size_required > 0
            ? (p.current_team_size / p.team_size_required * 100)
            : 0;
        const progressClass = progress === 100 ? '' : progress >= 50 ? 'warn' : 'danger';
        const skills = (p.required_skills || []).slice(0, 4);

        return `
        <div class="project-card ${p.status} ${p.priority === 'critical' ? 'critical' : ''}"
             onclick="showProjectDetail(${p.id})">
            <div class="project-name">${p.name}</div>
            <div class="project-client">👥 ${p.client}</div>
            <div class="project-meta">
                <span class="status-badge ${p.status}">${p.status.replace('_', ' ')}</span>
                <span class="priority-badge ${p.priority}">${p.priority}</span>
                ${p.domain ? `<span class="meta-badge dept">${p.domain}</span>` : ''}
            </div>
            <div class="team-progress">
                <div class="progress-label">
                    <span>Team: ${p.current_team_size}/${p.team_size_required}</span>
                    <span>${Math.round(progress)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${progressClass}" style="width:${Math.min(progress, 100)}%"></div>
                </div>
            </div>
            <div class="skill-tags">
                ${skills.map(s => `<span class="skill-tag">${s}</span>`).join('')}
                ${p.required_skills?.length > 4 ? `<span class="skill-tag">+${p.required_skills.length - 4}</span>` : ''}
            </div>
        </div>`;
    }).join('');
}

async function showProjectDetail(projectId) {
    try {
        const [p, team] = await Promise.all([
            api(`/projects/${projectId}`),
            api(`/projects/${projectId}/team`),
        ]);
        const modal = document.getElementById('modal');
        const body = document.getElementById('modal-body');
        body.innerHTML = `
            <h2 style="margin-bottom:0.5rem">${p.name}</h2>
            <p style="color:#6b7280;margin-bottom:1.5rem">${p.project_code} · ${p.client}</p>

            <div class="modal-detail-row"><span class="modal-label">Status</span>
                <span class="status-badge ${p.status}">${p.status}</span>
            </div>
            <div class="modal-detail-row"><span class="modal-label">Priority</span>
                <span class="priority-badge ${p.priority}">${p.priority}</span>
            </div>
            <div class="modal-detail-row"><span class="modal-label">Domain</span><span>${p.domain || 'N/A'}</span></div>
            <div class="modal-detail-row"><span class="modal-label">Location</span><span>${p.location || 'Remote'}</span></div>
            <div class="modal-detail-row"><span class="modal-label">Team Size</span><span>${p.current_team_size}/${p.team_size_required}</span></div>
            ${p.budget ? `<div class="modal-detail-row"><span class="modal-label">Budget</span><span>$${p.budget.toLocaleString()}</span></div>` : ''}
            ${p.start_date ? `<div class="modal-detail-row"><span class="modal-label">Start Date</span><span>${new Date(p.start_date).toLocaleDateString()}</span></div>` : ''}
            ${p.end_date ? `<div class="modal-detail-row"><span class="modal-label">End Date</span><span>${new Date(p.end_date).toLocaleDateString()}</span></div>` : ''}
            ${p.manager_name ? `<div class="modal-detail-row"><span class="modal-label">Manager</span><span>${p.manager_name}</span></div>` : ''}

            <div style="margin-top:1rem">
                <strong>Required Skills</strong>
                <div class="skill-tags" style="margin-top:0.5rem">
                    ${(p.required_skills || []).map(s => `<span class="skill-tag">${s}</span>`).join('')}
                </div>
            </div>

            ${p.description ? `<div style="margin-top:1rem"><strong>Description</strong><p style="margin-top:0.5rem;color:#4b5563;font-size:0.9rem">${p.description}</p></div>` : ''}

            <div style="margin-top:1.25rem">
                <strong>Current Team (${team.length})</strong>
                ${team.length ? `
                <table class="data-table" style="margin-top:0.5rem">
                    <thead><tr><th>Resource</th><th>Role</th><th>Allocation</th></tr></thead>
                    <tbody>
                    ${team.map(m => `
                        <tr>
                            <td>${m.resource_name}</td>
                            <td>${m.role}</td>
                            <td>${m.allocation_percentage}%</td>
                        </tr>`).join('')}
                    </tbody>
                </table>` : '<p style="color:#6b7280;font-size:0.875rem;margin-top:0.5rem">No team members assigned yet</p>'}
            </div>
        `;
        modal.classList.remove('hidden');
    } catch (e) {
        alert(`Error loading project: ${e.message}`);
    }
}

// ── RAG Query ─────────────────────────────────────────────────────────────────

function setQuery(chip) {
    document.getElementById('query-input').value = chip.textContent;
}

async function runRAGQuery() {
    const question = document.getElementById('query-input').value.trim();
    if (!question) { alert('Please enter a question'); return; }

    const benchOnly = document.getElementById('bench-only').checked;
    const filterType = document.getElementById('filter-type').value;

    const resultEl = document.getElementById('query-result');
    const sourcesEl = document.getElementById('query-sources');

    resultEl.classList.remove('hidden');
    resultEl.textContent = '🔍 Searching and generating response...';
    sourcesEl.classList.add('hidden');

    try {
        const result = await api('/rag/query', {
            method: 'POST',
            body: JSON.stringify({
                question,
                n_context_docs: 5,
                filter_type: filterType || null,
                filter_bench: benchOnly || null,
            }),
        });

        resultEl.innerHTML = `<strong>Answer:</strong>\n\n${escapeHtml(result.answer)}
<br><br><small style="color:#6b7280">LLM Provider: ${result.llm_provider} · Context docs used: ${result.context_used}</small>`;

        if (result.sources?.length) {
            sourcesEl.classList.remove('hidden');
            sourcesEl.innerHTML = `<h4>📚 Context Sources (${result.sources.length})</h4>` +
                result.sources.map((s, i) => `
                    <div class="source-item">
                        <strong>#${i+1}</strong> [Score: ${(s.score * 100).toFixed(0)}%]
                        ${s.metadata?.type === 'resource' ? '🧑' : '📋'}
                        <em>${s.metadata?.name || 'Unknown'}</em><br>
                        <span style="color:#9ca3af;font-size:0.75rem">${s.content?.substring(0, 150)}...</span>
                    </div>`).join('');
        }
    } catch (e) {
        resultEl.textContent = `❌ Error: ${e.message}`;
    }
}

// ── Recommendations ──────────────────────────────────────────────────────────

async function getRecommendations() {
    const requirements = document.getElementById('project-req').value.trim();
    const skillsStr = document.getElementById('required-skills').value.trim();
    const teamSize = parseInt(document.getElementById('team-size').value) || 1;

    if (!requirements) { alert('Please describe the project requirements'); return; }

    const skills = skillsStr ? skillsStr.split(',').map(s => s.trim()).filter(Boolean) : [];

    const resultEl = document.getElementById('recommendations-result');
    const candidatesEl = document.getElementById('recommendations-candidates');

    resultEl.classList.remove('hidden');
    resultEl.textContent = '🎯 Analyzing requirements and finding best matches...';
    candidatesEl.classList.add('hidden');

    try {
        const result = await api('/rag/recommend', {
            method: 'POST',
            body: JSON.stringify({
                project_requirements: requirements,
                required_skills: skills,
                team_size: teamSize,
                n_candidates: 10,
            }),
        });

        resultEl.innerHTML = `<strong>AI Recommendation:</strong>\n\n${escapeHtml(result.recommendation)}
<br><br><small style="color:#6b7280">Team size requested: ${result.team_size_requested} · Provider: ${result.llm_provider}</small>`;

        const allCandidates = result.bench_candidates || result.all_candidates || [];
        if (allCandidates.length) {
            candidatesEl.classList.remove('hidden');
            candidatesEl.innerHTML = `<h4>👥 Top Candidates from Vector Search (${allCandidates.length})</h4>` +
                allCandidates.map((c, i) => `
                    <div class="source-item">
                        <strong>#${i+1}</strong> 🧑 <em>${c.metadata?.name || 'Resource'}</em>
                        [Match: ${(c.score * 100).toFixed(0)}%]
                        ${c.metadata?.is_on_bench === 'True' ? '<span class="bench-badge on-bench" style="font-size:0.65rem;padding:1px 6px">On Bench</span>' : ''}<br>
                        <span style="color:#9ca3af;font-size:0.75rem">${c.content?.substring(0, 200)}...</span>
                    </div>`).join('');
        }
    } catch (e) {
        resultEl.textContent = `❌ Error: ${e.message}`;
    }
}

// ── Modal ─────────────────────────────────────────────────────────────────────

function closeModal() {
    document.getElementById('modal').classList.add('hidden');
}

document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
});

// ── Utils ─────────────────────────────────────────────────────────────────────

function escapeHtml(text) {
    return (text || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\n/g, '<br>');
}

// ── Init ──────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});
