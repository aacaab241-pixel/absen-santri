from flask import Flask
from datetime import datetime
from extensions import db, login_manager
import socket, os, secrets

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///absen_santri.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu.'
    login_manager.login_message_category = 'warning'

    from routes.auth        import auth_bp
    from routes.dashboard   import dashboard_bp
    from routes.santri      import santri_bp
    from routes.acara       import acara_bp
    from routes.absensi     import absensi_bp
    from routes.rekap       import rekap_bp
    from routes.impor       import impor_bp
    from routes.kartu       import kartu_bp
    from routes.panduan     import panduan_bp
    from routes.pengaturan  import pengaturan_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(santri_bp)
    app.register_blueprint(acara_bp)
    app.register_blueprint(absensi_bp)
    app.register_blueprint(rekap_bp)
    app.register_blueprint(impor_bp)
    app.register_blueprint(kartu_bp)
    app.register_blueprint(panduan_bp)
    app.register_blueprint(pengaturan_bp)

    from context_processors import inject_globals
    inject_globals(app)

    with app.app_context():
        db.create_all()
        _migrasi_db()
        seed_data()
    return app


def _migrasi_db():
    """Tambah kolom baru tanpa menghapus data lama."""
    from sqlalchemy import text
    migrasi = [
        ('admin', 'must_change_password', 'INTEGER NOT NULL DEFAULT 0'),
        ('admin', 'dibuat',               "DATETIME DEFAULT (datetime('now'))"),
    ]
    with db.engine.connect() as conn:
        for tabel, kolom, definisi in migrasi:
            try:
                conn.execute(text(f'ALTER TABLE {tabel} ADD COLUMN {kolom} {definisi}'))
                conn.commit()
            except Exception:
                pass  # kolom sudah ada


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '0.0.0.0'


def seed_data():
    from models import Admin, Santri, Acara, Pengaturan
    from werkzeug.security import generate_password_hash

    # Admin default
    if not Admin.query.first():
        db.session.add(Admin(
            username='admin', email='admin@pesantren.id',
            nama='Admin Pesantren',
            password=generate_password_hash('admin123'),
            must_change_password=True
        ))

    # Pengaturan default
    defaults = {
        'nama_pesantren' : 'Pesantren Digital',
        'tagline'        : 'Sistem Absensi Santri',
        'logo_base64'    : '',   # kosong = pakai emoji 🕌
        'tahun'          : str(datetime.today().year),
    }
    for k, v in defaults.items():
        if not Pengaturan.query.filter_by(kunci=k).first():
            db.session.add(Pengaturan(kunci=k, nilai=v))

    # Santri & Acara contoh
    if not Santri.query.first():
        db.session.add_all([
            Santri(nis='PST2024001', nama='Ahmad Fauzi',    orang_tua='Bapak Hasan', alamat='Jl. Mawar No. 5, Semarang', kelas='Kelas 1A'),
            Santri(nis='PST2024002', nama='Muhammad Rizal', orang_tua='Bapak Andi',  alamat='Jl. Kenanga No. 12, Demak',  kelas='Kelas 1B'),
        ])
    if not Acara.query.first():
        db.session.add(Acara(
            nama='Pengajian Rutin', deskripsi='Pengajian rutin',
            tanggal=datetime.today().date(), jam_mulai='19:00',
            jam_selesai='21:00', batas_terlambat='19:15', status='buka'
        ))

    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    ip  = get_local_ip()
    print(f'\n  HP ini   : http://127.0.0.1:5000')
    print(f'  HP lain  : http://{ip}:5000')
    print(f'  Login    : admin / admin123  (wajib ganti saat pertama login)\n')
    app.run(host='0.0.0.0', port=5000, debug=False)
