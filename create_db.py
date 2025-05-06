
import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('data.db')

# Tạo bảng users nếu chưa có
conn.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    branch TEXT
)
''')

# Thêm danh sách users (20 chi nhánh + admin)
conn.execute('''
INSERT OR IGNORE INTO users (username, password, role, branch)
VALUES 
    ('admin', 'scrypt:32768:8:1$YI9anF1cqMPm2lVI$1ee15ff277706ff977cf03d95c5791b91533cd1eb682647f2ab3ec160cc51a58a186aa5161aeeb51be916d2e23771311b9200ef033e2d3dcac0d3617eda68cdf', 'admin', 'None'),
    ('ptt_tranduyhung_manager1', 'scrypt:32768:8:1$hq96lMD8fDVgAyPl$990afbb4e6333aa4bbecefa9c510df8226bd4e158a19628795e3473fcc73fd26c9838faaa2287d8b349209bd41886dd4d1c9867dbc19b1ab99ddc2424722513a', 'branch', 'PTT-TRANDUYHUNG'),
    ('pttcantho', 'scrypt:32768:8:1$SVYmEy6cqy3woeV3$1ad2381ee7741a9d920c432f412d44c994fc2f2fd937024fcca3c7ccc0afcd05bbfbbd27970eb2d1c811867e913efdce6018464348de19c720e05ae7ed339e81', 'branch', 'PTT-CANTHO'),
    ('ptthanoi', 'scrypt:32768:8:1$bAIhf8nBzfahT5fd$a88ec166a7a49b3ca0f271791f0d1bef60d0a6b411c4abaa16458e9e4dcfb02f72764a4d68b94696e6f4566e19b76b755b84ae4107b7dfe8d5442a27c07d4928', 'branch', 'PTT-HANOI'),
    ('pttkhanhhoa', 'scrypt:32768:8:1$ZKXtMsWZiz9YAv80$96ef92011c87c69a9e76ac4445fd8ad6f82fb189287e79868ed700b3fbfc439d102c4f9552524530b51e60349edf80bbeca9dcd7da547ad4074a9ed7a59bc6fb', 'branch', 'PTT-KHANHHOA'),
    ('pttlandmark81', 'scrypt:32768:8:1$rNTeWQnXmIqZ0vvI$e83bf163881875ff3d0256c85ee69d8335f83a02cbe65467e72e16a1e0846f9a866c2acdf6b5aa7e9c704a33fef4f1b17c0d7bd33e89e869baa1ff0ad3855910', 'branch', 'PTT-LANDMARK81'),
    ('pttnghean', 'scrypt:32768:8:1$EmrZ8RPgQZdWR3KF$a0d1d70b3606775423c8fd9b33a02959ac2860ceb2425b13da7ba5ab60090b213798982d6d3a6d5d53a3b29213f6ab9e0cbeba05f2149761a8b09e1bccc4c9e7', 'branch', 'PTT-NGHEAN'),
    ('pttngochoi', 'scrypt:32768:8:1$1WfEI3CF41K0m0Kn$a9e2635d48f662e11053760970dc768ef5518132d4cf3585ff58e74a0786333a624abe65705be8b617431660a10fa84f0450828288cd4c27ba6e5255881edb65', 'branch', 'PTT-NGOCHOI'),
    ('pttnhatrang', 'scrypt:32768:8:1$u4FYXvMgt0Uq3F6R$923bd0cd1b2e5ca3f1cb4dc8f1226970682f783ee3f4d2a9837c6f0a4c7c60186a2d55408016bf80d9a77318a285c164a4c32507fd30f0238e2668739956a694', 'branch', 'PTT-NHATRANG'),
    ('pttq7', 'scrypt:32768:8:1$KK03qqv0pKmhE0dH$fdc893be9e25999dc67f2fffe3b3d29c4b4609889843ede8374a6c243b68860d584ac2a5c11d7eceaa56d038fcd4d176613cd10f102abf4997285669165a6fae', 'branch', 'PTT-Q7'),
    ('pttq12', 'scrypt:32768:8:1$zYFJz3vrHrqctbSU$d43466aad88ec8d7bb096e10ec5b737778bdba98125292cc0d47f9c28d88acf17a2fed575fdd2e5485e930deb080fb5e60805ad505d3925d9d08086f30a42df9', 'branch', 'PTT-Q12'),
    ('ptttdh', 'scrypt:32768:8:1$bEmvE2z77bIPDJv7$4b9fb91445cafecfe0ba3e19fcfee4d7ab114861fc56cbaf4cd81cf6f6fb77da830ba37c4fcd35706fadb3fdabe3f8766cd8aaf7f7dd66c161b4718608dbcd93', 'branch', 'PTT-TDH'),
    ('xdvcantho', 'scrypt:32768:8:1$cOELqyrwVTLusMje$602e0899d6ca7aece592953b0279391c5bdbc8f46e81820dccd747fea4cc9f89e4c85931dbb02445530203a17c5f33440912029d6af915784be4188d4e5a1fed', 'branch', 'XDV-CANTHO'),
    ('xdvdanang', 'scrypt:32768:8:1$wbpVli1HGjJWvL3O$6639f575e50bfb1668da8ab705274d8cad2b8a8926adc905cc9ff05f4f7ecb30f13a7aaf110b8444237cc5157662368457cc9c2266850b4f953585591f850eb4', 'branch', 'XDV-DANANG'),
    ('xdvhanoi', 'scrypt:32768:8:1$PYgVQg2l0GDp0RTq$11a2ac045ff3323ac12af51f3e934f229ace1a55ce8c00848ee55c7f379f07d812c6804a9ada911c41a98899523309a22c82f882c8d7e0e9a14b86f5f2064865', 'branch', 'XDV-HANOI'),
    ('xdvkhanhhoa', 'scrypt:32768:8:1$t2Udzg0U3JlMOZk4$62250a7f49777d44eef03e9ad33ee290a39612c6ccfe9842ea0c10dd38bd7a087d5c101a5d11bcd1c8c55584ce7e218d5d6438c9617a1af327861e95f807433e', 'branch', 'XDV-KHANHHOA'),
    ('xdvnghean', 'scrypt:32768:8:1$cCqluMCIJR0Gfc24$ef48bb557eea1a3f149fefc9b3c829a49bdd682ad123826b818b4c13c69413c6ad1df1ba2d50de8d96756c371d1dbbf5be2ae343215c0eb058feb7463f66737d', 'branch', 'XDV-NGHEAN'),
    ('xdvq7', 'scrypt:32768:8:1$fPIw5OuNH2Tw3OaH$a47052a1d0a81d17fc83d62368c720051224e75dd72cbc4ea548a7afd59bafe4fc6cccbdde288f45ea5e997905658463073101edb477ec56b4e85998ccda382a', 'branch', 'XDV-Q7'),
    ('xdvq12', 'scrypt:32768:8:1$ghctsKQnOeYyeVql$37b191b009a5535e8ca15c64066f6fc25f75fad09a3ff4cc46862ef82be12f8c3eacb57cbacbfca8ed5a6e1bb2e981500c58dadac773dd861c478eb6ff506544', 'branch', 'XDV-Q12'),
    ('xdvthainguyen', 'scrypt:32768:8:1$qBldcJONkH8CKuiB$baa68caa7039a2ad953be7d265f71823a685e208db6f5a8b66221f3f4cdb3eb51fbdc0f3ee168e5e2c3daa1a482746e8e7063bb0187b38aae99267f7564e1b26', 'branch', 'XDV-THAINGUYEN')
''')

conn.commit()
conn.close()
print("✅ Đã tạo user admin và 20 chi nhánh với mật khẩu mã hóa.")
