#!/bin/bash --login
# The --login ensures the bash configuration is loaded,
# enabling Conda. 
set -euo pipefail
conda activate timeTracker
python wsgi.py
#gunicorn --bind 0.0.0.0:5000 wsgi:app --log-level=debug --reload --reload-extra-file src/templates/uploadVideo.html