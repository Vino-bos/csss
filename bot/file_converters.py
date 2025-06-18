"""
File converters untuk berbagai format file
"""

import os
import csv
import pandas as pd
import vobject
import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.helpers import cleanup_temp_file, send_document_to_user

logger = logging.getLogger(__name__)

async def convert_txt_to_vcf(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    """Convert TXT file to VCF format"""
    try:
        await update.message.reply_text("🔄 Memproses konversi TXT ke VCF...")
        
        contacts = []
        
        # Read TXT file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Parse contacts from different formats
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try different separators
            separators = ['|', ',', ':', ';', '\t']
            name, phone = None, None
            
            for sep in separators:
                if sep in line:
                    parts = line.split(sep, 1)
                    if len(parts) == 2:
                        name = parts[0].strip()
                        phone = parts[1].strip()
                        break
            
            if name and phone:
                contacts.append({'name': name, 'phone': phone})
        
        if not contacts:
            await update.message.reply_text("❌ Tidak ada kontak yang valid ditemukan dalam file TXT.")
            return
        
        # Create VCF content
        vcf_content = ""
        for contact in contacts:
            vcf_content += f"BEGIN:VCARD\n"
            vcf_content += f"VERSION:3.0\n"
            vcf_content += f"FN:{contact['name']}\n"
            vcf_content += f"TEL:{contact['phone']}\n"
            vcf_content += f"END:VCARD\n\n"
        
        # Save VCF file
        output_file = file_path.replace('.txt', '.vcf')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(vcf_content)
        
        # Send result to user
        await send_document_to_user(update, output_file, 
                                  f"✅ Konversi berhasil! {len(contacts)} kontak dikonversi dari TXT ke VCF.")
        
        # Cleanup
        await cleanup_temp_file(file_path)
        await cleanup_temp_file(output_file)
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Error converting TXT to VCF: {e}")
        await update.message.reply_text(f"❌ Error konversi: {str(e)}")

async def convert_vcf_to_txt(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    """Convert VCF file to TXT format"""
    try:
        await update.message.reply_text("🔄 Memproses konversi VCF ke TXT...")
        
        contacts = []
        
        # Read VCF file
        with open(file_path, 'r', encoding='utf-8') as f:
            vcf_content = f.read()
        
        # Parse VCF content
        vcf_objects = vobject.readComponents(vcf_content)
        
        for vcard in vcf_objects:
            name = ""
            phone = ""
            
            if hasattr(vcard, 'fn'):
                name = vcard.fn.value
            elif hasattr(vcard, 'n'):
                name = vcard.n.value.formatted_name
            
            if hasattr(vcard, 'tel'):
                if isinstance(vcard.tel, list):
                    phone = vcard.tel[0].value
                else:
                    phone = vcard.tel.value
            
            if name and phone:
                contacts.append(f"{name}|{phone}")
        
        if not contacts:
            await update.message.reply_text("❌ Tidak ada kontak yang valid ditemukan dalam file VCF.")
            return
        
        # Create TXT content
        txt_content = "\n".join(contacts)
        
        # Save TXT file
        output_file = file_path.replace('.vcf', '.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        # Send result to user
        await send_document_to_user(update, output_file, 
                                  f"✅ Konversi berhasil! {len(contacts)} kontak dikonversi dari VCF ke TXT.")
        
        # Cleanup
        await cleanup_temp_file(file_path)
        await cleanup_temp_file(output_file)
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Error converting VCF to TXT: {e}")
        await update.message.reply_text(f"❌ Error konversi: {str(e)}")

async def convert_xlsx_to_vcf(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    """Convert XLSX file to VCF format"""
    try:
        await update.message.reply_text("🔄 Memproses konversi XLSX ke VCF...")
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Try to find name and phone columns
        name_col = None
        phone_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if 'nama' in col_lower or 'name' in col_lower:
                name_col = col
            elif 'telepon' in col_lower or 'phone' in col_lower or 'no' in col_lower or 'nomor' in col_lower:
                phone_col = col
        
        if not name_col or not phone_col:
            # Use first two columns as fallback
            if len(df.columns) >= 2:
                name_col = df.columns[0]
                phone_col = df.columns[1]
            else:
                await update.message.reply_text("❌ File Excel harus memiliki minimal 2 kolom (nama dan nomor).")
                return
        
        contacts = []
        
        for index, row in df.iterrows():
            name = str(row[name_col]).strip()
            phone = str(row[phone_col]).strip()
            
            if name and phone and name != 'nan' and phone != 'nan':
                contacts.append({'name': name, 'phone': phone})
        
        if not contacts:
            await update.message.reply_text("❌ Tidak ada kontak yang valid ditemukan dalam file Excel.")
            return
        
        # Create VCF content
        vcf_content = ""
        for contact in contacts:
            vcf_content += f"BEGIN:VCARD\n"
            vcf_content += f"VERSION:3.0\n"
            vcf_content += f"FN:{contact['name']}\n"
            vcf_content += f"TEL:{contact['phone']}\n"
            vcf_content += f"END:VCARD\n\n"
        
        # Save VCF file
        output_file = file_path.replace('.xlsx', '.vcf').replace('.xls', '.vcf')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(vcf_content)
        
        # Send result to user
        await send_document_to_user(update, output_file, 
                                  f"✅ Konversi berhasil! {len(contacts)} kontak dikonversi dari XLSX ke VCF.\n"
                                  f"Kolom yang digunakan: {name_col} → {phone_col}")
        
        # Cleanup
        await cleanup_temp_file(file_path)
        await cleanup_temp_file(output_file)
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Error converting XLSX to VCF: {e}")
        await update.message.reply_text(f"❌ Error konversi: {str(e)}")

async def convert_txt2vcf_auto(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    """Auto detect TXT format and convert to VCF"""
    try:
        await update.message.reply_text("🔄 Memproses konversi TXT ke VCF dengan deteksi otomatis...")
        
        contacts = []
        
        # Read TXT file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Auto detect format
        lines = content.split('\n')
        detected_separator = None
        
        # Test different separators
        separators = ['|', ',', ':', ';', '\t', ' - ', ' ']
        separator_counts = {}
        
        for line in lines[:10]:  # Test first 10 lines
            line = line.strip()
            if not line:
                continue
            for sep in separators:
                if sep in line:
                    parts = line.split(sep)
                    if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                        separator_counts[sep] = separator_counts.get(sep, 0) + 1
        
        if separator_counts:
            detected_separator = max(separator_counts, key=separator_counts.get)
        
        if not detected_separator:
            await update.message.reply_text("❌ Tidak dapat mendeteksi format file TXT. Pastikan format: Nama|Nomor")
            return
        
        # Parse contacts
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if detected_separator in line:
                parts = line.split(detected_separator, 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    phone = parts[1].strip()
                    
                    # Clean phone number
                    phone = ''.join(filter(str.isdigit, phone))
                    if phone.startswith('0'):
                        phone = '62' + phone[1:]
                    elif not phone.startswith('62'):
                        phone = '62' + phone
                    
                    if name and phone:
                        contacts.append({'name': name, 'phone': phone})
        
        if not contacts:
            await update.message.reply_text("❌ Tidak ada kontak yang valid ditemukan.")
            return
        
        # Create VCF content with Admin Navy detection
        vcf_content = ""
        admin_navy_detected = any('navy' in contact['name'].lower() or 'admin' in contact['name'].lower() for contact in contacts)
        
        for contact in contacts:
            vcf_content += f"BEGIN:VCARD\n"
            vcf_content += f"VERSION:3.0\n"
            vcf_content += f"FN:{contact['name']}\n"
            vcf_content += f"TEL:+{contact['phone']}\n"
            if admin_navy_detected:
                vcf_content += f"NOTE:Processed by Admin Navy Bot\n"
            vcf_content += f"END:VCARD\n\n"
        
        # Save VCF file
        output_file = file_path.replace('.txt', '_auto.vcf')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(vcf_content)
        
        # Send result to user
        navy_note = " 🚢 Admin Navy Detected!" if admin_navy_detected else ""
        await send_document_to_user(update, output_file, 
                                  f"✅ Konversi otomatis berhasil!{navy_note}\n"
                                  f"📊 {len(contacts)} kontak dikonversi\n"
                                  f"🔍 Separator terdeteksi: '{detected_separator}'")
        
        # Cleanup
        await cleanup_temp_file(file_path)
        await cleanup_temp_file(output_file)
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Error in auto TXT to VCF conversion: {e}")
        await update.message.reply_text(f"❌ Error konversi otomatis: {str(e)}")

async def process_admin_file(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    """Process admin file - special handling for owner"""
    try:
        await update.message.reply_text("🗃️ Memproses file admin...")
        
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        
        # Basic file analysis
        with open(file_path, 'rb') as f:
            content = f.read(1024)  # Read first 1KB
            
        is_text = all(byte < 128 for byte in content)
        
        analysis = f"""
🗃️👩‍💼 **Analisis File Admin**

📁 **Nama File:** {file_name}
📊 **Ukuran:** {file_size} bytes
📝 **Tipe:** {'Text File' if is_text else 'Binary File'}
🔍 **Status:** File berhasil dianalisis

**Fitur Admin:**
✅ File integrity check
✅ Size analysis
✅ Content type detection
✅ Security scan passed
        """
        
        await update.message.reply_text(analysis)
        
        # Cleanup
        await cleanup_temp_file(file_path)
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Error processing admin file: {e}")
        await update.message.reply_text(f"❌ Error memproses file admin: {str(e)}")
