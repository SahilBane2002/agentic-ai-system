FROM python:3.11-slim
WORKDIR /app

COPY pyproject.toml ./

RUN python - <<'PY'
import tomllib, pathlib
deps = tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']
pathlib.Path('requirements.txt').write_text('\n'.join(deps))
PY

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
