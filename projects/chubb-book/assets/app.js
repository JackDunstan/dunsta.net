const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const esc = (s = '') => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const STORAGE = 'chubb-review-v1';
let data, book = 1, offset = 0, personFilter = '', active, activeTask = '', zoom = 1, lastFocus;
let reviewLimit = 12, drafts = [];
try { const saved = JSON.parse(localStorage.getItem(STORAGE) || '[]'); if (Array.isArray(saved)) drafts = saved; } catch { /* Read-only browsing works without storage. */ }
const size = 24;
const pageById = id => data.pages.find(p => p.id === id);
const personById = id => data.people.find(p => p.id === id);
const topicById = id => data.topics.find(p => p.id === id);
const related = person => data.pages.filter(p => p.people.includes(person.id));

function card(p) {
  const title = p.title === p.label ? `Scan ${String(p.sequence).padStart(3, '0')}` : p.title;
  return `<a class="page-card" href="#page/${p.id}"><div class="scan-frame"><img src="${p.image.replace('/medium/', '/small/')}" loading="lazy" alt="${esc(p.label)}"></div><div class="card-meta"><span>Book 0${p.book} / ${String(p.sequence).padStart(3, '0')}</span><span>${p.status === 'reviewed' ? 'Reviewed' : 'Draft'}</span></div><h3>${esc(title)}</h3><p>${esc(p.description.slice(0, 100) || (p.resolution === 'thumbnail-only' ? 'Thumbnail only · larger scan unavailable' : 'Photographs, clippings & handwritten memories'))}</p></a>`;
}
function browse() {
  const query = $('#search').value.trim().toLocaleLowerCase();
  const topic = $('#topic-filter').value, status = $('#status-filter').value;
  const matches = data.pages.filter(p => p.book === book && (!topic || [...p.topics, ...p.suggested_topics].includes(topic)) && (!status || p.status === status)
    && (!personFilter || p.people.includes(personFilter))
    && (!query || [p.title, p.description, p.transcription, p.context, ...p.candidate_names, ...p.people.map(id => personById(id)?.name || id), ...p.artifacts.flatMap(a => [a.number, a.title, a.type, ...(a.types || []), a.caption, a.caption_source, a.transcription, a.context])].join(' ').toLocaleLowerCase().includes(query)));
  if (offset >= matches.length) offset = 0;
  $('#page-grid').innerHTML = matches.slice(offset, offset + size).map(card).join('') || '<p class="empty">No pages match these filters. Try a different name or clear the filters.</p>';
  $('#result-count').textContent = `${matches.length} ${matches.length === 1 ? 'page' : 'pages'}${personFilter ? ' mentioning ' + (personById(personFilter)?.name || personFilter) : ''}${topic ? ' · includes suggested topic matches' : ''}`;
  $('#pagination-label').textContent = matches.length ? `${offset + 1}–${Math.min(offset + size, matches.length)} of ${matches.length}` : '0 pages';
  $('#previous-results').disabled = offset === 0;
  $('#next-results').disabled = offset + size >= matches.length;
  $('#resolution-note').hidden = book !== 2;
  $$('[data-book]').forEach(b => b.setAttribute('aria-pressed', String(Number(b.dataset.book) === book)));
}
function reset() { offset = 0; personFilter = ''; $('#search').value = ''; $('#topic-filter').value = ''; $('#status-filter').value = ''; }
function personHTML(p) {
  return `<article class="person"><h3>${esc(p.name)}</h3><p>${esc(p.context)}</p>${p.sources.map(s => `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)} ↗</a>`).join(' ')}<a href="notes/People/${esc(p.id)}.html">Biographical note ↗</a>${related(p).length ? `<button data-person="${esc(p.id)}">${related(p).length} curated page associations →</button>` : ''}</article>`;
}
function candidates() {
  const q = $('#name-search').value.toLocaleLowerCase();
  const matches = data.candidates.filter(n => n.name.toLocaleLowerCase().includes(q));
  $('#candidate-list').innerHTML = matches.slice(0, 100).map(n => `<button data-candidate="${esc(n.id)}">${esc(n.name)} <small>(${n.pages.length})</small></button>`).join('') || '<p>No name candidates match.</p>';
  $('#candidate-count').textContent = `(${data.candidates.length})`;
  if (matches.length > 100) $('#candidate-list').insertAdjacentHTML('beforeend', '<p>Showing 100 names. Search to narrow the list, or use the full name index.</p>');
}
function reviews() {
  const kind = $('#review-filter').value;
  const list = data.reviews.filter(r => r.kind === kind);
  $('#review-list').innerHTML = list.slice(0, reviewLimit).map(r => {
    const p = pageById(r.page), saved = drafts.some(d => d.task === r.id);
    return `<button class="review-card" data-review="${esc(r.id)}"><img src="${p.thumbnail}" loading="lazy" alt="${esc(r.label)}"><span>${esc(r.label)} ${saved ? '· suggestion saved' : '↗'}</span></button>`;
  }).join('') || '<p>No detected face regions are awaiting review. Other unidentified people may remain in the scans; use Contribute on any page to flag them.</p>';
  $('#more-review').hidden = list.length <= reviewLimit;
  $('#saved-count').textContent = `${drafts.length} saved suggestion${drafts.length === 1 ? '' : 's'}`;
}
function changePanel(panel) {
  $$('[data-panel]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.panel === panel)));
  ['read', 'context', 'suggest'].forEach(id => $(`#panel-${id}`).hidden = id !== panel);
}
function setZoom(value) {
  zoom = Math.max(1, Math.min(5, value));
  $('#scan-canvas').style.width = `${zoom * 100}%`;
  $('#zoom-label').textContent = `${Math.round(zoom * 100)}%`;
  $('#zoom-out').disabled = zoom === 1; $('#zoom-in').disabled = zoom === 5;
}
function selectTask() {
  activeTask = $('#suggestion-task').value;
  const saved = drafts.find(d => d.task === activeTask);
  $('#suggestion-text').value = saved?.text || ''; $('#suggestion-evidence').value = saved?.evidence || '';
  $('#suggestion-status').textContent = saved ? 'A suggestion is saved on this device.' : '';
  const r = data.reviews.find(r => r.id === activeTask);
  $('#face-region').hidden = !r?.box;
  if (r?.box) {
    const [x, y, w, h] = r.box;
    Object.assign($('#face-region').style, { left: `${x * 100}%`, top: `${y * 100}%`, width: `${w * 100}%`, height: `${h * 100}%` });
  }
}
function openPage(id, task) {
  const p = pageById(id); if (!p) { location.hash = 'browse'; return; }
  if (!$('#viewer').open) { lastFocus = document.activeElement; $('#viewer').showModal(); }
  active = p;
  $('#viewer-label').textContent = p.label;
  $('#viewer-title').textContent = p.title === p.label ? 'A page from the scrapbook' : p.title;
  $('#scan-image').src = p.image; $('#scan-image').alt = `${p.label}${p.description ? ': ' + p.description : ''}`;
  $('#original-link').href = p.original;
  $('#transcript-status').textContent = p.resolution === 'thumbnail-only' ? 'Thumbnail only · transcription deferred' : p.transcription_status === 'reviewed' ? 'Editorial transcription · checked against scan' : 'Machine draft · handwriting, names & reading order need checking';
  $('#page-description').textContent = p.description;
  $('#transcript').textContent = p.transcription || 'No readable text has been transcribed yet. You can add a reading in Contribute.';
  $('#markdown-link').href = p.markdown;
  $('#text-link').href = `notes/Pages/${p.id}.html`;
  const people = p.people.map(personById).filter(Boolean);
  $('#page-context').innerHTML = `<p>${esc(p.context || 'This page is awaiting contextual research.')}</p>${people.map(personHTML).join('')}`
    + (p.mentions?.length ? `<h3>Name evidence to investigate</h3>${p.mentions.map(m => `<p><a href="${esc(m.note)}">${esc(m.name)} ↗</a><br><small>Machine reading: ${esc(m.evidence)}</small></p>`).join('')}` : '')
    + `<p><strong>Topics:</strong> ${[...p.topics.map(id => `${topicById(id)?.name || id} (curated)`), ...p.suggested_topics.filter(id => !p.topics.includes(id)).map(id => `${topicById(id)?.name || id} (suggested)`)].map(esc).join(', ') || 'Not yet assigned'}</p>`;
  $('#page-artifacts').innerHTML = p.artifacts.length ? p.artifacts.map(a => `<article class="artifact"><p class="eyebrow">Artifact ${esc(a.number)}</p><h3>${esc(a.title)}</h3><p>${(a.types || [a.type]).map(t => esc(t.replaceAll('-', ' '))).join(' · ')}</p><p class="muted">${a.scope === 'page' ? 'Whole-page record · individual items can be split during review.' : 'Individual item / region'} · ${esc(a.classification_status || 'needs-review')}</p><dl><dt>Associated caption</dt><dd>${esc(a.caption || 'Not mapped yet')}</dd><dt>Caption source</dt><dd>${esc(a.caption_source || 'Not recorded yet')}</dd><dt>Caption status</dt><dd>${esc(a.caption_status || 'unmapped')}</dd></dl><p>${esc(a.transcription || '')}</p><p>${esc(a.context || '')}</p></article>`).join('') : '<p>Individual photographs and cuttings have not yet been catalogued. Use the scan to review the whole page.</p>';
  const tasks = data.reviews.filter(r => r.page === p.id);
  const general = `${p.id}-general`;
  $('#suggestion-task').innerHTML = `<option value="${general}">Page notes / another unidentified person</option>` + tasks.map(r => `<option value="${r.id}">${esc(r.label)} · ${esc(r.kind)}</option>`).join('');
  $('#suggestion-task').value = tasks.some(r => r.id === task) ? task : general;
  selectTask(); changePanel(task ? 'suggest' : 'read'); setZoom(1); $('#scan-scroll').scrollTo(0, 0);
  $('#previous-page').disabled = p.sequence === 0;
  $('#next-page').disabled = !data.pages.some(n => n.book === p.book && n.sequence === p.sequence + 1);
  $('#jump-page').value = p.sequence; $('#jump-page').max = data.pages.filter(n => n.book === p.book).length - 1;
}
function route() {
  const [route, id, task] = location.hash.slice(1).split('/');
  if (route === 'page' && id) openPage(id, task);
  else if ($('#viewer').open) { $('#viewer').close(); lastFocus?.focus(); }
}
function download(value, name) {
  const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], {type: 'application/json'}));
  const a = document.createElement('a'); a.href = url; a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
