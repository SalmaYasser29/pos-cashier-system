document.addEventListener('DOMContentLoaded', () => {
  const listEl = document.getElementById('branchesList');
  const form = document.getElementById('branchForm');

  async function loadBranches() {
    listEl.innerHTML = 'Loading branches...';
    try {
      const data = await apiFetch('/api/branches/');
      renderBranches(data);
    } catch (err) {
      listEl.innerHTML = 'Error loading branches.';
      console.error(err);
    }
  }

  function renderBranches(branches) {
    if (!branches.length) {
      listEl.innerHTML = '<p>No branches yet.</p>';
      return;
    }
    const ul = document.createElement('ul');
    for (const b of branches) {
      const li = document.createElement('li');
      li.innerHTML = `<strong>${escapeHtml(b.name)}</strong> — ${escapeHtml(b.address || '')}
        <button data-id="${b.id}" class="delete-branch">Delete</button>
        <button data-id="${b.id}" class="edit-branch">Edit</button>`;
      ul.appendChild(li);
    }
    listEl.innerHTML = '';
    listEl.appendChild(ul);

    // attach delete handlers
    listEl.querySelectorAll('.delete-branch').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const id = btn.dataset.id;
        if (!confirm('Delete branch?')) return;
        try {
          await apiFetch(`/api/branches/${id}/`, { method: 'DELETE' });
          loadBranches();
        } catch (err) {
          alert('Delete failed: ' + (err.payload ? JSON.stringify(err.payload) : err.message));
        }
      });
    });

    // attach edit handlers (simple prompt flow)
    listEl.querySelectorAll('.edit-branch').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.id;
        const currentName = btn.parentElement.querySelector('strong').innerText;
        const newName = prompt('Branch name', currentName);
        if (!newName) return;
        try {
          await apiFetch(`/api/branches/${id}/`, { method: 'PUT', json: { name: newName } });
          loadBranches();
        } catch (err) {
          alert('Update failed');
        }
      });
    });
  }

  // handle create
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('branchName').value.trim();
    const address = document.getElementById('branchAddress').value.trim();
    if (!name) return alert('Name required');
    try {
      await apiFetch('/api/branches/', { method: 'POST', json: { name, address } });
      form.reset();
      loadBranches();
    } catch (err) {
      alert('Create failed');
      console.error(err);
    }
  });

  // small helper
  function escapeHtml(s){ if(!s) return ''; return s.replace(/[&<>"]/g, c=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;' }[c])); }

  loadBranches();
});
