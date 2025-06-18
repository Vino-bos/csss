"""
File management operations
"""

import os
import shutil
import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.helpers import cleanup_temp_file, send_document_to_user

logger = logging.getLogger(__name__)

async def rename_contact_in_vcf(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    """Rename contacts in VCF file"""
    try:
        await update.message.reply_text("✏️ File VCF diterima. Kirim nama baru untuk kontak (format: NamaLama|NamaBaru)")
        context.user_data['vcf_file'] = file_path
        context.user_data['waiting_for'] = 'new_contact_name'
        
    except Exception as e:
        logger.error(f"Error in rename contact: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def rename_uploaded_file(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str, original_name: str):
    """Rename uploaded file"""
    try:
        await update.message.reply_text(f"✏️ File '{original_name}' diterima. Kirim nama baru untuk file (tanpa ekstensi):")
        context.user_data['file_path'] = file_path
        context.user_data['original_name'] = original_name
        context.user_data['waiting_for'] = 'new_file_name'
        
    except Exception as e:
        logger.error(f"Error in rename file: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def process_rename_file(update: Update, context: ContextTypes.DEFAULT_TYPE, new_name: str):
    """Process file rename with new name"""
    try:
        file_path = context.user_data.get('file_path')
        original_name = context.user_data.get('original_name')
        
        if not file_path or not original_name:
            await update.message.reply_text("❌ Data file tidak ditemukan. Silakan upload ulang.")
            return
        
        # Get file extension
        file_ext = os.path.splitext(original_name)[1]
        new_filename = f"{new_name}{file_ext}"
        
        # Create new file path
        new_file_path = os.path.join(os.path.dirname(file_path), new_filename)
        
        # Rename file
        shutil.move(file_path, new_file_path)
        
        # Send renamed file to user
        await send_document_to_user(update, new_file_path, 
                                  f"✅ File berhasil diubah namanya!\n"
                                  f"📝 Nama lama: {original_name}\n"
                                  f"📝 Nama baru: {new_filename}")
        
        # Cleanup
        await cleanup_temp_file(new_file_path)
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Error renaming file: {e}")
        await update.message.reply_text(f"❌ Error mengubah nama file: {str(e)}")

async def merge_txt_files(update: Update, context: ContextTypes.DEFAULT_TYPE, file_paths: list):
    """Merge multiple TXT files"""
    try:
        await update.message.reply_text("🔗 Menggabungkan file TXT...")
        
        merged_content = []
        file_count = 0
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        merged_content.append(f"=== File {file_count + 1}: {os.path.basename(file_path)} ===")
                        merged_content.append(content)
                        merged_content.append("")  # Empty line separator
                        file_count += 1
        
        if not merged_content:
            await update.message.reply_text("❌ Tidak ada konten yang dapat digabungkan.")
            return
        
        # Create merged file
        output_file = "temp/merged_files.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(merged_content))
        
        # Send result to user
        await send_document_to_user(update, output_file, 
                                  f"✅ Berhasil menggabungkan {file_count} file TXT!")
        
        # Cleanup
        for file_path in file_paths:
            await cleanup_temp_file(file_path)
        await cleanup_temp_file(output_file)
        
    except Exception as e:
        logger.error(f"Error merging TXT files: {e}")
        await update.message.reply_text(f"❌ Error menggabungkan file: {str(e)}")

async def merge_vcf_files(update: Update, context: ContextTypes.DEFAULT_TYPE, file_paths: list):
    """Merge multiple VCF files"""
    try:
        await update.message.reply_text("🔗 Menggabungkan file VCF...")
        
        merged_vcards = []
        total_contacts = 0
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        # Count vcards in this file
                        vcard_count = content.count('BEGIN:VCARD')
                        total_contacts += vcard_count
                        merged_vcards.append(content)
        
        if not merged_vcards:
            await update.message.reply_text("❌ Tidak ada kontak yang dapat digabungkan.")
            return
        
        # Create merged VCF file
        output_file = "temp/merged_contacts.vcf"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(merged_vcards))
        
        # Send result to user
        await send_document_to_user(update, output_file, 
                                  f"✅ Berhasil menggabungkan {len(file_paths)} file VCF!\n"
                                  f"📇 Total kontak: {total_contacts}")
        
        # Cleanup
        for file_path in file_paths:
            await cleanup_temp_file(file_path)
        await cleanup_temp_file(output_file)
        
    except Exception as e:
        logger.error(f"Error merging VCF files: {e}")
        await update.message.reply_text(f"❌ Error menggabungkan file: {str(e)}")

async def split_vcf_file(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    """Split VCF file into multiple parts"""
    try:
        await update.message.reply_text("📂 File VCF diterima. Kirim jumlah bagian yang diinginkan (angka):")
        context.user_data['vcf_file'] = file_path
        context.user_data['waiting_for'] = 'split_parts'
        
    except Exception as e:
        logger.error(f"Error in split VCF: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def process_split_parts(update: Update, context: ContextTypes.DEFAULT_TYPE, parts_text: str):
    """Process VCF file splitting by parts"""
    try:
        parts = int(parts_text.strip())
        if parts < 2:
            await update.message.reply_text("❌ Jumlah bagian harus minimal 2.")
            return
        
        file_path = context.user_data.get('vcf_file')
        if not file_path:
            await update.message.reply_text("❌ File VCF tidak ditemukan. Silakan upload ulang.")
            return
        
        await update.message.reply_text(f"✂️ Memecah file VCF menjadi {parts} bagian...")
        
        # Read VCF file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into individual vcards
        vcards = []
        current_vcard = []
        
        for line in content.split('\n'):
            if line.strip() == 'BEGIN:VCARD':
                if current_vcard:
                    vcards.append('\n'.join(current_vcard))
                current_vcard = [line]
            else:
                current_vcard.append(line)
        
        if current_vcard:
            vcards.append('\n'.join(current_vcard))
        
        if len(vcards) < parts:
            await update.message.reply_text(f"❌ File hanya memiliki {len(vcards)} kontak, tidak dapat dipecah menjadi {parts} bagian.")
            return
        
        # Calculate contacts per part
        contacts_per_part = len(vcards) // parts
        remainder = len(vcards) % parts
        
        # Create split files
        output_files = []
        start_idx = 0
        
        for i in range(parts):
            end_idx = start_idx + contacts_per_part
            if i < remainder:
                end_idx += 1
            
            part_vcards = vcards[start_idx:end_idx]
            part_content = '\n\n'.join(part_vcards)
            
            output_file = f"temp/split_part_{i+1}.vcf"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(part_content)
            
            output_files.append(output_file)
            start_idx = end_idx
        
        # Send all parts to user
        await update.message.reply_text(f"✅ File berhasil dipecah menjadi {parts} bagian!")
        
        for i, output_file in enumerate(output_files):
            part_contacts = len([line for line in open(output_file, 'r').read().split('\n') if line.strip() == 'BEGIN:VCARD'])
            await send_document_to_user(update, output_file, f"📂 Bagian {i+1}/{parts} ({part_contacts} kontak)")
        
        # Cleanup
        await cleanup_temp_file(file_path)
        for output_file in output_files:
            await cleanup_temp_file(output_file)
        context.user_data.clear()
        
    except ValueError:
        await update.message.reply_text("❌ Masukkan angka yang valid untuk jumlah bagian.")
    except Exception as e:
        logger.error(f"Error splitting VCF by parts: {e}")
        await update.message.reply_text(f"❌ Error memecah file: {str(e)}")

async def split_vcf_by_contact(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    """Split VCF file by contact count"""
    try:
        await update.message.reply_text("📇 File VCF diterima. Kirim jumlah kontak per file yang diinginkan:")
        context.user_data['vcf_file'] = file_path
        context.user_data['waiting_for'] = 'contacts_per_file'
        
    except Exception as e:
        logger.error(f"Error in split VCF by contact: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def process_contacts_per_file(update: Update, context: ContextTypes.DEFAULT_TYPE, contacts_text: str):
    """Process VCF file splitting by contact count"""
    try:
        contacts_per_file = int(contacts_text.strip())
        if contacts_per_file < 1:
            await update.message.reply_text("❌ Jumlah kontak per file harus minimal 1.")
            return
        
        file_path = context.user_data.get('vcf_file')
        if not file_path:
            await update.message.reply_text("❌ File VCF tidak ditemukan. Silakan upload ulang.")
            return
        
        await update.message.reply_text(f"📇 Memecah file VCF dengan {contacts_per_file} kontak per file...")
        
        # Read VCF file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into individual vcards
        vcards = []
        current_vcard = []
        
        for line in content.split('\n'):
            if line.strip() == 'BEGIN:VCARD':
                if current_vcard:
                    vcards.append('\n'.join(current_vcard))
                current_vcard = [line]
            else:
                current_vcard.append(line)
        
        if current_vcard:
            vcards.append('\n'.join(current_vcard))
        
        total_contacts = len(vcards)
        total_files = (total_contacts + contacts_per_file - 1) // contacts_per_file
        
        # Create split files
        output_files = []
        
        for i in range(0, total_contacts, contacts_per_file):
            end_idx = min(i + contacts_per_file, total_contacts)
            part_vcards = vcards[i:end_idx]
            part_content = '\n\n'.join(part_vcards)
            
            file_num = (i // contacts_per_file) + 1
            output_file = f"temp/contacts_{file_num}.vcf"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(part_content)
            
            output_files.append(output_file)
        
        # Send all files to user
        await update.message.reply_text(f"✅ File berhasil dipecah menjadi {total_files} file!")
        
        for i, output_file in enumerate(output_files):
            actual_contacts = len([line for line in open(output_file, 'r').read().split('\n') if line.strip() == 'BEGIN:VCARD'])
            await send_document_to_user(update, output_file, f"📇 File {i+1}/{total_files} ({actual_contacts} kontak)")
        
        # Cleanup
        await cleanup_temp_file(file_path)
        for output_file in output_files:
            await cleanup_temp_file(output_file)
        context.user_data.clear()
        
    except ValueError:
        await update.message.reply_text("❌ Masukkan angka yang valid untuk jumlah kontak per file.")
    except Exception as e:
        logger.error(f"Error splitting VCF by contact count: {e}")
        await update.message.reply_text(f"❌ Error memecah file: {str(e)}")

async def save_message_to_txt(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
    """Save message to TXT file"""
    try:
        await update.message.reply_text("📝 Menyimpan pesan ke file TXT...")
        
        # Create TXT file with message
        output_file = "temp/saved_message.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Pesan dari: {update.effective_user.first_name}\n")
            f.write(f"Username: @{update.effective_user.username}\n")
            f.write(f"User ID: {update.effective_user.id}\n")
            f.write(f"Tanggal: {update.message.date}\n")
            f.write("=" * 50 + "\n")
            f.write(message_text)
        
        # Send file to user
        await send_document_to_user(update, output_file, 
                                  "✅ Pesan berhasil disimpan ke file TXT!")
        
        # Cleanup
        await cleanup_temp_file(output_file)
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Error saving message to TXT: {e}")
        await update.message.reply_text(f"❌ Error menyimpan pesan: {str(e)}")

async def process_bug_report(update: Update, context: ContextTypes.DEFAULT_TYPE, bug_text: str):
    """Process bug report"""
    try:
        # Save bug report to file
        bug_file = "temp/bug_report.txt"
        with open(bug_file, 'w', encoding='utf-8') as f:
            f.write(f"Bug Report dari: {update.effective_user.first_name}\n")
            f.write(f"Username: @{update.effective_user.username}\n")
            f.write(f"User ID: {update.effective_user.id}\n")
            f.write(f"Tanggal: {update.message.date}\n")
            f.write("=" * 50 + "\n")
            f.write(bug_text)
        
        await update.message.reply_text(
            "🐞 **Bug Report Diterima!**\n\n"
            "Terima kasih telah melaporkan bug.\n"
            "Laporan Anda akan diproses dan diperbaiki.\n\n"
            "✅ Status: Tercatat\n"
            "🔧 Estimasi perbaikan: 1-3 hari kerja"
        )
        
        # Send bug report to developer (in real implementation, send to admin)
        logger.info(f"Bug report from {update.effective_user.id}: {bug_text}")
        
        # Cleanup
        await cleanup_temp_file(bug_file)
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Error processing bug report: {e}")
        await update.message.reply_text(f"❌ Error memproses laporan bug: {str(e)}")
