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

navigate to the server directory
```bash
cd server
```

**Create and activate a python virtual environment before proceeding**

After activating your virtual environment, install the fastapi dependency
```bash
pip install "fastapi[standard]"
```

Finally, run the development server
```bash
fastapi dev main.py
```

# To Update GitHub

**make sure you are on your branch**

git add .

git commit -m "your message"

git push origin main
