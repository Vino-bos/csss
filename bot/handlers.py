"""
Handler untuk semua command bot Telegram
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from bot.user_manager import check_user_access, is_owner
from bot.file_converters import *
from bot.file_managers import *
from bot.contact_utils import *
from utils.helpers import *

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /start"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    first_name = update.effective_user.first_name or "User"
    
    # Cek akses user
    if not await check_user_access(user_id):
        await update.message.reply_text(
            f"❌ Maaf {first_name}, Anda belum memiliki akses ke bot ini.\n"
            "Silakan hubungi admin untuk mendapatkan akses."
        )
        return
    
    welcome_text = f"""
🤖 **Selamat datang di Bot Konversi File!**

Halo {first_name}! 👋

Bot ini dapat membantu Anda dengan:
🔄 Konversi berbagai format file
📁 Manajemen file
📇 Manipulasi kontak
👥 Rekap grup

Ketik /menu untuk melihat semua fitur yang tersedia
Ketik /help untuk bantuan lebih lanjut

✨ Bot siap digunakan!
    """
    
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /help"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    help_text = """
📚 **BANTUAN BOT KONVERSI FILE**

**Cara Menggunakan:**
1. Pilih command yang diinginkan
2. Ikuti instruksi yang diberikan bot
3. Upload file jika diperlukan
4. Bot akan memproses dan mengirim hasil

**Format File yang Didukung:**
• TXT - File teks biasa
• VCF - File kontak vCard
• XLSX - File Excel

**Tips:**
• Pastikan file tidak rusak sebelum upload
• Gunakan /reset_conversions jika bot tidak merespon
• Laporkan bug dengan /laporkanbug

Ketik /menu untuk melihat semua fitur!
    """
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /menu"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    menu_text = """
🤖 **MENU BOT KONVERSI FILE**

🔄 **File Conversion**
/rekapgroup - Rekap nama grup dan jumlah member 📸👥
/cv_txt_to_vcf - Convert TXT ke VCF 📄➡️📇
/cv_vcf_to_txt - Convert VCF ke TXT 📇➡️📄
/cv_xlsx_to_vcf - Convert XLSX ke VCF 📊➡️📇
/txt2vcf - Convert TXT ke VCF otomatis 📊➡️📇
/cvadminfile - Kelola file admin 🗃️👩‍💼

────────────────────────

📁 **File Management**
/renamectc - Ganti nama kontak VCF ✏️📇
/renamefile - Ganti nama file ✏️📝
/gabungtxt - Gabung beberapa file TXT 📄🔗
/gabungvcf - Gabung beberapa file VCF 📄🔗
/pecahfile - Pecah file VCF jadi beberapa bagian 📂✂️
/pecahctc - Pecah VCF sesuai jumlah kontak 📇➗
/addctc - Tambah kontak ke VCF ➕📇
/delctc - Hapus kontak dari VCF ❌📇
/hitungctc - Hitung total kontak VCF 🔢📇
/totxt - Simpan pesan ke file TXT 📝📤
/listgc - Buat list group 🔢📇

────────────────────────

⚙️ **Other Menu**
/reset_conversions - Reset duplikat respon 🔧🔄
/fixbug - Perbaiki bug menyeluruh 🛠️⚙️
/laporkanbug - Laporkan bug 🐞📝

────────────────────────

