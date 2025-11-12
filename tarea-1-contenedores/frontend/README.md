# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.



---

## 📘 **frontend/README.md**

```markdown
# Frontend — React + Vite + Nginx

Interfaz web que consume la API de FastAPI y permite crear, listar y eliminar tareas.

---

## ⚙️ Variables de entorno

| Variable | Descripción | Ejemplo |
|-----------|-------------|----------|
| `VITE_API_URL` | URL del backend | `http://localhost:3000` |

---

## ▶️ Correr localmente (sin Docker)
```bash
cd frontend
npm install
npm run dev
```

Luego abre http://localhost:5173

## 🐳 Correr con Docker

```bash
docker compose up frontend
```

## 📦 Build manual
```bash
npm run build
```
Los archivos compilados se guardan en dist/ y se sirven por Nginx dentro del contenedor.