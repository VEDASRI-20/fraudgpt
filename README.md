
# FraudGPT – Real-Time Financial Fraud Detection System

FraudGPT is a full-stack AI-powered platform designed to detect real-time financial fraud before transactions are completed. It minimizes false positives and provides live alerts, enabling timely interventions. The system is built using **FastAPI** for the backend and **React.js** for the frontend, with a modern dashboard, transaction analytics, and an explainable fraud detection engine.

---

## Features

- Real-time fraud detection using AI models (CatBoost/XGBoost)  
- Administrative dashboard for monitoring live transactions  
- Dedicated flagged transactions view for high-risk activities  
- Light and dark mode interface  
- Real-time notifications for fraudulent alerts  
- WebSocket integration for live data streaming  

---

## Project Structure

```

fraudgpt-branch2/
├── fraudgpt-backend/       # FastAPI backend with model, WebSocket & API logic
├── fraudgpt-frontend/      # React frontend with dashboard, charts, and pages
│   ├── src/
│   │   ├── components/     # Sidebar, Navbar, Transaction Table
│   │   ├── pages/          # Landing, Login, Signup, Dashboard, Analysis
│   │   └── App.js          # Core layout logic with routing
├── transactions.csv        # Sample/mock data for simulations

````

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/fraudgpt.git
cd fraudgpt-branch2
````

---

### 2. Backend Setup (FastAPI)

Navigate to the backend folder:

```bash
cd fraudgpt-backend
```

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If a `requirements.txt` file is not available, install manually:

```bash
pip install fastapi uvicorn catboost scikit-learn pandas numpy joblib python-multipart haversine
```

> **Note:** The `haversine` library is required for geolocation calculations in the fraud detection logic.

Run the FastAPI server:

```bash
uvicorn backend:app --reload
```

The API will be available at:
[http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### 3. Frontend Setup (React.js)

Open a new terminal:

```bash
cd fraudgpt-frontend
npm install
npm start
```

The application will be available at:
[http://localhost:3000](http://localhost:3000)

---

## Routes

### Frontend (React)

| Route        | Description               |
| ------------ | ------------------------- |
| `/`          | Landing Page              |
| `/login`     | Login Page                |
| `/signup`    | Signup Page               |
| `/dashboard` | Transaction Dashboard     |
| `/flagged`   | Flagged Transactions View |
| `/analysis`  | Analytics and Graphs View |

### Backend (FastAPI)

| Endpoint   | Description                         |
| ---------- | ----------------------------------- |
| `/predict` | POST transaction for fraud scoring  |
| `/ws`      | WebSocket stream for real-time data |

---

## Mock Data Generation

To simulate transactions, run or modify the `train_model.py` script, or any relevant script that sends mock payloads to the backend API or WebSocket.

---

## Future Enhancements

* Addition of geo-location heatmaps
* Enhanced explainability layer using SHAP or LIME
* User authentication and access control
* Improved model accuracy with updated datasets

---

## Contributors

* Development Team – Built during Synchrony Hackathon 2025
* AI Model & Backend – Development Lead
* UI/UX & Frontend – Team Members

---

## License

This project is intended for educational and demonstration purposes only.

```

