# Setup

### Activating the Virtual Environment
```bash
cd .venv/Scripts
activate
cd ..
cd ..
```

### Running the Python Script
```bash
python app.py
```

# Tech Stack

**Client:** Flask, HTML5, CSS, MongoDB

# Application Overview
This application is a web-based platform designed for managing items and invoices. It utilizes the Flask framework for the backend and MongoDB for the database. The application consists of various HTML templates for different functionalities, suggesting a user interface for item and invoice management.

# Key Features
### Item Management:

- Add Item: Users can add new items to the inventory (add-item.html).
- Edit Item: Users can edit existing items (edit-item.html).
- View Item Details: Users can view details of individual items (item-details.html, item-details-new.html).
- New Item: Interface for creating a new item (new-item.html).

### Invoice Management:

- Create Invoice: Users can create new invoices (create-invoice.html).
- View Invoices: Users can view invoices (invoice.html, view-invoice.html, view-invoice-new.html).
- Invoice Creation Form: A form for creating invoices (invoice_creation_form.html).

### User Authentication:

- Login: Interface for user login (login.html).

### Dashboard:

- Dashboard: Main dashboard for the application (dashboard.html, dashboard-new.html).

### Index and Success Pages:

- Index: The main landing page of the application (index.html).
- Success: A success page to indicate successful operations (success.html).