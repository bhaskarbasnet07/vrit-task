🔗 URL Shortener (Django)

A simple and powerful URL Shortener web app built with Django.
Shorten long links, track clicks, generate QR codes, and manage everything from a clean dashboard.

✨ What it does

. 🔐 User registration & login

. 🔗 Shortens long URLs using base62 keys

. ✏️ Create custom short URLs

. 📊 Track click counts & analytics

. ⏰ Expiration dates

. 📱 Generate QR codes

. 🔍 Search and manage your links

. 💻 Responsive design

🛠 Tech Stack

. Backend: Django 4.2

. Database: SQLite (easy setup)

. Frontend: Bootstrap 5, HTML, CSS

. Extras: QR Code generation, Bootstrap Icons

🚀 Quick Start

git clone <repository-url>
cd Vrit Task
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


Open 👉 http://127.0.0.1:8000/

📌 How to use

. Register & log in

. Create a short URL

. Add a custom key or expiry date

. Share the short link or QR code

. View analytics anytime

📁 Main Features at a Glance

. Create / Edit / Delete URLs

. Redirect via /<short_key>/

. Analytics with click history

. Secure & user-specific access