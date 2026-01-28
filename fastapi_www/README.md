# FastAPI Auth Frontend

หน้า Frontend สำหรับทดสอบ API Authentication

## วิธีรัน

### วิธีที่ 1: Python HTTP Server (แนะนำ)

```bash
cd fastapi_www
python -m http.server 3000
```

แล้วเปิด http://localhost:3000

### วิธีที่ 2: Node.js (ถ้ามี npx)

```bash
cd fastapi_www
npx serve -p 3000
```

### วิธีที่ 3: PHP Built-in Server

```bash
cd fastapi_www
php -S localhost:3000
```

## โครงสร้างไฟล์

```
fastapi_www/
├── index.html      # หน้าหลัก
├── css/
│   └── style.css   # Styles
├── js/
│   └── app.js      # JavaScript logic
└── README.md
```

## การตั้งค่า

- **API URL**: สามารถเปลี่ยน URL ของ API ได้ที่ด้านบนของหน้าเว็บ (default: http://localhost:8000)
- **Tokens**: เก็บใน localStorage จะยังคงอยู่เมื่อ refresh หน้า

## Features

| ฟีเจอร์ | รายละเอียด |
|--------|------------|
| Register | สมัครสมาชิกใหม่ |
| Login | เข้าสู่ระบบ (auto-save tokens) |
| Get Profile | ดูข้อมูลผู้ใช้ |
| Update Profile | แก้ไข username |
| Refresh Token | ขอ access token ใหม่ |
| Logout | ออกจากระบบ |
| Logout All | ออกจากระบบทุกอุปกรณ์ |
| Deactivate | ปิดใช้งานบัญชี |
| Health Check | ตรวจสอบสถานะ API |

## หมายเหตุ

- ต้องรัน Backend (fastapi_auth) ก่อน ที่ port 8000
- Frontend รันที่ port 3000
- CORS ถูกตั้งค่าไว้แล้วใน Backend
