```markdown
# API Documentation

## Base URL
`https://de-xuat-ea0h.onrender.com/api`

## Authentication
- All endpoints (except `/login`) require a JWT token in the `Authorization` header: `Bearer <token>`.
- Token is obtained from the `/login` endpoint.
- Tokens expire after 1 hour.

## Error Format
All errors return JSON with the following structure:
```json
{
  "message": "Error description",
  "status_code": <HTTP status code>
}
```

## Endpoints

### 1. POST /login
Authenticate a user and return a JWT token.

**Request**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Example Request**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response** (200 OK):
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "role": "admin",
  "branch": "Trụ sở chính"
}
```

**Errors**:
- 400 Bad Request: `{"message": "Username and password are required", "status_code": 400}`
- 401 Unauthorized: `{"message": "Tên đăng nhập hoặc mật khẩu không đúng!", "status_code": 401}`

### 2. GET /proposals
Retrieve a list of proposals (admin: all proposals; manager: proposals from their branch).

**Response** (200 OK):
```json
[
  {
    "branch": "Chi Nhánh 1",
    "id": 1,
    "proposer": "Nguyễn Văn A",
    "room": "Kinh Doanh",
    "department": "KD",
    "date": "2025-05-01",
    "code": "DX001",
    "proposal": "Mua laptop",
    "content": "Mua laptop phục vụ công việc",
    "purpose": "Phục vụ công việc hàng ngày",
    "supplier": "Công ty ABC",
    "estimated_cost": 15000000,
    "budget": 20000000,
    "approved_amount": 12000000,
    "transfer_code": "XBDC-28AFGEG",
    "payment_date": "2025-05-03",
    "notes": "",
    "status": "Đã duyệt",
    "approver": "Nguyễn Văn B",
    "approval_date": "2025-05-02",
    "completed": "Yes"
  }
]
```

**Errors**:
- 401 Unauthorized: `{"message": "Token required", "status_code": 401}`
- 403 Forbidden: `{"message": "Invalid token", "status_code": 403}`

### 3. POST /proposals
Create a new proposal (only managers can create).

**Request**:
```json
{
  "proposer": "string",
  "room": "string",
  "department": "string",
  "date": "string (YYYY-MM-DD)",
  "code": "string",
  "proposal": "string",
  "content": "string",
  "purpose": "string",
  "supplier": "string",
  "estimated_cost": number,
  "budget": number,
  "approved_amount": number,
  "transfer_code": "string",
  "payment_date": "string (YYYY-MM-DD)",
  "notes": "string",
  "status": "string",
  "approver": "string",
  "approval_date": "string (YYYY-MM-DD)",
  "completed": "string"
}
```

**Example Request**:
```json
{
  "proposer": "Nguyễn Văn A",
  "room": "Kinh Doanh",
  "department": "KD",
  "date": "2025-05-01",
  "code": "DX001",
  "proposal": "Mua laptop",
  "content": "Mua laptop phục vụ công việc",
  "purpose": "Phục vụ công việc hàng ngày",
  "supplier": "Công ty ABC",
  "estimated_cost": 15000000,
  "budget": 20000000,
  "approved_amount": 0,
  "transfer_code": "",
  "payment_date": "",
  "notes": "",
  "status": "Đang chờ duyệt",
  "approver": "",
  "approval_date": "",
  "completed": ""
}
```

**Response** (201 Created):
```json
{
  "branch": "Chi Nhánh 1",
  "id": 1,
  "proposer": "Nguyễn Văn A",
  "room": "Kinh Doanh",
  "department": "KD",
  "date": "2025-05-01",
  "code": "DX001",
  "proposal": "Mua laptop",
  "content": "Mua laptop phục vụ công việc",
  "purpose": "Phục vụ công việc hàng ngày",
  "supplier": "Công ty ABC",
  "estimated_cost": 15000000,
  "budget": 20000000,
  "approved_amount": 0,
  "transfer_code": "",
  "payment_date": "",
  "notes": "",
  "status": "Đang chờ duyệt",
  "approver": "",
  "approval_date": "",
  "completed": ""
}
```

**Errors**:
- 400 Bad Request: `{"message": "Validation error: {'proposer': ['Missing data for required field.']}", "status_code": 400}`
- 403 Forbidden: `{"message": "Admin không thể thêm đề xuất!", "status_code": 403}`
- 401 Unauthorized: `{"message": "Token required", "status_code": 401}`

### 4. PUT /proposals/:id
Update an existing proposal.

**Request**:
```json
{
  "proposer": "string",
  "room": "string",
  "department": "string",
  "date": "string (YYYY-MM-DD)",
  "code": "string",
  "proposal": "string",
  "content": "string",
  "purpose": "string",
  "supplier": "string",
  "estimated_cost": number,
  "budget": number,
  "approved_amount": number,
  "transfer_code": "string",
  "payment_date": "string (YYYY-MM-DD)",
  "notes": "string",
  "status": "string",
  "approver": "string",
  "approval_date": "string (YYYY-MM-DD)",
  "completed": "string"
}
```

**Example Request**:
```json
{
  "approved_amount": 12000000,
  "status": "Đã duyệt",
  "approver": "Nguyễn Văn B",
  "approval_date": "2025-05-02",
  "completed": "Yes"
}
```

**Response** (200 OK):
```json
{
  "branch": "Chi Nhánh 1",
  "id": 1,
  "proposer": "Nguyễn Văn A",
  "room": "Kinh Doanh",
  "department": "KD",
  "date": "2025-05-01",
  "code": "DX001",
  "proposal": "Mua laptop",
  "content": "Mua laptop phục vụ công việc",
  "purpose": "Phục vụ công việc hàng ngày",
  "supplier": "Công ty ABC",
  "estimated_cost": 15000000,
  "budget": 20000000,
  "approved_amount": 12000000,
  "transfer_code": "",
  "payment_date": "",
  "notes": "",
  "status": "Đã duyệt",
  "approver": "Nguyễn Văn B",
  "approval_date": "2025-05-02",
  "completed": "Yes"
}
```

**Errors**:
- 400 Bad Request: `{"message": "Validation error: {'date': ['Not a valid date format.']}", "status_code": 400}`
- 403 Forbidden: `{"message": "Bạn không có quyền chỉnh sửa đề xuất này!", "status_code": 403}`
- 404 Not Found: `{"message": "Đề xuất không tồn tại!", "status_code": 404}`
- 401 Unauthorized: `{"message": "Token required", "status_code": 401}`

### 5. DELETE /proposals/:id
Delete a proposal.

**Response** (204 No Content):
- No body

**Errors**:
- 403 Forbidden: `{"message": "Bạn không có quyền xóa đề xuất này!", "status_code": 403}`
- 404 Not Found: `{"message": "Đề xuất không tồn tại!", "status_code": 404}`
- 401 Unauthorized: `{"message": "Token required", "status_code": 401}`
```

