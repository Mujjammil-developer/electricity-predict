"""
Create clean deployment zip file excluding venv, __pycache__, etc.
"""
import os
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_OUT = os.path.join(BASE_DIR, "electricity_prediction_render.zip")

EXCLUDE_DIRS = {'venv', '.venv', '__pycache__', '.git'}
EXCLUDE_EXTS = {'.pyc', '.zip'}

with zipfile.ZipFile(ZIP_OUT, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            ext = os.path.splitext(f)[1]
            if ext in EXCLUDE_EXTS or f.startswith('.'):
                if f not in {'.python-version', '.gitignore'}:
                    continue
            file_path = os.path.join(root, f)
            arcname = os.path.relpath(file_path, BASE_DIR)
            zf.write(file_path, arcname)

print(f"Zip created at {ZIP_OUT} ({round(os.path.getsize(ZIP_OUT)/1024, 1)} KB)")
