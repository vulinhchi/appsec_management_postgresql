# Sử dụng Python 3.10
FROM python:3.10

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép files vào container
COPY . .

# Cài đặt các dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Chạy server
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "task_manager.wsgi:application"]
