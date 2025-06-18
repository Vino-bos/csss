"""
Contact manipulation utilities for VCF files
"""

import os
import vobject
import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.helpers import cleanup_temp_file, send_document_to_user

logger = logging.getLogger(__name__)

async def count_contacts_in_vcf(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    """Count total contacts in VCF file"""
    try:
        await update.message.reply_text("🔢 Menghitung total kontak dalam file VCF...")
        
        # Read VCF file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count BEGIN:VCARD occurrences
        vcard_count = content.count('BEGIN:VCARD')
        
        # Try to parse with vobject for detailed analysis
        try:
            vcf_objects = list(vobject.readComponents(content))
            detailed_count = len(vcf_objects)
            
            # Analyze contact details
            contacts_with_phone = 0
            contacts_with_name = 0
            
            for vcard in vcf_objects:
                if hasattr(vcard, 'tel'):
                    contacts_with_phone += 1
                if hasattr(vcard, 'fn') or hasattr(vcard, 'n'):
                    contacts_with_name += 1
            
            result_message = f"""
🔢📇 **Hasil Perhitungan Kontak VCF**

📊 **Total Kontak:** {detailed_count}
📞 **Kontak dengan Nomor:** {contacts_with_phone}
👤 **Kontak dengan Nama:** {contacts_with_name}
📄 **Ukuran File:** {os.path.getsize(file_path)} bytes

✅ **Status:** Analisis berhasil
📝 **Catatan:** File VCF valid dan dapat diproses
            """
            
        except Exception as parse_error:
            logger.warning(f"VCF parsing error, using simple count: {parse_error}")
            result_message = f"""
🔢📇 **Hasil Perhitungan Kontak VCF**

📊 **Total Kontak:** {vcard_count} (estimasi)
📄 **Ukuran File:** {os.path.getsize(file_path)} bytes

⚠️ **Catatan:** Menggunakan perhitungan sederhana
📝 **Saran:** File mungkin memiliki format yang tidak standar
            """
        
        await update.message.reply_text(result_message)
        
        # Cleanup
        await cleanup_temp_file(file_path)
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Error counting contacts: {e}")
        await update.message.reply_text(f"❌ Error menghitung kontak: {str(e)}")

async def add_contact_to_vcf(update: Update, context: ContextTypes.DEFAULT_TYPE, contact_data: str):
    """Add new contact to existing VCF file"""
    try:
        vcf_file = context.user_data.get('vcf_file')
        if not vcf_file:
            await update.message.reply_text("❌ File VCF tidak ditemukan. Silakan upload ulang.")
            return
        
        # Parse contact data
        if '|' not in contact_data:
            await update.message.reply_text("❌ Format salah. Gunakan: Nama|Nomor")
            return
        
        name, phone = contact_data.split('|', 1)
        name = name.strip()
        phone = phone.strip()
        
        if not name or not phone:
            await update.message.reply_text("❌ Nama dan nomor tidak boleh kosong.")
            return
        
        await update.message.reply_text("➕ Menambahkan kontak ke file VCF...")
        
        # Read existing VCF content
        with open(vcf_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # Create new vCard
        new_vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
TEL:{phone}
END:VCARD"""
        
        # Combine content
        if existing_content.strip():
            updated_content = existing_content.strip() + '\n\n' + new_vcard
        else:
            updated_content = new_vcard
        
        # Save updated VCF
        output_file = vcf_file.replace('.vcf', '_updated.vcf')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        # Count total contacts
        total_contacts = updated_content.count('BEGIN:VCARD')
        
        # Send updated file
        await send_document_to_user(update, output_file, 
                                  f"✅ Kontak berhasil ditambahkan!\n"
                                  f"👤 Nama: {name}\n"
                                  f"📞 Nomor: {phone}\n"
                                  f"📇 Total kontak: {total_contacts}")
        
        # Cleanup
        await cleanup_temp_file(vcf_file)
        await cleanup_temp_file(output_file)
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Error adding contact: {e}")
        await update.message.reply_text(f"❌ Error menambah kontak: {str(e)}")

async def delete_contact_from_vcf(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    """Delete contact from VCF file"""
    try:
        await update.message.reply_text("🔍 Menganalisis kontak dalam file VCF...")
        
        # Read VCF file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse contacts
        contacts = []
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
        
        # Extract contact info for display
        for i, vcard_text in enumerate(vcards):
            name = "Unknown"
            phone = "Unknown"
            
            for line in vcard_text.split('\n'):
                if line.startswith('FN:'):
                    name = line[3:].strip()
                elif line.startswith('TEL:'):
                    phone = line[4:].strip()
            
            contacts.append({'index': i, 'name': name, 'phone': phone, 'vcard': vcard_text})
        
        if not contacts:
            await update.message.reply_text("❌ Tidak ada kontak ditemukan dalam file VCF.")
            return
        
        # Display contacts for selection
        contact_list = []
        for i, contact in enumerate(contacts[:10]):  # Show first 10 contacts
            contact_list.append(f"{i+1}. {contact['name']} - {contact['phone']}")
        
        if len(contacts) > 10:
            contact_list.append(f"... dan {len(contacts) - 10} kontak lainnya")
        
        contacts_text = "\n".join(contact_list)
        
        await update.message.reply_text(
            f"📇 **Daftar Kontak ({len(contacts)} total):**\n\n{contacts_text}\n\n"
            "Kirim nomor urut kontak yang ingin dihapus (1, 2, 3, dst)"
        )
        
        context.user_data['vcf_contacts'] = contacts
        context.user_data['vcf_file'] = file_path
        context.user_data['waiting_for'] = 'delete_contact_index'
        
    except Exception as e:
        logger.error(f"Error analyzing VCF for deletion: {e}")
        await update.message.reply_text(f"❌ Error menganalisis file: {str(e)}")

async def process_delete_contact(update: Update, context: ContextTypes.DEFAULT_TYPE, index_text: str):
    """Process contact deletion by index"""
    try:
        index = int(index_text.strip()) - 1  # Convert to 0-based index
        contacts = context.user_data.get('vcf_contacts')
        file_path = context.user_data.get('vcf_file')
        
        if not contacts or not file_path:
            await update.message.reply_text("❌ Data kontak tidak ditemukan. Silakan upload ulang.")
            return
        
        if index < 0 or index >= len(contacts):
            await update.message.reply_text(f"❌ Nomor urut tidak valid. Pilih antara 1-{len(contacts)}")
            return
        
        contact_to_delete = contacts[index]
        await update.message.reply_text(f"🗑️ Menghapus kontak: {contact_to_delete['name']}")
        
        # Remove the selected contact
        remaining_vcards = [c['vcard'] for i, c in enumerate(contacts) if i != index]
        
        if not remaining_vcards:
            await update.message.reply_text("❌ Tidak dapat menghapus semua kontak. File akan kosong.")
            return
        
        # Create updated VCF content
        updated_content = '\n\n'.join(remaining_vcards)
        
        # Save updated file
        output_file = file_path.replace('.vcf', '_deleted.vcf')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        # Send updated file
        await send_document_to_user(update, output_file, 
                                  f"✅ Kontak berhasil dihapus!\n"
                                  f"🗑️ Dihapus: {contact_to_delete['name']} - {contact_to_delete['phone']}\n"
                                  f"📇 Sisa kontak: {len(remaining_vcards)}")
        
        # Cleanup
        await cleanup_temp_file(file_path)
        await cleanup_temp_file(output_file)
        context.user_data.clear()
        
    except ValueError:
        await update.message.reply_text("❌ Masukkan nomor urut yang valid.")
    except Exception as e:
        logger.error(f"Error deleting contact: {e}")
        await update.message.reply_text(f"❌ Error menghapus kontak: {str(e)}")

async def process_rename_contact(update: Update, context: ContextTypes.DEFAULT_TYPE, rename_data: str):
    """Process contact renaming in VCF"""
    try:
        vcf_file = context.user_data.get('vcf_file')
        if not vcf_file:
            await update.message.reply_text("❌ File VCF tidak ditemukan. Silakan upload ulang.")
            return
        
        # Parse rename data
        if '|' not in rename_data:
            await update.message.reply_text("❌ Format salah. Gunakan: NamaLama|NamaBaru")
            return
        
        old_name, new_name = rename_data.split('|', 1)
        old_name = old_name.strip()
        new_name = new_name.strip()
        
        if not old_name or not new_name:
            await update.message.reply_text("❌ Nama lama dan nama baru tidak boleh kosong.")
            return
        
        await update.message.reply_text(f"✏️ Mengganti nama '{old_name}' menjadi '{new_name}'...")
        
        # Read VCF file
        with open(vcf_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace contact name
        updated_content = content.replace(f'FN:{old_name}', f'FN:{new_name}')
        
        # Check if any replacement was made
        if updated_content == content:
            await update.message.reply_text(f"❌ Kontak dengan nama '{old_name}' tidak ditemukan.")
            return
        
        # Save updated VCF
        output_file = vcf_file.replace('.vcf', '_renamed.vcf')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        # Count replacements
        replacements = content.count(f'FN:{old_name}')
        
        # Send updated file
        await send_document_to_user(update, output_file, 
                                  f"✅ Nama kontak berhasil diubah!\n"
                                  f"📝 Dari: {old_name}\n"
                                  f"📝 Ke: {new_name}\n"
                                  f"🔄 Jumlah perubahan: {replacements}")
        
        # Cleanup
        await cleanup_temp_file(vcf_file)
        await cleanup_temp_file(output_file)
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Error renaming contact: {e}")
        await update.message.reply_text(f"❌ Error mengubah nama kontak: {str(e)}")
