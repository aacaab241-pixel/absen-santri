# Panduan Deploy AbsenSantri ke Vercel + PostgreSQL

File-file di paket ini adalah **pengganti** untuk file dengan nama sama di
proyek aslimu. File yang TIDAK disertakan di sini (folder `templates/`,
`static/`, dan isi `routes/*.py`) **tidak perlu diubah** — salin apa adanya
dari proyek lama kamu.

## File yang diganti/ditambahkan
- `app.py` — diganti (logika koneksi DB & migrasi disesuaikan untuk serverless)
- `requirements.txt` — diganti (tambah driver Postgres, hapus gunicorn/waitress)
- `vercel.json` — baru (konfigurasi build & routing Vercel)
- `api/index.py` — baru (entry point WSGI yang dibaca Vercel)
- `migrate.py` — baru (skrip migrasi manual, dijalankan sekali)
- `.env.example` — baru (contoh environment variable)
- `extensions.py`, `models.py` — sama seperti asli, disertakan untuk lengkap

## File yang TIDAK berubah (pakai punya kamu yang lama)
- `context_processors.py`
- `routes/*.py` (semua isi route)
- `templates/*.html` (semua)
- `static/css/style.css`, `static/js/main.js`, `static/js/jsQR.js`

---

## Langkah Deploy

### 1. Siapkan database PostgreSQL
Pilih salah satu (semua punya free tier):
- **Vercel Postgres** (Storage tab di dashboard project Vercel kamu) — paling mudah karena env var otomatis terpasang
- **Neon** (neon.tech) — generous free tier
- **Supabase** (supabase.com)

Catat connection string-nya, formatnya:
`postgresql://user:password@host:5432/dbname`

### 2. Gabungkan file
Ambil semua file di paket ini dan timpa ke proyek `absen_santri/` kamu yang
lama. Struktur akhir harus seperti ini:

```
absen_santri/
├── api/
│   └── index.py          ← baru
├── routes/                ← punya kamu (tidak berubah)
├── templates/              ← punya kamu (tidak berubah)
├── static/                  ← punya kamu (tidak berubah)
├── app.py                ← diganti
├── extensions.py
├── models.py
├── context_processors.py  ← punya kamu (tidak berubah)
├── migrate.py             ← baru
├── requirements.txt       ← diganti
├── vercel.json            ← baru
└── .env.example           ← baru
```

### 3. Jalankan migrasi database (SEKALI, dari komputer kamu)
```bash
cd absen_santri
pip install -r requirements.txt
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
python migrate.py
```
Ini akan membuat semua tabel dan mengisi admin default
(`admin` / `admin123`).

### 4. Push ke GitHub
```bash
git init
git add .
git commit -m "Siap deploy ke Vercel"
git remote add origin <url-repo-github-kamu>
git push -u origin main
```

### 5. Import ke Vercel
1. Buka vercel.com → New Project → Import dari GitHub
2. Di langkah konfigurasi, tambahkan Environment Variables:
   - `DATABASE_URL` = connection string Postgres kamu
   - `SECRET_KEY` = string acak (boleh generate pakai `python -c "import secrets; print(secrets.token_hex(32))"`)
3. Klik Deploy

### 6. Setelah deploy
- Buka URL Vercel kamu, login dengan `admin` / `admin123`
- **Wajib ganti password** segera (sistem akan otomatis minta)

---

## ⚠️ Batasan yang Perlu Diketahui di Vercel (Free Tier)

1. **Timeout 10 detik per request.** Fitur "Unduh ZIP Semua Kartu Santri"
   (generate PNG untuk banyak santri sekaligus) berisiko timeout kalau
   jumlah santri banyak (kira-kira >30-50 santri, tergantung kompleksitas
   render). Kalau ini masalah, opsi: upgrade Vercel Pro (timeout lebih
   panjang) atau pertimbangkan platform non-serverless (Railway/Render).

2. **Tidak ada local file storage.** Logo pesantren sudah disimpan sebagai
   base64 di database (aman), tapi jangan tambah fitur yang menyimpan file
   ke disk lokal — di Vercel filesystem bersifat read-only kecuali `/tmp`
   yang hilang setiap request baru.

3. **Cold start.** Request pertama setelah idle beberapa menit akan sedikit
   lebih lambat karena fungsi serverless perlu "bangun" dulu.

4. **Koneksi database.** `pool_pre_ping=True` sudah diaktifkan di `app.py`
   supaya koneksi yang putus karena idle otomatis dicoba ulang — penting
   karena karakteristik serverless yang sering cold start.

5. **WebSocket / koneksi kamera real-time** (`getUserMedia` di
   `absensi.html`) tetap jalan normal karena itu murni di sisi browser,
   tidak melalui server — tidak terdampak migrasi ini.
