# FarmIntel-API

FarmIntel-API is a comprehensive farm management and intelligence backend built with Django and Django REST Framework. It provides a robust suite of tools for managing agricultural operations, including crop tracking, disease detection, cooperative management, and financial transactions.

## 🚀 Features

- **User & Organization Management**: Secure user authentication (JWT) and organization-based access control.
- **Crop Management**: Track crop lifecycles and data.
- **Disease Detection**: Integrated machine learning capabilities for plant disease detection (e.g., Tomato Yellow Leaf Curl Virus).
- **Cooperatives**: Tools for managing agricultural cooperatives.
- **Orders & Billing**: Complete system for managing orders, billing, and financial transactions.
- **Analytics**: Data-driven insights for farm productivity.
- **Notifications & Emails**: Integrated communication system.
- **Cloud Storage**: Seamless media management using Cloudinary.

## 🛠 Tech Stack

- **Framework**: Django 5.x, Django REST Framework (DRF)
- **Authentication**: JWT (JSON Web Tokens) via `rest_framework_simplejwt`
- **Database**: SQLite (Development) / PostgreSQL (Production ready)
- **Storage**: Cloudinary
- **Utilities**: `python-decouple` for configuration management

## 📂 Project Structure

The project consists of several modular applications:

- `users`: User accounts and authentication.
- `organizations`: Farm and organization hierarchy.
- `crops`: Crop data management.
- `detector`: ML-based plant disease detection.
- `orders`: Order processing and tracking.
- `billing`: Subscription and billing management.
- `transactions`: Financial transaction records.
- `cooperatives`: Cooperative group management.
- `analytics`: Reporting and data analysis.
- `notifications`: In-app and push notifications.
- `emails`: Email service integration.

## 🔧 Installation & Setup

### Prerequisites

- Python 3.10+
- pip (Python package manager)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/FarmIntel-API.git
cd FarmIntel-API
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory and add the following configuration variables:

```env
SECRET_KEY=your_secret_key
DEBUG=True
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

## 📖 API Documentation

The API endpoints are organized by module:

- **Admin**: `/admin/`
- **Users**: `/users/`
- **Organizations**: `/orgs/`
- **Billing**: `/billing/`
- **Cooperatives**: `/cooperatives/`
- **Notifications**: `/notifications/`
- **Detector**: `/detector/`
- **Crops**: `/crops/`
- **Analytics**: `/analytics/`
- **Orders**: `/orders/`
- **Transactions**: `/transactions/`
- **Upload**: `/upload/`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.
