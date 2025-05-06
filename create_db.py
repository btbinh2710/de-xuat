import sqlite3
import bcrypt

def create_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Tạo bảng users
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        branch TEXT NOT NULL
    )''')
    
    # Tạo bảng proposals
    c.execute('''CREATE TABLE IF NOT EXISTS proposals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        maHang TEXT,
        tenHang TEXT,
        donVi TEXT,
        soLuong INTEGER,
        donGia REAL,
        thanhTien REAL,
        nhaCungCap TEXT,
        ghiChu TEXT,
        branch TEXT
    )''')
    
    # Tạo tài khoản admin
    admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    c.execute('INSERT OR IGNORE INTO users (username, password, branch) VALUES (?, ?, ?)',
              ('admin', admin_password, 'Trụ sở chính'))
    
    # Tạo tài khoản cho 14 chi nhánh (mẫu)
    branches = [
        ('hanoi', 'Hn@2025!', 'Hà Nội'),
        ('danang', 'Dn@2025!', 'Đà Nẵng'),
        ('hcm', 'Hcm@2025!', 'TP.HCM'),
        ('haiphong', 'Hp@2025!', 'Hải Phòng'),
        ('cantho', 'Ct@2025!', 'Cần Thơ'),
        ('hue', 'Hue@2025!', 'Huế'),
        ('nhatrang', 'Nt@2025!', 'Nha Trang'),
        ('vungtau', 'Vt@2025!', 'Vũng Tàu'),
        ('quangninh', 'Qn@2025!', 'Quảng Ninh'),
        ('longan', 'La@2025!', 'Long An'),
        ('binhduong', 'Bd@2025!', 'Bình Dương'),
        ('dongnai', 'Dn@2025!', 'Đồng Nai'),
        ('tayninh', 'Tn@2025!', 'Tây Ninh'),
        ('bacninh', 'Bn@2025!', 'Bắc Ninh')
    ]
    
    for username, password, branch in branches:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        c.execute('INSERT OR IGNORE INTO users (username, password, branch) VALUES (?, ?, ?)',
                  (username, hashed_password, branch))
    
    conn.commit()
    print('✅ Đã tạo user admin và các chi nhánh với mật khẩu mã hóa.')
    conn.close()

if __name__ == '__main__':
    create_db()