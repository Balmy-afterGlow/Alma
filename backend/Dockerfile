FROM python:3.12

ENV PYTHONBUFFERED=1

WORKDIR /code/

# Install git and pip-tools
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Generate requirements.txt using mkreq.sh with BuildKit mounts
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=pyproject.toml,target=/code/pyproject.toml \
    --mount=type=bind,source=scripts/python_meta_script/extract_dependencies.py,target=/code/extract_dependencies.py \
    --mount=type=bind,source=scripts/mkreq.sh,target=/code/mkreq.sh,rw \
    chmod +x /code/mkreq.sh && \
    /code/mkreq.sh && \
    pip install -r requirements.txt

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