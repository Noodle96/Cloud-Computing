FROM postgres:16-alpine

# Variables por defecto (se pueden overridear en docker-compose)
ENV POSTGRES_DB=todos \
    POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres

# Scripts de inicialización (se ejecutan solo si el volumen está vacío)
COPY init/ /docker-entrypoint-initdb.d/
