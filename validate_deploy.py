"""Day 10 deployment validation script."""
import ast
import sys
import yaml

errors = []

# 1. app.py syntax
with open("app.py", encoding="utf-8") as f:
    src = f.read()
try:
    ast.parse(src)
    print("app.py          syntax OK")
except SyntaxError as e:
    errors.append(f"app.py syntax error: {e}")

# 2. Dockerfile
with open("Dockerfile", encoding="utf-8") as f:
    df = f.read()
for token in ["EXPOSE 8501", "HEALTHCHECK", "streamlit", "CMD"]:
    if token in df:
        print(f"Dockerfile      {token}: present")
    else:
        errors.append(f"Dockerfile missing: {token}")

# 3. render.yaml
with open("render.yaml", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
svc = cfg["services"][0]
print(f"render.yaml     service={svc['name']}  runtime={svc['runtime']}  region={svc['region']}")
env_keys = [e["key"] for e in svc["envVars"]]
print(f"render.yaml     env vars: {env_keys}")

# 4. README_HF.md front-matter
with open("README_HF.md", encoding="utf-8") as f:
    hf = f.read()
for line in ["sdk: streamlit", "app_file: app.py"]:
    if line in hf:
        print(f"README_HF.md    '{line}' OK")
    else:
        errors.append(f"README_HF.md missing: {line}")

# 5. .dockerignore
with open(".dockerignore", encoding="utf-8") as f:
    di = f.read()
for entry in [".env", "chroma_db/", "venv/"]:
    if entry in di:
        print(f".dockerignore   '{entry}' ignored OK")
    else:
        errors.append(f".dockerignore missing entry: {entry}")

print()
if errors:
    print("ERRORS:")
    for e in errors:
        print(" ", e)
    sys.exit(1)
else:
    print("All deployment files are valid.")
