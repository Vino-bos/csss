"""
User access management for bot
"""

import logging
from bot.database import get_db_connection

logger = logging.getLogger(__name__)

# Owner user ID - change this to your Telegram user ID
OWNER_USER_ID = 7614202330  # Replace with actual owner user ID

async def check_user_access(user_id: int) -> bool:
    """Check if user has access to the bot"""
    try:
        # Owner always has access
        if user_id == OWNER_USER_ID:
            return True
        
        # Check database for user access
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM authorized_users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
        
    except Exception as e:
        logger.error(f"Error checking user access: {e}")
        return False

async def is_owner(user_id: int) -> bool:
    """Check if user is the owner"""
    return user_id == OWNER_USER_ID

async def add_user(user_id: int, username: str = None) -> bool:
    """Add user to authorized users"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT user_id FROM authorized_users WHERE user_id = ?", (user_id,))
        if cursor.fetchone():
            conn.close()
            return False  # User already exists
        
        # Add user
        cursor.execute(
            "INSERT INTO authorized_users (user_id, username, added_date) VALUES (?, ?, datetime('now'))",
            (user_id, username)
        )
        conn.commit()
        conn.close()
        
        logger.info(f"User {user_id} ({username}) added to authorized users")
        return True
        
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return False

async def remove_user(user_id: int) -> bool:
    """Remove user from authorized users"""
    try:
        # Don't allow removing owner
        if user_id == OWNER_USER_ID:
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT user_id FROM authorized_users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            return False  # User doesn't exist
        
        # Remove user
        cursor.execute("DELETE FROM authorized_users WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        
        logger.info(f"User {user_id} removed from authorized users")
        return True
        
    except Exception as e:
        logger.error(f"Error removing user: {e}")
        return False

async def get_total_users() -> int:
    """Get total number of authorized users"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM authorized_users")
        count = cursor.fetchone()[0]
        conn.close()
        
        # Add 1 for owner if not in database
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM authorized_users WHERE user_id = ?", (OWNER_USER_ID,))
        if not cursor.fetchone():
            count += 1
        
        return count
        
    except Exception as e:
        logger.error(f"Error getting total users: {e}")
        return 0

async def get_all_users() -> list:
    """Get all authorized users"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, added_date FROM authorized_users ORDER BY added_date")
        users = []
        
        for row in cursor.fetchall():
            users.append({
                'user_id': row[0],
                'username': row[1] or 'Unknown',
                'added_date': row[2]
            })
        
        conn.close()
        
        # Add owner if not in database
        owner_in_db = any(user['user_id'] == OWNER_USER_ID for user in users)
        if not owner_in_db:
            users.insert(0, {
                'user_id': OWNER_USER_ID,
                'username': 'Owner',
                'added_date': 'System'
            })
        
        return users
        
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return []

async def process_add_user(update, context, user_input: str):
    """Process add user command"""
    try:
        user_input = user_input.strip()
        
        # Parse user input
        if user_input.startswith('@'):
            # Username format
            username = user_input[1:]  # Remove @
            await update.message.reply_text(
                f"❌ Fitur menambah user berdasarkan username belum tersedia.\n"
                f"Gunakan User ID numerik.\n"
                f"User dapat mengetahui ID mereka dengan command /start di bot @userinfobot"
            )
            return
        else:
            # User ID format
            try:
                user_id = int(user_input)
            except ValueError:
                await update.message.reply_text("❌ Format User ID tidak valid. Masukkan angka.")
                return
        
        # Add user
        success = await add_user(user_id)
        
        if success:
            await update.message.reply_text(
                f"✅ **Pengguna berhasil ditambahkan!**\n\n"
                f"👤 User ID: {user_id}\n"
                f"🎉 User sekarang dapat mengakses bot"
            )
        else:
            await update.message.reply_text(
                f"❌ **Gagal menambah pengguna**\n\n"
                f"Kemungkinan penyebab:\n"
                f"• User sudah memiliki akses\n"
                f"• Error database\n"
                f"• User ID tidak valid"
            )
        
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Error processing add user: {e}")
        await update.message.reply_text(f"❌ Error menambah user: {str(e)}")

async def process_delete_user(update, context, user_input: str):
    """Process delete user command"""
    try:
        user_input = user_input.strip()
        
        # Parse user input
        if user_input.startswith('@'):
            # Username format
            await update.message.reply_text(
                f"❌ Fitur menghapus user berdasarkan username belum tersedia.\n"
                f"Gunakan User ID numerik."
            )
            return
        else:
            # User ID format
            try:
                user_id = int(user_input)
            except ValueError:
                await update.message.reply_text("❌ Format User ID tidak valid. Masukkan angka.")
                return
        
        # Check if trying to remove owner
        if user_id == OWNER_USER_ID:
            await update.message.reply_text("❌ Tidak dapat menghapus akses owner!")
            return
        
        # Remove user
        success = await remove_user(user_id)
        
        if success:
            await update.message.reply_text(
                f"✅ **Akses pengguna berhasil dihapus!**\n\n"
                f"👤 User ID: {user_id}\n"
                f"🚫 User tidak dapat lagi mengakses bot"
            )
        else:
            await update.message.reply_text(
                f"❌ **Gagal menghapus akses pengguna**\n\n"
                f"Kemungkinan penyebab:\n"
                f"• User tidak memiliki akses\n"
                f"• Error database\n"
                f"• User ID tidak ditemukan"
            )
        
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Error processing delete user: {e}")
        await update.message.reply_text(f"❌ Error menghapus user: {str(e)}")
