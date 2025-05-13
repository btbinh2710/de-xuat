import sqlite3
import bcrypt
def init_db():
        try:
            conn = sqlite3.connect('proposals.db')
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT,
                    branch TEXT,
                    role TEXT
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS proposals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proposer TEXT,
                    room TEXT,
                    branch TEXT,
                    department TEXT,
                    date TEXT,
                    code TEXT,
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
                    completed TEXT,
                    UNIQUE(branch, code)
                )
            ''')
            users = [
                ('admin', 'admin123', 'Admin', 'admin'),
                ('accountant', 'accountant123', 'Accountant', 'accountant'),
                ('xdv_thaodien_manager1', 'manager123', 'XDV_ThaoDien', 'manager'),
                ('xdv_thaodien_employee1', 'employee123', 'XDV_ThaoDien', 'employee'),
                # Thêm các người dùng khác nếu cần
            ]
            for user in users:
                username, password, branch, role = user
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                c.execute('INSERT OR IGNORE INTO users (username, password, branch, role) VALUES (?, ?, ?, ?)',
                          (username, hashed.decode('utf-8'), branch, role))
            conn.commit()
            conn.close()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {str(e)}")

if __name__ == '__main__':
    init_db()
