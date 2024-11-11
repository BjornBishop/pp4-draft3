FROM gitpod/workspace-postgres

# Install PostgreSQL
RUN sudo install-packages postgresql-12 postgresql-contrib-12