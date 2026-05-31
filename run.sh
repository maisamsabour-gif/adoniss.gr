#!/bin/bash
# Run Adonis Site on port 8001
cd "$(dirname "$0")"
python manage.py runserver 0.0.0.0:8001
