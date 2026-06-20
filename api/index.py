# api/index.py — entry point untuk Vercel Python runtime.
# Vercel mendeteksi file ini lewat konfigurasi di vercel.json dan
# mengekspos variabel `app` (objek WSGI Flask) sebagai handler request.

import sys
import os

# Pastikan root project (satu level di atas folder api/) ada di sys.path
# supaya `import app`, `import models`, dll bisa ditemukan.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402  (import setelah path diatur, sengaja)

# Vercel's Python runtime akan memanggil `app` ini secara langsung
# sebagai WSGI callable.
