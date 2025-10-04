# 🧾 POS Cashier System

A Point of Sale (POS) Cashier System built with **Django** and **Bootstrap**, designed to manage sales, branches, customers, inventory, and reporting for retail businesses.  
It includes cashier operations, discounts, multiple payment methods and delivery order handling.

---

## 🚀 Features

- 👥 **User & Role Management** (Admin, Cashier, Manager)
- 🛒 **Sales Management**  
  - Add items to cart  
  - Discounts  
  - Multiple payment methods (cash, card, mixed)  
- 📦 **Inventory Management** (items, categories, and suppliers)  
- 👨‍👩‍👧 **Customer Management** (addresses, delivery orders)  
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
