# Smart Expense Tracker

A modern, full-stack web application designed for students to track expenses, manage budgets, and analyze spending habits. Built with Flask, Python, MySQL, and modern web UI principles incorporating vibrant Gradients and Glassmorphism.

## Features
- **User Authentication**: Secure Login & Registration paired with a Hybrid Twilio OTP Verification framework (Graceful fallbacks).
- **Profile Management**: Dynamic Profile Dashboard supporting custom Avatar uploads, activity logs, and seamless profile editing.
- **Smart Expense Tracking**: Add, categorize, and delete daily expenses efficiently.
- **Dashboard Analytics**: Beautiful layouts designed to visually summarize daily expenditures.
- **Consistent UX/UI**: Professional typography integration and Dark Mode Switch mechanics natively built into the dashboard.

## Tech Stack
- **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphism), Vanilla JavaScript, FontAwesome Icons.
- **Backend**: Python, Flask, PyMySQL, Werkzeug Security Hooks.
- **Integrations**: Twilio (OTP Deliverability).

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/yuvakishorekoppula/smart-tracker.git
   cd smart-tracker
   ```

2. **Setup virtual environment**
   ```bash
   python -m venv venv
   # On Windows: venv\Scripts\activate
   # On Mac/Linux: source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize MySQL Database**
   Ensure MySQL is running on localhost. The app connects natively without strict environment keys for local runs, or modify `get_db_connection` in `app.py`.
   Run the initial setup scripts to generate tables:
   ```bash
   python init_db.py
   python update_db.py
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```
   *The server runs locally on `http://127.0.0.1:5000`.*
