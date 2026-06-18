# 🕌 AbsenSantri — Sistem Absensi Pesantren Digital

Aplikasi absensi berbasis web (Flask + SQLite) yang dapat dijalankan di **Termux (Android)** maupun PC/laptop biasa.

---

## 📁 Struktur Project

```
absen_santri/
├── app.py                  ← Entry point utama
├── models.py               ← Model database (SQLAlchemy)
├── context_processors.py   ← Variabel global Jinja2
├── requirements.txt        ← Daftar library Python
├── setup_termux.sh         ← Skrip instalasi Termux
├── routes/
│   ├── auth.py             ← Login & logout
│   ├── dashboard.py        ← Halaman dashboard
│   ├── santri.py           ← Manajemen data santri
│   ├── acara.py            ← Manajemen acara
│   ├── absensi.py          ← Scan QR / input manual
│   ├── rekap.py            ← Rekap + ekspor Excel/PDF
│   └── impor.py            ← Import data dari Excel/CSV
├── templates/
│   ├── base.html           ← Layout utama (sidebar)
│   ├── login.html
│   ├── dashboard.html
│   ├── santri.html
│   ├── acara.html
│   ├── absensi.html
│   ├── rekap.html
│   ├── import.html
│   └── qr_modal.html
└── static/
    ├── css/style.css
    └── js/main.js
```

---

## 🚀 Cara Menjalankan di Termux (Android)

### Langkah 1 — Install Termux
Download **Termux** dari [F-Droid](https://f-droid.org/packages/com.termux/) (bukan Play Store).

### Langkah 2 — Copy project ke Termux
```bash
# Buat folder di home Termux
mkdir -p ~/absen_santri

# Copy semua file project ke folder tersebut
# (bisa via Airdrop, Bluetooth, USB, atau scp)
```

### Langkah 3 — Jalankan skrip instalasi
```bash
cd ~/absen_santri
bash setup_termux.sh
```

### Langkah 4 — Jalankan aplikasi
```bash
python app.py
```

### Langkah 5 — Buka di browser
- **HP sendiri:** `http://127.0.0.1:5000`
- **HP/PC lain (1 WiFi):**
  ```bash
  ifconfig | grep 'inet '
  # Catat IP, contoh: 192.168.1.5
  # Buka: http://192.168.1.5:5000
  ```

---

## 🔐 Login Default
| Field    | Value          |
|----------|----------------|
| Username | `admin`        |
| Password | `admin123`     |

---

## ✨ Fitur

| Fitur | Keterangan |
|---|---|
| 🔐 Login Admin | Autentikasi dengan username/email + password |
| 📊 Dashboard | Statistik santri, acara, absensi, grafik |
| 📅 Manajemen Acara | Tambah/edit/hapus, buka/tutup sesi |
| 👨‍🎓 Data Santri | CRUD lengkap + pagination + pencarian |
| 📱 QR Code | Generate QR otomatis dari NIS, print QR |
| 🔍 Scan Absensi | Scan via kamera (jsQR) atau input manual NIS |
| ✅ Status Kehadiran | Tepat waktu / terlambat otomatis |
| 📋 Rekap | Filter by acara/kelas/tanggal |
| 📊 Export Excel | File `.xlsx` berformat rapi |
| 📄 Export PDF | File `.pdf` dengan ReportLab |
| 📥 Import Excel/CSV | Validasi + preview sebelum simpan |
| 📋 Template Import | Download template Excel siap pakai |

---

## 🛠️ Cara Install Manual (Tanpa Script)

```bash
pkg update && pkg upgrade -y
pkg install python python-pip libjpeg-turbo libpng -y
pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug \
            "qrcode[pil]" openpyxl reportlab Pillow
```

---

## 🔧 Troubleshooting

**Error `pip install` gagal?**
```bash
pkg install clang libffi openssl -y
pip install --upgrade pip setuptools wheel
```

**Error `Pillow` tidak bisa install?**
```bash
pkg install libjpeg-turbo libpng zlib -y
pip install Pillow --no-cache-dir
```

**Kamera tidak bisa akses saat scan?**
- Pastikan browser diberi izin kamera
- Gunakan Chrome/Firefox di Android
- Atau gunakan mode **Input Manual NIS** sebagai alternatif

**Database error?**
```bash
cd ~/absen_santri
rm -f instance/absen_santri.db   # hapus DB lama
python app.py                     # buat ulang
```

---

## 📝 Catatan

- Database: **SQLite** (file `instance/absen_santri.db`) — tidak butuh server database
- Semua data tersimpan lokal di perangkat
- Untuk production, disarankan menggunakan WSGI server seperti `gunicorn`:
  ```bash
  pip install gunicorn
  gunicorn -w 2 -b 0.0.0.0:5000 "app:create_app()"
  ```
