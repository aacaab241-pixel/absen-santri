from extensions import db
from flask_login import UserMixin
from datetime import datetime
import qrcode
import io
import base64


class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    id                   = db.Column(db.Integer, primary_key=True)
    username             = db.Column(db.String(50), unique=True, nullable=False)
    email                = db.Column(db.String(100), unique=True, nullable=False)
    nama                 = db.Column(db.String(100), nullable=False)
    password             = db.Column(db.String(256), nullable=False)
    must_change_password = db.Column(db.Boolean, default=False, nullable=False)
    dibuat               = db.Column(db.DateTime, default=datetime.utcnow)


class Pengaturan(db.Model):
    """Konfigurasi pesantren: nama, logo, dll."""
    __tablename__ = 'pengaturan'
    id        = db.Column(db.Integer, primary_key=True)
    kunci     = db.Column(db.String(50), unique=True, nullable=False)
    nilai     = db.Column(db.Text, default='')

    @staticmethod
    def get(kunci, default=''):
        row = Pengaturan.query.filter_by(kunci=kunci).first()
        return row.nilai if row else default

    @staticmethod
    def set(kunci, nilai):
        row = Pengaturan.query.filter_by(kunci=kunci).first()
        if row:
            row.nilai = nilai
        else:
            db.session.add(Pengaturan(kunci=kunci, nilai=nilai))
        db.session.commit()


class Santri(db.Model):
    __tablename__ = 'santri'
    id        = db.Column(db.Integer, primary_key=True)
    nis       = db.Column(db.String(20), unique=True, nullable=False)
    nama      = db.Column(db.String(100), nullable=False)
    orang_tua = db.Column(db.String(100))
    alamat    = db.Column(db.Text)
    kelas     = db.Column(db.String(20))
    dibuat    = db.Column(db.DateTime, default=datetime.utcnow)

    absensi = db.relationship('Absensi', backref='santri', lazy=True, cascade='all, delete-orphan')

    def qr_base64(self):
        img = qrcode.make(self.nis)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return base64.b64encode(buf.getvalue()).decode()


class Acara(db.Model):
    __tablename__ = 'acara'
    id              = db.Column(db.Integer, primary_key=True)
    nama            = db.Column(db.String(100), nullable=False)
    deskripsi       = db.Column(db.Text)
    tanggal         = db.Column(db.Date, nullable=False)
    jam_mulai       = db.Column(db.String(5), nullable=False)
    jam_selesai     = db.Column(db.String(5), nullable=False)
    batas_terlambat = db.Column(db.String(5), nullable=False)
    status          = db.Column(db.String(10), default='tutup')
    dibuat          = db.Column(db.DateTime, default=datetime.utcnow)

    absensi = db.relationship('Absensi', backref='acara', lazy=True, cascade='all, delete-orphan')

    def jumlah_hadir(self):
        return Absensi.query.filter_by(acara_id=self.id).count()


class Absensi(db.Model):
    __tablename__ = 'absensi'
    id        = db.Column(db.Integer, primary_key=True)
    santri_id = db.Column(db.Integer, db.ForeignKey('santri.id'), nullable=False)
    acara_id  = db.Column(db.Integer, db.ForeignKey('acara.id'),  nullable=False)
    waktu     = db.Column(db.DateTime, default=datetime.utcnow)
    status    = db.Column(db.String(15))

    __table_args__ = (
        db.UniqueConstraint('santri_id', 'acara_id', name='uq_santri_acara'),
    )
