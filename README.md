# appsec_management_mongo

tạo key:
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout nginx/ssl/selfsigned.key \
  -out nginx/ssl/selfsigned.crt \
  -subj "/C=VN/ST=HCM/L=HCM/O=MyApp/OU=Dev/CN=localhost"


hoặc (để có thể setup dùng domain hoặc IP và file openss.cnf)
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout nginx/ssl/selfsigned.key \
  -out nginx/ssl/selfsigned.crt \
  -config nginx/ssl/openssl.cnf
