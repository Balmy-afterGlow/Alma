FROM python:3.12

ENV PYTHONBUFFERED=1

WORKDIR /code/

# Install git and pip-tools
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/* \
    && pip install pip-tools

# Generate requirements.txt and install dependencies with BuildKit cache
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    pip-compile pyproject.toml --output-file requirements.txt \
    && pip install -r requirements.txt

# Copy project files
COPY ./pyproject.toml ./alembic.ini /code/
COPY ./scripts /code/scripts
COPY ./alembic /code/alembic
COPY ./app /code/app

# Install the project with BuildKit cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install .

ENV PYTHONPATH=/code

CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]