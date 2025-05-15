# appsec_management_mongo

## Tạo key SSL:
```
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout nginx/ssl/selfsigned.key \
  -out nginx/ssl/selfsigned.crt \
  -subj "/C=VN/ST=HCM/L=HCM/O=MyApp/OU=Dev/CN=localhost"
```

hoặc (để có thể setup dùng domain hoặc IP và file openss.cnf)
```
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout nginx/ssl/selfsigned.key \
  -out nginx/ssl/selfsigned.crt \
  -config nginx/ssl/openssl.cnf
```

## Build app
### Tạo account thường
- Account `webadmin`
- Thư mục chứa code /home/webadmin/web

### Tạo image của webapp
- Chạy lệnh để build toàn bộ code: `docker-compose build`
Sau khi build xong, sẽ có image `myapp_web:latest`

- Nếu chỉ muốn build 1 web image thôi: `docker build -t myapp_web:latest .` (cũng k cần lắm, cứ build hết rồi nén file .tar riêng sau)

-  Import tất cả image thành file .tar
`docker save -o myapp_images.tar myapp_web:latest postgres:latest nginx:latest`
Nếu chỉ cần nén 1 image thôi: `docker save -o myapp_web.tar myapp_web:latest`

Có thể lỗi không đủ space, chạy `docker image prune -a`  `docker system prune -a --volumes` để xóa image k dùng tới
### Build app từ image đã build
- Sau đó copy file qua server, load image vào Docker:
`docker load -i myapp_images.tar`
Có thể check xem đã có những image nào `docker images`

- Tạo lại container từ image
	– Nếu  có file docker-compose.yml:
	`docker-compose up -d`
	Lưu ý: 
		- docker-compose.yml cần bỏ dòng `build: .` _Vì nếu để dòng này thì sẽ tự động build mới chứ k dùng image có sẵn_
		- Sửa thông tin image của postgresl và nginx cho đúng với danh sách images đang có
	– Nếu không dùng docker-compose, thì  chạy tay:
	Ví dụ chạy web app:
	`docker run -d -p 8000:8000 --name my_web myapp_web:latest`
Tương tự với postgres, nginx…

### Tạo account superuser
`docker-compose exec web python manage.py createsuperuser`
sau khi tạo xong superuser, login tại `https://<ip/domain>/admin`

## Vận hành app
### Import dữ liệu


## Backup


## Một số câu lệnh có thể cần thiết
`docker-compose down -v`  # Xóa toàn bộ dữ liệu tức là xóa volume DB
`docker-compose up -d --build` #nếu muốn chạy lại cài đặt thư viện requirement **áp dụng khi build app từ source code**
`docker-compose up -d` #nếu run lại image, k cài lại thư viện
`docker-compose restart web` #nếu chỉ cần restart container web để apply code mới.
`docker-compose exec web bash` #access vào container

