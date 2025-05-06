#!/usr/bin/env bash
set -e                         # gặp lỗi bất kỳ là dừng ngay

# 1) Tạo (hoặc bổ sung) user admin + 20 chi nhánh
python create_db.py

# 2) Khởi chạy Gunicorn – Render tự cấp biến $PORT
exec gunicorn app:app