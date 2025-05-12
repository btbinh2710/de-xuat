from app import create_app, db
from app.models import User, Proposal
import bcrypt

def create_db():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Tạo tài khoản admin
        admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin = User(
            username='admin',
            password=admin_password,
            branch='Trụ sở chính',
            role='admin'
        )
        db.session.add(admin)

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
                user = User(
                    username=username,
                    password=password,
                    branch=branch,
                    role='manager'
                )
                db.session.add(user)
        
        db.session.commit()
        print('✅ Đã tạo user admin và 36 tài khoản cho 18 chi nhánh với mật khẩu mã hóa.')

if __name__ == '__main__':
    create_db()