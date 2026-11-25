# RobertRide – Backend API

RobertRide is a ride-hailing application designed to connect passengers with drivers through a digital platform.

This repository contains the backend API responsible for handling application logic, ride management, database operations and communication with the frontend.

## 🚀 Project Features

- Backend API built with Flask.
- Ride management functionality.
- Driver location tracking support.
- GPS integration support.
- Fare calculation based on distance.
- Database integration.
- Frontend and backend API communication.

## 🛠️ Technologies Used

- Python
- Flask
- SQLAlchemy
- PostgreSQL
- REST APIs
- Git and GitHub

## 💰 Fare Calculation

The application uses the following fare structure:

- Base fare: KSh 100
- Distance charge: KSh 50 per kilometre

**Total Fare = Base Fare + (Distance × Rate per Kilometre)**

## 📁 Project Structure

```text
robertride-backend/
├── app/
├── requirements.txt
├── ...
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/robert00-1/robertride-backend.git
cd robertride-backend
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file and configure the required database and application settings.

### 4. Run the application

Use the appropriate Flask startup command configured in the project.

## 🌐 Related Repository

**Frontend:** https://github.com/robert00-1/robertride-frontend

## 👨‍💻 Developer

**Robert Mmasi**

GitHub: https://github.com/robert00-1

Portfolio: https://portfolio1-zeta-sand.vercel.app

---

Developed as a full-stack software engineering project.
