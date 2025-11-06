# Girvi Management System

A modern web application for managing Girvi (pawn) transactions efficiently and securely.

## Features

- User authentication (register/login)
- Create and manage Girvi transactions
- Track transaction amounts, interest rates, and durations
- Modern and responsive UI
- Secure data storage

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Girvi
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure your virtual environment is activated

2. Run the Flask application:
```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Register a new account or login with existing credentials
2. Create new Girvi transactions with amount, interest rate, and duration
3. View and manage your transactions from the dashboard
4. Track transaction status and total amounts

## Security

- Passwords are securely hashed using Werkzeug's security functions
- Session management for authenticated users
- SQL injection protection through SQLAlchemy
- CSRF protection through Flask-WTF

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 