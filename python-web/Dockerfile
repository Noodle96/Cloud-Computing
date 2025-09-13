# syntax=docker/dockerfile:1.7
# ↑ Habilita características modernas de Dockerfile (como RUN --mount para cachear pip)

# 1) Imagen base mínima con Python 3.12
# Crea un nuevo stage 
FROM python:3.12-slim

# 2) Variables de entorno para buen comportamiento de Python en contenedores
# no generar .pyc (menos I/O) y 
# logs inmediatos a stdout/stderr

# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1                 

# 3) Directorio de trabajo dentro del contenedor (mejor que "RUN cd ...")
WORKDIR /app

# 4) Copiamos SOLO requirements primero:
#    - Optimiza la caché: si no cambian deps, no reinstala en rebuilds.
COPY requirements.txt .

# 5) Instala dependencias de Python:
#    - --mount=type=cache: cache local de pip (requiere BuildKit) -> builds más rápidos.
#    - --no-cache-dir: no guarda caches de pip en la imagen final (más liviana).
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# 6) Ahora sí copiamos TODO el código (esto invalida menos capas)
COPY . .

# 7) Seguridad: crear usuario no-root y asignarle la app
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 8) Documenta el puerto en el que escucha la app (EXPOSE no publica, solo documenta)
EXPOSE 8000

# 9) HEALTHCHECK: orquestadores/`docker ps` verán el estado del contenedor
#    - Usamos Python estándar para hacer una petición a /healthz
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/healthz').read()" || exit 1

# 10) Comando por defecto:
#     - ENTRYPOINT fija el ejecutable (gunicorn)
#     - CMD define argumentos por defecto (puedes sobreescribirlos con "docker run ... --workers 4", etc.)
ENTRYPOINT ["gunicorn"]
CMD ["app:app", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--access-logfile", "-", "--error-logfile", "-"]