**Giải thích**:
- Mô tả chi tiết các endpoint `/login`, `/proposals`, `/proposals/:id` (GET, POST, PUT, DELETE).
- Bao gồm ví dụ request/response với các cột mới (`room`, `purpose`, `budget`, `status`, `approver`, `approval_date`).
- Định dạng lỗi JSON với `message` và `status_code`, tương thích với `APIError` trong `app.py`.
- Dữ liệu trả về có `branch` ở đầu, đồng bộ với `format_proposal`.

---

### Hướng dẫn áp dụng các file

#### Bước 1: Cập nhật file trong thư mục `C:\de-xuat`
1. **Sao lưu file cũ**:
   ```bash
   mkdir C:\de-xuat\backup
   copy C:\de-xuat\app.py C:\de-xuat\backup\app.py
   copy C:\de-xuat\create_db.py C:\de-xuat\backup\create_db.py
   copy C:\de-xuat\requirements.txt C:\de-xuat\backup\requirements.txt
   copy C:\de-xuat\start.sh C:\de-xuat\backup\start.sh
   copy C:\de-xuat\API.md C:\de-xuat\backup\API.md
   ```

2. **Thay thế các file**:
   - **app.py**:
     - Mở `C:\de-xuat\app.py`, xóa nội dung cũ, dán nội dung từ đoạn code trên, và lưu.
   - **create_db.py**:
     - Mở `C:\de-xuat\create_db.py`, xóa nội dung cũ, dán nội dung từ đoạn code trên, và lưu **create_db.py**:
       - M opened `C:\de-xuat\create_db.py`, delete old content, paste content from the code above, and save.
   - **requirements.txt**:
     - M opened `C:\de-xuat\requirements.txt`, delete old content, paste content from the code above, and save.
   - **start.sh**:
     - M opened `C assaulted `C:\de-xuat\start.sh`, delete old content, paste content from the code above, and save.
   - **API.md**:
     - M opened `C:\de-xuat\API.md`, delete old content, paste content from the code above, and save.
   - **.env**:
     - Create or update `C:\de-xuat\.env` with the content above. Ensure `SECRET_KEY` is a secure random string.

3. **Add .env to .gitignore**:
   - M opened `C:\de-xuat\.gitignore` (or create it if it doesn't exist).
   - Add the following line:
     ```
     .env
     ```
   - Save the file.

#### Bước 2: Đẩy thay đổi lên GitHub
1. **Mở Command Prompt hoặc PowerShell**:
   ```bash
   cd C:\de-xuat
   ```

2. **Thêm file vào staging area**:
   ```bash
   git add app.py create_db.py requirements.txt start.sh API.md .gitignore
   ```

3. **Commit thay đổi**:
   ```bash
   git commit -m "Cập nhật backend với các cột mới, bảo mật, logging, và API documentation"
   ```

4. **Đẩy lên GitHub**:
   ```bash
   git push origin main
   ```
   - Nếu nhánh chính là `master`, thay `main` bằng `master`.

#### Bước 3: Triển khai trên Render
1. **Đăng nhập vào Render**:
   - Truy cập [Render Dashboard](https://dashboard.render.com) và mở dự án `de-xuat-ea0h`.

2. **Kiểm tra cấu hình**:
   - Đảm bảo dự án liên kết với repository `btbinh2710/de-xuat`.
   - Xác nhận nhánh triển khai là `main` (hoặc `master`).
   - Kiểm tra **Auto-Deploy** được bật.

3. **Thêm biến môi trường**:
   - Trong Render Dashboard, vào **Environment** của dự án.
   - Thêm biến:
     ```
     Key: SECRET_KEY
     Value: <your-secure-secret-key>
     ```
   - Lưu thay đổi.

4. **Kích hoạt triển khai thủ công (nếu cần)**:
   - Nếu Render không tự động triển khai, vào **Deploy** > **Manual Deploy** và chọn nhánh mới nhất.
   - Chờ 1-2 phút để triển khai hoàn tất.

#### Bước 4: Kiểm tra
1. **Backend**:
   - Truy cập `https://de-xuat-ea0h.onrender.com/api/proposals` với token hợp lệ (sử dụng Postman hoặc curl).
   - Kiểm tra response có các cột mới (`room`, `purpose`, `budget`, `status`, `approver`, `approval_date`) và `branch` ở đầu.
   - Kiểm tra log trong Render Dashboard (`logs/app.log`) để xác nhận các sự kiện và lỗi.

