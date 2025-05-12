# Sử dụng image Python 3.11 slim để giảm kích thước
FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép requirements.txt và cài đặt thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn
COPY . .

# Thiết lập biến môi trường
ENV PORT=10000
ENV SECRET_KEY=e0e55e5f584ef6555aa9bb957a4b75fb0d674e0693c54da243ee8dcbefff7258
ENV DATABASE_URL=sqlite:///data.db

# Khởi tạo database và chạy migration
RUN python create_db.py && \
    flask db init && \
    flask db migrate && \
    flask db upgrade

# Mở port
EXPOSE 10000

# Chạy ứng dụng với Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:create_app()"]