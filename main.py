#!/usr/bin/env python3
"""
Telegram Bot untuk Konversi dan Manajemen File
Dibuat untuk deployment berkelanjutan di GitHub
"""

import os
import sys
import asyncio
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bot.handlers import *
from bot.database import init_database

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token bot dari environment variable
BOT_TOKEN = "8131425355:AAFWisLEDBnXm-NsJq-6EgVh247n4o7NwOY"

async def setup_commands(application):
    """Setup bot commands untuk menu"""
    commands = [
        BotCommand("start", "Mulai menggunakan bot"),
        BotCommand("help", "Tampilkan bantuan"),
        BotCommand("menu", "Tampilkan semua menu"),
        
        # File Conversion
        BotCommand("rekapgroup", "Rekap nama grup dan jumlah member"),
        BotCommand("cv_txt_to_vcf", "Convert TXT ke VCF"),
        BotCommand("cv_vcf_to_txt", "Convert VCF ke TXT"),
        BotCommand("cv_xlsx_to_vcf", "Convert XLSX ke VCF"),
        BotCommand("txt2vcf", "Convert TXT ke VCF otomatis"),
        BotCommand("cvadminfile", "Kelola file admin"),
        
        # File Management
        BotCommand("renamectc", "Ganti nama kontak VCF"),
        BotCommand("renamefile", "Ganti nama file"),
        BotCommand("gabungtxt", "Gabung file TXT"),
        BotCommand("gabungvcf", "Gabung file VCF"),
        BotCommand("pecahfile", "Pecah file VCF"),
        BotCommand("pecahctc", "Pecah VCF sesuai jumlah kontak"),
        BotCommand("addctc", "Tambah kontak ke VCF"),
        BotCommand("delctc", "Hapus kontak dari VCF"),
        BotCommand("hitungctc", "Hitung total kontak VCF"),
        BotCommand("totxt", "Simpan pesan ke TXT"),
        BotCommand("listgc", "Buat list group"),
        
        # Other Menu
        BotCommand("reset_conversions", "Reset duplikat respon"),
        BotCommand("fixbug", "Perbaiki bug menyeluruh"),
        BotCommand("laporkanbug", "Laporkan bug"),
        
        # Owner Menu
        BotCommand("adduser", "Tambah pengguna"),
        BotCommand("deluser", "Hapus akses pengguna"),
        BotCommand("totaluser", "Lihat jumlah pengguna"),
    ]
    
    await application.bot.set_my_commands(commands)

def main():
    """Main function untuk menjalankan bot"""
    try:
        # Inisialisasi database
        init_database()
        
        # Buat aplikasi bot
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("menu", menu_command))
        
        # File Conversion handlers
        application.add_handler(CommandHandler("rekapgroup", rekap_group_command))
        application.add_handler(CommandHandler("cv_txt_to_vcf", cv_txt_to_vcf_command))
        application.add_handler(CommandHandler("cv_vcf_to_txt", cv_vcf_to_txt_command))
        application.add_handler(CommandHandler("cv_xlsx_to_vcf", cv_xlsx_to_vcf_command))
        application.add_handler(CommandHandler("txt2vcf", txt2vcf_command))
        application.add_handler(CommandHandler("cvadminfile", cv_admin_file_command))
        
        # File Management handlers
        application.add_handler(CommandHandler("renamectc", rename_ctc_command))
        application.add_handler(CommandHandler("renamefile", rename_file_command))
        application.add_handler(CommandHandler("gabungtxt", gabung_txt_command))
        application.add_handler(CommandHandler("gabungvcf", gabung_vcf_command))
        application.add_handler(CommandHandler("pecahfile", pecah_file_command))
        application.add_handler(CommandHandler("pecahctc", pecah_ctc_command))
        application.add_handler(CommandHandler("addctc", add_ctc_command))
        application.add_handler(CommandHandler("delctc", del_ctc_command))
        application.add_handler(CommandHandler("hitungctc", hitung_ctc_command))
        application.add_handler(CommandHandler("totxt", to_txt_command))
        application.add_handler(CommandHandler("listgc", list_gc_command))
        
        # Other handlers
        application.add_handler(CommandHandler("reset_conversions", reset_conversions_command))
        application.add_handler(CommandHandler("fixbug", fix_bug_command))
        application.add_handler(CommandHandler("laporkanbug", laporkan_bug_command))
        
        # Owner handlers
        application.add_handler(CommandHandler("adduser", add_user_command))
        application.add_handler(CommandHandler("deluser", del_user_command))
        application.add_handler(CommandHandler("totaluser", total_user_command))
        
        # Message handlers untuk file upload
        application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        # Start bot
        logger.info("Bot dimulai...")
        
        # Untuk development, gunakan polling
        application.run_polling(allowed_updates=Update.ALL_TYPES)
            
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