2. **Frontend**:
   - Truy cập `https://btbinh2710.github.io/de-xuat/`.
   - Đăng nhập (ví dụ: `admin`/`admin123`).
   - Tải mẫu Excel (`Tải mẫu Excel`) và kiểm tra file `DE_XUAT_THANH_TOAN_TEMPLATE.xlsx` có các cột mới và thứ tự đúng (`CHI NHÁNH` trước `BỘ PHẬN`).
   - Kiểm tra bảng đề xuất, modal chỉnh sửa, và chức năng tải lên/xuất báo cáo.
   - Mở console trình duyệt (F12 > Console) để xác nhận không có lỗi CORS hoặc API.

3. **Validation**:
   - Tạo file Excel với dữ liệu không hợp lệ (ví dụ: thiếu `proposer`) và thử tải lên.
   - Kiểm tra thông báo lỗi từ backend (như "Validation error: ...").

---

### Lưu ý
- **Bảo mật**:
  - Đảm bảo `SECRET_KEY` trong `.env` là duy nhất và an toàn. Không chia sẻ file `.env` hoặc đẩy lên GitHub.
  - Kiểm tra `.gitignore` để đảm bảo `.env` không được commit.

- **Logging**:
  - Sau khi triển khai, kiểm tra `logs/app.log` trên Render để xem các log về login, tạo/sửa/xóa đề xuất, và lỗi.

- **Backend đồng bộ**:
  - File `app.py` và `create_db.py` đã được cập nhật để hỗ trợ các cột mới. Nếu bạn đã có dữ liệu trong database, cần chạy migration để thêm các cột mới (liên hệ nếu cần hỗ trợ).

- **API.md**:
  - File `API.md` được cung cấp dựa trên giả định. Nếu bạn có nội dung `API.md` khác, hãy chia sẻ để tôi kiểm tra và điều chỉnh.

- **Môi trường Windows**:
  - Các lệnh trên được thiết kế cho Windows 11. Nếu bạn dùng MacBook, hãy báo lại để tôi điều chỉnh (dù các lệnh Git và Python thường giống nhau).

---

Nếu bạn cần hỗ trợ thêm, như kiểm tra lỗi cụ thể, cập nhật thêm file, hoặc tối ưu hóa, hãy phản hồi chi tiết! Chúc bạn thành công với dự án!