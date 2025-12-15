const tabs = document.querySelectorAll('.tab');
const sections = document.querySelectorAll('.tab-content');
const seedBanner = document.getElementById('seed-banner');
const weedDialog = document.getElementById('weed-dialog');
const weedForm = document.getElementById('weed-form');
const weedFormTitle = document.getElementById('weed-form-title');
const addWeedBtn = document.getElementById('add-weed');
const editWeedBtn = document.getElementById('edit-weed');
const deleteWeedBtn = document.getElementById('delete-weed');
let selectedWeedId = null;
let strainChart = null;

function switchTab(target) {
  tabs.forEach(tab => tab.classList.toggle('active', tab.dataset.target === target));
  sections.forEach(section => section.classList.toggle('active', section.id === target));
}

tabs.forEach(tab => {
  tab.addEventListener('click', () => switchTab(tab.dataset.target));
});

addWeedBtn.addEventListener('click', () => {
  selectedWeedId = null;
  weedForm.reset();
  weedForm.elements.date.valueAsDate = new Date();
  weedFormTitle.textContent = 'Add strain';
  weedDialog.showModal();
});

editWeedBtn.addEventListener('click', () => {
  if (!selectedWeedId) return alert('Select a row to edit (double-click it).');
  weedFormTitle.textContent = 'Edit strain';
  weedDialog.showModal();
});

deleteWeedBtn.addEventListener('click', async () => {
  if (!selectedWeedId) return alert('Select a row to delete (double-click it).');
  if (confirm('Delete this entry?')) {
    await fetch(`/api/weed/${selectedWeedId}`, { method: 'DELETE' });
    selectedWeedId = null;
    loadWeed();
  }
});

document.getElementById('cancel-weed').addEventListener('click', () => weedDialog.close());

weedForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = Object.fromEntries(new FormData(weedForm).entries());
  const payload = {
    ...formData,
    thc_percent: formData.thc_percent ? parseFloat(formData.thc_percent) : null,
    rating: formData.rating ? parseInt(formData.rating, 10) : null,
  };
  const method = selectedWeedId ? 'PUT' : 'POST';
  const url = selectedWeedId ? `/api/weed/${selectedWeedId}` : '/api/weed';
  await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  weedDialog.close();
  loadWeed();
});

async function loadWeed() {
  const res = await fetch('/api/weed');
  const data = await res.json();
  const tbody = document.querySelector('#weed-table tbody');
  tbody.innerHTML = '';
  data.forEach(row => {
    const tr = document.createElement('tr');
    tr.dataset.id = row.id;
    tr.innerHTML = `
      <td>${row.date}</td>
      <td>${row.strain_name}</td>
      <td>${row.thc_percent ?? ''}</td>
      <td>${row.strain_type ?? ''}</td>
      <td>${row.terpenes ?? ''}</td>
      <td>${row.notes ?? ''}</td>
      <td>${row.rating ?? ''}</td>
    `;
    tr.addEventListener('dblclick', () => {
      selectedWeedId = row.id;
      weedForm.elements.date.value = row.date;
      weedForm.elements.strain_name.value = row.strain_name;
      weedForm.elements.thc_percent.value = row.thc_percent ?? '';
      weedForm.elements.strain_type.value = row.strain_type ?? '';
      weedForm.elements.terpenes.value = row.terpenes ?? '';
      weedForm.elements.notes.value = row.notes ?? '';
      weedForm.elements.rating.value = row.rating ?? '';
      weedFormTitle.textContent = 'Edit strain';
    });
    tbody.appendChild(tr);
  });
  loadWeedStats();
}

async function loadWeedStats() {
  const res = await fetch('/api/weed/stats');
  const stats = await res.json();
  const recentWrap = document.getElementById('recent-strains');
  recentWrap.innerHTML = '';
  stats.recent.forEach(item => {
    const pill = document.createElement('div');
    pill.className = 'pill';
    pill.textContent = `${item.strain_name} (${item.date})`;
    recentWrap.appendChild(pill);
  });

  const countsWrap = document.getElementById('strain-counts');
  countsWrap.innerHTML = '';
  const labels = stats.counts.map(c => c.strain_name || 'Unknown');
  const values = stats.counts.map(c => c.count);
  stats.counts.forEach(c => {
    const pill = document.createElement('div');
    pill.className = 'pill';
    pill.textContent = `${c.strain_name || 'Unknown'} — ${c.count}`;
    countsWrap.appendChild(pill);
  });

  const ctx = document.getElementById('strain-chart');
  if (strainChart) strainChart.destroy();
  strainChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Purchases',
        data: values,
        backgroundColor: 'rgba(34,211,238,0.7)',
        borderColor: 'rgba(14,165,233,1)',
        borderWidth: 1,
      }],
    },
    options: {
      scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
      plugins: { legend: { display: false } },
    },
  });
}

