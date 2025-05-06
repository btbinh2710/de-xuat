#!/usr/bin/env bash
set -e

python create_db.py         # tạo / bổ sung user
exec gunicorn app:app       # Render tự đặt $PORT
