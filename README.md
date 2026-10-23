# Tour of Savings

A desktop financial-literacy application built for a Class 12 mathematics exhibition.

## Features
- User authentication with password hashing
- Savings dashboard with charts and account summaries
- Government savings scheme library
- Returns calculator and comparison charts
- Savings goals tracker
- Expense tracker with SQLite persistence
- Simulated wallet with educational warnings
- Side-income and financial education sections

## Requirements
Python 3.10+

## Windows setup
1. Install Python 3.10+ from https://python.org
2. Open Command Prompt and run:
   python -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
3. Start the app:
   python main.py

## Linux/macOS setup
1. python3 -m venv .venv
2. source .venv/bin/activate
3. python -m pip install --upgrade pip
4. python -m pip install -r requirements.txt
5. python main.py

## Testing
Run:
pytest

## Notes
- The app works offline after installation.
- The wallet is explicitly simulated and does not use real banking or payment systems.
- Scheme information includes official sources and should be checked against the latest government notifications before any investment decision.