// Recommendations
const recForm = document.getElementById('recommendation-form');
recForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const content = document.getElementById('recommendation-text').value;
  if (!content.trim()) return;
  await fetch('/api/recommendations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });
  document.getElementById('recommendation-text').value = '';
  loadRecommendations();
});

async function loadRecommendations() {
  const res = await fetch('/api/recommendations');
  const items = await res.json();
  const list = document.getElementById('recommendation-list');
  list.innerHTML = '';
  items.forEach(item => {
    const li = document.createElement('li');
    li.textContent = item.content;
    const btn = document.createElement('button');
    btn.className = 'danger';
    btn.textContent = 'Delete';
    btn.addEventListener('click', async () => {
      await fetch(`/api/recommendations/${item.id}`, { method: 'DELETE' });
      loadRecommendations();
    });
    li.appendChild(btn);
    list.appendChild(li);
  });
}

// PC setup
const pcDialog = document.getElementById('pc-dialog');
const pcForm = document.getElementById('pc-form');
document.getElementById('edit-pc').addEventListener('click', () => {
  pcDialog.showModal();
});

document.getElementById('cancel-pc').addEventListener('click', () => pcDialog.close());

pcForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(pcForm).entries());
  await fetch('/api/pc', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  pcDialog.close();
  loadPc();
});

async function loadPc() {
  const res = await fetch('/api/pc');
  const pc = await res.json();
  const dl = document.getElementById('pc-details');
  dl.innerHTML = '';
  const fields = [
    ['CPU', pc.cpu],
    ['GPU', pc.gpu],
    ['Monitors', pc.monitors],
    ['PSU', pc.psu],
    ['Storage', pc.storage],
  ];
  fields.forEach(([label, value]) => {
    const dt = document.createElement('dt');
    dt.textContent = label;
    const dd = document.createElement('dd');
    dd.textContent = value || '';
    dl.append(dt, dd);
    pcForm.elements[label.toLowerCase()].value = value || '';
  });
}

// Games
async function loadGames() {
  const res = await fetch('/api/games');
  const games = await res.json();
  const groups = {
    Finish: document.getElementById('games-finish'),
    'Dip in & out': document.getElementById('games-dip'),
    Done: document.getElementById('games-done'),
  };
  Object.values(groups).forEach(list => list.innerHTML = '');
  games.forEach(game => {
    const li = document.createElement('li');
    li.textContent = game.title;
    const btn = document.createElement('button');
    btn.className = 'secondary';
    btn.textContent = 'Remove';
    btn.addEventListener('click', async () => {
      await fetch(`/api/games/${game.id}`, { method: 'DELETE' });
      loadGames();
    });
    li.appendChild(btn);
    groups[game.category]?.appendChild(li);
  });
}

document.getElementById('add-game').addEventListener('click', async () => {
  const title = document.getElementById('game-title').value;
  const category = document.getElementById('game-category').value;
  if (!title.trim()) return;
  await fetch('/api/games', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, category }),
  });
  document.getElementById('game-title').value = '';
  loadGames();
});

// Media
async function loadMedia() {
  const res = await fetch('/api/media');
  const items = await res.json();
  const lists = {
    docs: document.getElementById('media-docs'),
    music: document.getElementById('media-music'),
    shows: document.getElementById('media-shows'),
  };
  Object.values(lists).forEach(l => l.innerHTML = '');
  items.forEach(item => {
    const li = document.createElement('li');
    li.textContent = item.title;
    const btn = document.createElement('button');
    btn.className = 'secondary';
    btn.textContent = 'Remove';
    btn.addEventListener('click', async () => {
      await fetch(`/api/media/${item.id}`, { method: 'DELETE' });
      loadMedia();
    });
    li.appendChild(btn);
    lists[item.category]?.appendChild(li);
  });
}

document.getElementById('add-media').addEventListener('click', async () => {
  const title = document.getElementById('media-title').value;
  const category = document.getElementById('media-category').value;
  if (!title.trim()) return;
  await fetch('/api/media', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, category }),
  });
  document.getElementById('media-title').value = '';
  loadMedia();
});

async function checkSeedStatus() {
  const res = await fetch('/api/seed-status');
  const status = await res.json();
  if (seedBanner) {
    seedBanner.hidden = !status.seeded;
  }
}

// Init
async function boot() {
  await Promise.all([
    checkSeedStatus(),
    loadWeed(),
    loadRecommendations(),
    loadPc(),
    loadGames(),
    loadMedia(),
  ]);
}

boot();
