document.addEventListener('DOMContentLoaded', () => {
  const listEl = document.getElementById('customersList');
  const searchInput = document.getElementById('customerSearch');
  const addBtn = document.getElementById('addCustomerBtn');
  const formContainer = document.getElementById('customerFormContainer');

  async function loadCustomers(q = '') {
    if (!listEl) return;
    listEl.innerHTML = 'Loading...';
    try {
      const url = q ? `/api/customers/?q=${encodeURIComponent(q)}` : '/api/customers/';
      const data = await apiFetch(url);
      renderCustomers(data);
    } catch (err) {
      listEl.innerHTML = 'Error loading customers';
    }
  }

  function renderCustomers(customers) {
    if (!customers.length) {
      listEl.innerHTML = '<p>No customers</p>';
      return;
    }
    const table = document.createElement('table');
    table.innerHTML = '<tr><th>Name</th><th>Phone</th><th>Type</th><th>Actions</th></tr>';
    for (const c of customers) {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${escapeHtml(c.name)}</td><td>${escapeHtml(c.phone||'')}</td><td>${escapeHtml(c.type||'')}</td>
        <td>
          <button data-id="${c.id}" class="edit-c">Edit</button>
          <button data-id="${c.id}" class="delete-c">Delete</button>
        </td>`;
      table.appendChild(tr);
    }
    listEl.innerHTML = '';
    listEl.appendChild(table);

    table.querySelectorAll('.delete-c').forEach(btn=>{
      btn.addEventListener('click', async ()=> {
        if(!confirm('Delete customer?')) return;
        try {
          await apiFetch(`/api/customers/${btn.dataset.id}/`, { method: 'DELETE' });
          loadCustomers();
        } catch (err) { alert('Delete failed'); }
      });
    });

    table.querySelectorAll('.edit-c').forEach(btn=>{
      btn.addEventListener('click', async ()=>{
        const id = btn.dataset.id;
        // fetch and show simple inline edit form
        try {
          const data = await apiFetch(`/api/customers/${id}/`);
          showForm(data);
        } catch (err) { alert('Failed to load'); }
      });
    });
  }

  // simple add button opens form UI (or redirect to a dedicated form URL)
  if (addBtn) addBtn.addEventListener('click', () => {
    showForm();
  });

  // search typing
  if (searchInput) {
    let t;
    searchInput.addEventListener('input', () => {
      clearTimeout(t);
      t = setTimeout(()=> loadCustomers(searchInput.value.trim()), 300);
    });
  }

  function showForm(customer = null) {
    formContainer.style.display = 'block';
    formContainer.innerHTML = `
      <div class="card">
        <h3>${customer ? 'Edit' : 'Add'} Customer</h3>
        <form id="inlineCustomerForm">
          <input type="hidden" id="custId" value="${customer ? customer.id : ''}">
          <label>Name</label>
          <input id="custName" value="${customer ? escapeHtml(customer.name) : ''}" required>
          <label>Phone</label>
          <input id="custPhone" value="${customer ? escapeHtml(customer.phone||'') : ''}">
          <label>Type</label>
          <select id="custType">
            <option value="regular" ${customer && customer.type === 'regular' ? 'selected' : ''}>Regular</option>
            <option value="vip" ${customer && customer.type === 'vip' ? 'selected' : ''}>VIP</option>
          </select>
          <div style="margin-top:8px">
            <button type="submit">Save</button>
            <button type="button" id="cancelCust">Cancel</button>
          </div>
        </form>
        <div id="custMsg"></div>
      </div>`;
    document.getElementById('cancelCust').addEventListener('click', () => { formContainer.style.display='none'; });
    document.getElementById('inlineCustomerForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const id = document.getElementById('custId').value;
      const payload = {
        name: document.getElementById('custName').value.trim(),
        phone: document.getElementById('custPhone').value.trim(),
        type: document.getElementById('custType').value
      };
      try {
        if (id) await apiFetch(`/api/customers/${id}/`, { method: 'PUT', json: payload });
        else await apiFetch('/api/customers/', { method: 'POST', json: payload });
        formContainer.style.display='none';
        loadCustomers();
      } catch (err) {
        document.getElementById('custMsg').innerText = 'Save failed';
      }
    });
  }

  function escapeHtml(s){ if(!s) return ''; return s.replace(/[&<>"]/g, c=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;' }[c])); }

  // initial load
  loadCustomers();
});