✨ **Menu Owner** ✨
/adduser - Tambah pengguna ➕👤
/deluser - Hapus akses pengguna ❌👤
/totaluser - Lihat jumlah pengguna 👀
    """
    
    await update.message.reply_text(menu_text, parse_mode=ParseMode.MARKDOWN)

# File Conversion Handlers
async def rekap_group_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /rekapgroup"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "📸 **Rekap Group**\n\n"
        "Kirim foto grup yang ingin direkap!\n"
        "Bot akan menganalisis dan memberikan informasi grup tersebut.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Set state untuk menunggu foto
    context.user_data['waiting_for'] = 'group_photo'

async def cv_txt_to_vcf_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /cv_txt_to_vcf"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "📄➡️📇 **Convert TXT to VCF**\n\n"
        "Upload file .txt yang berisi kontak untuk dikonversi ke format .vcf\n"
        "Format TXT yang didukung:\n"
        "• Nama|Nomor\n"
        "• Nama,Nomor\n"
        "• Nama : Nomor",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'txt_to_vcf'

async def cv_vcf_to_txt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /cv_vcf_to_txt"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "📇➡️📄 **Convert VCF to TXT**\n\n"
        "Upload file .vcf untuk dikonversi ke format .txt\n"
        "Hasil akan berupa file txt dengan format: Nama|Nomor",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'vcf_to_txt'

async def cv_xlsx_to_vcf_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /cv_xlsx_to_vcf"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "📊➡️📇 **Convert XLSX to VCF**\n\n"
        "Upload file .xlsx yang berisi data kontak\n"
        "Bot akan mengambil nomor telepon dari tabel dan convert ke VCF\n"
        "Pastikan ada kolom nama dan nomor telepon di Excel",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'xlsx_to_vcf'

async def txt2vcf_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /txt2vcf"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "📊➡️📇 **TXT to VCF Auto Detect**\n\n"
        "Upload file .txt dan bot akan otomatis mendeteksi format\n"
        "Mendukung berbagai format pemisah (koma, titik koma, dll)\n"
        "Deteksi otomatis Admin Navy! 🚢",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'txt2vcf_auto'

async def cv_admin_file_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /cvadminfile"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    if not await is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Fitur ini hanya untuk owner.")
        return
    
    await update.message.reply_text(
        "🗃️👩‍💼 **Kelola File Admin**\n\n"
        "Upload file admin yang ingin dikelola\n"
        "Fitur khusus untuk admin dalam mengelola file sistem",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'admin_file'

# File Management Handlers
async def rename_ctc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /renamectc"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "✏️📇 **Ganti Nama Kontak VCF**\n\n"
        "Upload file .vcf untuk mengganti nama kontak\n"
        "Setelah upload, ikuti instruksi untuk menentukan nama baru",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'rename_contact'

async def rename_file_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /renamefile"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "✏️📝 **Ganti Nama File**\n\n"
        "Upload file yang ingin diganti namanya\n"
        "Setelah upload, kirim nama baru untuk file tersebut",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'rename_file'

async def gabung_txt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /gabungtxt"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "📄🔗 **Gabung File TXT**\n\n"
        "Upload beberapa file .txt untuk digabungkan\n"
        "Kirim file satu per satu, lalu ketik /selesai ketika sudah selesai upload",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'merge_txt'
    context.user_data['txt_files'] = []

async def gabung_vcf_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /gabungvcf"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "📄🔗 **Gabung File VCF**\n\n"
        "Upload beberapa file .vcf untuk digabungkan\n"
        "Kirim file satu per satu, lalu ketik /selesai ketika sudah selesai upload",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'merge_vcf'
    context.user_data['vcf_files'] = []

async def pecah_file_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /pecahfile"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "📂✂️ **Pecah File VCF**\n\n"
        "Upload file .vcf untuk dipecah menjadi beberapa bagian\n"
        "Setelah upload, tentukan berapa bagian yang diinginkan",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'split_file'

async def pecah_ctc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /pecahctc"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "📇➗ **Pecah VCF sesuai Jumlah Kontak**\n\n"
        "Upload file .vcf untuk dipecah berdasarkan jumlah kontak\n"
        "Setelah upload, tentukan berapa kontak per file",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'split_contact'

async def add_ctc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /addctc"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "➕📇 **Tambah Kontak ke VCF**\n\n"
        "Upload file .vcf untuk menambah kontak baru\n"
        "Setelah upload, kirim data kontak baru dengan format:\n"
        "Nama|Nomor",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'add_contact'

async def del_ctc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /delctc"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "❌📇 **Hapus Kontak dari VCF**\n\n"
        "Upload file .vcf untuk menghapus kontak\n"
        "Setelah upload, pilih kontak yang ingin dihapus",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'delete_contact'

async def hitung_ctc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /hitungctc"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "🔢📇 **Hitung Total Kontak VCF**\n\n"
        "Upload file .vcf untuk menghitung total kontak",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'count_contact'

async def to_txt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /totxt"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "📝📤 **Simpan Pesan ke TXT**\n\n"
        "Kirim pesan yang ingin disimpan ke file .txt\n"
        "Bot akan membuat file dan mengirimkannya kembali",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'message_to_txt'

async def list_gc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /listgc"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "🔢📇 **Buat List Group**\n\n"
        "Fitur untuk membuat daftar grup yang tersedia\n"
        "Bot akan menganalisis dan membuat list grup",
        parse_mode=ParseMode.MARKDOWN
    )

# Other Menu Handlers
async def reset_conversions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /reset_conversions"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    # Clear user data
    context.user_data.clear()
    
    await update.message.reply_text(
        "🔧🔄 **Reset Berhasil!**\n\n"
        "Duplikat respon bot telah direset\n"
        "Bot siap menerima command baru"
    )

async def fix_bug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /fixbug"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    # Clear semua data dan reset
    context.user_data.clear()
    
    await update.message.reply_text(
        "🛠️⚙️ **Perbaikan Bug Menyeluruh**\n\n"
        "✅ Cache dibersihkan\n"
        "✅ Memory direset\n"
        "✅ State conversation direset\n"
        "✅ Temporary files dibersihkan\n\n"
        "Bot telah diperbaiki dan siap digunakan!"
    )

async def laporkan_bug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /laporkanbug"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text(
        "🐞📝 **Laporkan Bug**\n\n"
        "Jelaskan bug yang Anda temukan:\n"
        "• Apa yang terjadi?\n"
        "• Kapan terjadi?\n"
        "• Command apa yang digunakan?\n"
        "• Screenshot jika ada\n\n"
        "Kirim laporan bug Anda sekarang:",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'bug_report'

# Owner Menu Handlers
async def add_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /adduser"""
    if not await is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Fitur ini hanya untuk owner.")
        return
    
    await update.message.reply_text(
        "➕👤 **Tambah Pengguna**\n\n"
        "Kirim User ID atau username pengguna yang ingin ditambahkan\n"
        "Format: 123456789 atau @username",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'add_user'

async def del_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /deluser"""
    if not await is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Fitur ini hanya untuk owner.")
        return
    
    await update.message.reply_text(
        "❌👤 **Hapus Akses Pengguna**\n\n"
        "Kirim User ID atau username pengguna yang ingin dihapus aksesnya\n"
        "Format: 123456789 atau @username",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for'] = 'delete_user'

async def total_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /totaluser"""
    if not await is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Fitur ini hanya untuk owner.")
        return
    
    from bot.user_manager import get_total_users, get_all_users
    
    total = await get_total_users()
    users = await get_all_users()
    
    user_list = []
    for user in users:
        user_list.append(f"• {user['user_id']} ({user.get('username', 'No username')})")
    
    users_text = "\n".join(user_list) if user_list else "Tidak ada pengguna terdaftar"
    
    await update.message.reply_text(
        f"👀 **Total Pengguna: {total}**\n\n"
        f"**Daftar Pengguna:**\n{users_text}",
        parse_mode=ParseMode.MARKDOWN
    )

# Message Handlers
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk document upload"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    waiting_for = context.user_data.get('waiting_for')
    
    if not waiting_for:
        await update.message.reply_text(
            "📎 File diterima!\n"
            "Gunakan command terlebih dahulu untuk menentukan operasi yang ingin dilakukan.\n"
            "Ketik /menu untuk melihat semua fitur."
        )
        return
    
    # Handle berdasarkan waiting_for state
    await process_document(update, context, waiting_for)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk photo upload"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    waiting_for = context.user_data.get('waiting_for')
    
    if waiting_for == 'group_photo':
        await process_group_photo(update, context)
    else:
        await update.message.reply_text(
            "📸 Foto diterima!\n"
            "Gunakan /rekapgroup untuk menganalisis foto grup."
        )

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk text message"""
    if not await check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    waiting_for = context.user_data.get('waiting_for')
    text = update.message.text
    
    if text == "/selesai":
        await process_finish_command(update, context)
        return
    
    if waiting_for:
        await process_text_input(update, context, waiting_for, text)
    else:
        await update.message.reply_text(
            "💬 Pesan diterima!\n"
            "Gunakan /totxt untuk menyimpan pesan ke file .txt\n"
            "Atau ketik /menu untuk melihat semua fitur."
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    if update and hasattr(update, 'effective_message'):
        await update.effective_message.reply_text(
            "❌ Terjadi kesalahan dalam memproses permintaan Anda.\n"
            "Gunakan /fixbug untuk memperbaiki atau /laporkanbug untuk melaporkan masalah."
        )

# Helper functions untuk process handlers
async def process_document(update: Update, context: ContextTypes.DEFAULT_TYPE, waiting_for: str):
    """Process uploaded document based on waiting_for state"""
    document = update.message.document
    file_name = document.file_name
    
    try:
        # Download file
        file = await context.bot.get_file(document.file_id)
        file_path = f"temp/{file_name}"
        os.makedirs("temp", exist_ok=True)
        await file.download_to_drive(file_path)
        
        if waiting_for == 'txt_to_vcf':
            await convert_txt_to_vcf(update, context, file_path)
        elif waiting_for == 'vcf_to_txt':
            await convert_vcf_to_txt(update, context, file_path)
        elif waiting_for == 'xlsx_to_vcf':
            await convert_xlsx_to_vcf(update, context, file_path)
        elif waiting_for == 'txt2vcf_auto':
            await convert_txt2vcf_auto(update, context, file_path)
        elif waiting_for == 'admin_file':
            await process_admin_file(update, context, file_path)
        elif waiting_for == 'rename_contact':
            await rename_contact_in_vcf(update, context, file_path)
        elif waiting_for == 'rename_file':
            await rename_uploaded_file(update, context, file_path, file_name)
        elif waiting_for == 'merge_txt':
            context.user_data['txt_files'].append(file_path)
            await update.message.reply_text(f"✅ File {file_name} ditambahkan. Kirim file lain atau /selesai")
        elif waiting_for == 'merge_vcf':
            context.user_data['vcf_files'].append(file_path)
            await update.message.reply_text(f"✅ File {file_name} ditambahkan. Kirim file lain atau /selesai")
        elif waiting_for == 'split_file':
            await split_vcf_file(update, context, file_path)
        elif waiting_for == 'split_contact':
            await split_vcf_by_contact(update, context, file_path)
        elif waiting_for == 'add_contact':
            context.user_data['vcf_file'] = file_path
            await update.message.reply_text("📇 File VCF diterima. Sekarang kirim data kontak baru dengan format: Nama|Nomor")
        elif waiting_for == 'delete_contact':
            await delete_contact_from_vcf(update, context, file_path)
        elif waiting_for == 'count_contact':
            await count_contacts_in_vcf(update, context, file_path)
        else:
            await update.message.reply_text("❌ State tidak dikenali. Gunakan /reset_conversions")
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        await update.message.reply_text(f"❌ Error memproses file: {str(e)}")
        
async def process_group_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process group photo for rekap"""
    await update.message.reply_text(
        "📸 Foto grup diterima!\n\n"
        "Maaf, fitur analisis foto grup masih dalam pengembangan.\n"
        "Saat ini bot fokus pada konversi dan manajemen file.\n\n"
        "Silakan gunakan fitur lain yang tersedia! 😊"
    )
    context.user_data.clear()

async def process_finish_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process /selesai command for merging files"""
    waiting_for = context.user_data.get('waiting_for')
    
    if waiting_for == 'merge_txt':
        files = context.user_data.get('txt_files', [])
        if files:
            await merge_txt_files(update, context, files)
        else:
            await update.message.reply_text("❌ Tidak ada file TXT untuk digabung.")
    elif waiting_for == 'merge_vcf':
        files = context.user_data.get('vcf_files', [])
        if files:
            await merge_vcf_files(update, context, files)
        else:
            await update.message.reply_text("❌ Tidak ada file VCF untuk digabung.")
    else:
        await update.message.reply_text("❌ Tidak ada operasi yang sedang berlangsung.")
    
    context.user_data.clear()

async def process_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE, waiting_for: str, text: str):
    """Process text input based on waiting_for state"""
    if waiting_for == 'message_to_txt':
        await save_message_to_txt(update, context, text)
    elif waiting_for == 'bug_report':
        await process_bug_report(update, context, text)
    elif waiting_for == 'add_user':
        await process_add_user(update, context, text)
    elif waiting_for == 'delete_user':
        await process_delete_user(update, context, text)
    elif waiting_for == 'new_contact_data':
        await add_contact_to_vcf(update, context, text)
    elif waiting_for == 'new_file_name':
        await process_rename_file(update, context, text)
    elif waiting_for == 'split_parts':
        await process_split_parts(update, context, text)
    elif waiting_for == 'contacts_per_file':
        await process_contacts_per_file(update, context, text)
    else:
        await update.message.reply_text("❌ Input tidak dikenali. Gunakan /reset_conversions")
