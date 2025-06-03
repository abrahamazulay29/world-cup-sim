FROM python:3.11-bookworm

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ── 1. requirements first ───────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --only-binary=:all: -r requirements.txt

# ── 2. copy project *including* pyproject.toml / src / tests / etc. ─────
COPY . .

# ── 3. editable install so “import src…” works anywhere ─────────────────
RUN pip install -e .

ENV PYTHONPATH=/app
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "src/app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
