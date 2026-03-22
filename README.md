# Smart Expense Tracker

A modern, full-stack expense tracking web application that helps individuals monitor their daily spending, manage budget limits, and gain financial insights through interactive data visualization.

Built with Flask, PyMySQL, and modern frontend technologies — featuring a robust hybrid authentication system and a premium glassmorphism UI.

## ✨ Features
| Feature | Description |
|---|---|
| 📊 **Dashboard Analytics** | Visual summary of spending categorizations using interactive charts. |
| 🔐 **Hybrid Authentication** | Secure Login & Registration paired with a Hybrid Twilio OTP Verification framework (with graceful mock fallbacks). |
| 👤 **Profile Management** | Dynamic Profile Dashboard supporting custom Avatar uploads, password resets, and activity logs. |
| 💸 **Expense Tracking** | Add, categorize, and delete daily expenses efficiently. |
| 🌙 **Dark Mode** | Seamless toggle between light and dark themes via an iOS-style switch. |
| 📱 **Responsive UI** | Modern, mobile-friendly design incorporating vibrant gradients and glassmorphism panels. |
| ⏳ **Activity Timeline** | Tracks and visualizes user behaviors directly on their profile dashboard. |

## 🏗️ Tech Stack
- **Backend:** Python, Flask, PyMySQL
- **Frontend:** HTML5, CSS3 (Glassmorphism/Variables), Vanilla JavaScript, Chart.js
- **Auth & Security:** Flask Sessions, Werkzeug (PBKDF2 Password Hashing)
- **Integrations:** Twilio REST API (SMS Delivery)

## 📁 Project Structure
```text
smart_expense_tracker/
├── app.py                  # Main Flask application & routing logic
├── init_db.py              # Initial database schema setup
├── update_db.py            # Schema migrations & database updates
├── generate_sample_data.py # Mock data populator for testing
├── requirements.txt        # Python dependencies
├── .gitignore              # Ignored files (venv, pycache)
├── .env                    # Twilio API keys and Secrets (not tracked)
│
├── static/
│   ├── css/
│   │   └── style.css       # Core styling (glassmorphism, dark mode, auth)
│   ├── js/
│   │   └── main.js         # Client-side form logic, dropdowns & Chart.js
│   └── uploads/profiles/   # User uploaded profile avatars
│
└── templates/
    ├── base.html           # Main layout block (Headers, Navbars, Fonts)
    ├── auth.html           # Unified login/register/forgot-password forms
    ├── dashboard.html      # Analytics, charts, and expense tables
    └── profile.html        # Profile management and activity timeline
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MySQL Server running locally
- A Twilio Account SID & Auth Token (Optional for SMS routing)

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/yuvakishorekoppula/smart-tracker.git
cd smart-tracker

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file with your API keys (Optional)
echo TWILIO_ACCOUNT_SID=your_sid_here > .env
echo TWILIO_AUTH_TOKEN=your_token_here >> .env
echo TWILIO_PHONE_NUMBER=your_number_here >> .env

# 5. Initialize the database
python init_db.py
python update_db.py

# 6. Run the application
python app.py
```
*The app will be live at `http://localhost:5000`*

## 🔄 Application Workflow

### Authentication Flow (Hybrid Architecture)
- Users visit `/login` and can register or login.
- If a user triggers the `Forgot Password` flow, the system pings the **Twilio API**.
- **Fail-Safe mechanism**: If Twilio credentials are missing or encounter an error, the system gracefully falls back to a Mock OTP (`123456`), guaranteeing users are never blocked during local development or API outages.

### Financial Tracking Flow
- User logs in → redirected to `/dashboard`.
- Submits an expense via the modal form → processed securely via backend and appended to MySQL.
- Chart.js instances fetch dynamic aggregations from the backend to render categorized spendings instantly.

### Profile & Activity Flow
- User accesses Avatar dropdown → Settings.
- Updates to personal details or profile pictures trigger file validations (using `werkzeug.utils.secure_filename`).
- Dedicated `activity_log` tracking scripts append timestamps into the DB visualizing a history timeline.

## 🗄️ Database Schema
| Table | Key Columns | Purpose |
|---|---|---|
| **users** | `id, name, email, phone, password_hash, profile_picture` | Student accounts and settings |
| **expenses** | `id, user_id, amount, category, date, description` | Financial transactions tracking |
| **activity_log** | `id, user_id, action, created_at` | Tracks user behaviors for timelines |

## 🔒 Security
- Passwords are hashed dynamically using **Werkzeug (PBKDF2)**.
- Protected endpoints leverage a robust `@login_required` session-based authentication wrapper.
- All Avatar uploads sanitize filenames enforcing secure storage protocols.
- The `.env` configurations are explicitly excluded from version control protecting infrastructure secrets.

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📄 License
This full-stack application was built for educational portfolio purposes mirroring enterprise design standards.
