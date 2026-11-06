import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eminakkurt.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Veritabanı tablolarını oluşturur."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Ziyaretçi Takip Tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visitors (
                session_id TEXT PRIMARY KEY,
                ip_address TEXT,
                user_agent TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                visit_count INTEGER DEFAULT 1
            )
        """)

        # 2. Sohbet Geçmişi Tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL, -- 'user' veya 'bot'
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES visitors (session_id)
            )
        """)

        # 3. İletişim & İş Teklifi Mesajları (MCP Tool ile doğrudan buraya yazılır!)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT DEFAULT 'unread', -- 'unread', 'read', 'replied'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

def log_visitor(session_id: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None):
    """Ziyaretçiyi kaydeder veya son görülme zamanını günceller."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO visitors (session_id, ip_address, user_agent, first_seen, last_seen, visit_count)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)
            ON CONFLICT(session_id) DO UPDATE SET
                last_seen = CURRENT_TIMESTAMP,
                visit_count = visitors.visit_count + 1
        """, (session_id, ip_address, user_agent))
        conn.commit()

def save_chat_message(session_id: str, role: str, message: str):
    """Sohbet mesajını kaydeder."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_logs (session_id, role, message)
            VALUES (?, ?, ?)
        """, (session_id, role, message))
        conn.commit()

def get_chat_history(session_id: str, limit: int = 15) -> List[Dict[str, Any]]:
    """Oturuma ait son sohbet geçmişini getirir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, message, created_at
            FROM chat_logs
            WHERE session_id = ?
            ORDER BY id ASC
            LIMIT ?
        """, (session_id, limit))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def save_contact_message(name: str, email: str, message: str, session_id: Optional[str] = None) -> int:
    """Ziyaretçinin Emin'e bıraktığı mesajı veritabanına kaydeder (MCP Tool fonksiyonu)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contact_messages (session_id, name, email, message)
            VALUES (?, ?, ?, ?)
        """, (session_id, name, email, message))
        conn.commit()
        return cursor.lastrowid

def get_all_contact_messages() -> List[Dict[str, Any]]:
    """Emin'e bırakılan tüm mesajları listeler."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contact_messages ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_site_statistics() -> Dict[str, Any]:
    """Ziyaretçi ve mesaj istatistiklerini getirir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total_visitors FROM visitors")
        visitors_count = cursor.fetchone()["total_visitors"]

        cursor.execute("SELECT COUNT(*) as total_messages FROM contact_messages")
        messages_count = cursor.fetchone()["total_messages"]

        cursor.execute("SELECT COUNT(*) as total_chats FROM chat_logs WHERE role = 'user'")
        chats_count = cursor.fetchone()["total_chats"]

        return {
            "total_visitors": visitors_count,
            "total_messages": messages_count,
            "total_user_questions": chats_count
        }

if __name__ == "__main__":
    init_db()
    print("Veritabani ve tablolar basariyla baslatildi!")
