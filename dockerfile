FROM python:3.11-slim as base

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y git

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=base /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Create and switch to a new user
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

# Install application into container
COPY . .

EXPOSE 5000

# Run the application, appropriate command for web and worker containers is specified in the docker compose file
# uncomment this only when you want to run this as standalone app
# ENTRYPOINT ["python", "app.py"]
