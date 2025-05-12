import sqlite3
import re

def migrate_db():
    try:
        conn = sqlite3.connect('data.db')
        c = conn.cursor()

        # Phần 1: Thêm các cột thiếu
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

        # Phần 2: Chuyển đổi định dạng ngày
        # Lấy tất cả đề xuất
        c.execute("SELECT id, date, payment_date, approval_date FROM proposals")
        rows = c.fetchall()

        for row in rows:
            proposal_id = row[0]
            date = row[1]
            payment_date = row[2]
            approval_date = row[3]

            # Chuyển đổi định dạng ngày từ YYYY-MM-DD sang DD/MM/YYYY
            def convert_date(date_str):
                if date_str and re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                    year, month, day = date_str.split('-')
                    return f"{day}/{month}/{year}"
                return date_str

            new_date = convert_date(date)
            new_payment_date = convert_date(payment_date)
            new_approval_date = convert_date(approval_date)

            # Cập nhật lại đề xuất
            c.execute("""
                UPDATE proposals
                SET date = ?, payment_date = ?, approval_date = ?
                WHERE id = ?
            """, (new_date, new_payment_date, new_approval_date, proposal_id))

        conn.commit()
        print("✅ Migration hoàn tất, đã thêm cột thiếu và chuyển đổi định dạng ngày sang DD/MM/YYYY.")
    except Exception as e:
        print(f"⚠ Lỗi khi migration: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_db()