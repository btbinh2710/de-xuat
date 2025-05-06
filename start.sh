# start.sh
#!/usr/bin/env bash
set -e                            # có lỗi là dừng

python create_db.py              # ➊ tạo (nếu chưa có) data.db + user
exec gunicorn app:app            # ➋ chạy Gunicorn (sử dụng biến PORT của Render)
