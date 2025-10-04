document.addEventListener('DOMContentLoaded', () => {
  // ======================
  // Items + Cart logic
  // ======================
  const searchInput = document.querySelector('input[name="q"]');
  const itemsContainer = document.getElementById('items-container');
  const cartEl = document.getElementById('cart');

  // Debounced search for items
  if (searchInput) {
    let timer;
    searchInput.addEventListener('input', () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        loadItems(1, searchInput.value.trim());
      }, 300);
    });
  }

  // Load items via AJAX
  async function loadItems(page = 1, query = '') {
    if (!itemsContainer) return;
    const branchId = itemsContainer.dataset.branch;
    const categoryId = itemsContainer.dataset.category;
    const url = `/inventory/items/partial/${branchId}/${categoryId}/?page=${page}&q=${encodeURIComponent(query)}`;

    try {
      const response = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
      if (!response.ok) throw new Error("Network error");
      const data = await response.json();
      itemsContainer.innerHTML = data.html;

      // Re-bind pagination and cart buttons after reload
      bindPagination();
      bindCartButtons();
    } catch (err) {
      itemsContainer.innerHTML = '<p class="text-danger">Failed to load items.</p>';
      console.error(err);
    }
  }

  // Bind pagination buttons
  function bindPagination() {
    if (!itemsContainer) return;
    const buttons = itemsContainer.querySelectorAll('.paginate-btn');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const page = btn.dataset.page;
        const query = searchInput ? searchInput.value.trim() : '';
        loadItems(page, query);
      });
    });
  }

  // --- CART LOGIC ---
  window.__pos_cart = window.__pos_cart || [];

  function addItemToCart(item) {
    const cart = window.__pos_cart;
    const found = cart.find(c => c.id === item.id);
    if (found) found.quantity += item.quantity;
    else cart.push({ id: item.id, quantity: item.quantity });
    window.__pos_cart = cart;
    renderCart();
  }

  function renderCart() {
    if (!cartEl) return;
    const cart = window.__pos_cart || [];
    if (!cart.length) {
      cartEl.innerHTML = '<p>Cart is empty</p>';
      return;
    }
    const ul = document.createElement('ul');
    cart.forEach(c => {
      const li = document.createElement('li');
      li.textContent = `Item ${c.id} × ${c.quantity} `;
      const rem = document.createElement('button');
      rem.textContent = 'Remove';
      rem.classList.add('btn', 'btn-sm', 'btn-outline-danger', 'ms-2');
      rem.addEventListener('click', () => {
        window.__pos_cart = window.__pos_cart.filter(x => x.id !== c.id);
        renderCart();
      });
      li.appendChild(rem);
      ul.appendChild(li);
    });
    cartEl.innerHTML = '';
    cartEl.appendChild(ul);
  }

  function bindCartButtons() {
    if (!itemsContainer) return;
    const addBtns = itemsContainer.querySelectorAll('.add-to-cart');
    addBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const id = parseInt(btn.dataset.id);
        addItemToCart({ id, quantity: 1 });
      });
    });
  }

  // Initialize items and cart
  bindPagination();
  bindCartButtons();
  renderCart();

  // ======================
  // Categories AJAX search + pagination
  // ======================
  const categoriesContainer = document.getElementById('categoriesContainer');
  const categoriesSearchInput = document.getElementById('searchInput');
  const categoriesUrl = window.categoriesListUrl;

  function fetchCategories(url) {
    if (!categoriesContainer) return;
    if (typeof jQuery === 'undefined') return console.error("jQuery not loaded");
    
    $.ajax({
      url: url,
      data: $("#searchForm").serialize(),
      headers: { "X-Requested-With": "XMLHttpRequest" },
      success: function(data) {
        categoriesContainer.innerHTML = data.html;
      },
      error: function() {
        categoriesContainer.innerHTML = '<p class="text-danger">Failed to load categories.</p>';
      }
    });
  }

  // Live search for categories (debounced)
  if (categoriesSearchInput) {
    let timer;
    categoriesSearchInput.addEventListener('input', () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        fetchCategories(categoriesUrl);
      }, 300);
    });
  }

  // Handle pagination clicks (delegated)
  if (typeof jQuery !== 'undefined') {
    $(document).on('click', '.ajax-page', function(e) {
      e.preventDefault();
      const url = $(this).attr('href');
      fetchCategories(url);
    });
  }
});
