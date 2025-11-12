
---

## 📙 **database/README.md**

```markdown
# Database — PostgreSQL 16

Contenedor de base de datos basado en la imagen oficial de Postgres.

---

## 📂 Estructura

database/
├── Dockerfile
└── init/
├── 001_schema.sql # crea tablas
└── 002_seed.sql # datos de ejemplo


---

## ⚙️ Variables de entorno

| Variable | Descripción | Valor |
|-----------|--------------|-------|
| `POSTGRES_DB` | Nombre de la base de datos | `todos` |
| `POSTGRES_USER` | Usuario | `postgres` |
| `POSTGRES_PASSWORD` | Contraseña | `postgres` |

---

## 💾 Volumen de datos

El volumen `dbdata` mapea `/var/lib/postgresql/data` para persistir datos entre reinicios.

---

## ▶️ Conectarse manualmente
```bash
docker exec -it todos-db psql -U postgres -d todos
```

## 🧩 Nota

Los scripts de init/ se ejecutan automáticamente solo la primera vez que el volumen está vacío.
Si eliminas el volumen (docker compose down -v), se recrea la base y se vuelven a aplicar los scripts.