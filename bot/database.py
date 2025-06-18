"""
Database operations for bot
"""

import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = 'bot_database.db'

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def init_database():
    """Initialize database tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create authorized_users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authorized_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                added_date TEXT,
                added_by INTEGER
            )
        ''')
        
        # Create bug_reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bug_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                bug_description TEXT NOT NULL,
                report_date TEXT,
                status TEXT DEFAULT 'open'
            )
        ''')
        
        # Create file_operations table for logging
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                operation_type TEXT NOT NULL,
                file_name TEXT,
                operation_date TEXT,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

def log_file_operation(user_id: int, operation_type: str, file_name: str, status: str):
    """Log file operation to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO file_operations (user_id, operation_type, file_name, operation_date, status)
            VALUES (?, ?, ?, datetime('now'), ?)
        ''', (user_id, operation_type, file_name, status))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error logging file operation: {e}")

def log_bug_report(user_id: int, username: str, bug_description: str):
    """Log bug report to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bug_reports (user_id, username, bug_description, report_date)
            VALUES (?, ?, ?, datetime('now'))
        ''', (user_id, username, bug_description))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Bug report logged from user {user_id}")
        
    except Exception as e:
        logger.error(f"Error logging bug report: {e}")

def get_user_stats(user_id: int):
    """Get user statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get operation count
        cursor.execute('''
            SELECT operation_type, COUNT(*) 
            FROM file_operations 
            WHERE user_id = ? 
            GROUP BY operation_type
        ''', (user_id,))
        
        operations = cursor.fetchall()
        conn.close()
        
        return operations
        
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        return []

def cleanup_old_records(days: int = 30):
    """Clean up old records from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Clean old file operations
        cursor.execute('''
            DELETE FROM file_operations 
            WHERE operation_date < datetime('now', '-' || ? || ' days')
        ''', (days,))
        
        # Clean old bug reports that are resolved
        cursor.execute('''
            DELETE FROM bug_reports 
            WHERE status = 'resolved' AND report_date < datetime('now', '-' || ? || ' days')
        ''', (days,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Cleaned up records older than {days} days")
        
    except Exception as e:
        logger.error(f"Error cleaning up old records: {e}")
