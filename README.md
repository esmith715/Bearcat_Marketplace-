# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

## To Run

cd bearcat-marketplace

(**first time only**) npm install 

npm run dev

# FastAPI Backend (Server)

The backend server is built using FastAPI and runs in a Python virtual environment.

## Setup & Run Server

Follow these steps to get your local development enviornment up and running.

### Prerequisites

Before you begin, ensure you have the following installed on your system:

*   **Git:** For cloning the repository.
    *   [Download Git](https://git-scm.com/downloads)
*   **Python 3.8+:** The programming language for this project.
    *   [Download Python](https://www.python.org/downloads/)
*   **PostgreSQL:** The database system used by this application.
    *   [Download PostgreSQL](https://www.postgresql.org/download/)

### 1. Setup PostgreSQL

Set the password for the postgres user to 1234.

```bash
psql -U postgre
ALTER USER postgres WITH PASSWORD '1234';
```

Make sure the PostgreSQL service is running:

Linux:
```bash
sudo service postgresql start
```

Mac:
```bash
brew services start postgresql
```

### 2. Clone the Repository

Get a copy of the project onto your local machine.

```bash
git clone https://github.com/esmith715/Bearcat_Marketplace-.git
cd Bearcat_Marketplace
```

### 3. Create Database Schema

run:

```bash
psql -U postgres -f sql/schema.sql
```

You will be prompted for the password: 
Enter 1234

### 4. Install python Dependencies

Create and activate a python virtual environment:

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

After activating your virtual environment, install required packages:

```bash
pip install -r requirements.txt
```

### 5. Run the FastAPI Server

Finally, run the development server
```bash
uvicorn server.main:app --reload
```

The server will start at: http://127.0.0.1:8000

Swagger UI(Interactive Docs): http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

You can test endpoints directly from the browser using Swagger UI.

# To Update GitHub

**make sure you are on your branch**

git add .

git commit -m "your message"

git push origin main
