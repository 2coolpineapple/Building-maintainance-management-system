# 🏢 Building Maintenance Management System

A web-based **Building Maintenance Management System** built with **Django** and **Python**. It allows residents/tenants to raise maintenance complaints and enables admins/managers to track, assign, and resolve them efficiently.

---

## 📌 Features

- 🔐 User authentication (login/register)
- 📋 Raise maintenance complaints with media attachments
- 🗂️ Admin dashboard to view and manage all complaints
- 📁 Media upload support for complaint evidence (images, documents)
- ✅ Track complaint status (Pending / In Progress / Resolved)
- 🗃️ SQLite database for easy local setup

---

## 🛠️ Tech Stack

| Layer      | Technology        |
|------------|-------------------|
| Backend    | Python, Django    |
| Frontend   | HTML, CSS         |
| Database   | SQLite3           |
| Media      | Django Media Files|

---

## 📁 Project Structure

```
Building-maintainance-management-system/
│
├── core/                    # Main app — models, views, URLs, templates
├── maintenance_system/      # Django project config (settings, urls, wsgi)
├── complaint_media/         # Uploaded media files (complaint attachments)
├── manage.py                # Django management script
├── db.sqlite3               # SQLite database
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/2coolpineapple/Building-maintainance-management-system.git
   cd Building-maintainance-management-system
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install django
   ```

4. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Open in browser**
   ```
   http://127.0.0.1:8000/
   ```

---

## 🔑 Admin Panel

Access the Django admin panel at:
```
http://127.0.0.1:8000/admin/
```
Login with the superuser credentials you created above.

---

## 📸 Media Files

Complaint attachments are stored in the `complaint_media/` directory. Make sure `MEDIA_URL` and `MEDIA_ROOT` are correctly configured in `maintenance_system/settings.py`.

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'complaint_media'
```

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
