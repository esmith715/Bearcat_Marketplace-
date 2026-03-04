# Prerequisites
Before you begin, ensure you have the following installed on your system:
*   **Git:** For cloning the repository.
    *   [Download Git](https://git-scm.com/downloads)
*   **Python 3.8+:** Used for the backend API.
    *   [Download Python](https://www.python.org/downloads/)
*   **Node.js (LTS) + npm:** Used for the React frontend.
    *   [Download Node.js](https://nodejs.org/en/download)
*   **PostgreSQL:** The database system used by this application.
    *   [Download PostgreSQL](https://www.postgresql.org/download/)

# How To Run

You will need to clone the repository and run the **postgres database**, **frontend client**, and the **backend server**

## Clone Repository

In your terminal, navigate to the directory you want the repository to exist in

Clone the repo:
```bash
git clone https://github.com/esmith715/Bearcat_Marketplace-.git
cd Bearcat_Marketplace-
```

## Create The Database

Make sure the postgres service is running:
```bash
# Windows (Powershell)
net start postgresql-x64-16

# MacOS
brew services start postgresql

# Linux
sudo service postgresql start
```

The following commands can also be performed using a GUI such as pgAdmin if you prefer.

Create the database (first time only):
```bash
psql -U postgres -c "CREATE DATABASE \"bearcat-marketplace\";"
```

For development, the backend expects the **postgres** user with password **1234**.

If your postgres password is different, either:
- update the database connection string in `server/db/database.py`, or
- change the postgres password with the following commands.

Change the postgres password (optional):

```bash
psql -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD '1234';"
```

Once the database is set up, you can now create the tables:
```bash
psql -U postgres -d "bearcat-marketplace" -f sql/schema.sql
```

There are more files in the sql folder that you can run to drop tables, or insert fake data for testing

## Run Frontend Client

In your first terminal, navigate to the frontend folder:
```bash
cd bearcat-marketplace
```

install the npm packages (first time only):
```bash
npm install 
```

Start the client:
```bash
npm run dev
```

## Run Backend Server

In your second terminal, make sure you are in the root directory (Bearcat_Marketplace-)

Create your Python virtual environment (first time only):
```bash
# Windows
python -m venv .venv

# MacOS/Linux
python3 -m venv .venv
```

Activate your Python virtual environment:
```bash
# Windows
./.venv/Scripts/Activate.ps1

# MacOS/Linux
source .venv/bin/activate
```

Install the required packages (first time, then again whenever the list is updated):
```bash
pip install -r server/requirements.txt
```

Start the server:
```bash
uvicorn server.main:app --reload
```
