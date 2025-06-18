# Bot Telegram Konversi File 🤖

Bot Telegram komprehensif untuk konversi dan manajemen file dengan fitur lengkap.

## Fitur Utama

### 🔄 File Conversion
- `/rekapgroup` - Rekap nama grup dan jumlah member 📸👥
- `/cv_txt_to_vcf` - Convert TXT ke VCF 📄➡️📇
- `/cv_vcf_to_txt` - Convert VCF ke TXT 📇➡️📄
- `/cv_xlsx_to_vcf` - Convert XLSX ke VCF 📊➡️📇
- `/txt2vcf` - Convert TXT ke VCF otomatis 📊➡️📇
- `/cvadminfile` - Kelola file admin 🗃️👩‍💼

### 📁 File Management
- `/renamectc` - Ganti nama kontak VCF ✏️📇
- `/renamefile` - Ganti nama file ✏️📝
- `/gabungtxt` - Gabung beberapa file TXT 📄🔗
- `/gabungvcf` - Gabung beberapa file VCF 📄🔗
- `/pecahfile` - Pecah file VCF jadi beberapa bagian 📂✂️
- `/pecahctc` - Pecah VCF sesuai jumlah kontak 📇➗
- `/addctc` - Tambah kontak ke VCF ➕📇
- `/delctc` - Hapus kontak dari VCF ❌📇
- `/hitungctc` - Hitung total kontak VCF 🔢📇
- `/totxt` - Simpan pesan ke file TXT 📝📤
- `/listgc` - Buat list group 🔢📇

### ⚙️ Other Menu
- `/reset_conversions` - Reset duplikat respon 🔧🔄
- `/fixbug` - Perbaiki bug menyeluruh 🛠️⚙️
- `/laporkanbug` - Laporkan bug 🐞📝

### ✨ Menu Owner
- `/adduser` - Tambah pengguna ➕👤
- `/deluser` - Hapus akses pengguna ❌👤
- `/totaluser` - Lihat jumlah pengguna 👀

## Setup dan Deployment

### 1. Setup Lokal

```bash
# Clone repository
git clone <repository-url>
cd telegram-file-converter-bot

# Install dependencies
pip install python-telegram-bot pandas openpyxl vobject

# Buat direktori temp
mkdir -p temp

# Jalankan bot
python main.py
```

### 2. Setup untuk GitHub Actions (Continuous Deployment)

#### A. Setup Repository Secrets

1. Buka repository di GitHub
2. Pergi ke Settings > Secrets and variables > Actions
3. Tambahkan secrets berikut:

```
BOT_TOKEN = 8131425355:AAFWisLEDBnXm-NsJq-6EgVh247n4o7NwOY
HEROKU_API_KEY = <your-heroku-api-key>
HEROKU_APP_NAME = <your-heroku-app-name>
HEROKU_EMAIL = <your-heroku-email>
```

#### B. Deploy ke Heroku

1. Buat akun di [Heroku](https://heroku.com)
2. Buat aplikasi baru
3. Dapatkan API Key dari Account Settings
4. Masukkan credentials ke GitHub Secrets

#### C. Deploy ke Railway (Alternatif)

1. Buat akun di [Railway](https://railway.app)
2. Connect dengan GitHub repository
3. Set environment variable `BOT_TOKEN`

### 3. Konfigurasi Bot

#### Update Owner ID
Edit file `bot/user_manager.py`:
```python
OWNER_USER_ID = YOUR_TELEGRAM_USER_ID  # Ganti dengan User ID Anda
```

Untuk mendapatkan User ID Anda:
1. Chat dengan bot @userinfobot di Telegram
2. Bot akan memberikan User ID Anda

## Struktur Project

```
├── bot/
│   ├── contact_utils.py     # Utilitas manipulasi kontak VCF
│   ├── database.py          # Operasi database SQLite
│   ├── file_converters.py   # Konverter berbagai format file
│   ├── file_managers.py     # Operasi manajemen file
│   ├── handlers.py          # Handler command Telegram
│   └── user_manager.py      # Manajemen akses user
├── utils/
│   └── helpers.py           # Helper utilities
├── .github/workflows/
│   └── deploy.yml           # GitHub Actions CI/CD
├── main.py                  # Entry point bot
├── Procfile                 # Konfigurasi Heroku
└── runtime.txt              # Versi Python untuk Heroku
```

## Cara Menggunakan

1. **Start Bot**: Kirim `/start` untuk memulai
2. **Lihat Menu**: Kirim `/menu` untuk melihat semua fitur
3. **Upload File**: Upload file yang ingin dikonversi
4. **Ikuti Instruksi**: Bot akan memberikan panduan langkah demi langkah

## Teknologi yang Digunakan

- **Python 3.11** - Bahasa pemrograman utama
- **python-telegram-bot** - Library untuk Telegram Bot API
- **pandas** - Manipulasi data untuk file Excel
- **openpyxl** - Membaca/menulis file Excel
- **vobject** - Parsing dan generasi file VCF
- **SQLite** - Database untuk manajemen user
- **GitHub Actions** - CI/CD deployment
- **Heroku/Railway** - Platform hosting

## Kontribusi

1. Fork repository
2. Buat branch fitur baru
3. Commit perubahan
4. Push ke branch
5. Buat Pull Request

## Lisensi

Project ini menggunakan lisensi MIT.

## Support

Jika mengalami masalah:
1. Gunakan command `/laporkanbug` di bot
2. Buat issue di GitHub repository
3. Contact developer

---

**Bot siap digunakan 24/7 dengan GitHub Actions deployment!** 🚀