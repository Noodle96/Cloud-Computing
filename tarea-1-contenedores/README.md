# 🧩 Tarea 1 — Aplicación con Contenedores (Docker)

Aplicación tipo **To-Do con etiquetas y estados**, dividida en **3 contenedores**:
- **Frontend:** React + Vite (interfaz web)
- **Backend:** FastAPI (API REST)
- **Database:** PostgreSQL 16 (persistencia)

---

## 🚀 Arquitectura general
[Navegador] → [Frontend:Nginx:80] → [Backend:FastAPI:3000] → [Postgres:5432]


Cada servicio tiene su propio `Dockerfile`, y se orquesta con **docker-compose**.  
Los contenedores se comunican por una red interna creada automáticamente por Docker Compose.

- **DB_HOST:** `database` (nombre del servicio)
- **DB_PORT:** `5432`
- **API:** `http://localhost:3000`
- **Frontend:** `http://localhost:5173`

---

## 🧰 Requisitos previos

1. Tener instalado **Docker Engine + Docker Compose v2**  
   - Verificar con:
     ```bash
     docker --version
     docker compose version
     ```

2. (Opcional) Node.js ≥ 20 si deseas probar el frontend sin Docker:
   ```bash
   npm install
   npm run dev


## 🏗️ Instalación y configuración

Clona el proyecto y entra al directorio:
```bash
git clone https://github.com/Noodle96/Cloud-Computing.git
cd tarea-1-contenedores
```

Construye las imágenes y levanta los contenedores:
```bash
docker compose up --build -d
```

Verifica:
```bash
docker compose ps
```
## 🌐 Acceso

| Servicio | URL local                                      | Descripción                      |
| -------- | ---------------------------------------------- | -------------------------------- |
| Frontend | [http://localhost:5173](http://localhost:5173) | Interfaz web (React + Nginx)     |
| Backend  | [http://localhost:3000](http://localhost:3000) | API REST (FastAPI)               |
| Database | localhost:5432                                 | PostgreSQL (volumen persistente) |

## 🧩 Comandos útiles

| Acción                 | Comando                                              |
| ---------------------- | ---------------------------------------------------- |
| Levantar en background | `docker compose up -d`                               |
| Detener contenedores   | `docker compose stop`                                |
| Ver logs               | `docker compose logs -f`                             |
| Reconstruir todo       | `docker compose up -d --build`                       |
| Borrar todo            | `docker compose down -v`                             |
| Entrar al backend      | `docker exec -it todos-api sh`                       |
| Entrar a la DB         | `docker exec -it todos-db psql -U postgres -d todos` |

## 💾 Volúmenes y persistencia

La base de datos usa un volumen llamado `dbdata` para persistir datos entre ejecuciones.

Para resetear la DB:
```bash
docker compose down -v
docker compose up -d
```

## 🧱 Estructura de carpetas
```bash
tarea-1-contenedores/
├── docker-compose.yml
├── README.md
├── frontend/
│   ├── README.md
│   ├── Dockerfile
│   └── src/...
├── backend/
│   ├── README.md
│   ├── Dockerfile
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── models.py
│       ├── schemas.py
│       ├── database.py
│       ├── tasks.py
│       ├── routers/
│       ├── migrations/
│       └── ...
└── database/
    ├── README.md
    ├── Dockerfile
    └── init/
        ├── 001_schema.sql
        └── 002_seed.sql
```

## 📦 Dependencias principales

| Servicio | Stack                        |
| -------- | ---------------------------- |
| Frontend | React, Vite, Nginx           |
| Backend  | FastAPI, SQLAlchemy, Uvicorn |
| Database | PostgreSQL 16                |

