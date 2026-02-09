FROM postgres:16-alpine

# These defaults will be overridden by docker-compose env_file
# PostgreSQL will use these variables to initialize the database on first run
ENV POSTGRES_DB=carsales
ENV POSTGRES_USER=carsales_user
ENV POSTGRES_PASSWORD=changeme

# Expose PostgreSQL port
EXPOSE 5432