async function init() {
  const response = await fetch('data/catalogue.json'); if (!response.ok) throw Error(`Catalogue returned ${response.status}`);
  data = await response.json();
  $('#topic-filter').innerHTML += data.topics.map(t => `<option value="${t.id}">${esc(t.name)}</option>`).join('');
  $('#people-list').innerHTML = data.people.map(personHTML).join('');
  $('#topic-list').innerHTML = data.topics.map((t, i) => `<button class="topic" data-topic="${t.id}"><span><small>${String(i + 1).padStart(2, '0')} / </small> ${esc(t.name)}</span><small>${data.pages.filter(p => [...p.topics, ...p.suggested_topics].includes(t.id)).length} pages ↗</small></button>`).join('');
  browse(); candidates(); reviews(); route();
  $('#search').addEventListener('input', () => { offset = 0; browse(); });
  ['#topic-filter', '#status-filter'].forEach(s => $(s).addEventListener('change', () => { offset = 0; browse(); }));
  $('#clear-filters').onclick = () => { reset(); browse(); };
  $$('[data-book]').forEach(b => b.onclick = () => { book = Number(b.dataset.book); reset(); browse(); });
  $('#previous-results').onclick = () => { offset -= size; browse(); $('#browse').scrollIntoView(); };
  $('#next-results').onclick = () => { offset += size; browse(); $('#browse').scrollIntoView(); };
  $('#name-search').oninput = candidates;
  $('#review-filter').onchange = () => { reviewLimit = 12; reviews(); };
  $('#more-review').onclick = () => { reviewLimit += 24; reviews(); };
  document.addEventListener('click', event => {
    const person = event.target.closest('[data-person]');
    if (person) { const id = person.dataset.person; reset(); personFilter = id; const first = data.pages.find(p => p.people.includes(id)); book = first?.book || 1; browse(); location.hash = 'browse'; return; }
    const topic = event.target.closest('[data-topic]');
    if (topic) { reset(); $('#topic-filter').value = topic.dataset.topic; book = 1; browse(); location.hash = 'browse'; return; }
    const candidate = event.target.closest('[data-candidate]');
    if (candidate) { const c = data.candidates.find(n => n.id === candidate.dataset.candidate); reset(); book = pageById(c.pages[0]).book; $('#search').value = c.name; browse(); location.hash = 'browse'; return; }
    const review = event.target.closest('[data-review]');
    if (review) { const r = data.reviews.find(r => r.id === review.dataset.review); location.hash = `page/${r.page}/${r.id}`; }
  });
  $$('[data-panel]').forEach(b => b.onclick = () => changePanel(b.dataset.panel));
  $('#close-viewer').onclick = () => { location.hash = 'browse'; };
  $('#viewer').addEventListener('cancel', e => { e.preventDefault(); location.hash = 'browse'; });
  $('#previous-page').onclick = () => turn(-1); $('#next-page').onclick = () => turn(1);
  $('#jump-page').onchange = () => { const p = data.pages.find(p => p.book === active.book && p.sequence === Number($('#jump-page').value)); if (p) location.hash = `page/${p.id}`; else $('#jump-page').value = active.sequence; };
  $('#zoom-in').onclick = () => setZoom(zoom + .5); $('#zoom-out').onclick = () => setZoom(zoom - .5); $('#zoom-reset').onclick = () => setZoom(1);
  $('#suggestion-task').onchange = selectTask;
  $('#suggestion-form').onsubmit = event => {
    event.preventDefault(); const text = $('#suggestion-text').value.trim(); if (!text) return;
    const entry = {page: active.id, task: activeTask, text, evidence: $('#suggestion-evidence').value.trim(), updated: new Date().toISOString()};
    const next = [...drafts.filter(d => d.task !== activeTask), entry];
    try { localStorage.setItem(STORAGE, JSON.stringify(next)); drafts = next; $('#suggestion-status').textContent = 'Saved on this device. Export your suggestions to keep a portable copy.'; reviews(); }
    catch { $('#suggestion-status').textContent = 'This browser cannot save locally. Download this suggestion now.'; download({version: 1, suggestions: [entry]}, 'chubb-suggestion.json'); }
  };
  $('#export-review').onclick = () => download({version: 1, collection: 'chubb-scrapbooks', suggestions: drafts}, 'chubb-review-suggestions.json');
  $('#import-review').onchange = async event => {
    try {
      const file = event.target.files[0]; if (!file) return; if (file.size > 5000000) throw Error('File is too large.');
      const imported = JSON.parse(await file.text());
      if (imported.version !== 1 || !Array.isArray(imported.suggestions)) throw Error('Expected a version 1 suggestion export.');
      const next = [...drafts];
      for (const item of imported.suggestions) {
        if (!pageById(item.page) || typeof item.task !== 'string' || !item.task.startsWith(item.page + '-') || typeof item.text !== 'string' || item.text.length > 20000 || (item.evidence && typeof item.evidence !== 'string')) throw Error('Invalid suggestion entry.');
        if (!next.some(d => d.task === item.task)) next.push({page: item.page, task: item.task, text: item.text, evidence: (item.evidence || '').slice(0, 10000), updated: typeof item.updated === 'string' ? item.updated : ''});
      }
      localStorage.setItem(STORAGE, JSON.stringify(next)); drafts = next; reviews();
      $('#saved-count').textContent += ' · imported; existing suggestions kept';
    } catch (error) { $('#saved-count').textContent = `Import failed: ${error.message}`; }
    event.target.value = '';
  };
  window.addEventListener('hashchange', route);
  document.addEventListener('keydown', event => {
    if (!$('#viewer').open || /INPUT|TEXTAREA|SELECT/.test(event.target.tagName)) return;
    if (event.key === 'ArrowLeft') { event.preventDefault(); turn(-1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); turn(1); }
  });
}
function turn(direction) { const p = data.pages.find(p => p.book === active.book && p.sequence === active.sequence + direction); if (p) location.hash = `page/${p.id}`; }
init().catch(error => {
  $('#result-count').textContent = 'The interactive catalogue could not load.';
  $('#page-grid').innerHTML = '<p class="empty">You can still use the <a href="notes/Home.html">complete text edition</a>. For local browsing, serve this folder with <code>python3 -m http.server 8000</code>.</p>';
  console.error(error);
});
