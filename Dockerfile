FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt requirements-production.txt ./
RUN pip install --no-cache-dir -r requirements-production.txt
RUN groupadd --gid 10001 flowdesk && useradd --uid 10001 --gid flowdesk --create-home flowdesk
COPY --chown=flowdesk:flowdesk . .
RUN mkdir -p /app/database/data /app/staticfiles && chown -R flowdesk:flowdesk /app
USER flowdesk
EXPOSE 8000
CMD ["python", "scripts/production_start.py"]
