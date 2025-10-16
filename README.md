# 🧾 POS Cashier System

A **Point of Sale (POS) Cashier System** built with **Django** and **Bootstrap**, designed for managing retail sales, inventory, customers, and reports across multiple branches.  
It enables smooth cashier operations, supports multiple payment methods, manages discounts, delivery order handling, and provides comprehensive reporting dashboards.

---

## 💡 Distinctiveness and Complexity

This project is **distinct** from all prior CS50W projects (Search, Wiki, Commerce, Mail, and Network) in both **purpose** and **technical implementation**.

Unlike the earlier assignments, which focused on single-purpose applications (e.g., a wiki or an email client), this POS Cashier System integrates **multiple business modules** into one large-scale, production-ready web system. It demonstrates a **real-world use case** that simulates how retail companies operate digitally.

### 🔹 Distinctiveness
- **Business Focus**: While previous CS50W projects are academic exercises, this one is a full enterprise application intended for day-to-day business operations.
- **Multi-role Access System**: Implements *Admin*, *Cashier*, and *Manager* roles, each with different permissions, extending beyond the simple authentication seen in “Network.”
- **Branch Management**: Supports multiple branches and branch-based sales tracking — a feature not present in any prior project.
- **Real-time Reporting & Analysis**: Uses Chart.js and dynamic JavaScript rendering to generate reports and visual insights.
- **Integrated Modules**: Combines sales, inventory, customers, and reports — multiple interconnected apps within a single Django project.

### 🔹 Complexity
This project demonstrates **technical complexity** in the following ways:
- **Modular Architecture**: Built as multiple Django apps (`accounts`, `sales`, `inventory`, `customers`, `branches`, `reports`) communicating through relationships and shared data models.
- **Role-based Authentication**: Enforces permissions at both view and template levels using session-based access control.
- **Dynamic Frontend Logic**: JavaScript and AJAX are used for live cart updates, mixed payment calculation, and delivery handling without reloading the page.
- **Reporting Engine**: Implements custom aggregation logic and visual dashboards for analyzing transactions, revenues, and payment methods.
- **Database-Driven Triggers (Conceptual)**: Simulates accounting logic and financial tracking for future database integration.
- **UI/UX Design**: Uses Bootstrap 5 with custom styles for a professional cashier interface.

Together, these features make this project more **complex and production-oriented** than any of the course’s prior assignments, showcasing full-stack mastery of Django, HTML, CSS, and JavaScript.

---

## 📁 Files Created and Modified

Below is a detailed summary of the main files I created or modified and their purposes.

### `pos_system/` (Main Django Configuration)
- **settings.py** — Configured installed apps, static/media paths, and database.
- **urls.py** — Global URL routing linking to all app URLs.
- **wsgi.py/asgi.py** — Deployment configuration files.

### `accounts/`
- **models.py** — Defines custom user model extensions with role and branch attributes.
- **views.py** — Handles login/logout, session management, and access control.
- **templates/accounts/** — Includes HTML templates for login pages, layout, and navigation.
- **static/** — Contains CSS and JS used sitewide.

### `branches/`
- **models.py** — Defines Branch model used to segment sales and reports.
- **views.py** — Provides branch CRUD operations for admins.
- **templates/branches/** — Displays branch lists and forms.

### `customers/`
- **models.py** — Manages customer data, including delivery addresses.
- **views.py** — Handles customer CRUD and dynamic address fetching (used in sales interface).
- **templates/customers/** — Customer form and list pages.

### `inventory/`
- **models.py** — Manages item, category, and supplier data.
- **views.py** — Handles inventory CRUD operations and stock tracking.
- **templates/inventory/** — Pages for adding and editing inventory data.

### `sales/`
- **models.py** — Core transactional logic (Sales, SaleItems, Payments).
- **views.py** — Processes checkout logic, discounts, mixed payments, and order types.
- **templates/sales/** — POS cashier interface (cart, order creation, checkout).

### `reports/`
- **views.py** — Generates aggregated sales and revenue data for dashboards.
- **templates/reports/** — Displays data visualization using Chart.js.
- **models.py** — Defines any helper models for storing summarized report data.

---

## 🚀 Features

- 👥 **User & Role Management** (Admin, Cashier, Manager)
- 🛒 **Sales Management**  
  - Add items to cart  
  - Discounts  
  - Multiple payment methods (cash, card, mixed)  
- 📦 **Inventory Management** (items, categories, and suppliers)  
- 👨‍👩‍👧 **Customer Management** (addresses, delivery orders)  
- 🏢 **Branch Handling**
  - Branch-specific sales and user restrictions
- 📊 **Reports & Dashboards**  
  - Daily, weekly, monthly, and yearly sales reports  
  - Payment method charts  
  - Branch-wise sales  
- 🔒 **Authentication & Security**  
  - Login/logout with session handling  
  - Branch-based restrictions  

---

## 🛠️ Tech Stack

- **Backend**: [Django](https://www.djangoproject.com/) (Python 3.x)
- **Frontend**: HTML5, CSS3, [Bootstrap 5](https://getbootstrap.com/), JavaScript
- **Database**: SQLite (default, can be changed to MySQL/PostgreSQL)
- **Other**: jQuery, Chart.js (for reports) and daterangepicker

---

## 📂 Project Structure

```
POS-cashier-system/
│── manage.py
│── db.sqlite3
│── requirements.txt
│
├── pos_system/              # Main Django project (settings, urls, wsgi, asgi)
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                # User authentication, roles, and profiles
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── tests.py
│   ├── migrations/
│   ├── templates/accounts/
│   └── static/              # Global static files
│       ├── css/
│       ├── js/
│       └── images/
│
├── branches/                # Branches management
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   └── templates/branches/
│
├── customers/               # Customer records and delivery addresses
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   └── templates/customers/
│
├── inventory/               # Items, categories, and suppliers
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   └── templates/inventory/
│
├── media/                   # Uploaded files (images, docs, etc.)
│   ├── items/
│   └── profiles/
│
├── reports/                 # Sales & finance reports
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   └── templates/reports/
│
└── sales/                   # Sales and checkout module
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── urls.py
    ├── views.py
    ├── migrations/
    └── templates/sales/

```

---

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/POS-cashier-system.git
   cd POS-cashier-system
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv YOURVENVNAME
   source YOURVENVNAME/bin/activate   # On Linux/Mac
   YOURVENVNAME\Scripts\activate      # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the server**
   ```bash
   python manage.py runserver
   ```

7. **Access the app**  
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

### 🎥Video demo 
  <https://youtu.be/Y_9lZrPOiws>

---

## 👨‍💻 Author

- Developed by **SALMA YASSER ABDELRAHMAN**  
- 📧 Contact: yasalma850@gmail.com
