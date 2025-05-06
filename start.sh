<<<<<<< HEAD
# start.sh
#!/usr/bin/env bash
set -e                            # có lỗi là dừng

python create_db.py              # ➊ tạo (nếu chưa có) data.db + user
exec gunicorn app:app            # ➋ chạy Gunicorn (sử dụng biến PORT của Render)
=======
#!/usr/bin/env bash
set -e

python create_db.py         # tạo / bổ sung user
exec gunicorn app:app       # Render tự đặt $PORT
>>>>>>> c61cfaea19d145307cefde1bc39dfc4cd646d0fb
