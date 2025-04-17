# Use official Postgres image as the base
FROM postgres:15

# Install pgvector extension
RUN apt-get update && \
    apt-get install -y postgresql-server-dev-15 && \
    apt-get install -y gcc make git && \
    git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git /pgvector && \
    cd /pgvector && \
    make && \
    make install && \
    rm -rf /pgvector
