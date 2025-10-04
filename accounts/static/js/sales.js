document.addEventListener("DOMContentLoaded", () => {
  // === Elements ===
  let cart = JSON.parse(localStorage.getItem("cart") || "[]");

  const cartTable = document.querySelector("#cartTable tbody");
  const discountInput = document.getElementById("discount");
  const paymentSelect = document.getElementById("payment_method");
  const mixedInputs = document.getElementById("mixedPaymentInputs");
  const checkoutBtn = document.getElementById("checkoutBtn");
  const customerSelect = document.getElementById("customer_id");
  const orderTypeSelect = document.getElementById("order_type");
  const itemSearchInput = document.getElementById("itemSearch");

  const deliveryWrapper = document.getElementById("deliveryAddressWrapper");
  const deliveryInput = document.getElementById("delivery_address");
  const tableNumberWrapper = document.getElementById("tableNumberWrapper");
  const tableNumberInput = document.getElementById("table_number");
  const customerWrapper = document.getElementById("customerWrapper");

  const addCustomerBtn = document.getElementById("addCustomerBtn");
  const customerModalEl = document.getElementById("customerModal");
  const customerForm = document.getElementById("customerForm");

  // === Helpers ===
  function getCSRFToken() {
    return document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="))
      ?.split("=")[1];
  }

  function saveCart() {
    localStorage.setItem("cart", JSON.stringify(cart));
  }

  // === Cart Rendering ===
  function renderCart() {
    if (!cartTable) return;
    cartTable.innerHTML = "";
    let total = 0;

    if (!cart.length) {
      cartTable.innerHTML = `<tr><td colspan="5">Cart is empty</td></tr>`;
      document.getElementById("cartTotal").innerText = "0.00";
      return;
    }

    cart.forEach((item) => {
      const line = item.price * item.quantity;
      total += line;

      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${item.name}</td>
        <td>
          <button class="btn btn-sm btn-danger decrease-btn" data-id="${item.id}">-</button>
          <span class="mx-2">${item.quantity}</span>
          <button class="btn btn-sm btn-success increase-btn" data-id="${item.id}">+</button>
        </td>
        <td>${item.price.toFixed(2)}</td>
        <td>${line.toFixed(2)}</td>
        <td>
          <button class="btn btn-sm btn-danger delete-btn" data-id="${item.id}">
            <i class="bi bi-trash"></i>
          </button>
        </td>
      `;
      cartTable.appendChild(row);
    });

    const discount = parseFloat(discountInput?.value) || 0;
    const discountedTotal = (total - (total * discount) / 100).toFixed(2);
    document.getElementById("cartTotal").innerText = discountedTotal;

    // Quantity controls
    document.querySelectorAll(".increase-btn").forEach((btn) => {
      btn.addEventListener("click", () => changeQuantity(parseInt(btn.dataset.id), 1));
    });
    document.querySelectorAll(".decrease-btn").forEach((btn) => {
      btn.addEventListener("click", () => changeQuantity(parseInt(btn.dataset.id), -1));
    });

    // Delete controls
    document.querySelectorAll(".delete-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        cart = cart.filter((i) => i.id !== parseInt(btn.dataset.id));
        saveCart();
        renderCart();
      });
    });
  }

  function changeQuantity(id, delta) {
    const item = cart.find((i) => i.id === id);
    if (!item) return;
    item.quantity += delta;
    if (item.quantity <= 0) {
      cart = cart.filter((i) => i.id !== id);
    }
    saveCart();
    renderCart();
  }

  function addToCart(id, name, price) {
    price = parseFloat(price);
    let existing = cart.find((i) => i.id === id);
    if (existing) existing.quantity += 1;
    else cart.push({ id, name, price, quantity: 1 });
    saveCart();
    renderCart();
  }

  // === Add-to-cart using clickable item cards ===
  document.querySelectorAll(".clickable-item").forEach((card) => {
    card.addEventListener("click", () => {
      addToCart(
        parseInt(card.dataset.id),
        card.dataset.name,
        parseFloat(card.dataset.price)
      );
    });
  });

  // === Payment Type Toggle ===
  if (paymentSelect && mixedInputs) {
    paymentSelect.addEventListener("change", () => {
      mixedInputs.style.display = paymentSelect.value === "mixed" ? "block" : "none";
    });
  }

  // === Delivery Address Logic ===
  function updateDeliveryAddress() {
    if (orderTypeSelect.value !== "delivery") {
      deliveryInput.value = "";
      return;
    }

    const customerId = customerSelect.value;
    if (!customerId) {
      deliveryInput.value = "";
      return;
    }

    const selectedOption = customerSelect.selectedOptions[0];
    if (selectedOption && selectedOption.dataset.address) {
      deliveryInput.value = selectedOption.dataset.address;
      return;
    }

    // AJAX fallback
    fetch(`/sales/customers/get_address/${customerId}/`)
      .then(res => res.json())
      .then(data => {
        deliveryInput.value = data.address || "";
      })
      .catch(err => {
        console.error("Failed to fetch customer address:", err);
        deliveryInput.value = "";
      });
  }

  function toggleOrderType() {
    const orderType = orderTypeSelect.value;

    if (orderType === "delivery") {
      deliveryWrapper.style.display = "block";
      tableNumberWrapper.style.display = "none";
      customerWrapper.style.display = "block";
      updateDeliveryAddress();
    } else if (orderType === "dine_in") {
      tableNumberWrapper.style.display = "block";
      deliveryWrapper.style.display = "none";
      deliveryInput.value = "";
      customerWrapper.style.display = "none";
      customerSelect.value = "";
      $(customerSelect).trigger("change");
    } else {
      tableNumberWrapper.style.display = "none";
      deliveryWrapper.style.display = "none";
      deliveryInput.value = "";
      customerWrapper.style.display = "none";
      customerSelect.value = "";
      $(customerSelect).trigger("change");
    }
  }

  orderTypeSelect.addEventListener("change", () => {
    toggleOrderType();
    updateDeliveryAddress();
  });

  if (customerSelect) {
    customerSelect.addEventListener("change", updateDeliveryAddress);
    $(customerSelect).on("select2:select", updateDeliveryAddress);
  }

  // === Live Discount Calculation ===
  if (discountInput) discountInput.addEventListener("input", renderCart);

  // === Checkout ===
  if (checkoutBtn) {
    checkoutBtn.addEventListener("click", () => {
      if (!cart.length) return alert("Cart is empty!");

      const discount = parseFloat(discountInput?.value) || 0;
      const payment_method = paymentSelect?.value || "";
      const customer_id = customerSelect?.value || null;
      const order_type = orderTypeSelect?.value || null;

      let delivery_address = "";
      let table_number = "";

      if (order_type === "delivery") {
        delivery_address = deliveryInput?.value || "";
        if (!delivery_address.trim()) return alert("Please enter delivery address.");
      } else if (order_type === "dine_in") {
        table_number = tableNumberInput?.value || "";
        if (!table_number.trim()) return alert("Please enter table number.");
      }

      let cash_amount = 0, card_amount = 0;
      if (payment_method === "mixed") {
        cash_amount = parseFloat(document.getElementById("cash_amount")?.value) || 0;
        card_amount = parseFloat(document.getElementById("card_amount")?.value) || 0;
      }

      const total = cart.reduce((sum, i) => sum + i.price * i.quantity, 0);
      const final_total = total - (total * discount) / 100;

      if (payment_method === "mixed" && cash_amount + card_amount !== parseFloat(final_total.toFixed(2))) {
        return alert(`Cash + Card must equal final total (${final_total.toFixed(2)})`);
      }

      fetch("/sales/checkout/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({
          items: cart.map((i) => ({ id: i.id, quantity: i.quantity })),
          discount,
          payment_method,
          customer_id,
          order_type,
          delivery_address,
          table_number,
          cash_amount,
          card_amount,
        }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.error) return alert("Error: " + data.error);
          localStorage.removeItem("cart");
          alert(`Sale completed!\nFinal Total: ${data.final_total}`);
          window.location.href = `/sales/detail/${data.sale_id}/`;
        })
        .catch((err) => alert("Checkout failed: " + err));
    });
  }

  // === Live Item Search ===
  if (itemSearchInput) {
    itemSearchInput.addEventListener("input", () => {
      const query = itemSearchInput.value.toLowerCase();
      document.querySelectorAll(".item-card").forEach((card) => {
        const name = card.dataset.name.toLowerCase();
        const category = card.dataset.category.toLowerCase();
        const supplier = (card.dataset.supplier || "").toLowerCase();
        const price = (card.dataset.price || "").toLowerCase();
        const stock = (card.dataset.stock || "").toLowerCase();

        card.style.display =
          name.includes(query) || category.includes(query) || supplier.includes(query) ||
          price.includes(query) || stock.includes(query)
            ? "block" : "none";
      });

      document.querySelectorAll(".category-items").forEach((container) => {
        const anyVisible = Array.from(container.children).some(c => c.style.display !== "none");
        if (container.previousElementSibling) {
          container.previousElementSibling.style.display = anyVisible ? "block" : "none";
        }
        container.style.display = anyVisible ? "flex" : "none";
      });
    });
  }

  // === Customer Modal Logic ===
  if (addCustomerBtn && customerModalEl && customerForm && customerSelect) {
    const customerModal = new bootstrap.Modal(customerModalEl);

    addCustomerBtn.addEventListener("click", () => {
      customerForm.reset();
      customerModal.show();
    });

    customerForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const formData = new FormData(customerForm);

      fetch(customerForm.action, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCSRFToken(),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: formData,
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.error) return alert("Error: " + data.error);

          const option = new Option(`${data.name} (${data.type})`, data.id, true, true);
          option.dataset.address = data.address || "";
          customerSelect.add(option);

          customerForm.reset();
          customerModal.hide();

          // Update delivery address immediately
          if (orderTypeSelect.value === "delivery") updateDeliveryAddress();
        })
        .catch((err) => alert("Failed to add customer: " + err));
    });
  }

  // === Initial Render ===
  renderCart();
  toggleOrderType();
  updateDeliveryAddress();
});
