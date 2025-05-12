import sqlite3
import bcrypt
import os

def create_db():
    # Xóa database cũ nếu tồn tại
    try:
        if os.path.exists('data.db'):
            os.remove('data.db')
            print('Da xoa database cu.')
    except Exception as e:
        print(f'Loi khi xoa database cu: {e}')

    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Tạo bảng users
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        branch TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    
    # Tạo bảng proposals với đầy đủ cột
    c.execute('''CREATE TABLE IF NOT EXISTS proposals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proposer TEXT,
        room TEXT,
        branch TEXT,
        department TEXT,
        date TEXT,
        code TEXT,
        proposal TEXT,
        content TEXT,
        purpose TEXT,
        supplier TEXT,
        estimated_cost REAL,
        budget REAL,
        approved_amount REAL,
        transfer_code TEXT,
        payment_date TEXT,
        notes TEXT,
        status TEXT,
        approver TEXT,
        approval_date TEXT,
        completed TEXT
    )''')
    
    # Tạo tài khoản admin
    admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    c.execute('INSERT OR IGNORE INTO users (username, password, branch, role) VALUES (?, ?, ?, ?)',
              ('admin', admin_password, 'Trụ sở chính', 'admin'))
    
    # Tạo tài khoản cho 18 chi nhánh
    branches = [
        "XDV-THAODIEN", "XDV-THAINGUYEN", "XDV-QUAN12", "XDV-QUAN7", 
        "XDV-NGHEAN", "XDV-KHANHHOA", "XDV-HANOI", "XDV-DANANG", 
        "XDV-CANTHO", "PTT-TRANDUYHUNG", "PTT-THAODIEN", "PTT-QUAN12", 
        "PTT-QUAN7", "PTT-NHATRANG", "PTT-NGOCHOI", "PTT-NGHEAN", 
        "PTT-LANDMARK81", "PTT-KHANHHOA"
    ]
    
    for branch in branches:
        branch_lower = branch.lower().replace("-", "_")
        for i in range(1, 3):
            username = f"{branch_lower}_manager{i}"
            password = bcrypt.hashpw('manager123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            c.execute('INSERT OR IGNORE INTO users (username, password, branch, role) VALUES (?, ?, ?, ?)',
                      (username, password, branch, 'manager'))
    
    conn.commit()
    print('Da tao user admin va 36 tai khoan cho 18 chi nhanh voi mat khau ma hoa.')
    conn.close()

if __name__ == '__main__':
    create_db()