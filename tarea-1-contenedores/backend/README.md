
---

## 📗 **backend/README.md**

```markdown
# Backend — FastAPI

## ⚙️ Descripción
Servicio de API REST que gestiona tareas con etiquetas y estados.

---

## 🧱 Stack
- FastAPI
- SQLAlchemy
- PostgreSQL
- Uvicorn

---

## ⚙️ Variables de entorno

| Variable | Descripción | Valor por defecto |
|-----------|--------------|-------------------|
| `DB_HOST` | Host de la base de datos | `database` |
| `DB_PORT` | Puerto de conexión | `5432` |
| `DB_USER` | Usuario | `postgres` |
| `DB_PASSWORD` | Contraseña | `postgres` |
| `DB_NAME` | Nombre de la base de datos | `todos` |

---

## 🧩 Endpoints principales

| Método | Ruta | Descripción |
|---------|------|--------------|
| `GET` | `/api/tasks` | Listar tareas (opcional `status`, `tag`) |
| `POST` | `/api/tasks` | Crear tarea |
| `GET` | `/api/tasks/{id}` | Obtener una tarea |
| `PUT` | `/api/tasks/{id}` | Actualizar estado o info |
| `DELETE` | `/api/tasks/{id}` | Eliminar tarea |
| `GET` | `/healthz` | Comprobación de salud |

---

## ▶️ Correr localmente (opcional)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

## 🐳 Correr con Docker
```bash
docker compose up backend
```

## 🔌 Notas

- El servicio se conecta automáticamente a database (nombre de servicio en docker-compose).
- El CORS está habilitado para http://localhost:5173.