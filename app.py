from flask import Flask, jsonify
from datetime import datetime
from extensions import db, login_manager
import os, secrets

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _get_database_uri():
    """
    Ambil URI database dari environment variable.
    Vercel Postgres / Neon / Supabase biasanya menyediakan POSTGRES_URL atau DATABASE_URL.
    Fallback ke SQLite untuk pengembangan lokal (misal di Termux).
    """
    uri = (
        os.environ.get('POSTGRES_URL')
        or os.environ.get('DATABASE_URL')
        or os.environ.get('POSTGRES_PRISMA_URL')
    )
    if uri:
        if uri.startswith('postgres://'):
            uri = uri.replace('postgres://', 'postgresql://', 1)
        return uri
    return 'sqlite:///absen_santri.db'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    app.config['SQLALCHEMY_DATABASE_URI'] = _get_database_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }
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

    @app.context_processor
    def _inject_globals():
        from models import Pengaturan, Acara
        from flask_login import current_user

        nama_pesantren = Pengaturan.get('nama_pesantren', 'Pesantren Digital')
        tagline        = Pengaturan.get('tagline', 'Sistem Absensi Santri')
        logo_base64    = Pengaturan.get('logo_base64', '')

        acara_buka_count = 0
        if current_user.is_authenticated:
            try:
                acara_buka_count = Acara.query.filter_by(status='buka').count()
            except Exception:
                acara_buka_count = 0

        return dict(
            nama_pesantren=nama_pesantren,
            tagline=tagline,
            logo_base64=logo_base64,
            acara_buka_count=acara_buka_count,
        )

    # ── ROUTE SETUP MANUAL ──────────────────────────────────────────
    # Buka URL https://domain-kamu.vercel.app/setup di browser untuk
    # membuat tabel + admin default secara manual. AMAN dijalankan
    # berulang kali (tidak menghapus data yang sudah ada).
    @app.route('/setup')
    def _setup_route():
        try:
            with app.app_context():
                db.create_all()
                _migrasi_db()
                seed_data()
            return jsonify(
                ok=True,
                pesan='Setup berhasil! Tabel dan admin default sudah dibuat.',
                login='username: admin / password: admin123 (wajib ganti saat login)'
            )
        except Exception as e:
            import traceback
            return jsonify(
                ok=False,
                error=str(e),
                error_type=type(e).__name__,
                traceback=traceback.format_exc()
            ), 500

    # Tetap coba auto-migrate diam-diam jika env var di-set (tidak wajib)
    if os.environ.get('AUTO_MIGRATE_ON_BOOT', '').lower() in ('1', 'true', 'yes'):
        try:
            with app.app_context():
                db.create_all()
                _migrasi_db()
                seed_data()
        except Exception:
            pass  # biarkan, bisa di-trigger manual lewat /setup

    return app


def _migrasi_db():
    """Tambah kolom baru tanpa menghapus data lama (aman dijalankan berulang)."""
    from sqlalchemy import text, inspect
    migrasi = [
        ('admin', 'must_change_password', 'BOOLEAN NOT NULL DEFAULT FALSE'),
        ('admin', 'dibuat',               'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
    ]
    inspector = inspect(db.engine)
    with db.engine.connect() as conn:
        for tabel, kolom, definisi in migrasi:
            existing_cols = [c['name'] for c in inspector.get_columns(tabel)] if tabel in inspector.get_table_names() else []
            if kolom in existing_cols:
                continue
            try:
                conn.execute(text(f'ALTER TABLE {tabel} ADD COLUMN {kolom} {definisi}'))
                conn.commit()
            except Exception:
                pass


def seed_data():
    from models import Admin, Santri, Acara, Pengaturan
    from werkzeug.security import generate_password_hash

    if not Admin.query.first():
        db.session.add(Admin(
            username='admin', email='admin@pesantren.id',
            nama='Admin Pesantren',
            password=generate_password_hash('admin123'),
            must_change_password=True
        ))

    defaults = {
        'nama_pesantren' : 'Pesantren Digital',
        'tagline'        : 'Sistem Absensi Santri',
        'logo_base64'    : '',
        'tahun'          : str(datetime.today().year),
    }
    for k, v in defaults.items():
        if not Pengaturan.query.filter_by(kunci=k).first():
            db.session.add(Pengaturan(kunci=k, nilai=v))

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


app = create_app()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        _migrasi_db()
        seed_data()

    import socket
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return '0.0.0.0'

    ip = get_local_ip()
    print(f'\n  HP ini   : http://127.0.0.1:5000')
    print(f'  HP lain  : http://{ip}:5000')
    print(f'  Login    : admin / admin123  (wajib ganti saat pertama login)\n')
    app.run(host='0.0.0.0', port=5000, debug=False)
