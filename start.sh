#!/usr/bin/env bash
set -e
python create_db.py
exec gunicorn app:app