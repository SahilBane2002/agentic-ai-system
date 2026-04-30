# FROM python:3.12-slim

# WORKDIR /app

# # Copy just the metadata first for better layer caching
# COPY pyproject.toml ./

# # Upgrade pip (optional) and generate a requirements.txt from pyproject
# RUN python - <<'PY' > requirements.txt
# import tomllib, sys
# data = tomllib.load(open('pyproject.toml','rb'))
# deps = data.get('project', {}).get('dependencies', [])
# print("\n".join(deps))
# PY

# # Install dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Now copy the rest of the app
# COPY . .

# EXPOSE 8000
# # Change to whatever your entrypoint is
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]



FROM python:3.11-slim
WORKDIR /app

# Copy only pyproject first to leverage Docker layer caching
COPY pyproject.toml ./

# Generate requirements.txt from pyproject (clean heredoc; no prompts)
RUN python - <<'PY'
import tomllib, pathlib
deps = tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']
pathlib.Path('requirements.txt').write_text('\n'.join(deps))
print('Wrote requirements.txt with', len(deps), 'deps')
PY

# Install deps
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Add the rest of the source
COPY . .

EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
