# mancoreapi

API backend built with FastAPI, PostgreSQL, and Alembic.

## Requirements

- Python 3.10+
- PostgreSQL

## Setup & Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/GustavoSanchezOrtiz/mancoreapi.git
   cd mancoreapi
   ```

2. **Set up virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Copy `.env.example` to `.env` and fill in your database and credentials:
   ```bash
   cp .env.example .env
   ```

4. **Run Database Migrations:**
   ```bash
   alembic upgrade head
   ```

5. **Start Development Server:**
   ```bash
   uvicorn app.main:app --reload
   ```
