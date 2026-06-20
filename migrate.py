"""
migrate.py — Jalankan skrip ini SEKALI secara manual untuk membuat tabel
dan mengisi data awal (admin default, dll) di database PostgreSQL kamu.

Cara pakai (di komputer lokal, BUKAN di Vercel):
    1. Set environment variable DATABASE_URL ke connection string Postgres kamu
       (dari Vercel Postgres / Neon / Supabase).
       export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
    2. pip install -r requirements.txt
    3. python migrate.py

Skrip ini AMAN dijalankan berulang kali — tidak akan menghapus data yang sudah ada.
"""
import os
import sys

if not (os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')):
    print("❌ ERROR: Set environment variable DATABASE_URL atau POSTGRES_URL dulu.")
    print('   Contoh: export DATABASE_URL="postgresql://user:pass@host:5432/dbname"')
    sys.exit(1)

from app import app, db
from app import _migrasi_db, seed_data

with app.app_context():
    print("⏳ Membuat tabel (jika belum ada)...")
    db.create_all()

    print("⏳ Menjalankan migrasi kolom tambahan...")
    _migrasi_db()

    print("⏳ Mengisi data awal (admin default, dll jika kosong)...")
    seed_data()

    print("✅ Migrasi selesai!")
    print("   Login default → username: admin / password: admin123")
    print("   (wajib diganti saat pertama login)")
