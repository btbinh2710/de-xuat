import sqlite3

def migrate_db():
    try:
        conn = sqlite3.connect('data.db')
        c = conn.cursor()

        # Danh sách cột cần thêm
        new_columns = [
            ('room', 'TEXT'),
            ('purpose', 'TEXT'),
            ('budget', 'REAL'),
            ('transfer_code', 'TEXT'),
            ('payment_date', 'TEXT'),
            ('status', 'TEXT'),
            ('approver', 'TEXT'),
            ('approval_date', 'TEXT')
        ]

        # Lấy danh sách cột hiện tại
        c.execute("PRAGMA table_info(proposals)")
        existing_columns = [info[1] for info in c.fetchall()]

        # Thêm các cột thiếu
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                c.execute(f"ALTER TABLE proposals ADD COLUMN {column_name} {column_type}")
                print(f"✅ Đã thêm cột {column_name} vào bảng proposals.")
            else:
                print(f"ℹ Cột {column_name} đã tồn tại.")

        conn.commit()
        print("✅ Migration hoàn tất.")
    except Exception as e:
        print(f"⚠ Lỗi khi migration: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_db()