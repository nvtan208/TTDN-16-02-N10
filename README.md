<h2 align="center">
    <a href="https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin">
    🎓 Faculty of Information Technology (DaiNam University)
    </a>
</h2>
<h2 align="center">
    PLATFORM ERP – BUSINESS INTERNSHIP
</h2>
<div align="center">
    <p align="center">
        <img src="docs/logo/aiotlab_logo.png" alt="AIoTLab Logo" width="170"/>
        <img src="docs/logo/fitdnu_logo.png" alt="FIT DNU Logo" width="180"/>
        <img src="docs/logo/dnu_logo.png" alt="DaiNam University Logo" width="200"/>
    </p>

[![AIoTLab](https://img.shields.io/badge/AIoTLab-green?style=for-the-badge)](https://www.facebook.com/DNUAIoTLab)
[![Faculty of Information Technology](https://img.shields.io/badge/Faculty%20of%20Information%20Technology-blue?style=for-the-badge)](https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin)
[![DaiNam University](https://img.shields.io/badge/DaiNam%20University-orange?style=for-the-badge)](https://dainam.edu.vn)

</div>

---

## 📖 1. Giới thiệu

**Platform ERP – Business Internship** là hệ thống ERP phục vụ cho học phần *Thực tập doanh nghiệp* tại Khoa Công nghệ Thông tin – Trường Đại học Đại Nam, được phát triển dựa trên mã nguồn mở **Odoo**.

Repository này **fork và kế thừa** từ dự án gốc:

* 🔗 https://github.com/FIT-DNU/Business-Internship

Repository GitHub cá nhân:

* 🔗 https://github.com/nvtan208/TTDN-16-02-N10

Trên nền tảng đó, nhóm thực hiện đã **mở rộng và phát triển thêm các module nghiệp vụ**, tiêu biểu là:

* 📌 Module Chấm công  
* 📌 Module Tính lương  

Mục tiêu của repository này là phục vụ mục đích **học tập, nghiên cứu, thực hành triển khai Odoo**, cũng như làm tài liệu tham khảo cho sinh viên trong quá trình thực tập và làm đồ án.

---

## ✨ 2. Các chức năng mở rộng

### 🕒 Module Chấm công
- Quản lý thông tin nhân viên
- Ghi nhận thời gian vào/ra
- Theo dõi ngày công, giờ làm việc
- Tổng hợp dữ liệu chấm công theo tháng

### 💰 Module Tính lương
- Tính lương dựa trên dữ liệu chấm công
- Hỗ trợ các khoản phụ cấp, khấu trừ
- Quản lý bảng lương theo kỳ
- Xuất báo cáo lương cho nhân viên

---

## 🔧 3. Các công nghệ được sử dụng
<div align="center">

### Hệ điều hành
[![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)](https://ubuntu.com/)
### Công nghệ chính
[![Odoo](https://img.shields.io/badge/Odoo-714B67?style=for-the-badge&logo=odoo&logoColor=white)](https://www.odoo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![XML](https://img.shields.io/badge/XML-FF6600?style=for-the-badge&logo=codeforces&logoColor=white)](https://www.w3.org/XML/)
### Cơ sở dữ liệu
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
</div>

---

## ⚙️ 4. Cài đặt

### 4.1. Cài đặt công cụ, môi trường và các thư viện cần thiết

#### 4.1.1. Tải project.
```
git clone https://github.com/nvtan208/TTDN-16-02-N10
```
#### 4.1.2. Cài đặt các thư viện cần thiết
Người sử dụng thực thi các lệnh sau đề cài đặt các thư viện cần thiết

```
sudo apt-get install libxml2-dev libxslt-dev libldap2-dev libsasl2-dev libssl-dev python3.10-distutils python3.10-dev build-essential libssl-dev libffi-dev zlib1g-dev python3.10-venv libpq-dev
```
#### 4.1.3. Khởi tạo môi trường ảo.
- Khởi tạo môi trường ảo
```
python3.10 -m venv ./venv
```
- Thay đổi trình thông dịch sang môi trường ảo
```
source venv/bin/activate
```
- Chạy requirements.txt để cài đặt tiếp các thư viện được yêu cầu
```
pip3 install -r requirements.txt
```
### 4.2. Setup database

Khởi tạo database trên docker bằng việc thực thi file dockercompose.yml.
```
sudo docker-compose up -d
```
### 4.3. Setup tham số chạy cho hệ thống
Tạo tệp **odoo.conf** có nội dung như sau:
```
[options]
addons_path = addons
db_host = localhost
db_password = odoo
db_user = odoo
db_port = 5431
xmlrpc_port = 8069
```
Có thể kế thừa từ file **odoo.conf.template**
### 4.4. Chạy hệ thống và cài đặt các ứng dụng cần thiết
Lệnh chạy
```
python3 odoo-bin.py -c odoo.conf -u all
```
Người sử dụng truy cập theo đường dẫn _http://localhost:8069/_ để đăng nhập vào hệ thống.

---

## 📝 5. Hình ảnh các chức năng của hệ thống

### 👥 Module Quản lý nhân sự
<img src="docs/logo/nhansu.png" width="800"/>
<img src="docs/logo/nhansu1.png" width="800"/>

### 🕒 Module Chấm công
<img src="docs/logo/chamcong.png" width="800"/>
<img src="docs/logo/chamcong1.png" width="800"/>

### 💰 Module Tính lương
<img src="docs/logo/tinhluong.png" width="800"/>
<img src="docs/logo/tinhluong1.png" width="800"/>

---

## 🖼️ 6. Poster hệ thống

<p align="center">
  <img src="docs/logo/Poster.png" alt="Poster hệ thống ERP" width="900"/>
</p>

---

✨ Developed & extended for learning and internship purposes.
